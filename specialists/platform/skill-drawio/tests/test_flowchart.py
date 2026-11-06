"""Tests for the regular flowchart page: the graph, the grid, the family chain, the audit on awkward shapes, and that it is opt-in."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from drawio.audit import faults, page_audit
from drawio.mxfile import Page as PageOf
from flowmap import model
from flowmap.flowchart.page import chart_page, short_text
from flowmap.route_costs import label_spot, on_lane_edge, too_close, with_under
from flowmap.flowchart.branches import _after_answer, _short, expand_branches
from flowmap.flowchart.graph import END, START, chart_graph, swap_branches, lane_columns, lane_map, layers, place, spine, stitched
from flowmap.flowchart.pages import _named, chart_flows, flowchart_pages
from flowmap.pages import named_pages
from flowmap.profile import Profile

#: The modules under test, for the contract test: "graph", "route", "page", "pages", "bpmn", "labels", "branches", "order", "lanes".
ROOT = Path(__file__).resolve().parents[1] / "examples" / "shop"
COMPS = {"c": {"id": "c", "name": "Comp", "kind": "service"}}


def step(sid: str, **kw) -> dict:
    """A step.

    Args:
        sid: its id.
        **kw: more keys.

    Returns:
        The step.
    """
    return {"id": sid, "actor": "c", "action": f"do {sid}", "via": ["SSH"], **kw}


def flow(steps: list[dict], fid: str = "f", kind: str = "command") -> dict:
    """A flow.

    Args:
        steps: its steps.
        fid: its id.
        kind: its trigger kind.

    Returns:
        The flow.
    """
    return {"id": fid, "title": "T", "purpose": "P", "trigger": {"kind": kind, "detail": "go"}, "steps": steps}


def profile() -> Profile:
    """The example's profile.

    Returns:
        The profile.
    """
    data = model.read_map(ROOT, "flows.yaml")
    return Profile.from_drawing(data, "flows.yaml", "", "test", "")


class Graph(unittest.TestCase):
    """Nodes, edges and rows."""

    def test_chain_has_start_and_end(self):
        """A plain flow gets both terminators."""
        g = chart_graph(flow([step("a"), step("b")]))
        self.assertEqual(g.order, [START, "a", "b", END])
        self.assertEqual(layers(g), {START: 0, "a": 1, "b": 2, END: 3})

    def test_terminator_step_needs_no_end(self):
        """A step that is the end draws no second end."""
        self.assertNotIn(END, chart_graph(flow([step("a", shape="terminator")])).order)

    def test_back_edge_is_by_map_order(self):
        """A retry goes back and the rows stay acyclic."""
        g = chart_graph(flow([step("a"), step("b", next=["a", "c"], gate="ok?"), step("c")]))
        self.assertEqual([e.kind for e in g.edges if e.src == "b"], ["back", "main"])
        self.assertLess(layers(g)["b"], layers(g)["c"])

    def test_failure_makes_a_stop_beside_its_step(self):
        """A stop box shares its step's row, one column right."""
        g = chart_graph(flow([step("a", failures=["boom"]), step("b")]))
        grid = place(g)
        self.assertEqual(grid.rows["__stop-a"], grid.rows["a"])
        self.assertEqual(grid.cols["__stop-a"], grid.cols["a"] + 1)

    def test_decision_with_two_ways_out_gets_no_stop(self):
        """Its failure path is already drawn."""
        g = chart_graph(flow([step("a", gate="ok?", next=["b", "c"], failures=["x"]), step("b"), step("c")]))
        self.assertEqual(g.stops, {})

    def test_spine_is_column_zero(self):
        """The main path runs straight down."""
        f = flow([step("a", gate="ok?", next=["b", "c"]), step("b", next=["d"]), step("c", next=["d"]), step("d")])
        g = chart_graph(f)
        grid = place(g)
        self.assertEqual({grid.cols[n] for n in spine(g)}, {0})
        self.assertGreater(grid.cols["c"], 0)

    def test_stitch_joins_ends_and_keeps_inner_branches(self):
        """A flow's last step leads to the next flow's first."""
        joined = stitched("x", [flow([step("a", gate="q", next=["b"], when={"b": "yes"}), step("b")], "one"), flow([step("c")], "two")])
        by_id = {s["id"]: s for s in joined["steps"]}
        self.assertEqual(by_id["one.b"]["next"], ["two.c"])
        self.assertEqual(by_id["one.a"]["when"], {"one.b": "yes"})


