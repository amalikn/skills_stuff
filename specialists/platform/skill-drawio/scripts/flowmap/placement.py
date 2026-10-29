"""Placement searches that cut arrow crossings after the barycentre ordering (operator, 2026-10-28: "rearranging the order of the boxes",
"apply the same logic for the intergroup arrows"). Sugiyama-style adjacent exchange: a swap is kept only when a crossing count falls.
Stdlib only.

- E2E pages (look key e2e_row_search): column_search over e2e_edges, scored by grid_crossings (arrows between two columns whose ends swap
  order, arcs inside one column that interleave, an arrow leaving a column across an arc); flowmap.e2e.routed_e2e keeps its order only
  when the real routes cross less than the barycentre order's.
- Overview group interiors (overview_row_search): row_search, scored by row_crossings between consecutive rows.
- Overview group grid (overview_group_search): candidates from group_candidates, each routed (routed_crossings); best_cells keeps the
  fewest thick-arrow crossings with no more shared runs than the map's own placement.
"""

from __future__ import annotations

import random

from drawio.audit import crossing


def row_crossings(rows: list, chains: list) -> int:
    """Crossings between consecutive rows implied by the order: two chain segments between the same two rows whose ends swap order.

    Args:
        rows: the rows, in their current order.
        chains: the arrows' chains (component and slot keys, top row first).

    Returns:
        The count.
    """
    pos = {k: i for row in rows for i, k in enumerate(row)}
    rof = {k: r for r, row in enumerate(rows) for k in row}
    segs = [(rof[a], pos[a], pos[b]) for ch in chains for a, b in zip(ch, ch[1:]) if a in rof and b in rof]
    return sum(1 for i, (r1, a1, b1) in enumerate(segs) for r2, a2, b2 in segs[i + 1:] if r1 == r2 and (a1 - a2) * (b1 - b2) < 0)


def row_search(rows: list, chains: list) -> None:
    """Swap keys inside each row while that lowers row_crossings (first improvement, at most 20 passes).

    Args:
        rows: the rows, reordered in place.
        chains: the arrows' chains.
    """
    best = row_crossings(rows, chains)
    for _ in range(20):
        better = False
        for row in rows:
            for i in range(len(row)):
                for j in range(i + 1, len(row)):
                    row[i], row[j] = row[j], row[i]
                    n = row_crossings(rows, chains)
                    if n < best:
                        best, better = n, True
                    else:
                        row[i], row[j] = row[j], row[i]
        if not better:
            break


def turn(a: tuple, b: tuple, c: tuple) -> int:
    """Orientation of c against the line a-b.

    Args:
        a, b, c: (x, y) points.

    Returns:
        1 left turn, -1 right turn, 0 collinear.
    """
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


def segments_cross(p: tuple, q: tuple, r: tuple, s: tuple) -> bool:
    """Whether segment p-q properly crosses segment r-s (shared ends and collinear touches do not count).

    Args:
        p, q, r, s: (x, y) points.

    Returns:
        True on a proper crossing.
    """
    if len({p, q, r, s}) < 4:
        return False
    return turn(p, q, r) * turn(p, q, s) < 0 and turn(r, s, p) * turn(r, s, q) < 0


def channel_path(a: tuple, b: tuple) -> list:
    """The orthogonal path a thick arrow takes between two group cells, as the overview routes it: straight between neighbours in a row,
    through the channel below the row when it skips a cell, through the channel between two adjacent rows, along a column channel when
    it skips a row. Points are (column, row) in cell units; channels sit at half steps.

    Args:
        a: (row, column) of one group.
        b: (row, column) of the other.

    Returns:
        The path's corner points.
    """
    (ra, ca), (rb, cb) = a, b
    if ra == rb:
        return [(ca, ra), (cb, rb)] if abs(ca - cb) == 1 else [(ca, ra), (ca, ra + 0.5), (cb, ra + 0.5), (cb, rb)]
    if abs(ra - rb) == 1:
        mid = (ra + rb) / 2
        return [(ca, ra), (ca, mid), (cb, mid), (cb, rb)]
    x = min(ca, cb) + 0.5
    return [(ca, ra), (x, ra), (x, rb), (cb, rb)]


