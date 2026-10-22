"""scripts/plan_timeline.py: schedule marks follow the dates, a stale page is drift, bad data is refused. Offline."""

import datetime as dt
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("plan_timeline", _ROOT / "scripts/plan_timeline.py")
pt = importlib.util.module_from_spec(_spec)
sys.modules["plan_timeline"] = pt  # dataclasses resolve annotations through the module
_spec.loader.exec_module(pt)
tw = sys.modules["table_wrap"]

D = dt.date


def row(**kw):
    """A valid plan row with overrides.

    Args:
        **kw: fields to set or replace.

    Returns:
        The row as validate() would return it.
    """
    base = {"due": D(2026, 10, 23), "stage": "U1.3", "step": "proof", "done": None}
    base.update(kw)
    return base


class Schedule(unittest.TestCase):
    """schedule()."""

    def test_late_counts_days_and_overrides_a_flag(self):
        """A passed due date is LATE with its day count, whatever the flag says."""
        self.assertEqual(pt.schedule(row(flag="at_risk"), D(2026, 10, 24)), ("🔴 **LATE: 1 day**", "late"))
        self.assertEqual(pt.schedule(row(), D(2026, 10, 28))[0], "🔴 **LATE: 5 days**")

    def test_due_today_then_flag_then_open(self):
        """On the day it is DUE TODAY; before it, the flag or Not yet due."""
        self.assertEqual(pt.schedule(row(), D(2026, 10, 23))[1], "today")
        self.assertEqual(pt.schedule(row(flag="ahead"), D(2026, 10, 1))[0], "🔵 Ahead")
        self.assertEqual(pt.schedule(row(), D(2026, 10, 1))[0], "⚪ Not yet due")

    def test_week_row_is_late_after_its_friday(self):
        """A "Wk of" row is due on that week's Friday."""
        wk = row(due=D(2027, 1, 25), week=True)
        self.assertEqual(pt.schedule(wk, D(2027, 1, 29))[1], "today")
        self.assertEqual(pt.schedule(wk, D(2027, 1, 30))[1], "late")
        self.assertEqual(pt.due_label(wk), "Wk of 25 Jan")
        self.assertEqual(pt.due_label(row()), "Fri 23 Oct")

    def test_done_shows_done_and_how_late(self):
        """A done step is Done, with the days it was late."""
        self.assertEqual(pt.schedule(row(done=D(2026, 10, 22)), D(2026, 12, 1))[0], "✅ Done 22 Oct")
        self.assertEqual(pt.schedule(row(done=D(2026, 10, 26)), D(2026, 12, 1))[0], "✅ Done 26 Oct, 3 days late")

    def test_fixed_and_extra_rows(self):
        """An outside date and work outside the plan are never late."""
        self.assertEqual(pt.schedule(row(kind="fixed"), D(2026, 10, 1))[0], "📌 Fixed date")
        self.assertEqual(pt.schedule(row(kind="fixed"), D(2026, 11, 1))[0], "📌 Passed")
        self.assertEqual(pt.schedule({"kind": "extra", "step": "x"}, D(2026, 11, 1))[0], "➖ Unscheduled")


class Validate(unittest.TestCase):
    """validate()."""

    def test_refuses_bad_flag_kind_date_and_missing_due(self):
        """Each kind of bad row is named."""
        _, problems = pt.validate({"rows": [
            {"due": "2026-10-16", "step": "a", "flag": "late"},
            {"due": "16 Oct", "step": "b"},
            {"step": "c"},
            {"due": "2026-10-16", "step": "d", "kind": "maybe"},
        ]})
        text = "\n".join(problems)
        for part in ("flag 'late'", "not a YYYY-MM-DD", "needs `due`", "kind 'maybe'"):
            self.assertIn(part, text)


