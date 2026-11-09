---
Title: Storage
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/storage.md
Last reviewed: 2026-11-07
Summary: Storage types and content types in storage.cfg, the import content type, hyperconverged Ceph with pveceph, and how to choose a storage.
---

# Storage

Storage is defined cluster-wide in `/etc/pve/storage.cfg` and addressed as `<storage-id>:<volume>`. Sources: [pvesm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvesm.md), [PBS storage](../documents/research-sources-20261107/pve-wiki-storage-pbs.md).

## Contents

- [Types](#types)
- [Content types](#content-types)
- [The import content type](#the-import-content-type)
- [Hyperconverged Ceph](#hyperconverged-ceph)
- [Choosing](#choosing)

## Types

`VERIFIED_PRIMARY` (pvesm chapter, storage type table):

| Description           | Plugin type                   | Level | Shared | Snapshots                 |
| --------------------- | ----------------------------- | ----- | ------ | ------------------------- |
| ZFS (local)           | `zfspool`                     | both  | no     | yes                       |
| Directory             | `dir`                         | file  | no     | qcow2 (internal or chain) |
| BTRFS                 | `btrfs`                       | file  | no     | yes                       |
| NFS / CIFS            | `nfs`, `cifs`                 | file  | yes    | qcow2                     |
| Proxmox Backup        | `pbs`                         | both  | yes    | n/a                       |
| CephFS                | `cephfs`                      | file  | yes    | yes                       |
| LVM                   | `lvm`                         | block | no*    | qcow2 volume chains       |
| LVM-thin              | `lvmthin`                     | block | no     | yes                       |
| Ceph/RBD              | `rbd`                         | block | yes    | yes                       |
| iSCSI, ZFS over iSCSI | `iscsi`, `iscsidirect`, `zfs` | block | yes    | varies                    |

\* LVM on top of shared iSCSI or FC storage is shared. A default installation creates `local` (dir, `/var/lib/vz`) and `local-lvm` (lvmthin, VG `pve`, pool `data`) on the system disk. Thin pools can
over-commit: watch `used_fraction` (the node report warns at 85 %).

## Content types

`images` (VM disks), `rootdir` (container data), `vztmpl` (container templates), `backup` (vzdump), `iso`, `snippets` (hook scripts, cloud-init user data), `import` ("OVAs and VM disk images that can
be imported from this storage"). Not every type supports every content. On a directory storage they map to `images/<VMID>/`, `template/iso/`, `template/cache/`, `dump/`, `snippets/` and `import/`.
`VERIFIED_PRIMARY` (pvesm chapter, Storage Configuration and Directory Backend).

`pvesm set <id> --content ...` **replaces** the list. Name every type the storage keeps, or a running workload loses its storage.

## The import content type

- `import` is **not enabled by default**; add it before OpenTofu's `import_from` or `download_file` with `content_type = "import"` can use the storage. `VERIFIED_PRIMARY` ([bpg download_file](../documents/research-sources-20261107/bpg-provider-virtual_environment_download_file.md)).
- A disk is imported with `qm set <vmid> --scsi0 <target>:0,import-from=<source>` where the source is a path or a volume (`local:import/<file>.qcow2`). `VERIFIED_PRIMARY` ([qm chapter](../documents/research-sources-20261107/pve-admin-chapter-qm.html), cloud-init
  example).
- Who may put a file there matters: `POST /nodes/{node}/storage/{storage}/download-url` (the provider's `download_file`) needs `Datastore.AllocateTemplate` on the storage **and** either `Sys.Audit` +
  `Sys.Modify` on `/` or the newer `Sys.AccessNetwork` on `/nodes/{node}`. `VERIFIED_PRIMARY` for 9.1.5 from the installed API source ([excerpt](../documents/research-sources-20261107/pve-9.1.5-installed-storage-download-url-permissions.txt)); the bpg page names only `Sys.Audit` and `Sys.Modify`
  ([bpg download_file](../documents/research-sources-20261107/bpg-provider-virtual_environment_download_file.md)), and the pveum chapter's privilege list does not yet name `Sys.AccessNetwork`. Either way the right lets the token make the node fetch any URL (probing the host's network), so a
  pool-scoped automation token is better kept without it: a root-run step places the file and the token only imports it ([access-control.md](access-control.md#worked-example-an-opentofu-identity)).

## Hyperconverged Ceph

Proxmox VE runs Ceph on the cluster nodes themselves and manages it with `pveceph` (or the GUI wizard, which the chapter recommends). Source: [pveceph chapter](../documents/research-sources-20261109/pve-admin-chapter-pveceph.html), fetched 2026-11-09. All
`VERIFIED_PRIMARY`; every command below is a **write**.

| Step               | Command (run on)                                                   | Effect                                                                             |
| ------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Packages           | `pveceph install` (each node)                                      | Adds `/etc/apt/sources.list.d/ceph.sources`, installs Ceph                         |
| Initial config     | `pveceph init --network <ceph-cidr>` (one node)                    | Writes `/etc/pve/ceph.conf` (shared by pmxcfs), symlinked at `/etc/ceph/ceph.conf` |
| Monitors, managers | `pveceph mon create`, `pveceph mgr create`                         | One per node that should carry them                                                |
| OSDs               | `pveceph osd create /dev/sdX [-db_dev /dev/sdY -wal_dev /dev/sdZ]` | Disk must be wiped of earlier ZFS/OSD traces first                                 |
| Pool               | `pveceph pool create <name> --add_storages`                        | Defaults: 128 PGs, `size` 3, `min_size` 2; also adds the `rbd` storage             |
| Erasure-coded pool | `pveceph pool create <name> --erasure-coding k=2,m=1`              | Creates data and metadata pools; `min_size` defaults to k (m = 1) or k + 1         |
| CephFS             | `pveceph fs create --pg_num 128 --add-storage`                     | Needs metadata servers; adds the `cephfs` storage                                  |

- Size: at least three nodes and at least 12 OSDs, spread evenly. Never set `min_size 1` on a replicated pool: I/O with one replica left risks data loss, incomplete PGs or unfound objects.
- Releases: Proxmox VE 9.x offers Ceph Squid (19.2) and Tentacle (20.2, the option added in 9.2); the chapter's FastEC erasure-coding I/O path is Tentacle-only. Check `ceph versions` before applying a
  version-specific procedure.
- Removing a node that carries OSDs: see [architecture-and-cluster.md](architecture-and-cluster.md#removing-a-node); destroying an OSD starts a rebalance, so check free space first.

```text
  node1             node2             node3           (>= 3 nodes, >= 12 OSDs, spread evenly)
  mon  mgr          mon  mgr          mon  mgr
  OSD OSD OSD OSD   OSD OSD OSD OSD   OSD OSD OSD OSD
        |                 |                 |
        +----- Ceph network (pveceph init --network <cidr>) -----+
                          |
        replicated pool: size 3, min_size 2, 128 PGs  --> rbd storage    (VM disks, CT volumes)
        CephFS (pveceph mds create; fs create)        --> cephfs storage (ISOs, CT templates, backups, snippets)
```

## Choosing

- Lab single node: `local` (dir) for ISOs, templates, snippets, import and qcow2 disks that need snapshots; `local-lvm` for raw thin disks.
- Shared storage (Ceph RBD, NFS, iSCSI with LVM) is the precondition for live migration without moving disks and for HA ([ha-and-replication.md](ha-and-replication.md)).
- Backups go to a `pbs` storage when a Proxmox Backup Server exists (deduplicated, incremental) or to a `backup`-content storage ([backup-and-restore.md](backup-and-restore.md)).

> **Learned 2026-11-07 (b)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /storage`, `/nodes/localhost/storage`) and the smc-resiliency x86 lab setup script
> (uncommitted on 2026-11-07) · Falsifier: a 9.x node where `pvesm set local --content ...,import` leaves the other types in place when they are omitted The worked example adds `import` with the full
> list (`pvesm set local --content images,snippets,backup,rootdir,iso,vztmpl,import`), guarded by a check of `storage.cfg` so a rerun changes nothing. After it, the API lists `import` among `local`'s
> content and OpenTofu imports `local:import/<file>.qcow2` with no SSH block. The same lab showed `local-lvm` (thin) at 90.6 % used while the directory storage was at 43 %: thin-pool fill is the first
> storage risk on a single-disk lab.
