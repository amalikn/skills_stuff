#!/usr/bin/env python3
"""Find inline linter suppressions (noqa, type: ignore, shellcheck disable, eslint-disable, nolint, allow), as a shrink-only ratchet.
Read-only unless --write-baseline. Stdlib only.

Why (operator rule, references/documentation-and-headers.md: never silence a linter inline): a suppression hides the finding instead of fixing
it, and an agent under pressure adds one rather than restructure the code (2026-10-20: a `# noqa: E402` was written into a new test, and only
review caught it). Existing ones are counted per file so adoption is possible; a new one fails the check.

Python comments are read with `tokenize`, so a marker inside a string never counts. Other languages are read per line: a marker counts only
after that language's comment opener (`#`, `//`, `--`, `/*`), or as Rust's `#[allow(` / `#![allow(` attribute.

Usage:
    suppressions.py --project-root . [--roots src,scripts] [--baseline scripts/suppressions-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more suppressions than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import tokenize
from pathlib import Path

import code_map
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Python comment markers that silence a linter or type checker.
PY_MARKERS = re.compile(r"\bnoqa\b|\btype:\s*ignore\b|\bpylint:\s*disable|\bpyright:\s*ignore\b|\bmypy:\s*ignore|\bruff:\s*noqa\b", re.I)

#: Per file suffix: (comment openers, markers). A marker counts only after an opener on the same line.
LANGUAGES: dict[str, tuple[tuple[str, ...], re.Pattern]] = {
    ".sh": (("#",), re.compile(r"shellcheck\s+disable=")),
    ".bash": (("#",), re.compile(r"shellcheck\s+disable=")),
    ".js": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".mjs": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".cjs": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".jsx": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".ts": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".tsx": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".go": (("//",), re.compile(r"\bnolint\b")),
    ".sql": (("--",), re.compile(r"\bnoqa\b")),
    ".yml": (("#",), re.compile(r"yamllint\s+disable")),
    ".yaml": (("#",), re.compile(r"yamllint\s+disable")),
}
#: Rust silences lints with an attribute, not a comment.
RUST_ALLOW = re.compile(r"^\s*#!?\[allow\(")

SKIP_PARTS = {".venv", "venv", "node_modules", "__pycache__", ".git", "target", "dist", "build"}


def python_suppressions(text: str) -> list[tuple[int, str]]:
    """Suppression comments in Python source.

    Args:
        text: the source.

    Returns:
        (line, comment text) per suppression; a source that does not tokenize gives what was read before the error.
    """
    out: list[tuple[int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT and PY_MARKERS.search(tok.string):
                out.append((tok.start[0], tok.string.strip()))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


def line_suppressions(text: str, suffix: str) -> list[tuple[int, str]]:
    """Suppressions in a non-Python file, read per line.

    Args:
        text: the file's text.
        suffix: its suffix (".sh", ".ts", ".rs", ...).

    Returns:
        (line, text) per suppression; an unknown suffix gives none.
    """
    out: list[tuple[int, str]] = []
    if suffix == ".rs":
        return [(n, line.strip()) for n, line in enumerate(text.splitlines(), 1) if RUST_ALLOW.match(line)]
    if suffix not in LANGUAGES:
        return out
    openers, marker = LANGUAGES[suffix]
    for n, line in enumerate(text.splitlines(), 1):
        starts = [line.find(o) for o in openers if o in line]
        if not starts:
            continue
        comment = line[min(starts):]
        if marker.search(comment):
            out.append((n, comment.strip()))
    return out


def suppressions(path: Path) -> list[tuple[int, str]]:
    """Suppressions in one file, by its suffix.

    Args:
        path: the file.

    Returns:
        (line, text) per suppression.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    return python_suppressions(text) if path.suffix == ".py" else line_suppressions(text, path.suffix)


def measure(root: Path, roots: list[str]) -> tuple[dict[str, float], dict[str, list]]:
    """Suppressions per file under the roots.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        ({path: count} for files with any, {path: [(line, text)]}).
    """
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    wanted = {".py", ".rs", *LANGUAGES}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file() or path.suffix not in wanted or SKIP_PARTS & set(path.parts):
                continue
            found = suppressions(path)
            if found:
                rel = path.relative_to(root).as_posix()
                counts[rel], detail[rel] = len(found), found
    return counts, detail


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [suppressions] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [suppressions] baseline, else scripts/suppressions-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every suppression")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"suppressions: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "suppressions")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"suppressions: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    base_path = root / (args.baseline or code_map.section(cmap, "suppressions").get("baseline", "scripts/suppressions-baseline.json"))
    counts, detail = measure(root, roots)
    if args.list:
        for rel, found in detail.items():
            for line, text in found:
                print(f"{rel}:{line}: {text}")
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"suppressions: baseline written, {sum(counts.values()):g} suppression(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "suppressions", base_path):
        print(line)
    if verdict.ok:
        print(f"suppressions: OK, {sum(counts.values()):g} suppression(s), all within the baseline")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
