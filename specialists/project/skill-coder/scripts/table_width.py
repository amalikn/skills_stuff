#!/usr/bin/env python3
"""Report each markdown table's aligned width and its continuation rows, so a table is kept under the hook's wrap limit before the hook sees it. Read-only.

Why: the governance markdown hook pads every table column to its widest cell and then wraps rows wider than 200 columns into continuation rows
(a first cell of spaces), which render as broken half-empty rows and split commands. The width that matters is the aligned width,
sum(widest cell per column) + 3 x columns + 1, not the length of any written line (markdown-guide, "Keep a table's aligned width under 200 columns").
On 2026-11-25 (home NAS) one edit made the hook split six tables of a filed operator document; this check found them all before and after.

Usage:
  table_width.py FILE [FILE ...] [--limit 200] [--before HEADING]

  --before HEADING   check only tables above the first line starting with HEADING (for a file whose tail is another author's)

Exit 0: every table under the limit with no continuation rows. Exit 1: a table at or over the limit, or with continuation rows. Exit 2: bad arguments.
"""

from __future__ import annotations

import argparse
import pathlib
import sys


def tables(lines: list[str]) -> list[tuple[int, list[str]]]:
  """Group consecutive table rows.

  Args:
    lines: the file's lines.

  Returns:
    (1-based first line, rows) for each run of lines starting with "|".

  """
  out: list[tuple[int, list[str]]] = []
  cur: list[str] = []
  start = 0
  for i, line in enumerate(lines, 1):
    if line.startswith("|"):
      if not cur:
        start = i
      cur.append(line)
    elif cur:
      out.append((start, cur))
      cur = []
  if cur:
    out.append((start, cur))
  return out


def measure(rows: list[str]) -> tuple[int, int, int]:
  """Measure one table.

  Args:
    rows: its lines, header and separator included.

  Returns:
    (columns, aligned width, continuation rows); the separator row is left out of the width.

  """
  cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
  body = cells[:1] + cells[2:]
  n = max(len(c) for c in cells)
  width = sum(max(len(c[k]) if k < len(c) else 0 for c in body) for k in range(n)) + 3 * n + 1
  continuation = sum(1 for c in cells[2:] if c and c[0] == "")
  return n, width, continuation


def check(path: pathlib.Path, limit: int, before: str | None) -> list[str]:
  """Check one file.

  Args:
    path: the markdown file.
    limit: the column limit.
    before: only tables above the first line starting with this, when given.

  Returns:
    One report line per table, each prefixed "ok" or "BAD".

  Raises:
    OSError: the file cannot be read.

  """
  lines = path.read_text(encoding="utf-8").splitlines()
  if before:
    cut = next((i for i, line in enumerate(lines) if line.startswith(before)), len(lines))
    lines = lines[:cut]
  report = []
  for start, rows in tables(lines):
    n, width, cont = measure(rows)
    flag = "BAD" if width >= limit or cont else "ok"
    report.append(f"{flag} {path}:{start}: {n} cols, aligned width {width}, continuation rows {cont}")
  return report


def main(argv: list[str] | None = None) -> int:
  """Run the check.

  Args:
    argv: command-line arguments.

  Returns:
    The exit code (see the module docstring).

  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("files", nargs="+")
  ap.add_argument("--limit", type=int, default=200)
  ap.add_argument("--before")
  a = ap.parse_args(argv)
  bad = False
  for f in a.files:
    try:
      lines = check(pathlib.Path(f), a.limit, a.before)
    except OSError as error:
      print(f"table_width: {error}", file=sys.stderr)
      return 2
    for line in lines:
      print(line)
      bad |= line.startswith("BAD")
  return 1 if bad else 0


if __name__ == "__main__":
  sys.exit(main())
