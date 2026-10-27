"""Folded flow pages (`drawing.look.fold`; operator, 2026-10-27, from skill-goal-guard's 13-step "Decision order" page: "after box six box
seven can be just below ... add an option of fold"): a flow longer than `fold_after` steps is drawn in rows of that many columns.
"serpentine": every second row runs right to left and one short arrow turns down at the row's end; "z": every row runs left to right and the
turn arrow runs back under the row. Off by default, so a map that sets nothing draws exactly as before. Stdlib only.

Folding happens at layout time, never after (drawio.mxfile.Page stores finished XML per cell). Each row repeats every lane band of the flow
with its heads on the left in both styles, and its notes sit under it; the header is on top and the shape legend under the last row. A row's own
arrows are routed by the ordinary router (flowmap.routing, flowmap.uncross) on a scratch page laid out left to right, then copied onto the page,
mirrored for a right-to-left row, so the router needs no second direction. An arrow between rows runs through gutters: across the gap after its
source (the row's turning side for its last step), along the space between the rows, down the gap before its target. An arrow back to an earlier
row runs along both rows' bands below the lanes and up a gutter right of the lanes.

Imported, not run: `from flowmap.fold import fold_rows, folded_page` with the skill's scripts/ on sys.path; flowmap.pages calls them.
"""

from __future__ import annotations

from drawio.audit import seg_hits_rect, segments
from drawio.mxfile import Page, label

from .flow_geometry import BACK_MARK, LANE_HEAD_W, back_arrow, col_gap, column_lefts, label_gaps, plan_runs, reserve, run_ys
from .fold_turns import TRACK, back, between, forward, nest
from .lanes import draw_lanes
from .model import GAP, MARGIN
from .route_costs import SPLIT_GAP
from .routing import branch_label, draw_label, route_flow
from .shapes import lane_shape, shape_legend
from .uncross import uncross, unshare
#: The fold styles; "off" draws one row.
FOLDS = ("off", "serpentine", "z")


def fold_setting(flow: dict, look: dict) -> tuple[str, int]:
    """A flow's fold: its own `layout: {fold, fold_after}` over the drawing's `look.fold` and `look.fold_after`.

    Args:
        flow: the flow from the map.
        look: the drawing look.

    Returns:
        (style, columns per row).
    """
    own = flow.get("layout") or {}
    return str(own.get("fold", look.get("fold", "off"))), max(2, int(own.get("fold_after", look.get("fold_after", 7))))


