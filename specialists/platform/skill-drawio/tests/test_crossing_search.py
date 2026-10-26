"""Offline tests for flowmap.crossing_search: the End-to-end local search with joint port-and-track moves (2026-10-26). A page never ends with
more crossings than the plain search left it, and an out-and-back pair between two boxes stops crossing when an order allows it. Row
moves: a far link that crosses another whatever the order runs along its target's row instead when that row is free.

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
e2e, moves, profile = (importlib.import_module(f"flowmap.{n}") for n in ("e2e", "crossing_search", "profile"))
EXAMPLE = ROOT / "examples" / "shop" / "flows.yaml"
FIXTURE = ROOT / "tests" / "fixtures" / "crossing_search.yaml"
ROW_FIXTURE = ROOT / "tests" / "fixtures" / "row_move.yaml"


def _grid(data: dict, joint: bool) -> object:
    """The End-to-end page of a map, improved with or without joint moves.

    Args:
        data: the map.
        joint: whether improve() may keep the joint-move run.

    Returns:
        The laid-out page (EndToEnd).
    """
    real = moves._search
    if not joint:
        moves._search = lambda grid, _joint: real(grid, False)
    try:
        return e2e.EndToEnd(data, profile.Profile.from_drawing(data, "flows.yaml", "s", "g"))
    finally:
        moves._search = real


def _total(grid: object) -> int:
    """Every crossing on the page.

    Args:
        grid: the laid-out page.

    Returns:
        The count.
    """
    return grid._crossings({link.cid for link in grid.links})


def _out_and_back() -> dict:
    """The shop map plus a flow that goes from one box to another and straight back, among the other flows.

    Returns:
        The map.
    """
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    first = data["flows"][0]
    src, dst = first["runs_on"], next(s["actor"] for s in first["steps"] if s["actor"] != first["runs_on"])
    data["flows"].insert(0, {"id": "ping", "title": "Ping", "category": first["category"], "purpose": "out and back",
                             "trigger": {"kind": "manual", "detail": "x"}, "runs_on": src, "owner": src,
                             "steps": [{"id": "ask", "actor": dst, "action": "ask", "via": ["x"]},
                                       {"id": "reply", "actor": src, "action": "reply", "via": ["x"]}]})
    return data


class JointMoves(unittest.TestCase):
    """improve(): never worse than the plain search; the joint move clears an out-and-back crossing; a two-track channel move helper."""

    def test_never_worse_than_plain(self) -> None:
        """On the example and on the example with an out-and-back flow, the kept run has no more crossings than the plain one."""
        for data in (yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")), _out_and_back()):
            self.assertLessEqual(_total(_grid(data, True)), _total(_grid(data, False)))

    def test_joint_moves_cut_crossings_where_plain_swaps_stop(self) -> None:
        """On the fixture the plain search stops with crossings a joint move removes: the kept run has strictly fewer."""
        data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        self.assertLess(_total(_grid(data, True)), _total(_grid(data, False)))

    def test_moved_next_to_keeps_the_rest_in_order(self) -> None:
        """Track 3 moved beside track 0: the other tracks keep their relative order, and both sides are offered."""
        slots = [0, 1, 2, 3]
        got = moves.moved_next_to(slots, 3, 0)
        self.assertIn([1, 2, 3, 0], got)   # 3 left of 0
        self.assertIn([0, 2, 3, 1], got)   # 3 right of 0
        for perm in got:
            order = sorted(range(4), key=perm.__getitem__)
            self.assertEqual([t for t in order if t != 3], [0, 1, 2])

    def test_only_a_crossing_pair_is_tried(self) -> None:
        """A pair of ports whose links do not cross each other is left alone (keeps the search fast)."""
        grid = _grid(yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")), True)
        for users in grid.pools.values():
            for i in range(len(users) - 1):
                a, b = users[i][0], users[i + 1][0]
                if a != b and not moves.count_crossings(grid.segs[a], grid.segs[b]):
                    before = [u[:] for u in grid.pools.values()]
                    self.assertFalse(moves.port_and_tracks(grid, users, i))
                    self.assertEqual(before, [u[:] for u in grid.pools.values()])
                    return
        self.skipTest("every neighbouring pair crosses")


class RowMoves(unittest.TestCase):
    """row_move: the PHP page's user-to-portal link runs along the portal's row and stops crossing the role's link to the portal."""

    def _link(self, grid: object, src: str, dst: str) -> object:
        """The step arrow from one component to another.

        Args:
            grid: the laid-out page.
            src: the source component id.
            dst: the target component id.

        Returns:
            The link.
        """
        return next(x for x in grid.links if x.klass == "thick" and (x.src, x.dst) == (src, dst))

    def test_user_link_runs_along_the_portal_row(self) -> None:
        """With row moves the user's link is a row link, crosses the role's link no more, and the page has fewer crossings than without."""
        data = yaml.safe_load(ROW_FIXTURE.read_text(encoding="utf-8"))
        grid = _grid(data, False)
        user, role = self._link(grid, "wifi-user", "portal"), self._link(grid, "role", "portal")
        self.assertEqual(user.kind, "row")
        self.assertEqual(moves.count_crossings(grid.segs[user.cid], grid.segs[role.cid]), 0)
        real = moves.row_free
        moves.row_free = lambda _grid, _link: False
        try:
            without = _grid(yaml.safe_load(ROW_FIXTURE.read_text(encoding="utf-8")), False)
        finally:
            moves.row_free = real
        self.assertLess(_total(grid), _total(without))

    def test_laid_out_again_with_a_row_link(self) -> None:
        """Sizing again (as loops do) after a row move gives every link its runs back, and the search runs again without error."""
        grid = _grid(yaml.safe_load(ROW_FIXTURE.read_text(encoding="utf-8")), True)
        grid._size()
        grid._improve()
        self.assertTrue(all(link.cid in grid.pts for link in grid.links))

    def test_row_needs_a_free_row(self) -> None:
        """A far link whose target row has a box in a column it passes is never made a row link."""
        grid = _grid(yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")), True)
        for link in grid.links:
            if link.kind in ("far", "row"):
                (cs, _r), (ct, rt) = grid.cell[link.src], grid.cell[link.dst]
                lo, hi = sorted((cs, ct))
                if any(lo < col < hi and r == rt for c, (col, r) in grid.cell.items() if c != link.dst):
                    self.assertFalse(moves.row_free(grid, link))
                    self.assertEqual(link.kind, "far")


class InColumnLinks(unittest.TestCase):
    """A link between two boxes in one column always uses the channel on that column's right, the last column's too (operator, 2026-10-26)."""

    def test_in_column_links_go_right(self) -> None:
        """On the example and the row fixture every in-column link leaves and enters by the right side, through its own column's channel."""
        for path in (EXAMPLE, ROW_FIXTURE):
            grid = _grid(yaml.safe_load(path.read_text(encoding="utf-8")), True)
            inside = [x for x in grid.links if grid.cell[x.src][0] == grid.cell[x.dst][0]]
            for link in inside:
                col = grid.cell[link.src][0]
                self.assertEqual((link.exit[0], link.exit[2], link.entry[2]), (col, "R", "R"), link.cid)
            if any(grid.cell[x.src][0] == grid.ncol - 1 for x in inside):
                self.assertEqual(grid.nch, grid.ncol)


if __name__ == "__main__":
    unittest.main()
