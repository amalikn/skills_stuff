#!/usr/bin/env python3
"""Hold modules and functions to a size limit in any language, as a shrink-only ratchet. Read-only unless --write-baseline. Stdlib only.

Why (unified-network-controller code architecture design, rule R34, 2026-10-10): "a module stays under 400 lines and a function under 60; a larger
one at adoption is recorded with its size and may only shrink". Small units are cheaper to read, test and replace; the limit is a prompt to split
along a real seam, not an aesthetic.

How functions are found, per language (LANGS): Python exactly, through `ast`; shell by `name() {` or `function name` and brace depth; C-family
languages (JavaScript, TypeScript, Go, Rust, Java, C, C#, Kotlin, Swift, PHP) by a function header pattern and brace depth, ignoring braces in
strings and comments. The brace scan is a heuristic: it is right for code a formatter has laid out, and says so in its output.

Two thresholds per unit: past `warn_*` the unit is reported as a warning (plan the split along a seam the next time it is touched); past the hard
limit it fails unless the baseline records it. Defaults (DEFAULT_LIMITS, LANG_LIMITS): modules warn 300 / fail 400, functions warn 40 / fail 60;
shell scripts warn 100 / fail 200, functions 30 / 40. A project overrides any of them per language or suffix with --limits FILE (JSON
{"go": {"module": 600}, "sh": {...}}), which is how a language override is kept without editing this script.

Usage:
    code_size.py --project-root . [--roots src,scripts] [--baseline scripts/code-size-baseline.json]
    code_size.py --project-root . --write-baseline      # adopt: record today's oversized units
    code_size.py --project-root . --list                # every oversized unit, baseline or not
Exit: 0 when nothing is over its allowance and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Language by file suffix.
LANGS = {".py": "python", ".sh": "shell", ".bash": "shell", ".js": "c-family", ".mjs": "c-family", ".ts": "c-family", ".tsx": "c-family",
         ".jsx": "c-family", ".go": "c-family", ".rs": "c-family", ".java": "c-family", ".c": "c-family", ".h": "c-family", ".cs": "c-family",
         ".kt": "c-family", ".swift": "c-family", ".php": "c-family"}
#: Lines at which a unit must be split (fails the check unless baselined) and at which the split should be planned (a warning, never a failure).
DEFAULT_LIMITS = {"module": 400, "function": 60, "warn_module": 300, "warn_function": 40}
#: Built-in language defaults over DEFAULT_LIMITS. Shell: past about 100 lines a script belongs in a structured language (Google Shell Style
#: Guide; UNVERIFIED until the pack's sources record it), so the warning is 100 and the hard limit 200.
LANG_LIMITS = {"shell": {"module": 200, "function": 40, "warn_module": 100, "warn_function": 30}}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "vendor", "dist", "build", ".mypy_cache", ".ruff_cache"}
SHELL_FN = re.compile(r"^\s*(?:function\s+([A-Za-z_][\w-]*)\s*(?:\(\))?|([A-Za-z_][\w-]*)\s*\(\))\s*\{?\s*$")
C_FN = re.compile(r"^\s*(?:export\s+|pub(?:\([^)]*\))?\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|override\s+|fun\s+|func\s+|fn\s+|"
                  r"function\s+)*(?:func\s*(?:\([^)]*\)\s*)?|fn\s+|function\s*\*?\s*|fun\s+)?([A-Za-z_$][\w$]*)\s*(?:<[^>]*>)?\s*\([^;]*$")
C_KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "else", "do", "try", "match", "loop", "select", "with"}


def python_functions(text: str, grammar: tuple[int, int] | None = None) -> list[tuple[str, int]]:
    """Every function and method in Python source, with its length in lines (decorators excluded).

    Args:
        text: the source.
        grammar: (major, minor) to parse with the target project's grammar (ast feature_version); None for this interpreter's.

    Returns:
        (qualified name, lines) per function.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it; a file is never skipped silently).
    """
    tree = pyparse.parse(text, grammar)
    out: list[tuple[str, int]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        """Collect functions under one node.

        Args:
            node: an AST node.
            prefix: the qualified name of the enclosing class or function.
        """
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                out.append((name, child.end_lineno - child.lineno + 1))
                walk(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")

    walk(tree, "")
    return out


def _strip_line(line: str, state: dict) -> str:
    """A C-family or shell line with string, character and comment contents removed, so only code braces remain.

    Shell has no `//` or `/* */` comments (`dir/*` is a glob), and `#` starts a comment only at the start of a word (`${#arr[@]}` is code).

    Args:
        line: one source line.
        state: {"block": bool, "shell": bool}; "block" carries an open /* comment */ across lines.

    Returns:
        The line's code characters.
    """
    out, i, quote = [], 0, ""
    while i < len(line):
        two = line[i:i + 2]
        if state["block"]:
            if two == "*/":
                state["block"], i = False, i + 2
                continue
            i += 1
            continue
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        shell = state.get("shell")
        if two == "/*" and not shell:
            state["block"], i = True, i + 2
            continue
        if (two == "//" and not shell) or (shell and ch == "#" and (i == 0 or line[i - 1] in " \t;|&(")):
            break
        if ch in "\"'`":
            quote = ch
        else:
            out.append(ch)
        i += 1
    return "".join(out)


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w]*)\1")


def _blank_heredocs(lines: list[str]) -> list[str]:
    """Shell lines with every here-document body blanked, so braces in embedded JSON, Terraform or templates are not counted as code.

    Args:
        lines: the script's lines.

    Returns:
        The same number of lines; a body line becomes "" and the line opening the here-document keeps only its text before `<<`.
    """
    out, end = [], None
    for line in lines:
        if end is not None:
            out.append("")
            if line.strip() == end:
                end = None
            continue
        m = HEREDOC.search(line)
        if m and "<<<" not in line:
            end = m.group(2)
            out.append(line[:m.start()])
        else:
            out.append(line)
    return out


def brace_functions(text: str, lang: str) -> list[tuple[str, int]]:
    """Functions in a brace language or shell, found by header pattern and brace depth (a heuristic for formatted code).

    Args:
        text: the source.
        lang: "c-family" or "shell".

    Returns:
        (name, lines) per function whose body closes; nested functions are counted on their own and inside their parent.
    """
    lines = text.splitlines()
    header = SHELL_FN if lang == "shell" else C_FN
    state = {"block": False, "shell": lang == "shell"}
    code = [_strip_line(line, state) for line in (_blank_heredocs(lines) if lang == "shell" else lines)]
    out: list[tuple[str, int]] = []
    for start, line in enumerate(lines):
        m = header.match(line)
        if not m:
            continue
        name = next(g for g in m.groups() if g)
        if name in C_KEYWORDS:
            continue
        depth, opened = 0, False
        for end in range(start, min(len(lines), start + 5000)):
            depth += code[end].count("{") - code[end].count("}")
            opened = opened or "{" in code[end]
            if opened and depth <= 0:
                out.append((name, end - start + 1))
                break
            if not opened and end - start > 3:   # a declaration with no body (prototype, interface method)
                break
    return out


@dataclass
class Measurement:
    """What measure() found.

    Args:
        modules: {path: lines} for modules over their hard limit.
        functions: {"path::name": lines} for functions over their hard limit.
        warnings: "path: N lines (plan the split at W, must split at H)" per unit past its warning but within its hard limit.
        unparsed: "path: line L: error" per file that did not parse (reported, never skipped silently).
    """

    modules: dict[str, float] = field(default_factory=dict)
    functions: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)


def limits_for(path: Path, lang: str, overrides: dict[str, dict], base: dict | None = None) -> dict[str, int]:
    """The four limits for one file: the base, then the language's built-in default, then the project's language and suffix overrides.

    Args:
        path: the file.
        lang: its language from LANGS.
        overrides: the project's {language or suffix: {key: n}} (keys as DEFAULT_LIMITS).
        base: limits for every language; default DEFAULT_LIMITS.

    Returns:
        {"module", "function", "warn_module", "warn_function"}.
    """
    return {**(base or DEFAULT_LIMITS), **LANG_LIMITS.get(lang, {}), **overrides.get(lang, {}), **overrides.get(path.suffix.lstrip("."), {})}


def _check_unit(out: Measurement, key: str, size: int, hard: int, warn: int, bucket: dict) -> None:
    """File one unit as over its hard limit, past its warning, or fine.

    Args:
        out: the measurement being filled.
        key: the unit's key (path, or path::name).
        size: its length in lines.
        hard: the limit that fails.
        warn: the limit that warns.
        bucket: out.modules or out.functions.
    """
    if size > hard:
        bucket[key] = max(size, bucket.get(key, 0))
    elif size > warn:
        out.warnings.append(f"{key}: {size} lines (plan the split at {warn}, must split at {hard})")


def measure(root: Path, roots: list[str], overrides: dict[str, dict], base: dict | None = None,
            grammar: tuple[int, int] | None = None, exclude: frozenset = frozenset()) -> Measurement:
    """Every module and function past its language's warning or hard limit.

    Args:
        root: the project root.
        roots: folders to scan, relative to the root.
        overrides: the project's {language or suffix: {key: n}}.
        base: limits for every language; default DEFAULT_LIMITS.
        grammar: the Python grammar to parse with (see python_functions).
        exclude: repo-relative files not measured (the code map's [scan.exclude]).

    Returns:
        The measurement.
    """
    out = Measurement()
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            lang = LANGS.get(path.suffix)
            if not lang or not path.is_file() or SKIP_PARTS & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            if rel in exclude:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lim = limits_for(path, lang, overrides, base)
            _check_unit(out, rel, len(text.splitlines()), lim["module"], lim["warn_module"], out.modules)
            try:
                found = python_functions(text, grammar) if lang == "python" else brace_functions(text, lang)
            except SyntaxError as exc:
                out.unparsed.append(f"{rel}: line {exc.lineno}: {exc.msg}")
                continue
            for name, size in found:
                _check_unit(out, f"{rel}::{name}", size, lim["function"], lim["warn_function"], out.functions)
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line: measure, compare with the baseline, or write it.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within allowance and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders to scan (default: the code map's, else src,scripts; missing ones are skipped)")
    ap.add_argument("--baseline", default="scripts/code-size-baseline.json")
    ap.add_argument("--limits", type=Path, help='JSON {"<language or suffix>": {"module": n, "function": m, "warn_module": w, "warn_function": v}}')
    ap.add_argument("--write-baseline", action="store_true", help="record today's oversized units (adoption or after an improvement)")
    ap.add_argument("--list", action="store_true", help="print every oversized unit and every warning")
    ap.add_argument("--python", help="parse Python at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"code_size: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap)
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"code_size: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    overrides = {**code_map.section(cmap, "limits"), **(json.loads(args.limits.read_text(encoding="utf-8")) if args.limits else {})}
    grammar = code_map.grammar(args.python, cmap)
    try:
        exclude = frozenset(code_map.excluded(cmap))
    except ValueError as exc:
        print(f"code_size: {exc}", file=sys.stderr)
        return 2
    got = measure(root, roots, overrides, grammar=grammar, exclude=exclude)
    for line in got.unparsed:
        print(f"FAIL unparsed: {line} (not measured; check --python matches the project)")
    found = {**{f"module {k}": v for k, v in got.modules.items()}, **{f"function {k}": v for k, v in got.functions.items()}}
    base_path = root / args.baseline
    if args.list:
        print("\n".join([f"{key}: {size:g} lines" for key, size in sorted(found.items())] + [f"WARN {w}" for w in got.warnings]))
    if args.write_baseline:
        ratchet.save(base_path, found)
        print(f"code_size: baseline written, {len(got.modules)} module(s) and {len(got.functions)} function(s) over ({base_path})")
        return 0
    verdict = ratchet.compare(found, ratchet.load(base_path))
    print("\n".join(ratchet.report(verdict, "size", base_path)) or
          f"code_size: OK, {len(found)} oversized unit(s) within the baseline, {len(got.warnings)} warning(s) (--list shows them)")
    return 0 if verdict.ok and not got.unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