class Page(unittest.TestCase):
    """The drawn page."""

    def audit(self, steps: list[dict]) -> list[str]:
        """Audit a chart.

        Args:
            steps: the flow's steps.

        Returns:
            The faults.
        """
        return faults(page_audit(chart_page(flow(steps), COMPS, profile(), (set(), set()))))

    def test_long_skip_clear_of_boxes(self):
        """An arrow over several rows passes no box."""
        self.assertEqual(self.audit([step("a", gate="q", next=["b", "d"]), step("b"), step("c"), step("d")]), [])

    def test_loop_and_stop_together(self):
        """A retry beside a failure stays clean."""
        self.assertEqual(self.audit([step("a"), step("b", gate="ok?", next=["c", "a"]), step("c", failures=["boom"]), step("d")]), [])

    def test_three_way_decision_and_merge(self):
        """Three branches meet again without a fault."""
        steps = [step("a", shape="decision", next=["b", "c", "d"], when={"b": "one", "c": "two", "d": "three"}), step("b", next=["e"]), step("c", next=["e"]),
                 step("d", next=["e"]), step("e")]
        self.assertEqual(self.audit(steps), [])

    def test_label_wins_then_gate_then_cut_action(self):
        """A box's words."""
        self.assertEqual(short_text({"label": "L", "gate": "G", "action": "A"}), "L")
        self.assertEqual(short_text({"gate": "G", "action": "A"}), "G")
        self.assertTrue(short_text({"action": "word " * 30}).endswith(" ..."))


class Branches(unittest.TestCase):
    """A step's `branches` key."""

    FLOW = flow([step("a"), step("b", branches=[{"question": "Needed?", "outcomes": ["run: yes: do it", "skip: no: already there"]}]), step("c")])

    def test_diamond_before_the_step_routes_each_outcome(self):
        """Run goes in, skip goes past, and the arrow into the step meets the diamond."""
        steps = {s["id"]: s for s in expand_branches(self.FLOW)["steps"]}
        self.assertEqual(steps["b~0"]["next"], ["b", "c"])
        self.assertEqual(steps["b~0"]["when"], {"b": "yes", "c": "no"})
        self.assertEqual([s["id"] for s in expand_branches(self.FLOW)["steps"]], ["a", "b~0", "b", "c"])

    def test_stop_outcome_ends_there(self):
        """A stop is a terminator of its own."""
        f = flow([step("a", branches=[{"question": "Fit?", "outcomes": ["run: yes", "stop: no: refused"]}]), step("b")])
        steps = {s["id"]: s for s in expand_branches(f)["steps"]}
        self.assertEqual(steps["a~0-stop1"]["shape"], "terminator")
        self.assertEqual(steps["a~0"]["next"][0], "a")

    def test_an_explicit_next_is_redirected(self):
        """A step that points at a branched step reaches its diamond."""
        f = flow([step("a", next=["b"]), step("b", branches=[{"question": "Q?", "outcomes": ["run: yes", "stop: no"]}])])
        self.assertEqual(expand_branches(f)["steps"][0]["next"], ["b~0"])

    def test_outcomes_to_one_place_draw_nothing(self):
        """A split that goes nowhere different is no decision."""
        f = flow([step("a", branches=[{"question": "Q?", "outcomes": ["run: one", "run: two"]}]), step("b")])
        self.assertEqual([s["id"] for s in expand_branches(f)["steps"]], ["a", "b"])

    def test_two_branches_chain_and_the_audit_passes(self):
        """Two on one step stack, in every notation."""
        branches = [{"question": "One?", "outcomes": ["run: yes", "skip: no"]}, {"question": "Two?", "outcomes": ["run: yes", "stop: no"]}]
        f = [step("a"), step("b", branches=branches, failures=["x"]), step("c")]
        for mode in ("chart", "lanes", "bpmn"):
            self.assertEqual(faults(page_audit(chart_page(flow(f), COMPS, profile(), (set(), set()), mode))), [], mode)

    def test_map_without_branches_is_untouched(self):
        """No key, the same object."""
        f = flow([step("a")])
        self.assertIs(expand_branches(f), f)


class LeftSide(unittest.TestCase):
    """Arrows beside the main path."""

    def test_skip_and_retry_leave_by_the_left(self):
        """Both run beside the column and enter the target's side, and the audit passes."""
        f = flow([step("a"), step("b", gate="ok?", next=["c", "e"]), step("c"), step("d", gate="again?", next=["e", "a"]), step("e")])
        page = chart_page(f, COMPS, profile(), (set(), set()))
        self.assertEqual(faults(page_audit(page)), [])
        for r in page.routes:
            if r.cid.endswith(("b-e", "d-a")):
                x, _y, w, _h = page.rects[r.dst]
                self.assertIn(r.points[-1][0], (x, x + w))

    def test_lanes_keep_their_gutters(self):
        """A lane page has no left channel."""
        f = flow([step("a", gate="ok?", next=["b", "a"]), step("b")])
        self.assertEqual(faults(page_audit(chart_page(f, COMPS, profile(), (set(), set()), "lanes"))), [])


