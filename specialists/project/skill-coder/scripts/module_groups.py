#!/usr/bin/env python3
"""Report folders where three or more code files share a name prefix: a module family that wants to be a package. Read-only, warn only. Stdlib only.

Why (operator, 2026-10-19: "when modularising a large piece of code, is it better to create a subdirectory under scripts and put all the related
modules under that relevant folder with a proper name? If so, then make it part of the skill coder logic"): a shared prefix (`flowmap_model.py`,
`flowmap_overview.py`, `flowmap_pages.py`) is a folder trying to exist. The rule and its exceptions are in references/module-and-function-shape.md,
"Grouping modules into packages". This helper finds the candidates; whether to move them is a judgement (a refactor), so it never fails by default.

A prefix is the file name up to its first `_` or `-`. Test files (`test_`) and the files a language names by convention are not grouped.

Usage:
    module_groups.py --project-root . [--roots scripts,src] [--min 3] [--strict]
Exit: 0 (warn only); with --strict 1 when a candidate exists; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: Code file suffixes grouped.
CODE_SUFFIXES = (".py", ".sh", ".bash", ".js", ".mjs", ".ts", ".go", ".rs")
#: Prefixes never grouped: test files are named by the test runner's convention, not by feature.
EXEMPT_PREFIXES = ("test", "conftest")
#: Folders never walked.
SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".venv", "venv", "fixtures"}
PREFIX = re.compile(r"^([A-Za-z0-9]+)[_-].+")


def prefix_of(name: str) -> str | None:
    """A code file's family prefix.

    Args:
        name: the file name.

    Returns:
        The text before the first `_` or `-` of a code file's stem, or None for a non-code file, a one-word name or an exempt prefix.
    """
    path = Path(name)
    if path.suffix not in CODE_SUFFIXES:
        return None
    m = PREFIX.match(path.stem)
    if not m or m.group(1).lower() in EXEMPT_PREFIXES:
        return None
    return m.group(1)


def candidates(root: Path, roots: list[str], least: int = 3) -> list[tuple[str, str, list[str]]]:
    """Every folder under the roots with `least` or more code files sharing a prefix.

    Args:
        root: the project root.
        roots: folders under it to walk.
        least: the smallest family reported.

    Returns:
        (folder relative to root, prefix, file names) per family, sorted by folder then prefix.
    """
    out = []
    for folder in roots:
        base = root / folder
        dirs = [base, *sorted(p for p in base.rglob("*") if p.is_dir())] if base.is_dir() else []
        for d in dirs:
            if any(part in SKIP_DIRS or part.startswith(".") for part in d.relative_to(root).parts):
                continue
            families: dict[str, list[str]] = {}
            for f in sorted(p for p in d.iterdir() if p.is_file()):
                if (pre := prefix_of(f.name)) is not None:
                    families.setdefault(pre, []).append(f.name)
            for pre, names in sorted(families.items()):
                if len(names) >= least:
                    out.append((d.relative_to(root).as_posix(), pre, names))
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 (warn only), or 1 with --strict when a candidate exists; 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else scripts,src)")
    ap.add_argument("--min", type=int, default=3, help="the smallest family reported (default 3)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a candidate exists")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        wanted = args.roots or code_map.scan_roots(code_map.for_root(root, args.code_map), default="scripts,src")
    except (OSError, ValueError) as exc:
        print(f"module_groups: {exc}", file=sys.stderr)
        return 2
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots or args.min < 2:
        print(f"module_groups: no folder of {wanted} under {root}, or --min below 2", file=sys.stderr)
        return 2
    found = candidates(root, roots, args.min)
    for folder, pre, names in found:
        print(f"{folder}: {len(names)} files share `{pre}`: {', '.join(names)}; candidate package {folder}/{pre}/")
    print(f"module_groups: {len(found)} candidate famil{'y' if len(found) == 1 else 'ies'} (references/module-and-function-shape.md, "
          "'Grouping modules into packages')")
    return 1 if (args.strict and found) else 0


if __name__ == "__main__":
    sys.exit(main())
