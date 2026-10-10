#!/usr/bin/env python3
"""Measure whether agents actually use a file, folder or command, from recent Claude Code transcripts. Stdlib only; read-only.

Why (operator, 2026-10-10): Graphify was rebuilt thousands of times and queried zero times, and the LLM wiki took no writes in 30 days, but nobody had
measured it. Before adding, keeping or retiring a navigation aid (a graph, a wiki, a map, a context pack), count how often agents touch it.

Counts tool calls whose input contains each term, by tool name, in transcripts under ~/.claude/projects modified within the window. Codex and Hermes
sessions are not read.

Usage:
    python scripts/agent_usage.py graphify-out "graphify query" _wiki/wiki_stuff                     # all projects, last 30 days
    python scripts/agent_usage.py --days 14 --project unified-network-controller target-map.yaml context-map.yaml
Exit: 0, or 2 when no term is given.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from collections import Counter


def count(terms: list[str], days: int, project: str) -> tuple[int, int, dict[str, Counter], dict[str, int]]:
    """Count tool calls naming each term.

    Args:
        terms: substrings to look for in each tool call's input.
        days: how far back, by transcript modification time.
        project: a substring the transcript folder name must contain; empty for all.

    Returns:
        (sessions read, tool calls read, per term a Counter of tool name to calls, per term the number of sessions with a hit).
    """
    cutoff = time.time() - days * 86400
    by_tool = {t: Counter() for t in terms}
    sessions = {t: 0 for t in terms}
    nsess = ncalls = 0
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        if project and project not in os.path.basename(os.path.dirname(path)):
            continue
        if os.path.getmtime(path) < cutoff:
            continue
        nsess += 1
        hit: set[str] = set()
        with open(path, errors="ignore") as fh:
            for line in fh:
                if '"tool_use"' not in line:
                    continue
                try:
                    msg = json.loads(line).get("message") or {}
                except ValueError:
                    continue
                for block in msg.get("content") or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    ncalls += 1
                    text = json.dumps(block.get("input", {}))
                    for t in terms:
                        if t in text:
                            by_tool[t][block.get("name", "?")] += 1
                            hit.add(t)
        for t in hit:
            sessions[t] += 1
    return nsess, ncalls, by_tool, sessions


def main(argv: list[str] | None = None) -> int:
    """Print the counts.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        The exit code: 0, or 2 without terms.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--project", default="", help="substring of the ~/.claude/projects folder name")
    args = ap.parse_args(argv)
    if not args.terms:
        ap.print_usage(sys.stderr)
        return 2
    nsess, ncalls, by_tool, sessions = count(args.terms, args.days, args.project)
    print(f"window={args.days}d sessions={nsess} tool_calls={ncalls}")
    for t in args.terms:
        tools = ", ".join(f"{k}={v}" for k, v in by_tool[t].most_common())
        print(f"{t}: calls={sum(by_tool[t].values())} sessions={sessions[t]} {tools}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
