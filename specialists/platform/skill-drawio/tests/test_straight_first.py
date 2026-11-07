"""Offline tests for straight-first routing and diamond-aware label spots (flowmap.routing.straight_first, flowmap.route_costs.near_box; operator
review 2026-11-07, smc-resiliency commission-gps: "4 on the right of 3, not on the top; 5 at the bottom of 3, not on the right", and a branch
label pushed above its arrow onto a lane edge).

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pages, routing, costs = (importlib.import_module(f"flowmap.{n}") for n in ("pages", "routing", "route_costs"))
TestMap = importlib.import_module("test_layout_rules")
FIXTURE = ROOT / "tests" / "fixtures" / "commission_gps.yaml"


def _side(pt: tuple, rect: tuple) -> str:
    """Which side of a box a route's first point leaves by.

    Args:
        pt: the point.
        rect: the box.

    Returns:
        "right", "top", "bottom" or "left".
    """
    x, y, w, h = rect
    return "right" if abs(pt[0] - x - w) < .5 else "left" if abs(pt[0] - x) < .5 else "top" if abs(pt[1] - y) < .5 else "bottom"


def _commissioning(look: dict) -> tuple:
    """Render the commissioning-shaped page and read how the first gate's two branches leave it.

    Args:
        look: drawing look keys.

    Returns:
        (the next-step branch is one straight run out of the right, the skipping branch's exit side, the page).
    """
    import yaml   # the pack's test venv has PyYAML, as a map is read at the edge
    data = yaml.safe_load(FIXTURE.read_text())
    data["drawing"] = {"look": {**data.get("drawing", {}).get("look", {}), **look}}
    comps = {c["id"]: c for c in data["components"]}
    page = pages.flow_page(data["flows"][0], comps, 1, TestMap._profile(data))
    routes = {r.cid: r for r in page.routes}
    fid = data["flows"][0]["id"]
    near, skip = routes[f"{fid}-e-register-probe-old"], routes[f"{fid}-e-register-record"]
    reg = page.rects[f"{fid}-s-register"]
    return routing.straight(near.points) and _side(near.points[0], reg) == "right", _side(skip.points[0], reg), page


class StraightFirstTests(unittest.TestCase):
    """A decision's branch to the step beside it goes straight across; the other branch goes round."""

    def test_next_step_branch_runs_straight_and_the_skip_leaves_the_bottom(self) -> None:
        """With the default look, 3 -> 4 is one run out of 3's right and 3 -> 5 leaves 3's bottom."""
        straight, skip_side, _page = _commissioning({})
        self.assertTrue(straight)
        self.assertEqual(skip_side, "bottom")

    def test_the_rule_can_fail(self) -> None:
        """With `straight_first: off` the old order returns: the page is no longer the operator's layout, so the test above can fail."""
        straight, skip_side, _page = _commissioning({"straight_first": "off"})
        self.assertNotEqual((straight, skip_side), (True, "bottom"))

    def test_straight_needs_one_line(self) -> None:
        """One horizontal or one vertical run is straight; a bend is not."""
        self.assertTrue(routing.straight([(0, 5), (10, 5), (20, 5)]))
        self.assertTrue(routing.straight([(3, 0), (3, 40)]))
        self.assertFalse(routing.straight([(0, 0), (10, 0), (10, 10)]))


class DiamondLabelTests(unittest.TestCase):
    """A label beside a decision is judged by the diamond's outline, not the rectangle around it."""

    @staticmethod
    def _page(style: str) -> SimpleNamespace:
        """A page holding one 200 x 100 box at the origin.

        Args:
            style: its cell style.

        Returns:
            The page.
        """
        return SimpleNamespace(rects={"d": (0, 0, 200, 100)}, cell_style={"d": style})

    def test_corner_region_is_clear_of_a_diamond(self) -> None:
        """A label in the empty top-right corner meets the rectangle but not the diamond."""
        label = (150, 0, 30, 10)
        self.assertFalse(costs.near_box(label, self._page("rhombus;"), "d"))
        self.assertTrue(costs.near_box(label, self._page("rounded=1;"), "d"))

    def test_label_on_the_diamond_meets_it(self) -> None:
        """A label over the diamond's middle, or just past its right corner within LABEL_GAP, meets it."""
        self.assertTrue(costs.near_box((90, 40, 20, 20), self._page("rhombus;"), "d"))
        self.assertTrue(costs.near_box((203, 45, 20, 10), self._page("rhombus;"), "d"))

    def test_label_keeps_off_lane_edges(self) -> None:
        """No branch label on the commissioning page straddles a lane edge."""
        page = _commissioning({})[2]
        edges = getattr(page, "lane_edges", [])
        self.assertTrue(edges)
        for m in page.marks:
            if m.cid.endswith(("-lbl", "-lbl-case")):
                y, h = m.rect[1], m.rect[3]
                self.assertFalse(any(y < e < y + h for e in edges), m.cid)


if __name__ == "__main__":
    unittest.main()
