"""Offline tests for scripts/palette_check.py ("palette_check"): contrast and CIEDE2000 measured, a light colour refused, suggestions farther than the bar.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
palette_check = importlib.import_module("palette_check")


class PaletteCheck(unittest.TestCase):
    """scripts/palette_check.py: measured contrast and distance, a failing colour exits 1, suggestions keep the bar."""

    def test_distance_is_zero_for_one_colour_and_symmetric(self) -> None:
        """CIEDE2000 of a colour with itself is 0; swapping the pair gives the same value."""
        self.assertAlmostEqual(palette_check.de2000("#1f4e9c", "#1f4e9c"), 0.0, places=6)
        self.assertAlmostEqual(palette_check.de2000("#1b7a3a", "#4d6b00"), palette_check.de2000("#4d6b00", "#1b7a3a"), places=6)

    def test_first_ten_closest_pair_is_green_and_olive(self) -> None:
        """The bar the second ten were picked against: green and olive at 13.1."""
        self.assertAlmostEqual(palette_check.de2000("#1b7a3a", "#4d6b00"), 13.1, delta=0.1)

    def test_light_colour_exits_1(self) -> None:
        """A light grey is below 4.5:1 on white, so the check fails; the shipped palette passes."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(palette_check.main(["--palette", "#1f4e9c,#9ca3af"]), 1)
            self.assertEqual(palette_check.main([]), 0)

    def test_suggestion_clears_the_bar(self) -> None:
        """Against the first ten, the first farthest-first pick sits above their closest pair and is readable on white."""
        (colour, dist, _), = palette_check.suggest(list(palette_check.DISTINCT[:10]), [palette_check.THIN_GREY], 1)
        self.assertGreater(dist, 13.1)
        self.assertGreaterEqual(palette_check.contrast(colour), 4.5)


if __name__ == "__main__":
    unittest.main()
