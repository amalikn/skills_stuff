"""Catalog family: SKILL.md routes every topic reference, the upstream index lists every mirrored file, every script is catalogued with a recipe.

Imported, not run. Rules from the pack's AGENTS.md (Working rules) and skill-ai-it's script inventory.
"""

from .. import config
from ..core import counted, fail
from ..helpers import links, rel, root


def check_router_routes_every_reference() -> None:
  """SKILL.md links every markdown file directly under references/.

  Catches: a new topic reference no agent will open because the activation surface does not route to it.
  """
  router = root() / config.ROUTER
  routed = {(router.parent / t).resolve() for t in links(router)}
  for ref in sorted((root() / config.REFERENCES).glob("*.md")):
    counted()
    if ref.resolve() not in routed:
      fail("route", f"{config.ROUTER} does not route {rel(ref)}")


def check_upstream_index_lists_every_file() -> None:
  """references/upstream/readme.md links every mirrored file.

  Catches: a file fetched into the mirror without an index row (AGENTS.md: "record new files in references/upstream/readme.md").
  """
  index = root() / config.UPSTREAM_INDEX
  linked = {(index.parent / t).resolve() for t in links(index)}
  for path in sorted((root() / config.UPSTREAM).rglob("*")):
    if not path.is_file() or path == index or path.name in config.SKIP_FILES:
      continue
    counted()
    if path.resolve() not in linked:
      fail("upstream", f"{config.UPSTREAM_INDEX} does not list {rel(path)}")


def check_scripts_catalogued_with_recipe() -> None:
  """Every pad_* script has a row in scripts/README.md and is run by a justfile recipe.

  Catches: a script added without its catalogue row or recipe.
  """
  index = (root() / config.SCRIPTS_INDEX).read_text(encoding="utf-8")
  runner = (root() / config.RUNNER).read_text(encoding="utf-8")
  scripts = sorted({p for pattern in config.FRONT_ENDS for p in root().glob(pattern)})
  for script in scripts:
    counted()
    if f"`{script.name}`" not in index:
      fail("scripts", f"{config.SCRIPTS_INDEX} has no row for {script.name}")
    counted()
    if f"scripts/{script.name}" not in runner:
      fail("scripts", f"{config.RUNNER} has no recipe running {script.name}")
