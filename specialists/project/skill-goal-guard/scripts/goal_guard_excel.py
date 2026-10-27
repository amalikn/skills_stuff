#!/usr/bin/env python3
"""Generate the management workbook sample (.xlsx) from a spoke's milestone links (pilot feature 34, step 7).

Usage:
  python scripts/goal_guard_excel.py --project examples/project_stuff/apn/demo-spoke --out /tmp/gg-sample.xlsx [--apply]
  (or `just excel <project> <out>`)

Inputs:
  --project DIR         the spoke folder (.gg/mappings.yaml milestones, .gg/internal-targets.yaml)
  --out FILE            the workbook to write
  --date YYYY-MM-DD     judge risk on this date (default today)
  --include-internal    add the owner's private internal targets (left out by default, DATE-006)
  Example: python scripts/goal_guard_excel.py --project examples/project_stuff/apn/demo-spoke --out /tmp/gg-sample.xlsx --date 2026-12-05

Safety: prints the rows it would write; writes the one --out file only with --apply, refusing to overwrite an existing file. It
never edits the issued workbook, the hub plan or Vikunja. Compare the output with the issued workbook before any claim of reproduction.
"""

import argparse
import datetime as dt
from pathlib import Path

from goal_guard_lib import cli, excel, project, records
from goal_guard_lib.errors import WriteRefused


def main() -> int:
  """Build the rows and, with --apply, write the workbook.

  Returns:
    0 on success.

  Raises:
    WriteRefused: --out already exists.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--project", type=Path, required=True)
  parser.add_argument("--out", type=Path, required=True)
  parser.add_argument("--date")
  parser.add_argument("--include-internal", action="store_true")
  parser.add_argument("--apply", action="store_true")
  args = parser.parse_args()
  proj = project.load(args.project)
  today = records.parse_date(args.date, "--date") if args.date else dt.date.today()
  table = excel.rows(proj, today, args.include_internal)
  generated = dt.datetime.now().astimezone().isoformat(timespec="seconds")
  if args.apply:
    if args.out.exists():
      raise WriteRefused(f"{args.out} exists; choose a new file name (generated exports are new versions)")
    excel.write(args.out, proj, table, generated)
  cli.emit({"applied": args.apply, "out": str(args.out), "generated_at": generated, "rows": table})
  return cli.EXIT_OK


if __name__ == "__main__":
  cli.run(main)
