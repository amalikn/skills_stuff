"""Offline tests for band_search's worker pool (2026-11-06) and flowmap.render_cache: the pooled walk keeps exactly the swaps the one-at-a-time
walk keeps, and a drift check served from the cache still sees a changed or missing drawing.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
cs, rc = (importlib.import_module(f"flowmap.{n}") for n in ("band_pool", "render_cache"))


class FakePage:
    """A page whose crossing count is a fixed function of its band swaps."""

    def __init__(self, swaps: tuple):
        """Score the swaps.

        Args:
            swaps: the band swaps applied.
        """
        self.swaps, self.band, self.segs = swaps, 1, {}
        self.cell = {c: (0, 1) for c in "abcde"}
        self.score = 40 - 7 * len(swaps) + sum(ord(a) * 3 + ord(b) for a, b in swaps) % 11

    def _crossings(self, _segs: set) -> int:
        """The fixed score.

        Args:
            _segs: unused.

        Returns:
            The score, never below zero.
        """
        return max(0, self.score)


class PoolMatchesSequential(unittest.TestCase):
    """The pooled walk and the one-at-a-time walk keep the same swaps, at several pool widths."""

    def test_same_swaps_for_every_width(self):
        """Width 1 is the plain loop; wider pools must end on the identical swaps."""
        runs = {}
        for width in ("1", "2", "3", "8"):
            with mock.patch.dict(os.environ, {"SKILL_DRAWIO_WORKERS": width}):
                runs[width] = cs.band_search(FakePage(()), FakePage, {}).swaps
        self.assertTrue(runs["1"])
        self.assertEqual(len(set(runs.values())), 1, runs)


class RenderCache(unittest.TestCase):
    """Keys follow every input; a recorded key answers by hash; the cache can be turned off."""

    def test_key_changes_with_map_order_and_profile(self):
        """Key order of the map and the profile both change the key."""
        base = rc.key({"a": 1, "b": 2}, "p")
        self.assertNotEqual(base, rc.key({"b": 2, "a": 1}, "p"))
        self.assertNotEqual(base, rc.key({"a": 1, "b": 2}, "q"))
        self.assertEqual(base, rc.key({"a": 1, "b": 2}, "p"))

    def test_record_lookup_and_off(self):
        """A recorded drawing hash comes back; with the cache off nothing is kept."""
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"SKILL_DRAWIO_CACHE": d}):
            rc.record("k1", "<mxfile/>")
            self.assertEqual(rc.lookup("k1"), rc.text_hash("<mxfile/>"))
            self.assertIsNone(rc.lookup("k2"))
        with mock.patch.dict(os.environ, {"SKILL_DRAWIO_CACHE": "off"}):
            rc.record("k1", "x")
            self.assertIsNone(rc.lookup("k1"))


if __name__ == "__main__":
    unittest.main()
