"""Offline tests for scripts/audit_rotations.py: an entry whose first line moved while its wrapped tail stayed live is reported as split."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_rotations.py"
_spec = importlib.util.spec_from_file_location("audit_rotations", SCRIPT)
ar = importlib.util.module_from_spec(_spec)
sys.modules["audit_rotations"] = ar
_spec.loader.exec_module(ar)

BEFORE = "\n".join(["## Next actions", "", "1. **2026-09-15** ask the carrier about the plan", "around Feb/Mar 2026 the usage dropped", "",
                    "- **2026-09-16** whole entry moved", "with its tail", ""])


class SplitTest(unittest.TestCase):
    """split_tails() on hand-built before/live/moved sets."""

    def test_split_entry_is_reported(self):
        live = {"## Next actions", "", "around Feb/Mar 2026 the usage dropped"}
        moved = {"1. **2026-09-15** ask the carrier about the plan", "- **2026-09-16** whole entry moved", "with its tail"}
        self.assertEqual(ar.split_tails(BEFORE, live, moved), ["around Feb/Mar 2026 the usage dropped"])

    def test_whole_moves_are_not_reported(self):
        moved = {"1. **2026-09-15** ask the carrier about the plan", "around Feb/Mar 2026 the usage dropped",
                 "- **2026-09-16** whole entry moved", "with its tail"}
        self.assertEqual(ar.split_tails(BEFORE, {"## Next actions", ""}, moved), [])


if __name__ == "__main__":
    unittest.main()
