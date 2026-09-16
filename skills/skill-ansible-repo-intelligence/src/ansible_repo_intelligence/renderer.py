"""Deterministic serialization of the lean output artifact set.

Emits exactly:
  manifest.yaml, graph.yaml, diagnostics.yaml, ANSIBLE_REPO_MAP.md, cache/scan-state.yaml

All collections are sorted by stable key. No timestamps are embedded inside
content-derived hashes. The repository map is bounded by the configured budget
and reports exact omitted counts on truncation.
"""

from __future__ import annotations

import io
from pathlib import Path

from ruamel.yaml import YAML

from . import PARSER_VERSION, SCHEMA_VERSION, TOOL_VERSION
from .app_config import AppConfig
from .diagnostics import ARI021_MAP_SECTION_TRUNCATED, Diagnostics
from .graph import Graph
from .models import Significance


def _yaml() -> YAML:
    y = YAML()
    y.default_flow_style = False
    y.width = 4096
    y.sort_keys = False  # we pre-sort; preserve our deterministic order
    return y


def _dump(data) -> str:
    buf = io.StringIO()
    _yaml().dump(data, buf)
    return buf.getvalue()


def render_graph_yaml(g: Graph) -> str:
    nodes = [g.nodes[k].to_dict() for k in sorted(g.nodes)]
    edges = [g.edges[k].to_dict() for k in sorted(g.edges)]
    doc = {
        "schema_version": g.schema_version,
        "statistics": g.statistics(),
        "retrieval_topics": g.retrieval_topics,
        "nodes": nodes,
        "edges": edges,
    }
    return _dump(doc)


def render_diagnostics_yaml(diags: Diagnostics) -> str:
    items = [d.to_dict() for d in diags.sorted_items()]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "counts": diags.counts(),
        "diagnostics": items,
    }
    return _dump(doc)


def render_manifest_yaml(
    cfg: AppConfig, g: Graph, diags: Diagnostics, source_fingerprint: str,
    config_fingerprint: str, output_hashes: dict[str, str],
    vendored_yaml_count: int, external_tools: dict,
) -> str:
    ci = g.context_integration.to_dict() if g.context_integration else {}
    doc = {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "parser_version": PARSER_VERSION,
        "understanding_boundary": (
            "High-coverage static understanding of repository structure and "
            "statically resolvable relationships, with explicit identification "
            "of dynamic and unresolved behaviour. Not complete runtime understanding."
        ),
        "source_fingerprint": source_fingerprint,
        "configuration_fingerprint": config_fingerprint,
        "parser_capabilities": {
            "jinja_parse_only": True,
            "inventory_executed": g.__dict__.get("_inventory_executed", False),
            "vendored_deep_indexed": cfg.deep_index_vendored,
        },
        "counts": {
            **g.statistics(),
            "vendored_yaml_excluded": vendored_yaml_count,
            "diagnostics": diags.counts(),
        },
        "output_files": output_hashes,
        "context_integration": ci,
        "external_tools": external_tools,
    }
    return _dump(doc)


def render_scan_state_yaml(file_hashes: dict[str, str], config_fingerprint: str) -> str:
    doc = {
        "schema_version": SCHEMA_VERSION,
        "parser_version": PARSER_VERSION,
        "configuration_fingerprint": config_fingerprint,
        "files": dict(sorted(file_hashes.items())),
    }
    return _dump(doc)


# --------------------------------------------------------------------------
# Repository map (bounded, human-readable)
# --------------------------------------------------------------------------

