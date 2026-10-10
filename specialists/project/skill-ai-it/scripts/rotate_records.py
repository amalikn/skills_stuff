#!/usr/bin/env python3
"""Rotate a running record (CHANGELOG.md, SCRATCHPAD.md) into dated archive files so the live file stays within its budget. Stdlib plus git.

Why (operator, 2026-10-10): records an agent loads grew to thousands of lines (UNC: CHANGELOG 7,483, SCRATCHPAD 2,519); the standard is 200 lines
and 25 KB for any file loaded whole. Rotation must "not lose data", "not move things that should remain active", and give a way to consult the
rotated data only when needed. So:

- **Units.** A log (`Kind: log`, CHANGELOG) rotates whole dated `## <stamp>` entries. A working-state file (`Kind: state`, SCRATCHPAD) rotates
  dated top-level bullets and `###` subsections inside each `##` section, and whole `##` sections whose heading carries a stamp.
- **Never moved:** units with no date; the newest `--min-keep` units of each section (the whole log for CHANGELOG: 5; SCRATCHPAD: 3 per
  section); units younger than `--keep-days` (0 by default); units containing `PIN`; units in a pinned section (`Pinned sections:` key; SCRATCHPAD
  default `Open items`) unless they say done, closed, resolved or superseded; and, in a working-state file, units whose stamp a live governance
  file (AGENTS.md, AI_NAVIGATION.md, context-map.yaml, target-map.yaml, ROADMAP.md, ARCHITECTURE.md, README.md) still cites. A log stamp cited
  elsewhere stays reachable through `--show`, and tools that need the whole log read the archives too.
- **Oldest first** until the file fits `Budget` (default 200 lines, 25 KB); it reports when protected units keep it over.
- **No loss.** Units move verbatim except relative markdown links, rewritten for the archive's folder; before writing, every removed line must be
  found in the archive or the run stops. Git keeps the rest.
- **Recall on need.** Each archive opens with an index (stamp, section, first line); `--find TERM` searches the archives and `--show STAMP` prints one
  unit, so an agent reads old entries only when a live entry cites one or the history is the question.

The archive is `docs/history/<file>-<stamp>.md` (front matter `Status: archived`, indexed in `docs/history/readme.md`); the live file's front matter
records `Archive`, `Last rotated` and `Budget`. Without `--apply` it prints the plan.

Usage:
    python scripts/rotate_records.py --project-root . CHANGELOG.md                 # plan
    python scripts/rotate_records.py --project-root . --apply SCRATCHPAD.md        # rotate
    python scripts/rotate_records.py --project-root . --find "OpenWISP token" CHANGELOG.md
    python scripts/rotate_records.py --project-root . --show 20260927_2027 CHANGELOG.md
Exit: 0 planned, rotated or found; 1 when verification fails or nothing matches; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field

_spec = importlib.util.spec_from_file_location("file_headers", pathlib.Path(__file__).resolve().parent / "file_headers.py")
file_headers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(file_headers)

STAMP = re.compile(r"(20\d{2})(\d{2})(\d{2})_(\d{4})|(20\d{2})-(\d{2})-(\d{2})")
LIVE_SURFACES = ("AGENTS.md", "AI_NAVIGATION.md", "context-map.yaml", "target-map.yaml", "ROADMAP.md", "ARCHITECTURE.md", "README.md")
RESOLVED = re.compile(r"\b(done|closed|resolved|superseded|retired)\b", re.I)
ARCHIVE_DIR = "docs/history"
#: Measured 2026-10-10 on UNC (about 30 log entries a day): age protects too much in an active project, so the newest units are kept by
#: count and age is opt-in (`--keep-days`). A SCRATCHPAD section's newest entries supersede its older ones.
DEFAULTS = {"log": {"keep_days": 0, "min_keep": 5}, "state": {"keep_days": 0, "min_keep": 3}}


@dataclass
class Unit:
    """One rotatable piece of a record.

    Args:
        section: the `##` heading it sits under (the unit's own heading for a log entry or a dated section).
        lines: its text lines, verbatim.
        stamp: its date stamp as written (`YYYYMMDD_hhmm` or `YYYY-MM-DD`), or empty.
    """

    section: str
    lines: list[str]
    stamp: str = ""
    keep_reason: str = ""
    moved: bool = False

    @property
    def when(self) -> dt.datetime | None:
        """The unit's moment, from its stamp; None when undated."""
        m = STAMP.search(self.stamp)
        if not m:
            return None
        if m.group(1):
            return dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)[:2]), int(m.group(4)[2:]))
        return dt.datetime(int(m.group(5)), int(m.group(6)), int(m.group(7)))


