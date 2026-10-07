#!/usr/bin/env python3
"""Per-site reboot and outage timeline from Prometheus, classifying each event. Read-only.

usage: fleet-reboot-timeline.py [days=90] [selector='flavor="wh"'] [events_per_site=25]
  e.g. fleet-reboot-timeline.py 90 'site="arrkapa"'

Classification (node_boot_time_seconds, 5-minute resolution):
  reboot          boot time moved forward and the box was dark <1h before the new boot: an ordinary reboot (operator, watchdog,
                  kernel update) - the box went down BECAUSE it rebooted.
  DARK->boot      box was dark >1h and then came back by BOOTING: it lost power (solar battery / LVD, mains) or hard-hung and was
                  power-cycled. Many of these at the same clock time each day = power, not software (2026-10-07 WH finding).
  gap-no-reboot   dark >30 min with no boot-time change: the box stayed up, its WAN / tunnel / federation path was down.
                  A gap shared by EVERY site at once is a central Prometheus outage, not a site fault (e.g. 2026-09-14 19:00 -> 09-16 07:30).
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_prom import rng, ts

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90
SEL = sys.argv[2] if len(sys.argv) > 2 else 'flavor="wh"'
SHOW = int(sys.argv[3]) if len(sys.argv) > 3 else 25
STEP, GAP_MIN = 300, 30

end = int(time.time())
start = end - DAYS * 86400
data = rng(f"max by (site) (node_boot_time_seconds{{{SEL}}})", start, end, STEP)

summary = []
for key, vals in data.items():
    site = json.loads(key).get("site", key)
    reboots, gaps = [], []
    for (t0, b0), (t1, b1) in zip(vals, vals[1:]):
        if t1 - t0 > GAP_MIN * 60:
            gaps.append((t0, t1))
        if b1 - b0 > 120:  # node_boot_time_seconds jitters by ~1s; a real reboot moves it by minutes or more
            reboots.append((t0, t1, b1))
    events = []
    for t0, t1, boot in reboots:
        dark = boot - t0
        kind = "DARK->boot" if dark > 3600 else "reboot"
        events.append((t0, f"{kind:13s} last_seen={ts(t0)} booted={ts(boot)} back={ts(t1)} dark_before_boot={dark/3600:.1f}h"))
    windows = {(a, b) for a, b, _ in reboots}
    net_gaps = [(a, b) for a, b in gaps if (a, b) not in windows]
    events += [(a, f"gap-no-reboot {ts(a)} -> {ts(b)} ({(b-a)/3600:.1f}h)") for a, b in net_gaps]
    dark_boots = sum(1 for _, e in events if e.startswith("DARK"))
    cover = len(vals) * STEP / (DAYS * 86400) * 100
    summary.append((site, len(reboots), dark_boots, len(net_gaps), sum(b - a for a, b in net_gaps) / 3600, cover, ts(vals[-1][0]) if vals else "-"))
    print(f"\n=== {site}  reboots={len(reboots)} dark_boots={dark_boots} net_gaps={len(net_gaps)} coverage={cover:.0f}% last={summary[-1][-1]}")
    for _, line in sorted(events)[-SHOW:]:
        print("   ", line)

print(f"\nSITE (last {DAYS}d, AEDT)       reboots dark_boots net_gaps net_gap_h coverage% last_seen")
for s in sorted(summary, key=lambda x: (-x[2], -x[1], -x[3])):
    print(f"{s[0]:28s} {s[1]:7d} {s[2]:10d} {s[3]:8d} {s[4]:9.1f} {s[5]:9.0f}  {s[6]}")
print("\nNote: coverage < 100% with few gaps usually means the series started mid-window (site onboarded / relabelled).")
