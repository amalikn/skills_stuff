#!/usr/bin/env python3
"""Site power budget: PoE per switch against its PSE budget and port classes, and UPS load and runtime for the site.

Usage: just power examples/power-budget.json (or: <venv python> scripts/power_budget.py <site.json>)
Reads at most 1 MiB; prints JSON; never writes or connects.
PoE class power at the PSE (IEEE 802.3, via Ethernet Alliance 802.3bt overview, checked 2026-10-29): af/type 1 15.4 W, at/type 2 30 W,
bt type 3 60 W, bt type 4 90 W. UPS runtime here is linear (Wh x inverter efficiency / load); real batteries deliver less at high load.
Exit 0: within budget and policy, 1: a finding, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
PSE_CLASS_W = {"af": 15.4, "at": 30.0, "bt3": 60.0, "bt4": 90.0}


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
      raise ValueError(f"{obj.get('id', 'site')}: {key} is required")
    return float(default)
  value = obj[key]
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
    raise ValueError(f"{obj.get('id', 'site')}: {key} must be a number {low}..{high}")
  return float(value)


def check_site(data):
  """Check every switch's PoE budget and the UPS load and runtime.

  Args:
    data: Parsed JSON with schema_version, switches, other_loads_w and optional ups.
  Returns:
    Pair of (result dictionary, findings list).
  Raises:
    ValueError: When the schema or a value is invalid.
  """
  allowed = {"schema_version", "switches", "other_loads_w", "ups"}
  if not isinstance(data, dict) or not {"schema_version", "switches"} <= set(data) or set(data) - allowed:
    raise ValueError("expected schema_version and switches, optionally other_loads_w and ups")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  switches = data["switches"]
  if not isinstance(switches, list) or not 1 <= len(switches) <= 200:
    raise ValueError("switches must contain 1..200 entries")
  findings, rows, site_w = [], [], number(data, "other_loads_w", 0, 100000, 0)
  for switch in switches:
    if not isinstance(switch, dict) or not {"id", "base_w", "poe_budget_w", "ports"} <= set(switch):
      raise ValueError("each switch needs id, base_w, poe_budget_w and ports")
    ports = switch["ports"]
    if not isinstance(ports, list):
      raise ValueError(f"{switch['id']}: ports must be a list")
    drawn = 0.0
    for port in ports:
      if not isinstance(port, dict) or not {"device", "draw_w"} <= set(port):
        raise ValueError(f"{switch['id']}: each port needs device and draw_w, optional port_class and device_class")
      draw = number(port, "draw_w", 0, 100)
      drawn += draw
      port_class = port.get("port_class")
      if port_class is not None:
        if port_class not in PSE_CLASS_W:
          raise ValueError(f"{switch['id']}: port_class must be one of {sorted(PSE_CLASS_W)}")
        if draw > PSE_CLASS_W[port_class]:
          findings.append(f"{switch['id']} {port['device']}: draws {draw:g} W, above the {PSE_CLASS_W[port_class]:g} W a {port_class} port supplies")
    budget = number(switch, "poe_budget_w", 0, 10000)
    if drawn > budget:
      findings.append(f"{switch['id']}: PoE draw {drawn:.1f} W exceeds the {budget:.1f} W PSE budget")
    total = number(switch, "base_w", 0, 5000) + drawn
    site_w += total
    rows.append(
      {"id": switch["id"], "poe_draw_w": round(drawn, 1), "poe_budget_w": budget, "poe_headroom_w": round(budget - drawn, 1), "total_w": round(total, 1)}
    )
  result = {"switches": rows, "site_load_w": round(site_w, 1)}
  ups = data.get("ups")
  if ups is not None:
    if not isinstance(ups, dict):
      raise ValueError("ups is {va, power_factor, battery_wh, inverter_efficiency, max_load_fraction, required_runtime_min}")
    watts = number(ups, "va", 1, 1000000) * number(ups, "power_factor", 0.5, 1)
    load = site_w / watts
    runtime = number(ups, "battery_wh", 1, 10000000) * number(ups, "inverter_efficiency", 0.5, 1, 0.9) / site_w * 60 if site_w else None
    result["ups"] = {"rated_w": round(watts, 1), "load_fraction": round(load, 3), "linear_runtime_min": round(runtime, 1) if runtime else None}
    if load > number(ups, "max_load_fraction", 0.1, 1, 0.8):
      findings.append(f"UPS load {load:.0%} is above the {number(ups, 'max_load_fraction', 0.1, 1, 0.8):.0%} policy")
    if runtime is not None and "required_runtime_min" in ups and runtime < number(ups, "required_runtime_min", 0, 100000):
      findings.append(f"UPS linear runtime {runtime:.1f} min is below the required {ups['required_runtime_min']} min (and real runtime is lower)")
  return result, findings


def main():
  """Read the bounded JSON input and print the site power budget.

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
    result, findings = check_site(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  result.update(
    {
      "status": "findings" if findings else "pass",
      "findings": findings,
      "elapsed_seconds": round(time.perf_counter() - started, 6),
      "limits": "Measured or datasheet draw per device; cable loss is inside the class PSE figures. Battery runtime is non-linear: use the UPS maker's runtime table.",
    }
  )
  print(json.dumps(result, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
