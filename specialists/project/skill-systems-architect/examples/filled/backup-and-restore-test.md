---
Title: Nautobot Postgres restore drill (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/backup-and-restore-test.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  RPO and RTO for the hub-1 Nautobot database, 3-2-1 placement, a `just capacity` restore estimate and restore drill RD-003 measured against the RTO;
  the drill passes the RTO and finds an off-site RPO gap. All site facts are fictional.
---

# hub-1 Nautobot backup and restore test

Fills template: [templates/backup-and-restore-test.md](../../templates/backup-and-restore-test.md). Drill RD-003, follow-up to PIR-005; cluster as in `host-and-cluster-build.md` (DES-014).

## Contents

- [How to use](#how-to-use)
- [1. Datasets and targets](#1-datasets-and-targets)
- [2. Copies and placement](#2-copies-and-placement)
- [3. Restore estimate](#3-restore-estimate)
- [4. Restore drill record](#4-restore-drill-record)
- [5. Findings and actions](#5-findings-and-actions)
- [6. Review state](#6-review-state)

## How to use

How this example applied the template's rules:

- The drill, not the nightly job log, is the recovery evidence. Every duration in section 4 is a (fictional) measured value; the model in section 3 is a lower bound only.
- DR rung: backup and restore. Nautobot is intent and inventory, not the forwarding path, so an hours-scale RTO is acceptable (service owner, USER_STATED).
- Labels: every ERN fact is fictional and therefore USER_STATED. Helper results are static (model) evidence on those inputs.

## 1. Datasets and targets

| Dataset           | Service            | Size (GiB) and growth                          | Consistency need (crash, app, DB log)            | RPO    | RTO     | Owner             | Label       |
| ----------------- | ------------------ | ---------------------------------------------- | ------------------------------------------------ | ------ | ------- | ----------------- | ----------- |
| nautobot-postgres | Nautobot (REQ-22)  | 38 on disk; custom-format dump 14; +3 per year | DB-consistent (pg_dump), app quiesced not needed | 60 min | 240 min | systems architect | USER_STATED |
| openwisp-influxdb | OpenWISP charts    | 610; +45% at 60 sites                          | crash-consistent acceptable (charts)             | 24 h   | 24 h    | NOC lead          | USER_STATED |
| grafana-config    | Grafana dashboards | 0.2                                            | app export (JSON) in git                         | 24 h   | 120 min | NOC lead          | USER_STATED |

This drill covers nautobot-postgres only. The other two are listed so their targets exist; they are untested (section 5).

## 2. Copies and placement

| Dataset           | Copy         | Location / failure domain   | Medium or system     | Schedule         | Retention   | Immutable / offline        | Encryption key custody         | Last success  |
| ----------------- | ------------ | --------------------------- | -------------------- | ---------------- | ----------- | -------------------------- | ------------------------------ | ------------- |
| nautobot-postgres | 1 production | hub-1, Ceph pool vm-rbd     | Ceph RBD             | live             | n/a         | no                         | n/a                            | n/a           |
|                   |              |   (3 domains)               |   on pve-1/2/3       |                  |             |                            |                                |               |
| nautobot-postgres | 2            | hub-1 rack-b, pbs-1 (not    | Proxmox Backup       | hourly dump at   | 48 hourly,  | PBS datastore,             | PBS client key in the ERN      | 2026-10-21    |
|                   |   local      |   in cluster)               |   Server             |   :00, about 6   |   30 daily  |   not immutable            |   vault; paper copy in the     |   08:06       |
|                   |   backup     |                             |   datastore, ZFS     |   min to finish  |             |                            |   hub-1 safe                   |               |
| nautobot-postgres | 3 off site   | hub-2 (other town)          | PBS sync target on   | sync every 4 h   | 30 daily,   | sync job pull-only,        | same key as copy 2             | 2026-10-21    |
|                   |              |                             |   hub-2, ZFS         |   at :20 (00:20, |   12        |   removed-vanished off;    |                                |   08:20       |
|                   |              |                             |                      |   04:20 ...)     |   monthly   |   not offline              |                                |               |

3-2-1 result for nautobot-postgres: copies 3, media or systems 2 (Ceph, PBS on ZFS), off site yes, immutable no (finding F-03).

```text
Copy and restore paths for nautobot-postgres

  [production hub-1 Ceph, pve-1/2/3] --hourly dump--> [pbs-1 hub-1 rack-b]
  [pbs-1 hub-1 rack-b]  --pull sync every 4 h-->  [hub-2 off-site PBS]
  restore (RD-003): [hub-2 off-site PBS] --200 Mbit/s link--> [new VM on pve-2, hub-1]
  Shares a domain with production?  pbs-1: hub-1 building and room (X); hub-2: no
  Legend: --> data flow   X shared failure domain
```

## 3. Restore estimate

```text
$ just capacity examples/filled/backup-and-restore-test.json          # exit 0
  restore: estimated_seconds 1758.99, rto_seconds 14400, exceeds_rto false
  (scenarios normal and lose-pve-2 pass: 280.8 and 187.2 GiB effective vs 112 GiB demand)

$ just capacity examples/filled/backup-and-restore-test-local.json    # exit 0
  restore: estimated_seconds 924.05, rto_seconds 14400, exceeds_rto false
```

Arithmetic (scripts/README.md): 14 GiB x 2^30 x 8 / (200 x 10^6 x 0.7) = 858.99 s, plus 900 s fixed (PBS catalogue, mount and decrypt; USER_STATED from a previous drill) = 1,758.99 s = 29.3 min. Local
copy at 10 Gbit/s and 0.5 efficiency: 24.05 s + 900 s = 924.05 s. Both are transfer lower bounds, not RTO evidence.

| Dataset                     | data_gib | throughput_mbps | efficiency | fixed_seconds | Estimated seconds | rto_seconds | Exit code |
| --------------------------- | -------- | --------------- | ---------- | ------------- | ----------------- | ----------- | --------- |
| nautobot-postgres, off site | 14       | 200             | 0.7        | 900           | 1,758.99          | 14,400      | 0         |
| nautobot-postgres, local    | 14       | 10,000          | 0.5        | 900           | 924.05            | 14,400      | 0         |

## 4. Restore drill record

| Field                                                         | Value                                                                                                                                |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Drill ID / date / operator                                    | RD-003 / 2026-10-21 / on-call engineer, verified by the NOC lead                                                                     |
| Scenario                                                      | full dataset, hub-1 local backup assumed lost (site-loss rehearsal for the database): restore from hub-2                             |
| Restore point chosen and its age                              | 08:00 dump, synced to hub-2 at 08:20; simulated loss declared at 08:47, so 47 min old at loss                                        |
| Recovery target and isolation from production                 | new VM nb-restore on pve-2, VLAN 100 address 10.10.0.121, firewall blocks it from sites and workers                                  |
| Dependencies needed (keys, identity, DNS, licences) and       | PBS key from the vault: available; Nautobot SECRET_KEY from the vault: available; DNS record: not needed (IP test); Postgres 16      |
|   whether available                                           |   package mirror: available                                                                                                          |

| Phase                      | Start | End   | Measured duration  | Notes                                                      |
| -------------------------- | ----- | ----- | ------------------ | ---------------------------------------------------------- |
| Detection and decision     | 09:00 | 09:12 | 12 min             | drill clock started at the simulated page                  |
| Provision target           | 09:12 | 09:31 | 19 min             | VM from template, Postgres 16 installed from the mirror    |
| Data transfer              | 09:31 | 10:02 | 31 min             | model 29.3 min; measured efficiency about 0.63 on transfer |
| Replay / consistency       | 10:02 | 10:41 | 39 min             | pg_restore with 4 jobs; index rebuild dominated            |
| Start and validate service | 10:41 | 10:58 | 17 min             | Nautobot started against the restored DB; checks below     |
| **Total vs RTO**           | 09:00 | 10:58 | 118 min vs 240 min | pass                                                       |

Transfer phase check: (31 x 60 - 900) s = 960 s for the data versus 858.99 s modelled, so measured efficiency = 0.7 x 858.99 / 960 = 0.63.

Data loss measured vs RPO: 47 min of changes lost vs 60 min allowed (pass for this restore point). The worst case is not 47 min; see F-01.
Validation: the NOC lead logged in, listed site-a devices, read the 2026-10-21 08:00 change-log tail and ran the device-count query (40 site boxes, 40 switches): all matched the dump time.

## 5. Findings and actions

| Finding                                    | Effect on RTO/RPO                                                            | Action                                     | Owner          | Due        |
| ------------------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------ | -------------- | ---------- |
| F-01 Off-site copy syncs every 4 h at :20, | worst-case off-site RPO: a loss just before 12:20 leaves the 08:00 dump, 240 | sync to hub-2 on dump completion; or       | systems        | 2026-11-30 |
|   carrying the :00 dump                    |   + 20 = 260 min vs 60 min required (fails if hub-1 lost)                    |   archive WAL to hub-2 every 5 min         |   architect    |            |
| F-02 Replay (39 min) is the longest phase, | RTO margin 122 min; grows with the index set                                 | keep the drill; record replay time per     | on-call        | next drill |
|   not transfer                             |                                                                              |   drill to see the trend                   |   engineer     |            |
| F-03 No immutable copy                     | ransomware in scope could reach both PBS stores with one key                 | enable an immutable or offline monthly     | systems        | 2027-01-31 |
|                                            |                                                                              |   copy at hub-2                            |   architect    |            |
| F-04 openwisp-influxdb and grafana-config  | their RTOs are unproven                                                      | drill each once (RD-004, RD-005)           | NOC lead       | 2027-02-28 |
|   never restored                           |                                                                              |                                            |                |            |

## 6. Review state

| Revision | State    | Date       | Reviewer (role)                 | Evidence                                 |
| -------- | -------- | ---------- | ------------------------------- | ---------------------------------------- |
| r1       | proposed | 2026-10-07 | systems architect               | targets from service owner               |
| r2       | verified | 2026-10-29 | NOC lead (independent verifier) | RD-003 journal; helper runs in section 3 |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
