#!/usr/bin/env python3
"""Read a large Markdown file by section: an outline with each heading's line range, or one section by selector. Read-only; stdlib only.

Why (lilmd assessment, 2026-10-11, UNC docs/reports/knowledge-tooling/lilmd-assessment-20261011_0517.md): agents rebuilt heading outlines by
hand (`grep -n '^#'`) 747 times in 98 of 182 sessions, and a heading grep gives a section's first line but not its last, so the range was
guessed or read twice. The outline prints both ends; `section` prints one section. The idea is lilmd's (molefrog/lilmd); no code is taken
from it (it carries no licence). Unlike lilmd the default match is exact, because numbered headings collide under substring matching
(`8.7.1` inside `8.7.10`: 44 of 123 headings in UNC's target design), and an ambiguous selector is an error that lists every match.

Selector: segments joined by ` > `; each later segment must be a descendant (any depth) of the one before. A segment matches a heading when
- it equals the title (case-insensitive), or is a whole-word prefix of it (`Stage 1` matches `Stage 1 — Containment`, not `Stage 10`),
  with or without the title's leading section number (`17.6.2 Stage 1 — ...` matches `Stage 1` and `17.6.2`, never `17.6.20`);
- `~text`: the title contains text (case-insensitive);
- `#anchor`: the heading's GitHub/VS Code anchor equals it (paste a Contents link target).

Usage:
    python scripts/md_sections.py outline <file> [--depth N] [--json]
    python scripts/md_sections.py section <file> "<selector>" [--max-lines N] [--no-children] [--all]
Exit: 0 found; 1 no match (closest titles listed); 2 bad arguments or unreadable file; 3 ambiguous selector (matches listed; `--all` prints them).
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import json
import pathlib
import re
import sys

ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
#: a leading section number (`17.6.2 `, `17. `), so `Stage 1` names `17.6.2 Stage 1 — ...`
NUMBER = re.compile(r"^\d+(\.\d+)*\.?\s+")
#: `.6` after `17` continues a section number, so `17` never names `17.6`
BOUNDARY_NUMBER = re.compile(r"^\.\d")
#: lines that cannot be the text of a setext heading: blank, list items, quotes, table rows, other headings, fences
NOT_PARAGRAPH = re.compile(r"^\s*$|^ {0,3}([-*+]|\d+[.)])\s|^ {0,3}>|^\s*\||^ {0,3}#|^ {0,3}(`{3,}|~{3,})")


@dataclasses.dataclass
class Section:
    """One heading and the lines it owns.

    Args:
        level: 1 to 6.
        title: heading text without hashes.
        start: 1-indexed line of the heading.
        end: 1-indexed last line of the section, children included.
        parent: index of the enclosing section in the list, or None.
        body_end: last line before the first child heading (equals end when there is no child).
    """

    level: int
    title: str
    start: int
    end: int = 0
    parent: int | None = None
    body_end: int = 0


def slug(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading (same rule as move_sections.py).

    Args:
        heading: the heading text without its hashes.

    Returns:
        The anchor, without `#`.
    """
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def front_matter_end(lines: list[str]) -> int:
    """Index of the line after a `---` fenced front matter block, or 0 when there is none.

    Args:
        lines: the file's lines.

    Returns:
        The 0-based index where the body starts.
    """
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() in ("---", "..."):
                return i + 1
    return 0


def scan(lines: list[str]) -> list[Section]:
    """Every ATX and setext heading outside front matter and fenced code, with its line range and parent.

    Args:
        lines: the file's lines.

    Returns:
        Sections in document order.
    """
    heads: list[Section] = []
    fence = ""
    #: a setext heading's text is a one-line paragraph: first body line or after a blank line (multi-line setext text is not supported)
    body = i = front_matter_end(lines)
    while i < len(lines):
        line = lines[i]
        m = FENCE.match(line)
        if m:
            mark = m.group(1)
            if not fence:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not line.strip()[len(mark):].strip():
                fence = ""
            i += 1
            continue
        if fence:
            i += 1
            continue
        a = ATX.match(line)
        if a:
            heads.append(Section(len(a.group(1)), (a.group(2) or "").strip(), i + 1))
        elif i + 1 < len(lines) and SETEXT.match(lines[i + 1]) and not NOT_PARAGRAPH.match(line) \
                and (i == body or not lines[i - 1].strip()):
            heads.append(Section(1 if lines[i + 1].strip()[0] == "=" else 2, line.strip(), i + 1))
            i += 2
            continue
        i += 1
    total = len(lines)
    stack: list[int] = []
    for k, sec in enumerate(heads):
        while stack and heads[stack[-1]].level >= sec.level:
            stack.pop()
        sec.parent = stack[-1] if stack else None
        stack.append(k)
        nxt = next((h.start for h in heads[k + 1:] if h.level <= sec.level), total + 1)
        sec.end = nxt - 1
        child = heads[k + 1].start if k + 1 < len(heads) and heads[k + 1].start <= sec.end else None
        sec.body_end = child - 1 if child else sec.end
    return heads


