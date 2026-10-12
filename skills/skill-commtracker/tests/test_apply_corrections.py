"""Offline tests for scripts/apply_corrections.py: corrections apply only below the marker, in order, and unmatched pairs fail."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apply_corrections.py"
_spec = importlib.util.spec_from_file_location("commtracker_apply_corrections", SCRIPT)
ac = importlib.util.module_from_spec(_spec)
sys.modules["commtracker_apply_corrections"] = ac
_spec.loader.exec_module(ac)

TRANSCRIPT = "# Meeting\n\nSummary mentions gooey.\n\n## Full transcript\n\n**A:** a gooey for the fast food form. Mm. I talked with Rob.\n"


class ApplyCorrectionsTest(unittest.TestCase):
    """main() against a small transcript."""

    def _run(self, tsv: str, *flags: str) -> tuple[int, str]:
        """Write the fixtures, run main(), return its code and the resulting file.

        Args:
            tsv: corrections file content.
            flags: extra command-line flags.

        Returns:
            (exit code, transcript text after the run).
        """
        with tempfile.TemporaryDirectory() as tmp:
            transcript, corrections = Path(tmp, "t.md"), Path(tmp, "c.tsv")
            transcript.write_text(TRANSCRIPT)
            corrections.write_text(tsv)
            code = ac.main([str(transcript), str(corrections), *flags])
            return code, transcript.read_text()

    def test_only_dialogue_changes(self) -> None:
        """The summary above the marker keeps its wording."""
        code, out = self._run("gooey\tGUI\n")
        self.assertEqual(code, 0)
        self.assertIn("Summary mentions gooey.", out)
        self.assertIn("a GUI for", out)

    def test_order_and_speaker_split(self) -> None:
        """Specific pairs run before generic ones and \\n splits a turn."""
        code, out = self._run("fast food form\tFastField form\nMm. I talked with Rob.\tMm.\\n\\n**B:** I talked with Rob.\n")
        self.assertEqual(code, 0)
        self.assertIn("FastField form. Mm.\n\n**B:** I talked with Rob.", out)

    def test_unmatched_fails_unless_optional(self) -> None:
        """A required pair with no match returns 1; a ?-prefixed one does not."""
        self.assertEqual(self._run("absent\tx\n")[0], 1)
        self.assertEqual(self._run("?absent\tx\n")[0], 0)

    def test_table_and_dry_run(self) -> None:
        """--table adds the corrections section; --dry-run leaves the file as it was."""
        _, out = self._run("gooey\tGUI\n", "--table")
        self.assertIn("| gooey | GUI | 1 |", out)
        self.assertEqual(self._run("gooey\tGUI\n", "--dry-run")[1], TRANSCRIPT)


if __name__ == "__main__":
    unittest.main()
