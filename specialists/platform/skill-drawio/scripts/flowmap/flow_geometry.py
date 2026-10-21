"""Flow page geometry: step box widths by shape, column positions, and the route of an arrow back to an earlier step. Moved out of
flowmap.pages on 2026-10-21 to keep that module within its size budget; behaviour unchanged. Stdlib only.

Imported, not run: `from flowmap.flow_geometry import column_lefts` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .model import GAP, MARGIN

#: Flow page geometry shared with flowmap.pages: lane heading width, column width and step box width.
LANE_HEAD_W, COL_W, STEP_W = 190, 270, 220
#: A decision's diamond is wider, in a wider column, so it grows sideways rather than tall (operator review, 2026-10-21).
DEC_STEP_W = 380


def step_width(shape: str, look: dict | None = None) -> int:
    """A step box's width for its shape.

    Args:
        shape: a flowmap.shapes key.
        look: the profile's look (decision_width, step_width); absent keys use DEC_STEP_W and STEP_W.

    Returns:
        The decision width for a decision, else the step width.
    """
    look = look or {}
    return int(look.get("decision_width", DEC_STEP_W)) if shape == "decision" else int(look.get("step_width", STEP_W))


def col_gap(look: dict | None = None) -> float:
    """The space between step columns (`drawing.look.column_gap`).

    Args:
        look: the profile's look; absent, the old fixed gap.

    Returns:
        The gap in pixels.
    """
    return float((look or {}).get("column_gap", COL_W - STEP_W))


def column_lefts(widths: list[int], gap: float = COL_W - STEP_W) -> list[float]:
    """Each step column's left edge, columns as wide as their step plus the gap.

    Args:
        widths: each step box's width, in step order.
        gap: the space between columns (`col_gap`).

    Returns:
        The x of each column's left edge.
    """
    lefts, x = [], MARGIN + LANE_HEAD_W + GAP
    for w in widths:
        lefts.append(x)
        x += w + gap
    return lefts


def plan_runs(steps: list[dict], pairs: list[tuple[str, str]]) -> dict:
    """Which lane edge each engine-routed forward arrow (one that skips a column) runs along, and its track there, before anything is drawn,
    so each lane can reserve the room (operator review 2026-10-21: two runs overlapped and a run sat 6 px from the lane line).

    Args:
        steps: the flow's steps in order.
        pairs: (source step id, target step id) of the forward arrows.

    Returns:
        {"track": {(src, dst): n}, "count": {(lane index, "top" or "bottom"): runs}}.
    """
    order = {s["id"]: k for k, s in enumerate(steps)}
    actors = list(dict.fromkeys(s["actor"] for s in steps))
    lane = {s["id"]: actors.index(s["actor"]) for s in steps}
    track, count = {}, {}
    for a, b in pairs:
        if order[b] <= order[a] + 1:
            continue
        key = (lane[b], "bottom" if lane[b] < lane[a] else "top")
        track[(a, b)] = count.get(key, 0)
        count[key] = track[(a, b)] + 1
    return {"track": track, "count": count}


def reserve(runs: int, track_gap: float) -> float:
    """The room a lane keeps along one edge for its planned runs.

    Args:
        runs: the runs planned on that edge.
        track_gap: the spacing between runs.

    Returns:
        Pixels; 0 when no run is planned.
    """
    return runs * track_gap + 10 if runs else 0.0


def _clear(page: Page, points: list, skip: set) -> bool:
    """True when no step box (cell id containing "-s-") other than those in `skip` lies across the polyline.

    Args:
        page: the page.
        points: the polyline (horizontal and vertical runs only).
        skip: the source and target cell ids.

    Returns:
        Whether the path crosses no other step.
    """
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        lo_x, hi_x, lo_y, hi_y = min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)
        for cid, (x, y, w, h) in page.rects.items():
            if "-s-" in cid and cid not in skip and lo_x < x + w and hi_x > x and lo_y < y + h and hi_y > y:
                return False
    return True


def skip_arrow(page: Page, edge: tuple, lanes: tuple, gap: float, track: int = 0, track_gap: float = 12) -> bool:
    """A forward arrow that skips a column, routed by the engine (operator review, 2026-10-21: draw.io's own route ran an arrow through the
    step in between). In one lane it leaves the source's top, runs along the top of the lane and drops into the target's top (or, when that is
    blocked, the same along the bottom). Into another lane it leaves the source's right side, turns down or up in the gap after the source's
    column, runs along the edge of the target's lane and enters the target's top (lane below) or bottom (lane above). Every run is checked clear
    of other steps first.

    Args:
        page: the page (the steps and lanes are drawn).
        edge: (cell id, source cell, target cell, label, style); the style's colours are kept, its ports replaced.
        lanes: ((source lane top, source lane height), (target lane top, target lane height)).
        gap: the horizontal gap between step columns.
        track: this arrow's run on its lane edge (from `plan_runs`).
        track_gap: the spacing between runs (`drawing.look.track_gap`).

    Returns:
        True when the arrow was drawn; False leaves it to draw.io (no clear engine route found).
    """
    cid, src, dst, text, _style = edge
    sx, sy, sw, sh = page.rects[src]
    dx, dy, dw, dh = page.rects[dst]
    (s_top, s_h), (d_top, d_h) = lanes
    off = 10 + track_gap * track
    if s_top == d_top:   # same lane: over the top, else under the bottom
        tries = [[(sx + sw / 2, sy), (sx + sw / 2, s_top + off), (dx + dw / 2, s_top + off), (dx + dw / 2, dy)],
                 [(sx + sw / 2, sy + sh), (sx + sw / 2, s_top + s_h - off), (dx + dw / 2, s_top + s_h - off), (dx + dw / 2, dy + dh)]]
    else:
        turn = sx + sw + gap / 2
        run_y, end_y = (d_top + off, dy) if d_top > s_top else (d_top + d_h - off, dy + dh)
        tries = [[(sx + sw, sy + sh / 2), (turn, sy + sh / 2), (turn, run_y), (dx + dw / 2, run_y), (dx + dw / 2, end_y)]]
    for pts in tries:
        if _clear(page, pts, {src, dst}):
            page.route(cid, src, dst, pts, "edgeStyle=none;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#000000;", klass="thin")
            mid = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
            page.mark(f"{cid}-lbl", label(f"**{text}**"), (mid[0][0] + mid[1][0]) / 2, (mid[0][1] + mid[1][1]) / 2, 24, 22,
                      "text;html=1;align=center;verticalAlign=middle;fontSize=16;fontStyle=1;labelBackgroundColor=#ffffff;", cid)
            return True
    return False

def back_arrow(page: Page, edge: tuple, band: float, mode: str = "short-first") -> float:
    """An arrow back to an earlier step, routed by the engine rather than draw.io (operator review, 2026-10-21: draw.io's own route crossed
    many boxes). First choice, the short way: out of the source's left side, along its own lane, into the target's top right (or bottom right
    when the target's lane is higher). When a step lies on that path, the long way: down in the source's column, along a band between the
    lanes and the notes, up into the target; a column holds one step, so those vertical runs cross nothing.

    Args:
        page: the page.
        edge: (cell id, source cell, target cell, label, style with exitX and entryX).
        band: the y of the band a long-way arrow runs along.
        mode: "short-first" tries the short way, "below-lanes" always takes the band (`drawing.look.back_arrows`).

    Returns:
        The y for the next long-way arrow's band (8 px higher when this one used it, so two never share a run).
    """
    cid, src, dst, text, style = edge
    sx, sy, sw, sh = page.rects[src]
    dx, dy, dw, dh = page.rects[dst]
    route_style = "edgeStyle=none;rounded=0;html=1;endArrow=block;endFill=1;dashed=1;strokeColor=#6a3fa0;"
    mark_style = "text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#6a3fa0;labelBackgroundColor=#ffffff;"
    mid, x2 = sy + sh * 0.2, dx + dw * 0.75   # above the forward arrows, which enter the left side at 1/3 to 2/3 or the middle
    short = [(sx, mid), (x2, mid), (x2, dy if dy > mid else dy + dh)]
    if mode == "short-first" and x2 < sx and not (dy < mid < dy + dh) and _clear(page, short, {src, dst}):
        page.route(cid, src, dst, short, route_style, klass="thin")
        page.mark(f"{cid}-lbl", label(f"**{text}**"), (sx + x2) / 2, mid - 10, 90, 18, mark_style, cid)
        return band
    fx = float(style.split("exitX=")[1].split(";")[0])
    tx = float(style.split("entryX=")[1].split(";")[0])
    x1, x2 = sx + sw * fx, dx + dw * tx
    page.route(cid, src, dst, [(x1, sy + sh), (x1, band), (x2, band), (x2, dy + dh)], route_style, klass="thin")
    page.mark(f"{cid}-lbl", label(f"**{text}**"), (x1 + x2) / 2, band - 10, 90, 18, mark_style, cid)
    return band - 8
