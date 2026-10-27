"""Flow page arrows routed by the engine: candidate paths over every pair of connection points, scored by the layout audit's geometry, the
cheapest kept. Stdlib only.

Operator, 2026-10-21 (smc-resiliency reviews of a crowded flow page): overlaps are the skill's to find and resolve, as the Overview's router does,
using every connection point of a shape. Every forward arrow goes through `route_forward`. Its candidates pair each exit (a box's right side; a
decision's right, top and bottom corners; a plain box's top and bottom too, at a small cost) with each entry (the left side at a third, half and two
thirds; top; bottom; a diamond only at its corners), joined through the column gaps and the runs the lanes reserved. A candidate must leave and
arrive the way its ports face and never run inside its own source or target. Each is scored against what is drawn: a box crossed, a run alongside
another or over a label, a point or a side already used, crossings (drawn as arc hops), bends, length. A decision's branches are routed together
(`route_branches`); a yes/no decision's branches are green (Yes) and red (No). Greedy order can still leave two arrows crossing that need
not: `flowmap.uncross` then redraws each crossing pair in the other order and keeps it only when the page has fewer crossings (2026-10-22).

Imported, not run: `from flowmap.routing import route_flow, branch_label` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from itertools import permutations

from drawio.audit import crossing, rects_overlap, seg_hits_rect, segments
from drawio.mxfile import ARROW_HEAD, Page, label

from .route_costs import NEAR, _along, _crosses, _overlaps, label_size, leaves_off_side, overshoot

#: Costs: a crossed box (or the arrow's own box) is unusable in practice; a run alongside another or over a label, a reused point, a reused side,
#: a crossing, a bend and an exit off a plain box's right side each make a path worse.
COST_BOX, COST_ALONG, COST_PORT, COST_SIDE, COST_CROSS, COST_BEND, COST_ODD_EXIT = 1000, 200, 60, 120, 30, 4, 15
#: A path into a box on the right that runs flat past the gap, over the target's column, to come in at its top or bottom (operator review
#: 2026-10-26: "why is it extending so much to the right and then going down?"): turning in the gap and entering the left side reads as the
#: next step. Above COST_SIDE, so a second arrow takes another left port rather than overshoot; well below a crossing of a box or a label.
COST_OVERSHOOT = 150
# Two branches of one decision crossing each other: a swap of their corners nearly always avoids it, so it outweighs a shared side
# (operator review 2026-10-27, smc_change Apply page: "overlap of 7 and 10 could have been easily avoided").
COST_SIBLING_CROSS = 400
#: Shortest first run (leaving a box) and last run (the arrowhead's room, as drawio.audit.HEAD_ROOM thin).
STUB, HEAD = 12, 22
#: Arc size where a flow arrow crosses another: an unavoidable crossing hops, as on the Overview.
JUMP = 6
STYLE = "edgeStyle=none;rounded={rounded};html=1;" + ARROW_HEAD + "jumpStyle=arc;jumpSize=6;strokeColor={colour};"
LABEL = "text;html=1;align=center;verticalAlign=middle;fontSize=16;fontStyle=1;labelBackgroundColor=#ffffff;fontColor={colour};"
#: A yes/no decision's branch colours (operator, 2026-10-21: show the boolean nature); other arrows are black.
YES, NO, PLAIN = "#1b7a3a", "#b3261e", "#000000"


def branch_label(step: dict, target: str, number: int, look: dict) -> tuple[str, str]:
    """An arrow's label and colour: the target's step number, and for a decision's branch its case.

    Args:
        step: the source step.
        target: the target step id.
        number: the target's step number.
        look: the drawing look (`branch_labels`: "yes-no" by default, "off" for numbers only).

    Returns:
        ("5", black), ("5\nYes", green), ("5\nNo", red), or ("5\n<case>", black) for a step's own `when` case: the step number on its
        own line and the case below it, so a long case does not stretch the label along the arrow (operator, 2026-10-27: "9\nstill busy
        ... make this a standard").
    """
    nxt = step.get("next") or []
    # A decision is a gate or an explicit shape: decision; every branch out of it says why it is taken (operator, 2026-10-23).
    decision = step.get("gate") or step.get("shape") == "decision"
    if not decision or len(nxt) < 2 or look.get("branch_labels", "yes-no") == "off":
        return str(number), PLAIN
    case = (step.get("when") or {}).get(target)
    if case:
        return f"{number}\n{case}", PLAIN
    if len(nxt) == 2 and target in nxt:
        yes = nxt.index(target) == 0
        return f"{number}\n{'Yes' if yes else 'No'}", YES if yes else NO
    return str(number), PLAIN


def cost(page: Page, path: tuple, ends: tuple, used: dict) -> float:
    """A candidate's cost against what the page already holds.

    Args:
        page: the page (its solid boxes, routed edges and labels).
        path: (points, exit side, entry side, odd exit).
        ends: (source cell id, target cell id).
        used: {"points": set of rounded points, "sides": set of (cell id, side)} already taken.

    Returns:
        The weighted fault count plus the length / 1000 (a shorter clean path wins).
    """
    pts, out_side, in_side, odd = path
    src, dst = ends
    segs = segments(pts)
    boxes = sum(1 for p, q in segs for cid in page.solid if cid not in ends and seg_hits_rect(p, q, page.rects[cid]))
    own = sum(1 for p, q in segs[1:] if seg_hits_rect(p, q, page.rects[src])) + sum(1 for p, q in segs[:-1] if seg_hits_rect(p, q, page.rects[dst]))
    others = [s for r in page.routes for s in segments(r.points)]
    along = sum(1 for s in segs for o in others if _along(s, o))
    crosses = sum(1 for s in segs for o in others if crossing(s, o) is not None)
    labels = sum(1 for p, q in segs for m in page.marks if seg_hits_rect(p, q, m.rect, 0))
    points = sum(1 for pt in (pts[0], pts[-1]) if (round(pt[0]), round(pt[1])) in used["points"])
    # A decision has one point per corner, so a second arrow there merges into the first for its last run (operator review 2026-10-27,
    # smc_change PHP step page: 12 -> 13 and 11 -> 13 shared 13's left corner). Weighted as a crossed box, so it takes a free corner,
    # top or bottom, whichever path is better, and shares only when every corner is taken.
    shared = sum(1 for cid, pt in ((src, pts[0]), (dst, pts[-1])) if cid in used.get("diamonds", ()) and (round(pt[0]), round(pt[1])) in used["points"])
    # A branchy decision's top and bottom are held for its own branches (route_flow): they block arrows in, not a branch leaving there,
    # unless a sibling branch already took that corner (operator review 2026-10-27: branch 7 left the right and crossed branch 10, which
    # had the bottom, because the bottom counted as taken for both).
    own_corner = src in used.get("branchy", ()) and (src, out_side) not in used.get("taken", ())
    sides = ((src, out_side) in used["sides"] and not own_corner) + ((dst, in_side) in used["sides"])
    length = sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in segs)
    return ((boxes + own + shared) * COST_BOX + (along + labels) * COST_ALONG + points * COST_PORT + sides * COST_SIDE + crosses * COST_CROSS
            + (len(segs) - 1) * COST_BEND + odd * COST_ODD_EXIT + length / 1000
            + (overshoot(segs, in_side, page.rects[src], page.rects[dst]) + leaves_off_side(out_side, ends, page.rects, used)) * COST_OVERSHOOT)


def _ports(rect: tuple, diamond: bool, out: bool) -> list:
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


def _joins(p: tuple, out_side: str, q: tuple, in_side: str, corridors: dict) -> list:
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


def _valid(pts: list, out_side: str, in_side: str) -> bool:
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


def _candidates(page: Page, ends: tuple, diamonds: tuple, corridors: dict, ways: tuple | None) -> list:
    """Every usable path from the source to the target.

    Args:
        page: the page.
        ends: (source cell id, target cell id).
        diamonds: (source is a decision, target is a decision).
        corridors: as for `_joins`.
        ways: exit sides allowed; all when None.

    Returns:
        (points, exit side, entry side, odd exit) per usable path.
    """
    src, dst = ends
    out = []
    for p, side in _ports(page.rects[src], diamonds[0], True):
        if ways is not None and side not in ways:
            continue
        odd = side != "right" and not diamonds[0]
        for q, entry in _ports(page.rects[dst], diamonds[1], False):
            for pts in _joins(p, side, q, entry, corridors):
                pts = [pt for k, pt in enumerate(pts) if k == 0 or pt != pts[k - 1]]
                if _valid(pts, side, entry):
                    out.append((pts, side, entry, odd))
    return out


def route_forward(page: Page, edge: tuple, diamonds: tuple, corridors: dict, used: dict, ways: tuple | None = None, strict: bool = False,
                  fewest_crossings: bool = False, choice: int = 0) -> float:
    """Draw one forward arrow along its cheapest candidate, in its colour, labelled on a clear spot.

    Args:
        page: the page (steps drawn as solid boxes).
        edge: (cell id, source cell id, target cell id, label text, colour).
        diamonds: (source is a decision, target is a decision).
        corridors: {"xs": column gap centres, "ys": reserved run heights, "rounded": 1 or 0 for the corner style}.
        used: points and sides already taken; this arrow's are added.
        ways: exit sides allowed; all when None.
        strict: with `ways`, draw nothing and return a very large cost when no path leaves that way (no fallback to another side).
        fewest_crossings: choose the path crossing the fewest drawn arrows (one through a box or a shared decision corner never wins,
            and one running along another arrow or over a label loses to any that does not), then the cheapest; flowmap.uncross uses it when reordering and other exit sides cannot remove a crossing.
        choice: with `fewest_crossings`, take the path at this rank instead of the best (the repair tries a pair's combinations); past
            the last candidate nothing is drawn and a very large cost is returned.

    Returns:
        The drawn path's cost (a very large number when nothing fits).
    """
    cid, src, dst, text, colour = edge
    cands = _candidates(page, (src, dst), diamonds, corridors, ways)
    if not cands and strict:
        return 1e6
    cands = cands or _candidates(page, (src, dst), diamonds, corridors, None)
    if not cands:
        page.edge(cid, src, dst, label=text.replace("\n", " "), style=f"strokeColor={colour};fontColor={colour};")
        return 1e9
    if fewest_crossings:   # the repair pass's last resort: fewest crossings first, a box or a shared corner still ruled out, then cost
        ranked = sorted(cands, key=lambda c: (cost(page, c, (src, dst), used) >= COST_BOX, _overlaps(page, c), _crosses(page, c),
                                              cost(page, c, (src, dst), used)))
        if choice >= len(ranked):
            return 1e6
        best = ranked[choice]
    else:
        best = min(cands, key=lambda c: cost(page, c, (src, dst), used))
    spent = cost(page, best, (src, dst), used)
    pts, out_side, in_side, _odd = best
    page.route(cid, src, dst, pts, STYLE.format(colour=colour, rounded=corridors.get("rounded", 1)), klass="thin", jump=JUMP)
    used["points"].update((round(p[0]), round(p[1])) for p in (pts[0], pts[-1]))
    used["sides"].update({(src, out_side), (dst, in_side)})
    used.setdefault("taken", set()).add((src, out_side))
    width, height = label_size(text)
    cx, cy = label_spot(page, cid, pts, width, height)
    page.mark(f"{cid}-lbl", label(*(f"**{line}**" for line in text.split("\n"))), cx, cy, width, height, LABEL.format(colour=colour), cid)
    return spent


def route_branches(page: Page, branches: list, corridors: dict, used: dict) -> None:
    """Route a decision's branches together: every assignment of its corners (right, top, bottom) to the branches is tried and the one with
    the lowest total cost drawn, a crossing between two of the branches costing COST_SIBLING_CROSS (operator review 2026-10-21: "move arrow
    eight to the right and seven to the top"; 2026-10-27: branches 7 and 10 crossed).

    Args:
        page: the page.
        branches: (edge, target is a decision) per branch, edge as for `route_forward`; all from one decision.
        corridors: as for `route_forward`.
        used: points and sides already taken.
    """
    best, best_total = None, None
    for ways in permutations(("right", "top", "bottom"), len(branches)):
        mark = (len(page.routes), len(page.cells), len(page.marks), dict(page.rects), {k: set(v) for k, v in used.items()})
        total = sum(route_forward(page, edge, (True, diamond), corridors, used, (way,), True) for (edge, diamond), way in zip(branches, ways))
        mine = page.routes[mark[0]:]
        total += COST_SIBLING_CROSS * sum(1 for i, a in enumerate(mine) for b in mine[i + 1:]
                                          for s in segments(a.points) for o in segments(b.points) if crossing(s, o) is not None)
        del page.routes[mark[0]:], page.cells[mark[1]:], page.marks[mark[2]:]
        page.rects.clear(), page.rects.update(mark[3])
        for key in used:
            used[key].clear(), used[key].update(mark[4][key])
        if best_total is None or total < best_total:
            best, best_total = ways, total
    for (edge, diamond), way in zip(branches, best):
        route_forward(page, edge, (True, diamond), corridors, used, (way,))


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
    segs = sorted(segments(pts), key=lambda s: -(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1])))
    others = [s for r in page.routes if r.cid != cid for s in segments(r.points)]
    for p, q in segs:
        flat = abs(p[1] - q[1]) < .5
        beside = [(0, 0)] + ([(0, -h / 2 - 3), (0, h / 2 + 3)] if flat else [(w / 2 + 4, 0), (-w / 2 - 4, 0)])   # on the line, then just beside it
        for (ox, oy), f in [(o, f) for o in beside for f in (0.5, 0.33, 0.67, 0.2, 0.8)]:
            cx, cy = p[0] + (q[0] - p[0]) * f + ox, p[1] + (q[1] - p[1]) * f + oy
            rect = (cx - w / 2, cy - h / 2, w, h)
            if (not any(seg_hits_rect(a, b, rect, 0) for a, b in others) and not any(rects_overlap(rect, m.rect) for m in page.marks)
                    and not any(rects_overlap(rect, page.rects[c]) for c in page.solid)):
                return cx, cy
    p, q = segs[0]
    return (p[0] + q[0]) / 2, (p[1] + q[1]) / 2


def route_flow(page: Page, flow: tuple, corridors: dict, look: dict) -> tuple:
    """Route every forward arrow of a flow page: short arrows first so the long ones route around them, a decision's branches together.

    Args:
        page: the page (steps drawn as solid boxes).
        flow: (flow id, steps, edges from `step_edges`, shapes by step id).
        corridors: {"xs": column gap centres, "ys": reserved run heights}.
        look: the drawing look (branch labels).

    Returns:
        (drawn, corridors, reserved) for `flowmap.uncross.uncross`: cell id -> (edge, diamonds) per arrow drawn, the corridors with the corner
        style, and the sides held back for a decision's branches.
    """
    fid, steps, edges, shapes = flow
    corridors = dict(corridors, rounded=0 if look.get("arrow_corners", "rounded") == "square" else 1)   # rounded corners, as on the Overview
    by_id = {s["id"]: s for s in steps}
    order = {s["id"]: k for k, s in enumerate(steps)}
    fwd = [e for e in edges if "back to" not in e[3]]
    span = {e[0]: order[e[2]] - order[e[1]] for e in fwd}
    # A decision's branches route together, when their longest branch's turn comes: a branch that skips steps then finds the shorter arrows
    # into its target already drawn and takes a port beside them (operator review 2026-10-26: 8 -> 9 rose into 9's bottom because 7's
    # "read-only" branch had taken 9's left first).
    longest = look.get("branch_order", "longest") == "longest"
    group_span = {e[0]: max(span[g[0]] for g in fwd if g[1] == e[1]) if longest and shapes[e[1]] == "decision" else span[e[0]] for e in fwd}
    forward = sorted(fwd, key=lambda e: (group_span[e[0]], span[e[0]]))
    used: dict = {"points": set(), "sides": set(), "branchy": set(), "taken": set()}
    used["diamonds"] = {f"{fid}-s-{s['id']}" for s in steps if shapes[s["id"]] == "decision"}
    for s in steps:   # a decision with branches keeps its top and bottom corners for them: arrows in prefer its left corner
        if shapes[s["id"]] == "decision" and len(s.get("next") or []) > 1:
            used["sides"].update({(f"{fid}-s-{s['id']}", "top"), (f"{fid}-s-{s['id']}", "bottom")})
            used["branchy"].add(f"{fid}-s-{s['id']}")
    reserved = set(used["sides"])
    done: set = set()
    drawn: dict = {}   # cell id -> (edge, diamonds), for the uncrossing pass
    for cid, src, dst, _text, _style in forward:
        if cid in done:
            continue
        group = [e for e in forward if e[1] == src] if shapes[src] == "decision" else []
        if 1 < len(group) <= 3:   # a decision's branches are routed together (best corner per branch)
            branch = [(_edge_of((fid, by_id, order, look), c, s, d), shapes[d] == "decision") for c, s, d, _t, _st in group]
            route_branches(page, branch, corridors, used)
            drawn.update({edge[0]: (edge, (True, diamond)) for edge, diamond in branch})
            done.update(e[0] for e in group)
            continue
        edge = _edge_of((fid, by_id, order, look), cid, src, dst)
        diamonds = (shapes[src] == "decision", shapes[dst] == "decision")
        route_forward(page, edge, diamonds, corridors, used)
        drawn[cid] = (edge, diamonds)
    return drawn, corridors, reserved


def _edge_of(ctx: tuple, cid: str, src: str, dst: str) -> tuple:
    """One arrow as the router takes it: its cell ids, label and colour.

    Args:
        ctx: (flow id, steps by id, step order, look).
        cid: the edge cell id.
        src: the source step id.
        dst: the target step id.

    Returns:
        (cell id, source cell, target cell, label, colour).
    """
    fid, by_id, order, look = ctx
    text, colour = branch_label(by_id[src], dst, order[dst] + 1, look)
    return cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text, colour
