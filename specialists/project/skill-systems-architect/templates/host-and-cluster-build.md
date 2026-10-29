---
Title: Host and cluster build template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Build sheet for a host or virtualisation cluster covering sizing under failure, quorum, storage, network bonds and VLANs, backup, monitoring and acceptance.
---

# <cluster-name> host and cluster build

Worked example: [examples/filled/host-and-cluster-build.md](../examples/filled/host-and-cluster-build.md)

## How to use

- One sheet per cluster or standalone host.
- Size from the capacity model, not node count. The cluster must carry required load after losing the largest host.
- Where the requirement says so, also remove a whole rack or power domain.
- Run the helpers and paste each exit code (0 pass, 1 findings, 2 invalid input):
  - memory per scenario: `just capacity <plan.json>` ([capacity_check.py](../scripts/capacity_check.py));
  - votes per node, domain and QDevice loss: `just quorum <cluster.json>` ([quorum_check.py](../scripts/quorum_check.py));
  - Ceph plan capacity and min_size: `just ceph <pools.json>` ([ceph_capacity.py](../scripts/ceph_capacity.py)).
- Agree section 5 (host networking) with skill-network-architect as an interface contract.
- Label platform facts with version and source (VERIFIED_PRIMARY from vendor docs).
- Rules and red flags: [virtualisation](../references/virtualization-and-proxmox.md), [storage](../references/storage-and-data.md),
  [red flags](../references/red-flags.md).

## 1. Purpose and requirements

| Field                      | Value                                                                               |
| -------------------------- | ----------------------------------------------------------------------------------- |
| Workloads hosted           | <service list, REQ IDs>                                                             |
| Availability model         | *HA restart, live migration, application-level redundancy, or none (accepted SPOF)* |
| Failure tolerance required | *largest host / one rack / one power feed*                                          |
| Platform and version       | <hypervisor or OS> <version> (support end <date>)                                   |
| Owner / on-call            | <role> / <role>                                                                     |

## 2. Nodes and sizing

| Node     | Failure domain (rack, PDU feed) | CPU (cores, model) | Memory (GiB) | Reserve for host (GiB) | Local disks | NICs | Out-of-band controller |
| -------- | ------------------------------- | ------------------ | ------------ | ---------------------- | ----------- | ---- | ---------------------- |
| <node-1> | rack A, feed A                  |                    |              |                        |             |      |                        |

| Scenario          | Usable memory (GiB) | Demand (GiB) | vCPU:pCPU | Storage used / plan TB (`just ceph`) | Meets? (`just capacity` exit) |
| ----------------- | ------------------- | ------------ | --------- | --------------------- | ----------------------------- |
| normal            |                     |              |           |                       |                               |
| largest host lost |                     |              |           |                       |                               |
| rack / feed lost  |                     |              |           |                       |                               |

## 3. Quorum and membership

```text
Quorum map for <cluster-name> (fill in; one line per failure domain)

  :::: <domain A> ::::   node-1 (1 vote)   node-2 (1 vote)
  :::: <domain B> ::::   node-3 (1 vote)
  :::: <domain C> ::::   qdevice (1 vote, even node counts only)

  total <n>   quorum = floor(<n> / 2) + 1 = <q>
  domain A lost --> <votes left> of <n> --> quorate yes/no   (`just quorum` result)
  Legend: :::: failure domain   --> outcome
```

| Item                                | Value                                                |
| ----------------------------------- | ---------------------------------------------------- |
| Cluster network(s) for membership   | *dedicated link or VLAN, redundancy, latency budget* |
| Witness location and failure domain |                                                      |
| Fencing method and test             |                                                      |
| Behaviour on quorum loss            | *workloads stop / freeze / continue*                 |

## 4. Storage

| Pool | Type (ZFS, Ceph, NFS, iSCSI) | Redundancy (mirror, raidz, size/min_size) | Usable / plan limit | Failure domain rule | Rebuild path and time | Latency target | `just ceph` exit |
| ---- | ---------------------------- | ----------------------------------------- | ------------------- | ------------------- | --------------------- | -------------- | ---------------- |
|      |                              |                                           |                     |                     |                       |                |                  |

## 5. Host networking

| Function           | Bond (mode, LACP rate, members) | VLAN / bridge | MTU | Switch pair / ports | Failover time measured | Interface contract |
| ------------------ | ------------------------------- | ------------- | --- | ------------------- | ---------------------- | ------------------ |
| management         |                                 |               |     |                     |                        | IF-<nnn>           |
| cluster membership |                                 |               |     |                     |                        |                    |
| storage            |                                 |               |     |                     |                        |                    |
| guest traffic      |                                 |               |     |                     |                        |                    |
| migration          |                                 |               |     |                     |                        |                    |

## 6. Backup, monitoring and lifecycle

| Item                                                           | Value                                |
| -------------------------------------------------------------- | ------------------------------------ |
| Backup target, schedule, retention, restore test ref           | *see backup-and-restore-test*        |
| Configuration backup of hosts and cluster                      |                                      |
| Monitoring (node, quorum, storage health, NIC/bond state, OOB) | *signal -> threshold -> alert owner* |
| Patching ring and window                                       | *see lifecycle-and-patching*         |

## 7. Acceptance

| Test             | Method                            | Pass criterion                                 | Result | Date |
| ---------------- | --------------------------------- | ---------------------------------------------- | ------ | ---- |
| Host loss        | power off largest host under load | workloads restart within <n> min, no data loss |        |      |
| Bond member loss | pull one link per bond            | no membership change, storage latency < <n> ms |        |      |
| Quorum partition | isolate one node                  | minority fences, majority continues            |        |      |
| Restore          | restore one VM from backup        | service usable within RTO                      |        |      |

## 8. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