class Clearance(unittest.TestCase):
    """A label keeps off another arrow, not just off its line."""

    def spot(self, margin: float) -> float:
        """Where a label lands beside an arrow running just above where it would sit.

        Args:
            margin: `label_clearance`.

        Returns:
            The label's centre y.
        """
        page = PageOf("p", "P")
        page.label_clearance = margin
        page.box("a", "", 0, 0, 40, 40, "", solid=True)
        page.box("b", "", 600, 0, 40, 40, "", solid=True)
        page.route("other", "a", "b", [(40, 89), (600, 89)], "", "thin")
        return label_spot(page, "mine", [(40, 100), (600, 100)], 100, 20)[1]

    def test_zero_keeps_the_old_spot_and_a_margin_moves_it(self):
        """A line 1 px past the label passes at 0, and moves the label at 6."""
        self.assertEqual(self.spot(0), 100)
        self.assertNotEqual(self.spot(6), 100)


class RunSpacing(unittest.TestCase):
    """Parallel arrows keep apart."""

    def test_near_side_by_side_and_end_to_end(self):
        """Close beside, or one ending where the other starts in line."""
        self.assertTrue(too_close(((0, 0), (0, 100)), ((10, 50), (10, 200)), 30))
        self.assertTrue(too_close(((0, 0), (0, 100)), ((0, 120), (0, 300)), 30))

    def test_far_apart_or_crossing_is_fine(self):
        """Distance clears it, and a crossing is not parallel."""
        self.assertFalse(too_close(((0, 0), (0, 100)), ((40, 0), (40, 100)), 30))
        self.assertFalse(too_close(((0, 0), (0, 100)), ((0, 200), (0, 300)), 30))
        self.assertFalse(too_close(((0, 50), (100, 50)), ((50, 0), (50, 100)), 30))


class LaneEdge(unittest.TestCase):
    """A run keeps off a lane boundary."""

    def test_a_flat_run_near_an_edge_counts_and_others_do_not(self):
        """Close and flat counts; far, or vertical, does not."""
        self.assertTrue(on_lane_edge(((0, 100), (500, 100)), [105]))
        self.assertFalse(on_lane_edge(((0, 100), (500, 100)), [160]))
        self.assertFalse(on_lane_edge(((0, 0), (0, 500)), [100]))


class FreeBand(unittest.TestCase):
    """Tracks spread over the room there is."""

    def test_tracks_sit_across_the_free_band(self):
        """A band under the boxes gives tracks near its two edges, then its middle."""
        page = PageOf("p", "P")
        page.box("a", "", 0, 0, 100, 76, "", solid=True)
        page.lane_edges = [0, 300]
        ys = with_under(page, {"under": True, "ys": [], "xs": []}, (0, 0), (100, 0))["ys"]
        self.assertEqual([round(y) for y in ys[:3]], [130, 270, 200])


class Words(unittest.TestCase):
    """Short words on charts."""

    def test_outcome_on_an_arrow_cuts_at_a_word(self):
        """A clause boundary first, then a word."""
        self.assertEqual(_short("no (no apt_pin action)"), "no")
        self.assertEqual(_short("plain root or lower dir there"), "plain root or")

    def test_stop_box_drops_the_answer(self):
        """The arrow already says no."""
        self.assertEqual(_after_answer("no: refused, the host fails"), "Refused, the host fails")
        self.assertEqual(_after_answer("needs_repair, or resume off: refused"), "needs_repair, or resume off: refused")

    def test_chart_tab_names_the_page(self):
        """`look.chart_tab` replaces "Chart" in a flowchart page's tab; the default stays "Chart" (2026-11-06)."""
        f = flow([step("a"), step("b")])
        self.assertTrue(chart_page(f, COMPS, profile(), (set(), set())).name.startswith("Chart: "))
        named = replace(profile(), look={**profile().look, "chart_tab": "Step by step"})
        self.assertTrue(chart_page(f, COMPS, named, (set(), set())).name.startswith("Step by step: "))

    def test_a_refusal_end_does_not_lead_into_the_next_flow(self):
        """Stitched flows: the main path's end leads on, a step reached only through a gate's other way ends (2026-11-06)."""
        one = {"id": "f1", "steps": [step("a", gate="ok?", next=["b", "no"]), step("b", next=[]), step("no", next=[])]}
        two = {"id": "f2", "steps": [step("c")]}
        got = {s["id"]: s["next"] for s in stitched("fam", [one, two])["steps"]}
        self.assertEqual(got["f1.b"], ["f2.c"])
        self.assertEqual(got["f1.no"], [])

    def test_tabs_stay_unique(self):
        """Two flows with one title show their ids."""
        self.assertEqual([f["title"] for f in _named([{"id": "a", "title": "T"}, {"id": "b", "title": "T"}, {"id": "c", "title": "U"}])], ["a", "b", "U"])


