# HA and replication

High availability with `ha-manager`, placement rules, fencing, the load balancer, and ZFS storage replication. Sources: [HA
chapter](../documents/research-sources-20261107/pve-admin-chapter-ha-manager.md), [pvesr chapter](../documents/research-sources-20261107/pve-admin-chapter-pvesr.md),
[Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html), [pvecm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvecm.md).

## Contents

- [Requirements](#requirements)
- [Managing resources](#managing-resources)
- [Placement rules (9.x)](#placement-rules-9x)
- [Fencing and maintenance](#fencing-and-maintenance)
- [Storage replication](#storage-replication)

## Requirements

At least three cluster nodes for reliable quorum, shared storage for the guests, redundant hardware and reliable server components; a hardware watchdog is optional (the kernel `softdog` otherwise).
`VERIFIED_PRIMARY` (HA chapter, Requirements). A single node or a two-node cluster without a QDevice is not an HA platform ([architecture-and-cluster.md](architecture-and-cluster.md)).

## Managing resources

```bash
ha-manager add vm:100            # write
ha-manager set vm:100 --state stopped|started
ha-manager migrate vm:100 node2  # live; relocate = stop, move, start
ha-manager config; ha-manager status   # reads ("quorum OK" first)
ha-manager remove vm:100
```

`VERIFIED_PRIMARY` (HA chapter, Management Tasks). An HA-managed guest is started and stopped through HA; a plain `qm stop` is undone by the manager.

## Placement rules (9.x)

- 9.0 replaced HA groups with **rules**: node affinity rules (where a resource may run, with priorities) and resource affinity rules (keep resources together or apart). Existing groups were migrated
  to node affinity rules. `VERIFIED_PRIMARY` (HA chapter note; Roadmap 9.0 highlights).
- 9.2 added dynamic load balancing in the Cluster Resource Scheduler (live utilisation, automatic migration of HA guests) and `disarm-ha` / `arm-ha` for cluster-wide maintenance without fencing.
  Upgrading from before pve-ha-manager 5.2.4 while disarmed and migrating can stall: keep HA armed during the upgrade. `VERIFIED_PRIMARY` (Roadmap 9.2 highlights and known issues).

## Fencing and maintenance

- A node that loses quorum with active HA resources fences itself through its watchdog (reset) so the resources can start elsewhere. `VERIFIED_PRIMARY` (HA chapter, How It Works and fencing).
- Before network or Corosync work on an HA cluster, disarm HA (9.2+) or put nodes in maintenance; a Corosync outage otherwise reboots every node with HA resources.

## Storage replication

- `pvesr` replicates guest volumes between nodes on a schedule (asynchronous) and works on local ZFS (`zfspool`). HA may use it, but "there may be some data loss between the last synced time and the
  time a node failed". `VERIFIED_PRIMARY` (pvesr chapter).
- Since 9.0, creating or scheduling replication jobs needs `VM.Replicate` on `/vms/<vmid>`. `VERIFIED_PRIMARY` (Roadmap 9.0 breaking changes).
