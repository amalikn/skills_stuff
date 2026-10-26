"""Offline tests for flowmap.e2e_family ("e2e_family"): one End-to-end page per family after the full one when `look.e2e_family_pages` is on
(operator, 2026-10-23), drawn from the example shop map.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
(page_audit,) = (importlib.import_module("drawio.audit").page_audit,)
e2e_family, isolate, loops, step_labels, pages, profile = (importlib.import_module(f"flowmap.{n}")
                                                           for n in ("e2e_family", "isolate", "loops", "step_labels", "pages", "profile"))
EXAMPLE = ROOT / "examples" / "shop" / "flows.yaml"


def _map(**look: object) -> dict:
    """The example shop map with look keys pinned.

    Args:
        look: the `drawing.look` keys to set.

    Returns:
        The map.
    """
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    data["drawing"]["look"] = {**(data["drawing"].get("look") or {}), **look}
    return data


def _diagrams(text: str) -> list[ET.Element]:
    """The `<diagram>` elements of a rendered file.

    Args:
        text: the file text (banner comment first).

    Returns:
        The diagrams, in tab order.
    """
    return list(ET.fromstring(text.split("-->", 1)[1]).iter("diagram"))


def _render(data: dict) -> str:
    """Render a map under the profile its drawing block gives.

    Args:
        data: the map.

    Returns:
        The file text.
    """
    return pages.render(data, profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g"))


class FamilyPages(unittest.TestCase):
    """Family End-to-end pages: off by default, after the full page when on, the map's flow numbers, unique ids, audits clean."""

    def test_off_by_default_and_full_page_unchanged(self) -> None:
        """Without the key no family page is drawn; with it the full End-to-end page is byte-identical to before."""
        off, on = _render(_map()), _render(_map(e2e_family_pages=True))
        self.assertFalse([d for d in _diagrams(off) if d.get("id", "").startswith("end-to-end-")])
        full = [ET.tostring(d) for d in _diagrams(off) if d.get("id") == "end-to-end"]
        self.assertEqual(full, [ET.tostring(d) for d in _diagrams(on) if d.get("id") == "end-to-end"])

    def test_one_page_per_family_after_the_full_page(self) -> None:
        """Pages follow the full one in family order, each holding only its family's flows, numbered as in the whole map."""
        data = _map(e2e_family_pages=True, e2e_layers="flow")
        ids = [d.get("id") for d in _diagrams(_render(data))]
        at = ids.index("end-to-end")
        self.assertEqual(ids[at + 1:at + 4], ["end-to-end-orders", "end-to-end-catalogue", "end-to-end-operations"])
        number = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        for fam, _name, part in e2e_family.family_parts(data, prof):
            page = next(d for d in _diagrams(_render(data)) if d.get("id") == f"end-to-end-{fam}")
            labels = {re.match(r"<b>(\d+)\.", u.get("tooltip")).group(1) for u in page.iter("UserObject") if "step-arrow" in (u.get("tags") or "")}
            self.assertEqual(labels, {str(number[f["id"]]) for f in part["flows"]}, fam)

    def test_ids_unique_in_the_file_and_colours_unique_per_page(self) -> None:
        """Family pages rename their ids (no clash with the full page); per-flow colours do not repeat on one page."""
        text = _render(_map(e2e_family_pages=True, e2e_layers="flow"))
        ids = [c.get("id") for d in _diagrams(text) for c in d.iter() if c.get("id") and c.tag in ("mxCell", "UserObject") and c.get("id") not in ("0", "1")]
        self.assertEqual(len(ids), len(set(ids)))
        for d in _diagrams(text):
            if d.get("id", "").startswith("end-to-end-"):
                swatches = [re.search(r"fillColor=(#\w+)", c.get("style")).group(1) for c in d.iter("mxCell")
                            if (c.get("style") or "").startswith("rounded=0") and "strokeColor=none" in c.get("style") and "fillColor=#f" not in c.get("style")]
                self.assertEqual(len(swatches), len(set(swatches)), d.get("id"))

    def test_flow_colours_match_the_full_page(self) -> None:
        """With `e2e_family_colours: flow` each flow keeps its full-page colour on its family page; the default does not for every flow."""
        def colours(data: dict) -> dict:
            prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
            number = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
            groups = {}
            for _fam, _name, part in e2e_family.family_parts(data, prof):
                got, _of = importlib.import_module("flowmap.tips").e2e_groups(part, prof, {f["id"]: number[f["id"]] for f in part["flows"]})
                groups.update({g[0]: g[2] for g in got})
            return groups
        data = _map(e2e_family_pages=True, e2e_layers="flow", e2e_family_colours="flow")
        full = {f["id"]: profile.DISTINCT[(i - 1) % len(profile.DISTINCT)] for i, f in enumerate(data["flows"], 1)}
        self.assertEqual(colours(data), full)
        self.assertNotEqual(colours(_map(e2e_family_pages=True, e2e_layers="flow")), full)

    def test_audits_clean_and_unused_tiers_dropped(self) -> None:
        """Every family page passes the layout audits; a family that touches two tiers draws two columns."""
        data = _map(e2e_family_pages=True)
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        for page in e2e_family.family_pages(data, prof):
            self.assertFalse([k for k, v in page_audit(page).items() if v], page.page_id)
        comps = [c for c in data["components"] if c["group"] in ("People", "Application")]
        self.assertEqual([t[0] for t in e2e_family.narrowed(prof, comps).tiers], ["People", "Application"])

    def test_overview_index_links_each_family_page(self) -> None:
        """The Overview index gains one entry per family page, linking to it."""
        overview = _diagrams(_render(_map(e2e_family_pages=True)))[0]
        links = {u.get("link") for u in overview.iter("UserObject") if (u.get("id") or "").startswith("ov-f-end-to-end-")}
        self.assertEqual(links, {f"data:page/id,end-to-end-{f}" for f in ("orders", "catalogue", "operations")})


