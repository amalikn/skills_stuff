#!/usr/bin/env python3
"""Check that every markdown link to a `#heading` in a project's markdown lands on a heading that exists.

Operator, 2026-10-22: plan trackers link their nouns into design sections ("the rescue layout", "Step 2"), and those links must not break
silently when a heading is retitled (for example "(open, operator)" becoming "(decided 2026-10-20)"). Piloted in smc-resiliency's and
unified-network-controller's govchecks the same day and promoted here so both call one copy.

Anchors follow GitHub and VS Code: the heading text lowercased, HTML tags and punctuation other than `-` and `_` dropped, spaces turned into
`-`, a repeated heading suffixed `-1`, `-2`; explicit `<a id="...">` and `<a name="...">` anchors count too. Fenced code is ignored on both
sides. Only links whose target is a markdown file (or the same page) are checked; a missing file is a path check's business, not this one's.

Skipped: any path part starting with `.`, any folder or file whose name contains `-sources-` (verbatim captures, kept as fetched), plus each
`--skip` path prefix and `--skip-name` glob the project names (rotated history, operator prompt files).

Links into a file outside the project root (another project's design, a sibling tracker) are checked the same way. With `--outside warn`
they are reported but do not fail `--check` (operator's side agent, 2026-10-22: a heading renamed by another project's session must not block
this project's commits); the message says to look at the linked project's recent edits first. The default, `--outside fail`, treats them like
any other link.

Read-only: it writes nothing. Runtime: about a second for a few hundred files (each target page parsed once; no network, no subprocess).

Usage (run with the project's venv; paths relative to --project-root, default the current folder):
    python3 anchor_links.py --project-root .                                   # list broken anchors; exit 0
    python3 anchor_links.py --project-root . --check                           # exit 1 on a broken anchor
    python3 anchor_links.py --project-root . --check --skip docs/history/ --skip-name 'prompt-*.md'
    python3 anchor_links.py --project-root . --check --outside warn            # links into other projects warn only
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

_FENCE = re.compile(r"```.*?```", re.DOTALL)
_HEADING = re.compile(r"#{1,6} (.*)")
_HTML_ANCHOR = re.compile(r'<a (?:id|name)="([^"]+)"')
_LINK = re.compile(r"\]\(([^)\s#]*)#([^)\s]+)\)")


def slug(text: str) -> str:
    """The GitHub/VS Code anchor of one heading's text (before any duplicate suffix).

    Args:
        text: the heading text without its leading hashes.

    Returns:
        The anchor slug.
    """
    return re.sub(r"[^\w\- ]", "", re.sub(r"<[^>]+>", "", text).strip().lower()).replace(" ", "-")


def headings(path: Path) -> list[tuple[str, str]]:
    """Every heading of a markdown file with the anchor a link uses for it, in page order.

    Args:
        path: the markdown file.

    Returns:
        (heading text, anchor) pairs; a repeated heading's anchor carries its `-1`, `-2` suffix.
    """
    out: list[tuple[str, str]] = []
    seen: dict[str, int] = {}
    for line in _FENCE.sub("", path.read_text(encoding="utf-8", errors="replace")).splitlines():
        m = _HEADING.match(line)
        if m:
            base = slug(m.group(1))
            n = seen.get(base, 0)
            seen[base] = n + 1
            out.append((m.group(1).strip(), base if n == 0 else f"{base}-{n}"))
    return out


def heading_anchors(path: Path) -> set[str]:
    """Every fragment a link may name to land in this file: heading anchors and HTML `id`/`name` anchors.

    Args:
        path: the markdown file.

    Returns:
        The set of anchors.
    """
    out = {a for _, a in headings(path)}
    out |= set(_HTML_ANCHOR.findall(_FENCE.sub("", path.read_text(encoding="utf-8", errors="replace"))))
    return out


def _skipped(rel: Path, skip: tuple[str, ...], skip_names: tuple[str, ...]) -> bool:
    """Whether a file is outside the check.

    Args:
        rel: the file's path relative to the project root.
        skip: path prefixes to skip (posix, relative to the root).
        skip_names: file-name globs to skip.

    Returns:
        True when the file is skipped.
    """
    if any(part.startswith(".") or "-sources-" in part for part in rel.parts):
        return True
    posix = rel.as_posix()
    return any(posix.startswith(p) for p in skip) or any(fnmatch.fnmatch(rel.name, g) for g in skip_names)


def broken_links(root: Path, skip: tuple[str, ...] = (), skip_names: tuple[str, ...] = ()) -> tuple[int, list[str], list[str]]:
    """Find links to a `#heading` that does not exist.

    Args:
        root: the project root.
        skip: path prefixes to skip, relative to the root.
        skip_names: file-name globs to skip.

    Returns:
        (links checked, broken links into this project, broken links into files outside the root), one message per broken link.
    """
    root = root.resolve()  # targets are resolved, so the root must be too (macOS /var is /private/var)
    cache: dict[Path, set[str]] = {}
    checked, broken, outside = 0, [], []
    for doc in sorted(root.rglob("*.md")):
        rel = doc.relative_to(root)
        if _skipped(rel, skip, skip_names):
            continue
        for target, frag in _LINK.findall(_FENCE.sub("", doc.read_text(encoding="utf-8", errors="replace"))):
            dest = (doc.parent / target).resolve() if target else doc.resolve()
            if dest.suffix != ".md" or not dest.is_file():
                continue
            checked += 1
            if dest not in cache:
                cache[dest] = heading_anchors(dest)
            if frag in cache[dest]:
                continue
            if dest.is_relative_to(root):
                broken.append(f"{rel.as_posix()} links `{target}#{frag}`: no such heading; fix the link to the heading's current title")
            else:
                outside.append(f"{rel.as_posix()} links `{target}#{frag}`: no such heading in another project's file; check that "
                               "project's recent edits (a retitled heading), then fix the link here")
    return checked, broken, outside


def main(argv: list[str] | None = None) -> int:
    """Command line: list broken anchors, failing with `--check`.

    Args:
        argv: arguments (default: sys.argv).

    Returns:
        1 with `--check` and a broken anchor, else 0.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", type=Path, default=Path("."), help="the project to scan (default: the current folder)")
    ap.add_argument("--check", action="store_true", help="exit 1 when a link's heading does not exist")
    ap.add_argument("--skip", action="append", default=[], help="a path prefix to skip, relative to the root (repeatable)")
    ap.add_argument("--skip-name", action="append", default=[], help="a file-name glob to skip (repeatable)")
    ap.add_argument("--outside", choices=("fail", "warn"), default="fail", help="links into files outside the root: fail like others, or warn only")
    args = ap.parse_args(argv)
    checked, broken, outside = broken_links(args.project_root.resolve(), tuple(args.skip), tuple(args.skip_name))
    if args.outside == "fail":
        broken, outside = broken + outside, []
    for msg in outside:
        print(f"anchor (warning, not failing): {msg}", file=sys.stderr)
    for msg in broken:
        print(f"anchor: {msg}", file=sys.stderr)
    if broken:
        print(f"anchor links: {len(broken)} broken of {checked}", file=sys.stderr)
        return 1 if args.check else 0
    print(f"OK — anchor links: {checked} checked" + (f", {len(outside)} into other projects warned" if outside else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
