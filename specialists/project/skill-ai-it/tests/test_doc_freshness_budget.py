"""Offline tests for scripts/doc_freshness.py budgets: a budget counts lines only (operator, 2026-10-26: "remove file size limit from everywhere..
just use line count"), so a short file of any size passes, a long one fails, and an old header's KB part or baseline's bytes are ignored."""

from __future__ import annotations

import datetime
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("doc_freshness", SCRIPTS / "doc_freshness.py")
df = importlib.util.module_from_spec(_spec)
sys.modules["doc_freshness"] = df
_spec.loader.exec_module(df)

HEAD = "---\nTitle: Changelog\nStatus: current\nSummary: Log.\nLast reviewed: {today}\nBudget: 200 lines, 25 KB\n---\n"


class LineBudget(unittest.TestCase):
    """Only the line count decides whether a budgeted file is over."""

    def _findings(self, body: str) -> dict[str, str]:
        """Findings for a one-file git project holding CHANGELOG.md with the given body.

        Args:
            body: the text after the front matter.

        Returns:
            doc_freshness.findings for that project.
        """
        today = datetime.date.today()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CHANGELOG.md").write_text(HEAD.format(today=today.isoformat()) + body, encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, timeout=30)
            subprocess.run(["git", "add", "CHANGELOG.md"], cwd=root, check=True, timeout=30)
            return df.findings(root, today, 90)

    def test_a_short_large_file_is_within_budget(self) -> None:
        """50 lines of 1,000 characters (about 50 KB, twice the old 25 KB limit) is not over budget."""
        self.assertNotIn("over-budget:CHANGELOG.md", self._findings(("x" * 1000 + "\n") * 50))

    def test_a_long_file_is_over_budget(self) -> None:
        """250 short lines are over a 200-line budget, and the finding names lines only."""
        msg = self._findings("x\n" * 250)["over-budget:CHANGELOG.md"]
        self.assertTrue(msg.startswith("lines="), msg)
        self.assertNotIn("KB", msg)

    def test_old_kb_parts_are_ignored(self) -> None:
        """A header's KB part and a baseline's bytes neither set nor move the budget."""
        self.assertEqual(df.parse_budget("150 lines, 1 KB"), 150)
        self.assertEqual(df.sizes("lines=210 bytes=99999 CHANGELOG.md: over"), 210)
        self.assertFalse(df.regressions({"over-budget:a": "lines=210 a"}, {"over-budget:a": "lines=210 bytes=1 a"}))


if __name__ == "__main__":
    unittest.main()
