#!/usr/bin/env python3
"""Hold a flow map to the code it describes: list the steps whose cited code changed since their review, code no flow cites, and step words the
code no longer holds; record a review with --accept. What a pass proves: every cited change was looked at by someone, not that the words are right.

The lock is `<map stem>.lock.json` beside the map, with the accepted source in `<map stem>.lock.d/`; start one with `--accept all --apply`. Output is
for people by default and for agents with --json (each finding with the step's words, what changed and the diff).

Usage (from the project root, with the project's interpreter: PyYAML reads the map):
    trace_sync.py --map docs/flows/flows.yaml                     # check; exit 1 on a finding (read only)
    trace_sync.py --map docs/flows/flows.yaml --diff              # also print each suspect's diff (read only)
    trace_sync.py --map docs/flows/flows.yaml --json              # the same as JSON (read only)
    trace_sync.py --map docs/flows/flows.yaml --accept rollback/undo --apply   # record a review of a step, a flow, a cited file, or `all`
    trace_sync.py --map docs/flows/flows.yaml --accept all        # plan only: what would be accepted
Exit: 0 clean (or accepted), 1 on a finding or when the map cannot be read, 2 on bad arguments.
Writes: only with --accept and --apply, only the lock file and its folder.
Runtime: under a second for 200 steps (measured 2026-11-02).
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from flowmap import model
from flowtrace import coverage, lockfile

#: The oldest Python this script runs on (stdlib; PyYAML to read the map).
REQUIRES_PYTHON = (3, 11)


def report(items: list, cover: list[str], words: list[str], show_diff: bool) -> list[str]:
    """The findings as text.

    Args:
        items: lockfile.findings().
        cover: coverage.coverage_problems().
        words: coverage.stale_words().
        show_diff: print each suspect's diff.

    Returns:
        The lines.
    """
    lines = []
    for f in items:
        lines.append(f"{f.state}: {f.step}{' (its words were edited since the review)' if f.edited else ''}")
        lines += [f"  {why}: {ref}" for ref, why in f.refs]
        lines += [f"  > {d}" for d in f.diff] if show_diff else []
    return lines + cover + [f"word not in the code (warning): {w}" for w in words]


def do_accept(root: Path, map_path: str, data: dict, args: argparse.Namespace) -> int:
    """Plan or record a review.

    Args:
        root: the project root.
        map_path: the map, relative to the root.
        data: the loaded map.
        args: the parsed arguments.

    Returns:
        0 done or planned, 1 when nothing matched or the map is broken.
    """
    chosen = lockfile.selected(data, args.accept)
    if not chosen:
        print(f"trace_sync: nothing matches {args.accept}", file=sys.stderr)
        return 1
    if not args.apply:
        print(f"plan: accept {len(chosen)} steps as reviewed against the code as it is now; add --apply")
        return 0
    try:
        done = lockfile.accept(root, map_path, data, args.accept, args.by or getpass.getuser())
    except ValueError as exc:
        print(f"trace_sync: {exc}", file=sys.stderr)
        return 1
    print(f"accepted {len(done)} steps")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, 1 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=Path("."), help="the project root (default: the current folder)")
    ap.add_argument("--map", required=True, help="the map, relative to the root")
    ap.add_argument("--diff", action="store_true", help="print each suspect's diff")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--accept", nargs="+", metavar="STEP", help="record a review: <flow>/<step>, <flow>, a cited file, or all")
    ap.add_argument("--by", default="", help="the reviewer's name (default: the login)")
    ap.add_argument("--apply", action="store_true", help="with --accept: write the lock")
    args = ap.parse_args(argv)
    if args.apply and not args.accept:
        print("trace_sync: --apply needs --accept", file=sys.stderr)
        return 2
    root, start = args.root.resolve(), time.monotonic()
    try:
        data = model.read_map(root, args.map)
        if args.accept:
            return do_accept(root, args.map, data, args)
        items = lockfile.findings(root, args.map, data)
    except (OSError, ValueError) as exc:
        print(f"trace_sync: {exc}", file=sys.stderr)
        return 1
    cover, words = coverage.coverage_problems(root, data), coverage.stale_words(root, data)
    if args.json:
        print(json.dumps({"findings": [asdict(f) for f in items], "coverage": cover, "stale_words": words}, indent=1))
    else:
        print("\n".join(report(items, cover, words, args.diff)) or "trace_sync: every review holds")
        print(f"trace_sync: {len(items)} steps to review, {len(cover)} coverage problems, {len(words)} word warnings, {time.monotonic() - start:.2f} s")
    return 1 if items or cover else 0


if __name__ == "__main__":
    sys.exit(main())
