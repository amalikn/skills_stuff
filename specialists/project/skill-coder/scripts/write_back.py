#!/usr/bin/env python3
"""Find write-back entries a project is still holding for a skill, so the next engagement promotes them into the skill. Read-only. Stdlib only.

Why (operator, 2026-10-19: "add the write back mechanism so that whatever learning is there, any project which is calling skill coder should
write that learning back"): when a session cannot write the skill's source, the contract (references/evolution-and-write-back.md) parks the entry
in the engaging project under a heading naming the skill. Without a way to find those entries again they stay there; this lists them, and the
slurp (skill-slurp-chat Step 5b) runs it for every engaged skill.

An entry is a `> **Learned YYYY-MM-DD**` or `> **Disputed YYYY-MM-DD**` blockquote line inside a Markdown section whose heading names the skill
(for example `## skill-coder write-back candidates`); the section ends at the next heading of the same or a higher level.

Usage:
    write_back.py --project-root /path/to/project [--skill skill-coder] [--strict]
Exit: 0 (report); with --strict 1 while an entry is pending; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
ENTRY = re.compile(r"^>\s*\*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})\*\*")
#: Folders never read: rebuildable caches, history archives (a rotated entry was already handled), vendored code.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "history", "archive"}


def pending_in(text: str, skill: str) -> list[tuple[int, str, str]]:
    """The entries parked for a skill in one Markdown text.

    Args:
        text: the file's text.
        skill: the skill's name as it appears in the parking heading.

    Returns:
        (line number, kind, date) per entry inside a section whose heading names the skill; code fences are skipped.
    """
    out, level, fence = [], 0, False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if (h := HEADING.match(line)) is not None:
            depth = len(h.group(1))
            if level and depth <= level:
                level = 0
            if skill.lower() in h.group(2).lower():
                level = depth
            continue
        if level and (e := ENTRY.match(line)) is not None:
            out.append((n, e.group(1), e.group(2)))
    return out


def pending(root: Path, skill: str) -> list[tuple[str, int, str, str]]:
    """Every entry a project holds for a skill.

    Args:
        root: the project root.
        skill: the skill's name.

    Returns:
        (file relative to root, line number, kind, date) per entry, in path order.
    """
    found = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found += [(rel.as_posix(), n, kind, date) for n, kind, date in pending_in(text, skill)]
    return found


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, or 1 with --strict while an entry is pending; 2 when the project root is not a folder.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--skill", default="skill-coder", help="the skill whose parked entries to find (default skill-coder)")
    ap.add_argument("--strict", action="store_true", help="exit 1 while an entry is pending")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    if not root.is_dir():
        print(f"write_back: {root} is not a folder", file=sys.stderr)
        return 2
    found = pending(root, args.skill)
    for rel, n, kind, date in found:
        print(f"{rel}:{n}: {kind} {date} parked for {args.skill}: promote it into the skill, then remove it here")
    print(f"write_back: {len(found)} entr{'y' if len(found) == 1 else 'ies'} pending for {args.skill} in {root.name}")
    return 1 if (args.strict and found) else 0


if __name__ == "__main__":
    sys.exit(main())
