#!/usr/bin/env python3
"""Audit rotated records: every content line of a record before its first rotation is still live, archived, or in its open-items tracker. Stdlib plus git.

Why (2026-10-10): an early rotate_records.py treated prose under a Contents list as navigation and dropped 424 lines in one project, while
its own verification passed. This independent audit compares each record with its pre-rotation version in git, so a rotation bug cannot hide.

Usage:
    python scripts/audit_rotations.py ROOT [ROOT ...]        # every project with docs/history/readme.md under the roots
Exit: 0 when nothing is missing, 1 when a record lost lines, 2 on bad arguments.
"""

from __future__ import annotations

import importlib.util
import pathlib
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


def audit(project: pathlib.Path, name: str) -> list[str] | None:
    """The content lines a record has lost since before its first rotation.

    Args:
        project: the project folder.
        name: `CHANGELOG.md` or `SCRATCHPAD.md`.

    Returns:
        The missing lines; None when the record was never rotated or has no earlier version in git.
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
    have += Counter(l for t in trackers for l in t.read_text().split("\n") if l.strip())
    return [l for l in Counter(l for l in rotate_records.content_lines(before) if l.strip())
            if have[l] < 1 and have[rotate_records.relink([l], "", "docs/history")[0]] < 1
            and have[rotate_records.relink([l], "", "docs/trackers")[0]] < 1]


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
                print(f"{'OK  ' if not missing else 'LOST'} {project}/{name}" + (f": {len(missing)} line(s), e.g. {missing[0][:90]!r}" if missing else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
