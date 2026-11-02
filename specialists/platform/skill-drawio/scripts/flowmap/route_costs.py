"""Route costs that judge how an arrow meets its boxes on a flow page, used by flowmap.routing.cost. Stdlib only.

Operator review 2026-10-26 (smc_change PHP step page): arrows to the next step ran flat over the target's column to come in at its top or
bottom, and an arrow left a decision's top vertex to climb at its centre; both should turn in the gap between the columns.

Also the run tests the router and its repair passes share: `_along`, `_crosses`, `_overlaps`, and an arrow label's size (`label_size`).

Imported, not run: `from flowmap.route_costs import overshoot, leaves_off_side, _along, _crosses, _overlaps, label_size` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import crossing, rects_overlap, seg_hits_rect, segments

#: The least first run out of a box, and the least last run into one.
STUB, HEAD = 12, 22
#: How far below the lowest box a `look.route_under` track runs, the least step to the next, and how many are on offer.
UNDER_CLEAR, UNDER_STEP, UNDER_TRACKS = 24, 14, 4
#: Where tracks sit across a free band: two arrows take the outer two, a third the middle.
BAND_SHARES = (0.15, 0.85, 0.5)
#: How close a horizontal run may come to a lane boundary (`look.run_spacing` on).
EDGE_GAP = 18
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

def too_close(seg: tuple, other: tuple, gap: float) -> bool:
    """Whether two parallel runs sit within `gap` of each other, side by side or one ending where the other starts (operator, 2026-11-02: an arrow turned
    beside another with open space to spare).

    Args:
        seg: one run.
        other: another run.
        gap: the least space between them.

    Returns:
        True when they are too close.
    """
    (p, q), (u, v) = seg, other
    for across, along in ((1, 0), (0, 1)):   # horizontal runs, then vertical
        if abs(p[across] - q[across]) < .5 and abs(u[across] - v[across]) < .5 and abs(p[across] - u[across]) < gap:
            return max(min(p[along], q[along]), min(u[along], v[along])) < min(max(p[along], q[along]), max(u[along], v[along])) + gap
    return False


def on_lane_edge(seg: tuple, edges: list) -> bool:
    """Whether a horizontal run hugs a lane boundary, where it reads as part of the boundary (operator, 2026-11-02).

    Args:
        seg: the run.
        edges: the lanes' boundaries, y.

    Returns:
        True when it runs within EDGE_GAP of one.
    """
    (_x0, y0), (_x1, y1) = seg
    return abs(y0 - y1) < .5 and any(abs(y0 - y) < EDGE_GAP for y in edges)


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


#: Room between a vertical line and each half of a label split across it.
SPLIT_GAP = 5
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


def label_spot(page: Page, cid: str, pts: list, w: float, h: float, split: tuple | None = None) -> tuple[float, float, bool]:
    """Where an arrow's label goes: along its runs, longest first, at the middle then a third and two thirds in, the first spot whose box
    touches no other arrow, no other label and no box (operator review 2026-10-21: a branch label sat on its sibling arrow).

    Args:
        page: the page (routes, labels and boxes already drawn).
        cid: the arrow's cell id (its own route is ignored).
        pts: the arrow's polyline.
        w: the label's width.
        h: the label's height.
        split: (number width, case width) for a two-line label: on a vertical run it may then sit across the line, number left of it and
            case right of it (operator, 2026-10-27), with no text on the line.

    Returns:
        (x, y, across): the label's centre (on the line, else just beside it; the middle of the longest run when no spot is clear), and
        whether a split label sits across a vertical line (x is then the line).
    """
    # Points straight through drop out first: a run drawn as two halves put the label beside one box or the other, never between them
    # (operator review 2026-10-27, smc_change Apply: "text of arrow 2 is too close to box 1").
    pts = [pt for k, pt in enumerate(pts) if k in (0, len(pts) - 1) or not _straight(pts[k - 1], pt, pts[k + 1])]
    segs = sorted(segments(pts), key=lambda s: -(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1])))
    others = [s for r in page.routes if r.cid != cid for s in segments(r.points)]
    margin = float(getattr(page, "label_clearance", 0))   # `look.label_clearance`: a label stopping 1 px short of a line still reads as on it (operator, 2026-11-02)
    for p, q in segs:
        flat = abs(p[1] - q[1]) < .5
        beside = [(0, 0)] + ([(0, -h / 2 - 3), (0, h / 2 + 3)] if flat else [(w / 2 + 4, 0), (-w / 2 - 4, 0)])   # on the line, then just beside it
        for (ox, oy), f in [(o, f) for o in beside for f in (0.5, 0.33, 0.67, 0.2, 0.8)]:
            cx, cy = p[0] + (q[0] - p[0]) * f + ox, p[1] + (q[1] - p[1]) * f + oy
            across = split is not None and not flat and (ox, oy) == (0, 0)
            rect = (cx - split[0] - SPLIT_GAP, cy - 11, split[0] + split[1] + 2 * SPLIT_GAP, 22) if across else (cx - w / 2, cy - h / 2, w, h)
            near = (rect[0] - margin, rect[1] - margin, rect[2] + 2 * margin, rect[3] + 2 * margin)
            if (not any(seg_hits_rect(a, b, near, 0) for a, b in others) and not any(rects_overlap(rect, m.rect) for m in page.marks)
                    and not any(rects_overlap(_clear(rect, LABEL_GAP), page.rects[c]) for c in page.solid)):
                return cx, cy, across
    p, q = segs[0]
    return (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, False


def ports(rect: tuple, diamond: bool, out: bool) -> list:
    """A box's connection points for leaving (`out`) or entering, each with its side.

    Args:
        rect: the box.
        diamond: whether it is a decision (only its corners are on the outline).
        out: exits (right, top, bottom) or entries (left, top, bottom).

    Returns:
        (point, side) pairs; an exit's side also names its direction ("right", "top" = up, "bottom" = down).
    """
    x, y, w, h = rect
    if out:
        return [((x + w, y + h / 2), "right"), ((x + w / 2, y), "top"), ((x + w / 2, y + h), "bottom")]
    lefts = [((x, y + h / 2), "left")] if diamond else [((x, y + h * f), "left") for f in (0.5, 0.33, 0.67)]
    return lefts + [((x + w / 2, y), "top"), ((x + w / 2, y + h), "bottom")]


def joins(p: tuple, out_side: str, q: tuple, in_side: str, corridors: dict) -> list:
    """Orthogonal polylines from an exit point to an entry point through the corridors.

    Args:
        p: the exit point.
        out_side: "right", "top" or "bottom".
        q: the entry point.
        in_side: "left", "top" or "bottom".
        corridors: {"xs": column gap centres, "ys": reserved run heights}.

    Returns:
        Polylines, unchecked.
    """
    xs, ys = corridors["xs"], corridors["ys"]
    out = []
    if out_side == "right":
        if in_side == "left":
            out += [[p, (x, p[1]), (x, q[1]), q] for x in xs if p[0] < x < q[0]]
        else:
            out.append([p, (q[0], p[1]), q])
            out += [[p, (x, p[1]), (x, y), (q[0], y), q] for x in xs if p[0] < x < q[0] for y in ys]
    else:
        mid = (p[1] + q[1]) / 2
        out.append([p, (p[0], q[1]), q] if in_side == "left" else [p, (p[0], mid), (q[0], mid), q])
        for y in ys:
            if in_side == "left":
                out += [[p, (p[0], y), (x, y), (x, q[1]), q] for x in xs if p[0] < x < q[0]]
            else:
                out.append([p, (p[0], y), (q[0], y), q])
    return out


def _direction(a: tuple, b: tuple) -> str:
    """The direction of a run.

    Args:
        a: its start.
        b: its end.

    Returns:
        "right", "left", "down", "up", or "" for a zero-length or diagonal run.
    """
    if abs(a[1] - b[1]) < .5 and abs(a[0] - b[0]) >= .5:
        return "right" if b[0] > a[0] else "left"
    if abs(a[0] - b[0]) < .5 and abs(a[1] - b[1]) >= .5:
        return "down" if b[1] > a[1] else "up"
    return ""


def valid(pts: list, out_side: str, in_side: str) -> bool:
    """Whether a polyline leaves and arrives the way its ports face, with room to leave and for the arrowhead, and no diagonal or zero run.

    Args:
        pts: the polyline (repeated points already dropped).
        out_side: the exit side.
        in_side: the entry side.

    Returns:
        True when usable.
    """
    if len(pts) < 2:
        return False
    runs = list(zip(pts, pts[1:]))
    if any(_direction(a, b) == "" for a, b in runs):
        return False
    first, last = runs[0], runs[-1]
    leave = {"right": "right", "top": "up", "bottom": "down"}[out_side]
    arrive = {"left": "right", "top": "down", "bottom": "up"}[in_side]
    first_len = abs(first[0][0] - first[1][0]) + abs(first[0][1] - first[1][1])
    last_len = abs(last[0][0] - last[1][0]) + abs(last[0][1] - last[1][1])
    return _direction(*first) == leave and _direction(*last) == arrive and first_len >= STUB and last_len >= HEAD


def with_under(page: Page, corridors: dict, p: tuple, q: tuple) -> dict:
    """The corridors for one arrow, with `look.route_under`'s tracks: just below the lowest box between its ends, so it clears the boxes it passes and no
    more (operator, 2026-11-02: below the shapes, not below every lane).

    Args:
        page: the page.
        corridors: as for `joins`, with "under" set when the look asks.
        p: the exit point.
        q: the entry point.

    Returns:
        The corridors.
    """
    if not corridors.get("under"):
        return corridors
    lo, hi = sorted((p[0], q[0]))
    bottoms = [r[1] + r[3] for r in (page.rects[c] for c in page.solid) if r[0] < hi and r[0] + r[2] > lo]
    if not bottoms:
        return corridors
    step = max(UNDER_STEP, float(getattr(page, "run_spacing", 0)))   # tracks keep the page's spacing; several, so one clear of the lane edges is on offer
    base = max(bottoms) + UNDER_CLEAR
    tracks = [base + k * step for k in range(UNDER_TRACKS)]
    below = [y for y in getattr(page, "lane_edges", []) if y > base + EDGE_GAP]
    if below:   # spread over the free band, so arrows use the room there is (operator, 2026-11-02)
        tracks = [base + (below[0] - base) * f for f in BAND_SHARES] + tracks
    return {**corridors, "ys": [*corridors["ys"], *tracks]}
