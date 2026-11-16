"""Tests for scripts/ascii_flow_render.py ("ascii_flow_render"): boxes, chains, grids and columns keep their edges in line.

Run: `just test` (unittest, the pack's venv); read-only: strings and a temporary spec file. The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
afr = importlib.import_module("ascii_flow_render")


class Shapes(unittest.TestCase):
  """Every drawn line of a box has the same length, and edges line up."""

  def test_box_lines_equal_length(self) -> None:
    """A box pads every line to its width."""
    lines = afr.box(["a", "longer line"], 20)
    self.assertEqual({len(x) for x in lines}, {22})

  def test_box_refuses_overflow(self) -> None:
    """A line wider than the box is refused, not truncated (negative test)."""
    with self.assertRaises(ValueError):
      afr.box(["x" * 19], 20)

  def test_chain_arrows_and_exits(self) -> None:
    """Arrows sit under the box centre; an exit follows the first text line."""
    out = afr.chain([{"lines": ["one"], "exit": "fails: stop", "label": "next"}, {"lines": ["two"]}], 10, indent=0)
    self.assertTrue(out[1].endswith(" --> fails: stop"))
    self.assertEqual(out[3].index("|"), 1 + 10 // 2)
    self.assertEqual(out[4].index("v"), 1 + 10 // 2)
    self.assertIn("next", out[3])

  def test_grid_refuses_unequal_rows(self) -> None:
    """Rows of different spans are refused (negative test)."""
    with self.assertRaises(ValueError):
      afr.grid([[[10, ["a"]]], [[5, ["b"]], [5, ["c"]]]])

  def test_grid_edges_line_up(self) -> None:
    """Rows of equal span share their outer edges."""
    out = afr.grid([[[10, ["a"]], [9, ["b"]]], [[20, ["c"]]]])
    self.assertEqual({len(x) for x in out}, {22})

  def test_columns_side_by_side(self) -> None:
    """Columns are top-aligned and separated by the gap."""
    out = afr.render([{"columns": {"gap": 3, "parts": [{"box": {"width": 6, "lines": ["a"]}}, {"text": ["x"]}]}}])
    self.assertEqual(out[0], "+------+   x")

  def test_unknown_part_refused(self) -> None:
    """An unknown part kind is refused (negative test)."""
    with self.assertRaises(ValueError):
      afr.render([{"circle": {}}])


class Cli(unittest.TestCase):
  """The command line."""

  def test_exit_codes(self) -> None:
    """0 for a good spec, 1 for one that does not fit, 2 for an unreadable file."""
    with tempfile.TemporaryDirectory() as d:
      good, bad = Path(d, "good.json"), Path(d, "bad.json")
      good.write_text(json.dumps([{"box": {"width": 8, "lines": ["ok"]}}]))
      bad.write_text(json.dumps([{"box": {"width": 4, "lines": ["too wide"]}}]))
      self.assertEqual(afr.main([str(good)]), 0)
      self.assertEqual(afr.main([str(bad)]), 1)
      self.assertEqual(afr.main([str(Path(d, "missing.json"))]), 2)


if __name__ == "__main__":
  unittest.main()
