"""Orthogonal routing primitives for generated draw.io drawings: tracks in channels, ports spread along an edge, interval tracks, crossing counts,
label spots clear of other arrows, and the untwist pass that keeps crossing hops apart. Stdlib only.

Promoted from unified-network-controller `scripts/render/flows_drawio.py` (2026-10-19), where the flow-map overview and End-to-end pages use
them. Every function is pure: it takes polylines and numbers and returns positions, so a layout that uses them stays deterministic.

Imported, not run: `from drawio import route` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from .audit import rects_overlap, segments
from .mxfile import Point, Rect


def near(pt: Point, full: list, gap: float = 24) -> bool:
    """Whether a point lies within `gap` of an orthogonal polyline (a label there would sit on that arrow).

    Args:
        pt: the point.
        full: the polyline.
        gap: the clearance.

    Returns:
        True when too close.
    """
    for u, v in segments(full):
        if abs(u[1] - v[1]) < .5 and min(u[0], v[0]) - gap < pt[0] < max(u[0], v[0]) + gap and abs(pt[1] - u[1]) < gap:
            return True
        if abs(u[0] - v[0]) < .5 and min(u[1], v[1]) - gap < pt[1] < max(u[1], v[1]) + gap and abs(pt[0] - u[0]) < gap:
            return True
    return False


def count_spot(full: list, others: list, placed: list = ()) -> Point:
    """Where an arrow's count label goes: on its longest run (then the next), at the first point clear of every other arrow and placed label.

    Args:
        full: the arrow's polyline.
        others: the other arrows' polylines.
        placed: the labels already placed (40 x 30 rects), which a new one must not overlap.

    Returns:
        The label centre (the longest run's middle when no clear point exists; the layout audit then reports it).
    """
    segs = sorted(segments(full), key=lambda sg: -(abs(sg[0][0] - sg[1][0]) + abs(sg[0][1] - sg[1][1])))
    for p1, p2 in segs:
        if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) < 60:
            continue
        for fr in (0.5, 0.35, 0.65, 0.25, 0.75):
            cand = (p1[0] + (p2[0] - p1[0]) * fr, p1[1] + (p2[1] - p1[1]) * fr)
            rect = (cand[0] - 20, cand[1] - 15, 40, 30)
            if not any(near(cand, o) for o in others) and not any(rects_overlap(rect, q) for q in placed):
                return cand
    p1, p2 = segs[0]
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def spread(users: list, side: str) -> dict:
    """Points along one box edge for the arrows using it, ordered by where each arrow's other end is (port spreading).

    Top and bottom edges interleave (top: slot i+1, bottom: slot i+2 of n+2), so a stub rising from a box below never meets one dropping from a
    box above at the same x.

    Args:
        users: (sort position, arrow id, end) per arrow on the edge.
        side: "top", "bottom", "left" or "right".

    Returns:
        {(arrow id, end): fraction along the edge}.
    """
    users = sorted(users)
    shift = {"top": 1, "bottom": 2}.get(side, 1)
    n = len(users) + (2 if side in ("top", "bottom") else 1)
    return {(u[1], u[2]): (i + shift) / n for i, u in enumerate(users)}


def edge_point(rect: Rect, side: str, fr: float) -> Point:
    """A point on a rectangle's edge.

    Args:
        rect: (x, y, width, height).
        side: the edge.
        fr: the fraction along it.

    Returns:
        The point.
    """
    x0, y0, w, h = rect
    return {"top": (x0 + w * fr, y0), "bottom": (x0 + w * fr, y0 + h), "left": (x0, y0 + h * fr), "right": (x0 + w, y0 + h * fr)}[side]


def track(users: list, key: object, centre: float, sp: float, last: bool = False) -> float:
    """A track's position in a channel: tracks are `sp` apart, centred on the channel's middle.

    Args:
        users: the arrow ids using the channel, in order (an arrow may appear twice).
        key: this arrow's id.
        centre: the channel's middle.
        sp: the track spacing.
        last: take the arrow's last place in the list rather than its first.

    Returns:
        The track's coordinate.
    """
    places = [i for i, u in enumerate(users) if u == key]
    k = places[-1] if last else places[0]
    return centre + (k - (len(users) - 1) / 2) * sp


def oriented(points: list) -> tuple[list, list]:
    """A polyline's runs split by direction, for fast crossing counts.

    Args:
        points: an orthogonal polyline.

    Returns:
        (horizontal runs as (y, x low, x high), vertical runs as (x, y low, y high)).
    """
    hs, vs = [], []
    for (x1, y1), (x2, y2) in segments(points):
        if abs(y1 - y2) < .5:
            hs.append((y1, min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) < .5:
            vs.append((x1, min(y1, y2), max(y1, y2)))
    return hs, vs


def count_crossings(a: tuple, b: tuple) -> int:
    """How many times two orthogonal polylines cross (strictly inside both runs), from their oriented() runs.

    Args:
        a: one polyline's runs.
        b: the other's.

    Returns:
        The count.
    """
    n = 0
    for hs, vs in ((a[0], b[1]), (b[0], a[1])):
        for y, x0, x1 in hs:
            for x, y0, y1 in vs:
                if x0 < x < x1 and y0 < y < y1:
                    n += 1
    return n


def interval_tracks(spans: list, sep: float) -> dict:
    """Give intervals tracks (interval colouring): two share a track only when `sep` or more apart (left-edge greedy, deterministic).

    Args:
        spans: (low, high, key) per interval.
        sep: the least separation on one track.

    Returns:
        {key: track index}.
    """
    ends: list[float] = []
    out = {}
    for lo, hi, key in sorted(spans):
        for t, end in enumerate(ends):
            if end + sep <= lo:
                ends[t] = hi
                out[key] = t
                break
        else:
            out[key] = len(ends)
            ends.append(hi)
    return out


def _bounds(routes: dict, ends: dict, limit: float, box_w: float) -> tuple[dict, dict]:
    """Where each vertical run starts and how far untwist() may move it.

    Args:
        routes: {key: polyline}.
        ends: {key: (source box left x, target box left x)}.
        limit: the furthest a run may move.
        box_w: the boxes' width (a port stays at least 12 px inside its box's corners).

    Returns:
        ({(key, run index): start x}, {(key, run index): (low x, high x)}).
    """
    start, bound = {}, {}
    for key, pts in routes.items():
        for k in range(len(pts) - 1):
            if abs(pts[k][0] - pts[k + 1][0]) < .5:
                x = pts[k][0]
                lo, hi = x - limit, x + limit
                if k in (0, len(pts) - 2):   # a box's port: stay on its edge
                    left = ends[key][0] if k == 0 else ends[key][1]
                    lo, hi = max(lo, left + 12), min(hi, left + box_w - 12)
                start[(key, k)], bound[(key, k)] = x, (lo, hi)
    return start, bound


def _untwist_once(routes: dict, need: float, start: dict, bound: dict) -> bool:
    """Move the first vertical run found too close to its neighbour along some horizontal run.

    Args:
        routes: {key: polyline}, changed in place.
        need: the least gap between two crossings on one run.
        start: the movable runs (from _bounds).
        bound: each movable run's range.

    Returns:
        True when a run moved.
    """
    verticals = [(key, k, pts[k][0], min(pts[k][1], pts[k + 1][1]), max(pts[k][1], pts[k + 1][1]))
                 for key, pts in routes.items() for k in range(len(pts) - 1) if abs(pts[k][0] - pts[k + 1][0]) < .5]
    for key, pts in routes.items():
        for (x1, y1), (x2, y2) in segments(pts):
            if abs(y1 - y2) > .5:
                continue
            hits = sorted((v[2], v[0], v[1]) for v in verticals if v[0] != key and min(x1, x2) < v[2] < max(x1, x2) and v[3] < y1 < v[4])
            for (xa, ka, ia), (xb, kb, ib) in zip(hits, hits[1:]):
                if xb - xa >= need:
                    continue
                for kk, ii, sign in ((kb, ib, 1), (ka, ia, -1)):
                    if (kk, ii) in start:
                        px = routes[kk][ii][0] + sign * (need - (xb - xa) + 1)
                        if bound[(kk, ii)][0] <= px <= bound[(kk, ii)][1]:
                            routes[kk][ii] = (px, routes[kk][ii][1])
                            routes[kk][ii + 1] = (px, routes[kk][ii + 1][1])
                            return True
    return False


def untwist(routes: dict, jump: float, ends: dict, box_w: float, limit: float = 16.0) -> None:
    """Move vertical runs sideways until no horizontal run hops two crossings closer than 2 * jump + 6 (a double twist).

    A run is moved away from the run it crowds, at most `limit` px from where it started; a run leaving or entering a box slides its port along
    that box's edge, at least 12 px inside the corners. At most 60 moves.

    Args:
        routes: {key: polyline}, changed in place.
        jump: the hop size (draw.io jumpSize).
        ends: {key: (source box left x, target box left x)}.
        box_w: the boxes' width.
        limit: the furthest a run may move.
    """
    need = 2 * jump + 6
    start, bound = _bounds(routes, ends, limit, box_w)
    for _ in range(60):
        if not _untwist_once(routes, need, start, bound):
            return


def gap_crossings(seq: list, span: dict) -> int:
    """How many times the thin arrows in one row gap cross there, for one top-to-bottom order of their horizontal runs.

    A run enters the gap from above at its start x, runs across on its track and leaves downwards at its end x. So run i's horizontal crosses
    run j's way in when i's track is above j's and j's start x lies strictly inside i's run, and j's way out when i's track is below j's and
    j's end x lies strictly inside it. A straight drop (start x equal to end x) spans the whole gap and is crossed by any run around its x.

    Args:
        seq: the runs' keys, top track first.
        span: {key: (start x, end x)}.

    Returns:
        The number of crossings in the gap.
    """
    n = 0
    for a, i in enumerate(seq):
        lo, hi = sorted(span[i])
        for b, j in enumerate(seq):
            if i == j:
                continue
            x0, x1 = span[j]
            n += (a < b and lo < x0 < hi) + (a > b and lo < x1 < hi)
    return n


def gap_order(seq: list, span: dict) -> list:
    """The runs of one row gap reordered by neighbour swaps that each strictly lower gap_crossings; the given order when none does.

    Args:
        seq: the runs' keys in their default order, top track first.
        span: {key: (start x, end x)}.

    Returns:
        The new order, top track first.
    """
    seq, best = list(seq), gap_crossings(seq, span)
    better = True
    while better and best:
        better = False
        for k in range(len(seq) - 1):
            trial = seq[:k] + [seq[k + 1], seq[k]] + seq[k + 2:]
            cost = gap_crossings(trial, span)
            if cost < best:
                seq, best, better = trial, cost, True
    return seq


def gap_ranks(runs: list) -> list:
    """Each horizontal run's track number in its row gap (1 = top): chain order per gap, improved by gap_order.

    Args:
        runs: [(row, start x, end x)], one per run, in chain order.

    Returns:
        The track numbers, one per run, in the same order.
    """
    gaps: dict[int, list] = {}
    for i, (row, _, _) in enumerate(runs):
        gaps.setdefault(row, []).append(i)
    rank = [0] * len(runs)
    for idx in gaps.values():
        for n, i in enumerate(gap_order(idx, {i: (runs[i][1], runs[i][2]) for i in idx})):
            rank[i] = n + 1
    return rank
