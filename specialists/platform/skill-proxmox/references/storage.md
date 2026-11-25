---
Title: Storage
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/storage.md
Last reviewed: 2026-11-19
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
- [ZFS root: installer, ARC and adding a boot mirror](#zfs-root-installer-arc-and-adding-a-boot-mirror)

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

## ZFS root: installer, ARC and adding a boot mirror

> **Learned 2026-11-24 (a)** · Proxmox VE 9.2 (admin guide 9.2.15 of 2026-11-18) · VERIFIED_PRIMARY · Source: [Host System Administration, "Limit ZFS Memory Usage" and "Changing a failed bootable device"](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html), read 2026-11-24 · Falsifier: a 9.2 ZFS install whose `/etc/modprobe.d/zfs.conf` has no `zfs_arc_max`, or a mirror that boots without `proxmox-boot-tool init` on the new ESP.
> - The installer writes the ARC limit to `/etc/modprobe.d/zfs.conf`: 10% of host memory, clamped to 16 GiB (since 8.1; before that ZFS's own 50% or 62.5% applied). On 32 GB that is about 3.2 GiB; the installer's narrow "ARC max size" field can show only the first digits (`318` for 3180 MiB). Check after boot: `cat /etc/modprobe.d/zfs.conf; cat /sys/module/zfs/parameters/zfs_arc_max`. The guide's sizing rule of thumb is 2 GiB base plus 1 GiB per TiB of pool.
> - Choose **ZFS (RAID0)** on a single boot disk, not ext4, when a second disk may come later: a single-disk vdev becomes a mirror with `zpool attach`; ext4 or LVM needs a reinstall. Never `zpool add` (a stripe with no redundancy).
> - Adding the second boot disk follows the guide's failed-bootable-device steps with `attach` in place of `replace`: `sgdisk <healthy> -R <new>`, `sgdisk -G <new>`, `zpool attach -f rpool <existing zfs part> <new zfs part>` (wait for the resilver), `proxmox-boot-tool format <new ESP>`, `proxmox-boot-tool init <new ESP> [grub]` (`grub` only when `proxmox-boot-tool status` reports GRUB mode). On a default ZFS install the ESP is partition 2 and ZFS partition 3; read `lsblk` and `zpool status -P` rather than assume. The new disk must be at least the old one's exact byte size (`blockdev --getsize64`).
> - Seen on a home NAS install (TerraMaster F4-424 Pro, single WD SN740 NVMe): the installer's default was ext4; it was switched to ZFS (RAID0) for the later mirror. Screenshot pending: installer "Advanced bootdisk options", after first boot on a lab or redacted shot.

> **Learned 2026-11-24 (c)** · OpenZFS 2.3+ (PVE 9.2 ships ZFS 2.4) · VERIFIED_PRIMARY · Source: OpenZFS man pages zpool-attach.8, zpool-remove.8, zfs-rewrite.8 (master,
> read 2026-11-24); home NAS project `docs/references/07-community-baseline-and-pool-layout.md` · Falsifier: removing a top-level mirror from a pool that also holds a raidz vdev
> Growing a two-disk pool when the future disks' size is unknown: a **second mirror vdev** takes any size pair at full capacity and stays removable
> (`zpool remove` of a top-level mirror works only while the pool has no raidz or draid top-level vdev, all top-level vdevs share an ashift and encryption keys are loaded).
> **RAIDZ expansion** (`zpool attach pool raidzN-0 dev`, OpenZFS 2.3) counts a new disk only up to the smallest member, keeps old blocks at the old data-to-parity ratio
> until rewritten (`zfs rewrite`; whether a given PVE build ships it: check `man zfs-rewrite`), never changes the parity level, and makes the layout permanent.
> Capacity with 12 TB disks: mirror pairs 10.9 then 21.8 TiB; 4-wide RAIDZ1 about 32.7 TiB. No visual surface.

> **Learned 2026-11-25** · Proxmox VE 9.2.2, OpenZFS 2.4.2 · VERIFIED_PRIMARY (run on a node) · Source: home NAS project `scripts/host/pve_disk_clear.sh`,
> `scripts/host/pve_tank_create.sh` (commit 5f6bd80) · Falsifier: `zfs create -o keylocation=prompt` refusing a key on a non-terminal stdin
> Disks from an old NAS (TerraMaster TOS here) carry md-RAID members (`TNAS:UTOS*`, `<host>:UTOSUSER`) and a vfat boot partition; `wipefs -n` shows them
> and `zpool import` finds nothing. A safe clear is per disk, by serial, refused while a SMART test runs or the disk is in a pool, mounted or in an active
> md array, with a typed `CLEAR-<serial>`: `wipefs -a` each partition, `sgdisk --zap-all`, `wipefs -a` the disk, re-read the table, then prove
> `wipefs -n` is empty. For an encrypted dataset with `keyformat=passphrase,keylocation=prompt`, `zfs create` reads the passphrase from stdin when stdin is
> not a terminal (once, no confirmation), so it can be piped from a password manager; prove the stored copy by `zfs unmount` of the tree,
> `zfs unload-key`, then `zfs load-key` from the same source and `zfs mount -a`.
> ```bash
> { printf 'CREATE-tank\n'; kp show -s -a Password "$ZFS_ENTRY"; printf '\n'; } | ssh root@node 'bash pve_tank_create.sh <disk1> <disk2> --apply'
> for d in $(zfs list -H -o name -r tank/secure | sort -r); do zfs unmount "$d"; done; zfs unload-key tank/secure   # then load-key from the vault
> ```
