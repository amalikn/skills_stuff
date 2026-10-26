"""Offline tests for a family with `own_page: true` (operator, 2026-10-26): its flows are drawn only on their own End-to-end page, left off
the full one, and that page is drawn even with `look.e2e_family_pages` off. Drawn from the example shop map, operations family marked.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
page_audit = importlib.import_module("drawio.audit").page_audit
e2e, e2e_family, model, pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("e2e", "e2e_family", "map_parts", "pages", "profile"))
EXAMPLE = ROOT / "examples" / "shop" / "flows.yaml"
OWN = "operations"


def _map(own: object = True, **look: object) -> dict:
    """The example shop map with the operations family's `own_page` set and look keys pinned.

    Args:
        own: the value of `own_page` on the operations family; None leaves the key out.
        look: the `drawing.look` keys to set.

    Returns:
        The map.
    """
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    data["drawing"]["look"] = {**(data["drawing"].get("look") or {}), **look}
    for fam in data["drawing"]["families"]:
        if fam["id"] == OWN and own is not None:
            fam["own_page"] = own
    return data


def _prof(data: dict) -> object:
    """The profile the map's drawing block gives.

    Args:
        data: the map.

    Returns:
        The profile.
    """
    return profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")


def _diagrams(data: dict) -> dict[str, ET.Element]:
    """The rendered file's `<diagram>` elements by id.

    Args:
        data: the map.

    Returns:
        {diagram id: element}, in tab order.
    """
    text = pages.render(data, _prof(data))
    return {d.get("id"): d for d in ET.fromstring(text.split("-->", 1)[1]).iter("diagram")}


def _own_flows(data: dict) -> list[str]:
    """The flow ids of the operations family.

    Args:
        data: the map.

    Returns:
        Their ids.
    """
    return next(f["flows"] for f in data["drawing"]["families"] if f["id"] == OWN)


class OwnPage(unittest.TestCase):
    """own_page: off the full page, on its own page with the whole map's numbers, indexed, audits clean."""

    def test_false_is_the_same_as_absent(self) -> None:
        """`own_page: false` renders byte-identical to a map without the key."""
        self.assertEqual(pages.render(_map(None), _prof(_map(None))), pages.render(_map(False), _prof(_map(False))))

    def test_only_the_own_family_gets_a_page(self) -> None:
        """With e2e_family_pages off, the own family's page follows the full page and no other family page is drawn."""
        ids = list(_diagrams(_map()))
        at = ids.index("end-to-end")
        self.assertEqual(ids[at + 1], f"end-to-end-{OWN}")
        self.assertEqual([i for i in ids if i.startswith("end-to-end-")], [f"end-to-end-{OWN}"])

    def test_e2e_page_false_keeps_only_flow_pages(self) -> None:
        """`e2e_page: false` on an own family: no family End-to-end page or index entry, its flows off the full page, each on its own page."""
        data = _map()
        for fam in data["drawing"]["families"]:
            if fam["id"] == OWN:
                fam["e2e_page"] = False
        dia = _diagrams(data)
        self.assertFalse([i for i in dia if i.startswith("end-to-end-")])
        self.assertNotIn(f"end-to-end-{OWN}", ET.tostring(dia["overview"], encoding="unicode"))
        full = ET.tostring(dia["end-to-end"], encoding="unicode")
        for fid in _own_flows(data):
            self.assertNotIn(f"flow-{fid}", full)
            self.assertIn(f"flow-{fid}", dia)

    def test_tab_names_the_flow_page(self) -> None:
        """A flow's `tab` is its page's tab name in place of '<number>. <title>'."""
        data = _map()
        data["flows"][0]["tab"] = "Named outright"
        names = {d.get("id"): d.get("name") for d in _diagrams(data).values()}
        self.assertEqual(names[f"flow-{data['flows'][0]['id']}"], "Named outright")

    def test_full_page_leaves_the_own_flows_off(self) -> None:
        """No cell on the full page is tagged with an own flow; the own page tags each of them."""
        data = _map(e2e_layers="flow")
        dia = _diagrams(data)
        full, own = (ET.tostring(dia[k], encoding="unicode") for k in ("end-to-end", f"end-to-end-{OWN}"))
        for fid in _own_flows(data):
            self.assertNotIn(f"flow-{fid}", full, fid)
            self.assertIn(f"flow-{fid}", own, fid)

    def test_own_flows_numbered_from_one(self) -> None:
        """Shared flows count 1.. among themselves and the own flows 1.. on their own page; tabs carry the family prefix."""
        data = _map()
        own_ids = _own_flows(data)
        shared = [f["id"] for f in data["flows"] if f["id"] not in own_ids]
        self.assertEqual([f["id"] for f in model.shared_part(data, _prof(data))["flows"]], shared)
        nums = model.flow_numbers(data, _prof(data))
        self.assertEqual([nums[f] for f in shared], list(range(1, len(shared) + 1)))
        self.assertEqual([nums[f] for f in own_ids], list(range(1, len(own_ids) + 1)))
        dia = _diagrams(data)
        own = ET.tostring(dia[f"end-to-end-{OWN}"], encoding="unicode")
        self.assertEqual({int(n) for n in re.findall(r"&lt;b&gt;(\d+)\.\d+", own)}, set(range(1, len(own_ids) + 1)))
        self.assertEqual(dia[f"flow-{own_ids[0]}"].get("name").split(".")[0], "Operations 1")

    def test_prefix_names_the_tabs(self) -> None:
        """A family `prefix` replaces its name before the flow number on tabs."""
        data = _map()
        for fam in data["drawing"]["families"]:
            if fam["id"] == OWN:
                fam["prefix"] = "Ops"
        self.assertTrue(_diagrams(data)[f"flow-{_own_flows(data)[0]}"].get("name").startswith("Ops 1. "))

    def test_components_only_the_own_flows_touch_leave_the_full_page(self) -> None:
        """A component only an own flow touches is off the full page; one a shared flow also touches stays."""
        data = _map()
        prof = _prof(data)
        part = model.shared_part(data, prof)
        own = model.flows_part(data, [f for f in data["flows"] if f["id"] in _own_flows(data)])
        shared = {c["id"] for c in model.flows_part(data, part["flows"])["components"]}
        only = {c["id"] for c in own["components"]} - shared
        self.assertTrue(only, "no component is touched only by the own flows, so this test cannot fail")
        kept = {c["id"] for c in part["components"]}
        self.assertFalse(only & kept)
        self.assertTrue({c["id"] for c in own["components"]} & shared <= kept)

    def test_overview_indexes_only_the_own_page(self) -> None:
        """The Overview links the own family's page and no other family page."""
        overview = ET.tostring(_diagrams(_map())["overview"], encoding="unicode")
        self.assertEqual(re.findall(r'id="ov-f-end-to-end-([a-z-]+)"', overview), [OWN])

    def test_audits_clean(self) -> None:
        """The full page and the own page pass every layout audit."""
        data = _map(e2e_layers="flow")
        prof = _prof(data)
        for page in [e2e.end_to_end_page(data, prof)] + e2e_family.family_pages(data, prof):
            self.assertFalse([k for k, v in page_audit(page).items() if v], page.page_id)


    def test_flow_pages_false_drops_the_pages_and_index_rows(self) -> None:
        """`flow_pages: false` leaves the family's E2E page and drops its flow tabs and index rows; other flows keep theirs."""
        data = _map()
        for fam in data["drawing"]["families"]:
            if fam["id"] == OWN:
                fam["flow_pages"] = False
        dia = _diagrams(data)
        overview = ET.tostring(dia["overview"], encoding="unicode")
        self.assertIn(f"end-to-end-{OWN}", dia)
        for f in data["flows"]:
            own = f["id"] in _own_flows(data)
            self.assertEqual(f"flow-{f['id']}" in dia, not own, f["id"])
            self.assertEqual(f'id="ov-f-{f["id"]}"' in overview, not own, f["id"])

    def test_full_page_drops_a_column_only_own_flows_use(self) -> None:
        """A tier holding only components of the own family is no column on the full page, and is one on the own page."""
        data = _map()
        own = model.flows_part(data, [f for f in data["flows"] if f["id"] in _own_flows(data)])["components"]
        shared = {c["id"] for c in model.flows_part(data, model.shared_part(data, _prof(data))["flows"])["components"]}
        lone = next(c for c in own if c["id"] not in shared)
        lone["group"] = "Own only"
        data["drawing"]["tiers"] = [{"name": "Own only", "groups": ["Own only"]}] + data["drawing"]["tiers"]
        dia = _diagrams(data)
        heads = lambda pid: re.findall(r'value="&lt;b&gt;([^&]+)&lt;/b&gt;"[^>]*id="e2[ef]-[a-z-]*tier-', ET.tostring(dia[pid], encoding="unicode")) or \
            re.findall(r'id="e2[ef]-[a-z-]*tier-\d+"[^>]*value="&lt;b&gt;([^&]+)&lt;/b&gt;"', ET.tostring(dia[pid], encoding="unicode"))
        self.assertNotIn("Own only", heads("end-to-end"))
        self.assertIn("Own only", heads(f"end-to-end-{OWN}"))

