"""Cross-file relationship resolution: edges + resolution states.

Builds edges from parsed records + the handler index:

- ``notifies``: task -> handler (by exact name, then by ``listen`` topic)
- ``includes`` / ``imports``: task -> target task-file or role
- ``uses_role``: play -> role
- ``depends_on``: role -> role (meta/main.yml dependencies)
- ``uses_collection``: node -> collection (FQCN usage)

Every edge carries a resolution state. Unresolved / dynamic notifications and
includes are reported to the diagnostics sink by the caller.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .handlers import HandlerIndex
from .models import Confidence, Edge, Resolution, ResolutionStatus, SourceRef
from .parser import PlaybookRecord, TaskRecord


@dataclass
class ResolveResult:
    edges: list[Edge] = field(default_factory=list)
    unresolved_notifies: list[tuple] = field(default_factory=list)  # (task_id, name, src)
    dynamic_includes: list[tuple] = field(default_factory=list)     # (task_id, target, src)
    unresolved_includes: list[tuple] = field(default_factory=list)


_RESOLVED = Resolution(ResolutionStatus.RESOLVED, Confidence.HIGH, "Exact static match")
_AMBIG = Resolution(ResolutionStatus.PARTIALLY_RESOLVED, Confidence.MEDIUM,
                    "Multiple candidates match; runtime scope decides")
_UNRESOLVED = Resolution(ResolutionStatus.UNRESOLVED, Confidence.MEDIUM, "No matching target found")
_DYNAMIC = Resolution(ResolutionStatus.DYNAMIC, Confidence.HIGH, "Target is templated / runtime-derived")


def _edge_id(etype: str, frm: str, to: str, extra: str = "") -> str:
    h = hashlib.sha256(f"{etype}|{frm}|{to}|{extra}".encode()).hexdigest()[:16]
    return f"edge:{etype}:{h}"


def resolve_notifies(tasks: list[TaskRecord], hidx: HandlerIndex) -> ResolveResult:
    res = ResolveResult()
    for task in tasks:
        for topic in task.notify:
            if "{{" in topic:
                res.dynamic_includes.append((task.id, topic, task.source))
                continue
            # Prefer role-scoped handler, then global name, then listen topic.
            candidates = (
                hidx.by_role_name.get((task.role, topic))
                or hidx.by_name.get(topic)
                or hidx.by_listen.get(topic)
                or []
            )
            if not candidates:
                res.unresolved_notifies.append((task.id, topic, task.source))
                continue
            resolution = _RESOLVED if len(candidates) == 1 else _AMBIG
            for hid in candidates:
                res.edges.append(Edge(
                    id=_edge_id("notifies", task.id, hid, topic),
                    type="notifies", from_id=task.id, to_id=hid,
                    resolution=resolution, source=task.source,
                    attributes={"notification": topic},
                ))
    return res


def resolve_includes(tasks: list[TaskRecord], task_file_ids: dict[str, str], role_names: set[str]) -> ResolveResult:
    """Resolve include/import task-file and role targets.

    ``task_file_ids`` maps a repository-relative task-file path to a node id.
    """
    res = ResolveResult()
    for task in tasks:
        inc = task.include
        if inc is None:
            continue
        kind, target, dynamic = inc["kind"], inc["target"], inc["dynamic"]
        if dynamic:
            res.dynamic_includes.append((task.id, target or "<computed>", task.source))
            res.edges.append(Edge(
                id=_edge_id(kind, task.id, "dynamic", target),
                type=kind, from_id=task.id, to_id=f"unresolved:{kind}",
                resolution=_DYNAMIC, source=task.source,
                attributes={"target_expression": target or "<computed>"},
            ))
            continue
        if kind in ("include_role", "import_role"):
            if target in role_names:
                res.edges.append(Edge(
                    id=_edge_id(kind, task.id, f"role:{target}", target),
                    type=kind, from_id=task.id, to_id=f"role:{target}",
                    resolution=_RESOLVED, source=task.source, attributes={"role": target},
                ))
            else:
                res.unresolved_includes.append((task.id, target, task.source))
        else:  # include_tasks / import_tasks
            tid = _match_task_file(task, target, task_file_ids)
            if tid:
                res.edges.append(Edge(
                    id=_edge_id(kind, task.id, tid, target),
                    type=kind, from_id=task.id, to_id=tid,
                    resolution=_RESOLVED, source=task.source, attributes={"target": target},
                ))
            else:
                res.unresolved_includes.append((task.id, target, task.source))
    return res


def resolve_play_roles(playbooks: list[PlaybookRecord], role_names: set[str]) -> ResolveResult:
    res = ResolveResult()
    for pb in playbooks:
        for play in pb.plays:
            for role in play.roles:
                to = f"role:{role}"
                resolution = _RESOLVED if role in role_names else _UNRESOLVED
                res.edges.append(Edge(
                    id=_edge_id("uses_role", play.id, to, role),
                    type="uses_role", from_id=play.id, to_id=to,
                    resolution=resolution, source=play.source, attributes={"role": role},
                ))
            for imp in play.import_playbooks:
                res.edges.append(Edge(
                    id=_edge_id("import_playbook", play.id, imp, imp),
                    type="import_playbook", from_id=play.id, to_id=f"playbook:{imp}",
                    resolution=Resolution(
                        ResolutionStatus.RESOLVED if "{{" not in imp else ResolutionStatus.DYNAMIC,
                        Confidence.HIGH,
                        "Static import_playbook" if "{{" not in imp else "Templated playbook path",
                    ),
                    source=play.source, attributes={"target": imp},
                ))
    return res


def resolve_role_dependencies(role_deps: dict[str, list[str]], role_names: set[str]) -> ResolveResult:
    res = ResolveResult()
    for role, deps in sorted(role_deps.items()):
        for dep in deps:
            to = f"role:{dep}"
            resolution = _RESOLVED if dep in role_names else _UNRESOLVED
            res.edges.append(Edge(
                id=_edge_id("depends_on", f"role:{role}", to, dep),
                type="depends_on", from_id=f"role:{role}", to_id=to,
                resolution=resolution, source=SourceRef(path=f"roles/{role}/meta/main.yml"),
                attributes={"dependency": dep},
            ))
    return res


def _match_task_file(task: TaskRecord, target: str, task_file_ids: dict[str, str]) -> str | None:
    """Match an include target to a known task-file node id.

    Role-relative includes resolve against ``roles/<role>/tasks/<target>``.
    Absolute-ish repo-relative targets match directly.
    """
    if target in task_file_ids:
        return task_file_ids[target]
    if task.role:
        cand = f"{_role_root(task)}/tasks/{target}"
        if cand in task_file_ids:
            return task_file_ids[cand]
    # Suffix match as a fallback (deterministic: first sorted match).
    for path in sorted(task_file_ids):
        if path.endswith("/" + target):
            return task_file_ids[path]
    return None


def _role_root(task: TaskRecord) -> str:
    # Derive role root from the task's own source path when possible.
    parts = task.source.path.split("/")
    if "tasks" in parts:
        return "/".join(parts[: parts.index("tasks")])
    return f"roles/{task.role}"
