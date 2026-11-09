---
Title: Monitoring and metrics
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/monitoring-and-metrics.md
Last reviewed: 2026-11-07
Summary: Health reads, external metric servers, the notification system (targets, matchers, events, templates), and the pack's read-only node report.
---

# Monitoring and metrics

What to read for node health, where PVE pushes metrics, and the pack's read-only node report. Sources: [External Metric
Server](../documents/research-sources-20261107/pve-wiki-external-metric-server.md), [sysadmin chapter](../documents/research-sources-20261107/pve-admin-chapter-sysadmin.html),
[pvesh(1)](../documents/research-sources-20261107/pve-pvesh-man1.md).

## Contents

- [Health reads](#health-reads)
- [External metric servers](#external-metric-servers)
- [Notifications](#notifications)
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

## Notifications

```text
  event (type / severity / fields)     matcher (notifications.cfg)                    target
  vzdump / error / hostname, job-id -> backup-failures                           -> smtp: ops mailbox
                                         match-field exact:type=vzdump
                                         match-severity error      (mode all)
  fencing / error / hostname        -+
                                     +-> cluster-alarms                          -> webhook: chat room
  replication / error / job-id      -+     match-field exact:type=replication,fencing  -> gotify: on-call
  package-updates / info            -> default (no rules: matches everything)    -> sendmail: root@pam
  (matcher and target names are examples; one matcher may notify several targets)
```

Proxmox VE emits notification events and routes them through **matchers** to **targets**. Configuration lives in `/etc/pve/notifications.cfg`, with secrets (SMTP passwords, Gotify tokens,
webhook secrets) in `/etc/pve/priv/notifications.cfg`. All `VERIFIED_PRIMARY` ([notifications chapter](../documents/research-sources-20261109/pve-admin-chapter-notifications.html), fetched 2026-11-09).

- **Targets**: `sendmail` (the system MTA), `smtp` (direct to a relay), `gotify`, `webhook` (HTTP request with Handlebars templating of URL, headers and body, secrets through the
  `secrets` namespace). Mail targets take `mailto` addresses and `mailto-user` users (the user's configured e-mail).
- **Matchers**: `match-severity`, `match-field` (for example `exact:type=vzdump`) and `match-calendar`, combined with `mode all|any` and `invert-match`; a matcher with no rule matches
  everything. One target can serve several matchers.
- **Events**, with their `type` and severity. Route `fencing` and `replication` somewhere a person reads; they are the cluster's own alarms.

  | Event                          | `type`            | Severity      | Extra fields      |
  | ------------------------------ | ----------------- | ------------- | ----------------- |
  | System updates available       | `package-updates` | info          | hostname          |
  | Cluster node fenced            | `fencing`         | error         | hostname          |
  | Storage replication job failed | `replication`     | error         | hostname, job-id  |
  | Backup succeeded / failed      | `vzdump`          | info / error  | hostname, job-id  |
  | Mail for root                  | `system-mail`     | unknown       | hostname          |

- **Templates**: defaults in `/usr/share/pve-manager/templates/default/`; override per type in `/etc/pve/notification-templates/default/` (`<type>-subject.txt.hbs`,
  `<type>-body.txt.hbs`, `<type>-body.html.hbs`); a missing or broken override falls back to the default.

## The node report

`just node_report --host <node>` (read-only, one SSH round trip, about 15 s on the lab node) prints version, kernel, uptime, memory and root fill, quorum rows, pending updates with the PVE-stack
packages listed and when the list was last refreshed, repositories with their format and state, storage use (warns at 85 %), guests with pool, pools, users and tokens (privsep, expiry) and the access
audit. It never runs `apt update`; `--refresh --apply` asks PVE to refresh the list first (`POST /nodes/<node>/apt/update`, a write). Exit 1 when there is any warning. Catalogue:
[scripts/README.md](../scripts/README.md).

> **Learned 2026-11-07 (l)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: `pve_node_report.py --host` against the lab node, 2026-11-07 (run time measured with `time`) · Falsifier: a run on the
> same node taking over 60 s
> One SSH session running eleven `pvesh get` reads plus a `systemctl show` took about 14 s end to end on a single lab node; most of it is the API's package and repository reads. Budget 30 s per node
> for the report and run nodes in parallel, bounded, for a cluster.
