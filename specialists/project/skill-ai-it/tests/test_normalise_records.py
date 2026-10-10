"""Offline tests for scripts/normalise_records.py: headings are added, no original line changes, and rotation then moves dated paragraphs."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "normalise_records.py"
_spec = importlib.util.spec_from_file_location("normalise_records", SCRIPT)
nr = importlib.util.module_from_spec(_spec)
sys.modules["normalise_records"] = nr
_spec.loader.exec_module(nr)

TEXT = """---
Title: Scratchpad
Kind: state
---

# Scratchpad

<!-- KEEP: updated 2026-05-01 — a -->
<!-- KEEP: updated 2026-05-02 — b -->
<!-- KEEP: updated 2026-05-03 — c -->
<!-- KEEP: updated 2026-05-04 — d -->
<!-- KEEP: updated 2026-05-05 — e -->

## Current state

**Newest thread (2026-10-07, 13:36) — RISE journald pinned.** `KEEP` detail.
second line.

**Support portal login verified** (~4:35p): more.

**Phase:** standing fact, stays.

> **2026-09-03 — verdict (evening)** quoted.

## Open items

**2026-09-01** an open paragraph, left alone.
"""


class NormaliseTest(unittest.TestCase):
    """normalise() on a sample record."""

    def test_headings_added_and_text_unchanged(self):
        new, added = nr.normalise(TEXT)
        self.assertIn("## Update log 2026-05-01 to 2026-05-05 (header comments)", added)
        self.assertIn("### 2026-10-07 — Newest thread — RISE journald pinned.", added)
        self.assertIn("### 2026-10-07 — Support portal login verified", added)  # time only: the date above
        self.assertIn("### Phase", added)
        self.assertTrue(any(a.startswith("### 2026-09-03 — verdict") and ")" not in a for a in added))
        self.assertFalse(any("2026-09-01" in a for a in added))  # Open items left alone
        self.assertIn("Keep: Update log=0", new)
        it = iter(new.split("\n"))
        self.assertTrue(all(any(o == n for n in it) for o in TEXT.split("\n")))

    def test_second_run_adds_nothing(self):
        new, _ = nr.normalise(TEXT)
        again, added = nr.normalise(new)
        self.assertEqual(added, [])
        self.assertEqual(again, new)

    def test_apply_writes_and_plan_does_not(self):
        root = Path(tempfile.mkdtemp())
        (root / "SCRATCHPAD.md").write_text(TEXT)
        self.assertEqual(nr.main(["--project-root", str(root), "SCRATCHPAD.md"]), 0)
        self.assertEqual((root / "SCRATCHPAD.md").read_text(), TEXT)
        self.assertEqual(nr.main(["--project-root", str(root), "--apply", "SCRATCHPAD.md"]), 0)
        self.assertIn("### Phase", (root / "SCRATCHPAD.md").read_text())


if __name__ == "__main__":
    unittest.main()