@dataclass
class Record:
    """A parsed record: its preamble (front matter, title, contents) and its units in file order."""

    preamble: list[str]
    blocks: list[tuple[str, list[Unit | str]]] = field(default_factory=list)


def first_stamp(line: str) -> str:
    """The first date stamp on a line.

    Args:
        line: a heading or a bullet's first line.

    Returns:
        The stamp as written, or an empty string.
    """
    m = STAMP.search(line)
    return m.group(0) if m else ""


def parse(text: str, kind: str) -> Record:
    """Split a record into preamble, sections and units.

    Args:
        text: the file's content.
        kind: `log` or `state`.

    Returns:
        The parsed record; joining it back gives the original text.
    """
    lines = text.split("\n")
    first = next((i for i, l in enumerate(lines) if l.startswith("## ") and l.strip() != "## Contents"), len(lines))
    rec = Record(preamble=lines[:first])
    i = first
    while i < len(lines):
        head = lines[i]
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            j += 1
        body = lines[i + 1:j]
        stamp = first_stamp(head)
        if kind == "log" or stamp:
            rec.blocks.append((head, [Unit(section=head, lines=[head] + body, stamp=stamp)]))
        else:
            items: list[Unit | str] = []
            k = 0
            while k < len(body):
                line = body[k]
                if line.startswith("- ") or line.startswith("### "):
                    end = k + 1
                    if line.startswith("### "):
                        while end < len(body) and not body[end].startswith("### "):
                            end += 1
                    else:
                        while end < len(body) and (body[end].startswith("  ") or (body[end] == "" and end + 1 < len(body) and body[end + 1].startswith("  "))):
                            end += 1
                    items.append(Unit(section=head, lines=body[k:end], stamp=first_stamp(line)))
                    k = end
                else:
                    items.append(line)
                    k += 1
            rec.blocks.append((head, items))
        i = j
    return rec


def render(rec: Record, moved_only: bool = False) -> list[str]:
    """Lines of the record, without the moved units (or only them).

    Args:
        rec: the parsed record.
        moved_only: True for the moved units' lines only.

    Returns:
        The lines.
    """
    out: list[str] = [] if moved_only else list(rec.preamble)
    for head, items in rec.blocks:
        whole = len(items) == 1 and isinstance(items[0], Unit) and items[0].lines[:1] == [head]
        if whole:
            u = items[0]
            if u.moved == moved_only:
                out += u.lines
            continue
        if not moved_only:
            out.append(head)
        for it in items:
            if isinstance(it, Unit):
                if it.moved == moved_only:
                    out += it.lines
            elif not moved_only:
                out.append(it)
    return out


def cited_stamps(root: pathlib.Path) -> set[str]:
    """Stamps the live governance files cite, so the units they point at stay live.

    Args:
        root: the project root.

    Returns:
        Every `YYYYMMDD_hhmm` stamp found in the live surfaces.
    """
    found: set[str] = set()
    for name in LIVE_SURFACES:
        p = root / name
        if p.is_file():
            found |= set(re.findall(r"20\d{6}_\d{4}", p.read_text(encoding="utf-8", errors="ignore")))
    return found


