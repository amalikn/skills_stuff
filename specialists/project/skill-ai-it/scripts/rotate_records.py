#!/usr/bin/env python3
"""Rotate a running record (CHANGELOG.md, SCRATCHPAD.md) into dated archive files so the live file stays within its budget. Stdlib plus git.

Why (operator, 2026-10-10): records an agent loads grew to thousands of lines (UNC: CHANGELOG 7,483, SCRATCHPAD 2,519); the standard is 200 lines
and 25 KB for any file loaded whole. Rotation must "not lose data", "not move things that should remain active", and give a way to consult the
rotated data only when needed. So:

- **Units.** A log (`Kind: log`, CHANGELOG) rotates whole dated `## <stamp>` entries. A working-state file (`Kind: state`, SCRATCHPAD) rotates
  dated top-level bullets and `###` subsections inside each `##` section, and whole `##` sections whose heading carries a stamp.
- **Never moved:** units with no date; the newest `--min-keep` units of each section (the whole log for CHANGELOG: 5; SCRATCHPAD: 3 per
  section); units younger than `--keep-days` (0 by default); units carrying the pin marker (`` `PIN` `` in backticks or `<!-- PIN -->`; a bare word such as a captive-portal PIN is content, not a pin); units in a pinned section (`Pinned sections:` key; SCRATCHPAD
  default `Open items`) unless they say done, closed, resolved or superseded; and, in a working-state file, units whose stamp a live governance
  file (AGENTS.md, AI_NAVIGATION.md, context-map.yaml, target-map.yaml, ROADMAP.md, ARCHITECTURE.md, README.md) still cites. A log stamp cited
  elsewhere stays reachable through `--show`, and tools that need the whole log read the archives too.
- **Open items are not history.** With an `Open items tracker:` key (UNC: `docs/trackers/open-items-<stamp>.md`), every unresolved
  open item beyond the newest 3 moves verbatim to that live tracker (review due in two weeks, indexed in its folder readme), and the
  working state keeps a pointer to it. Resolved items (`[x]`, done, closed) rotate to history like any entry.
- **Per-section counts.** `Keep: Next actions=1, Memory pointers=1, ...` sets how many newest entries a section keeps; dated `##`
  sections of one kind (nine "Residual risk <stamp>" sections) form one group and keep 1. Bullets and numbered items are units.
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
#: an explicit pin; a bare "PIN" substring matched content such as "portal/PIN-activation" and kept history (ansible-wifi, 2026-10-10)
PIN_MARK = re.compile(r"`PIN`|<!--\s*PIN\b")
LONG_DATE = re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+(20\d{2})\b")
MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
TIME = re.compile(r"~?\b\d{1,2}[:.]\d{2}\s*(?:[ap]\.?m?\.?\b)?(?:\s*[–-]\s*\d{1,2}[:.]\d{2}\s*(?:[ap]\.?m?\.?\b)?)?", re.I)
TRACKER_POINTER = "- Older open items are tracked in"
RESOLVED = re.compile(r"\b(done|closed|resolved|superseded|retired)\b|^- \[x\]|~~", re.I)
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
    to_tracker: bool = False
    start: int = -1
    blamed: dt.datetime | None = None

    @property
    def when(self) -> dt.datetime | None:
        """The unit's moment: from its stamp, else from git blame of its first line; None when neither is known."""
        m = STAMP.search(self.stamp)
        if not m:
            return self.blamed
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


def heading_stamp(line: str) -> str:
    """The date of a `##` or `###` heading: a stamp, or a written date such as "21 September 2026" returned as `YYYY-MM-DD`.

    Written dates count only in headings; in prose they are content (a status line saying "created 10 Jul 2026" is not an entry date).

    Args:
        line: the heading line.

    Returns:
        The stamp, or an empty string.
    """
    stamp = first_stamp(line)
    if stamp:
        return stamp
    m = LONG_DATE.search(line)
    return f"{m.group(3)}-{MONTHS[m.group(2)[:3]]:02d}-{int(m.group(1)):02d}" if m else ""


