"""Offline tests for maps split into parts (`#@include`, added 2026-10-21): parts land indented where the include line sits, a part included
twice is refused, and a part file nobody includes is reported.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

model = importlib.import_module("flowmap.model")


class MapPartsTests(unittest.TestCase):
    """The include contract."""

    def setUp(self) -> None:
        """A temporary project with a master map and a parts folder."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "parts").mkdir()
        (self.root / "parts" / "a.yaml").write_text("- id: a\n  name: A\n", encoding="utf-8")
        (self.root / "map.yaml").write_text("title: T\nitems:\n  #@include parts/a.yaml\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Remove the temporary project."""
        self.tmp.cleanup()

    def test_part_lands_indented(self) -> None:
        """The part's lines are indented to the include line, so it loads as the list under `items`."""
        self.assertEqual(model.read_map(self.root, "map.yaml"), {"title": "T", "items": [{"id": "a", "name": "A"}]})

    def test_part_included_twice_is_refused(self) -> None:
        """Naming one part twice raises (negative test)."""
        (self.root / "map.yaml").write_text("items:\n  #@include parts/a.yaml\n  #@include parts/a.yaml\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            model.read_map(self.root, "map.yaml")

    def test_stray_part_is_reported(self) -> None:
        """A part file nobody includes is named; with every part included the list is empty."""
        self.assertEqual(model.stray_parts(self.root, "map.yaml"), [])
        (self.root / "parts" / "b.yaml").write_text("- id: b\n", encoding="utf-8")
        self.assertEqual(model.stray_parts(self.root, "map.yaml"), ["part parts/b.yaml is not included by any #@include"])


if __name__ == "__main__":
    unittest.main()
