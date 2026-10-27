"""Settings for the Knowledge Curator: fixed names, vocabularies, defaults and the per-project config loader.

Imported, not run. The vocabularies mirror the enums in schemas/*.schema.json; tests/test_contract.py fails if they drift.
Environment: KC_ACTOR names the person recording a decision (default "project-owner"). Safety: reads .kc/config.yaml only.
"""

import os
from pathlib import Path

from . import yaml_io
from .errors import InputError

SKILL_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = SKILL_ROOT / "schemas"
KC_DIR = ".kc"
CONFIG_FILE = "config.yaml"
LEDGERS = ("sources", "sections", "claims", "relations", "conflicts", "decisions")

CATEGORIES = ("architecture", "requirements", "technical", "governance", "operations")
KINDS = ("observed", "target", "requirement", "proposal", "decision", "hypothesis", "test_result", "external_fact", "procedure")
EPISTEMIC = ("OBSERVED", "PROPOSED", "APPROVED", "INFERRED", "DISPUTED")
DISPOSITIONS = ("CURRENT", "HISTORICAL", "SUPERSEDED", "DUPLICATE", "REJECTED", "REVIEW_REQUIRED")
SUBCATEGORIES = {
  "architecture": ("components", "topology", "integration", "security"),
  "requirements": ("functional", "nonfunctional", "acceptance"),
  "technical": ("protocols", "api", "configuration", "limitations"),
  "governance": ("decisions", "rationale", "policy", "risks"),
  "operations": ("deployment", "troubleshooting", "recovery"),
}
SEVERITIES = ("P0", "P1", "P2", "P3")
BLOCKING_SEVERITIES = ("P0", "P1")
RELATIONS = (
  "equivalent",
  "corroborating",
  "refinement",
  "time-evolution",
  "different-scope",
  "proposal-vs-observation",
  "true-conflict",
  "uncertain",
)
SECTION_STATUSES = ("context", "unreadable", "pending-review")
ACTIONS = ("ACCEPT_RECOMMENDATION", "USE_OTHER", "BOTH_APPLY_SCOPED", "CORRECTED", "DEFER")
PROMOTION_GATES = ("no_open_p0_p1", "operator_decision", "governing_files", "evidence_verified")

GIT_TIMEOUT_S = 10
NLI_TIMEOUT_S = 120

DEFAULT_CONFIG = {
  "schema_version": 1,
  "project_id": None,
  "include": ["**/*.md"],
  "exclude_dirs": [".git", ".kc", "knowledge", "archive", "node_modules", ".venv", "__pycache__", ".remember", ".code-context-notes"],
  "knowledge_dir": "knowledge",
  "archive_dir": "archive/originals",
  "governing_files": ["AGENTS.md"],
  "taxonomy_extensions": {},
  # Operator chose the first three (2026-10-27); evidence_verified added by default on review because a source edited after render
  # would otherwise be promoted stale. A project may drop it in .kc/config.yaml.
  "promotion_gates": ["no_open_p0_p1", "operator_decision", "governing_files", "evidence_verified"],
  "candidates": {"min_ratio": 80, "fts_neighbours": 20},
  "worksheet": {"max_sections": 25, "max_chars": 12000},
}


def kc_path(root: Path, *parts: str) -> Path:
  """Path inside a project's .kc/ folder.

  Args:
    root: project root.
    *parts: path parts below .kc/.

  Returns:
    The joined path (not created).
  """
  return root / KC_DIR / Path(*parts)


def ledger_path(root: Path, name: str) -> Path:
  """Path of one JSONL ledger.

  Args:
    root: project root.
    name: one of LEDGERS.

  Returns:
    The ledger path.

  Raises:
    InputError: unknown ledger name.
  """
  if name not in LEDGERS:
    raise InputError(f"unknown ledger {name!r}")
  return kc_path(root, f"{name}.jsonl")


def load_config(root: Path) -> dict:
  """Project config: defaults overlaid with .kc/config.yaml when it exists.

  Args:
    root: project root.

  Returns:
    The merged config; project_id defaults to the folder name.

  Raises:
    InputError: the config file is not a mapping or names an unknown promotion gate.
  """
  cfg = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v) for k, v in DEFAULT_CONFIG.items()}
  path = kc_path(root, CONFIG_FILE)
  if path.exists():
    loaded = yaml_io.load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
      raise InputError(f"{path}: config must be a mapping")
    for key, value in loaded.items():
      if isinstance(cfg.get(key), dict) and isinstance(value, dict):
        cfg[key] = {**cfg[key], **value}
      else:
        cfg[key] = value
  cfg["project_id"] = cfg.get("project_id") or root.resolve().name
  unknown = [g for g in cfg["promotion_gates"] if g not in PROMOTION_GATES]
  if unknown:
    raise InputError(f"unknown promotion gate(s): {', '.join(unknown)}")
  return cfg


def actor() -> str:
  """Name recorded on decisions.

  Returns:
    KC_ACTOR from the environment, or "project-owner".
  """
  return os.environ.get("KC_ACTOR", "project-owner")
