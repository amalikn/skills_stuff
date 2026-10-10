#!/usr/bin/env python3
"""Audit rotated records: every content line of a record before its first rotation is still live, archived, or in its open-items tracker, and no
entry was split (its first line moved, its wrapped tail left live). Stdlib plus git.

Why (2026-10-10): an early rotate_records.py treated prose under a Contents list as navigation and dropped 424 lines in one project, while
its own verification passed. This independent audit compares each record with its pre-rotation version in git, so a rotation bug cannot hide.

Usage:
    python scripts/audit_rotations.py ROOT [ROOT ...]        # every project with docs/history/readme.md under the roots
Exit: 0 when nothing is missing or split, 1 when a record lost lines or split an entry, 2 on bad arguments.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys
from collections import Counter

_spec = importlib.util.spec_from_file_location("rotate_records", pathlib.Path(__file__).resolve().parent / "rotate_records.py")
rotate_records = importlib.util.module_from_spec(_spec)
sys.modules["rotate_records"] = rotate_records
_spec.loader.exec_module(rotate_records)


def git(root: pathlib.Path, *args: str) -> str:
    """Run git in a folder.

    Args:
        root: the folder.
        args: git arguments.

    Returns:
        Its standard output.
    """
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def text_only(line: str) -> str:
    """A line with its markdown link targets blanked, so a relinked line still matches its original.

    Args:
        line: one line.

    Returns:
        The line with every `](target)` replaced by `]()`.
    """
    return re.sub(r"\]\([^)]*\)", "]()", line)


def audit(project: pathlib.Path, name: str) -> list[str] | None:
    """The content lines a record has lost since before its first rotation.

    Args:
        project: the project folder.
        name: `CHANGELOG.md` or `SCRATCHPAD.md`.

    Returns:
        The missing lines, then `SPLIT: <tail>` for each entry split across files; None when the record was never rotated or has no earlier
        version in git.
    """
    archives = sorted((project / "docs" / "history").glob(f"{name[:-3].lower()}-*.md"))
    if not archives:
        return None
    added = git(project, "log", "--diff-filter=A", "--format=%H", "--reverse", "--", str(archives[0].relative_to(project))).split()
    ref = f"{added[0]}~1" if added else "HEAD"
    before = subprocess.run(["git", "-C", str(project), "show", f"{ref}:./{name}"], capture_output=True, text=True).stdout
    if not before:
        return None
    have = Counter(l for l in rotate_records.content_lines((project / name).read_text()) if l.strip())
    have += Counter(l for a in archives for l in a.read_text().split("\n") if l.strip())
    trackers = sorted((project / "docs" / "trackers").glob("open-items-*.md")) if name == "SCRATCHPAD.md" else []
    # reference docs written by move_sections.py carry "Moved verbatim from `<record>`"; their sections left the record on purpose
    trackers += [d for d in sorted((project / "docs").rglob("*.md")) if "/history/" not in str(d) and d not in trackers
                 and f"Moved verbatim from `{name}`" in d.read_text(errors="replace")[:2000]]
    have += Counter(l for t in trackers for l in t.read_text().split("\n") if l.strip())
    have = Counter(text_only(l) for l in have.elements())
    lost = [l for l in Counter(l for l in rotate_records.content_lines(before) if l.strip()) if have[text_only(l)] < 1]
    moved = {text_only(l) for f in archives + trackers for l in f.read_text().split("\n")}
    live = {text_only(l) for l in (project / name).read_text().split("\n")}
    return lost + [f"SPLIT: {l}" for l in split_tails(before, live, moved)]


def split_tails(before: str, live: set[str], moved: set[str]) -> list[str]:
    """Tails of wrapped list items whose first line was rotated away while the tail stayed live (rotations before 2026-10-10).

    Args:
        before: the record's text before its first rotation.
        live: the live record's lines, link targets blanked.
        moved: the archives' and trackers' lines, link targets blanked.

    Returns:
        The first line of each tail left behind.
    """
    lines = before.split("\n")
    out = []
    for i, line in enumerate(lines[:-1]):
        head, tail = text_only(line), text_only(lines[i + 1])
        if (line.startswith("- ") or re.match(r"^\d+[.)] ", line)) and rotate_records.lazy_continuation(lines[i + 1]) \
                and head in moved and head not in live and tail in live and tail not in moved:
            out.append(lines[i + 1])
    return out


def main(argv: list[str] | None = None) -> int:
    """Audit every rotated record under the roots.

    Args:
        argv: root folders; None reads sys.argv.

    Returns:
        0 when nothing is missing, 1 when a record lost lines, 2 without roots.
    """
    roots = argv if argv is not None else sys.argv[1:]
    if not roots:
        print(__doc__.split("\n\n")[-2], file=sys.stderr)
        return 2
    bad = 0
    for root in roots:
        for index in sorted(pathlib.Path(root).resolve().rglob("docs/history/readme.md")):
            project = index.parent.parent.parent
            for name in ("CHANGELOG.md", "SCRATCHPAD.md"):
                missing = audit(project, name)
                if missing is None:
                    continue
                bad += bool(missing)
                split = [m for m in missing if m.startswith("SPLIT: ")]
                lost = [m for m in missing if not m.startswith("SPLIT: ")]
                tag = "LOST" if lost else "SPLIT" if split else "OK  "
                detail = f": {len(lost)} line(s) lost, e.g. {lost[0][:90]!r}" if lost else f": {len(split)} entry tail(s) left live, e.g. {split[0][7:97]!r}" if split else ""
                print(f"{tag} {project}/{name}{detail}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