def _text(page: ET.Element, prefix: str) -> list[str]:
    """The text of every cell or UserObject on a page whose id starts with a prefix.

    Args:
        page: the `<diagram>` element.
        prefix: the id prefix.

    Returns:
        The labels and values, in file order.
    """
    return [e.get("label") or e.get("value") or "" for e in page.iter() if e.tag in ("mxCell", "UserObject") and (e.get("id") or "").startswith(prefix)]


class StepTotals(unittest.TestCase):
    """`look.e2e_step_total` and `look.e2e_label_font`: step counts on labels (sub, sup, slash) and in the legend, a bigger label box; off, nothing changes."""

    def test_labels_read_x_y_of_n_with_the_font_asked_for(self) -> None:
        """Every step arrow label on the End-to-end page is x.y with n (the flow's steps) as a subscript, at the font asked for; audits clean."""
        data = _map(e2e_layers="flow", e2e_step_total="sub", e2e_label_font=12)
        steps = {str(i): len(f["steps"]) for i, f in enumerate(data["flows"], 1)}
        page = next(d for d in _diagrams(_render(data)) if d.get("id") == "end-to-end")
        labels = [u for u in page.iter("UserObject") if (u.get("id") or "").startswith("e2e-a-") and u.get("id").endswith("-l")]
        self.assertTrue(labels)
        for obj in labels:   # a label is a UserObject (hover text) holding its mxCell
            x, y, n = re.fullmatch(r"<b>(\d+)\.(\d+)<sub>(\d+)</sub></b>", obj.get("label")).groups()
            self.assertEqual(int(n), steps[x], obj.get("id"))
            self.assertLessEqual(int(y), int(n))
            self.assertIn("fontSize=12;", obj.find("mxCell").get("style"))
            self.assertEqual(float(obj.find("mxCell/mxGeometry").get("height")), 18)   # font 12 + 6
        legend = " ".join(_text(page, "e2e-leg-"))
        self.assertIn(f"({steps['1']} steps)", legend)
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        e2e = importlib.import_module("flowmap.e2e").end_to_end_page(data, prof)
        self.assertFalse([k for k, v in page_audit(e2e).items() if v])

    def test_sup_and_slash_forms(self) -> None:
        """`sup` raises n, `slash` writes x.y/n, and `true` means a subscript."""
        for value, pattern in (("sup", r"<b>\d+\.\d+<sup>\d+</sup></b>"), ("slash", r"<b>\d+\.\d+/\d+</b>"), (True, r"<b>\d+\.\d+<sub>\d+</sub></b>")):
            page = next(d for d in _diagrams(_render(_map(e2e_layers="flow", e2e_step_total=value))) if d.get("id") == "end-to-end")
            texts = [u.get("label") for u in page.iter("UserObject") if (u.get("id") or "").startswith("e2e-a-") and u.get("id").endswith("-l")]
            self.assertTrue(texts and all(re.fullmatch(pattern, t) for t in texts), value)

    def test_label_size_from_advance_widths(self) -> None:
        """The defaults hold for x.y at font 10; a subscript count is narrower than /n at the same font."""
        self.assertEqual(step_labels.e2e_label_size([("4.20", "20")], 10, None), (38, 16))
        sub, slash = (step_labels.e2e_label_size([("10.13", "19")], 12, form)[0] for form in ("sub", "slash"))
        self.assertLess(sub, slash)
        self.assertLessEqual(sub + 4, 2 * 24)   # fits between two tracks E2E_SP apart

    def test_off_by_default(self) -> None:
        """Without the keys the labels stay x.y at font 10 and the legend has no step counts."""
        page = next(d for d in _diagrams(_render(_map(e2e_layers="flow"))) if d.get("id") == "end-to-end")
        self.assertNotIn(" steps)", " ".join(_text(page, "e2e-leg-")))
        self.assertFalse([t for t in _text(page, "e2e-a-") if re.search(r"\d/\d", t)])


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
        """Without the key no cell carries an action link and no layer is locked; `e2e_tab` renames the End-to-end tabs."""
        text = _render(_map(e2e_layers="flow", e2e_family_pages=True))
        self.assertNotIn("data:action/json", text)
        self.assertNotIn("locked=1", text)
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

