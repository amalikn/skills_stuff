#!/usr/bin/env python3
"""Keep ROADMAP.md to what is open: move every done item into a dated archive under docs/history/, as rotate_records.py does for CHANGELOG and SCRATCHPAD.

Operator, 2026-10-13 (unified-network-controller): "like trimming was done for scratch pad, you need to do it for roadmap as well"; ROADMAP had grown to
330 lines, most of them done items and a current phase three weeks old, so milestone state drifted into SCRATCHPAD instead. Promoted to skill-ai-it on
2026-10-14 (operator: ROADMAP needs a budget and every project should know its use); the contract is in references/files-architecture-conventions-roadmap.md. A done item is a `- [x]` line with its indented
continuation lines; it moves verbatim under its section heading, and the `## Completed` section's items move whole. Never moved: open `- [ ]` items,
prose, headings, a done item dated within --keep-days (7), and an item carrying `PIN` in backticks. The archive is indexed in docs/history/readme.md
(created when missing); `just history <term>` finds an entry. A project without ROADMAP.md is left alone.

Usage: python3 <skill-ai-it>/scripts/roadmap_trim.py --project-root P [--apply] [--keep-days N]      (a project's `just rotate` runs it)
Without --apply it prints what would move. Exit 0.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

TOUCHES = ("files only",)
ITEM = re.compile(r"^- \[( |x|X)\] ")
PIN = "`PIN`"


def newest_date(lines: list[str]) -> datetime.date | None:
    """The latest YYYY-MM-DD date an item names.

    Args:
        lines: the item's lines.

    Returns:
        The date, or None when it names none.
    """
    found = [datetime.date.fromisoformat(d) for d in re.findall(r"\b(20\d\d-[01]\d-[0-3]\d)\b", " ".join(lines))]
    return max(found) if found else None


def split(text: str, keep_since: datetime.date | None = None) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """ROADMAP's lines with done items removed, and the removed items with their section headings.

    Args:
        text: ROADMAP.md.
        keep_since: a done item whose newest date is on or after this stays (recent work stays visible); None moves every done item.

    Returns:
        (kept lines, [(section heading path, item lines)]): an item is its `- [x]` line and every following indented or blank-then-indented line;
        every item of the `## Completed` section counts as done.
    """
    lines = text.splitlines()
    kept, moved, heads = [], [], {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if m := re.match(r"^(#{2,4}) (.+)$", line):
            depth = len(m.group(1))
            heads = {d: h for d, h in heads.items() if d < depth}
            heads[depth] = m.group(2)
        done = bool(re.match(r"^- \[[xX]\] ", line)) or (heads.get(2) == "Completed" and line.startswith("- "))
        if done and PIN not in line:
            item = [line]
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  ") or (lines[j] == "" and j + 1 < len(lines) and lines[j + 1].startswith("  "))):
                item.append(lines[j])
                j += 1
            dated = newest_date(item)
            # An undated done item is kept: its age is unknown (2026-10-13: three of that day's items moved at once); --keep-days 0 moves it.
            recent = keep_since is not None and (dated is None or dated >= keep_since)
            if not recent:
                moved.append((" > ".join(heads[d] for d in sorted(heads)), item))
                i = j
                continue
            kept += item
            i = j
            continue
        kept.append(line)
        i += 1
    return kept, moved


def archive_text(moved: list[tuple[str, list[str]]], stamp: str) -> str:
    """The archive file's content: front matter, then the moved items under their section paths, in ROADMAP order.

    Args:
        moved: split()'s moved items.
        stamp: YYYYMMDD_hhmm of this run.

    Returns:
        Markdown text.
    """
    out = ["---", f"Title: ROADMAP done items to {stamp}", "Category: history", "Status: archived", "Authority: record",
           "Scope: Done milestones moved out of ROADMAP.md by skill-ai-it scripts/roadmap_trim.py", f"Last reviewed: {stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}",
           f"Summary: {len(moved)} done items moved verbatim from ROADMAP.md on {stamp}, under their section headings.", "---", "",
           f"# ROADMAP done items to {stamp}", ""]
    last = None
    for head, item in moved:
        if head != last:
            out += [f"## {head}", ""]
            last = head
        out += item
    return "\n".join(out) + "\n"


def tidy(lines: list[str]) -> str:
    """The kept lines with runs of blank lines collapsed and an empty `## Completed` section given a pointer to the archives.

    Args:
        lines: split()'s kept lines.

    Returns:
        ROADMAP.md text.
    """
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip() + "\n")
    return text.replace("## Completed\n\n", "## Completed\n\nDone items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).\n\n", 1) \
        if "docs/history/roadmap-" not in text else text


def main(argv: list[str] | None = None) -> int:
    """Print or apply the trim.

    Args:
        argv: command-line arguments (default: sys.argv[1:]).

    Returns:
        0.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--project-root", "--root", dest="root", type=Path, default=Path("."))
    ap.add_argument("--keep-days", type=int, default=7, help="done items dated within this many days stay (default 7; 0 moves all)")
    args = ap.parse_args(argv)
    roadmap = args.root / "ROADMAP.md"
    if not roadmap.is_file():
        print("ROADMAP.md: none in this project; nothing to trim")
        return 0
    text = roadmap.read_text(encoding="utf-8")
    since = datetime.date.today() - datetime.timedelta(days=args.keep_days) if args.keep_days > 0 else None
    kept, moved = split(text, since)
    print(f"ROADMAP.md: {len(text.splitlines())} lines; {len(moved)} done item(s) to move, {sum(len(i) for _, i in moved)} lines")
    if not moved or not args.apply:
        return 0
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    name = f"roadmap-{stamp}.md"
    (args.root / "docs/history").mkdir(parents=True, exist_ok=True)
    (args.root / "docs/history" / name).write_text(archive_text(moved, stamp), encoding="utf-8")
    roadmap.write_text(tidy(kept), encoding="utf-8")
    index = args.root / "docs/history/readme.md"
    if not index.is_file():
        index.write_text("---\nTitle: History\nCategory: folder-index\nStatus: current\nSummary: Rotated records: CHANGELOG, SCRATCHPAD and ROADMAP entries moved out by their tools.\n---\n\n# History\n",
                         encoding="utf-8")
    index.write_text(index.read_text(encoding="utf-8").rstrip() + f"\n- [{name}]({name}) {len(moved)} done items from `ROADMAP.md`, moved {stamp}.\n",
                     encoding="utf-8")
    print(f"moved to docs/history/{name}; ROADMAP.md now {len(tidy(kept).splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
