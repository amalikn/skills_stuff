"""A flowchart's graph and grid, before any pixels: nodes and edges from a flow, then the layered layout's phases as pure functions. Stdlib only.

The phases are those of a layered (Sugiyama) drawing (Eclipse ELK's overview names them, documents/drawio-sources-20261102/): cycle breaking,
layer assignment, ordering, placement; flowmap.flowchart.page does the routing. Two choices fit a flow map: cycles break by map order (a step that
points at itself or an earlier step is a back edge, as on the flow pages, so the result never depends on a tie-break), and placement puts the
spine (the path from the start through each step's first target) straight down column 0, with branches to its right, which is how a person
draws a flowchart; with swimlanes each node keeps to its actor's column instead. A step needing room at its side (a decision's second branch, a stop box) reserves the cell to its right.

Imported, not run: `from flowmap.flowchart.graph import chart_graph, place, lane_map, stitched` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..model import step_targets
from .order import lane_order

START, END = "__start", "__end"


@dataclass
class Edge:
    """One arrow of the chart.

    Args:
        src: the source node id.
        dst: the target node id.
        kind: "main", "back" (to a step at or before its source) or "stop" (a step to its failure box).
        index: its position among the source's arrows (0 is the first target, which runs straight down).
    """

    src: str
    dst: str
    kind: str = "main"
    index: int = 0


@dataclass
class Graph:
    """A flow as nodes and edges.

    Args:
        order: every node id in drawing order (start, the steps in map order, end).
        steps: each step by id.
        edges: every arrow.
        stops: {stop node id: the step it belongs to}.
    """

    order: list[str]
    steps: dict[str, dict]
    edges: list[Edge]
    stops: dict[str, str] = field(default_factory=dict)


@dataclass
class Grid:
    """The placed chart.

    Args:
        rows: each node's row.
        cols: each node's column.
        chains: {(src, dst): [(row, col)]} the cells a long forward arrow passes through.
    """

    rows: dict[str, int]
    cols: dict[str, int]
    chains: dict[tuple[str, str], list[tuple[int, int]]]


def is_decision(step: dict, targets: list[str]) -> bool:
    """Whether a step draws as a diamond: it says so, it is a gate, or it leads to more than one place.

    Args:
        step: the step from the map.
        targets: where it leads.

    Returns:
        True for a decision; an explicit other shape wins.
    """
    return step.get("shape", "decision") == "decision" and (bool(step.get("gate")) or len(targets) > 1 or step.get("shape") == "decision")


def chart_graph(flow: dict) -> Graph:
    """The chart's nodes and edges: a start, the steps, one end unless every path ends in a terminator step, and a stop box beside a step with
    failures (a decision with two or more ways out already draws its own failure path, so it gets none).

    Args:
        flow: the flow from the map.

    Returns:
        The graph.
    """
    steps = flow["steps"]
    index = {s["id"]: k for k, s in enumerate(steps)}
    edges, stops, sinks = [Edge(START, steps[0]["id"])], {}, []
    for k, s in enumerate(steps):
        targets = step_targets(steps, k)
        edges += [Edge(s["id"], t, "back" if index[t] <= k else "main", i) for i, t in enumerate(targets)]
        if not targets and s.get("shape") != "terminator":
            sinks.append(s["id"])
        if s.get("failures") and len(targets) < 2:
            stops[f"__stop-{s['id']}"] = s["id"]
            edges.append(Edge(s["id"], f"__stop-{s['id']}", "stop", len(targets)))
    edges += [Edge(sid, END) for sid in sinks]
    return Graph([START] + [s["id"] for s in steps] + ([END] if sinks else []) + list(stops), {s["id"]: s for s in steps}, edges, stops)


def lane_map(graph: Graph) -> tuple[dict[str, int], list[str]]:
    """Swimlanes: each node's lane, one per actor in the order that keeps hand-offs short (flowmap.flowchart.order); the start and end sit with the step
    next to them, a stop with its step.

    Args:
        graph: the graph.

    Returns:
        ({node id: lane index}, [actor id per lane]).
    """
    actors = lane_order(list(dict.fromkeys(s["actor"] for s in graph.steps.values())),
                        [(graph.steps[e.src]["actor"], graph.steps[e.dst]["actor"]) for e in graph.edges if e.src in graph.steps and e.dst in graph.steps])
    lanes = {sid: actors.index(s["actor"]) for sid, s in graph.steps.items()}
    lanes[START] = lanes[next(iter(graph.steps))]
    for e in graph.edges:
        if e.dst == END:
            lanes[END] = lanes[e.src]
    return lanes | {stop: lanes[sid] for stop, sid in graph.stops.items()}, actors


def _beside(graph: Graph, nid: str, rows: dict, lanes: dict, used: set) -> int | None:
    """The row of a node that can sit level with its parent: a plain hand-off to a lane on the right, with every lane between free, runs sideways instead
    of stepping down (operator, 2026-11-02: it can span horizontally and vertically wherever it makes sense).

    Args:
        graph: the graph.
        nid: the node.
        rows: the rows so far.
        lanes: {node id: lane}.
        used: the (row, lane) cells taken.

    Returns:
        The parent's row, or None when the node must go below.
    """
    into = [e for e in graph.edges if e.dst == nid and e.kind != "stop"]
    if len(into) != 1 or into[0].kind != "main" or into[0].src not in rows:
        return None
    src = into[0].src
    if sum(1 for e in graph.edges if e.src == src) != 1 or lanes[nid] <= lanes[src]:
        return None
    row = rows[src]
    return None if any((row, k) in used for k in range(lanes[src] + 1, lanes[nid] + 1)) else row


def layers(graph: Graph, lanes: dict | None = None) -> dict[str, int]:
    """Layer assignment: each node on the row after its deepest forward parent (longest path); a stop box on its step's row. With lanes, a node
    moves down until its lane is free on that row, so a lane never holds two boxes side by side.

    Args:
        graph: the graph. Forward edges follow map order, so one pass in that order sees every parent first.
        lanes: {node id: lane}, for swimlanes.

    Returns:
        {node id: row}.
    """
    rows, used = {START: 0}, {(0, (lanes or {}).get(START))}
    for nid in graph.order:
        if nid in graph.stops or nid in rows:
            continue
        parents = [rows[e.src] for e in graph.edges if e.dst == nid and e.kind == "main" and e.src in rows]
        row = 1 + max(parents, default=0)
        beside = _beside(graph, nid, rows, lanes, used) if lanes is not None else None
        if beside is not None:
            row = beside
            parent = next(e.src for e in graph.edges if e.dst == nid and e.kind == "main")
            used.update((row, k) for k in range(lanes[parent] + 1, lanes[nid]))
        while lanes is not None and (row, lanes[nid]) in used:
            row += 1
        rows[nid] = row
        used.add((row, (lanes or {}).get(nid)))
        stop = f"__stop-{nid}"
        if lanes is not None and stop in graph.stops:   # a lane holds one column of boxes: a stop goes under its step, never beside it (operator, 2026-11-02)
            rows[stop] = row + 1
            used.add((row + 1, lanes[nid]))
    return rows if lanes is not None else rows | {stop: rows[sid] for stop, sid in graph.stops.items()}


def spine(graph: Graph) -> list[str]:
    """The main path: from the start through each step's first forward target.

    Args:
        graph: the graph.

    Returns:
        The node ids on it, in order.
    """
    path, seen = [START], {START}
    while True:
        nxt = next((e.dst for e in graph.edges if e.src == path[-1] and e.kind == "main" and e.dst not in seen), None)
        if nxt is None:
            return path
        path.append(nxt)
        seen.add(nxt)


def _wants_side(graph: Graph, nid: str) -> bool:
    """Whether a node needs the cell to its right: its second arrow or its stop box leaves by that side.

    Args:
        graph: the graph.
        nid: the node id.

    Returns:
        True when an arrow with index 1, or a stop arrow, leaves it.
    """
    return any(e.src == nid and (e.kind == "stop" or e.index == 1) for e in graph.edges)


def _first_free(taken: set, row: int, col: int, width: int) -> int:
    """The first column at or right of `col` with `width` free cells on a row.

    Args:
        taken: the (row, col) cells in use.
        row: the row.
        col: the column wanted.
        width: the cells needed side by side.

    Returns:
        The column.
    """
    while any((row, col + k) in taken for k in range(width)):
        col += 1
    return col


def _wanted_col(graph: Graph, nid: str, cols: dict) -> int:
    """Where a node would like to sit: under its first placed parent, one to the right when it is that parent's second arrow.

    Args:
        graph: the graph.
        nid: the node id.
        cols: the columns placed so far.

    Returns:
        The column wanted (0 with no placed parent).
    """
    for e in graph.edges:
        if e.dst == nid and e.kind == "main" and e.src in cols:
            return cols[e.src] + (1 if e.index == 1 else 0)
    return 0


def lane_columns(count: int) -> list[int]:
    """Each lane's first column: one for its boxes and a gutter that only arrows use.

    Args:
        count: the number of lanes.

    Returns:
        The first column per lane, then one past the last.
    """
    return [2 * k for k in range(count + 1)]


def place(graph: Graph, lanes: dict | None = None, first_col: list[int] | None = None) -> Grid:
    """Ordering and placement, row by row from the top: the spine in column 0 (with lanes, each node in its lane's column), then each step under
    its parent, then long arrows' pass-through cells straight down where they can be. A stop box takes the cell its step reserved; in a lane it has its own row under the step.

    Args:
        graph: the graph.
        lanes: {node id: lane}, for swimlanes.
        first_col: lane_columns(), with `lanes`.

    Returns:
        The grid.
    """
    rows = layers(graph, lanes)
    main = [e for e in graph.edges if e.kind == "main"]
    cols, taken, on_spine = {}, set(), spine(graph)
    runs = {(e.src, e.dst): {r: None for r in range(rows[e.src] + 1, rows[e.dst])} for e in main if rows[e.dst] - rows[e.src] > 1}
    for row in range(max(rows.values()) + 1):
        here = [n for n in graph.order if rows[n] == row and (n not in graph.stops or lanes is not None)]
        for nid in sorted(here, key=lambda n: (n not in on_spine, _wanted_col(graph, n, cols))):
            width = 2 if _wants_side(graph, nid) else 1
            want = first_col[lanes[nid]] if lanes is not None else 0 if nid in on_spine else _wanted_col(graph, nid, cols)
            cols[nid] = _first_free(taken, row, want, width)
            taken.update((row, cols[nid] + k) for k in range(width))
            for stop, sid in graph.stops.items():
                if sid == nid and lanes is None:
                    cols[stop] = cols[nid] + 1
        for key, cells in runs.items():
            if row in cells:
                above = cells.get(row - 1)
                cells[row] = _first_free(taken, row, cols[key[0]] if above is None else above, 1)
                taken.add((row, cells[row]))
    return Grid(rows, cols, {k: sorted(v.items()) for k, v in runs.items()})


def swap_branches(graph: Graph, grid: Grid) -> None:
    """Send a decision's arrow straight down when its target sits below it: the second arrow swaps with the first when it stays in the column and lands
    sooner, so a stop under a diamond is not reached by a loop round the side (operator, 2026-11-02). Run after the labels are read, which follow the map.

    Args:
        graph: the graph; its edges' `index` change.
        grid: the placed chart.
    """
    for nid in graph.steps:
        out = {e.index: e for e in graph.edges if e.src == nid and e.kind != "stop"}
        first, second = out.get(0), out.get(1)
        if first is None or second is None or grid.cols[second.dst] != grid.cols[nid] or grid.rows[second.dst] <= grid.rows[nid]:
            continue
        if grid.cols[first.dst] != grid.cols[nid] or grid.rows[second.dst] < grid.rows[first.dst]:
            first.index, second.index = 1, 0


def stitched(fid: str, flows: list[dict]) -> dict:
    """Several flows as one (a change's flows, a family), each flow's last steps leading to the next flow's first.

    Args:
        fid: the id of the joined flow.
        flows: the flows in order.

    Returns:
        A flow with step ids `<flow>.<step>`; its title and trigger are the first flow's.
    """
    steps = []
    for n, f in enumerate(flows):
        ids = [s["id"] for s in f["steps"]]
        for k, s in enumerate(f["steps"]):
            targets = [f"{f['id']}.{t}" for t in step_targets(f["steps"], k)]
            if not targets and n + 1 < len(flows) and s.get("shape") != "terminator":
                targets = [f"{flows[n + 1]['id']}.{flows[n + 1]['steps'][0]['id']}"]
            when = {f"{f['id']}.{t}": v for t, v in s.get("when", {}).items() if t in ids}
            steps.append({**s, "id": f"{f['id']}.{s['id']}", "next": targets, **({"when": when} if when else {})})
    return {**flows[0], "id": fid, "steps": steps}
