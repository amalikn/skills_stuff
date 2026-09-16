"""Static parsing of playbooks, plays, roles and tasks into raw records.

This module extracts structure only. It does not resolve cross-file
relationships (that is ``resolver.py``) nor build the final graph
(``graph.py``). It records source provenance and a resolution hint for each
record. Task recursion descends into ``block``/``rescue``/``always``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .hashing import hash_region
from .models import Confidence, Resolution, ResolutionStatus, SourceRef
from .yaml_loader import LoadedFile, load_yaml_file, node_line

# Keys that introduce reusable content / delegation we care about.
INCLUDE_KEYS = {
    "include_tasks": "include_tasks",
    "import_tasks": "import_tasks",
    "ansible.builtin.include_tasks": "include_tasks",
    "ansible.builtin.import_tasks": "import_tasks",
    "include_role": "include_role",
    "import_role": "import_role",
    "ansible.builtin.include_role": "include_role",
    "ansible.builtin.import_role": "import_role",
    "include_vars": "include_vars",
    "ansible.builtin.include_vars": "include_vars",
    "include": "include_tasks",  # legacy
}

# Task directive keys (not modules).
TASK_DIRECTIVES = {
    "name", "when", "tags", "notify", "register", "loop", "with_items",
    "loop_control", "become", "become_user", "delegate_to", "delegate_facts",
    "run_once", "environment", "vars", "block", "rescue", "always",
    "changed_when", "failed_when", "check_mode", "retries", "delay", "until",
    "ignore_errors", "no_log", "listen", "args",
}
# Note: `set_fact` is a MODULE, not a directive — it must be discoverable as the
# task's module so it is labelled/extracted correctly.
WITH_PREFIX = "with_"


@dataclass
class TaskRecord:
    id: str
    name: str
    module: str
    role: str | None
    source: SourceRef
    resolution: Resolution
    notify: list[str] = field(default_factory=list)
    register: str | None = None
    set_facts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    when: list[str] = field(default_factory=list)
    loop: bool = False
    delegate_to: str | None = None
    become: bool = False
    include: dict[str, Any] | None = None  # {kind, target, dynamic}
    module_key: str = ""              # raw key, e.g. "ansible.builtin.command"
    module_args: Any = None           # value under the module key (dict|str|list)
    args: dict[str, Any] = field(default_factory=dict)
    in_block: bool = False


@dataclass
class PlayRecord:
    id: str
    name: str
    hosts: str
    source: SourceRef
    roles: list[str] = field(default_factory=list)
    import_playbooks: list[str] = field(default_factory=list)
    vars_keys: list[str] = field(default_factory=list)
    vars_files: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybookRecord:
    id: str
    path: str
    source: SourceRef
    plays: list[PlayRecord] = field(default_factory=list)


@dataclass
class ParseResult:
    playbooks: list[PlaybookRecord] = field(default_factory=list)
    tasks: list[TaskRecord] = field(default_factory=list)
    load_errors: list[tuple[str, str]] = field(default_factory=list)  # (path, err)
    vault_files: list[str] = field(default_factory=list)


_STATIC = Resolution(ResolutionStatus.RESOLVED, Confidence.HIGH, "Static declaration")


def _src(loaded: LoadedFile, obj: Any, document: int) -> SourceRef:
    line = node_line(obj)
    return SourceRef(
        path=loaded.path,
        document=document,
        line_start=line,
        line_end=line,
        content_hash=hash_region(loaded.lines, line, line) if line else loaded.content_hash,
    )


def parse_playbook(abs_path: Path, rel_path: str, max_bytes: int) -> tuple[PlaybookRecord | None, list[TaskRecord], LoadedFile]:
    loaded = load_yaml_file(abs_path, rel_path, max_bytes)
    if not loaded.ok or loaded.is_vault_file:
        return None, [], loaded

    pb = PlaybookRecord(
        id=f"playbook:{rel_path}",
        path=rel_path,
        source=SourceRef(path=rel_path, document=0, content_hash=loaded.content_hash),
    )
    tasks: list[TaskRecord] = []
    for doc_idx, doc in enumerate(loaded.documents):
        if not isinstance(doc, list):
            continue
        for play_idx, play in enumerate(doc):
            if not isinstance(play, dict):
                continue
            play_rec, play_tasks = _parse_play(loaded, doc_idx, play_idx, play)
            pb.plays.append(play_rec)
            tasks.extend(play_tasks)
    return pb, tasks, loaded


def _parse_play(loaded: LoadedFile, doc_idx: int, play_idx: int, play: dict) -> tuple[PlayRecord, list[TaskRecord]]:
    pid = f"play:{loaded.path}:{doc_idx}:{play_idx}"
    src = _src(loaded, play, doc_idx)

    if "import_playbook" in play or "ansible.builtin.import_playbook" in play:
        target = play.get("import_playbook") or play.get("ansible.builtin.import_playbook")
        rec = PlayRecord(id=pid, name=f"import_playbook {target}", hosts="", source=src)
        rec.import_playbooks.append(str(target))
        return rec, []

    hosts = _stringify(play.get("hosts", ""))
    name = str(play.get("name") or f"play[{play_idx}] {hosts}")
    rec = PlayRecord(id=pid, name=name, hosts=hosts, source=src)

    for role in _play_roles(play):
        rec.roles.append(role)
    rec.vars_keys = sorted((play.get("vars") or {}).keys()) if isinstance(play.get("vars"), dict) else []
    vf = play.get("vars_files") or []
    rec.vars_files = [str(v) for v in vf] if isinstance(vf, list) else [str(vf)]
    for attr in ("gather_facts", "become", "serial", "strategy"):
        if attr in play:
            rec.attributes[attr] = _scalarize(play[attr])

    tasks: list[TaskRecord] = []
    counter = _Counter()
    for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
        block = play.get(section)
        if isinstance(block, list):
            for item in block:
                tasks.extend(_parse_task(loaded, doc_idx, item, role=None, counter=counter,
                                         in_block=False, section=section))
    return rec, tasks


def _parse_task(loaded, doc_idx, item, role, counter, in_block, section="tasks") -> list[TaskRecord]:
    if not isinstance(item, dict):
        return []
    out: list[TaskRecord] = []

    # block/rescue/always recursion
    if "block" in item:
        for sub_section in ("block", "rescue", "always"):
            sub = item.get(sub_section)
            if isinstance(sub, list):
                for sub_item in sub:
                    out.extend(_parse_task(loaded, doc_idx, sub_item, role, counter, True, section))
        return out

    idx = counter.next()
    tid = f"task:{loaded.path}:{doc_idx}:{idx}"
    src = _src(loaded, item, doc_idx)
    module = _module_of(item)
    name = str(item.get("name") or module or "unnamed")

    rec = TaskRecord(
        id=tid, name=name, module=module or "unknown", role=role,
        source=src, resolution=_STATIC, in_block=in_block,
    )
    rec.notify = _as_list(item.get("notify"))
    rec.register = item.get("register")
    rec.tags = _as_list(item.get("tags"))
    rec.when = _as_list(item.get("when"))
    rec.delegate_to = _stringify(item["delegate_to"]) if "delegate_to" in item else None
    rec.loop = any(k in item for k in ("loop",)) or any(k.startswith(WITH_PREFIX) for k in item)
    rec.become = bool(item.get("become", False)) if isinstance(item.get("become"), bool) else False
    # Capture the raw module key + args for deterministic managed-resource extraction.
    mkey = _module_key_of(item)
    if mkey is not None:
        rec.module_key = mkey
        rec.module_args = item.get(mkey)
    if module in ("set_fact", "ansible.builtin.set_fact") and isinstance(item.get(module), dict):
        rec.set_facts = sorted(item[module].keys())
    elif "set_fact" in item and isinstance(item["set_fact"], dict):
        rec.set_facts = sorted(item["set_fact"].keys())

    inc = _include_of(item)
    if inc is not None:
        rec.include = inc
        rec.resolution = (
            Resolution(ResolutionStatus.DYNAMIC, Confidence.HIGH,
                       "Include/role target is templated or variable-derived")
            if inc["dynamic"]
            else Resolution(ResolutionStatus.RESOLVED, Confidence.HIGH,
                            f"Static {inc['kind']} target")
        )
    out.append(rec)
    return out


def _play_roles(play: dict) -> list[str]:
    roles = play.get("roles")
    out: list[str] = []
    if isinstance(roles, list):
        for r in roles:
            if isinstance(r, str):
                out.append(r)
            elif isinstance(r, dict):
                rn = r.get("role") or r.get("name")
                if rn:
                    out.append(str(rn))
    return out


def _module_of(item: dict) -> str | None:
    for k in item:
        if k in TASK_DIRECTIVES or k.startswith(WITH_PREFIX):
            continue
        if k in INCLUDE_KEYS:
            return INCLUDE_KEYS[k]
        return k
    return None


def _module_key_of(item: dict) -> str | None:
    """Return the raw module key (e.g. 'ansible.builtin.command'), not normalized."""
    for k in item:
        if k in TASK_DIRECTIVES or k.startswith(WITH_PREFIX):
            continue
        return k
    return None


def _include_of(item: dict) -> dict[str, Any] | None:
    for k, kind in INCLUDE_KEYS.items():
        if k in item:
            val = item[k]
            target = ""
            if isinstance(val, str):
                target = val
            elif isinstance(val, dict):
                target = str(val.get("name") or val.get("file") or "")
            dynamic = "{{" in target or target == ""
            return {"kind": kind, "target": target, "dynamic": dynamic}
    return None


def _as_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(v) for v in val]
    return [str(val)]


def _stringify(val: Any) -> str:
    return "" if val is None else str(val)


def _scalarize(val: Any) -> Any:
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)


class _Counter:
    def __init__(self) -> None:
        self._n = -1

    def next(self) -> int:
        self._n += 1
        return self._n
