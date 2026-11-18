#!/usr/bin/env python3
"""Prove that a re-wrapped markdown file changed no table cell and no word. Read-only.

Why: a formatter hook re-wraps a whole markdown file on the first edit when the file was not already in its normal form. The diff is then far
larger than the edit and reads as damage; on 2026-11-18 a lossless re-wrap of a 1,400-line register was reported as corruption because a token
comparison cannot tell a table re-wrap from damage (a table wraps column by column, so the word order changes). This compares the two versions
the only safe way: tables un-wrapped and matched row by row and cell by cell, prose matched word by word (operator, 2026-11-18).

Usage:
  reflow_lossless.py BEFORE AFTER --table-reflow <path to table-reflow cli.mjs>
  reflow_lossless.py --git FILE --table-reflow <cli.mjs>      # BEFORE is the file at HEAD, AFTER the working copy
  TABLE_REFLOW_CLI=<cli.mjs> reflow_lossless.py --git FILE --ignore-contents

Exit 0: no cell and no word changed. Exit 1: differences, listed. Exit 2: bad arguments, or tables present and no un-wrapper to prove them.
It writes nothing but temporary copies, which it removes.
"""

from __future__ import annotations

import argparse
import difflib
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Callable

#: Oldest Python this helper runs on (the pack's contract test parses it at that grammar).
REQUIRES_PYTHON = (3, 11)

#: Seconds any one call out (git, node) may take; every call states one.
CALL_TIMEOUT_S = 60

#: How many differing spans or rows are printed before the rest are only counted.
SHOWN = 5

SEPARATOR = re.compile(r":?-{1,}:?")
CONTENTS = re.compile(r"^#{1,6}\s+Contents\s*$")
HEADING = re.compile(r"^#{1,6}\s")


def is_table_line(line: str) -> bool:
  """Whether a line belongs to a markdown table.

  Args:
    line: one line of the file.

  Returns:
    True when its first non-blank character is a pipe.
  """
  return line.lstrip().startswith("|")


def drop_contents(lines: list[str]) -> list[str]:
  """Remove a generated `Contents` block, which a formatter may rebuild.

  Args:
    lines: the file's lines.

  Returns:
    The lines without the Contents heading and its body, up to the next heading or horizontal rule.
  """
  out, skipping = [], False
  for line in lines:
    if CONTENTS.match(line):
      skipping = True
      continue
    if skipping and (HEADING.match(line) or line.strip() == "---"):
      skipping = False
    if not skipping:
      out.append(line)
  return out


def prose_words(text: str, ignore_contents: bool = False) -> list[str]:
  """The words of everything that is not a table, in order.

  Args:
    text: the file's text.
    ignore_contents: leave a generated Contents block out.

  Returns:
    Words split on white space. A blockquote marker at the start of a line is dropped, because re-wrapping a quoted paragraph changes how
    many lines carry one.
  """
  lines = text.split("\n")
  if ignore_contents:
    lines = drop_contents(lines)
  words: list[str] = []
  for line in lines:
    if is_table_line(line):
      continue
    words.extend(re.sub(r"^\s*(>\s*)+", "", line).split())
  return words


def table_rows(unwrapped: str) -> list[tuple[str, ...]]:
  """The rows of every table in an un-wrapped file, as cells.

  Args:
    unwrapped: the file's text after its tables were un-wrapped to one line per row.

  Returns:
    One tuple of cells per table row, white space collapsed; a separator row becomes dashes of one length.
  """
  rows = []
  for line in unwrapped.split("\n"):
    if not is_table_line(line):
      continue
    cells = [re.sub(r"\s+", " ", cell).strip() for cell in line.strip().strip("|").split("|")]
    if cells and all(SEPARATOR.fullmatch(cell) for cell in cells if cell):
      cells = ["---"] * len(cells)
    rows.append(tuple(cells))
  return rows


def unwrap_with_cli(cli: pathlib.Path) -> Callable[[str], str]:
  """Build an un-wrapper that runs the table-reflow command line on a temporary copy.

  Args:
    cli: path of table-reflow's `cli.mjs`.

  Returns:
    A function from a file's text to the same text with every table row on one line.
  """

  def unwrap(text: str) -> str:
    """Un-wrap one text.

    Args:
      text: the file's text.

    Returns:
      The text with tables un-wrapped.

    Raises:
      subprocess.CalledProcessError: the tool refused the file.
      subprocess.TimeoutExpired: the tool took longer than CALL_TIMEOUT_S.
    """
    with tempfile.TemporaryDirectory() as tmp:
      copy = pathlib.Path(tmp) / "doc.md"
      copy.write_text(text, encoding="utf-8")
      subprocess.run(["node", str(cli), str(copy), "--unwrap", "--in-place"], check=True, capture_output=True, timeout=CALL_TIMEOUT_S)
      return copy.read_text(encoding="utf-8")

  return unwrap


