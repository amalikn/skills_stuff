#!/usr/bin/env python3
"""Add one entry to a project's CHANGELOG.md in that project's own heading style and order, with its Contents line. Stdlib only.

Why (operator, 2026-10-10): entries were written by hand-built scratch scripts about 25 times in one session, because each project writes its
headings differently and keeps a Contents list that must gain the new entry's link. One run:
1. Reads the clock (or `--stamp`) so no time is invented.
2. Detects the style from the existing entries and writes the heading the same way:
   `## 20261010_2227 — title` (dash), `## 20261010_2227 (title)` (bracket), `## 2026-10-10 (label, 20261010_2227) — title` (dated, with
   `--label`), `## 2026-10-10 — title` (plain date), `## 20261010_2227` with the title as a bold first line (bare stamp). The newest entry
   sets the style; a file with no entries gets the dash style.
3. Detects the order (newest first, or oldest first) and inserts above the newest entry or appends at the end.
4. Adds the entry's link to the Contents list when the file keeps one, in the same position.
5. Verifies every original line is still present, in order. Without `--apply` it prints the heading and position and changes nothing.
After writing, it says when the file is over its 200-line / 25 KB budget (`just budget --apply` rotates it).

Usage:
    python scripts/add_changelog_entry.py --project-root . --title "Navigation block compact" --body-file /tmp/entry.md
    python scripts/add_changelog_entry.py --project-root . --title "x" --body "- one line" --label "budget pass" --apply
Exit: 0 planned or written, 1 on a refusal (no body, an original line would change), 2 on bad arguments.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

STYLES = [
    ("dated", re.compile(r"^## (\d{4}-\d{2}-\d{2}) \(([^)]*?)(\d{8}_\d{4})\) — ")),
    ("dash", re.compile(r"^## (\d{8}_\d{4}) — ")),
    ("bracket", re.compile(r"^## (\d{8}_\d{4}) \(")),
    ("stamp", re.compile(r"^## (\d{8}_\d{4})\s*$")),
    ("date", re.compile(r"^## (\d{4}-\d{2}-\d{2})\b")),
]
TOC_ENTRY = re.compile(r"^\s*- \[(.+?)\]\(#[^)]*\)\s*$")
BUDGET = (200, 25 * 1024)


def slug(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading (double hyphens kept).

    Args:
        heading: the heading text without its hashes.

    Returns:
        The anchor.
    """
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def entry_lines(lines: list[str]) -> list[tuple[int, str, str]]:
    """The dated entry headings of a change log, outside fenced code.

    Args:
        lines: the file's lines.

    Returns:
        [(line index, style name, sortable date string)] in file order.
    """
    out, fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or not line.startswith("## "):
            continue
        for name, rx in STYLES:
            m = rx.match(line)
            if m:
                key = m.group(3) if name == "dated" else m.group(1).replace("-", "")
                out.append((i, name, key))
                break
    return out


def heading(style: str, title: str, stamp: str, label: str | None) -> str:
    """The new entry's heading text (without the hashes) in a given style.

    Args:
        style: the detected style name.
        title: the entry's title.
        stamp: `YYYYMMDD_hhmm`.
        label: the dated style's label, when given.

    Returns:
        The heading text.
    """
    date = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"
    if style == "bracket":
        return f"{stamp} ({title})"
    if style == "dated":
        return f"{date} ({label + ', ' if label else ''}{stamp}) — {title}"
    if style == "date":
        return f"{date} — {title}"
    if style == "stamp":
        return stamp
    return f"{stamp} — {title}"


def add(text: str, title: str, body: str, stamp: str, label: str | None = None) -> tuple[str, str, str]:
    """Insert one entry and its Contents line.

    Args:
        text: the change log's text.
        title: the entry title.
        body: the entry body (markdown, already wrapped).
        stamp: `YYYYMMDD_hhmm`.
        label: the dated style's label.

    Returns:
        (the new text, the heading written, "top" or "end").
    """
    lines = text.split("\n")
    entries = entry_lines(lines)
    newest_first = len(entries) < 2 or entries[0][2] >= entries[1][2]
    style = (entries[0] if newest_first else entries[-1])[1] if entries else "dash"  # the newest entry sets the style
    head = heading(style, title, stamp, label)
    lead = [f"**{title}**", ""] if style == "stamp" else []
    block = [f"## {head}", ""] + lead + body.rstrip("\n").split("\n") + [""]
    if entries and newest_first:
        at = entries[0][0]
        lines[at:at] = block
        where = "top"
    else:
        while lines and lines[-1] == "":
            lines.pop()
        lines += [""] + block
        where = "end"
    toc = [i for i, l in enumerate(lines) if TOC_ENTRY.match(l) and re.search(r"\]\(#(\d{8}|\d{4}-\d{2}-\d{2})", l)]
    if toc:
        link = f"- [{head}](#{slug(head)})"
        if where == "top":
            lines.insert(toc[0], link)
        else:
            lines.insert(toc[-1] + 1, link)
    return "\n".join(lines), head, where


def main(argv: list[str] | None = None) -> int:
    """Plan or write one change-log entry.

    Args:
        argv: command-line arguments (default: sys.argv).

    Returns:
        The exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--record", default="CHANGELOG.md")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", help="the entry body; or --body-file")
    ap.add_argument("--body-file")
    ap.add_argument("--label", help="label for the dated style: `## 2026-10-10 (label, stamp) — title`")
    ap.add_argument("--stamp", help="YYYYMMDD_hhmm; default: now")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    body = args.body if args.body is not None else (pathlib.Path(args.body_file).read_text() if args.body_file else "")
    if not body.strip():
        print("refused: the entry has no body")
        return 1
    stamp = args.stamp or dt.datetime.now().strftime("%Y%m%d_%H%M")
    path = pathlib.Path(args.project_root) / args.record
    text = path.read_text() if path.exists() else "# Changelog\n"
    new, head, where = add(text, args.title, body, stamp, args.label)
    it = iter(new.split("\n"))
    if not all(any(o == n for n in it) for o in text.split("\n")):
        print(f"refused: an original line of {args.record} would change or move out of order")
        return 1
    wide = [l for l in body.split("\n") if len(l) > 200]
    print(f"{args.record}: ## {head}  ({'above the newest entry' if where == 'top' else 'appended at the end'})"
          + (f"; {len(wide)} body line(s) over 200 columns" if wide else ""))
    if not args.apply:
        print("plan only; add --apply to write")
        return 0
    path.write_text(new)
    lines, size = new.count("\n"), len(new.encode())
    print(f"written; {args.record} is {lines} lines, {size // 1024} KB" + ("; over budget, run `just budget --apply`" if lines > BUDGET[0] or size > BUDGET[1] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
