#!/usr/bin/env python3
"""Move named sections of a governed markdown file (AGENTS.md, SCRATCHPAD.md, SKILL.md) verbatim into an on-need reference file. Stdlib only.

Why (operator, 2026-10-10): rotation moves only dated history, so a file held over its 200-line / 25 KB budget by durable reference material
(key anchors, audit procedures, hardware tables) stayed over budget after every rotation, and each fix needed hand-written scripts. One run does it:
1. Cut the named `##`, `###` or `####` sections (each to the next heading at its level or above) and write them, verbatim and in order, to the
   destination under a front-matter header.
2. Leave a pointer naming each moved section, so a citation such as `AGENTS.md § Live Audit Procedure` still resolves: a pointer section
   (default), one linked line (`--pointer-line`), or a bullet added to one shared section (`--pointer-into HEADING`, created when missing).
3. Drop the moved sections' Contents entries (matched by link text, so any anchor style works).
4. Rewrite relative links for the destination's folder, but only links whose target exists (example links stay as written).
5. Repoint in-page `#anchor` links that cross the move, in both files, and links from other project markdown to a moved section of the source.
6. Refuse to write if any moved line is missing from the destination.
Without `--apply` it prints the plan and changes nothing. Index the destination in its folder `readme.md` afterwards (budget_plan.py does).

Usage:
    python scripts/move_sections.py --project-root . --source AGENTS.md --dest docs/agent-reference-20261010_1859.md \
        --title "Agent reference" --summary "On-need reference moved from AGENTS.md" "Live Audit Procedure" "Decision Matrix"
    python scripts/move_sections.py ... --pointer-into "Reference moved out" --apply
Exit: 0 planned or moved, 1 on a refusal (section not found, destination exists, a line would be lost), 2 on bad arguments.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import pathlib
import re
import sys
from collections import Counter

_spec = importlib.util.spec_from_file_location("rotate_records", pathlib.Path(__file__).resolve().parent / "rotate_records.py")
rr = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("rotate_records", rr)
_spec.loader.exec_module(rr)

HEADING = re.compile(r"^(#{2,4}) (.+?)\s*$")
ANY_HEADING = re.compile(r"^#{1,6} (.+?)\s*$")
TOC_ENTRY = re.compile(r"^\s*- \[(.+?)\]\(#[^)]*\)\s*$")
IN_PAGE = re.compile(r"\]\(#([\w\-]+)\)")
LEGACY_POINTER = re.compile(r"^## Reference moved out \((\d+)\)\s*$")
SKIP_DIRS = ("/.git/", "/docs/history/", "/node_modules/", "/.venv/")


def slug(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading: lower case, punctuation dropped, each space a hyphen (double hyphens kept).

    Args:
        heading: the heading text without its hashes.

    Returns:
        The anchor.
    """
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(lines: list[str]) -> set[str]:
    """Anchors of every heading outside fenced code.

    Args:
        lines: a file's lines.

    Returns:
        The set of anchors.
    """
    out, fence = set(), False
    for line in lines:
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and ANY_HEADING.match(line):
            out.add(slug(ANY_HEADING.match(line).group(1)))
    return out


