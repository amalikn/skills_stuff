"""Parse the *repository's* effective ``ansible.cfg`` and honour its settings.

Path resolution across the scanner must use the effective configured values
rather than assuming only ``./roles`` or default collection paths. Jinja
parsing must enable the same safe parse-time extensions declared in
``jinja2_extensions`` (e.g. ``jinja2.ext.do``, ``jinja2.ext.loopcontrols``).
Enabling an extension for *parsing* never permits rendering or code execution.

This module only reads static INI configuration; it never runs ansible.
"""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path

# ansible.cfg search order (first existing wins), relative to repo root.
CFG_CANDIDATES = ("ansible.cfg", ".ansible.cfg")

# Parse-time-safe Jinja extensions we are willing to enable. Anything outside
# this allowlist is ignored for safety even if declared in ansible.cfg.
SAFE_JINJA_EXTENSIONS = {
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols",
    "jinja2.ext.i18n",
    "jinja2.ext.debug",
}


@dataclass
class AnsibleConfig:
    """Effective settings extracted from ``ansible.cfg``."""

    cfg_path: str | None = None  # repository-relative, None if absent
    roles_paths: tuple[str, ...] = ("roles",)
    collections_paths: tuple[str, ...] = ("collections",)
    inventory: str | None = None
    vars_plugins_enabled: tuple[str, ...] = ()
    jinja2_extensions: tuple[str, ...] = ()
    callback_plugins_enabled: tuple[str, ...] = ()
    raw_defaults: dict[str, str] = field(default_factory=dict)

    @property
    def safe_jinja_extensions(self) -> list[str]:
        """Configured extensions intersected with the parse-safe allowlist."""
        return sorted(e for e in self.jinja2_extensions if e in SAFE_JINJA_EXTENSIONS)


def _split_paths(value: str) -> tuple[str, ...]:
    """Split an ansible path list on ':' and ',' and normalize each entry."""
    parts: list[str] = []
    for chunk in value.replace(",", ":").split(":"):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Ansible allows ~ and env-relative; we keep repo-relative where possible.
        chunk = os.path.expanduser(chunk)
        if chunk.startswith("./"):
            chunk = chunk[2:]
        parts.append(chunk.rstrip("/"))
    return tuple(parts)


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in value.replace(",", " ").split() if v.strip())


def load_ansible_config(repo: Path) -> AnsibleConfig:
    """Load effective ansible.cfg from the repo root. Returns defaults if absent."""
    cfg_file: Path | None = None
    for candidate in CFG_CANDIDATES:
        p = repo / candidate
        if p.is_file():
            cfg_file = p
            break

    if cfg_file is None:
        return AnsibleConfig()

    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(cfg_file, encoding="utf-8")
    except configparser.Error:
        # Malformed cfg: fall back to defaults but record the path.
        return AnsibleConfig(cfg_path=cfg_file.name)

    # ConfigParser lowercases option keys; ansible.cfg keys are case-insensitive.
    defaults = dict(parser["defaults"]) if parser.has_section("defaults") else {}

    def get(*keys: str) -> str | None:
        for k in keys:
            if k in defaults:
                return defaults[k]
        return None

    roles = get("roles_path")
    colls = get("collections_path", "collections_paths")
    inv = get("inventory")
    vars_enabled = get("vars_plugins_enabled")
    jinja_ext = get("jinja2_extensions")
    cb_enabled = get("callbacks_enabled", "callback_whitelist")

    return AnsibleConfig(
        cfg_path=str(cfg_file.relative_to(repo)),
        roles_paths=_split_paths(roles) if roles else ("roles",),
        collections_paths=_split_paths(colls) if colls else ("collections",),
        inventory=inv.strip() if inv else None,
        vars_plugins_enabled=_split_list(vars_enabled) if vars_enabled else (),
        jinja2_extensions=_split_list(jinja_ext) if jinja_ext else (),
        callback_plugins_enabled=_split_list(cb_enabled) if cb_enabled else (),
        raw_defaults=defaults,
    )
