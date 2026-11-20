#!/usr/bin/env python3
"""commtracker/teams_docx.py — Convert a Microsoft Teams transcript export (.docx) into a Markdown transcript file.

Why (operator, 2026-11-20): Teams gives a meeting transcript as a .docx ("Download as .docx"); the tracker keeps transcripts as Markdown under
communications/transcripts/. The .docx lays out one paragraph per turn: the speaker's avatar, then "Name   m:ss", then one caption segment per line
break. Its first lines are the recording title (with the start as YYYYMMDD_HHMMSSUTC), the date in UTC, the duration and "started transcription".

The output follows SKILL.md (Transcript turn layout): front matter to complete, a header block, then `## Full transcript` with one block per turn,
`**Name (m:ss):**` and the caption lines directly under it. Consecutive paragraphs of one speaker join into one turn (the first timestamp is kept).
Wording is copied as exported, never corrected; misheard words are fixed later with apply_corrections.py when the operator asks. Avatars are skipped.

Run:
  python3 teams_docx.py <transcript.docx> [--tz Australia/Sydney]                  # preview: prints the Markdown, writes nothing
  python3 teams_docx.py <transcript.docx> --tz Australia/Sydney --out <file.md> --apply  # write the file

Safety: reads the .docx; writes one Markdown file only with --apply, and refuses to replace an existing file unless --force. No network.
Runtime: under 1 s for a one-hour meeting (measured 0.06 s on a 47-minute export, 2026-11-20).
Exit: 0 ok, 1 refused (file exists), 2 bad input (not a Teams transcript .docx).
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SPEAKER = re.compile(r"^(?P<name>\S.*?)\s{2,}(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)$")
START_UTC = re.compile(r"-(\d{8})_(\d{6})UTC-")
DURATION = re.compile(r"^\d+[hms](?:\s*\d+[ms])*$")


class InputError(Exception):
  """The file is not a Teams transcript .docx this script can read."""


@dataclass
class Turn:
  """One speaker turn: the name, the first timestamp and its caption lines."""

  name: str
  ts: str
  lines: list[str] = field(default_factory=list)


@dataclass
class Transcript:
  """The parsed export."""

  title: str
  start_utc: datetime | None
  duration: str
  turns: list[Turn]


def paragraphs(docx: Path) -> list[list[str]]:
  """Read the document's paragraphs as lists of segments, split at line breaks.

  Args:
    docx: the .docx file.

  Returns:
    One list per paragraph; each holds the text between line breaks, stripped, empty segments dropped.

  Raises:
    InputError: when the file is not a readable .docx.
  """
  try:
    with zipfile.ZipFile(docx) as z:
      root = ElementTree.fromstring(z.read("word/document.xml"))
  except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
    raise InputError(f"{docx}: not a readable .docx ({exc})") from exc
  out = []
  for p in root.iter(f"{W}p"):
    segs, cur = [], ""
    for el in p.iter():
      if el.tag == f"{W}br":
        segs.append(cur)
        cur = ""
      elif el.tag == f"{W}t":
        cur += el.text or ""
      elif el.tag == f"{W}tab":
        cur += " "
    segs.append(cur)
    out.append([s.strip() for s in segs if s.strip()])
  return [p for p in out if p]


def parse(docx: Path) -> Transcript:
  """Parse a Teams transcript export.

  Args:
    docx: the .docx file.

  Returns:
    The title, the start in UTC (when the title carries it), the duration and the turns.

  Raises:
    InputError: when no speaker turn is found.
  """
  paras = paragraphs(docx)
  title, start, duration, turns = "", None, "", []
  for segs in paras:
    m = SPEAKER.match(segs[0])
    if m:
      text = segs[1:]
      if turns and turns[-1].name == m["name"]:
        turns[-1].lines.extend(text)
      else:
        turns.append(Turn(m["name"], m["ts"], list(text)))
      continue
    if turns:
      turns[-1].lines.extend(segs)  # a caption paragraph without its own speaker line
      continue
    line = " ".join(segs)
    if not title:
      title = line
      s = START_UTC.search(line)
      if s:
        start = datetime.strptime(s[1] + s[2], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    elif DURATION.match(line):
      duration = line
  if not turns:
    raise InputError(f"{docx}: no speaker turns found (expected lines like 'Name   0:08')")
  return Transcript(title, start, duration, turns)


def meeting_name(title: str) -> str:
  """The meeting name without the recording suffix Teams appends.

  Args:
    title: the first line of the export.

  Returns:
    The name before "-YYYYMMDD_HHMMSSUTC-Meeting Recording", or the whole title.
  """
  return START_UTC.split(title)[0].strip() if START_UTC.search(title) else title.strip()


def render(t: Transcript, tz: str | None, source_name: str) -> str:
  """Write the Markdown transcript.

  Args:
    t: the parsed export.
    tz: IANA zone for the start time (for example Australia/Sydney); None keeps UTC.
    source_name: the .docx file name, linked as the source.

  Returns:
    The Markdown text: front matter to complete, header block, full transcript.

  Raises:
    InputError: when tz is not a known zone.
  """
  start = t.start_utc
  if start and tz:
    try:
      from zoneinfo import ZoneInfo

      start = start.astimezone(ZoneInfo(tz))
    except Exception as exc:  # zoneinfo raises several types for a bad key
      raise InputError(f"unknown time zone {tz!r}: {exc}") from exc
  when = start.strftime("%A, %-d %B %Y, %-I:%M %p %Z") if start else "not in the export"
  speakers = list(dict.fromkeys(turn.name for turn in t.turns))
  name = meeting_name(t.title)
  head = [
    "---",
    f"Title: Transcript — {name}",
    "Category: communications-transcript",
    "Status: current",
    "Authority: source-capture",
    f"Scope: Microsoft Teams transcript, {when}{', ' + t.duration if t.duration else ''}",
    f"Last reviewed: {date.today().isoformat()}",
    "Summary: TODO one line on what the meeting covered",
    "---",
    "",
    f"# Transcript — {name}",
    "",
    f"**Date:** {when}" + (f" (Teams recording {t.start_utc.strftime('%Y%m%d_%H%M%S')} UTC)" if t.start_utc else ""),
    f"**Duration:** {t.duration or 'not in the export'}",
    f"**Speakers:** {', '.join(speakers)}",
    f"**Source:** [{source_name}]({source_name.replace(' ', '%20')})",
    "",
    "> **Transcription note:** Microsoft Teams speech-to-text with Teams' speaker labels. Consecutive paragraphs of one speaker are joined into one turn;",
    "> the wording is as exported and not corrected.",
    "",
    "## Full transcript",
    "",
  ]
  body = ["\n".join([f"**{turn.name} ({turn.ts}):**", *turn.lines]) for turn in t.turns]
  return "\n".join(head) + "\n" + "\n\n".join(body) + "\n"


def main(argv: list[str] | None = None) -> int:
  """Preview or write the Markdown transcript.

  Args:
    argv: command-line arguments (default: sys.argv[1:]).

  Returns:
    The exit code (see the module docstring).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("docx", type=Path)
  ap.add_argument("--tz", help="IANA time zone for the start time, e.g. Australia/Sydney (default: UTC)")
  ap.add_argument("--out", type=Path, help="Markdown file to write (default: beside the .docx, same stem, .md)")
  ap.add_argument("--apply", action="store_true", help="write the file (default: print it)")
  ap.add_argument("--force", action="store_true", help="replace an existing file")
  args = ap.parse_args(argv)
  try:
    parsed = parse(args.docx)
    text = render(parsed, args.tz, args.docx.name)
  except InputError as exc:
    print(f"teams_docx: {exc}", file=sys.stderr)
    return 2
  if not args.apply:
    sys.stdout.write(text)
    return 0
  out = args.out or args.docx.with_suffix(".md")
  if out.exists() and not args.force:
    print(f"teams_docx: {out} exists; refusing; --force to replace", file=sys.stderr)
    return 1
  out.write_text(text, encoding="utf-8")
  print(f"wrote {out} ({len(parsed.turns)} turns)")
  return 0


if __name__ == "__main__":
  sys.exit(main())
