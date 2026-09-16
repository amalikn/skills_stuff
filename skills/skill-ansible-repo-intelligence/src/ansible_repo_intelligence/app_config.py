"""Tool CLI/config-file parsing and defaults.

This module owns the *tool's own* configuration — CLI options, defaults and an
optional YAML config file. It does NOT parse the repository's ``ansible.cfg``
(that is ``ansible_config.py``). Keeping these separate avoids conflating the
scanner's settings with the scanned repository's Ansible settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

# ---------------------------------------------------------------------------
# Defaults (also the source of truth for validation gates)
# ---------------------------------------------------------------------------

DEFAULT_MAX_FILE_BYTES = 2_000_000

# Repository-map hard budget.
MAP_MAX_LINES = 1000
MAP_MAX_ROLES = 120
MAP_MAX_ENTRY_PLAYBOOKS = 50
MAP_MAX_EXECUTION_PATHS = 100
MAP_MAX_DIAGNOSTICS = 30

# Query bounds.
QUERY_LIMIT = 25
QUERY_MAX_DEPTH = 1
QUERY_MAX_OUTPUT_BYTES = 65_536

# Impact bounds.
IMPACT_LIMIT = 50
IMPACT_MAX_DEPTH = 3
IMPACT_MAX_OUTPUT_BYTES = 131_072

# Directories always excluded from first-class discovery.
DEFAULT_EXCLUDE_DIRS = (
    ".git",
    ".ai-context",
    ".archcore",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "graphify-out",
    ".serena",
    ".smart-coding-cache",
)

DEFAULT_EXCLUDE_GLOBS = (
    "inventories/**/*.zip",
    "**/*.retry",
)

DEFAULT_SECRET_PATTERNS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "private_key", "credential", "auth", "vault", "community",
)


@dataclass
class AppConfig:
    """Fully-resolved configuration for a scan run."""

    repo: Path
    output: Path
    inventory: Path | None = None
    inventory_root: Path | None = None
    inventory_flavors: dict[str, Path] = field(default_factory=dict)
    all_inventory_flavors: bool = False
    exclude_inventory_globs: tuple[str, ...] = ()
    playbooks: tuple[Path, ...] = ()
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    exclude_dirs: tuple[str, ...] = DEFAULT_EXCLUDE_DIRS
    exclude_globs: tuple[str, ...] = DEFAULT_EXCLUDE_GLOBS
    follow_symlinks: bool = False
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES
    strict: bool = False
    fail_on_warning: bool = False
    offline: bool = True
    incremental: bool = False
    force: bool = False
    output_format: str = "yaml"
    log_level: str = "info"
    secret_patterns: tuple[str, ...] = DEFAULT_SECRET_PATTERNS
    run_inventory: bool = False  # opt-in; inventory plugins can execute code
    deep_index_vendored: bool = False

    # Map budget (overridable via config file).
    map_max_lines: int = MAP_MAX_LINES
    map_max_roles: int = MAP_MAX_ROLES
    map_max_entry_playbooks: int = MAP_MAX_ENTRY_PLAYBOOKS
    map_max_execution_paths: int = MAP_MAX_EXECUTION_PATHS
    map_max_diagnostics: int = MAP_MAX_DIAGNOSTICS

    def fingerprint_dict(self) -> dict[str, Any]:
        """Configuration values that affect analysis output.

        Used for the manifest configuration fingerprint and incremental
        invalidation. Volatile/path-only fields that do not change semantics
        are intentionally excluded, but include/exclude rules ARE included.
        """
        return {
            "include_patterns": sorted(self.include_patterns),
            "exclude_patterns": sorted(self.exclude_patterns),
            "exclude_dirs": sorted(self.exclude_dirs),
            "exclude_globs": sorted(self.exclude_globs),
            "exclude_inventory_globs": sorted(self.exclude_inventory_globs),
            "follow_symlinks": self.follow_symlinks,
            "max_file_bytes": self.max_file_bytes,
            "secret_patterns": sorted(self.secret_patterns),
            "run_inventory": self.run_inventory,
            "deep_index_vendored": self.deep_index_vendored,
            "map_budget": {
                "max_lines": self.map_max_lines,
                "max_roles": self.map_max_roles,
                "max_entry_playbooks": self.map_max_entry_playbooks,
                "max_execution_paths": self.map_max_execution_paths,
                "max_diagnostics": self.map_max_diagnostics,
            },
        }


def load_config_file(path: Path) -> dict[str, Any]:
    """Load an optional tool config YAML file. Returns {} if missing/empty."""
    if not path.exists():
        return {}
    yaml = YAML(typ="safe", pure=True)
    data = yaml.load(path.read_text(encoding="utf-8"))
    return data or {}


def apply_config_overrides(cfg: AppConfig, data: dict[str, Any]) -> AppConfig:
    """Return a new AppConfig with recognised overrides from a config file."""
    updates: dict[str, Any] = {}
    if "max_file_bytes" in data:
        updates["max_file_bytes"] = int(data["max_file_bytes"])
    if "secret_patterns" in data:
        updates["secret_patterns"] = tuple(data["secret_patterns"])
    if "exclude_globs" in data:
        updates["exclude_globs"] = tuple(data["exclude_globs"])
    if "deep_index_vendored" in data:
        updates["deep_index_vendored"] = bool(data["deep_index_vendored"])
    rm = data.get("repository_map", {}) or {}
    if "max_lines" in rm:
        updates["map_max_lines"] = int(rm["max_lines"])
    if "max_roles" in rm:
        updates["map_max_roles"] = int(rm["max_roles"])
    if "max_entry_playbooks" in rm:
        updates["map_max_entry_playbooks"] = int(rm["max_entry_playbooks"])
    if "max_execution_paths" in rm:
        updates["map_max_execution_paths"] = int(rm["max_execution_paths"])
    if "max_diagnostics" in rm:
        updates["map_max_diagnostics"] = int(rm["max_diagnostics"])
    return replace(cfg, **updates) if updates else cfg
