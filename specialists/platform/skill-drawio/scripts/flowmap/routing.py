"""Flow page arrows routed by the engine: candidate paths scored by the layout audit's own geometry, the cleanest kept. Stdlib only.

Operator, 2026-10-21 (smc-resiliency review of a crowded flow page): overlaps must be found and resolved by the skill, not fixed by hand per
case. Every forward arrow on a flow page goes through `route_forward`: it builds the orthogonal candidates an arrow could take (straight through
the column gaps; over or under the lane on each reserved track; into the target's left side, top or bottom; from a decision's right, top or bottom
corner), scores each against what is already drawn (a box crossed, a run shared or running alongside another within NEAR px, a port already used,
crossings), and draws the cheapest. A decision's branches carry their case ("Yes" or "No" by default, or the step's `when` labels).

Imported, not run: `from flowmap.routing import route_forward, branch_label` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from itertools import permutations

from drawio.audit import crossing, rects_overlap, seg_hits_rect, segments
from drawio.mxfile import Page, label

#: Two parallel runs closer than this (px) read as one arrow.
NEAR = 8
#: Penalties: a crossed box makes a path unusable in practice; a shared or adjacent run, a reused port and a crossing make it worse.
COST_BOX, COST_ALONG, COST_PORT, COST_CROSS = 1000, 200, 60, 8
#: Edge style for engine-routed forward arrows (matching draw.io's forward arrows before 2026-10-21) and its label style.
STYLE = "edgeStyle=none;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#000000;jumpStyle=arc;jumpSize=6;"
#: Arc size where a flow arrow crosses another: a crossing that cannot be avoided hops, as on the Overview (operator review 2026-10-21).
JUMP = 6
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


def _candidates(src: tuple, dst: tuple, src_decision: bool, gap: float, tracks: dict, ways: tuple | None = None, dst_decision: bool = False) -> list:
    """Orthogonal paths from one box to another, each a polyline from the source's border to the target's.

    Args:
        src: the source box (x, y, w, h).
        dst: the target box.
        src_decision: whether the source is a decision.
        gap: the space between step columns.
        tracks: {"top": [y, ...], "bottom": [y, ...]} runs reserved in the source and target lanes, nearest the edge first.
        ways: exits allowed ("right", "up", "down"); all when None.
        dst_decision: the target is a diamond, entered only at its left corner (a side entry off the middle misses the outline).

    Returns:
        Candidate polylines.
    """
    sx, sy, sw, sh = src
    dx, dy, dw, dh = dst
    lefts = [(dx, dy + dh * f) for f in ((0.5,) if dst_decision else (0.5, 0.33, 0.67))]   # spread entries so two arrows never share a point
    top_in, bottom_in = (dx + dw / 2, dy), (dx + dw / 2, dy + dh)
    before, after = dx - gap / 2, sx + sw + gap / 2
    out = []
    for (ex, ey), way in _exits(src, src_decision):
        if ways is not None and way not in ways:
            continue
        if way == "right":
            for turn in dict.fromkeys((after, before)):   # down or up in a column gap, then into the left side
                out += [[(ex, ey), (turn, ey), (turn, left[1]), left] for left in lefts]
            if ey < dy:   # straight across above the target, then down into its top (never through the target itself)
                out.append([(ex, ey), (top_in[0], ey), top_in])
            elif ey > dy + dh:
                out.append([(ex, ey), (bottom_in[0], ey), bottom_in])
        for edge in ("top", "bottom"):
            for ty in tracks.get(edge, []):
                rise = (ex, ty) if way != "right" else None
                head = [(ex, ey), rise] if rise else [(ex, ey), (after, ey), (after, ty)]
                end_in = top_in if edge == "top" else bottom_in
                out.append(head + [(end_in[0], ty), end_in])
                out += [head + [(before, ty), (before, left[1]), left] for left in lefts]
    return [[p for k, p in enumerate(c) if k == 0 or p != c[k - 1]] for c in out]


def route_forward(page: Page, edge: tuple, src_decision: bool, gap: float, tracks: dict, used: set, ways: tuple | None = None,
                  dst_decision: bool = False) -> float:
    """Draw one forward arrow along its cheapest candidate and label it on its longest clear run.

    Args:
        page: the page (steps drawn as solid boxes).
        edge: (cell id, source cell id, target cell id, label text).
        src_decision: whether the source step is a decision.
        gap: the space between step columns.
        tracks: reserved runs, as for `_candidates`.
        used: ports already taken; this arrow's ends are added.
        ways: exits allowed; all when None.
        dst_decision: the target is a diamond.

    Returns:
        The drawn path's cost.
    """
    cid, src, dst, text = edge
    ends = {src, dst}
    cands = (_candidates(page.rects[src], page.rects[dst], src_decision, gap, tracks, ways, dst_decision)
             or _candidates(page.rects[src], page.rects[dst], src_decision, gap, tracks, None, dst_decision))
    best = min(cands, key=lambda c: cost(page, c, ends, used))
    spent = cost(page, best, ends, used)
    page.route(cid, src, dst, best, STYLE, klass="thin", jump=JUMP)
    used.update((round(p[0]), round(p[1])) for p in (best[0], best[-1]))
    width = 18 + 9 * len(text)
    cx, cy = label_spot(page, cid, best, width, 22)
    page.mark(f"{cid}-lbl", label(f"**{text}**"), cx, cy, width, 22, LABEL, cid)
    return spent


def route_branches(page: Page, branches: list, gap: float, used: set) -> None:
    """Route a decision's branches together: try every assignment of the diamond's corners (right, top, bottom) to the branches, keep the one
    with the lowest total cost, then draw it (operator review 2026-10-21: "move arrow eight to the right and seven to the top" removed a
    crossing a branch-by-branch choice had made).

    Args:
        page: the page.
        branches: (edge, tracks, target is a diamond) per branch, edge as for `route_forward`; all from one decision.
        gap: the space between step columns.
        used: ports already taken.
    """
    best, best_total = None, None
    for ways in permutations(("right", "up", "down"), len(branches)):
        mark = (len(page.routes), len(page.cells), len(page.marks), set(used))
        total = sum(route_forward(page, edge, True, gap, tracks, used, (way,), diamond) for (edge, tracks, diamond), way in zip(branches, ways))
        del page.routes[mark[0]:], page.cells[mark[1]:], page.marks[mark[2]:]
        page.rects = {k: v for k, v in page.rects.items() if not k.endswith("-lbl") or k.rsplit("-lbl", 1)[0] not in {e[0] for e, _t, _d in branches}}
        used.clear(), used.update(mark[3])
        if best_total is None or total < best_total:
            best, best_total = ways, total
    for (edge, tracks, diamond), way in zip(branches, best):
        route_forward(page, edge, True, gap, tracks, used, (way,), diamond)


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


def _tracks_for(lanes: tuple, src: str, dst: str) -> dict:
    """The one run `plan_runs` reserved for this arrow (on the target lane's planned edge), so routes keep to the room the lanes were sized for.

    Args:
        lanes: ({step id: (lane top, lane height, lane index)}, run counts, track gap, planned routes {(src, dst): (side, track)}).
        src: the source step id.
        dst: the target step id.

    Returns:
        {"top": [y]} or {"bottom": [y]}; empty for an arrow with no planned run (adjacent, or entering from the left).
    """
    at, _count, gap, route = lanes
    side, n = route.get((src, dst), ("", 0))
    if side not in ("top", "bottom"):
        return {}
    top, height, _li = at[dst]
    return {side: [top + 10 + gap * n if side == "top" else top + height - 10 - gap * n]}


def route_flow(page: Page, flow: tuple, lanes: tuple, gap: float, look: dict) -> None:
    """Route every forward arrow of a flow page: short arrows first so the long ones route around them, a decision's branches together.

    Args:
        page: the page (steps drawn as solid boxes).
        flow: (flow id, steps, edges from `step_edges`, shapes by step id).
        lanes: ({step id: (lane top, lane height, lane index)}, run counts and planned routes from `plan_runs`, track gap).
        gap: the space between step columns.
        look: the drawing look (branch labels).
    """
    fid, steps, edges, shapes = flow
    by_id = {s["id"]: s for s in steps}
    order = {s["id"]: k for k, s in enumerate(steps)}
    forward = sorted((e for e in edges if "back to" not in e[3]), key=lambda e: order[e[2]] - order[e[1]])
    used: set = set()
    done: set = set()
    ctx = (fid, by_id, order, lanes, look)
    for cid, src, dst, _text, _style in forward:
        if cid in done:
            continue
        group = [e for e in forward if e[1] == src] if shapes[src] == "decision" else []
        if 1 < len(group) <= 3:   # a decision's branches are routed together (best corner per branch)
            route_branches(page, [(*_edge_of(ctx, c, s, d), shapes[d] == "decision") for c, s, d, _t, _st in group], gap, used)
            done.update(e[0] for e in group)
            continue
        edge, tracks = _edge_of(ctx, cid, src, dst)
        route_forward(page, edge, shapes[src] == "decision", gap, tracks, used, None, shapes[dst] == "decision")


def _edge_of(ctx: tuple, cid: str, src: str, dst: str) -> tuple:
    """One arrow as the router takes it: its cell ids and label, and the runs it may use.

    Args:
        ctx: (flow id, steps by id, step order, lanes as for `route_flow`, look).
        cid: the edge cell id.
        src: the source step id.
        dst: the target step id.

    Returns:
        ((cell id, source cell, target cell, label), tracks).
    """
    fid, by_id, order, lanes, look = ctx
    text = branch_label(by_id[src], dst, order[dst] + 1, look)
    return (cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text), _tracks_for(lanes, src, dst)

