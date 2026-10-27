"""Offline tests for flow page routing (flowmap.routing, "routing", 2026-10-21): a decision's branches read Yes and No or the step's own
cases, and a crowded page (two gates in one lane, skips into another lane) routes every forward arrow clear of boxes with no two runs alongside.

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

audit = importlib.import_module("drawio.audit")
router, pages, lanes = (importlib.import_module(f"flowmap.{n}") for n in ("routing", "pages", "lanes"))
TestMap = importlib.import_module("test_layout_rules")
costs = importlib.import_module("flowmap.route_costs")   # "route_costs"


def _crowded() -> dict:
    """A map shaped like smc-resiliency's commissioning flow: two gates in one lane, a skip over each, a skip into the next lane.

    Returns:
        The map.
    """
    data = TestMap._minimal()
    data["flows"][0]["steps"] = [
        {"id": "reg", "actor": "a", "action": "x", "via": ["API"], "gate": "g1", "next": ["rec", "probe"]},
        {"id": "probe", "actor": "a", "action": "x", "via": ["SSH"], "gate": "g2", "next": ["ref", "rec"]},
        {"id": "rec", "actor": "a", "action": "x", "via": ["API"], "next": ["fetch"]},
        {"id": "ref", "actor": "a", "action": "x", "via": ["API"], "next": []},
        {"id": "fetch", "actor": "b", "action": "x", "via": ["API"]}]
    return data


class RouteCostTests(unittest.TestCase):
    """Overshoot into a box on the right, and leaving a source's top or bottom toward it (operator review 2026-10-26)."""

    SRC, DST = (0, 0, 100, 60), (200, 300, 100, 60)

    def test_overshoot(self) -> None:
        """A flat run past the target's left edge into its top counts; a left entry or a target not wholly right does not."""
        over = [((100, 30), (250, 30)), ((250, 30), (250, 300))]
        turn = [((100, 30), (150, 30)), ((150, 30), (150, 330)), ((150, 330), (200, 330))]
        self.assertTrue(costs.overshoot(over, "top", self.SRC, self.DST))
        self.assertFalse(costs.overshoot(turn, "left", self.SRC, self.DST))
        self.assertFalse(costs.overshoot(over, "top", self.SRC, (50, 300, 100, 60)))

    def test_leaves_off_side(self) -> None:
        """Leaving top or bottom toward a box wholly right counts, unless the source is a multi-branch decision."""
        rects = {"s": self.SRC, "d": self.DST}
        self.assertTrue(costs.leaves_off_side("top", ("s", "d"), rects, {"branchy": set()}))
        self.assertFalse(costs.leaves_off_side("right", ("s", "d"), rects, {"branchy": set()}))
        self.assertFalse(costs.leaves_off_side("top", ("s", "d"), rects, {"branchy": {"s"}}))


