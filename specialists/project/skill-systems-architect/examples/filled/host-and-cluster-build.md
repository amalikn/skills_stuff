---
Title: hub-1 Proxmox cluster build (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/host-and-cluster-build.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Three-node Proxmox VE cluster at hub-1 hosting Nautobot, OpenWISP and Grafana; answers the QDevice question with `just quorum`, sizes memory with
  `just capacity`, Ceph with `just ceph` and the platform with `just availability`. All site facts are fictional.
---

# hub-1 host and cluster build

Fills template: [templates/host-and-cluster-build.md](../../templates/host-and-cluster-build.md). Design DES-014 r2, decision ADR-0009. Fictional operator "Example Remote Networks" (ERN).

## Contents

- [How to use](#how-to-use)
- [1. Purpose and requirements](#1-purpose-and-requirements)
- [2. Nodes and sizing](#2-nodes-and-sizing)
- [3. Quorum and membership](#3-quorum-and-membership)
- [4. Storage](#4-storage)
- [5. Host networking](#5-host-networking)
- [6. Backup, monitoring and lifecycle](#6-backup-monitoring-and-lifecycle)
- [7. Acceptance](#7-acceptance)
- [8. Review state](#8-review-state)

## How to use

How this example applied the template's rules:

- Sized from the capacity model (`capacity-model.md` in this folder), not from node count: the cluster carries all 112 GiB of guest demand after losing any one host or any one power domain.
- Every helper input is saved beside this file (`host-and-cluster-build*.json`); commands ran from the pack root on 2026-10-29.
- Labels: every ERN fact is fictional and therefore USER_STATED. Helper results are static (model) evidence on those inputs; they close no acceptance test in section 7.
- Section 5 is the interface contract IF-004 side for the hub hosts; the network architect owns the switch side.

## 1. Purpose and requirements

| Field                      | Value                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Workloads hosted           | Nautobot (app, Postgres, Redis, worker), OpenWISP (+InfluxDB), Grafana, Prometheus, Loki; REQ-21 platform availability, REQ-22 Nautobot RTO/RPO |
| Availability model         | HA restart of guests on a surviving node; no application-level redundancy (accepted: one Postgres instance, restore path in RD-003)             |
| Failure tolerance required | any one host, or any one power domain (feed A, B or C), without manual action. Two simultaneous domains: accepted outage                        |
| Platform and version       | Proxmox VE 9.x on all three nodes (support end: UNVERIFIED, read the vendor lifecycle page before acceptance)                                   |
| Owner / on-call            | systems architect / ERN on-call engineer                                                                                                        |

Label: requirements and tolerance USER_STATED (service owner, fictional). Site traffic does not depend on this cluster: the WireGuard concentrators hub-gw-1 and hub-gw-2 are separate hosts (DES-012).

## 2. Nodes and sizing

As-was layout (the cause of INC-0417): pve-1 and pve-2 in rack-a on feed A, pve-3 in rack-b. Target layout below moves one node per power domain.

| Node  | Failure domain (rack, PDU feed) | CPU (cores, model) | Memory (GiB) | Reserve for host (GiB) | Local disks                            | NICs               | Out-of-band controller          |
| ----- | ------------------------------- | ------------------ | ------------ | ---------------------- | -------------------------------------- | ------------------ | ------------------------------- |
| pve-1 | rack-a, feed A                  | 16 cores, 1 socket | 128          | 24                     | 2 x 480 GB boot mirror, 2 x 3.84 TB    | 2 x 1 GbE, 2 x     | BMC on mgmt VLAN                |
|       |                                 |                    |              |                        |   NVMe (OSD)                           |   25 GbE           |   101, 10.10.1.111              |
| pve-2 | rack-b, feed B                  | 16 cores, 1 socket | 128          | 24                     | as pve-1                               | as pve-1           | BMC 10.10.1.112                 |
| pve-3 | comms-c, feed C                 | 16 cores, 1 socket | 128          | 24                     | as pve-1                               | as pve-1           | BMC 10.10.1.113                 |

Reserve 24 GiB per node = host 8 GiB + 2 Ceph OSDs at 8 GiB each (USER_STATED sizing rule of ERN; check the OSD memory target in the Ceph documentation for the deployed release).

Guest demand (USER_STATED, configured VM memory): Nautobot app 8 + Postgres 16 + Redis 4 + worker 8 + OpenWISP 16 + InfluxDB 16 + Grafana 4 + Prometheus 24 + Loki 16 = 112 GiB.

```text
$ just capacity examples/filled/host-and-cluster-build.json      # exit 0
  normal                   effective_memory_gib 280.8  demand 112.0  deficit 0
  maintenance-drain-pve-1  effective_memory_gib 187.2  demand 112.0  deficit 0
  lose-pve-2               effective_memory_gib 187.2  demand 112.0  deficit 0
  lose-rack-a              effective_memory_gib 187.2  demand 112.0  deficit 0
  lose-comms-c             effective_memory_gib 187.2  demand 112.0  deficit 0
  status pass, findings []
```

Arithmetic the helper applies (scripts/README.md): (128 - 24) x 3 x (1 - 0.10 headroom) = 280.8 GiB; with one node gone (128 - 24) x 2 x 0.9 = 187.2 GiB.

| Scenario          | Usable memory (GiB) | Demand (GiB) | vCPU:pCPU           | Storage used / usable          | Meets? (`just capacity` exit) |
| ----------------- | ------------------- | ------------ | ------------------- | ------------------------------ | ----------------------------- |
| normal            | 280.8               | 112          | 30 vCPU : 48 = 0.63 | 2.4 TB / 6.53 TB (normal plan) | yes (exit 0)                  |
| largest host lost | 187.2               | 112          | 30 vCPU : 32 = 0.94 | 2.4 TB / 4.35 TB (`just ceph`) | yes (exit 0)                  |
| rack / feed lost  | 187.2               | 112          | 30 vCPU : 32 = 0.94 | 2.4 TB / 4.35 TB, degraded     | yes (exit 0)                  |

Two hosts lost together is outside the requirement: one vote of three remains, so the cluster is not quorate and memory is moot (section 3).

## 3. Quorum and membership

The QDevice question. The as-was layout could not survive rack-a. Two fixes were compared; each ran through `just quorum`.

```text
$ just quorum examples/filled/host-and-cluster-build-quorum-as-was.json    # exit 1
  total_votes 3, quorum 2
  domain:rack-a  remaining 1  quorate false
  findings: "domain:rack-a: cluster loses quorum (2 of 3 votes needed)"

$ just quorum examples/filled/host-and-cluster-build-quorum-qdevice.json   # exit 0, status warnings
  total_votes 5, quorum 3, qdevice_votes 2 (QDevice in comms-c, nodes as-was)
  domain:rack-a  remaining 3  quorate true
  qdevice        remaining 3  quorate true
  findings: "QDevice on an odd node count holds 2 votes; Proxmox discourages it
            (if it fails, no further node may fail)"

$ just quorum examples/filled/host-and-cluster-build-quorum.json           # exit 0 (chosen)
  total_votes 3, quorum 2
  node:pve-1 / node:pve-2 / node:pve-3      remaining 2  quorate true
  domain:rack-a / domain:rack-b / domain:comms-c  remaining 2  quorate true
```

Decision (ADR-0009): move pve-2 to rack-b and pve-3 to comms-c (feed C), one node per power domain, and do not add a QDevice. The QDevice option keeps quorum through rack-a loss but gives one small
box 2 of 5 votes; while it is down, losing any node stops the cluster. The vote rule is as the pack states it in scripts/README.md (Proxmox pvecm behaviour, not re-read for this example).

```text
Quorum map for hub-1 cluster (chosen layout)

  :::: rack-a, feed A ::::    pve-1 (1 vote)
  :::: rack-b, feed B ::::    pve-2 (1 vote)
  :::: comms-c, feed C :::    pve-3 (1 vote)

  total 3   quorum = floor(3 / 2) + 1 = 2
  rack-a lost  --> 2 of 3 --> quorate yes   (`just quorum` exit 0)
  rack-b lost  --> 2 of 3 --> quorate yes
  comms-c lost --> 2 of 3 --> quorate yes
  any two lost --> 1 of 3 --> quorate no (accepted, section 1)
  Legend: :::: failure domain   --> outcome
```

| Item                                | Value                                                                                                                                                          |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cluster network(s) for membership   | corosync link 0 on VLAN 102 (10.10.2.0/24, 1 GbE dedicated port); link 1 on the 25 GbE bond, VLAN 103. Latency budget: UNVERIFIED, read the Proxmox cluster    |
|                                     |   manager page for the version                                                                                                                                 |
| Witness location and failure domain | none: three equal votes, one per domain (ADR-0009)                                                                                                             |
| Fencing method and test             | Proxmox HA watchdog self-fence on quorum loss; tested in section 7 by isolating pve-3                                                                          |
| Behaviour on quorum loss            | the minority node fences itself and its HA guests restart on the majority; with no majority, all HA guests stop                                                |

## 4. Storage

```text
$ just ceph examples/filled/host-and-cluster-build-ceph.json     # exit 1 (finding accepted below)
  vm-rbd  width 3  min_size 2  raw_tb 23.04  surviving_raw_tb 15.36  plan_tb 4.352  demand_tb 2.4
  findings: "vm-rbd: losing 1 domain(s) leaves 2 for 3 placements;
            data stays degraded until the domain returns"
```

Plan arithmetic (scripts/README.md): (23.04 - 7.68) / 3 x 0.85 nearfull = 4.352 TB.

Accepted finding: with three hosts and size 3, Ceph cannot re-place the third copy after a host loss; the pool runs degraded on two copies (still at min_size 2, so writes continue) until the host
returns. A fourth host would remove the finding; ERN accepts the degraded window because the restore path (RD-003) and off-site copies cover a second loss, and a fourth host does not fit the comms-c
power budget (USER_STATED). Reopen trigger: a host repair takes longer than 72 h, or demand passes 3.5 TB (80% of plan).

| Pool   | Type (ZFS, Ceph, NFS, iSCSI) | Redundancy (mirror, raidz, size/min_size) | Usable / plan limit   | Failure domain rule  | Rebuild path and time       | Latency target   | `just ceph` exit |
| ------ | ---------------------------- | ----------------------------------------- | --------------------- | -------------------- | --------------------------- | ---------------- | ---------------- |
| vm-rbd | Ceph RBD, 6 x 3.84 TB        | size 3 / min_size 2                       | 6.53 TB normal / 4.35 | host (one host per   | no re-placement on 3 hosts; | p99 write < 10   | 1, accepted      |
|        |   NVMe OSD                   |                                           |   TB plan after one   |   power domain)      |   backfill when the host    |   ms             |                  |
|        |                              |                                           |   host lost           |                      |   returns: 2.4 TB at        |   (USER_STATED)  |                  |
|        |                              |                                           |                       |                      |   measured rate, UNVERIFIED |                  |                  |
|        |                              |                                           |                       |                      |   until the section 7 test  |                  |                  |
| boot   | ZFS mirror per node          | mirror 2 x 480 GB                         | local only            | node                 | reinstall plus              | n/a              | n/a              |
|        |                              |                                           |                       |                      |   config restore            |                  |                  |

## 5. Host networking

Interface contract IF-004 (hub hosts side). Switch pair: hub-sw-1 (rack-a) and hub-sw-2 (rack-b), MLAG; comms-c is fed by two runs, one from each switch (USER_STATED).

| Function           | Bond (mode, LACP rate, members)               | VLAN / bridge      | MTU  | Switch pair / ports          | Failover time measured                 | Interface contract |
| ------------------ | --------------------------------------------- | ------------------ | ---- | ---------------------------- | -------------------------------------- | ------------------ |
| management         | bond0 active-backup, 2 x 1 GbE                | VLAN 101, vmbr0    | 1500 | hub-sw-1/2, port 1 per node  | not yet measured (T-02)                | IF-004             |
| cluster membership | none: link 0 dedicated 1 GbE; link 1 on bond1 | VLAN 102; VLAN 103 | 1500 | hub-sw-1 port 2 (link 0)     | corosync link switch: not yet measured | IF-004             |
| storage            | bond1 802.3ad, LACP fast, 2 x 25 GbE          | VLAN 103           | 9000 | hub-sw-1/2, port 49 per node | not yet measured (T-02)                | IF-004             |
| guest traffic      | bond1                                         | VLAN 100, vmbr1    | 1500 | as storage                   | as storage                             | IF-004             |
| migration          | bond1                                         | VLAN 103           | 9000 | as storage                   | as storage                             | IF-004             |

## 6. Backup, monitoring and lifecycle

Availability of the management platform (series items are shared by every guest, so they dominate):

```text
$ just availability examples/filled/host-and-cluster-build-availability.json   # exit 0
  availability 0.998001125, downtime_minutes_per_year 1051.33
  target 0.995 (REQ-21), target_downtime_minutes_per_year 2629.8, status pass
```

The three-node parallel block contributes almost nothing to the 1,051 min per year; the room, the shared Ceph software domain and the single Nautobot guest do. Adding a fourth node would not move this
number; an application-level replica would. All block availabilities are USER_STATED estimates, not measurements.

| Item                                                           | Value                                                                                                                               |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Backup target, schedule, retention, restore test ref           | pbs-1 (standalone, rack-b) nightly VM backups, 14 daily + 8 weekly; Nautobot Postgres hourly dump; see                              |
|                                                                |   `backup-and-restore-test.md` (RD-003)                                                                                             |
| Configuration backup of hosts and cluster                      | /etc/pve and network config copied nightly to pbs-1 and hub-2                                                                       |
| Monitoring (node, quorum, storage health, NIC/bond state, OOB) | quorum lost -> page on-call; Ceph HEALTH_WARN > 15 min -> ticket; bond member down -> ticket; BMC unreachable -> ticket. Alert path |
|                                                                |   runs from a probe outside the cluster (PIR-005 action A-02)                                                                       |
| Patching ring and window                                       | one node per week, Tuesday 22:00-24:00 local; lifecycle sheet not filled in this example set                                        |

## 7. Acceptance

Planned tests. No result exists yet: this example is at the accepted, not verified, state.

| Test             | Method                                                 | Pass criterion                                                             | Result                 | Date               |
| ---------------- | ------------------------------------------------------ | -------------------------------------------------------------------------- | ---------------------- | ------------------ |
| Host loss        | power off pve-1 (largest-equal host) under normal load | HA guests restart on pve-2/pve-3 within 5 min, no data loss, Ceph at       | not run                | planned 2026-11-10 |
|                  |                                                        |   min_size 2                                                               |                        |                    |
| Bond member loss | pull one 25 GbE link per bond, one node at a time      | no membership change, storage latency p99 < 10 ms                          | not run                | planned 2026-11-10 |
| Quorum partition | isolate pve-3 on VLAN 102 and 103                      | pve-3 fences itself, pve-1 and pve-2 continue                              | not run                | planned 2026-11-10 |
| Feed loss        | switch off feed C at the comms-c PDU in a window       | quorum held (2 of 3), guests on pve-3 restart elsewhere                    | not run                | planned 2026-11-17 |
| Restore          | restore Nautobot Postgres from the off-site copy       | service usable within RTO 240 min                                          | pass, 118 min (RD-003) | 2026-10-21         |

## 8. Review state

| Revision | State    | Date       | Reviewer (role)                       | Evidence                                                          |
| -------- | -------- | ---------- | ------------------------------------- | ----------------------------------------------------------------- |
| r1       | proposed | 2026-09-24 | systems architect                     | as-was quorum finding (exit 1), PIR-005                           |
| r2       | accepted | 2026-10-29 | network architect, operations manager | helper runs above; Ceph finding accepted; tests in section 7 open |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
