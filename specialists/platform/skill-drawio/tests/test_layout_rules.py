"""Offline tests for the flow-map engine's layout and text rules, each from an operator review of unified-network-controller's drawing
(2026-10-19): text fits its box, notes and step boxes read as sections, arrows into one step keep apart, the overview's thin and thick arrows,
the flow page header, bold spans, and each layout audit at its exact threshold. Moved here from that project's tests/test_flows_drawio.py on
2026-10-19, when its renderer retired in favour of this pack; the project keeps only the tests of its own map.

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

# scripts/ goes on sys.path first, as a consuming project's seam does, so the modules are loaded by name after it.
audit, mxfile, route = (importlib.import_module(f"drawio.{n}") for n in ("audit", "mxfile", "route"))
e2e, layout, overview, pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("e2e", "overview_layout", "overview", "pages", "profile"))
CLEAN = {k: [] for k in audit.AUDIT_KEYS}


def _minimal() -> dict:
    """A small valid map: two components in one group and one two-step flow.

    Returns:
        The map as loaded YAML would be.
    """
    return {
        "schema_version": 1, "title": "T", "updated": "2026-10-15",
        "components": [
            {"id": "a", "name": "A", "kind": "host", "group": "G", "host": "h", "health": "ok"},
            {"id": "b", "name": "B", "kind": "container", "group": "G", "host": "h", "health": "ok", "depends_on": ["a"]},
        ],
        "flows": [{
            "id": "f", "title": "F", "category": "custom", "purpose": "p", "trigger": {"kind": "timer", "detail": "d"},
            "runs_on": "a", "owner": "b",
            "steps": [
                {"id": "one", "actor": "a", "action": "x", "via": ["SSH"], "failures": ["boom"], "look": ["log"]},
                {"id": "two", "actor": "b", "action": "y", "via": ["API"]},
            ],
        }],
    }


def _profile(data: dict) -> profile.Profile:
    """The default profile for a map (no drawing block).

    Args:
        data: the map.

    Returns:
        The profile.
    """
    return profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")


def _render(data: dict) -> str:
    """The whole drawing for a map under its default profile.

    Args:
        data: the map.

    Returns:
        The file text.
    """
    return pages.render(data, _profile(data))


def _route(cid: str, points: list, klass: str = "thick", jump: float = 0.0, layer: str = "1") -> mxfile.Route:
    """A synthetic route between boxes s and t.

    Args:
        cid: the edge id.
        points: its polyline.
        klass: "thick" or "thin".
        jump: its hop size.
        layer: its layer.

    Returns:
        The route.
    """
    return mxfile.Route(cid, "s", "t", points, klass, frozenset({"s", "t"}), jump, layer)


class TextAndBoxes(unittest.TestCase):
    """Text stays inside its shape, and notes, step boxes and headers read as sections."""

    def test_long_tokens_get_break_points_and_bold_spans_anywhere(self) -> None:
        """A long path gains zero-width break points (visible text unchanged); `**` spans render bold wherever they sit, text stays escaped."""
        path = "code: wc-local/nautobot/apps/unc-ownership/unc_ownership/onboarding_execution.py:complete_driver"
        self.assertEqual(mxfile.label(path).replace("​", ""), path)
        self.assertIn("​", mxfile.label(path))
        self.assertNotIn("​", mxfile.label("short words only"))
        self.assertEqual(mxfile.label("**Title**"), "<b>Title</b>")
        self.assertEqual(mxfile.label("**Flows** (click to open the page)"), "<b>Flows</b> (click to open the page)")
        self.assertEqual(mxfile.label("**9. Site <x>** (custom)", "a & b"), "<b>9. Site &lt;x&gt;</b> (custom)<br>a &amp; b")
        self.assertEqual(mxfile.label("plain * star"), "plain * star")

    def test_step_box_and_lane_grow_with_the_text(self) -> None:
        """A step whose action needs more lines than the minimum box gets a taller box, and its lane grows to hold it."""
        data = _minimal()
        data["flows"][0]["steps"][0]["action"] = " ".join(["word"] * 120)
        cells = {c.get("id"): c for c in ET.fromstring(_render(data).split("-->", 1)[1]).iter("mxCell")}
        box_h, lane_h = (float(cells[cid].find("mxGeometry").get("height")) for cid in ("f-s-one", "f-lane-0"))
        self.assertGreater(box_h, pages.STEP_H)
        self.assertGreaterEqual(lane_h, box_h)

    def test_note_has_headings_bullets_blank_lines_and_monospace_code(self) -> None:
        """Bold headings, one bullet per item, a blank line between sections, code in a monospace font; empty sections are left out."""
        step = {"id": "run", "reads": ["SMC"], "writes": ["captures/"], "code": ["scripts/x.py:render"], "failures": ["boom"], "look": ["`just flows`"]}
        lines = pages.note_lines(step, 5)
        self.assertEqual(lines[0], "**5. run**")
        for heading in ("**Reads**", "**Writes**", "**Code**", "**Fails**", "**Look**"):
            self.assertIn(heading, lines)
        self.assertEqual(lines[lines.index("**Writes**") - 1], mxfile.BLANK)
        self.assertIn("• `scripts/x.py:render`", lines)
        html_label = mxfile.label(*lines)
        self.assertIn('<font face="Courier New">', html_label)
        self.assertNotIn("`", html_label)
        self.assertEqual(pages.note_lines({"id": "x", "failures": ["f"]}, 1), ["**1. x**", mxfile.BLANK, "**Fails**", "• f"])

    def test_step_box_has_title_action_italic_via_and_gate(self) -> None:
        """Bold title, blank line, the action, blank line, the transport in italics, and a gate in bold when present."""
        lines = pages.step_lines({"id": "land", "action": "Create devices", "via": ["SSH", "API"], "gate": "land"}, 6)
        self.assertEqual(lines, ["**6. land**", mxfile.BLANK, "Create devices", mxfile.BLANK, "*via SSH + API*", "**GATE: land**"])
        self.assertIn("<i>via SSH + API</i>", mxfile.label(*lines))
        self.assertEqual(pages.step_lines({"id": "x", "action": "a", "via": ["UI"]}, 1)[-1], "*via UI*")

    def test_header_lines_have_spacing_and_bold_field_names(self) -> None:
        """Title and category, blank, purpose, blank, bold fields one per line (missing ones left out), blank, link back."""
        data = _minimal()
        comps = {c["id"]: c for c in data["components"]}
        flow = dict(data["flows"][0], budget="1 min", dependencies={"flows": ["g"], "credentials": ["kp"]})
        self.assertEqual(pages.flow_header_lines(flow, comps, 3), [
            "**3. F** (custom)", mxfile.BLANK, "p", mxfile.BLANK, "**Trigger:** timer: d", "**Runs on:** A · **Owner:** B", "**Budget:** 1 min",
            "**Depends on flows:** g", "**Credentials:** kp", mxfile.BLANK, "[back to Overview]"])

    def test_overview_box_text_is_set_out_like_a_note(self) -> None:
        """Bold name, kind, a blank line, a bold Needs heading and one bullet per cross-group need; nothing after when there is no need."""
        comp = {"name": "Collector", "kind": "project-code"}
        self.assertEqual(layout.box_lines(comp, ["Nautobot web", "SMC"]),
                         ["**Collector**", "project-code", mxfile.BLANK, "**Needs**", "• Nautobot web", "• SMC"])
        self.assertEqual(layout.box_lines(comp, []), ["**Collector**", "project-code"])


class Arrows(unittest.TestCase):
    """Flow page structure, step arrows and the overview's arrows."""

    def test_flow_page_has_lanes_numbered_edges_notes_and_links(self) -> None:
        """A lane per actor, a numbered arrow between steps, a note per step, links back to the overview, and the generated banner."""
        text = _render(_minimal())
        root = ET.fromstring(text.split("\n", 2)[2])
        flow = root.findall("diagram")[2]   # after the Overview and the End-to-end page
        ids = {c.get("id") for c in flow.iter() if c.get("id")}
        self.assertTrue({"f-lane-0", "f-lane-1", "f-s-one", "f-s-two", "f-n-one", "f-e-one-two"} <= ids)
        self.assertNotIn("f-n-two", ids)   # step two has nothing under its title: its note is hidden (look.empty_notes, 2026-10-21)
        self.assertIn("2", next(c for c in flow.iter("mxCell") if c.get("id") == "f-e-one-two-lbl").get("value"))   # the router labels its arrow
        links = {u.get("link") for u in root.iter("UserObject") if u.get("link")}
        self.assertTrue({"data:page/id,flow-f", "data:page/id,overview"} <= links)
        self.assertIn("GENERATED", text.splitlines()[1])

    def test_forward_and_back_arrows_use_separate_ports(self) -> None:
        """Two arrows into one step get different entry points; a back arrow is dashed, labelled and crosses no other step: the short way
        along the source's lane when clear, else below every lane."""
        data = _minimal()
        steps = data["flows"][0]["steps"]
        steps.append({"id": "three", "actor": "a", "action": "z", "via": ["SSH"], "next": ["two"]})
        steps[0]["next"] = ["two", "three"]
        steps[1]["next"] = ["three"]
        text = _render(data)
        styles = dict(re.findall(r'id="(f-e-[^"]+)"[^>]*style="([^"]+)"', text))
        ports = lambda s: re.search(r"entryX=([0-9.]+);entryY=([0-9.]+)", s).groups()
        self.assertNotEqual(ports(styles["f-e-one-three"]), ports(styles["f-e-two-three"]))
        self.assertIn("dashed=1", styles["f-e-three-two"])
        self.assertRegex(text, r'id="f-e-three-two-lbl" value="[^"]*back to 2')   # the label is a text mark beside the routed arrow (2026-10-21)
        flow_geometry = importlib.import_module("flowmap.flow_geometry")
        comps = {c["id"]: c for c in data["components"]}
        page = pages.flow_page(data["flows"][0], comps, 1, _profile(data))
        route = next(r for r in page.routes if r.cid == "f-e-three-two")
        self.assertTrue(flow_geometry._clear(page, route.points, {route.src, route.dst}))   # crosses no other step
        # A step in the source's lane between the two columns blocks the short way, so the arrow runs below every lane.
        steps.insert(2, {"id": "mid", "actor": "a", "action": "m", "via": ["SSH"]})
        steps[1]["next"] = ["mid"]
        page = pages.flow_page(data["flows"][0], comps, 1, _profile(data))
        route = next(r for r in page.routes if r.cid == "f-e-three-two")
        lanes_bottom = max(y + h for cid, (x, y, w, h) in page.rects.items() if "-lane-" in cid)
        self.assertGreater(route.points[1][1], lanes_bottom)
        self.assertTrue(flow_geometry._clear(page, route.points, {route.src, route.dst}))

    def test_thin_arrows_are_grey_and_thick_arrows_take_their_target_colour(self) -> None:
        """Same-group arrows are solid thin grey with hops; a cross-group dependency is one thick arrow with a count, a dot and a layer."""
        data = _minimal()
        data["components"].append({"id": "c", "name": "C", "kind": "container", "group": "H", "host": "h", "health": "ok", "depends_on": ["a", "b"]})
        page = overview.overview_page(data, _profile(data))
        text = "\n".join(page.cells)
        styles = dict(re.findall(r'id="(ov-(?:d|gg)-[^"]+)"[^>]*style="([^"]+)"', text))
        self.assertEqual(set(styles), {"ov-d-b-a", "ov-gg-1-0"})
        self.assertIn(f"strokeColor={layout.THIN_GREY}", styles["ov-d-b-a"])
        self.assertNotIn("dashed=1", styles["ov-d-b-a"])
        self.assertIn(f"jumpStyle=arc;jumpSize={layout.OV_THIN_JUMP}", styles["ov-d-b-a"])
        for part in ("strokeWidth=4", "jumpStyle=arc", f"strokeColor={profile.DISTINCT[0]}"):
            self.assertIn(part, styles["ov-gg-1-0"])
        self.assertIn("&lt;b&gt;×2&lt;/b&gt;", text)   # c needs a and b in group G: one arrow, count ×2 (a count, never a flow step)
        self.assertIn('id="ov-dot-c-0"', text)
        self.assertTrue({"ov-L-into-0", "ov-L-inside"} <= set(dict(page.layers)))
        self.assertIn("&lt;b&gt;Needs&lt;/b&gt;&lt;br&gt;• A&lt;br&gt;• B", text)


    def test_one_column_end_to_end_page_draws_and_passes_every_audit(self) -> None:
        """A map whose components share one tier column (the default profile with one group) draws its End-to-end page cleanly.

        Regression, 2026-10-19: with one column there was no channel, so a link inside it raised IndexError while the page was built.
        """
        data = _minimal()
        page = e2e.end_to_end_page(data, _profile(data))
        self.assertEqual(audit.faults(audit.page_audit(page)), [])
        self.assertEqual(e2e.e2e_untouched(data, page), [])


