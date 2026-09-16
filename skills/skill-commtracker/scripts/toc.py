#!/usr/bin/env python3
"""
commtracker/toc.py — Regenerate the ## Contents TOC in a communications-tracking.md
from its ## Email N / ## Teams N headings.

Usage:
    python toc.py <tracker-file>
        [--update]   rewrite Contents section in-place (default: print diff to stdout)
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# GFM anchor generation
# Matches GitHub-Flavored Markdown heading anchor rules exactly.
# ---------------------------------------------------------------------------

def gfm_anchor(heading_text: str) -> str:
    # Lowercase
    text = heading_text.lower()
    # Remove anything that isn't alphanumeric, space, or hyphen
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text.strip())
    return text


# ---------------------------------------------------------------------------
# Heading → TOC line
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r'^## (.+)$')
_ENTRY_RE   = re.compile(r'^(Email|Teams)\s+[\da-z]+\s*[-–]', re.IGNORECASE)


def heading_to_toc_line(heading_text: str) -> str:
    anchor = gfm_anchor(heading_text)
    return f"- [{heading_text}](#{anchor})"


# ---------------------------------------------------------------------------
# Parse tracker
# ---------------------------------------------------------------------------

def build_toc_lines(content: str) -> list[str]:
    toc_lines = []
    for line in content.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            heading_text = m.group(1).strip()
            if _ENTRY_RE.match(heading_text):
                toc_lines.append(heading_to_toc_line(heading_text))
    return toc_lines


# ---------------------------------------------------------------------------
# Replace Contents section
# ---------------------------------------------------------------------------

_CONTENTS_START = re.compile(r'^## Contents\s*$', re.IGNORECASE)
_SEPARATOR      = re.compile(r'^---\s*$')


def replace_contents(content: str, new_toc_lines: list[str]) -> str:
    lines = content.splitlines(keepends=True)
    out = []
    state = "before"   # before | in_contents | after

    for line in lines:
        stripped = line.rstrip('\n').rstrip('\r')

        if state == "before":
            out.append(line)
            if _CONTENTS_START.match(stripped):
                state = "in_contents"
                # Write new TOC immediately after the heading
                out.append("\n")
                for toc_line in new_toc_lines:
                    out.append(toc_line + "\n")
            continue

        if state == "in_contents":
            # Skip old TOC lines until we hit the first --- separator
            if _SEPARATOR.match(stripped):
                out.append(line)
                state = "after"
            # else skip old TOC content
            continue

        if state == "after":
            out.append(line)

    return "".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Regenerate TOC in communications-tracking.md")
    parser.add_argument("tracker", help="Path to communications-tracking.md")
    parser.add_argument("--update", action="store_true",
                        help="Rewrite the Contents section in-place (default: print diff)")
    args = parser.parse_args()

    tracker_path = Path(args.tracker)
    if not tracker_path.exists():
        print(f"ERROR: file not found: {tracker_path}", file=sys.stderr)
        sys.exit(1)

    content = tracker_path.read_text(encoding="utf-8")
    new_toc = build_toc_lines(content)

    if not new_toc:
        print("No Email/Teams headings found.", file=sys.stderr)
        sys.exit(1)

    new_content = replace_contents(content, new_toc)

    if args.update:
        tracker_path.write_text(new_content, encoding="utf-8")
        print(f"Updated: {tracker_path} ({len(new_toc)} TOC entries)")
    else:
        # Print diff-style preview
        print("=== Generated TOC ===")
        for line in new_toc:
            print(line)
        print(f"\n({len(new_toc)} entries)")

        # Check if different from current
        old_toc = []
        in_contents = False
        for line in content.splitlines():
            if _CONTENTS_START.match(line.strip()):
                in_contents = True
                continue
            if in_contents:
                if _SEPARATOR.match(line.strip()):
                    break
                if line.strip():
                    old_toc.append(line.strip())

        if old_toc == new_toc:
            print("\nTOC is already up to date. No changes needed.")
        else:
            print("\nDifferences detected. Run with --update to apply.")


if __name__ == "__main__":
    main()
