#!/usr/bin/env python3
"""Check that every runnable script's native header says what it is for, how to run it and what it touches, as a shrink-only ratchet.
Read-only unless --write-baseline. Stdlib only.

Why (operator, 2026-10-19: "should we also define front matter ... for individual scripts"): a script's header is its front matter, in the form
its language allows (governance `naming-and-file-summary-guide.md`, "File headers"): the module docstring for Python, the leading `#` comment
block (after the shebang) for shell. skill-ai-it's doc_freshness.py already fails a file with no summary line; this adds what a reader needs
before running it:

    summary   the first line says what the script is for
    run       a `Usage:` or `Run:` line (or `Imported, not run` for a module that is only imported)
    safety    what it touches: read-only, files only, or how its writes are gated (`--apply`, a plan/apply subcommand)

Only entry points are checked (Python with a `__main__` block, shell with a shebang); a library module needs only its summary.

Usage:
    script_headers.py --project-root . [--roots scripts,src] [--baseline scripts/script-headers-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more missing parts than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: The header parts and how each is recognised.
PARTS = {
    "run": re.compile(r"(?im)^\s*(?:usage|run)\b.*:|\bimported, not run\b"),
    "safety": re.compile(r"(?i)\bread[- ]only\b|\bfiles only\b|--apply\b|\bwrites?\b|\bdry[- ]run\b|\bplan\b|\bchanges nothing\b|\bno side effects\b"),
}
SHELL_SUFFIXES = (".sh", ".bash")


def header(text: str, suffix: str) -> str | None:
    """A script's header in its native form.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        The Python module docstring, or the shell comment block after the shebang (without `#`); None when the file has none or does not parse.
    """
    if suffix == ".py":
        try:
            return ast.get_docstring(pyparse.parse(text))
        except SyntaxError:
            return None
    lines = text.splitlines()[1:] if text.startswith("#!") else text.splitlines()
    block = []
    for line in lines:
        if not line.startswith("#"):
            break
        block.append(line.lstrip("#").strip())
    return "\n".join(block).strip() or None


def is_entry(text: str, suffix: str) -> bool:
    """Whether a file is meant to be run.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        True for Python with a `__main__` block or a shell script with a shebang.
    """
    if suffix == ".py":
        return re.search(r"""__name__\s*==\s*["']__main__["']""", text) is not None
    return suffix in SHELL_SUFFIXES and text.startswith("#!")


def missing_parts(text: str, suffix: str) -> list[str]:
    """Which header parts a runnable script lacks.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        A subset of ["summary", "run", "safety"] (all three when there is no header); empty for a library module with a summary.
    """
    head = header(text, suffix)
    if not head:
        return ["summary", "run", "safety"] if is_entry(text, suffix) else ["summary"]
    if not is_entry(text, suffix):
        return []
    return [name for name, pattern in PARTS.items() if not pattern.search(head)]


def measure(root: Path, roots: list[str]) -> dict[str, list[str]]:
    """Missing header parts per script.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        {path: missing parts} for files missing any.
    """
    out: dict[str, list[str]] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if path.suffix not in (".py", *SHELL_SUFFIXES) or not path.is_file() or "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            missing = missing_parts(path.read_text(encoding="utf-8", errors="replace"), path.suffix)
            if missing:
                out[path.relative_to(root).as_posix()] = missing
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else scripts,src)")
    ap.add_argument("--baseline", default="scripts/script-headers-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every script with a missing header part")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        wanted = args.roots or code_map.scan_roots(code_map.for_root(root, args.code_map), default="scripts,src")
    except (OSError, ValueError) as exc:
        print(f"script_headers: {exc}", file=sys.stderr)
        return 2
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"script_headers: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    found = measure(root, roots)
    counts = {rel: len(parts) for rel, parts in found.items()}
    if args.list:
        print("\n".join(f"{rel}: header lacks {', '.join(parts)}" for rel, parts in found.items()))
    base_path = root / args.baseline
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"script_headers: baseline written, {len(counts)} file(s) with gaps")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    print("\n".join(ratchet.report(verdict, "header", base_path)) or f"script_headers: OK, {len(counts)} file(s) with gaps, all within the baseline")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
