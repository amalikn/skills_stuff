"""Repository discovery and file classification.

Walks the repository once, applies exclusion policy (dirs, globs, vendored
collection roots, symlink-escape prevention), and classifies each file by its
Ansible role. Produces a deterministic, sorted inventory of files. Never reads
file *content* here beyond what the OS provides — content parsing happens later.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .ansible_config import AnsibleConfig
from .app_config import AppConfig
from .collections import CollectionInfo, discover_collections, vendored_roots


class FileKind(str, Enum):
    PLAYBOOK = "playbook"
    ROLE_TASKS = "role_tasks"
    ROLE_HANDLERS = "role_handlers"
    ROLE_DEFAULTS = "role_defaults"
    ROLE_VARS = "role_vars"
    ROLE_META = "role_meta"
    ROLE_TEMPLATE = "role_template"
    ROLE_FILE = "role_file"
    GROUP_VARS = "group_vars"
    HOST_VARS = "host_vars"
    INVENTORY = "inventory"
    ANSIBLE_CFG = "ansible_cfg"
    REQUIREMENTS = "requirements"
    VARS_PLUGIN = "vars_plugin"
    CALLBACK_PLUGIN = "callback_plugin"
    FILTER_PLUGIN = "filter_plugin"
    LOOKUP_PLUGIN = "lookup_plugin"
    ACTION_PLUGIN = "action_plugin"
    MODULE = "module"
    MODULE_UTILS = "module_utils"
    VENDORED_COLLECTION = "vendored_collection"
    SUPPORT_SCRIPT = "support_script"
    OTHER_YAML = "other_yaml"
    UNKNOWN = "unknown"


YAML_SUFFIXES = (".yml", ".yaml")
PLUGIN_DIR_KIND = {
    "vars_plugins": FileKind.VARS_PLUGIN,
    "callback_plugins": FileKind.CALLBACK_PLUGIN,
    "filter_plugins": FileKind.FILTER_PLUGIN,
    "lookup_plugins": FileKind.LOOKUP_PLUGIN,
    "action_plugins": FileKind.ACTION_PLUGIN,
    "library": FileKind.MODULE,
    "module_utils": FileKind.MODULE_UTILS,
}


@dataclass
class DiscoveredFile:
    rel_path: str
    kind: FileKind
    role: str | None = None  # owning role name, when applicable


@dataclass
class Discovery:
    repo: Path
    files: list[DiscoveredFile] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    role_paths: dict[str, str] = field(default_factory=dict)  # role -> rel dir
    collections: list[CollectionInfo] = field(default_factory=list)
    vendored_yaml_count: int = 0
    excluded_backup_count: int = 0
    symlink_escapes: list[str] = field(default_factory=list)

    def by_kind(self, kind: FileKind) -> list[DiscoveredFile]:
        return [f for f in self.files if f.kind == kind]


def discover(cfg: AppConfig, acfg: AnsibleConfig) -> Discovery:
    repo = cfg.repo.resolve()
    collections = discover_collections(repo, acfg.collections_paths)
    vend_roots = set(vendored_roots(collections))

    disc = Discovery(repo=repo, collections=collections)

    roles_dirs = [repo / rp for rp in acfg.roles_paths]
    role_names: set[str] = set()
    for rd in roles_dirs:
        if rd.is_dir():
            for role_dir in sorted(rd.iterdir()):
                if role_dir.is_dir() and not role_dir.name.startswith("."):
                    role_names.add(role_dir.name)
                    disc.role_paths.setdefault(
                        role_dir.name, str(role_dir.relative_to(repo))
                    )
    disc.roles = sorted(role_names)

    for abs_path in _walk(repo, cfg, disc):
        rel = str(abs_path.relative_to(repo))

        # Vendored collection content: count YAML, do not classify as first-class.
        if _under_any(rel, vend_roots):
            if abs_path.suffix in YAML_SUFFIXES:
                disc.vendored_yaml_count += 1
            if not cfg.deep_index_vendored:
                continue

        kind, role = _classify(rel, abs_path, disc.role_paths, acfg)
        if kind is None:
            continue
        disc.files.append(DiscoveredFile(rel_path=rel, kind=kind, role=role))

    disc.files.sort(key=lambda f: (f.kind.value, f.rel_path))
    return disc


def _walk(repo: Path, cfg: AppConfig, disc: Discovery):
    """Yield files under repo, applying dir/glob/symlink exclusions."""
    stack = [repo]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            name = entry.name
            if entry.is_symlink() and not cfg.follow_symlinks:
                # Symlink-escape prevention: record links that resolve outside repo.
                try:
                    target = entry.resolve()
                    target.relative_to(repo)
                except (OSError, ValueError):
                    disc.symlink_escapes.append(str(entry.relative_to(repo)))
                continue
            if entry.is_dir():
                if name in cfg.exclude_dirs:
                    continue
                if _is_virtualenv(entry):
                    continue
                stack.append(entry)
                continue
            rel = str(entry.relative_to(repo))
            if _excluded_by_glob(rel, cfg.exclude_globs):
                if fnmatch.fnmatch(rel, "inventories/**/*.zip") or rel.endswith(".zip"):
                    disc.excluded_backup_count += 1
                continue
            if cfg.include_patterns and not any(
                fnmatch.fnmatch(rel, p) for p in cfg.include_patterns
            ):
                continue
            if any(fnmatch.fnmatch(rel, p) for p in cfg.exclude_patterns):
                continue
            yield entry


def _is_virtualenv(d: Path) -> bool:
    """Detect a Python virtual environment directory to avoid indexing its libs.

    Catches ``.venv``, ``venv``, ``.venv-sheets`` and any dir carrying the
    ``pyvenv.cfg`` marker regardless of name.
    """
    name = d.name
    if name.startswith(".venv") or name == "venv" or name.endswith("-venv"):
        return True
    return (d / "pyvenv.cfg").is_file()


def _excluded_by_glob(rel: str, globs: tuple[str, ...]) -> bool:
    for g in globs:
        if fnmatch.fnmatch(rel, g):
            return True
        # Support "dir/**/*.ext" matching at any depth including zero.
        if "**/" in g and fnmatch.fnmatch(rel, g.replace("**/", "")):
            return True
    return False


def _under_any(rel: str, roots: set[str]) -> bool:
    return any(rel == r or rel.startswith(r + "/") for r in roots)


def _classify(
    rel: str, abs_path: Path, role_paths: dict[str, str], acfg: AnsibleConfig
) -> tuple[FileKind | None, str | None]:
    parts = rel.split("/")
    suffix = abs_path.suffix

    # ansible.cfg / requirements
    if parts[-1] in ("ansible.cfg", ".ansible.cfg"):
        return FileKind.ANSIBLE_CFG, None
    if parts[-1] in ("requirements.yml", "requirements.yaml"):
        return FileKind.REQUIREMENTS, None

    # Top-level plugin dirs (vars_plugins/, callback_plugins/, library/, ...)
    if len(parts) >= 2 and parts[0] in PLUGIN_DIR_KIND and suffix == ".py":
        if parts[-1] == "__init__.py":
            return None, None
        return PLUGIN_DIR_KIND[parts[0]], None

    # Inventory tree
    if parts[0] == "inventories" or parts[0] == "inventory":
        if "group_vars" in parts:
            return FileKind.GROUP_VARS, None
        if "host_vars" in parts:
            return FileKind.HOST_VARS, None
        return FileKind.INVENTORY, None

    # Role-owned files: find the role by matching a known role dir prefix.
    role = _owning_role(rel, role_paths)
    if role is not None:
        role_root = role_paths[role]
        sub = rel[len(role_root) + 1 :]
        sub_parts = sub.split("/")
        top = sub_parts[0] if sub_parts else ""
        if top == "tasks" and suffix in YAML_SUFFIXES:
            return FileKind.ROLE_TASKS, role
        if top == "handlers" and suffix in YAML_SUFFIXES:
            return FileKind.ROLE_HANDLERS, role
        if top == "defaults" and suffix in YAML_SUFFIXES:
            return FileKind.ROLE_DEFAULTS, role
        if top == "vars" and suffix in YAML_SUFFIXES:
            return FileKind.ROLE_VARS, role
        if top == "meta" and suffix in YAML_SUFFIXES:
            return FileKind.ROLE_META, role
        if top == "templates":
            return FileKind.ROLE_TEMPLATE, role
        if top == "files":
            return FileKind.ROLE_FILE, role
        if top in PLUGIN_DIR_KIND and suffix == ".py":
            return PLUGIN_DIR_KIND[top], role
        return None, None

    # Top-level group_vars / host_vars
    if parts[0] == "group_vars":
        return FileKind.GROUP_VARS, None
    if parts[0] == "host_vars":
        return FileKind.HOST_VARS, None

    # Top-level playbooks: YAML at repo root or in a playbooks/ dir.
    if suffix in YAML_SUFFIXES:
        if len(parts) == 1:
            return FileKind.PLAYBOOK, None
        if parts[0] in ("playbooks", "plays"):
            return FileKind.PLAYBOOK, None
        return FileKind.OTHER_YAML, None

    if suffix in (".sh", ".py", ".j2"):
        return FileKind.SUPPORT_SCRIPT, None

    return None, None


def _owning_role(rel: str, role_paths: dict[str, str]) -> str | None:
    best: str | None = None
    best_len = -1
    for role, root in role_paths.items():
        if rel == root or rel.startswith(root + "/"):
            if len(root) > best_len:
                best = role
                best_len = len(root)
    return best
