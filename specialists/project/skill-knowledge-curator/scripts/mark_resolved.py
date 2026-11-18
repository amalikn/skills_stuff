#!/usr/bin/env python3
"""Mark decided conflicts on authored pages: append `Resolved <date>: `<dr-id>` (<summary>).` to their conflict rows, list items and `### cf-` sections.

After the operator decides conflicts, every page that still cites them as open must say so. This handles the three mechanical places: a table row
whose first cell names the conflict, a list item that names it anywhere in its block, and a `### cf-...` section, whose `Status: open` paragraph is
replaced or which gets the note appended. Prose sentences that call a conflict open still need a hand edit; `--report` lists them. Deferred decisions
are written `Deferred <date>`. Found in Continuum (2026-11-18): 41 decisions over 44 pages; the ad-hoc first version missed five list items whose id
sat past column 60.

Safety: plan by default (counts per page); `--apply` writes. Idempotent: a line or section already carrying the note's date is left alone. Lines it
lengthens past --width are wrapped (list items with a two-space continuation); tables are never wrapped.

Run: python scripts/mark_resolved.py --project <p> --summaries s.json --pages 'docs/architecture/**/*.md' [--date YYYY-MM-DD] [--report] [--apply]
(or `just mark-resolved ...`). s.json: {"cf-...": "short outcome"}. Standard library only. Exit 0 ok, 1 refused input.
"""

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

CF = re.compile(r"cf-[0-9a-f]{10}")
OPEN_WORDS = re.compile(r"\b(stays? open|still open|remains open|is open|OPEN)\b")


def latest_decisions(project: Path) -> dict[str, tuple[str, str, str]]:
  """Read the last decision per conflict.

  Args:
    project: the curated project.

  Returns:
    conflict id -> (decision id, action, decided date YYYY-MM-DD).
  """
  out = {}
  for line in (project / ".kc/decisions.jsonl").read_text().splitlines():
    if line.strip():
      d = json.loads(line)
      out[d["conflict_id"]] = (d["decision_id"], d["action"], d["decided_at"][:10])
  return out


def note(cf: str, dec: dict, summ: dict, date: str | None) -> str:
  """Format the resolution note for one conflict.

  Args:
    cf: conflict id.
    dec: latest decisions.
    summ: conflict id -> summary.
    date: override date, or None for the decision's own date.

  Returns:
    The note sentence.
  """
  dr, action, decided = dec[cf]
  return f"{'Deferred' if action == 'DEFER' else 'Resolved'} {date or decided}: `{dr}` ({summ[cf]})."


def mark_section(sec: list[str], cf: str, ctx: dict) -> bool:
  """Replace a conflict section's `Status: open` paragraph with the note, or append the note.

  Args:
    sec: the section's lines after its heading (edited in place).
    cf: conflict id.
    ctx: dec, summ, date and width.

  Returns:
    True when the section was changed.
  """
  dec, date = ctx["dec"], ctx["date"]
  if any((date or dec[cf][2]) in s and dec[cf][0] in s for s in sec):
    return False
  wrapped = textwrap.wrap(note(cf, dec, ctx["summ"], date), ctx["width"], break_on_hyphens=False, break_long_words=False)
  k = next((n for n, s in enumerate(sec) if s.startswith("Status: open")), None)
  if k is not None:
    e = k + 1
    while e < len(sec) and sec[e].strip():
      e += 1
    sec[k:e] = wrapped
  else:
    while sec and not sec[-1].strip():
      sec.pop()
    sec += ["", *wrapped, ""]
  return True


def mark_row(line: str, ctx: dict) -> str | None:
  """Append notes to a table row whose first cell names decided conflicts.

  Args:
    line: the row.
    ctx: dec, summ, date and width.

  Returns:
    The new row, or None when nothing changes.
  """
  dec, summ = ctx["dec"], ctx["summ"]
  hits = [c for c in CF.findall(line.split("|")[1] if line.count("|") > 1 else "") if c in summ and dec[c][0] not in line]
  if not hits:
    return None
  return line.rstrip().rstrip("|").rstrip() + " " + " ".join(note(c, dec, summ, ctx["date"]) for c in hits) + " |"