class FlowRouterTests(unittest.TestCase):
    """The router's contract."""

    def test_branch_labels(self) -> None:
        """A two-way gate's branches read Yes (green) then No (red); `when` names other cases; a plain step and `branch_labels: off` keep the number."""
        gate = {"gate": "g", "next": ["a", "b"]}
        self.assertEqual(router.branch_label(gate, "a", 4, {}), ("4\nYes", router.YES))   # yes/no branches green and red
        self.assertEqual(router.branch_label(gate, "b", 5, {}), ("5\nNo", router.NO))
        self.assertEqual(router.branch_label(dict(gate, when={"b": "stale"}), "b", 5, {}), ("5\nstale", router.PLAIN))
        self.assertEqual(router.branch_label({"next": ["a"]}, "a", 2, {}), ("2", router.PLAIN))
        self.assertEqual(router.branch_label(gate, "a", 4, {"branch_labels": "off"}), ("4", router.PLAIN))
        shaped = {"shape": "decision", "next": ["a", "b"], "when": {"a": "overlay Pi"}}   # a decision by shape, no gate
        self.assertEqual(router.branch_label(shaped, "a", 3, {}), ("3\noverlay Pi", router.PLAIN))
        self.assertEqual(router.branch_label(shaped, "b", 4, {}), ("4\nNo", router.NO))

    def test_two_line_label_size(self) -> None:
        """A branch label is as wide as its longest line and one line taller per line below the number."""
        self.assertEqual(router.label_size("9"), (27, 22))
        self.assertEqual(router.label_size("9\nstill busy"), (18 + 9 * 10, 37))

    def test_unshare_parts_arrows_at_one_decision_corner(self) -> None:
        """Two arrows ending at one decision corner are found as a pair; arrows at different corners or at a plain box are not."""
        from types import SimpleNamespace as Route
        unc = importlib.import_module("flowmap.uncross")
        drawn = {c: None for c in ("a", "b", "c", "d")}
        page = SimpleNamespace(routes=[Route(cid="a", src="s1", dst="dia", points=[(0, 0), (100, 50)]),
                                       Route(cid="b", src="s2", dst="dia", points=[(0, 90), (100, 50)]),
                                       Route(cid="c", src="s3", dst="dia", points=[(0, 10), (150, 0)]),
                                       Route(cid="d", src="s4", dst="box", points=[(0, 10), (150, 0)])])
        self.assertEqual(unc._shared_corners(page, drawn, {"dia"}), [("a", "b")])
        self.assertEqual(unc._shared_corners(page, drawn, set()), [])

    def test_alongside_counts_shared_runs_not_crossings(self) -> None:
        """Two arrows sharing a run count as alongside; two that only cross do not."""
        unc = importlib.import_module("flowmap.uncross")
        page = SimpleNamespace(routes=[SimpleNamespace(points=[(0, 50), (100, 50)]), SimpleNamespace(points=[(40, 52), (160, 52)]),
                                       SimpleNamespace(points=[(70, 0), (70, 120)])])
        self.assertEqual(unc._alongside(page), 1)
        self.assertEqual(unc._crossings(page), 2)

    def test_lane_head_symbol_sized_to_text(self) -> None:
        """lanes: an external (cloud) lane head needs room for its text; a plain head needs none."""
        data = TestMap._minimal()
        prof = TestMap._profile(data)
        cloud = {"id": "x", "name": "Setup menu", "kind": "external", "host": "a long host description that wraps", "health": "ok"}
        self.assertGreater(lanes.head_symbol_h(cloud, prof), 60)
        self.assertEqual(lanes.head_symbol_h(dict(cloud, kind="service"), prof), 0)

    def test_crowded_page_routes_clean(self) -> None:
        """Every forward arrow avoids the boxes, no two runs lie alongside, and the page's layout audit is clean."""
        data = _crowded()
        prof = TestMap._profile(data)
        comps = {c["id"]: c for c in data["components"]}
        page = pages.flow_page(data["flows"][0], comps, 1, prof)
        self.assertEqual(audit.faults(audit.page_audit(page)), [])
        segs = {r.cid: audit.segments(r.points) for r in page.routes}
        ids = sorted(segs)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                self.assertFalse(any(router._along(s, t) for s in segs[a] for t in segs[b]), f"{a} runs alongside {b}")


    def test_flipped_target_port_mirrored(self) -> None:
        """An arrow into the top of a flipV shape is written with entryY=1, because draw.io mirrors ports on a flipped shape."""
        mx = importlib.import_module("drawio.mxfile")
        page = mx.Page("p", "P")
        page.box("a", "", 0, 0, 100, 50, "rounded=0;")
        page.box("b", "", 200, 200, 100, 50, "shape=trapezoid;flipV=1;")
        page.route("e", "a", "b", [(100, 25), (250, 25), (250, 200)], "edgeStyle=none;")
        self.assertIn("entryY=1;", page.cells[-1])

    def test_flow_quality_counts_a_clean_page(self) -> None:
        """flow_quality: the crowded page has no faults, crossings or shared starts."""
        fq = importlib.import_module("flow_quality")
        data = _crowded()
        q = fq.page_quality(pages.flow_page(data["flows"][0], {c["id"]: c for c in data["components"]}, 1, TestMap._profile(data)))
        self.assertEqual((q["faults"], q["crossings"], q["shared_starts"]), ([], 0, 0))

    def test_uncross_redraws_a_crossing_pair(self) -> None:
        """Three arrows into one box, one coming down from a lane above (smc-resiliency fw-x86, operator review 2026-10-22): with `uncross` the
        page has no crossing; with it switched off the greedy order leaves one, so the test can fail."""
        data = dict(_firmware(), drawing={"look": {"branch_order": "first"}})   # the order that left the crossing for uncross to clear
        comps = {c["id"]: c for c in data["components"]}
        fq = importlib.import_module("flow_quality")
        page = pages.flow_page(data["flows"][0], comps, 1, TestMap._profile(data))
        self.assertEqual(audit.faults(audit.page_audit(page)), [])
        self.assertEqual(fq.page_quality(page)["crossings"], 0)
        greedy = pages.flow_page(data["flows"][0], comps, 1, TestMap._profile(dict(data, drawing={"look": {"uncross": "off", "branch_order": "first"}})))
        self.assertGreater(fq.page_quality(greedy)["crossings"], 0)

    def test_branches_route_at_their_longest_turn(self) -> None:
        """With the default branch_order a decision's branches route after the shorter arrows, so the same map has no crossing even without
        uncross (operator review 2026-10-26: a skipping branch had taken a port a next-step arrow needed)."""
        data = dict(_firmware(), drawing={"look": {"uncross": "off"}})
        comps = {c["id"]: c for c in data["components"]}
        page = pages.flow_page(data["flows"][0], comps, 1, TestMap._profile(data))
        self.assertEqual(importlib.import_module("flow_quality").page_quality(page)["crossings"], 0)
        self.assertEqual(audit.faults(audit.page_audit(page)), [])


def _firmware() -> dict:
    """A map shaped like smc-resiliency's fw-x86 flow: two gates, a step in the top lane and one below both feeding the same box.

    Returns:
        The map.
    """
    data = TestMap._minimal()
    data["components"] += [{"id": c, "name": c.upper(), "kind": "container", "group": "G", "host": "h", "health": "ok"} for c in ("c", "d", "e")]
    data["flows"][0]["steps"] = [
        {"id": "on", "actor": "a", "action": "x", "via": ["SSH"]},
        {"id": "read", "actor": "b", "action": "x", "via": ["API"], "gate": "g1", "next": ["enrol", "qual"]},
        {"id": "qual", "actor": "b", "action": "x", "via": ["API"], "gate": "g2", "next": ["apply", "list"]},
        {"id": "apply", "actor": "c", "action": "x", "via": ["API"], "next": ["enrol"]},
        {"id": "list", "actor": "a", "action": "x", "via": ["API"], "next": ["enrol"]},
        {"id": "enrol", "actor": "d", "action": "x", "via": ["API"]},
        {"id": "record", "actor": "e", "action": "x", "via": ["API"], "next": []}]
    return data


if __name__ == "__main__":
    unittest.main()
