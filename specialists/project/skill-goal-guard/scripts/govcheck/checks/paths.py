"""Path family: every relative link in the pack's own markdown resolves on disk (skill-ai-it T1 "referenced paths resolve").

Imported, not run. Verbatim sources are skipped: their links point into the original source tree, and they are never edited.
"""

from ..core import counted, fail
from ..helpers import files, is_verbatim, links, rel


def check_relative_links_resolve() -> None:
  """A relative markdown link that points nowhere fails.

  Catches: a renamed or moved file whose old links remain (AGENTS.md, Before calling work done: "no broken relative links").
  """
  for doc in files("*.md"):
    if is_verbatim(doc):
      continue
    for target in links(doc):
      counted()
      if not (doc.parent / target).exists():
        fail("path", f"{rel(doc)}: link {target} does not resolve")