class ThinSharedRuns(unittest.TestCase):
    """Thin arrows with no end in common may not share a run (audit), and the Overview nudges such an entry aside (2026-10-26)."""

    def test_audit_flags_thin_arrows_with_no_common_end(self) -> None:
        """Two thin arrows on one vertical line with different ends are a shared run; a fan-out from one box is not."""
        mx = importlib.import_module("drawio.mxfile")
        audit = importlib.import_module("drawio.audit")
        a = mx.Route("a", "s1", "t1", [(100, 0), (100, 50)], klass="thin")
        b = mx.Route("b", "s2", "t2", [(100, 40), (100, 90)], klass="thin")
        fan = mx.Route("c", "s1", "t3", [(100, 10), (100, 45)], klass="thin")
        self.assertEqual(audit.layout_audit({}, [a, b])["shared_runs"], ["a = b"])
        self.assertEqual(audit.layout_audit({}, [a, fan])["shared_runs"], [])

    def test_overview_entry_leaves_another_exit_line(self) -> None:
        """A box stacked above another's target exits on the line the drop into that target follows; the drop is moved off it.

        The group is the one that showed it (2026-10-26): a root needing two boxes, and two boxes needing a third.
        """
        data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
        needs = {"z-root": ["z-lower", "z-svc"], "z-lower": [], "z-backup": [], "z-svc": [], "z-pkgs": [], "z-web": ["z-pkgs"],
                 "z-cron": ["z-pkgs"]}
        kind = data["components"][0]["kind"]
        data["components"] += [{"id": k, "name": k, "kind": kind, "group": "Zone", "host": "h", "health": "h", **({"depends_on": v} if v else {})}
                               for k, v in needs.items()]
        page = importlib.import_module("flowmap.overview").overview_page(data, _prof(data))
        self.assertFalse(page_audit(page)["shared_runs"])

if __name__ == "__main__":
    unittest.main()
