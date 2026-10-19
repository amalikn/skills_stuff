#!/usr/bin/env python3
"""Layout audits for routed draw.io drawings: the faults a reviewer must never be shown. Stdlib only.

Promoted from unified-network-controller `scripts/render/flows_drawio.py` (2026-10-19). Each audit encodes an operator complaint about a real
drawing: an arrow through a box, two arrows drawn as one, an arrowhead with no straight run before its box, a label sitting on another arrow,
two labels overlapping, a diagonal run in an orthogonal drawing, two crossing hops so close they merge into a double twist, and a cell whose
layer does not exist. A generator runs page_audit() on every routed page in its tests and asserts every list is empty; each audit has a test
feeding it a deliberately bad drawing, so it is known to be able to fail.

Imported, not run: `from drawio.audit import page_audit, layout_audit` with the skill's scripts/ on sys.path. Geometry is orthogonal: a run is
horizontal or vertical within half a pixel.
"""

from __future__ import annotations

import re

from .mxfile import Page, Point, Rect

#: The straight run an arrowhead needs before the box it enters: thick arrows 24 px, thin ones 22 px (below this the head looks cramped).
HEAD_ROOM = {"thick": 24, "thin": 22}
#: The faults layout_audit() reports, each a list of offending ids.
AUDIT_KEYS = ("box_crossings", "diagonal", "shared_runs", "short_heads", "labels_on_arrows", "label_overlaps", "arc_clashes", "missing_layers")
#: Extra gap two hops need beyond their two arcs: draw.io's jumpSize is a hop's full width, so hops closer than 2 * jump + ARC_GAP merge.
ARC_GAP = 6


def segments(points: list) -> list[tuple[Point, Point]]:
    """The straight runs of a polyline.

    Args:
        points: the polyline.

    Returns:
        (start, end) per run.
    """
    return list(zip(points, points[1:]))


def seg_hits_rect(p: Point, q: Point, rect: Rect, inset: float = 2.0) -> bool:
    """Whether an orthogonal run passes through a rectangle's inside (touching its border does not count).

    Args:
        p: one end.
        q: the other end.
        rect: (x, y, width, height).
        inset: how far inside the border the run must reach to count.

    Returns:
        True when a horizontal or vertical run overlaps the shrunk rectangle; a diagonal run returns False (reported separately).
    """
    (x1, y1), (x2, y2) = p, q
    x0, y0, w, h = rect
    x0, y0, w, h = x0 + inset, y0 + inset, w - 2 * inset, h - 2 * inset
    if abs(y1 - y2) < 0.5:
        return y0 < y1 < y0 + h and max(min(x1, x2), x0) < min(max(x1, x2), x0 + w)
    if abs(x1 - x2) < 0.5:
        return x0 < x1 < x0 + w and max(min(y1, y2), y0) < min(max(y1, y2), y0 + h)
    return False


def collinear(s: tuple[Point, Point], t: tuple[Point, Point]) -> bool:
    """Whether two runs lie on one line (within 3 px) and overlap by more than 2 px: two arrows drawn as one.

    Args:
        s: one run.
        t: the other run.

    Returns:
        True for a shared run.
    """
    (p, q), (u, v) = s, t
    if abs(p[1] - q[1]) < .5 and abs(u[1] - v[1]) < .5 and abs(p[1] - u[1]) < 3:
        return max(min(p[0], q[0]), min(u[0], v[0])) < min(max(p[0], q[0]), max(u[0], v[0])) - 2
    if abs(p[0] - q[0]) < .5 and abs(u[0] - v[0]) < .5 and abs(p[0] - u[0]) < 3:
        return max(min(p[1], q[1]), min(u[1], v[1])) < min(max(p[1], q[1]), max(u[1], v[1])) - 2
    return False


def crossing(s: tuple[Point, Point], t: tuple[Point, Point]) -> float | None:
    """Where a perpendicular run crosses this one, strictly inside both.

    Args:
        s: the run measured along.
        t: the other run.

    Returns:
        The coordinate along `s` (x for a horizontal run, y for a vertical one), or None when they do not cross.
    """
    (p, q), (u, v) = s, t
    if abs(p[1] - q[1]) < .5 and abs(u[0] - v[0]) < .5:
        if min(u[1], v[1]) < p[1] < max(u[1], v[1]) and min(p[0], q[0]) < u[0] < max(p[0], q[0]):
            return u[0]
    elif abs(p[0] - q[0]) < .5 and abs(u[1] - v[1]) < .5:
        if min(u[0], v[0]) < p[0] < max(u[0], v[0]) and min(p[1], q[1]) < u[1] < max(p[1], q[1]):
            return u[1]
    return None


