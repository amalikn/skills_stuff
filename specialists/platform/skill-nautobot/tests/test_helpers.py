"""Offline tests for the promoted helpers in scripts/: the fail-closed paging guard, the IPAM mask rule, the mask planner and
the site linkage engine."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
_ipam = importlib.import_module("nautobot_ipam")
_paging = importlib.import_module("nautobot_paging")
network_mask, with_mask = _ipam.network_mask, _ipam.with_mask
PagingError, listing, traverse = _paging.PagingError, _paging.listing, _paging.traverse
_masks = importlib.import_module("nautobot_masks")
_linkage = importlib.import_module("nautobot_linkage")


def pages(*chunks, count=None):
    """A fake GET over numbered pages: page n holds chunks[n]."""
    total = count if count is not None else sum(len(c) for c in chunks)
    book = {}
    for n, rows in enumerate(chunks):
        nxt = f"p{n + 1}" if n + 1 < len(chunks) else None
        book[f"p{n}"] = {"count": total, "next": nxt, "results": [{"id": r} for r in rows]}
    return lambda url: book[url]


class Listing(unittest.TestCase):
    def test_adds_limit_and_total_order(self):
        self.assertEqual(listing("/api/dcim/devices/"), "/api/dcim/devices/?limit=200&sort=id")
        self.assertEqual(listing("/api/x/?location=a"), "/api/x/?location=a&limit=200&sort=id")

    def test_keeps_callers_choices(self):
        self.assertEqual(listing("/api/x/?limit=50&sort=name"), "/api/x/?limit=50&sort=name")


class Traverse(unittest.TestCase):
    def test_reads_every_page(self):
        self.assertEqual([r["id"] for r in traverse(pages("ab", "cd"), "p0")], list("abcd"))

    def test_repeated_object_fails_rather_than_deduplicates(self):
        with self.assertRaisesRegex(PagingError, "two pages"):
            traverse(pages("ab", "bc", count=4), "p0")

    def test_count_mismatch_fails(self):
        with self.assertRaisesRegex(PagingError, "count"):
            traverse(pages("ab", "c", count=4), "p0")

    def test_repeated_continuation_fails(self):
        book = {"p0": {"count": 2, "next": "p0", "results": [{"id": 1}]}}
        with self.assertRaisesRegex(PagingError, "continuation"):
            traverse(book.__getitem__, "p0")

    def test_empty_page_before_end_fails(self):
        book = {"p0": {"count": 1, "next": "p1", "results": []}, "p1": {"count": 1, "next": None, "results": [{"id": 1}]}}
        with self.assertRaisesRegex(PagingError, "empty page"):
            traverse(book.__getitem__, "p0")

    def test_missing_results_and_missing_id_fail(self):
        with self.assertRaises(PagingError):
            traverse(lambda url: {"detail": "error"}, "p0")
        with self.assertRaises(PagingError):
            traverse(lambda url: {"count": 1, "next": None, "results": [{"name": "x"}]}, "p0")

    def test_page_bound(self):
        with self.assertRaisesRegex(PagingError, "pages"):
            traverse(lambda url: {"count": 9, "next": url + "x", "results": [{"id": url}]}, "p", max_pages=3)


class Mask(unittest.TestCase):
    PREFIXES = [
        {"prefix": "192.0.2.0/24", "type": {"value": "container"}},
        {"prefix": "192.0.2.0/25", "type": {"value": "network"}},
        {"prefix": "192.0.2.0/27", "type": "network"},
        {"prefix": "192.0.2.0/28", "type": {"value": "pool"}},
    ]

    def test_narrowest_network_prefix_wins(self):
        self.assertEqual(network_mask(self.PREFIXES, "192.0.2.10"), 27)
        self.assertEqual(with_mask(self.PREFIXES, "192.0.2.100"), "192.0.2.100/25")

    def test_containers_and_pools_are_not_subnets(self):
        self.assertIsNone(network_mask([self.PREFIXES[0], self.PREFIXES[3]], "192.0.2.5"))

    def test_no_holder_means_none_not_32(self):
        self.assertIsNone(with_mask(self.PREFIXES, "198.51.100.1"))


class MaskPlan(unittest.TestCase):
    """nautobot_masks: which /32s get their subnet's mask, which are only reported, and how the PATCH calls are shaped."""

    PREFIXES = [
        {"prefix": "198.51.100.0/24", "type": {"value": "container"}},
        {"prefix": "198.51.100.0/26", "type": {"value": "network"}},
        {"prefix": "192.0.2.0/24", "type": "network"},
        {"prefix": "198.51.100.0/28", "type": {"value": "pool"}},
    ]

    @staticmethod
    def addr(host, mask):
        return {"id": host, "host": host, "mask_length": mask, "address": f"{host}/{mask}"}

    def test_fixes_32s_and_reports_the_rest(self):
        a = self.addr
        fix, report = _masks.plan([a("198.51.100.5", 32), a("192.0.2.9", 32), a("198.51.100.6", 26), a("198.51.100.200", 32),
                                   a("198.51.100.7", 24)], self.PREFIXES)
        self.assertEqual([(x["host"], new) for x, new in fix], [("198.51.100.5", "198.51.100.5/26"), ("192.0.2.9", "192.0.2.9/24")])
        self.assertEqual([(x["host"], why) for x, why in report],
                         [("198.51.100.200", "no network Prefix holds it"), ("198.51.100.7", "mask /24 differs from its subnet's /26")])

    def test_placeholder_wider_than_min_subnet_is_reported_not_fixed(self):
        wide = [{"prefix": "198.51.0.0/16", "type": "network"}]
        fix, report = _masks.plan([self.addr("198.51.100.5", 32)], wide)
        self.assertEqual(fix, [])
        self.assertIn("/16, wider than /17", report[0][1])
        fix, _ = _masks.plan([self.addr("198.51.100.5", 32)], wide, min_subnet=16)
        self.assertEqual(fix[0][1], "198.51.100.5/16")

    def test_caller_wording_and_a_32_network_left_alone(self):
        _, report = _masks.plan([self.addr("198.51.100.200", 32)], self.PREFIXES, messages={"none": "orphan {have}"})
        self.assertEqual(report[0][1], "orphan 32")
        self.assertEqual(_masks.plan([self.addr("192.0.2.1", 32)], [{"prefix": "192.0.2.1/32", "type": "network"}]), ([], []))

    def test_second_plan_finds_nothing(self):
        fix, _ = _masks.plan([self.addr("198.51.100.5", 32)], self.PREFIXES)
        fixed = [self.addr(*new.split("/")[:1], int(new.split("/")[1])) for _, new in fix]
        self.assertEqual(_masks.plan(fixed, self.PREFIXES), ([], []))

    def test_apply_batches_patches(self):
        calls = []
        fix = [(self.addr(f"198.51.100.{n}", 32), f"198.51.100.{n}/26") for n in range(1, 6)]
        self.assertEqual(_masks.apply(lambda m, p, body: calls.append((m, p, body)), fix, batch=2), 5)
        self.assertEqual([len(b) for _, _, b in calls], [2, 2, 1])
        self.assertEqual(calls[0][:2], ("PATCH", "/ipam/ip-addresses/"))
        self.assertEqual(calls[0][2][0], {"id": "198.51.100.1", "address": "198.51.100.1/26"})
        self.assertEqual(_masks.apply(calls.append, [], batch=2), 0)
        with self.assertRaises(ValueError):
            _masks.apply(calls.append, fix, batch=0)


