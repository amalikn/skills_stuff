"""Data for skill-pad's governance checker: paths, registries and exemptions with their reasons. No logic.

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

# Markdown that must carry the governance front matter: every .md except these names (SKILL.md carries the skill's own name/description header,
# CLAUDE.md is a thin @AGENTS.md wrapper).
FRONT_MATTER_EXEMPT = ("SKILL.md", "CLAUDE.md")
FRONT_MATTER_KEYS = ("Title", "Category", "Status", "Authority", "Scope", "Last reviewed", "Summary")

# Verbatim upstream mirror (AGENTS.md: "never edit a mirrored file"): its links point into Pad's own trees and its files carry no front matter.
# Its index readme.md is the operator's file and is checked.
VERBATIM = ("references/upstream/v", "references/upstream/getpad.dev/", "references/upstream/github.com/")
UPSTREAM = "references/upstream"
UPSTREAM_INDEX = "references/upstream/readme.md"

# The activation surface that must route every topic reference (AGENTS.md, Working rules: "detail goes in one topic file under references/,
# linked from SKILL.md").
ROUTER = "SKILL.md"
REFERENCES = "references"
ROUTER_MAX_LINES = 200
SKILL_NAME = "skill-pad"

# The scripts catalogue and task runner (skill-ai-it script inventory: every script catalogued with a recipe).
SCRIPTS_INDEX = "scripts/README.md"
FRONT_ENDS = ("scripts/pad_*.py", "scripts/pad_*.sh")
RUNNER = "justfile"

# Pad-shipped skill folders that must not come back (AGENTS.md, Working rules; operator 2026-11-10: "remove these files").
FORBIDDEN_PATHS = (".claude/skills/pad", ".agents/skills/pad")
# Install links that must point at the pack root (SETUP.md, Install links). Checked only on a machine where the parent folder exists.
INSTALL_LINKS = ("~/.claude/skills/skill-pad", "~/.agents/skills/skill-pad")
