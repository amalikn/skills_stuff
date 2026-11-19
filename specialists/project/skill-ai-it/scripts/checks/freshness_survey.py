#!/usr/bin/env python3
"""Survey review dates across many governed projects: docs overdue now, docs due by a date, and early Review by keys. Read-only; stdlib plus git.

Why (operator, 2026-11-19: "Are there any other skill which also need this sort of regular review"): doc_freshness.py answers for one project and
hides baselined findings, so a fleet question needed a hand-written loop twice in one session. This runs doc_freshness's own rule over every project
given (or every folder under --scan whose justfile calls doc_freshness.py), with the baseline ignored, and reports per project:
  - overdue: living docs past their review date today;
  - due-by: living docs that will be past it on --by;
  - early: non-tracker docs whose `Review by` falls before `Last reviewed` + the window (an adoption-era date that undercuts the window).

Run:
    python scripts/checks/freshness_survey.py --scan /Volumes/Data/_ai/_skills/skills_stuff --window-days 90 --by 2026-12-19
    python scripts/checks/freshness_survey.py --project-root ../skill-coder --project-root ../skill-drawio --list
Safety: reads files and git history only; writes nothing. Exit: 0 when nothing is overdue, 1 when something is, 2 on bad arguments.
Runtime budget: about 0.3 s per project (16 skill packs measured at 5 s with the shell loop this replaces).
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import re
import sys

REQUIRES_PYTHON = (3, 11)
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # doc_freshness imports file_headers beside it
_spec = importlib.util.spec_from_file_location("doc_freshness", HERE / "doc_freshness.py")
df = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(df)

SKIP = ("-github/", "/node_modules/", "/.venv/", "/templates/")
FRONT_KEY = re.compile(r"(?m)^(Review by|Last reviewed|Category): *(.+)$")


def due_files(root: pathlib.Path, today: dt.date, window_days: int) -> list[str]:
  """Project-relative docs that doc_freshness's review-due rule flags on a given day, baseline ignored.

  Args:
    root: the project root.
    today: the day to judge.
    window_days: the review window for docs without `Review by`.

  Returns:
    Sorted paths of review-due docs.
  """
  found = df.findings(root, today, window_days)
  return sorted(key.split(":", 1)[1] for key in found if key.startswith("review-due:"))


def early_review_by(root: pathlib.Path, window_days: int) -> list[str]:
  """Non-tracker docs whose `Review by` comes before `Last reviewed` + the window.

  Args:
    root: the project root.
    window_days: the project's review window.

  Returns:
    Lines `path Review-by Last-reviewed`, sorted.
  """
  out = []
  for path in sorted(root.rglob("*.md")):
    rel = path.relative_to(root).as_posix()
    if any(s in "/" + rel for s in SKIP) or "/trackers/" in "/" + rel or "docs/history/" in rel:
      continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
      continue
    keys = {k.lower(): v.strip() for k, v in FRONT_KEY.findall(text.split("\n---", 1)[0])}
    review_by, reviewed = df.parse_date(keys.get("review by", "")), df.parse_date(keys.get("last reviewed", ""))
    if review_by and reviewed and "tracker" not in keys.get("category", "") and review_by < reviewed + dt.timedelta(days=window_days):
      out.append(f"{rel} {review_by} {reviewed}")
  return out


def scan_roots(scan: pathlib.Path) -> list[pathlib.Path]:
  """Folders under a tree whose justfile runs doc_freshness.py (governed projects), skipping templates and upstream clones.

  Args:
    scan: the tree to search.

  Returns:
    Sorted project roots.
  """
  roots = []
  for justfile in scan.rglob("justfile"):
    rel = "/" + justfile.relative_to(scan).as_posix()
    if not any(s in rel for s in SKIP) and "doc_freshness.py" in justfile.read_text(encoding="utf-8", errors="replace"):
      roots.append(justfile.parent)
  return sorted(roots)


def main(argv: list[str] | None = None) -> int:
  """Print one line per project (and the files with --list).

  Args:
    argv: command-line arguments.

  Returns:
    0 when nothing is overdue, 1 when something is.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project-root", action="append", default=[], help="a project to survey (repeatable)")
  ap.add_argument("--scan", help="survey every governed project under this folder")
  ap.add_argument("--window-days", type=int, default=df.DEFAULT_WINDOW_DAYS)
  ap.add_argument("--by", help="YYYY-MM-DD: also count docs due by this day")
  ap.add_argument("--today", help="YYYY-MM-DD; default the machine's date (tests)")
  ap.add_argument("--list", action="store_true", help="print each file, not only counts")
  args = ap.parse_args(argv)
  roots = [pathlib.Path(p).resolve() for p in args.project_root] + (scan_roots(pathlib.Path(args.scan).resolve()) if args.scan else [])
  if not roots:
    ap.error("give --project-root or --scan")
  today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
  by = dt.date.fromisoformat(args.by) if args.by else None
  any_overdue = False
  for root in roots:
    now = due_files(root, today, args.window_days)
    later = due_files(root, by, args.window_days) if by else []
    early = early_review_by(root, args.window_days)
    any_overdue = any_overdue or bool(now)
    print(f"{root.name:28} overdue={len(now):<3} " + (f"due-by-{by}={len(later):<3} " if by else "") + f"early-review-by={len(early)}")
    if args.list:
      for rel in now:
        print(f"  overdue   {rel}")
      for rel in sorted(set(later) - set(now)):
        print(f"  due-by    {rel}")
      for line in early:
        print(f"  early     {line}")
  return 1 if any_overdue else 0


if __name__ == "__main__":
  if sys.version_info < REQUIRES_PYTHON:
    sys.exit(f"needs Python {'.'.join(map(str, REQUIRES_PYTHON))}+")
  sys.exit(main())
