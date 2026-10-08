#!/usr/bin/env python3
"""Measure and hold a project's Python docstrings to the global standard, as a ratchet that only tightens. Stdlib only.

Why (operator, 2026-10-08): "create the docstrings for the code whenever you are creating or updating a script", "specify what are the arguments
passed and what is returned", "make it as a standard for all the scripts". The standard lives in the global policy (~/.agents/AGENTS.md) and in
governance `categories/naming-and-file-summary-guide.md` (Code docstrings): every module, class and function has a docstring; a function names each
parameter under `Args:` and, when it returns a value, says what under `Returns:`.

A project with years of code cannot meet that in one change, so this counts the shortfalls per file and keeps a baseline (JSON, {path: count}). A new
file must have none, a file's count may never rise, and a count that fell must be written into the baseline. First built as a check in
unified-network-controller's `scripts/check_governance.py` (`check_docstrings`); this is the same rule for any project.

Usage:
    python scripts/docstring_ratchet.py --project-root /path/to/project                      # report, compare with the baseline; exit 1 on a regression
    python scripts/docstring_ratchet.py --project-root . --write-baseline                     # record today's counts (adopting the standard)
    python scripts/docstring_ratchet.py --project-root . --roots scripts,src --baseline scripts/docstring-baseline.json --list
Exit: 0 when every file is at or below its baseline (and no file fell below it unrecorded), 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

DEFAULT_ROOTS = ("scripts",)
DEFAULT_BASELINE = "scripts/docstring-baseline.json"
SKIP_PARTS = ("__pycache__", "/migrations/", "/.venv/", "/node_modules/")


def returns_value(fn: ast.AST) -> bool:
    """Whether a function returns a value.

    Args:
        fn: a FunctionDef or AsyncFunctionDef node.

    Returns:
        True when its return annotation is not None, or, unannotated, when a `return <value>` appears in its body.
    """
    if fn.returns is not None:
        return not (isinstance(fn.returns, ast.Constant) and fn.returns.value is None)
    return any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(fn))


def shortfalls(text: str) -> list[str]:
    """Every docstring that is absent or short of the standard in one source file.

    Args:
        text: the Python source.

    Returns:
        One entry per shortfall: `<module>` or a class/function name when its docstring is absent, `name (args: a, b)` when parameters are
        not named under `Args:`, `name (returns)` when a value is returned and `Returns:` is missing.

    Raises:
        SyntaxError: when the source does not parse.
    """
    tree = ast.parse(text)
    out = ["<module>"] if ast.get_docstring(tree) is None else []
    for n in ast.walk(tree):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        doc = ast.get_docstring(n)
        if doc is None:
            out.append(n.name)
            continue
        if isinstance(n, ast.ClassDef):
            continue
        params = [a.arg for a in (*n.args.posonlyargs, *n.args.args, *n.args.kwonlyargs) if a.arg not in ("self", "cls")]
        params += [a.arg for a in (n.args.vararg, n.args.kwarg) if a is not None]
        unnamed = [p for p in params if not re.search(rf"^\s+\*{{0,2}}{re.escape(p)}\s*(\(|:)", doc, re.M)]
        if params and ("Args:" not in doc or unnamed):
            out.append(f"{n.name} (args: {', '.join(unnamed or params)})")
        if returns_value(n) and "Returns:" not in doc:
            out.append(f"{n.name} (returns)")
    return out


def measure(root: pathlib.Path, roots: list[str]) -> dict[str, list[str]]:
    """The shortfalls of every Python file under the given folders.

    Args:
        root: the project root.
        roots: folders under it to scan (missing ones are skipped).

    Returns:
        {project-relative path: shortfalls}, for every file scanned (an empty list when it meets the standard).
    """
    out: dict[str, list[str]] = {}
    for d in roots:
        for p in sorted((root / d).rglob("*.py")):
            rel = p.relative_to(root).as_posix()
            if any(part in f"/{rel}" for part in SKIP_PARTS):
                continue
            try:
                out[rel] = shortfalls(p.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                out[rel] = [f"<does not parse: {exc.msg} line {exc.lineno}>"]
    return out


def compare(found: dict[str, list[str]], baseline: dict[str, int]) -> tuple[list[str], list[str]]:
    """Regressions and unrecorded gains against the baseline.

    Args:
        found: shortfalls per file, as measure() gives them.
        baseline: {path: allowed count}; a file not in it is allowed none.

    Returns:
        (one line per file above its baseline, one line per file below it whose new count must be written down).
    """
    worse, better = [], []
    for rel, items in found.items():
        allowed = baseline.get(rel, 0)
        if len(items) > allowed:
            worse.append(f"{rel}: {len(items)} shortfall(s), allowed {allowed}: {', '.join(items[:8])}")
        elif len(items) < allowed:
            better.append(f"{rel}: {len(items)} shortfall(s), baseline {allowed}: lower it")
    return worse, better


def main() -> int:
    """Measure, then write the baseline or compare with it (see the module docstring).

    Returns:
        0 when the project holds its baseline, 1 on a regression or an unrecorded gain, 2 when the project root does not exist.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".", help="the project to measure (default: the current folder)")
    ap.add_argument("--roots", default=",".join(DEFAULT_ROOTS), help="comma-separated folders under the root to scan (default: scripts)")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE, help=f"baseline JSON, relative to the root (default: {DEFAULT_BASELINE})")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts as the baseline (when adopting the standard)")
    ap.add_argument("--list", action="store_true", help="print every shortfall, file by file")
    args = ap.parse_args()
    root = pathlib.Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"no such project root: {root}")
        return 2
    found = measure(root, [r.strip() for r in args.roots.split(",") if r.strip()])
    total = sum(len(v) for v in found.values())
    print(f"{len(found)} file(s), {total} shortfall(s) in {sum(1 for v in found.values() if v)} file(s)")
    if args.list:
        for rel, items in found.items():
            if items:
                print(f"  {rel}: {', '.join(items)}")
    path = root / args.baseline
    if args.write_baseline:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({k: len(v) for k, v in sorted(found.items()) if v}, indent=1) + "\n", encoding="utf-8")
        print(f"baseline written: {path.relative_to(root)}")
        return 0
    baseline = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    worse, better = compare(found, baseline)
    for line in worse:
        print(f"FAIL {line}")
    for line in better:
        print(f"LOWER {line}")
    return 1 if worse or better else 0


if __name__ == "__main__":
    sys.exit(main())
