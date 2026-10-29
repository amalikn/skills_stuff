#!/usr/bin/env python3
"""Screen pooled memory and a serialized restore budget; no infrastructure access.

Usage: python3 scripts/capacity_check.py examples/capacity-plan.json
Reads at most 1 MiB, 1,000 nodes and 5,000 scenarios; prints JSON only.
Exit 0: modeled criteria pass, 1: modeled shortfall, 2: invalid input.
This is not a placement, quorum, storage-consistency or availability proof.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024


def number(value, label, minimum=0, maximum=None):
  """Check a finite numeric input within inclusive bounds.

  Args:
    value: Candidate JSON value.
    label: Field name for diagnostics.
    minimum: Inclusive lower bound.
    maximum: Optional inclusive upper bound.
  Returns:
    The value as a float.
  Raises:
    ValueError: When the value is not a finite number within bounds.
  """
  if isinstance(value, bool) or not isinstance(value, (int, float)):
    raise ValueError(f"{label} must be numeric")
  try:
    result = float(value)
  except OverflowError as error:
    raise ValueError(f"{label} is too large") from error
  if not math.isfinite(result) or result < minimum:
    raise ValueError(f"{label} must be finite and at least {minimum}")
  if maximum is not None and result > maximum:
    raise ValueError(f"{label} must be at most {maximum}")
  return result


def text(value, label):
  """Check a nonempty identifier.

  Args:
    value: Candidate JSON identifier.
    label: Field name for diagnostics.
  Returns:
    The original string.
  Raises:
    ValueError: When the value is not a nonempty string.
  """
  if not isinstance(value, str) or not value.strip():
    raise ValueError(f"{label} must be a nonempty string")
  return value


def check_capacity(data):
  """Compute each explicit failure scenario and optional restore estimate.

  Args:
    data: Parsed capacity-plan JSON object.
  Returns:
    Report dictionary with scenario results, restore result and findings.
  Raises:
    ValueError: When schema, identifiers, bounds or references are invalid.
  """
  required = {"schema_version", "nodes", "demand_gib", "headroom_fraction", "scenarios"}
  if not isinstance(data, dict) or not required <= set(data):
    raise ValueError("missing capacity plan fields")
  if set(data) - required - {"restore"}:
    raise ValueError("unknown capacity plan fields")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  demand = number(data["demand_gib"], "demand_gib")
  headroom = number(data["headroom_fraction"], "headroom_fraction", 0, 0.99)
  rows = data["nodes"]
  if not isinstance(rows, list) or not 1 <= len(rows) <= 1000:
    raise ValueError("nodes must contain 1..1000 entries")
  nodes, domains = {}, set()
  for row in rows:
    if not isinstance(row, dict) or set(row) != {"id", "domain", "memory_gib", "reserve_gib"}:
      raise ValueError("node requires only id, domain, memory_gib and reserve_gib")
    name = text(row["id"], "node id")
    domain = text(row["domain"], "node domain")
    if name in nodes:
      raise ValueError("duplicate node id")
    memory = number(row["memory_gib"], "memory_gib", 0.001)
    reserve = number(row["reserve_gib"], "reserve_gib", 0, memory)
    nodes[name] = (domain, memory - reserve)
    domains.add(domain)
  scenarios = data["scenarios"]
  if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 5000:
    raise ValueError("scenarios must contain 1..5000 entries")
  reports, findings, names = [], [], set()
  for row in scenarios:
    if not isinstance(row, dict) or set(row) != {"id", "failed_nodes", "failed_domains"}:
      raise ValueError("scenario requires id, failed_nodes and failed_domains")
    name = text(row["id"], "scenario id")
    if name in names:
      raise ValueError("duplicate scenario id")
    names.add(name)
    for field in ("failed_nodes", "failed_domains"):
      if not isinstance(row[field], list):
        raise ValueError(f"{field} must be a list")
      if not all(isinstance(item, str) and item.strip() for item in row[field]):
        raise ValueError(f"{field} must contain identifiers")
      if len(set(row[field])) != len(row[field]):
        raise ValueError(f"{field} contains duplicates")
    failed_nodes, failed_domains = set(row["failed_nodes"]), set(row["failed_domains"])
    if failed_nodes - nodes.keys() or failed_domains - domains:
      raise ValueError("scenario references unknown node/domain")
    available = math.fsum(capacity for node, (domain, capacity) in nodes.items() if node not in failed_nodes and domain not in failed_domains) * (1 - headroom)
    if not math.isfinite(available):
      raise ValueError("aggregate capacity is not finite")
    deficit = max(0, demand - available)
    reports.append({"id": name, "effective_memory_gib": available, "demand_gib": demand, "deficit_gib": deficit})
    if deficit > 0:
      findings.append(f"{name}: memory deficit {deficit:g} GiB")
  restore_report = None
  if "restore" in data:
    restore = data["restore"]
    keys = {"data_gib", "throughput_mbps", "efficiency", "fixed_seconds", "rto_seconds"}
    if not isinstance(restore, dict) or set(restore) != keys:
      raise ValueError("restore requires data_gib, throughput_mbps, efficiency, fixed_seconds, rto_seconds")
    size = number(restore["data_gib"], "data_gib")
    rate = number(restore["throughput_mbps"], "throughput_mbps", 0.000001)
    efficiency = number(restore["efficiency"], "efficiency", 0.000001, 1)
    fixed = number(restore["fixed_seconds"], "fixed_seconds")
    rto = number(restore["rto_seconds"], "rto_seconds", 0.000001)
    duration = fixed + size * (2**30) * 8 / (rate * 1_000_000 * efficiency)
    if not math.isfinite(duration):
      raise ValueError("restore estimate is not finite")
    restore_report = {"estimated_seconds": duration, "rto_seconds": rto, "exceeds_rto": duration > rto}
    if duration > rto:
      findings.append("serialized restore estimate exceeds RTO")
  return {"scenarios": reports, "restore": restore_report, "findings": findings}


def main():
  """Read the bounded input and print model results.

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
    report = check_capacity(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError, OverflowError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  report.update(
    {
      "status": "findings" if report["findings"] else "pass",
      "elapsed_seconds": round(time.perf_counter() - started, 6),
      "limits": "Pooled RAM and serialized restore only; no placement, quorum, CPU, storage or RPO proof.",
    }
  )
  print(json.dumps(report, indent=2))
  return 1 if report["findings"] else 0


if __name__ == "__main__":
  sys.exit(main())
