"""Offline tests for the Options page (flowmap.options, added 2026-10-21): a map without an `options` block renders exactly as before, a map
with one gains a page after the Overview whose decision flow and option chains pass every layout audit, decision arrows end on the chosen heads only, and
duplicate option ids are refused.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

audit, mxfile = (importlib.import_module(f"drawio.{n}") for n in ("audit", "mxfile"))
model, options, pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("model", "options", "pages", "profile"))
TestMap = importlib.import_module("test_layout_rules")


def _block() -> dict:
    """An options block: one decided group of three options (the chosen one last, so its arrow crosses the gap above the others) and one open.

    Returns:
        The block as loaded YAML would be.
    """
    opt = {"steps": ["one", "two", "three"], "pros": ["p"], "cons": ["c"]}
    return {"title": "Choices", "decisions": ["start here"], "groups": [
        {"id": "g1", "title": "Q1", "decision": "take c", "options": [
            {"id": "a", "title": "A", "status": "rejected", **opt}, {"id": "b", "title": "B", "status": "evaluate", **opt},
            {"id": "c", "title": "C", "status": "chosen", **opt}]},
        {"id": "g2", "title": "Q2", "options": [{"id": "x", "title": "X", "status": "open", **opt}]}]}


class OptionsPageTests(unittest.TestCase):
    """The Options page's contract."""

    def setUp(self) -> None:
        """Build a minimal map and the generic profile."""
        self.data = TestMap._minimal()
        self.profile = TestMap._profile(self.data)

    def test_no_block_renders_as_before(self) -> None:
        """Without `options` the file has no Options page, so existing consumers stay byte-identical."""
        text = pages.render(self.data, self.profile)
        self.assertNotIn('id="options"', text)
        self.assertNotIn("ov-f-options", text)

    def test_block_adds_a_clean_last_page(self) -> None:
        """With `options` the second page (right after the Overview) is the Options page, every audit is clean, and the legend is drawn."""
        self.data["options"] = _block()
        text = pages.render(self.data, self.profile)
        ids = [m.split('"')[1] for m in text.split("<diagram id=")[1:]]
        self.assertEqual(ids[:2], ["overview", "options"])
        self.assertIn("opt-leg-title", text)
        self.assertIn('id="ov-f-options"', text)   # the Overview's flow index links the page
        self.assertEqual(audit.faults(audit.page_audit(options.options_page(self.data, self.profile))), [])

    def test_decision_arrows_reach_chosen_heads_only(self) -> None:
        """A decided group's arrow ends on its chosen head; an evaluated or open option gets none; the decision boxes are chained."""
        self.data["options"] = _block()
        page = options.options_page(self.data, self.profile)
        targets = {r.dst for r in page.routes if r.src.startswith("opt-dec-") and not r.dst.startswith("opt-dec-")}
        self.assertEqual(targets, {"opt-g1-c-head"})

    def test_open_question_points_at_evaluated_option(self) -> None:
        """A group with a decision text but no chosen option stays open: blue box, a dashed arrow to the evaluated option only."""
        block = _block()
        block["groups"][0]["options"][2]["status"] = "rejected"
        self.data["options"] = block
        page = options.options_page(self.data, self.profile)
        arrows = [r for r in page.routes if r.src == "opt-dec-g1" and not r.dst.startswith("opt-dec-")]
        self.assertEqual([r.dst for r in arrows], ["opt-g1-b-head"])
        self.assertIn("dashed=1", next(c for c in page.cells if 'id="opt-dec-g1-to-b"' in c))
        self.assertIn("Decision 1: open", next(c for c in page.cells if 'id="opt-dec-g1"' in c))
        chain = [(r.src, r.dst) for r in page.routes if r.dst.startswith("opt-dec-")]
        self.assertEqual(chain, [("opt-dec-start", "opt-dec-g1"), ("opt-dec-g1", "opt-dec-g2")])

    def test_two_evaluated_options_get_their_own_tracks(self) -> None:
        """Two options under evaluation in one open group (unified-network-controller asset custody, operator review 2026-10-22): two dashed
        arrows, each on its own run (no shared run), the nearer one lower, and the page audit clean."""
        block = _block()
        block["groups"][0]["options"][0]["status"] = "evaluate"
        block["groups"][0]["options"][2]["status"] = "rejected"
        self.data["options"] = block
        page = options.options_page(self.data, self.profile)
        arrows = sorted((r for r in page.routes if r.src == "opt-dec-g1" and not r.dst.startswith("opt-dec-")), key=lambda r: r.points[-1][0])
        self.assertEqual([r.dst for r in arrows], ["opt-g1-a-head", "opt-g1-b-head"])
        self.assertGreater(arrows[0].points[0][1], arrows[1].points[0][1])
        self.assertEqual(audit.faults(audit.page_audit(page)), [])

    def test_skipping_arrow_climbs_in_target_column(self) -> None:
        """An arrow from step 1 to step 3 in another lane, with step 2 in step 3's lane, enters step 3 from below (2026-10-21: 6 to 8 crossed 7)."""
        steps = [{"id": "pre", "actor": "a"}, {"id": "check", "actor": "h", "next": ["keep", "revert"]}, {"id": "keep", "actor": "a", "next": []},
                 {"id": "revert", "actor": "a"}]
        edges = {(a, b): st for _, a, b, _, st in pages.step_edges(steps, "f")}
        self.assertIn("entryX=0;", edges[("check", "keep")])          # next column: enters from the left as before
        self.assertIn("entryY=1;", edges[("check", "revert")])        # skips keep, lane above: enters from below
        self.assertNotIn("entryX=0;", edges[("check", "revert")])

    def test_duplicate_option_ids_are_refused(self) -> None:
        """Two options with one id in a group is a reference problem (negative test: the rule can fail)."""
        block = _block()
        block["groups"][0]["options"][1]["id"] = "a"
        self.data["options"] = block
        found = model.reference_problems(self.data, ROOT)
        self.assertTrue(any("option in group g1" in p for p in found), found)


    def test_option_pages_by_subject(self) -> None:
        """`option_pages` draws one page per subject after the Overview, each tab its title with no "Options:" prefix, each linked and clean."""
        first, second = _block(), _block()
        second["groups"] = [dict(g, id=g["id"] + "b") for g in second["groups"]]
        self.data["option_pages"] = [dict(first, id="updates", title="Updates and releases"), dict(second, id="layout", title="Boot and rescue")]
        text = pages.render(self.data, self.profile)
        ids = [m.split('"')[1] for m in text.split("<diagram id=")[1:]]
        self.assertEqual(ids[:3], ["overview", "options-updates", "options-layout"])
        self.assertIn('name="Updates and releases"', text)
        self.assertNotIn('name="Options:', text)
        self.assertIn('id="ov-f-options-layout"', text)
        for pid, name, block in model.option_blocks(self.data):
            self.assertEqual(audit.faults(audit.page_audit(options.options_page(self.data, self.profile, block, pid, name))), [])

    def test_option_page_and_group_ids_unique_across_pages(self) -> None:
        """A page id used twice, or a group id used on two pages, is refused."""
        self.data["option_pages"] = [dict(_block(), id="same", title="One"), dict(_block(), id="same", title="Two")]
        problems = model.reference_problems(self.data, ROOT)
        self.assertTrue(any("option page" in p for p in problems))
        self.assertTrue(any("option group" in p for p in problems))

if __name__ == "__main__":
    unittest.main()
