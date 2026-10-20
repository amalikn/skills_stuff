#!/usr/bin/env python3
"""Read a project's code map (`code-map.toml`): the human decisions about its code that the pack's checkers act on. Stdlib only (tomllib).

Why (operator, 2026-10-19: "is there a need of code-map like we have context-map or target-map or guide-map"): a project's code intent was
spread over several files that drift apart (an import-layer TOML, a write-gate register inside a checker, a promotion register, a refactor
tracker). The code map holds that intent in one place, data first, and every checker in this pack reads its own section from it.

It holds only decisions, never facts the code states: no line counts, import edges or header text (the checkers measure those, and their
shrink-only baselines stay separate, machine-written files). TOML, not YAML, because the checkers run with the target project's own
interpreter and Python 3.11 reads TOML without installing anything.

Sections (all optional; template: the pack's templates/code-map.toml):
    [scan]            roots = ["src", "scripts"]; python = "3.11"; [scan.exclude] "<path>" = "<why its rule lives elsewhere>"
    [limits.<lang>]   module, function, warn_module, warn_function  (lang: python, shell, c-family, or a suffix such as "go")
    [layers]          src = "src"; package = "app"; baseline = "..."; then [layers.rules.<subpackage>] layer, may_import
    [write_gates]     roots, suffixes, write_patterns, apply_pattern; [write_gates.exceptions] "<path>" = "<reason>"
    [timeouts]        roots; baseline
    [group_timeouts]  roots; baseline   (timed ssh/shell subprocess calls that leave children running)
    [suppressions]    roots; baseline   (inline linter suppressions)
    [naming]          recipe = "<convention>"; [naming.files] "<glob>" = "<convention>"  (overrides the pack's naming.toml)
    [modules."<path>"] status = "project_only" | "candidate" | "promoted"; reason; needs; skill

Imported, not run: `from code_map import load, section`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: Section names a code map may have; anything else is reported, so a typo does not silently switch a rule off.
SECTIONS = ("scan", "limits", "layers", "write_gates", "timeouts", "group_timeouts", "suppressions", "modules", "naming", "meta")
STATUSES = ("project_only", "candidate", "promoted")


def load(path: Path | None) -> dict:
    """Read and check a code map.

    Args:
        path: the code-map.toml file, or None for no map.

    Returns:
        The map as a dict ({} for None).

    Raises:
        ValueError: when the file does not parse, names an unknown section, or a module entry has an unknown status or no reason.
    """
    if path is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    problems = [f"unknown section [{k}]" for k in data if k not in SECTIONS]
    for rel, entry in data.get("modules", {}).items():
        if entry.get("status") not in STATUSES:
            problems.append(f"modules.\"{rel}\": status must be one of {', '.join(STATUSES)}")
        elif entry["status"] == "promoted" and not entry.get("skill"):
            problems.append(f"modules.\"{rel}\": a promoted module names the skill file it moved to")
        elif entry["status"] != "promoted" and not (entry.get("reason") or entry.get("needs")):
            problems.append(f"modules.\"{rel}\": say why (reason) or what it still needs (needs)")
    if problems:
        raise ValueError(f"{path}: " + "; ".join(problems))
    return data


def section(data: dict, name: str) -> dict:
    """One section of a loaded map.

    Args:
        data: load()'s result.
        name: a name from SECTIONS.

    Returns:
        The section ({} when absent).
    """
    return dict(data.get(name, {}))


def for_root(root: Path, given: Path | None) -> dict:
    """The code map a checker uses: the one given, else `code-map.toml` at the project root when it exists, else none.

    Args:
        root: the project root.
        given: --code-map as passed (relative to the root), or None.

    Returns:
        load()'s result.

    Raises:
        ValueError: as load().
    """
    path = root / given if given else root / "code-map.toml"
    return load(path if (given or path.is_file()) else None)


def grammar(cli: str | None, data: dict) -> tuple[int, int] | None:
    """The Python grammar to parse with: --python, else `[scan] python`, else this interpreter's.

    Args:
        cli: --python as passed, or None.
        data: load()'s result.

    Returns:
        (major, minor), or None.
    """
    text = cli or section(data, "scan").get("python")
    return tuple(int(x) for x in str(text).split(".")[:2]) if text else None


def scan_roots(data: dict, own: str = "", default: str = "src,scripts") -> str:
    """The folders a checker scans: its own section's `roots`, else `[scan] roots`, else the default.

    Args:
        data: load()'s result.
        own: the checker's section name.
        default: comma-separated fallback.

    Returns:
        Comma-separated folders.
    """
    roots = section(data, own).get("roots") if own else None
    roots = roots or section(data, "scan").get("roots")
    return ",".join(roots) if roots else default


def excluded(data: dict) -> dict[str, str]:
    """Files no checker measures, each with the reason (a file whose rule is owned elsewhere, such as a checker generated from another skill's
    template, or vendored code).

    Args:
        data: load()'s result.

    Returns:
        {repo-relative path: reason} from `[scan.exclude]`.

    Raises:
        ValueError: when an entry has no reason.
    """
    out = dict(section(data, "scan").get("exclude", {}))
    if blank := [k for k, v in out.items() if not str(v).strip()]:
        raise ValueError(f"[scan.exclude] entries need a reason: {', '.join(blank)}")
    return out
