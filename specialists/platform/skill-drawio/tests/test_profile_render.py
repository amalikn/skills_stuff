"""Offline test for scripts/profile_render.py: one profiled render of the example map prints its timing line and a table of functions.

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
profile_render = importlib.import_module("profile_render")


class ProfileExample(unittest.TestCase):
    """The example shop map profiles in a second and names the engine's own modules."""

    def test_prints_timing_and_engine_rows(self):
        """Exit 0, a timing line for the map, and rows that point into the engine's packages."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = profile_render.main(["--root", str(ROOT / "examples" / "shop"), "--map", "flows.yaml", "--top", "8", "--workers", "1"])
        text = out.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("flows.yaml: load", text)
        self.assertIn("render", text)
        self.assertTrue(any("flowmap/" in line for line in text.splitlines()[2:]), text)

    def test_bad_map_is_exit_2(self):
        """A map that cannot be read exits 2."""
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(profile_render.main(["--root", str(ROOT), "--map", "no-such-map.yaml"]), 2)


if __name__ == "__main__":
    unittest.main()
