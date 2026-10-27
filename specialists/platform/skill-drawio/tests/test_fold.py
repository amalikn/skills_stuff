"""Offline tests for folded flow pages (flowmap.fold, flowmap.fold_turns; operator, 2026-10-27: "after box six box seven can be just below
... add an option of fold"): which steps go in which row, both styles passing every layout audit with arrows between rows (a turn, a skip of
a row, a branch, an arrow back to an earlier row), a right-to-left row in serpentine, a flow's own `layout` over the look, fold off drawing
as before, and the audit failing an arrow drawn through a box in a reversed row.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

audit = importlib.import_module("drawio.audit")
fold, turns, pages = (importlib.import_module(f"flowmap.{n}") for n in ("fold", "fold_turns", "pages"))
TestMap = importlib.import_module("test_layout_rules")


def _long() -> dict:
    """A map whose one flow has eleven steps over two lanes: a decision whose No branch skips into a later row, a skip of a whole row,
    and an arrow back to an earlier row.

    Returns:
        The map.
    """
    data = TestMap._minimal()
    steps = [{"id": f"s{k}", "actor": "ab"[k % 2], "action": "x", "via": ["API"]} for k in range(11)]
    steps[2].update(gate="ok?", next=["s3", "s8"])   # Yes to the next step, No into the third row
    steps[4]["next"] = ["s5", "s10"]   # past a whole row
    steps[9]["next"] = ["s10", "s1"]   # back to the first row
    data["flows"][0]["steps"] = steps
    return data


def _page(data: dict, **look: object) -> object:
    """The map's one flow page under the default look with overrides.

    Args:
        data: the map.
        look: drawing.look keys to set.

    Returns:
        The page.
    """
    prof = TestMap._profile(data)
    prof.look.update(look)
    comps = {c["id"]: c for c in data["components"]}
    return pages.flow_page(data["flows"][0], comps, 1, prof)


class FoldRowsTests(unittest.TestCase):
    def test_rows_off_short_and_long(self) -> None:
        """Off or a flow that fits draws one row; otherwise rows of fold_after steps, the last part-filled; a flow's layout wins."""
        flow = {"steps": [{}] * 11}
        self.assertEqual(fold.fold_rows(flow, {"fold": "off", "fold_after": 4}), [list(range(11))])
        self.assertEqual(fold.fold_rows(flow, {"fold": "z", "fold_after": 11}), [list(range(11))])
        self.assertEqual(fold.fold_rows(flow, {"fold": "z", "fold_after": 4}), [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10]])
        own = dict(flow, layout={"fold": "serpentine", "fold_after": 6})
        self.assertEqual(fold.fold_rows(own, {}), [list(range(6)), list(range(6, 11))])

    def test_a_short_last_row_stretches_the_rows_above(self) -> None:
        """13 steps at 6 a row: not 6, 6 and a lone 1, but 7 and 6 (operator, 2026-10-27); half a row or more still starts a row."""
        look = {"fold": "serpentine", "fold_after": 6}
        self.assertEqual([len(r) for r in fold.fold_rows({"steps": [{}] * 13}, look)], [7, 6])
        self.assertEqual([len(r) for r in fold.fold_rows({"steps": [{}] * 15}, look)], [5, 5, 5])
        self.assertEqual([len(r) for r in fold.fold_rows({"steps": [{}] * 7}, look)], [4, 3])


class TurnsTests(unittest.TestCase):
    def test_tidy_drops_repeats_and_points_straight_through(self) -> None:
        """flowmap "fold_turns".tidy: a repeated point and a point on a straight run go; corners stay."""
        pts = [(0, 0), (10, 0), (10, 0), (20, 0), (20, 5), (20, 9), (30, 9)]
        self.assertEqual(turns.tidy(pts), [(0, 0), (20, 0), (20, 9), (30, 9)])


