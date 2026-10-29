#!/usr/bin/env python3
"""Count where a drawing's arrows cross each other on one page: horizontal against vertical runs of their full paths. Read-only, stdlib only.

Why (2026-10-20): an engine change that is not byte-identical for a consumer must show the consumer's drawing got no worse. The layout audits
say clean or not; this gives the number to compare before and after (unified-network-controller's Overview thin arrows, `--prefix ov-d-`:
54 to 44 crossings with drawio.route.gap_order). Paths come from drawio.read, which resolves each arrow's ends on its boxes and any group offsets, so
arrows stored as waypoints only (the End-to-end page) are measured whole.

Compare mode (2026-10-27): `--compare BEFORE.drawio` measures every page of both files, prints the pages whose crossings or shared runs
changed and the totals, and exits 3 when any page got worse. Shared runs (two arrows lying along each other within 8 px) are counted too: a
crossing count alone missed two arrows merged on one run (smc_change Apply, 2026-10-27).

Usage:
    count_crossings.py FILE.drawio [--page 1] [--prefix ov-d-]
    count_crossings.py AFTER.drawio --compare BEFORE.drawio [--prefix ov-d-]
    (--prefix keeps only arrows whose id starts with it, e.g. `ov-d-` for the Overview's thin arrows; default every arrow on the page)
Exit: 0 when counted (compare: no page worse), 1 when the file or page cannot be read, 2 on bad arguments, 3 when a compared page got worse.
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


def alongside(runs: dict[str, list], near: float = 8) -> int:
    """How many pairs of runs from different arrows lie along each other (parallel, closer than `near`, overlapping by more than 2 px).

    Args:
        runs: {arrow id: [((x1, y1), (x2, y2)), ...]}.
        near: the distance under which two parallel runs read as one arrow.

    Returns:
        The count over every pair of arrows.
    """
    def along(p: tuple, q: tuple) -> bool:
        """Whether two runs lie along each other.

        Args:
            p: one run.
            q: the other.

        Returns:
            True for parallel runs closer than `near` that overlap by more than 2 px.
        """
        (a, b), (c, d) = p, q
        if a[1] == b[1] and c[1] == d[1] and abs(a[1] - c[1]) < near:
            return max(min(a[0], b[0]), min(c[0], d[0])) < min(max(a[0], b[0]), max(c[0], d[0])) - 2
        if a[0] == b[0] and c[0] == d[0] and abs(a[0] - c[0]) < near:
            return max(min(a[1], b[1]), min(c[1], d[1])) < min(max(a[1], b[1]), max(c[1], d[1])) - 2
        return False
    ids = sorted(runs)
    return sum(along(p, q) for i, a in enumerate(ids) for b in ids[i + 1:] for p in runs[a] for q in runs[b])


def compare(before: str, after: str, prefix: str = "") -> tuple[list, tuple]:
    """Crossings and shared runs per page of two versions of one drawing.

    Args:
        before: the earlier .drawio text.
        after: the later .drawio text.
        prefix: keep only arrows whose id starts with this.

    Returns:
        ([(page, (crossings, shared) before, (crossings, shared) after) for each page that changed], (total before, total after)), totals
        as (crossings, shared); pages only one version has count as 0 in the other.
    """
    def measure(text: str) -> list:
        """Each page's crossings and shared runs.

        Args:
            text: a .drawio file's text.

        Returns:
            [(crossings, shared runs) per page].
        """
        return [(crossings(r), alongside(r)) for r in (wire_runs(pg["wires"], prefix) for pg in read.pages(text))]   # parsed once
    b, a = measure(before), measure(after)
    pad = max(len(a), len(b))
    b, a = b + [(0, 0)] * (pad - len(b)), a + [(0, 0)] * (pad - len(a))
    changed = [(k + 1, x, y) for k, (x, y) in enumerate(zip(b, a)) if x != y]
    return changed, (tuple(map(sum, zip(*b))) if b else (0, 0), tuple(map(sum, zip(*a))) if a else (0, 0))


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
    return wire_runs(read.pages(file_text)[page - 1]["wires"], prefix)


def wire_runs(wires: list[dict], prefix: str) -> dict[str, list]:
    """Each arrow's straight runs from one page's wires.

    Args:
        wires: the page's wires (drawio.read.pages(...)[k]["wires"]).
        prefix: keep only arrows whose id starts with this ("" for every arrow).

    Returns:
        {arrow id: runs}.
    """
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
    ap.add_argument("--compare", type=Path, help="an earlier version of FILE: every page, before and after")
    args = ap.parse_args(argv)
    if args.compare:
        try:
            changed, (tb, ta) = compare(args.compare.read_text(encoding="utf-8"), args.file.read_text(encoding="utf-8"), args.prefix)
        except (OSError, ValueError, IndexError) as exc:
            print(f"count_crossings: {exc}", file=sys.stderr)
            return 1
        for page, (cb, sb), (ca, sa) in changed:
            print(f"page {page}: crossings {cb} -> {ca}, shared runs {sb} -> {sa}")
        print(f"total: crossings {tb[0]} -> {ta[0]}, shared runs {tb[1]} -> {ta[1]} ({len(changed)} page(s) changed)")
        return 3 if any(ca > cb or sa > sb for _p, (cb, sb), (ca, sa) in changed) else 0
    try:
        runs = page_runs(args.file.read_text(encoding="utf-8"), args.page, args.prefix)
    except (OSError, ValueError, IndexError) as exc:
        print(f"count_crossings: {args.file} page {args.page}: {exc}", file=sys.stderr)
        return 1
    print(f"{args.file.name} page {args.page}{' prefix ' + args.prefix if args.prefix else ''}: {len(runs)} arrows, {crossings(runs)} crossings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
