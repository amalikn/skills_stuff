"""Tests for how a chart is arranged: measured diamond exits, lane order, sideways hand-offs and exits to the left; flowmap "lane_fold" and "step_text" too."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from drawio.audit import crossing, faults, page_audit, segments
from flowmap.flowchart.graph import chart_graph, lane_map, layers, place, swap_branches
from flowmap.flowchart.order import improve_branches, lane_cost, lane_order, score
from flowmap.flowchart.page import chart_page
from flowmap.lane_fold import foldable, snake
from flowmap.pages import flow_page
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


class LaneFold(unittest.TestCase):
    """A long run folds inside its own lane."""

    def steps(self) -> list:
        """One step, a long run by one actor, then one more.

        Returns:
            The steps.
        """
        return [step("a")] + [step(f"m{k}", actor="d") for k in range(7)] + [step("z")]

    def test_a_long_run_snakes_and_the_rest_keep_a_column(self):
        """Three rows of three, every second row running back."""
        place, rows = snake(self.steps(), 3)
        self.assertEqual(rows["d"], 3)
        self.assertEqual([place[k] for k in range(1, 8)], [(1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (1, 1), (1, 2)])
        self.assertEqual(place[8], (4, 0))

    def test_only_a_straight_flow_folds(self):
        """A branch keeps the normal page."""
        self.assertTrue(foldable(self.steps()))
        self.assertFalse(foldable([step("a", next=["c", "b"], gate="q"), step("b"), step("c")]))

    def test_each_lane_appears_once_and_the_audit_passes(self):
        """Two actors, two lanes, however long the run."""
        f = {**flow(self.steps()), "runs_on": "c", "owner": "c", "category": "x", "layout": {"fold": "lane", "fold_after": 3}}
        comps = {k: {**v, "host": "h", "health": "h", "group": "g"} for k, v in Lanes.COMPS.items()}
        page = flow_page(f, comps, 1, profile())
        self.assertEqual(sum(cid.startswith("f-lanehead-") for cid in page.rects), 2)
        self.assertEqual(faults(page_audit(page)), [])

    def test_a_branching_flow_is_left_alone(self):
        """It draws, unfolded."""
        f = {**flow([step("a", next=["c", "b"], gate="q"), step("b"), step("c")]), "runs_on": "c", "owner": "c", "category": "x", "layout": {"fold": "lane", "fold_after": 2}}
        comps = {k: {**v, "host": "h", "health": "h", "group": "g"} for k, v in COMPS.items()}
        self.assertEqual(faults(page_audit(flow_page(f, comps, 1, profile()))), [])


class LaneFoldExit(unittest.TestCase):
    """The arrow out of a folded lane stays inside the band."""

    def test_arrow_out_of_a_row_running_back_clears_the_lane_edge(self):
        """Its long run sits at least 20 px above the lane's bottom edge."""
        steps = [step(f"m{k}", actor="d") for k in range(4)] + [step("z")]
        f = {**flow(steps), "runs_on": "c", "owner": "c", "category": "x", "layout": {"fold": "lane", "fold_after": 2}}
        comps = {k: {**v, "host": "h", "health": "h", "group": "g"} for k, v in Lanes.COMPS.items()}
        page = flow_page(f, comps, 1, profile())
        out = next(r for r in page.routes if r.cid.endswith("m3-z"))
        lane = page.rects["f-lane-0"]
        self.assertLessEqual(out.points[1][1], lane[1] + lane[3] - 20)


class RouteUnder(unittest.TestCase):
    """A long branch can run below every box."""

    def page(self, under: bool) -> object:
        """A decision whose long branch would otherwise cross the arrows between two lanes.

        Args:
            under: `look.route_under`.

        Returns:
            The flow page.
        """
        steps = [step("a", gate="q", next=["b", "e"], when={"b": "yes", "e": "no"}, writes=["x"]), step("b", actor="d"), step("c"), step("d", actor="d"), step("e")]
        f = {**flow(steps), "runs_on": "c", "owner": "c", "category": "x"}
        comps = {k: {**v, "host": "h", "health": "h", "group": "g"} for k, v in Lanes.COMPS.items()}
        return flow_page(f, comps, 1, replace(profile(), look={**profile().look, "route_under": under}))

    def test_the_router_chooses_it_and_crosses_less(self):
        """With the track on, room is kept for it, crossings do not rise, and the audit passes."""
        def crossings(page: object) -> int:
            runs = [segments(r.points) for r in page.routes]
            return sum(crossing(s, t) is not None for i, a in enumerate(runs) for b in runs[i + 1:] for s in a for t in b)

        off, on = self.page(False), self.page(True)
        self.assertEqual(faults(page_audit(on)), [])
        self.assertLessEqual(crossings(on), crossings(off))
        notes = lambda page: min(r[1] for c, r in page.rects.items() if "-n-" in c)
        self.assertGreater(notes(on), notes(off))   # the track has its own room above the notes


class BothSides(unittest.TestCase):
    """Overlapping skips split left and right."""

    def test_two_overlapping_skips_take_a_side_each(self):
        """Nested spans go one each way, each entering its own side, and the audit passes."""
        f = flow([step("a", gate="p", next=["b", "e"]), step("b", gate="q", next=["c", "d"]), step("c"), step("d"), step("e")])
        chart_ = chart_page(f, COMPS, profile(), (set(), set()))
        self.assertEqual(faults(page_audit(chart_)), [])
        ends = {r.cid.rsplit("-", 2)[-2]: r for r in chart_.routes}
        boxes = chart_.rects
        left = min(p[0] for p in ends["b"].points) < boxes[ends["b"].src][0]
        right = max(p[0] for p in ends["a"].points) > boxes[ends["a"].src][0] + boxes[ends["a"].src][2]
        self.assertTrue(left and right)

    def test_a_label_is_bold_and_on_the_page_style(self):
        """Chart labels use the step pages' label."""
        f = flow([step("a", gate="p", next=["b", "c"]), step("b"), step("c")])
        self.assertIn("fontStyle=1", "".join(chart_page(f, COMPS, profile(), (set(), set())).cells))


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
        self.assertTrue(any(m.cid.endswith("-stop1-lbl") for m in page.marks))

    def test_spine_keeps_its_first_arrow(self):
        """When the first target is already straight below, nothing moves."""
        g = chart_graph(flow([step("a", gate="q", next=["b", "c"]), step("b"), step("c")]))
        grid = place(g)
        before = [(e.dst, e.index) for e in g.edges]
        swap_branches(g, grid)
        self.assertEqual([(e.dst, e.index) for e in g.edges], before)


if __name__ == "__main__":
    unittest.main()
