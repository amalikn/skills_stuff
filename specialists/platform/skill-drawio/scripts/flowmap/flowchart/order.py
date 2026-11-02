"""Choose which way out each diamond uses by measuring: on a lane page, try a two-way diamond's arrows both ways round and keep what draws fewer crossings,
then fewer bends, then less ink (operator, 2026-11-02: swap the branches to reduce overlaps). Stdlib only.

Imported, not run: `from flowmap.flowchart.order import improve_branches` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from itertools import permutations

from drawio.audit import crossing, segments

#: Most lanes searched exhaustively; beyond this, neighbours are swapped while that helps.
EXHAUSTIVE = 8


def lane_cost(order: list[str], hops: list[tuple[str, str]]) -> tuple[int, int]:
    """How a lane order reads; lower is better.

    Args:
        order: the actors, left to right.
        hops: (from actor, to actor) per arrow.

    Returns:
        (total columns the arrows span, arrows heading left).
    """
    at = {a: k for k, a in enumerate(order)}
    return sum(abs(at[a] - at[b]) for a, b in hops), sum(at[b] < at[a] for a, b in hops)


def lane_order(actors: list[str], hops: list[tuple[str, str]]) -> list[str]:
    """The lane order with the shortest hand-offs (operator, 2026-11-02: choose the column order to improve the layout). The first actor stays leftmost,
    where the flow starts; ties keep first use, so the result never depends on chance.

    Args:
        actors: the actors in order of first use.
        hops: (from actor, to actor) per arrow.

    Returns:
        The actors, left to right.
    """
    if len(actors) < 3:
        return actors
    if len(actors) <= EXHAUSTIVE:
        return min(([actors[0], *rest] for rest in permutations(actors[1:])), key=lambda o: lane_cost(o, hops))
    order, better = list(actors), True
    while better:
        better = False
        for k in range(1, len(order) - 1):
            swapped = order[:k] + [order[k + 1], order[k]] + order[k + 2:]
            if lane_cost(swapped, hops) < lane_cost(order, hops):
                order, better = swapped, True
    return order


def score(lines: list[list]) -> tuple[int, int, float]:
    """How clean a set of arrows is; lower is better.

    Args:
        lines: each arrow's polyline.

    Returns:
        (crossings, bends, total length).
    """
    runs = [segments(pts) for pts in lines]
    hits = sum(crossing(s, t) is not None for i, a in enumerate(runs) for b in runs[i + 1:] for s in a for t in b)
    length = sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for a in runs for p, q in a)
    return hits, sum(len(a) - 1 for a in runs), length


def improve_branches(graph: object, draw: object) -> None:
    """Swap each two-way diamond's arrows where that scores better, one diamond at a time in map order.

    Args:
        graph: the chart's graph; its edges' `index` change.
        draw: a function returning every arrow's polyline as the graph stands.
    """
    best = score(draw())
    for nid in graph.steps:
        out = {e.index: e for e in graph.edges if e.src == nid and e.kind != "stop"}
        if set(out) != {0, 1}:
            continue
        out[0].index, out[1].index = 1, 0
        now = score(draw())
        if now < best:
            best = now
        else:
            out[0].index, out[1].index = 0, 1
