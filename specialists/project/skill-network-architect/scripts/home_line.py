#!/usr/bin/env python3
"""Classify a home or small-site internet line from a saved traceroute: public IPv4, CGNAT, or double NAT behind the router.

Usage: just home-line examples/home-line.json (or: <venv python> scripts/home_line.py <line.json>)
Input JSON: {"schema_version": 1, "traceroute": "<text of `traceroute -n -m 5 -q 1 1.1.1.1`>", "public_ipv4": "<what an
echo service reports>", "router_wan_ipv4": "<optional: the WAN address on the router's status page>", "global_ipv6": <optional bool>}.
Reads at most 1 MiB; prints JSON; never writes or connects (run the traceroute and the echo lookup yourself first).
Verdict rules: hop 1 is the LAN router; the first hop after it that answers decides. 100.64.0.0/10 there means CGNAT (RFC 6598);
an RFC 1918 address means a second NAT (a modem or ISP router in front); a public address means the router likely holds a public
IPv4. A router WAN address equal to the public address confirms it; one in 100.64.0.0/10 or RFC 1918 overrides the hops.
Exit 0: public IPv4 (likely or confirmed), 1: CGNAT or double NAT, 2: invalid input or no hop after the router answered.
"""

import argparse
import ipaddress
import json
import re
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
CGNAT = ipaddress.ip_network("100.64.0.0/10")
RFC1918 = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
HOP = re.compile(r"^\s*(\d+)\s+(\S+)")


def kind(addr: str) -> str:
  """Name the address class that matters for reachability.

  Args:
    addr: an IPv4 address as text.

  Returns:
    "cgnat", "private", "public" or "other" (loopback, link-local, reserved).

  Raises:
    ValueError: addr is not an IPv4 address.
  """
  ip = ipaddress.IPv4Address(addr)
  if ip in CGNAT:
    return "cgnat"
  # Explicit RFC 1918 nets: ipaddress's is_private also covers the RFC 5737 documentation ranges, which stand for public addresses.
  if any(ip in n for n in RFC1918):
    return "private"
  if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:
    return "other"
  return "public"


def hops(text: str) -> list[tuple[int, str]]:
  """Parse `traceroute -n` output into (hop number, address) pairs, skipping hops that did not answer (`*`).

  Args:
    text: traceroute output.

  Returns:
    The answering hops in order.

  Raises:
    Nothing; lines that are not hops are skipped.
  """
  out = []
  for line in text.splitlines():
    m = HOP.match(line)
    if not m or m.group(2) == "*":
      continue
    try:
      ipaddress.IPv4Address(m.group(2))
    except ValueError:
      continue
    out.append((int(m.group(1)), m.group(2)))
  return out


def classify(line: dict) -> dict:
  """Decide the line's verdict from the hops and the optional router WAN address.

  Args:
    line: the parsed input object.

  Returns:
    A result with verdict, evidence, findings and limits.

  Raises:
    ValueError: a malformed field.
  """
  found = hops(str(line.get("traceroute", "")))
  public = line.get("public_ipv4")
  if public is not None and kind(public) != "public":
    raise ValueError(f"public_ipv4 {public} is not a public address")
  wan = line.get("router_wan_ipv4")
  findings, verdict, evidence = [], "unknown", ""
  after = [(n, a) for n, a in found if n >= 2]
  if found and kind(found[0][1]) != "private":
    findings.append(f"hop {found[0][0]} ({found[0][1]}) is not a private address: is the traceroute from inside the LAN?")
  if after:
    n, a = after[0]
    k = kind(a)
    verdict = {"cgnat": "cgnat", "private": "double-nat", "public": "public-likely"}.get(k, "unknown")
    evidence = f"first answering hop after the router: hop {n} {a} ({k})"
  if wan:
    wk = kind(wan)
    if wk == "cgnat":
      verdict, evidence = "cgnat", f"router WAN {wan} is in 100.64.0.0/10"
    elif wk == "private":
      verdict, evidence = "double-nat", f"router WAN {wan} is a private address"
    elif public and wan == public:
      verdict, evidence = "public-confirmed", f"router WAN {wan} equals the public address"
    elif public:
      findings.append(f"router WAN {wan} differs from the public address {public}: a NAT sits further upstream")
      verdict = "cgnat" if verdict == "public-likely" else verdict
  if verdict in ("cgnat", "double-nat"):
    findings.append("inbound connections (a WireGuard port forward) will not reach this line without a relay, an overlay, or a bridge mode")
  ipv6 = line.get("global_ipv6")
  if ipv6 is False:
    findings.append("no global IPv6: an IPv6-only path is not an option")
  return {
    "status": "ok" if verdict != "unknown" else "invalid",
    "verdict": verdict,
    "evidence": evidence,
    "public_ipv4": public,
    "findings": findings,
    "limits": "a public-likely verdict without router_wan_ipv4 is an inference; a static address is the ISP's statement, not visible here",
  }


def main(argv: list[str]) -> int:
  """Read the input file, classify and print the result.

  Args:
    argv: command-line arguments.

  Returns:
    0 public, 1 CGNAT or double NAT, 2 invalid or undecided.

  Raises:
    Nothing; errors become exit 2.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("line", type=Path)
  args = ap.parse_args(argv)
  started = time.monotonic()
  try:
    if args.line.stat().st_size > MAX_BYTES:
      raise ValueError("input over 1 MiB")
    data = json.loads(args.line.read_text())
    if data.get("schema_version") != 1:
      raise ValueError("schema_version must be 1")
    result = classify(data)
  except (OSError, ValueError, json.JSONDecodeError) as e:
    print(json.dumps({"status": "invalid", "error": str(e)}))
    return 2
  result["elapsed_seconds"] = round(time.monotonic() - started, 3)
  print(json.dumps(result, indent=2))
  if result["verdict"] in ("public-likely", "public-confirmed"):
    return 0
  return 1 if result["verdict"] in ("cgnat", "double-nat") else 2


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