def differences(before: str, after: str, unwrap: Callable[[str], str] | None, ignore_contents: bool = False) -> list[str]:
  """Every way the two texts differ in content.

  Args:
    before: the text before the re-wrap.
    after: the text after it.
    unwrap: un-wraps tables; None when no un-wrapper is available.
    ignore_contents: leave a generated Contents block out of the prose comparison.

  Returns:
    One line per finding; empty when no cell and no word changed.

  Raises:
    ValueError: a table is present and there is no un-wrapper to prove it.
  """
  found: list[str] = []
  a, b = prose_words(before, ignore_contents), prose_words(after, ignore_contents)
  if a != b:
    spans = [op for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op[0] != "equal"]
    found.append(f"prose: {len(spans)} differing span(s) ({len(a)} words before, {len(b)} after)")
    for tag, i1, i2, j1, j2 in spans[:SHOWN]:
      found.append(f"  {tag}: {' '.join(a[i1:i2])[:120]!r} -> {' '.join(b[j1:j2])[:120]!r}")
  has_tables = any(is_table_line(line) for line in (before + "\n" + after).split("\n"))
  if has_tables:
    if unwrap is None:
      raise ValueError("the file has tables and no un-wrapper was given (--table-reflow or TABLE_REFLOW_CLI)")
    ra, rb = table_rows(unwrap(before)), table_rows(unwrap(after))
    if ra != rb:
      blocks = [op for op in difflib.SequenceMatcher(None, ra, rb, autojunk=False).get_opcodes() if op[0] != "equal"]
      found.append(f"tables: {len(blocks)} differing block(s) of rows ({len(ra)} rows before, {len(rb)} after)")
      for tag, i1, i2, j1, j2 in blocks[:SHOWN]:
        found.append(f"  {tag}: {' | '.join(ra[i1])[:120] if i1 < len(ra) else ''!r} -> {' | '.join(rb[j1])[:120] if j1 < len(rb) else ''!r}")
  return found


def head_text(path: pathlib.Path) -> str:
  """A file's text as committed at HEAD.

  Args:
    path: the working-copy file.

  Returns:
    Its text at HEAD.

  Raises:
    subprocess.CalledProcessError: the file is not tracked, or this is not a git repository.
  """
  run = subprocess.run(["git", "-C", str(path.parent), "show", f"HEAD:./{path.name}"], check=True, capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
  return run.stdout


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 when lossless, 1 when content differs, 2 on bad arguments or when tables cannot be proven.
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("files", nargs="*", help="BEFORE AFTER, or with --git one FILE")
  ap.add_argument("--git", action="store_true", help="compare FILE at HEAD with the working copy")
  ap.add_argument("--table-reflow", default=os.environ.get("TABLE_REFLOW_CLI", ""), help="path of table-reflow's cli.mjs (or TABLE_REFLOW_CLI)")
  ap.add_argument("--ignore-contents", action="store_true", help="leave a generated Contents block out of the prose comparison")
  args = ap.parse_args(argv)
  try:
    if args.git:
      if len(args.files) != 1:
        ap.error("--git takes one FILE")
      path = pathlib.Path(args.files[0]).resolve()
      before, after = head_text(path), path.read_text(encoding="utf-8")
    else:
      if len(args.files) != 2:
        ap.error("give BEFORE and AFTER, or --git FILE")
      before, after = (pathlib.Path(f).read_text(encoding="utf-8") for f in args.files)
    cli = pathlib.Path(args.table_reflow) if args.table_reflow else None
    if cli is not None and not cli.is_file():
      print(f"table-reflow command line not found: {cli}", file=sys.stderr)
      return 2
    found = differences(before, after, unwrap_with_cli(cli) if cli else None, args.ignore_contents)
  except ValueError as exc:
    print(f"cannot prove it: {exc}", file=sys.stderr)
    return 2
  except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
    print(f"could not read or un-wrap: {exc}", file=sys.stderr)
    return 2
  if found:
    print("NOT lossless:")
    print("\n".join(found))
    return 1
  print("lossless: no table cell and no word changed")
  return 0


if __name__ == "__main__":
  sys.exit(main())