class ThinTrackOrder(unittest.TestCase):
    """Thin arrows sharing a row gap take tracks that minimise their crossings there (route.gap_order, 2026-10-20)."""

    def test_counts_a_run_crossing_a_neighbours_drop(self) -> None:
        """Two arrows leaving one box to the right: the left one on the upper track crosses the right one's way in, and its own way out is
        crossed by the right one's run below (two hops); swapped, never."""
        span = {"a": (655, 795), "b": (733, 880)}
        self.assertEqual(route.gap_crossings(["a", "b"], span), 2)
        self.assertEqual(route.gap_crossings(["b", "a"], span), 0)

    def test_reorders_only_when_it_strictly_helps(self) -> None:
        """smc-resiliency's S2 overview (2026-10-20): the activation step's arrows crossed; reordered they do not. An order with no crossing,
        or one where no swap helps, comes back unchanged, so a drawing already at its best renders byte-identical."""
        span = {"health": (575, 570), "timer": (655, 795), "confext": (733, 880)}
        order = route.gap_order(["health", "timer", "confext"], span)
        self.assertEqual(route.gap_crossings(order, span), 0)
        self.assertEqual(order, ["health", "confext", "timer"])
        clean = {"a": (10, 10), "b": (50, 90)}
        self.assertEqual(route.gap_order(["a", "b"], clean), ["a", "b"])
        tie = {"a": (0, 100), "b": (50, 50)}   # a straight drop inside a run is crossed whichever track is above
        self.assertEqual(route.gap_order(["a", "b"], tie), ["a", "b"])


