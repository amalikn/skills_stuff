"""Repoint references to moved scripts across a workspace: `scripts/<name>.py` becomes `scripts/<family>/<name>.py`. Stdlib only.

Written 2026-10-27 when skill-ai-it's flat scripts/ folder was split into family folders and about 30 projects and skills called the old
paths from their justfiles, docs and code. History is never rewritten: CHANGELOG and change-log files, docs/history/, archive/ folders, dated files
(`<slug>-YYYYMMDD_hhmm.md`) and generated context are skipped, and so is any file whose own project still has a local script by that name.

Run (plan by default; nothing is written without --apply):
    python scripts/adoption/repoint_paths.py --map families.txt --root /Volumes/Data/_ai/_project/project_stuff [--root ...] [--apply]

families.txt: one line per family, `<family> <name> <name> ...` (names without `.py`).
Exit: 0 when nothing is left to repoint (or --apply wrote every change), 1 when a plan has changes pending, 2 on bad input.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".ai-context", "graphify-out", "archive", ".staleness-audit"}
SKIP_PARTS = ("docs/history/", "docs/reviews/staleness-audit-", "/.remember/")
TEXT_SUFFIXES = {".md", ".py", ".sh", ".yaml", ".yml", ".toml", ".json", ".txt", ".j2", ""}
MAX_BYTES = 2_000_000
DATED = re.compile(r"-\d{8}_\d{4}\.md$")


def load_map(path: Path) -> dict[str, str]:
    """Read the family file into a name -> family mapping.

    Args:
        path: the families file, one `<family> <name> ...` line each.

    Returns:
        Each script stem mapped to its family folder.

    Raises:
        SystemExit: when a name is listed twice.
    """
    mapping: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        for name in parts[1:]:
            if name in mapping:
                raise SystemExit(f"{name} listed twice in {path}")
            mapping[name] = parts[0]
    return mapping


def skipped(path: Path) -> bool:
    """Say whether a file is history, generated or vendored and must not be rewritten.

    Args:
        path: the candidate file.

    Returns:
        True when the file is left alone.
    """
    posix = path.as_posix()
    if any(part in SKIP_DIRS or part.endswith("-github") for part in path.parts):
        return True
    if path.name.upper().startswith("CHANGELOG") or path.name.lower().startswith("change-log") or any(s in posix for s in SKIP_PARTS):
        return True
    if DATED.search(path.name):  # a dated report or record is history
        return True
    if path.suffix not in TEXT_SUFFIXES and path.name not in {"justfile", "Justfile", "Makefile"}:
        return True
    return path.suffix == "" and path.name not in {"justfile", "Justfile", "Makefile"}


def has_local(path: Path, name: str, stop: Path) -> bool:
    """Say whether a folder between the file and the root holds its own `scripts/<name>.py`.

    Args:
        path: the file holding the reference.
        name: the script stem.
        stop: the search root; the walk does not go above it.

    Returns:
        True when the reference may mean a local script, so it is left alone.
    """
    for folder in path.parents:
        if (folder / "scripts" / f"{name}.py").is_file():
            return True
        if folder == stop:
            break
    return False


def plan_file(path: Path, pattern: re.Pattern[str], mapping: dict[str, str], root: Path) -> tuple[str, int]:
    """Rewrite one file's text in memory.

    Args:
        path: the file.
        pattern: matches `scripts/<name>.py` for every mapped name, not already inside a family folder.
        mapping: name -> family.
        root: the search root, for the local-script guard.

    Returns:
        The new text and how many references changed.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return "", 0
    count = 0

    def swap(match: re.Match[str]) -> str:
        """Repoint one match unless a local script of that name exists."""
        nonlocal count
        name = match.group(1)
        if has_local(path, name, root):
            return match.group(0)
        count += 1
        return f"scripts/{mapping[name]}/{name}.py"

    return pattern.sub(swap, text), count


def main(argv: list[str] | None = None) -> int:
    """Plan or apply the repointing over every root.

    Args:
        argv: command-line arguments; None reads sys.argv.

    Returns:
        0 when clean or applied, 1 when changes are pending, 2 on bad input.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--map", required=True, type=Path, help="families file")
    ap.add_argument("--root", required=True, action="append", type=Path, help="folder to search; repeatable")
    ap.add_argument("--apply", action="store_true", help="write the changes")
    args = ap.parse_args(argv)
    if not args.map.is_file():
        print(f"no such map: {args.map}", file=sys.stderr)
        return 2
    mapping = load_map(args.map)
    pattern = re.compile(r"(?<![\w-])scripts/(" + "|".join(map(re.escape, sorted(mapping))) + r")\.py\b")
    total = files = 0
    for root in args.root:
        root = root.resolve()
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if skipped(path.relative_to(root)) or path.stat().st_size > MAX_BYTES:
                continue
            new, count = plan_file(path, pattern, mapping, root)
            if not count:
                continue
            files += 1
            total += count
            print(f"{count:4d}  {path}")
            if args.apply:
                path.write_text(new, encoding="utf-8")
    verb = "repointed" if args.apply else "to repoint (plan only; add --apply)"
    print(f"{total} reference(s) in {files} file(s) {verb}")
    return 0 if args.apply or total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
