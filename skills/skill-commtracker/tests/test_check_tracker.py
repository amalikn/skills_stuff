"""Offline tests for scripts/check_tracker.py: a clean tracker and index pass; a broken anchor, a missing file, a date out of order, a numbering gap,
a rule glued to a heading, a broken index link and an unlisted source file are each reported.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_tracker.py"
_spec = importlib.util.spec_from_file_location("commtracker_check_tracker", SCRIPT)
ck = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ck
_spec.loader.exec_module(ck)

CLEAN = """# Tracker

## Contents

- [Email 1 - 20261012_1001 - First](#email-1---20261012_1001---first)
- [Meeting 1 - 20261013 - Rob's notes](#meeting-1---20261013---robs-notes)

---

## Email 1 - 20261012_1001 - First

**Source:** [a.eml](emails/a.eml)

---

## Meeting 1 - 20261013 - Rob's notes

See [Email 1](#email-1---20261012_1001---first).

---
"""


def build(folder: Path, tracker: str, index: str | None = "- [communications-tracking.md](communications-tracking.md)\n- [a.eml](emails/a.eml)\n") -> Path:
  """Write a communications folder with one source email.

  Args:
    folder: a temporary folder.
    tracker: the tracker text.
    index: the readme text, or None for no index.

  Returns:
    The folder.
  """
  (folder / "emails").mkdir()
  (folder / "emails" / "a.eml").write_text("x", encoding="utf-8")
  (folder / "communications-tracking.md").write_text(tracker, encoding="utf-8")
  if index is not None:
    (folder / "readme.md").write_text(index, encoding="utf-8")
  return folder


class CheckTrackerTest(unittest.TestCase):
  """Each finding kind, and a clean pass."""

  def test_clean(self) -> None:
    """A consistent tracker and index give exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
      self.assertEqual(ck.main([str(build(Path(tmp), CLEAN))]), 0)

  def test_tracker_findings(self) -> None:
    """Broken anchor, missing file, date order, numbering and a glued rule are reported."""
    bad = CLEAN.replace("(#email-1---20261012_1001---first).", "(#email-9).").replace("emails/a.eml", "emails/b.eml")
    bad = bad.replace("## Meeting 1 - 20261013", "## Meeting 3 - 20261011").replace("---\n\n## Meeting", "---\n## Meeting")
    with tempfile.TemporaryDirectory() as tmp:
      found = "\n".join(ck.check_tracker(build(Path(tmp), bad) / "communications-tracking.md"))
    for part in ("anchor not found: #email-9", "file not found: emails/b.eml", "out of date order", "Meeting numbering", "no blank line"):
      self.assertIn(part, found)

  def test_index_findings(self) -> None:
    """A broken index link and an unlisted file are reported; no index is one finding."""
    with tempfile.TemporaryDirectory() as tmp:
      folder = build(Path(tmp), CLEAN, "- [gone.md](gone.md)\n")
      found = ck.check_index(folder)
    self.assertIn("index link not found: gone.md", found)
    self.assertIn("not listed in the index: emails/a.eml", found)
    with tempfile.TemporaryDirectory() as tmp:
      self.assertEqual(ck.check_index(build(Path(tmp), CLEAN, None)), ["no readme.md or README.md in the folder"])


if __name__ == "__main__":
  unittest.main()
