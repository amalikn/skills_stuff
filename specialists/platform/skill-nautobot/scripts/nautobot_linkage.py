"""Find the breaks in a Location's Nautobot hierarchy: objects that belong to it but that nothing links to it. Read-only, stdlib only.

Why: a site is only navigable when every object can be reached from its Location by following links (foreign keys, M2M fields,
Relationship associations). Objects found by a filter or by name (a Namespace named after the site, a DNS view, the A records in its
zone) can exist with no link back, and nothing in the UI shows it. One deployment had Prefixes that did not list their Location, A
records whose address was on no device and devices with no primary address, all invisible until a graph walk reported them; two
objects can also share a Namespace without the link that matters existing, which is why reachability alone is not enough and named
rules sit beside it.

The engine is generic; the caller supplies the HTTP GET, what to collect and the rules:
    collectors  `Scoped` (filterable to the site; `query` formatted with the quoted site name), `Linked` (has a foreign key, any of
                `via`, to an object already collected; the listing is fetched whole once) and `Referenced` (pointed at through `field`
                by objects of `from_kind`). Order matters: Linked and Referenced see only what earlier collectors added.
    rules       a `Rules` registry of functions over the graph (no API calls), each yielding (kind, name, detail); `evaluate()` runs
                them and adds a `graph.island` finding for every collected object unreachable from the Location.
    unmodelled  `Source.unmodelled(covered)` lists endpoints that hold objects but that nothing covers, so a new kind of object shows
                up until someone adds a collector or says why it is not site data.
Listings are read through `nautobot_paging` (total order, fail-closed), so a doubtful listing raises instead of hiding a gap.

Usage:
    from nautobot_linkage import Rules, Scoped, Linked, Source, evaluate, print_site
    RULES = Rules()
    @RULES.rule("prefix.location", "error")
    def _prefix_location(g):
        "Each Prefix lists the site's Location."
        ...
    src = Source(lambda path: session.get(base + path, timeout=60).json())   # path is relative to /api
    g = src.graph("site-a", [Scoped("dcim.location", "/dcim/locations/", "name={site}"), ...])
    print_site("site-a", evaluate(g, RULES), RULES)
"""

from __future__ import annotations

import collections
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Iterable, Iterator

from nautobot_paging import listing, traverse

SEVERITIES = ("error", "warn", "info")
EXAMPLES = 5
ISLAND_RULE = "graph.island"
ISLAND_DOC = "Everything collected for the site is reachable from its Location."
#: Relationship associations are edges, not objects; they are fetched once and joined on source_id/destination_id.
RELATIONSHIP_PATH = "/extras/relationship-associations/"
RELATIONSHIPS_PATH = "/extras/relationships/"
#: What every collected listing asks for: plain foreign keys, and M2M members included.
DEPTH_QUERY = "depth=0&exclude_m2m=false"


# -- collectors: what belongs to a site -----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Scoped:
    """Objects the API can filter to the site. `query` is formatted with the site name."""
    kind: str
    path: str
    query: str


@dataclass(frozen=True)
class Linked:
    """Objects with a foreign key (any of `via`) pointing at an object already collected. Fetched whole once, kept by link."""
    kind: str
    path: str
    via: tuple[str, ...]


@dataclass(frozen=True)
class Referenced:
    """Objects that an already-collected object points at through `field` on objects of `from_kind`."""
    kind: str
    path: str
    from_kind: str
    field: str


# -- the graph ----------------------------------------------------------------------------------------------------------------

def refs(obj: dict) -> Iterator[tuple[str, str]]:
    """(field, id) for every foreign key and M2M member in a depth-0 object."""
    for key, value in obj.items():
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, dict) and "id" in item and "object_type" in item:
                yield key, item["id"]


def ref(obj: dict, key: str) -> str | None:
    """The id behind foreign key `key`, or None."""
    value = obj.get(key)
    return value.get("id") if isinstance(value, dict) else None


