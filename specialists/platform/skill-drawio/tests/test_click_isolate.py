"""`look.click_isolate` on End-to-end, Overview and step pages, and the End-to-end band search and label ground.

Run: just test.
"""

import importlib
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from test_e2e_family import _diagrams, _map, _render  # the shared map helpers

band_pool, e2e, isolate, pages, profile, step_labels = (importlib.import_module(f"flowmap.{n}")
                                                        for n in ("band_pool", "e2e", "isolate", "pages", "profile", "step_labels"))


class ClickIsolate(unittest.TestCase):
    """`look.click_isolate`: one click shows a colour alone, a second shows all, a click on another colour switches (draw.io 32.5.5 rules)."""

    @staticmethod
    def _cells(page: ET.Element) -> dict:
        """Every cell of a page by id, with its tags and link.

        Args:
            page: the `<diagram>` element.

        Returns:
            {id: (tags, link)}.
        """
        out = {}
        for e in page.iter():
            if e.tag in ("mxCell", "UserObject") and e.get("id") and e.get("id") not in out:
                out[e.get("id")] = ((e.get("tags") or "").split(), e.get("link") or "")
        return out

    def _run(self, link: str, cells: dict, style: dict) -> None:
        """Replay a link as draw.io 32.5.5 does: transient, so a toggleStyle decides per cell (its value unless the cell holds it already).

        Args:
            link: the `data:action/json,...` text.
            cells: {id: (tags, link)} of the page.
            style: {(id, key): value}, changed in place.
        """
        for act in json.loads(link.split(",", 1)[1])["actions"]:
            kind, sel = next((k, v) for k, v in act.items() if k in ("toggleStyle", "style"))
            ids = list(sel.get("cells", []))
            want = sel.get("tags", [])
            match = any if sel.get("tagsMatch") == "or" else all
            ids += [c for c, (tags, _l) in cells.items() if want and match(t in tags for t in want) and c not in ids]
            ids = [c for c in ids if c not in sel.get("excludeCells", [])]
            key = sel["key"]
            self.assertIs(sel.get("transient"), True)   # never a saved change: a click on a cell defaults to one in draw.io
            for c in ids:
                if kind == "toggleStyle":
                    held = style.get((c, key), sel["defaultValue"])
                    style[(c, key)] = sel["defaultValue"] if held == sel["value"] else sel["value"]
                else:
                    style[(c, key)] = sel["value"]

    def _page(self, page_id: str, **look: object) -> dict:
        """One rendered page's cells.

        Args:
            page_id: the diagram id.
            **look: look keys.

        Returns:
            {id: (tags, link)}.
        """
        return self._cells(next(d for d in _diagrams(_render(_map(**look))) if d.get("id") == page_id))

    def test_box_click_shows_its_arrows_on_the_e2e_page(self) -> None:
        """A box click keeps the box, every arrow touching it and their far boxes; a second click restores; other arrows dim."""
        cells = self._page("end-to-end", e2e_layers="flow", click_isolate=True)
        boxes = [c for c, (tags, link) in cells.items() if c.startswith("e2e-c-") and link.startswith("data:action") and "box" in tags]
        self.assertTrue(boxes)
        own = next(t for t in cells[boxes[0]][0] if t == f"node-{boxes[0].removeprefix('e2e-c-')}")
        touching = [c for c, (tags, _l) in cells.items() if own in tags and c not in boxes]
        self.assertTrue(touching)
        style: dict = {}
        self._run(cells[boxes[0]][1], cells, style)
        self.assertEqual(style.get((boxes[0], "opacity"), "100"), "100")
        for cid in touching:
            self.assertEqual(style[(cid, "opacity")], "100")
        others = [c for c, (tags, _l) in cells.items() if "step-arrow" in tags and own not in tags]
        self.assertTrue(others and all(style[(c, "opacity")] != "100" for c in others))
        self._run(cells[boxes[0]][1], cells, style)
        self.assertTrue(all(v == "100" for v in style.values()))

    def test_step_page_arrow_shows_one_and_box_its_arrows(self) -> None:
        """Step page: an arrow click keeps that arrow, its label and its boxes only; a box click keeps its arrows; a flow link stays a link."""
        data = _map(click_isolate=True)
        diagram = next(d for d in _diagrams(_render(data)) if d.get("id", "").startswith("flow-"))
        cells = self._cells(diagram)
        arrows = [c for c, (tags, link) in cells.items() if "step-arrow" in tags and link.startswith("data:action") and "-l" not in c[-2:]]
        self.assertGreater(len(arrows), 1)
        style: dict = {}
        self._run(cells[arrows[0]][1], cells, style)
        self.assertEqual(style[(arrows[0], "opacity")], "100")
        own = next(t for t in cells[arrows[0]][0] if t.startswith("arrow-"))
        self.assertTrue(all(style[(c, "opacity")] != "100" for c in arrows if own not in cells[c][0]))   # its label shares the tag and stays lit
        self._run(cells[arrows[0]][1], cells, style)
        self.assertTrue(all(v == "100" for v in style.values()))
        boxes = [c for c, (tags, link) in cells.items() if "step-box" in tags and link.startswith("data:action")]
        self.assertTrue(boxes)
        self._run(cells[boxes[0]][1], cells, style)
        node = next(t for t in cells[boxes[0]][0] if t.startswith("node-"))
        self.assertTrue(all(style[(c, "opacity")] == "100" for c in arrows if node in cells[c][0]))

    def test_click_off_draws_no_step_links(self) -> None:
        """Without `look.click_isolate` no step page has a click action or a node tag."""
        text = _render(_map())
        self.assertNotIn("node-", text)
        self.assertNotIn("step-box", text)

    def test_click_toggles_and_switches_on_the_e2e_page(self) -> None:
        """Click a flow: only its cells stay at 100; click it again: all at 100; click another straight away: that one alone."""
        cells = self._page("end-to-end", e2e_layers="flow", click_isolate=True)
        clickable = {c: link for c, (tags, link) in cells.items() if link.startswith("data:action")}
        kinds = {k for c in clickable for k in ("step-arrow", "connector", "legend") if k in cells[c][0]}
        self.assertEqual(kinds, {"step-arrow", "connector", "legend"})
        dimmable = [c for c, (tags, _l) in cells.items() if set(tags) & {"step-arrow", "connector", "box", "legend"}]

        def shown(style: dict) -> set:
            return {c for c in dimmable if style.get((c, "opacity"), "100") == "100"}

        arrow = {f: next(c for c, (t, _l) in cells.items() if "step-arrow" in t and f"flow-{f}" in t) for f in ("checkout", "refund")}
        style: dict = {}
        self._run(clickable[arrow["checkout"]], cells, style)
        self.assertEqual(shown(style), {c for c in dimmable if "flow-checkout" in cells[c][0]})
        self._run(clickable[arrow["checkout"]], cells, style)
        self.assertEqual(shown(style), set(dimmable))
        self._run(clickable[arrow["checkout"]], cells, style)
        self._run(clickable["e2e-leg-refund-t"], cells, style)   # switch straight to another flow
        self.assertEqual(shown(style), {c for c in dimmable if "flow-refund" in cells[c][0]})
        self.assertTrue(style[("e2e-leg-checkout-t", "textOpacity")].startswith("15."))   # the other legend rows dim too
        self._run(clickable["e2e-leg-refund-t"], cells, style)
        self.assertEqual(shown(style), set(dimmable))
        self.assertNotIn("e2e-leg-all", cells)

    def test_overview_colours_toggle_and_layers_lock(self) -> None:
        """An Overview thick arrow shows its colour alone (arrows, counts, dots, legend row) and toggles back; clickable layers are locked."""
        rendered = _render(_map(click_isolate=True))
        page = _diagrams(rendered)[0]
        cells = self._cells(page)
        thick = next(c for c, (t, link) in cells.items() if "ov-thick" in t and c.startswith("ov-gg-"))
        own = next(t for t in cells[thick][0] if t.startswith("into-"))
        style: dict = {}
        self._run(cells[thick][1], cells, style)
        dimmable = [c for c, (t, _l) in cells.items() if set(t) & {"ov-thick", "ov-thin", "legend"}]
        self.assertEqual({c for c in dimmable if style.get((c, "opacity"), "100") == "100"}, {c for c in dimmable if own in cells[c][0]})
        self._run(cells[thick][1], cells, style)
        self.assertTrue(all(style.get((c, "opacity"), "100") == "100" for c in dimmable))
        layers = {c.get("id"): c.get("style") for c in page.iter("mxCell") if c.get("parent") == "0"}
        self.assertTrue(all(v == "locked=1;" for k, v in layers.items() if k.startswith("ov-L-")))

    def test_off_by_default_and_tab_names(self) -> None:
        """Without the key no cell carries an action link; the base layer is locked by default (one click follows a link; operator, 2026-11-11);
        `e2e_tab` renames the E2E tabs."""
        text = _render(_map(e2e_layers="flow", e2e_family_pages=True))
        self.assertNotIn("data:action/json", text)
        self.assertIn('style="locked=1;"', text)
        names = [d.get("name") for d in _diagrams(_render(_map(e2e_family_pages=True, e2e_tab="E2E")))]
        self.assertIn("E2E flow", names)
        self.assertTrue([n for n in names if n.startswith("E2E: ")])
        self.assertIsNone(isolate.dim_level({}))

    def test_lock_base_layer_on_every_page(self) -> None:
        """`lock_base_layer` draws layer 1 locked on every page; off, no page has it."""
        for value, want in ((True, 'style="locked=1;"'), (False, None)):
            for d in _diagrams(_render(_map(lock_base_layer=value, e2e_family_pages=True))):
                base = next(c for c in d.iter("mxCell") if c.get("id") == "1")
                self.assertEqual(base.get("style"), want and "locked=1;", d.get("id"))

