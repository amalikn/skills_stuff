"""Canonical graph assembly: turns analyzer output into nodes + edges + topics.

This is the orchestrator for the static model. It owns the node/edge collections
and their deterministic serialization. It does not perform bounded traversal
(Phase 2 ``traversal.py``) nor render the map (``renderer.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import SCHEMA_VERSION
from .ansible_config import AnsibleConfig
from .app_config import AppConfig
from .collections import CollectionInfo, CollectionOrigin
from .diagnostics import (
    ARI002_DYNAMIC_INCLUDE, ARI001_UNRESOLVED_STATIC_INCLUDE,
    ARI003_UNRESOLVED_HANDLER, ARI004_DUPLICATE_HANDLER_NAME,
    ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT, ARI007_EXTERNAL_SYMLINK_BLOCKED,
    ARI015_VENDORED_COLLECTION_EXCLUDED, ARI016_COLLECTION_ORIGIN_UNKNOWN,
    ARI017_CUSTOM_VARS_PLUGIN_DYNAMIC, ARI019_INVENTORY_FLAVOR_COLLISION,
    ARI020_CONTEXT_AUTHORITY_CONFLICT, ARI022_INVENTORY_BACKUP_EXCLUDED,
    ARI023_YAML_PARSE_ERROR, ARI024_GENERATED_CACHE_EXCLUDED, Diagnostics,
)
from .discovery import Discovery, FileKind
from .handlers import HandlerIndex, HandlerRecord, parse_handlers
from .inventory import parse_inventory_source
from .inventory_flavors import (
    FlavorLayout, discover_flavors, namespaced_group_id, namespaced_host_id,
)
from .context_integration import ContextIntegration, integrate_context
from .models import (
    Confidence, Edge, Node, Resolution, ResolutionStatus, Significance, SourceRef,
)
from .parser import PlaybookRecord, TaskRecord, parse_playbook
from .resolver import (
    resolve_includes, resolve_notifies, resolve_play_roles, resolve_role_dependencies,
)
from .actions import extract_action
from .significance import SignificanceEngine
from .templates import analyze_template
from .variables import (
    PrecedenceConfig, VariableIndex, add_definitions, collect_yaml_vars, compute_conflicts,
    is_secret_name,
)
from .vars_plugins import analyze_vars_plugin
from .yaml_loader import load_yaml_file

_DYNAMIC_VP = Resolution(
    ResolutionStatus.DYNAMIC, Confidence.HIGH,
    "Custom vars plugin executes during inventory loading and is not statically resolvable",
)
_STATIC = Resolution(ResolutionStatus.RESOLVED, Confidence.HIGH, "Static declaration")


@dataclass
class Graph:
    schema_version: str = SCHEMA_VERSION
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)
    retrieval_topics: dict[str, dict] = field(default_factory=dict)
    flavor_layout: FlavorLayout | None = None
    context_integration: ContextIntegration | None = None

    def add_node(self, node: Node) -> None:
        self.nodes.setdefault(node.id, node)

    def add_edge(self, edge: Edge) -> None:
        self.edges.setdefault(edge.id, edge)

    def statistics(self) -> dict:
        kinds: dict[str, int] = {}
        for n in self.nodes.values():
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
        etypes: dict[str, int] = {}
        for e in self.edges.values():
            etypes[e.type] = etypes.get(e.type, 0) + 1
        sig: dict[str, int] = {}
        for n in self.nodes.values():
            sig[n.significance.value] = sig.get(n.significance.value, 0) + 1
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes_by_kind": dict(sorted(kinds.items())),
            "edges_by_type": dict(sorted(etypes.items())),
            "nodes_by_significance": dict(sorted(sig.items())),
            "retrieval_topic_count": len(self.retrieval_topics),
        }


def build_graph(
    cfg: AppConfig, acfg: AnsibleConfig, disc: Discovery, sig: SignificanceEngine,
    pcfg: PrecedenceConfig, diags: Diagnostics,
) -> Graph:
    repo = cfg.repo.resolve()
    g = Graph()

    # --- context authority integration (read-only) -------------------------
    g.context_integration = integrate_context(repo, cfg.output)
    if g.context_integration.conflict:
        diags.warning(ARI020_CONTEXT_AUTHORITY_CONFLICT,
                      g.context_integration.conflict_reason or "context authority conflict")

    # --- symlink escapes & excluded backups --------------------------------
    for esc in disc.symlink_escapes:
        diags.info(ARI007_EXTERNAL_SYMLINK_BLOCKED,
                   f"Symlink resolves outside repository: {esc}", path=esc)
    if disc.excluded_backup_count:
        diags.info(ARI022_INVENTORY_BACKUP_EXCLUDED,
                   f"Excluded {disc.excluded_backup_count} inventory backup/archive file(s)")
    if disc.vendored_yaml_count:
        diags.info(ARI015_VENDORED_COLLECTION_EXCLUDED,
                   f"Excluded {disc.vendored_yaml_count} vendored collection YAML file(s) "
                   "from first-class indexing; FQCN usage still tracked")

    # --- role nodes --------------------------------------------------------
    for role in disc.roles:
        g.add_node(Node(
            id=f"role:{role}", kind="role", name=role, significance=Significance.NORMAL,
            resolution=_STATIC, source=SourceRef(path=disc.role_paths.get(role, f"roles/{role}")),
        ))

    # --- collections (FQCN prefixes) ---------------------------------------
    _add_collection_nodes(g, disc.collections, diags)

    # --- playbooks, plays, tasks -------------------------------------------
    all_tasks: list[TaskRecord] = []
    playbooks: list[PlaybookRecord] = []
    task_file_ids: dict[str, str] = {}

    for f in disc.by_kind(FileKind.PLAYBOOK):
        pb, tasks, loaded = parse_playbook(repo / f.rel_path, f.rel_path, cfg.max_file_bytes)
        if not loaded.ok:
            diags.warning(ARI023_YAML_PARSE_ERROR, loaded.error or "parse error", path=f.rel_path)
            continue
        if pb is None:
            continue
        playbooks.append(pb)
        all_tasks.extend(tasks)
        _add_playbook_nodes(g, pb, sig)

    # role task files
    for f in disc.by_kind(FileKind.ROLE_TASKS):
        task_file_ids[f.rel_path] = f"taskfile:{f.rel_path}"
        pb, tasks, loaded = parse_playbook_tasks(repo / f.rel_path, f.rel_path, f.role, cfg.max_file_bytes)
        if not loaded.ok:
            diags.warning(ARI023_YAML_PARSE_ERROR, loaded.error or "parse error", path=f.rel_path)
            continue
        all_tasks.extend(tasks)
        g.add_node(Node(
            id=f"taskfile:{f.rel_path}", kind="task_file", name=f.rel_path,
            significance=Significance.NORMAL, resolution=_STATIC,
            source=SourceRef(path=f.rel_path, content_hash=loaded.content_hash),
            attributes={"role": f.role} if f.role else {},
        ))

    _add_task_nodes(g, all_tasks, sig)

    # --- handlers ----------------------------------------------------------
    hidx = _build_handler_index(g, disc, repo, cfg, diags)

    # --- edges: notifies, includes, roles, deps ----------------------------
    role_names = set(disc.roles)
    nres = resolve_notifies(all_tasks, hidx)
    for e in nres.edges:
        _add_edge_if_endpoints(g, e)
    for tid, topic, src in nres.unresolved_notifies:
        diags.warning(ARI003_UNRESOLVED_HANDLER,
                      f"notify '{topic}' has no matching handler", path=src.path, node_id=tid)

    ires = resolve_includes(all_tasks, task_file_ids, role_names)
    for e in ires.edges:
        _add_edge_relaxed(g, e)
    for tid, target, src in ires.dynamic_includes:
        diags.info(ARI002_DYNAMIC_INCLUDE,
                   f"dynamic include/notify target: {target}", path=src.path, node_id=tid)
    for tid, target, src in ires.unresolved_includes:
        diags.warning(ARI001_UNRESOLVED_STATIC_INCLUDE,
                      f"unresolved static include target: {target}", path=src.path, node_id=tid)

    pres = resolve_play_roles(playbooks, role_names)
    for e in pres.edges:
        _add_edge_relaxed(g, e)

    role_deps = _collect_role_deps(disc, repo, cfg)
    dres = resolve_role_dependencies(role_deps, role_names)
    for e in dres.edges:
        _add_edge_relaxed(g, e)

    # --- variables ---------------------------------------------------------
    vindex = _collect_variables(disc, repo, cfg, diags)
    compute_conflicts(vindex, pcfg)
    _add_variable_nodes(g, vindex)
    for conflict in vindex.conflicts:
        conf = "low" if conflict.runtime_only else "medium"
        diags.warning(ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT,
                      f"variable '{conflict.name}': {conflict.reason} (confidence {conf})",
                      variable=conflict.name, classes=conflict.classes, scopes=conflict.scopes)

    # --- custom vars plugins (dynamic sources) -----------------------------
    _add_vars_plugin_nodes(g, disc, repo, diags)

    # --- other custom plugins & modules (callback/filter/lookup/action/module) --
    _add_plugin_nodes(g, disc, acfg)

    # --- templates ---------------------------------------------------------
    _add_template_nodes(g, disc, repo, cfg, acfg)

    # --- inventory (offline static) + flavors ------------------------------
    _add_inventory(g, cfg, repo, disc, diags)

    # --- retrieval topics --------------------------------------------------
    g.retrieval_topics = _build_retrieval_topics(g, disc)

    return g


# --------------------------------------------------------------------------
# node builders
# --------------------------------------------------------------------------

def _add_playbook_nodes(g: Graph, pb: PlaybookRecord, sig: SignificanceEngine) -> None:
    g.add_node(Node(id=pb.id, kind="playbook", name=Path(pb.path).name,
                    significance=Significance.HIGH, resolution=_STATIC, source=pb.source))
    for play in pb.plays:
        g.add_node(Node(id=play.id, kind="play", name=play.name,
                        significance=Significance.NORMAL, resolution=_STATIC,
                        source=play.source,
                        attributes={"hosts": play.hosts, **play.attributes}))


def _add_task_nodes(g: Graph, tasks: list[TaskRecord], sig: SignificanceEngine) -> None:
    for t in tasks:
        text = _action_text(t) + "\n" + t.name
        significance, rule_id = sig.classify(t.module, text)
        attrs: dict = {}
        if t.tags:
            attrs["tags"] = sorted(set(t.tags))
        if t.notify:
            attrs["notify"] = t.notify
        if t.register:
            attrs["register"] = t.register
        if t.set_facts:
            attrs["set_fact"] = t.set_facts
        if t.when:
            attrs["when"] = t.when
        if t.loop:
            attrs["loop"] = True
        if t.delegate_to:
            attrs["delegate_to"] = t.delegate_to
        if t.become:
            attrs["become"] = True
        if t.role:
            attrs["role"] = t.role
        attrs["module"] = t.module
        # Deterministic managed-resource enrichment (Phase 1): a compact fact
        # record so a bounded query is a sufficient, source-traceable answer.
        if t.include is None and t.module_key:
            action = extract_action(
                t.module_key, t.module, t.module_args, t.when,
                is_critical=significance is Significance.CRITICAL,
            )
            if action is not None:
                attrs.update(action.to_attrs())
        g.add_node(Node(
            id=t.id, kind="task", name=t.name, significance=significance,
            resolution=t.resolution, source=t.source,
            significance_rule_id=rule_id, attributes=attrs,
        ))


def _action_text(t: TaskRecord) -> str:
    """Searchable text for significance classification from the raw module args."""
    parts = [t.module or ""]
    a = t.module_args
    if isinstance(a, str):
        parts.append(a)
    elif isinstance(a, dict):
        for k in ("name", "dest", "path", "src", "cmd", "command", "job", "url"):
            v = a.get(k)
            if isinstance(v, str):
                parts.append(v)
    return "\n".join(parts)


def _build_handler_index(g, disc, repo, cfg, diags) -> HandlerIndex:
    hidx = HandlerIndex()
    for f in disc.by_kind(FileKind.ROLE_HANDLERS):
        for h in parse_handlers(repo / f.rel_path, f.rel_path, f.role, cfg.max_file_bytes):
            hidx.add(h)
    # play-level handlers already parsed as tasks in section 'handlers' -> also
    # index any handler-kind names by treating them as handler records is skipped
    # here to avoid double counting; role handlers are the common case.
    for h in hidx.handlers:
        g.add_node(Node(
            id=h.id, kind="handler", name=h.name, significance=Significance.HIGH,
            resolution=_STATIC, source=h.source,
            attributes={"listen": h.listen, "role": h.role, "module": h.module}
            if (h.listen or h.role) else {"module": h.module},
        ))
    # duplicate handler names within same role scope
    for (role, name), ids in hidx.by_role_name.items():
        if len(ids) > 1:
            diags.warning(ARI004_DUPLICATE_HANDLER_NAME,
                          f"duplicate handler name '{name}'"
                          + (f" in role {role}" if role else ""),
                          details_ids=ids)
    return hidx


def _add_collection_nodes(g, collections: list[CollectionInfo], diags) -> None:
    for c in collections:
        g.add_node(Node(
            id=f"collection:{c.fqcn_prefix}", kind="collection", name=c.fqcn_prefix,
            significance=Significance.NORMAL, resolution=_STATIC,
            source=SourceRef(path=c.root),
            attributes={"origin": c.origin.value, "version": c.version or "unknown"},
        ))
        if c.origin is CollectionOrigin.UNKNOWN_ORIGIN:
            diags.warning(ARI016_COLLECTION_ORIGIN_UNKNOWN,
                          f"collection '{c.fqcn_prefix}' has unknown origin", path=c.root)


def _add_variable_nodes(g, vindex: VariableIndex) -> None:
    # One node per (name, class, scope) definition, deterministic id.
    seen: set[str] = set()
    for i, d in enumerate(sorted(vindex.definitions, key=lambda x: (x.name, x.precedence_class, x.scope))):
        vid = f"variable:{d.name}:{d.source.path}:{d.precedence_class}"
        if vid in seen:
            continue
        seen.add(vid)
        g.add_node(Node(
            id=vid, kind="variable", name=d.name, significance=Significance.LOW,
            resolution=_STATIC, source=d.source,
            attributes={"precedence_class": d.precedence_class, "scope": d.scope,
                        "sensitive_name": d.is_secret_name},
        ))


def _add_vars_plugin_nodes(g, disc, repo, diags) -> None:
    for f in disc.by_kind(FileKind.VARS_PLUGIN):
        info = analyze_vars_plugin(repo / f.rel_path, f.rel_path)
        pid = f"vars_plugin:{f.rel_path}"
        g.add_node(Node(
            id=pid, kind="vars_plugin", name=Path(f.rel_path).stem,
            significance=Significance.HIGH, resolution=_DYNAMIC_VP,
            source=SourceRef(path=f.rel_path, content_hash=info.content_hash),
            attributes={"classes": info.class_names, "consumed_dirs": info.consumed_dirs,
                        "variable_prefixes": info.variable_prefixes},
        ))
        diags.info(ARI017_CUSTOM_VARS_PLUGIN_DYNAMIC,
                   f"custom vars plugin '{f.rel_path}' supplies variables dynamically",
                   path=f.rel_path, node_id=pid)
        # Literal keys become dynamic variable-source nodes linked to the plugin.
        for key in info.literal_var_keys:
            vid = f"variable:{key}:{f.rel_path}:vars_plugin"
            g.add_node(Node(
                id=vid, kind="variable", name=key, significance=Significance.NORMAL,
                resolution=_DYNAMIC_VP,
                source=SourceRef(path=f.rel_path, content_hash=info.content_hash),
                attributes={"precedence_class": "unknown_runtime", "source_kind": "vars_plugin",
                            "plugin": f.rel_path},
            ))
            g.add_edge(Edge(
                id=f"edge:supplies:{_short(pid + vid)}", type="supplies",
                from_id=pid, to_id=vid, resolution=_DYNAMIC_VP,
                source=SourceRef(path=f.rel_path),
            ))
        if not info.literal_var_keys and info.variable_prefixes:
            # Unresolved dynamic namespace marker rather than inventing vars.
            for prefix in info.variable_prefixes:
                g.add_node(Node(
                    id=f"variable-namespace:{prefix}:{f.rel_path}", kind="variable_namespace",
                    name=prefix, significance=Significance.NORMAL,
                    resolution=Resolution(ResolutionStatus.UNRESOLVED, Confidence.MEDIUM,
                                          "Dynamic namespace supplied by vars plugin; concrete names unknown"),
                    source=SourceRef(path=f.rel_path, content_hash=info.content_hash),
                    attributes={"plugin": f.rel_path},
                ))


# Plugin FileKind -> (node kind, significance, runtime note)
_PLUGIN_KINDS = {
    FileKind.CALLBACK_PLUGIN: ("callback_plugin", Significance.HIGH,
                               "Callback plugin runs during play execution (runtime behaviour)"),
    FileKind.FILTER_PLUGIN: ("filter_plugin", Significance.NORMAL,
                             "Jinja filter plugin invoked at template render time (runtime)"),
    FileKind.LOOKUP_PLUGIN: ("lookup_plugin", Significance.HIGH,
                             "Lookup plugin executes at runtime and may access external systems"),
    FileKind.ACTION_PLUGIN: ("action_plugin", Significance.HIGH,
                             "Action plugin wraps module dispatch at runtime"),
    FileKind.MODULE: ("module", Significance.NORMAL,
                      "Custom module executed on the target host at runtime"),
    FileKind.MODULE_UTILS: ("module_utils", Significance.LOW,
                            "Shared module utility code"),
}


def _add_plugin_nodes(g, disc, acfg) -> None:
    """Emit first-class nodes for custom plugins and modules.

    These are static source files whose *effect* is at runtime, so they are
    marked ``dynamic`` (their behaviour is not statically resolvable). Callback
    plugins enabled in ``ansible.cfg`` (callbacks_enabled / callback_whitelist)
    are flagged ``enabled: true`` and linked to that configuration.
    """
    enabled_callbacks = {c.lower() for c in acfg.callback_plugins_enabled}
    for kind, (node_kind, significance, note) in _PLUGIN_KINDS.items():
        for f in disc.by_kind(kind):
            stem = Path(f.rel_path).stem
            attrs: dict = {}
            if f.role:
                attrs["role"] = f.role
            resolution = Resolution(
                ResolutionStatus.DYNAMIC, Confidence.HIGH, note,
            )
            if kind is FileKind.CALLBACK_PLUGIN:
                is_enabled = stem.lower() in enabled_callbacks
                attrs["enabled_in_ansible_cfg"] = is_enabled
                if is_enabled:
                    attrs["enablement"] = "callbacks_enabled/callback_whitelist"
            g.add_node(Node(
                id=f"{node_kind}:{f.rel_path}", kind=node_kind, name=stem,
                significance=significance, resolution=resolution,
                source=SourceRef(path=f.rel_path), attributes=attrs,
            ))


def _add_template_nodes(g, disc, repo, cfg, acfg) -> None:
    safe_ext = acfg.safe_jinja_extensions
    for f in disc.by_kind(FileKind.ROLE_TEMPLATE):
        if not (f.rel_path.endswith(".j2")):
            g.add_node(Node(
                id=f"template:{f.rel_path}", kind="template", name=Path(f.rel_path).name,
                significance=Significance.HIGH, resolution=_STATIC,
                source=SourceRef(path=f.rel_path),
            ))
            continue
        info = analyze_template(repo / f.rel_path, f.rel_path, safe_ext, cfg.max_file_bytes)
        g.add_node(Node(
            id=f"template:{f.rel_path}", kind="template", name=Path(f.rel_path).name,
            significance=Significance.HIGH,
            resolution=_STATIC if info.parse_ok else Resolution(
                ResolutionStatus.PARTIALLY_RESOLVED, Confidence.MEDIUM,
                info.parse_error or "template parse issue"),
            source=SourceRef(path=f.rel_path, content_hash=info.content_hash),
            attributes={"variables": info.variables, "role": f.role} if info.variables else {"role": f.role},
        ))


def _add_inventory(g, cfg, repo, disc, diags) -> None:
    # Detect extra var dirs from vars plugins to feed flavor discovery generically.
    extra_dirs: set[str] = set()
    for f in disc.by_kind(FileKind.VARS_PLUGIN):
        info = analyze_vars_plugin(repo / f.rel_path, f.rel_path)
        extra_dirs.update(info.consumed_dirs)

    layout = discover_flavors(cfg, repo, extra_var_dirs=extra_dirs)
    g.flavor_layout = layout
    for name in layout.collisions:
        diags.warning(ARI019_INVENTORY_FLAVOR_COLLISION,
                      f"inventory flavor name collision: {name}")

    for flavor in layout.flavors:
        g.add_node(Node(
            id=f"inventory-flavor:{flavor.name}", kind="inventory_flavor", name=flavor.name,
            significance=Significance.NORMAL, resolution=_STATIC,
            source=SourceRef(path=flavor.root_rel),
            attributes={"environments": [e.name for e in flavor.environments],
                        "var_dirs": sorted(flavor.var_dirs.keys())},
        ))
        if flavor.generated_cache:
            diags.info(ARI024_GENERATED_CACHE_EXCLUDED,
                       f"flavor '{flavor.name}': {len(flavor.generated_cache)} generated cache "
                       "file(s) treated as derived, not authored",
                       flavor=flavor.name)
        # offline static inventory parse per environment
        for env in flavor.environments:
            abs_src = repo / env.source_rel
            if not abs_src.is_file():
                continue
            for grp in parse_inventory_source(abs_src, env.source_rel, flavor.name, env.name, cfg.max_file_bytes):
                gid = namespaced_group_id(flavor.name, env.name, grp.name)
                g.add_node(Node(
                    id=gid, kind="inventory_group", name=grp.name, significance=Significance.NORMAL,
                    resolution=_STATIC, source=SourceRef(path=grp.source_rel, content_hash=grp.content_hash),
                    attributes={"flavor": flavor.name, "environment": env.name,
                                "host_count": len(grp.hosts), "children": grp.children},
                ))
                for host in grp.hosts:
                    hid = namespaced_host_id(flavor.name, env.name, host)
                    g.add_node(Node(
                        id=hid, kind="inventory_host", name=host, significance=Significance.LOW,
                        resolution=_STATIC, source=SourceRef(path=grp.source_rel),
                        attributes={"flavor": flavor.name, "environment": env.name},
                    ))
                    g.add_edge(Edge(
                        id=f"edge:member_of:{_short(hid + gid)}", type="member_of",
                        from_id=hid, to_id=gid, resolution=_STATIC,
                        source=SourceRef(path=grp.source_rel),
                    ))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _collect_variables(disc, repo, cfg, diags) -> VariableIndex:
    index = VariableIndex()
    kind_class = {
        FileKind.ROLE_DEFAULTS: ("role_default", "role"),
        FileKind.ROLE_VARS: ("role_var", "role"),
        FileKind.GROUP_VARS: ("inventory_group", "flavor"),
        FileKind.HOST_VARS: ("inventory_host", "flavor"),
    }
    for kind, (pclass, scope_kind) in kind_class.items():
        for f in disc.by_kind(kind):
            scope = _scope_for(f, scope_kind)
            add_definitions(index, collect_yaml_vars(
                repo / f.rel_path, f.rel_path, pclass, scope, cfg.secret_patterns, cfg.max_file_bytes))
    return index


def _scope_for(f, scope_kind: str) -> str:
    if scope_kind == "role" and f.role:
        return f"role:{f.role}"
    parts = f.rel_path.split("/")
    if parts and parts[0] == "inventories" and len(parts) > 1:
        return f"flavor:{parts[1]}"
    return f"path:{f.rel_path}"


def _collect_role_deps(disc, repo, cfg) -> dict[str, list[str]]:
    deps: dict[str, list[str]] = {}
    for f in disc.by_kind(FileKind.ROLE_META):
        if not f.role:
            continue
        loaded = load_yaml_file(repo / f.rel_path, f.rel_path, cfg.max_file_bytes)
        if not loaded.ok:
            continue
        for doc in loaded.documents:
            if isinstance(doc, dict) and isinstance(doc.get("dependencies"), list):
                for dep in doc["dependencies"]:
                    if isinstance(dep, str):
                        deps.setdefault(f.role, []).append(dep)
                    elif isinstance(dep, dict):
                        rn = dep.get("role") or dep.get("name")
                        if rn:
                            deps.setdefault(f.role, []).append(str(rn))
    return deps


def _build_retrieval_topics(g: Graph, disc: Discovery) -> dict[str, dict]:
    topics: dict[str, dict] = {}
    for role in disc.roles:
        rp = disc.role_paths.get(role, f"roles/{role}")
        source_paths = sorted(
            n.source.path for n in g.nodes.values()
            if n.source and n.source.path.startswith(rp + "/")
            and n.kind in ("task_file", "handler", "template")
        )
        primary = [f"role:{role}"]
        primary += [n.id for n in g.nodes.values()
                    if n.kind == "template" and n.source and n.source.path.startswith(rp + "/")][:5]
        topics[role] = {
            "summary": f"Role '{role}' tasks, handlers and templates",
            "primary_nodes": primary,
            "source_paths": source_paths[:20],
        }
    return dict(sorted(topics.items()))


def _add_edge_if_endpoints(g: Graph, e: Edge) -> None:
    if e.from_id in g.nodes and e.to_id in g.nodes:
        g.add_edge(e)


def _add_edge_relaxed(g: Graph, e: Edge) -> None:
    # Edges may point to declared-but-unbuilt targets (e.g. role: names that
    # are declarations). Keep them; validator flags truly invalid refs unless
    # the resolution is unresolved/dynamic.
    g.add_edge(e)


def _short(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()[:16]


# Parse a role task-file (list of tasks, no plays).
def parse_playbook_tasks(abs_path: Path, rel_path: str, role, max_bytes: int):
    from .parser import _Counter, _parse_task
    loaded = load_yaml_file(abs_path, rel_path, max_bytes)
    if not loaded.ok or loaded.is_vault_file:
        return None, [], loaded
    tasks: list[TaskRecord] = []
    for doc_idx, doc in enumerate(loaded.documents):
        if not isinstance(doc, list):
            continue
        counter = _Counter()
        for item in doc:
            tasks.extend(_parse_task(loaded, doc_idx, item, role=role, counter=counter, in_block=False))
    return None, tasks, loaded