def fold_rows(flow: dict, look: dict) -> list[list[int]]:
    """The step indexes in each row of a flow page: as many rows as `fold_after` steps a row makes, rounded to the nearest, the steps then
    spread evenly over them, so a short last row is not drawn on its own but its steps stretch the rows above (operator, 2026-10-27: "if
    there is an overflow like we have only one going to the third one, stretch it so that it fits in the two rows"): 13 steps at 6 a row
    make rows of 7 and 6.

    Args:
        flow: the flow from the map.
        look: the drawing look.

    Returns:
        One list of step indexes per row; a single row when the fold is off or the flow fits in one.
    """
    style, after = fold_setting(flow, look)
    n = len(flow["steps"])
    if style == "off" or n <= after:
        return [list(range(n))]
    count = max(2, int(n / after + 0.5))
    sizes = [n // count + (k < n % count) for k in range(count)]
    return [list(range(sum(sizes[:k]), sum(sizes[:k + 1]))) for k in range(count)]


class _Scratch(Page):
    """A page that remembers how each arrow and label was drawn, so a row routed here can be copied onto the real page (`_copy`)."""

    def __init__(self, page_id: str) -> None:
        """Start an empty scratch page.

        Args:
            page_id: the real page's id.
        """
        super().__init__(page_id, "scratch")
        self.route_args: dict = {}
        self.mark_args: dict = {}

    def route(self, cid: str, src: str, dst: str, points: list, style: str, klass: str = "thick", layer: str = "1",
              ignore: tuple = (), jump: float = 0.0) -> None:
        """Page.route, remembering the style and options by (cell id, drawn points): the uncrossing pass redraws arrows and may restore
        an earlier drawing, so only the routes left on the page are copied.

        Args:
            cid: as for Page.route.
            src: as for Page.route.
            dst: as for Page.route.
            points: as for Page.route.
            style: as for Page.route.
            klass: as for Page.route.
            layer: as for Page.route.
            ignore: as for Page.route.
            jump: as for Page.route.
        """
        super().route(cid, src, dst, points, style, klass, layer, ignore, jump)
        self.route_args[(cid, tuple(self.routes[-1].points))] = (style, klass, layer, tuple(ignore), jump)

    def mark(self, cid: str, label: str, cx: float, cy: float, w: float, h: float, style: str, owner: str, layer: str = "1") -> None:
        """Page.mark, remembering the text and style by (cell id, box).

        Args:
            cid: as for Page.mark.
            label: as for Page.mark.
            cx: as for Page.mark.
            cy: as for Page.mark.
            w: as for Page.mark.
            h: as for Page.mark.
            style: as for Page.mark.
            owner: as for Page.mark.
            layer: as for Page.mark.
        """
        super().mark(cid, label, cx, cy, w, h, style, owner, layer)
        self.mark_args[(cid, self.marks[-1].rect)] = (label, style)


def _copy_routes(scratch: _Scratch, page: Page, axis: float | None) -> None:
    """Copy a row's arrows from its scratch page, mirrored about `axis` (x to axis - x) for a right-to-left row.

    Args:
        scratch: the row's scratch page.
        page: the real page (the row's boxes already drawn where they belong).
        axis: the mirror's x sum, or None for a left-to-right row.
    """
    for rt in scratch.routes:
        style, klass, layer, ignore, jump = scratch.route_args[(rt.cid, tuple(rt.points))]
        pts = [(axis - x, y) for x, y in rt.points] if axis is not None else rt.points
        page.route(rt.cid, rt.src, rt.dst, pts, style, klass, layer, ignore, jump)


def _copy_marks(scratch: _Scratch, page: Page, axis: float | None, relabel: dict) -> None:
    """Copy a row's labels from its scratch page, mirrored like its arrows; a label split across a vertical line keeps its number left of
    the line and its case right of it. A label that now lies on an arrow drawn after the row (between rows) is placed again on the page.

    Args:
        scratch: the row's scratch page.
        page: the real page (every arrow drawn).
        axis: the mirror's x sum, or None for a left-to-right row.
        relabel: {arrow cell id: (label, colour)} for the arrows whose label may be placed again.
    """
    fx = (lambda x: axis - x) if axis is not None else (lambda x: x)
    names = {m.cid for m in scratch.marks}
    moved, placed = {}, set()
    for m in scratch.marks:
        x, y, w, h = m.rect
        cx = fx(x + w / 2)
        if axis is not None and m.cid.endswith("-lbl-case"):
            cx = fx(x - SPLIT_GAP) + SPLIT_GAP + w / 2
        elif axis is not None and f"{m.cid}-case" in names:
            cx = fx(x + w + SPLIT_GAP) - SPLIT_GAP - w / 2
        moved[m.cid] = (m, cx)
    hit = {m.owner for m, cx in moved.values() if m.owner in relabel and any(
        seg_hits_rect(p, q, (cx - m.rect[2] / 2, m.rect[1], m.rect[2], m.rect[3]), 0)
        for r in page.routes if r.cid != m.owner for p, q in segments(r.points))}
    for m, cx in moved.values():
        if m.owner in hit:
            if m.owner not in placed:
                placed.add(m.owner)
                draw_label(page, m.owner, next(r.points for r in page.routes if r.cid == m.owner), *relabel[m.owner])
            continue
        text, style = scratch.mark_args[(m.cid, m.rect)]
        page.mark(m.cid, text, cx, m.rect[1] + m.rect[3] / 2, m.rect[2], m.rect[3], style, m.owner, m.layer)


def _gutters(ks: list, flat: dict, box_w: list, gaps: list, geo: dict, flip: bool) -> tuple[dict, dict]:
    """Where an arrow between rows turns beside each step of a row: the gap after it and the gap before it, in reading order.

    Args:
        ks: the row's step indexes.
        flat: each step's left edge laid out left to right.
        box_w: each step's width, by position in the row.
        gaps: the gap after each column.
        geo: the page geometry (`start`, `end`, `xl`, `xr`).
        flip: whether the row runs right to left.

    Returns:
        ({step index: x after}, {step index: x before}).
    """
    axis = geo["start"] + geo["end"]
    inner = [flat[k] + box_w[j] + gaps[j] / 2 for j, k in enumerate(ks[:-1])]
    inner = [axis - x for x in inner] if flip else inner
    after = dict(zip(ks, inner + [geo["xl"] if flip else geo["xr"]]))
    before = dict(zip(ks, [geo["xr"] if flip else geo["xl"]] + inner))
    return after, before


def _row(page: Page, ctx: tuple, sized: tuple, spec: tuple) -> dict:
    """Draw one row: its lanes, steps and notes, and its own arrows (routed left to right on a scratch page, then copied).

    Args:
        page: the page.
        ctx: (flow, components by id, flow number, profile).
        sized: (shapes, texts, box widths, box heights, edges, label widths) as flowmap.pages works them out.
        spec: (row number, step indexes, right to left, gaps, top, lane order, lane width, page geometry, step drawer, arrows leaving
            the row, whether the page draws one lane for every row so the row draws none of its own).

    Returns:
        The row: its number, step indexes, direction, top, notes top and bottom, band for back arrows, the gutters beside each step, and
        its scratch page (its labels are copied once every arrow is drawn).
    """
    flow, comps, number, profile = ctx
    shapes, texts, box_w, box_h, edges, _widths = sized
    r, ks, flip, gaps, top, lanes, width, geo, draw_step, leaving, merged = spec
    fid, steps, look = flow["id"], flow["steps"], profile.look
    order = {s["id"]: k for k, s in enumerate(steps)}
    mine = [e for e in edges if order[e[1]] in ks and order[e[2]] in ks]
    plan = plan_runs(steps, [(a, b) for _c, a, b, text, _s in mine if "back to" not in text])
    tg = float(look.get("track_gap", 12))
    room = {key: reserve(n, tg) for key, n in plan["count"].items()}
    scratch = _Scratch(page.page_id)
    part = {"id": fid if r == 0 else f"{fid}-r{r}", "steps": [steps[k] for k in ks]}
    for target in (scratch,) if merged else (page, scratch):
        _lanes, lane_y, lane_h = draw_lanes(target, part, comps, profile, top, box_h, box_w, room, width, lanes)
    widths = [box_w[steps[k]["id"]] for k in ks]
    flat = {k: x + geo["start"] - column_lefts([0])[0] for k, x in zip(ks, column_lefts(widths, gaps))}
    real = {k: geo["start"] + geo["end"] - x - box_w[steps[k]["id"]] for k, x in flat.items()} if flip else flat
    # Under the lanes: the back-arrow band (moving up as on an unfolded page), then a track per arrow leaving the row, then the notes.
    notes_top = top + sum(lane_h) + GAP + TRACK * leaving
    for target, lefts in ((page, real), (scratch, flat)):
        note_h = [draw_step(target, flow, k, comps, profile, (lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts, room, box_w), number)
                  for k in ks]
    band = top + sum(lane_h) + GAP / 2
    for cid, src, dst, text, style in mine:   # back arrows first, as on an unfolded page
        if "back to" in text:
            band = back_arrow(scratch, (cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text, style), band, look["back_arrows"])
    xs = [flat[k] + widths[j] + gaps[j] / 2 for j, k in enumerate(ks[:-1])]
    ys = sorted({y for li in range(len(lanes)) for y in run_ys(li, lane_y, lane_h, plan["count"], tg)})
    drawn, corridors, reserved = route_flow(scratch, (fid, steps, mine, shapes), {"xs": xs, "ys": ys}, look)
    if look.get("uncross", "on") != "off":
        uncross(scratch, drawn, corridors, reserved)
    if look.get("unshare", "on") != "off":
        unshare(scratch, drawn, corridors, reserved)
    _copy_routes(scratch, page, geo["start"] + geo["end"] if flip else None)
    after, before = _gutters(ks, flat, widths, gaps, geo, flip)
    return {"r": r, "ks": ks, "flip": flip, "top": top, "notes_top": notes_top, "exit_y": top + sum(lane_h) + GAP / 2 + TRACK,
            "lanes_bottom": top + sum(lane_h),
            "notes": max(note_h + [0]) > 0, "notes_bottom": notes_top + max(note_h + [0]), "band": band, "after": after, "before": before, "scratch": scratch}


def _place(page: Page, ctx: tuple, sized: tuple, plan: tuple, at: tuple) -> list:
    """Draw every row, each below the one before with room for the arrows between them.

    Args:
        page: the page.
        ctx: as for `folded_page`.
        sized: as for `folded_page`.
        plan: (rows, gaps per row, fold style, tracks under each row, arrows leaving each row, lane order, lane width, page geometry,
            step drawer).
        at: (the first row's top, whether one lane holds every row).

    Returns:
        The placed rows (see `_row`).
    """
    rows, row_gaps, style, tracks, leaving, lanes, width, geo, draw_step = plan
    top, merged = at
    placed = []
    for r, ks in enumerate(rows):
        row = _row(page, ctx, sized, (r, ks, style == "serpentine" and r % 2 == 1, row_gaps[r], top, lanes, width, geo, draw_step,
                                       leaving.get(r, 0), merged))
        placed.append(row)
        top = row["notes_bottom"] + 2 * GAP + TRACK * tracks.get(r, 0)
    return placed


def folded_page(page: Page, ctx: tuple, sized: tuple, how: tuple) -> Page:
    """A flow page drawn in rows: the header, each row (lanes, steps, notes, its own arrows), the arrows between rows, and the shape legend.

    Args:
        page: the empty page (arrow hover texts and tags already set).
        ctx: (flow, components by id, flow number, profile).
        sized: (shapes, texts, box widths, box heights, edges, label widths) as flowmap.pages works them out.
        how: (the rows from `fold_rows`, flowmap.pages' step drawer, its header drawer).

    Returns:
        The page.
    """
    flow, comps, _number, profile = ctx
    shapes, _texts, box_w, _box_h, edges, widths = sized
    rows, draw_step, draw_header = how
    style, _after = fold_setting(flow, profile.look)
    steps, gap = flow["steps"], col_gap(profile.look)
    order = {s["id"]: k for k, s in enumerate(steps)}
    row_gaps = [label_gaps(gap, {j: widths[k] for j, k in enumerate(ks) if k in widths and k + 1 in ks}, len(ks)) for ks in rows]
    content = max(sum(box_w[steps[k]["id"]] for k in ks) + sum(g[:-1]) for ks, g in zip(rows, row_gaps))
    # Room for a turn gutter each side, clear of the lane heads and the outermost notes (a note overhangs its column by half a gap).
    start = MARGIN + LANE_HEAD_W + 2 * GAP + gap / 2
    geo = {"start": start, "end": start + content, "xl": MARGIN + LANE_HEAD_W + GAP, "xr": start + content + gap / 2 + GAP}
    # The lane ends as far past the right gutter's drops as an unfolded lane ends past its last box (operator, 2026-10-27: "too narrow").
    geo["right"] = geo["xr"] + gap + GAP
    width = geo["right"] - MARGIN
    top = MARGIN + draw_header(page, flow, comps, ctx[2], width) + GAP
    lanes = list(dict.fromkeys(s["actor"] for s in steps))
    row_of = {k: r for r, ks in enumerate(rows) for k in ks}
    tracks, leaving = between(edges, row_of, order)
    plan = (rows, row_gaps, style, tracks, leaving, lanes, width, geo, draw_step)
    merged = len(lanes) == 1   # one swim lane holds every row (operator, 2026-10-27: "keep it under the same swim lane")
    pad = 2 * GAP if merged else 0   # the one lane's room above the first row and below the last (operator, 2026-10-27: "a bit more on the top")
    if merged:   # measured on a throwaway page first: the lane is drawn before the steps that sit on it
        last = _place(Page("measure", ""), ctx, sized, plan, (top + pad, True))[-1]
        draw_lanes(page, {"id": flow["id"], "steps": steps}, comps, profile, top, sized[3], box_w, {}, width, lanes,
                   least=last["lanes_bottom"] + pad - top)
    placed = _place(page, ctx, sized, plan, (top + pad, merged))
    turns, drops = nest([e for e in edges if row_of[order[e[1]]] != row_of[order[e[2]]]], (placed, row_of, order))   # arrows between rows
    count: dict = {"drops": drops}
    geo["far"] = geo["right"] + GAP + TRACK * len(turns)   # clear of every turning track
    labels = [(back if "back to" in e[3] else forward)(page, e, (placed, row_of, order), geo, (flow, profile, shapes, count)) for e in turns]
    by_id = {s["id"]: s for s in steps}
    relabel = {cid: branch_label(by_id[a], b, order[b] + 1, profile.look) for cid, a, b, text, _s in edges if "back to" not in text}
    for row in placed:   # labels last, so none sits on an arrow drawn after it
        _copy_marks(row["scratch"], page, geo["start"] + geo["end"] if row["flip"] else None, relabel)
    for spot in labels:
        if isinstance(spot[1], list):   # forward: (cell id, points, label, colour); back: (cell id, label, x, y)
            draw_label(page, spot[0], spot[1], spot[2], spot[3])
        else:
            page.mark(f"{spot[0]}-lbl", label(f"**{spot[1]}**"), spot[2], spot[3], 90, 18, BACK_MARK, spot[0])
    used = list(dict.fromkeys(list(shapes.values()) + [lane_shape(comps[c], profile.kind_shapes) for c in lanes]))
    shape_legend(page, used, MARGIN, placed[-1]["notes_bottom"] + GAP * 2, flow["id"])
    return page
