"""Offline tests for the Overview's per-group grid of unlinked boxes: `drawing.group_layout` and `drawing.group_columns` (flowmap.profile) and
how flowmap.overview_layout places the boxes.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
profile = importlib.import_module("flowmap.profile")
overview_layout = importlib.import_module("flowmap.overview_layout")


class GroupLayout(unittest.TestCase):
    """group_layout and group_columns: parsing, merging, refusing, and the rows they give."""

    def test_group_layout_and_columns(self) -> None:
        """group_layout reads vertical, horizontal and grid N; it merges with group_columns; a group in both, or a bad value, is refused."""
        self.assertEqual([profile.layout_columns(s) for s in ("vertical", "horizontal", "grid 2")], [1, 0, 2])
        for bad in ("down", "grid 0", "grid x", "grid"):
            with self.assertRaises(ValueError):
                profile.layout_columns(bad)
        self.assertEqual(profile.group_columns({"group_columns": {"A": 1}, "group_layout": {"B": "horizontal"}}), {"A": 1, "B": 0})
        with self.assertRaises(ValueError):
            profile.group_columns({"group_columns": {"A": 1}, "group_layout": {"A": "vertical"}})

    def test_group_layout_places_unlinked_boxes(self) -> None:
        """Unlinked boxes: one per row when vertical, all in one row when horizontal, rows of N for grid N."""
        same = {c: [] for c in "abcd"}
        self.assertEqual(overview_layout._rows_and_chains(list("abcd"), same, 1)[0], [["a"], ["b"], ["c"], ["d"]])
        self.assertEqual(overview_layout._rows_and_chains(list("abcd"), same, 0)[0], [list("abcd")])
        self.assertEqual(overview_layout._rows_and_chains(list("abcd"), same, 2)[0], [["a", "b"], ["c", "d"]])
        self.assertEqual(overview_layout._rows_and_chains(list("abcd"), same)[0], [["a", "b", "c"], ["d"]])



if __name__ == "__main__":
    unittest.main()
