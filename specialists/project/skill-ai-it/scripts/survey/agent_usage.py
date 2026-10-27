#!/usr/bin/env python3
"""Measure whether agents actually use a file, folder or command, from recent Claude Code transcripts. Stdlib only; read-only.

Why (operator, 2026-10-10): Graphify was rebuilt thousands of times and queried zero times, and the LLM wiki took no writes in 30 days, but nobody had
measured it. Before adding, keeping or retiring a navigation aid (a graph, a wiki, a map, a context pack), count how often agents touch it.

Counts tool calls whose input contains each term, by tool name, in transcripts under ~/.claude/projects modified within the window. Codex and Hermes
sessions are not read.

Usage:
    python scripts/survey/agent_usage.py graphify-out "graphify query" _wiki/wiki_stuff                     # all projects, last 30 days
    python scripts/survey/agent_usage.py --days 14 --project unified-network-controller target-map.yaml context-map.yaml
    python scripts/survey/agent_usage.py --md-reads --days 14 --project unified-network-controller                 # how large Markdown is read

`--md-reads` (lilmd assessment, 2026-10-11) counts, across transcripts and their subagent transcripts: Bash/Grep calls that build a heading
outline by hand (`grep -n '^#'` and similar on a `.md`), `just outline` / `just section` calls, and Read calls on `.md` files, whole or ranged.
Baseline for UNC, 30 days to 2026-10-11: 182 transcripts, 747 outline greps in 98 of them. The outline-grep count matches command text, so it
can include greps that were not building an outline; compare windows, not absolute numbers.
Exit: 0, or 2 when no term is given.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter

OUTLINE_GREP = re.compile(r"""(grep[^|]*-n[^|]*['"]\^#|['"]\^#{1,6}[ \\s]|\^#\+)""")
RECIPE = re.compile(r"\bjust (outline|section)\b")


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


def md_reads(days: int, project: str, root: str = "~/.claude/projects") -> dict[str, int]:
    """Count how agents read Markdown: hand-built outlines, the outline/section recipes, and whole or ranged Reads.

    Args:
        days: how far back, by transcript modification time.
        project: a substring the project folder name must contain; empty for all.
        root: the transcripts folder (tests pass a temporary one).

    Returns:
        Counts: transcripts, outline_greps, outline_grep_sessions, recipe_calls, recipe_sessions, md_read_whole, md_read_ranged.
    """
    cutoff = time.time() - days * 86400
    out = Counter()
    base = os.path.expanduser(root)
    for path in glob.glob(os.path.join(base, "*", "**", "*.jsonl"), recursive=True):
        if project and project not in os.path.relpath(path, base).split(os.sep)[0]:
            continue
        if os.path.getmtime(path) < cutoff:
            continue
        out["transcripts"] += 1
        grep_hit = recipe_hit = False
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
                    name, inp = block.get("name"), block.get("input") or {}
                    if name == "Read" and str(inp.get("file_path", "")).endswith(".md"):
                        out["md_read_ranged" if "offset" in inp or "limit" in inp else "md_read_whole"] += 1
                    elif name in ("Bash", "Grep"):
                        text = inp.get("command", "") or inp.get("pattern", "")
                        if RECIPE.search(text):
                            out["recipe_calls"] += 1
                            recipe_hit = True
                        elif OUTLINE_GREP.search(text) and ".md" in json.dumps(inp):
                            out["outline_greps"] += 1
                            grep_hit = True
        out["outline_grep_sessions"] += grep_hit
        out["recipe_sessions"] += recipe_hit
    return {k: out[k] for k in ("transcripts", "outline_greps", "outline_grep_sessions", "recipe_calls", "recipe_sessions", "md_read_whole",
                                "md_read_ranged")}


def main(argv: list[str] | None = None) -> int:
    """Print the counts.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        The exit code: 0, or 2 without terms (and without --md-reads).
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--project", default="", help="substring of the ~/.claude/projects folder name")
    ap.add_argument("--md-reads", action="store_true", help="count how large Markdown is read (outline greps, recipes, whole/ranged Reads)")
    args = ap.parse_args(argv)
    if args.md_reads:
        print(f"window={args.days}d " + " ".join(f"{k}={v}" for k, v in md_reads(args.days, args.project).items()))
        return 0
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