def mark_item(lines: list[str], i: int, ctx: dict) -> tuple[list[str] | None, int]:
  """Append notes to a list item that cites decided conflicts anywhere in its block.

  Args:
    lines: the page's lines.
    i: index of the item's first line.
    ctx: dec, summ, date and width.

  Returns:
    (new wrapped lines or None when unchanged, index after the item's block).
  """
  dec, summ = ctx["dec"], ctx["summ"]
  j = i + 1
  while j < len(lines) and lines[j].startswith("  ") and not lines[j].lstrip().startswith(("- ", "* ")) and lines[j].strip():
    j += 1
  block = " ".join([lines[i]] + [x.strip() for x in lines[i + 1 : j]])
  hits = [c for c in dict.fromkeys(CF.findall(block)) if c in summ and dec[c][0] not in block]
  if not hits:
    return None, j
  block += " " + " ".join(note(c, dec, summ, ctx["date"]) for c in hits)
  return textwrap.wrap(block, ctx["width"], subsequent_indent="  ", break_on_hyphens=False, break_long_words=False), j


def mark_text(text: str, dec: dict, summ: dict, date: str | None, width: int) -> tuple[str, dict]:
  """Mark one page.

  Args:
    text: the page.
    dec: latest decisions.
    summ: conflict id -> summary (only these are marked).
    date: override date or None.
    width: wrap width for lengthened prose lines.

  Returns:
    (new text, counts by kind).
  """
  ctx = {"dec": dec, "summ": summ, "date": date, "width": width}
  lines, out, i = text.split("\n"), [], 0
  counts = {"row": 0, "item": 0, "section": 0}
  while i < len(lines):
    line = lines[i]
    m = CF.match(line[4:]) if line.startswith("### cf-") else None
    if m and m.group() in summ:
      j = i + 1
      while j < len(lines) and not lines[j].startswith("#"):
        j += 1
      sec = lines[i + 1 : j]
      counts["section"] += mark_section(sec, m.group(), ctx)
      out += [line, *sec]
      i = j
      continue
    if line.startswith("|") and (row := mark_row(line, ctx)) is not None:
      line, counts["row"] = row, counts["row"] + 1
    elif line.startswith("- "):
      new, j = mark_item(lines, i, ctx)
      if new is not None:
        out += new
        counts["item"] += 1
        i = j
        continue
    out.append(line)
    i += 1
  return "\n".join(out), counts


def open_prose(text: str, summ: dict) -> list[str]:
  """List prose lines that still call a marked conflict open.

  Args:
    text: a page.
    summ: conflict id -> summary.

  Returns:
    Line excerpts that need a hand edit.
  """
  return [f"L{n}: {line.strip()[:140]}" for n, line in enumerate(text.split("\n"), 1) if OPEN_WORDS.search(line) and set(CF.findall(line)) & set(summ)]


def main(argv: list[str] | None = None) -> int:
  """Plan, apply or report.

  Args:
    argv: command-line arguments; None uses sys.argv.

  Returns:
    0 ok; 1 when a summary names a conflict with no decision.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project", required=True, type=Path)
  ap.add_argument("--summaries", required=True, type=Path)
  ap.add_argument("--pages", required=True, help="glob relative to the project")
  ap.add_argument("--date", help="YYYY-MM-DD; default: each decision's own date")
  ap.add_argument("--width", type=int, default=200)
  ap.add_argument("--report", action="store_true", help="also list prose lines still calling a marked conflict open")
  ap.add_argument("--apply", action="store_true")
  a = ap.parse_args(argv)
  dec, summ = latest_decisions(a.project), json.loads(a.summaries.read_text())
  missing = [c for c in summ if c not in dec]
  if missing:
    print(f"refused: no decision for {', '.join(missing)}", file=sys.stderr)
    return 1
  total = {"row": 0, "item": 0, "section": 0}
  for page in sorted(a.project.glob(a.pages)):
    text = page.read_text()
    new, counts = mark_text(text, dec, summ, a.date, a.width)
    if any(counts.values()):
      print(f"{page.relative_to(a.project)}: {counts}")
      total = {k: total[k] + counts[k] for k in total}
      if a.apply:
        page.write_text(new)
    if a.report:
      for hit in open_prose(new, summ):
        print(f"  prose {page.relative_to(a.project)} {hit}")
  print(f"{'applied' if a.apply else 'plan'}: {total}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