def segment_matches(segment: str, sec: Section) -> bool:
    """Whether one selector segment names this heading.

    Args:
        segment: one part of the selector (`Title`, `~text` or `#anchor`).
        sec: the candidate heading.

    Returns:
        True when it matches.
    """
    seg = segment.strip()
    title = sec.title.lower()
    if seg.startswith("#"):
        return slug(sec.title) == seg[1:].lower()
    if seg.startswith("~"):
        return seg[1:].lower() in title
    seg = seg.lower()
    for text in {title, NUMBER.sub("", title)}:
        if text == seg or (text.startswith(seg) and not text[len(seg)].isalnum() and not BOUNDARY_NUMBER.match(text[len(seg):])):
            return True
    return False


def select(sections: list[Section], selector: str) -> list[Section]:
    """Sections the selector names: the last segment matches the section, earlier ones match ancestors in order.

    Args:
        sections: from scan().
        selector: segments joined by ` > `.

    Returns:
        Matching sections in document order.
    """
    parts = [p for p in (s.strip() for s in selector.split(" > ")) if p]
    out = []
    for sec in sections:
        if not parts or not segment_matches(parts[-1], sec):
            continue
        cursor, ok = sec.parent, True
        for part in reversed(parts[:-1]):
            while cursor is not None and not segment_matches(part, sections[cursor]):
                cursor = sections[cursor].parent
            if cursor is None:
                ok = False
                break
            cursor = sections[cursor].parent
        if ok:
            out.append(sec)
    return out


def path_of(sections: list[Section], sec: Section) -> str:
    """The heading path from the top, for headers and listings.

    Args:
        sections: from scan().
        sec: the section.

    Returns:
        Titles joined by ` > `.
    """
    titles, cursor = [sec.title], sec.parent
    while cursor is not None:
        titles.append(sections[cursor].title)
        cursor = sections[cursor].parent
    return " > ".join(reversed(titles))


def outline(path: pathlib.Path, lines: list[str], depth: int, as_json: bool) -> str:
    """The outline: one line per heading with its line range and size.

    Args:
        path: the file, for the header line.
        lines: its lines.
        depth: deepest heading level shown (6 shows all).
        as_json: emit JSON instead of text.

    Returns:
        The text to print.
    """
    secs = [s for s in scan(lines) if s.level <= depth]
    if as_json:
        return json.dumps([{"level": s.level, "title": s.title, "anchor": slug(s.title), "start": s.start, "end": s.end} for s in secs], indent=1)
    width = len(str(len(lines)))
    rows = [f"{path}  L1-{len(lines)}  {len(secs)} headings  (read one: just section <file> \"<title>\", or Read offset=start limit=lines)"]
    for s in secs:
        rows.append(f"L{s.start:>{width}}-{s.end:<{width}} {s.end - s.start + 1:>5}  {'  ' * (s.level - 1)}{'#' * s.level} {s.title}")
    return "\n".join(rows)


def show(sections: list[Section], lines: list[str], sec: Section, max_lines: int, no_children: bool) -> str:
    """One section's text, under a header naming its path and range.

    Args:
        sections: from scan().
        lines: the file's lines.
        sec: the section to print.
        max_lines: cap on printed lines (0 = no cap).
        no_children: stop before the first child heading.

    Returns:
        The text to print.
    """
    last = sec.body_end if no_children else sec.end
    body = lines[sec.start - 1:last]
    head = f"── {path_of(sections, sec)}  L{sec.start}-{last}"
    if max_lines and len(body) > max_lines:
        cut = sec.start + max_lines
        return "\n".join([head, *body[:max_lines], f"… {len(body) - max_lines} more lines (L{cut}-{last})"])
    return "\n".join([head, *body])


def main(argv: list[str] | None = None) -> int:
    """Run `outline` or `section`.

    Args:
        argv: command-line arguments (default: sys.argv[1:]).

    Returns:
        The exit code (0 found, 1 no match, 2 bad input, 3 ambiguous).
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".", help="resolve relative files against this folder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("outline", help="headings with line ranges")
    o.add_argument("file")
    o.add_argument("--depth", type=int, default=6)
    o.add_argument("--json", action="store_true")
    s = sub.add_parser("section", help="print one section")
    s.add_argument("file")
    s.add_argument("selector")
    s.add_argument("--max-lines", type=int, default=0)
    s.add_argument("--no-children", action="store_true", help="stop before the first child heading")
    s.add_argument("--all", action="store_true", help="print every match instead of refusing an ambiguous selector")
    args = ap.parse_args(argv)
    path = pathlib.Path(args.file)
    if not path.is_absolute():
        path = pathlib.Path(args.project_root) / path
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except OSError as exc:
        print(f"md_sections: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    if lines and lines[-1] == "":
        lines.pop()
    if args.cmd == "outline":
        print(outline(pathlib.Path(args.file), lines, args.depth, args.json))
        return 0
    sections = scan(lines)
    found = select(sections, args.selector)
    if not found:
        close = difflib.get_close_matches(args.selector.split(" > ")[-1].lstrip("~#"), [x.title for x in sections], n=5, cutoff=0.4)
        print(f"no section matches {args.selector!r}" + ("; closest: " + " | ".join(close) if close else ""), file=sys.stderr)
        return 1
    if len(found) > 1 and not args.all:
        print(f"{len(found)} sections match {args.selector!r}; give a longer title, a `Parent > Child` path, a #anchor, or --all:", file=sys.stderr)
        for x in found:
            print(f"  L{x.start}-{x.end}  {path_of(sections, x)}", file=sys.stderr)
        return 3
    print("\n\n".join(show(sections, lines, x, args.max_lines, args.no_children) for x in found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
