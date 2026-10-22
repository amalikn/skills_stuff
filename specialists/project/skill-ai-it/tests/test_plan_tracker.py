"""scripts/plan_tracker.py: the starter page passes its own shape checks once filled; missing sections, unlinked or split What next rows
and a missing As of line fail; split rows elsewhere and a stale As of are notes. Offline: works in a temporary folder."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("plan_tracker", _ROOT / "scripts/plan_tracker.py")
pt = importlib.util.module_from_spec(_spec)
sys.modules["plan_tracker"] = pt
_spec.loader.exec_module(pt)


def page(where="As of 2026-10-22. Live.", next_rows="| 1 | Do [x](a.md#b) | Agent | Done |", other_rows="| A | B | C | D |"):
    """A minimal tracker with every required section."""
    return (f"# Plan tracker\n\n## Where we are\n\n{where}\n\n### Timeline\n\n<!-- BEGIN GENERATED: plan-timeline -->\n<!-- END GENERATED: plan-timeline -->\n\n"
            f"## What next\n\n| # | Next | Owner | Done when |\n| --- | --- | --- | --- |\n{next_rows}\n\n"
            f"## Which document to follow\n\n| Topic | Follow | State | Inputs |\n| --- | --- | --- | --- |\n{other_rows}\n\n"
            "## Decided but not yet in the designs\n\n| Decision | Goes into | Done |\n| --- | --- | --- |\n\n"
            "## Stages\n\n<!-- BEGIN GENERATED: target-map -->\n<!-- END GENERATED: target-map -->\n\n## How this page is kept\n\n- Kept.\n")


class PlanTrackerCheck(unittest.TestCase):
    """check() problems and notes."""

    def run_check(self, text, changelog=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/trackers").mkdir(parents=True)
            (root / pt.PAGE).write_text(text, encoding="utf-8")
            if changelog:
                (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            return pt.check(root)

    def test_a_good_page_passes(self):
        self.assertEqual(self.run_check(page()), ([], []))

    def test_missing_section_and_as_of_fail(self):
        problems, _ = self.run_check(page(where="Live.").replace("## How this page is kept", "## Notes"))
        self.assertTrue(any("How this page is kept" in p for p in problems))
        self.assertTrue(any("As of" in p for p in problems))

    def test_unlinked_or_split_what_next_row_fails(self):
        problems, _ = self.run_check(page(next_rows="| 1 | Do it | Agent | Done |"))
        self.assertTrue(any("no link" in p for p in problems))
        problems, _ = self.run_check(page(next_rows="| 1 | Do [x](a.md) | Agent | Done |\n|   |   more | | |"))
        self.assertTrue(any("split" in p and "What next" in p for p in problems))

    def test_split_rows_elsewhere_and_stale_as_of_are_notes(self):
        problems, notes = self.run_check(page(other_rows="| A | B | C | D |\n|   | more | | |"), changelog="## 20261023_0900 — Later\n")
        self.assertEqual(problems, [])
        self.assertTrue(any("Which document" in n for n in notes))
        self.assertTrue(any("older than the newest CHANGELOG" in n for n in notes))

    def test_template_has_every_section(self):
        text = pt.TEMPLATE.read_text(encoding="utf-8")
        secs = pt.sections(text)
        for name in pt.SECTIONS:
            self.assertIsNotNone(pt.find(secs, name), name)


class PlanTrackerInit(unittest.TestCase):
    """init() writes only when the page is absent."""

    def test_init_writes_once_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(pt.init(root, pt.PAGE, apply=False), 0)
            self.assertFalse((root / pt.PAGE).exists())
            self.assertEqual(pt.init(root, pt.PAGE, apply=True), 0)
            self.assertIn("## What next", (root / pt.PAGE).read_text(encoding="utf-8"))
            self.assertEqual(pt.init(root, pt.PAGE, apply=True), 1)


if __name__ == "__main__":
    unittest.main()
