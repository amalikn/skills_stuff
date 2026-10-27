"""Uncrossing pass for flow page arrows: the router draws arrows greedily (short ones first), which can leave two crossing that need not. For
each crossing pair both arrows are taken up and drawn again in the other order, each leaving its source the same way, and the result kept only
when the page then has fewer crossings (operator review 2026-10-22, smc-resiliency fw-x86: an arrow coming down from above took the lower entry
of a box and crossed a Yes branch entering it above). `drawing.look.uncross: "off"` keeps the greedy order. Stdlib only.

Imported, not run: `from flowmap.uncross import uncross` with the skill's scripts/ on sys.path; `flowmap.pages` calls it after `route_flow`.
"""

from __future__ import annotations

from drawio.audit import crossing, segments
from drawio.mxfile import Page

from .route_costs import _along
from .routing import route_forward


def _side(pt: tuple, rect: tuple) -> str:
    """Which side of a box a route's end point sits on.

    Args:
        pt: the end point (on the box's border or a decision's corner).
        rect: the box.

    Returns:
        "left", "right", "top" or "bottom".
    """
    x, y, w, h = rect
    if abs(pt[0] - x) < .5:
        return "left"
    if abs(pt[0] - x - w) < .5:
        return "right"
    return "top" if abs(pt[1] - y) < .5 else "bottom"


def _alongside(page: Page) -> int:
    """How many pairs of runs from different arrows lie along each other (they read as one arrow; a crossing count does not see them).

    Args:
        page: the page.

    Returns:
        The count of such run pairs.
    """
    runs = [(k, s) for k, r in enumerate(page.routes) for s in segments(r.points)]
    return sum(1 for i, (a, s) in enumerate(runs) for b, t in runs[i + 1:] if a != b and _along(s, t))


def _crossings(page: Page) -> int:
    """How many times two arrows on the page cross.

    Args:
        page: the page.

    Returns:
        The count of crossing run pairs between different routes.
    """
    runs = [(k, s) for k, r in enumerate(page.routes) for s in segments(r.points)]
    return sum(1 for i, (a, s) in enumerate(runs) for b, t in runs[i + 1:] if a != b and crossing(s, t) is not None)


def _snapshot(page: Page) -> tuple:
    """Copy what routing changes on a page, so a trial can be undone.

    Args:
        page: the page.

    Returns:
        (cells, routes, marks, rects, cell styles).
    """
    return list(page.cells), list(page.routes), list(page.marks), dict(page.rects), dict(page.cell_style)


def _restore(page: Page, snap: tuple) -> None:
    """Put a page back as `_snapshot` copied it.

    Args:
        page: the page.
        snap: what `_snapshot` returned.
    """
    page.cells[:], page.routes[:], page.marks[:] = snap[0], snap[1], snap[2]
    page.rects.clear(), page.rects.update(snap[3])
    page.cell_style.clear(), page.cell_style.update(snap[4])


def _take_up(page: Page, cid: str) -> str:
    """Remove one routed arrow and its label from the page.

    Args:
        page: the page.
        cid: the arrow's cell id.

    Returns:
        The side the arrow left its source by (kept when it is drawn again).
    """
    route = next(r for r in page.routes if r.cid == cid)
    out_side = _side(route.points[0], page.rects[route.src])
    gone = tuple(f'<{tag} id="{c}" ' for tag in ("mxCell", "UserObject") for c in (cid, f"{cid}-lbl"))   # a cell with a tooltip is a UserObject
    page.cells[:] = [c for c in page.cells if not c.startswith(gone)]
    page.routes[:] = [r for r in page.routes if r.cid != cid]
    page.marks[:] = [m for m in page.marks if m.cid != f"{cid}-lbl"]
    page.rects.pop(f"{cid}-lbl", None), page.cell_style.pop(f"{cid}-lbl", None)
    return out_side


def _used(page: Page, reserved: set, diamonds: set) -> dict:
    """The points and sides the page's arrows take, as `route_forward` tracks them.

    Args:
        page: the page.
        reserved: sides held back for a decision's branches.
        diamonds: the decisions' cell ids, whose corners two arrows must not share (`routing.cost`).

    Returns:
        {"points": end points, "sides": (cell id, side) pairs, "diamonds": the decisions}.
    """
    used = {"points": set(), "sides": set(reserved), "diamonds": diamonds}
    for r in page.routes:
        used["points"].update((round(p[0]), round(p[1])) for p in (r.points[0], r.points[-1]))
        used["sides"].update({(r.src, _side(r.points[0], page.rects[r.src])), (r.dst, _side(r.points[-1], page.rects[r.dst]))})
    return used


