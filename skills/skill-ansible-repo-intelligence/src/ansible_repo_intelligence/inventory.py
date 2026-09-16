"""Static inventory parsing (offline default) with flavor/environment scoping.

By default the scanner is offline and does NOT execute ``ansible-inventory``
(inventory / vars plugins can execute code). Instead it statically inspects
inventory source files:

- INI-style: ``[group]`` / ``[group:children]`` headers and host lines
- YAML-style: top-level groups with ``hosts:`` / ``children:``

Every group/host node is namespaced by flavor + environment. Values that look
secret are never emitted. Running ``ansible-inventory`` is a separate opt-in
path (``run_inventory``) and clearly distinguished as parsed-output provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml import YAML

from .hashing import EncodingError, hash_bytes, normalize_text


@dataclass
class InventoryGroup:
    flavor: str
    environment: str
    name: str
    children: list[str] = field(default_factory=list)
    hosts: list[str] = field(default_factory=list)
    source_rel: str = ""
    content_hash: str = ""


@dataclass
class InventoryScan:
    groups: list[InventoryGroup] = field(default_factory=list)
    parsed_via_execution: bool = False  # True only when ansible-inventory ran

    def hosts(self) -> set[tuple]:
        out: set[tuple] = set()
        for g in self.groups:
            for h in g.hosts:
                out.add((g.flavor, g.environment, h))
        return out


def parse_inventory_source(
    abs_path: Path, rel_path: str, flavor: str, environment: str, max_bytes: int,
) -> list[InventoryGroup]:
    """Statically parse a single inventory source file (INI or YAML)."""
    try:
        raw = abs_path.read_bytes()
    except OSError:
        return []
    if len(raw) > max_bytes:
        return []
    try:
        text = normalize_text(raw)
    except EncodingError:
        return []
    content_hash = hash_bytes(raw)

    stripped = text.lstrip()
    if stripped.startswith(("all:", "---")) or _looks_yaml(text):
        groups = _parse_yaml_inventory(text, flavor, environment, rel_path, content_hash)
        if groups:
            return groups
    return _parse_ini_inventory(text, flavor, environment, rel_path, content_hash)


def _looks_yaml(text: str) -> bool:
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # INI group header vs yaml mapping key
        return not s.startswith("[")
    return False


def _parse_ini_inventory(text, flavor, environment, rel_path, content_hash) -> list[InventoryGroup]:
    groups: dict[str, InventoryGroup] = {}
    current = "ungrouped"
    mode = "hosts"
    groups[current] = InventoryGroup(flavor, environment, current, source_rel=rel_path, content_hash=content_hash)
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            header = line[1:-1]
            if ":" in header:
                name, sub = header.split(":", 1)
                mode = "children" if sub == "children" else "vars"
            else:
                name, mode = header, "hosts"
            current = name
            groups.setdefault(current, InventoryGroup(
                flavor, environment, current, source_rel=rel_path, content_hash=content_hash))
            continue
        g = groups[current]
        if mode == "children":
            g.children.append(line.split()[0])
        elif mode == "hosts":
            host = line.split()[0]
            if host:
                g.hosts.append(host)
        # vars mode: we intentionally do not record inventory var *values*.
    return [g for g in groups.values() if g.hosts or g.children or g.name != "ungrouped"]


def _parse_yaml_inventory(text, flavor, environment, rel_path, content_hash) -> list[InventoryGroup]:
    yaml = YAML(typ="safe", pure=True)
    try:
        data = yaml.load(text)
    except Exception:  # noqa: BLE001
        return []
    if not isinstance(data, dict):
        return []
    groups: list[InventoryGroup] = []

    def walk(name: str, body: dict) -> None:
        g = InventoryGroup(flavor, environment, name, source_rel=rel_path, content_hash=content_hash)
        if isinstance(body, dict):
            hosts = body.get("hosts")
            if isinstance(hosts, dict):
                g.hosts.extend(str(h) for h in hosts.keys())
            elif isinstance(hosts, list):
                g.hosts.extend(str(h) for h in hosts)
            children = body.get("children")
            if isinstance(children, dict):
                g.children.extend(children.keys())
                groups.append(g)
                for cname, cbody in children.items():
                    walk(str(cname), cbody or {})
                return
        groups.append(g)

    for top, body in data.items():
        walk(str(top), body or {})
    return groups
