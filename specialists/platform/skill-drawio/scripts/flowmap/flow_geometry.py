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


def column_lefts(widths: list[int]) -> list[float]:
    """Each step column's left edge, columns as wide as their step plus the usual margin.

    Args:
        widths: each step box's width, in step order.

    Returns:
        The x of each column's left edge.
    """
    lefts, x = [], MARGIN + LANE_HEAD_W + GAP
    for w in widths:
        lefts.append(x)
        x += w + (COL_W - STEP_W)
    return lefts


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
