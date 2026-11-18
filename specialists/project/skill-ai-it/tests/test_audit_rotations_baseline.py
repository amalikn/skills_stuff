"""Offline tests for scripts/records/audit_rotations.py audit(): the comparison text is the record before its FIRST rotation even after
docs/history was regrouped by kind, and a ticked sync item archived under docs/history/sync is not lost. Needs git; no network."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "records" / "audit_rotations.py"
_spec = importlib.util.spec_from_file_location("audit_rotations", SCRIPT)
ar = importlib.util.module_from_spec(_spec)
sys.modules["audit_rotations"] = ar
_spec.loader.exec_module(ar)


def commit(root: Path, message: str) -> None:
  """Stage everything and commit it.

  Args:
      root: the repository.
      message: the commit subject.

  Raises:
      subprocess.CalledProcessError: git refused.
  """
  for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", message]):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, timeout=60)


def rotated_project(tmp: str) -> Path:
  """A repository whose SCRATCHPAD.md was rotated once into the flat layout, gained a later entry, then had docs/history regrouped by kind.

  Args:
      tmp: an empty folder.

  Returns:
      The project root.
  """
  root = Path(tmp)
  subprocess.run(["git", "-C", tmp, "init", "-q"], check=True, capture_output=True, timeout=60)
  (root / "SCRATCHPAD.md").write_text("## Log\n\n- **2026-10-01** old entry\n- [x] **2026-10-02** to es: old sync item\n")
  commit(root, "record")
  hist = root / "docs" / "history"
  hist.mkdir(parents=True)
  (hist / "scratchpad-20261010_1748.md").write_text("- **2026-10-01** old entry\n")
  (root / "SCRATCHPAD.md").write_text("## Log\n\n- [x] **2026-10-02** to es: old sync item\n")
  commit(root, "first rotation, flat layout")
  (root / "SCRATCHPAD.md").write_text("## Log\n\n- [x] **2026-10-02** to es: old sync item\n- **2026-11-10** later entry\n")
  commit(root, "an entry written after the first rotation")
  (hist / "scratchpad").mkdir()
  subprocess.run(["git", "-C", tmp, "mv", "docs/history/scratchpad-20261010_1748.md", "docs/history/scratchpad/"], check=True, capture_output=True, timeout=60)
  commit(root, "docs/history grouped by kind")
  return root


class FirstRotationTest(unittest.TestCase):
  """audit() against a small real git history."""

  def test_regrouped_archive_keeps_the_first_rotation_as_baseline(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = rotated_project(tmp)
      # the later entry is rewritten after the regroup: it was never in the pre-rotation text, so the audit has no say on it
      (root / "SCRATCHPAD.md").write_text("## Log\n\n- [x] **2026-10-02** to es: old sync item\n- **2026-11-10** later entry, reworded\n")
      self.assertEqual(ar.audit(root, "SCRATCHPAD.md"), [])

  def test_pre_rotation_loss_is_still_caught_after_a_regroup(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = rotated_project(tmp)
      (root / "docs" / "history" / "scratchpad" / "scratchpad-20261010_1748.md").write_text("emptied\n")
      self.assertEqual(ar.audit(root, "SCRATCHPAD.md"), ["- **2026-10-01** old entry"])

  def test_sync_archive_counts_as_archived(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = rotated_project(tmp)
      sync = root / "docs" / "history" / "sync"
      sync.mkdir()
      (sync / "sync-archive-20261118_1747.md").write_text("- [x] **2026-10-02** to es: old sync item\n")
      (root / "SCRATCHPAD.md").write_text("## Log\n\n- **2026-11-10** later entry\n")
      self.assertEqual(ar.audit(root, "SCRATCHPAD.md"), [])


if __name__ == "__main__":
  unittest.main()