def render_repository_map(cfg: AppConfig, g: Graph, diags: Diagnostics) -> str:
    """Render ANSIBLE_REPO_MAP.md within the configured budget.

    Truncated sections always state the exact omitted count and the retrieval
    command, and emit ARI021. The whole document is capped at map_max_lines.
    """
    out: list[str] = []
    nodes = g.nodes

    def add(line: str = "") -> None:
        out.append(line)

    def section(title: str) -> None:
        add("")
        add(f"## {title}")
        add("")

    # --- header ---
    add("# Ansible Repository Map")
    add("")
    add("> Derived, non-authoritative navigation metadata. **Source files are")
    add("> authoritative.** This map orients an agent; it never replaces reading")
    add("> the original source. High-coverage *static* understanding only —")
    add("> dynamic/unresolved behaviour is labelled, not guessed.")

    stats = g.statistics()
    section("Scan metadata")
    add(f"- Nodes: {stats['node_count']} | Edges: {stats['edge_count']}")
    add(f"- Roles: {stats['nodes_by_kind'].get('role', 0)}")
    add(f"- Playbooks: {stats['nodes_by_kind'].get('playbook', 0)}")
    add(f"- Diagnostics: {diags.counts()}")
    if g.context_integration and g.context_integration.existing_context_map:
        add(f"- Existing context authority preserved: {g.context_integration.existing_context_map} "
            "(generated artifacts registered as derived)")

    # --- entry playbooks ---
    playbooks = sorted((n for n in nodes.values() if n.kind == "playbook"),
                       key=lambda n: n.source.path if n.source else n.name)
    section("Entry playbooks")
    _bounded_list(add, diags,
                  [f"- `{n.source.path if n.source else n.name}`" for n in playbooks],
                  cfg.map_max_entry_playbooks, "playbook",
                  "ansible-repo-intelligence query --kind playbook")

    # --- inventory overview ---
    flavors = sorted((n for n in nodes.values() if n.kind == "inventory_flavor"), key=lambda n: n.name)
    if flavors:
        section("Inventory scopes (flavors / environments)")
        for n in flavors:
            envs = ", ".join(n.attributes.get("environments", []))
            vdirs = ", ".join(n.attributes.get("var_dirs", []))
            add(f"- **{n.name}** — environments: {envs or 'default'}"
                + (f"; var dirs: {vdirs}" if vdirs else ""))

    # --- role catalogue ---
    roles = sorted((n for n in nodes.values() if n.kind == "role"), key=lambda n: n.name)
    section("Role catalogue")
    _bounded_list(add, diags, [f"- `{n.name}`" for n in roles],
                  cfg.map_max_roles, "role",
                  "ansible-repo-intelligence query role --limit 200")

    # --- role dependencies ---
    dep_edges = sorted((e for e in g.edges.values() if e.type == "depends_on"),
                       key=lambda e: (e.from_id, e.to_id))
    if dep_edges:
        section("Role dependencies")
        for e in dep_edges[:cfg.map_max_execution_paths]:
            add(f"- `{e.from_id.split(':',1)[1]}` → `{e.to_id.split(':',1)[1]}`")

    # --- key handlers ---
    handlers = sorted((n for n in nodes.values() if n.kind == "handler"), key=lambda n: n.name)
    if handlers:
        section("Key handlers")
        _bounded_list(add, diags, [f"- `{n.name}` ({n.source.path})" for n in handlers[:60]],
                      60, "handler", 'ansible-repo-intelligence query handler "<name>"')

    # --- high-impact templates ---
    templates = sorted((n for n in nodes.values()
                        if n.kind == "template" and n.significance in (Significance.CRITICAL, Significance.HIGH)),
                       key=lambda n: n.source.path if n.source else n.name)
    if templates:
        section("High-impact templates")
        _bounded_list(add, diags, [f"- `{n.source.path}`" for n in templates],
                      50, "template", "ansible-repo-intelligence query --kind template")

    # --- critical / high tasks ---
    crit = sorted((n for n in nodes.values()
                   if n.kind == "task" and n.significance is Significance.CRITICAL),
                  key=lambda n: n.source.path if n.source else n.name)
    if crit:
        section("Critical operations (review carefully)")
        _bounded_list(add, diags,
                      [f"- `{n.name}` — {n.source.path}:{n.source.line_start or '?'} "
                       f"[{n.attributes.get('module','?')}]" for n in crit],
                      cfg.map_max_execution_paths, "critical-task",
                      "ansible-repo-intelligence query --significance critical")

    # --- custom plugins & modules ---
    vps = sorted((n for n in nodes.values() if n.kind == "vars_plugin"), key=lambda n: n.name)
    if vps:
        section("Custom vars plugins (dynamic variable sources)")
        for n in vps:
            add(f"- `{n.source.path}` — supplies variables at inventory load "
                "(**dynamic**, not statically resolvable)")

    plugin_kinds = ("callback_plugin", "filter_plugin", "lookup_plugin",
                    "action_plugin", "module", "module_utils")
    plugins = sorted((n for n in nodes.values() if n.kind in plugin_kinds),
                     key=lambda n: (n.kind, n.source.path if n.source else n.name))
    if plugins:
        section("Custom plugins & modules")
        for n in plugins:
            enabled = n.attributes.get("enabled_in_ansible_cfg")
            flag = ""
            if n.kind == "callback_plugin":
                flag = " — **enabled in ansible.cfg**" if enabled else " (present, not enabled)"
            add(f"- `{n.source.path}` [{n.kind}]{flag} (**dynamic** — runtime behaviour)")

    # --- dynamic / unresolved ---
    dyn = [d for d in diags.sorted_items()
           if d.code.startswith(("ARI001", "ARI002", "ARI003"))]
    if dyn:
        section("Dynamic & unresolved references")
        _bounded_list(add, diags,
                      [f"- `{d.code}` {d.message}" + (f" ({d.path})" if d.path else "") for d in dyn],
                      cfg.map_max_diagnostics, "diagnostic",
                      "read diagnostics.yaml")

    # --- retrieval guidance ---
    section("Retrieval guidance")
    add("1. Start here, not in `graph.yaml`.")
    add("2. Run a bounded query: `ansible-repo-intelligence query <kind> <name>`.")
    add("3. Open only the 3–10 source files the query points to.")
    add("4. Verify every important claim against source. Never treat this map as source.")
    add("5. Do not load `graph.yaml` in full unless doing a repository-wide audit.")

    # --- enforce hard line budget ---
    if len(out) > cfg.map_max_lines:
        kept = out[: cfg.map_max_lines - 3]
        omitted = len(out) - len(kept)
        kept.append("")
        kept.append(f"> _{omitted} additional line(s) omitted to honour the "
                    f"{cfg.map_max_lines}-line budget. Query `graph.yaml` for the rest._")
        diags.warning(ARI021_MAP_SECTION_TRUNCATED,
                      f"repository map truncated to {cfg.map_max_lines} lines ({omitted} omitted)")
        out = kept
    return "\n".join(out) + "\n"


def _bounded_list(add, diags, items: list[str], limit: int, kind: str, query_hint: str) -> None:
    shown = items[:limit]
    for it in shown:
        add(it)
    if len(items) > limit:
        omitted = len(items) - limit
        add("")
        add(f"_{omitted} additional {kind}(s) omitted from this view. Retrieve with:_")
        add(f"`{query_hint}`")
        diags.info(ARI021_MAP_SECTION_TRUNCATED,
                   f"{kind} section truncated: {omitted} omitted", section=kind)
