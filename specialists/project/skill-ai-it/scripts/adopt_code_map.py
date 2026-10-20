#!/usr/bin/env python3
"""Create or extend a project's code map (`code-map.toml`, skill-coder's format) during bootstrap, refresh and govern. Stdlib only (tomllib).

Why (operator, 2026-10-20: "coder-map to be created.. it should be part of skill-ai-it bootstrap/refresh"): a project with code holds its code
decisions (scan roots, size limits, write gates, each module's promotion status) in one map that skill-coder's checkers read. This script makes
that map from skill-coder's template when a project has code and none, and adds a `[modules]` entry for every code file the map does not list
yet. It never changes an existing decision: entries it adds are marked unreviewed, and entries for files that are gone are only reported.

Run:
    adopt_code_map.py --project-root .            # plan: print what would be created or added (writes nothing)
    adopt_code_map.py --project-root . --apply    # write code-map.toml, then load it with skill-coder's reader
Exit: 0 nothing to do or written; 1 a problem (the map does not load, the template is missing); 2 bad arguments.
Runtime: under a second on a project with a few hundred files (one directory walk).
"""

from __future__ import annotations

import argparse
import datetime
import importlib
import re
import sys
import tomllib
from pathlib import Path

#: The oldest Python this script runs on (it runs with the target project's interpreter).
REQUIRES_PYTHON = (3, 11)
#: skill-coder, the owner of the code map's format, beside this skill under specialists/project/.
CODER = Path(__file__).resolve().parents[2] / "skill-coder"
TEMPLATE = CODER / "templates" / "code-map.toml"
MAP_NAME = "code-map.toml"
#: Folders that hold a project's code, checked in this order; only the ones that exist and hold code become scan roots.
CANDIDATE_ROOTS = ("src", "scripts", "adapters", "tools", "wc-local/scripts")
CODE_SUFFIXES = (".py", ".sh", ".bash")
#: What `[modules]` lists: Python scripts, not the application package (`src/`) and not shell, as the first adopter's promotion check does
#: (unified-network-controller scripts/govcheck/checks/scripts.py, check_promotion_register: *.py under its script folders).
MODULE_SUFFIXES = (".py",)
MODULE_EXCLUDED_ROOTS = ("src",)
SKIP_PARTS = {"__pycache__", ".venv", "node_modules", ".git"}


def code_files(root: Path, roots: list[str], suffixes: tuple = CODE_SUFFIXES) -> list[str]:
    """Every code file under the scan roots, as project-relative paths, sorted.

    Args:
        root: the project root.
        roots: scan roots, relative to the root.
        suffixes: the file suffixes that count as code.

    Returns:
        The paths; `__init__.py` files are left out (a package's status is its modules').
    """
    found = []
    for r in roots:
        for path in (root / r).rglob("*"):
            if path.is_file() and path.suffix in suffixes and path.name != "__init__.py" and not SKIP_PARTS & set(path.parts):
                found.append(path.relative_to(root).as_posix())
    return sorted(found)


def module_files(root: Path, roots: list[str]) -> list[str]:
    """The files `[modules]` must list: Python scripts under the scan roots, outside the application package.

    Args:
        root: the project root.
        roots: the scan roots.

    Returns:
        The paths, sorted.
    """
    return code_files(root, [r for r in roots if r not in MODULE_EXCLUDED_ROOTS], MODULE_SUFFIXES)


def scan_roots(root: Path) -> list[str]:
    """The candidate folders that exist and hold code.

    Args:
        root: the project root.

    Returns:
        The roots, in CANDIDATE_ROOTS order.
    """
    return [r for r in CANDIDATE_ROOTS if (root / r).is_dir() and code_files(root, [r])]


def pinned_python(root: Path) -> str:
    """The project's Python version from the nearest `.mise.toml` (the project's, then its parents'), else "3.11".

    Args:
        root: the project root.

    Returns:
        A "major.minor" string.
    """
    for folder in (root, *root.parents):
        pin = folder / ".mise.toml"
        if pin.is_file():
            version = str(tomllib.loads(pin.read_text()).get("tools", {}).get("python", ""))
            match = re.match(r"(\d+\.\d+)", version)
            if match:
                return match.group(1)
    return "3.11"


