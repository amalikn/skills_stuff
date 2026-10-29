"""Offline tests for the placement searches (operator, 2026-10-28): overview_row_search, overview_group_search and e2e_row_search,
all in flowmap.placement, and the real-route guard on e2e_row_search (flowmap.e2e.routed_e2e, 2026-10-29).
Modules tested here (the contract test looks for each name): "placement".

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
pl = importlib.import_module("flowmap.placement")
e2e, profile = importlib.import_module("flowmap.e2e"), importlib.import_module("flowmap.profile")
EXAMPLE = ROOT / "examples" / "shop" / "flows.yaml"


class OverviewRowSearch(unittest.TestCase):
    """Boxes inside a group row are swapped only when that lowers row-to-row crossings."""

    def test_untangles_two_rows(self) -> None:
        """a->d and b->c cross when the bottom row is [c, d]; the search swaps them and the count drops to 0."""
        rows, chains = [["a", "b"], ["c", "d"]], [["a", "d"], ["b", "c"]]
        self.assertEqual(pl.row_crossings(rows, chains), 1)
        pl.row_search(rows, chains)
        self.assertEqual(pl.row_crossings(rows, chains), 0)


class GroupSearch(unittest.TestCase):
    """Unpinned groups move to the cells where the thick arrows cross least; pinned ones stay."""

    def test_reduces_cost_and_keeps_pins(self) -> None:
        """A 2x2 grid with crossing diagonals: the map's own placement comes first, a candidate is cheaper, the pinned group never moves."""
        cells = {"A": (0, 0), "B": (0, 1), "C": (1, 0), "D": (1, 1)}
        pairs = {("A", "D"): 1, ("B", "C"): 1}
        before = pl.group_cost(cells, pairs)
        cands = pl.group_candidates(cells, {"A"}, pairs, 2)
        self.assertEqual(cands[0], cells)
        self.assertLess(min(pl.group_cost(c, pairs) for c in cands), before)
        self.assertTrue(all(c["A"] == (0, 0) and len(set(c.values())) == 4 for c in cands))

    def test_segments_cross(self) -> None:
        """Proper crossings count; shared ends do not."""
        self.assertTrue(pl.segments_cross((0, 0), (1, 1), (0, 1), (1, 0)))
        self.assertFalse(pl.segments_cross((0, 0), (1, 1), (1, 1), (2, 0)))


class E2ERowSearch(unittest.TestCase):
    """The E2E grid count sees arcs inside one column, and the swap search lowers it."""

    def test_grid_crossings_and_search(self) -> None:
        """Two arcs in one column that interleave cross once; swapping rows separates them."""
        row = {"a": 0, "b": 1, "c": 2, "d": 3}
        colof = dict.fromkeys(row, 0)
        edges = [("a", "c"), ("b", "d")]
        self.assertEqual(pl.grid_crossings(edges, row, colof), 1)
        pl.column_search([["a", "b", "c", "d"]], row, colof, edges)
        self.assertEqual(pl.grid_crossings(edges, row, colof), 0)


class RealRouteGuards(unittest.TestCase):
    """A placement search result is kept only when its real routes are no worse (2026-10-29)."""

    def test_shared_runs(self) -> None:
        """Two lines along each other within 8 px count once; further apart, or only touching end to end, they do not."""
        self.assertEqual(pl.shared_runs([[(0, 50), (100, 50)], [(40, 54), (160, 54)]]), 1)
        self.assertEqual(pl.shared_runs([[(0, 50), (100, 50)], [(0, 70), (100, 70)], [(100, 50), (140, 50)]]), 0)

    def test_e2e_search_never_worse_than_barycentre(self) -> None:
        """With e2e_row_search on, the page kept has no more real crossings than the barycentre order's."""
        data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
        data["drawing"]["look"] = {**(data["drawing"].get("look") or {}), "e2e_row_search": True}
        on = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        off = profile.Profile.from_drawing({**data, "drawing": {**data["drawing"], "look": {**data["drawing"]["look"], "e2e_row_search": False}}},
                                           "flows.yaml", "s.json", "g")
        kept, plain = e2e.routed_e2e(data, on), e2e.EndToEnd(data, off)
        self.assertLessEqual(kept._crossings(set(kept.segs)), plain._crossings(set(plain.segs)))
        self.assertIs(kept.profile, on)


if __name__ == "__main__":
    unittest.main()
