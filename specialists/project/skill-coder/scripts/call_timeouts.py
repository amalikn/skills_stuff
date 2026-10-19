#!/usr/bin/env python3
"""Find Python calls to the network or a subprocess that pass no timeout, as a shrink-only ratchet. Read-only unless --write-baseline. Stdlib only.

Why (unified-network-controller code architecture design, rule R15; its Phase 1 review found 16 of 96 such calls without one): a call with no
timeout can hang a job, a page or a whole collector cycle forever, and the hang looks like slowness rather than a fault. Every subprocess, HTTP
request and socket connect states how long it may take.

Found through `ast`, so only real calls count (not text in strings): subprocess.run/call/check_call/check_output, Popen(...).communicate/wait,
urllib.request.urlopen, requests/httpx verbs and request(), socket.create_connection. A call passing `**kwargs` is trusted (the timeout may be
inside). Other languages: see the pack's languages/ notes for the equivalent rule and linter.

Usage:
    call_timeouts.py --project-root . [--roots src,scripts] [--baseline scripts/timeout-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more untimed calls than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Dotted call names that must carry `timeout=`, by their last two parts (module.function or object.method).
NEEDS_TIMEOUT = {
    "subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output",
    "request.urlopen", "urllib.urlopen", "socket.create_connection",
    "requests.get", "requests.post", "requests.put", "requests.patch", "requests.delete", "requests.head", "requests.request",
    "httpx.get", "httpx.post", "httpx.put", "httpx.patch", "httpx.delete", "httpx.request",
}
#: Bare method names that must carry a timeout wherever they are called on a Popen.
POPEN_METHODS = {"communicate", "wait"}


def _dotted(node: ast.AST) -> str:
    """A call target as dotted text (`subprocess.run`), or "" when it is not a plain name chain.

    Args:
        node: the call's func node.

    Returns:
        The dotted name.
    """
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def untimed_calls(text: str, popen_names: frozenset = frozenset(), grammar: tuple[int, int] | None = None) -> list[tuple[int, str]]:
    """Calls in Python source that need a timeout and pass none.

    Args:
        text: the source.
        popen_names: variable names known to hold a Popen (found by the caller); `x.communicate()` on them counts.
        grammar: (major, minor) to parse with the target project's grammar; None for this interpreter's.

    Returns:
        (line, call name) per untimed call.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it).
    """
    tree = pyparse.parse(text, grammar)
    popens = set(popen_names)
    for node in ast.walk(tree):   # names bound to subprocess.Popen(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and _dotted(node.value.func).endswith("Popen"):
            popens |= {t.id for t in node.targets if isinstance(t, ast.Name)}
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _dotted(node.func)
        tail = ".".join(name.split(".")[-2:])
        popen_call = isinstance(node.func, ast.Attribute) and node.func.attr in POPEN_METHODS and _dotted(node.func.value) in popens
        if tail not in NEEDS_TIMEOUT and not popen_call:
            continue
        if any(k.arg == "timeout" or k.arg is None for k in node.keywords):
            continue
        out.append((node.lineno, name))
    return out


def measure(root: Path, roots: list[str], grammar: tuple[int, int] | None = None) -> tuple[dict[str, float], dict[str, list], list[str]]:
    """Untimed calls per file.

    Args:
        root: the project root.
        roots: folders to scan.
        grammar: the Python grammar to parse with.

    Returns:
        ({path: count} for files with any, {path: [(line, name)]}, ["path: error"] for files that do not parse).
    """
    unparsed: list[str] = []
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*.py")):
            if {".venv", "venv", "node_modules", "__pycache__"} & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                found = untimed_calls(path.read_text(encoding="utf-8", errors="replace"), grammar=grammar)
            except SyntaxError as exc:
                unparsed.append(f"{rel}: line {exc.lineno}: {exc.msg}")
                continue
            if found:
                counts[rel], detail[rel] = len(found), found
    return counts, detail, unparsed


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [timeouts] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [timeouts] baseline, else scripts/timeout-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every untimed call")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--python", help="parse at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"call_timeouts: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "timeouts")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"call_timeouts: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    grammar = code_map.grammar(args.python, cmap)
    args.baseline = args.baseline or code_map.section(cmap, "timeouts").get("baseline", "scripts/timeout-baseline.json")
    counts, detail, unparsed = measure(root, roots, grammar)
    for line in unparsed:
        print(f"FAIL unparsed: {line} (not checked; check --python matches the project)")
    if args.list:
        for rel, calls in detail.items():
            for line, name in calls:
                print(f"{rel}:{line}: {name}() has no timeout")
    base_path = root / args.baseline
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"call_timeouts: baseline written, {sum(counts.values()):g} untimed call(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "timeouts", base_path):
        print(line)
    if verdict.ok:
        print(f"call_timeouts: OK, {sum(counts.values()):g} untimed call(s), all within the baseline")
    return 0 if verdict.ok and not unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