def choose(rec: Record, kind: str, now: dt.datetime, keep_days: int, min_keep: int, pinned: set[str], cited: set[str],
           budget: tuple[int, int], preview_len) -> tuple[int, int]:
    """Mark the units to move, oldest first, until the live file fits its budget.

    Args:
        rec: the parsed record (units are marked in place).
        kind: `log` or `state`.
        now: the moment ages are measured from.
        keep_days: units younger than this stay.
        min_keep: the newest units of each section (of the whole log, for `log`) that stay.
        pinned: section headings whose unresolved units never move.
        cited: stamps live files cite.
        budget: (max lines, max bytes).
        preview_len: a function giving (lines, bytes) of the live file as currently marked.

    Returns:
        The live (lines, bytes) after marking.
    """
    groups: dict[str, list[Unit]] = {}
    for head, items in rec.blocks:
        for it in items:
            if isinstance(it, Unit):
                groups.setdefault("log" if kind == "log" else head, []).append(it)
    for units in groups.values():
        dated = sorted((u for u in units if u.when), key=lambda u: u.when, reverse=True)
        for u in dated[:min_keep]:
            u.keep_reason = "newest"
    candidates = []
    for units in groups.values():
        for u in units:
            text = "\n".join(u.lines)
            if u.keep_reason:
                continue
            if not u.when:
                u.keep_reason = "undated"
            elif now - u.when < dt.timedelta(days=keep_days):
                u.keep_reason = "recent"
            elif "PIN" in text or re.search(r"until resolved", text, re.I):
                u.keep_reason = "pinned"
            elif any(p in u.section for p in pinned) and not RESOLVED.search(u.lines[0] if u.lines else ""):
                u.keep_reason = "open item"
            elif kind == "state" and u.stamp and u.stamp in cited:
                u.keep_reason = "cited by a live file"
            else:
                candidates.append(u)
    for u in sorted(candidates, key=lambda u: u.when):
        size = preview_len()
        if size[0] <= budget[0] and size[1] <= budget[1]:
            break
        u.moved = True
    return preview_len()


def relink(lines: list[str], source_dir: str, archive_dir: str) -> list[str]:
    """Rewrite relative markdown link targets so they resolve from the archive's folder.

    Args:
        lines: unit lines.
        source_dir: the live file's folder, project-relative ("" for the root).
        archive_dir: the archive's folder, project-relative.

    Returns:
        The lines with `](relative)` targets recomputed; absolute, URL and anchor-only targets unchanged.
    """
    def fix(m: re.Match) -> str:
        """One markdown link target, recomputed from the archive's folder.

        Args:
            m: the match of `](target)`.

        Returns:
            The link with its relative target rewritten, or unchanged.
        """
        target = m.group(1)
        if re.match(r"^(https?:|mailto:|/|#)", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        new = os.path.relpath(os.path.normpath(os.path.join(source_dir, path)), archive_dir)
        return f"]({new}{'#' + anchor if anchor else ''})"
    return [re.sub(r"\]\(([^)\s]+)\)", fix, l) for l in lines]


def front_matter_update(preamble: list[str], keys: dict[str, str]) -> list[str]:
    """Set keys in a fenced front matter, adding the fence when the file has none.

    Args:
        preamble: the record's lines before its first entry.
        keys: header keys to set (in display case).

    Returns:
        The preamble with the keys set.
    """
    lines = list(preamble)
    if not lines or lines[0].strip() != "---":
        lines = ["---"] + [f"{k}: {v}" for k, v in keys.items()] + ["---", ""] + lines
        return lines
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    for k, v in keys.items():
        idx = next((i for i in range(1, end) if lines[i].startswith(f"{k}:")), None)
        if idx is None:
            lines.insert(end, f"{k}: {v}")
            end += 1
        else:
            lines[idx] = f"{k}: {v}"
    return lines


def slug(heading: str) -> str:
    """The GitHub/VS Code anchor of a heading.

    Args:
        heading: the heading text without the leading hashes.

    Returns:
        The anchor: lower case, punctuation dropped, spaces as hyphens.
    """
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading.strip().lower()))


def rebuild_contents(lines: list[str]) -> list[str]:
    """Regenerate a `## Contents` list from the level-2 headings that remain.

    Args:
        lines: the live file's lines.

    Returns:
        The lines with the bullet list under `## Contents` replaced; unchanged when there is no Contents heading.
    """
    try:
        start = lines.index("## Contents")
    except ValueError:
        return lines
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    heads = [l[3:] for l in lines[end:] if l.startswith("## ")]
    block = ["## Contents", ""] + [f"- [{h}](#{slug(h)})" for h in heads] + [""]
    return lines[:start] + block + lines[end:]


def archives_of(root: pathlib.Path, live: str) -> list[pathlib.Path]:
    """The archive files a record has rotated into, oldest first.

    Args:
        root: the project root.
        live: the record's project-relative path.

    Returns:
        Paths under docs/history named after the record.
    """
    stem = pathlib.Path(live).stem.lower()
    return sorted((root / ARCHIVE_DIR).glob(f"{stem}-*.md"))


