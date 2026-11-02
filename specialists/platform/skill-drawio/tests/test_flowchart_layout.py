"""Tests for how a chart is arranged: measured diamond exits, lane order, sideways hand-offs and exits to the left."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from drawio.audit import faults, page_audit
from flowmap.flowchart.graph import chart_graph, lane_map, layers, place, swap_branches
from flowmap.flowchart.order import improve_branches, lane_cost, lane_order, score
from flowmap.flowchart.page import chart_page
from test_flowchart import COMPS, Lanes, flow, profile, step


class Turned(unittest.TestCase):
    """Lanes run left to right by default."""

    F = flow([step("a"), step("b", actor="d", gate="ok?", next=["c", "a"], failures=["x"]), step("c", failures=["boom"]), step("e", actor="d"), step("f")])

    def test_horizontal_is_the_default_and_clean(self):
        """Later steps sit further right, lanes stack down, and the audit passes in both notations."""
        for mode in ("lanes", "bpmn"):
            page = chart_page(self.F, Lanes.COMPS, profile(), (set(), set()), mode)
            self.assertEqual(faults(page_audit(page)), [], mode)
            a, c = page.rects[f"{mode}-f-c-a"], page.rects[f"{mode}-f-c-c"]
            self.assertGreater(c[0], a[0])
            self.assertLess(page.rects[f"{mode}-f-lane-head-0"][2], page.rects[f"{mode}-f-lane-head-0"][3])

    def test_a_vertical_entry_keeps_the_page_upright(self):
        """The heading sits along the top, and the suffix is valid in a map."""
        page = chart_page({**self.F, "_vertical": True}, Lanes.COMPS, profile(), (set(), set()), "lanes")
        self.assertGreater(page.rects["lanes-f-lane-head-0"][2], page.rects["lanes-f-lane-head-0"][3])

    def test_a_box_keeps_its_shape_when_turned(self):
        """Turning moves a box; it does not lie down."""
        upright = chart_page({**self.F, "_vertical": True}, Lanes.COMPS, profile(), (set(), set()), "lanes").rects["lanes-f-c-a"]
        turned = chart_page(self.F, Lanes.COMPS, profile(), (set(), set()), "lanes").rects["lanes-f-c-a"]
        self.assertEqual(upright[2:], turned[2:])


class Order(unittest.TestCase):
    """A diamond's exits are chosen by measure."""

    def test_score_counts_a_crossing_first(self):
        """A crossing outweighs any length."""
        cross = [[(0, 5), (10, 5)], [(5, 0), (5, 10)]]
        apart = [[(0, 0), (900, 0)], [(0, 9), (900, 9)]]
        self.assertLess(score(apart), score(cross))

    def test_keeps_the_better_way_round(self):
        """A swap that scores better stays; asked again, it stays too."""
        g = chart_graph(flow([step("a", gate="q", next=["b", "c"]), step("b"), step("c")]))
        worse = [[(0, 5), (10, 5)], [(5, 0), (5, 10)]]
        better = [[(0, 0), (1, 0)]]
        draw = lambda: better if next(e for e in g.edges if e.dst == "b").index == 1 else worse
        improve_branches(g, draw)
        self.assertEqual(next(e for e in g.edges if e.dst == "b").index, 1)
        improve_branches(g, draw)
        self.assertEqual(next(e for e in g.edges if e.dst == "b").index, 1)


class LaneOrder(unittest.TestCase):
    """Columns chosen for short hand-offs."""

    def test_neighbours_end_up_side_by_side(self):
        """A talks to C most, so C comes next; A stays first."""
        hops = [("a", "c"), ("c", "a"), ("a", "c"), ("c", "b")]
        self.assertEqual(lane_order(["a", "b", "c"], hops), ["a", "c", "b"])

    def test_a_tie_keeps_first_use(self):
        """No hops, no change."""
        self.assertEqual(lane_order(["a", "b", "c"], []), ["a", "b", "c"])

    def test_many_lanes_still_improve(self):
        """Past the exhaustive limit, swaps never make it worse."""
        actors = [f"x{k}" for k in range(10)]
        hops = list(zip(actors, actors[5:] + actors[:5]))
        self.assertLessEqual(lane_cost(lane_order(actors, hops), hops), lane_cost(actors, hops))


class LeftExit(unittest.TestCase):
    """A hand-off to a lane on the left leaves by the left."""

    def test_step_with_a_stop_heads_left_without_crossing_it(self):
        """The arrow leaves the box's left side, and the audit passes."""
        f = flow([step("a", failures=["x"]), step("b", actor="d", failures=["boom"]), step("c")])
        page = chart_page({**f, "_vertical": True}, Lanes.COMPS, profile(), (set(), set()), "lanes")
        self.assertEqual(faults(page_audit(page)), [])
        out = next(r for r in page.routes if r.cid.endswith("-b-c"))
        self.assertEqual(out.points[0][0], page.rects[out.src][0])
        self.assertLess(out.points[1][0], out.points[0][0])


class Sideways(unittest.TestCase):
    """A plain hand-off to the right runs level."""

    def test_hand_off_stays_on_the_row_and_the_audit_passes(self):
        """The next actor sits level, and a step back to the left goes below."""
        f = flow([step("a"), step("b", actor="d"), step("c")])
        g = chart_graph(f)
        lanes, _ = lane_map(g)
        rows = layers(g, lanes)
        self.assertEqual(rows["a"], rows["b"])
        self.assertGreater(rows["c"], rows["b"])
        self.assertEqual(faults(page_audit(chart_page({**f, "_vertical": True}, Lanes.COMPS, profile(), (set(), set()), "lanes"))), [])

    def test_a_decision_hands_off_downward(self):
        """Two ways out need the room below."""
        g = chart_graph(flow([step("a", gate="q", next=["b", "c"]), step("b", actor="d"), step("c")]))
        lanes, _ = lane_map(g)
        self.assertGreater(layers(g, lanes)["b"], layers(g, lanes)["a"])

    def test_a_stop_blocks_the_row(self):
        """A step with a stop keeps its arrow in the gutter."""
        g = chart_graph(flow([step("a", failures=["x"]), step("b", actor="d")]))
        lanes, _ = lane_map(g)
        self.assertGreater(layers(g, lanes)["b"], layers(g, lanes)["a"])


class BranchSwap(unittest.TestCase):
    """A diamond's arrow to the box below it goes straight down."""

    def test_stop_under_a_diamond_is_reached_straight_down(self):
        """In a lane the stop sits under the diamond, so its arrow leaves by the bottom and keeps its words."""
        f = flow([step("a", branches=[{"question": "Fit?", "outcomes": ["run: yes", "stop: no: refused"]}]), step("b", actor="d")])
        page = chart_page({**f, "_vertical": True}, Lanes.COMPS, profile(), (set(), set()), "lanes")
        self.assertEqual(faults(page_audit(page)), [])
        down = next(r for r in page.routes if r.cid.endswith("-stop1"))
        self.assertEqual(down.points[0][0], down.points[-1][0])
        self.assertTrue(any(m.cid.endswith("-stop1-t") for m in page.marks))

    def test_spine_keeps_its_first_arrow(self):
        """When the first target is already straight below, nothing moves."""
        g = chart_graph(flow([step("a", gate="q", next=["b", "c"]), step("b"), step("c")]))
        grid = place(g)
        before = [(e.dst, e.index) for e in g.edges]
        swap_branches(g, grid)
        self.assertEqual([(e.dst, e.index) for e in g.edges], before)


if __name__ == "__main__":
    unittest.main()
