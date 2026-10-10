"""Split a project's single-file `scripts/check_governance.py` into the govcheck package (patterns/governance-checks.md, "Structure and growth").

Why (operator, 2026-10-10: the checker must not "go crazy indefinitely"; split with "good coding logics" so the parts stay coherent): one file
grows without limit and costs an agent the whole file to change one check. Code moves verbatim into `govcheck/config.py` (constants),
`helpers.py` (shared functions), `checks/<family>.py` (one module per family) and the shared `core.py`; the entry point keeps its path and
output. First used on unified-network-controller (1,820 lines; output identical before and after on a clean and a failing tree).

Usage:
    python scripts/split_checker.py --project-root P --families families.json [--docs docs.json] [--apply]
families.json: {"family": {"doc": "one line", "checks": ["check_a", ...]}, ...}; every `check_*` function must be assigned.
docs.json (optional): {"function": ["summary or null", ["arg: text", ...], "returns text"]} appended to or written as docstrings.
Without --apply it writes the package to a temporary copy, runs both checkers there and reports whether the output is identical.
Exit: 0 identical (or applied), 1 when the outputs differ or a check is unassigned, 2 on bad arguments.
"""
import ast
import pathlib
import re
import sys

import argparse
import json
import shutil
import subprocess
import tempfile

ap = argparse.ArgumentParser(description="split check_governance.py into the govcheck package")
ap.add_argument("--project-root", required=True)
ap.add_argument("--families", required=True)
ap.add_argument("--docs", default="")
ap.add_argument("--python", default=sys.executable, help="interpreter to run the project's checker with")
ap.add_argument("--apply", action="store_true")
args = ap.parse_args()
real_root = pathlib.Path(args.project_root).resolve()
core_template = (pathlib.Path(__file__).resolve().parent.parent / "templates/govcheck/core.py").read_text()
spec = json.loads(pathlib.Path(args.families).read_text())
FAMILIES = {f: v["checks"] for f, v in spec.items()}
FAMILY_DOC = {f: v.get("doc", f"The {f} checks.") for f, v in spec.items()}
DOCS = {k: tuple(v) for k, v in json.loads(pathlib.Path(args.docs).read_text()).items()} if args.docs else {}
work = pathlib.Path(tempfile.mkdtemp()) / real_root.name
shutil.copytree(real_root, work, ignore=shutil.ignore_patterns(".git", ".venv", "node_modules"), symlinks=True)
root = work if not args.apply else real_root
before = subprocess.run([args.python, "scripts/check_governance.py"], cwd=root, capture_output=True, text=True)
src_path = root / "scripts/check_governance.py"
src = src_path.read_text()
lines = src.split("\n")
tree = ast.parse(src)

CORE_NAMES = {"failures", "checks_run", "fail", "counted"}
STDLIB = ["csv", "functools", "importlib", "ast", "json", "re", "subprocess", "sys"]

DOCS = {  # name -> (Args lines, Returns line) appended to the existing docstring, or a whole docstring when none exists
    "_live_surfaces": ("The governance surfaces this project keeps current: root markdown, docs function folders, archcore, script and lab readmes.",
                       [], "Repo-relative paths, sorted, without the sibling surfaces this project only reads."),
    "read": ("The text of a repo file.", ["rel: repo-relative path."], "Its text, or None when the file does not exist."),
    "without_code": (None, ["text: markdown."], "The text without its fenced code blocks."),
    "table_rows": (None, ["rel: repo-relative CSV path."], "One dict per row, keyed by the header; empty when the file does not exist."),
    "members": ("Files directly matching a glob under a folder, hidden files excluded.", ["folder: repo-relative folder.", "glob: pattern inside it."],
                "Sorted paths; empty when the folder does not exist."),
    "_sibling_roots": (None, [], "The roots references are resolved against: this repo's ancestors and the declared siblings present here."),
    "_resolves": (None, ["tok: the path as written.", "surface: the repo-relative file that names it.", "siblings: roots from _sibling_roots()."],
                  "True when the path resolves in any of those places."),
    "_pinned_files": (None, ["name: a sibling named in SIBLING_BRANCHES."], "The file paths on its pinned ref; empty when the ref cannot be read."),
    "_moved_paths": ("Old path to new path for files moved in this project.", [], "The `moves` map of MOVED_PATHS_FILE; empty when the file is absent."),
    "_catalog_lines": (None, ["text: the rendered catalog.", "key: a top-level section name."], "(indent, text) per content line of that section."),
    "_flow_list": (None, ["value: a YAML flow list as written."], "Its items as strings."),
    "_flow_map": (None, ["value: a YAML flow map as written."], "Its keys and values as strings."),
    "_device_type_answers": (None, ["section: catalog section, e.g. `gps`.", "key: the answer field.", "values: the answers allowed.",
                                    "question: how the question reads in a failure."], "Each device type's answer fields, for the caller's own rules."),
    "plan_shaped": ("Whether a markdown file is a plan or plan supplement by its metadata or name.",
                    ["path: the file.", "text: its content."], "True for an architecture plan, a file naming a plan as Parent, or an addendum."),
}


