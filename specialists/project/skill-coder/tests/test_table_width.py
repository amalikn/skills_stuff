"""Offline tests for table_width: aligned width is measured as the hook pads it, continuation rows and wide tables fail, --before limits the scope.

Run: just test (stdlib unittest).
"""

import importlib
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
table_width = importlib.import_module("table_width")


class TableWidthTest(unittest.TestCase):
  """Width, continuation rows, scope and exit codes."""

  def write(self, text: str) -> pathlib.Path:
    """Write a temp markdown file.

    Args:
      text: its content.

    Returns:
      Its path.

    """
    d = tempfile.mkdtemp()
    p = pathlib.Path(d) / "t.md"
    p.write_text(text, encoding="utf-8")
    return p

  def test_aligned_width_uses_widest_cell_per_column(self) -> None:
    """Short written rows still count at their padded width."""
    n, width, cont = table_width.measure(["| a | bb |", "|---|---|", "| cccc | d |"])
    self.assertEqual((n, width, cont), (2, 4 + 2 + 7, 0))

  def test_wide_table_fails(self) -> None:
    """A table at the limit is reported BAD and exits 1."""
    p = self.write("| " + "x" * 196 + " |\n|---|\n| y |\n")
    self.assertEqual(table_width.main([str(p)]), 1)

  def test_continuation_rows_fail(self) -> None:
    """A row whose first cell is empty is a continuation row."""
    p = self.write("| a | b |\n|---|---|\n| c | d |\n|   | e |\n")
    self.assertEqual(table_width.main([str(p)]), 1)

  def test_narrow_table_passes(self) -> None:
    """A small table passes with exit 0."""
    p = self.write("intro\n\n| a | b |\n|---|---|\n| c | d |\n")
    self.assertEqual(table_width.main([str(p)]), 0)

  def test_before_limits_scope(self) -> None:
    """Tables below the --before heading are not checked."""
    p = self.write("| a |\n|---|\n| b |\n\n## Tail\n\n| " + "x" * 300 + " |\n|---|\n")
    self.assertEqual(table_width.main([str(p), "--before", "## Tail"]), 0)
    self.assertEqual(table_width.main([str(p)]), 1)

  def test_missing_file_exits_2(self) -> None:
    """An unreadable file is a usage error."""
    self.assertEqual(table_width.main(["/nonexistent/x.md"]), 2)


if __name__ == "__main__":
  unittest.main()
