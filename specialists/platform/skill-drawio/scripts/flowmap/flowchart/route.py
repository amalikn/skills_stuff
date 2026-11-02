"""A flowchart's arrows before any y is known: which horizontal runs each arrow needs in the gaps between rows, and a track for each run. Stdlib only.

Split from flowmap.flowchart.page to keep that module within its size budget. An arrow runs down a column, sideways along a track in a gap, and an
arrow back to an earlier step up a channel right of the columns.

Imported, not run: `from flowmap.flowchart.route import plan_gaps, assign_tracks` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

#: Track pitch in a gap (room for the arrows' hops) and channel spacing for arrows back up.
TRACK, CHANNEL = 18, 18
#: How far an entry moves along a box's top to clear another arrow.
NUDGE = 30


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
        side = edge.kind == "stop" or edge.index == 1
    else:   # a stop sits straight below its step, so the way on takes the lane's gutter
        side = edge.kind != "stop" and (edge.index == 1 or f"__stop-{edge.src}" in chart.graph.stops)
    return side, chart.cx[c + 1 if side else c]


def plan_gaps(chart: object) -> tuple[dict, dict]:
    """Every horizontal run an arrow needs, by gap, and each arrow's route as x positions per gap.

    Args:
        chart: the chart.

    Returns:
        (legs, entries): legs is {edge key: [(gap row, x from, x to)]}; entries is {edge key: entry x at the target's top}.
    """
    g, grid = chart.graph, chart.grid
    forward = [e for e in g.edges if e.kind == "main" and (e.src, e.dst) not in chart.left]
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
    """Arrows that take the left side: within the first column, a side exit or an arrow back up. They leave by the box's left, run down or up a channel
    left of the column and enter the target's left, so a skip or a retry stays beside the main path and no track or right channel is needed.

    Args:
        graph: the chart's graph.
        grid: its grid.

    Returns:
        {(src, dst): channel, 0 nearest the boxes}; arrows whose rows overlap take different channels.
    """
    picked = [e for e in graph.edges if e.kind != "stop" and (e.kind == "back" or e.index == 1) and grid.cols[e.src] == 0 == grid.cols[e.dst]]
    sources = {e.src for e in picked}
    picked = [e for e in picked if e.dst not in sources]   # one left side cannot both take an arrow in and send one out: that one stays on the right
    spans = sorted(picked, key=lambda e: abs(grid.rows[e.src] - grid.rows[e.dst]))
    taken: list[list[tuple]] = []
    out = {}
    for e in spans:
        lo, hi = sorted((grid.rows[e.src], grid.rows[e.dst]))
        k = next((i for i, used in enumerate(taken) if all(hi < a or lo > b for a, b in used)), None)
        if k is None:
            taken.append([])
            k = len(taken) - 1
        taken[k].append((lo, hi))
        out[(e.src, e.dst)] = k
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


def assign_tracks(legs: dict) -> dict:
    """A track per horizontal run: runs that overlap take different tracks, and a run leaving an x sits above a run arriving at the same x, so
    the two arrows do not share that vertical.

    Args:
        legs: plan_gaps()'s legs.

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
    return out
