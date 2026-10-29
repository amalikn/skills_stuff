#!/usr/bin/env python3
"""Composite availability of a series/parallel block model, with expected downtime per year, compared with a target.

Usage: just availability examples/availability.json (or: <venv python> scripts/availability.py <model.json>)
Shared helper: canonical in skill-network-architect, symlinked into skill-systems-architect.
Reads at most 1 MiB and 2,000 blocks; prints JSON; never writes or connects.
Exit 0: target met, 1: target missed, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_BLOCKS = 2000
MAX_DEPTH = 20
MINUTES_PER_YEAR = 365.25 * 24 * 60


def evaluate(block, counter, depth=0):
  """Reduce one block to its availability: a component, all-of (series) or any-of (parallel).

  Args:
    block: {name, availability} | {series: [blocks]} | {parallel: [blocks]}.
    counter: One-item list counting blocks seen, shared across the walk.
    depth: Current nesting depth.
  Returns:
    Availability as a float in [0, 1].
  Raises:
    ValueError: When a block is malformed, too deep or the model too large.
  """
  counter[0] += 1
  if counter[0] > MAX_BLOCKS or depth > MAX_DEPTH:
    raise ValueError(f"model exceeds {MAX_BLOCKS} blocks or depth {MAX_DEPTH}")
  if not isinstance(block, dict) or len(block) not in (1, 2):
    raise ValueError("a block is {name, availability}, {series: [...]} or {parallel: [...]}")
  if set(block) == {"name", "availability"}:
    value = block["availability"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
      raise ValueError(f"{block['name']}: availability must be a fraction 0..1")
    return float(value)
  if len(block) != 1:
    raise ValueError("a component block has exactly name and availability")
  kind, children = next(iter(block.items()))
  if kind not in ("series", "parallel") or not isinstance(children, list) or not children:
    raise ValueError("series and parallel need a nonempty list of blocks")
  values = [evaluate(child, counter, depth + 1) for child in children]
  product = 1.0
  if kind == "series":
    for value in values:
      product *= value
    return product
  for value in values:
    product *= 1 - value
  return 1 - product


def check_model(data):
  """Evaluate the model and compare the result with the target.

  Args:
    data: Parsed JSON object with schema_version, target and model.
  Returns:
    Pair of (result dictionary, findings list).
  Raises:
    ValueError: When the schema or a block is invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "target", "model"}:
    raise ValueError("expected only schema_version, target and model")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  target = data["target"]
  if isinstance(target, bool) or not isinstance(target, (int, float)) or not 0 < target < 1:
    raise ValueError("target must be a fraction strictly between 0 and 1")
  counter = [0]
  value = evaluate(data["model"], counter)
  result = {
    "availability": round(value, 9),
    "downtime_minutes_per_year": round((1 - value) * MINUTES_PER_YEAR, 2),
    "target": target,
    "target_downtime_minutes_per_year": round((1 - target) * MINUTES_PER_YEAR, 2),
    "blocks": counter[0],
  }
  findings = [] if value >= target else [f"composite availability {value:.6f} misses target {target}"]
  return result, findings


def main():
  """Read the bounded JSON input and print the composite availability.

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
    result, findings = check_model(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  result.update(
    {
      "status": "findings" if findings else "pass",
      "findings": findings,
      "elapsed_seconds": round(time.perf_counter() - started, 6),
      "limits": "Assumes independent failures and steady state; correlated power, path, software or operator failures break the parallel formula. Model them as series blocks.",
    }
  )
  print(json.dumps(result, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