def with_docstring(fn_lines: list[str], node: ast.FunctionDef, indent: str) -> list[str]:
    """Return the function's lines with Args/Returns added (or a docstring written) per DOCS."""
    summary, args, ret = DOCS[node.name]
    block = []
    if args:
        block += ["", f"{indent}Args:"] + [f"{indent}    {a}" for a in args]
    if ret:
        block += ["", f"{indent}Returns:", f"{indent}    {ret}"]
    base = node.lineno
    first = node.body[0]
    has_doc = isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) and isinstance(first.value.value, str)
    if has_doc:
        s, e = first.lineno - base, first.end_lineno - base
        doc = "\n".join(fn_lines[s:e + 1])
        body = doc.strip()[3:-3].rstrip()
        text = body.strip()
        new = [f'{indent}"""{line}' if i == 0 else line for i, line in enumerate(text.split("\n"))]
        new = [f'{indent}"""' + text.split("\n")[0]] + text.split("\n")[1:] + block + [f'{indent}"""']
        return fn_lines[:s] + new + fn_lines[e + 1:]
    s = first.lineno - base
    new = [f'{indent}"""{summary}'] + block + [f'{indent}"""']
    return fn_lines[:s] + new + fn_lines[s:]


def segment(node) -> list[str]:
    """The node's lines with decorators and the comment lines directly above it."""
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])]) - 1
    while start > 0 and lines[start - 1].startswith("#") and not lines[start - 1].startswith("# ---"):
        start -= 1
    seg = lines[start:node.end_lineno]
    if isinstance(node, ast.FunctionDef):
        if node.name in DOCS:
            offset = node.lineno - 1 - start
            seg = seg[:offset] + with_docstring(seg[offset:], node, "    ") + []
        for inner in ast.walk(node):
            if isinstance(inner, ast.FunctionDef) and inner is not node and inner.name in DOCS:
                text = "\n".join(seg)
                old = "\n".join(lines[inner.lineno - 1:inner.end_lineno])
                ind = " " * (inner.col_offset + 4)
                new = "\n".join(with_docstring(lines[inner.lineno - 1:inner.end_lineno], inner, ind))
                seg = text.replace(old, new).split("\n")
    return seg


nodes = {}
config_parts, order = [], []
for n in tree.body:
    if isinstance(n, (ast.Import, ast.ImportFrom)) or (isinstance(n, ast.Expr) and n is tree.body[0]) or isinstance(n, ast.If):
        continue
    if isinstance(n, (ast.Assign, ast.AnnAssign)):
        name = (n.targets[0] if isinstance(n, ast.Assign) else n.target).id
        if name in CORE_NAMES or name == "CHECKS":
            continue
        config_parts.append((name, segment(n)))
        continue
    if isinstance(n, ast.FunctionDef):
        if n.name in CORE_NAMES or n.name == "main":
            continue
        nodes[n.name] = (n, segment(n))

config_names = [c for c, _ in config_parts if c != "SELF"] + ["SELF_FILES"]
assigned = {c for fam in FAMILIES.values() for c in fam}
unassigned = sorted(n for n in nodes if n.startswith("check_") and n not in assigned)
if unassigned:
    sys.exit(f"unassigned checks: {unassigned}")
helper_names = [n for n in nodes if n not in assigned]


def used_names(seg: list[str]) -> set[str]:
    """Names a code segment references."""
    t = ast.parse("\n".join(seg))
    return {x.id for x in ast.walk(t) if isinstance(x, ast.Name)} | {x.value.id for x in ast.walk(t) if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name)}


def header(doc: str, segs: list[list[str]], local: set[str], tier: str) -> str:
    """Module docstring plus the imports its code needs."""
    names = set().union(*(used_names(s) for s in segs)) - local
    out = [f'"""{doc}"""', "", "from __future__ import annotations", ""]
    std = [m for m in STDLIB if m in names]
    out += [f"import {m}" for m in std]
    if "Path" in names:
        out.append("from pathlib import Path")
    out.append("")
    if tier != "config":
        core = sorted(names & {"fail", "counted"})
        if core:
            out.append(f"from {'..' if tier == 'family' else '.'}core import {', '.join(core)}")
        cfg = sorted(names & set(config_names))
        if cfg:
            out.append(f"from {'..' if tier == 'family' else '.'}config import (\n    " + ",\n    ".join(cfg) + ",\n)")
        if tier == "family":
            hp = sorted(names & set(helper_names))
            if hp:
                out.append("from ..helpers import (\n    " + ",\n    ".join(hp) + ",\n)")
    return "\n".join(out) + "\n\n"


