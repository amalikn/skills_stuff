#!/usr/bin/env python3
"""commtracker/compact_turns.py — Make each speaker turn in a transcript one block, with no blank lines inside it.

Standard: SKILL.md, "Transcript and chat turn layout". A turn starts at a speaker label alone on its line (`**Martin:**`, `**Stu (2:15 PM):**`) and
runs to the next label, heading or `---`. Inside a turn the label and its lines sit together with no blank line and no trailing backslash (operator,
2026-11-11: the file is read as source); a quote, list or table stays its own block with one blank line around it, and consecutive quote lines become
one quote. Trailing backslashes left by an earlier layout are removed. A label whose turn holds no plain text (a field label over a list, such as
`**Participants:**`) is left as written. Wording never changes: the script compares every non-blank line, without its trailing backslash, before
and after, and refuses to write when they differ.

Run:
  python3 compact_turns.py <transcript.md> [...]          # preview: counts per file, writes nothing
  python3 compact_turns.py <transcript.md> [...] --apply  # write the files

Safety: reads by default; writes only the named files and only with --apply. Exit 0 ok, 1 wording check failed, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LABEL = re.compile(r"^\*\*[^*\n]+:\*\*\\?\s*$")
HEADING = re.compile(r"^#{1,6} ")
RULE = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")
QUOTE = re.compile(r"^>")
LIST = re.compile(r"^\s*([-*+]|\d+[.)])\s")
TABLE = re.compile(r"^\s*\|")
FENCE = re.compile(r"^\s*(```|~~~)")


def _kind(line: str) -> str:
  """Classify one non-blank line inside a turn.

  Args:
    line: The line, without its newline.

  Returns:
    "quote", "list", "table" or "text".

  Raises:
    Nothing.
  """
  if QUOTE.match(line):
    return "quote"
  if LIST.match(line):
    return "list"
  if TABLE.match(line):
    return "table"
  return "text"


def _ends_turn(line: str) -> bool:
  """Tell whether a line closes the current turn.

  Args:
    line: The line, without its newline.

  Returns:
    True for a speaker label, a heading, a horizontal rule or a code fence.

  Raises:
    Nothing.
  """
  return bool(LABEL.match(line) or HEADING.match(line) or RULE.match(line) or FENCE.match(line))


def _bare(lines: list[str]) -> list[str]:
  """Strip trailing whitespace and any trailing backslash (hard break) from each line.

  Args:
    lines: Lines of one block.

  Returns:
    The same lines without trailing whitespace or backslash.

  Raises:
    Nothing.
  """
  return [ln.rstrip().rstrip("\\").rstrip() for ln in lines]


def _render_turn(label: str, body: list[str]) -> list[str] | None:
  """Lay out one turn as a single block.

  Args:
    label: The speaker label line.
    body: The turn's lines after the label, blank lines included.

  Returns:
    The new lines (label first, no trailing blank), or None when the turn holds no plain text and is left as written.

  Raises:
    Nothing.
  """
  groups: list[tuple[str, list[str]]] = []
  for line in body:
    if not line.strip():
      continue
    kind = _kind(line)
    if groups and groups[-1][0] == kind and kind != "text":
      groups[-1][1].append(line)
    elif groups and groups[-1][0] == kind == "text":
      groups[-1][1].append(line)
    else:
      groups.append((kind, [line]))
  if not any(kind == "text" for kind, _ in groups):
    return None
  out: list[str] = []
  head = label.rstrip().rstrip("\\").rstrip()
  for i, (kind, lines) in enumerate(groups):
    if kind == "text":
      block = _bare(lines)
      if i == 0:
        out.append(head)
      else:
        out.append("")
      out.extend(block)
    else:
      if i == 0:
        out.append(head)
      out.append("")
      out.extend(_bare(lines) if kind == "quote" else [ln.rstrip() for ln in lines])
  return out


def compact(text: str) -> tuple[str, int]:
  """Compact every speaker turn in a transcript.

  Args:
    text: The whole Markdown file.

  Returns:
    The new text and the number of turns changed.

  Raises:
    Nothing.
  """
  lines = text.split("\n")
  out: list[str] = []
  changed = 0
  i = 0
  in_fence = False
  while i < len(lines):
    line = lines[i]
    if FENCE.match(line):
      in_fence = not in_fence
    if in_fence or not LABEL.match(line):
      out.append(line)
      i += 1
      continue
    j = i + 1
    while j < len(lines) and not _ends_turn(lines[j]):
      j += 1
    body = lines[i + 1 : j]
    new = _render_turn(line, body)
    if new is None:
      out.extend(lines[i:j])
    else:
      trailing = 1 if j < len(lines) else (1 if body and not body[-1].strip() else 0)
      new_block = new + [""] * trailing
      if new_block != lines[i:j]:
        changed += 1
      out.extend(new_block)
    i = j
  return "\n".join(out), changed


def wording(text: str) -> list[str]:
  """Return the file's wording: non-blank lines without a trailing backslash.

  Args:
    text: Markdown text.

  Returns:
    The stripped, non-blank lines in order.

  Raises:
    Nothing.
  """
  return [ln.rstrip().rstrip("\\").rstrip() for ln in text.split("\n") if ln.strip()]


def main(argv: list[str] | None = None) -> int:
  """Preview or apply turn compaction on the named files.

  Args:
    argv: Command-line arguments; None reads sys.argv.

  Returns:
    0 on success, 1 when a wording check fails, 2 on bad input.

  Raises:
    Nothing; errors are reported on stderr.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("files", nargs="+", type=Path)
  ap.add_argument("--apply", action="store_true", help="write the files (default: preview only)")
  args = ap.parse_args(argv)
  rc = 0
  for path in args.files:
    if not path.is_file():
      print(f"ERROR: not a file: {path}", file=sys.stderr)
      return 2
    old = path.read_text(encoding="utf-8")
    new, turns = compact(old)
    if wording(old) != wording(new):
      print(f"FAIL {path}: wording would change; not written", file=sys.stderr)
      rc = 1
      continue
    before, after = old.count("\n"), new.count("\n")
    verb = "wrote" if args.apply and new != old else "would change" if new != old else "unchanged"
    print(f"{verb} {path}: {turns} turns, {before} -> {after} lines")
    if args.apply and new != old:
      path.write_text(new, encoding="utf-8")
  return rc


if __name__ == "__main__":
  sys.exit(main())
