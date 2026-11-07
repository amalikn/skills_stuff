# Monitoring and metrics

What to read for node health, where PVE pushes metrics, and the pack's read-only node report. Sources: [External Metric
Server](../documents/research-sources-20261107/pve-wiki-external-metric-server.md), [sysadmin chapter](../documents/research-sources-20261107/pve-admin-chapter-sysadmin.html),
[pvesh(1)](../documents/research-sources-20261107/pve-pvesh-man1.md).

## Contents

- [Health reads](#health-reads)
- [External metric servers](#external-metric-servers)
- [The node report](#the-node-report)

## Health reads

| Question                      | Read                                                      |
| ----------------------------- | --------------------------------------------------------- |
| Version, kernel, uptime, load | `GET /nodes/<node>/status`, `GET /nodes/<node>/version`   |
| Quorum                        | `GET /cluster/status`, `pvecm status`                     |
| Storage fill and state        | `GET /nodes/<node>/storage` (`used_fraction`, `active`)   |
| Guests and their state        | `GET /cluster/resources` (one call for the whole cluster) |
| Pending updates               | `GET /nodes/<node>/apt/update`                            |
| Failed tasks                  | `GET /nodes/<node>/tasks --errors 1`                      |
| HA                            | `ha-manager status`                                       |
| Disk health                   | `GET /nodes/<node>/disks/list` (SMART summary)            |

Paths `VERIFIED_PRIMARY` by use on 9.1.5 for status, version, cluster status, storage, resources, apt/update and tasks; `--errors` and `disks/list` are `UNVERIFIED` (not run here).

## External metric servers

- PVE pushes node, guest and storage metrics to **Graphite** (default UDP 2003, path `proxmox`), **InfluxDB** (UDP or HTTP(S)) or **OpenTelemetry**; definitions are cluster-wide in
  `/etc/pve/status.cfg`. `VERIFIED_PRIMARY` (External Metric Server; sysadmin chapter).
- Prometheus is not a built-in target: a third-party exporter that reads the API is the usual route; give it a token with `PVEAuditor` (read-only) on `/`, privilege-separated. The exporter choice is
  project-specific. `UNVERIFIED` for any particular exporter.

## The node report

`just node_report --host <node>` (read-only, one SSH round trip, about 15 s on the lab node) prints version, kernel, uptime, memory and root fill, quorum rows, pending updates with the PVE-stack
packages listed and when the list was last refreshed, repositories with their format and state, storage use (warns at 85 %), guests with pool, pools, users and tokens (privsep, expiry) and the access
audit. It never runs `apt update`; `--refresh --apply` asks PVE to refresh the list first (`POST /nodes/<node>/apt/update`, a write). Exit 1 when there is any warning. Catalogue:
[scripts/README.md](../scripts/README.md).

> **Learned 2026-11-07 (l)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: `pve_node_report.py --host` against the lab node, 2026-11-07 (run time measured with `time`) · Falsifier: a run on the
> same node taking over 60 s
> One SSH session running eleven `pvesh get` reads plus a `systemctl show` took about 14 s end to end on a single lab node; most of it is the API's package and repository reads. Budget 30 s per node
> for the report and run nodes in parallel, bounded, for a cluster.