@dataclass
class SiteGraph:
    """The objects collected for one site, keyed by id, plus Relationship edges (a, b, relationship key)."""
    site: str
    nodes: dict[str, tuple[str, dict]] = field(default_factory=dict)          # id -> (kind, object)
    extra_edges: list[tuple[str, str, str]] = field(default_factory=list)      # (a, b, relationship key)
    root_kind: ClassVar[str] = "dcim.location"

    def add(self, kind: str, obj: dict) -> None:
        self.nodes.setdefault(obj["id"], (kind, obj))

    def of(self, kind: str) -> list[dict]:
        return [o for k, o in self.nodes.values() if k == kind]

    def kind_of(self, oid: str | None) -> str | None:
        return self.nodes[oid][0] if oid in self.nodes else None

    @property
    def location(self) -> dict | None:
        locs = self.of(self.root_kind)
        return locs[0] if locs else None

    def edges(self) -> dict[str, set[str]]:
        adj: dict[str, set[str]] = collections.defaultdict(set)
        for oid, (_, obj) in self.nodes.items():
            for _, target in refs(obj):
                if target in self.nodes:
                    adj[oid].add(target)
                    adj[target].add(oid)
        for a, c, _ in self.extra_edges:
            if a in self.nodes and c in self.nodes:
                adj[a].add(c)
                adj[c].add(a)
        return adj

    def reachable(self) -> set[str]:
        loc = self.location
        if not loc:
            return set()
        adj, seen, todo = self.edges(), {loc["id"]}, [loc["id"]]
        while todo:
            for nxt in adj[todo.pop()]:
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        return seen

    def related(self, key: str, oid: str) -> set[str]:
        """The objects joined to `oid` by Relationship `key`, in either direction."""
        return {c if a == oid else a for a, c, k in self.extra_edges if k == key and oid in (a, c)}


def label(kind: str, obj: dict) -> str:
    """A readable name for any object: name, address, prefix, display, else the id's first 8 characters."""
    return str(obj.get("name") or obj.get("address") or obj.get("prefix") or obj.get("display") or obj["id"][:8])


# -- rules: the links that should exist -----------------------------------------------------------------------------------------

@dataclass
class Finding:
    rule: str
    severity: str
    kind: str
    name: str
    detail: str = ""


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    doc: str
    fn: Callable[[SiteGraph], Iterable[tuple[str, str, str]]]


class Rules(list):
    """An ordered registry of rules. `@rules.rule(id, severity)` registers a function; its docstring is the rule's description."""

    def rule(self, rule_id: str, severity: str):
        if severity not in SEVERITIES:
            raise ValueError(f"severity {severity!r} is not one of {SEVERITIES}")
        if any(r.id == rule_id for r in self):
            raise ValueError(f"rule {rule_id!r} is already registered")

        def register(fn):
            self.append(Rule(rule_id, severity, (fn.__doc__ or "").strip(), fn))
            return fn
        return register


def islands(g: SiteGraph) -> Iterator[Finding]:
    """A `graph.island` warning for every collected object no chain of links reaches from the Location."""
    seen = g.reachable()
    for oid, (kind, obj) in g.nodes.items():
        if oid not in seen:
            yield Finding(ISLAND_RULE, "warn", kind, label(kind, obj), "not reachable from the Location through any link")


def evaluate(g: SiteGraph, rules: Iterable[Rule]) -> list[Finding]:
    """Every rule's findings, in rule order, then the islands."""
    out = [Finding(r.id, r.severity, k, n, dt) for r in rules for k, n, dt in r.fn(g)]
    return out + list(islands(g))


# -- collection (the only part that calls the API) ----------------------------------------------------------------------------

def _relative(url: str) -> str:
    """A `next` link is absolute; the caller's GET takes paths relative to /api."""
    return url.split("/api", 1)[1] if "://" in url else url


def pages(get: Callable[[str], dict], path: str) -> list[dict]:
    """Every row of `path` at depth 0 with M2M members, in a total order, failing closed (`nautobot_paging.traverse`)."""
    return traverse(lambda url: get(_relative(url)), listing(path + ("&" if "?" in path else "?") + DEPTH_QUERY))


