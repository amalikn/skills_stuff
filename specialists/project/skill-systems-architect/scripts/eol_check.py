#!/usr/bin/env python3
"""End-of-life register check: components past end of support, inside the warning window, or with no owner or plan.

Usage: just eol examples/eol-register.json [--today 2026-10-29] (or: <venv python> scripts/eol_check.py <register.json> [--today YYYY-MM-DD])
Reads at most 1 MiB and 5,000 entries; prints JSON; never writes or connects. Dates come from the register, which cites its source per entry.
Exit 0: nothing past end of support, 1: a component is past it or a required field is missing, 2: invalid input.
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_ENTRIES = 5000
REQUIRED = {"id", "product", "version", "end_of_support", "source", "owner"}
OPTIONAL = {"extended_until", "plan", "count"}


def parse_day(text, field, name):
  """Parse an ISO date.

  Args:
    text: Date string (YYYY-MM-DD).
    field: Field name, for the error.
    name: Entry id, for the error.
  Returns:
    A date.
  Raises:
    ValueError: When the string is not an ISO date.
  """
  try:
    return date.fromisoformat(text)
  except (TypeError, ValueError):
    raise ValueError(f"{name}: {field} must be YYYY-MM-DD") from None


def check_register(data, today):
  """Classify every entry by days to the end of its support (extended support counts when present).

  Args:
    data: Parsed JSON with schema_version, warn_days and entries.
    today: Date to measure from.
  Returns:
    Pair of (result dictionary, findings list).
  Raises:
    ValueError: When the schema or a value is invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "warn_days", "entries"}:
    raise ValueError("expected only schema_version, warn_days and entries")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  warn = data["warn_days"]
  if type(warn) is not int or not 0 <= warn <= 3650:
    raise ValueError("warn_days must be an integer 0..3650")
  entries = data["entries"]
  if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_ENTRIES:
    raise ValueError(f"entries must contain 1..{MAX_ENTRIES} items")
  rows, findings, seen = [], [], set()
  buckets = {"past": 0, "warning": 0, "ok": 0}
  for entry in entries:
    if not isinstance(entry, dict) or not REQUIRED <= set(entry) or set(entry) - REQUIRED - OPTIONAL:
      raise ValueError(f"each entry needs {sorted(REQUIRED)} and may add {sorted(OPTIONAL)}")
    name = entry["id"]
    if not isinstance(name, str) or not name or name in seen:
      raise ValueError("entry id must be a unique nonempty string")
    seen.add(name)
    end = parse_day(entry["end_of_support"], "end_of_support", name)
    effective = parse_day(entry["extended_until"], "extended_until", name) if entry.get("extended_until") else end
    days = (effective - today).days
    state = "past" if days < 0 else "warning" if days <= warn else "ok"
    buckets[state] += 1
    rows.append(
      {"id": name, "product": entry["product"], "version": entry["version"], "support_ends": effective.isoformat(), "days_left": days, "state": state}
    )
    label = f"{name} ({entry['product']} {entry['version']})"
    if state == "past":
      findings.append(f"{label}: support ended {effective.isoformat()}, {-days} days ago; plan: {entry.get('plan') or 'NONE'}")
    elif state == "warning" and not entry.get("plan"):
      findings.append(f"{label}: support ends in {days} days and the entry has no plan")
    if not str(entry["owner"]).strip() or not str(entry["source"]).strip():
      findings.append(f"{label}: owner and source must not be empty")
  failed = [finding for finding in findings if "support ended" in finding or "must not be empty" in finding]
  return {"today": today.isoformat(), "warn_days": warn, "counts": buckets, "entries": sorted(rows, key=lambda row: row["days_left"])}, findings, failed


def main():
  """Read the register and print entries ordered by days left.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("input", type=Path)
  parser.add_argument("--today", help="measure from this date (YYYY-MM-DD) instead of the system date")
  args = parser.parse_args()
  started = time.perf_counter()
  try:
    today = parse_day(args.today, "--today", "cli") if args.today else date.today()
    with args.input.open("rb") as handle:
      raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
      raise ValueError("input exceeds 1 MiB")
    result, findings, failed = check_register(json.loads(raw), today)
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  result.update(
    {
      "status": "findings" if failed else ("warnings" if findings else "pass"),
      "findings": findings,
      "elapsed_seconds": round(time.perf_counter() - started, 6),
      "limits": "Only as current as the register: each entry cites its vendor lifecycle page; recheck those when a date nears.",
    }
  )
  print(json.dumps(result, indent=2))
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
