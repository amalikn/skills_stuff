#!/usr/bin/env python3
"""Ask a flow map what happens instead of reading the code: which steps a change runs, which steps touch a file, what writes a thing, what can fail.
Each step shown says when its review no longer holds. Read-only.

Usage (from the project root, with the project's interpreter: PyYAML reads the map):
    trace_query.py --map docs/flows/flows.yaml --flow checkout            # a flow, or every flow of a family
    trace_query.py --map docs/flows/flows.yaml --file tasks/verify.yml    # the steps citing a file (the end of its path is enough)
    trace_query.py --map docs/flows/flows.yaml --writes "run record"      # the steps writing something
    trace_query.py --map docs/flows/flows.yaml --failure timeout --actor api --json
Exit: 0 found, 1 nothing found or the map cannot be read, 2 on bad arguments.
Runtime: under a second for 200 steps (measured 2026-11-02).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flowmap import model
from flowtrace import lockfile
from flowtrace.query import Ask, digest, select

#: The oldest Python this script runs on (stdlib; PyYAML to read the map).
REQUIRES_PYTHON = (3, 11)


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
    for name in ("flow", "file", "writes", "failure", "actor", "text"):
        ap.add_argument(f"--{name}", default="", help=f"match on {name}")
    ap.add_argument("--json", action="store_true", help="print matches as JSON")
    args = ap.parse_args(argv)
    ask = Ask(args.flow, args.file, args.writes, args.failure, args.actor, args.text)
    if not any(vars(ask).values()):
        print("trace_query: name at least one of --flow --file --writes --failure --actor --text", file=sys.stderr)
        return 2
    root = args.root.resolve()
    try:
        data = model.read_map(root, args.map)
        states = {f.step: f.state for f in lockfile.findings(root, args.map, data)}
    except (OSError, ValueError) as exc:
        print(f"trace_query: {exc}", file=sys.stderr)
        return 1
    found = select(data, ask)
    if args.json:
        print(json.dumps([{"flow": f["id"], "steps": [{**s, "review": states.get(f"{f['id']}/{s['id']}", "current")} for s in steps]} for f, steps in found], indent=1))
    else:
        print("\n".join(digest(found, {c["id"]: c for c in data["components"]}, states)) or "nothing found")
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
