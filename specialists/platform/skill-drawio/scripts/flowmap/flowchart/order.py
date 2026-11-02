"""Choose which way out each diamond uses by measuring: on a lane page, try a two-way diamond's arrows both ways round and keep what draws fewer crossings,
then fewer bends, then less ink (operator, 2026-11-02: swap the branches to reduce overlaps). Stdlib only.

Imported, not run: `from flowmap.flowchart.order import improve_branches` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import crossing, segments


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
