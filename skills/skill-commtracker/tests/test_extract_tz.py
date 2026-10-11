"""Offline tests for scripts/extract.py --tz: a UTC Date header converts to the named zone; without --tz the header's own offset is kept."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract.py"
_spec = importlib.util.spec_from_file_location("commtracker_extract", SCRIPT)
ex = importlib.util.module_from_spec(_spec)
sys.modules["commtracker_extract"] = ex
_spec.loader.exec_module(ex)

EML = (
    "From: A Sender <a@example.com>\nTo: B Person <b@example.com>\nSubject: Test\n"
    "Date: Sun, 11 Oct 2026 23:01:00 +0000\nContent-Type: text/plain; charset=utf-8\n\nHello.\n"
)


class TzTest(unittest.TestCase):
    """extract() with and without tz."""

    def _run(self, tz: str | None) -> dict:
        """Extract the sample message.

        Args:
            tz: IANA zone name, or None for the header's own offset.

        Returns:
            The extraction result.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.eml"
            path.write_text(EML)
            return ex.extract(str(path), attachments_dir=tmp, tz=tz)

    def test_default_keeps_header_offset(self):
        """No tz: the slug is the UTC time the header carries."""
        self.assertEqual(self._run(None)["slug"], "20261011_2301")

    def test_tz_converts(self):
        """tz=Australia/Sydney (AEDT, UTC+11 in October): the slug moves to the next local day."""
        r = self._run("Australia/Sydney")
        self.assertEqual(r["slug"], "20261012_1001")
        self.assertIn("AEDT", r["date_human"])


if __name__ == "__main__":
    unittest.main()
