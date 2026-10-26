"""Route costs that judge how an arrow meets its boxes on a flow page, used by flowmap.routing.cost. Stdlib only.

Operator review 2026-10-26 (smc_change PHP step page): arrows to the next step ran flat over the target's column to come in at its top or
bottom, and an arrow left a decision's top vertex to climb at its centre; both should turn in the gap between the columns.

Imported, not run: `from flowmap.route_costs import overshoot, leaves_off_side` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations


def leaves_off_side(out_side: str, ends: tuple, rects: dict, used: dict) -> bool:
    """Whether a path to a box wholly on the right leaves the source's top or bottom (a diamond's top vertex, climbing at its centre) when its
    right side could turn in the gap (operator review 2026-10-26: arrow 12 left decision 11 from its top). A decision whose branches hold its
    top and bottom (route_flow's `branchy`) is exempt: one branch takes the right, the others must leave up or down.

    Args:
        out_side: the exit side.
        ends: (source cell id, target cell id).
        rects: every cell's rectangle.
        used: route_flow's bookkeeping; its `branchy` names the multi-branch decisions.

    Returns:
        True for such an exit.
    """
    src, dst = ends
    s, d = rects[src], rects[dst]
    return out_side in ("top", "bottom") and src not in used.get("branchy", ()) and d[0] >= s[0] + s[2]


def overshoot(segs: list, in_side: str, src: tuple, dst: tuple) -> bool:
    """Whether a path into a box to the right runs flat over the target's column to enter its top or bottom.

    Args:
        segs: the path's runs.
        in_side: the entry side.
        src: the source box.
        dst: the target box.

    Returns:
        True for an entry at the top or bottom after a horizontal run past the target's left edge, when the target lies wholly right of
        the source (a left entry could turn in the gap between them).
    """
    if in_side == "left" or dst[0] < src[0] + src[2]:
        return False
    return any(abs(p[1] - q[1]) < .5 and max(p[0], q[0]) > dst[0] + .5 for p, q in segs)
