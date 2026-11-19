#!/usr/bin/env python3
"""Verify that the rotation just made lost nothing: every content line the uncommitted change removed from a record is in `docs/history/`.

Why (continuum, 2026-11-19): `audit_rotations.py` compares against each record's state before its first rotation, so a line edited since
then reads as LOST (the phantom '## 20261118_2150' report, four times in one day). This check has the narrow job a person did by hand after
each `just budget --apply`: take the lines `git diff` shows removed from the record (ignoring blanks, Contents links and the 'Last rotated'
stamp) and find each, whitespace-folded, in some file under the history folder. Read-only.
Run: python3 -I scripts/records/rotation_verify.py --project-root <project> [--record CHANGELOG.md] [--history docs/history]
     (just rotation-verify <project>)
Exit codes: 0 every removed line found (or nothing removed); 1 lines missing (listed); 2 not a git work tree or the record is missing.
Budget: one git call and one read of the history folder; well under a second on a project's records.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SKIP = re.compile(r"^\s*$|^\s*- \[[^\]]*\]\(#|^Last rotated:")


def fold(text: str) -> str:
  """Collapse runs of whitespace to one space, so a re-wrapped line still matches.

  Args:
    text: any text.

  Returns:
    The text with whitespace folded and trimmed.
  """
  return " ".join(text.split())


def removed_lines(root: Path, record: str) -> list[str]:
  """Lines the uncommitted change removed from `record`, minus blanks, Contents links and the rotation stamp.

  Args:
    root: the project's git work tree.
    record: the record's path relative to root.

  Returns:
    The removed lines, in order.

  Raises:
    RuntimeError: when git fails (not a work tree, or the path is unknown to git).
  """
  p = subprocess.run(["git", "-C", str(root), "diff", "--no-color", "-U0", "--", record], capture_output=True, text=True, timeout=30, check=False)
  if p.returncode != 0:
    raise RuntimeError(p.stderr.strip() or "git diff failed")
  out = []
  for line in p.stdout.splitlines():
    if line.startswith("-") and not line.startswith("---"):
      body = line[1:]
      if not SKIP.match(body):
        out.append(body)
  return out


def missing(lines: list[str], history: Path) -> list[str]:
  """The lines not found, whitespace-folded, in any file under `history`.

  Args:
    lines: removed lines.
    history: the history folder.

  Returns:
    Lines with no match.
  """
  corpus = fold(" ".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(history.rglob("*.md"))))
  return [line for line in lines if fold(line) not in corpus]


def main(argv: list[str] | None = None) -> int:
  """Run the check.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project-root", type=Path, required=True)
  ap.add_argument("--record", default="CHANGELOG.md")
  ap.add_argument("--history", default="docs/history")
  a = ap.parse_args(argv)
  root = a.project_root.resolve()
  if not (root / a.record).is_file():
    print(f"{a.record} not found in {root}", file=sys.stderr)
    return 2
  try:
    lines = removed_lines(root, a.record)
  except RuntimeError as e:
    print(f"git: {e}", file=sys.stderr)
    return 2
  lost = missing(lines, root / a.history)
  for line in lost:
    print(f"MISSING {line[:160]}")
  print(f"{a.record}: {len(lines)} removed line(s), {len(lost)} not in {a.history}")
  return 1 if lost else 0


if __name__ == "__main__":
  sys.exit(main())
