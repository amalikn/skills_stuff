"""Offline tests for hover texts, draw.io tags, frozen cells and the End-to-end per-flow layers (operator review 2026-10-23): x.1 start arrows,
a tooltip on every arrow and its x.y label, `look.e2e_layers` and `look.connector_width`, drawio.cell and flowmap.tips.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

(cell,) = (importlib.import_module(f"drawio.{n}") for n in ("cell",))
(tips,) = (importlib.import_module(f"flowmap.{n}") for n in ("tips",))
TestMap = importlib.import_module("test_layout_rules")

class EndToEndFlows(unittest.TestCase):
    """End-to-end arrows: x.1 start arrows, hover text, and one colour and layer per flow when asked (operator review 2026-10-23)."""

    def _two_flows(self, look: dict | None = None) -> dict:
        """Two flows that run on A and start in B, so each draws an x.1 arrow; C is a dependency only (a dashed connector).

        Args:
            look: the drawing look to pin, if any.

        Returns:
            The map.
        """
        data = TestMap._minimal()
        data["components"].append({"id": "c", "name": "C", "kind": "host", "group": "G", "host": "h", "health": "ok"})
        f = data["flows"][0]
        f["steps"] = [{"id": "one", "actor": "b", "action": "x", "via": ["SSH"]}, {"id": "two", "actor": "b", "action": "w", "via": ["internal"]},
                      {"id": "three", "actor": "a", "action": "y", "via": ["API"]}]
        f["dependencies"] = {"components": ["c"]}
        data["flows"].append({**f, "id": "g", "title": "G2"})
        if look:
            data["drawing"] = {"look": look}
        return data

    def test_start_arrow_tooltips_and_family_layers_by_default(self) -> None:
        """x.1 runs from the runs_on component; a same-actor step draws no arrow but is named in the next arrow's hover text."""
        root = ET.fromstring(TestMap._render(self._two_flows()).split("-->", 1)[1])
        e2e = next(d for d in root.iter("diagram") if d.get("id") == "end-to-end")
        objs = {u.get("id"): u for u in e2e.iter("UserObject")}
        self.assertEqual(objs["e2e-a-f-1"].find("mxCell").get("source"), "e2e-c-a")   # 1.1: A (runs on) to B
        self.assertNotIn("e2e-a-f-2", objs)   # step 2 stays in B
        self.assertIn("<b>Earlier in B (no arrow):</b> <b>1.2 two:</b> w", objs["e2e-a-f-3"].get("tooltip"))
        self.assertEqual(objs["e2e-a-f-3-l"].get("tooltip"), objs["e2e-a-f-3"].get("tooltip"))   # the x.y label hovers the same
        self.assertIn("depends on C", objs["e2e-c-custom-b-c"].get("tooltip"))
        self.assertIn('<ul style=', objs["e2e-c-custom-b-c"].get("tooltip"))   # two flows need C: a bullet list
        self.assertEqual([c.get("id") for c in e2e.iter("mxCell") if c.get("parent") == "0" and c.get("id") != "1"], ["e2e-L-custom"])

    def test_per_flow_layers_colours_and_bold_connectors(self) -> None:
        """look.e2e_layers: flow gives each flow a layer and a colour; look.connector_width sets the dashed connectors' stroke."""
        root = ET.fromstring(TestMap._render(self._two_flows({"e2e_layers": "flow", "connector_width": 2})).split("-->", 1)[1])
        e2e = next(d for d in root.iter("diagram") if d.get("id") == "end-to-end")
        layers = {c.get("id"): c.get("value") for c in e2e.iter("mxCell") if c.get("parent") == "0" and c.get("id") != "1"}
        self.assertEqual(layers, {"e2e-L-f": "Flow 1. F", "e2e-L-g": "Flow 2. G2"})
        cells = {u.get("id"): u.find("mxCell") for u in e2e.iter("UserObject")}
        colour = {fid: re.search(r"strokeColor=([^;]+)", cells[f"e2e-a-{fid}-1"].get("style")).group(1) for fid in ("f", "g")}
        self.assertNotEqual(colour["f"], colour["g"])
        self.assertEqual(cells["e2e-a-g-1"].get("parent"), "e2e-L-g")
        self.assertIn("strokeWidth=2;dashed=1", cells["e2e-c-f-b-c"].get("style"))