class PageDrift(unittest.TestCase):
    """evaluate() and splice() against a page on disk."""

    def test_a_new_day_is_drift_and_text_outside_markers_survives(self):
        """A page rendered yesterday differs from today's render; splice keeps the hand-written text."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/trackers").mkdir(parents=True)
            (root / pt.DATA).write_text(
                "source: the plan\nrender_to: docs/trackers/page.md\nrows:\n  - {due: 2026-10-23, stage: U1.3, step: proof}\n", encoding="utf-8")
            page = root / "docs/trackers/page.md"
            page.write_text(f"before\n{pt.BEGIN}\n{pt.END}\nafter\n", encoding="utf-8")
            first = pt.evaluate(root, D(2026, 10, 22))
            page.write_text(pt.splice(page.read_text(encoding="utf-8"), first.block), encoding="utf-8")
            self.assertFalse(pt.evaluate(root, D(2026, 10, 22)).drift)
            later = pt.evaluate(root, D(2026, 10, 24))
            self.assertTrue(later.drift)
            self.assertIn("LATE: 1 day", later.block)
            text = page.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("before\n") and text.endswith("after\n"))

    def test_page_without_markers_is_a_problem(self):
        """splice() refuses a page that lacks the markers."""
        with self.assertRaises(ValueError):
            pt.splice("no markers here", f"{pt.BEGIN}\n{pt.END}")


class GenericColumns(unittest.TestCase):
    """Promotion to skill-ai-it (2026-10-21): columns, the note and parked rows are data, so no project is named in the code."""

    def test_default_columns(self):
        """Without `columns`, the table is Due, Schedule, Stage, Step, Where it stands, Next with."""
        block = pt.render([row(where="lab", next_with="Agent")], "the plan", D(2026, 10, 1))
        self.assertIn("| Due | Schedule | Stage | Step | Where it stands | Next with |", block)
        self.assertIn("| Fri 23 Oct | ⚪ Not yet due | U1.3 | proof | lab | Agent |", block)

    def test_declared_columns_and_note(self):
        """Declared columns set headers and order; the note follows the source sentence."""
        cols = [{"key": "stage", "header": "Stage"}, {"key": "target_steps", "header": "Our steps"}]
        block = pt.render([row(target_steps="2, 8")], "the plan", D(2026, 10, 1), cols, "Our reading.")
        self.assertIn("Dates and steps are the plan. Our reading.", block)
        self.assertIn("| Due | Schedule | Stage | Our steps |", block)
        self.assertIn("| U1.3 | 2, 8 |", block)

    def test_undeclared_field_is_a_problem(self):
        """A row field that is neither core nor a declared column is refused, so a typo cannot vanish from the table."""
        _, problems = pt.validate({"rows": [{"due": "2026-10-23", "step": "x", "wehre": "typo"}]})
        self.assertTrue(any("`wehre`" in p for p in problems), problems)

    def test_parked_row_needs_no_date_and_is_counted(self):
        """A parked row shows Parked and No date, adds the legend line and a count; it is never LATE."""
        rows, problems = pt.validate({"rows": [{"kind": "parked", "stage": "S1", "step": "A/B boot", "where": "VM first"}]})
        self.assertEqual(problems, [])
        self.assertEqual(pt.schedule(rows[0], D(2027, 1, 1)), ("⏸️ Parked", "parked"))
        block = pt.render(rows, "the plan", D(2026, 10, 21))
        self.assertIn("| No date | ⏸️ Parked | S1 |", block)
        self.assertIn("⏸️ 1 parked (S1)", block)
        self.assertIn("⏸️ Parked: waiting on a decision", block)

    def test_no_parked_rows_no_parked_text(self):
        """Without parked rows the legend and counts are as before promotion (a pilot's page renders byte for byte)."""
        block = pt.render([row()], "the plan", D(2026, 10, 1))
        self.assertNotIn("Parked", block)

    def test_custom_data_path_in_marker(self):
        """The BEGIN marker names the data file a reader must edit."""
        block = pt.render([row()], "the plan", D(2026, 10, 1), data_path="plans/t.yaml")
        self.assertTrue(block.startswith("<!-- BEGIN GENERATED: plan-timeline (edit plans/t.yaml, then `just plan-timeline`) -->"))


    def test_dated_extra_row_is_tracked(self) -> None:
        """An extra row with a due date goes LATE like a plan row; without one it stays Unscheduled."""
        today = pt.dt.date(2026, 10, 21)
        self.assertIn("LATE", pt.schedule({"kind": "extra", "due": pt.dt.date(2026, 10, 19)}, today)[0])
        self.assertEqual(pt.schedule({"kind": "extra", "due": None}, today)[1], "extra")

    def test_rows_by_due_date_with_years_across_years(self) -> None:
        """Rows render in due order, undated last; a timeline across two years names the year on every date."""
        d = pt.dt.date
        rows = [{"due": d(2027, 1, 25), "week": True, "stage": "B", "step": "b"}, {"kind": "parked", "due": None, "stage": "Z", "step": "z"},
                {"due": d(2026, 10, 23), "stage": "A", "step": "a"}]
        self.assertEqual([r["stage"] for r in pt.in_order(rows)], ["A", "B", "Z"])
        self.assertEqual(pt.due_label(rows[0], True), "Wk of 25 Jan 2027")
        self.assertEqual(pt.due_label(rows[2]), "Fri 23 Oct")

class AfterPlacement(unittest.TestCase):
    """`after:` places an undated row beside the plan step it belongs to."""

    def test_undated_row_follows_its_stage_and_others_stay_last(self):
        """X goes after U1, Y after U2 and Z (no `after`) last, each in file order."""
        rows, problems = pt.validate({"rows": [
            {"due": "2026-11-20", "stage": "U2", "step": "b"},
            {"kind": "extra", "step": "z"},
            {"due": "2026-10-16", "stage": "U1", "step": "a"},
            {"kind": "extra", "step": "y", "after": "U2"},
            {"kind": "extra", "step": "x", "after": "U1"},
        ]})
        self.assertEqual(problems, [])
        self.assertEqual([r["step"] for r in pt.in_order(rows)], ["a", "x", "b", "y", "z"])

    def test_unknown_stage_and_dated_row_are_refused(self):
        """`after` must name a dated row's stage, and only an undated row may carry it."""
        _, problems = pt.validate({"rows": [
            {"due": "2026-10-16", "stage": "U1", "step": "a"},
            {"kind": "extra", "step": "x", "after": "U9"},
            {"due": "2026-10-20", "stage": "U2", "step": "b", "after": "U1"},
        ]})
        text = "\n".join(problems)
        self.assertIn("`after: U9` names no dated row's stage", text)
        self.assertIn("a row with `due` is placed by its date", text)


    def test_extra_before_plan_row_on_one_date(self) -> None:
        """On one date the extra row that feeds a plan row comes first."""
        d = pt.dt.date
        same = [{"due": d(2026, 11, 6), "stage": "R2.1", "step": "p"}, {"kind": "extra", "due": d(2026, 11, 6), "stage": "", "step": "feeds"}]
        self.assertEqual([r["step"] for r in pt.in_order(same)], ["feeds", "p"])

class WrapTable(unittest.TestCase):
    """wrap_table: the Timeline table goes through the markdown hook's table formatter, or stays as it is (operator, 2026-10-22)."""

    TABLE = "| Due | Step |\n| --- | --- |\n| Fri 23 Oct 2026 | a long step |"

    def test_zero_width_keeps_one_line_per_row(self):
        """wrap 0 never calls the formatter."""
        calls = []
        self.assertEqual(tw.wrap_table(self.TABLE, 0, lambda *a, **k: calls.append(a)), self.TABLE)
        self.assertEqual(calls, [])

    def test_formatter_output_is_used_and_flags_match_the_hook(self):
        """The formatter runs on a temporary file with --width and --measure-rendered; its table replaces the input."""
        seen = {}

        class Done:
            returncode, stdout = 0, "| Due | Step |\n| --- | --- |\n| Fri 23 Oct | a long |\n|  | step |\n"

        def fake(argv, **kw):
            seen["argv"], seen["input"] = argv, Path(argv[2]).read_text(encoding="utf-8")
            return Done()
        orig_file, orig_which = tw.Path.is_file, tw.shutil.which
        tw.Path.is_file, tw.shutil.which = lambda self: True, lambda name: "/usr/bin/node"
        try:
            out = tw.wrap_table(self.TABLE, 120, fake)
        finally:
            tw.Path.is_file, tw.shutil.which = orig_file, orig_which
        self.assertEqual(seen["argv"][-3:], ["--width", "120", "--measure-rendered"])
        self.assertTrue(seen["input"].startswith("| Due |"))
        self.assertEqual(out.splitlines()[-1], "|  | step |")

    def test_a_failing_formatter_leaves_the_table(self):
        """A non-zero exit or empty output leaves the table unwrapped."""
        class Bad:
            returncode, stdout = 1, ""
        orig_file, orig_which = tw.Path.is_file, tw.shutil.which
        tw.Path.is_file, tw.shutil.which = lambda self: True, lambda name: "/usr/bin/node"
        try:
            self.assertEqual(tw.wrap_table(self.TABLE, 120, lambda *a, **k: Bad()), self.TABLE)
        finally:
            tw.Path.is_file, tw.shutil.which = orig_file, orig_which


if __name__ == "__main__":
    unittest.main()


class LinkIds(unittest.TestCase):
    """link_ids: plain ids in a declared column link to their headings (2026-10-22)."""

    def _project(self, tmp, column, cell):
        """A project with a step tracker, a page and one row.

        Args:
            tmp: the temporary folder.
            column: the column's YAML mapping text.
            cell: the row's value for that column (YAML scalar text).

        Returns:
            The project root.
        """
        root = Path(tmp)
        (root / "docs/trackers").mkdir(parents=True)
        (root / "docs/trackers/steps.md").write_text(
            "# Steps\n\n### Step 1 — Unattended transport\n\n### Step 10 — Remaining families\n\n### Step CA — Code: stages\n", encoding="utf-8")
        (root / pt.DATA).write_text(
            "source: the plan\nrender_to: docs/trackers/page.md\n"
            f"columns:\n  - {{key: step, header: Step}}\n  - {column}\nrows:\n  - {{due: 2026-10-23, step: proof, ours: {cell}}}\n",
            encoding="utf-8")
        (root / "docs/trackers/page.md").write_text(f"{pt.BEGIN}\n{pt.END}\n", encoding="utf-8")
        return root

    def test_ids_link_to_their_heading_and_unknown_ids_stay_plain(self):
        """1 and CA link (not to Step 10); 7 has no heading and stays text; separators are kept."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, '{key: ours, header: Ours, link_ids: {page: docs/trackers/steps.md, heading: "Step {id}"}}', '"1, CA,7"')
            out = pt.evaluate(root, D(2026, 10, 22))
            self.assertEqual(out.problems, [])
            self.assertIn("[1](steps.md#step-1--unattended-transport), [CA](steps.md#step-ca--code-stages),7", out.block)

    def test_a_cell_with_a_hand_link_is_left_alone(self):
        """A hand-written link keeps the whole cell as written."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, '{key: ours, header: Ours, link_ids: {page: docs/trackers/steps.md, heading: "Step {id}"}}', '"[x](y.md), 1"')
            self.assertIn("[x](y.md), 1 ", pt.evaluate(root, D(2026, 10, 22)).block)

    def test_missing_page_and_bad_spec_are_problems(self):
        """A link_ids page that does not exist, or a spec without a page, is refused."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, "{key: ours, header: Ours, link_ids: {page: docs/none.md}}", '"1"')
            self.assertIn("does not exist", pt.evaluate(root, D(2026, 10, 22)).problems[0])
        cols, problems = pt.columns_of({"columns": [{"key": "a", "header": "A", "link_ids": "x"}]})
        self.assertTrue(problems)
