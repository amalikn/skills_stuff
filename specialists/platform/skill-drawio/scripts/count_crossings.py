#!/usr/bin/env python3
"""Count where a drawing's arrows cross each other on one page: horizontal against vertical runs of their full paths. Read-only, stdlib only.

Why (2026-10-20): an engine change that is not byte-identical for a consumer must show the consumer's drawing got no worse. The layout audits
say clean or not; this gives the number to compare before and after (unified-network-controller's Overview thin arrows, `--prefix ov-d-`:
54 to 44 crossings with drawio.route.gap_order). Paths come from drawio.read, which resolves each arrow's ends on its boxes and any group offsets, so
arrows stored as waypoints only (the End-to-end page) are measured whole.

Usage:
    count_crossings.py FILE.drawio [--page 1] [--prefix ov-d-]
    (--prefix keeps only arrows whose id starts with it, e.g. `ov-d-` for the Overview's thin arrows; default every arrow on the page)
Exit: 0 when counted, 1 when the file or page cannot be read, 2 on bad arguments.
Runtime: well under a second on a 7-page drawing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drawio import read

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)


def cuts(h: tuple, v: tuple) -> bool:
    """Whether horizontal run h passes strictly through vertical run v.

    Args:
        h: ((x1, y1), (x2, y2)), counted only when y1 == y2.
        v: ((x1, y1), (x2, y2)), counted only when x1 == x2.

    Returns:
        True for a crossing inside both runs; touching ends and diagonal runs do not count.
    """
    (hx1, hy1), (hx2, hy2) = h
    (vx1, vy1), (vx2, vy2) = v
    return hy1 == hy2 and vx1 == vx2 and min(hx1, hx2) < vx1 < max(hx1, hx2) and min(vy1, vy2) < hy1 < max(vy1, vy2)


def crossings(runs: dict[str, list]) -> int:
    """How many times a run of one arrow crosses a run of another.

    Args:
        runs: {arrow id: [((x1, y1), (x2, y2)), ...]}.

    Returns:
        The count over every pair of arrows.
    """
    ids, n = sorted(runs), 0
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            n += sum(cuts(p, q) + cuts(q, p) for p in runs[a] for q in runs[b])
    return n


def page_runs(file_text: str, page: int, prefix: str) -> dict[str, list]:
    """Each arrow's straight runs on one page.

    Args:
        file_text: the .drawio file's text (compressed pages are decoded).
        page: the page, counted from 1.
        prefix: keep only arrows whose id starts with this ("" for every arrow).

    Returns:
        {arrow id: runs}.

    Raises:
        IndexError: when the page does not exist.
    """
    wires = read.pages(file_text)[page - 1]["wires"]
    return {w["id"]: [tuple(map(tuple, r)) for r in zip(w["path"], w["path"][1:])]
            for w in wires if w["id"].startswith(prefix) and len(w["path"]) > 1}


def main(argv: list[str] | None = None) -> int:
    """Print the crossing count of one page.

    Args:
        argv: command-line arguments (None for sys.argv).

    Returns:
        The exit code.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--page", type=int, default=1, help="page, counted from 1 (default 1)")
    ap.add_argument("--prefix", default="", help="only arrows whose id starts with this")
    args = ap.parse_args(argv)
    try:
        runs = page_runs(args.file.read_text(encoding="utf-8"), args.page, args.prefix)
    except (OSError, ValueError, IndexError) as exc:
        print(f"count_crossings: {args.file} page {args.page}: {exc}", file=sys.stderr)
        return 1
    print(f"{args.file.name} page {args.page}{' prefix ' + args.prefix if args.prefix else ''}: {len(runs)} arrows, {crossings(runs)} crossings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
