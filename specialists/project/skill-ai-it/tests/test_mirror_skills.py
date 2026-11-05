"""Offline tests for scripts/install/mirror_skills.py: plan is read-only, apply links to the canonical folder, collisions and prune behave."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install" / "mirror_skills.py"
_spec = importlib.util.spec_from_file_location("mirror_skills", SCRIPT)
ms = importlib.util.module_from_spec(_spec)
sys.modules["mirror_skills"] = ms
_spec.loader.exec_module(ms)


class MirrorSkillsTest(unittest.TestCase):
  """A source with a real skill, a linked skill and a non-skill folder; a target with one real folder."""

  def setUp(self) -> None:
    """Build the temporary source, canonical and target folders.

    Returns:
      None.
    """
    self.tmp = tempfile.TemporaryDirectory()
    root = Path(self.tmp.name)
    self.canon = root / "canon" / "linked"
    self.canon.mkdir(parents=True)
    (self.canon / "SKILL.md").write_text("---\nname: linked\n---\n")
    self.source = root / "source"
    (self.source / "real").mkdir(parents=True)
    (self.source / "real" / "SKILL.md").write_text("---\nname: real\n---\n")
    (self.source / "notes").mkdir()
    (self.source / "linked").symlink_to(self.canon)
    self.target = root / "target"
    (self.target / "real").mkdir(parents=True)

  def tearDown(self) -> None:
    """Remove the temporary folders.

    Returns:
      None.
    """
    self.tmp.cleanup()

  def test_plan_then_apply(self) -> None:
    """The plan writes nothing; apply links to the resolved canonical folder and never touches the real folder.

    Returns:
      None.
    """
    rows = ms.plan(ms.source_skills(self.source), self.target, prune=False)
    self.assertEqual({(a, n) for a, n, _ in rows}, {("collision", "real"), ("create", "linked")})
    self.assertFalse((self.target / "linked").exists())
    ms.apply([r for r in rows if r[0] == "create"], self.target)
    self.assertEqual(Path(os.readlink(self.target / "linked")), self.canon.resolve())
    self.assertFalse((self.target / "real").is_symlink())
    again = ms.plan(ms.source_skills(self.source), self.target, prune=False)
    self.assertIn(("ok", "linked"), {(a, n) for a, n, _ in again})

  def test_prune_removes_only_links(self) -> None:
    """A stale link is pruned; a real folder with a name absent from the source is left alone.

    Returns:
      None.
    """
    (self.target / "gone").symlink_to(self.canon)
    (self.target / "mine").mkdir()
    rows = ms.plan(ms.source_skills(self.source), self.target, prune=True)
    self.assertIn(("prune", "gone"), {(a, n) for a, n, _ in rows})
    ms.apply([r for r in rows if r[0] in ("create", "prune")], self.target)
    self.assertFalse((self.target / "gone").is_symlink())
    self.assertTrue((self.target / "mine").is_dir())


if __name__ == "__main__":
  unittest.main()
