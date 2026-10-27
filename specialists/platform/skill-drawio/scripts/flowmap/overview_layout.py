"""The overview page's geometry: layered group interiors (rows by dependency depth, slots for row-skipping arrows, barycentre sweeps), box
text sizing, and which group edge and channels a thick arrow uses. Stdlib only.

The layout (approved for unified-network-controller, 2026-10-19: "align boxes so arrows overlap, twist and turn less"): inside each group, rows
by same-group dependency depth (a box sits above what it needs), ordered by barycentre to cut crossings; an arrow that skips rows takes a slot
in each row it passes, so a long arrow runs between boxes; boxes with no arrow inside the group sit in a 3-column grid below. Groups sit on a
grid with per-column widths; thick arrows between groups run in the channels between groups, each on its own track.

Imported, not run: `from flowmap import overview_layout` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass

from drawio.mxfile import BLANK, heading, wrapped_lines

from .model import COMP_W

#: Overview box size, gaps and the group-interior layout (slot width for a row-skipping arrow, padding, grid columns).
OV_BW, OV_BH, OV_HGAP, OV_SLOT, OV_PAD, OV_GRID_COLS = COMP_W, 44, 34, 22, 26, 3
#: Thin arrows inside a group: their track spacing in a row gap and their hop size (a hop needs 2 * jump + 6 px between crossings).
OV_THIN_SP, OV_THIN_JUMP = 16, 4
#: Channel between groups (at least; it grows so tracks stay OV_SP apart), thin head room, thick head room, track spacing, hop size.
OV_CHANNEL, OV_MIN_THIN, OV_MIN_HEAD, OV_SP, OV_JUMP = 210, 22, 34, 24, 7
#: Box text (font 10): characters per line in the 180 px between the left padding and the dot column (conservative: bold text is wider), line
#: height, left padding, and the right padding that keeps the dot column clear of the text.
OV_CHARS, OV_LINE_H, OV_LEFT, OV_SIDE = 26, 13, 8, 22
#: Space above the group grid for the title.
OV_TOP = 90
#: One neutral colour for every arrow inside a group, so no thin arrow is mistaken for a thick one.
THIN_GREY = "#4b5563"


@dataclass
class GroupLayout:
    """One group's interior on the overview.

    Args:
        rows: the rows top to bottom, each a list of component ids and `slot:` keys (a row-skipping arrow's place in a row it passes).
        x: each key's left offset inside the group.
        gaps: per row, how many arrows cross the gap below it (one track each).
        chains: each same-group arrow as the keys it passes, from the dependent component to the one it needs.
        width: the group's width.
    """

    rows: list
    x: dict
    gaps: list
    chains: list
    width: float


def depth(cid: str, same: dict, seen: tuple = ()) -> int:
    """A component's row height from the bottom: 0 when it needs nothing in its group, else one more than the deepest thing it needs.

    Args:
        cid: the component id.
        same: {component id: the components it needs in its own group}.
        seen: the ids already on this path (a cycle stops there).

    Returns:
        The depth.
    """
    return 1 + max((depth(d, same, seen + (cid,)) for d in same[cid] if d not in seen), default=-1)


def key_width(key: str) -> float:
    """How wide a row entry is.

    Args:
        key: a component id or a `slot:` key.

    Returns:
        OV_SLOT for a slot, else the box width.
    """
    return OV_SLOT if key.startswith("slot:") else OV_BW


def _rows_and_chains(ids: list, same: dict, cols: int = OV_GRID_COLS) -> tuple[list, list]:
    """A group's rows by dependency depth (unlinked boxes in a grid below) and each same-group arrow's chain of slots.

    Args:
        ids: the group's component ids, in map order.
        same: {component id: the components it needs in its own group}.
        cols: columns in the grid of unlinked boxes; 0 puts them all in one row.

    Returns:
        (rows, chains).
    """
    linked = {cid for cid in ids if same[cid]} | {d for cid in ids for d in same[cid]}
    alone = [cid for cid in ids if cid not in linked]
    dep = {cid: depth(cid, same) for cid in ids if cid in linked}
    top = max(dep.values(), default=0)
    rows: list[list[str]] = [[] for _ in range(top + 1)] if linked else []
    for cid in ids:
        if cid in linked:
            rows[top - dep[cid]].append(cid)
    step = cols or max(len(alone), 1)
    for i in range(0, len(alone), step):
        rows.append(alone[i:i + step])
    chains = []
    for cid in ids:
        for d in same[cid]:
            chain = [cid]
            for r in range(top - dep[cid] + 1, top - dep[d]):
                slot = f"slot:{cid}>{d}:{r}"
                rows[r].append(slot)
                chain.append(slot)
            chains.append(chain + [d])
    return rows, chains


def _barycentre(rows: list, chains: list) -> None:
    """Order each row by the mean position of its neighbours in the row above (down sweeps) or below (up sweeps), six sweeps.

    Args:
        rows: the rows, sorted in place.
        chains: the arrows' chains.
    """
    nbr_up: dict[str, list[str]] = {}
    nbr_dn: dict[str, list[str]] = {}
    for ch in chains:
        for a, b in zip(ch, ch[1:]):
            nbr_dn.setdefault(a, []).append(b)
            nbr_up.setdefault(b, []).append(a)
    order = {k: i for row in rows for i, k in enumerate(row)}
    for sweep in range(6):   # barycentre sweeps, down then up
        for r in list(range(1, len(rows))) + list(range(len(rows) - 2, -1, -1)):
            ref = nbr_up if r and sweep % 2 == 0 else nbr_dn
            rows[r].sort(key=lambda k, ref=ref: (sum(order[n] for n in ref[k]) / len(ref[k])) if ref.get(k) else order[k])
            for i, k in enumerate(rows[r]):
                order[k] = i


def layout_group(ids: list, same: dict, cols: int = OV_GRID_COLS) -> GroupLayout:
    """Lay out one group's interior: layered rows, slots for row-skipping arrows, barycentre ordering, unlinked boxes in a grid below.

    Args:
        ids: the group's component ids, in map order.
        same: {component id: the components it needs in its own group}.
        cols: columns in the grid of unlinked boxes (the map's `drawing.group_columns` or `group_layout`, default 3; 0 is one row).

    Returns:
        The group layout.
    """
    rows, chains = _rows_and_chains(ids, same, cols)
    _barycentre(rows, chains)
    row_w = [sum(key_width(k) for k in row) + OV_HGAP * (len(row) - 1) for row in rows]
    gw = max(row_w, default=OV_BW) + 2 * OV_PAD
    x = {}
    for row, rw in zip(rows, row_w):
        cx = OV_PAD + (gw - 2 * OV_PAD - rw) / 2
        for k in row:
            x[k] = cx
            cx += key_width(k) + OV_HGAP
    gaps = [0] * len(rows)
    row_of = {k: i for i, row in enumerate(rows) for k in row}
    for ch in chains:
        for a in ch[:-1]:
            gaps[row_of[a]] += 1
    return GroupLayout(rows, x, gaps, chains, gw)


def box_lines(comp: dict, far: list, scale: int = 100) -> list[str]:
    """An overview box's text, set out like a flow note: bold name, kind, then a blank line, a bold Needs heading and one bullet per need.

    Args:
        comp: the component.
        far: the names of what it needs outside its group (only these are listed; arrows show the rest).
        scale: the name's size, percent of the box font (`look.heading_scale`).

    Returns:
        Label lines for drawio.mxfile.label().
    """
    return [heading(f"**{comp['name']}**", scale), comp["kind"]] + ([BLANK, "**Needs**"] + [f"• {name}" for name in far] if far else [])


def text_height(lines: list) -> float:
    """How tall an overview box must be for its text: wrapped lines at OV_CHARS a line, plus the top and bottom padding.

    Args:
        lines: the label lines.

    Returns:
        The height, at least OV_BH.
    """
    return max(OV_BH, 4 + sum(wrapped_lines(x.replace("*", ""), OV_CHARS) for x in lines) * OV_LINE_H + 10)


def side(plan: dict, end: str, grow: dict, gcol: dict) -> str:
    """Which edge of a group a thick arrow leaves (end "a") or enters (end "b").

    Args:
        plan: the arrow's plan (a, b, kind).
        end: "a" for the source group, "b" for the target.
        grow: each group's grid row.
        gcol: each group's grid column.

    Returns:
        "top", "bottom", "left" or "right".
    """
    a, b = plan["a"], plan["b"]
    if plan["kind"] == "side":
        right = gcol[b] > gcol[a]
        return ("right" if right else "left") if end == "a" else ("left" if right else "right")
    if plan["kind"] == "adjacent":
        down = grow[b] > grow[a]
        return ("bottom" if down else "top") if end == "a" else ("top" if down else "bottom")
    down = grow[b] >= grow[a]
    if end == "a":
        return "bottom" if down else "top"
    return "top" if (down and grow[b] != grow[a]) else "bottom"


def far_channels(plan: dict, grow: dict, gcol: dict) -> tuple[int, int, int]:
    """The channels a row-skipping thick arrow uses: the row gap it leaves through, the one it arrives through, and the column gap between.

    Args:
        plan: the arrow's plan.
        grow: each group's grid row.
        gcol: each group's grid column.

    Returns:
        (first row gap, second row gap, column gap); row gap r lies below grid row r, column gap c left of grid column c.
    """
    a, b = plan["a"], plan["b"]
    down = grow[b] >= grow[a]
    r1 = grow[a] if down else grow[a] - 1
    r2 = (grow[b] - 1) if (down and grow[b] != grow[a]) else grow[b]
    return r1, r2, (gcol[b] if gcol[b] > 0 else 1)

def grid_cells(names: list, placed: dict, ncol: int, align: str = "left") -> dict:
    """Each overview group's (row, column) in the group grid: placed groups where the map puts them, the rest in the free cells in map order.

    Args:
        names: the group names, in map order.
        placed: {group name: (row, column)} counted from 0 (the map's `drawing.group_cell`).
        ncol: groups per grid row.
        align: "left", or "centre" to centre a part-filled last row that holds no placed group under the row above
            (`drawing.look.last_row_align`; operator, 2026-10-27: a lone band need not sit at the far left).

    Returns:
        {group name: (row, column)}.

    Raises:
        ValueError: a placed group the map does not have, a column past ncol, or two groups in one cell.
    """
    for name, (r, c) in placed.items():
        if name not in names:
            raise ValueError(f"group_cell: no group named {name!r}")
        if not (0 <= c < ncol and r >= 0):
            raise ValueError(f"group_cell: {name!r} at row {r + 1}, column {c + 1} is outside a grid {ncol} wide (groups_per_row)")
    taken = list(placed.values())
    if len(set(taken)) != len(taken):
        raise ValueError("group_cell: two groups in one cell")
    cells, used, i = {}, set(taken), 0
    for name in names:
        if name in placed:
            cells[name] = placed[name]
            continue
        while (i // ncol, i % ncol) in used:
            i += 1
        cells[name] = (i // ncol, i % ncol)
        used.add(cells[name])
    return centre_last_row(cells, placed, ncol) if align == "centre" else cells


def centre_last_row(cells: dict, placed: dict, ncol: int) -> dict:
    """Shift a part-filled last grid row to the middle columns, unless the map placed a group in it.

    Args:
        cells: {group name: (row, column)} from grid_cells.
        placed: the map's `drawing.group_cell` pins.
        ncol: groups per grid row.

    Returns:
        The cells, with the last row's groups moved right by (ncol - their count) // 2; unchanged for a full row or one with a pin.
    """
    if not cells:
        return cells
    last = max(r for r, _ in cells.values())
    row = sorted((c, name) for name, (r, c) in cells.items() if r == last)
    shift = (ncol - len(row)) // 2
    if last == 0 or shift == 0 or any(name in placed for _, name in row):
        return cells
    return {**cells, **{name: (last, c + shift) for c, name in row}}