class Source:
    """Reads Nautobot through `get(path)` (path relative to /api, returning parsed JSON). Whole listings are cached per instance."""

    def __init__(self, get: Callable[[str], dict]):
        self._get = get
        self._whole: dict[str, list[dict]] = {}

    def pages(self, path: str) -> list[dict]:
        return pages(self._get, path)

    def whole(self, path: str) -> list[dict]:
        if path not in self._whole:
            self._whole[path] = self.pages(path)
        return self._whole[path]

    def names(self, path: str) -> dict[str, str]:
        return {o["id"]: o["name"] for o in self.whole(path)}

    def graph(self, site: str, collectors: Iterable[Scoped | Linked | Referenced], *,
              new: Callable[[str], SiteGraph] = SiteGraph, annotate: Callable[[str, dict], None] | None = None) -> SiteGraph:
        """Collect `site`'s objects in collector order, then join Relationship associations touching any of them.

        `new(site)` builds the graph (a SiteGraph subclass may carry more state); `annotate(kind, obj)` may add derived fields before
        an object is added.
        """
        g = new(site)
        for c in collectors:
            if isinstance(c, Scoped):
                found = self.pages(f"{c.path}?{c.query.format(site=urllib.parse.quote(site))}")
            elif isinstance(c, Linked):
                found = [o for o in self.whole(c.path) if any(ref(o, v) in g.nodes for v in c.via)]
            else:
                wanted = {ref(o, c.field) for o in g.of(c.from_kind)}
                found = [o for o in self.whole(c.path) if o["id"] in wanted]
            for obj in found:
                if annotate:
                    annotate(c.kind, obj)
                g.add(c.kind, obj)
        rel_keys = {r["id"]: r["key"] for r in self.whole(RELATIONSHIPS_PATH)}
        for a in self.whole(RELATIONSHIP_PATH):
            if a["source_id"] in g.nodes or a["destination_id"] in g.nodes:
                g.extra_edges.append((a["source_id"], a["destination_id"], rel_keys.get(ref(a, "relationship") or "", "?")))
        return g

    def unmodelled(self, covered: Iterable[str], *, skip_apps: Iterable[str] = ("plugins", "status", "graphql", "docs", "swagger", "ui"),
                   skip_plugins: Iterable[str] = ("installed-plugins",)) -> list[tuple[str, int]]:
        """(path, count) for every list endpoint that holds objects and is not in `covered`, sorted by path."""
        covered, skip_apps, skip_plugins = set(covered), set(skip_apps), set(skip_plugins)
        roots = [f"/{app}/" for app in self._get("/") if app not in skip_apps]
        roots += [f"/plugins/{p}/" for p in self._get("/plugins/") if p not in skip_plugins]
        out = []
        for root in roots:
            try:
                index = self._get(root)
            except urllib.error.HTTPError:  # an app root that is not a listing is not a model endpoint
                continue
            for url in index.values() if isinstance(index, dict) else []:
                path = "/" + url.split("/api/", 1)[1]
                if path in covered:
                    continue
                try:
                    count = self._get(f"{path}?limit=1").get("count", 0)
                except urllib.error.HTTPError:  # not a list endpoint
                    continue
                if count:
                    out.append((path, count))
        return sorted(out)


# -- report -------------------------------------------------------------------------------------------------------------------

def summarise(findings: list[Finding]) -> dict[tuple[str, str], list[Finding]]:
    """Findings grouped by (severity, rule)."""
    by: dict[tuple[str, str], list[Finding]] = collections.defaultdict(list)
    for f in findings:
        by[(f.severity, f.rule)].append(f)
    return by


def print_site(site: str, findings: list[Finding], rules: Iterable[Rule], examples: int = EXAMPLES) -> None:
    """One site's findings: a count per severity, then each rule (worst first, most findings first) with up to `examples` lines."""
    by = summarise(findings)
    counts = collections.Counter(f.severity for f in findings)
    print(f"\n{site}: " + ", ".join(f"{counts[s]} {s}" for s in SEVERITIES))
    docs = {r.id: r.doc for r in rules} | {ISLAND_RULE: ISLAND_DOC}
    for (sev, rid), fs in sorted(by.items(), key=lambda kv: (SEVERITIES.index(kv[0][0]), -len(kv[1]))):
        print(f"  [{sev}] {rid} x{len(fs)}: {docs.get(rid, '')}")
        for f in fs[:examples]:
            print(f"      {f.kind:28} {f.name:32} {f.detail}")
        if len(fs) > examples:
            print(f"      ... and {len(fs) - examples} more")


def print_estate(report: dict[str, list[Finding]]) -> None:
    """Many sites: one line per site (most errors first), then each rule's reach across the estate."""
    print(f"{'site':18} {'error':>5} {'warn':>5} {'info':>5}  top rules")
    for site, fs in sorted(report.items(), key=lambda kv: -sum(f.severity == 'error' for f in kv[1])):
        c = collections.Counter(f.severity for f in fs)
        top = collections.Counter(f.rule for f in fs if f.severity != "info").most_common(3)
        print(f"{site:18} {c['error']:5} {c['warn']:5} {c['info']:5}  " + ", ".join(f"{r} {n}" for r, n in top))
    total = collections.Counter((f.severity, f.rule) for fs in report.values() for f in fs)
    print("\nrules across the estate (sites affected / findings):")
    for (sev, rid), n in sorted(total.items(), key=lambda kv: (SEVERITIES.index(kv[0][0]), -kv[1])):
        print(f"  [{sev}] {rid:24} {sum(any(f.rule == rid for f in fs) for fs in report.values()):3} sites / {n}")
