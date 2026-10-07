#!/usr/bin/env python3
"""One CSV row per site: memory, load, PSI, temperature, throttling, overlay usage and RISE watchdog state over a window. Read-only.

usage: fleet-resource-profile.py [selector='flavor="wh"'] [window=90d] > profile.csv
Empty cell = metric not exported for that site (e.g. node_vmstat_oom_kill is not exported on the RISE Pis).

Caveat (2026-10-07): node_hwmon_in_lcrit_alarm_volts reads 0 even on boxes logging "hwmon: Undervoltage detected!" thousands of times
a day - the rpi_volt alarm is not latched between scrapes. Use undervoltage-profile.py (Graylog kern.log) for undervoltage instead.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_prom import instant

SEL = sys.argv[1] if len(sys.argv) > 1 else 'flavor="wh"'
W = sys.argv[2] if len(sys.argv) > 2 else "90d"

Q = {
    "mem_total_gb": f"max by (site) (max_over_time(node_memory_MemTotal_bytes{{{SEL}}}[{W}]))/1e9",
    "mem_used_p95": f"max by (site) (quantile_over_time(0.95, rise_watchdog_mem_used_pct{{{SEL}}}[{W}]))",
    "mem_used_max": f"max by (site) (max_over_time(rise_watchdog_mem_used_pct{{{SEL}}}[{W}]))",
    "memavail_min_mb": f"min by (site) (min_over_time(node_memory_MemAvailable_bytes{{{SEL}}}[{W}]))/1e6",
    "load15_max": f"max by (site) (max_over_time(rise_watchdog_load_15m{{{SEL}}}[{W}]))",
    "mempsi_max": f"max by (site) (max_over_time(rise_hc_memory_pressure_avg10{{{SEL}}}[{W}]))",
    "iopsi_max": f"max by (site) (max_over_time(rise_hc_io_pressure_avg10{{{SEL}}}[{W}]))",
    "cpu_temp_max": f"max by (site) (max_over_time(rise_hc_cpu_temp_celsius{{{SEL}}}[{W}]))",
    "throttle_max": f"max by (site) (max_over_time(rise_hc_thermal_throttling{{{SEL}}}[{W}]))",
    "oom_kills": f"sum by (site) (increase(node_vmstat_oom_kill{{{SEL}}}[{W}]))",
    "overlay_max_pct": f"max by (site) (max_over_time(rise_watchdog_disk_used_pct{{{SEL}}}[{W}]))",
    "overlay_now_pct": f"max by (site) (last_over_time(rise_watchdog_disk_used_pct{{{SEL}}}[{W}]))",
    "overlay_ge70_hours": f"sum by (site) (count_over_time((rise_watchdog_disk_used_pct{{{SEL}}} >= 70)[{W}:5m]))*5/60",
    "wd_cleanup_minutes": f'sum by (site) (count_over_time((rise_watchdog_last_action{{{SEL},action="cleanup"}} == 1)[{W}:1m]))',
    "overlay_on": f"max by (site) (last_over_time(rise_watchdog_fs_overlay{{{SEL}}}[{W}]))",
    "auto_reboot": f"max by (site) (last_over_time(rise_watchdog_auto_reboot{{{SEL}}}[{W}]))",
    "conntrack_max": f"max by (site) (max_over_time(node_nf_conntrack_entries{{{SEL}}}[{W}]))",
}

rows = {}
for name, q in Q.items():
    try:
        for r in instant(q):
            rows.setdefault(r["metric"].get("site", "?"), {})[name] = float(r["value"][1])
    except Exception as e:
        print(f"# {name} failed: {str(e)[:120]}", file=sys.stderr)

print("site," + ",".join(Q))
for site in sorted(rows):
    print(site + "," + ",".join("" if (v := rows[site].get(c)) is None else f"{v:.1f}" for c in Q))
