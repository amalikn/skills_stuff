#!/usr/bin/env python3
"""commtracker/check_tracker.py — Read-only checks of a communications tracker and its folder index, run before a review date is set.

Why (operator, 2026-11-20): a tracker review needs evidence beyond reading. This checks what a reader cannot see at a glance: every in-file anchor
resolves to a heading, every linked file exists, entries are in date order and each entry type (Email, Teams, Meeting, Call, Cross-reference) is numbered
1, 2, 3 without gaps; and, for the folder index (readme.md or README.md beside the tracker), every link resolves and every file in emails/, teams/,
transcripts/ and attachments/ is listed. It reports; it never edits. A clean run is not a review: the operator's rule is that Last reviewed changes
only after a full re-read.

Run:
  python3 check_tracker.py <communications-folder>           # tracker and index
  python3 check_tracker.py <communications-folder> --no-index # tracker only

Safety: read-only; no network. Runtime: under 0.1 s for a 1,100-line tracker (measured 2026-11-20).
Exit: 0 clean, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

HEADING = re.compile(r"(?m)^(#{1,6}) (.+?)\s*$")
ENTRY = re.compile(r"^(Email|Teams|Meeting|Call|Cross-reference) (\d+) - (\d{8})(?:_\d{4})? - ")
LINK = re.compile(r"\]\((<[^>]+>|[^)\s]+)\)")
SOURCE_DIRS = ("emails", "teams", "transcripts", "attachments")


def slug(heading: str) -> str:
  """The GitHub anchor of a heading: lower case, punctuation removed, spaces to hyphens.

  Args:
    heading: the heading text without its hashes.

  Returns:
    The anchor, without the leading "#".
  """
  return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def link_targets(text: str) -> list[str]:
  """Every link target in Markdown text, angle brackets removed and percent-escapes decoded.

  Args:
    text: the Markdown.

  Returns:
    The targets in order.
  """
  return [urllib.parse.unquote(t[1:-1] if t.startswith("<") else t) for t in LINK.findall(text)]


def check_tracker(path: Path) -> list[str]:
  """Check one tracker file.

  Args:
    path: communications-tracking.md.

  Returns:
    One line per finding; empty when clean.
  """
  text = path.read_text(encoding="utf-8")
  anchors = {slug(h) for _, h in HEADING.findall(text)}
  out = []
  entries = [(m[1], int(m[2]), m[3], h) for _, h in HEADING.findall(text) if (m := ENTRY.match(h))]
  for t in link_targets(text):
    if t.startswith(("http://", "https://", "mailto:")):
      continue
    file_part, _, anchor = t.partition("#")
    if not file_part:
      if anchor not in anchors:
        out.append(f"anchor not found: #{anchor}")
    elif not (path.parent / file_part).exists():
      out.append(f"file not found: {file_part}")
  for prev, cur in zip(entries, entries[1:], strict=False):
    if cur[2] < prev[2]:
      out.append(f"out of date order: '{cur[3]}' after '{prev[3]}'")
  for kind in dict.fromkeys(e[0] for e in entries):
    nums = [e[1] for e in entries if e[0] == kind]
    if sorted(nums) != list(range(1, len(nums) + 1)):
      out.append(f"{kind} numbering not 1..{len(nums)}: {sorted(nums)}")
  for m in re.finditer(r"(?m)^---\n(## )", text):
    out.append(f"no blank line between a rule and the heading at offset {m.start(1)}")
  return out


def check_index(folder: Path) -> list[str]:
  """Check the folder index: links resolve and every source file is listed.

  Args:
    folder: the communications folder.

  Returns:
    One line per finding; empty when clean. A missing index is one finding.
  """
  index = next((folder / n for n in ("readme.md", "README.md") if (folder / n).is_file()), None)
  if index is None:
    return ["no readme.md or README.md in the folder"]
  targets = {t.partition("#")[0] for t in link_targets(index.read_text(encoding="utf-8"))}
  out = [f"index link not found: {t}" for t in sorted(targets) if t and not t.startswith("http") and not (folder / t).exists()]
  for d in SOURCE_DIRS:
    if (folder / d).is_dir():
      for f in sorted((folder / d).iterdir()):
        rel = f"{d}/{f.name}"
        if f.is_file() and not f.name.startswith(".") and rel not in targets:
          out.append(f"not listed in the index: {rel}")
  return out


def main(argv: list[str] | None = None) -> int:
  """Run the checks and print the findings.

  Args:
    argv: command-line arguments (default: sys.argv[1:]).

  Returns:
    The exit code (see the module docstring).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("folder", type=Path, help="the communications folder holding communications-tracking.md")
  ap.add_argument("--no-index", action="store_true", help="skip the folder index check")
  args = ap.parse_args(argv)
  tracker = args.folder / "communications-tracking.md"
  if not tracker.is_file():
    print(f"check_tracker: {tracker} not found", file=sys.stderr)
    return 2
  findings = check_tracker(tracker) + ([] if args.no_index else check_index(args.folder))
  for f in findings:
    print(f)
  print(f"check_tracker: {len(findings)} finding(s)")
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
