#!/usr/bin/env python3
"""Pick a reproducible sample of SMC hosts per flavour: prod inventory hosts that Teleport lists, N per flavour, with each one's proxy.

Why: fleet surveys read a sample per flavour (operator 2026-11-10: "20 from each flavor"); the inventory alone holds retired boxes, so a host is
kept only when its project's Teleport cluster lists it. The proxy comes from the flavour's project, never guessed (skill-smc 01_overview.md).
Run: sample_fleet.py --inventories <ansible-wifi>/inventories [--per-flavour 20] [--seed 20261110] [--flavours rct,wh,nbn_wh,rcp,nbn_accelerate]
     Prints `<flavour> <proxy> <host>` lines, sorted. Read-only: reads the inventory files and runs `tsh ls --format=names` once per cluster.
Exit: 0 sample printed; 1 a cluster could not be listed; 2 bad arguments or an inventory missing.
"""

from __future__ import annotations

import argparse
import random
import re
import subprocess
import sys
from pathlib import Path

#: Teleport proxy per flavour (skill-smc references/01_overview.md: the split is by project).
PROXY = {
  "rct": "teleport.apn.au",
  "wh": "teleport.apn.au",
  "rcp": "teleport.apn.au",
  "nbn_wh": "teleport.communitywifi.net.au",
  "nbn_accelerate": "teleport.communitywifi.net.au",
}
HOST = re.compile(r"^([a-z0-9-]+-smc0\d)\s*$", re.M)


def inventory_hosts(root: Path, flavour: str) -> list[str]:
  """The SMC host names in one flavour's prod inventory (INI form).

  Args:
    root: the inventories folder.
    flavour: the flavour folder name.

  Returns:
    Sorted unique host names.

  Raises:
    FileNotFoundError: the flavour has no prod inventory.
  """
  return sorted(set(HOST.findall((root / flavour / "prod").read_text(encoding="utf-8"))))


def teleport_names(proxy: str, timeout: int = 90) -> set[str]:
  """The node names one Teleport cluster lists.

  Args:
    proxy: the cluster's proxy.
    timeout: seconds before the listing is abandoned.

  Returns:
    The node names.

  Raises:
    RuntimeError: tsh failed or timed out.
  """
  try:
    r = subprocess.run(["tsh", "ls", f"--proxy={proxy}", "--format=names"], capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
  except subprocess.TimeoutExpired as e:
    raise RuntimeError(f"tsh ls on {proxy} timed out after {timeout} s") from e
  if r.returncode:
    raise RuntimeError(f"tsh ls on {proxy} failed: {r.stderr.strip()[-200:]}")
  return set(r.stdout.split())


def sample(hosts: list[str], listed: set[str], n: int, seed: int) -> tuple[list[str], int]:
  """Pick n listed hosts reproducibly.

  Args:
    hosts: the inventory's hosts.
    listed: the names Teleport lists.
    n: how many to pick (all when fewer are listed).
    seed: the random seed, so the same sample can be read again.

  Returns:
    (the sorted sample, how many inventory hosts Teleport does not list).
  """
  live = [h for h in hosts if h in listed]
  return sorted(random.Random(seed).sample(live, min(n, len(live)))), len(hosts) - len(live)


def main(argv: list[str] | None = None) -> int:
  """Print the sample.

  Args:
    argv: command line arguments (default sys.argv[1:]).

  Returns:
    0 printed; 1 a cluster could not be listed; 2 bad arguments.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--inventories", type=Path, required=True)
  ap.add_argument("--per-flavour", type=int, default=20)
  ap.add_argument("--seed", type=int, default=20261110)
  ap.add_argument("--flavours", default=",".join(PROXY))
  args = ap.parse_args(argv)
  flavours = [f for f in args.flavours.split(",") if f]
  if bad := [f for f in flavours if f not in PROXY]:
    print(f"unknown flavour(s): {bad}", file=sys.stderr)
    return 2
  try:
    listed = {p: teleport_names(p) for p in sorted({PROXY[f] for f in flavours})}
  except RuntimeError as e:
    print(e, file=sys.stderr)
    return 1
  for f in flavours:
    try:
      hosts = inventory_hosts(args.inventories, f)
    except FileNotFoundError as e:
      print(e, file=sys.stderr)
      return 2
    picked, gone = sample(hosts, listed[PROXY[f]], args.per_flavour, args.seed)
    print(f"# {f}: {len(hosts)} in inventory, {gone} not listed by {PROXY[f]}, {len(picked)} sampled", file=sys.stderr)
    for h in picked:
      print(f, PROXY[f], h)
  return 0


if __name__ == "__main__":
  sys.exit(main())
