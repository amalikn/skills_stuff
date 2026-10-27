"""Route costs that judge how an arrow meets its boxes on a flow page, used by flowmap.routing.cost. Stdlib only.

Operator review 2026-10-26 (smc_change PHP step page): arrows to the next step ran flat over the target's column to come in at its top or
bottom, and an arrow left a decision's top vertex to climb at its centre; both should turn in the gap between the columns.

Also the run tests the router and its repair passes share: `_along`, `_crosses`, `_overlaps`, and an arrow label's size (`label_size`).

Imported, not run: `from flowmap.route_costs import overshoot, leaves_off_side, _along, _crosses, _overlaps, label_size` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import crossing, seg_hits_rect, segments

#: Two parallel runs closer than this (px) read as one arrow.
NEAR = 8


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


def _along(seg: tuple, other: tuple) -> bool:
    """Whether two runs are parallel, within NEAR px of each other and overlap by more than 2 px.

    Args:
        seg: one run.
        other: the other run.

    Returns:
        True when they would read as one arrow.
    """
    (p, q), (u, v) = seg, other
    if abs(p[1] - q[1]) < .5 and abs(u[1] - v[1]) < .5 and abs(p[1] - u[1]) < NEAR:
        return max(min(p[0], q[0]), min(u[0], v[0])) < min(max(p[0], q[0]), max(u[0], v[0])) - 2
    if abs(p[0] - q[0]) < .5 and abs(u[0] - v[0]) < .5 and abs(p[0] - u[0]) < NEAR:
        return max(min(p[1], q[1]), min(u[1], v[1])) < min(max(p[1], q[1]), max(u[1], v[1])) - 2
    return False

def _crosses(page: Page, path: tuple) -> int:
    """How many routed arrows' runs a candidate crosses.

    Args:
        page: the page.
        path: (points, exit side, entry side, odd exit).

    Returns:
        The crossing count.
    """
    others = [s for r in page.routes for s in segments(r.points)]
    return sum(1 for s in segments(path[0]) for o in others if crossing(s, o) is not None)

def _overlaps(page: Page, path: tuple) -> int:
    """How many runs of routed arrows or labels a candidate runs along or over (two arrows sharing a run read as one).

    Args:
        page: the page.
        path: (points, exit side, entry side, odd exit).

    Returns:
        The count of runs alongside another arrow plus labels crossed.
    """
    segs = segments(path[0])
    others = [s for r in page.routes for s in segments(r.points)]
    return sum(1 for s in segs for o in others if _along(s, o)) + sum(1 for p, q in segs for m in page.marks if seg_hits_rect(p, q, m.rect, 0))

def label_size(text: str) -> tuple[float, float]:
    """An arrow label's box: as wide as its longest line, one 22 px line plus 15 px for each line below it.

    Args:
        text: the label, lines split by a newline (see branch_label).

    Returns:
        (width, height) in px.
    """
    lines = text.split("\n")
    return 18 + 9 * max(len(line) for line in lines), 22 + 15 * (len(lines) - 1)
