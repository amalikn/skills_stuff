#!/usr/bin/env python3
"""Python import structure: layer violations against a rules file, import cycles, and a package-level import graph. Read-only. Stdlib only.

Promoted from unified-network-controller `scripts/checks/import_graph.py` (2026-10-19). Why (its code architecture design, principles 2 and rules
R2-R3): dependencies point inwards and there are no import cycles, so a lower layer can be tested and replaced without the code above it. The
rule is data: a TOML file with one table per top-level package of the checked package, its layer name and the packages it may import:

    [core]
    layer = "L0"
    may_import = []
    [services]
    layer = "L5"
    may_import = ["core", "backends.skills"]   # a dotted entry allows that subpackage only

A package the file does not list is not checked yet, so a code base adopts layers one package at a time. Accepted violations (code moved in
unchanged) go in a baseline file, one line each; any other violation fails.

Usage:
    import_layers.py --project-root . --src src --package app --layers src/app/layers.toml [--baseline scripts/import-layers-baseline.json]
    import_layers.py --project-root . --graph --roots src,scripts                    # modules, edges, fan-in, cycles (report only)
Exit: 0 when no new violation (and no cycle with --fail-on-cycles), 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import collections
import json
import sys
import tomllib
from pathlib import Path

import code_map
import pyparse

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


def _imported_names(tree: ast.AST) -> list[str]:
    """Absolute dotted names a module imports (relative imports are inside its own package and never cross a layer).

    Args:
        tree: the parsed module.

    Returns:
        Names in source order.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.append(node.module)
    return out


