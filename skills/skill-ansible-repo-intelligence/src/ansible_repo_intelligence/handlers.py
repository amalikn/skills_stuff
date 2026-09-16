"""Handler extraction and notify -> handler resolution support.

Parses role/play handler files into handler records capturing ``name`` and
``listen`` topics with source provenance. The actual notify->handler edge
construction happens in ``resolver.py`` using this index; duplicate names and
unresolved notifications are surfaced as diagnostics there.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .hashing import hash_region
from .models import SourceRef
from .yaml_loader import load_yaml_file, node_line


@dataclass
class HandlerRecord:
    id: str
    name: str
    role: str | None
    source: SourceRef
    listen: list[str] = field(default_factory=list)
    module: str = "unknown"


@dataclass
class HandlerIndex:
    handlers: list[HandlerRecord] = field(default_factory=list)
    # name -> list of handler ids (list because duplicates are possible)
    by_name: dict[str, list[str]] = field(default_factory=dict)
    by_listen: dict[str, list[str]] = field(default_factory=dict)
    # (role, name) -> ids, for role-scoped resolution preference
    by_role_name: dict[tuple, list[str]] = field(default_factory=dict)

    def add(self, h: HandlerRecord) -> None:
        self.handlers.append(h)
        self.by_name.setdefault(h.name, []).append(h.id)
        self.by_role_name.setdefault((h.role, h.name), []).append(h.id)
        for topic in h.listen:
            self.by_listen.setdefault(topic, []).append(h.id)


def parse_handlers(abs_path: Path, rel_path: str, role: str | None, max_bytes: int) -> list[HandlerRecord]:
    loaded = load_yaml_file(abs_path, rel_path, max_bytes)
    if not loaded.ok or loaded.is_vault_file:
        return []
    out: list[HandlerRecord] = []
    for doc_idx, doc in enumerate(loaded.documents):
        if not isinstance(doc, list):
            continue
        for h_idx, item in enumerate(doc):
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "")
            if not name:
                continue
            line = node_line(item)
            src = SourceRef(
                path=rel_path, document=doc_idx, line_start=line, line_end=line,
                content_hash=hash_region(loaded.lines, line, line) if line else loaded.content_hash,
            )
            listen = item.get("listen")
            listen_list = [str(x) for x in listen] if isinstance(listen, list) else ([str(listen)] if listen else [])
            module = _module_of(item)
            out.append(HandlerRecord(
                id=f"handler:{rel_path}:{doc_idx}:{h_idx}",
                name=name, role=role, source=src, listen=listen_list, module=module,
            ))
    return out


_DIRECTIVES = {"name", "listen", "when", "notify", "become", "vars", "tags"}


def _module_of(item: dict) -> str:
    for k in item:
        if k not in _DIRECTIVES:
            return k
    return "unknown"
