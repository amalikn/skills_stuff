"""Self-loops on the End-to-end page: a step done by the same component as the step before is drawn as a small loop on that component's
box, labelled x.y (or x.y–z for a run of such steps), when `look.e2e_loops` is on. Stdlib only.

Why (operator, 2026-10-26): "Can we create a 14.3 as a loop on the same box? ... like it is done in the Turing machines". Without it such a
step draws nothing (nothing moves) and is only named in the next arrow's hover text, so a reader sees 14.2 then 14.4 and looks for 14.3.

Placement (operator: "the top or the bottom, depending where more space is available ... case by case"). Arrows meet a box only on its
sides, so loops sit on its top or bottom edge. The page is laid out first; for each box the clear room above and below (to the nearest run,
box or loop) is measured and its loops go on the roomier edge, packed by label width and overflowing to the other edge. Where an edge lacks
the room, the gap next to it is widened by the shortfall and the page is laid out again (E2EGrid.loop_reserve); otherwise nothing moves.

Imported, not run: `from flowmap.loops import plan_loops, draw_loops` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from drawio.cell import tag
from drawio.mxfile import ARROW_HEAD, Page

from .e2e_grid import E2E_BW
from .isolate import E2E_DIMMED, group_tag, isolate_link
from .model import flow_family
from .step_labels import e2e_label_size, step_label
from .tips import tip_html

#: Loop height: its last run reaches the box at the audit's head room for a step arrow (drawio.audit.HEAD_ROOM "thick").
LOOP_H = 24
#: Distance between a loop's two legs.
LOOP_W = 12
#: Clear space kept beyond a loop's label, and at each end of an edge.
LOOP_PAD = 6


@dataclass
class Loop:
    """One self-loop: a run of consecutive steps of one flow done by one component.

    Args:
        cid: the edge cell id.
        comp: the component id.
        family: the colour group id (a flow id or a family id).
        text: the label, x.y or x.y–z.
        n: the flow's step count, as text.
        tip: the hover text.
        tags: its draw.io tags (flow, family, step-arrow, loop).
        edge: "top" or "bottom", set by plan_loops.
        width: its slot width along the edge.
        pts: its polyline once drawn (draw_loops).
    """

    cid: str
    comp: str
    family: str
    text: str
    n: str
    tip: str
    tags: tuple
    edge: str = ""
    width: float = 0.0
    pts: list = field(default_factory=list)


def loop_runs(grid: object) -> list[Loop]:
    """Every run of consecutive steps that stays in one component (a step whose actor is the one before, x.1 counting the flow's runs_on).

    Args:
        grid: the End-to-end layout (E2EGrid).

    Returns:
        The loops, in map order.
    """
    loops = []
    for f in grid.data["flows"]:
        fi, steps = grid.number[f["id"]], f["steps"]
        acts = [s["actor"] for s in steps]
        path = ([f["runs_on"]] if f["runs_on"] != acts[0] else [acts[0]]) + acts
        k = 0
        while k < len(steps):
            if path[k] != path[k + 1]:
                k += 1
                continue
            end = k
            while end + 1 < len(steps) and path[end + 1] == path[end + 2]:
                end += 1
            text = f"{fi}.{k + 1}" + (f"–{end + 1}" if end > k else "")
            lines = [f"**{fi}.{j + 1} {steps[j]['id']}:** {steps[j]['action']}" for j in range(k, end + 1)]
            tip = tip_html(f"{text} {f['title']}: stays in {grid.comps[path[k + 1]]['name']}", *lines)
            loops.append(Loop(f"e2e-o-{f['id']}-{k + 1}", path[k + 1], grid.group_of[f["id"]], text, str(len(steps)), tip,
                              (tag("flow", f["id"]), tag("family", flow_family(f, grid.profile)), "step-arrow", "loop")))
            k = end + 1
    return loops


def _room(grid: object, comp: str, taken: dict) -> tuple[float, float]:
    """The clear room above and below a box: to the nearest horizontal run over it, the nearest box in its column, or loops already placed.

    Args:
        grid: the laid-out End-to-end page (EndToEnd, with routed points).
        comp: the component id.
        taken: {component id: (room its top loops use, room its bottom loops use)} for boxes already planned.

    Returns:
        (room above, room below) in pixels.
    """
    c, r = grid.cell[comp]
    x0, x1 = grid.col_x[c], grid.col_x[c] + E2E_BW
    top, h = grid._box_span(comp)
    up, down = top - grid.gap_top[-1], grid.bottom - (top + h)
    for pts in grid.pts.values():
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if ay == by and min(ax, bx) < x1 and max(ax, bx) > x0:
                up = min(up, top - ay) if ay < top else up
                down = min(down, ay - top - h) if ay > top + h else down
    for other, (oc, orow) in grid.cell.items():
        if oc == c and other != comp:
            otop, oh = grid._box_span(other)
            ut, ub = taken.get(other, (0, 0))
            if orow < r:
                up = min(up, top - otop - oh - ub)
            elif orow > r:
                down = min(down, otop - top - h - ut)
    return up, down


def plan_loops(e2e: object) -> list[Loop]:
    """Find the loops, put each box's on its roomier edge (overflowing to the other), and widen any gap that lacks room, relaying the page.

    Args:
        e2e: the laid-out End-to-end page (EndToEnd); its layout is redone when a gap is widened.

    Returns:
        The loops, each with its edge and width; none unless `look.e2e_loops` is on.
    """
    if not e2e.profile.look.get("e2e_loops"):
        return []
    loops = loop_runs(e2e)
    need = LOOP_H + 4 + e2e.label_h + LOOP_PAD
    by_comp: dict[str, list[Loop]] = {}
    for loop in loops:
        loop.width = max(e2e_label_size([(loop.text, loop.n)], e2e.label_font, e2e.step_total)[0], LOOP_W + 8) + LOOP_PAD
        by_comp.setdefault(loop.comp, []).append(loop)
    taken: dict[str, tuple[float, float]] = {}
    reserve: dict[int, list[float]] = {}
    for comp in sorted(by_comp, key=lambda cid: e2e.cell[cid][1]):   # top rows first, so a box sees the loops placed above it
        up, down = _room(e2e, comp, taken)
        edges = ("top", "bottom") if up >= down else ("bottom", "top")
        used = {"top": 0.0, "bottom": 0.0}
        for loop in by_comp[comp]:
            loop.edge = edges[0] if used[edges[0]] + loop.width <= E2E_BW - 2 * LOOP_PAD else edges[1]
            used[loop.edge] += loop.width
        taken[comp] = (need if used["top"] else 0, need if used["bottom"] else 0)
        r = e2e.cell[comp][1]
        for edge, room, gap, side in (("top", up, r - 1, 1), ("bottom", down, r, 0)):
            if used[edge] and room < need:
                reserve.setdefault(gap, [0.0, 0.0])[side] = max(reserve.get(gap, [0.0, 0.0])[side], need - room)
    if reserve:
        e2e.loop_reserve = {g: (rt, rb) for g, (rt, rb) in reserve.items()}
        e2e._size()
        e2e._improve()
    return loops


def draw_loops(e2e: object, page: Page, colour: dict, dim: float | None) -> None:
    """Draw every loop on its box's edge (centred as a group), with its x.y label beyond it, its hover text, tags and click link.

    Args:
        e2e: the End-to-end page (EndToEnd) with its loops planned.
        page: the page, boxes already drawn.
        colour: {group id: colour}.
        dim: the click-isolation opacity, or None when off.
    """
    groups: dict[tuple[str, str], list[Loop]] = {}
    for loop in e2e.loops:
        groups.setdefault((loop.comp, loop.edge), []).append(loop)
    for (comp, edge), row in groups.items():
        top, h = e2e._box_span(comp)
        y, s = (top, -1) if edge == "top" else (top + h, 1)
        x = e2e.col_x[e2e.cell[comp][0]] + (E2E_BW - sum(lp.width for lp in row)) / 2
        for loop in row:
            cx, x = x + loop.width / 2, x + loop.width
            loop.pts = [(cx - LOOP_W / 2, y), (cx - LOOP_W / 2, y + s * LOOP_H), (cx + LOOP_W / 2, y + s * LOOP_H), (cx + LOOP_W / 2, y)]
            page.tips[loop.cid], page.tags[loop.cid] = loop.tip, loop.tags
            if dim is not None:
                page.links[loop.cid] = isolate_link(e2e.group_index[loop.family], E2E_DIMMED, group_tag(e2e.profile.look, loop.family), dim)
            layer, col = f"e2e-L-{loop.family}", colour[loop.family]
            page.route(loop.cid, f"e2e-c-{comp}", f"e2e-c-{comp}", loop.pts,
                       f"edgeStyle=none;rounded=1;html=1;strokeColor={col};strokeWidth=2;{ARROW_HEAD}endSize=6;", klass="thick", layer=layer)
            lw, lh = e2e_label_size([(loop.text, loop.n)], e2e.label_font, e2e.step_total)
            page.mark(f"{loop.cid}-l", step_label(loop.text, loop.n, e2e.step_total), cx, y + s * (LOOP_H + 2 + lh / 2), lw, lh,
                      f"text;html=1;align=center;verticalAlign=middle;fontSize={e2e.label_font:g};fontColor={col};labelBackgroundColor=#ffffff;"
                      "spacing=0;", owner=loop.cid, layer=layer)
