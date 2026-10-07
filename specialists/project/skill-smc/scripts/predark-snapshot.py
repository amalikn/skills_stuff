#!/usr/bin/env python3
"""What a box looked like in the hours before it went dark: memory, swap, overlay, load, PSI, temperature, conntrack, traffic. Read-only.

usage: predark-snapshot.py <site> '<last_seen YYYY-MM-DD HH:MM AEDT>' [hours=8] [step_min=30]
Take last_seen from fleet-reboot-timeline.py. Flat, healthy numbers right up to the last sample (the 2026-10-07 WH result) mean the
box did not die of resource exhaustion: look at power (undervoltage-profile.py) or the WAN path instead.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_prom import epoch, rng, ts

if len(sys.argv) < 3:
    sys.exit(__doc__)
site, last = sys.argv[1], sys.argv[2]
hours = float(sys.argv[3]) if len(sys.argv) > 3 else 8
step = int(sys.argv[4]) * 60 if len(sys.argv) > 4 else 1800
end = epoch(last) + 300
start = end - int(hours * 3600)
S = f'site="{site}"'

Q = {
    "mem%": f"max(rise_watchdog_mem_used_pct{{{S}}})",
    "avail_MB": f"max(node_memory_MemAvailable_bytes{{{S}}})/1e6",
    "swap_MB": f"max(node_memory_SwapTotal_bytes{{{S}}}-node_memory_SwapFree_bytes{{{S}}})/1e6",
    "ovl%": f"max(rise_watchdog_disk_used_pct{{{S}}})",
    "load1": f"max(node_load1{{{S}}})",
    "memPSI": f"max(rise_hc_memory_pressure_avg10{{{S}}})",
    "ioPSI": f"max(rise_hc_io_pressure_avg10{{{S}}})",
    "tempC": f"max(rise_hc_cpu_temp_celsius{{{S}}})",
    "conntrk": f"max(node_nf_conntrack_entries{{{S}}})",
    "procs_r": f"max(node_procs_running{{{S}}})",
    "forks/s": f"max(rate(node_forks_total{{{S}}}[5m]))",
    "rxMbps": f'sum(rate(node_network_receive_bytes_total{{{S},device!~"lo|docker.*|veth.*"}}[5m]))*8/1e6',
}
cols = {}
for k, q in Q.items():
    try:
        cols[k] = dict(next(iter(rng(q, start, end, step).values()), []))
    except Exception:
        cols[k] = {}
times = sorted({t for c in cols.values() for t in c})
print(f"{site}: {hours:g}h before {last} AEDT (nan = not exported / no sample)")
print("time             " + " ".join(f"{k:>8s}" for k in Q))
for t in times:
    print(ts(t) + " " + " ".join(f"{cols[k].get(t, float('nan')):8.1f}" for k in Q))
