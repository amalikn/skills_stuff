---
Title: Backup and restore
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/backup-and-restore.md
Last reviewed: 2026-11-07
Summary: vzdump modes and targets, Proxmox Backup Server 4.x (S3 datastores, encrypted sync), prune-backups retention, restores, and what a backup is not.
---

# Backup and restore

vzdump backups to a storage or to Proxmox Backup Server (PBS), retention, and restores. Sources: [vzdump chapter](../documents/research-sources-20261107/pve-admin-chapter-vzdump.md), [PBS
storage](../documents/research-sources-20261107/pve-wiki-storage-pbs.md), [Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html).

## Contents

- [Modes](#modes)
- [Targets](#targets)
- [Retention](#retention)
- [Restore](#restore)
- [What a backup is not](#what-a-backup-is-not)

## Modes

| Mode       | VMs                                                                                           | Containers                                       |
| ---------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `snapshot` | Live backup, minimal downtime; recommended; the guest agent freezes file systems when enabled | Needs every volume on a snapshot-capable storage |
| `suspend`  | Kept for compatibility; snapshot mode is recommended instead                                  | Suspends briefly after a first rsync pass        |
| `stop`     | Clean shutdown, backup, restart: most consistent, longest downtime                            | Same                                             |

`VERIFIED_PRIMARY` (vzdump chapter, Backup Modes). **Fleecing** caches blocks a running VM rewrites during a snapshot-mode backup on a fast local storage, so a slow target does not slow the guest:
`vzdump <vmid> --fleecing enabled=1,storage=<local-thin>`. Use a thin-provisioned fleecing storage. `VERIFIED_PRIMARY` (VM Backup Fleecing).

## Targets

- Any storage with `backup` content (directory, NFS, CIFS) holds `vzdump-*.vma.zst` / `.tar.zst` files under `dump/`.
- **PBS** (`pbs` storage type): incremental, deduplicated; optional client-side AES-256-GCM encryption whose key must be kept apart from the backups ("Without their key, backups will be
  inaccessible"). `VERIFIED_PRIMARY` (PBS storage).
- Jobs are cluster-wide (Datacenter → Backup, stored in pmxcfs); a job runs on each node for that node's guests.
- `maxfiles` was removed in 9.0; use `prune-backups`. `VERIFIED_PRIMARY` (Roadmap, 9.0 breaking changes).
- **PBS 4.x** (on Debian 13): 4.0 (2025-08-06) added S3-compatible object stores as a datastore backend as a technology preview; 4.2 (2026-04-29) made S3 datastores officially supported,
  with request and traffic counters and notification thresholds, added server-side encryption for push sync jobs (decryption on pull), parallel group sync (`worker-threads`), and moving
  groups and namespaces inside a datastore. `VERIFIED_PRIMARY` ([PBS Roadmap](../documents/research-sources-20261109/pbs-wiki-roadmap.html), fetched 2026-11-09). An S3 datastore is a PBS
  feature; Proxmox VE still sees it as a `pbs` storage.

```text
  vzdump job (cluster-wide; each node backs up its own guests)
  mode snapshot | suspend | stop   [+ fleecing on a fast local thin storage]
     |
     +--> dir / NFS / CIFS storage (backup content)
     |      dump/vzdump-*.vma.zst | .tar.zst      full archive every run
     |
     +--> pbs storage --> PBS datastore: chunked, incremental, deduplicated,
                            |               optional client-side encryption (keep the key apart)
                            |   backend: local disk | S3 object store (supported from PBS 4.2)
                            +--> sync job push/pull to a second PBS (4.2: encrypt on push)
```

## Retention

`prune-backups` with `keep-last`, `keep-hourly`, `keep-daily`, `keep-weekly`, `keep-monthly`, `keep-yearly`, processed in that order. Protected backups are ignored by pruning and cannot be removed
through the UI, CLI or API. `VERIFIED_PRIMARY`
(vzdump chapter, Backup Retention).

## Restore

- `qmrestore <archive> <vmid>` and `pct restore <ctid> <archive>`, or the GUI; restoring over an existing guest replaces it. `VERIFIED_PRIMARY` (vzdump chapter, Restore). Live restore from PBS
  (start the VM while it restores) is `UNVERIFIED` here (not in the captured chapter).
- A restore is proven only by booting the restored guest and checking its service; a finished task is not proof.
- Restore privileges: `VM.Backup` on the guest plus `Datastore.AllocateSpace` on the target storage; since 9.0 creating a privileged container needs
  `Sys.Modify` in most cases, but restoring one in place over an already privileged container does not. `VERIFIED_PRIMARY`
  for `VM.Backup` (pveum privilege list) and the 9.0 rule (Roadmap).

## What a backup is not

- Snapshots are not backups: they live on the same storage.
- Storage replication (ZFS) is not a backup either: it copies the latest state, mistakes included ([ha-and-replication.md](ha-and-replication.md)).
- `/etc/pve` is in no guest backup: back up the node configuration (pmxcfs database, `/etc/network/interfaces`, `/etc/apt`) separately.
