"""Offline tests for flowmap.crossing_search: the End-to-end local search with joint port-and-track moves (2026-10-26). A page never ends with
more crossings than the plain search left it, and an out-and-back pair between two boxes stops crossing when an order allows it.

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


if __name__ == "__main__":
    unittest.main()
