"""Offline tests for scripts/flowmap/colours.py ("colours") and scripts/flowmap/colour_math.py ("colour_math"): flows that touch get colours
far apart, the result is never worse than palette order, it is deterministic and fast, and the moved colour maths still measures as before.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
colours = importlib.import_module("flowmap.colours")
colour_math = importlib.import_module("flowmap.colour_math")
palette_check = importlib.import_module("palette_check")

#: Mustard and bronze (17.9 apart, the pair smc-resiliency complained of), then a blue far from both.
OLIVES = ("#857700", "#574b19", "#1f4e9c")


def _flow(fid: str, *actors: str) -> dict:
    """A minimal flow acting in the given boxes.

    Args:
        fid: the flow id.
        actors: the boxes its steps act in.

    Returns:
        The flow dict.
    """
    return {"id": fid, "steps": [{"id": f"s{i}", "actor": a} for i, a in enumerate(actors)]}


class FlowColours(unittest.TestCase):
    """flowmap.colours.spread_colours and touches; flowmap.colour_math."""

    def test_touch_counts_shared_boxes_and_neighbours(self) -> None:
        """Two shared boxes plus being numbered side by side weigh 3; flows far apart in number and sharing nothing do not touch."""
        flows = [_flow("a", "x", "y"), _flow("b", "x", "y", "z"), _flow("c", "q")]
        self.assertEqual(colours.touches(flows), {(0, 1): 3, (1, 2): 1})

    def test_touching_flows_leave_the_close_pair(self) -> None:
        """Palette order gives the two touching flows mustard and bronze; the spread gives one of them the far blue."""
        flows = [_flow("a", "x"), _flow("b", "x")]
        got = colours.spread_colours(flows, OLIVES)
        self.assertGreater(colour_math.de2000(got["a"], got["b"]), colour_math.de2000(OLIVES[0], OLIVES[1]))
        self.assertIn("#1f4e9c", got.values())

    def test_never_worse_than_palette_order_and_deterministic(self) -> None:
        """On 32 flows sharing boxes in a ring (more flows than colours) the cost does not rise, two runs agree, and it settles within 2 s."""
        palette = importlib.import_module("flowmap.profile").DISTINCT
        flows = [_flow(f"f{i}", f"b{i % 9}", f"b{(i + 1) % 9}") for i in range(32)]
        pairs = colours.touches(flows)
        start = time.perf_counter()
        got = colours.spread_colours(flows, palette)
        self.assertLess(time.perf_counter() - start, 2.0)
        cost = colours._cost([got[f["id"]] for f in flows], pairs, colour_math.de2000)
        before = colours._cost([palette[i % len(palette)] for i in range(32)], pairs, colour_math.de2000)
        self.assertLessEqual(cost, before)
        self.assertEqual(got, colours.spread_colours(flows, palette))

    def test_untouched_flows_keep_palette_order(self) -> None:
        """Flows that share nothing and are not neighbours cost nothing, so they keep palette order."""
        flows = [_flow("a", "x")]
        self.assertEqual(colours.spread_colours(flows, OLIVES), {"a": OLIVES[0]})

    def test_a_pinned_colour_is_kept_and_not_reused(self) -> None:
        """A flow with `colour` keeps it even when it is close to a neighbour's, and no other flow is given that colour."""
        flows = [dict(_flow("a", "x"), colour="#857700"), _flow("b", "x"), _flow("c", "x")]
        got = colours.spread_colours(flows, OLIVES)
        self.assertEqual(got["a"], "#857700")
        self.assertNotIn("#857700", (got["b"], got["c"]))

    def test_moved_maths_still_measures(self) -> None:
        """The green and olive bar is still 13.1 apart, and palette_check uses the same function."""
        self.assertAlmostEqual(colour_math.de2000("#1b7a3a", "#4d6b00"), 13.1, delta=0.1)
        self.assertIs(palette_check.de2000, colour_math.de2000)


if __name__ == "__main__":
    unittest.main()