def lazy_continuation(line: str) -> bool:
    """Whether a line continues the list item above it without indentation (markdown "lazy" continuation).

    A wrapped item whose later lines start at column 0 was cut after its first line, leaving its tail behind as an orphan paragraph
    (ansible-wifi SCRATCHPAD, 2026-10-10).

    Args:
        line: the line after a non-blank line of the item.

    Returns:
        True when it is plain text, not a blank line, list marker, heading, table row, rule, fence or comment.
    """
    return bool(line.strip()) and not (line.startswith(("- ", "* ", "#", "|", "```", "<!--", "---", ">")) or re.match(r"^\d+[.)] ", line))


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
        stamp = heading_stamp(head)
        if kind == "log" or stamp:
            rec.blocks.append((head, [Unit(section=head, lines=[head] + body, stamp=stamp)]))
        else:
            # Units are top-level bullets. A `###` subheading (and the blank lines after it) travels with its first bullet, and a bullet with
            # no date of its own takes its subheading's, so dated session notes rotate while undated open items stay put.
            items: list[Unit | str] = []
            pending: list[str] = []
            sub_stamp = ""
            k = 0
            while k < len(body):
                line = body[k]
                if line.startswith("### "):
                    items.extend(pending)
                    nxt = next((x for x in body[k + 1:] if x.strip()), "")
                    if heading_stamp(line) and nxt and not (nxt.startswith(("- ", "### ")) or re.match(r"^\d+[.)] ", nxt)):
                        # A dated `###` subsection written as prose is one unit to the next `###`; as loose lines it never rotated
                        # (ansible-wifi's "Newest thread" paragraphs, 2026-10-10).
                        end = k + 1
                        while end < len(body) and not body[end].startswith("### "):
                            end += 1
                        items.append(Unit(section=head, lines=body[k:end], stamp=heading_stamp(line)))
                        pending, sub_stamp = [], ""
                        k = end
                        continue
                    pending, sub_stamp = [line], heading_stamp(line)
                    k += 1
                elif line.startswith("- ") or re.match(r"^\d+[.)] ", line):
                    end = k + 1
                    while end < len(body) and (body[end].startswith("  ") or (body[end] == "" and end + 1 < len(body) and body[end + 1].startswith("  "))
                                               or (body[end - 1] != "" and lazy_continuation(body[end]))):
                        end += 1
                    items.append(Unit(section=head, lines=pending + body[k:end], stamp=first_stamp(line) or sub_stamp))
                    pending = []
                    k = end
                elif pending and line == "":
                    pending.append(line)
                    k += 1
                else:
                    items.extend(pending)
                    pending = []
                    items.append(line)
                    k += 1
            items.extend(pending)
            rec.blocks.append((head, items))
        i = j
    return rec


def blame_dates(root: pathlib.Path, rel: str) -> dict[int, dt.datetime]:
    """When each line of a committed file was written, from git blame.

    Args:
        root: the project root.
        rel: the file, project-relative.

    Returns:
        0-based line index to author time; empty when the file is not in git. Uncommitted lines are absent (treated as new).
    """
    out = subprocess.run(["git", "-C", str(root), "blame", "--line-porcelain", "--", rel], capture_output=True, text=True)
    dates: dict[int, dt.datetime] = {}
    line_no = None
    for row in out.stdout.split("\n"):
        parts = row.split(" ")
        if len(parts) >= 3 and len(parts[0]) == 40 and parts[1].isdigit():
            line_no = int(parts[2]) - 1
        elif row.startswith("author-time ") and line_no is not None:
            dates[line_no] = dt.datetime.fromtimestamp(int(row.split(" ", 1)[1]))
        elif row.startswith("author ") and "Not Committed Yet" in row:
            line_no = None
    return dates


def date_undated(rec: Record, dates: dict[int, dt.datetime]) -> None:
    """Give units without a stamp the git date of their first line, so an old undated entry can rotate.

    Args:
        rec: the parsed record (units updated in place).
        dates: from blame_dates().
    """
    index = len(rec.preamble)
    for head, items in rec.blocks:
        whole = len(items) == 1 and isinstance(items[0], Unit) and items[0].lines[:1] == [head]
        if not whole:
            index += 1
        for it in items:
            if isinstance(it, Unit):
                if not STAMP.search(it.stamp):
                    first = next((i for i, l in enumerate(it.lines) if l.strip() and not l.startswith("### ")), 0)
                    it.blamed = dates.get(index + first)
                index += len(it.lines)
            else:
                index += 1


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


def group_key(kind: str, head: str) -> str:
    """The group a unit's newest-entry count applies to.

    Args:
        kind: `log` or `state`.
        head: the unit's `##` heading.

    Returns:
        `log` for a log; for a working-state file the heading, with dates and code marks removed when the heading is dated, so dated
        sections of one kind (nine "Residual risk — staleness audit <stamp>" sections) form one group instead of nine groups of one.
    """
    if kind == "log":
        return "log"
    if not heading_stamp(head):
        return head
    # times and their markers go too: "(staleness audit, 2026-09-14 ~1:35p)" and "(..., 2026-09-15 ~10:53a)" are one group (cambium-swap, 2026-10-10)
    key = TIME.sub("", LONG_DATE.sub("", STAMP.sub("", head)).replace("`KEEP`", ""))
    return re.sub(r"\s+", " ", re.sub(r"\(\s*[,;]?\s*\)|,\s*\)", ")", key)).strip(" #—-")