def rects_overlap(a: Rect, b: Rect) -> bool:
    """Whether two rectangles overlap (touching does not count).

    Args:
        a: one (x, y, width, height).
        b: the other.

    Returns:
        True when their insides meet.
    """
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def layout_audit(obstacles: dict, routes: list, marks: list = (), cells: list = (), layers: list = (),
                 head_room: dict | None = None) -> dict[str, list]:
    """Check a routed drawing for every fault in AUDIT_KEYS.

    Args:
        obstacles: {cell id: rect} of boxes no edge may cross (except the ids in each route's `ignore`).
        routes: the drawio.mxfile.Route records.
        marks: the drawio.mxfile.TextMark records (edge labels).
        cells: the page's cell XML, to check every `parent` names a layer that exists.
        layers: the declared layer ids.
        head_room: {klass: least final run}; default HEAD_ROOM.

    Returns:
        {fault: sorted offending ids} for every key in AUDIT_KEYS: an edge crossing a box; a diagonal run; two thick edges sharing a run; a
        last run shorter than its head room; a label on another edge; two labels overlapping; an edge whose hops at two crossings are closer than
        two arcs plus ARC_GAP (a double twist); a parent that is not a declared layer.
    """
    room = HEAD_ROOM if head_room is None else head_room
    out: dict[str, set] = {k: set() for k in AUDIT_KEYS}
    segs = {r.cid: segments(r.points) for r in routes}
    for r in routes:
        for p, q in segs[r.cid]:
            if abs(p[0] - q[0]) > .5 and abs(p[1] - q[1]) > .5:
                out["diagonal"].add(r.cid)
            for rid, rect in obstacles.items():
                if rid not in r.ignore and seg_hits_rect(p, q, rect):
                    out["box_crossings"].add(f"{r.cid} x {rid}")
        (p, q) = segs[r.cid][-1]
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) < room[r.klass] - 0.5:
            out["short_heads"].add(r.cid)
    thick = [r for r in routes if r.klass == "thick"]
    for i, a in enumerate(thick):
        for b in thick[i + 1:]:
            if any(collinear(s, t) for s in segs[a.cid] for t in segs[b.cid]):
                out["shared_runs"].add(f"{a.cid} = {b.cid}")
    for m in marks:
        for r in routes:
            if r.cid != m.owner and any(seg_hits_rect(p, q, m.rect, 0) for p, q in segs[r.cid]):
                out["labels_on_arrows"].add(f"{m.cid} on {r.cid}")
    for i, a in enumerate(marks):
        for b in marks[i + 1:]:
            if rects_overlap(a.rect, b.rect):
                out["label_overlaps"].add(f"{a.cid} / {b.cid}")
    for r in routes:
        if r.jump <= 0:
            continue
        for s in segs[r.cid]:
            hits = sorted(x for o in routes if o.cid != r.cid for t in segs[o.cid] if (x := crossing(s, t)) is not None)
            if any(b - a < 2 * r.jump + ARC_GAP for a, b in zip(hits, hits[1:])):
                out["arc_clashes"].add(r.cid)
    known = {"0", "1", *layers}
    for c in cells:
        out["missing_layers"].update(p for p in re.findall(r'parent="([^"]+)"', c) if p not in known)
    out["missing_layers"].update(x.layer for x in (*routes, *marks) if x.layer not in known)
    return {k: sorted(v) for k, v in out.items()}


def page_audit(page: Page, head_room: dict | None = None) -> dict[str, list]:
    """layout_audit() for a page built with Page.route() and Page.mark().

    Args:
        page: the page.
        head_room: {klass: least final run}; default HEAD_ROOM.

    Returns:
        The audit report.
    """
    return layout_audit({cid: page.rects[cid] for cid in page.solid}, page.routes, page.marks, page.cells, [lid for lid, _ in page.layers],
                        head_room)


def faults(report: dict[str, list]) -> list[str]:
    """The report's faults as one line each, for a command line or a test message.

    Args:
        report: a layout_audit() report.

    Returns:
        "<fault>: <id>" per offending id, in AUDIT_KEYS order; empty when the drawing is clean.
    """
    return [f"{key}: {item}" for key in AUDIT_KEYS for item in report.get(key, [])]
