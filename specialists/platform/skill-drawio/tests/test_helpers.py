"""Offline tests for skill-drawio's engine and front ends: each rule shown passing on good input and failing on bad input, every layout audit
shown able to fail, and the example map rendered, current and clean.

Run: `just test` (unittest, the pack's venv; PyYAML reads maps). The scripts folder is put on sys.path, as a consuming project does.
Modules tested here (the contract test looks for each name): "mxfile", "audit", "route", "read", "export", "profile", "model", "overview_layout",
"overview", "e2e_grid", "e2e", "pages", "schema_lite", "code_refs", "render_flowmap", "drawio_export", "drawio_read", "yaml_list_patch".
"""

from __future__ import annotations

import importlib
import json
import shutil
import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# scripts/ goes on sys.path first, as a consuming project's seam does, so the modules are loaded by name after it.
code_refs, drawio_export, drawio_read, render_flowmap, schema_lite, yaml_list_patch = (
    importlib.import_module(n) for n in ("code_refs", "drawio_export", "drawio_read", "render_flowmap", "schema_lite", "yaml_list_patch"))
audit, export, mxfile, read, route = (importlib.import_module(f"drawio.{n}") for n in ("audit", "export", "mxfile", "read", "route"))
e2e, model, overview, pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("e2e", "model", "overview", "pages", "profile"))
DISTINCT, Profile = profile.DISTINCT, profile.Profile

EXAMPLE = ROOT / "examples" / "shop"


def _tmp() -> Path:
    """A temporary folder, removed at exit.

    Returns:
        Its path.
    """
    path = Path(tempfile.mkdtemp())
    unittest.addModuleCleanup(shutil.rmtree, path, True)
    return path


def _route(cid: str, points: list, klass: str = "thick", jump: float = 0.0, layer: str = "1") -> mxfile.Route:
    """A route record for the audits, between cells s and t.

    Args:
        cid: the edge id.
        points: the polyline.
        klass: "thick" or "thin".
        jump: the hop size.
        layer: the layer id.

    Returns:
        The record.
    """
    return mxfile.Route(cid, "s", "t", points, klass, frozenset({"s", "t"}), jump, layer)


def _minimal() -> dict:
    """A small valid flow map: three components in two groups and one three-step flow.

    Returns:
        The map as loaded YAML would be.
    """
    return {"schema_version": 1, "title": "T", "updated": "2026-10-19",
            "components": [{"id": "a", "name": "A", "kind": "svc", "group": "G1", "host": "h", "health": "ok", "depends_on": ["b"]},
                           {"id": "b", "name": "B", "kind": "svc", "group": "G1", "host": "h", "health": "ok", "depends_on": ["c"]},
                           {"id": "c", "name": "C", "kind": "store", "group": "G2", "host": "h", "health": "ok"}],
            "flows": [{"id": "f", "title": "F", "category": "custom", "purpose": "p", "trigger": {"kind": "manual", "detail": "d"},
                       "runs_on": "a", "owner": "a",
                       "steps": [{"id": "one", "actor": "a", "action": "x", "via": ["API"]},
                                 {"id": "two", "actor": "b", "action": "y", "via": ["API"]},
                                 {"id": "three", "actor": "c", "action": "z", "via": ["DB"]}]}]}


