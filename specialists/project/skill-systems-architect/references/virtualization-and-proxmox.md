---
Title: Virtualisation, Proxmox and cluster design
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Virtualisation, Proxmox and cluster design decisions, failure modes and validation.
---

# Virtualisation, Proxmox and cluster design

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Quorum arithmetic and QDevice](#quorum-arithmetic-and-qdevice)
- [HA, fencing and replication timing](#ha-fencing-and-replication-timing)
- [Topology decision table](#topology-decision-table)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Choosing bare metal, VM, system container (LXC) or application container per workload.
- Cluster quorum, fencing, HA restart and replication on Proxmox VE (KVM/libvirt, Hyper-V and VMware are peers, not defaults).
- Topology choice: single host, 2 nodes + QDevice, 3+ nodes with ZFS replication, 3+ nodes with Ceph.

## Decision rules

Platform-neutral:

- Choose the runtime from isolation, kernel coupling, portability, hardware access and recovery needs. Do not impose a vendor.
- Record per workload: CPU compatibility, migration limits, storage mode, guest agents, passthrough, scheduling and licensing.
- A host cluster is not application availability. HA restart is a cold boot, so the application still sees a crash.
- Online migration works only between CPUs of the same vendor. VERIFIED_PRIMARY, [pvecm], checked 2026-10-29.

Five separate questions for every failure:

| Question     | Asks                                        | A witness/QDevice helps? |
| ------------ | ------------------------------------------- | ------------------------ |
| Quorum       | Can a surviving partition safely decide?    | yes: one vote            |
| Fencing      | Can it exclude a failed or isolated writer? | no                       |
| Data         | Does the survivor hold current data?        | no                       |
| Capacity     | Can survivors run the required guests?      | no                       |
| Reachability | Can users reach the restarted guests?       | no                       |

- Never force quorum or disable fencing to meet an availability claim.
- `pvecm expected 1` overrides quorum. It is a last-resort step on an isolated node, not a fix.
- Two hosts in rack A plus one in rack B do not survive rack-A loss: B holds 1 of 3 votes.
- Inspect, never assume: VE version, corosync links and latency, expected votes, QDevice placement, HA rules, watchdog type, storage per guest, replication lag and backup target.
- Coordinate bridges, VLANs, bonds, SDN, migration network, storage traffic and MTU with the network architect.

## Quorum arithmetic and QDevice

- `quorum = floor(total_votes / 2) + 1`. Tolerated vote loss = `total_votes - quorum`.
- One vote per node by default. An inquorate node makes the cluster filesystem read-only. VERIFIED_PRIMARY, [pvecm], checked 2026-10-29.

| Nodes | QDevice votes | Total | Quorum | Node failures tolerated | Note                                                    |
| ----- | ------------- | ----- | ------ | ----------------------- | ------------------------------------------------------- |
| 1     | -             | 1     | 1      | 0                       | no cluster; HA meaningless                              |
| 2     | -             | 2     | 2      | 0                       | either node loss freezes management                     |
| 2     | 1             | 3     | 2      | 1                       | supported and recommended for 2-node (VERIFIED_PRIMARY) |
| 3     | -             | 3     | 2      | 1                       | Proxmox minimum for reliable HA                         |
| 4     | -             | 4     | 3      | 1                       | even count buys no extra tolerance                      |
| 4     | 1             | 5     | 3      | 2                       | QDevice on even counts adds one vote                    |
| 5     | -             | 5     | 3      | 2                       |                                                         |

- QDevice on an odd node count holds N-1 votes. If it fails, no further node may fail. Proxmox discourages it. VERIFIED_PRIMARY, [pvecm].
- On a 50/50 split the QDevice votes for the partition with the lowest node id by default (tunable `tie_breaker`).
- QDevice uses TCP, not corosync, so it may sit off-LAN. Remove it before adding or removing nodes; re-add on an even count.
- Corosync latency: under 5 ms between all nodes. Above ~10 ms with more than three nodes is unlikely to work. VERIFIED_PRIMARY, [pvecm].
- Give corosync a dedicated physical link plus a second link on another physical network. Kronosnet supports up to 8 links.
- Use bonds only as additional corosync links; a single link on a bond can fail badly.
- Membership re-forms in `token + consensus`: `token = 3000 + (nodes - 2) * token_coefficient` ms; `consensus = 1.2 * token`.
- Default coefficient 650 ms; Proxmox VE 9.2 sets 125 ms on new clusters. Lower it if the sum exceeds 30-45 s. VERIFIED_PRIMARY, [pvecm] master, checked 2026-10-29; confirm the deployed release.

```text
2-node cluster + QDevice: the corosync link between the nodes fails

  :::: rack A ::::::::        :::: rack B ::::::::
  +---------------+           +---------------+
  | node 1 (id 1) |-----X-----| node 2 (id 2) |
  | 1 vote        |  corosync | 1 vote        |
  +-------+-------+           +-------+-------+
          |                           |
          | TCP                       | TCP
          |     :::: site C ::::      |
          |     +-------------+       |
          +---->| qnetd       |<------+
                | 1 vote      |
                +-------------+

  qnetd votes for the lowest node id (default tie_breaker)
  node 1 + qnetd = 2 of 3  --> quorate: may run HA guests
  node 2         = 1 of 3  --> inquorate: read-only; self-fences if it held HA guests
  qnetd also unreachable from node 1 --> both sides inquorate, nothing restarts

  Legend: X failed link   :::: failure domain   --> votes / outcome
```

## HA, fencing and replication timing

- HA needs 3+ nodes (or 2 + QDevice), shared or replicated storage and redundant hardware. Watchdog: hardware if present, else `softdog`.
- A node whose LRM loses its quorum lock stops renewing the watchdog and resets after 60 s. Only then are its resources recovered elsewhere.
- Typical detection plus failover is about 2 minutes. VERIFIED_PRIMARY, [ha-manager], checked 2026-10-29.
- The cluster cannot recover a guest whose data lives only on the failed node.
- ZFS storage replication (pvesr): minimum interval 1 minute, ZFS only. HA works, but writes since the last sync are lost. VERIFIED_PRIMARY, [pvesr], checked 2026-10-29.
- Replication RPO = interval + any failed-job backlog. Failed jobs retry every 30 minutes.
- Choose the shutdown policy deliberately: default `conditional`; `migrate` moves HA guests off a node being shut down.

```text
HA recovery timeline after a node isolation (Proxmox VE)

  t=0       node isolated (corosync lost)
  t~token   survivors re-form membership, still quorate
  t<=60s    isolated node: watchdog expires --> hard reset (self-fence)
  t>60s     CRM marks node fenced --> resources "recovery" --> start on a survivor
  t~120s    guest booted; application recovery time is extra

  RTO budget = detection + fence wait + boot + app start + client reconnect
```

## Topology decision table

| Requirement                       | Single host | 2 nodes + QDevice + ZFS repl.  | 3+ nodes + ZFS repl. | 3+ nodes + Ceph (hyper-converged)                    |
| --------------------------------- | ----------- | ------------------------------ | -------------------- | ---------------------------------------------------- |
| Automatic restart after host loss | no          | yes, RPO = repl. interval      | yes, RPO = interval  | yes, RPO ~0 (synchronous replicas)                   |
| Live migration without data copy  | n/a         | delta only if replicated       | delta if replicated  | yes                                                  |
| Minimum network                   | 1 GbE       | dedicated corosync + repl link | same                 | 10 GbE+ storage; 25 GbE+ for NVMe (VERIFIED_PRIMARY) |
| Self-healing after a node loss    | n/a         | no                             | no                   | only when node count > replica count                 |
| Operational load                  | lowest      | low                            | medium               | highest; Ceph skills required                        |
| Good fit                          | edge, lab   | small site needing HA          | small cluster        | zero-RPO VM storage; 4+ nodes preferred              |

- Choose the simplest column that meets the stated RTO and RPO.
- Ceph on exactly three nodes with size 3 runs degraded after a node loss. It cannot re-replicate until the node returns ([pveceph]).

## Patterns and anti-patterns

| Pattern                               | Use when              | Anti-pattern                   | Why it fails                                 |
| ------------------------------------- | --------------------- | ------------------------------ | -------------------------------------------- |
| 2 nodes + QDevice in a third domain   | small site needing HA | 2 nodes, no QDevice            | either node loss freezes management          |
| Odd node count, votes spread by rack  | 3+ nodes              | majority of votes in one rack  | losing that rack loses quorum for all        |
| Two corosync links, separate switches | any cluster           | one link on one bond or switch | one switch fault splits membership           |
| QDevice only on even node counts      | 2, 4, 6 nodes         | QDevice on 3 or 5 nodes        | QDevice failure leaves zero spare tolerance  |
| Lowest common guest CPU model         | live-migration groups | `host` CPU on mixed hardware   | migration fails to the older host            |
| Alert on replication state            | ZFS replication       | trusting the schedule          | a silently failing job stretches RPO to days |

## Failure modes and tests

| Failure                             | Symptom                                      | Blast radius              | Proving test                                                           |
| ----------------------------------- | -------------------------------------------- | ------------------------- | ---------------------------------------------------------------------- |
| Quorum held, no capacity for guests | HA guests stuck in recovery state            | guests of the failed node | power off the largest node; time until all HA guests run               |
| Watchdog absent or disabled         | two writers after a partition (split-brain)  | data on shared storage    | isolate one node's corosync links; it resets; guests start once        |
| qnetd shares a domain with one node | survivor goes inquorate with that site       | whole 2-node cluster      | lose that node's site; the other side keeps quorum                     |
| Both corosync links on one switch   | membership flaps or splits on a switch fault | whole cluster management  | fail each switch in turn; membership stays stable                      |
| Replication job failing silently    | RPO grows with no alarm                      | replicated guests         | alert on replication state; restore-test the last replica              |
| Votes concentrated in one rack      | rack loss stops the whole cluster            | all guests                | `just quorum` per rack; vote and capacity count per rack in the design |

## Worked example

Three nodes: pve1 and pve2 in rack A, pve3 in rack B. Requirement: survive any node and the loss of rack A.

```text
$ just quorum examples/quorum.json                 (exit 1)
  total_votes 3, quorum 2; each single node lost --> 2 votes, quorate
  domain:rack-a lost --> 1 vote: "cluster loses quorum (2 of 3 votes needed)"

$ just quorum examples/quorum-qdevice.json         (exit 0, fix: 2 nodes + QDevice at site C)
  total_votes 3, quorum 2, qdevice_votes 1
  rack-a lost --> 2 | rack-b lost --> 2 | qdevice lost --> 2   all quorate, status pass
```

Then check membership timing for a five-node cluster:

1. Coefficient 650 ms: token = 3000 + 3 x 650 = 4,950 ms; consensus = 1.2 x 4,950 = 5,940 ms; total ~10.9 s.
2. Coefficient 125 ms: token = 3000 + 3 x 125 = 3,375 ms; consensus = 4,050 ms; total ~7.4 s.
3. Both sit well under the 30-45 s concern. Add the 60 s watchdog and guest boot to estimate RTO (~2 min), then drill it.

Quorum is necessary, not sufficient. Run `just capacity` for memory and `just ceph` for storage before signing off.

## Review checklist

- [ ] Vote count per rack and per site written down; `just quorum` passes every `must_survive` scenario.
- [ ] QDevice only on an even node count, in a third failure domain.
- [ ] Two corosync links on separate physical networks; latency under 5 ms measured.
- [ ] Hardware watchdog present or `softdog` confirmed; isolation test resets the node.
- [ ] Every HA guest has shared or replicated storage; replication lag alerted.
- [ ] Capacity survives the largest node loss (`just capacity`); largest guest fits one survivor.
- [ ] Guest CPU model pinned to the lowest common host; same CPU vendor in each migration group.
- [ ] Shutdown policy chosen and recorded; RTO includes fence wait and application start.

## Further reading

Links checked 2026-10-29.

Primary sources cited above (VERIFIED_PRIMARY, master = PVE 9.x)

- [pvecm]: cluster manager source. [ha-manager]: HA manager source. [pvesr]: storage replication source. [pveceph]: Ceph source.

Proxmox VE

- [Proxmox VE admin guide (single page)](https://pve.proxmox.com/pve-docs/pve-admin-guide.html): read this for the whole current-release reference in one place.
- [Cluster manager](https://pve.proxmox.com/pve-docs/chapter-pvecm.html): read this for network requirements, QDevice support rules, corosync links and token tuning.
- [High availability](https://pve.proxmox.com/pve-docs/chapter-ha-manager.html): read this for fencing, watchdog, resource states, affinity rules and shutdown policy.
- [Storage replication](https://pve.proxmox.com/pve-docs/chapter-pvesr.html): read this for ZFS replication schedules, error handling and RPO caveats.
- [Ceph on Proxmox VE](https://pve.proxmox.com/pve-docs/chapter-pveceph.html): read this for hyper-converged sizing, network and pool defaults.
- [QEMU/KVM VMs](https://pve.proxmox.com/pve-docs/chapter-qm.html): read this for CPU types, VirtIO devices, guest agent and passthrough.
- [Linux containers](https://pve.proxmox.com/pve-docs/chapter-pct.html): read this for LXC isolation limits, privileged vs unprivileged, and when to use a VM instead.
- [Software-defined network](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html): read this for zones, VNets and EVPN/VXLAN overlays shared with the network architect.

Consensus and virtualisation fundamentals

- [etcd FAQ: why an odd number of members](https://etcd.io/docs/v3.5/faq/): read this for majority-quorum arithmetic that applies to any consensus cluster.
- [QEMU CPU models](https://www.qemu.org/docs/master/system/qemu-cpu-models.html): read this for migration-safe CPU model selection.

[pvecm]: https://raw.githubusercontent.com/proxmox/pve-docs/master/pvecm.adoc [ha-manager]: https://raw.githubusercontent.com/proxmox/pve-docs/master/ha-manager.adoc [pvesr]:
https://raw.githubusercontent.com/proxmox/pve-docs/master/pvesr.adoc [pveceph]: https://raw.githubusercontent.com/proxmox/pve-docs/master/pveceph.adoc
