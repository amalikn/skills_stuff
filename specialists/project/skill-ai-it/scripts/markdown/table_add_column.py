"""Add a column to markdown tables, keyed by each row's first cell; wrapped continuation rows are merged into one line per row first.

A table the markdown hook wrapped carries continuation rows whose first cell is empty; adding a column by hand to such a table breaks it. This merges each
continuation row into the row above (cell by cell), appends the new column from a key-to-value JSON map, and writes one line per row, which the hook may
wrap again on its next edit. Every row must have a value (or `--default`), so a missing key is refused rather than left blank. Promoted 2026-11-09 from
unified-network-controller (audit follow-up verdict column, two tables, 34 rows).

Run: python3 table_add_column.py FILE --header-first-cell 'ID|Prior ID' --column 'Verdict' --values values.json [--default TEXT] [--apply]
Writes FILE only with --apply; without it prints the plan (tables found, rows, line counts). Runtime: milliseconds per file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def cells(line: str) -> list[str]:
  """Split one markdown table row into stripped cells.

  Args:
    line: a row such as `| a | b |`.

  Returns:
    The cell texts, outer pipes removed.
  """
  return [c.strip() for c in line.strip().strip("|").split("|")]


def merge_rows(rows: list[str]) -> list[list[str]]:
  """Merge wrapped continuation rows (empty first cell) into the row above.

  Args:
    rows: body rows of one table, without header and separator.

  Returns:
    One cell list per logical row.
  """
  merged: list[list[str]] = []
  for line in rows:
    row = cells(line)
    if row[0] == "" and merged:
      prev = merged[-1]
      prev += [""] * (len(row) - len(prev))
      merged[-1] = [(a + " " + b).strip() for a, b in zip(prev, row + [""] * (len(prev) - len(row)))]
    else:
      merged.append(row)
  return merged


def add_column(table: list[str], column: str, values: dict[str, str], default: str | None) -> list[str]:
  """Rebuild one table with the new column, one line per row.

  Args:
    table: the table's lines: header, separator, body.
    column: the new column's header.
    values: first-cell key to the new cell's text.
    default: text for a row whose key is missing; None refuses such a row.

  Returns:
    The rebuilt table lines.

  Raises:
    KeyError: a row's key has no value and no default was given.
  """
  header = cells(table[0]) + [column]
  out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
  for row in merge_rows(table[2:]):
    if row[0] in values:
      value = values[row[0]]
    elif default is not None:
      value = default
    else:
      raise KeyError(row[0])
    out.append("| " + " | ".join(row + [value.replace("|", "\\|")]) + " |")
  return out


def find_tables(lines: list[str], first_cell: str) -> list[tuple[int, int]]:
  """Locate tables whose header's first cell matches a regex.

  Args:
    lines: the file's lines.
    first_cell: regex the header's first cell must match in full.

  Returns:
    (start, end) line index pairs, end exclusive.
  """
  found = []
  pattern = re.compile(first_cell)
  i = 0
  while i < len(lines):
    is_header = lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1])
    if is_header and pattern.fullmatch(cells(lines[i])[0]):
      end = i
      while end < len(lines) and lines[end].startswith("|"):
        end += 1
      found.append((i, end))
      i = end
    else:
      i += 1
  return found


def main(argv: list[str] | None = None) -> int:
  """Plan or apply the new column on every matching table.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    0 on success; 1 when no table matches or a row has no value.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("file", type=Path)
  ap.add_argument("--header-first-cell", required=True, help="regex the header's first cell must match, e.g. 'ID|Prior ID'")
  ap.add_argument("--column", required=True, help="header of the new column")
  ap.add_argument("--values", required=True, type=Path, help="JSON object: first-cell key -> cell text")
  ap.add_argument("--default", help="text for rows missing from --values (default: refuse)")
  ap.add_argument("--apply", action="store_true", help="write the file (default: plan only)")
  args = ap.parse_args(argv)
  lines = args.file.read_text(encoding="utf-8").split("\n")
  values = json.loads(args.values.read_text(encoding="utf-8"))
  tables = find_tables(lines, args.header_first_cell)
  if not tables:
    print(f"no table whose header's first cell matches {args.header_first_cell!r}")
    return 1
  for start, end in reversed(tables):
    try:
      new = add_column(lines[start:end], args.column, values, args.default)
    except KeyError as exc:
      print(f"table at line {start + 1}: no value for row {exc.args[0]!r} (give it in --values or pass --default)")
      return 1
    print(f"table at line {start + 1}: {len(new) - 2} rows, {end - start} lines -> {len(new)} lines")
    lines[start:end] = new
  if args.apply:
    args.file.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {args.file}")
  else:
    print("plan only; add --apply to write")
  return 0


if __name__ == "__main__":
  sys.exit(main())