def find(root: pathlib.Path, live: str, term: str | None, stamp: str | None) -> int:
    """Search a record's archives, or print one archived unit.

    Args:
        root: the project root.
        live: the record's project-relative path.
        term: text to search for (case-insensitive), or None.
        stamp: a unit's stamp to print in full, or None.

    Returns:
        0 when something matched, 1 otherwise.
    """
    hits = 0
    kind = "log" if pathlib.Path(live).name.upper().startswith("CHANGELOG") else "state"
    for arc in archives_of(root, live):
        rec = parse(arc.read_text(encoding="utf-8"), kind)
        for _, items in rec.blocks:
            for u in (it for it in items if isinstance(it, Unit)):
                text = "\n".join(u.lines)
                if stamp and u.stamp == stamp:
                    print(f"# {arc.relative_to(root)}\n{text}")
                    hits += 1
                elif term and term.lower() in text.lower():
                    print(f"{arc.relative_to(root)}  {u.stamp:<14} {u.lines[0][:140]}")
                    hits += 1
    if not hits:
        print("no match in the archives")
    return 0 if hits else 1


def main(argv: list[str] | None = None) -> int:
    """Plan or apply a rotation, or search the archives.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        The exit code (see the module docstring).
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("record", help="project-relative record: CHANGELOG.md or SCRATCHPAD.md")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--kind", choices=("log", "state"), help="default: from the Kind key, else log for CHANGELOG and state otherwise")
    ap.add_argument("--keep-days", type=int)
    ap.add_argument("--min-keep", type=int)
    ap.add_argument("--find", metavar="TERM")
    ap.add_argument("--show", metavar="STAMP")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    live = os.path.normpath(args.record)
    path = root / live
    if not path.is_file():
        print(f"no such record: {live}", file=sys.stderr)
        return 2
    if args.find or args.show:
        return find(root, live, args.find, args.show)
    head = file_headers.read_header(path)
    kind = args.kind or head.get("kind") or ("log" if path.name.upper().startswith("CHANGELOG") else "state")
    keep_days = args.keep_days if args.keep_days is not None else DEFAULTS[kind]["keep_days"]
    min_keep = args.min_keep if args.min_keep is not None else DEFAULTS[kind]["min_keep"]
    pinned = {p.strip() for p in head.get("pinned sections", "Open items" if kind == "state" else "").split(",") if p.strip()}
    budget_lines, budget_bytes = 200, 25 * 1024
    m = re.search(r"(\d+)\s*lines", head.get("budget", ""))
    budget_lines = int(m.group(1)) if m else budget_lines
    m = re.search(r"(\d+)\s*KB", head.get("budget", ""), re.I)
    budget_bytes = int(m.group(1)) * 1024 if m else budget_bytes
    original = path.read_text(encoding="utf-8")
    rec = parse(original, kind)
    assert "\n".join(render(rec)) == original, "parser did not round-trip the file; refusing to rotate"
    now = dt.datetime.now()
    stamp_now = now.strftime("%Y%m%d_%H%M")
    archive_rel = f"{ARCHIVE_DIR}/{path.stem.lower()}-{stamp_now}.md"
    title = path.stem.title() if path.stem.isupper() else path.stem
    new_keys = {} if head.get("title") else {
        "Title": path.stem.title() if path.stem.isupper() else path.stem,
        "Category": "change-log" if kind == "log" else "working-state",
        "Status": "current",
        "Summary": ("Newest entries only; older ones rotate to docs/history (search with --find, print with --show)." if kind == "log" else
                    "Current working state, newest first per section; superseded entries rotate to docs/history (search with --find)."),
    }
    new_keys |= {"Kind": kind, "Budget": f"{budget_lines} lines, {budget_bytes // 1024} KB", "Archive": f"{ARCHIVE_DIR}/ (`--find`, `--show`)",
                "Last rotated": stamp_now}

    def preview() -> tuple[int, int]:
        """The live file's size as currently marked.

        Returns:
            (lines, bytes) of the live text with the new front matter.
        """
        text = "\n".join(front_matter_update(rec.preamble, new_keys) + render(rec)[len(rec.preamble):])
        return text.count("\n"), len(text.encode())

    after = choose(rec, kind, now, keep_days, min_keep, pinned, cited_stamps(root), (budget_lines, budget_bytes), preview)
    moved = [u for _, items in rec.blocks for u in items if isinstance(u, Unit) and u.moved]
    kept = Counter(u.keep_reason for _, items in rec.blocks for u in items if isinstance(u, Unit) and not u.moved)
    print(f"{live}: {original.count(chr(10))} lines -> {after[0]} lines, {after[1] // 1024} KB; {len(moved)} unit(s) to {archive_rel}")
    print("  kept: " + ", ".join(f"{n} {r or 'within budget'}" for r, n in kept.most_common()))
    if after[0] > budget_lines or after[1] > budget_bytes:
        print(f"  note: still over {budget_lines} lines / {budget_bytes // 1024} KB because of kept units; review them or raise Budget")
    if not moved:
        return 0
    removed = render(rec, moved_only=True)
    source_dir = os.path.dirname(live)
    by_section: dict[str, list[Unit]] = {}
    for u in moved:
        by_section.setdefault(u.section, []).append(u)
    dates = sorted(u.when for u in moved if u.when)
    arc = ["---", f"Title: {title} archive {stamp_now}", "Category: archive", "Status: archived", f"Source: {live}",
           f"Covers: {dates[0]:%Y-%m-%d %H:%M} to {dates[-1]:%Y-%m-%d %H:%M}", f"Last reviewed: {now:%Y-%m-%d}",
           f"Summary: {len(moved)} entries rotated out of {live} on {stamp_now} to keep it within its budget; verbatim except relative links."
           " Read the index first; open an entry only when a live record cites it or the history is the question.", "---", "",
           f"# {title} archive {stamp_now}", "", "## Index", "", "| Stamp | Section | First line |", "| --- | --- | --- |"]
    for u in sorted(moved, key=lambda u: u.when or dt.datetime.min):
        first = re.sub(r"\s+", " ", (u.lines[1] if u.lines[0] == u.section and len(u.lines) > 1 else u.lines[0])).replace("|", "/")[:110]
        arc.append(f"| {u.stamp} | {u.section.lstrip('# ').replace('|', '/')[:40]} | {first} |")
    arc.append("")
    for section, units in by_section.items():
        if units[0].lines[:1] != [section]:
            arc.append(section)
            arc.append("")
        for u in units:
            arc += relink(u.lines, source_dir, ARCHIVE_DIR)
        arc.append("")
    arc_text = "\n".join(arc) + "\n"
    live_text = "\n".join(rebuild_contents(front_matter_update(rec.preamble, new_keys) + render(rec)[len(rec.preamble):]))
    # Compare entry bodies only: the preamble (front matter, title, regenerated Contents) is navigation, not record content.
    body_before = original.split("\n")[len(rec.preamble):]
    live_lines = live_text.split("\n")
    body_after = live_lines[next((i for i, l in enumerate(live_lines) if l.startswith("## ") and l != "## Contents"), len(live_lines)):]
    lost = Counter(l for l in body_before if l.strip()) - Counter(l for l in body_after if l.strip())
    archived = Counter(l for l in relink(removed, source_dir, ARCHIVE_DIR) if l.strip())
    relinked = Counter(relink(list(lost.elements()), source_dir, ARCHIVE_DIR))
    if relinked - archived:
        print(f"refused: {sum((relinked - archived).values())} removed line(s) not found in the archive; nothing written", file=sys.stderr)
        return 1
    if not args.apply:
        print("plan only; add --apply to rotate")
        return 0
    (root / ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
    (root / archive_rel).write_text(arc_text, encoding="utf-8")
    path.write_text(live_text if live_text.endswith("\n") else live_text + "\n", encoding="utf-8")
    index = root / ARCHIVE_DIR / "readme.md"
    line = f"- [{pathlib.Path(archive_rel).name}]({pathlib.Path(archive_rel).name}) {len(moved)} entries from `{live}`, {dates[0]:%Y-%m-%d} to {dates[-1]:%Y-%m-%d}."
    if index.is_file():
        index.write_text(index.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
    else:
        index.write_text("# History\n\nRecords rotated out of the live CHANGELOG and SCRATCHPAD to keep them within budget. Do not read these by default:"
                         " search with `rotate_records.py --find` (`just history`) or print one entry with `--show <stamp>`.\n\n" + line + "\n",
                         encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-N", archive_rel, f"{ARCHIVE_DIR}/readme.md"], check=False)
    print(f"rotated: wrote {archive_rel}; {live} now {after[0]} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
