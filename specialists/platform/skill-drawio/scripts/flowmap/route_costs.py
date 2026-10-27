"""Route costs that judge how an arrow meets its boxes on a flow page, used by flowmap.routing.cost. Stdlib only.

Operator review 2026-10-26 (smc_change PHP step page): arrows to the next step ran flat over the target's column to come in at its top or
bottom, and an arrow left a decision's top vertex to climb at its centre; both should turn in the gap between the columns.

Also the run tests the router and its repair passes share: `_along`, `_crosses`, `_overlaps`, and an arrow label's size (`label_size`).

Imported, not run: `from flowmap.route_costs import overshoot, leaves_off_side, _along, _crosses, _overlaps, label_size` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import crossing, rects_overlap, seg_hits_rect, segments

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


#: Room a label keeps from every box (operator review 2026-10-27: "text of arrow 2 is too close to box 1").
LABEL_GAP = 8


def _clear(rect: tuple, gap: float) -> tuple:
    """A rectangle grown by a margin on every side.

    Args:
        rect: (x, y, width, height).
        gap: the margin.

    Returns:
        The grown rectangle.
    """
    return rect[0] - gap, rect[1] - gap, rect[2] + 2 * gap, rect[3] + 2 * gap


def lane_colour(page: Page, x: float, y: float) -> str:
    """The colour a lane shows at a point (its fill over the white page at the lane's opacity), for a label background that hides the line
    behind the text without showing a white box on a tinted lane (operator, 2026-10-27: "remove white background from arrow text").

    Args:
        page: the page.
        x: the point's x.
        y: the point's y.

    Returns:
        A #rrggbb colour; white outside every lane.
    """
    for cid, (lx, ly, lw, lh) in page.rects.items():
        if "-lane-" not in cid or not (lx <= x <= lx + lw and ly <= y <= ly + lh):
            continue
        style = dict(kv.split("=", 1) for kv in page.cell_style.get(cid, "").split(";") if "=" in kv)
        fill, alpha = style.get("fillColor", "#ffffff"), float(style.get("opacity", 100)) / 100
        if not fill.startswith("#") or len(fill) != 7:
            continue
        rgb = [int(fill[k:k + 2], 16) for k in (1, 3, 5)]
        return "#" + "".join(f"{round(c * alpha + 255 * (1 - alpha)):02x}" for c in rgb)
    return "#ffffff"


def _straight(a: tuple, b: tuple, c: tuple) -> bool:
    """Whether b lies on the straight run from a to c (all three on one horizontal or one vertical line).

    Args:
        a: the point before.
        b: the point.
        c: the point after.

    Returns:
        True when b is no corner.
    """
    return (abs(a[1] - b[1]) < .5 and abs(b[1] - c[1]) < .5) or (abs(a[0] - b[0]) < .5 and abs(b[0] - c[0]) < .5)


def label_spot(page: Page, cid: str, pts: list, w: float, h: float) -> tuple[float, float]:
    """Where an arrow's label goes: along its runs, longest first, at the middle then a third and two thirds in, the first spot whose box
    touches no other arrow, no other label and no box (operator review 2026-10-21: a branch label sat on its sibling arrow).

    Args:
        page: the page (routes, labels and boxes already drawn).
        cid: the arrow's cell id (its own route is ignored).
        pts: the arrow's polyline.
        w: the label's width.
        h: the label's height.

    Returns:
        The label's centre (on the line, else just beside it); the middle of the longest run when no spot is clear.
    """
    # Points straight through drop out first: a run drawn as two halves put the label beside one box or the other, never between them
    # (operator review 2026-10-27, smc_change Apply: "text of arrow 2 is too close to box 1").
    pts = [pt for k, pt in enumerate(pts) if k in (0, len(pts) - 1) or not _straight(pts[k - 1], pt, pts[k + 1])]
    segs = sorted(segments(pts), key=lambda s: -(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1])))
    others = [s for r in page.routes if r.cid != cid for s in segments(r.points)]
    for p, q in segs:
        flat = abs(p[1] - q[1]) < .5
        beside = [(0, 0)] + ([(0, -h / 2 - 3), (0, h / 2 + 3)] if flat else [(w / 2 + 4, 0), (-w / 2 - 4, 0)])   # on the line, then just beside it
        for (ox, oy), f in [(o, f) for o in beside for f in (0.5, 0.33, 0.67, 0.2, 0.8)]:
            cx, cy = p[0] + (q[0] - p[0]) * f + ox, p[1] + (q[1] - p[1]) * f + oy
            rect = (cx - w / 2, cy - h / 2, w, h)
            if (not any(seg_hits_rect(a, b, rect, 0) for a, b in others) and not any(rects_overlap(rect, m.rect) for m in page.marks)
                    and not any(rects_overlap(_clear(rect, LABEL_GAP), page.rects[c]) for c in page.solid)):
                return cx, cy
    p, q = segs[0]
    return (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
