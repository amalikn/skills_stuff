#!/usr/bin/env python3
"""commtracker/verify_quotes.py — Check that every quote in a tracker entry is verbatim in its transcript, and said by the speaker it is given to.

A tracker entry for a long call or meeting carries key extracts as italic quotes (`*"..."*`, ADR-001: verbatim). This reads one entry (from its
heading to the next `---` line or `## ` heading), finds every `*"..."*` or `_"..."_`, and checks it against the transcript with whitespace normalised. When the
quote is introduced as `Name: *"..."*`, it also checks that the quote sits inside a turn labelled `**Name:**`. Built after a filing (2026-11-18) where
the operator relabelled 16 turns and every extract had to be re-attributed by hand.

Run:
  python3 verify_quotes.py <tracker.md> "<heading start, e.g. ## Meeting 6 - >" <transcript.md>

Safety: read-only; writes nothing. Exit 0 all quotes found and attributed, 1 a quote missing or misattributed, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# A speaker is one or two capitalised words right before the colon ("Sandro: ", "Martin Camilleri: "); an opening *" inside **bold** is not a quote.
# Italic quotes in either Markdown form, *"..."* or _"..."_ (both since 2026-11-18: an operator's _"..."_ edit slipped past the check).
QUOTE = re.compile(r'(?:\b([A-Z][a-z]+(?: [A-Z][a-z]+)?): )?(?<![*_\w])([*_])"(.+?)"\2(?![*_\w])', re.S)
LABEL = re.compile(r"^\*\*([^*\n]+?)(?: \([^)]*\))?:\*\*\s*$")
TURN_END = re.compile(r"^(#{1,6} |---\s*$|\*\*[^*\n]+\*\*\s*$)")


EMPHASIS = re.compile(r"(?<![\w*])(\*{1,2}|_{1,2})(?=\S)(.+?)(?<=\S)\1(?![\w*])")


def _norm(text: str) -> str:
  """Collapse whitespace runs to one space and drop Markdown emphasis markers (`*x*`, `**x**`, `_x_`), keeping the words.

  A transcript that italicises a word (*cleaned*) still matches a quote typed without the markers (2026-11-18).

  Args:
    text: Any text.

  Returns:
    The text with emphasis markers removed and whitespace normalised and trimmed.

  Raises:
    Nothing.
  """
  prev = None
  while prev != text:
    prev, text = text, EMPHASIS.sub(r"\2", text)
  return " ".join(text.split())


def entry_text(tracker: str, heading: str) -> str:
  """Return one entry's text, from its heading line to the next rule or level-2 heading.

  Args:
    tracker: The whole tracker file.
    heading: The start of the entry's heading line, e.g. "## Meeting 6 - ".

  Returns:
    The entry text without its heading line.

  Raises:
    ValueError: when no heading line starts with the given text.
  """
  lines = tracker.split("\n")
  starts = [i for i, ln in enumerate(lines) if ln.startswith(heading)]
  if not starts:
    raise ValueError(f"no heading starts with {heading!r}")
  out: list[str] = []
  for ln in lines[starts[0] + 1 :]:
    if ln.startswith("## ") or ln.strip() == "---":
      break
    out.append(ln)
  return "\n".join(out)


def turns(transcript: str) -> list[tuple[str, str]]:
  """Split a transcript into (speaker, normalised text) turns.

  Args:
    transcript: The transcript Markdown.

  Returns:
    One pair per speaker turn; the speaker without any time in brackets.

  Raises:
    Nothing.
  """
  found: list[tuple[str, list[str]]] = []
  current: list[str] | None = None
  for ln in transcript.split("\n"):
    m = LABEL.match(ln)
    if m:
      current = []
      found.append((m.group(1).strip(), current))
    elif TURN_END.match(ln):
      current = None
    elif current is not None:
      current.append(ln)
  return [(who, _norm(" ".join(body))) for who, body in found]


def check(entry: str, transcript: str) -> list[str]:
  """Check every quote in an entry against the transcript.

  Args:
    entry: The entry text (see entry_text).
    transcript: The transcript Markdown.

  Returns:
    One problem line per quote not found, or found only under another speaker; empty when all pass.

  Raises:
    Nothing.
  """
  whole = _norm(transcript)
  by_turn = turns(transcript)
  problems: list[str] = []
  for who, _mark, quote in QUOTE.findall(entry):
    q = _norm(quote)
    if q not in whole:
      problems.append(f"NOT VERBATIM: {q[:80]}")
      continue
    if who:
      speakers = sorted({s for s, body in by_turn if q in body})
      if speakers and who not in speakers:
        problems.append(f"SPEAKER {who} but said by {', '.join(speakers)}: {q[:70]}")
  return problems


def main(argv: list[str] | None = None) -> int:
  """Verify one tracker entry's quotes and print the result.

  Args:
    argv: Command-line arguments; None reads sys.argv.

  Returns:
    0 when every quote passes, 1 on any problem, 2 on bad input.

  Raises:
    Nothing; errors are reported on stderr.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("tracker", type=Path)
  ap.add_argument("heading", help='start of the entry heading, e.g. "## Meeting 6 - "')
  ap.add_argument("transcript", type=Path)
  args = ap.parse_args(argv)
  for path in (args.tracker, args.transcript):
    if not path.is_file():
      print(f"ERROR: not a file: {path}", file=sys.stderr)
      return 2
  try:
    entry = entry_text(args.tracker.read_text(encoding="utf-8"), args.heading)
  except ValueError as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 2
  count = len(QUOTE.findall(entry))
  problems = check(entry, args.transcript.read_text(encoding="utf-8"))
  for line in problems:
    print(line)
  print(f"{count} quotes checked, {len(problems)} problem(s)")
  return 1 if problems else 0


if __name__ == "__main__":
  sys.exit(main())
