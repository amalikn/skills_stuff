#!/usr/bin/env python3
"""Restore time per phase against the RTO, for each dataset and recovery path, without a capacity model.

Usage: just restore examples/restore-time.json (or: <venv python> scripts/restore_time.py <plan.json>)
Reads at most 1 MiB and 200 plans; prints JSON; never writes or connects.
Transfer seconds = data_gib x 2^30 x 8 / (throughput_mbps x 10^6 x efficiency x streams_factor); the other phases are timed inputs
(detect, decide, provision, replay, verify), because a restore is late as often from them as from the copy.
Exit 0: every plan meets its RTO, 1: a plan misses, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_PLANS = 200
PHASES = ("detect_s", "decide_s", "provision_s", "replay_s", "verify_s")


def number(obj, key, low, high, default=None):
  """Read one bounded number, or its default when absent.

  Args:
    obj: Object holding the field.
    key: Field name.
    low: Inclusive lower bound.
    high: Inclusive upper bound.
    default: Value used when absent; None makes it required.
  Returns:
    The value as a float.
  Raises:
    ValueError: When missing, not a number or out of bounds.
  """
  if key not in obj:
    if default is None:
      raise ValueError(f"{obj.get('id', '?')}: {key} is required")
    return float(default)
  value = obj[key]
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
    raise ValueError(f"{obj.get('id', '?')}: {key} must be a number {low}..{high}")
  return float(value)


def check_plans(data):
  """Time every phase of every restore plan and compare the total with its RTO.

  Args:
    data: Parsed JSON with schema_version and plans.
  Returns:
    Pair of (per-plan results, findings list).
  Raises:
    ValueError: When the schema or a value is invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "plans"}:
    raise ValueError("expected only schema_version and plans")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  plans = data["plans"]
  if not isinstance(plans, list) or not 1 <= len(plans) <= MAX_PLANS:
    raise ValueError(f"plans must contain 1..{MAX_PLANS} entries")
  allowed = {"id", "data_gib", "throughput_mbps", "efficiency", "parallel_streams", "stream_scaling", "rto_s", *PHASES}
  results, findings, seen = [], [], set()
  for plan in plans:
    if not isinstance(plan, dict) or not {"id", "data_gib", "throughput_mbps", "rto_s"} <= set(plan) or set(plan) - allowed:
      raise ValueError(f"each plan needs id, data_gib, throughput_mbps, rto_s and may add {sorted(allowed - {'id', 'data_gib', 'throughput_mbps', 'rto_s'})}")
    name = plan["id"]
    if not isinstance(name, str) or not name or name in seen:
      raise ValueError("plan id must be a unique nonempty string")
    seen.add(name)
    streams = number(plan, "parallel_streams", 1, 256, 1)
    # Streams rarely scale linearly: the shared link, the target disks or the repository cap them. 1.0 = linear, 0 = no gain.
    factor = 1 + (streams - 1) * number(plan, "stream_scaling", 0, 1, 0)
    rate_bps = number(plan, "throughput_mbps", 0.001, 10000000) * 1e6 * number(plan, "efficiency", 0.05, 1, 0.8) * factor
    transfer = number(plan, "data_gib", 0, 10000000) * 2**30 * 8 / rate_bps
    phases = {key[:-2]: number(plan, key, 0, 10000000, 0) for key in PHASES}
    total = transfer + sum(phases.values())
    rto = number(plan, "rto_s", 1, 100000000)
    share = {phase: round(seconds / total, 3) for phase, seconds in {**phases, "transfer": transfer}.items()} if total else {}
    results.append(
      {
        "id": name,
        "transfer_s": round(transfer, 1),
        "phases_s": phases,
        "total_s": round(total, 1),
        "rto_s": rto,
        "slack_s": round(rto - total, 1),
        "largest_phase": max(share, key=share.get) if share else None,
      }
    )
    if total > rto:
      findings.append(
        f"{name}: restore takes {total:.0f} s against an RTO of {rto:.0f} s ({total - rto:.0f} s late; largest phase {max(share, key=share.get)})"
      )
  return results, findings


def main():
  """Read the bounded JSON input and print the per-plan timing.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("input", type=Path)
  args = parser.parse_args()
  started = time.perf_counter()
  try:
    with args.input.open("rb") as handle:
      raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
      raise ValueError("input exceeds 1 MiB")
    results, findings = check_plans(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  report = {
    "status": "findings" if findings else "pass",
    "findings": findings,
    "plans": results,
    "elapsed_seconds": round(time.perf_counter() - started, 6),
    "limits": "An estimate from timed inputs; only a measured restore drill proves the RTO. Phase times should come from the last drill, not from hope.",
  }
  print(json.dumps(report, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
