"""Arrows between the rows of a folded flow page (flowmap.fold). Stdlib only.

A forward arrow from a row's last step leaves its leading side (right in a left-to-right row, left in a right-to-left one) and turns down the
gutter beside it; from any other step it drops at once (operator review 2026-10-27: never out to the row's end and back), down the gap after
the step or straight down from a decision's bottom corner. It then runs along the space under its row (down a gutter right of the lanes when it
skips a row), down the gap before its target and into the target's leading side, or a decision's top corner when its leading corner is taken
(operator review 2026-10-27: three branches of one decision left one corner and ran on top of each other). An arrow back to an earlier row
runs along both rows' bands below the lanes and up a gutter right of the lanes. Labels are placed by the caller after every arrow is drawn, so
none sits on an arrow drawn after it.

Imported, not run: `from flowmap.fold_turns import between, forward, back` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page

from .flow_geometry import BACK_STYLE
from .model import GAP
from .routing import JUMP, STYLE, branch_label

#: Spacing of arrows that share a gutter: an arrow crossing two of them hops twice, and draw.io merges hops closer than two arcs and a gap
#: (drawio.audit.ARC_GAP; 6 px arcs, routing.JUMP).
TRACK = 2 * JUMP + 6
#: Offset from a gap's middle (where the row's own arrows run) for an arrow between rows in that gap: off it, clear of NEAR, and two such
#: arrows either side of the middle a full track apart.
INNER = TRACK / 2


def tidy(pts: list) -> list:
    """A polyline without repeated points or points straight through.

    Args:
        pts: the points.

    Returns:
        The points that remain.
    """
    out: list = []
    for p in pts:
        if out and abs(p[0] - out[-1][0]) < .5 and abs(p[1] - out[-1][1]) < .5:
            continue
        if len(out) >= 2 and ((abs(out[-2][0] - out[-1][0]) < .5 and abs(out[-1][0] - p[0]) < .5)
                              or (abs(out[-2][1] - out[-1][1]) < .5 and abs(out[-1][1] - p[1]) < .5)):
            out[-1] = p
            continue
        out.append(p)
    return out


def _take(count: dict, key: object) -> int:
    """The next free track of a gutter.

    Args:
        count: tracks taken so far, by gutter.
        key: the gutter.

    Returns:
        The track number (0 first).
    """
    count[key] = count.get(key, -1) + 1
    return count[key]


def _free(page: Page, pt: tuple) -> bool:
    """Whether no drawn arrow starts or ends at a point.

    Args:
        page: the page.
        pt: the point.

    Returns:
        True when the point is free.
    """
    return all((round(r.points[k][0]), round(r.points[k][1])) != (round(pt[0]), round(pt[1])) for r in page.routes for k in (0, -1))


def _side_point(page: Page, cid: str, right: bool, diamond: bool) -> tuple | None:
    """A free point on a box's left or right side: the middle, else a third or two thirds down (a decision has only its corner).

    Args:
        page: the page.
        cid: the box.
        right: the right side, else the left.
        diamond: whether the box is a decision.

    Returns:
        The point, or None when every one is taken.
    """
    x, y, w, h = page.rects[cid]
    for f in (0.5,) if diamond else (0.5, 0.33, 0.67):
        if _free(page, (x + w if right else x, y + h * f)):
            return x + w if right else x, y + h * f
    return None


def _under(row: dict, count: dict) -> float:
    """The next free track under a row's lanes, above its notes, for an arrow leaving the row.

    Args:
        row: the placed row (`r`, `exit_y`).
        count: tracks taken so far.

    Returns:
        The track's y.
    """
    return row["exit_y"] + TRACK * _take(count, ("under", row["r"]))


def _turn(row: dict, count: dict) -> float:
    """The next free track of the gutter a row turns down (beside its last step).

    Args:
        row: the placed row (`ks`, `after`, `flip`).
        count: tracks taken so far.

    Returns:
        The track's x.
    """
    turn = row["after"][row["ks"][-1]]
    return turn + TRACK * _take(count, ("x", round(turn))) * (-1 if row["flip"] else 1)


def _start(page: Page, ends: tuple, row: dict, ka: int, count: dict) -> tuple[list, bool]:
    """The first points of an arrow leaving a step for a later row, ending where it drops straight down to the space under the row.

    Only the row's last step turns in the row's turning gutter. Any other step drops at once, never out to the row's end and back (operator
    review 2026-10-27 of a z fold: "from 5 to right and then ... a U turn and coming back towards 7"): from its leading side down the gap
    after it (off the gap's middle, where the row's own arrows run); from a decision whose leading corner is taken, straight down from its
    bottom corner. Where a note lies below, the drop moves under the lanes to the middle of the gap, the only room between two notes. A
    decision with its bottom corner taken too leaves by its top corner, over the row to the turning gutter.

    Args:
        page: the page.
        ends: (source box, the id its note would have).
        row: the source's placed row (`r`, `ks`, `flip`, `top`, `exit_y`, `after`, `notes`), and `diamond` (the source is a decision)
            and `drop` (leave by the bottom corner when free; `nest`).
        ka: the source's step index.
        count: tracks taken so far.

    Returns:
        (points, whether the drop is the row's turning gutter).
    """
    src, note = ends
    x, y, w, h = page.rects[src]
    sign = -1 if row["flip"] else 1
    side = None if row["drop"] and _free(page, (x + w / 2, y + h)) else _side_point(page, src, not row["flip"], row["diamond"])
    if side and ka == row["ks"][-1]:
        return [side, (_turn(row, count), side[1])], True
    mid = row["after"][ka]
    if side:
        gx = mid - sign * (INNER + TRACK * _take(count, ("x", round(mid))))   # between the step and the gap's middle
        if not row["notes"]:
            return [side, (gx, side[1])], False
        ye = _under(row, count)
        return [side, (gx, side[1]), (gx, ye), (mid, ye)], False
    if _free(page, (x + w / 2, y + h)):
        if note not in page.rects:
            return [(x + w / 2, y + h)], False
        ye = _under(row, count)
        return [(x + w / 2, y + h), (x + w / 2, ye), (mid, ye)], False
    if _free(page, (x + w / 2, y)):
        over = row["top"] + 4 + TRACK * _take(count, ("over", row["r"]))
        return [(x + w / 2, y), (x + w / 2, over), (_turn(row, count), over)], True
    return [(x + w if not row["flip"] else x, y + h / 2), (_turn(row, count), y + h / 2)], True


def _finish(page: Page, dst: str, row: dict, diamond: bool, ways: tuple) -> list:
    """The last points of an arrow into a step of a later row, from the space above that row.

    Args:
        page: the page.
        dst: the target box.
        row: the target's placed row.
        diamond: whether the target is a decision.
        ways: (the gap's x before the target, or None to come down into its top, the y of the space above the row).

    Returns:
        The points.
    """
    in_x, above = ways
    x, y, w, h = page.rects[dst]
    side = _side_point(page, dst, row["flip"], diamond)
    if (in_x is None or side is None and diamond) and _free(page, (x + w / 2, y)):   # down into the top (a decision's top corner)
        return [(x + w / 2, above), (x + w / 2, y)]
    side = side or (x + w if row["flip"] else x, y + h / 2)
    return [(in_x, above), (in_x, side[1]), side]


def forward(page: Page, edge: tuple, rows: tuple, geo: dict, ctx: tuple) -> tuple:
    """Draw an arrow to a step in a later row (its label is left to the caller).

    Args:
        page: the page.
        edge: (cell id, source step id, target step id, label, style) from step_edges.
        rows: (the placed rows, row of each step index, step order).
        geo: the page geometry (`far`: the gutter right of the lanes and of every turning track).
        ctx: (flow, profile, shapes, tracks taken).

    Returns:
        (cell id, points, label, colour) for the label.
    """
    cid, a, b, _text, _style = edge
    placed, row_of, order = rows
    flow, profile, shapes, count = ctx
    fid, by_id = flow["id"], {s["id"]: s for s in flow["steps"]}
    ka, kb = order[a], order[b]
    top, bot = placed[row_of[ka]], placed[row_of[kb]]
    src, dst = f"{fid}-s-{a}", f"{fid}-s-{b}"
    pts, turned = _start(page, (src, f"{fid}-n-{a}"), dict(top, diamond=shapes[a] == "decision", drop=cid in count.get("drops", ())), ka, count)
    y1 = top["notes_bottom"] + GAP + TRACK * _take(count, ("y", row_of[ka]))
    drop = pts[-1][0]
    pts.append((drop, y1))
    before, sign = bot["before"][kb], -1 if bot["flip"] else 1
    if turned and round(before) == round(top["after"][top["ks"][-1]]):   # one gutter (a serpentine turn): straight down it
        in_x = drop
    elif kb == bot["ks"][0]:   # the target row's turning-in gutter
        in_x = before - sign * TRACK * _take(count, ("x", round(before)))
    else:   # an inner gap, off its middle (the row's own arrows use it): first between it and the target, then the other side
        k = _take(count, ("x", round(before)))
        in_x = before + sign * (INNER if k == 0 else -INNER - TRACK * (k - 1))
        x, y, w, _h = page.rects[dst]
        if k and _free(page, (x + w / 2, y)):   # the gap already holds one: straight down into the top instead of a third run there
            in_x = None
    if row_of[kb] > row_of[ka] + 1:   # past a row: down a gutter right of the lanes
        far = geo["far"] + TRACK * _take(count, "out")
        y2 = placed[row_of[kb] - 1]["notes_bottom"] + GAP + TRACK * _take(count, ("y", row_of[kb] - 1))
        pts += [(far, y1), (far, y2)]
        y1 = y2
    pts = tidy(pts + _finish(page, dst, bot, shapes[b] == "decision", (in_x, y1)))
    text, colour = branch_label(by_id[a], b, kb + 1, profile.look)
    rounded = 0 if profile.look.get("arrow_corners", "rounded") == "square" else 1
    page.route(cid, src, dst, pts, STYLE.format(colour=colour, rounded=rounded), klass="thin", jump=JUMP)
    return cid, pts, text, colour


def back(page: Page, edge: tuple, rows: tuple, geo: dict, ctx: tuple) -> tuple:
    """Draw an arrow back to a step in an earlier row: down to its row's band below the lanes, right to a gutter right of the lanes, up to
    the target row's band, along it and up into the target's bottom (each band then moves up a track, as on an unfolded page).

    Args:
        page: the page.
        edge: (cell id, source step id, target step id, label, style with exitX and entryX) from step_edges.
        rows: (the placed rows, row of each step index, step order).
        geo: the page geometry (`far`: the gutter right of the lanes and of every turning track).
        ctx: (flow, profile, shapes, tracks taken).

    Returns:
        (cell id, label text, label centre x, label centre y) for the "back to N" mark.
    """
    cid, a, b, text, style = edge
    placed, row_of, order = rows
    flow, _profile, _shapes, count = ctx
    src, dst = f"{flow['id']}-s-{a}", f"{flow['id']}-s-{b}"
    low, high = placed[row_of[order[a]]], placed[row_of[order[b]]]
    fx = float(style.split("exitX=")[1].split(";")[0])
    tx = float(style.split("entryX=")[1].split(";")[0])
    sx, sy, sw, sh = page.rects[src]
    dx, dy, dw, dh = page.rects[dst]
    x1, x2 = sx + sw * (1 - fx if low["flip"] else fx), dx + dw * (1 - tx if high["flip"] else tx)
    far = geo["far"] + TRACK * _take(count, "out")
    pts = [(x1, sy + sh), (x1, low["band"]), (far, low["band"]), (far, high["band"]), (x2, high["band"]), (x2, dy + dh)]
    page.route(cid, src, dst, pts, BACK_STYLE, klass="thin")
    spot = (cid, text, (x1 + far) / 2, low["band"] - 10)
    low["band"] -= TRACK
    high["band"] -= TRACK
    return spot


def _reach(edge: tuple, rows: tuple) -> float:
    """How far an arrow between rows runs along the space between them: from the gap after its source to the gap before its target.

    Args:
        edge: the arrow (step_edges).
        rows: (the placed rows, row of each step index, step order).

    Returns:
        The distance in px.
    """
    placed, row_of, order = rows
    top, bot = placed[row_of[order[edge[1]]]], placed[row_of[order[edge[2]]]]
    return abs(top["after"][top["ks"][-1]] - bot["before"][order[edge[2]]])


def nest(turns: list, rows: tuple) -> tuple[list, set]:
    """The order arrows between rows take their tracks, and which leave their decision by its bottom corner.

    The arrow going farthest along the space between the rows goes first, so it takes the track nearest the row in the turning gutter and
    the highest one under the row, and no arrow of the bundle crosses another (operator review 2026-10-27 of a folded page: hops of nested
    turn arrows merged). Of a decision's branches into later rows only the one going least far takes its leading corner; the others drop
    from its bottom corner (operator review 2026-10-27, Decision order: the far branch took the corner and crossed the near one).

    Args:
        turns: the arrows between rows, in step order.
        rows: (the placed rows, row of each step index, step order).

    Returns:
        (the arrows in drawing order: forward ones nested, then back ones in step order; cell ids of the branches that drop).
    """
    fwd = [e for e in turns if "back to" not in e[3]]
    nearest: dict = {}
    for e in sorted(fwd, key=lambda e: _reach(e, rows)):
        nearest.setdefault(e[1], e[0])
    drops = {e[0] for e in fwd if sum(1 for f in fwd if f[1] == e[1]) > 1 and nearest[e[1]] != e[0]}
    return sorted(fwd, key=lambda e: -_reach(e, rows)) + [e for e in turns if "back to" in e[3]], drops


def between(edges: list, row_of: dict, order: dict) -> tuple[dict, dict]:
    """How many arrows between rows each row needs room for: tracks in the space under it (between its notes and the next row), and
    tracks under its lanes for arrows leaving it.

    Args:
        edges: the flow's arrows.
        row_of: each step index's row.
        order: each step id's index.

    Returns:
        ({row number: tracks under the row}, {row number: arrows leaving it}).
    """
    under: dict = {}
    leaving: dict = {}
    for _c, a, b, text, _s in edges:
        ra, rb = row_of[order[a]], row_of[order[b]]
        if "back to" in text or ra >= rb:
            continue
        under[ra] = under.get(ra, 0) + 1
        leaving[ra] = leaving.get(ra, 0) + 1
        if rb > ra + 1:
            under[rb - 1] = under.get(rb - 1, 0) + 1
    return under, leaving
