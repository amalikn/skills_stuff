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

model, pages, shapes = (importlib.import_module(f"flowmap.{n}") for n in ("model", "pages", "shapes"))
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


if __name__ == "__main__":
    unittest.main()