def choose(rec: Record, kind: str, now: dt.datetime, keep_days: int, min_keep: int, pinned: set[str], cited: set[str],
           budget: tuple[int, int], preview_len, section_keep: dict[str, int] | None = None, open_days: int | None = None) -> tuple[int, int]:
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
        section_keep: newest units to keep per group, by a substring of its heading (`Next actions=1`); others use min_keep, a group of
            dated sections uses 1.
        open_days: when set (a tracker is configured), unresolved open items beyond the newest of their section move to the open-items
            tracker, not the archive.

    Returns:
        The live (lines, bytes) after marking.
    """
    groups: dict[str, list[Unit]] = {}
    for head, items in rec.blocks:
        for it in items:
            if isinstance(it, Unit):
                groups.setdefault(group_key(kind, head), []).append(it)
    for key, units in groups.items():
        keep = next((n for k, n in (section_keep or {}).items() if k.lower() in key.lower()), None)
        if keep is None:
            keep = 1 if kind == "state" and key != units[0].section else min_keep
        dated = sorted((u for u in units if u.when), key=lambda u: u.when, reverse=True)
        tracked = open_days is not None and any(p in key for p in pinned)
        for u in dated[:keep]:
            # With a tracker, the newest open items stay in the working state and every other open item moves to the tracker.
            u.keep_reason = "open item (newest)" if tracked else "newest"
    candidates = []
    for units in groups.values():
        for u in units:
            text = "\n".join(u.lines)
            if u.keep_reason:
                continue
            if u.lines and u.lines[0].startswith(TRACKER_POINTER):
                u.keep_reason = "tracker pointer"  # never an open item itself: moving it is how duplicates piled up (skill-ai-it, 2026-10-10)
                continue
            open_item = any(p in u.section for p in pinned) and not RESOLVED.search(u.lines[0] if u.lines else "")
            if open_item and open_days is not None:
                u.moved = u.to_tracker = True  # still open: it moves to the live tracker, not to history
            elif not u.when:
                u.keep_reason = "undated"
            elif now - u.when < dt.timedelta(days=keep_days):
                u.keep_reason = "recent"
            elif PIN_MARK.search(text) or re.search(r"until resolved", text, re.I):
                u.keep_reason = "pinned"
            elif open_item:
                u.keep_reason = "open item"
            elif kind == "state" and u.stamp and u.stamp in cited:
                u.keep_reason = "cited by a live file"
            else:
                candidates.append(u)
    for u in sorted(candidates, key=lambda u: u.when):
        if u.moved:
            continue
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


def collapse_blanks(lines: list[str]) -> list[str]:
    """Collapse runs of blank lines left where units were removed.

    Args:
        lines: the live file's lines.

    Returns:
        The lines with no two blank lines in a row.
    """
    out: list[str] = []
    for line in lines:
        if line.strip() == "" and out and out[-1].strip() == "":
            continue
        out.append(line)
    return out


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


TOC_LINE = re.compile(r"^\s*[-*] \[.*\]\(#[^)]*\)\s*$|^<!-- toc")


def contents_span(lines: list[str]) -> tuple[int, int] | None:
    """Where a `## Contents` block sits: its heading and the contents-link lines under it, nothing else.

    Prose after the links is record content, not navigation (vocus-profitability, 2026-10-10: 424 lines of text under a Contents list
    were dropped when the block was taken to run to the next heading).

    Args:
        lines: a record's lines.

    Returns:
        (start, end) indices, end exclusive; None when there is no Contents heading.
    """
    if "## Contents" not in lines:
        return None
    start = lines.index("## Contents")
    end = start + 1
    while end < len(lines) and (lines[end].strip() == "" or TOC_LINE.match(lines[end])):
        end += 1
    while end > start + 1 and lines[end - 1].strip() == "":
        end -= 1
    return start, end


def without_contents(lines: list[str]) -> list[str]:
    """The lines without the Contents heading and its link lines.

    Args:
        lines: a record's lines.

    Returns:
        The lines with only the navigation removed.
    """
    span = contents_span(lines)
    return lines if span is None else lines[:span[0]] + lines[span[1]:]


def rebuild_contents(lines: list[str]) -> list[str]:
    """Regenerate the Contents links from the level-2 headings that remain, above the first entry.

    Args:
        lines: the live file's lines.

    Returns:
        The lines with the link list under `## Contents` replaced; unchanged when there is no Contents heading.
    """
    span = contents_span(lines)
    if span is None:
        return lines
    rest = lines[:span[0]] + lines[span[1]:]
    if rest[span[0]:span[0] + 1] == [""] and span[0] > 0 and rest[span[0] - 1] == "":
        del rest[span[0]]
    first = next((i for i, l in enumerate(rest) if l.startswith("## ")), len(rest))
    # A Contents list left below an entry (an entry inserted above it) goes back above the first entry; prose stays where it was.
    first = min(first, span[0])
    heads = [l[3:] for l in rest if l.startswith("## ")]
    return rest[:first] + ["## Contents", ""] + [f"- [{h}](#{slug(h)})" for h in heads] + [""] + rest[first:]


def content_lines(text: str) -> list[str]:
    """A record's lines that carry content: everything except the top front matter and the Contents navigation.

    Args:
        text: the whole file.

    Returns:
        The lines, in order.
    """
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        lines = lines[close + 1:]
    return without_contents(lines)


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


def archive_text(moved: list[Unit], title: str, live: str, stamp_now: str, now: dt.datetime, source_dir: str) -> str:
    """The archive file for the units leaving the live record: front matter, an index, then the units verbatim (links relinked).

    Args:
        moved: the units going to history.
        title: the record's title.
        live: the record's project-relative path.
        stamp_now: this run's stamp.
        now: this run's moment.
        source_dir: the record's folder, for relinking.

    Returns:
        The archive text.
    """
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
    by_section: dict[str, list[Unit]] = {}
    for u in moved:
        by_section.setdefault(u.section, []).append(u)
    for section, units in by_section.items():
        if units[0].lines[:1] != [section]:
            arc += [section, ""]
        for u in units:
            arc += relink(u.lines, source_dir, ARCHIVE_DIR)
        arc.append("")
    return "\n".join(arc) + "\n"


def write_archive(root: pathlib.Path, archive_rel: str, text: str, moved: list[Unit], live: str) -> None:
    """Write the archive and add it to docs/history/readme.md.

    Args:
        root: the project root.
        archive_rel: the archive's project-relative path.
        text: its content.
        moved: the units in it (for the index line's date range).
        live: the record it came from.
    """
    (root / ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
    (root / archive_rel).write_text(text, encoding="utf-8")
    dates = sorted(u.when for u in moved if u.when)
    index = root / ARCHIVE_DIR / "readme.md"
    line = f"- [{pathlib.Path(archive_rel).name}]({pathlib.Path(archive_rel).name}) {len(moved)} entries from `{live}`, {dates[0]:%Y-%m-%d} to {dates[-1]:%Y-%m-%d}."
    if index.is_file():
        index.write_text(index.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
    else:
        index.write_text("# History\n\nRecords rotated out of the live CHANGELOG and SCRATCHPAD to keep them within budget. Do not read these by default:"
                         " search with `rotate_records.py --find` (`just history`) or print one entry with `--show <stamp>`.\n\n" + line + "\n",
                         encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-N", archive_rel, f"{ARCHIVE_DIR}/readme.md"], check=False)


def write_tracker(path: pathlib.Path, lines: list[str], live: str, stamp_now: str, now: dt.datetime) -> None:
    """Append open items to the live open-items tracker, creating it with front matter the first time.

    The tracker is a living document, not history: its Review by date makes doc_freshness ask for a review, which is where an item is
    closed, decided or dropped.

    Args:
        path: the tracker file.
        lines: the open items, verbatim (links relinked for the tracker's folder).
        live: the record they came from.
        stamp_now: this run's stamp.
        now: this run's moment.
    """
    block = [f"## Moved from {live} on {stamp_now}", ""] + lines + [""]
    index = path.parent / "readme.md"
    if index.is_file() and path.name not in index.read_text(encoding="utf-8"):
        index.write_text(index.read_text(encoding="utf-8").rstrip("\n") + f"\n- [{path.name}]({path.name}) Open items moved out of `{live}`"
                         " (live tracker: review, close, decide or drop).\n", encoding="utf-8")
    if path.is_file():
        path.write_text(path.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + "\n".join(block) + "\n", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    review = (now + dt.timedelta(days=14)).strftime("%Y-%m-%d")
    head = ["---", "Title: Open items", "Category: living-tracker", "Status: current", f"Last reviewed: {now:%Y-%m-%d}", f"Review by: {review}",
            f"Summary: Open items older than 7 days, moved verbatim from {live} so the working state stays small. Review: close, decide or drop;",
            "  closed items are deleted here (git keeps them).", "---", "", "# Open items", "",
            f"Items still open after a week leave `{live}` for this file (skill-ai-it rotate_records.py). Mark one done with `[x]`, or delete it",
            "once closed and recorded in the CHANGELOG.", ""]
    path.write_text("\n".join(head + block) + "\n", encoding="utf-8")


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
    date_undated(rec, blame_dates(root, live))
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
        text = "\n".join(collapse_blanks(rebuild_contents(front_matter_update(rec.preamble, new_keys) + render(rec)[len(rec.preamble):])))
        return text.count("\n"), len(text.encode())

    section_keep = {k.strip(): int(v) for k, _, v in (p.partition("=") for p in head.get("keep", "").split(",")) if v.strip().isdigit()}
    tracker_rel = head.get("open items tracker", "").split(" ")[0].strip("`")
    after = choose(rec, kind, now, keep_days, min_keep, pinned, cited_stamps(root), (budget_lines, budget_bytes), preview,
                   section_keep=section_keep, open_days=7 if tracker_rel else None)
    units = [u for _, items in rec.blocks for u in items if isinstance(u, Unit)]
    to_archive = [u for u in units if u.moved and not u.to_tracker]
    to_tracker = [u for u in units if u.to_tracker]
    if to_tracker:
        # A pointer so the live file still says where its older open items are (undated, so it never rotates itself).
        pointer = f"{TRACKER_POINTER} [{pathlib.Path(tracker_rel).name}]({os.path.relpath(tracker_rel, os.path.dirname(live) or '.')})."
        for head_line, items in rec.blocks:
            # the pointer, once written, parses back as a bullet Unit, not a string: compare lines or it is added on every run
            present = any((x == pointer) or (isinstance(x, Unit) and pointer in x.lines) for x in items)
            if any(p in head_line for p in pinned) and not present:
                at = 1 if items[:1] == [""] else 0
                items.insert(at, pointer)
        after = preview()
    kept = Counter(u.keep_reason for u in units if not u.moved)
    print(f"{live}: {original.count(chr(10))} lines -> {after[0]} lines, {after[1] // 1024} KB; {len(to_archive)} unit(s) to {archive_rel}"
          + (f", {len(to_tracker)} open item(s) to {tracker_rel}" if to_tracker else ""))
    print("  kept: " + ", ".join(f"{n} {r or 'within budget'}" for r, n in kept.most_common()))
    if after[0] > budget_lines or after[1] > budget_bytes:
        print(f"  note: still over {budget_lines} lines / {budget_bytes // 1024} KB because of kept units; review them, move durable reference sections out with move_sections.py, or raise Budget")
    if not to_archive and not to_tracker:
        return 0
    source_dir = os.path.dirname(live)
    arc_text = archive_text(to_archive, title, live, stamp_now, now, source_dir) if to_archive else ""
    tracker_dir = os.path.dirname(tracker_rel)
    tracker_lines = [l for u in to_tracker for l in relink(u.lines, source_dir, tracker_dir)]
    live_text = "\n".join(collapse_blanks(rebuild_contents(front_matter_update(rec.preamble, new_keys) + render(rec)[len(rec.preamble):])))
    # Verify the whole file: every content line (all but front matter and Contents links) is still live, archived or in the tracker.
    lost = Counter(l for l in content_lines(original) if l.strip()) - Counter(l for l in content_lines(live_text) if l.strip())
    found = Counter(l for l in arc_text.split("\n") if l.strip()) + Counter(l for l in tracker_lines if l.strip())
    missing = [l for l in lost.elements() if found[relink([l], source_dir, ARCHIVE_DIR)[0]] < 1 and found[relink([l], source_dir, tracker_dir)[0]] < 1]
    if missing:
        print(f"refused: {len(missing)} removed line(s) not found in the archive or tracker; nothing written", file=sys.stderr)
        for line in missing[:3]:
            print(f"  missing: {line[:150]!r}", file=sys.stderr)
        return 1
    if not args.apply:
        print("plan only; add --apply to rotate")
        return 0
    path.write_text(live_text if live_text.endswith("\n") else live_text + "\n", encoding="utf-8")
    if to_tracker:
        write_tracker(root / tracker_rel, tracker_lines, live, stamp_now, now)
        subprocess.run(["git", "-C", str(root), "add", "-N", tracker_rel], check=False)
    if to_archive:
        write_archive(root, archive_rel, arc_text, to_archive, live)
    print(f"rotated: {live} now {after[0]} lines" + (f"; archive {archive_rel}" if to_archive else "") + (f"; tracker {tracker_rel}" if to_tracker else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
