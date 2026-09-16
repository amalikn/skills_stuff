"""Generic inventory flavor + environment discovery and namespacing.

A *flavor* is an independent inventory scope (e.g. ``apn``, ``rct``). An
*environment* is a sub-scope within a flavor (e.g. ``prod``, ``stage``). Both
are discovered generically from the filesystem — names are never hardcoded, so
repositories using ``hosts``, ``production``/``staging`` dirs, or a single flat
inventory all work.

This module only decides *structure and boundaries*. Parsing inventory content
(and optional ``ansible-inventory`` execution) lives in ``inventory.py``.

Reserved var directories (``group_vars``, ``host_vars`` and any directory a
custom vars-plugin consumes) are flavor-scoped and shared across environments.
Hidden dotfile YAML that mirrors an authored sibling is treated as generated
cache, not an authored source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .app_config import AppConfig

# Directory names that hold flavor-scoped variables, not inventory sources.
# ``topology_vars`` is included because the ansible-wifi custom vars plugin
# consumes it; this list is extended at runtime from detected vars-plugins.
DEFAULT_RESERVED_VAR_DIRS = {"group_vars", "host_vars"}
COMMON_PLUGIN_VAR_DIRS = {"topology_vars"}

# Files/dirs that are never inventory sources.
NON_INVENTORY_NAMES = {"group_vars", "host_vars", "README", "README.md", ".gitkeep"}


@dataclass
class Environment:
    name: str
    source_rel: str  # repository-relative path to the inventory source (file or dir)
    is_dir: bool


@dataclass
class Flavor:
    name: str
    root_rel: str  # repository-relative flavor directory (or file for single-inv)
    environments: list[Environment] = field(default_factory=list)
    var_dirs: dict[str, str] = field(default_factory=dict)  # kind -> rel path
    generated_cache: list[str] = field(default_factory=list)  # rel paths of .*.yml cache


@dataclass
class FlavorLayout:
    flavors: list[Flavor] = field(default_factory=list)
    root_rel: str | None = None
    collisions: list[str] = field(default_factory=list)  # names shared across flavors

    def flavor_names(self) -> list[str]:
        return [f.name for f in self.flavors]


def discover_flavors(
    cfg: AppConfig, repo: Path, extra_var_dirs: set[str] | None = None
) -> FlavorLayout:
    """Resolve inventory flavors from explicit config or auto-discovery."""
    reserved = DEFAULT_RESERVED_VAR_DIRS | COMMON_PLUGIN_VAR_DIRS | (extra_var_dirs or set())

    # 1. Explicit named flavors take precedence.
    if cfg.inventory_flavors:
        layout = FlavorLayout()
        for name, path in sorted(cfg.inventory_flavors.items()):
            layout.flavors.append(_build_flavor(name, repo, path, reserved))
        return layout

    # 2. Single inventory path.
    if cfg.inventory is not None:
        p = cfg.inventory
        name = p.stem if p.is_file() else p.name
        layout = FlavorLayout(root_rel=_rel(repo, p.parent))
        layout.flavors.append(_build_flavor(name, repo, p, reserved))
        return layout

    # 3. Auto-discovery under an inventory root.
    root = cfg.inventory_root or (repo / "inventories")
    if not root.is_dir():
        alt = repo / "inventory"
        if alt.is_dir():
            root = alt
        else:
            return FlavorLayout()  # no inventory; tool still works

    layout = FlavorLayout(root_rel=_rel(repo, root))
    for child in sorted(root.iterdir()):
        if child.name.startswith(".") or child.name in NON_INVENTORY_NAMES:
            continue
        if child.is_dir():
            layout.flavors.append(_build_flavor(child.name, repo, child, reserved))
        elif _looks_like_inventory_file(child):
            # A flat inventory file directly under the root = its own flavor.
            layout.flavors.append(_build_flavor(child.stem, repo, child, reserved))

    _detect_collisions(layout)
    return layout


def _build_flavor(name: str, repo: Path, path: Path, reserved: set[str]) -> Flavor:
    root_rel = _rel(repo, path)
    flavor = Flavor(name=name, root_rel=root_rel)

    if path.is_file():
        flavor.environments.append(
            Environment(name="default", source_rel=root_rel, is_dir=False)
        )
        return flavor

    for child in sorted(path.iterdir()):
        cname = child.name
        if cname in reserved and child.is_dir():
            flavor.var_dirs[cname] = _rel(repo, child)
            # Record hidden generated-cache files inside var dirs.
            for f in sorted(child.rglob(".*.yml")) + sorted(child.rglob(".*.yaml")):
                flavor.generated_cache.append(_rel(repo, f))
            continue
        if cname.startswith("."):
            continue
        if child.is_dir():
            # A non-reserved subdir is an environment if it holds inventory data.
            if _dir_has_inventory(child):
                flavor.environments.append(
                    Environment(name=cname, source_rel=_rel(repo, child), is_dir=True)
                )
        elif _looks_like_inventory_file(child):
            flavor.environments.append(
                Environment(name=child.stem if "." in cname else cname,
                            source_rel=_rel(repo, child), is_dir=False)
            )

    if not flavor.environments:
        # Flavor dir with only var dirs / no explicit env → one implicit env.
        flavor.environments.append(
            Environment(name="default", source_rel=root_rel, is_dir=True)
        )
    return flavor


def _looks_like_inventory_file(p: Path) -> bool:
    if not p.is_file() or p.name.startswith("."):
        return False
    if p.name in NON_INVENTORY_NAMES:
        return False
    # INI-style (no suffix, e.g. ``prod``/``stage``/``hosts``) or yaml/ini inventory.
    if p.suffix in ("", ".ini", ".yml", ".yaml"):
        return True
    return False


def _dir_has_inventory(d: Path) -> bool:
    for child in d.iterdir():
        if _looks_like_inventory_file(child):
            return True
    return False


def _detect_collisions(layout: FlavorLayout) -> None:
    """Flag flavor names that would collide if not namespaced (defensive)."""
    seen: set[str] = set()
    for f in layout.flavors:
        if f.name in seen:
            layout.collisions.append(f.name)
        seen.add(f.name)


def _rel(repo: Path, p: Path) -> str:
    try:
        return str(p.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(p)


def namespaced_group_id(flavor: str, environment: str, group: str) -> str:
    return f"inventory-group:{flavor}:{environment}:{group}"


def namespaced_host_id(flavor: str, environment: str, host: str) -> str:
    return f"inventory-host:{flavor}:{environment}:{host}"
