"""Records family: every governed markdown file carries the front matter, followed by one blank line.

Imported, not run. Rules from the pack's AGENTS.md (Working rules; operator, 2026-10-27).
"""

from .. import config
from ..core import counted, fail
from ..helpers import files, front_matter, rel


def check_front_matter() -> None:
  """Front matter is present with every required key, and a blank line follows the closing ---.

  Catches: a new document without Title, Category, Status, Authority, Scope, Last reviewed and Summary, or one whose body starts directly under
  the front matter (operator, 2026-10-27: "there should be a line gap after the frontmatter").
  """
  for doc in files("*.md"):
    if doc.name in config.FRONT_MATTER_EXEMPT:
      continue
    found = front_matter(doc)
    counted()
    if found is None:
      fail("front-matter", f"{rel(doc)}: no front matter")
      continue
    keys, blank_after = found
    missing = [k for k in config.FRONT_MATTER_KEYS if k not in keys]
    counted()
    if missing:
      fail("front-matter", f"{rel(doc)}: missing {', '.join(missing)}")
    counted()
    if not blank_after:
      fail("front-matter", f"{rel(doc)}: no blank line after the closing ---")
