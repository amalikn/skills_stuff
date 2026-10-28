#!/usr/bin/env python3
"""Find `pgrep -f` / `pkill -f` patterns that are not anchored with `^`, which can match the automation's own command line. Read-only. Stdlib only.

Why (references/safety-and-writes.md, Learned 2026-10-26 and 2026-10-28): `-f` matches whole command lines, and the pattern's text keeps turning
up in other command lines: a shell script's own text is its `sh -c` line, Ansible `environment:` values sit on the remote command line, a
cron job's shell carries the job. An unanchored wait then waits on itself and a pkill ends its own session. Recurred four times in one
project (ansible-wifi smc_change, 2026-10-26 to 2026-10-28) although the rule was already written down, so it is now a check. Anchor at the
real program instead (`pgrep -f '^php artisan update:stats'`): a shell line starts with /bin/sh and cannot match.

Only literal quoted patterns are read; a pattern built at run time (`pgrep -f "$p"`) is not judged. Markdown is not scanned (docs show the
wrong form on purpose), and a call after a `#` on its line is a comment and is skipped.

Usage:
    process_match.py --project-root . [--roots roles,scripts] [--list]
Exit: 0 when every literal pattern is anchored, 1 when one is not, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: A pgrep or pkill call with an -f flag (alone or combined, e.g. -fc, -af) followed by a quoted literal pattern.
CALL = re.compile(r"""\b(?P<tool>pgrep|pkill)\b(?:\s+-\w+)*?\s+-[A-Za-z]*f[A-Za-z]*(?:\s+-\w+)*\s+(?P<q>['"])(?P<pat>[^'"\n]*)(?P=q)""")

SUFFIXES = {".sh", ".bash", ".yml", ".yaml", ".py", ".j2", ".service", ".timer", ".cron"}
SKIP_PARTS = {".venv", "venv", "node_modules", "__pycache__", ".git", "target", "dist", "build"}


def unanchored(text: str) -> list[tuple[int, str, str]]:
    """Unanchored pgrep/pkill -f patterns in a file's text.

    Args:
        text: the file's text.

    Returns:
        (line, tool, pattern) per pattern that does not start with ^.
    """
    out: list[tuple[int, str, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        hash_at = line.find("#")
        for m in CALL.finditer(line):
            if 0 <= hash_at < m.start():
                continue  # a shell or YAML comment: never executed
            pat = m.group("pat")
            if pat.startswith(("$", "{{")):
                continue  # built at run time (shell variable or Jinja): its text is not known here
            if not pat.startswith("^"):
                out.append((n, m.group("tool"), m.group("pat")))
    return out


def scan(root: Path, roots: list[str]) -> dict[str, list[tuple[int, str, str]]]:
    """Findings per file under the roots.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        {relative path: [(line, tool, pattern)]} for files with any.
    """
    found: dict[str, list[tuple[int, str, str]]] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES or SKIP_PARTS & set(path.parts):
                continue
            hits = unanchored(path.read_text(encoding="utf-8", errors="replace"))
            if hits:
                found[path.relative_to(root).as_posix()] = hits
    return found


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when every literal pattern is anchored, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [process_match] or [scan] roots, else src,scripts)")
    ap.add_argument("--list", action="store_true", help="print every finding (the default prints them too; kept for symmetry)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"process_match: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "process_match")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"process_match: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    found = scan(root, roots)
    for rel, hits in found.items():
        for line, tool, pat in hits:
            print(f"{rel}:{line}: {tool} -f '{pat}' is not anchored with ^; anchor it at the program's own command line (e.g. '^php artisan ...')")
    total = sum(len(h) for h in found.values())
    print(f"process_match: {'OK, every literal pgrep/pkill -f pattern is anchored' if not total else f'{total} unanchored pattern(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
