"""Offline tests for scripts/upgrade_navigation_control_layer.py: the CHANGELOG entry it writes carries the YYYYMMDD_hhmm stamp and lands first in a newest-first log."""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "upgrade_navigation_control_layer.py"
_spec = importlib.util.spec_from_file_location("upgrade_navigation_control_layer", SCRIPT)
unc = importlib.util.module_from_spec(_spec)
sys.modules["upgrade_navigation_control_layer"] = unc
_spec.loader.exec_module(unc)

NEWEST_FIRST = "# Changelog\n\n## 20261010_1847 — Older entry\n\n- a\n\n## 20261009_1200 — Oldest\n\n- b\n"


def _report(root: str) -> dict:
    """A minimal report_data as main() builds it.

    Args:
        root: the project root the report describes.

    Returns:
        The report dictionary append_changelog reads and fills.
    """
    return {"project_root": root, "changed_files": [], "skipped_files": [], "proposed_files": [], "warnings": []}


class AppendChangelogTest(unittest.TestCase):
    """append_changelog() heading stamp and placement."""

    def test_heading_uses_stamp_and_goes_first(self):
        """The entry heading is `## YYYYMMDD_hhmm — ...` (not an ISO date) and is the first `##` heading of a newest-first log."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text(NEWEST_FIRST)
            unc.append_changelog(str(path), False, _report(tmp), "Applied to: AGENTS.md")
            headings = re.findall(r"^## (.+)$", path.read_text(), re.M)
            self.assertRegex(headings[0], r"^\d{8}_\d{4} — deterministic navigation-control upgrade$")
            self.assertNotRegex(headings[0], r"^\d{4}-\d{2}-\d{2}")

    def test_second_run_is_idempotent(self):
        """A log that already holds the upgrade marker is left unchanged."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text(NEWEST_FIRST)
            unc.append_changelog(str(path), False, _report(tmp), "")
            once = path.read_text()
            unc.append_changelog(str(path), False, _report(tmp), "")
            self.assertEqual(once, path.read_text())


if __name__ == "__main__":
    unittest.main()
