#!/usr/bin/env python3
"""Triage claim_scan's BROKEN path claims: which resolve once read as a suffix, which name a file that moved, and which are gone.

claim_scan resolves a path against the project root and the declared sibling roots. A package-relative path (`unc_ownership/jobs.py`), a bare
name (`seed_smc_devices.py`) or a path into another repo then counts as BROKEN, so a real audit reports about 1,500 and the few real defects
hide among them (unified-network-controller audit 16, 2026-11-18: 942 named a file that exists elsewhere, 143 resolved as a suffix, 429 gone).
This script sorts them, with live surfaces first, so only the `gone` class in live files needs a person.

Run: python3 <skill>/scripts/broken_path_triage.py --root <project> --claims <claim_scan output file> [--also <dir> ...] [--all]
Read-only: reads the claims file and lists files under --root and each --also; writes nothing.
"""

from __future__ import annotations

import argparse
import collections
import os
import re
import sys
from pathlib import Path

#: A claim_scan output line for an unresolved path: `  BROKEN    <file>:<line>  <path>`.
BROKEN_LINE = re.compile(r"^\s+BROKEN\s+(\S+?):(\d+)\s+(.*)$")
#: Characters that mark a pattern or placeholder rather than a path.
NOT_A_PATH = re.compile(r"[|*<>{}$\s]")
#: Folders whose files are records of what was true then; a broken path there is history, not a defect.
HISTORY_PARTS = ("docs/history/", "archive/", "docs/reports/", ".remember/", "CHANGELOG")
#: Folders never walked when indexing files.
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".ruff_cache"}


def parse_claims(text: str) -> list[tuple[str, int, str]]:
  """The BROKEN rows of a claim_scan output.

  Args:
    text: claim_scan's printed output.

  Returns:
    [(citing file, line, path as written)] in output order.
  """
  rows = []
  for line in text.splitlines():
    m = BROKEN_LINE.match(line)
    if m:
      rows.append((m.group(1), int(m.group(2)), m.group(3).strip().strip("`").rstrip("/")))
  return rows


def index_files(roots: list[Path]) -> dict[str, list[str]]:
  """Every path suffix of every file under the roots, mapped to the files ending in it.

  Args:
    roots: directories to walk.

  Returns:
    {"a/b.py": [...], "b.py": [...]} for a file `x/a/b.py`, keyed by each trailing run of path parts.
  """
  suffixes: dict[str, list[str]] = collections.defaultdict(list)
  for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
      dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".staleness-audit")]
      for name in filenames:
        full = str(Path(dirpath, name))
        parts = Path(full).relative_to(root).parts
        for i in range(len(parts)):
          suffixes["/".join(parts[i:])].append(full)
  return suffixes


def classify(path: str, suffixes: dict[str, list[str]]) -> str:
  """One BROKEN path's class.

  Args:
    path: the path as written.
    suffixes: the index from index_files().

  Returns:
    "suffix" when a file ends in the whole path, "moved" when only its file name exists somewhere, "not-a-path" for a pattern or placeholder,
    else "gone".
  """
  if NOT_A_PATH.search(path):
    return "not-a-path"
  if path in suffixes:
    return "suffix"
  if Path(path).name in suffixes:
    return "moved"
  return "gone"


def is_history(citing: str) -> bool:
  """Whether the citing file is a record (history, a dated report, a change log).

  Args:
    citing: the citing file, relative to the project root.

  Returns:
    True for a record, where a stale path is evidence of its date.
  """
  return any(part in citing for part in HISTORY_PARTS)


def main(argv: list[str] | None = None) -> int:
  """Print the triage: counts per class, then the `gone` rows in live files, then (with --all) every row.

  Args:
    argv: command-line arguments, or None for sys.argv.

  Returns:
    0 when no live file cites a gone path, 1 when one does, 2 when the claims file cannot be read.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--root", default=".", help="the project root")
  ap.add_argument("--claims", required=True, help="a file holding claim_scan's output")
  ap.add_argument("--also", action="append", default=[], help="another tree to search (a sibling repo, a skill); repeatable")
  ap.add_argument("--all", action="store_true", help="print every row, not only gone paths in live files")
  args = ap.parse_args(argv)
  try:
    rows = parse_claims(Path(args.claims).read_text())
  except OSError as e:
    print(f"cannot read {args.claims}: {e}", file=sys.stderr)
    return 2
  suffixes = index_files([Path(args.root).resolve(), *(Path(a).resolve() for a in args.also)])
  counts: collections.Counter = collections.Counter()
  live_gone = []
  for citing, line, path in rows:
    cls = classify(path, suffixes)
    where = "history" if is_history(citing) else "live"
    counts[(cls, where)] += 1
    if args.all:
      print(f"{cls:10} {where:7} {citing}:{line}  {path}")
    elif cls == "gone" and where == "live":
      live_gone.append(f"{citing}:{line}  {path}")
  print(f"BROKEN rows: {len(rows)}")
  for (cls, where), n in sorted(counts.items()):
    print(f"  {cls:10} {where:7} {n}")
  for row in live_gone:
    print(f"GONE (live) {row}")
  return 1 if live_gone else 0


if __name__ == "__main__":
  sys.exit(main())
