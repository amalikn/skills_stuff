#!/usr/bin/env python3
"""Turn pi_resiliency_probe.sh and x86_resiliency_probe.sh output into per-box CSV rows and Markdown tables, with fleet counts.

Why: a fleet survey prints one `== <node> (<proxy>)` block of key=value lines per box; reading 80 blocks by eye misses the pattern. This keeps the raw
files as the evidence and derives the tables from them, so a table can always be rebuilt and checked against its source.
Run: summarise_survey.py <flavour>=<probe output file> [...] [--csv out.csv]   (a later file's answer replaces an unreachable block: pass retries last)   (read-only apart from --csv; prints Markdown to stdout)
     e.g. summarise_survey.py rct=rct.txt wh=wh.txt rcp=rcp.txt --csv boxes.csv
Exit: 0 printed; 2 bad arguments or a file missing.
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
from pathlib import Path

GIB = 1024**3
X86_FLAVOURS = ("rcp", "nbn_accelerate")  # an unreachable x86 block has no dmi_model to tell it apart


def blocks(text: str) -> list[tuple[str, list[str]]]:
  """Split probe output into (node, lines) per box.

  Args:
    text: the probe's output.

  Returns:
    One entry per `== node` block, in order.
  """
  out: list[tuple[str, list[str]]] = []
  for line in text.splitlines():
    if m := re.match(r"^== (\S+)", line):
      out.append((m.group(1), []))
    elif out and line.strip():
      out[-1][1].append(line)
  return out


def kv(lines: list[str]) -> dict[str, list[str]]:
  """Every key=value pair on the lines (several per line allowed); a repeated key keeps each value.

  Args:
    lines: the block's lines.

  Returns:
    key to its values, in order.
  """
  d: dict[str, list[str]] = collections.defaultdict(list)
  for line in lines:
    if line.startswith(("part=", "smart=", "efi=", "esrt=", "bios_char=", "eeprom=", "disk=", "df=", "state=", "io=", "shrink=", "vg=", "watchdog=")):
      k, v = line.split("=", 1)
      d[k].append(v)
      continue
    if line.startswith(("watchdog_drivers=", "watchdog_dev=", "cmdline_root=")):  # space-separated lists: the rest of the line
      k, v = line.split("=", 1)
      d[k].append(v.strip())
      continue
    if m := re.match(r"^os=(.*?) codename=", line):  # the OS name holds spaces (the probe prints it unquoted)
      d["os"].append(m.group(1))
      line = line[m.end() - len("codename=") :]
    for m in re.finditer(r'(\w+)=("[^"]*"|\S*)', line):
      d[m.group(1)].append(m.group(2).strip('"'))
  return d


def first(d: dict[str, list[str]], key: str) -> str:
  """The first value of a key, or "".

  Args:
    d: as kv() returns.
    key: the key.

  Returns:
    The value.
  """
  return (d.get(key) or [""])[0]


def rate(d: dict[str, list[str]], disk: str) -> str:
  """GB written per day since boot for one disk, from the kernel's sector counter and the uptime.

  Args:
    d: as kv() returns.
    disk: the block device name.

  Returns:
    The rate to one decimal, or "".
  """
  up = int(first(d, "uptime_s") or 0)
  for v in d.get("io", []):
    name, rest = v.split(",", 1)
    if name == disk and up > 0:
      written = int(dict(p.split("=") for p in rest.split(","))["sectors_written"]) * 512
      return f"{written / 1e9 / (up / 86400):.1f}"
  return ""


def pi_row(flavour: str, node: str, d: dict[str, list[str]]) -> dict[str, str]:
  """One Pi box as a flat row.

  Args:
    flavour: its flavour.
    node: its node name.
    d: its key=values.

  Returns:
    The row.
  """
  shrink = dict(p.split("=") for p in first(d, "shrink").split(",") if "=" in p)
  ro = next((v for v in d.get("df", []) if v.startswith("/media/root-ro,")), "")
  return {
    "flavour": flavour, "node": node, "reachable": "no" if first(d, "unreachable") else "yes", "mem_mb": first(d, "mem_mb"), "os": first(d, "os"),
    "kernel": first(d, "kernel"), "card": first(d, "card_name"), "manfid": first(d, "manfid"), "card_date": first(d, "card_date"),
    "card_gb": f"{int(first(d, 'size_bytes') or 0) / 1e9:.0f}", "pttype": first(d, "pttype"), "root": first(d, "root_mount").split(",")[0],
    "lower_used": ro.split("used=")[1].split(",")[0] if ro else "", "bootloader": first(d, "bootloader"), "autoboot": first(d, "autoboot"),
    "throttled": first(d, "throttled"), "uptime_d": f"{int(first(d, 'uptime_s') or 0) / 86400:.0f}", "gb_written_per_day": rate(d, "mmcblk0"),
    "used_gib": shrink.get("used_gib", ""), "above_25G": shrink.get("above_25G", ""),
  }


def smart(d: dict[str, list[str]], disk: str, names: tuple[str, ...]) -> str:
  """The raw value of the first SMART attribute of a disk whose name is in names.

  Args:
    d: as kv() returns.
    disk: the block device name.
    names: attribute names, in order of preference.

  Returns:
    "name=raw", or "".
  """
  for v in d.get("smart", []):
    dev, line = v.split(",", 1)
    parts = line.split()
    if dev == disk and len(parts) >= 10 and parts[1] in names:
      return f"{parts[1]}={parts[9]}"
  return ""


def x86_row(flavour: str, node: str, d: dict[str, list[str]]) -> dict[str, str]:
  """One x86 box as a flat row (its system disk is the root's).

  Args:
    flavour: its flavour.
    node: its node name.
    d: its key=values.

  Returns:
    The row.
  """
  disks = [v.split()[0] for v in d.get("disk", [])]
  root = first(d, "root")
  sysd = next((x for x in disks if x in root), disks[0] if disks else "")
  if "mapper" in root and disks:
    sysd = disks[0]
  return {
    "flavour": flavour, "node": node, "reachable": "no" if first(d, "unreachable") else "yes", "model": first(d, "dmi_model"), "bios": first(d, "bios"),
    "mem": first(d, "mem"), "disks": "; ".join(d.get("disk", [])), "root": root.split(",")[0], "root_use": first(d, "root_use"),
    "vg_free": "; ".join(d.get("vg", [])), "os": first(d, "os"), "kernel": first(d, "kernel"), "uefi": first(d, "uefi_mode"),
    "secure_boot": first(d, "secure_boot"), "watchdog_dev": first(d, "watchdog_dev"),
    "itco_driver": "yes" if "iTCO_wdt" in first(d, "watchdog_drivers") else "no", "runtime_watchdog": first(d, "runtime_watchdog"),
    "uptime_d": f"{int(first(d, 'uptime_s') or 0) / 86400:.0f}", "sys_disk": sysd, "gb_written_per_day": rate(d, sysd),
    "power_on_h": smart(d, sysd, ("Power_On_Hours",)).split("=")[-1],
    "wear": smart(d, sysd, ("Wear_Leveling_Count", "Media_Wearout_Indicator", "Percent_Lifetime_Remain", "Percentage")),
    "host_writes": smart(d, sysd, ("Total_LBAs_Written", "Host_Writes_32MiB", "Host_Writes_GiB")),
    "smart": "absent" if "smartctl-absent" in first(d, "smart") else "",
  }


def table(rows: list[dict[str, str]]) -> str:
  """A Markdown table of rows (all with the same keys).

  Args:
    rows: the rows.

  Returns:
    The table text.
  """
  if not rows:
    return ""
  keys = list(rows[0])
  lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
  lines += ["| " + " | ".join(r[k].replace("|", "/") for k in keys) + " |" for r in rows]
  return "\n".join(lines)


def counts(rows: list[dict[str, str]], keys: tuple[str, ...]) -> str:
  """How many boxes share each value of each key.

  Args:
    rows: the rows.
    keys: the keys to count.

  Returns:
    One line per key.
  """
  return "\n".join(f"- {k}: " + ", ".join(f"{v or '(none)'} x{n}" for v, n in collections.Counter(r[k] for r in rows).most_common()) for k in keys)


def main(argv: list[str] | None = None) -> int:
  """Print the summary.

  Args:
    argv: command line arguments (default sys.argv[1:]).

  Returns:
    0 printed; 2 bad arguments.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("files", nargs="+", help="<flavour>=<file>")
  ap.add_argument("--csv", type=Path)
  args = ap.parse_args(argv)
  pis, x86s, seen = [], [], set()
  for spec in args.files:
    flavour, _, name = spec.partition("=")
    path = Path(name)
    if not flavour or not path.is_file():
      print(f"bad argument or missing file: {spec}", file=sys.stderr)
      return 2
    for node, lines in blocks(path.read_text(encoding="utf-8")):
      d = kv(lines)
      if "unreachable" in d and node in seen:
        continue
      seen.add(node)
      rows = x86s if "dmi_model" in d or flavour in X86_FLAVOURS else pis
      rows[:] = [r for r in rows if r["node"] != node]  # a later answer (a retry file) replaces an unreachable block for the same box
      rows.append((x86_row if "dmi_model" in d or flavour in X86_FLAVOURS else pi_row)(flavour, node, d))
  if pis:
    print("## Pi boxes\n")
    print(counts(pis, ("reachable", "mem_mb", "os", "card", "card_gb", "pttype", "root", "bootloader", "autoboot", "throttled")) + "\n")
    print(table(pis) + "\n")
  if x86s:
    print("## x86 boxes\n")
    print(counts(x86s, ("reachable", "model", "os", "uefi", "secure_boot", "watchdog_dev", "itco_driver", "runtime_watchdog", "smart")) + "\n")
    print(table(x86s) + "\n")
  if args.csv:
    rows = pis + x86s
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with args.csv.open("w", newline="", encoding="utf-8") as f:
      w = csv.DictWriter(f, fieldnames=keys)
      w.writeheader()
      w.writerows(rows)
  return 0


if __name__ == "__main__":
  sys.exit(main())
