#!/usr/bin/env python3
"""Flow colours spread by measured distance: flows that share a box, or sit next to each other in the legend, get colours far apart.

Why (operator, 2026-11-06): smc-resiliency's End-to-end page drew flows 17 and 18 in two olive shades (CIEDE2000 17.9 apart) because colour n
went to flow n in palette order. Each pair is now weighed by how much the two flows touch (boxes they both act in, plus 1 for neighbours in
the numbering, which sit side by side in the legend), and colours are swapped between flows (or with an unused palette colour) while that
lowers the shortfall below SPREAD_TARGET. Deterministic: the start is palette order and moves are tried in a fixed order.

Imported, not run: `from flowmap.colours import spread_colours` with the skill's scripts/ on sys.path. Stdlib only. Runtime: a 31-flow map
settles in well under a second (measured in tests/test_flow_colours.py).
"""

from __future__ import annotations

from .colour_math import de2000

#: Pairs closer than this (CIEDE2000) cost; above it two touching flows read as different at a glance.
SPREAD_TARGET = 40.0
#: Most improvement passes; each pass tries every move once and stops early when none helps.
MAX_PASSES = 50


def touches(flows: list) -> dict:
    """How much each pair of flows touches: boxes both act in, plus 1 when they are numbered next to each other.

    Args:
        flows: the map's flows, in drawing order (each with `id` and `steps`, each step with `actor`).

    Returns:
        {(i, j): weight} for i < j indexes into flows, only pairs with a weight above 0.
    """
    acts = [{s["actor"] for s in f.get("steps", ())} | ({f["runs_on"]} if f.get("runs_on") else set()) for f in flows]
    pairs = {}
    for i in range(len(flows)):
        for j in range(i + 1, len(flows)):
            w = len(acts[i] & acts[j]) + (1 if j == i + 1 else 0)
            if w:
                pairs[(i, j)] = w
    return pairs


def _cost(cols: list, pairs: dict, dist) -> float:
    """The total shortfall: each touching pair's weight times the square of how far its colours fall below SPREAD_TARGET.

    Args:
        cols: a colour per flow index.
        pairs: {(i, j): weight} from touches().
        dist: a cached distance function of two colours.

    Returns:
        The cost; 0 when every touching pair is at least SPREAD_TARGET apart.
    """
    return sum(w * max(0.0, SPREAD_TARGET - dist(cols[i], cols[j])) ** 2 for (i, j), w in pairs.items())


def spread_colours(flows: list, palette: tuple) -> dict:
    """A colour per flow, starting from palette order and improved by swaps until no swap lowers the cost.

    Args:
        flows: the flows to colour, in drawing order.
        palette: the colours to use (flowmap.profile.DISTINCT); with more flows than colours, colours repeat and the cost keeps repeats apart.

    Returns:
        {flow id: colour}.
    """
    cols = [palette[i % len(palette)] for i in range(len(flows))]
    pairs = touches(flows)
    cache: dict = {}

    def dist(a: str, b: str) -> float:
        """CIEDE2000 between two colours, cached.

        Args:
            a: one colour, #rrggbb.
            b: the other.

        Returns:
            The distance.
        """
        key = (a, b) if a <= b else (b, a)
        if key not in cache:
            cache[key] = de2000(a, b)
        return cache[key]

    best = _cost(cols, pairs, dist)
    for _ in range(MAX_PASSES):
        if best == 0:
            break
        improved = False
        for i in range(len(cols)):
            spare = [c for c in palette if c not in cols]
            for move in [("swap", j) for j in range(len(cols)) if j != i] + [("take", c) for c in spare]:
                trial = list(cols)
                if move[0] == "swap":
                    trial[i], trial[move[1]] = trial[move[1]], trial[i]
                else:
                    trial[i] = move[1]
                cost = _cost(trial, pairs, dist)
                if cost < best - 1e-9:
                    cols, best, improved = trial, cost, True
        if not improved:
            break
    return {f["id"]: c for f, c in zip(flows, cols)}