def uncross(page: Page, drawn: dict, corridors: dict, reserved: set, passes: int = 3) -> None:
    """Repair what the greedy order leaves: for two arrows that cross, take both up and draw them again in the other order (each leaving its
    source the same way), keeping the result only when the page then has fewer crossings (operator review 2026-10-22: an arrow coming down
    from above took the lower entry and crossed a Yes branch entering the same box above it).

    Args:
        page: the page, every forward arrow routed.
        drawn: cell id -> (edge, diamonds) as `route_forward` takes them.
        corridors: as for `route_forward`.
        reserved: sides held back for a decision's branches.
        passes: rounds over the crossing pairs (each round only ever lowers the count).
    """
    # Every decision an arrow starts or ends at, so a redrawn arrow keeps off a corner another arrow holds.
    diamonds = {end for edge, flags in drawn.values() for end, is_diamond in zip(edge[1:3], flags) if is_diamond}
    for _ in range(passes):
        before, improved = _crossings(page), False
        if not before:
            return
        ids = [r.cid for r in page.routes if r.cid in drawn]
        pairs = [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]
                 if any(crossing(s, t) is not None for s in segments(_points(page, a)) for t in segments(_points(page, b)))]
        for a, b in pairs:
            if a not in drawn or b not in drawn or not any(r.cid == a for r in page.routes) or not any(r.cid == b for r in page.routes):
                continue
            if _redraw_pair(page, (a, b), drawn, corridors, (reserved, diamonds)):
                improved = True
        if not improved or _crossings(page) >= before:
            return


#: The sides an arrow may leave its source by (routing._ports).
EXITS = ("right", "top", "bottom")
#: How many of the first-drawn arrow's paths the last repair tier tries.
CHOICES = 6


def _redraw_pair(page: Page, pair: tuple, drawn: dict, corridors: dict, held: tuple) -> bool:
    """Take up two crossing arrows and draw them again in the other order, first leaving their sources as before; when that crosses as much,
    every other pair of exit sides is tried (operator, 2026-10-27, option b: smc-resiliency fw-x86 crossed once after two-line labels narrowed
    a gap, and the same sides could not avoid it). The best result is kept only when the page then has fewer crossings, no more shared
    decision corners and no more runs lying along another arrow's (smc_change Apply, same day: a crossing traded for 10 and 12 sharing a
    run); otherwise the page is restored.

    Args:
        page: the page, every forward arrow routed.
        pair: the two crossing arrows' cell ids (a drawn before b).
        drawn: cell id -> (edge, diamonds) as `route_forward` takes them.
        corridors: as for `route_forward`.
        held: (sides reserved for decisions' branches, the decisions' cell ids).

    Returns:
        True when the pair was redrawn with fewer crossings.
    """
    a, b = pair
    reserved, diamonds = held
    snap, count, shared, along = _snapshot(page), _crossings(page), len(_shared_corners(page, drawn, diamonds)), _alongside(page)
    sides = {a: _take_up(page, a), b: _take_up(page, b)}
    bare = _snapshot(page)
    # Same sides first (the old repair), then every other pair of exit sides, then the same sides choosing paths by fewest crossings rather
    # than cost: the cost rates a crossing (30) below a flat run into the target's top (150), so a cost-ranked redraw can keep a crossing
    # a slightly longer path avoids (smc-resiliency fw-x86, 2026-10-27, operator: "fix the skill").
    trials = [(sides[a], sides[b], False)] + [(sa, sb, False) for sa in EXITS for sb in EXITS if (sa, sb) != (sides[a], sides[b])]
    # Ranked by crossings, the arrow drawn first takes each of its CHOICES best paths in turn, so it can step aside for the second.
    trials += [(sides[a], sides[b], pick) for pick in range(CHOICES)]
    best = None
    for k, (side_a, side_b, pick) in enumerate(trials):
        _restore(page, bare)
        spent = 0.0
        fewest = pick is not False
        for cid, side, rank in ((b, side_b, pick if fewest else 0), (a, side_a, 0)):   # the other order: last time's second arrow first
            edge, flags = drawn[cid]
            spent = max(spent, route_forward(page, edge, flags, corridors, _used(page, reserved, diamonds), (side,), k > 0, fewest, rank))
        if spent >= 1e6:   # a side the arrow cannot leave by: nothing drawn, not a result
            continue
        after = _crossings(page)
        if after < count and _alongside(page) > along:   # the pair is clear but now runs along a third arrow: let that one step aside
            _step_aside(page, pair, drawn, corridors, held)
            after = _crossings(page)
        if after < count and len(_shared_corners(page, drawn, diamonds)) <= shared and _alongside(page) <= along and (best is None or after < best[0]):
            best = (after, _snapshot(page))
            if k == 0:   # the same sides already help: keep the old repair's choice
                break
    _restore(page, best[1] if best else snap)
    return best is not None


