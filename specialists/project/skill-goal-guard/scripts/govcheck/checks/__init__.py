"""The run order of skill-goal-guard's governance checks: one module per family; CHECKS fixes the order.

Imported, not run.
"""

from .catalog import check_catalog_lists_every_file, check_router_routes_every_reference, check_scripts_catalogued_with_recipe
from .paths import check_relative_links_resolve
from .records import check_front_matter
from .runner import check_recipes_use_pinned_venv
from .structure import check_govcheck_structure

CHECKS = (
  check_relative_links_resolve,
  check_router_routes_every_reference,
  check_catalog_lists_every_file,
  check_scripts_catalogued_with_recipe,
  check_front_matter,
  check_recipes_use_pinned_venv,
  check_govcheck_structure,
)
