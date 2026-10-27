"""Data for skill-goal-guard's governance checker: paths, registries and exemptions with their reasons. No logic.

Imported, not run. Imports point one way: checks -> helpers -> config -> core (skill-ai-it patterns/governance-checks.md, "Structure and growth").
Tests point ROOT at a temporary copy; every reader goes through helpers.root(), so the change takes effect at call time.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PACKAGE = "scripts/govcheck"
CORE_TEMPLATE = "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/govcheck/core.py"
MODULE_MAX_LINES = 400
CHECK_MAX_LINES = 60
OVERSIZE: dict[str, int] = {}

# Folders never scanned besides every dot-folder (helpers.files): caches and rebuildable output.
SKIP_DIRS = ("__pycache__",)
# Operating-system clutter that is never pack content.
SKIP_FILES = (".DS_Store",)

# Markdown that must carry the governance front matter (AGENTS.md, Working rules): every .md except these names.
FRONT_MATTER_EXEMPT = ("readme.md", "SKILL.md", "CLAUDE.md", "AGENTS.md")
FRONT_MATTER_KEYS = ("Title", "Category", "Status", "Authority", "Scope", "Last reviewed", "Summary")

# Verbatim sources (AGENTS.md: "docs/ sources are kept verbatim"): their links point into the original source tree, so link checks skip them.
VERBATIM = (
  "docs/goal-guard/",
  "docs/goal-guard-research-pack/",
  "docs/goal_guard_agent_kickoff_v1_7.md",
  "docs/goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md",
  "documents/",
)

# The file catalog (AGENTS.md, "Before calling work done": "docs/catalog.md lists every file").
CATALOG = "docs/catalog.md"
# The activation surface that must route every reference (AGENTS.md, Layout: "must route every file in references/").
ROUTER = "SKILL.md"
REFERENCES = "references"
# The scripts catalogue and task runner (AGENTS.md, Layout: "every script catalogued with a recipe").
SCRIPTS_INDEX = "scripts/readme.md"
FRONT_ENDS = "scripts/goal_guard*.py"
RUNNER = "justfile"
