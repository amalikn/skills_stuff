#!/usr/bin/env python3
"""Plan usable Ceph capacity per pool layout, after losing the largest failure domains, and check self-healing and min_size.

Usage: just ceph examples/ceph-capacity.json (or: <venv python> scripts/ceph_capacity.py <pools.json>)
Reads at most 1 MiB, 256 domains and 64 pools; prints JSON; never writes or connects.
Plan = (raw - largest f domains) / overhead * nearfull, where overhead is size for replicas or (k+m)/k for erasure coding.
Exit 0: every pool fits and heals, 1: a finding, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_DOMAINS = 256
MAX_POOLS = 64
NEARFULL_DEFAULT = 0.85  # Ceph mon_osd_nearfull_ratio default


def check_pools(data):
  """Compute plan capacity and layout findings for every pool against the shared failure domains.

  Args:
    data: Parsed JSON with schema_version, domains, pools and optional nearfull_ratio.
  Returns:
    Pair of (per-pool results, findings list).
  Raises:
    ValueError: When the schema or a value is invalid.
  """
  allowed = {"schema_version", "domains", "pools", "nearfull_ratio"}
  if not isinstance(data, dict) or not {"schema_version", "domains", "pools"} <= set(data) or set(data) - allowed:
    raise ValueError("expected schema_version, domains, pools and optional nearfull_ratio")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  nearfull = data.get("nearfull_ratio", NEARFULL_DEFAULT)
  if isinstance(nearfull, bool) or not isinstance(nearfull, (int, float)) or not 0.5 <= nearfull < 1:
    raise ValueError("nearfull_ratio must be 0.5..<1")
  domains = data["domains"]
  if not isinstance(domains, list) or not 1 <= len(domains) <= MAX_DOMAINS:
    raise ValueError(f"domains must contain 1..{MAX_DOMAINS} entries")
  sizes = []
  for domain in domains:
    if (
      not isinstance(domain, dict)
      or set(domain) != {"id", "raw_tb"}
      or isinstance(domain["raw_tb"], bool)
      or not isinstance(domain["raw_tb"], (int, float))
      or domain["raw_tb"] <= 0
    ):
      raise ValueError("each domain is {id, raw_tb > 0}")
    sizes.append(float(domain["raw_tb"]))
  pools = data["pools"]
  if not isinstance(pools, list) or not 1 <= len(pools) <= MAX_POOLS:
    raise ValueError(f"pools must contain 1..{MAX_POOLS} entries")
  raw, count = sum(sizes), len(sizes)
  results, findings = [], []
  for pool in pools:
    keys = set(pool) if isinstance(pool, dict) else set()
    if not {"id", "tolerate_domain_failures", "demand_tb"} <= keys or not (keys & {"size", "ec"}) or len(keys & {"size", "ec"}) != 1:
      raise ValueError("each pool needs id, tolerate_domain_failures, demand_tb and exactly one of size or ec {k, m}, optional min_size")
    if keys - {"id", "size", "ec", "min_size", "tolerate_domain_failures", "demand_tb"}:
      raise ValueError(f"{pool['id']}: unknown pool fields")
    name, failures = pool["id"], pool["tolerate_domain_failures"]
    if type(failures) is not int or not 0 <= failures < count:
      raise ValueError(f"{name}: tolerate_domain_failures must be an integer below the domain count")
    if "size" in pool:
      width = pool["size"]
      if type(width) is not int or not 1 <= width <= 10:
        raise ValueError(f"{name}: size must be an integer 1..10")
      overhead, floor_min = float(width), 2
      min_size = pool.get("min_size", width - width // 2)
    else:
      ec = pool["ec"]
      if not isinstance(ec, dict) or set(ec) != {"k", "m"} or any(type(ec[key]) is not int or ec[key] < 1 for key in ("k", "m")):
        raise ValueError(f"{name}: ec is {{k, m}} with positive integers")
      width, overhead, floor_min = ec["k"] + ec["m"], (ec["k"] + ec["m"]) / ec["k"], ec["k"] + 1
      min_size = pool.get("min_size", ec["k"] + 1)
    if type(min_size) is not int or not 1 <= min_size <= width:
      raise ValueError(f"{name}: min_size must be an integer 1..{width}")
    surviving = raw - sum(sorted(sizes, reverse=True)[:failures])
    plan = surviving / overhead * nearfull
    results.append(
      {
        "id": name,
        "width": width,
        "min_size": min_size,
        "raw_tb": round(raw, 3),
        "surviving_raw_tb": round(surviving, 3),
        "plan_tb": round(plan, 3),
        "demand_tb": pool["demand_tb"],
      }
    )
    if width > count:
      findings.append(f"{name}: {width} placements need {width} failure domains; only {count} exist")
    elif width + failures > count:
      findings.append(f"{name}: losing {failures} domain(s) leaves {count - failures} for {width} placements; data stays degraded until the domain returns")
    if min_size < floor_min:
      findings.append(f"{name}: min_size {min_size} is below {floor_min}; writes would be accepted with no redundancy")
    demand = pool["demand_tb"]
    if isinstance(demand, bool) or not isinstance(demand, (int, float)) or demand < 0:
      raise ValueError(f"{name}: demand_tb must be a number >= 0")
    if demand > plan:
      findings.append(f"{name}: demand {demand} TB exceeds the plan limit {plan:.2f} TB after losing {failures} domain(s)")
  return results, findings


def main():
  """Read the bounded JSON input and print the per-pool plan.

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
    results, findings = check_pools(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  report = {
    "status": "findings" if findings else "pass",
    "findings": findings,
    "pools": results,
    "elapsed_seconds": round(time.perf_counter() - started, 6),
    "limits": "Pools are assessed one at a time against all raw capacity; shared-OSD pools compete. No PG balance, BlueStore overhead, compression or performance model.",
  }
  print(json.dumps(report, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
