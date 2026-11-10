"""The run order of skill-pad's governance checks: one module per family; CHECKS fixes the order.

Imported, not run.
"""

from .catalog import check_router_routes_every_reference, check_scripts_catalogued_with_recipe, check_upstream_index_lists_every_file
from .pack import check_install_links_point_here, check_no_pad_shipped_skills, check_skill_header_and_budget
from .paths import check_relative_links_resolve
from .records import check_front_matter
from .runner import check_recipes_use_pinned_venv
from .structure import check_govcheck_structure

CHECKS = (
  check_relative_links_resolve,
  check_router_routes_every_reference,
  check_upstream_index_lists_every_file,
  check_scripts_catalogued_with_recipe,
  check_front_matter,
  check_recipes_use_pinned_venv,
  check_skill_header_and_budget,
  check_no_pad_shipped_skills,
  check_install_links_point_here,
  check_govcheck_structure,
)
