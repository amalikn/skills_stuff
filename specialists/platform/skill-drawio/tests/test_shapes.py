"""Offline tests for flow page shapes (flowmap.shapes, adopted 2026-10-21): each derivation rule picks its shape, an override wins, a lane head
follows its kind, a step that runs another flow links to it, an unknown flow is refused, and a flow page carries a legend of the shapes it uses.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

flow_geometry, model, pages, shapes = (importlib.import_module(f"flowmap.{n}") for n in ("flow_geometry", "model", "pages", "shapes"))
TestMap = importlib.import_module("test_layout_rules")
IO = shapes.DEFAULT_IO_VIAS


class ShapeTests(unittest.TestCase):
    """The shape rules."""

    def setUp(self) -> None:
        """Components of each kind the rules read."""
        self.comps = {"op": {"kind": "person"}, "svc": {"kind": "service"}, "db": {"kind": "store"}, "t": {"kind": "timer"},
                      "doc": {"kind": "store", "shape": "document"}}

    def test_step_rules(self) -> None:
        """First and last steps are terminators, a person's step a manual operation, a gate a decision, a flow call a predefined process,
        a network transport data in or out, the rest a process; an explicit shape wins."""
        steps = [{"id": "a", "actor": "svc", "via": ["file"]}, {"id": "b", "actor": "op", "via": ["SSH"]},
                 {"id": "c", "actor": "svc", "via": ["internal"], "gate": "g"}, {"id": "d", "actor": "svc", "via": ["internal"], "flow": "x"},
                 {"id": "e", "actor": "svc", "via": ["HTTPS"]}, {"id": "f", "actor": "svc", "via": ["internal"]},
                 {"id": "g", "actor": "svc", "via": ["internal"], "shape": "preparation"}, {"id": "h", "actor": "svc", "via": ["file"]}]
        got = [shapes.step_shape(steps, k, self.comps, {}, IO) for k in range(len(steps))]
        self.assertEqual(got, ["terminator", "manual-operation", "decision", "predefined-process", "data-io", "process", "preparation",
                               "terminator"])

    def test_lane_rules(self) -> None:
        """A lane head follows its kind (defaults, then the map's kind_shapes); a component's own shape wins."""
        self.assertEqual(shapes.lane_shape(self.comps["db"], {}), "stored-data")
        self.assertEqual(shapes.lane_shape(self.comps["t"], {}), "delay")
        self.assertEqual(shapes.lane_shape(self.comps["doc"], {}), "document")
        self.assertEqual(shapes.lane_shape(self.comps["svc"], {"service": "external"}), "external")
        self.assertEqual(shapes.lane_shape(self.comps["svc"], {}), "process")

    def test_flow_page_has_legend_and_link(self) -> None:
        """A step that runs another flow links to its page; the page carries a shape legend; an unknown flow is refused (negative)."""
        data = TestMap._minimal()
        data["flows"].append(dict(data["flows"][0], id="g", title="G"))
        data["flows"][1]["steps"] = [dict(s) for s in data["flows"][1]["steps"]]
        data["flows"][1]["steps"][0]["flow"] = "f"
        text = pages.render(data, TestMap._profile(data))
        self.assertIn("data:page/id,flow-f", text)
        self.assertIn("-shp-title", text)
        data["flows"][1]["steps"][0]["flow"] = "nope"
        self.assertTrue(any("unknown flow `nope`" in p for p in model.reference_problems(data, ROOT)))


class GeometryTests(unittest.TestCase):
    """flow_geometry: a decision's column is wider, so its diamond grows sideways (operator review, 2026-10-21)."""

    def test_decision_column_is_wider(self) -> None:
        """A decision step is DEC_STEP_W wide and pushes the next column right by the difference; other steps keep STEP_W."""
        self.assertEqual(flow_geometry.step_width("decision"), flow_geometry.DEC_STEP_W)
        self.assertEqual(flow_geometry.step_width("process"), flow_geometry.STEP_W)
        lefts = flow_geometry.column_lefts([flow_geometry.STEP_W, flow_geometry.DEC_STEP_W, flow_geometry.STEP_W])
        self.assertEqual(lefts[2] - lefts[1], flow_geometry.DEC_STEP_W + flow_geometry.COL_W - flow_geometry.STEP_W)


class LookTests(unittest.TestCase):
    """drawing.look: each setting reaches the drawing, and a map without it draws with the defaults (operator, 2026-10-21)."""

    def test_look_settings_change_the_drawing(self) -> None:
        """group_fill, shapes and step_width each change the output; no look means DEFAULT_LOOK."""
        data = TestMap._minimal()
        base = pages.render(data, TestMap._profile(data))
        data["drawing"] = {"look": {"group_fill": "#fafafa", "shapes": False, "step_width": 260}}
        text = pages.render(data, TestMap._profile(data))
        self.assertIn("fillColor=#fafafa;strokeColor=#777777;dashed=1", text)
        self.assertNotIn("arcSize=40", text)   # no terminators when shapes are off
        self.assertIn('width="260"', text)
        self.assertNotEqual(base, text)
        self.assertEqual(TestMap._profile(TestMap._minimal()).look, importlib.import_module("flowmap.profile").DEFAULT_LOOK)


class LookReportTests(unittest.TestCase):
    """profile.look_report: pins are named, and a pin equal to the current default is warned about (operator, 2026-10-21)."""

    def test_report(self) -> None:
        """No look: defaults. A pin: named. A pin equal to the default: warned (negative: a differing pin is not)."""
        prof = importlib.import_module("flowmap.profile")
        self.assertEqual(prof.look_report({}), ["look: skill-drawio defaults (nothing pinned)"])
        lines = prof.look_report({"drawing": {"look": {"step_width": 240, "shapes": True}}})
        self.assertIn("step_width=240", lines[0])
        self.assertEqual([x for x in lines if x.startswith("warning")], ["warning: look.shapes is pinned to the current default (True); remove it to follow future defaults"])


class OpaqueDashedBoxTests(unittest.TestCase):
    """A dashed box is never see-through (operator, 2026-10-21: "white background so that I don't see the draw.io grid", as a standard)."""

    def test_no_dashed_vertex_is_transparent(self) -> None:
        """Every vertex drawn dashed has a fill; a group box is white. Negative: the old group style (fillColor=none) would be named."""
        import re
        data = TestMap._minimal()
        data["components"][0]["status"] = {"state": "proposed", "since": "2026-10-21"}
        text = pages.render(data, TestMap._profile(data))
        styles = re.findall(r'style="([^"]*dashed=1[^"]*)"[^>]*vertex="1"', text)
        self.assertTrue(styles)   # the page has dashed boxes, so the check below can fail
        self.assertEqual([st for st in styles if "fillColor=none" in st or "fillColor=" not in st], [])
        self.assertTrue(any("fillColor=#ffffff" in st for st in styles))



class ComponentShapeTests(unittest.TestCase):
    """Overview and End-to-end boxes take their lane head's symbol (look.component_shapes, 2026-10-21)."""

    def _map(self) -> dict:
        """The minimal map with its second component a store.

        Returns:
            The map.
        """
        data = TestMap._minimal()
        data["components"][1]["kind"] = "store"
        return data

    def test_store_is_a_cylinder_on_overview_and_end_to_end(self) -> None:
        """By default a store draws as a cylinder on both pages, taller than its text alone, and a plain kind stays a rectangle."""
        data = self._map()
        prof = TestMap._profile(data)
        text = pages.render(data, prof)
        for cell in ('id="ov-c-b"', 'id="e2e-c-b"'):
            style = text.split(cell, 1)[1].split('style="', 1)[1].split('"', 1)[0]
            self.assertIn("shape=cylinder3", style)
        self.assertNotIn("cylinder3", text.split('id="ov-c-a"', 1)[1].split('style="', 1)[1].split('"', 1)[0])
        self.assertGreater(shapes.fit_height(data["components"][1], prof, 40), 40)

    def test_look_off_draws_rounded_boxes(self) -> None:
        """With `component_shapes: false` the Overview and End-to-end boxes are the plain rounded boxes again."""
        data = self._map()
        data["drawing"] = {"look": {"component_shapes": False}}
        text = pages.render(data, TestMap._profile(data))
        for cell in ('id="ov-c-b"', 'id="e2e-c-b"'):
            self.assertNotIn("cylinder3", text.split(cell, 1)[1].split('style="', 1)[1].split('"', 1)[0])

if __name__ == "__main__":
    unittest.main()
