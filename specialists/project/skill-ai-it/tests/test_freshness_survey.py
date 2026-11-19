"""Offline tests for freshness_survey: counts overdue and due-by docs with the baseline ignored, flags an early Review by on a non-tracker
doc but not on a tracker, and exits 1 only when something is overdue. Uses a temporary git repository (findings() reads tracked files).
Run: just test."""

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "checks"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("freshness_survey", SCRIPTS / "freshness_survey.py")
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)


def doc(reviewed: str, review_by: str = "", category: str = "reference") -> str:
  """A living markdown document with the given dates.

  Args:
    reviewed: its Last reviewed date.
    review_by: its Review by date, or "" for none.
    category: its Category.

  Returns:
    The file text.
  """
  extra = f"Review by: {review_by}\n" if review_by else ""
  return f"---\nTitle: T\nCategory: {category}\nStatus: current\nLast reviewed: {reviewed}\n{extra}Summary: test\n---\n\n# T\n"


class Survey(unittest.TestCase):
  """The survey answers per project from doc_freshness's own rule."""

  def project(self, tmp: str) -> Path:
    """A git project with one fresh doc, one old doc, one early Review by and one tracker.

    Args:
      tmp: a temporary folder.

    Returns:
      The project root.
    """
    root = Path(tmp) / "pack"
    (root / "docs" / "trackers").mkdir(parents=True)
    (root / "fresh.md").write_text(doc("2026-11-19"))
    (root / "old.md").write_text(doc("2026-08-01"))
    (root / "early.md").write_text(doc("2026-11-19", "2026-11-26"))
    (root / "docs" / "trackers" / "open-items.md").write_text(doc("2026-11-19", "2026-12-03", "living-tracker"))
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    return root

  def test_counts_and_early_review_by(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = self.project(tmp)
      self.assertEqual(fs.due_files(root, fs.dt.date(2026, 11, 20), 90), ["old.md"])
      self.assertEqual(fs.due_files(root, fs.dt.date(2026, 12, 5), 90), ["docs/trackers/open-items.md", "early.md", "old.md"])
      self.assertEqual(fs.early_review_by(root, 90), ["early.md 2026-11-26 2026-11-19"])

  def test_exit_code_follows_overdue(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = self.project(tmp)
      out = io.StringIO()
      with contextlib.redirect_stdout(out):
        self.assertEqual(fs.main(["--project-root", str(root), "--window-days", "90", "--today", "2026-11-20"]), 1)
      self.assertIn("overdue=1", out.getvalue())
      (root / "old.md").write_text(doc("2026-11-19"))
      with contextlib.redirect_stdout(io.StringIO()):
        self.assertEqual(fs.main(["--project-root", str(root), "--window-days", "90", "--today", "2026-11-20"]), 0)


if __name__ == "__main__":
  unittest.main()
