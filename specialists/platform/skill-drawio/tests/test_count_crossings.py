"""Offline tests for scripts/count_crossings.py ("count_crossings"): strict crossings only, and the command line reads a page through drawio.read.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
count_crossings = importlib.import_module("count_crossings")
EXAMPLE = ROOT / "examples" / "shop"


class CountCrossings(unittest.TestCase):
    """scripts/count_crossings.py: strict crossings only, and the command line reads a page through drawio.read."""

    def test_counts_strict_crossings_only(self) -> None:
        """One arrow across another counts once; an arrow that only touches the other's end counts nothing."""
        runs = {"h": [((0, 50), (100, 50))], "v": [((50, 0), (50, 100))], "t": [((100, 0), (100, 50))]}
        self.assertEqual(count_crossings.crossings(runs), 1)
        self.assertEqual(count_crossings.crossings({"h": runs["h"], "t": runs["t"]}), 0)

    def test_cli_counts_a_page_and_reports_a_missing_one(self) -> None:
        """The example drawing's End-to-end page is counted (exit 0); a page past the last exits 1."""
        drawing = str(EXAMPLE / "drawio" / "flows.drawio")
        self.assertEqual(count_crossings.main([drawing, "--page", "2"]), 0)
        self.assertEqual(count_crossings.main([drawing, "--page", "99"]), 1)


if __name__ == "__main__":
    unittest.main()


class CompareDrawings(unittest.TestCase):
    """Compare mode: every page before and after, shared runs counted, exit 3 only when a page got worse."""

    def test_shared_runs_are_counted(self) -> None:
        """Two arrows lying along each other count once; parallel runs further apart, or only touching, do not."""
        runs = {"a": [((0, 50), (100, 50))], "b": [((40, 54), (160, 54))], "c": [((0, 80), (100, 80))], "d": [((100, 50), (140, 50))]}
        self.assertEqual(count_crossings.alongside(runs), 2)   # a-b overlap; b-d overlap (d ends inside b); a-d only touch

    def test_same_drawing_compares_clean(self) -> None:
        """A drawing compared with itself changes no page and exits 0."""
        example = ROOT / "examples" / "shop" / "drawio" / "flows.drawio"
        changed, (before, after) = count_crossings.compare(example.read_text(encoding="utf-8"), example.read_text(encoding="utf-8"))
        self.assertEqual(changed, [])
        self.assertEqual(before, after)
        self.assertEqual(count_crossings.main([str(example), "--compare", str(example)]), 0)