def _graph_names(module: str, path: Path, tree: ast.AST) -> list[str]:
    """The dotted names a module imports for the graph: relative imports made absolute, and `from pkg import name` as `pkg.name` (name may be
    a submodule; resolution falls back to `pkg` when it is not).

    Args:
        module: the importing module's dotted name.
        path: its file (an `__init__.py` resolves relative imports from itself).
        tree: its parsed AST.

    Returns:
        Imported dotted names in source order.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                base = node.module or ""
            else:
                parts = module.split(".")
                keep = len(parts) - node.level + (1 if path.name == "__init__.py" else 0)
                base = ".".join(parts[:max(keep, 0)] + ([node.module] if node.module else []))
            out += [f"{base}.{a.name}" if base else a.name for a in node.names]
    return out


def layer_violations(src: Path, package: str, rules: dict) -> list[str]:
    """Imports inside `src/<package>` that break the layer rules.

    A module in subpackage P may import `<package>` itself, P, and what P's `may_import` lists.

    Args:
        src: the folder holding the package.
        package: the top-level package name.
        rules: the parsed TOML {subpackage: {"layer": str, "may_import": [str]}}.

    Returns:
        Sorted lines `<module> -> <imported module> (<layer> <P> may not import <Q>)`.
    """
    found: set[str] = set()
    for path in sorted((src / package).rglob("*.py")):
        parts = path.relative_to(src).with_suffix("").parts
        module = ".".join(p for p in parts if p != "__init__")
        sub = parts[1] if len(parts) > 2 else None
        if sub not in rules:
            continue
        allowed = rules[sub].get("may_import", [])
        for name in _imported_names(pyparse.parse(path.read_text(encoding="utf-8"))):
            if not name.startswith(package + "."):
                continue
            target = name.split(".")[1:]
            if target[0] == sub or any(".".join(target[: len(a.split("."))]) == a for a in allowed):
                continue
            found.add(f"{module} -> {name} ({rules[sub]['layer']} {sub} may not import {target[0]})")
    return sorted(found)


def module_map(root: Path, roots: list[str]) -> dict[str, Path]:
    """Every Python module under the roots, by dotted name relative to its root.

    Args:
        root: the project root.
        roots: folders relative to the root.

    Returns:
        {dotted name: path}; a package's `__init__` is named as the package.
    """
    mods: dict[str, Path] = {}
    for folder in roots:
        base = root / folder
        for path in sorted(base.rglob("*.py")) if base.is_dir() else []:
            if "__pycache__" not in path.parts:
                mods[".".join(path.relative_to(base).with_suffix("").parts).removesuffix(".__init__")] = path
    return mods


def graph(mods: dict[str, Path]) -> dict[str, set[str]]:
    """Which known module imports which.

    Args:
        mods: module_map()'s result.

    Returns:
        {module: modules it imports}; stdlib and third-party imports are left out.
    """
    out: dict[str, set[str]] = collections.defaultdict(set)
    for name, path in mods.items():
        try:
            tree = pyparse.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for imported in _graph_names(name, path, tree):
            parts = imported.split(".")
            hit = next((".".join(parts[:i]) for i in range(len(parts), 0, -1) if ".".join(parts[:i]) in mods), None)
            if hit and hit != name:
                out[name].add(hit)
    return out


def cycles(edges: dict[str, set[str]], nodes: list[str]) -> list[list[str]]:
    """Import cycles: strongly connected components of more than one module (Tarjan, iterative, so deep graphs do not hit the recursion limit).

    Args:
        edges: module -> modules it imports.
        nodes: every module.

    Returns:
        Each cycle as a sorted list of names.
    """
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    found: list[list[str]] = []
    for start in nodes:
        if start in index:
            continue
        work = [(start, iter(sorted(edges.get(start, ()))))]
        index[start] = low[start] = len(index)
        stack.append(start)
        on_stack.add(start)
        while work:
            node, children = work[-1]
            child = next((c for c in children if c not in index or c in on_stack), None)
            if child is not None and child not in index:
                index[child] = low[child] = len(index)
                stack.append(child)
                on_stack.add(child)
                work.append((child, iter(sorted(edges.get(child, ())))))
                continue
            if child is not None:
                low[node] = min(low[node], index[child])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                comp = []
                while (member := stack.pop()) != node:
                    on_stack.discard(member)
                    comp.append(member)
                on_stack.discard(node)
                comp.append(node)
                if len(comp) > 1:
                    found.append(sorted(comp))
    return found


def _top(module: str) -> str:
    """A module's top-level package.

    Args:
        module: a dotted name.

    Returns:
        Its first part.
    """
    return module.split(".")[0]


def summary(mods: dict[str, Path], edges: dict[str, set[str]]) -> list[str]:
    """A plain-text report: modules per top-level package, cross-package edges, top fan-in and cycles.

    Args:
        mods: module_map()'s result.
        edges: graph()'s result.

    Returns:
        Report lines.
    """
    cross = collections.Counter((_top(a), _top(b)) for a, bs in edges.items() for b in bs if _top(a) != _top(b))
    fan_in = collections.Counter(b for bs in edges.values() for b in bs)
    lines = ["modules per package: " + ", ".join(f"{k} {v}" for k, v in sorted(collections.Counter(map(_top, mods)).items()))]
    lines += [f"  {a} -> {b}: {n}" for (a, b), n in sorted(cross.items())]
    lines.append("top fan-in: " + ", ".join(f"{m} {n}" for m, n in fan_in.most_common(15)))
    lines.append("cycles: " + ("; ".join(" <-> ".join(c) for c in cycles(edges, list(mods))) or "none"))
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command line: check layers against the baseline, or print the graph report.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when clean, 1 on a new violation (or a cycle with --fail-on-cycles), 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--src", default="src", help="folder holding the checked package")
    ap.add_argument("--package", help="top-level package to check against --layers")
    ap.add_argument("--layers", help="TOML rules file, relative to the root")
    ap.add_argument("--baseline", help="JSON list of accepted violation lines")
    ap.add_argument("--graph", action="store_true", help="print the import graph report for --roots")
    ap.add_argument("--roots", help="comma-separated folders for --graph and cycle checks (default: the code map's [scan] roots, else src)")
    ap.add_argument("--fail-on-cycles", action="store_true")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"import_layers: {exc}", file=sys.stderr)
        return 2
    layers = code_map.section(cmap, "layers")
    rc = 0
    mods = module_map(root, (args.roots or code_map.scan_roots(cmap, default="src")).split(","))
    edges = graph(mods)
    if args.graph:
        print("\n".join(summary(mods, edges)))
    if args.fail_on_cycles and (found := cycles(edges, list(mods))):
        print("\n".join("cycle: " + " <-> ".join(c) for c in found))
        rc = 1
    if args.layers or layers.get("rules"):
        package = args.package or layers.get("package")
        if not package:
            print("layer rules need --package (or [layers] package in the code map)", file=sys.stderr)
            return 2
        rules = tomllib.loads((root / args.layers).read_text(encoding="utf-8")) if args.layers else layers["rules"]
        baseline = args.baseline or layers.get("baseline")
        accepted = set(json.loads((root / baseline).read_text(encoding="utf-8"))) if baseline and (root / baseline).is_file() else set()
        src = args.src if args.src != "src" else layers.get("src", "src")
        new = [v for v in layer_violations(root / src, package, rules) if v not in accepted]
        print("\n".join(f"layer: {v}" for v in new) if new else f"layers: no new violation ({args.layers or 'code map'})")
        rc = rc or (1 if new else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
