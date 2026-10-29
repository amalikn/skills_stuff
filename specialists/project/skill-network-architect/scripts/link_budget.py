#!/usr/bin/env python3
"""Point-to-point radio link budget: free-space loss, received level, fade margin and first-Fresnel-zone clearance.

Usage: just link-budget examples/link-budget.json (or: <venv python> scripts/link_budget.py <links.json>)
Reads at most 1 MiB and 1,000 links; prints JSON; never writes or connects.
Free space only: no rain, gas, multipath or diffraction model. Regulatory EIRP limits are not checked; read the regulator's instrument.
Exit 0: every link meets its margin and clearance, 1: a link falls short, 2: invalid input.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_LINKS = 1000
CLEARANCE_FRACTION = 0.6  # common planning rule: keep 60% of the first Fresnel zone clear
EARTH_RADIUS_KM = 6371.0
REQUIRED = {"id", "distance_km", "freq_mhz", "tx_power_dbm", "tx_gain_dbi", "rx_gain_dbi", "losses_db", "rx_sensitivity_dbm", "required_fade_margin_db"}
OPTIONAL = {"obstacles", "k_factor"}


def fspl_db(distance_km, freq_mhz):
  """Free-space path loss in dB (ITU-R P.525 form for km and MHz).

  Args:
    distance_km: Path length in kilometres.
    freq_mhz: Carrier frequency in megahertz.
  Returns:
    Loss in dB as a float.
  """
  return 20 * math.log10(distance_km) + 20 * math.log10(freq_mhz) + 32.44


def fresnel_radius_m(d1_km, d2_km, freq_mhz):
  """Radius of the first Fresnel zone at a point on the path.

  Args:
    d1_km: Distance from one end to the point, in kilometres.
    d2_km: Distance from the point to the other end, in kilometres.
    freq_mhz: Carrier frequency in megahertz.
  Returns:
    Radius in metres.
  """
  wavelength_m = 299.792458 / freq_mhz
  return math.sqrt(wavelength_m * d1_km * d2_km * 1000 / (d1_km + d2_km))


def earth_bulge_m(d1_km, d2_km, k_factor):
  """Height of the effective earth bulge at a point, for refraction factor k.

  Args:
    d1_km: Distance from one end, in kilometres.
    d2_km: Distance to the other end, in kilometres.
    k_factor: Effective earth radius factor (4/3 for standard atmosphere).
  Returns:
    Bulge in metres.
  """
  return d1_km * d2_km * 1000 / (2 * k_factor * EARTH_RADIUS_KM)


def number(link, key, low, high):
  """Read one numeric field and bound it.

  Args:
    link: The link object.
    key: Field name.
    low: Inclusive lower bound.
    high: Inclusive upper bound.
  Returns:
    The value as a float.
  Raises:
    ValueError: When the field is not a number within bounds.
  """
  value = link[key]
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
    raise ValueError(f"{link.get('id')}: {key} must be a number {low}..{high}")
  return float(value)


def check_links(data):
  """Compute the budget of every link and list the ones short of margin or clearance.

  Args:
    data: Parsed JSON object with schema_version and links.
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
    if not isinstance(link, dict) or not REQUIRED <= set(link) or set(link) - REQUIRED - OPTIONAL:
      raise ValueError(f"each link needs {sorted(REQUIRED)} and may add {sorted(OPTIONAL)}")
    name = link["id"]
    if not isinstance(name, str) or not name.strip() or name in seen:
      raise ValueError("link id must be a unique nonempty string")
    seen.add(name)
    distance = number(link, "distance_km", 0.001, 500)
    freq = number(link, "freq_mhz", 1, 300000)
    k_factor = number(link, "k_factor", 0.3, 10) if "k_factor" in link else 4 / 3
    loss = fspl_db(distance, freq)
    rx_level = (
      number(link, "tx_power_dbm", -30, 60)
      + number(link, "tx_gain_dbi", -10, 60)
      + number(link, "rx_gain_dbi", -10, 60)
      - number(link, "losses_db", 0, 100)
      - loss
    )
    margin = rx_level - number(link, "rx_sensitivity_dbm", -150, 0)
    required = number(link, "required_fade_margin_db", 0, 100)
    result = {
      "id": name,
      "fspl_db": round(loss, 2),
      "rx_level_dbm": round(rx_level, 2),
      "fade_margin_db": round(margin, 2),
      "midpoint_fresnel_m": round(fresnel_radius_m(distance / 2, distance / 2, freq), 2),
      "obstacles": [],
    }
    if margin < required:
      findings.append(f"{name}: fade margin {margin:.1f} dB is below the required {required:.1f} dB")
    obstacles = link.get("obstacles", [])
    if not isinstance(obstacles, list):
      raise ValueError(f"{name}: obstacles must be a list")
    for obstacle in obstacles:
      if not isinstance(obstacle, dict) or set(obstacle) != {"d1_km", "clearance_m"}:
        raise ValueError(f"{name}: an obstacle is {{d1_km, clearance_m}} (clearance below the straight line of sight, curvature excluded)")
      d1 = number(obstacle, "d1_km", 0, distance)
      if not 0 < d1 < distance:
        raise ValueError(f"{name}: obstacle d1_km must lie strictly inside the path")
      radius = fresnel_radius_m(d1, distance - d1, freq)
      effective = number(obstacle, "clearance_m", -10000, 10000) - earth_bulge_m(d1, distance - d1, k_factor)
      ratio = effective / radius
      result["obstacles"].append(
        {"d1_km": d1, "fresnel_radius_m": round(radius, 2), "effective_clearance_m": round(effective, 2), "clear_fraction": round(ratio, 3)}
      )
      if ratio < CLEARANCE_FRACTION:
        findings.append(f"{name}: obstacle at {d1:g} km clears {ratio:.0%} of the first Fresnel zone (planning rule {CLEARANCE_FRACTION:.0%})")
    results.append(result)
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
    "limits": "Free-space model with k-factor earth bulge; no rain fade (ITU-R P.530/P.838), multipath, diffraction or regulatory EIRP check. Survey before committing.",
  }
  print(json.dumps(report, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
