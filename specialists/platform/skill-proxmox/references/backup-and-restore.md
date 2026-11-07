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
