"""Tests for scripts/ascii_fix.py ("ascii_fix"): an existing ASCII diagram is repaired at its edges and nothing else moves.

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