class Lanes(unittest.TestCase):
    """Vertical swimlanes."""

    STEPS = [step("a"), step("b", actor="d", gate="ok?", next=["c", "a"], failures=["x"]), step("c", failures=["boom"]), step("e", actor="d"), step("f")]
    COMPS = {**COMPS, "d": {"id": "d", "name": "Other", "kind": "service"}}

    def test_each_node_stays_in_its_lane(self):
        """Every box of a lane, stops included, sits in its one column."""
        g = chart_graph(flow(self.STEPS))
        lanes, actors = lane_map(g)
        first = lane_columns(len(actors))
        grid = place(g, lanes, first)
        self.assertEqual(actors, ["c", "d"])
        for nid, lane in lanes.items():
            self.assertEqual(grid.cols[nid], first[lane], nid)   # one column of boxes: never side by side
        self.assertEqual(grid.rows["__stop-c"], grid.rows["c"] + 1)

    def test_one_actor_never_has_two_steps_on_a_row(self):
        """A branch into the same lane moves down."""
        f = flow([step("a", gate="q", next=["b", "c"]), step("b"), step("c")])
        g = chart_graph(f)
        lanes, _ = lane_map(g)
        rows = layers(g, lanes)
        self.assertNotEqual(rows["b"], rows["c"])

    def test_page_is_clean_with_a_lane_per_actor(self):
        """The audit passes, and each actor has a heading."""
        page = chart_page(flow(self.STEPS), self.COMPS, profile(), (set(), set()), "lanes")
        self.assertEqual(faults(page_audit(page)), [])
        self.assertEqual(page.page_id, "lanes-f")
        self.assertEqual(sum("-lane-head-" in cid for cid in page.rects), 2)


class Bpmn(unittest.TestCase):
    """BPMN notation."""

    def test_symbols_are_bpmn_and_the_audit_passes(self):
        """Start, end and error end events, a call activity, a gateway; every arrow solid."""
        steps = [step("a", gate="ok?", next=["b", "c"]), step("b", flow="other", failures=["boom"]), step("c", actor="d")]
        page = chart_page(flow(steps), Lanes.COMPS, profile(), (set(), set()), "bpmn")
        self.assertEqual(faults(page_audit(page)), [])
        xml = page.xml()
        for mark in ("outline=standard", "outline=end;symbol=general", "outline=end;symbol=error", "rhombus", "strokeWidth=3"):
            self.assertIn(mark, xml)
        self.assertEqual((page.page_id, page.name), ("bpmn-f", "BPMN: T"))
        self.assertIn(f"fillColor={profile().style('service')[0]}", xml)   # the actor's colour, as on the step pages
        self.assertFalse(any("dashed=1" in c for c in page.cells if 'edge="1"' in c))


class OptIn(unittest.TestCase):
    """The page exists only when a map asks."""

    def test_default_draws_none(self):
        """No key, no page, so consumers stay byte-identical."""
        data = model.read_map(ROOT, "flows.yaml")
        names = [n for _r, n, _p in named_pages(data, replace(profile(), look={**profile().look, "flowcharts": [], "swimlanes": [], "bpmn": []}))]
        self.assertFalse(any(n.startswith("Flowchart") for n in names))

    def test_all_and_a_family_chain(self):
        """`all` draws every flow; a family skips a flow started on its own."""
        data = model.read_map(ROOT, "flows.yaml")
        prof = replace(profile(), look={**profile().look, "flowcharts": "all", "swimlanes": [], "bpmn": []})
        self.assertEqual(len(flowchart_pages(data, prof, set())), len(data["flows"]))
        prof = replace(profile(), look={**profile().look, "flowcharts": ["family:orders"]})
        self.assertEqual(len(chart_flows(data, prof)), 1)

    def test_every_example_chart_is_clean(self):
        """The audit passes on every flow of the example."""
        data = model.read_map(ROOT, "flows.yaml")
        prof = replace(profile(), look={**profile().look, "flowcharts": "all"})
        self.assertEqual([f for p in flowchart_pages(data, prof, set()) for f in faults(page_audit(p))], [])

    def test_unknown_name_is_a_map_problem(self):
        """A typo in the list is refused."""
        data = model.read_map(ROOT, "flows.yaml")
        data["drawing"].setdefault("look", {})["flowcharts"] = ["nope", "family:nope"]
        problems = model.reference_problems(data, ROOT)
        self.assertEqual(sum("look.flowcharts" in p for p in problems), 2)


if __name__ == "__main__":
    unittest.main()
