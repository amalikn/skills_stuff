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
    """How each forward arrow that skips a column is routed, planned before anything is drawn so lanes reserve only the room they use.

    Operator review 2026-10-21: runs overlapped, hugged the lane line, and an arrow into a lower lane came in from the top when it could come
    from the left. Rules: into another lane, enter the target's left side when no step of the target's lane lies between (no room needed);
    else run along the target lane's near edge. In one lane, run over the top; when that run would lie beside another over-the-top run (their
    spans overlap), the arrow whose source is earlier runs under the bottom instead. Arrows are planned latest source first, so earlier sources
    take the bottom.

    Args:
        steps: the flow's steps in order.
        pairs: (source step id, target step id) of the forward arrows.

    Returns:
        {"route": {(src, dst): (side, track)} with side "top", "bottom" or "left"; "count": {(lane index, side): runs}}.
    """
    order = {s["id"]: k for k, s in enumerate(steps)}
    actors = list(dict.fromkeys(s["actor"] for s in steps))
    lane = {s["id"]: actors.index(s["actor"]) for s in steps}
    route, count, spans = {}, {}, {}
    skips = sorted(((a, b) for a, b in pairs if order[b] > order[a] + 1), key=lambda p: -order[p[0]])
    for a, b in skips:
        lo, hi = order[a], order[b]
        if lane[a] != lane[b]:
            between = [s["id"] for s in steps if lane[s["id"]] == lane[b] and lo < order[s["id"]] < hi]
            if not between:
                route[(a, b)] = ("left", 0)
                continue
            side = "bottom" if lane[b] < lane[a] else "top"
        else:
            beside = [sp for sp in spans.get((lane[a], "top"), []) if sp[0] < hi and lo < sp[1]]
            side = "bottom" if beside else "top"
        key = (lane[b], side)
        route[(a, b)] = (side, count.get(key, 0))
        count[key] = route[(a, b)][1] + 1
        spans.setdefault(key, []).append((lo, hi))
    return {"route": route, "count": count}


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