class AuditThresholds(unittest.TestCase):
    """Each audit at its exact threshold, on synthetic boxes (a check that cannot fail proves nothing)."""

    BOXES = {"s": (0, 0, 100, 60), "t": (400, 0, 100, 60), "x": (200, 0, 100, 60)}

    def _audit(self, routes: list, marks: list = (), cells: list = (), layers: list = ()) -> dict:
        """layout_audit over this class's boxes.

        Args:
            routes: the routes.
            marks: the labels.
            cells: cell XML.
            layers: declared layers.

        Returns:
            The report.
        """
        return audit.layout_audit(self.BOXES, routes, marks, cells, layers)

    def test_crossing_diagonal_and_clean(self) -> None:
        """A route around the middle box is clean; a straight run through it and a slanted run are each reported, by name."""
        self.assertEqual(self._audit([_route("ok", [(100, 30), (150, 30), (150, 100), (350, 100), (350, 30), (400, 30)])]), CLEAN)
        self.assertEqual(self._audit([_route("thru", [(100, 30), (400, 30)])])["box_crossings"], ["thru x x"])
        self.assertEqual(self._audit([_route("slant", [(100, 30), (150, 120), (350, 120), (350, 30), (400, 30)])])["diagonal"], ["slant"])

    def test_shared_run_compares_thick_routes_only(self) -> None:
        """Two thick routes along one line are reported; a thin one is not compared."""
        a = _route("a", [(100, 20), (150, 20), (150, 100), (350, 100), (350, 20), (400, 20)])
        b = _route("b", [(100, 40), (160, 40), (160, 101), (340, 101), (340, 40), (400, 40)])
        c = _route("c", [(100, 50), (170, 50), (170, 100), (330, 100), (330, 50), (400, 50)], klass="thin")
        self.assertEqual(self._audit([a, b, c])["shared_runs"], ["a = b"])

    def test_short_head_is_24_px_thick_and_22_px_thin(self) -> None:
        """A thick last run under 24 px and a thin one under 22 px are reported; 22 px is enough for a thin one."""
        thick = _route("thick", [(100, 30), (380, 30), (380, 100), (390, 100), (390, 30), (400, 30)])
        thin = _route("thin", [(100, 20), (150, 20), (150, 100), (379, 100), (379, 21), (400, 21)], klass="thin")
        ok = _route("ok", [(100, 10), (140, 10), (140, 110), (378, 110), (378, 12), (400, 12)], klass="thin")
        self.assertEqual(self._audit([thick, thin, ok])["short_heads"], ["thick", "thin"])

    def test_label_on_its_own_arrow_is_allowed(self) -> None:
        """A label over another route is reported, one on its own route is not, and two overlapping labels are reported."""
        a = _route("a", [(100, 20), (150, 20), (150, 100), (350, 100), (350, 20), (400, 20)])
        b = _route("b", [(100, 40), (170, 40), (170, 120), (330, 120), (330, 40), (400, 40)])
        own, on_b, stray = (mxfile.TextMark("la", (230, 90, 40, 20), "a"), mxfile.TextMark("lb", (230, 110, 40, 20), "a"),
                            mxfile.TextMark("lc", (250, 95, 40, 10), "a"))
        report = self._audit([a, b], [own, on_b, stray])
        self.assertEqual(report["labels_on_arrows"], ["lb on b"])
        self.assertEqual(report["label_overlaps"], ["la / lc"])

    def test_arc_clash_is_two_jumps_plus_6_px_thick_or_thin(self) -> None:
        """A hopping route crossing two runs closer than 2 * jump + 6 is reported, far enough apart is clean, and thin routes are checked too."""
        hop = _route("hop", [(100, 30), (250, 30), (250, 200), (350, 200), (350, 30), (400, 30)], jump=7)
        near1 = _route("n1", [(100, 10), (120, 10), (120, 100), (300, 100), (300, 10), (400, 10)], klass="thin")
        near2 = _route("n2", [(100, 50), (130, 50), (130, 115), (290, 115), (290, 50), (400, 50)], klass="thin")
        far2 = _route("n2", [(100, 50), (130, 50), (130, 130), (290, 130), (290, 50), (400, 50)], klass="thin")
        self.assertEqual(self._audit([hop, near1, near2])["arc_clashes"], ["hop"])
        self.assertEqual(self._audit([hop, near1, far2])["arc_clashes"], [])
        thin_hop = _route("thinhop", [(100, 30), (250, 30), (250, 200), (350, 200), (350, 30), (400, 30)], klass="thin", jump=4)
        b = _route("b", [(100, 50), (130, 50), (130, 110), (290, 110), (290, 50), (400, 50)], klass="thin")
        self.assertEqual(self._audit([thin_hop, near1, b])["arc_clashes"], ["thinhop"])

    def test_missing_layer_names_routes_and_cells(self) -> None:
        """A cell or route whose parent is not a declared layer is reported, each by its layer."""
        cells = ['<mxCell id="e" parent="L-nope"/>', '<mxCell id="f" parent="L-ok"/>']
        route = _route("r", [(100, 30), (150, 30), (150, 100), (350, 100), (350, 30), (400, 30)], layer="L-gone")
        self.assertEqual(self._audit([route], cells=cells, layers=["L-ok"])["missing_layers"], ["L-gone", "L-nope"])

    def test_untouched_component_is_reported(self) -> None:
        """e2e_untouched names a component that no route reaches."""
        data = _minimal()
        data["components"].append({"id": "lonely", "name": "L", "kind": "store", "group": "G", "host": "h", "health": "ok"})
        self.assertEqual(e2e.e2e_untouched(data, e2e.end_to_end_page(data, _profile(data))), ["lonely"])


if __name__ == "__main__":
    unittest.main()
