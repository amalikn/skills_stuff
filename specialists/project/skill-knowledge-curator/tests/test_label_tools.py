"""merge_labels and locate_lines: the answer key from two blind labellers, and excerpt line repair (UNC pilot, 2026-11-05).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary folders.
"""

import importlib
import tempfile
import unittest
from pathlib import Path

from helpers import SCRIPTS

MERGE = importlib.import_module("merge_labels")
LOCATE = importlib.import_module("locate_lines")


def label(lid: str, a: tuple, b: tuple, severity: str = "P2") -> dict:
  """One label.

  Args:
    lid: id.
    a: (path, line).
    b: (path, line).
    severity: severity.

  Returns:
    Label dict.
  """
  return {"id": lid, "kind": "cross-file", "severity": severity, "a": {"path": a[0], "line": a[1]}, "b": {"path": b[0], "line": b[1]}}


class MergeTest(unittest.TestCase):
  """Union with agreement."""

  def test_matched_pair_kept_once_with_stricter_severity(self):
    """Sides swapped and a few lines apart still match; singles from each side are kept."""
    one = [label("L1-01", ("x.md", 10), ("y.md", 40)), label("L1-02", ("x.md", 90), ("z.md", 5))]
    two = [label("L2-01", ("y.md", 43), ("x.md", 12), "P1"), label("L2-02", ("w.md", 1), ("w.md", 9))]
    self.assertTrue((SCRIPTS / "merge_labels.py").is_file())
    merged, counts = MERGE.merge(one, two, 8, ("L1", "L2"))
    self.assertEqual((counts["union"], counts["both"], counts["agreement"]), (3, 1, 0.333))
    self.assertEqual(merged[0]["severity"], "P1")
    self.assertEqual(merged[0]["found_by"], ["L1", "L2"])
    self.assertEqual([m["id"] for m in merged], ["U01", "U02", "U03"])


class LocateTest(unittest.TestCase):
  """Lines from excerpts."""

  def setUp(self):
    """A project with one file."""
    self._tmp = tempfile.TemporaryDirectory()
    self.root = Path(self._tmp.name)
    (self.root / "doc.md").write_text("# T\n\nThe cache size\nis 10.\n\n> Quoted rule here.\n\nThe cache size\nis 20.\n")

  def tearDown(self):
    """Remove the folder."""
    self._tmp.cleanup()

  def test_wrong_lines_fixed_across_a_line_break_and_a_quote(self):
    """An excerpt spanning two lines and one inside a blockquote get their real lines."""
    recs = [
      {"record": "claim", "evidence": [{"source_path": "doc.md", "line_start": 1, "line_end": 1, "excerpt": "The cache size is 10."}]},
      {"record": "claim", "evidence": [{"source_path": "doc.md", "line_start": 2, "line_end": 2, "excerpt": "Quoted rule here."}]},
    ]
    out, unresolved, changed = LOCATE.fix(recs, self.root)
    self.assertEqual(unresolved, [])
    self.assertEqual(changed, 2)
    self.assertEqual((out[0]["evidence"][0]["line_start"], out[0]["evidence"][0]["line_end"]), (3, 4))
    self.assertEqual(out[1]["evidence"][0]["line_start"], 6)

  def test_missing_and_ambiguous_are_reported_not_guessed(self):
    """Words not in the file, or two matches with no hint, stay as written and are listed."""
    recs = [
      {"record": "claim", "evidence": [{"source_path": "doc.md", "excerpt": "not in the file at all"}]},
      {"record": "claim", "evidence": [{"source_path": "doc.md", "excerpt": "The cache size"}]},
    ]
    _, unresolved, changed = LOCATE.fix(recs, self.root)
    self.assertEqual((len(unresolved), changed), (2, 0))


if __name__ == "__main__":
  unittest.main()
