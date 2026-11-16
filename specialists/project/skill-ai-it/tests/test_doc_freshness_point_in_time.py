"""Offline tests for doc_freshness's point-in-time rule: a document whose Category names a point-in-time kind (a transcript, a report, an
audit) is never review-due, and a living document past its window still is (2026-11-16). Uses a temporary git repository, because
findings() reads only tracked files. Run: just test."""

import datetime as dt
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "checks"
sys.path.insert(0, str(SCRIPTS))  # doc_freshness imports file_headers beside it
_spec = importlib.util.spec_from_file_location("doc_freshness", SCRIPTS / "doc_freshness.py")
df = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(df)

HEAD = "---\nTitle: {title}\nCategory: {category}\nStatus: current\nLast reviewed: 2026-10-14\nSummary: test\n---\n\n# {title}\n"


class PointInTime(unittest.TestCase):
  """findings() skips point-in-time categories and still flags living documents."""

  def run_findings(self, category: str) -> dict[str, str]:
    """Write one document with the given Category, 33 days past its review, and return the findings.

    Args:
      category: the document's Category value.

    Returns:
      The findings dict from doc_freshness.findings().

    Raises:
      subprocess.CalledProcessError: when git cannot set up the temporary repository.
    """
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "doc.md").write_text(HEAD.format(title="Doc", category=category), encoding="utf-8")
      for cmd in (["init", "-q"], ["add", "doc.md"]):
        subprocess.run(["git", "-C", tmp, *cmd], check=True, capture_output=True, timeout=30)
      return df.findings(root, dt.date(2026, 11, 16), 30)

  def test_transcript_is_point_in_time(self):
    self.assertNotIn("review-due:doc.md", self.run_findings("communications-transcript"))

  def test_living_document_is_still_due(self):
    self.assertIn("review-due:doc.md", self.run_findings("living-tracker"))


if __name__ == "__main__":
  unittest.main()
