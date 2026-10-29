#!/usr/bin/env python3
"""Check concrete IP segments for overlap and gateway errors without network access.

Usage: just ip-plan examples/ip-plan.json (or: <venv python> scripts/ip_plan_check.py <plan.json>)
Reads at most 1 MiB and 5,000 segments; prints JSON; never writes or connects.
Exit 0: no findings, 1: plan findings, 2: invalid input.
"""

import argparse
import ipaddress
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_SEGMENTS = 5000


def check_plan(data):
  """Validate a segment plan and find overlaps in each routing scope.

  Args:
    data: Parsed JSON object with schema_version and segments.
  Returns:
    A list of human-readable findings.
  Raises:
    ValueError: When schema, identities or addresses are invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "segments"}:
    raise ValueError("expected only schema_version and segments")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  segments = data["segments"]
  if not isinstance(segments, list) or not 1 <= len(segments) <= MAX_SEGMENTS:
    raise ValueError("segments must contain 1..5000 concrete segments")
  identities, groups, findings = set(), {}, []
  for segment in segments:
    if not isinstance(segment, dict) or not {"id", "scope", "cidr"} <= set(segment):
      raise ValueError("each segment needs id, scope and cidr")
    if set(segment) - {"id", "scope", "cidr", "gateway"}:
      raise ValueError("unknown segment fields")
    for key in ("id", "scope", "cidr"):
      if not isinstance(segment[key], str) or not segment[key].strip():
        raise ValueError(f"{key} must be a nonempty string")
    identity = f"{segment['scope']}/{segment['id']}"
    if identity in identities:
      raise ValueError("duplicate segment identity within scope")
    identities.add(identity)
    network = ipaddress.ip_network(segment["cidr"], strict=True)
    # RFC 7421: SLAAC and most host stacks need a /64 per segment; /127 point-to-point (RFC 6164) and /128 loopbacks are the exceptions.
    if network.version == 6 and network.prefixlen not in (64, 127, 128):
      findings.append(f"{identity}: IPv6 segment is /{network.prefixlen}; use /64 per segment (/127 links, /128 loopbacks)")
    groups.setdefault((segment["scope"], network.version), []).append((int(network.network_address), int(network.broadcast_address), segment["id"]))
    if "gateway" in segment:
      if not isinstance(segment["gateway"], str):
        raise ValueError("gateway must be an address string")
      gateway = ipaddress.ip_address(segment["gateway"])
      if gateway.version != network.version or gateway not in network:
        findings.append(f"{identity}: gateway outside segment or wrong family")
      elif network.version == 4 and network.prefixlen < 31 and gateway in (network.network_address, network.broadcast_address):
        findings.append(f"{identity}: gateway is IPv4 network/broadcast address")
  for (scope, family), intervals in sorted(groups.items()):
    # Carry the furthest endpoint, so nested segments cannot hide an overlap.
    end, previous = -1, ""
    for start, stop, name in sorted(intervals):
      if start <= end:
        findings.append(f"{scope} IPv{family}: {name} overlaps {previous}")
      if stop > end:
        end, previous = stop, name
  return findings


def main():
  """Read the bounded JSON input and print a deterministic decision report.

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
    data = json.loads(raw)
    findings = check_plan(data)
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  print(
    json.dumps(
      {
        "status": "findings" if findings else "pass",
        "findings": findings,
        "segments": len(data["segments"]),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "limits": "Concrete segments only; no routing, allocation hierarchy or utilization model.",
      },
      indent=2,
    )
  )
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
