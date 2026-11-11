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


class CrowdedLabelTests(unittest.TestCase):
    """Two End-to-end runs 24 px apart, as on smc-resiliency's full page (2026-11-07): labels placed in drawing order land on each other;
    flowmap.step_labels.place_labels ("step_labels") places the arrow with less room first and both fit."""

    #: The two arrows as rendered: one with a 136 px run, one with an 88 px run beside it, flat ends shorter than a label.
    PTS = {"long": [(1776, 3436), (1834, 3436), (1834, 3300), (1776, 3300)], "short": [(1776, 3412), (1810, 3412), (1810, 3324), (1776, 3324)]}

    @staticmethod
    def _overlaps(page: object) -> int:
        """How many label pairs on a page overlap.

        Args:
            page: the page.

        Returns:
            The count.
        """
        marks = page.marks
        return sum(1 for i, m in enumerate(marks) for n in marks[i + 1:] if costs.rects_overlap(m.rect, n.rect))

    def test_place_labels_clears_the_pair(self) -> None:
        """place_labels leaves no two labels overlapping."""
        mxfile, labels = importlib.import_module("drawio.mxfile"), importlib.import_module("flowmap.step_labels")
        page = mxfile.Page("p", "P")
        labels.place_labels(page, {"long": ("1.1", "#000000", "1"), "short": ("2.1", "#000000", "1")}, self.PTS, (44, 18, 12), [])
        self.assertEqual(len(page.marks), 2)
        self.assertEqual(self._overlaps(page), 0)

    def test_drawing_order_alone_overlaps(self) -> None:
        """Placing each label in drawing order with label_spot, as before, overlaps: the test above can fail."""
        mxfile, labels = importlib.import_module("drawio.mxfile"), importlib.import_module("flowmap.step_labels")
        page = mxfile.Page("p", "P")
        for cid in ("long", "short"):
            cx, cy = labels.label_spot(cid, self.PTS, page, 44, 18)
            page.mark(f"{cid}-l", cid, cx, cy, 44, 18, "text;", owner=cid)
        self.assertGreater(self._overlaps(page), 0)


class RouteProbeTests(unittest.TestCase):
    """scripts/route_probe.py ("route_probe") reports the router's choices on the commissioning fixture."""

    def test_probe_names_the_straight_arrow_or_the_trials(self) -> None:
        """With the default look it lists 3 -> 4 drawn straight first; with straight_first off it lists the gate's corner trials instead."""
        import yaml
        rp = importlib.import_module("route_probe")
        data = yaml.safe_load(FIXTURE.read_text())
        comps = {c["id"]: c for c in data["components"]}
        lines, _page = rp.probe(data["flows"][0], comps, TestMap._profile(data))
        self.assertTrue(any("straight first" in x and "register-probe-old" in x for x in lines), lines)
        data["drawing"] = {"look": {"straight_first": "off"}}
        lines, _page = rp.probe(data["flows"][0], comps, TestMap._profile(data))
        self.assertTrue(any("('right', 'bottom')" in x for x in lines), lines)
        self.assertFalse(any("straight first" in x for x in lines))


class BackButtonTests(unittest.TestCase):
    """A step page links back to its End-to-end page (flowmap.e2e_family.back_target and back_button, "e2e_family")."""

    def _page(self, look: dict) -> object:
        """Render the commissioning fixture's step page.

        Args:
            look: look keys.

        Returns:
            The page.
        """
        import yaml
        data = yaml.safe_load(FIXTURE.read_text())
        data["drawing"] = {"look": look}
        return pages.flow_page(data["flows"][0], {c["id"]: c for c in data["components"]}, 1, TestMap._profile(data))

    @staticmethod
    def _button(page: object) -> str:
        """The back button's cell XML, or "" when the page has none.

        Args:
            page: the page.

        Returns:
            The cell.
        """
        return next((c for c in page.cells if 'id="flow-commission-gps-back"' in c), "")

    def test_button_links_to_the_family_page_or_the_full_one(self) -> None:
        """With family pages the button opens the family's page; without, the full End-to-end page; off draws none."""
        self.assertIn("data:page/id,end-to-end-", self._button(self._page({"e2e_family_pages": True})))
        self.assertIn('data:page/id,end-to-end"', self._button(self._page({})))
        self.assertEqual(self._button(self._page({"back_button": "off"})), "")

    def test_button_sits_above_the_header(self) -> None:
        """The button sits above the header's top-left corner, not beside its right end, and the header moves down to make room; with the
        button off the header keeps the top (operator, 2026-11-11)."""
        page = self._page({})
        (bx, by, _bw, bh), (hx, hy, _hw, _hh) = page.rects["flow-commission-gps-back"], page.rects["commission-gps-head"]
        self.assertEqual(bx, hx)
        self.assertLessEqual(by + bh, hy)
        off = self._page({"back_button": "off"}).rects["commission-gps-head"]
        self.assertLess(off[1], hy)


class NoteAuditTests(unittest.TestCase):
    """drawio.audit.page_audit ("audit") counts a note card as a box no arrow may cross, though the router does not (ROADMAP 2026-11-06)."""

    def test_an_arrow_across_a_note_is_a_box_crossing(self) -> None:
        """An arrow through a note card is reported; the same page without the note is clean."""
        mxfile, audit = importlib.import_module("drawio.mxfile"), importlib.import_module("drawio.audit")

        def page(with_note: bool) -> object:
            """Two boxes joined by an arrow that runs down through the gap where a note may sit.

            Args:
              with_note: draw the note card in the arrow's way.

            Returns:
              The page.
            """
            pg = mxfile.Page("p", "P")
            pg.box("a", "A", 0, 0, 100, 40, "rounded=1;", solid=True)
            pg.box("b", "B", 300, 0, 100, 40, "rounded=1;", solid=True)
            if with_note:
                pg.box("p-n-a", "note", 150, 100, 100, 60, "shape=note;whiteSpace=wrap;")
            pg.route("e", "a", "b", [(50, 40), (50, 130), (350, 130), (350, 40)], "edgeStyle=none;")
            return pg

        self.assertIn("e x p-n-a", audit.page_audit(page(True))["box_crossings"])
        self.assertEqual(audit.page_audit(page(False))["box_crossings"], [])


if __name__ == "__main__":
    unittest.main()


class FlowHeadModule(unittest.TestCase):
    """flowmap.flow_head ("flow_head") holds the step page header since 2026-11-11; flowmap.pages re-exports it for its callers."""

    def test_pages_reexports_the_header(self) -> None:
        """pages.flow_header and pages.flow_header_lines are the flow_head functions, so older imports keep working."""
        head, pages = importlib.import_module("flowmap.flow_head"), importlib.import_module("flowmap.pages")
        self.assertIs(pages.flow_header, head.flow_header)
        self.assertIs(pages.flow_header_lines, head.flow_header_lines)
