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


def improve_tracks(chart: object, draw: object) -> None:
    """Reverse the track order of a gap a diamond's branches share, alone or with the branches swapped, where that scores better.

    Swapping a diamond's branches (improve_branches) cannot uncross two branches that run through the same gap on tracks in the crossing order:
    each order of the branches then still crosses (operator, 2026-11-11: "those arrows could have been swapped"). Reversing that gap's tracks
    is the other half of the same swap.

    Args:
        chart: the flowmap.flowchart.page.Chart; its `reversed_gaps` change.
        draw: a function returning every arrow's polyline as the chart stands.
    """
    from .route import plan_gaps   # here, not at the top: route imports nothing from order, and page imports both
    best = score(draw())
    for nid in chart.graph.steps:
        out = [e for e in chart.graph.edges if e.src == nid and e.kind != "stop"]
        if len(out) < 2:
            continue
        legs = plan_gaps(chart)[0]
        gaps = {gap for e in out for gap, _a, _b in legs.get((e.src, e.dst), [])}
        shared = [g for g in sorted(gaps) if sum(any(gap == g for gap, _a, _b in legs.get((e.src, e.dst), [])) for e in out) > 1]
        two = {e.index: e for e in out}
        swappable = set(two) == {0, 1}
        for g in shared:
            keep = (chart.reversed_gaps, two[0].index if swappable else None)
            tries = [(True, False)] + ([(True, True), (False, True)] if swappable else [])   # reverse; reverse and swap; swap
            for rev, swap in tries:
                chart.reversed_gaps = keep[0] ^ ({g} if rev else set())
                if swappable:
                    two[0].index, two[1].index = (1, 0) if swap else (0, 1)
                now = score(draw())
                if now < best:
                    best, keep = now, (chart.reversed_gaps, two[0].index if swappable else None)
            chart.reversed_gaps = keep[0]
            if swappable:
                two[0].index, two[1].index = keep[1], 1 - keep[1]

