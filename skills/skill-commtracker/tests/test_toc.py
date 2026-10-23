"""Offline tests for scripts/toc.py: every entry type in the Contents, GFM anchors, blank line before ---, no silent shrink.

Run: python3 -m unittest discover -s tests   (from the skill folder; no network, no writes outside a temp dir)
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "toc.py"
_spec = importlib.util.spec_from_file_location("commtracker_toc", SCRIPT)
toc = importlib.util.module_from_spec(_spec)
sys.modules["commtracker_toc"] = toc
_spec.loader.exec_module(toc)

HEADINGS = [
    "Email 1 - 20261012_1001 - Field team effort",
    "Meeting 1 - 20261012_1030 - Adam on board",
    "Teams 1 - 20261012_1431 - Martin sets the presentation",
    "Call 1 - 20261012_1500 - Stu + Martin catch-up",
    "Meeting 2 - 20261013 - Hours/attendance: \"hard reset\" meeting",
    "Email 2 - 20261014_1733 - Plan — dates, sent (to Martin)",
]

EXPECTED_ANCHORS = [
    "email-1---20261012_1001---field-team-effort",
    "meeting-1---20261012_1030---adam-on-board",
    "teams-1---20261012_1431---martin-sets-the-presentation",
    "call-1---20261012_1500---stu--martin-catch-up",
    "meeting-2---20261013---hoursattendance-hard-reset-meeting",
    "email-2---20261014_1733---plan--dates-sent-to-martin",
]


def _tracker(old_toc: list[str]) -> str:
    """Build a small tracker with the given old Contents lines.

    Args:
        old_toc: lines to place in the existing Contents block.

    Returns:
        The tracker text.
    """
    body = "".join(f"## {h}\n\nBody of {h}.\n\n---\n\n" for h in HEADINGS)
    return "# Tracker\n\n## Contents\n\n" + "".join(f"{line}\n" for line in old_toc) + "\n---\n\n" + body


def _run(text: str, *flags: str) -> tuple[int, str, str]:
    """Write the tracker to a temp file, run main(), return code, stdout and the file afterwards.

    Args:
        text: tracker content.
        flags: extra command-line flags.

    Returns:
        (exit code, captured stdout and stderr, file text after the run).
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, "communications-tracking.md")
        path.write_text(text, encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                code = toc.main([str(path), *flags])
            except SystemExit as exc:  # the pre-fix script exits instead of returning
                code = exc.code
        return code or 0, buf.getvalue(), path.read_text(encoding="utf-8")


class TocTest(unittest.TestCase):
    """toc.py against a tracker holding all four entry types."""

    def test_all_entry_types_in_file_order(self) -> None:
        """Email, Teams, Call and Meeting entries all appear, in file order."""
        lines = toc.build_toc_lines(_tracker([]))
        self.assertEqual([re.match(r"- \[(.+)\]\(", ln).group(1) for ln in lines], HEADINGS)

    def test_gfm_anchors(self) -> None:
        """Punctuation and / removed; ' + ' and ' — ' give double hyphens."""
        lines = toc.build_toc_lines(_tracker([]))
        self.assertEqual([re.search(r"\(#(.+)\)$", ln).group(1) for ln in lines], EXPECTED_ANCHORS)

    def test_update_keeps_blank_line_before_separator(self) -> None:
        """--update writes every entry and leaves a blank line between the last entry and ---."""
        code, _, after = _run(_tracker(["- [old](#old)"]), "--update")
        self.assertEqual(code, 0)
        block = after.split("## Contents\n", 1)[1].split("\n---\n", 1)[0]
        self.assertEqual(block.count("- ["), len(HEADINGS))
        self.assertTrue(block.endswith("\n"), "last TOC line must be followed by a blank line")
        self.assertIn("Body of " + HEADINGS[-1], after)

    def test_update_refuses_to_shrink(self) -> None:
        """A Contents with more entries than the new one is not rewritten without --allow-shrink."""
        old = [f"- [x{i}](#x{i})" for i in range(len(HEADINGS) + 2)]
        original = _tracker(old)
        code, out, after = _run(original, "--update")
        self.assertNotEqual(code, 0)
        self.assertEqual(after, original)
        self.assertIn("fewer", out)
        code, _, after = _run(original, "--update", "--allow-shrink")
        self.assertEqual(code, 0)
        self.assertNotEqual(after, original)

    def test_every_anchor_resolves(self) -> None:
        """Each generated #anchor matches a heading anchor in the file."""
        text = _tracker([])
        anchors = {toc.gfm_anchor(h) for h in HEADINGS}
        for line in toc.build_toc_lines(text):
            self.assertIn(re.search(r"\(#(.+)\)$", line).group(1), anchors)


if __name__ == "__main__":
    unittest.main()
