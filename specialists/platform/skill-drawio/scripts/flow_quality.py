#!/usr/bin/env python3
"""Report the quality of every flow page a map renders: layout-audit faults, arrow crossings and arrows that leave from one point. Read-only.

Why (2026-10-21): the operator reviewed flow pages one screenshot at a time and found overlaps the audit had not checked. After the router was
rebuilt, this scan ran over every flow page of smc-resiliency (7) and unified-network-controller (22) to prove none had a fault, a crossing or a
shared start before anyone looked; it is the check to run after any routing change and before showing a drawing.

Usage (from the project root, with the project's interpreter: PyYAML reads the map):
    flow_quality.py --map docs/flows/flows.yaml [--schema docs/flows/flows.schema.json] [--all]
    (prints one line per page with an issue, or every page with --all, then a total)
Exit: 0 when every page is clean, 1 when a page has an issue or the map cannot be read, 2 on bad arguments.
Runtime: about a second for 22 pages.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drawio.audit import crossing, faults, page_audit, segments
from flowmap import model
from flowmap.pages import flow_page

#: The oldest Python this script runs on.
REQUIRES_PYTHON = (3, 11)


def page_quality(page) -> dict:
    """One flow page's numbers.

    Args:
        page: a rendered flow page (drawio.mxfile.Page).

    Returns:
        {"faults": audit fault lines, "crossings": count of arrow crossings, "shared_starts": arrows leaving a point another arrow leaves}.
    """
    segs = {r.cid: segments(r.points) for r in page.routes}
    ids = list(segs)
    crosses = sum(1 for i, a in enumerate(ids) for b in ids[i + 1:] for s in segs[a] for t in segs[b] if crossing(s, t) is not None)
    starts: dict = {}
    for r in page.routes:
        starts.setdefault((r.src, tuple(round(v) for v in r.points[0])), []).append(r.cid)
    shared = sum(len(v) - 1 for v in starts.values() if len(v) > 1)
    return {"faults": faults(page_audit(page)), "crossings": crosses, "shared_starts": shared}


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        The exit status: 0 clean, 1 an issue or an unreadable map, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--map", required=True)
    ap.add_argument("--schema", default="")
    ap.add_argument("--all", action="store_true", help="print every page, not only those with an issue")
    args = ap.parse_args(argv)
    import render_flowmap   # the front end builds the project's profile from the map's drawing block
    root = Path(".")
    profile = render_flowmap.profile_for(root, args.map, args.schema, "")
    data, problems = model.load(root, profile)
    if problems or data is None:
        print("\n".join(f"map: {p}" for p in problems) or "map: cannot be read")
        return 1
    comps = {c["id"]: c for c in data["components"]}
    bad = 0
    for i, f in enumerate(data["flows"]):
        q = page_quality(flow_page(f, comps, i + 1, profile))
        issue = q["faults"] or q["crossings"] or q["shared_starts"]
        bad += bool(issue)
        if issue or args.all:
            print(f"{i + 1} {f['id']}: faults={len(q['faults'])} crossings={q['crossings']} shared-starts={q['shared_starts']}"
                  + (f" {q['faults'][:2]}" if q["faults"] else ""))
    print(f"flow pages: {len(data['flows'])}, with an issue: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
