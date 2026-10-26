"""Offline tests for scripts/viewer_click.py ("viewer_click") and render_flowmap's --look overrides ("render_flowmap"): the pure helpers
only; the browser run is checked by hand on a real drawing (references/visual-style.md, Learned 2026-10-26).

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
viewer_click, render_flowmap = (importlib.import_module(n) for n in ("viewer_click", "render_flowmap"))


class ViewerClick(unittest.TestCase):
    """The viewer page and the click targets."""

    def test_page_opens_the_asked_diagram_without_the_banner(self) -> None:
        """The banner comment is dropped, the page index is passed, and the viewer script is loaded by file URI."""
        html = viewer_click.viewer_html(ROOT / "scripts" / "viewer_click.py", "<!-- GENERATED -->\n<mxfile><diagram/></mxfile>", 3)
        cfg = json.loads(json.loads(html.split("setAttribute('data-mxgraph', ", 1)[1].split(");", 1)[0]))
        self.assertEqual((cfg["page"], cfg["xml"].strip()), (3, "<mxfile><diagram/></mxfile>"))
        self.assertIn('src="file://', html)

    def test_targets_mark_the_click_path(self) -> None:
        """`!id` goes through draw.io's click path, a plain id is a mouse click; blanks are dropped."""
        self.assertEqual(viewer_click.parse_targets("!a, b,,!"), [("a", True), ("b", False)])


class LookOverrides(unittest.TestCase):
    """render_flowmap --look KEY=JSON."""

    def test_values_parse_as_json_or_text(self) -> None:
        """true, numbers and quoted strings are JSON; anything else is kept as text; a pair without '=' is refused."""
        self.assertEqual(render_flowmap.look_overrides(["a=true", "b=12", 'c="sub"', "d=flow"]), {"a": True, "b": 12, "c": "sub", "d": "flow"})
        with self.assertRaises(ValueError):
            render_flowmap.look_overrides(["nokey"])

    def test_look_needs_audit(self) -> None:
        """--look without --audit is refused, so a drawing is never written from settings the map does not hold."""
        self.assertEqual(render_flowmap.main(["--root", str(ROOT / "examples" / "shop"), "--map", "flows.yaml", "--look", "x=1"]), 2)


if __name__ == "__main__":
    unittest.main()
