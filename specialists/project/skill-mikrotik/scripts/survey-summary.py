#!/usr/bin/env python3
"""Summarise a mikrotik-fleet-survey.sh survey.csv: reach rate, models, versions, voltage/temperature ranges, outliers, and switches that
were power-cycled more recently than their SMC booted. Read-only.

usage: survey-summary.py <survey.csv> [--no-prom]
SMC boot times come from Prometheus through skill-smc's scripts/smc_prom.py (sibling pack); --no-prom skips that comparison.
"""
import csv, os, re, sys, time
from collections import Counter

if len(sys.argv) < 2:
    sys.exit(__doc__)
rows = list(csv.DictReader(open(sys.argv[1])))
use_prom = "--no-prom" not in sys.argv


def days(u):
    """RouterOS uptime like 29w3d4h23m19s -> days (float)."""
    mult = {"w": 7, "d": 1, "h": 1 / 24, "m": 1 / 1440, "s": 1 / 86400}
    return sum(float(n) * mult[k] for n, k in re.findall(r"(\d+)([wdhms])", u or "")) if u else None


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


smc_up = {}
if use_prom:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "skill-smc", "scripts"))
    try:
        from smc_prom import instant
        for r in instant('max by (site) (time() - node_boot_time_seconds{flavor=~"rct|wh|nbn_wh"})/86400'):
            smc_up[r["metric"]["site"] + "-smc01"] = float(r["value"][1])
    except Exception as e:
        print(f"(SMC uptime comparison skipped: {str(e)[:100]})")

for ip in sorted({r["device_ip"] for r in rows}):
    sub = [r for r in rows if r["device_ip"] == ip]
    ok = [r for r in sub if r["reached"] == "yes"]
    print(f"\n=== {ip}: reached {len(ok)}/{len(sub)}")
    print("  boards:  ", dict(Counter(r["board"] for r in ok).most_common()))
    print("  routeros:", dict(Counter(r["routeros"] for r in ok).most_common()))
    for col, unit in (("voltage_v", "V"), ("temp_c", "C")):
        vals = sorted((num(r[col]), r["smc"]) for r in ok if num(r[col]) is not None)
        if vals:
            print(f"  {col}: min {vals[0][0]}{unit} ({vals[0][1]})  median {vals[len(vals)//2][0]}{unit}  max {vals[-1][0]}{unit} ({vals[-1][1]})")
            lo = [f"{s}={v}" for v, s in vals if col == "voltage_v" and v < 24.0]
            if lo:
                print(f"  voltage below 24 V: {', '.join(lo)}")
    up = sorted((days(r["uptime"]), r["smc"]) for r in ok if r["uptime"])
    if up:
        print(f"  uptime days: min {up[0][0]:.1f} ({up[0][1]})  median {up[len(up)//2][0]:.1f}  max {up[-1][0]:.1f}")
    if smc_up:
        younger = [(s, d, smc_up[s]) for d, s in up if s in smc_up and smc_up[s] - d > 1]
        print(f"  device younger than its SMC by >1 day (power-cycled since the SMC booted): {len(younger)} of {len(up)}")
        for s, d, su in sorted(younger, key=lambda x: x[1])[:15]:
            print(f"    {s:32s} device {d:6.1f} d   smc {su:6.1f} d")
    ld = []
    for r in ok:
        for kv in filter(None, r["link_downs_by_port"].split(";")):
            port, n = kv.split("=")
            if "-vlan" not in port:
                ld.append((int(n), r["smc"], port))
    ld.sort(reverse=True)
    if ld:
        print("  most link-downs (physical ports, since device boot):")
        for n, s, p in ld[:12]:
            print(f"    {s:32s} {p:8s} {n}")
print(f"\nnot reached: {', '.join(sorted({r['smc'] + ':' + r['device_ip'] for r in rows if r['reached'] != 'yes'})) or 'none'}")