class CellsTipsAndTags(unittest.TestCase):
    """drawio.cell writes tags and tooltips on a UserObject; flowmap.tips builds the hover texts and tags (operator review 2026-10-23)."""

    def test_cell_xml_wraps_only_when_needed(self) -> None:
        """A plain cell stays an mxCell; a link, tooltip or tags make a UserObject with space-separated, unrepeated tags."""
        self.assertEqual(cell.cell_xml("a", "L", 'vertex="1"', ""), '<mxCell id="a" value="L" vertex="1"></mxCell>')
        wrapped = cell.cell_xml("a", "L", 'vertex="1"', "", tooltip="t", tags=("x", "y", "x", ""))
        self.assertEqual(wrapped, '<UserObject id="a" label="L" tooltip="t" tags="x y"><mxCell vertex="1"></mxCell></UserObject>')
        self.assertEqual(cell.tag("Flow", "Check (default)"), "flow-check-default")

    def test_step_tip_and_tags_carry_the_map(self) -> None:
        """A step's hover text holds its number, actor, action, gate and lists; its tags mark a gate and a step that can fail."""
        step = {"id": "guard", "actor": "r", "action": "Stop", "gate": "guard passes", "failures": ["boom"], "code": ["t.yml"]}
        self.assertEqual(tips.step_tip(step, "1.3", "Role"), "<b>1.3 guard (Role)</b><br><div>Stop</div><div><b>Gate:</b> guard passes</div>"
                         "<div><b>Fails:</b> boom</div><div><b>Code:</b> <font face=\"Courier New\">t.yml</font></div>")
        self.assertEqual(tips.tip_html("<x> & y", ("Host", "/var/<change>")), "<b>&lt;x&gt; &amp; y</b><br>"
                         '<div><b>Host:</b> <font face="Courier New">/var/&lt;change&gt;</font></div>')   # escaped, path in code font
        self.assertEqual(tips.step_tags(step, "process"), ("gate", "fails"))
        root = ET.fromstring(TestMap._render(TestMap._minimal()).split("-->", 1)[1])
        e2e = next(d for d in root.iter("diagram") if d.get("id") == "end-to-end")
        box = next(u for u in e2e.iter("UserObject") if u.get("id") == "e2e-c-b")
        self.assertEqual(box.get("tags"), "kind-container group-g flow-f")
        self.assertTrue(box.get("tooltip").startswith("<b>B (container)</b><br><div><b>Host:</b> h</div>"))

    def test_overview_dependency_arrows_have_tooltips(self) -> None:
        """An Overview thin arrow names what depends on what, with the needed component's health check."""
        root = ET.fromstring(TestMap._render(TestMap._minimal()).split("-->", 1)[1])
        ov = next(d for d in root.iter("diagram") if d.get("id") == "overview")
        arrow = next(u for u in ov.iter("UserObject") if u.get("id") == "ov-d-b-a")
        self.assertEqual(arrow.get("tooltip"), "<b>B needs A</b><br><div><b>B needs:</b> <b>A</b> (health: ok)</div>")
        many = tips.needs_tip("X", [({"name": "X"}, [{"name": "Y", "health": "h1"}, {"name": "Z", "health": "h2"}])])
        self.assertEqual(many.count("<li>"), 2)

    def test_every_generated_cell_is_frozen(self) -> None:
        """Every box, label and arrow is frozen (movable, resizable, rotatable, bendable, editable, deletable 0); layers stay unlocked."""
        root = ET.fromstring(TestMap._render(TestMap._minimal()).split("-->", 1)[1])
        styled = [c for c in root.iter("mxCell") if c.get("style") is not None]
        self.assertTrue(styled)
        self.assertEqual([c.get("id") or "?" for c in styled if "movable=0;resizable=0;rotatable=0;bendable=0;editable=0;deletable=0;" not in c.get("style")], [])


if __name__ == "__main__":
    unittest.main()
