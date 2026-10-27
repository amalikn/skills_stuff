#!/usr/bin/env python3
"""Raspberry Pi undervoltage events per day or per hour-of-day, from Graylog kern.log. Read-only.

usage: undervoltage-profile.py daily  <site> <from YYYY-MM-DD> <to YYYY-MM-DD>
       undervoltage-profile.py hourly <site> <from YYYY-MM-DD> <to YYYY-MM-DD>     # 24 queries per day - keep the range short

Reading it (2026-10-07, canteen-creek): thousands per day spread flat across all 24 hours = the 5V rail feeding the Pi is undersized or
sagging continuously (PSU / DC-DC converter / cable), independent of the battery state. Events clustered before dawn = battery running flat.
A day of zeros for ALL messages is a log-shipping gap (e.g. the 2026-09-12 -> 10-07 Graylog cert outage), not a fix.
"""
import os, sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_graylog import search

if len(sys.argv) != 5 or sys.argv[1] not in ("daily", "hourly"):
    sys.exit(__doc__)
mode, site, a, b = sys.argv[1:5]
UV = f'tp_site:{site} AND path:"/var/log/kern.log" AND (Undervoltage OR "Under-voltage")'
d, end = datetime.strptime(a, "%Y-%m-%d"), datetime.strptime(b, "%Y-%m-%d")


def count(q, f, t):
    return search(q, f.strftime("%Y-%m-%d %H:%M"), t.strftime("%Y-%m-%d %H:%M"), 1).get("total_results") or 0


if mode == "daily":
    print("day (AEDT)   uv_events  all_msgs")
    while d <= end:
        n = d + timedelta(days=1)
        print(d.strftime("%Y-%m-%d"), f"{count(UV, d, n):10d}", f"{count(f'tp_site:{site}', d, n):9d}")
        d = n
else:
    tot = [0] * 24
    while d <= end:
        for h in range(24):
            f = d + timedelta(hours=h)
            tot[h] += count(UV, f, f + timedelta(hours=1))
        d += timedelta(days=1)
    scale = max(1, max(tot) // 60)
    for h in range(24):
        print(f"{h:02d}h AEDT {tot[h]:7d} " + "#" * (tot[h] // scale))