class Loops(unittest.TestCase):
    """`look.e2e_loops`: a step done by the same box as the step before is a loop on that box's roomier edge, every page audit clean."""

    def test_every_stay_is_one_loop_on_its_box(self) -> None:
        """One loop per run of same-box steps, from the box back to it, above or below it, labelled x.y or x.y-z; audits clean; off, none."""
        data = _map(e2e_layers="flow", e2e_loops=True, e2e_family_pages=True)
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        e2e = importlib.import_module("flowmap.e2e").EndToEnd(data, prof)
        runs = loops.loop_runs(e2e)
        self.assertTrue(runs)
        number = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
        for f in data["flows"]:
            acts = [s["actor"] for s in f["steps"]]
            path = ([f["runs_on"]] if f["runs_on"] != acts[0] else [acts[0]]) + acts
            stays = [k + 1 for k in range(len(acts)) if path[k] == path[k + 1]]
            covered = [j for lp in runs if lp.cid.startswith(f"e2e-o-{f['id']}-") for j in self._steps(lp.text, number[f["id"]])]
            self.assertEqual(covered, stays, f["id"])
        page = next(d for d in _diagrams(_render(data)) if d.get("id") == "end-to-end")
        edges = [u for u in page.iter("UserObject") if (u.get("id") or "").startswith("e2e-o-") and not u.get("id").endswith("-l")]
        self.assertEqual(len(edges), len(runs))
        for u in edges:
            cell = u.find("mxCell")
            self.assertEqual(cell.get("source"), cell.get("target"))
            self.assertIn("loop", u.get("tags").split())
        for pg in [importlib.import_module("flowmap.e2e").end_to_end_page(data, prof)] + e2e_family.family_pages(data, prof):
            self.assertFalse([k for k, v in page_audit(pg).items() if v], pg.page_id)
        self.assertFalse([u for u in next(d for d in _diagrams(_render(_map(e2e_layers="flow"))) if d.get("id") == "end-to-end").iter("UserObject")
                          if (u.get("id") or "").startswith("e2e-o-")])

    def test_loops_take_the_roomier_edge(self) -> None:
        """Each box's first loop sits on the edge that had more room before any loop was placed."""
        data = _map(e2e_layers="flow", e2e_loops=True)
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        e2e_mod = importlib.import_module("flowmap.e2e")
        plain = e2e_mod.EndToEnd(_map(e2e_layers="flow"), prof)
        plain.label_h = e2e_mod.EndToEnd(data, prof).label_h
        drawn = e2e_mod.EndToEnd(data, prof)
        first = {}
        for lp in drawn.loops:
            first.setdefault(lp.comp, lp.edge)
        for comp, edge in first.items():
            up, down = loops._room(plain, comp, {})
            self.assertEqual(edge, "top" if up >= down else "bottom", comp)

    @staticmethod
    def _steps(text: str, number: int) -> list[int]:
        """The step numbers a loop label covers.

        Args:
            text: x.y or x.y-z (en dash).
            number: the flow's number.

        Returns:
            The steps, in order.
        """
        a, _, b = text[len(f"{number}."):].partition("\u2013")
        return list(range(int(a), int(b or a) + 1))


if __name__ == "__main__":
    unittest.main()