def _orth_cross(s: tuple, t: tuple) -> bool:
    """Whether a horizontal and a vertical segment cross strictly inside both.

    Args:
        s: ((x, y), (x, y)) segment.
        t: ((x, y), (x, y)) segment.

    Returns:
        True on a crossing; parallel segments never count.
    """
    (p, q), (r, w) = s, t
    sh, th = p[1] == q[1], r[1] == w[1]
    if sh == th:
        return False
    (h1, h2), (v1, v2) = ((p, q), (r, w)) if sh else ((r, w), (p, q))
    x, y = v1[0], h1[1]
    return min(h1[0], h2[0]) < x < max(h1[0], h2[0]) and min(v1[1], v2[1]) < y < max(v1[1], v2[1])


def group_cost(cells: dict, pairs: dict) -> float:
    """How tangled the thick arrows are for this placement: crossings of their channel paths (channel_path; weighted by the dependencies
    each carries), plus a small length term and a penalty per row an arrow skips (it then needs a column channel).

    Args:
        cells: {group name: (row, column)}.
        pairs: {(group name, group name): dependency count}.

    Returns:
        The cost; lower is better.
    """
    paths = [(channel_path(cells[a], cells[b]), n) for (a, b), n in pairs.items() if a in cells and b in cells]
    segs = [[(pts[i], pts[i + 1]) for i in range(len(pts) - 1)] for pts, _ in paths]
    cross = 0
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            hits = sum(1 for s in segs[i] for u in segs[j] if _orth_cross(s, u))
            cross += hits * paths[i][1] * paths[j][1]
    length = sum(n * (abs(cells[a][0] - cells[b][0]) + abs(cells[a][1] - cells[b][1])) for (a, b), n in pairs.items() if a in cells and b in cells)
    skip = sum(n * max(abs(cells[a][0] - cells[b][0]) - 1, 0) for (a, b), n in pairs.items() if a in cells and b in cells)
    return cross + 0.1 * length + 0.5 * skip


def _climb(cells: dict, pinned: set, pairs: dict, ncol: int) -> dict:
    """One hill climb: move unpinned groups between cells (swaps with each other or into empty cells) while group_cost falls; first
    improvement, at most 30 passes. Pinned groups (the map's drawing.group_cell) never move.

    Args:
        cells: {group name: (row, column)} from grid_cells.
        pinned: names the map places itself.
        pairs: {(group name, group name): dependency count}.
        ncol: groups per grid row.

    Returns:
        The improved {group name: (row, column)}.
    """
    cells = dict(cells)
    nrow = max((r for r, _ in cells.values()), default=0) + 1
    spots = [(r, c) for r in range(nrow) for c in range(ncol)]
    free = [n for n in cells if n not in pinned]
    best = group_cost(cells, pairs)
    for _ in range(30):
        better = False
        for n in free:
            for spot in spots:
                if cells[n] == spot:
                    continue
                owner = next((m for m, cl in cells.items() if cl == spot), None)
                if owner in pinned:
                    continue
                old = cells[n]
                cells[n] = spot
                if owner:
                    cells[owner] = old
                cost = group_cost(cells, pairs)
                if cost < best - 1e-9:
                    best, better = cost, True
                else:
                    cells[n] = old
                    if owner:
                        cells[owner] = spot
        if not better:
            break
    # keep the grid compact: drop rows the moves left empty
    used = sorted({r for r, _ in cells.values()})
    remap = {r: i for i, r in enumerate(used)}
    return {n: (remap[r], c) for n, (r, c) in cells.items()}


