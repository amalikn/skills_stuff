#!/usr/bin/env python3
"""Give a working-state record (SCRATCHPAD.md) the headings rotation needs, without changing a line of its text. Stdlib only.

Why (operator, 2026-10-10): rotation moves dated bullets and dated `###` subsections, but many SCRATCHPADs keep their history as bold-lead
paragraphs ("**Newest thread (2026-10-07, 13:36) — ...**", "**Stage 6 first pass, 2026-09-16 ~00:10**", "> **2026-09-03 — verdict ...**") or as a
block of dated header comments ("<!-- KEEP: updated 2026-05-04 — ... -->"). Rotation saw them as loose prose and never moved them, so the file stayed
over budget; ansible-wifi needed a hand-written script. This adds only heading lines:
1. Above each dated bold-lead paragraph: `### <date> — <lead>`. A lead with only a time ("(~3:50p)") takes the date of the dated lead above it.
2. Above an undated bold-lead paragraph that follows a dated one: `### <lead>`, undated, so rotation leaves that standing fact in place instead of
   carrying it away inside the previous dated entry.
3. Over a block of five or more dated `<!--` comment lines before the first section: `## Update log <first> to <last> (header comments)`, and
   `Update log=0` in the front matter's `Keep:` so the whole block rotates.
Contents, Open items, Key anchors and Memory pointers are left alone, as are sections whose heading is already dated. Every original line must still be
present, in order, or nothing is written.

Usage:
    python scripts/normalise_records.py --project-root . SCRATCHPAD.md            # plan: what headings it would add
    python scripts/normalise_records.py --project-root . --apply SCRATCHPAD.md    # write them
Exit: 0 planned, applied or nothing to do; 1 on a refusal; 2 on bad arguments.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

_spec = importlib.util.spec_from_file_location("rotate_records", pathlib.Path(__file__).resolve().parent / "rotate_records.py")
rr = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("rotate_records", rr)
_spec.loader.exec_module(rr)

LEFT_ALONE = re.compile(r"^## (Contents|Open items|Key anchors|Memory pointers)", re.I)
BLOCK_START = ("- ", "* ", "#", "|", "```", "<!--", "---")


def lead_text(line: str) -> str:
    """The bold lead of a paragraph's first line, or '' when the paragraph does not open in bold.

    Args:
        line: the paragraph's first line.

    Returns:
        The text inside the opening `**...**` (to the end of the line when the bold runs on), without a blockquote marker.
    """
    body = line[2:] if line.startswith("> ") else line
    if not body.startswith("**"):
        return ""
    end = body.find("**", 2)
    return body[2:end] if end > 2 else body[2:]


def lead_date(lead: str) -> str:
    """A date in a bold lead: a stamp, or a written date returned as `YYYY-MM-DD`.

    Args:
        lead: the bold lead text.

    Returns:
        The date, or ''.
    """
    return rr.heading_stamp(lead)


def title(lead: str, words: int = 9) -> str:
    """A short heading title from a lead: markdown marks, dates, times and `KEEP` removed, at most `words` words.

    Args:
        lead: the bold lead text.
        words: how many words to keep.

    Returns:
        The title.
    """
    t = rr.TIME.sub("", rr.LONG_DATE.sub("", rr.STAMP.sub("", lead.replace("`KEEP`", "").replace("`", ""))))
    t = re.sub(r"\(\s*[,;:]?\s*\)|^[\s(),;:—–-]+|[\s(),;:—–-]+$", "", re.sub(r"\s+", " ", t)).strip()
    if ")" in t and t.count(")") > t.count("("):
        t = t[t.index(")") + 1:]  # the tail of "(2026-08-29, evening)" once the date is gone
    if "(" in t and t.count("(") > t.count(")"):
        t = t[:t.rindex("(")]
    t = re.sub(r"^[\s,;:—–-]+|[\s,;:—–-]+$", "", t)
    parts = t.split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


def normalise(text: str) -> tuple[str, list[str]]:
    """Insert the headings rotation needs.

    Args:
        text: the record's text.

    Returns:
        (the new text, one line per heading added).
    """
    lines = text.split("\n")
    out: list[str] = []
    added: list[str] = []
    fm_end = lines.index("---", 1) if lines and lines[0] == "---" and "---" in lines[1:] else -1
    first_section = next((i for i, l in enumerate(lines) if l.startswith("## ") and l.strip() != "## Contents"), len(lines))
    comments = [i for i in range(fm_end + 1, first_section) if lines[i].lstrip().startswith("<!--") and rr.first_stamp(lines[i])]
    log_at = comments[0] if len(comments) >= 5 else -1
    section, last_date, dated_seen, prev = "", "", False, ""
    for i, line in enumerate(lines):
        if i == log_at:
            dates = sorted(rr.first_stamp(lines[k]) for k in comments)
            head = f"## Update log {dates[0]} to {dates[-1]} (header comments)"
            out += [head, ""]
            added.append(head)
        if line.startswith("## "):
            section, last_date, dated_seen = line, "", False
        elif (section and not LEFT_ALONE.match(section) and not rr.heading_stamp(section) and line.strip()
              and prev.strip() == "" and not line.startswith(BLOCK_START) and not re.match(r"^\d+[.)] ", line)):
            lead = lead_text(line)
            above = next((x for x in reversed(out) if x.strip()), "")
            if lead and not above.startswith("### "):
                date = lead_date(lead)
                if not date and rr.TIME.search(line) and last_date:
                    date = last_date
                if date:
                    head = f"### {date} — {title(lead) or 'entry'}"
                    last_date, dated_seen = date, True
                    out += [head, ""]
                    added.append(head)
                elif dated_seen:
                    head = f"### {title(lead) or 'standing note'}"
                    out += [head, ""]
                    added.append(head)
        out.append(line)
        prev = line
    if log_at >= 0 and fm_end > 0:
        fm = out[:out.index("---", 1) + 1]
        keep = next((k for k, l in enumerate(fm) if l.startswith("Keep:")), None)
        if keep is None:
            out.insert(out.index("---", 1), "Keep: Update log=0")
        elif "Update log" not in fm[keep]:
            out[keep] = fm[keep] + ", Update log=0"
    return "\n".join(out), added


def main(argv: list[str] | None = None) -> int:
    """Plan or apply heading normalisation for one record.

    Args:
        argv: command-line arguments (default: sys.argv).

    Returns:
        The exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("record", nargs="?", default="SCRATCHPAD.md")
    args = ap.parse_args(argv)
    path = pathlib.Path(args.project_root) / args.record
    text = path.read_text()
    new, added = normalise(text)
    old_lines, new_lines = text.split("\n"), new.split("\n")
    it = iter(new_lines)
    if not all(any(o == n for n in it) for o in old_lines if not o.startswith("Keep:")):
        print(f"refused: {args.record}: an original line would change or move out of order")
        return 1
    print(f"{args.record}: {len(added)} heading(s) to add" + "".join(f"\n  + {a}" for a in added[:12]) + ("\n  ..." if len(added) > 12 else ""))
    if not added:
        return 0
    if not args.apply:
        print("plan only; add --apply to write")
        return 0
    path.write_text(new)
    print("written; only heading lines (and the Keep key) were added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
