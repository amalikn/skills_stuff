"""A flowchart's arrows before any y is known: which horizontal runs each arrow needs in the gaps between rows, and a track for each run. Stdlib only.

Split from flowmap.flowchart.page to keep that module within its size budget. An arrow runs down a column, sideways along a track in a gap, and an
arrow back to an earlier step up a channel right of the columns.

Imported, not run: `from flowmap.flowchart.route import plan_gaps, assign_tracks` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

#: Track pitch in a gap (room for the arrows' hops) and channel spacing for arrows back up.
TRACK, CHANNEL = 18, 18
#: The room above a box for an arrowhead, and the height of a row only long arrows pass through.
HEAD_ROOM, EMPTY_ROW = 44, 56
#: How far an entry moves along a box's top to clear another arrow.
NUDGE = 30


def _gutter_busy(chart: object, row: int, col: int) -> bool:
    """Whether a long arrow already passes through a cell.

    Args:
        chart: the flowmap.flowchart.page.Chart.
        row: the cell's row.
        col: its column.

    Returns:
        True when a chain holds the cell.
    """
    return any((row, col) in cells for cells in chart.grid.chains.values())


def exit_point(chart: object, edge: object) -> tuple[bool, float]:
    """How an arrow leaves its node: the second arrow and a stop leave by the side, through the cell reserved beside it.

    Args:
        chart: the flowmap.flowchart.page.Chart.
        edge: the arrow.

    Returns:
        (leaves by the side, the x it carries into the gap below).
    """
    c = chart.grid.cols[edge.src]
    if chart.lanes is None:
        if edge.kind == "main" and edge.index > 1 and c == 0:
            return True, chart.third_x   # a third way out takes the left corner: two arrows never share an exit (operator, 2026-11-02)
        side = edge.kind == "stop" or edge.index == 1
    else:   # a stop sits straight below its step, so the way on takes the lane's gutter
        side = edge.kind != "stop" and (edge.index == 1 or f"__stop-{edge.src}" in chart.graph.stops)
        rows = chart.grid.rows
        if edge.index > 1 and edge.kind != "stop" and c > 0 and not _gutter_busy(chart, rows[edge.src], c - 1):
            return True, chart.cx[c - 1]   # a third way out takes the left corner: the bottom is the first's, and two there leave no room for a label
        level_in = any(e.dst == edge.src and e.kind == "main" and rows[e.src] == rows[e.dst] for e in chart.graph.edges)
        if side and edge.kind == "main" and chart.grid.cols[edge.dst] < c and not level_in and not _gutter_busy(chart, rows[edge.src], c - 1):
            return True, chart.cx[c - 1]   # heading left: out by the left, down the gutter of the lane before, so it crosses nothing of its own
    return side, chart.cx[c + 1 if side else c]


def plan_gaps(chart: object) -> tuple[dict, dict]:
    """Every horizontal run an arrow needs, by gap, and each arrow's route as x positions per gap.

    Args:
        chart: the chart.

    Returns:
        (legs, entries): legs is {edge key: [(gap row, x from, x to)]}; entries is {edge key: entry x at the target's top}.
    """
    g, grid = chart.graph, chart.grid
    forward = [e for e in g.edges if e.kind == "main" and (e.src, e.dst) not in chart.left and grid.rows[e.src] != grid.rows[e.dst]]
    backs = [e for e in g.edges if e.kind == "back" and (e.src, e.dst) not in chart.left]
    arrival = {}
    for e in forward + backs:
        cells = grid.chains.get((e.src, e.dst))
        x = chart.channel_x if e.kind == "back" else chart.cx[cells[-1][1]] if cells else exit_point(chart, e)[1]
        arrival.setdefault(e.dst, []).append((e.src, x))
    ports = {dst: chart.port_in(dst, inc) for dst, inc in arrival.items()}
    legs, entries, channels = {}, {}, {}
    for e in forward:
        key = (e.src, e.dst)
        x, runs = exit_point(chart, e)[1], []
        for row, col in grid.chains.get(key, []):
            if x != chart.cx[col]:
                runs.append((row - 1, x, chart.cx[col]))
            x = chart.cx[col]
        entry = ports[e.dst][e.src]
        if x != entry:
            runs.append((grid.rows[e.dst] - 1, x, entry))
        legs[key], entries[key] = runs, entry
    for n, e in enumerate(backs):
        key = (e.src, e.dst)
        channels[key] = chart.channel_x + CHANNEL * n
        entry = ports[e.dst][e.src]
        legs[key] = [(grid.rows[e.src], exit_point(chart, e)[1], channels[key]), (grid.rows[e.dst] - 1, channels[key], entry)]
        entries[key] = entry
    chart.channels = channels
    nudge_arrivals(chart, legs, entries)
    return legs, entries


def left_channels(graph: object, grid: object) -> dict:
    """Arrows that stay beside the main column: within the first column, a side exit or an arrow back up. Each leaves by one side of its box, runs down or
    up a channel on that side and enters the target's same side, so a skip or a retry needs no track (operator, 2026-11-02: half left, half right).

    Args:
        graph: the chart's graph.
        grid: its grid.

    Returns:
        {(src, dst): (side, channel, 0 nearest the boxes)}; arrows whose rows overlap take different channels.
    """
    picked = [e for e in graph.edges if e.kind != "stop" and (e.kind == "back" or e.index == 1) and grid.cols[e.src] == 0 == grid.cols[e.dst]]
    sources = {e.src for e in picked}
    picked = [e for e in picked if e.dst not in sources]   # one left side cannot both take an arrow in and send one out: that one stays on the right
    spans = sorted(picked, key=lambda e: abs(grid.rows[e.src] - grid.rows[e.dst]))
    taken: dict = {"left": [], "right": []}
    busy = {e.src for e in graph.edges if e.kind == "stop" or (e.index == 1 and (e.src, e.dst) not in {(p.src, p.dst) for p in picked})}
    out = {}
    for e in spans:
        lo, hi = sorted((grid.rows[e.src], grid.rows[e.dst]))
        free = {side: next((i for i, used in enumerate(tracks) if all(hi < a or lo > b for a, b in used)), len(tracks)) for side, tracks in taken.items()}
        # The nearer free channel, so overlapping arrows split left and right; the right needs both boxes' right sides free of stops.
        side = "right" if free["right"] < free["left"] and not {e.src, e.dst} & busy else "left"
        if free[side] == len(taken[side]):
            taken[side].append([])
        taken[side][free[side]].append((lo, hi))
        out[(e.src, e.dst)] = (side, free[side])
    return out


def leave_before_arrive(runs: list) -> list:
    """A gap's runs, each run that leaves an x before any run arriving there, so its track is higher and the two share no vertical. Short runs first
    among equals. A cycle is left in length order: plan_gaps() has moved the arrival of any box it can.

    Args:
        runs: [(edge key, x from, x to)].

    Returns:
        The runs in track order.
    """
    left, out = sorted(runs, key=lambda r: (abs(r[1] - r[2]), r[1])), []
    while left:
        ready = next((r for r in left if not any(o is not r and o[1] == r[2] for o in left)), left[0])
        left.remove(ready)
        out.append(ready)
    return out


def nudge_arrivals(chart: object, legs: dict, entries: dict) -> None:
    """Move an arrow sideways where another arrow in that gap leaves from the x it arrives at, so the two cannot share a vertical: along a box's top, or
    along the column in the middle of a long arrow. This also breaks a cycle no track order can.

    Args:
        chart: the flowmap.flowchart.page.Chart.
        legs: plan_gaps()'s legs, changed in place.
        entries: plan_gaps()'s entries, changed in place.
    """
    leaving = {(g, x, k) for k, others in legs.items() for g, x, _ in others}
    for key, runs in legs.items():
        for i, (gap, a, b) in enumerate(runs):
            if not any(g == gap and x == b and k != key for g, x, k in leaving):
                continue
            if i + 1 < len(runs) and runs[i + 1][1] == b:   # the middle of a long arrow: carry the move into its next run
                runs[i], runs[i + 1] = (gap, a, b + NUDGE), (runs[i + 1][0], b + NUDGE, runs[i + 1][2])
            elif i + 1 == len(runs) and chart.shapes.get(key[1], "terminator") not in ("decision", "terminator"):
                runs[i], entries[key] = (gap, a, b + NUDGE), b + NUDGE


def assign_tracks(legs: dict, reversed_gaps: frozenset = frozenset()) -> dict:
    """A track per horizontal run: runs that overlap take different tracks, and a run leaving an x sits above a run arriving at the same x, so
    the two arrows do not share that vertical. A gap in `reversed_gaps` takes its tracks in the opposite order, which can uncross two branches
    of one diamond that share the gap (flowmap.flowchart.order.improve_tracks; operator, 2026-11-11).

    Args:
        legs: plan_gaps()'s legs.
        reversed_gaps: gap rows whose track order is reversed.

    Returns:
        {(edge key, gap row, x from): track}, and under the key `"count"` {gap row: tracks used}.
    """
    by_gap: dict[int, list] = {}
    for key, runs in legs.items():
        for gap, a, b in runs:
            by_gap.setdefault(gap, []).append((key, a, b))
    out: dict = {"count": {}}
    for gap, runs in by_gap.items():
        used: list[list[tuple]] = []
        for key, a, b in leave_before_arrive(runs):
            lo, hi = min(a, b) - 8, max(a, b) + 8
            floor = 1 + max([t for t, track in enumerate(used) if any(leave == b for _, _arrive, leave in track)], default=-1)
            t = next((i for i in range(floor, len(used)) if all(hi < u[0] or lo > u[1] for u, *_ in used[i])), None)
            if t is None:
                used += [[] for _ in range(max(floor - len(used), 0) + 1)]
                t = len(used) - 1
            used[t].append(((lo, hi), b, a))
            out[(key, gap, a)] = t
        out["count"][gap] = len(used)
        if gap in reversed_gaps:
            for k in [k for k in out if k != "count" and k[1] == gap]:
                out[k] = len(used) - 1 - out[k]
    return out


def row_spans(chart: object, tracks: dict, top: float) -> dict:
    """Each row's top and height, and each gap's first track.

    Args:
        chart: the chart.
        tracks: assign_tracks()'s result.
        top: the first row's top.

    Returns:
        {"top": {row: y}, "h": {row: height}, "track": {gap row: y}}.
    """
    rows = chart.grid.rows
    last = max(rows.values())
    tops, heights, track_y, y = {}, {}, {}, top
    for r in range(last + 1):
        heights[r] = max((chart.size[n][1] for n in chart.graph.order if rows[n] == r), default=EMPTY_ROW)   # a lane can leave a row to long arrows alone
        tops[r] = y
        track_y[r] = y + heights[r] + chart.label_room
        y += heights[r] + chart.label_room + max(tracks["count"].get(r, 1) - 1, 0) * TRACK + HEAD_ROOM
    return {"top": tops, "h": heights, "track": track_y, "bottom": y}


def node_rect(chart: object, ys: dict, nid: str) -> tuple[float, float, float, float]:
    """A node's box, centred on its cell.

    Args:
        chart: the chart.
        ys: row_spans()'s result.
        nid: the node id.

    Returns:
        (x, y, width, height).
    """
    r, (w, h) = chart.grid.rows[nid], chart.size[nid]
    return chart.cx[chart.grid.cols[nid]] - w / 2, ys["top"][r] + (ys["h"][r] - h) / 2, w, h
