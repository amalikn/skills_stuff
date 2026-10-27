#!/usr/bin/env python3
"""Compare two sets of smc_change run records, ignoring what changes run to run, to prove a refactor changed no behaviour.

Run it with python3 on the controller: smc_change_compare_records.py <before_dir> <after_dir>
  e.g. run the same check/verify runs with -e smc_change_report_dir=<before_dir>, change the role, rerun with <after_dir>, then compare.
Both dirs hold <change>/runs/<flavor>/records/<host>-<change>-<mode>-<start>.json records (older: runs/records/, runs/ or <change>/); records are paired by host, change and mode. Read-only.
Ignored fields: timestamps (epoch, start, end), free space, log positions and hit counts (live traffic), samples, page sizes, and summary
lines that report new log lines or free space. Exit 0 when every pair is identical, 1 when any differs or has no partner, 2 on bad usage.
"""

import glob
import json
import os
import re
import sys

VOLATILE = {"epoch", "free_mb", "inode", "lines", "new", "start", "end", "samples", "bytes", "hits", "run"}
COMPARED = ("result", "gates", "before", "after", "plan")


def norm(obj):
  """Drop volatile fields and volatile summary lines from a record value, recursively.

  Args:
    obj: any JSON value from a record.

  Returns:
    the value without volatile parts.
  """
  if isinstance(obj, dict):
    return {k: norm(v) for k, v in obj.items() if k not in VOLATILE}
  if isinstance(obj, list):
    return [norm(x) for x in obj if not (isinstance(x, str) and ("new line" in x or "MB free" in x))]
  return obj


def load(root):
  """Read every record under root, keyed by (host, change, mode).

  Args:
    root: a report dir (the -e smc_change_report_dir of a set of runs).

  Returns:
    {(host, change, mode): normalised record}; the newest record wins when a key repeats.
  """
  out = {}
  layouts = (("*", "runs", "*", "records", "*.json"), ("*", "runs", "records", "*.json"), ("*", "runs", "*.json"), ("*", "*.json"))
  paths = [p for layout in layouts for p in glob.glob(os.path.join(root, *layout)) if "-" in os.path.basename(p)]
  for path in sorted(paths, key=os.path.basename):
    with open(path, encoding="utf-8") as handle:
      rec = json.load(handle)
    out[(rec.get("host"), rec.get("change"), rec.get("mode"))] = {k: norm(rec.get(k)) for k in COMPARED}
  return out


def diff(a, b, path=""):
  """List the differences between two normalised values.

  Args:
    a: value from the before set.
    b: value from the after set.
    path: dotted path of the value, for the messages.

  Returns:
    list of readable difference lines (empty when equal).
  """
  if isinstance(a, dict) and isinstance(b, dict):
    lines = []
    for k in sorted(set(a) | set(b)):
      if k not in a:
        lines.append(f"+ {path}{k}")
      elif k not in b:
        lines.append(f"- {path}{k}")
      else:
        lines += diff(a[k], b[k], f"{path}{k}.")
    return lines
  return [] if a == b else [f"~ {path.rstrip('.')}: {str(a)[:80]} | {str(b)[:80]}"]


def main(argv):
  """Compare the record sets named on the command line.

  Args:
    argv: [before_dir, after_dir].

  Returns:
    exit status: 0 identical, 1 differences or unpaired records, 2 bad usage.
  """
  if len(argv) != 2 or not all(os.path.isdir(d) for d in argv):
    print(__doc__.strip().split("\n")[2], file=sys.stderr)
    return 2
  before, after = load(argv[0]), load(argv[1])
  status = 0
  for key in sorted(set(before) | set(after), key=lambda k: tuple(str(x) for x in k)):
    label = " ".join(str(x) for x in key)
    if key not in before or key not in after:
      print(f"{label}: only in {'after' if key not in before else 'before'}")
      status = 1
      continue
    lines = diff(before[key], after[key])
    print(f"{label}: {'IDENTICAL' if not lines else 'DIFFERENT'}")
    for line in lines[:20]:
      flat = re.sub(r"\s+", " ", line)
      print(f"  {flat}")
    status = status or (1 if lines else 0)
  return status


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
