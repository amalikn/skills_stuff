#!/usr/bin/env python3
"""Move named `##` sections of a governed markdown file (AGENTS.md, SCRATCHPAD.md) verbatim into an on-need reference file. Stdlib only.

Why (operator, 2026-10-10): rotation moves only dated history, so a file held over its 200-line / 25 KB budget by durable reference material
(key anchors, audit procedures, hardware tables) stayed over budget after every rotation; the UNC AGENTS.md trim and the smc and ansible-wifi
SCRATCHPAD fixes were done by hand. One run does it safely:
1. Cut the named sections (heading to the next `##`) and write them, verbatim and in order, to the destination under a front-matter header.
2. Leave one pointer section in the source naming each moved section, so a citation such as `AGENTS.md § Live Audit Procedure` still resolves.
3. Drop the moved sections' Contents entries (matched by link text, so any anchor style works) and add one for the pointer section.
4. Refuse to write if any moved line is missing from the destination.
Without `--apply` it prints the plan and changes nothing. Index the destination in its folder `readme.md` afterwards (or run the project's
index generator).

Usage:
    python scripts/move_sections.py --project-root . --source AGENTS.md --dest docs/agent-reference-20261010_1859.md \
        --title "Agent reference" --summary "On-need reference moved from AGENTS.md" "Live Audit Procedure" "Decision Matrix"
    python scripts/move_sections.py ... --apply
Exit: 0 planned or moved, 1 on a refusal (section not found, destination exists, a line would be lost), 2 on bad arguments.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
from collections import Counter

HEADING = re.compile(r"^## (.+?)\s*$")
TOC_ENTRY = re.compile(r"^\s*- \[(.+?)\]\(#[^)]*\)\s*$")


def sections(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Map each level-2 heading to its line span, ignoring headings inside fenced code.

    Args:
        lines: the file's lines.

    Returns:
        {heading text: (start index, end index exclusive)}.
    """
    starts, fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and HEADING.match(line):
            starts.append(i)
    ends = starts[1:] + [len(lines)]
    return {HEADING.match(lines[a]).group(1): (a, b) for a, b in zip(starts, ends)}


def plan(lines: list[str], names: list[str], dest: str, pointer: str) -> tuple[list[str], list[list[str]]]:
    """Build the new source text and the moved blocks.

    Args:
        lines: the source file's lines.
        names: headings of the sections to move, in the order they should appear in the destination.
        dest: the destination path as the source should link it.
        pointer: heading of the pointer section left in the source.

    Returns:
        (the source's new lines, the moved blocks verbatim).

    Raises:
        KeyError: a named section does not exist.
    """
    spans = sections(lines)
    missing = [n for n in names if n not in spans]
    if missing:
        raise KeyError(", ".join(missing))
    moved, cut = [], set()
    for n in names:
        a, b = spans[n]
        block = lines[a:b]
        while block and block[-1].strip() in ("", "---"):
            block.pop()
        moved.append(block)
        cut |= set(range(a, b))
    first = min(spans[n][0] for n in names)
    ptr = [f"## {pointer}", "",
           f"Read [{dest}]({dest}) before the work it covers. It holds these sections, moved verbatim from this file (a citation of a section",
           "by name resolves there): " + "; ".join(names) + ".", ""]
    out, toc_done = [], False
    for i, line in enumerate(lines):
        if i == first:
            out += ptr
        if i in cut:
            continue
        m = TOC_ENTRY.match(line)
        if m and m.group(1) in names:
            if not toc_done:
                anchor = re.sub(r"-+", "-", re.sub(r"[^\w\- ]", "", pointer.lower()).replace(" ", "-"))
                out.append(f"- [{pointer}](#{anchor})")
                toc_done = True
            continue
        out.append(line)
    return out, moved


def dest_text(moved: list[list[str]], source: str, title: str, summary: str, today: str) -> str:
    """The destination file: front matter, a one-line provenance note, then the sections verbatim.

    Args:
        moved: the moved blocks.
        source: the source path, for the provenance note.
        title: the destination's title.
        summary: its one-line summary.
        today: ISO date for `Last reviewed`.

    Returns:
        The file text.
    """
    head = ["---", f"Title: {title}", "Category: reference", "Status: current", "Authority: local-supplement",
            f"Scope: On-need reference moved verbatim from {source}", f"Last reviewed: {today}", "Summary: >-", f"  {summary}", "---", "",
            f"# {title}", "", f"Moved verbatim from `{source}` on {today} to keep that file within its budget for files loaded whole.", ""]
    names = [HEADING.match(b[0]).group(1) for b in moved]
    if sum(len(b) for b in moved) > 100:
        head += ["## Contents", ""] + [f"- [{n}](#{re.sub(r'-+', '-', re.sub(r'[^\w\- ]', '', n.lower()).replace(' ', '-'))})" for n in names] + [""]
    body: list[str] = []
    for b in moved:
        body += b + [""]
    return "\n".join(head + body).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """Plan or apply one section move.

    Args:
        argv: command-line arguments (default: sys.argv).

    Returns:
        The exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--source", required=True, help="project-relative file to cut from")
    ap.add_argument("--dest", required=True, help="project-relative reference file to create")
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--pointer", default="Reference loaded on need", help="heading of the pointer section left in the source")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("names", nargs="+", help="exact `##` headings to move")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root)
    src, dst = root / args.source, root / args.dest
    if dst.exists():
        print(f"refused: {args.dest} exists")
        return 1
    lines = src.read_text().splitlines()
    try:
        new, moved = plan(lines, args.names, args.dest, args.pointer)
    except KeyError as exc:
        print(f"refused: section(s) not found in {args.source}: {exc}")
        return 1
    text = dest_text(moved, args.source, args.title, args.summary, dt.date.today().isoformat())
    lost = Counter(l for b in moved for l in b) - Counter(text.splitlines())
    if lost:
        print(f"refused: {sum(lost.values())} moved line(s) would be lost, e.g. {next(iter(lost))!r}")
        return 1
    n = sum(len(b) for b in moved)
    print(f"{args.source}: {len(lines)} -> {len(new)} lines; {n} lines in {len(moved)} section(s) -> {args.dest}")
    if not args.apply:
        print("plan only; add --apply to move")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    src.write_text("\n".join(new).rstrip() + "\n")
    print("moved; no line lost. Index the destination in its folder readme.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
