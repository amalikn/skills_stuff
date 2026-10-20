#!/usr/bin/env python3
"""Find timed subprocess calls whose command starts children of its own (ssh, a shell), which the timeout leaves running, as a shrink-only
ratchet. Read-only unless --write-baseline. Stdlib only.

Why (references/errors-and-timeouts.md, Learned 2026-10-20): `subprocess.run(timeout=)` kills only the process it started. `ssh` to a host
reached through a ProxyCommand (`tsh proxy ssh`, a jump host) starts the proxy as its own child, and a shell starts the pipeline it runs; both
outlive the kill. In one project, Teleport proxies to an unreachable box were still running ten minutes after the 90 s timeout, and the host's
load rose. The fix is a runner that starts the child in its own session and ends the whole process group on timeout.

Counted, through `ast`: subprocess.run/call/check_call/check_output with `timeout=` whose command is a list or tuple starting with one of
SPAWNERS, a call to a function named like one (`tsh(...)`, `ssh_argv(...)`), or `shell=True`. A call passing `**kwargs` is trusted.

Usage:
    group_timeouts.py --project-root . [--roots src,scripts] [--baseline scripts/group-timeout-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more such calls than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import call_timeouts
import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Commands that start children of their own: ssh and its relatives start a ProxyCommand; a shell starts what it runs.
SPAWNERS = {"ssh", "tsh", "scp", "sftp", "rsync", "autossh", "sh", "bash", "zsh", "dash"}
#: The run family: these wait for the child and kill only it on timeout.
RUN_FAMILY = {"subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output"}


def _command_name(node: ast.AST) -> str:
    """The program a call's first argument starts, as far as the source shows it.

    Args:
        node: the call's first positional argument.

    Returns:
        The program ("ssh"), the last part of a builder function's name ("tsh" for teleport.tsh(...)), or "".
    """
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return Path(first.value).name
        return ""
    if isinstance(node, ast.Call):
        return call_timeouts._dotted(node.func).split(".")[-1]
    return ""


def group_unsafe_calls(text: str, grammar: tuple[int, int] | None = None) -> list[tuple[int, str]]:
    """Timed run-family calls whose command starts children the timeout would leave running.

    Args:
        text: the Python source.
        grammar: (major, minor) to parse with the target project's grammar; None for this interpreter's.

    Returns:
        (line, "subprocess.run(ssh ...)") per call.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it).
    """
    out: list[tuple[int, str]] = []
    for node in ast.walk(pyparse.parse(text, grammar)):
        if not isinstance(node, ast.Call):
            continue
        name = call_timeouts._dotted(node.func)
        if ".".join(name.split(".")[-2:]) not in RUN_FAMILY:
            continue
        keywords = {k.arg for k in node.keywords}
        if "timeout" not in keywords or None in keywords:
            continue
        shell = any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords)
        program = _command_name(node.args[0]) if node.args else ""
        spawns = shell or program in SPAWNERS or any(program.endswith(f"_{s}") or program.startswith(f"{s}_") for s in SPAWNERS)
        if spawns:
            out.append((node.lineno, f"{name}({'shell=True' if shell else program} ...)"))
    return out


def measure(root: Path, roots: list[str], grammar: tuple[int, int] | None = None) -> tuple[dict[str, float], dict[str, list], list[str]]:
    """Group-unsafe calls per file.

    Args:
        root: the project root.
        roots: folders to scan.
        grammar: the Python grammar to parse with.

    Returns:
        ({path: count} for files with any, {path: [(line, text)]}, ["path: error"] for files that do not parse).
    """
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    unparsed: list[str] = []
    for folder in roots:
        for path in sorted((root / folder).rglob("*.py")):
            if {".venv", "venv", "node_modules", "__pycache__"} & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                found = group_unsafe_calls(path.read_text(encoding="utf-8", errors="replace"), grammar)
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
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [group_timeouts] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [group_timeouts] baseline, else scripts/group-timeout-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every such call")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--python", help="parse at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"group_timeouts: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "group_timeouts")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"group_timeouts: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    base_path = root / (args.baseline or code_map.section(cmap, "group_timeouts").get("baseline", "scripts/group-timeout-baseline.json"))
    counts, detail, unparsed = measure(root, roots, code_map.grammar(args.python, cmap))
    for line in unparsed:
        print(f"FAIL unparsed: {line} (not checked; check --python matches the project)")
    if args.list:
        for rel, calls in detail.items():
            for line, text in calls:
                print(f"{rel}:{line}: {text} kills only its child on timeout; end the process group")
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"group_timeouts: baseline written, {sum(counts.values()):g} call(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "group timeouts", base_path):
        print(line)
    if verdict.ok:
        print(f"group_timeouts: OK, {sum(counts.values()):g} call(s), all within the baseline")
    return 0 if verdict.ok and not unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
