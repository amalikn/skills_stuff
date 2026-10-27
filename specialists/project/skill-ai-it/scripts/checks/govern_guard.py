"""Refuse `just govern` while a file it may change holds uncommitted work. Stdlib only.

govern rewrites governed files in place (navigation blocks, headers, recipes, rotation, baselines). On enterprise-strategy (2026-10-14) it ran
over an uncommitted CHANGELOG and history index, and its edits could not be split from the operator's afterwards. This guard runs first and
lists the governed paths that are modified, staged or untracked; commit or stash them, or set GOVERN_ALLOW_DIRTY=1 to run anyway.

Usage:
    python scripts/checks/govern_guard.py --project-root P    # exit 1 and list the dirty governed paths; 0 when clean or not in git
Exit: 0 clean (or no git repository), 1 dirty governed paths, 2 bad arguments.

Read-only: it runs `git status` and writes nothing.
"""

from __future__ import annotations

import argparse
import fnmatch
import pathlib
import subprocess
import sys

#: paths, relative to the project root, that govern's steps may write (upgrade, adopt, budget and rotation, baselines)
GOVERNED = ("AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "README.md", "ARCHITECTURE.md", "CONVENTIONS.md", "SETUP.md", "SCRATCHPAD.md",
            "CHANGELOG.md", "ROADMAP.md", "context-map.yaml", "justfile", "scripts/README.md", "scripts/*-baseline.json", "docs/history/*",
            "docs/trackers/*")


def dirty_governed(root: pathlib.Path) -> list[str] | None:
    """The governed paths under `root` with uncommitted changes.

    Args:
        root: the project root.

    Returns:
        Sorted project-relative paths, or None when `root` is not inside a git work tree.
    """
    inside = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, timeout=60)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return None
    prefix = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-prefix"], capture_output=True, text=True, check=True, timeout=60).stdout.strip()
    # porcelain paths are relative to the repository root, so the project's prefix is stripped from each
    out = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "-z", "--untracked-files=all", "--", "."],
                         capture_output=True, text=True, check=True, timeout=60).stdout
    paths, entries = [], out.split("\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        if entry[0] in "RC":  # a rename or copy carries its source path as the next entry
            i += 1
        path = entry[3:].removeprefix(prefix)
        if any(fnmatch.fnmatch(path, pat) for pat in GOVERNED):
            paths.append(path)
    return sorted(set(paths))


def main(argv: list[str] | None = None) -> int:
    """Report and gate on dirty governed paths.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        0 clean or not in git, 1 dirty governed paths, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    dirty = dirty_governed(root)
    if dirty is None:
        print("govern guard: not a git work tree; nothing to protect, continuing")
        return 0
    if not dirty:
        return 0
    print(f"govern guard: {len(dirty)} governed file(s) hold uncommitted work; govern's edits could not be separated from it:")
    for p in dirty:
        print(f"  {p}")
    print("commit or stash them first, or run with GOVERN_ALLOW_DIRTY=1")
    return 1


if __name__ == "__main__":
    sys.exit(main())
