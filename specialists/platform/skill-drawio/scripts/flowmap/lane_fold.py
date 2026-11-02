"""A flow page folded inside its lanes (`layout: {fold: lane, fold_after: N}`; operator, 2026-11-02: "the fold should happen within the same lane by expanding
it vertically"). A run of more than N steps by one actor snakes back and forth inside that actor's lane, which grows taller; every lane appears once and
the page stays narrow. Notes keep to their step's column, stacked under the lanes. Only a flow with no branches folds this way; any other keeps its normal
page. Stdlib only.

Imported, not run: `from flowmap.lane_fold import lane_fold_page` with the skill's scripts/ on sys.path; flowmap.pages calls it.
"""

from __future__ import annotations

from drawio.mxfile import Page

from .flow_geometry import LANE_HEAD_W, col_gap
from .lanes import LANE_H, draw_lanes
from .model import GAP, MARGIN, step_targets
from .routing import JUMP, PLAIN, STYLE, draw_label
from .shapes import lane_shape, shape_legend

#: Least space between columns, for an arrow's number; the gap between a lane's rows; how far below a box an arrow runs when it leaves by the bottom.
LEAST_GAP, ROW_ROOM, UNDER = 70, 56, 14


def foldable(steps: list[dict]) -> bool:
    """Whether a flow is a straight line, which is what this layout draws.

    Args:
        steps: the flow's steps.

    Returns:
        True when every step leads only to the next.
    """
    return all(step_targets(steps, k) == ([steps[k + 1]["id"]] if k + 1 < len(steps) else []) for k in range(len(steps)))


def snake(steps: list[dict], after: int) -> tuple[dict, dict]:
    """Each step's place: a short run takes a column each, a long run snakes over `after` columns, every second row running back.

    Args:
        steps: the flow's steps.
        after: columns a long run may use.

    Returns:
        ({step index: (column, row in its lane)}, {actor: rows used}).
    """
    place, rows, col, k = {}, {}, 0, 0
    while k < len(steps):
        end = k
        while end < len(steps) and steps[end]["actor"] == steps[k]["actor"]:
            end += 1
        span = end - k
        for i in range(span):
            row, across = (i // after, i % after) if span > after else (0, i)
            place[k + i] = (col + (after - 1 - across if row % 2 else across), row)
        actor = steps[k]["actor"]
        rows[actor] = max(rows.get(actor, 1), (span - 1) // after + 1 if span > after else 1)
        col += min(span, after)
        k = end
    return place, rows


def _layout(steps: list[dict], place: dict, box_w: dict, box_h: dict, gap: float) -> tuple[dict, dict, dict]:
    """Column left edges and widths, and each lane's row heights.

    Args:
        steps: the flow's steps.
        place: from snake().
        box_w: step box widths.
        box_h: step box heights.
        gap: the space between columns.

    Returns:
        ({column: left}, {column: width}, {(actor, row): height}).
    """
    widths: dict = {}
    heights: dict = {}
    for k, (col, row) in place.items():
        s = steps[k]
        widths[col] = max(widths.get(col, 0), box_w[s["id"]])
        key = (s["actor"], row)
        heights[key] = max(heights.get(key, 0), box_h[s["id"]] + 28)
    lefts, x = {}, MARGIN + LANE_HEAD_W + GAP
    for col in sorted(widths):
        lefts[col] = x
        x += widths[col] + gap
    return lefts, widths, heights


def arrow(a: tuple, b: tuple, gap: float, back: bool) -> list:
    """The polyline between two boxes.

    Args:
        a: the source (x, y, width, height).
        b: the target.
        gap: the space between columns.
        back: the source sits on a row running back, so the way right is full of boxes.

    Returns:
        The points.
    """
    (ax, ay, aw, ah), (bx, by, bw, bh) = a, b
    amid, bmid = ay + ah / 2, by + bh / 2
    if abs(ax - bx) < 1 and by > ay:   # down at the end of a row
        return [(ax + aw / 2, ay + ah), (bx + bw / 2, by)]
    if abs(amid - bmid) < 1:   # along a row, either way
        return [(ax + aw, amid), (bx, bmid)] if bx > ax else [(ax, amid), (bx + bw, bmid)]
    turn = bx - gap / 2
    if back:
        low = ay + ah + UNDER
        return [(ax + aw / 2, ay + ah), (ax + aw / 2, low), (turn, low), (turn, bmid), (bx, bmid)]
    return [(ax + aw, amid), (turn, amid), (turn, bmid), (bx, bmid)]


def lane_fold_page(page: Page, ctx: tuple, sized: tuple, how: tuple) -> Page:
    """A flow page folded inside its lanes.

    Args:
        page: the empty page (arrow hover texts and tags already set).
        ctx: (flow, components by id, flow number, profile).
        sized: (shapes, texts, box widths, box heights, edges).
        how: (flowmap.pages' step drawer, its header drawer, columns a long run may use).

    Returns:
        The page.
    """
    flow, comps, number, profile = ctx
    shapes, texts, box_w, box_h, edges = sized
    draw_step, draw_header, after = how
    fid, steps = flow["id"], flow["steps"]
    gap = max(col_gap(profile.look), LEAST_GAP)
    place, rows = snake(steps, after)
    lefts, widths, heights = _layout(steps, place, box_w, box_h, gap)
    last = max(lefts)
    width = lefts[last] + widths[last] + GAP - MARGIN
    top = MARGIN + draw_header(page, flow, comps, number, width) + GAP
    lanes = list(dict.fromkeys(s["actor"] for s in steps))
    room = {(li, "bottom"): sum(heights.get((actor, r), 0) + ROW_ROOM for r in range(1, rows[actor])) for li, actor in enumerate(lanes)}
    _names, lane_y, lane_h = draw_lanes(page, flow, comps, profile, top, box_h, box_w, room, width, lanes)
    notes_y = {col: top + sum(lane_h) + GAP for col in lefts}
    for k, (col, row) in sorted(place.items()):
        s = steps[k]
        li = lanes.index(s["actor"])
        first = max(LANE_H, heights.get((s["actor"], 0), 0))
        y = lane_y[li] + (0 if row == 0 else first + sum(heights.get((s["actor"], r), 0) + ROW_ROOM for r in range(1, row)) + ROW_ROOM)
        h = first if row == 0 else heights[(s["actor"], row)]
        ys, hs = list(lane_y), list(lane_h)
        ys[li], hs[li] = y, h
        left = lefts[col] + (widths[col] - box_w[s["id"]]) / 2
        nh = draw_step(page, flow, k, comps, profile, (lanes, ys, hs, box_h, texts, notes_y[col], shapes, {k: left}, {}, box_w), number)
        notes_y[col] += nh + (GAP / 2 if nh else 0)
    index = {s["id"]: k for k, s in enumerate(steps)}
    for cid, a, b, _text, _style in edges:
        src, dst = f"{fid}-s-{a}", f"{fid}-s-{b}"
        back = place[index[a]][1] % 2 == 1
        pts = arrow(page.rects[src], page.rects[dst], gap, back)
        page.route(cid, src, dst, pts, STYLE.format(colour=PLAIN, rounded=1), klass="thin", jump=JUMP)
        draw_label(page, cid, pts, str(index[b] + 1), PLAIN)
    used = list(dict.fromkeys(list(shapes.values()) + [lane_shape(comps[c], profile.kind_shapes) for c in lanes]))
    shape_legend(page, used, MARGIN, max(notes_y.values()) + GAP, fid)
    return page
