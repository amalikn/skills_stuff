"""Offline tests for scripts/records/history_layout.py and history_migrate.py: the by-kind docs/history layout, the index with a summary per file,
and a migration that keeps every link working and never touches another project's archive of the same name."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RECORDS = Path(__file__).resolve().parents[1] / "scripts" / "records"


def load(name: str):
  """Load a records script by path.

  Args:
    name: module file stem.

  Returns:
    The module.
  """
  spec = importlib.util.spec_from_file_location(name, RECORDS / f"{name}.py")
  mod = importlib.util.module_from_spec(spec)
  sys.modules[name] = mod
  spec.loader.exec_module(mod)
  return mod


hl = load("history_layout")
hm = load("history_migrate")

CHANGELOG_ARC = """---
Title: Changelog archive 20261110_0032
Status: archived
Covers: 2026-11-08 00:10 to 2026-11-08 00:10
---

# Changelog archive 20261110_0032

## 20261108_0010 — Lab reruns close N01

See [the record](../../CHANGELOG.md) and [S](scratchpad-20261110_0136.md#current-state).
"""
SCRATCH_ARC = """---
Title: Scratchpad archive 20261110_0136
Covers: 2026-11-07 23:19 to 2026-11-08 00:10
---

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261107_2319 | Recent decisions | - **20261107_2319** `KEEP` (operator, 2026-11-07, `USER_STATED`): E2E fixtures re-signed as JWS today |
"""
SESSION = """---
Title: Session record 2026-11-06
Summary: Whole-chat record of the S3 steps.
---

# Session record
"""


def project(tmp: Path, flat: bool = True) -> Path:
  """A small project with a flat docs/history, a CHANGELOG that links an archive, and a readme with a hand-written session description.

  Args:
    tmp: a temporary folder.
    flat: put the archives at the top (unmigrated) when True.

  Returns:
    The project root (inside a git repo at tmp).
  """
  root = tmp / "proj"
  hist = root / "docs" / "history"
  hist.mkdir(parents=True)
  (hist / "changelog-20261110_0032.md").write_text(CHANGELOG_ARC)
  (hist / "scratchpad-20261110_0136.md").write_text(SCRATCH_ARC)
  (hist / "session-record-20261106_1650.md").write_text(SESSION)
  (hist / "rotation-audit-baseline.txt").write_text("# none\n")
  (hist / "readme.md").write_text(
    "# History\n\nIntro kept.\n\n- [session-record-20261106_1650.md](session-record-20261106_1650.md) Hand words.\n"
    "- [changelog-20261110_0032.md](changelog-20261110_0032.md) 1 entries from `CHANGELOG.md`, 2026-11-08 to 2026-11-08.\n"
  )
  (root / "CHANGELOG.md").write_text("# Changelog\n\nOld: [arc](docs/history/changelog-20261110_0032.md); also `docs/history/scratchpad-20261110_0136.md`.\n")
  other = tmp / "other" / "docs" / "history"
  other.mkdir(parents=True)
  (other / "changelog-20261110_0032.md").write_text("other project's own archive\n")
  (tmp / "other" / "notes.md").write_text(
    "Ours: `docs/history/changelog-20261110_0032.md`; theirs: proj/docs/history/changelog-20261110_0032.md "
    "and [link](../proj/docs/history/changelog-20261110_0032.md).\n"
  )
  for args in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"]):
    subprocess.run(["git", "-C", str(tmp), *args], check=True, capture_output=True, timeout=60)
  return root


class LayoutTest(unittest.TestCase):
  """Kinds, folders, summaries and the index."""

  def test_kind_and_dir(self):
    self.assertEqual(hl.kind_of("session-record-20261111_1102.md")[1], "session-records")
    self.assertEqual(hl.kind_of("scratchpad-20261023_1824-outbox.md")[1], "scratchpad")
    self.assertIsNone(hl.kind_of("readme.md"))
    with tempfile.TemporaryDirectory() as t:
      root = Path(t)
      self.assertEqual(hl.archive_dir(root, "changelog"), "docs/history/changelog")  # new project: by kind
      (root / "docs/history").mkdir(parents=True)
      (root / "docs/history/changelog-20261010_0000.md").write_text("x")
      self.assertEqual(hl.archive_dir(root, "changelog"), "docs/history")  # unmigrated: stays flat
      self.assertEqual(hl.archive_dir(root, "other-record"), "docs/history")

  def test_summaries(self):
    with tempfile.TemporaryDirectory() as t:
      root = project(Path(t))
      hist = root / "docs/history"
      self.assertEqual(hl.summary(hist / "changelog-20261110_0032.md"), "1 entry, 2026-11-08 to 2026-11-08: Lab reruns close N01")
      s = hl.summary(hist / "scratchpad-20261110_0136.md")
      self.assertTrue(s.startswith("1 entry, 2026-11-07 to 2026-11-08: Recent decisions: E2E fixtures"), s)
      self.assertEqual(hl.summary(hist / "session-record-20261106_1650.md"), "Whole-chat record of the S3 steps.")

  def test_index_keeps_intro_and_hand_descriptions(self):
    with tempfile.TemporaryDirectory() as t:
      root = project(Path(t))
      text = hl.render_index(root)
      self.assertIn("Intro kept.", text)
      self.assertIn("Hand words.", text)
      self.assertNotIn("1 entries from", text)
      self.assertIn("## Session records", text)
      self.assertEqual(hl.render_index(root), hl.render_index(root))


class MigrateTest(unittest.TestCase):
  """history_migrate.py end to end in a throwaway git repo."""

  def test_moves_relinks_and_spares_other_projects(self):
    with tempfile.TemporaryDirectory() as t:
      tmp = Path(t)
      root = project(tmp)
      self.assertEqual(hm.main(["--project-root", str(root), "--refs-root", str(tmp)]), 0)  # plan
      self.assertTrue((root / "docs/history/changelog-20261110_0032.md").exists())
      self.assertEqual(hm.main(["--project-root", str(root), "--refs-root", str(tmp), "--apply"]), 0)
      hist = root / "docs/history"
      moved = hist / "changelog" / "changelog-20261110_0032.md"
      self.assertTrue(moved.exists())
      self.assertTrue((hist / "session-records" / "session-record-20261106_1650.md").exists())
      self.assertTrue((hist / "rotation-audit-baseline.txt").exists())
      body = moved.read_text()
      self.assertIn("](../../../CHANGELOG.md)", body)
      self.assertIn("](../scratchpad/scratchpad-20261110_0136.md#current-state)", body)
      log = (root / "CHANGELOG.md").read_text()
      self.assertIn("](docs/history/changelog/changelog-20261110_0032.md)", log)
      self.assertIn("`docs/history/scratchpad/scratchpad-20261110_0136.md`", log)
      notes = (tmp / "other/notes.md").read_text()
      self.assertIn("Ours: `docs/history/changelog-20261110_0032.md`", notes)  # another project's own path: untouched
      self.assertIn("proj/docs/history/changelog/changelog-20261110_0032.md", notes)
      self.assertIn("](../proj/docs/history/changelog/changelog-20261110_0032.md)", notes)
      self.assertEqual((tmp / "other/docs/history/changelog-20261110_0032.md").read_text(), "other project's own archive\n")
      index = (hist / "readme.md").read_text()
      self.assertIn("](changelog/changelog-20261110_0032.md) 1 entry", index)
      self.assertIn("Hand words.", index)
      self.assertEqual(hm.main(["--project-root", str(root), "--refs-root", str(tmp)]), 0)  # second run: nothing to move

  def test_refuses_dirty_history(self):
    with tempfile.TemporaryDirectory() as t:
      root = project(Path(t))
      (root / "docs/history/changelog-20261110_0032.md").write_text("edited\n")
      self.assertEqual(hm.main(["--project-root", str(root), "--apply"]), 1)

  def test_check_gate_and_dirty_references(self):
    """A red check before refuses; red after undoes the move; a dirty reference file refuses; --apply takes one project."""
    with tempfile.TemporaryDirectory() as t:
      tmp = Path(t)
      root = project(tmp)
      hist = root / "docs/history"
      self.assertEqual(hm.main(["--project-root", str(root), "--apply", "--check-cmd", "false"]), 1)
      self.assertTrue((hist / "changelog-20261110_0032.md").exists())  # red before: nothing moved
      self.assertEqual(hm.main(["--project-root", str(root), "--apply", "--check-cmd", "test ! -d docs/history/changelog"]), 1)
      self.assertTrue((hist / "changelog-20261110_0032.md").exists())  # red after: undone
      self.assertFalse((hist / "changelog").exists())
      self.assertIn("](docs/history/changelog-20261110_0032.md)", (root / "CHANGELOG.md").read_text())
      (root / "CHANGELOG.md").write_text((root / "CHANGELOG.md").read_text() + "another session's edit\n")
      self.assertEqual(hm.main(["--project-root", str(root), "--refs-root", str(tmp), "--apply"]), 1)
      self.assertTrue((hist / "changelog-20261110_0032.md").exists())
      self.assertEqual(hm.main(["--project-root", str(root), str(tmp / "other"), "--apply"]), 2)


if __name__ == "__main__":
  unittest.main()