def fix_self(text: str) -> str:
    """SELF (one file) becomes SELF_FILES (the checker's files), so scans keep excluding the checker."""
    text = text.replace("!= SELF ", "not in SELF_FILES ").replace("!= SELF\n", "not in SELF_FILES\n")
    return re.sub(r"== SELF\b", "in SELF_FILES", text)


pkg = root / "scripts/govcheck"
(pkg / "checks").mkdir(parents=True, exist_ok=True)
(pkg / "core.py").write_text(core_template)
(pkg / "__init__.py").write_text('"""The governance checker of this project, split by family (skill-ai-it standard, patterns/governance-checks.md). Entry: scripts/check_governance.py."""\n')

# config.py: data, plus _live_surfaces which a constant is computed from
cfg_segs = []
for name, seg in config_parts:
    text = "\n".join(seg)
    if name == "ROOT":
        text = text.replace("Path(__file__).resolve().parent.parent", "Path(__file__).resolve().parents[2]")
    if name == "SELF":
        text = ('#: The checker\'s own files, excluded from the scans that would otherwise report its own pattern definitions (the split of\n'
                '#: 2026-10-10 turned one file into a package).\n'
                'SELF_FILES = frozenset({"scripts/check_governance.py", *(p.relative_to(ROOT).as_posix() for p in (ROOT / "scripts/govcheck").rglob("*.py"))})')
    cfg_segs.append(text.split("\n"))
cfg_text = "\n\n".join("\n".join(s) for s in cfg_segs)
cfg_doc = ("This project's governance data: roots, registries, path policy and exemptions with their reasons. No checks here; checks read it.")
(pkg / "config.py").write_text(header(cfg_doc, [s for s in cfg_segs], set(config_names), "config") + fix_self(cfg_text) + "\n")

help_segs = [fix_self("\n".join(nodes[h][1])).split("\n") for h in helper_names]
help_doc = "Shared readers for this project's checks: file and table reads, path resolution, catalog parsing, docstring counting."
(pkg / "helpers.py").write_text(header(help_doc, help_segs, set(helper_names), "helpers") + fix_self("\n\n\n".join("\n".join(s) for s in help_segs)) + "\n")

for fam, names in FAMILIES.items():
    segs = [fix_self("\n".join(nodes[c][1])).split("\n") for c in names]
    body = fix_self("\n\n\n".join("\n".join(s) for s in segs))
    (pkg / "checks" / f"{fam}.py").write_text(header(FAMILY_DOC[fam], segs, set(names), "family") + body + "\n")

checks_order = [ast.unparse(e) for e in next(n for n in tree.body if isinstance(n, ast.Assign) and n.targets[0].id == "CHECKS").value.elts]
fam_of = {c: f for f, cs in FAMILIES.items() for c in cs}
init = ['"""The checks, by family, and the order they run in (unchanged from the single-file checker, so output is identical)."""', "",
        "from __future__ import annotations", ""]
init += [f"from . import {f}" for f in FAMILIES] + ["", "CHECKS = ("] + [f"    {fam_of[c]}.{c}," for c in checks_order] + [")", ""]
(pkg / "checks" / "__init__.py").write_text("\n".join(init))

doc = ast.get_docstring(tree)
entry = f'''#!/usr/bin/env python3
"""{doc}

Since 2026-10-10 the checks live in the `govcheck` package beside this file, one module per family (skill-ai-it
`patterns/governance-checks.md`, "Structure and growth"); this file is the entry point. Options: --select FAMILY,... --json --timings.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def main() -> int:
    """Run every check in order and report.

    Returns:
        0 when nothing failed, 1 otherwise.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    core = importlib.import_module("govcheck.core")
    checks = importlib.import_module("govcheck.checks")
    return core.run(checks.CHECKS)


if __name__ == "__main__":
    sys.exit(main())
'''
src_path.write_text(entry)
after = subprocess.run([args.python, "scripts/check_governance.py"], cwd=root, capture_output=True, text=True)
same = before.stdout == after.stdout and before.returncode == after.returncode
print(f"written to {'the project' if args.apply else 'a temporary copy'}: {len(list(pkg.rglob('*.py')))} files")
print(f"output {'identical' if same else 'DIFFERS'} (exit {before.returncode} -> {after.returncode})")
if not same:
    import difflib
    print("\n".join(list(difflib.unified_diff(before.stdout.splitlines(), after.stdout.splitlines(), lineterm=""))[:40]))
    print("note: new files can trip the project's own registries (promotion register, structure tracker); register them, then compare again")
sys.exit(0 if same else 1)