def module_block(rel: str, today: str) -> str:
    """One `[modules]` entry for a file nobody has reviewed yet.

    Args:
        rel: the file, relative to the project root.
        today: the date to record, YYYY-MM-DD.

    Returns:
        The TOML text, ending in a blank line.
    """
    return f'[modules."{rel}"]\nstatus = "project_only"\nreason = "unreviewed: added by skill-ai-it adopt_code_map {today}; set the real status"\n\n'


def new_map(root: Path, roots: list[str], files: list[str], today: str) -> str:
    """A new code map from skill-coder's template: the project's name, roots and Python, no example layers or modules.

    The template's `[layers]` example (package "app") is dropped: layers are a design decision made one package at a time, not a default.

    Args:
        root: the project root.
        roots: the scan roots.
        files: the code files to list under `[modules]`.
        today: the date to record.

    Returns:
        The file text.
    """
    text = TEMPLATE.read_text()
    text = text.replace("(copy to the project root as code-map.toml)", f"(created by skill-ai-it adopt_code_map {today})")
    text = text.replace("# Status: template\n", "")
    text = text.replace("<project>", root.name)
    roots_toml = "[" + ", ".join(f'"{r}"' for r in roots) + "]"
    text = re.sub(r'^roots = \["src", "scripts"\]   #', f"roots = {roots_toml}   #", text, count=1, flags=re.M)
    text = re.sub(r'^python = "3\.11"', f'python = "{pinned_python(root)}"', text, count=1, flags=re.M)
    text = re.sub(r"^# Import layers \(Python\).*?(?=^# Entry points that write)", "", text, count=1, flags=re.M | re.S)
    text = re.sub(r'^roots = \["scripts"\]$', f"roots = {roots_toml}", text, count=1, flags=re.M)
    text = re.sub(r'^\[timeouts\]\nroots = \["src", "scripts"\]', f"[timeouts]\nroots = {roots_toml}", text, count=1, flags=re.M)
    text = re.sub(r'^\[modules\."scripts/example\.py"\].*\Z', "", text, count=1, flags=re.M | re.S)
    return text + "".join(module_block(f, today) for f in files)


def plan(root: Path, today: str) -> tuple[str | None, list[str], list[str]]:
    """What adoption would do.

    Args:
        root: the project root.
        today: the date to record.

    Returns:
        (the new full text of code-map.toml or None when nothing changes, files added to [modules], listed files that are gone).
    """
    target = root / MAP_NAME
    if not target.is_file():
        roots = scan_roots(root)
        if not roots:
            return None, [], []
        files = module_files(root, roots)
        return new_map(root, roots, files, today), files, []
    current = target.read_text()
    data = tomllib.loads(current)
    roots = data.get("scan", {}).get("roots") or scan_roots(root)
    listed = set(data.get("modules", {}))
    files = module_files(root, roots)
    added = [f for f in files if f not in listed]
    gone = sorted(f for f in listed if not (root / f).exists() and data["modules"][f].get("status") != "promoted")
    if not added:
        return None, [], gone
    return current.rstrip("\n") + "\n\n" + "".join(module_block(f, today) for f in added), added, gone


def main(argv: list[str] | None = None) -> int:
    """Plan or apply code-map adoption for one project.

    Args:
        argv: command-line arguments (None for sys.argv).

    Returns:
        The exit code.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--apply", action="store_true", help="write code-map.toml (default: print the plan)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    if not TEMPLATE.is_file():
        print(f"code map: skill-coder's template not found at {TEMPLATE}", file=sys.stderr)
        return 1
    text, added, gone = plan(root, datetime.date.today().isoformat())
    for rel in gone:
        print(f"code map: [modules.\"{rel}\"] names a file that is gone; mark it promoted or remove it by hand")
    if text is None:
        print(f"code map: {'no code to map' if not (root / MAP_NAME).is_file() else 'current'}")
        return 0
    verb = "create" if not (root / MAP_NAME).is_file() else "extend"
    print(f"code map: {verb} {MAP_NAME} with {len(added)} unreviewed module entr{'y' if len(added) == 1 else 'ies'}")
    if not args.apply:
        print("plan only; add --apply to write")
        return 0
    (root / MAP_NAME).write_text(text)
    sys.path.insert(0, str(CODER / "scripts"))
    try:
        importlib.import_module("code_map").load(root / MAP_NAME)
    except (ImportError, ValueError) as exc:
        print(f"code map: written but skill-coder's reader refuses it: {exc}", file=sys.stderr)
        return 1
    print(f"code map: written and loaded by skill-coder's reader ({root / MAP_NAME})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
