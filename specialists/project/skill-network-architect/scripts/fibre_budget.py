#!/usr/bin/env python3
"""Fibre link loss budget: worst-case plant loss against the optic's power budget, with margin.

Usage: just fibre examples/fibre-budget.json (or: <venv python> scripts/fibre_budget.py <links.json>)
Reads at most 1 MiB and 500 links; prints JSON; never writes or connects.
Defaults are the TIA-568 maximum acceptable values (via the Fiber Optic Association loss-budget page, checked 2026-10-29):
fibre 3.5 dB/km multimode at 850 nm, 1.5 at 1300 nm, 1.0 singlemode premises, 0.5 singlemode outside plant; 0.75 dB per mated connector pair;
0.3 dB per splice. Override any of them per link with measured or datasheet values.
Exit 0: every link has its required margin, 1: a link falls short, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_LINKS = 500
ATTENUATION = {"mm-850": 3.5, "mm-1300": 1.5, "sm-premises": 1.0, "sm-osp": 0.5}  # dB/km, TIA-568 maximum
CONNECTOR_DB = 0.75
SPLICE_DB = 0.3
FIELDS = {"id", "fibre", "length_km", "connections", "splices", "tx_min_dbm", "rx_sensitivity_dbm", "required_margin_db"}
OPTIONAL = {"attenuation_db_km", "connector_db", "splice_db", "other_db", "max_channel_loss_db"}


def value(link, key, low, high, default=None):
  """Read one bounded number, or its default when absent.

  Args:
    link: Link object.
    key: Field name.
    low: Inclusive lower bound.
    high: Inclusive upper bound.
    default: Value used when the key is absent; None makes it required.
  Returns:
    The value as a float.
  Raises:
    ValueError: When the value is missing, not a number or out of bounds.
  """
  if key not in link:
    if default is None:
      raise ValueError(f"{link.get('id')}: {key} is required")
    return float(default)
  number = link[key]
  if isinstance(number, bool) or not isinstance(number, (int, float)) or not low <= number <= high:
    raise ValueError(f"{link.get('id')}: {key} must be a number {low}..{high}")
  return float(number)


def check_links(data):
  """Compute worst-case loss and margin for every link.

  Args:
    data: Parsed JSON with schema_version and links.
  Returns:
    Pair of (per-link results, findings list).
  Raises:
    ValueError: When the schema or a value is invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "links"}:
    raise ValueError("expected only schema_version and links")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  links = data["links"]
  if not isinstance(links, list) or not 1 <= len(links) <= MAX_LINKS:
    raise ValueError(f"links must contain 1..{MAX_LINKS} entries")
  results, findings, seen = [], [], set()
  for link in links:
    if not isinstance(link, dict) or not FIELDS <= set(link) or set(link) - FIELDS - OPTIONAL:
      raise ValueError(f"each link needs {sorted(FIELDS)} and may add {sorted(OPTIONAL)}")
    name = link["id"]
    if not isinstance(name, str) or not name or name in seen:
      raise ValueError("link id must be a unique nonempty string")
    seen.add(name)
    if link["fibre"] not in ATTENUATION:
      raise ValueError(f"{name}: fibre must be one of {sorted(ATTENUATION)}")
    for key in ("connections", "splices"):
      if type(link[key]) is not int or not 0 <= link[key] <= 100:
        raise ValueError(f"{name}: {key} must be an integer 0..100")
    length = value(link, "length_km", 0, 200)
    fibre_db = length * value(link, "attenuation_db_km", 0, 10, ATTENUATION[link["fibre"]])
    connection_db = link["connections"] * value(link, "connector_db", 0, 3, CONNECTOR_DB)
    splice_db = link["splices"] * value(link, "splice_db", 0, 3, SPLICE_DB)
    loss = fibre_db + connection_db + splice_db + value(link, "other_db", 0, 50, 0)
    budget = value(link, "tx_min_dbm", -40, 20) - value(link, "rx_sensitivity_dbm", -60, 0)
    margin = budget - loss
    required = value(link, "required_margin_db", 0, 20)
    result = {
      "id": name,
      "fibre_db": round(fibre_db, 2),
      "connections_db": round(connection_db, 2),
      "splices_db": round(splice_db, 2),
      "plant_loss_db": round(loss, 2),
      "power_budget_db": round(budget, 2),
      "margin_db": round(margin, 2),
    }
    results.append(result)
    if margin < required:
      findings.append(f"{name}: margin {margin:.2f} dB is below the required {required:.2f} dB (plant loss {loss:.2f} dB, budget {budget:.2f} dB)")
    if "max_channel_loss_db" in link:
      limit = value(link, "max_channel_loss_db", 0, 50)
      if loss > limit:
        findings.append(f"{name}: plant loss {loss:.2f} dB exceeds the PHY channel insertion-loss limit {limit:.2f} dB")
  return results, findings


def main():
  """Read the bounded JSON input and print the per-link budget.

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
    results, findings = check_links(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  report = {
    "status": "findings" if findings else "pass",
    "findings": findings,
    "links": results,
    "elapsed_seconds": round(time.perf_counter() - started, 6),
    "limits": "Worst-case passive loss only; no dispersion or bandwidth limit (high-speed multimode reach is set by the PHY, not loss). Prove with an OLTS test.",
  }
  print(json.dumps(report, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
