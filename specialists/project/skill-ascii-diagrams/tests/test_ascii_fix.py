"""Tests for scripts/ascii_fix.py ("ascii_fix") and scripts/ascii/checks.py ("checks"): an existing ASCII diagram is repaired at its edges and
nothing else moves.

Run: `just test` (unittest, the pack's venv); read-only except one temporary Markdown file. The scripts folder is put on sys.path, as a consuming
project does.
"""

from __future__ import annotations

import importlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
fx = importlib.import_module("ascii_fix")
afr = importlib.import_module("ascii_flow_render")

RAGGED = [
  "  +--------------------+",
  "  | Release trial boots   |",
  "  | short |                 --> fails: rejected",
  "  +-----------------+",
]


def same_width(lines: list[str], a: int) -> bool:
  """Whether every row of the box starting at column `a` ends its edge in one column.

  Args:
    lines: a fixed single box.
    a: its left column.

  Returns:
    True when top, rows and bottom share the right edge column.
  """
  ends = {line.index("+", a + 1) if line[a] == "+" else line.index("|", a + 1) for line in lines}
  return len(ends) == 1


class Repairs(unittest.TestCase):
  """Faults a person makes by hand are repaired."""

  def test_ragged_box_closed(self) -> None:
    """Rows and borders of a ragged box end in one column: the text's, with the one padding space it had."""
    out, problems = fx.fix(RAGGED)
    self.assertEqual(problems, [])
    self.assertTrue(same_width(out, 2), out)
    self.assertEqual(out[1], "  | Release trial boots |")
    self.assertEqual(out[0], "  +" + "-" * 21 + "+")

  def test_exit_kept_after_the_edge(self) -> None:
    """The exit text stays on its row, after the new edge."""
    out, _ = fx.fix(RAGGED)
    self.assertRegex(out[2], r"^  \| short +\| +--> fails: rejected$")
    self.assertEqual(out[2].index("|", 3), out[1].rindex("|"))

  def test_glued_connector_stays_glued(self) -> None:
    """A connector glued to the edge (`|---> next`) stays glued when the box grows."""
    lines = ["+-----+", "| a long |---> next", "+-----+"]
    out, _ = fx.fix(lines)
    self.assertEqual(out[1], "| a long |---> next")

  def test_never_adds_an_edge_finding(self) -> None:
    """A fix that would leave a broken edge the drawing did not have is refused."""

    def breaks(lines: list[str], box: dict, w: int) -> None:
      """A broken redraw that moves one row's right edge, words kept.

      Args:
        lines: the diagram (changed in place).
        box: the box.
        w: unused width.

      Returns:
        None.
      """
      lines[box["rows"][0][0]] = "  | Release trial boots" + " " * 9 + "|"

    clean = afr.box(["Release trial boots"], 24)
    with mock.patch.object(fx, "redraw", breaks):
      out, problems = fx.fix(["  " + x for x in clean])
    self.assertEqual(out, ["  " + x for x in clean])
    self.assertTrue(any("break an edge" in p for p in problems), problems)

  def test_stray_arrow_moved_inside(self) -> None:
    """An arrow drawn past a chained box's width moves to its centre."""
    lines = ["+------+", "| a    |", "+------+", "              v", "+------+", "| b    |", "+------+"]
    out, _ = fx.fix(lines)
    self.assertEqual(out[3], " " * 4 + "v")

  def test_even_widths_only_when_asked(self) -> None:
    """Chained boxes keep their own widths unless --even-widths is given."""
    lines = ["+----------+", "| wide box |", "+----------+", "     |", "     v", "+----+", "| b  |", "+----+"]
    self.assertEqual(fx.fix(lines)[0], lines)
    even, _ = fx.fix(lines, even=True)
    self.assertEqual(even[5], "+----------+")


class Leaves(unittest.TestCase):
  """What is already right, or not a standalone box, is left alone."""

  def test_renderer_output_unchanged(self) -> None:
    """A diagram drawn by ascii_flow_render.py is a fixed point."""
    drawn = afr.chain([{"lines": ["one"], "exit": "fails: x"}, {"lines": ["two", "three"]}], 30)
    self.assertEqual(fx.fix(drawn), (drawn, []))

  def test_grid_untouched(self) -> None:
    """A grid whose cells share edges, and a box with a grid divider, are not rewritten."""
    grid = ["+-----+-----+", "| a   | b   |", "+-----+-----+"]
    divided = ["+-----------+", "| head      |", "+-----+-----+", "| a   | b   |", "+-----+-----+"]
    self.assertEqual(fx.fix(grid)[0], grid)
    self.assertEqual(fx.fix(divided)[0], divided)

  def test_fan_out_branch_not_a_broken_box(self) -> None:
    """A branch line with bare `|` legs is not reported; a box that holds text and loses an edge is."""
    fan = ["        |", "   +----+----+", "   |         |", "  one       two"]
    broken = ["+--------+", "| text   |", "| more", "+--------+"]
    self.assertEqual(fx.edge_issues(fan), [])
    self.assertTrue(any("loses an edge" in x for x in fx.edge_issues(broken)))

  def test_words_never_change(self) -> None:
    """A fix that would alter the words is refused and the block returned as it was."""

    def lossy(lines: list[str], box: dict, w: int) -> None:
      """A broken redraw that drops a word.

      Args:
        lines: the diagram (changed in place).
        box: the box.
        w: unused width.

      Returns:
        None.
      """
      lines[box["rows"][0][0]] = "  | Release trial |"

    with mock.patch.object(fx, "redraw", lossy):
      out, problems = fx.fix(RAGGED)
    self.assertEqual(out, RAGGED)
    self.assertTrue(any("words" in p for p in problems), problems)