def e2e_edges(data: dict, comps: dict) -> list[tuple[str, str]]:
    """Every arrow an E2E page draws between two different boxes: step to step, and a flow's runs_on to its first actor.

    Args:
        data: the page's map (flows).
        comps: {component id: component} on the page.

    Returns:
        (from component, to component) pairs, repeated per arrow.
    """
    out = []
    for f in data["flows"]:
        acts = [s["actor"] for s in f["steps"]]
        if acts and f.get("runs_on") in comps and f["runs_on"] != acts[0]:
            out.append((f["runs_on"], acts[0]))
        out += [(a, b) for a, b in zip(acts, acts[1:]) if a != b]
    return out


def grid_crossings(edges: list, row: dict, colof: dict) -> int:
    """Crossings the E2E grid implies, before routing: arrows between the same two columns whose ends swap order; arcs inside one column
    (drawn in the channel on its right) that interleave; an arc crossed by an arrow leaving that column to the right between its ends.

    Args:
        edges: (from, to) component pairs.
        row: {component id: row}.
        colof: {component id: column}.

    Returns:
        The count.
    """
    inter, intra = [], []
    for a, b in edges:
        if a not in row or b not in row:
            continue
        if colof[a] == colof[b]:
            intra.append((colof[a], min(row[a], row[b]), max(row[a], row[b])))
        else:
            (ca, ra), (cb, rb) = sorted(((colof[a], row[a]), (colof[b], row[b])))
            inter.append((ca, cb, ra, rb))
    n = 0
    for i, (c1, d1, r1, s1) in enumerate(inter):
        n += sum(1 for c2, d2, r2, s2 in inter[i + 1:] if (c1, d1) == (c2, d2) and (r1 - r2) * (s1 - s2) < 0)
    for i, (k1, lo1, hi1) in enumerate(intra):
        n += sum(1 for k2, lo2, hi2 in intra[i + 1:] if k1 == k2 and (lo1 < lo2 < hi1 < hi2 or lo2 < lo1 < hi2 < hi1))
        n += sum(1 for c, d, r, s in inter if c == k1 and lo1 < r < hi1)
    return n


def column_search(cols: list, row: dict, colof: dict, edges: list) -> None:
    """Swap boxes inside each E2E column while that lowers grid_crossings (first improvement, at most 20 passes); rows change in place.

    Args:
        cols: component ids per column.
        row: {component id: row}, updated.
        colof: {component id: column}.
        edges: (from, to) pairs from e2e_edges.
    """
    best = grid_crossings(edges, row, colof)
    for _ in range(20):
        better = False
        for col in cols:
            for i in range(len(col)):
                for j in range(i + 1, len(col)):
                    a, b = col[i], col[j]
                    row[a], row[b] = row[b], row[a]
                    n = grid_crossings(edges, row, colof)
                    if n < best:
                        best, better = n, True
                    else:
                        row[a], row[b] = row[b], row[a]
        if not better:
            break


