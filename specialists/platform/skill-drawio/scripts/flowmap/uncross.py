"""Uncrossing pass for flow page arrows: the router draws arrows greedily (short ones first), which can leave two crossing that need not. For
each crossing pair both arrows are taken up and drawn again in the other order, each leaving its source the same way, and the result kept only
when the page then has fewer crossings (operator review 2026-10-22, smc-resiliency fw-x86: an arrow coming down from above took the lower entry
of a box and crossed a Yes branch entering it above). `drawing.look.uncross: "off"` keeps the greedy order. Stdlib only.

Imported, not run: `from flowmap.uncross import uncross` with the skill's scripts/ on sys.path; `flowmap.pages` calls it after `route_flow`.
"""

from __future__ import annotations

from drawio.audit import crossing, segments
from drawio.mxfile import Page

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
    gone = (f'<mxCell id="{cid}" ', f'<mxCell id="{cid}-lbl" ')
    page.cells[:] = [c for c in page.cells if not c.startswith(gone)]
    page.routes[:] = [r for r in page.routes if r.cid != cid]
    page.marks[:] = [m for m in page.marks if m.cid != f"{cid}-lbl"]
    page.rects.pop(f"{cid}-lbl", None), page.cell_style.pop(f"{cid}-lbl", None)
    return out_side


def _used(page: Page, reserved: set) -> dict:
    """The points and sides the page's arrows take, as `route_forward` tracks them.

    Args:
        page: the page.
        reserved: sides held back for a decision's branches.

    Returns:
        {"points": end points, "sides": (cell id, side) pairs}.
    """
    used = {"points": set(), "sides": set(reserved)}
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
            snap, count = _snapshot(page), _crossings(page)
            sides = {a: _take_up(page, a), b: _take_up(page, b)}
            for cid in (b, a):   # the other order: the arrow drawn second last time now chooses first
                edge, diamonds = drawn[cid]
                route_forward(page, edge, diamonds, corridors, _used(page, reserved), (sides[cid],))
            if _crossings(page) < count:
                improved = True
            else:
                _restore(page, snap)
        if not improved or _crossings(page) >= before:
            return


def _points(page: Page, cid: str) -> list:
    """A routed arrow's polyline.

    Args:
        page: the page.
        cid: the arrow's cell id.

    Returns:
        Its points.
    """
    return next(r.points for r in page.routes if r.cid == cid)
