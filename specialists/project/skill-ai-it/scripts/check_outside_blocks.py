#!/usr/bin/env python3
"""Confirm that a navigation upgrade changed only the text inside skill-ai-it's managed blocks.

The upgrader replaces each managed block and promises to leave everything else alone. check_expected_diff.py checks which
files changed; this checks what changed inside them: each file's text with its managed blocks removed must be identical at a
git ref (default HEAD, the state before the upgrade) and in the working tree. Run it after the upgrade and before committing.
Stdlib only; read-only.

Usage:
    python scripts/check_outside_blocks.py --project-root /path/to/project
    python scripts/check_outside_blocks.py --project-root . --ref a5f2c33~1 --files AI_NAVIGATION.md AGENTS.md
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_FILES = ("AGENTS.md", "AI_NAVIGATION.md", "scripts/README.md")
# Both marker families the upgrader writes: BEGIN/END MANAGED blocks and the managed:/ /managed: governance-checks block.
BLOCK = re.compile(
    r"<!-- BEGIN MANAGED: (?P<a>[\w:.-]+) -->.*?<!-- END MANAGED: (?P=a) -->"
    r"|<!-- managed:(?P<b>[\w:.-]+)[^>]*-->.*?<!-- /managed:(?P=b) -->",
    re.S,
)


def strip_blocks(text: str) -> str:
    """Remove every managed block, markers included, leaving a placeholder line so neighbouring text stays apart.

    Args:
        text: the file's full text.

    Returns:
        The text outside the managed blocks.
    """
    return BLOCK.sub("<!-- managed block -->", text)


def text_at_ref(root: Path, ref: str, rel: str) -> str | None:
    """Read a file's text at a git ref.

    Args:
        root: the project root (inside a git work tree).
        ref: the git ref to read, for example HEAD.
        rel: the file path relative to the project root.

    Returns:
        The file's text, or None when the file does not exist at that ref.
    """
    res = subprocess.run(["git", "-C", str(root), "show", f"{ref}:./{rel}"], capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else None


def compare(root: Path, ref: str, files: list[str]) -> list[tuple[str, list[str]]]:
    """Compare each file's outside-block text at the ref with the working tree.

    Args:
        root: the project root.
        ref: the git ref holding the state before the upgrade.
        files: paths relative to the root.

    Returns:
        One (path, diff lines) pair per file that differs or is missing on one side; empty when all match.
    """
    out = []
    for rel in files:
        before = text_at_ref(root, ref, rel)
        path = root / rel
        after = path.read_text() if path.exists() else None
        if before is None or after is None:
            if before != after:
                out.append((rel, [f"missing {'at ' + ref if before is None else 'in the working tree'}"]))
            continue
        a, b = strip_blocks(before), strip_blocks(after)
        if a != b:
            out.append((rel, list(difflib.unified_diff(a.splitlines(), b.splitlines(), f"{ref}:{rel}", rel, n=1, lineterm=""))))
    return out


def main(argv: list[str] | None = None) -> int:
    """Run the comparison and print one line per file.

    Args:
        argv: command-line arguments; sys.argv when None.

    Returns:
        0 when every file's outside-block text matches, 1 otherwise.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--ref", default="HEAD", help="git ref holding the state before the upgrade (default HEAD)")
    ap.add_argument("--files", nargs="+", default=list(DEFAULT_FILES))
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    diffs = dict(compare(root, args.ref, args.files))
    for rel in args.files:
        if rel in diffs:
            print(f"DIFFERS {rel}")
            for line in diffs[rel][:40]:
                print(f"  {line}")
        else:
            print(f"OK      {rel}: outside-block text identical")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
