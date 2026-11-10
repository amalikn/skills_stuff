"""Runner family: no recipe reaches an interpreter implicitly (skill-ai-it check 5b; skills_stuff AGENTS.md venv rule).

Imported, not run.
"""

import re

from .. import config
from ..core import counted, fail
from ..helpers import root

BARE = re.compile(r"(^|\s)(python3?|mise exec -- python)\s")


def check_recipes_use_pinned_venv() -> None:
  """Recipe lines call {{py}} or the venv path, never a bare python, python3 or `mise exec -- python`.

  Catches: a recipe that silently runs the host interpreter instead of the pinned working-cache venv. The bootstrap recipe is exempt: it
  is the one place that builds the venv with mise.
  """
  recipe = ""
  for line in (root() / config.RUNNER).read_text(encoding="utf-8").splitlines():
    if line and not line[0].isspace() and ":" in line and not line.startswith(("#", "set ")) and ":=" not in line:
      recipe = line.split(":", 1)[0].split()[0]
      continue
    if not line.startswith((" ", "\t")) or recipe == "bootstrap":
      continue
    counted()
    if BARE.search(line.strip() + " "):
      fail("runner", f"{config.RUNNER} recipe {recipe}: bare interpreter in `{line.strip()[:80]}`")
