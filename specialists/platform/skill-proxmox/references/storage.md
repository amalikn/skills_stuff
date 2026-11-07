# Storage

Storage is defined cluster-wide in `/etc/pve/storage.cfg` and addressed as `<storage-id>:<volume>`. Sources: [pvesm chapter](../documents/research-sources-20261107/pve-admin-chapter-pvesm.md),
[PBS storage](../documents/research-sources-20261107/pve-wiki-storage-pbs.md).

## Contents

- [Types](#types)
- [Content types](#content-types)
- [The import content type](#the-import-content-type)
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

- `import` is **not enabled by default**; add it before OpenTofu's `import_from` or `download_file` with `content_type = "import"` can use the storage. `VERIFIED_PRIMARY` ([bpg
  download_file](../documents/research-sources-20261107/bpg-provider-virtual_environment_download_file.md)).
- A disk is imported with `qm set <vmid> --scsi0 <target>:0,import-from=<source>` where the source is a path or a volume (`local:import/<file>.qcow2`). `VERIFIED_PRIMARY` ([qm
  chapter](../documents/research-sources-20261107/pve-admin-chapter-qm.html), cloud-init
  example).
- Who may put a file there matters: `POST /nodes/{node}/storage/{storage}/download-url` (the provider's `download_file`) needs
  `Datastore.AllocateTemplate` on the storage **and** either `Sys.Audit` + `Sys.Modify` on `/` or the newer `Sys.AccessNetwork` on
  `/nodes/{node}`. `VERIFIED_PRIMARY` for 9.1.5 from the installed API source
  ([excerpt](../documents/research-sources-20261107/pve-9.1.5-installed-storage-download-url-permissions.txt)); the bpg page names only
  `Sys.Audit` and `Sys.Modify` ([bpg download_file](../documents/research-sources-20261107/bpg-provider-virtual_environment_download_file.md)),
  and the pveum chapter's privilege list does not yet name `Sys.AccessNetwork`. Either way the right lets the token make the node
  fetch any URL (probing the host's network), so a pool-scoped automation token is better kept without it: a root-run step places
  the file and the token only imports it ([access-control.md](access-control.md#worked-example-an-opentofu-identity)).

## Choosing

- Lab single node: `local` (dir) for ISOs, templates, snippets, import and qcow2 disks that need snapshots; `local-lvm` for raw thin disks.
- Shared storage (Ceph RBD, NFS, iSCSI with LVM) is the precondition for live migration without moving disks and for HA ([ha-and-replication.md](ha-and-replication.md)).
- Backups go to a `pbs` storage when a Proxmox Backup Server exists (deduplicated, incremental) or to a `backup`-content storage ([backup-and-restore.md](backup-and-restore.md)).

> **Learned 2026-11-07 (b)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /storage`, `/nodes/localhost/storage`) and the smc-resiliency x86 lab setup script
> (uncommitted on 2026-11-07) · Falsifier: a 9.x node where `pvesm set local --content ...,import` leaves the other types in place when they are omitted
> The worked example adds `import` with the full list (`pvesm set local --content images,snippets,backup,rootdir,iso,vztmpl,import`), guarded by a check of `storage.cfg` so a rerun changes nothing.
> After it, the API lists `import` among `local`'s content and OpenTofu imports `local:import/<file>.qcow2` with no SSH block. The same lab showed `local-lvm` (thin) at 90.6 % used while the directory
> storage was at 43 %: thin-pool fill is the first storage risk on a single-disk lab.
