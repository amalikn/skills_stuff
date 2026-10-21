"""Flow page arrows routed by the engine: candidate paths scored by the layout audit's own geometry, the cleanest kept. Stdlib only.

Operator, 2026-10-21 (smc-resiliency review of a crowded flow page): overlaps must be found and resolved by the skill, not fixed by hand per
case. Every forward arrow on a flow page goes through `route_forward`: it builds the orthogonal candidates an arrow could take (straight through
the column gaps; over or under the lane on each reserved track; into the target's left side, top or bottom; from a decision's right, top or bottom
corner), scores each against what is already drawn (a box crossed, a run shared or running alongside another within NEAR px, a port already used,
crossings), and draws the cheapest. A decision's branches carry their case ("Yes" or "No" by default, or the step's `when` labels).

Imported, not run: `from flowmap.routing import route_forward, branch_label` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import crossing, rects_overlap, seg_hits_rect, segments
from drawio.mxfile import Page, label

#: Two parallel runs closer than this (px) read as one arrow.
NEAR = 8
#: Penalties: a crossed box makes a path unusable in practice; a shared or adjacent run, a reused port and a crossing make it worse.
COST_BOX, COST_ALONG, COST_PORT, COST_CROSS = 1000, 200, 60, 8
#: Edge style for engine-routed forward arrows (matching draw.io's forward arrows before 2026-10-21) and its label style.
STYLE = "edgeStyle=none;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#000000;"
LABEL = "text;html=1;align=center;verticalAlign=middle;fontSize=16;fontStyle=1;labelBackgroundColor=#ffffff;"


def branch_label(step: dict, target: str, number: int, look: dict) -> str:
    """An arrow's label: the target's step number, and for a decision's branch its case.

    Args:
        step: the source step.
        target: the target step id.
        number: the target's step number.
        look: the drawing look (`branch_labels`: "yes-no" by default, "off" for numbers only).

    Returns:
        "5", or "5 · No" for a decision's second branch (the step's `when` names other cases).
    """
    nxt = step.get("next") or []
    if not step.get("gate") or len(nxt) < 2 or look.get("branch_labels", "yes-no") == "off":
        return str(number)
    case = (step.get("when") or {}).get(target) or (("Yes", "No")[nxt.index(target)] if len(nxt) == 2 and target in nxt else "")
    return f"{number} · {case}" if case else str(number)


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


def cost(page: Page, pts: list, ends: set, used: set) -> float:
    """A candidate path's cost against what the page already holds.

    Args:
        page: the page (its solid boxes and routed edges).
        pts: the candidate polyline.
        ends: the source and target cell ids (the path may touch them).
        used: ports already taken, as rounded (x, y) points.

    Returns:
        The weighted fault count plus the path length / 1000 (so a shorter clean path wins).
    """
    segs = segments(pts)
    boxes = sum(1 for p, q in segs for cid in page.solid if cid not in ends and seg_hits_rect(p, q, page.rects[cid]))
    others = [s for r in page.routes for s in segments(r.points)]
    along = sum(1 for s in segs for o in others if _along(s, o))
    crosses = sum(1 for s in segs for o in others if crossing(s, o) is not None)
    labels = sum(1 for p, q in segs for m in page.marks if seg_hits_rect(p, q, m.rect, 0))   # running over another arrow's label
    ports = sum(1 for pt in (pts[0], pts[-1]) if (round(pt[0]), round(pt[1])) in used)
    length = sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in segs)
    return boxes * COST_BOX + (along + labels) * COST_ALONG + ports * COST_PORT + crosses * COST_CROSS + length / 1000


def _exits(rect: tuple, decision: bool) -> list:
    """Where an arrow may leave a box: the right side's middle, and for a decision also its top and bottom corners.

    Args:
        rect: the source box.
        decision: whether it is a decision (a diamond).

    Returns:
        (point, direction) pairs; direction is "right", "up" or "down".
    """
    x, y, w, h = rect
    out = [((x + w, y + h / 2), "right")]
    if decision:
        out += [((x + w / 2, y), "up"), ((x + w / 2, y + h), "down")]
    return out


def _candidates(src: tuple, dst: tuple, src_decision: bool, gap: float, tracks: dict) -> list:
    """Orthogonal paths from one box to another, each a polyline from the source's border to the target's.

    Args:
        src: the source box (x, y, w, h).
        dst: the target box.
        src_decision: whether the source is a decision.
        gap: the space between step columns.
        tracks: {"top": [y, ...], "bottom": [y, ...]} runs reserved in the source and target lanes, nearest the edge first.

    Returns:
        Candidate polylines.
    """
    sx, sy, sw, sh = src
    dx, dy, dw, dh = dst
    left, top_in, bottom_in = (dx, dy + dh / 2), (dx + dw / 2, dy), (dx + dw / 2, dy + dh)
    before, after = dx - gap / 2, sx + sw + gap / 2
    out = []
    for (ex, ey), way in _exits(src, src_decision):
        if way == "right":
            for turn in dict.fromkeys((after, before)):   # down or up in a column gap, then into the left side
                out.append([(ex, ey), (turn, ey), (turn, left[1]), left])
            out.append([(ex, ey), (top_in[0], ey), top_in] if ey < dy else [(ex, ey), (bottom_in[0], ey), bottom_in])
        for edge in ("top", "bottom"):
            for ty in tracks.get(edge, []):
                rise = (ex, ty) if way != "right" else None
                head = [(ex, ey), rise] if rise else [(ex, ey), (after, ey), (after, ty)]
                end_in = top_in if edge == "top" else bottom_in
                out.append(head + [(end_in[0], ty), end_in])
                out.append(head + [(before, ty), (before, left[1]), left])
    return [[p for k, p in enumerate(c) if k == 0 or p != c[k - 1]] for c in out]


def route_forward(page: Page, edge: tuple, src_decision: bool, gap: float, tracks: dict, used: set) -> None:
    """Draw one forward arrow along its cheapest candidate and label it on its longest clear run.

    Args:
        page: the page (steps drawn as solid boxes).
        edge: (cell id, source cell id, target cell id, label text).
        src_decision: whether the source step is a decision.
        gap: the space between step columns.
        tracks: reserved runs, as for `_candidates`.
        used: ports already taken; this arrow's ends are added.
    """
    cid, src, dst, text = edge
    ends = {src, dst}
    cands = _candidates(page.rects[src], page.rects[dst], src_decision, gap, tracks)
    best = min(cands, key=lambda c: cost(page, c, ends, used))
    page.route(cid, src, dst, best, STYLE, klass="thin")
    used.update((round(p[0]), round(p[1])) for p in (best[0], best[-1]))
    width = 18 + 9 * len(text)
    cx, cy = label_spot(page, cid, best, width, 22)
    page.mark(f"{cid}-lbl", label(f"**{text}**"), cx, cy, width, 22, LABEL, cid)


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
        The label's centre; the middle of the longest run when no spot is clear.
    """
    segs = sorted(segments(pts), key=lambda s: -(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1])))
    others = [s for r in page.routes if r.cid != cid for s in segments(r.points)]
    for p, q in segs:
        for f in (0.5, 0.33, 0.67, 0.2, 0.8):
            cx, cy = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
            rect = (cx - w / 2, cy - h / 2, w, h)
            clear = (not any(seg_hits_rect(a, b, rect, 0) for a, b in others)
                     and not any(rects_overlap(rect, m.rect) for m in page.marks)
                     and not any(rects_overlap(rect, page.rects[c]) for c in page.solid))
            if clear:
                return cx, cy
    p, q = segs[0]
    return (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
