"""Catalog family: SKILL.md routes every reference, docs/catalog.md lists every file, every front end is catalogued with a recipe.

Imported, not run. Rules from the pack's AGENTS.md (Layout; Before calling work done).
"""

from .. import config
from ..core import counted, fail
from ..helpers import files, links, rel, root


def check_router_routes_every_reference() -> None:
  """SKILL.md links every file in references/.

  Catches: a new reference no agent will open because the activation surface does not route to it.
  """
  router = root() / config.ROUTER
  routed = {(router.parent / t).resolve() for t in links(router)}
  for ref in sorted((root() / config.REFERENCES).glob("*.md")):
    counted()
    if ref.resolve() not in routed:
      fail("route", f"{config.ROUTER} does not route {rel(ref)}")


def check_catalog_lists_every_file() -> None:
  """Every file is linked from docs/catalog.md, directly, through a linked ancestor folder, or through its folder's linked readme.md.

  Catches: a file added without a catalog row (operator, 2026-10-27: "add frontmatter, catalog them properly").
  """
  catalog = root() / config.CATALOG
  linked = {(catalog.parent / t).resolve() for t in links(catalog)}
  for path in files():
    resolved = path.resolve()
    counted()
    covered = resolved == catalog.resolve() or resolved in linked or any(a in linked for a in resolved.parents)
    # A folder's linked readme.md covers the files beside it, except at the root, where readme.md is the front door, not an index of root files.
    if not covered and (path.parent == root() or (path.parent / "readme.md").resolve() not in linked):
      fail("catalog", f"{config.CATALOG} does not list {rel(path)} (link it, its folder, or its folder's readme.md)")


def check_scripts_catalogued_with_recipe() -> None:
  """Every front-end script has a row in scripts/readme.md and is run by a justfile recipe.

  Catches: a script added without its catalogue row or recipe (AGENTS.md, Layout: "every script catalogued with a recipe").
  """
  index = (root() / config.SCRIPTS_INDEX).read_text(encoding="utf-8")
  runner = (root() / config.RUNNER).read_text(encoding="utf-8")
  for script in sorted(root().glob(config.FRONT_ENDS)):
    counted()
    if f"`{script.name}`" not in index:
      fail("scripts", f"{config.SCRIPTS_INDEX} has no row for {script.name}")
    counted()
    if f"scripts/{script.name}" not in runner:
      fail("scripts", f"{config.RUNNER} has no recipe running {script.name}")
