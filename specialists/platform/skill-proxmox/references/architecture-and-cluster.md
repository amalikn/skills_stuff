---
Title: Architecture and cluster
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/architecture-and-cluster.md
Last reviewed: 2026-11-07
Summary: Node stack, pmxcfs and /etc/pve, Corosync clusters and quorum, QDevice, removing a node, arm64 hosts, and design rules for node identity.
---

# Architecture and cluster

A Proxmox VE node is Debian plus the PVE stack (pve-manager, qemu-server, pve-container, pve-storage, pve-cluster). Several nodes form a cluster over Corosync and share configuration through pmxcfs at
`/etc/pve`. Sources: [pmxcfs chapter](../documents/research-sources-20261107/pve-admin-chapter-pmxcfs.html), [pvecm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvecm.md).

## Contents

- [Node](#node)
- [pmxcfs and /etc/pve](#pmxcfs-and-etcpve)
- [Cluster and quorum](#cluster-and-quorum)
- [Removing a node](#removing-a-node)
- [arm64 hosts](#arm64-hosts)
- [Design rules](#design-rules)

## Node

- The release follows Debian: PVE 9.x runs on Debian 13 trixie. `VERIFIED_PRIMARY` ([Upgrade from 8 to 9](../documents/research-sources-20261107/pve-wiki-upgrade-from-8-to-9.md)).
- Release dates: 9.1 on 19 November 2025, 9.2 on 21 May 2026. `VERIFIED_PRIMARY` ([Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html)). A node on 9.1.x with the no-subscription repository sees the 9.2 packages as ordinary pending updates (see
  the Learned entry below).
- The web UI and API listen on TCP 8006 over HTTPS (`pveproxy`). `VERIFIED_PRIMARY` ([API wiki](../documents/research-sources-20261107/pve-wiki-api.md)).

## pmxcfs and /etc/pve

```text
  node1                      node2                      node3
  +----------------------+   +----------------------+   +----------------------+
  | pveproxy :8006 (API) |   | pveproxy :8006 (API) |   | pveproxy :8006 (API) |
  | qemu-server  pct     |   | qemu-server  pct     |   | qemu-server  pct     |
  | pmxcfs -> /etc/pve   |   | pmxcfs -> /etc/pve   |   | pmxcfs -> /etc/pve   |
  |   (SQLite on disk)   |   |   (SQLite on disk)   |   |   (SQLite on disk)   |
  +----------+-----------+   +----------+-----------+   +----------+-----------+
             |                          |                          |
             +---------- Corosync: own low-latency link ----------+
                  (keep storage and migration traffic off it)

  quorum lost on a node -> its /etc/pve turns read-only; running guests keep running
```

- pmxcfs is "a database-driven file system for storing configuration files, replicated in real time to all cluster nodes using corosync"; data lives in an SQLite database on disk, the file system size
  limit is 128 MiB, and `/etc/pve` becomes **read-only when a node loses quorum**. `VERIFIED_PRIMARY` (pmxcfs chapter).
- What lives there: `storage.cfg`, `user.cfg` (users, groups, ACLs, tokens without secrets), `domains.cfg` (realms), `priv/` (secrets, root-only), `nodes/<name>/` (per-node config,
  `qemu-server/<vmid>.conf`, `lxc/<vmid>.conf`, certificates), `firewall/`, `sdn/`, `status.cfg` (external metric servers), `vzdump.cron`. `VERIFIED_PRIMARY` (pmxcfs file table; [network](../documents/research-sources-20261107/pve-wiki-network-configuration.md) for `sdn/`).
- `/etc/pve/local` is a symlink to this node's `nodes/<name>/`. `VERIFIED_PRIMARY` ([Certificate Management](../documents/research-sources-20261107/pve-wiki-certificate-management.md)).
- Consequence for tooling: read config through the API or `pvesh` rather than parsing `/etc/pve` files where an endpoint exists; the file formats are internal and the API applies permissions.

## Cluster and quorum

- Create and join: `pvecm create <name>` on the first node, `pvecm add <existing-node-address>` on each new one; `pvecm status` shows votes and quorum. `VERIFIED_PRIMARY` (pvecm chapter).
- Use at least three nodes for reliable quorum; a two-node cluster gets its third vote from a **QDevice**. Corosync needs low, steady latency rather than bandwidth; keep it off networks carrying
  storage or migration traffic (a dedicated 1 Gbit NIC is usually enough). `VERIFIED_PRIMARY` (pvecm chapter, Requirements and Cluster Network).
- A node without quorum keeps running its guests but cannot change configuration (`/etc/pve` read-only): no starts of new guests, no config edits, no HA actions on it. `VERIFIED_PRIMARY` for
  read-only; the guest-level effect is `VERIFIED_SECONDARY` (follows from it).
- A single node is a cluster of one for the API: `GET /cluster/status` returns one `node` row and no `cluster` row (observed, see below).

## Removing a node

A **write** with no undo; read the whole pvecm procedure first. `VERIFIED_PRIMARY` ([pvecm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvecm.md), Remove a Cluster Node).

1. Before: move every guest off the node, back up its local data, and delete every replication job that involves it (a job left behind becomes irremovable; migrating a replicated guest off the node
   reverses the job's direction toward it). Remove a QDevice first if one is configured. With Ceph, destroy the node's OSDs, monitor and manager while the remaining cluster has room.
2. Power the node off and make sure it cannot come back on the cluster network with its current configuration; a returning node can break the cluster.
3. On a remaining node: `pvecm delnode <node>`, then `pvecm nodes` to confirm. An error `could not kill node (error = cs_err_not_exist)` is Corosync failing to kill an offline node and can be ignored.
4. Clean up: `/etc/pve/nodes/<node>/` (recover what you need, then remove), the node's key in `/etc/pve/priv/authorized_keys`, and the node in any HA rule. A node rejoining with the same name or
   address runs `pvecm updatecerts` once to refresh its fingerprint cluster-wide.

## arm64 hosts

Proxmox VE 9.2 for arm64 was released on 2026-08-05: official for NVIDIA Grace and Vera, best effort on other UEFI ARMv9-A or newer hardware. Hosts must boot UEFI and describe hardware through ACPI,
so device-tree boards such as the Raspberry Pi are not supported. It shares code base, repositories and lifecycle with x86-64; SeaBIOS for VMs, AMD SEV and Intel GVT-g are unavailable, and live
migration works only between nodes of the same architecture. `VERIFIED_PRIMARY` ([Roadmap](../documents/research-sources-20261109/pve-wiki-roadmap.html), "Proxmox VE 9.2 for 64-bit ARM"). Running it nested in a Parallels arm64 VM on a Mac is untested here (`UNVERIFIED`); the Mac's own arm64 VMs stay with `skill-vagrant`.

## Design rules

- Treat a node's identity (name, address) as fixed once clustered; renaming a clustered node is a documented multi-step procedure, not an edit.
- Plan HA only with three or more nodes and shared or replicated storage ([ha-and-replication.md](ha-and-replication.md)).
- A lab single node and a production cluster differ in quorum behaviour; do not carry a lab result about `/etc/pve` writes to a cluster without checking quorum.

> **Learned 2026-11-07 (a)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /cluster/status`, `/nodes/localhost/version`, `/nodes/localhost/apt/versions`) ·
> Falsifier: a single-node 9.x install whose `/cluster/status` carries a `cluster` row On a standalone node `GET /cluster/status` returns only a `node` row (no `quorate` field, `online: 1`).
> `localhost` is accepted as the node name in API paths. A 9.1.5 node on the no-subscription repository listed `proxmox-ve 9.2.0` and `pve-manager 9.2.26` as ordinary pending updates: a minor release
> arrives through `apt full-upgrade`, not a separate upgrade procedure.
