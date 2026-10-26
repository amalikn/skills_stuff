#!/usr/bin/env python3
"""Tabulate smc_change run records: result, phase times, whether the SMC rebooted, what held the lower dir, and the failure, one line per run.

Run it with python3 on the controller: smc_change_runs_table.py <runs_dir> [--mode apply] [--host SUBSTR]
  e.g. smc_change_runs_table.py .../roles/smc_change/files/changes/php-cve-2026-109618/runs
Reads the <host>-<change>-<mode>-<start>.json records in runs_dir (oldest first by start stamp). Read-only. A reboot is a changed boot_id
between the before- and after-probe; "?" when the run has no after-probe. Exit 0, or 2 on bad usage.
Written 2026-10-26 to answer "which runs rebooted, and did the ones that rebooted fail" across one change's rollout.
"""

import argparse
import glob
import json
import os
import sys


def phase_seconds(record):
  """Read a record's per-phase seconds.

  Args:
    record: one run record (dict).

  Returns:
    {phase number as str: whole seconds}, e.g. {"6": 184}.
  """
  out = {}
  for item in record.get("phase_timings") or []:
    name = str(item.get("phase", item.get("name", "")))
    out[name.split("/")[0].strip()] = round(float(item.get("seconds", 0)))
  return out


def row(path, record):
  """Build one table row from a record.

  Args:
    path: the record's file path.
    record: the parsed record.

  Returns:
    A dict with run, result, total, p6, p7, p8, p9, rebooted, busy and failure.
  """
  before = (record.get("before") or {}).get("boot_id")
  after = (record.get("after") or {}).get("boot_id")
  phases = phase_seconds(record)
  failure = record.get("failure") or {}
  busy = record.get("lower_busy") or {}
  return {
    "run": os.path.basename(path)[:-5],
    "result": str(record.get("result", "")),
    "total": round(float(record.get("elapsed_seconds") or 0)),
    "p6": phases.get("6", "-"),
    "p7": phases.get("7", "-"),
    "p8": phases.get("8", "-"),
    "p9": phases.get("9", "-"),
    "rebooted": "?" if not (before and after) else ("yes" if before != after else "no"),
    "busy": "; ".join(h[:40] for h in busy.get("holders", [])[:2]) if busy else "",
    "failure": (str(failure.get("stage", "")) + " " + str(failure.get("msg", ""))[:70]).strip() if isinstance(failure, dict) else "",
  }


def main(argv):
  """Print the table.

  Args:
    argv: command-line arguments without the program name.

  Returns:
    0, or 2 when runs_dir is not a directory.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("runs_dir")
  parser.add_argument("--mode", default="apply", help="record mode to list (apply, check, assess, verify, rollback; 'all' for every mode)")
  parser.add_argument("--host", default="", help="only records whose file name contains this")
  args = parser.parse_args(argv)
  if not os.path.isdir(args.runs_dir):
    print(f"not a directory: {args.runs_dir}", file=sys.stderr)
    return 2
  pattern = "*.json" if args.mode == "all" else f"*-{args.mode}-*.json"
  paths = [p for p in glob.glob(os.path.join(args.runs_dir, pattern)) if args.host in os.path.basename(p)]
  paths.sort(key=lambda p: os.path.basename(p).rsplit("-", 1)[-1])
  print(f"{'run':<64} {'result':<12} {'total':>5} {'p6':>4} {'p7':>4} {'p8':>4} {'p9':>4} reboot  busy / failure")
  for path in paths:
    try:
      with open(path) as handle:
        r = row(path, json.load(handle))
    except (OSError, ValueError) as exc:
      print(f"{os.path.basename(path):<64} unreadable: {exc}")
      continue
    print(
      f"{r['run']:<64} {r['result']:<12} {r['total']:>5} {r['p6']:>4} {r['p7']:>4} {r['p8']:>4} {r['p9']:>4} {r['rebooted']:<7} "
      f"{r['busy'] or r['failure']}"
    )
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