def group_candidates(cells: dict, pinned: set, pairs: dict, ncol: int, restarts: int = 24) -> list:
    """Distinct placements worth routing: the map's own, its hill climb, and the climbs from `restarts` seeded shuffles of the unpinned
    groups (Graphviz and ELK run the ordering from several starts). group_cost only ranks them; the overview routes each and keeps the
    one whose real thick arrows cross least, so a proxy that misjudges a route cannot make the drawing worse than the map's own placement.

    Args:
        cells: {group name: (row, column)} from grid_cells.
        pinned: names the map places itself.
        pairs: {(group name, group name): dependency count}.
        ncol: groups per grid row.
        restarts: shuffled starts tried besides the map's own placement.

    Returns:
        Distinct placements, the map's own first, then by group_cost.
    """
    rng = random.Random(20261028)
    free = [n for n in cells if n not in pinned]
    found = [dict(cells), _climb(cells, pinned, pairs, ncol)]
    for _ in range(restarts):
        spots = [cells[n] for n in free]
        rng.shuffle(spots)
        start = dict(cells)
        start.update(zip(free, spots))
        found.append(_climb(start, pinned, pairs, ncol))
    out, seen = [], set()
    for c in [found[0]] + sorted(found[1:], key=lambda c: group_cost(c, pairs)):
        key = tuple(sorted(c.items()))
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def shared_runs(lines: list) -> int:
    """Pairs of runs from different polylines lying along each other: parallel, closer than 8 px and overlapping by more than 2 px (the rule
    of scripts/count_crossings.alongside, which measures the drawn file).

    Args:
        lines: polylines, [[(x, y), ...], ...].

    Returns:
        The count over every pair of polylines.
    """
    def along(p: tuple, q: tuple) -> bool:
        """Whether two horizontal or two vertical runs lie along each other.

        Args:
            p: one run.
            q: the other.

        Returns:
            True for parallel runs closer than 8 px that overlap by more than 2 px.
        """
        (a, b), (c, d) = p, q
        for k in (1, 0):   # horizontal runs (same y), then vertical (same x)
            if a[k] == b[k] and c[k] == d[k] and abs(a[k] - c[k]) < 8:
                return max(min(a[1 - k], b[1 - k]), min(c[1 - k], d[1 - k])) < min(max(a[1 - k], b[1 - k]), max(c[1 - k], d[1 - k])) - 2
        return False
    runs = [list(zip(pts, pts[1:])) for pts in lines]
    return sum(along(p, q) for i in range(len(runs)) for j in range(i + 1, len(runs)) for p in runs[i] for q in runs[j])


def routed_crossings(ov) -> tuple[int, int]:
    """Crossings and shared runs between the thick arrows as the overview routes them now (their real polylines, not a proxy).

    Args:
        ov: the flowmap.overview.Overview being laid out.

    Returns:
        (segment crossings between different thick arrows, pairs of their runs lying along each other).
    """
    ov.gpos = {gi: (ov.col_left[ov.gcol[gi]] + (ov.col_w[ov.gcol[gi]] - gl.width) / 2, ov.row_top[ov.grow[gi]], gl.width,
                      ov.gh_of[gi]) for gi, gl in ov.lay.items()}
    frac = ov._ends()
    row_bot = [ov.row_top[r] + ov.row_h[r] for r in range(ov.nrow)]
    lines = [ov._thick_points(p, frac, row_bot) for p in ov.plans]
    segs = [list(zip(pts, pts[1:])) for pts in lines]
    n = sum(1 for i in range(len(segs)) for j in range(i + 1, len(segs)) for s in segs[i] for t in segs[j] if crossing(s, t) is not None)
    return n, shared_runs(lines)

def best_cells(ov) -> None:
    """overview_group_search (operator, 2026-10-28): route each candidate placement from group_candidates and keep the one whose thick
    arrows really cross least without more shared runs than the map's own placement (2026-10-29: UNC's 245 -> 130 had merged two pairs of
    thick arrows); the map's own placement is a candidate, so the result is never worse. Pinned groups never move.

    Args:
        ov: the flowmap.overview.Overview being laid out; re-placed in place.
    """
    best, (best_n, limit) = ov.cells0, routed_crossings(ov)
    for cells in group_candidates(ov.cells0, set(ov.profile.group_cells), cross_pairs(ov), ov.ncol)[1:]:
        ov._place_cells(cells)
        ov._plan()
        ov._grid()
        n, shared = routed_crossings(ov)
        if n < best_n and shared <= limit:
            best, best_n = cells, n
    ov._place_cells(best)
    ov._plan()
    ov._grid()


def cross_pairs(ov) -> dict:
    """Thick-arrow group pairs by name and how many dependencies each carries, as the overview's _plan counts them.

    Args:
        ov: the flowmap.overview.Overview being laid out.

    Returns:
        {(group name, group name): dependency count}.
    """
    out: dict[tuple[str, str], int] = {}
    for c in ov.data["components"]:
        for d in c.get("depends_on", []):
            ga, gb = ov.gnames[ov.gof[c["id"]]], ov.gnames[ov.gof[d]]
            if ga != gb:
                out[(ga, gb)] = out.get((ga, gb), 0) + 1
    return out