def _step_aside(page: Page, pair: tuple, drawn: dict, corridors: dict, held: tuple) -> None:
    """Redraw each other arrow that lies along a run of the redrawn pair, by fewest overlaps and crossings from any exit side (smc-resiliency
    fw-x86, 2026-10-27: clearing 3 -> 5 from 4 -> 6 made 4 -> 6 share its last run into 6 with 5 -> 6, which had to enter 6 from the top
    instead). The caller judges the whole page afterwards and restores it when the result is no better.

    Args:
        page: the page, the pair just redrawn.
        pair: the pair's cell ids.
        drawn: cell id -> (edge, diamonds) as `route_forward` takes them.
        corridors: as for `route_forward`.
        held: (sides reserved for decisions' branches, the decisions' cell ids).
    """
    reserved, diamonds = held
    mine = [s for r in page.routes if r.cid in pair for s in segments(r.points)]
    others = [r.cid for r in page.routes if r.cid in drawn and r.cid not in pair
              and any(_along(s, t) for s in segments(r.points) for t in mine)]
    for cid in others:
        _take_up(page, cid)
        edge, flags = drawn[cid]
        route_forward(page, edge, flags, corridors, _used(page, reserved, diamonds), None, False, True)


def _shared_corners(page: Page, drawn: dict, diamonds: set) -> list:
    """Pairs of arrows that meet at one decision corner (a diamond has a single point per corner, so they merge for their last run).

    Args:
        page: the page.
        drawn: cell id -> (edge, diamonds) as `route_forward` takes them.
        diamonds: the decisions' cell ids.

    Returns:
        (first, second) arrow cell id pairs, in drawing order.
    """
    ends: dict = {}
    for r in page.routes:
        if r.cid not in drawn:
            continue
        for cell, pt in ((r.src, r.points[0]), (r.dst, r.points[-1])):
            if cell in diamonds:
                ends.setdefault((cell, round(pt[0]), round(pt[1])), []).append(r.cid)
    return [(ids[i], ids[j]) for ids in ends.values() for i in range(len(ids)) for j in range(i + 1, len(ids))]


def unshare(page: Page, drawn: dict, corridors: dict, reserved: set) -> None:
    """Repair a decision corner two arrows share: the greedy order lets the first arrow take the corner a later one cannot avoid (its only free
    exit reaches no other), so both are taken up and drawn again in the other order, each leaving its source the same way; the result is kept
    only when that pair no longer shares and the page has no more crossings and no more shared corners (operator review 2026-10-27, smc_change
    PHP step page: 12 -> 13 took 13's left corner, and the "no" branch from 11, leaving by its bottom, then had to merge into it).

    Args:
        page: the page, every forward arrow routed.
        drawn: cell id -> (edge, diamonds) as `route_forward` takes them.
        corridors: as for `route_forward`.
        reserved: sides held back for a decision's branches.
    """
    diamonds = {end for edge, flags in drawn.values() for end, is_diamond in zip(edge[1:3], flags) if is_diamond}
    for a, b in _shared_corners(page, drawn, diamonds):
        if not any(r.cid == a for r in page.routes) or not any(r.cid == b for r in page.routes):
            continue
        snap, count, shared, along = _snapshot(page), _crossings(page), len(_shared_corners(page, drawn, diamonds)), _alongside(page)
        sides = {a: _take_up(page, a), b: _take_up(page, b)}
        for cid in (b, a):
            edge, flags = drawn[cid]
            route_forward(page, edge, flags, corridors, _used(page, reserved, diamonds), (sides[cid],))
        after = _shared_corners(page, drawn, diamonds)
        if (a, b) in after or (b, a) in after or len(after) >= shared or _crossings(page) > count or _alongside(page) > along:
            _restore(page, snap)


def _points(page: Page, cid: str) -> list:
    """A routed arrow's polyline.

    Args:
        page: the page.
        cid: the arrow's cell id.

    Returns:
        Its points.
    """
    return next(r.points for r in page.routes if r.cid == cid)