def sections(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Map each `##`, `###` or `####` heading to its span (to the next heading at its level or above), ignoring headings inside fenced code.

    A heading text that appears twice maps to its first occurrence.

    Args:
        lines: the file's lines.

    Returns:
        {heading text: (start index, end index exclusive)}.
    """
    heads, fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and HEADING.match(line):
            heads.append((i, len(HEADING.match(line).group(1))))
    out: dict[str, tuple[int, int]] = {}
    for k, (a, level) in enumerate(heads):
        b = next((j for j, lv in heads[k + 1:] if lv <= level), len(lines))
        out.setdefault(HEADING.match(lines[a]).group(2), (a, b))
    return out


def pointer_bullet(dest: str, names: list[str]) -> str:
    """One bullet naming a destination and the sections it holds.

    Args:
        dest: the destination as the source links it.
        names: the moved headings.

    Returns:
        The bullet line.
    """
    return f"- [{dest}]({dest}): " + "; ".join(names) + "."


def plan(lines: list[str], names: list[str], dest: str, pointer: str, pointer_line: bool = False,
         pointer_into: str | None = None) -> tuple[list[str], list[list[str]]]:
    """Build the new source text and the moved blocks.

    Args:
        lines: the source file's lines.
        names: headings of the sections to move, in the order they should appear in the destination.
        dest: the destination path as the source should link it.
        pointer: heading of the pointer section left in the source (default mode).
        pointer_line: leave one linked line instead of a pointer section (for many moves out of one file, e.g. a SKILL.md).
        pointer_into: add a bullet to the section with this heading, creating it where the first moved section was when it is missing.

    Returns:
        (the source's new lines, the moved blocks verbatim).

    Raises:
        KeyError: a named section does not exist.
    """
    spans = sections(lines)
    missing = [n for n in names if n not in spans]
    if missing:
        raise KeyError(", ".join(missing))
    moved, cut = [], set()
    for n in names:
        a, b = spans[n]
        block = lines[a:b]
        while block and block[-1].strip() in ("", "---"):
            block.pop()
        moved.append(block)
        cut |= set(range(a, b))
    first = min(spans[n][0] for n in names)
    existing = spans.get(pointer_into) if pointer_into else None
    if pointer_into and existing:
        ptr: list[str] = []
    elif pointer_into:
        ptr = [f"## {pointer_into}", "", "Sections moved verbatim from this file (read on need; a citation by section name resolves there):",
               pointer_bullet(dest, names), ""]
    elif pointer_line:
        ptr = [f"- Read [{dest}]({dest}) before that work (moved verbatim from here): " + "; ".join(names) + ".", ""]
    else:
        ptr = [f"## {pointer}", "",
               f"Read [{dest}]({dest}) before the work it covers. It holds these sections, moved verbatim from this file (a citation of a section",
               "by name resolves there): " + "; ".join(names) + ".", ""]
    toc_heading = None if (pointer_line or existing) else (pointer_into or pointer)
    out, toc_done = [], toc_heading is None
    for i, line in enumerate(lines):
        if i == first and ptr:
            if out and out[-1].strip():
                out.append("")
            out += ptr
        if i in cut:
            continue
        m = TOC_ENTRY.match(line)
        if m and m.group(1) in names:
            if not toc_done:
                out.append(f"- [{toc_heading}](#{slug(toc_heading)})")
                toc_done = True
            continue
        out.append(line)
    if existing:
        # the shared section's last bullet, or its heading when it has none: the new bullet goes after it
        start = next(i for i, l in enumerate(out) if l.strip() == f"## {pointer_into}")
        end = next((i for i in range(start + 1, len(out)) if out[i].startswith("## ")), len(out))
        last = max((i for i in range(start, end) if out[i].startswith("- ")), default=start + 1)
        out.insert(last + 1, pointer_bullet(dest, names))
    return out, moved


def consolidate(lines: list[str], heading: str = "Reference moved out") -> tuple[list[str], int]:
    """Merge legacy numbered pointer sections ("## Reference moved out (1)", "(2)", ...) into one section, keeping every destination link.

    The merged section takes the place of the first numbered one, and its Contents entry the place of the first numbered entry.

    Args:
        lines: a file's lines.
        heading: the merged section's heading.

    Returns:
        (the new lines, how many numbered sections were merged).
    """
    out: list[str] = []
    bullets: list[str] = []
    toc_seen = sec_seen = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if LEGACY_POINTER.match(line):
            j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
            body = " ".join(lines[i + 1:j])
            m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", body)
            names = re.search(r"resolves there\): (.+?)\.\s*$", body)
            if m:
                bullets.append(pointer_bullet(m.group(2), [names.group(1)] if names else [m.group(1)]))
            if not sec_seen:
                out.append("\0SECTION")
                sec_seen = True
            i = j
            continue
        if re.match(r"^\s*- \[Reference moved out \(\d+\)\]\(#[^)]*\)\s*$", line):
            if not toc_seen:
                out.append("\0TOC")
                toc_seen = True
            i += 1
            continue
        out.append(line)
        i += 1
    if len(bullets) < 2:
        return lines, 0
    section = [f"## {heading}", "", "Sections moved verbatim from this file (read on need; a citation by section name resolves there):"]
    section += sorted(bullets) + [""]
    merged: list[str] = []
    for line in out:
        if line == "\0SECTION":
            merged += section
        elif line == "\0TOC":
            merged.append(f"- [{heading}](#{slug(heading)})")
        else:
            merged.append(line)
    return merged, len(bullets)


def repoint_in_page(src_lines: list[str], moved: list[list[str]], src_rel: str, dst_rel: str) -> tuple[list[str], list[list[str]], int]:
    """Repoint `#anchor` links that cross the move: source links to a moved heading go to the destination, and moved links to a heading
    that stayed go back to the source.

    Args:
        src_lines: the source's lines after the cut.
        moved: the moved blocks.
        src_rel: the source, project-relative.
        dst_rel: the destination, project-relative.

    Returns:
        (the source's lines, the moved blocks, how many links changed).
    """
    moved_a = anchors([l for b in moved for l in b])
    stay_a = anchors(src_lines)
    to_dst = os.path.relpath(dst_rel, os.path.dirname(src_rel) or ".")
    to_src = os.path.relpath(src_rel, os.path.dirname(dst_rel) or ".")
    n = 0

    def fix(line: str, ours: set[str], theirs: set[str], target: str) -> str:
        """Rewrite the in-page links of one line whose anchor lives in the other file.

        Args:
            line: the line.
            ours: anchors present in this line's file.
            theirs: anchors present in the other file.
            target: the other file, relative to this one.

        Returns:
            The line.
        """
        nonlocal n

        def one(m: re.Match) -> str:
            """One in-page link, repointed when its anchor moved to the other file.

            Args:
                m: the link match.

            Returns:
                The link text.
            """
            nonlocal n
            a = m.group(1)
            if a in ours or a not in theirs:
                return m.group(0)
            n += 1
            return f"]({target}#{a})"
        return IN_PAGE.sub(one, line)

    new_src = [fix(l, stay_a, moved_a, to_dst) for l in src_lines]
    new_moved = [[fix(l, moved_a, stay_a, to_src) for l in b] for b in moved]
    return new_src, new_moved, n


def repoint_project(root: pathlib.Path, src_rel: str, dst_rel: str, moved_a: set[str], apply: bool) -> list[str]:
    """Repoint links from other project markdown that target a moved section of the source (`AGENTS.md#layout` -> the destination).

    Args:
        root: the project root.
        src_rel: the source, project-relative.
        dst_rel: the destination, project-relative.
        moved_a: anchors of the moved headings.
        apply: write the files.

    Returns:
        The files that link to a moved section (changed when apply is set).
    """
    src_abs = (root / src_rel).resolve()
    changed = []
    for path in sorted(root.rglob("*.md")):
        rel = "/" + path.relative_to(root).as_posix()
        if any(s in rel for s in SKIP_DIRS) or path.resolve() in (src_abs, (root / dst_rel).resolve()):
            continue
        text = path.read_text(errors="replace")

        def one(m: re.Match) -> str:
            """One link, repointed when it targets a moved section of the source.

            Args:
                m: the link match (target, anchor).

            Returns:
                The link text.
            """
            target, anchor = m.group(1), m.group(2)
            if anchor not in moved_a or target.startswith(("http", "mailto:")):
                return m.group(0)
            resolved = (pathlib.Path(target) if target.startswith("/") else (path.parent / target)).resolve()
            if resolved != src_abs:
                return m.group(0)
            return f"]({os.path.relpath(root / dst_rel, path.parent)}#{anchor})"
        new = re.sub(r"\]\(([^)#\s]+)#([\w\-]+)\)", one, text)
        if new != text:
            changed.append(path.relative_to(root).as_posix())
            if apply:
                path.write_text(new)
    return changed


def dest_text(moved: list[list[str]], source: str, title: str, summary: str, today: str) -> str:
    """The destination file: front matter, a one-line provenance note, then the sections verbatim.

    Args:
        moved: the moved blocks.
        source: the source path, for the provenance note.
        title: the destination's title.
        summary: its one-line summary.
        today: ISO date for `Last reviewed`.

    Returns:
        The file text.
    """
    head = ["---", f"Title: {title}", "Category: reference", "Status: current", "Authority: local-supplement",
            f"Scope: On-need reference moved verbatim from {source}", f"Last reviewed: {today}", "Summary: >-", f"  {summary}", "---", "",
            f"# {title}", "", f"Moved verbatim from `{source}` on {today} to keep that file within its budget for files loaded whole.", ""]
    names = [HEADING.match(b[0]).group(2) for b in moved]
    if sum(len(b) for b in moved) > 100:
        head += ["## Contents", ""] + [f"- [{n}](#{slug(n)})" for n in names] + [""]
    body: list[str] = []
    for b in moved:
        body += b + [""]
    return "\n".join(head + body).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """Plan or apply one section move.

    Args:
        argv: command-line arguments (default: sys.argv).

    Returns:
        The exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--source", required=True, help="project-relative file to cut from")
    ap.add_argument("--dest", required=True, help="project-relative reference file to create")
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--pointer", default="Reference loaded on need", help="heading of the pointer section left in the source")
    ap.add_argument("--pointer-line", action="store_true", help="leave one linked line instead of a pointer section")
    ap.add_argument("--pointer-into", help="add a bullet to the section with this heading (created when missing)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("names", nargs="+", help="exact headings to move")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root)
    src, dst = root / args.source, root / args.dest
    if dst.exists():
        print(f"refused: {args.dest} exists")
        return 1
    lines = src.read_text().splitlines()
    try:
        new, moved = plan(lines, args.names, args.dest, args.pointer, args.pointer_line, args.pointer_into)
    except KeyError as exc:
        print(f"refused: section(s) not found in {args.source}: {exc}")
        return 1
    src_dir, dst_dir = (("" if d == "." else d) for d in (str(pathlib.Path(args.source).parent), str(pathlib.Path(args.dest).parent)))

    def relink_real(line: str) -> str:
        """Relink only links whose target exists from the source's folder; example links (`../<folder>/README.md`) stay as written.

        Args:
            line: one moved line.

        Returns:
            The line with real relative links rewritten for the destination.
        """
        def one(m: re.Match) -> str:
            """One markdown link, relinked when its target is a real file.

            Args:
                m: the link match (label, target).

            Returns:
                The link text to keep.
            """
            target = m.group(2).split("#")[0]
            if not target or target.startswith(("/", "http", "mailto:")) or not (root / src_dir / target).exists():
                return m.group(0)
            return rr.relink([m.group(0)], src_dir, dst_dir)[0]
        return re.sub(r"(\[[^\]]*\])\(([^)\s]+)\)", one, line)

    moved = [[relink_real(l) for l in b] for b in moved]
    lost = Counter(l for b in moved for l in b)
    new, moved, n_links = repoint_in_page(new, moved, args.source, args.dest)
    text = dest_text(moved, args.source, args.title, args.summary, dt.date.today().isoformat())
    have = Counter(re.sub(r"\]\([^)]*\)", "]", l) for l in text.splitlines())
    lost = Counter(re.sub(r"\]\([^)]*\)", "]", l) for l in lost.elements()) - have
    if lost:
        print(f"refused: {sum(lost.values())} moved line(s) would be lost, e.g. {next(iter(lost))!r}")
        return 1
    others = repoint_project(root, args.source, args.dest, anchors([l for b in moved for l in b]), args.apply)
    n = sum(len(b) for b in moved)
    print(f"{args.source}: {len(lines)} -> {len(new)} lines; {n} lines in {len(moved)} section(s) -> {args.dest}; "
          f"{n_links} in-page link(s) repointed; other files linking to moved sections: {', '.join(others) or 'none'}")
    if not args.apply:
        print("plan only; add --apply to move")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    src.write_text("\n".join(new).rstrip() + "\n")
    print("moved; no line lost. Index the destination in its folder readme.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