class FoldedPageTests(unittest.TestCase):
    def test_both_styles_pass_every_audit(self) -> None:
        """Every arrow drawn by the engine, none through a box or along another, labels clear, in both styles and two widths."""
        for style in ("serpentine", "z"):
            for after in (3, 4):
                with self.subTest(style=style, after=after):
                    page = _page(_long(), fold=style, fold_after=after)
                    self.assertEqual(audit.faults(audit.page_audit(page)), [])
                    self.assertEqual(len(page.routes), 13)   # ten next-step arrows, the No branch, the skip and the back arrow
                    self.assertTrue(all(r.points for r in page.routes))

    def test_serpentine_reverses_every_second_row_and_z_does_not(self) -> None:
        """Row two runs right to left in serpentine (step 5 right of step 6), left to right in z; each row repeats both lanes."""
        for style, reversed_ in (("serpentine", True), ("z", False)):
            page = _page(_long(), fold=style, fold_after=4)
            x5, x6 = page.rects["f-s-s4"][0], page.rects["f-s-s5"][0]
            self.assertEqual(x5 > x6, reversed_, style)
            self.assertTrue({"f-lane-0", "f-lane-1", "f-r1-lane-0", "f-r1-lane-1", "f-r2-lane-0"} <= set(page.rects))
            self.assertGreater(page.rects["f-s-s4"][1], page.rects["f-s-s3"][1])   # row two lies below row one

    def test_serpentine_turn_is_one_short_drop(self) -> None:
        """The arrow from a row's last step to the next row's first goes straight down one gutter: three runs, no run back under the row."""
        page = _page(_long(), fold="serpentine", fold_after=4)
        turn = next(r for r in page.routes if r.cid == "f-e-s3-s4")
        self.assertEqual(len(turn.points), 4)
        self.assertEqual(turn.points[1][0], turn.points[2][0])

    def test_fold_off_draws_as_before(self) -> None:
        """With the fold off (the default) the page is the unfolded one, cell for cell."""
        self.assertEqual(_page(_long()).xml(), _page(_long(), fold="off", fold_after=3).xml())
        self.assertNotIn("f-r1-lane-0", _page(_long()).rects)

    def test_one_lane_holds_every_row(self) -> None:
        """A flow with one actor draws one lane, as tall as all its rows, and no lane per row (operator, 2026-10-27: "keep it under the
        same swim lane"); every audit still passes."""
        data = _long()
        for s in data["flows"][0]["steps"]:
            s["actor"] = "a"
        page = _page(data, fold="serpentine", fold_after=4)
        self.assertNotIn("f-r1-lane-0", page.rects)
        x, y, w, h = page.rects["f-lane-0"]
        self.assertGreaterEqual(y + h, page.rects["f-s-s10"][1] + page.rects["f-s-s10"][3])
        self.assertEqual(audit.faults(audit.page_audit(page)), [])

    def test_a_branch_from_mid_row_drops_at_once(self) -> None:
        """A decision mid-row sends its branch to a later row down beside itself, never out past the next step to the row's end and back
        (operator review 2026-10-27 of a z fold: "from 5 to right and then ... a U turn and coming back towards 7")."""
        for style in ("serpentine", "z"):
            page = _page(_long(), fold=style, fold_after=4)
            branch = next(r for r in page.routes if r.cid == "f-e-s2-s8")
            self.assertLess(branch.points[1][0], page.rects["f-s-s3"][0], style)   # its first drop, before the next step

    def test_audit_fails_an_arrow_through_a_box_in_a_reversed_row(self) -> None:
        """Negative: an arrow drawn straight across the reversed row, through its steps, is reported."""
        page = _page(_long(), fold="serpentine", fold_after=4)
        x, y, w, h = page.rects["f-s-s5"]
        a, b = page.rects["f-s-s4"], page.rects["f-s-s7"]
        page.route("f-e-bad", "f-s-s4", "f-s-s7", [(a[0], a[1] + a[3] / 2), (b[0] + b[2], a[1] + a[3] / 2)], "edgeStyle=none;", klass="thin")
        found = audit.faults(audit.page_audit(page))
        self.assertTrue(any(f.startswith("box_crossings: f-e-bad x ") for f in found), found)


if __name__ == "__main__":
    unittest.main()
