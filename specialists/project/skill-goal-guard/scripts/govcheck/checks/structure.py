"""Structure family: the checker's own shape (skill-ai-it patterns/governance-checks.md, "Structure and growth").

Imported, not run. Adapted from skill-ai-it templates/govcheck/checks/structure.py to read the root at call time and to the pack's two-space style.
"""

import ast
from pathlib import Path

from .. import config
from ..core import counted, fail
from ..helpers import root


def check_govcheck_structure() -> None:
  """Small modules, small checks, one-way imports, and a core.py identical to the skill-ai-it template.

  Catches: a family module over MODULE_MAX_LINES, a check over CHECK_MAX_LINES (except OVERSIZE entries, which may shrink but never grow), a
  family importing another family, and a core.py that differs from the template.
  """
  pkg = root() / config.CHECKER_PACKAGE
  families = {p.stem for p in (pkg / "checks").glob("*.py") if p.stem != "__init__"}
  for path in sorted(pkg.rglob("*.py")):
    name = path.relative_to(root()).as_posix()
    text = path.read_text(encoding="utf-8")
    counted()
    if path.name != "__init__.py" and text.count("\n") > config.MODULE_MAX_LINES:
      fail("structure", f"{name}: {text.count(chr(10))} lines, over {config.MODULE_MAX_LINES}; split the family")
    tree = ast.parse(text)
    for node in ast.walk(tree):
      if isinstance(node, ast.ImportFrom) and path.parent.name == "checks" and path.name != "__init__.py" and node.level == 1:
        for imported in [node.module] if node.module else [a.name for a in node.names]:
          counted()
          if imported in families:
            fail("structure", f"{name}: imports family `{imported}`; share code through helpers.py instead")
    for node in tree.body:
      if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
        size = node.end_lineno - node.lineno + 1
        counted()
        if size > config.OVERSIZE.get(node.name, config.CHECK_MAX_LINES):
          fail("structure", f"{name}: {node.name} is {size} lines; split it")
  canonical = Path(config.CORE_TEMPLATE)
  if canonical.is_file():
    counted()
    if canonical.read_text(encoding="utf-8") != (pkg / "core.py").read_text(encoding="utf-8"):
      fail("structure", f"{config.CHECKER_PACKAGE}/core.py differs from {config.CORE_TEMPLATE}; copy the template")
