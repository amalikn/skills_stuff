#!/usr/bin/env python3
"""Compute the payload MTU left after stacked encapsulations and compare it with what each path must carry.

Usage: just mtu examples/mtu-budget.json (or: <venv python> scripts/mtu_budget.py <budget.json>)
Reads at most 1 MiB and 500 paths; prints JSON; never writes or connects.
Overheads are fixed header sizes per encapsulation (no options); ESP layers assume AES-GCM with worst-case padding, other ciphers need a custom layer.
Exit 0: every path fits, 1: a path is short, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_PATHS = 500

# Bytes each encapsulation removes from the underlay IP MTU. Tunnels that carry an Ethernet frame count the inner 14-byte header.
OVERHEAD = {
  "wireguard-ipv4": 60,  # outer IPv4 20 + UDP 8 + WireGuard data header 16 + Poly1305 tag 16
  "wireguard-ipv6": 80,  # outer IPv6 40 + UDP 8 + 32
  "vxlan-ipv4": 50,  # outer IPv4 20 + UDP 8 + VXLAN 8 + inner Ethernet 14 (RFC 7348)
  "vxlan-ipv6": 70,  # outer IPv6 40 + UDP 8 + VXLAN 8 + inner Ethernet 14
  "geneve-ipv4": 50,  # outer IPv4 20 + UDP 8 + Geneve base 8 + inner Ethernet 14, no options (RFC 8926)
  "gre-ipv4": 24,  # outer IPv4 20 + GRE base 4 (RFC 2784), no key or sequence
  "gretap-ipv4": 38,  # gre-ipv4 24 + inner Ethernet 14
  "pppoe": 8,  # PPPoE 6 + PPP protocol 2 (RFC 2516)
  "mpls-label": 4,  # one label stack entry (RFC 3032)
  "dot1q-inner": 4,  # an 802.1Q tag carried inside a tunnelled Ethernet frame
  # ESP tunnel mode, AES-GCM (RFC 4106): outer IP + SPI/seq 8 + IV 8 + worst-case pad 3 + pad length/next header 2 + ICV 16.
  "esp-gcm-ipv4": 57,  # 54-57 depending on padding; worst case kept so the budget never overstates the payload
  "esp-gcm-ipv4-natt": 65,  # plus UDP 8 for NAT traversal (RFC 3948)
  "esp-gcm-ipv6": 77,
}


def check_budget(data):
  """Subtract each path's encapsulation stack from its underlay MTU and compare with the required payload.

  Args:
    data: Parsed JSON object with schema_version and paths.
  Returns:
    Pair of (per-path results, findings list).
  Raises:
    ValueError: When the schema, a layer name or a number is invalid.
  """
  if not isinstance(data, dict) or set(data) != {"schema_version", "paths"}:
    raise ValueError("expected only schema_version and paths")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  paths = data["paths"]
  if not isinstance(paths, list) or not 1 <= len(paths) <= MAX_PATHS:
    raise ValueError(f"paths must contain 1..{MAX_PATHS} entries")
  results, findings, seen = [], [], set()
  for path in paths:
    if not isinstance(path, dict) or set(path) != {"id", "underlay_mtu", "layers", "required_payload_mtu"}:
      raise ValueError("each path needs exactly id, underlay_mtu, layers and required_payload_mtu")
    if not isinstance(path["id"], str) or not path["id"].strip() or path["id"] in seen:
      raise ValueError("path id must be a unique nonempty string")
    seen.add(path["id"])
    for key in ("underlay_mtu", "required_payload_mtu"):
      if type(path[key]) is not int or not 68 <= path[key] <= 65535:
        raise ValueError(f"{path['id']}: {key} must be an integer 68..65535")
    if not isinstance(path["layers"], list):
      raise ValueError(f"{path['id']}: layers must be a list")
    total, steps = 0, []
    for layer in path["layers"]:
      if isinstance(layer, str):
        if layer not in OVERHEAD:
          raise ValueError(f"{path['id']}: unknown layer {layer!r}; give a custom {{name, bytes}} instead")
        name, size = layer, OVERHEAD[layer]
      elif (
        isinstance(layer, dict)
        and set(layer) == {"name", "bytes"}
        and isinstance(layer["name"], str)
        and type(layer["bytes"]) is int
        and 0 < layer["bytes"] < 1024
      ):
        name, size = layer["name"], layer["bytes"]
      else:
        raise ValueError(f"{path['id']}: a layer is a known name or {{name, bytes}} with 0 < bytes < 1024")
      total += size
      steps.append({"layer": name, "bytes": size})
    payload = path["underlay_mtu"] - total
    shortfall = path["required_payload_mtu"] - payload
    # TCP MSS clamp values for the inner packet: payload minus the IPv4 (20) or IPv6 (40) header and TCP (20), no options.
    results.append(
      {
        "id": path["id"],
        "underlay_mtu": path["underlay_mtu"],
        "overhead": total,
        "payload_mtu": payload,
        "tcp_mss_ipv4": payload - 40,
        "tcp_mss_ipv6": payload - 60,
        "layers": steps,
      }
    )
    if shortfall > 0:
      findings.append(
        f"{path['id']}: payload MTU {payload} is {shortfall} short of {path['required_payload_mtu']}; raise the underlay to {path['underlay_mtu'] + shortfall} or lower the inner MTU"
      )
  return results, findings


def main():
  """Read the bounded JSON input and print the per-path budget.

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
    results, findings = check_budget(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  report = {
    "status": "findings" if findings else "pass",
    "findings": findings,
    "paths": results,
    "elapsed_seconds": round(time.perf_counter() - started, 6),
    "limits": "Fixed header sizes only; no IP options, Geneve options, ESP padding or PMTUD behaviour. Prove with a do-not-fragment probe on the real path.",
  }
  print(json.dumps(report, indent=2))
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