class Borders(unittest.TestCase):
  """Borders that carry connectors, and rows that shift what follows them."""

  def test_arrow_and_tee_on_border_kept(self) -> None:
    """A box entered by an arrow (`+--v--+`) and left by a tee (`+--+--+`) is repaired and keeps both."""
    lines = ["   |", "+--v-------+", "| ok       |", "| short   |", "+--+-------+", "   |"]
    out, problems = fx.fix(lines)
    self.assertEqual(problems, [])
    self.assertEqual(out[3], "| short    |")
    self.assertEqual((out[1], out[4]), (lines[1], lines[4]))

  def test_box_beside_a_short_row_moves_back(self) -> None:
    """A row one column short shifts the box beside it; closing the row puts that box back in line."""
    lines = ["+-------+  +-----+", "| one   |  | two |", "| x    |  | y   |", "+-------+  +-----+"]
    out, _ = fx.fix(lines)
    self.assertEqual(out[2], "| x     |  | y   |")


class Generated(unittest.TestCase):
  """A rendered file is never written: its diagram is fixed in the source."""

  def test_generated_file_not_written(self) -> None:
    """--apply on a file with a GENERATED banner leaves it unchanged and returns a problem."""
    with tempfile.TemporaryDirectory() as d:
      path = Path(d) / "doc.md"
      text = "<!-- GENERATED by `just x` -->\n\n```text\n" + "\n".join(RAGGED) + "\n```\n"
      path.write_text(text, encoding="utf-8")
      with redirect_stdout(io.StringIO()) as buf:
        self.assertEqual(fx.main([str(path), "--apply"]), 1)
      self.assertEqual(path.read_text(encoding="utf-8"), text)
      self.assertIn("generated", buf.getvalue())


class Stage1(unittest.TestCase):
  """Connector snapping and the extra checks (ascii/checks.py)."""

  def test_straying_connector_snapped(self) -> None:
    """A connector row one column off its run is moved back; a separate arrow far away is not."""
    lines = ["+------+", "| a    |", "+------+", "    |  label", "     |", "    v", "+------+", "| b    |", "+------+"]
    out, _ = fx.fix(lines)
    self.assertEqual([out[3][:5], out[4], out[5]], ["    |", "    |", "    v"])
    self.assertEqual(out[3], "    |  label")

  def test_arrow_missing_its_box_reported(self) -> None:
    """An arrowhead outside the corners of the box below is reported, one inside is not."""
    self.assertTrue(fx.checks.arrow_issues(["          v", "  +----+"]))
    self.assertEqual(fx.checks.arrow_issues(["     v", "  +----+"]), [])

  def test_wide_characters_and_tabs_reported(self) -> None:
    """Emoji and tabs cannot be aligned, so they are reported."""
    issues = fx.checks.text_issues(["| ok 🚀 |", "|\tx |"])
    self.assertEqual(len(issues), 2)
    self.assertTrue(fx.report(["+----+", "|\tx |", "+----+"]))
    self.assertEqual(fx.report(["Boot0004* SlotB\tHD(15,GPT)"]), [])  # command output in a text block, no box


class Package(unittest.TestCase):
  """The `ascii` package (scripts/ascii/__init__.py) imports from the scripts folder and says what it holds."""

  def test_package_imports_with_docstring(self) -> None:
    """The package the front ends share is importable and documented."""
    pkg = importlib.import_module("ascii")
    self.assertTrue(Path(pkg.__file__).match("scripts/ascii/__init__.py"))
    self.assertIn("ASCII diagrams", pkg.__doc__ or "")


class Files(unittest.TestCase):
  """The command reads Markdown fences, prints a diff, and writes only with --apply."""

  def test_markdown_dry_run_then_apply(self) -> None:
    """Without --apply the file is unchanged; with it the block is fixed and the prose kept."""
    with tempfile.TemporaryDirectory() as d:
      path = Path(d) / "doc.md"
      text = "# T\n\nprose |  stays\n\n```text\n" + "\n".join(RAGGED) + "\n```\n"
      path.write_text(text, encoding="utf-8")
      with redirect_stdout(io.StringIO()) as buf:
        self.assertEqual(fx.main([str(path)]), 0)
      self.assertIn("+++ fixed", buf.getvalue())
      self.assertEqual(path.read_text(encoding="utf-8"), text)
      with redirect_stdout(io.StringIO()):
        self.assertEqual(fx.main([str(path), "--apply"]), 0)
      fixed = path.read_text(encoding="utf-8")
      self.assertIn("prose |  stays", fixed)
      block = fixed.split("```text\n")[1].split("\n```")[0].split("\n")
      self.assertTrue(same_width(block, 2), block)


if __name__ == "__main__":
  unittest.main()
