"""Bounded query + impact analysis over a generated graph.yaml.

Both operate on the shared ``traversal.py`` engine. Defaults are bounded:
query = 25 nodes / 1 hop; impact = 50 nodes / 3 hops. Output is concise by
default (id, kind, name, source, resolution, significance) and never prints the
full graph unless explicitly requested.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .traversal import Bounds, GraphStore, TraversalResult, bounded_bfs

CONCISE_FIELDS = ("id", "kind", "name", "source", "resolution", "significance")

# Query selector kinds -> node kind(s) they match.
KIND_ALIASES = {
    "role": ("role",),
    "task": ("task",),
    "handler": ("handler",),
    "variable": ("variable", "variable_namespace"),
    "template": ("template",),
    "playbook": ("playbook",),
    "play": ("play",),
    "file": ("template", "task_file", "role_file"),
    "service": ("task",),          # matched by attribute/name
    "tag": ("task",),              # matched by tags attribute
    "flavor": ("inventory_flavor",),
    "host": ("inventory_host",),
    "group": ("inventory_group",),
    "collection": ("collection",),
    "vars_plugin": ("vars_plugin",),
}


@dataclass
class QueryOptions:
    limit: int = 25
    max_depth: int = 1
    max_output_bytes: int = 65_536
    fields: tuple[str, ...] = CONCISE_FIELDS
    output: str = "concise"          # concise | yaml
    include_neighbours: bool = True
    include_attributes: bool = False
    direction: str = "both"


def find_roots(store: GraphStore, selector: str, term: str | None) -> list[str]:
    """Find matching root node ids for a query selector + optional term."""
    kinds = KIND_ALIASES.get(selector)
    roots: list[str] = []
    term_l = term.lower() if term else None

    for nid, n in store.nodes.items():
        if kinds and n.get("kind") not in kinds:
            continue
        if term_l is None:
            roots.append(nid)
            continue
        if selector == "tag":
            tags = [t.lower() for t in n.get("attributes", {}).get("tags", [])]
            if term_l in tags:
                roots.append(nid)
        elif selector == "service":
            hay = (n.get("name", "") + " " + str(n.get("attributes", {}))).lower()
            if term_l in hay:
                roots.append(nid)
        elif selector == "file":
            src = (n.get("source") or {}).get("path", "")
            if term_l in src.lower():
                roots.append(nid)
        else:
            if n.get("name", "").lower() == term_l or term_l in nid.lower():
                roots.append(nid)
    return sorted(roots)


def run_query(store: GraphStore, selector: str, term: str | None, opts: QueryOptions) -> dict[str, Any]:
    roots = find_roots(store, selector, term)
    bounds = Bounds(opts.limit, opts.max_depth if opts.include_neighbours else 0, opts.max_output_bytes)
    result = bounded_bfs(store, roots, bounds, direction=opts.direction)
    return _shape(store, result, opts, header={"selector": selector, "term": term,
                                               "matched_roots": len(roots)})


def run_impact(store: GraphStore, path: str, opts: QueryOptions) -> dict[str, Any]:
    """Static impact of a source path: what depends on / reaches it.

    Roots = every node whose source path matches ``path``. Traversal follows
    INCOMING edges (who reaches this) plus outgoing (what it affects), bounded.
    """
    path_l = path.lower().rstrip("/")
    roots = sorted(
        nid for nid, n in store.nodes.items()
        if _path_matches((n.get("source") or {}).get("path", "").lower(), path_l)
    )
    bounds = Bounds(opts.limit, opts.max_depth, opts.max_output_bytes)
    result = bounded_bfs(store, roots, bounds, direction="both")
    shaped = _shape(store, result, opts, header={"impact_path": path, "matched_roots": len(roots)})
    # Summaries an operator wants for impact specifically.
    shaped["affected"] = _impact_summary(store, result)
    shaped["caveat"] = ("Static reachability only. Dynamic includes, templated names, "
                        "custom vars plugins and runtime facts are NOT resolved here.")
    return shaped


def _path_matches(node_path: str, target: str) -> bool:
    """Exact file match, or directory-prefix match for a directory target.

    Deliberately does NOT match by bare basename (e.g. every ``main.yml``),
    which would explode the impact set.
    """
    if not node_path:
        return False
    if node_path == target:
        return True
    # target is a directory (or file dir) -> match everything under it
    return node_path.startswith(target + "/")


def _impact_summary(store: GraphStore, result: TraversalResult) -> dict[str, Any]:
    handlers, services, roles, playbooks, flavors, variables = set(), set(), set(), set(), set(), set()
    for nid in result.node_ids:
        n = store.nodes.get(nid, {})
        kind = n.get("kind")
        if kind == "handler":
            handlers.add(n.get("name"))
        elif kind == "role":
            roles.add(n.get("name"))
        elif kind == "playbook":
            playbooks.add(n.get("name"))
        elif kind == "inventory_flavor":
            flavors.add(n.get("name"))
        elif kind == "variable":
            variables.add(n.get("name"))
        elif kind == "task":
            svc = n.get("attributes", {}).get("module", "")
            if svc:
                services.add(svc)
    return {
        "handlers_notified": sorted(filter(None, handlers)),
        "roles_reached": sorted(filter(None, roles)),
        "playbooks_reached": sorted(filter(None, playbooks)),
        "flavors": sorted(filter(None, flavors)),
        "variables_consumed": sorted(filter(None, variables))[:50],
    }


def _shape(store: GraphStore, result: TraversalResult, opts: QueryOptions, header: dict) -> dict[str, Any]:
    nodes_out = []
    for nid in result.node_ids:
        n = store.nodes.get(nid, {})
        if opts.include_attributes or opts.output == "yaml":
            nodes_out.append(_select_fields(n, opts.fields, include_attrs=True))
        else:
            nodes_out.append(_select_fields(n, opts.fields, include_attrs=False))
    payload = {
        **header,
        "returned_nodes": len(nodes_out),
        "truncated": result.truncated,
        "truncation_reason": result.truncation_reason,
        "nodes": nodes_out,
    }
    if opts.include_neighbours:
        payload["edges"] = [
            {"id": e.get("id"), "type": e.get("type"), "from": e.get("from"),
             "to": e.get("to"), "resolution": e.get("resolution", {}).get("status")}
            for e in result.edges
        ]
    # Enforce output-byte ceiling deterministically.
    rendered = render_output(payload, opts.output)
    if len(rendered.encode("utf-8")) > opts.max_output_bytes:
        payload["nodes"] = payload["nodes"][: max(1, opts.limit // 2)]
        payload["truncated"] = True
        payload["truncation_reason"] = (payload.get("truncation_reason") or "") + \
            f"; output byte ceiling {opts.max_output_bytes} enforced"
    return payload


def _select_fields(n: dict, fields: tuple[str, ...], include_attrs: bool) -> dict:
    out = {}
    for f in fields:
        if f in n:
            out[f] = n[f]
    if include_attrs and "attributes" in n:
        out["attributes"] = n["attributes"]
    return out


def render_output(payload: dict, output: str) -> str:
    if output == "yaml":
        y = YAML()
        y.default_flow_style = False
        buf = io.StringIO()
        y.dump(payload, buf)
        return buf.getvalue()
    # concise text
    lines = []
    for k in ("selector", "term", "impact_path", "matched_roots", "returned_nodes",
              "truncated", "truncation_reason"):
        if k in payload and payload[k] is not None:
            lines.append(f"{k}: {payload[k]}")
    lines.append("nodes:")
    for n in payload.get("nodes", []):
        src = n.get("source") or {}
        loc = f"{src.get('path','?')}:{src.get('line_start','')}" if src else "?"
        res = (n.get("resolution") or {}).get("status", "")
        lines.append(f"  - [{n.get('kind','?')}] {n.get('name','')} "
                     f"({n.get('significance','')}, {res}) {loc}  id={n.get('id')}")
    if "affected" in payload:
        lines.append("affected:")
        for k, v in payload["affected"].items():
            if v:
                lines.append(f"  {k}: {', '.join(map(str, v))}")
    if payload.get("caveat"):
        lines.append(f"caveat: {payload['caveat']}")
    return "\n".join(lines) + "\n"


def load_store(context_dir: Path) -> GraphStore:
    return GraphStore.load(context_dir / "graph.yaml")


# --------------------------------------------------------------------------
# views: compact, source-traceable FACT digests (facts only — no prose)
# --------------------------------------------------------------------------

VIEWS = ("summary", "actions", "relationships", "sources")


def _role_task_nodes(store: GraphStore, role: str) -> list[dict]:
    prefix = f"roles/{role}/"
    tasks = [
        n for n in store.nodes.values()
        if n.get("kind") == "task"
        and (n.get("attributes", {}).get("role") == role
             or (n.get("source") or {}).get("path", "").startswith(prefix))
    ]
    return sorted(tasks, key=lambda n: ((n.get("source") or {}).get("path", ""),
                                        (n.get("source") or {}).get("line_start") or 0))


def _role_handlers(store: GraphStore, role: str) -> list[dict]:
    prefix = f"roles/{role}/"
    hs = [n for n in store.nodes.values()
          if n.get("kind") == "handler"
          and ((n.get("attributes", {}).get("role") == role)
               or (n.get("source") or {}).get("path", "").startswith(prefix))]
    return sorted(hs, key=lambda n: n.get("name", ""))


def run_view(store: GraphStore, selector: str, term: str | None, view: str,
             opts: "QueryOptions") -> dict[str, Any]:
    if view == "sources":
        payload = run_query(store, selector, term, opts)
        paths = sorted({(n.get("source") or {}).get("path") for n in payload["nodes"]
                        if n.get("source")})
        return {"view": "sources", "selector": selector, "term": term, "source_paths": paths}

    if view == "relationships":
        p = run_query(store, selector, term, opts)
        p["view"] = "relationships"
        return p

    # summary / actions are role-oriented digests.
    if selector != "role" or not term:
        # fall back to a plain query for non-role targets
        p = run_query(store, selector, term, opts)
        p["view"] = view
        return p

    role = term
    tasks = _role_task_nodes(store, role)
    handlers = _role_handlers(store, role)
    src_files = sorted({(n.get("source") or {}).get("path") for n in tasks if n.get("source")})

    if view == "summary":
        ops: dict[str, int] = {}
        pkgs, svcs, tmpls = set(), set(), set()
        for n in tasks:
            a = n.get("attributes", {})
            op = a.get("operation", "")
            ops[op] = ops.get(op, 0) + 1
            r = a.get("resource", {}) or {}
            if op == "install_package" and r.get("packages"):
                pkgs.update(_as_str_list(r["packages"]))
            if op == "service_state" and r.get("name"):
                svcs.add(str(r["name"]))
            if op == "render_template" and r.get("dest"):
                tmpls.add(str(r["dest"]))
        return {
            "view": "summary", "role": role, "task_count": len(tasks),
            "operations": dict(sorted(ops.items())),
            "packages": sorted(pkgs)[:20], "services": sorted(svcs)[:20],
            "templated_files": sorted(tmpls)[:20],
            "handlers": [h.get("name") for h in handlers],
            "source_files": src_files,
        }

    # view == "actions": the managed-resource digest (the crux)
    actions = []
    for i, n in enumerate(tasks, 1):
        a = n.get("attributes", {})
        src = n.get("source") or {}
        actions.append({
            "n": i,
            "operation": a.get("operation", a.get("module", "?")),
            "task": n.get("name"),
            "resource": a.get("resource", {}),
            "when": a.get("when"),
            "notify": a.get("notify"),
            "become": a.get("become"),
            "significance": n.get("significance"),
            "verify": a.get("verification"),
            "source": f"{src.get('path','?')}:{src.get('line_start','')}",
        })
    return {
        "view": "actions", "role": role, "task_count": len(tasks),
        "actions": actions,
        "handlers": [h.get("name") for h in handlers],
        "source_files": src_files,
        "note": "Deterministic facts extracted from source. Open the cited source "
                "file(s) for any action flagged 'verify', for exact conditionals, "
                "or before acting on critical/destructive operations.",
    }


def _as_str_list(v) -> list[str]:
    if isinstance(v, list):
        return [str(x) for x in v]
    return [str(v)]


def render_view(payload: dict, output: str = "concise") -> str:
    if output == "yaml":
        return render_output(payload, "yaml")
    view = payload.get("view")
    if view == "sources":
        lines = [f"sources for {payload.get('selector')} {payload.get('term') or ''}:".rstrip()]
        lines += [f"  {p}" for p in payload.get("source_paths", [])]
        return "\n".join(lines) + "\n"
    if view == "relationships":
        return render_output(payload, "concise")
    if view == "summary":
        lines = [f"role: {payload['role']}  ({payload['task_count']} tasks)"]
        if payload.get("packages"):
            lines.append(f"  packages: {', '.join(payload['packages'])}")
        if payload.get("services"):
            lines.append(f"  services: {', '.join(payload['services'])}")
        if payload.get("templated_files"):
            lines.append(f"  templates → {', '.join(payload['templated_files'])}")
        if payload.get("handlers"):
            lines.append(f"  handlers: {', '.join(payload['handlers'])}")
        lines.append(f"  operations: {payload.get('operations')}")
        lines.append(f"  source files: {', '.join(payload.get('source_files', []))}")
        return "\n".join(lines) + "\n"
    if view == "actions":
        lines = [f"role: {payload['role']}  ({payload['task_count']} actions)"]
        for a in payload["actions"]:
            flag = " ⚠verify" if a.get("verify") else ""
            crit = "" if a.get("significance") in (None, "normal", "low") else f" [{a['significance']}]"
            lines.append(f"{a['n']}. [{a['operation']}]{crit}{flag} {a['task']}")
            for k, v in (a.get("resource") or {}).items():
                lines.append(f"     {k}: {v}")
            if a.get("when"):
                lines.append(f"     when: {a['when']}")
            if a.get("notify"):
                lines.append(f"     notify: {', '.join(a['notify'])}")
            if a.get("verify"):
                lines.append(f"     verify: {a['verify'].get('reason')}")
            lines.append(f"     ↳ {a['source']}")
        if payload.get("handlers"):
            lines.append(f"handlers: {', '.join(payload['handlers'])}")
        lines.append(f"note: {payload['note']}")
        return "\n".join(lines) + "\n"
    return render_output(payload, "concise")


# --------------------------------------------------------------------------
# explain: focused, human-readable explanation of a single node
# --------------------------------------------------------------------------

def resolve_target(store: GraphStore, target: str) -> list[str]:
    """Resolve a target to node id(s): exact id, else name match across kinds."""
    if target in store.nodes:
        return [target]
    tl = target.lower()
    exact = sorted(nid for nid, n in store.nodes.items() if n.get("name", "").lower() == tl)
    if exact:
        return exact
    # substring on id/name as a last resort
    return sorted(nid for nid, n in store.nodes.items()
                  if tl in nid.lower() or tl in n.get("name", "").lower())[:25]


def run_explain(store: GraphStore, target: str, opts: QueryOptions) -> dict[str, Any]:
    matches = resolve_target(store, target)
    if not matches:
        return {"target": target, "found": False,
                "message": "no node matches that id or name"}
    if len(matches) > 1:
        return {
            "target": target, "found": True, "ambiguous": True,
            "candidates": [
                {"id": m, "kind": store.nodes[m].get("kind"),
                 "name": store.nodes[m].get("name")}
                for m in matches
            ],
            "message": f"{len(matches)} nodes match; re-run explain with an exact id",
        }

    nid = matches[0]
    n = store.nodes[nid]
    src = n.get("source") or {}
    res = n.get("resolution") or {}

    # 1-hop neighbours grouped by edge type + direction, each with its reason.
    outgoing: list[dict] = []
    incoming: list[dict] = []
    for to_id, e in store.neighbours(nid, "out"):
        outgoing.append(_edge_view(store, e, to_id, "→"))
    for from_id, e in store.neighbours(nid, "in"):
        incoming.append(_edge_view(store, e, from_id, "←"))

    return {
        "target": target, "found": True, "ambiguous": False,
        "id": nid,
        "kind": n.get("kind"),
        "name": n.get("name"),
        "significance": n.get("significance"),
        "significance_rule_id": n.get("significance_rule_id"),
        "source": {
            "path": src.get("path"),
            "lines": (f"{src.get('line_start')}-{src.get('line_end')}"
                      if src.get("line_start") else None),
            "content_hash": src.get("content_hash"),
        },
        "resolution": {
            "status": res.get("status"),
            "confidence": res.get("confidence"),
            "reason": res.get("reason"),
        },
        "attributes": n.get("attributes", {}) if opts.include_attributes else _key_attrs(n),
        "relationships": {
            "outgoing": sorted(outgoing, key=lambda x: (x["type"], x["other"])),
            "incoming": sorted(incoming, key=lambda x: (x["type"], x["other"])),
        },
    }


def _edge_view(store: GraphStore, edge: dict, other_id: str, arrow: str) -> dict:
    other = store.nodes.get(other_id, {})
    eres = edge.get("resolution") or {}
    return {
        "type": edge.get("type"),
        "arrow": arrow,
        "other": other_id,
        "other_kind": other.get("kind", "?"),
        "other_name": other.get("name", ""),
        "status": eres.get("status"),
        "reason": eres.get("reason"),
    }


def _key_attrs(n: dict) -> dict:
    """A trimmed attribute view for concise explain output."""
    attrs = n.get("attributes", {})
    keep = ("module", "role", "flavor", "environment", "origin", "version",
            "notify", "listen", "tags", "precedence_class", "scope",
            "sensitive_name", "consumed_dirs", "environments")
    return {k: attrs[k] for k in keep if k in attrs}


def render_explain(payload: dict, output: str = "concise") -> str:
    if output == "yaml":
        y = YAML()
        y.default_flow_style = False
        buf = io.StringIO()
        y.dump(payload, buf)
        return buf.getvalue()
    if not payload.get("found"):
        return payload.get("message", "not found") + "\n"
    if payload.get("ambiguous"):
        lines = [payload["message"], "candidates:"]
        for c in payload["candidates"]:
            lines.append(f"  - [{c['kind']}] {c['name']}  id={c['id']}")
        return "\n".join(lines) + "\n"

    s = payload["source"]
    r = payload["resolution"]
    lines = [
        f"{payload['id']}",
        f"  kind:         {payload['kind']}",
        f"  name:         {payload['name']}",
        f"  significance: {payload['significance']}"
        + (f"  (rule: {payload['significance_rule_id']})" if payload.get("significance_rule_id") else ""),
        f"  source:       {s['path']}" + (f":{s['lines']}" if s.get("lines") else ""),
        f"  resolution:   {r['status']} / {r['confidence']} — {r['reason']}",
    ]
    if payload.get("attributes"):
        lines.append("  attributes:")
        for k, v in payload["attributes"].items():
            lines.append(f"    {k}: {v}")
    rel = payload["relationships"]
    if rel["outgoing"]:
        lines.append("  outgoing:")
        for e in rel["outgoing"]:
            lines.append(f"    {e['arrow']} [{e['type']}] {e['other_kind']} {e['other_name']} "
                         f"({e['status']}: {e['reason']})  {e['other']}")
    if rel["incoming"]:
        lines.append("  incoming:")
        for e in rel["incoming"]:
            lines.append(f"    {e['arrow']} [{e['type']}] {e['other_kind']} {e['other_name']} "
                         f"({e['status']}: {e['reason']})  {e['other']}")
    return "\n".join(lines) + "\n"
