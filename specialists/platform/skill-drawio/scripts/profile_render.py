#!/usr/bin/env python3
"""Profile one render of a project's flow map: where the time goes, by function, so a slow render or drift check is found by measurement.

Found the 2026-11-06 regression this way: unified-network-controller's render had grown from 2.3 s (26 Oct) to 183 s with the map unchanged;
one profile showed band_search taking 200 of 250 s (one full End-to-end layout per pair of band boxes). Read-only: it loads and renders the map
in memory and writes nothing (no drawing, no render cache entry).

Usage (from the project root):
    profile_render.py --map docs/flows/flows.yaml                         # top 25 by cumulative time
    profile_render.py --map docs/flows/flows.yaml --sort tottime --top 15 # own time
    profile_render.py --map docs/flows/flows.yaml --workers 8             # with band_search's worker pool (wall time; the table then shows waiting)
Band trials run in this process by default (`--workers 1`): cProfile sees only its own process, so with workers the table shows the parent
waiting in connection.recv instead of the layout work (found on the first smoke run, 2026-11-06).
Exit: 0 after printing; 2 on bad arguments or a map that cannot be read or has problems. Runtime: one render plus profiling overhead (about
1.5x; UNC's 42-page map about 250 s, a small map a second).
"""

from __future__ import annotations

import argparse
import cProfile
import os
import pstats
import sys
import time
from pathlib import Path

from flowmap import model, pages
from render_flowmap import SCHEMA, profile_for

#: The oldest Python this script runs on (stdlib; PyYAML to read the map).
REQUIRES_PYTHON = (3, 11)
#: Paths under this folder print relative to it, so the table reads as module:line.
SCRIPTS = Path(__file__).resolve().parent


def rows(stats: pstats.Stats, sort: str, top: int) -> list[tuple[int, float, float, str]]:
    """The heaviest functions of a profile.

    Args:
        stats: the profile's statistics.
        sort: "cumulative" (time including callees) or "tottime" (own time).
        top: how many rows.

    Returns:
        (calls, own seconds, cumulative seconds, "file:line(function)") per row, heaviest first.
    """
    out = []
    for (path, line, func), (_cc, calls, tottime, cumtime, _callers) in stats.stats.items():
        try:
            where = Path(path).resolve().relative_to(SCRIPTS).as_posix()
        except ValueError:
            where = path if path.startswith("<") else Path(path).name
        out.append((calls, tottime, cumtime, f"{where}:{line}({func})"))
    key = 2 if sort == "cumulative" else 1
    return sorted(out, key=lambda r: r[key], reverse=True)[:top]


def table(found: list[tuple[int, float, float, str]]) -> list[str]:
    """Format profile rows as aligned text lines.

    Args:
        found: rows from rows().

    Returns:
        The lines, a header first.
    """
    lines = [f"{'calls':>11} {'own s':>8} {'cum s':>8}  function"]
    lines += [f"{calls:>11} {own:>8.2f} {cum:>8.2f}  {where}" for calls, own, cum, where in found]
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=Path("."), help="the project root (default: the current folder)")
    ap.add_argument("--map", required=True, help="the map, relative to the root")
    ap.add_argument("--schema", default=str(SCHEMA), help="the JSON Schema (default: the skill's generic one)")
    ap.add_argument("--sort", choices=("cumulative", "tottime"), default="cumulative", help="order of the table (default cumulative)")
    ap.add_argument("--top", type=int, default=25, help="rows to print (default 25)")
    ap.add_argument("--workers", type=int, default=1, help="band_search workers (default 1: in process, so the profile sees the work)")
    args = ap.parse_args(argv)
    os.environ["SKILL_DRAWIO_WORKERS"] = str(max(1, args.workers))
    root = args.root.resolve()
    try:
        profile = profile_for(root, args.map, args.schema, "")
        began = time.monotonic()
        data, problems = model.load(root, profile)
        loaded = time.monotonic() - began
    except (OSError, ValueError) as exc:
        print(f"profile_render: {exc}", file=sys.stderr)
        return 2
    if problems or data is None:
        print("profile_render: the map has problems; run render_flowmap.py first:", *problems[:5], sep="\n  ", file=sys.stderr)
        return 2
    prof = cProfile.Profile()
    began = time.monotonic()
    prof.enable()
    pages.render(data, profile)
    prof.disable()
    rendered = time.monotonic() - began
    print(f"{args.map}: load {loaded:.1f} s, render {rendered:.1f} s (profiled; band workers {os.environ['SKILL_DRAWIO_WORKERS']})")
    print("\n".join(table(rows(pstats.Stats(prof), args.sort, args.top))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