def fk(oid, kind):
    return {"id": oid, "object_type": kind, "url": f"http://x/{oid}/"}


class Linkage(unittest.TestCase):
    """nautobot_linkage: graph reachability, rules, islands, and collection through a fake API."""

    @staticmethod
    def site():
        g = _linkage.SiteGraph("site-a")
        g.add("dcim.location", {"id": "L", "name": "site-a"})
        g.add("ipam.namespace", {"id": "N", "name": "site-a", "location": fk("L", "dcim.location")})
        g.add("ipam.prefix", {"id": "P", "prefix": "192.0.2.0/24", "namespace": fk("N", "ipam.namespace"), "locations": []})
        g.add("ipam.ipaddress", {"id": "I", "address": "192.0.2.10/24", "parent": fk("P", "ipam.prefix")})
        g.add("dns.view", {"id": "V", "name": "site-a"})
        return g

    @staticmethod
    def rules():
        rules = _linkage.Rules()

        @rules.rule("prefix.location", "error")
        def _prefix_location(g):
            """Each Prefix lists the site's Location."""
            for p in g.of("ipam.prefix"):
                if g.location["id"] not in {i for k, i in _linkage.refs(p) if k == "locations"}:
                    yield "ipam.prefix", p["prefix"], "Location not in its locations"
        return rules

    def test_refs_reads_fk_and_m2m_only(self):
        obj = {"a": fk("1", "x.y"), "b": [fk("2", "x.y"), fk("3", "x.y")], "c": "plain", "d": None, "e": {"id": "4"}}
        self.assertEqual(sorted(_linkage.refs(obj)), [("a", "1"), ("b", "2"), ("b", "3")])
        self.assertEqual(_linkage.ref(obj, "a"), "1")
        self.assertIsNone(_linkage.ref(obj, "c"))

    def test_unlinked_object_is_an_island_until_a_relationship_joins_it(self):
        g = self.site()
        findings = _linkage.evaluate(g, self.rules())
        self.assertEqual([(f.rule, f.severity, f.name) for f in findings],
                         [("prefix.location", "error", "192.0.2.0/24"), ("graph.island", "warn", "site-a")])
        g.extra_edges.append(("V", "L", "view_site"))
        self.assertIn("V", g.reachable())
        self.assertEqual(g.related("view_site", "L"), {"V"})
        self.assertEqual([f.rule for f in _linkage.evaluate(g, self.rules())], ["prefix.location"])

    def test_no_location_means_nothing_is_reachable(self):
        g = _linkage.SiteGraph("site-b")
        g.add("ipam.prefix", {"id": "P", "prefix": "198.51.100.0/24"})
        self.assertEqual(g.reachable(), set())
        self.assertEqual([f.rule for f in _linkage.evaluate(g, [])], ["graph.island"])

    def test_registry_refuses_bad_severity_and_duplicate_ids(self):
        rules = self.rules()
        self.assertEqual(rules[0].doc, "Each Prefix lists the site's Location.")
        with self.assertRaises(ValueError):
            rules.rule("x", "fatal")
        with self.assertRaises(ValueError):
            rules.rule("prefix.location", "warn")

    def fake_api(self, extra=None):
        """A GET over a tiny Nautobot: one site with a Location, a Prefix, an A record linked by FK and a Relationship edge."""
        rows = {
            "/dcim/locations/": [{"id": "L", "name": "site-a"}],
            "/ipam/prefixes/": [{"id": "P", "prefix": "192.0.2.0/24", "locations": [fk("L", "dcim.location")]}],
            "/plugins/dns/a-records/": [{"id": "A", "name": "ap-1", "prefix": fk("P", "ipam.prefix")}, {"id": "B", "name": "far", "prefix": None}],
            "/dcim/devices/": [{"id": "D", "name": "dev-1", "status": fk("S", "extras.status")}],
            "/extras/relationships/": [{"id": "R", "key": "a_device"}],
            "/extras/relationship-associations/": [{"id": "X", "source_id": "A", "destination_id": "D", "relationship": fk("R", "extras.relationship")}],
            **(extra or {}),
        }
        seen = []

        def get(path):
            seen.append(path)
            base = path.split("?", 1)[0]
            return {"count": len(rows[base]), "next": None, "results": rows[base]}
        return get, seen

    def test_collects_in_order_and_joins_relationships(self):
        get, seen = self.fake_api()
        L = _linkage
        collectors = [L.Scoped("dcim.location", "/dcim/locations/", "name={site}"), L.Scoped("ipam.prefix", "/ipam/prefixes/", "location={site}"),
                      L.Linked("dns.a", "/plugins/dns/a-records/", ("prefix",))]
        tagged = []
        g = L.Source(get).graph("site a", collectors, annotate=lambda kind, obj: tagged.append(kind))
        self.assertEqual(sorted(g.nodes), ["A", "L", "P"])
        self.assertEqual(tagged, ["dcim.location", "ipam.prefix", "dns.a"])
        self.assertEqual(g.extra_edges, [("A", "D", "a_device")])
        self.assertTrue(seen[0].startswith("/dcim/locations/?name=site%20a&depth=0&exclude_m2m=false"))
        self.assertTrue(all("sort=id" in s for s in seen))

    def test_doubtful_listing_fails_closed(self):
        get, _ = self.fake_api({"/dcim/locations/": [{"id": "L", "name": "a"}, {"id": "L", "name": "a"}]})
        with self.assertRaises(PagingError):
            _linkage.Source(get).graph("a", [_linkage.Scoped("dcim.location", "/dcim/locations/", "name={site}")])

    def test_absolute_next_link_is_followed_as_a_path(self):
        book = {"/x/?depth=0&exclude_m2m=false&limit=200&sort=id": {"count": 2, "next": "https://n.example/api/x/?offset=1", "results": [{"id": 1}]},
                "/x/?offset=1": {"count": 2, "next": None, "results": [{"id": 2}]}}
        self.assertEqual([r["id"] for r in _linkage.pages(book.__getitem__, "/x/")], [1, 2])

    def test_unmodelled_lists_uncovered_endpoints_holding_objects(self):
        import urllib.error
        api = {"/": {"dcim": "u", "status": "u", "plugins": "u", "broken": "u"}, "/plugins/": {"dns": "u", "installed-plugins": "u"},
               "/dcim/": {"devices": "http://n/api/dcim/devices/", "racks": "http://n/api/dcim/racks/", "sites": "http://n/api/dcim/sites/"},
               "/plugins/dns/": {"views": "http://n/api/plugins/dns/views/"},
               "/dcim/devices/?limit=1": {"count": 3}, "/dcim/racks/?limit=1": {"count": 0}, "/plugins/dns/views/?limit=1": {"count": 2}}

        def get(path):
            if path not in api:
                raise urllib.error.HTTPError(path, 404, "not found", None, None)
            return api[path]
        self.assertEqual(_linkage.Source(get).unmodelled({"/dcim/devices/"}), [("/plugins/dns/views/", 2)])

    def test_reports_print_worst_first(self):
        import contextlib
        import io
        F = _linkage.Finding
        findings = [F("graph.island", "warn", "k", "n1"), F("prefix.location", "error", "ipam.prefix", "192.0.2.0/24", "d")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            _linkage.print_site("site-a", findings, self.rules())
            _linkage.print_estate({"site-a": findings, "site-b": []})
        text = out.getvalue()
        self.assertIn("site-a: 1 error, 1 warn, 0 info", text)
        self.assertLess(text.index("[error] prefix.location x1"), text.index("[warn] graph.island x1"))
        self.assertIn(_linkage.ISLAND_DOC, text)
        self.assertIn("rules across the estate", text)


class Governance(unittest.TestCase):
    """scripts/check_governance.py ("check_governance") is the pack's governance gate; it runs here so `just test` covers it."""

    PACK = Path(__file__).resolve().parents[1]

    def _run(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(root / "scripts" / "check_governance.py")], capture_output=True, text=True, check=False)

    def test_governance_claims_hold(self):
        result = self._run(self.PACK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_broken_reference_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "pack"
            shutil.copytree(self.PACK, copy, ignore=shutil.ignore_patterns(".git", "documents", "graphify-out", ".ai-context"))
            with (copy / "README.md").open("a", encoding="utf-8") as fh:
                fh.write("\nSee `references/does-not-exist.md`.\n")
            result = self._run(copy)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("does-not-exist.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
