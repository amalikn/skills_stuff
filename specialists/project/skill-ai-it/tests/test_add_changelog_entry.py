"""Offline tests for scripts/add_changelog_entry.py: each project's heading style and order, the Contents line, and plan-only by default."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "add_changelog_entry.py"
_spec = importlib.util.spec_from_file_location("add_changelog_entry", SCRIPT)
ace = importlib.util.module_from_spec(_spec)
sys.modules["add_changelog_entry"] = ace
_spec.loader.exec_module(ace)

DASH = """# Changelog

## Contents

- [20261010_1847 — Older entry](#20261010_1847--older-entry)
- [20261009_1200 — Oldest](#20261009_1200--oldest)

## 20261010_1847 — Older entry

- a

## 20261009_1200 — Oldest

- b
"""

BRACKET = "# Changelog\n\n## 20261010_1806 (governed files)\n\n- a\n\n## 20260902_1030 (rsync gate)\n\n- b\n"
DATED = "# Changelog\n\n## 2026-10-10 (governed files, 20261010_1819) — budgets\n\n- a\n\n## 2026-09-03 (audit, 20260903_1200) — x\n\n- b\n"
OLDEST_FIRST = "# Changelog\n\n## 2026-08-01 — first\n\n- a\n\n## 2026-09-01 — second\n\n- b\n"


class AddEntryTest(unittest.TestCase):
    """add() and main() on each style."""

    def test_dash_style_newest_first_with_contents(self):
        new, head, where = ace.add(DASH, "Navigation compact", "- c", "20261010_2300")
        self.assertEqual((head, where), ("20261010_2300 — Navigation compact", "top"))
        self.assertLess(new.index("## 20261010_2300 — Navigation compact"), new.index("## 20261010_1847"))
        self.assertLess(new.index("- [20261010_2300 — Navigation compact](#20261010_2300--navigation-compact)"),
                        new.index("- [20261010_1847 — Older entry]"))

    def test_bracket_and_dated_styles(self):
        new, head, _ = ace.add(BRACKET, "budget pass", "- c", "20261010_2300")
        self.assertEqual(head, "20261010_2300 (budget pass)")
        new, head, _ = ace.add(DATED, "every file within budget", "- c", "20261010_2300", label="budget")
        self.assertEqual(head, "2026-10-10 (budget, 20261010_2300) — every file within budget")
        self.assertLess(new.index(head), new.index("2026-10-10 (governed files"))

    def test_oldest_first_appends(self):
        new, head, where = ace.add(OLDEST_FIRST, "third", "- c", "20261010_2300")
        self.assertEqual((head, where), ("2026-10-10 — third", "end"))
        self.assertTrue(new.rstrip().endswith("- c"))

    def test_plan_does_not_write_and_apply_does(self):
        root = Path(tempfile.mkdtemp())
        (root / "CHANGELOG.md").write_text(DASH)
        base = ["--project-root", str(root), "--title", "t", "--body", "- c", "--stamp", "20261010_2300"]
        self.assertEqual(ace.main(base), 0)
        self.assertEqual((root / "CHANGELOG.md").read_text(), DASH)
        self.assertEqual(ace.main(base + ["--apply"]), 0)
        self.assertIn("## 20261010_2300 — t", (root / "CHANGELOG.md").read_text())
        self.assertEqual(ace.main(["--project-root", str(root), "--title", "t", "--body", " "]), 1)

    def test_bare_stamp_style_and_newest_entry_sets_the_style(self):
        bare = "# Changelog\n\n## 20261010_1806\n\n- a\n\n## 20260831_1252\n\n- b\n"
        new, head, where = ace.add(bare, "smoke", "- c", "20261010_2300")
        self.assertEqual((head, where), ("20261010_2300", "top"))
        self.assertIn("## 20261010_2300\n\n**smoke**\n\n- c", new)
        mixed = "# Changelog\n\n## 2026-09-13\n\n- a\n\n## 20261010_1805 — later\n\n- b\n"
        new, head, where = ace.add(mixed, "next", "- c", "20261010_2300")
        self.assertEqual((head, where), ("20261010_2300 — next", "end"))


if __name__ == "__main__":
    unittest.main()
