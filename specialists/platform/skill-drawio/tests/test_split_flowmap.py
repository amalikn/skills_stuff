"""Offline tests for scripts/split_flowmap.py ("split_flowmap", 2026-10-21): a map splits into group and section parts whose expansion loads
to the same data, a group in two runs stays whole, and an already split map is refused.

Run: `just test` (unittest, the pack's venv; PyYAML present). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

split_flowmap = importlib.import_module("split_flowmap")
assemble_flowmap = importlib.import_module("assemble_flowmap")
MAP = """title: T
components:
  # all the parts
  - id: a
    group: G1
  - id: b
    group: G2
flows:
  # ==== first section
  - id: f
    title: F
  # ==== second section
  - id: g
    title: G
"""


class SplitTests(unittest.TestCase):
    """The split contract."""

    def setUp(self) -> None:
        """A temporary map."""
        self.tmp = tempfile.TemporaryDirectory()
        self.map = Path(self.tmp.name) / "flows.yaml"
        self.map.write_text(MAP, encoding="utf-8")

    def tearDown(self) -> None:
        """Remove it."""
        self.tmp.cleanup()

    def test_split_is_proved_and_written(self) -> None:
        """Two component groups and two flow sections become four parts; the master includes them; the data is unchanged."""
        master, parts = split_flowmap.plan(MAP)
        self.assertEqual(list(parts), ["components-g1", "components-g2", "flows-first-section", "flows-second-section"])
        self.assertTrue(split_flowmap.proved(self.map, master, parts))
        self.assertEqual(split_flowmap.main(["--map", str(self.map), "--apply"]), 0)
        self.assertIn("#@include components-g1.yaml", (self.map.parent / "parts" / "master.yaml").read_text(encoding="utf-8"))
        text = self.map.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# GENERATED from") and "#@include" not in text)   # complete, no pointers
        self.assertEqual(assemble_flowmap.main(["--master", str(self.map.parent / "parts" / "master.yaml"), "--out", str(self.map)]), 0)
        self.assertEqual(split_flowmap.main(["--map", str(self.map)]), 1)   # negative: a split map is refused

    def test_assemble_refuses_a_stray_part_and_reports_drift(self) -> None:
        """A part nobody includes is refused, and a hand edit of the generated file is drift (negative tests)."""
        split_flowmap.main(["--map", str(self.map), "--apply"])
        master = str(self.map.parent / "parts" / "master.yaml")
        (self.map.parent / "parts" / "extra.yaml").write_text("- id: x\n", encoding="utf-8")
        self.assertEqual(assemble_flowmap.main(["--master", master, "--out", str(self.map)]), 1)
        (self.map.parent / "parts" / "extra.yaml").unlink()
        self.map.write_text(self.map.read_text(encoding="utf-8") + "# hand edit\n", encoding="utf-8")
        self.assertEqual(assemble_flowmap.main(["--master", master, "--out", str(self.map)]), 1)
        self.assertEqual(assemble_flowmap.main(["--master", master, "--out", str(self.map), "--write"]), 0)

    def test_group_in_two_runs_stays_whole(self) -> None:
        """A group that appears twice would be reordered by a split, so components stay one part."""
        text = MAP.replace("    group: G2", "    group: G1\n  - id: c\n    group: G2\n  - id: d\n    group: G1")
        _master, parts = split_flowmap.plan(text)
        self.assertIn("components", parts)



FAMILY_MAP = """title: T
drawing:
  families:
    - {id: a, name: Alpha, flows: [f, g]}
    - {id: b, name: Beta, flows: [h]}
components:
  - id: c
    group: G
flows:
  - id: f
    title: F
  - id: g
    title: G
  - id: h
    title: H
"""


class FamilySplitTests(unittest.TestCase):
    """Flows split by drawing.families when a map has no section comments (operator, 2026-10-27: parts are the standard)."""

    def setUp(self) -> None:
        """A temporary map with two families."""
        self.tmp = tempfile.TemporaryDirectory()
        self.map = Path(self.tmp.name) / "flows.yaml"
        self.map.write_text(FAMILY_MAP, encoding="utf-8")

    def tearDown(self) -> None:
        """Remove it."""
        self.tmp.cleanup()

    def test_families_become_parts_and_load_the_same(self) -> None:
        """Two families become two flow parts, in map order, and the expansion loads to the same data."""
        master, parts = split_flowmap.plan(FAMILY_MAP)
        self.assertEqual([p for p in parts if p.startswith("flows")], ["flows-alpha", "flows-beta"])
        self.assertTrue(split_flowmap.proved(self.map, master, parts))

    def test_interleaved_family_stays_whole(self) -> None:
        """A family whose flows are not contiguous keeps every flow in one part (negative: no reorder)."""
        text = FAMILY_MAP.replace("flows: [f, g]", "flows: [f, h]").replace("flows: [h]", "flows: [g]")
        _, parts = split_flowmap.plan(text)
        self.assertIn("flows", parts)
        self.assertNotIn("flows-alpha", parts)

    def test_section_comments_win(self) -> None:
        """A map with section comments is cut at them, not by family."""
        text = FAMILY_MAP.replace("flows:\n  - id: f", "flows:\n  # ==== first\n  - id: f")
        _, parts = split_flowmap.plan(text)
        self.assertEqual([p for p in parts if p.startswith("flows")], ["flows-first"])


if __name__ == "__main__":
    unittest.main()
