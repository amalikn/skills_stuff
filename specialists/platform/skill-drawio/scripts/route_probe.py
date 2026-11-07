#!/usr/bin/env python3
"""Show why a flow page's arrows went where they did: each decision's branch-corner trials with their costs, then every arrow's final route. Read-only.

Why (2026-11-07): on smc-resiliency's commission-gps page a gate's branch to the step beside it left by the top. The router's trials showed it had
drawn the operator's layout (right and bottom) and that the uncross pass then traded it away; `--look uncross="off"` and `--look unshare="off"`
told the passes apart. Run it before changing routing logic, to see which stage made a choice.

Usage (from the project root, with the project's interpreter: PyYAML reads the map):
    route_probe.py --map docs/flows/flows.yaml --flow commission-gps [--schema docs/flows/flows.schema.json] [--look uncross="off"]
    (prints the arrows drawn straight first, each corner assignment tried for a decision's remaining branches, then each arrow's exit side and points)
Exit: 0 when the page was drawn, 1 when the map cannot be read or the flow is unknown, 2 on bad arguments.
Runtime: about a second for one page.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import permutations
from pathlib import Path

from flowmap import model, routing
from flowmap.pages import flow_page
from flowmap.uncross import _side

#: The oldest Python this script runs on.
REQUIRES_PYTHON = (3, 11)


def trials(page: object, branches: list, corridors: dict, used: dict) -> list[tuple[tuple, list[float]]]:
    """Every corner assignment for one decision's branches and each branch's cost, the page left as it was.

    Args:
        page: the page being routed.
        branches: (edge, target is a decision) per branch, as routing.route_branches takes them.
        corridors: as for routing.route_forward.
        used: points and sides already taken.

    Returns:
        [(the exit sides in branch order, each branch's cost)].
    """
    out = []
    for ways in permutations(("right", "top", "bottom"), len(branches)):
        mark = routing._mark(page, used)
        out.append((ways, [routing.route_forward(page, e, (True, d), corridors, used, (w,), True) for (e, d), w in zip(branches, ways)]))
        routing._undo(page, used, mark)
    return out


def probe(flow: dict, comps: dict, profile: object) -> tuple[list[str], object]:
    """Render one flow page while recording each decision's trials.

    Args:
        flow: the flow from the map.
        comps: every component by id.
        profile: the drawing profile (look keys applied).

    Returns:
        (trial lines, the rendered page).
    """
    lines, real = [], routing.route_branches

    def spy(page: object, branches: list, corridors: dict, used: dict) -> None:
        """Record the trials, then route as the engine does.

        Args:
            page: the page being routed.
            branches: the decision's branches.
            corridors: as for routing.route_forward.
            used: points and sides already taken.
        """
        names = [e[3].replace("\n", " ") for e, _d in branches]
        for ways, costs in trials(page, branches, corridors, used):
            lines.append(f"  {branches[0][0][1]}: {names} {ways} costs={[round(c, 1) for c in costs]} total={round(sum(costs), 1)}")
        real(page, branches, corridors, used)

    first = routing.straight_first

    def pinned(*args: object) -> dict:
        """Record the arrows drawn straight before any trial (look.straight_first), then return them.

        Args:
            *args: routing.straight_first's arguments.

        Returns:
            What routing.straight_first returns.
        """
        drawn = first(*args)
        lines.extend(f"  straight first: {cid}" for cid in drawn)
        return drawn

    routing.route_branches, routing.straight_first = spy, pinned
    try:
        page = flow_page(flow, comps, 1, profile)
    finally:
        routing.route_branches, routing.straight_first = real, first
    return lines, page


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        The exit status: 0 drawn, 1 an unreadable map or unknown flow, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--map", required=True)
    ap.add_argument("--flow", required=True, help="the flow id")
    ap.add_argument("--schema", default="")
    ap.add_argument("--look", action="append", default=[], metavar="KEY=JSON", help='a look key for this run, e.g. uncross="off"')
    args = ap.parse_args(argv)
    import render_flowmap   # the front end builds the project's profile from the map's drawing block
    root = Path(".")
    profile = render_flowmap.profile_for(root, args.map, args.schema or str(render_flowmap.SCHEMA), "")
    for pair in args.look:
        key, _, value = pair.partition("=")
        profile.look[key] = json.loads(value)
    data, problems = model.load(root, profile)
    if problems or data is None:
        print("\n".join(f"map: {p}" for p in problems) or "map: cannot be read")
        return 1
    flow = next((f for f in data["flows"] if f["id"] == args.flow), None)
    if flow is None:
        print(f"no flow {args.flow!r}")
        return 1
    lines, page = probe(flow, {c["id"]: c for c in data["components"]}, profile)
    print(f"router choices ({len(lines)}):", *lines, sep="\n")
    print("routes:")
    for r in page.routes:
        print(f"  {r.cid}: leaves {_side(r.points[0], page.rects[r.src])}, {[tuple(round(v) for v in p) for p in r.points]}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
