"""Offline tests for scripts/layout_quality.py ("layout_quality"): bends, arrows through boxes, label ownership, overlaps and compare.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
layout_quality = importlib.import_module("layout_quality")
EXAMPLE = ROOT / "examples" / "shop" / "drawio" / "flows.drawio"


def _wire(cid: str, path: list, src: str = "", dst: str = "") -> dict:
    """A wire as drawio.read gives it.

    Args:
        cid: its id.
        path: its points.
        src: its source box id.
        dst: its target box id.

    Returns:
        The wire.
    """
    return {"id": cid, "source_id": src, "target_id": dst, "label": "", "path": path}


def _shape(cid: str, geo: list, label: str = "x") -> dict:
    """A shape as drawio.read gives it.

    Args:
        cid: its id.
        geo: [x, y, width, height].
        label: its text.

    Returns:
        The shape.
    """
    return {"id": cid, "label": label, "geo": geo}


class LayoutQuality(unittest.TestCase):
    """scripts/layout_quality.py measures."""

    def test_bends_ignore_repeats_and_straight_points(self) -> None:
        """An L has one bend; a repeated point and a point midway along a run add none."""
        self.assertEqual(layout_quality.bends([[0, 0], [0, 0], [50, 0], [100, 0], [100, 50]]), 1)
        self.assertEqual(layout_quality.bends([[0, 0], [100, 0]]), 0)

    def test_arrow_through_a_box_it_does_not_join(self) -> None:
        """An arrow across a third box counts; its own ends and a run along a box's edge do not."""
        page = {"shapes": [_shape("a", [0, 0, 20, 20]), _shape("b", [200, 0, 20, 20]), _shape("c", [90, 0, 20, 20]),
                           _shape("d", [90, 40, 20, 20])],
                "wires": [_wire("w", [[20, 10], [200, 10]], "a", "b"), _wire("v", [[90, 100], [90, 30]]), _wire("z", [[100, 0], [100, -40]], "c")]}
        q = layout_quality.page_quality(page)
        self.assertEqual(q["through"], 1)   # w through c (a box: z joins it); v runs along d's left edge
        self.assertEqual(q["where"], ["through w > c"])

    def test_own_label_is_not_a_clash_but_another_arrows_is(self) -> None:
        """A label centred on its arrow (named after it) is not counted; another arrow through that label is."""
        page = {"shapes": [_shape("w-l", [40, 0, 20, 20])],
                "wires": [_wire("w", [[0, 10], [100, 10]]), _wire("v", [[50, -50], [50, 50]])]}
        q = layout_quality.page_quality(page)
        self.assertEqual(q["where"], ["through v > w-l"])

    def test_unnamed_label_goes_to_the_nearest_arrow(self) -> None:
        """A label whose id names no arrow belongs to the arrow through its centre."""
        wires = [_wire("gg", [[0, 10], [100, 10]]), _wire("x", [[0, 40], [100, 40]])]
        self.assertEqual(layout_quality.label_owner(_shape("gl", [40, 0, 20, 20]), wires), "gg")
        self.assertIsNone(layout_quality.label_owner(_shape("far", [40, 100, 20, 20]), wires))

    def test_labelled_leaf_boxes_overlapping(self) -> None:
        """Two labelled boxes overlapping count; a box inside a lane does not (the lane is no leaf)."""
        page = {"shapes": [_shape("lane", [0, 0, 300, 100]), _shape("p", [10, 10, 50, 30]), _shape("q", [40, 20, 50, 30])], "wires": []}
        q = layout_quality.page_quality(page)
        self.assertEqual(q["overlap"], 1)

    def test_example_compares_clean_with_itself(self) -> None:
        """The example drawing compared with itself exits 0; its pages measure without error."""
        self.assertEqual(layout_quality.main([str(EXAMPLE), "--compare", str(EXAMPLE)]), 0)
        self.assertEqual(layout_quality.main([str(EXAMPLE), "--all"]), 0)


if __name__ == "__main__":
    unittest.main()
