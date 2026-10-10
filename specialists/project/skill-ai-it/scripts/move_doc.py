#!/usr/bin/env python3
"""Move a project document (typically a superseded one into its folder's `archive/`) without breaking anything. Stdlib plus git.

Why (operator, 2026-10-10): superseded files left beside current ones keep being read and searched; moving them by hand breaks links
and indexes (a 2026-10-09 move captured only file names and left three stale links). One move does all of it:

1. `git mv` the file to the destination (default: `<its folder>/archive/<name>`).
2. Rewrite every link that resolves to the old path in tracked text files, keeping each link's style: relative to the linking file,
   relative to the project root, or absolute. Dated records (`CHANGELOG.md`, `SCRATCHPAD.md`, and any `--keep-records` file) are not
   edited; they keep the old path and the moved-paths map resolves it.
3. Move the file's line in its old folder's `readme.md` into the destination folder's `readme.md` (created with a heading if missing),
   with the link adjusted, so `check_docs_indexed`-style rules keep passing.
4. Record `old -> new` in the project's moved-paths map (`--moved-paths`, JSON with a `moves` object) when one exists.

Without `--apply` it prints the plan and changes nothing.

Usage:
    python scripts/move_doc.py --project-root . docs/engineering/old-review-20261009_2304.md            # plan
    python scripts/move_doc.py --project-root . --apply docs/engineering/old-review-20261009_2304.md    # move to docs/engineering/archive/
    python scripts/move_doc.py --project-root . --to docs/archive/x.md --moved-paths wc-local/scripts/moved-paths.json --apply a.md
Exit: 0 planned or moved, 1 on a refusal (missing file, destination exists, not tracked), 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt", ".py", ".sh", ".toml"}
DATED_RECORDS = {"CHANGELOG.md", "SCRATCHPAD.md"}
PATH_CHARS = r"[A-Za-z0-9_./~@+-]"


def tracked_files(root: pathlib.Path) -> list[str]:
    """The text files git tracks under root.

    Args:
        root: the project root.

    Returns:
        Project-relative paths with a text suffix.
    """
    out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    return [p for p in out if p and pathlib.PurePosixPath(p).suffix in TEXT_SUFFIXES]


def resolves_to(token: str, linking_file: str, root: pathlib.Path, target: str) -> str | None:
    """Which style a path token uses if it names `target`.

    Args:
        token: the path as written (may carry a `#anchor`).
        linking_file: project-relative path of the file containing it.
        root: the project root (absolute).
        target: the project-relative path being moved.

    Returns:
        `relative`, `root` or `absolute` when the token resolves to target; None otherwise.
    """
    bare = token.split("#", 1)[0]
    if bare.startswith("/"):
        return "absolute" if os.path.normpath(bare) == str(root / target) else None
    rel = os.path.normpath(os.path.join(os.path.dirname(linking_file), bare))
    if rel == target:
        return "relative"
    if os.path.normpath(bare) == target:
        return "root"
    return None


def restyle(style: str, linking_file: str, root: pathlib.Path, new: str, anchor: str) -> str:
    """The new path written in the same style as the old one.

    Args:
        style: `relative`, `root` or `absolute`.
        linking_file: project-relative path of the file containing the link.
        root: the project root (absolute).
        new: the destination, project-relative.
        anchor: a `#...` suffix to keep, or an empty string.

    Returns:
        The replacement token.
    """
    if style == "absolute":
        path = str(root / new)
    elif style == "root":
        path = new
    else:
        path = os.path.relpath(new, os.path.dirname(linking_file) or ".")
    return path + anchor


def plan_link_edits(root: pathlib.Path, old: str, new: str, keep: set[str]) -> dict[str, tuple[str, int]]:
    """The rewritten text of every file that links to `old`.

    Args:
        root: the project root (absolute).
        old: the project-relative path being moved.
        new: its destination.
        keep: project-relative files never edited (dated records).

    Returns:
        File to (new text, number of links rewritten), only for files that change.
    """
    base = re.escape(pathlib.PurePosixPath(old).name)
    pattern = re.compile(rf"{PATH_CHARS}*{base}(#[A-Za-z0-9_-]*)?")
    edits: dict[str, tuple[str, int]] = {}
    for rel in tracked_files(root):
        if rel == old or rel in keep or pathlib.PurePosixPath(rel).name in DATED_RECORDS:
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if pathlib.PurePosixPath(old).name not in text:
            continue
        count = 0

        def swap(m: re.Match) -> str:
            """One path token, rewritten when it resolves to the moved file.

            Args:
                m: the match of a path-like token.

            Returns:
                The token, restyled to the new path, or unchanged.
            """
            nonlocal count
            token = m.group(0)
            anchor = m.group(1) or ""
            style = resolves_to(token, rel, root, old)
            if style is None:
                return token
            count += 1
            return restyle(style, rel, root, new, anchor)

        updated = pattern.sub(swap, text)
        if count:
            edits[rel] = (updated, count)
    return edits


def index_edits(root: pathlib.Path, old: str, new: str) -> dict[str, str]:
    """Move the file's line from its old folder index to the destination folder index.

    Args:
        root: the project root (absolute).
        old: the project-relative path being moved.
        new: its destination.

    Returns:
        Index file (project-relative) to its new text; empty when the old folder has no readme line for the file.
    """
    old_index = str(pathlib.PurePosixPath(old).parent / "readme.md")
    new_index = str(pathlib.PurePosixPath(new).parent / "readme.md")
    if not (root / old_index).is_file() or old_index == new_index:
        return {}
    name = pathlib.PurePosixPath(old).name
    lines = (root / old_index).read_text(encoding="utf-8").split("\n")
    link = re.compile(rf"\]\(([^)\s]*{re.escape(name)})(#[^)]*)?\)")
    start = next((i for i, l in enumerate(lines) if link.search(l) and l.lstrip().startswith(("-", "|"))), None)
    if start is None:
        return {}
    end = start + 1
    while end < len(lines) and lines[end].startswith("  ") and lines[start].lstrip().startswith("-"):
        end += 1
    moved = lines[start:end]
    rest = lines[:start] + lines[end:]
    target = os.path.relpath(new, os.path.dirname(new_index))
    moved = [link.sub(lambda m: f"]({target}{m.group(2) or ''})", l) for l in moved]
    out = {old_index: "\n".join(rest)}
    if (root / new_index).is_file():
        text = (root / new_index).read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(moved) + "\n"
    else:
        folder = pathlib.PurePosixPath(new_index).parent
        text = (f"# Archive — {folder.parent.name or folder}\n\nSuperseded documents, kept for history. Agents and searches skip this folder;"
                " open a file here only when a live document points to it or the history is the question.\n\n" + "\n".join(moved) + "\n")
        archive_link = f"- [archive/](archive/readme.md) Superseded documents from this folder, kept for history."
        if folder.name == "archive" and archive_link not in out[old_index]:
            out[old_index] = out[old_index].rstrip("\n") + "\n" + archive_link + "\n"
    out[new_index] = text
    return out


def main(argv: list[str] | None = None) -> int:
    """Plan or apply one move.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        The exit code: 0 planned or moved, 1 refused, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", help="project-relative file to move")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--to", help="project-relative destination; default <folder>/archive/<name>")
    ap.add_argument("--moved-paths", default="", help="project-relative JSON map with a `moves` object to record the move in")
    ap.add_argument("--keep-records", default="", help="comma-separated extra files never edited (dated records)")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    old = os.path.normpath(args.path)
    new = os.path.normpath(args.to) if args.to else str(pathlib.PurePosixPath(old).parent / "archive" / pathlib.PurePosixPath(old).name)
    if not (root / old).is_file():
        print(f"refused: {old} does not exist", file=sys.stderr)
        return 1
    if (root / new).exists():
        print(f"refused: {new} already exists", file=sys.stderr)
        return 1
    if old not in tracked_files(root):
        print(f"refused: {old} is not tracked by git", file=sys.stderr)
        return 1
    keep = {k.strip() for k in args.keep_records.split(",") if k.strip()}
    links = plan_link_edits(root, old, new, keep)
    indexes = index_edits(root, old, new)  # plan view; recomputed after the link edits are written so both apply
    print(f"move {old} -> {new}")
    for rel, (_, n) in sorted(links.items()):
        print(f"  relink {rel}: {n} link(s)")
    for rel in sorted(indexes):
        print(f"  index  {rel}")
    if args.moved_paths:
        print(f"  record {args.moved_paths}")
    if not args.apply:
        print("plan only; add --apply to move")
        return 0
    (root / new).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(root), "mv", old, new], check=True)
    for rel, (text, _) in links.items():
        (root / rel).write_text(text, encoding="utf-8")
    for rel, text in index_edits(root, old, new).items():
        (root / rel).write_text(text, encoding="utf-8")
    if args.moved_paths and (root / args.moved_paths).is_file():
        data = json.loads((root / args.moved_paths).read_text(encoding="utf-8"))
        data.setdefault("moves", {})[old] = new
        (root / args.moved_paths).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("moved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