class MxFile(unittest.TestCase):
    """Building pages and files."""

    def test_label_formats_spans_and_drops_empty_lines(self) -> None:
        """Bold, italic and code spans are formatted, HTML is escaped, long tokens get break points, empty lines are dropped."""
        got = mxfile.label("**A** & *b*", "", "`x`")
        self.assertEqual(got, '<b>A</b> &amp; <i>b</i><br><font face="Courier New">x</font>')
        self.assertIn("​", mxfile.label("a/" * 15))

    def test_wrapped_lines(self) -> None:
        """Words wrap at the width; a long token spans whole lines; empty text is one line."""
        self.assertEqual(mxfile.wrapped_lines("aaa bbb ccc", 7), 2)
        self.assertEqual(mxfile.wrapped_lines("x" * 25, 10), 3)
        self.assertEqual(mxfile.wrapped_lines("", 10), 1)

    def test_page_xml_layers_userobject_and_route_ends(self) -> None:
        """Layers follow cells 0 and 1; a tooltip makes a UserObject; route() pins exit and entry fractions and records the route."""
        page = mxfile.Page("p", "P")
        page.add_layer("L", "Layer")
        page.box("a", "A", 0, 0, 100, 50, "rounded=1;", tooltip="tip")
        page.box("b", "B", 300, 0, 100, 50, "rounded=1;")
        page.route("e", "a", "b", [(100, 25), (300, 25)], "edgeStyle=none;", layer="L")
        text = page.xml()
        self.assertLess(text.index('<mxCell id="1" parent="0"/>'), text.index('id="L"'))
        self.assertLess(text.index('id="L"'), text.index('<UserObject id="a"'))
        self.assertIn("exitX=1;exitY=0.5;entryX=0;entryY=0.5;", text)
        self.assertEqual(page.routes[0].points, [(100, 25), (300, 25)])
        whole = mxfile.mxfile([page], "gen", mxfile.banner("g.py", "m.yaml", "just flows", "just check"))
        self.assertTrue(whole.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by g.py from m.yaml'))


class Audits(unittest.TestCase):
    """Every audit passes a clean drawing and fails a drawing built to break it."""

    BOXES = {"s": (0, 0, 100, 100), "t": (400, 0, 100, 100), "x": (200, 0, 50, 300)}

    def _audit(self, routes: list, marks: list = (), cells: list = (), layers: list = ()) -> dict:
        """layout_audit over this class's boxes.

        Args:
            routes: route records.
            marks: label records.
            cells: cell XML.
            layers: declared layer ids.

        Returns:
            The report.
        """
        return audit.layout_audit(self.BOXES, routes, marks, cells, layers)

    def test_clean_route_passes(self) -> None:
        """A route around the obstacle with a long final run reports nothing."""
        good = _route("g", [(100, 50), (150, 50), (150, 350), (300, 350), (300, 50), (400, 50)])
        self.assertEqual(audit.faults(self._audit([good])), [])

    def test_each_fault_fires(self) -> None:
        """Box crossing, diagonal, shared run, short head, label on another arrow, label overlap, arc clash and missing layer each fire."""
        through = _route("a", [(100, 50), (400, 50)])
        diag = _route("d", [(100, 50), (150, 350), (300, 350), (300, 50), (400, 50)])
        twin1 = _route("t1", [(100, 20), (150, 20), (150, 320), (300, 320), (300, 20), (400, 20)])
        twin2 = _route("t2", [(100, 30), (150, 30), (150, 320), (300, 320), (300, 30), (400, 30)])
        short = _route("h", [(100, 80), (150, 80), (150, 340), (390, 340), (390, 80), (400, 80)])
        cases = {
            "box_crossings": ([through], [], [], []),
            "diagonal": ([diag], [], [], []),
            "shared_runs": ([twin1, twin2], [], [], []),
            "short_heads": ([short], [], [], []),
            "labels_on_arrows": ([twin1, short], [mxfile.TextMark("m", (220, 310, 40, 20), "h")], [], []),
            "label_overlaps": ([], [mxfile.TextMark("m1", (0, 0, 40, 20), "a"), mxfile.TextMark("m2", (10, 5, 40, 20), "a")], [], []),
            "missing_layers": ([_route("l", [(100, 50), (400, 50)], layer="nope")], [], ['<mxCell id="z" parent="ghost"/>'], []),
        }
        for key, (routes, marks, cells, layers) in cases.items():
            with self.subTest(key=key):
                self.assertTrue(self._audit(routes, marks, cells, layers)[key], key)
        hop = _route("j", [(100, 60), (160, 60), (160, 330), (290, 330), (290, 60), (400, 60)], jump=6)
        cross1 = _route("c1", [(170, 300), (175, 300), (175, 360)], klass="thin")
        cross2 = _route("c2", [(180, 300), (182, 300), (182, 360)], klass="thin")
        self.assertIn("j", audit.layout_audit({}, [hop, cross1, cross2])["arc_clashes"])

    def test_page_audit_reads_a_page(self) -> None:
        """page_audit() checks a built page's solid boxes and declared layers."""
        page = mxfile.Page("p", "P")
        page.box("a", "A", 0, 0, 100, 50, "", solid=True)
        page.box("b", "B", 300, 0, 100, 50, "", solid=True)
        page.box("x", "X", 150, -50, 50, 200, "", solid=True)
        page.route("e", "a", "b", [(100, 25), (300, 25)], "")
        self.assertEqual(audit.page_audit(page)["box_crossings"], ["e x x"])


class Route(unittest.TestCase):
    """Routing primitives."""

    def test_interval_tracks_share_only_when_apart(self) -> None:
        """Overlapping intervals take different tracks; one far enough away reuses the first."""
        self.assertEqual(route.interval_tracks([(0, 10, "a"), (5, 15, "b"), (30, 40, "c")], 5), {"a": 0, "b": 1, "c": 0})

    def test_spread_track_and_edge_point(self) -> None:
        """Ports interleave on top and bottom edges; tracks centre on the channel; an edge point lands on the side."""
        self.assertEqual(route.spread([(2, "p", "a"), (1, "q", "a")], "top"), {("q", "a"): 0.25, ("p", "a"): 0.5})
        self.assertEqual(route.track(["x", "y", "z"], "y", 100, 24), 100)
        self.assertEqual(route.edge_point((0, 0, 100, 40), "right", 0.5), (100, 20))

    def test_crossings_and_untwist(self) -> None:
        """Two crossing runs count once; untwist() moves a run so two hops on one line are at least 2 * jump + 6 apart."""
        a, b = route.oriented([(0, 10), (100, 10)]), route.oriented([(50, 0), (50, 20)])
        self.assertEqual(route.count_crossings(a, b), 1)
        routes = {"h": [(0, 50), (0, 60), (200, 60), (200, 70)], "v1": [(90, 0), (90, 100)], "v2": [(94, 0), (94, 100)]}
        route.untwist(routes, 4, {"h": (0, 200), "v1": (60, 60), "v2": (60, 60)}, 100)
        xs = sorted(pts[0][0] for key, pts in routes.items() if key != "h")
        self.assertGreaterEqual(xs[1] - xs[0], 2 * 4 + 6)


class Read(unittest.TestCase):
    """Reading drawings."""

    MODEL = ('<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
             '<mxCell id="g" value="" vertex="1" parent="1"><mxGeometry x="100" y="100" width="300" height="200" as="geometry"/></mxCell>'
             '<UserObject id="a" label="&lt;b&gt;Switch&lt;/b&gt;" tooltip="t"><mxCell vertex="1" parent="g">'
             '<mxGeometry x="10" y="10" width="80" height="40" as="geometry"/></mxCell></UserObject>'
             '<mxCell id="b" value="Router" vertex="1" parent="1"><mxGeometry x="600" y="110" width="80" height="40" as="geometry"/></mxCell>'
             '<mxCell id="e" value="" edge="1" parent="1" source="a" target="b" style="exitX=1;exitY=0.5;"><mxGeometry relative="1" as="geometry"/></mxCell>'
             '<mxCell id="p" value="SWP 5" vertex="1" parent="1"><mxGeometry x="300" y="115" width="40" height="10" as="geometry"/></mxCell>'
             "</root></mxGraphModel>")

    def test_codec_round_trip_and_bad_data(self) -> None:
        """encode_page() and decode_page() invert each other; non-page text raises ValueError."""
        self.assertEqual(read.decode_page(read.encode_page(self.MODEL)), self.MODEL)
        with self.assertRaises(ValueError):
            read.decode_page("not base64 deflate")

    def test_pages_offsets_and_label_matching(self) -> None:
        """A compressed page reads like a plain one; a child's box adds its group's corner; a port label goes to the nearest line."""
        plain = read.pages(f'<mxfile><diagram name="P">{self.MODEL}</diagram></mxfile>')[0]
        packed = read.pages(f'<mxfile><diagram name="P">{read.encode_page(self.MODEL)}</diagram></mxfile>')[0]
        self.assertEqual(plain, packed)
        self.assertIn({"source": "Switch", "target": "Router", "label": ""}, plain["edges"])
        shape = {s["id"]: s for s in plain["shapes"]}
        self.assertEqual(shape["a"]["geo"], [110.0, 110.0, 80.0, 40.0])
        wire = plain["wires"][0]
        self.assertEqual(wire["path"][0], [190.0, 130.0])
        self.assertEqual(read.match_labels([shape["p"]], [wire]), {"p": "e"})
        self.assertEqual(read.match_labels([shape["p"]], [wire], reach=1), {})

    def test_cli_reads_and_reports_bad_files(self) -> None:
        """drawio_read prints a page and exits 1 on a file that is not XML."""
        tmp = _tmp()
        (tmp / "good.drawio").write_text(f'<mxfile><diagram name="P">{self.MODEL}</diagram></mxfile>', encoding="utf-8")
        (tmp / "bad.drawio").write_text("nope", encoding="utf-8")
        self.assertEqual(drawio_read.main([str(tmp / "good.drawio"), "--json", str(tmp / "out.json")]), 0)
        self.assertIn("Switch", (tmp / "out.json").read_text(encoding="utf-8"))
        self.assertEqual(drawio_read.main([str(tmp / "bad.drawio")]), 1)


class Export(unittest.TestCase):
    """The desktop CLI wrapper, against a fake binary."""

    def test_argv_rules(self) -> None:
        """Pages count from 1, layers become --layers, the format comes from the output's extension; bad input raises."""
        argv = export.export_argv("drawio", Path("a.drawio"), Path("o.png"), 2, (0, 3), 2.0)
        self.assertEqual(argv[argv.index("-p") + 1], "2")
        self.assertEqual(argv[argv.index("--layers") + 1], "0,3")
        self.assertEqual(argv[-1], "a.drawio")
        for bad in ({"page": 0}, {"out": Path("o.gif")}):
            with self.assertRaises(ValueError):
                export.export_argv("drawio", Path("a.drawio"), bad.get("out", Path("o.png")), bad.get("page", 1))

    def test_run_writes_times_out_and_fails(self) -> None:
        """A fake binary that writes the file passes; one that sleeps is killed at the timeout; one that writes nothing fails."""
        tmp = _tmp()
        fakes = {"ok": 'out=""; while [ $# -gt 0 ]; do [ "$1" = "-o" ] && out="$2"; shift; done; echo png > "$out"',
                 "slow": "sleep 5", "silent": "exit 0"}
        for name, body in fakes.items():
            (tmp / name).write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
            (tmp / name).chmod(stat.S_IRWXU)
        out = tmp / "p.png"
        self.assertEqual(export.run(export.export_argv(str(tmp / "ok"), tmp / "a.drawio", out)), out)
        with self.assertRaises(RuntimeError):
            export.run(export.export_argv(str(tmp / "slow"), tmp / "a.drawio", tmp / "q.png"), timeout_s=1)
        with self.assertRaises(RuntimeError):
            export.run(export.export_argv(str(tmp / "silent"), tmp / "a.drawio", tmp / "r.png"))
        self.assertEqual(drawio_export.main([str(tmp / "a.drawio"), "--out-dir", str(tmp / "imgs"), "--binary", str(tmp / "ok")]), 0)
        self.assertEqual(drawio_export.main([str(tmp / "a.drawio"), "--out-dir", str(tmp), "--binary", str(tmp / "missing")]), 2)


class Model(unittest.TestCase):
    """The map's rules and the profile's defaults."""

    def test_schema_subset(self) -> None:
        """The generic schema accepts the example and rejects a component without its required keys."""
        schema = json.loads((ROOT / "schemas" / "flowmap.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema_lite.schema_errors(model.read_map(EXAMPLE, "flows.yaml"), schema), [])
        bad = _minimal()
        del bad["components"][0]["health"]
        self.assertIn("missing required `health`", "\n".join(schema_lite.schema_errors(bad, schema)))

    def test_reference_problems(self) -> None:
        """Duplicate ids, unknown actors, unreached steps and missing code paths or symbols are each reported; a clean map reports none."""
        self.assertEqual(model.reference_problems(_minimal(), ROOT), [])
        data = _minimal()
        data["components"].append(dict(data["components"][0]))
        steps = data["flows"][0]["steps"]
        steps[1]["actor"] = "ghost"
        steps[0]["next"] = ["three"]
        steps[2]["code"] = ["no/such.py", "scripts/render_flowmap.py:not_there", "scripts/render_flowmap.py:main"]
        got = "\n".join(model.reference_problems(data, ROOT))
        for text in ("component id `a` is used more than once", "actor names unknown component `ghost`", "step `two` has no arrow into it",
                     "code path `no/such.py` does not exist", "`not_there` is not defined"):
            self.assertIn(text, got)
        self.assertNotIn("`main` is not defined", got)
        self.assertTrue(code_refs.symbol_defined("class Page:\n    def edge(self):", "Page.edge"))

    def test_profile_defaults(self) -> None:
        """Without a drawing block every kind gets a colour, every group a tier, every category a family, and the output sits beside the map."""
        p = Profile.from_drawing(_minimal(), "docs/flows.yaml", "s.json", "g")
        self.assertEqual(list(p.kind_style), ["svc", "store"])
        self.assertEqual(p.tiers, (("G1", ("G1",)), ("G2", ("G2",))))
        self.assertEqual(p.families, (("custom", "Custom", DISTINCT[0], ()),))
        self.assertEqual(p.output, "docs/drawio/flows.drawio")
        self.assertEqual(model.flow_family(_minimal()["flows"][0], p), "custom")


class Rendering(unittest.TestCase):
    """The pages and the whole file."""

    def test_minimal_map_renders_clean_and_deterministic(self) -> None:
        """A minimal map renders the same twice, both routed pages pass every audit, and every component is reached on End-to-end."""
        data = _minimal()
        p = Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        self.assertEqual(pages.render(data, p), pages.render(json.loads(json.dumps(data)), p))
        self.assertEqual(audit.faults(audit.page_audit(overview.overview_page(data, p))), [])
        page = e2e.end_to_end_page(data, p)
        self.assertEqual(audit.faults(audit.page_audit(page)), [])
        self.assertEqual(e2e.e2e_untouched(data, page), [])

    def test_step_edges_ports(self) -> None:
        """Forward arrows leave right and enter left; an arrow back to an earlier step uses the bottom, dashed, labelled back to N."""
        steps = [{"id": "a"}, {"id": "b", "next": ["a"]}]
        (fwd, back) = pages.step_edges(steps, "f")
        self.assertIn("exitX=1;", fwd[4])
        self.assertEqual(back[3], "back to 1")
        self.assertIn("exitY=1;", back[4])

    def test_example_is_current_clean_and_complete(self) -> None:
        """The example map is valid, its committed drawing is what it renders, its routed pages are clean and every component is reached."""
        p = render_flowmap.profile_for(EXAMPLE, "flows.yaml", str(render_flowmap.SCHEMA), "")
        outcome = pages.evaluate(EXAMPLE, p)
        self.assertEqual(outcome.problems, [])
        self.assertFalse(outcome.drift, "examples/shop: run `just example`")
        self.assertEqual(render_flowmap.audit(EXAMPLE, p), [])
        data, _ = model.load(EXAMPLE, p)
        self.assertEqual(e2e.e2e_untouched(data, e2e.end_to_end_page(data, p)), [])

    def test_cli_drift_write_and_list(self) -> None:
        """A hand edit is drift (exit 1); --write makes it current (exit 0); --list prints one line per flow."""
        tmp = _tmp()
        shutil.copytree(EXAMPLE, tmp / "shop")
        args = ["--root", str(tmp / "shop"), "--map", "flows.yaml"]
        self.assertEqual(render_flowmap.main(args), 0)
        out = tmp / "shop" / "drawio" / "flows.drawio"
        out.write_text(out.read_text(encoding="utf-8").replace("Overview", "Hand edit"), encoding="utf-8")
        self.assertEqual(render_flowmap.main(args), 1)
        self.assertEqual(render_flowmap.main([*args, "--write"]), 0)
        self.assertEqual(render_flowmap.main(args), 0)
        self.assertEqual(render_flowmap.main([*args, "--list"]), 0)

    def test_write_refuses_a_hand_made_drawing(self) -> None:
        """A drawing at the output path without the generated banner is never written over (exit 1, file untouched)."""
        tmp = _tmp()
        shutil.copytree(EXAMPLE, tmp / "shop")
        out = tmp / "shop" / "drawio" / "flows.drawio"
        hand = '<mxfile host="app.diagrams.net"><diagram name="Mine"/></mxfile>\n'
        out.write_text(hand, encoding="utf-8")
        self.assertEqual(render_flowmap.main(["--root", str(tmp / "shop"), "--map", "flows.yaml", "--write"]), 1)
        self.assertEqual(out.read_text(encoding="utf-8"), hand)


class YamlListPatch(unittest.TestCase):
    """Comment-preserving list edits."""

    TEXT = textwrap.dedent("""\
        # a comment that must survive
        components:
          - id: a   # trailing comment
            health: ok
            depends_on: [b]
          - id: b
            health: ok
        flows:
          - id: f
            owner: a
            dependencies: {flows: [g]}
        """)

    def test_patch_adds_inserts_and_keeps_comments(self) -> None:
        """A value is appended once, a missing field is inserted after its anchor, a list inside a flow mapping is added, comments stay."""
        got = yaml_list_patch.patch(self.TEXT, "components", "id", "depends_on", {"a": ["b", "c"], "b": ["c"]}, after="health")
        self.assertIn("    depends_on: [b, c]\n", got)
        self.assertIn("    health: ok\n    depends_on: [c]\n", got)
        self.assertIn("# a comment that must survive", got)
        self.assertIn("# trailing comment", got)
        got = yaml_list_patch.patch(self.TEXT, "flows", "id", "dependencies.components", {"f": ["x"]})
        self.assertIn("dependencies: {flows: [g], components: [x]}", got)
        with self.assertRaises(KeyError):
            yaml_list_patch.patch(self.TEXT, "components", "id", "depends_on", {"zz": ["x"]})

    def test_plan_by_default_apply_writes(self) -> None:
        """Without --apply the file is unchanged; with it the file is written; a missing item exits 1."""
        tmp = _tmp()
        (tmp / "m.yaml").write_text(self.TEXT, encoding="utf-8")
        (tmp / "s.json").write_text('{"b": ["a"]}', encoding="utf-8")
        args = [str(tmp / "m.yaml"), "--list", "components", "--field", "depends_on", "--spec", str(tmp / "s.json")]
        self.assertEqual(yaml_list_patch.main(args), 0)
        self.assertEqual((tmp / "m.yaml").read_text(encoding="utf-8"), self.TEXT)
        self.assertEqual(yaml_list_patch.main([*args, "--apply"]), 0)
        self.assertIn("depends_on: [a]", (tmp / "m.yaml").read_text(encoding="utf-8"))
        (tmp / "s.json").write_text('{"zz": ["a"]}', encoding="utf-8")
        self.assertEqual(yaml_list_patch.main(args), 1)


if __name__ == "__main__":
    unittest.main()
