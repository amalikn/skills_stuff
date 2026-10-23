#!/usr/bin/env python3
"""Regenerate the ``## Contents`` block of a communications-tracking.md from its entry headings.

Entry headings are ``## Email N - ...``, ``## Teams N - ...``, ``## Call N - ...`` and ``## Meeting N - ...``
(the four prefixes in SKILL.md); they are listed in file order with GitHub-Flavored Markdown anchors.

Run:
    python toc.py <tracker-file>                    # preview: print the new Contents, say whether it differs
    python toc.py <tracker-file> --update           # rewrite only the Contents block in place
    python toc.py <tracker-file> --update --allow-shrink   # accept a Contents with fewer entries than before

Safety: reads by default; writes only the given file and only with ``--update``. ``--update`` refuses (exit 2)
when the new Contents would hold fewer entries than the old one, or when there is no ``## Contents`` heading,
so a heading the parser misses can never silently drop TOC lines. Stdlib only; no network.

Exit codes: 0 done (or preview), 1 file missing or no entry headings, 2 refused (shrink or no Contents block).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENTRY_PREFIXES = ("Email", "Teams", "Call", "Meeting")

_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_ENTRY_RE = re.compile(r"^(?:" + "|".join(ENTRY_PREFIXES) + r")\s+[\da-z]+\s*[-–—]", re.IGNORECASE)
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_CONTENTS_START = re.compile(r"^## Contents\s*$", re.IGNORECASE)
_SEPARATOR = re.compile(r"^---\s*$")
_SECTION_HEADING = re.compile(r"^#{1,2}\s")
_TOC_ENTRY = re.compile(r"^\s*[-*]\s+\[")


def gfm_anchor(heading_text: str) -> str:
    """Return the GitHub-Flavored Markdown anchor for a heading.

    Lowercase; drop every character that is not a letter, digit, underscore, hyphen or space (so ``:``, ``,``,
    ``/``, ``+`` and ``—`` vanish without a replacement); then turn each space into a hyphen without collapsing
    runs, so ``Stu + Martin`` gives ``stu--martin`` as SKILL.md Step 7 states.

    Args:
        heading_text: the heading text without the leading ``#`` marks.

    Returns:
        The anchor without the leading ``#``.
    """
    text = heading_text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def iter_headings(content: str) -> list[tuple[int, str, str]]:
    """List ATX headings outside fenced code blocks, with GFM anchors made unique the way GitHub does (-1, -2).

    Args:
        content: the whole markdown file.

    Returns:
        A list of (heading level, heading text, unique anchor) in file order.
    """
    seen: dict[str, int] = {}
    headings: list[tuple[int, str, str]] = []
    in_fence = False
    for line in content.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _ATX_HEADING_RE.match(line)
        if not m:
            continue
        text = m.group(2).strip()
        base = gfm_anchor(text)
        count = seen.get(base, 0)
        seen[base] = count + 1
        headings.append((len(m.group(1)), text, base if count == 0 else f"{base}-{count}"))
    return headings


def build_toc_lines(content: str) -> list[str]:
    """Build one Contents line per level-2 entry heading (Email, Teams, Call, Meeting), in file order.

    Args:
        content: the whole tracker file.

    Returns:
        Lines of the form ``- [heading](#anchor)``.
    """
    return [f"- [{text}](#{anchor})" for level, text, anchor in iter_headings(content) if level == 2 and _ENTRY_RE.match(text)]


def read_old_toc(content: str) -> list[str] | None:
    """Return the non-blank lines of the current Contents block, or None when there is no ``## Contents``.

    The block ends at the first ``---`` line or the next level-1 or level-2 heading.

    Args:
        content: the whole tracker file.

    Returns:
        The stripped non-blank lines inside the block, or None.
    """
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if _CONTENTS_START.match(line.strip()):
            block = []
            for nxt in lines[i + 1 :]:
                if _SEPARATOR.match(nxt.strip()) or _SECTION_HEADING.match(nxt):
                    break
                if nxt.strip():
                    block.append(nxt.strip())
            return block
    return None


def replace_contents(content: str, new_toc_lines: list[str]) -> str:
    """Replace the Contents block with the new lines, keeping one blank line before what follows.

    The block runs from ``## Contents`` to the first ``---`` line or the next level-1 or level-2 heading, so a
    missing separator can no longer swallow the rest of the file. Text outside the block is unchanged.

    Args:
        content: the whole tracker file.
        new_toc_lines: the generated Contents lines.

    Returns:
        The new file text (unchanged when there is no ``## Contents`` heading).
    """
    out: list[str] = []
    state = "before"  # before | in_contents | after
    for line in content.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if state == "before":
            out.append(line)
            if _CONTENTS_START.match(stripped):
                state = "in_contents"
                out.append("\n")
                out.extend(toc_line + "\n" for toc_line in new_toc_lines)
            continue
        if state == "in_contents":
            if _SEPARATOR.match(stripped) or _SECTION_HEADING.match(stripped):
                out.append("\n")
                out.append(line)
                state = "after"
            continue
        out.append(line)
    if state == "in_contents":  # Contents ran to end of file
        out.append("\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, then preview or rewrite the Contents block.

    Args:
        argv: command-line arguments without the program name; None reads ``sys.argv``.

    Returns:
        Exit code: 0 done, 1 file missing or no entry headings, 2 refused.
    """
    parser = argparse.ArgumentParser(description="Regenerate the Contents block in communications-tracking.md")
    parser.add_argument("tracker", help="Path to communications-tracking.md")
    parser.add_argument("--update", action="store_true", help="Rewrite the Contents block in place (default: preview)")
    parser.add_argument(
        "--allow-shrink", action="store_true", help="With --update, accept a Contents with fewer entries than the current one"
    )
    args = parser.parse_args(argv)

    tracker_path = Path(args.tracker)
    if not tracker_path.exists():
        print(f"ERROR: file not found: {tracker_path}", file=sys.stderr)
        return 1

    content = tracker_path.read_text(encoding="utf-8")
    new_toc = build_toc_lines(content)
    if not new_toc:
        print(f"No entry headings ({', '.join(ENTRY_PREFIXES)}) found.", file=sys.stderr)
        return 1

    old_toc = read_old_toc(content)
    old_entries = [ln for ln in (old_toc or []) if _TOC_ENTRY.match(ln)]
    dropped = [ln for ln in old_entries if ln not in new_toc]

    if args.update:
        if old_toc is None:
            print("REFUSED: no '## Contents' heading; add one, then rerun.", file=sys.stderr)
            return 2
        if len(new_toc) < len(old_entries) and not args.allow_shrink:
            print(
                f"REFUSED: new Contents has fewer entries ({len(new_toc)}) than the current one ({len(old_entries)}). "
                "Lines that would go:",
                file=sys.stderr,
            )
            for ln in dropped:
                print(f"  {ln}", file=sys.stderr)
            print("Check the headings; rerun with --allow-shrink only if the removal is intended.", file=sys.stderr)
            return 2
        tracker_path.write_text(replace_contents(content, new_toc), encoding="utf-8")
        print(f"Updated: {tracker_path} ({len(new_toc)} TOC entries; was {len(old_entries)})")
        return 0

    print("=== Generated TOC ===")
    for line in new_toc:
        print(line)
    print(f"\n({len(new_toc)} entries; current Contents has {len(old_entries)})")
    if old_toc == new_toc:
        print("\nTOC is already up to date. No changes needed.")
    else:
        if len(new_toc) < len(old_entries):
            print(f"\nWARNING: {len(old_entries) - len(new_toc)} fewer entries; --update will refuse without --allow-shrink.")
        print("\nDifferences detected. Run with --update to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
