"""Pack family: the rules that make skill-pad the operator's own skill (operator, 2026-11-10: own skill, no plugin, Pad's copies removed).

Imported, not run. Rules from the pack's AGENTS.md (Working rules) and SETUP.md (Install links).
"""

import os
import re
from pathlib import Path

from .. import config
from ..core import counted, fail
from ..helpers import root


def check_skill_header_and_budget() -> None:
  """SKILL.md is named skill-pad and stays within its line budget.

  Catches: Pad's own `name: pad` text coming back as the activation surface, or SKILL.md growing past 200 lines instead of moving detail into a
  reference (AGENTS.md: "It stays within 200 lines").
  """
  text = (root() / config.ROUTER).read_text(encoding="utf-8")
  counted()
  if not re.search(rf"^name: {re.escape(config.SKILL_NAME)}$", text, re.M):
    fail("pack", f"{config.ROUTER}: front matter name is not {config.SKILL_NAME}")
  lines = text.count("\n")
  counted()
  if lines > config.ROUTER_MAX_LINES:
    fail("pack", f"{config.ROUTER}: {lines} lines, over {config.ROUTER_MAX_LINES}; move detail into references/")


def check_no_pad_shipped_skills() -> None:
  """No Pad-generated skill folder exists in the pack.

  Catches: `pad agent install` run in this folder, which writes Pad's text beside the operator's own skill (AGENTS.md, Working rules).
  """
  for path in config.FORBIDDEN_PATHS:
    counted()
    if (root() / path).exists():
      fail("pack", f"{path} exists: Pad-shipped skill text is not kept in this pack (references/upgrade.md)")


def check_install_links_point_here() -> None:
  """Each install link that exists on this machine resolves to the pack root.

  Catches: a link left pointing at the old `.claude/skills/pad/` folder (a dangling skill) or at a copy. A machine without the link's parent folder
  is skipped, so the check runs anywhere; a missing link where the parent exists fails.
  """
  for link in config.INSTALL_LINKS:
    path = Path(os.path.expanduser(link))
    if not path.parent.is_dir():
      continue
    counted()
    if not path.is_symlink() or path.resolve() != root().resolve():
      fail("pack", f"{link} does not link to {root()} (SETUP.md, Install links)")
