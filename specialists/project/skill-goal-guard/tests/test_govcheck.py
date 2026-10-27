"""Negative tests for the pack's governance checker (scripts/govcheck): each family turns red on the defect it exists to catch.

Run: just test
Safety: read-only for the pack; each test breaks a temporary copy of it. No network.
"""

import importlib
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

config = importlib.import_module("govcheck.config")
core = importlib.import_module("govcheck.core")
checks = {name: importlib.import_module(f"govcheck.checks.{name}") for name in ("paths", "catalog", "records", "runner", "structure")}


class Copy:
  """A temporary copy of the pack with config.ROOT pointed at it; failures are reset on entry."""

  def __enter__(self) -> Path:
    """Copy the pack (without dot-folders and caches) and point the checker at it.

    Returns:
      The copied pack root.
    """
    self._tmp = tempfile.TemporaryDirectory()
    self.root = Path(self._tmp.name) / "pack"

    def skip(folder: str, names: list[str]) -> list[str]:
      """Skip tool dot-folders and caches; keep dot-files such as .mise.toml and the .archcore/ folder, which is pack content."""
      return [n for n in names if n == "__pycache__" or (n.startswith(".") and n != ".archcore" and (Path(folder) / n).is_dir())]

    shutil.copytree(ROOT, self.root, ignore=skip)
    self._saved = config.ROOT
    config.ROOT = self.root
    core.failures.clear()
    return self.root

  def __exit__(self, *exc) -> None:
    """Restore config.ROOT and remove the copy.

    Args:
      *exc: exception details, ignored.
    """
    config.ROOT = self._saved
    core.failures.clear()
    self._tmp.cleanup()


def failures_of(check) -> list[str]:
  """Run one check and return what it reported.

  Args:
    check: a check function.

  Returns:
    The failure lines it added.
  """
  core.failures.clear()
  check()
  return list(core.failures)


class Families(unittest.TestCase):
  """The pack passes, and each break is caught."""

  def test_pack_passes(self):
    """The unbroken copy reports nothing in any family."""
    with Copy():
      for module in checks.values():
        for name in dir(module):
          if name.startswith("check_"):
            self.assertEqual(failures_of(getattr(module, name)), [], name)

  def test_broken_link(self):
    """A link to a missing file fails the path family."""
    with Copy() as root:
      (root / "roadmap.md").write_text((root / "roadmap.md").read_text() + "\n[gone](references/gone.md)\n")
      self.assertTrue(any("gone.md" in f for f in failures_of(checks["paths"].check_relative_links_resolve)))

  def test_unrouted_reference(self):
    """A reference SKILL.md does not route fails."""
    with Copy() as root:
      (root / "references/new-topic.md").write_text("---\nTitle: x\n---\n\n# x\n")
      self.assertTrue(failures_of(checks["catalog"].check_router_routes_every_reference))

  def test_uncatalogued_file(self):
    """A root file the catalog does not list fails."""
    with Copy() as root:
      (root / "stray.txt").write_text("x\n")
      self.assertTrue(any("stray.txt" in f for f in failures_of(checks["catalog"].check_catalog_lists_every_file)))

  def test_script_without_recipe(self):
    """A new front end with no catalogue row or recipe fails twice."""
    with Copy() as root:
      (root / "scripts/goal_guard_new.py").write_text('"""New."""\n')
      self.assertEqual(len(failures_of(checks["catalog"].check_scripts_catalogued_with_recipe)), 2)

  def test_front_matter_gap(self):
    """A missing key and a missing blank line after the front matter both fail."""
    with Copy() as root:
      path = root / "roadmap.md"
      text = path.read_text().replace("\nScope:", "\nScopeless:", 1).replace("---\n\n#", "---\n#", 1)
      path.write_text(text)
      found = failures_of(checks["records"].check_front_matter)
    self.assertTrue(any("missing Scope" in f for f in found) and any("blank line" in f for f in found))

  def test_bare_interpreter(self):
    """A recipe calling python3 directly fails."""
    with Copy() as root:
      (root / "justfile").write_text((root / "justfile").read_text() + "\nbad:\n    python3 scripts/goal_guard.py validate\n")
      self.assertTrue(failures_of(checks["runner"].check_recipes_use_pinned_venv))

  def test_core_drift(self):
    """A core.py that differs from the skill-ai-it template fails the structure family."""
    with Copy() as root:
      core_file = root / "scripts/govcheck/core.py"
      core_file.write_text(core_file.read_text() + "\n# local edit\n")
      self.assertTrue(any("differs" in f for f in failures_of(checks["structure"].check_govcheck_structure)))


if __name__ == "__main__":
  unittest.main()
