# Architecture and cluster

A Proxmox VE node is Debian plus the PVE stack (pve-manager, qemu-server, pve-container, pve-storage, pve-cluster). Several nodes form a cluster over Corosync and share configuration through pmxcfs at
`/etc/pve`. Sources: [pmxcfs chapter](../documents/research-sources-20261107/pve-admin-chapter-pmxcfs.html), [pvecm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvecm.md).

## Contents

- [Node](#node)
- [pmxcfs and /etc/pve](#pmxcfs-and-etcpve)
- [Cluster and quorum](#cluster-and-quorum)
- [Design rules](#design-rules)

## Node

- The release follows Debian: PVE 9.x runs on Debian 13 trixie. `VERIFIED_PRIMARY` ([Upgrade from 8 to 9](../documents/research-sources-20261107/pve-wiki-upgrade-from-8-to-9.md)).
- Release dates: 9.1 on 19 November 2025, 9.2 on 21 May 2026. `VERIFIED_PRIMARY` ([Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html)). A node on 9.1.x with the no-subscription
  repository sees the 9.2 packages as ordinary pending updates (see
  the Learned entry below).
- The web UI and API listen on TCP 8006 over HTTPS (`pveproxy`). `VERIFIED_PRIMARY` ([API wiki](../documents/research-sources-20261107/pve-wiki-api.md)).

## pmxcfs and /etc/pve

- pmxcfs is "a database-driven file system for storing configuration files, replicated in real time to all cluster nodes using corosync"; data lives in an SQLite database on disk, the file system size
  limit is 128 MiB, and `/etc/pve` becomes **read-only when a node loses quorum**. `VERIFIED_PRIMARY` (pmxcfs chapter).
- What lives there: `storage.cfg`, `user.cfg` (users, groups, ACLs, tokens without secrets), `domains.cfg` (realms), `priv/` (secrets, root-only), `nodes/<name>/` (per-node config,
  `qemu-server/<vmid>.conf`, `lxc/<vmid>.conf`, certificates), `firewall/`, `sdn/`, `status.cfg` (external metric servers), `vzdump.cron`. `VERIFIED_PRIMARY` (pmxcfs file table;
  [network](../documents/research-sources-20261107/pve-wiki-network-configuration.md) for `sdn/`).
- `/etc/pve/local` is a symlink to this node's `nodes/<name>/`. `VERIFIED_PRIMARY` ([Certificate Management](../documents/research-sources-20261107/pve-wiki-certificate-management.md)).
- Consequence for tooling: read config through the API or `pvesh` rather than parsing `/etc/pve` files where an endpoint exists; the file formats are internal and the API applies permissions.

## Cluster and quorum

- Create and join: `pvecm create <name>` on the first node, `pvecm add <existing-node-address>` on each new one; `pvecm status` shows votes and quorum. `VERIFIED_PRIMARY` (pvecm chapter).
- Use at least three nodes for reliable quorum; a two-node cluster gets its third vote from a **QDevice**. Corosync needs low, steady latency rather than bandwidth; keep it off networks carrying
  storage or migration traffic (a dedicated 1 Gbit NIC is usually enough). `VERIFIED_PRIMARY` (pvecm chapter, Requirements and Cluster Network).
- A node without quorum keeps running its guests but cannot change configuration (`/etc/pve` read-only): no starts of new guests, no config edits, no HA actions on it. `VERIFIED_PRIMARY` for
  read-only; the guest-level effect is `VERIFIED_SECONDARY` (follows from it).
- A single node is a cluster of one for the API: `GET /cluster/status` returns one `node` row and no `cluster` row (observed, see below).

## Design rules

- Treat a node's identity (name, address) as fixed once clustered; renaming a clustered node is a documented multi-step procedure, not an edit.
- Plan HA only with three or more nodes and shared or replicated storage ([ha-and-replication.md](ha-and-replication.md)).
- A lab single node and a production cluster differ in quorum behaviour; do not carry a lab result about `/etc/pve` writes to a cluster without checking quorum.

> **Learned 2026-11-07 (a)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /cluster/status`, `/nodes/localhost/version`, `/nodes/localhost/apt/versions`) ·
> Falsifier: a single-node 9.x install whose `/cluster/status` carries a `cluster` row
> On a standalone node `GET /cluster/status` returns only a `node` row (no `quorate` field, `online: 1`). `localhost` is accepted as the node name in API paths. A 9.1.5 node on the no-subscription
> repository listed `proxmox-ve 9.2.0` and `pve-manager 9.2.26` as ordinary pending updates: a minor release arrives through `apt full-upgrade`, not a separate upgrade procedure.
