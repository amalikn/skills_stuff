#!/usr/bin/env python3
"""Where did an SMC's outage happen on the wire? Per-interface traffic around an outage. Read-only (Prometheus).

usage:
  vlan-traffic-timeline.py <site> '<from YYYY-MM-DD HH:MM AEDT>' '<to ...>' [step_min=120]   # rate table per interface
  vlan-traffic-timeline.py <site> --gap '<last_seen>' '<back>'                             # counter deltas across a dark gap

Interfaces and their roles come from my_node_network_device_info (eth0 trunk, VLAN sub-interfaces, bridges).

Why the gap mode works: node_network_* counters are cumulative since boot, so if node_boot_time_seconds did not change across the
gap, the difference between the last sample before and the first sample after is exactly what crossed each interface while the box
was invisible. Reading it (2026-10-07, arrkapa rct):
  - only the internet-role interface goes quiet, local VLANs (AP management, clients, modem management) keep their usual traffic
      -> the fault is upstream: the satellite / WAN service.
  - EVERY VLAN on the trunk receives nothing while the SMC keeps transmitting small packets (ARP/DHCP/ping retries, ~100 bytes each)
      -> the fault is on the SMC <-> site switch segment or in the switch itself. tx still counting suggests link (carrier) stayed up;
         this exporter has no node_network_carrier, so confirm with `journalctl -k | grep -i 'eth0.*link'` on the box (no reboot = the
         kernel log since boot is still there, even on overlayroot).
  - rx errors / frame errors growing -> a degraded cable or port.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_prom import epoch, instant, rng, ts

if len(sys.argv) < 4:
    sys.exit(__doc__)
site = sys.argv[1]
S = f'site="{site}"'

roles = {}
for r in instant(f"last_over_time(my_node_network_device_info{{{S}}}[30d])"):
    m = r["metric"]
    roles[m["device"]] = m.get("role") or m.get("deviceid") or m.get("type", "")
devs = sorted(d for d in roles if d != "lo")
if not devs:
    sys.exit(f"no my_node_network_device_info for {site}")
DEV = "|".join(devs)

if sys.argv[2] == "--gap":
    a, b = epoch(sys.argv[3]), epoch(sys.argv[4])
    boots = {x for v in rng(f"max(node_boot_time_seconds{{{S}}})", a - 1800, b + 1800, 300).values() for _, x in v}
    print(f"{site} gap {sys.argv[3]} -> {sys.argv[4]} AEDT ({(b-a)/3600:.1f} h); boot time "
          + ("UNCHANGED, counter deltas are valid" if len(boots) == 1 else "CHANGED, box rebooted: deltas are not valid"))
    metrics = ["receive_bytes", "transmit_bytes", "receive_packets", "transmit_packets", "receive_errs", "receive_frame", "receive_drop", "transmit_carrier"]
    out = {}
    for mname in metrics:
        for k, v in rng(f'node_network_{mname}_total{{{S},device=~"{DEV}"}}', a - 1800, b + 1800, 60).items():
            dev = json.loads(k)["device"]
            pre = [x for t, x in v if t <= a + 60]
            post = [x for t, x in v if t >= b - 60]
            if pre and post:
                out[(mname, dev)] = post[0] - pre[-1]
    print(f"{'interface':12s} {'role':14s} {'rx MB':>9s} {'tx MB':>9s} {'rx pkts':>9s} {'tx pkts':>9s} {'errs/frame/drop/carrier':>24s}")
    for d in devs:
        g = lambda m: out.get((m, d), float("nan"))
        bad = sum(out.get((m, d), 0) for m in metrics[4:])
        print(f"{d:12s} {roles[d]:14s} {g('receive_bytes')/1e6:9.1f} {g('transmit_bytes')/1e6:9.1f} {g('receive_packets'):9.0f} {g('transmit_packets'):9.0f} {bad:24.0f}")
else:
    a, b = epoch(sys.argv[2]), epoch(sys.argv[3])
    step = int(sys.argv[4]) * 60 if len(sys.argv) > 4 else 7200
    cols = {}
    for d in devs:
        q = f'rate(node_network_receive_bytes_total{{{S},device="{d}"}}[1h])*3600/1e6'
        cols[d] = dict(next(iter(rng(q, a, b, step).values()), []))
    cols["wan_check"] = dict(next(iter(rng(f'min(avg_over_time(my_node_interfacecheck_success{{{S}}}[1h]))', a, b, step).values()), []))
    print("receive MB/h per interface (role in brackets); wan_check = worst interfacecheck success ratio")
    print(f"{'time AEDT':16s} " + " ".join(f"{d+'('+roles[d][:8]+')':>22s}" for d in devs) + f" {'wan_check':>10s}")
    for t in sorted({t for c in cols.values() for t in c}):
        print(ts(t) + " " + " ".join(f"{cols[d].get(t, float('nan')):22.2f}" for d in devs) + f" {cols['wan_check'].get(t, float('nan')):10.2f}")