class BandSearch(unittest.TestCase):
    """`look.e2e_band_search`: band boxes swap only when the real routes cross less; labels take the colour beneath them."""

    def test_swap_taken_only_on_a_strict_drop(self) -> None:
        """A swap that cuts crossings is kept; with the key off, or when none gains, the page is the one already laid out."""
        data = _map()
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        base = e2e.EndToEnd(data, prof)
        band = [c for c, (_col, r) in base.cell.items() if r >= base.band]
        build = lambda swaps=(): e2e.EndToEnd(data, prof, None, swaps)
        kept = band_pool.band_search(base, build, prof.look)
        self.assertLessEqual(kept._crossings(set(kept.segs)), base._crossings(set(base.segs)))
        self.assertIs(band_pool.band_search(base, build, {"e2e_band_search": False}), base)
        if len(band) > 1:
            swapped = e2e.EndToEnd(data, prof, None, ((band[0], band[1]),))
            self.assertEqual(swapped.cell[band[0]], base.cell[band[1]])

    def test_label_takes_the_ground_beneath_it(self) -> None:
        """Inside a stripe or the band the colour is that fill; off both it is white."""
        grounds = [(0, 0, 10, 10, e2e.STRIPE_FILL), (0, 20, 30, 30, e2e.BAND_FILL)]
        self.assertEqual(step_labels.ground_at(grounds, 5, 5), e2e.STRIPE_FILL)
        self.assertEqual(step_labels.ground_at(grounds, 25, 25), e2e.BAND_FILL)
        self.assertEqual(step_labels.ground_at(grounds, 25, 5), "#ffffff")


if __name__ == "__main__":
    unittest.main()
