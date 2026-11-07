"""Offline tests for two step-shape fits from the operator review of 2026-11-07: a decision diamond is sized to its full text's inscribed
rectangle (half its width, half its height) with its label inset to that rectangle, and a store step keeps its text off the cylinder's rims.
Each rule has its look key ("decision_fit": "widen", "store_insets": "off") and the old drawing comes back with it.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

mxfile, read = (importlib.import_module(f"drawio.{n}") for n in ("mxfile", "read"))
pages, profile, shapes = (importlib.import_module(f"flowmap.{n}") for n in ("pages", "profile", "shapes"))
TestMap = importlib.import_module("test_layout_rules")
#: The X2 trial question (344 characters) that drew a 560 x 436 diamond before the fix.
LONG = ("The box boots B once; health running: mark-good moves B first in BootOrder (criterion 1); broken image or panic: the next boot is A "
        "(criterion 2); hang: no answer; only the lab script's hard reset landed on A, the box did not recover itself (criterion 3 PARTLY); "
        "power cut mid-trial: A, BootNext gone (criterion 4).")


def _decision_map(action: str, look: dict | None = None) -> dict:
    """The minimal map with its first step a decision holding `action`.

    Args:
        action: the decision's text.
        look: drawing.look settings, if any.

    Returns:
        The map.
    """
    data = TestMap._minimal()
    data["flows"][0]["steps"][0].update(action=action, shape="decision")
    data["flows"][0]["steps"][1]["shape"] = "stored-data"
    if look:
        data["drawing"] = {"look": look}
    return data


def _sizes(data: dict) -> tuple[dict, dict, dict]:
    """size_steps for the map's one flow, with the shapes its steps name.

    Args:
        data: the map.

    Returns:
        (texts, widths, heights) by step id.
    """
    steps = data["flows"][0]["steps"]
    return pages.size_steps(steps, {s["id"]: s["shape"] for s in steps}, TestMap._profile(data))


class DiamondFit(unittest.TestCase):
    """A diamond holds its full text in its inscribed rectangle and is no bigger than that needs."""

    def test_text_fits_the_inscribed_rectangle_and_aspect_is_capped(self) -> None:
        """Wrapped at half the width, the text block is no taller than half the height; height at most decision_aspect times width below the cap."""
        data = _decision_map(LONG)
        look = TestMap._profile(data).look
        texts, w, h = _sizes(data)
        chars = int((w["one"] / 2 - 4) / ((look["step_width"] - 14) / look["step_chars"] * shapes.DIAMOND_CHAR_FILL))
        block = sum(mxfile.wrapped_lines(x.replace("*", ""), chars) for x in texts["one"]) * pages.STEP_LINE_H
        self.assertLessEqual(block, h["one"] / 2)
        self.assertTrue(h["one"] <= look["decision_aspect"] * w["one"] or w["one"] >= look["decision_max_width"])
        self.assertIn("criterion 4", " ".join(texts["one"]))   # the full text, never cut (operator correction 2026-11-07)

    def test_smaller_than_the_widen_rule_short_text_and_long(self) -> None:
        """A long and a short question both draw smaller than under "widen", each within decision_aspect."""
        for action in (LONG, "Overlay SMC?"):
            _t, w, h = _sizes(_decision_map(action))
            _t, w_old, h_old = _sizes(_decision_map(action, {"decision_fit": "widen"}))
            self.assertLess(w["one"] * h["one"], w_old["one"] * h_old["one"], action[:20])
            self.assertLessEqual(h["one"], 0.6 * w["one"])

    def test_label_inset_is_a_quarter_width_each_side(self) -> None:
        """The drawn diamond's label is inset W/4 on each side (the inscribed rectangle); "widen" keeps the fixed 72 px."""
        for look, quarter in ((None, True), ({"decision_fit": "widen"}, False)):
            data = _decision_map(LONG, look)
            (_name, model), = [m for m in read.models(pages.render(data, TestMap._profile(data))) if m[0].startswith("1.")]
            cell = read.cells(model)["f-s-one"][0]
            width = float(cell.find("mxGeometry").get("width"))
            self.assertEqual(read.style(cell.get("style"))["spacingLeft"], f"{width / 4:g}" if quarter else "72")


class StoreFit(unittest.TestCase):
    """A store step's text stays on the cylinder's flat body."""

    def test_store_gets_insets_and_height(self) -> None:
        """A store step is taller by the rim allowance and carries the top and bottom insets; "off" restores the old cylinder."""
        _t, _w, h = _sizes(_decision_map("x"))
        _t, _w, h_off = _sizes(_decision_map("x", {"store_insets": "off"}))
        style, extra = shapes.STEP_FIT["stored-data"]
        self.assertEqual(h["two"] - h_off["two"], extra)
        self.assertGreaterEqual(extra, 30)   # two rims of size=10 plus the insets: the via line sat on the bottom curve at +0
        self.assertIn("spacingBottom=", style)
        text = pages.render(_decision_map("x"), TestMap._profile(_decision_map("x")))
        self.assertIn("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;" + style, text)
        self.assertEqual(shapes.step_fit("process", profile.DEFAULT_LOOK), ("", 0))


if __name__ == "__main__":
    unittest.main()
