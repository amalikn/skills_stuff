"""Offline tests for scripts/roadmap_trim.py: done items move with their continuation lines, open, pinned, recent and undated ones stay, and a
project without a ROADMAP is left alone."""

from __future__ import annotations

import datetime
import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "roadmap_trim.py"
_spec = importlib.util.spec_from_file_location("roadmap_trim", SCRIPT)
rt = importlib.util.module_from_spec(_spec)
sys.modules["roadmap_trim"] = rt
_spec.loader.exec_module(rt)

ROADMAP = """---
Title: Roadmap
Kind: roadmap
Budget: 200 lines, 25 KB
---

# Roadmap

## Current phase

**2026-10-14.** Building.

## Monitoring

- [ ] Open item 2026-01-01
- [x] Old done item (2026-01-02)
  with a continuation line
- [x] Pinned done item `PIN` (2026-01-03)
- [x] Undated done item

## Completed

- Finished thing (2026-01-04)
"""


class Split(unittest.TestCase):
    def test_old_done_items_move_with_continuations(self):
        kept, moved = rt.split(ROADMAP, datetime.date(2026, 6, 1))
        moved_text = [" ".join(item) for _, item in moved]
        self.assertTrue(any("Old done item" in t and "continuation" in t for t in moved_text))
        self.assertTrue(any("Finished thing" in t for t in moved_text))
        self.assertEqual([head for head, _ in moved], ["Monitoring", "Completed"])

    def test_open_pinned_and_undated_stay(self):
        kept, _ = rt.split(ROADMAP, datetime.date(2026, 6, 1))
        text = "\n".join(kept)
        for stays in ("Open item", "Pinned done item", "Undated done item", "## Current phase"):
            self.assertIn(stays, text)

    def test_recent_done_item_stays_and_keep_days_zero_moves_all(self):
        # Kept since 2026-01-03: the Old item (2026-01-02) moves; the Completed item (2026-01-04) and the undated one stay.
        self.assertEqual(len(rt.split(ROADMAP, datetime.date(2026, 1, 3))[1]), 1)
        # Nothing kept by age: Old, Undated and Completed move; only the pinned item stays.
        self.assertEqual(len(rt.split(ROADMAP, None)[1]), 3)


class Main(unittest.TestCase):
    def test_apply_writes_archive_and_index(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "ROADMAP.md").write_text(ROADMAP, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                rt.main(["--project-root", str(root), "--apply", "--keep-days", "0"])
            archives = list((root / "docs/history").glob("roadmap-*.md"))
            self.assertEqual(len(archives), 1)
            self.assertIn(archives[0].name, (root / "docs/history/readme.md").read_text(encoding="utf-8"))
            self.assertNotIn("Old done item", (root / "ROADMAP.md").read_text(encoding="utf-8"))

    def test_no_roadmap_is_left_alone(self):
        with tempfile.TemporaryDirectory() as d, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(rt.main(["--project-root", d, "--apply"]), 0)
        self.assertIn("none in this project", out.getvalue())
        self.assertFalse((Path(d) / "docs").exists())


if __name__ == "__main__":
    unittest.main()
