"""Custom vars-plugin discovery and dynamic-source modelling.

Custom vars plugins execute during inventory loading and are NOT statically
resolvable. This module never executes plugin code. It uses Python's ``ast``
module to extract *safe metadata only*:

- plugin class name(s)
- documented / literal variable prefixes (e.g. ``topology_``)
- literal variable keys assigned into the returned vars dict where evident
- data directories the plugin appears to consume (e.g. ``topology_vars``)

Everything a vars plugin may supply is represented with::

    resolution:
      status: dynamic
      confidence: high
      reason: Custom vars plugin executes during inventory loading and is not
              statically resolvable

When no literal name/namespace can be identified, an unresolved dynamic
namespace marker is emitted rather than inventing concrete variables.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from .hashing import hash_bytes


@dataclass
class VarsPluginInfo:
    rel_path: str
    content_hash: str
    class_names: list[str] = field(default_factory=list)
    variable_prefixes: list[str] = field(default_factory=list)
    literal_var_keys: list[str] = field(default_factory=list)
    consumed_dirs: list[str] = field(default_factory=list)
    parse_ok: bool = True
    parse_error: str | None = None


# Directory names commonly consumed by vars plugins (data dirs, not code).
_DATA_DIR_HINTS = ("topology_vars", "host_vars", "group_vars", "vars")


def analyze_vars_plugin(abs_path: Path, rel_path: str) -> VarsPluginInfo:
    """Statically analyze a vars-plugin ``.py`` file. Never executes it."""
    try:
        raw = abs_path.read_bytes()
    except OSError as exc:
        return VarsPluginInfo(rel_path, "", parse_ok=False, parse_error=str(exc))

    content_hash = hash_bytes(raw)
    info = VarsPluginInfo(rel_path=rel_path, content_hash=content_hash)

    try:
        tree = ast.parse(raw)
    except SyntaxError as exc:
        info.parse_ok = False
        info.parse_error = f"syntax error: {exc}"
        return info

    prefixes: set[str] = set()
    keys: set[str] = set()
    consumed: set[str] = set()

    for node in ast.walk(tree):
        # Plugin classes (usually subclass BaseVarsPlugin).
        if isinstance(node, ast.ClassDef):
            info.class_names.append(node.name)

        # String constants: detect variable-name prefixes and data dir hints.
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            for hint in _DATA_DIR_HINTS:
                if hint in s:
                    consumed.add(hint)
            # A literal ending in '_' that looks like a namespace prefix.
            if s.endswith("_") and s.replace("_", "").isalnum() and 3 <= len(s) <= 40:
                prefixes.add(s)

        # Dict subscript assignments: result['topology_interfaces'] = ...
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if isinstance(node.slice.value, str) and _looks_like_var(node.slice.value):
                keys.add(node.slice.value)

        # f-strings building var names: f"{prefix}foo" — capture literal parts.
        if isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    p = part.value
                    if p.endswith("_") and p.replace("_", "").isalnum():
                        prefixes.add(p)

    info.variable_prefixes = sorted(prefixes)
    info.literal_var_keys = sorted(keys)
    info.consumed_dirs = sorted(consumed)
    return info


def _looks_like_var(s: str) -> bool:
    return bool(s) and s[0].isalpha() and all(c.isalnum() or c == "_" for c in s) and "_" in s
