---
Title: Backup, disaster recovery and continuity
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Backup, disaster recovery and continuity decisions, failure modes and validation.
---

# Backup, disaster recovery and continuity

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [DR strategy ladder](#dr-strategy-ladder)
- [Copy placement and isolation](#copy-placement-and-isolation)
- [Recovery budget arithmetic](#recovery-budget-arithmetic)
- [Implementation notes: PostgreSQL and PBS](#implementation-notes-postgresql-and-pbs)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Service objectives (RPO, RTO, MTD) per service and per scenario.
- Choosing a DR strategy, copy placement and isolation from production admin.
- Restore-time arithmetic, database point-in-time recovery, deduplicating backup stores, drills and failback.

## Decision rules

Objectives (NIST SP 800-34 Rev. 1 definitions, VERIFIED_PRIMARY, [nist-rpo] and [nist-rto], checked 2026-10-29):

- RPO: "the point in time to which data must be recovered after an outage".
- RTO: "the overall length of time an information system's components can be in the recovery phase before negatively impacting the organization's mission".
- MTD (maximum tolerable downtime) is the business ceiling. RTO must fit inside it.
- Start the RTO clock at the agreed disruption point; stop it at verified recovery. Record detection and declaration as their own segments.
- Set RPO and RTO per service and per scenario: host loss, site loss, ransomware, operator deletion.
- Ransomware RPO is the age of the last clean copy, not the last copy.

Vocabulary that must not blur:

| Term              | Protects against                     | Does not protect against         |
| ----------------- | ------------------------------------ | -------------------------------- |
| High availability | component loss                       | deletion, corruption, ransomware |
| Replication       | site or host loss (copy changes)     | bad changes: it copies them too  |
| Backup            | deletion, corruption (point-in-time) | slow restore if never measured   |
| Archive           | retention obligations                | fast recovery                    |
| Disaster recovery | loss of the whole service location   | anything not rehearsed           |

- A completed backup job proves neither recoverability nor application consistency.
- Plan legal retention with the appropriate authority. Do not invent retention periods.

## DR strategy ladder

Four strategies, cheapest and slowest first. Names and distinctions paraphrased from the AWS DR whitepaper ([aws-dr], VERIFIED_SECONDARY, checked 2026-10-29). RPO/RTO classes below are illustrative
orders of magnitude (UNVERIFIED as targets); measure your own in a drill.

| Strategy                 | Running at the recovery site    | RPO class        | RTO class     | Cost driver             | Fits when                             | Still not covered        |
| ------------------------ | ------------------------------- | ---------------- | ------------- | ----------------------- | ------------------------------------- | ------------------------ |
| Backup and restore       | backup copies only;             | hours (interval) | hours to days | storage, spare hardware | most internal services; MTD in days   | procurement and          |
|                          | hardware later                  |                  |               |                         |                                       | long transfers           |
| Pilot light              | data replicated live; core      | minutes          | tens          | replication, small core | data must be fresh; app tier can be   | cannot serve until       |
|                          | always on                       |                  | of minutes+   |                         | built on demand                       | scaled out               |
| Warm standby             | scaled-down, fully working copy | seconds-minutes  | minutes       | a running reduced stack | short RTO; tolerable reduced capacity | capacity until scaled up |
|                          |                                 |                  |               |                         | at first                              |                          |
| Multi-site active/active | full capacity serving at        | near zero        | near zero     | double capacity,        | MTD in minutes and budget for         | corruption and           |
|                          | both sites                      |                  |               | data consistency        | two sites                             | ransomware replicate     |

- Pilot light cannot serve requests without action first; warm standby can serve at reduced capacity. That is the dividing line.
- Every rung still needs point-in-time backups. Replication and active/active copy logical damage instantly.
- Choose the cheapest rung whose measured RTO and RPO fit inside MTD. Implementations (PBS, ZFS replication, cold spare hosts) sit under the rung.

## Copy placement and isolation

- 3-2-1 is a practice, not a standard: at least 3 copies, on 2 different media or systems, 1 off-site.
- "3-2-1-1-0" adds 1 offline or immutable copy and 0 restore-verification errors. Vendor-originated term; UNVERIFIED as a standard.
- CISA advises offline, encrypted backups of critical data with regular restore tests. It warns immutable cloud storage may not meet every compliance need. VERIFIED_PRIMARY, [cisa], checked
  2026-10-29.
- Pull the off-site copy from the backup side, so production credentials cannot reach it.
- Escrow encryption keys and the backup catalog apart from production and apart from each other.

> **Learned 2026-11-20** · repository passwords generated into a secrets store · UNVERIFIED (design review; dev only) · Source: Continuum DL-067, FR-248;
> continuum-app `apps/coordinator/src/vault.rs` `resolve_or_create` (dffcd68) · Falsifier: a restic repository readable without its password.
> When a service generates each encrypted repository's password on first use and keeps it only in the secrets store (OpenBao KV here), the secrets store's
> data becomes part of every backup's recovery path: a copy of the repositories is unreadable without a separate, restore-tested copy of that store, kept
> apart from both. Unseal-key custody (Shamir shares) does not cover it; that only reopens a store whose data still exists. An in-memory dev secrets store
> beside persistent object storage reproduces the loss on every restart (orphaned repositories): give test runs a fresh namespace.
>
> ```text
> restic data (SeaweedFS)  --needs-->  password (OpenBao KV)  --needs-->  OpenBao data backup + unseal shares
> ```

> **Learned 2026-11-18** · backup repository on the primary's host · UNVERIFIED (design review, nothing deployed) · Source: Continuum first-slice review, flow map
> `docs/architecture/diagrams/first-slice/parts/components-data-and-offhost.yaml` (tools_stuff 2026-11-18) · Falsifier: a design where the snapshot store shares the host yet survives its loss.
> A snapshot store (restic on S3, here SeaweedFS) placed on the same single host as the coordinator and its database is copy 1 only: losing that host loses live state and every checkpoint at
> once. Draw it in the same failure domain and list the missing off-host copy, pulled from the backup side, as an open decision; a design that calls it "backups" without that copy overstates
> recovery. A single-node secrets store on the same host (OpenBao) adds a second question: who holds the unseal keys after a reboot.
>
> ```yaml
> - id: offsite-copy
>   name: Off-host backup copy (gap)
>   depends_on: [seaweedfs]
>   notes: 3-2-1 needs a copy off the VPS, pulled from the backup side. No decision yet.
>   status: {state: proposed, since: "2026-11-18"}
> ```

> **Learned 2026-11-19** · off-site copy of a content-addressed backup repository · VERIFIED_PRIMARY (restic 0.19.1 docs, References, Repository Format; SeaweedFS wiki
> S3-Configuration, edited 2026-10-31; both read 2026-11-19) · Source: Continuum TASK-30 design `docs/architecture-review/design/nas-pull-design-20261118_2206.md` (tools_stuff 6fec9a4) · Falsifier: a
> restic file whose name is not the SHA-256 of its bytes; a SeaweedFS S3 gateway that denies anonymous access with no config file.
> restic names every repository file except `config` by the SHA-256 of its content and never rewrites a file, so a pulled copy can be checked with `sha256sum` against the file names without
> the repository key: the off-site side can verify integrity while holding ciphertext only, keeping the key apart (escrow rule above). Pull with copy-never-delete so a compromised primary
> cannot prune the copy. For completeness, a key holder computes the packs a snapshot needs from the index and checks the off-site list covers them; "the snapshot file is there" alone
> can pass a partial copy. A self-hosted S3 gateway may be open by default: SeaweedFS `weed s3` without `-s3.config` is "Default Effect: Allow"; give the puller a read-only identity
> (`Read:<bucket>`) and bind the gateway to the private tunnel.
>
> ```text
> pull:   rclone copy vps-s3:restic /nas/restic      # never sync: no deletes propagate
> verify: for f in data/*/* index/* snapshots/*; do [ "$(sha256sum < "$f" | cut -c1-64)" = "$(basename "$f")" ] || echo "BAD $f"; done
> ```

```text
Backup isolation: production admin must not be able to delete copy 2 or copy 3

  ==== production admin domain ====================
  +------------+      +------------------------+
  | production |----->| (1) local backup store |   fast restore, same site
  +------------+      +-----------+------------+
  ==== off-site admin domain ====================== separate credentials
                                  |
                                  | pulled by (2)
                      +-----------v------------+
                      | (2) off-site store     |
                      +-----------+------------+
                                  |
                      +-----------v------------+
                      | (3) offline/immutable  |   tape, removable, or object lock
                      +------------------------+   prod admin cannot shorten retention
  escrowed outside production: identity break-glass, keys, backup catalog, runbook

  Legend: ---> and v data flow   ==== admin boundary
```

> **Learned 2026-11-22** · backup tool as an in-process library or a process per call · VERIFIED_PRIMARY (spike: rustic_core 0.14 and restic 0.19.1 read each other's
> snapshots) · Source: continuum `spikes/p5-rustic/results.md` (dfa0d76) · Falsifier: a library that writes a format the stock tool cannot restore. Choosing a library for speed
> (0.2 ms per small read against about 0.7 s per `restic --no-cache` process) is safe for recovery only while the repository stays in the stock tool's format: then a stock binary
> still restores and leaving the library is free. The library shares the service's crash and memory domain, so each call needs the timeout the process path had, and
> destructive maintenance (forget, prune) stays on the proven tool until the library's version is tested for it.

> **Learned 2026-11-22** · incremental and chunked artefacts couple transfer to retention · VERIFIED_SECONDARY (design review from measured spikes) · Source: continuum
> `spikes/p5-git-bundle/README.md`, `spikes/p5-fastcdc/README.md` (3e45de9, c8f4971) · Falsifier: a restore path that never needs the basis. A bundle made against a basis, or a
> chunk shared by several snapshots, is restorable only while its basis or every snapshot that names it is kept: retention must count references per object (keep while any live
> envelope names it), and a restore onto a fresh machine needs the basis from the store, not from the previous target. Savings measured: under 1 % of a full bundle for a
> 554 MB repository; 0.1 to 0.5 % of a 719 MB tree with 16 KiB chunks.

## Recovery budget arithmetic

- `RTO_actual = detect + decide + provision + transfer + replay/startup + validate + client cutover`.
- `transfer_s = bytes * 8 / (link_bps * efficiency)`. Measure efficiency: protocol, disk, dedup rehydration, contention.

| Data    | Path           | Efficiency             | Transfer            |
| ------- | -------------- | ---------------------- | ------------------- |
| 1 TiB   | 1 Gbit/s       | 1.0 (theoretical)      | 8,796 s = 146.6 min |
| 2 TiB   | 10 Gbit/s      | 0.6 (assumed; measure) | 2,932 s = 48.9 min  |
| 500 GiB | 100 Mbit/s WAN | 0.8                    | 53,687 s = 14.9 h   |

- Deduplicated and incremental backups shrink stored bytes, not restore bytes. A full VM restore rehydrates the whole disk.
- Live-restore starts the guest before transfer completes. It cuts RTO but runs at backup-store latency.
- Replication lag sets a loss window only when consistency and failure behaviour are understood.

```text
RTO budget: the clock starts at the agreed disruption point (example timeline)

  |<-------------------------- RTO target (agreed) -------------------------->|
  |--detect--|--decide--|--provision--|----transfer----|--start--|--verify--|
  0          15m        30m           45m              95m       105m       120m

  RPO window:  last clean recovery point <---- data lost ----> incident
  Every segment is measured in a drill; none is assumed.
```

> **Learned 2026-11-20** · restic 0.19.1 on SeaweedFS 4.54 (S3) · VERIFIED_PRIMARY (run against the live store) · Source: continuum-app
> `crates/continuum-store/src/restic/mod.rs` (dffcd68), `.github/workflows/ci.yml` (7aedc0d) · Falsifier: a restic release with other exit codes.
> restic exits 10 when the repository does not exist and 12 on a wrong password, so "create on first use" can tell the cases apart without parsing text;
> a comma in `--tag a,b` makes two tags and filters on both. Run it with a cleared environment and `--no-cache` (no cache under the home folder) and pin
> `--host` (snapshots otherwise record the machine name). A single-host CI that also runs another service on 8080 must give `weed server` its own
> `-volume.port`: the default volume port is 8080 and the S3 gateway then never answers.
>
> ```sh
> restic -r s3:http://127.0.0.1:8333/bucket/p-<hash> --no-cache cat config   # exit 10: no repository yet -> restic init
> weed server -dir=data -ip=127.0.0.1 -volume.port=8380 -s3 -s3.port=8333 -s3.config=s3.json
> ```

## Implementation notes: PostgreSQL and PBS

PostgreSQL PITR (current docs 18.x, VERIFIED_PRIMARY, [pg-archiving] and [pg-basebackup], checked 2026-10-29):

- PITR = a base backup plus a continuous, unbroken WAL archive from the start of that backup.
- Enable `wal_level=replica` (or higher), `archive_mode=on` and `archive_command` or `archive_library`. Test archiving before the first base backup.
- WAL segments are normally 16 MB. `archive_timeout` forces a switch so idle periods do not stretch RPO; about a minute is usually reasonable.
- `pg_dump` output is logical and cannot be used for WAL replay. `pg_basebackup --incremental` needs server 17+.
- WAL archiving does not restore `postgresql.conf` or `pg_hba.conf`. Back them up separately.
- RPO ~ `archive_timeout` + archive delivery lag. RTO ~ base restore + WAL replay time (measure the replay rate).
- Containerised databases (Nautobot, OpenWISP): back up through the database, not by copying a live volume.

Proxmox Backup Server (VERIFIED_PRIMARY, [pbs-overview] and [pbs-maint], checked 2026-10-29):

- Data is split into SHA-256-addressed chunks: fixed-size for VM images (typically 4 MiB), dynamic for file backups.
- Each snapshot references all its chunks, so each is logically a full backup.
- Pruning removes index references only; garbage collection frees chunks.
- Verify jobs re-read chunks and check digests. PBS recommends re-verifying all backups at least monthly. Off-site copies use sync jobs to a remote, or tape.
- One corrupted shared chunk damages every snapshot that references it. Hence verification and a second independent store.

> **Learned 2026-11-10** · PostgreSQL restore proof before and after an application upgrade · VERIFIED_PRIMARY (run on two stacks) · Source:
> unified-network-controller `scripts/upgrade/restore_proof.sh` (f3b6570e and its slurp commit), `docs/trackers/upgrade-log.md` · Falsifier: a dump whose
> restore has every table's exact row count yet misses data a later check finds.
> A dump-header check (`PGDMP`) proves a file exists, not that it restores. A cheap proof: restore the dump into a scratch database in the same server,
> count every public table exactly in live and restored (`query_to_xml(format('select count(*) ... %I', table_name))` per table, one query), drop the
> scratch database. On a live system the comparison has three outcomes: equal; live higher (rows written after the dump: job logs, change log, leases;
> list, do not fail); restored higher or a table missing (fail). After the upgrade, compare live counts with the saved ones: a missing table or a table
> that lost rows fails, except tables that expire rows (sessions). On a 299-table, ~190 MB Nautobot database this took about 2 min on a laptop and
> about 5 min on a small cloud host, cheap enough for every upgrade.
>
> ```bash
> # unified-network-controller scripts/upgrade/restore_proof.sh: the per-table verdict (excerpt)
> if (mode == "restored") { if (got[t] < ref[t]) print "GREW " t; else { print "MORE? " t; bad = 1 } }
> else if (got[t] > ref[t]) print "GREW " t; else if (t in ok) print "SHRANK (allowed) " t; else { print "SHRANK " t; bad = 1 }
> ```

## Patterns and anti-patterns

| Pattern                                | Use when                         | Anti-pattern                             | Why it fails                                              |
| -------------------------------------- | -------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| Pull-based off-site copy               | any off-site store               | production pushes with write credentials | ransomware with prod admin deletes the off-site copy too  |
| Timed full restore drill               | quarterly, and after big changes | trusting "job succeeded"                 | catalog gaps, corrupt chunks and slow paths stay hidden   |
| Restore in dependency order            | site and service recovery        | restoring apps first                     | apps fail without identity, DNS and databases             |
| Database-native backup or PITR         | every database                   | copying a live volume                    | torn files; restore will not start or loses data silently |
| Keys and catalog escrowed off-prod     | encrypted backups                | key only in the production vault         | intact backup that nobody can decrypt                     |
| Failback planned as a second migration | any failover                     | "we will just switch back"               | split-brain or lost writes made during the DR period      |

> **Learned 2026-11-24** · cloud file shares versus backups; secrets-store snapshots · VERIFIED_PRIMARY (OpenBao 2.7.2 restore drill 7/7) · Source: continuum-app
> `scripts/dev-stack/bao_snapshot_drill.py` (ac644e0); continuum DL-220 · Falsifier: an OpenBao release whose restored snapshot opens with the new node's keys.
> A live shared file system (AWS EFS, an NFS mount) is not a backup: a delete, corruption or ransomware write reaches it at once. The point-in-time layer is snapshots
> (EBS by Data Lifecycle Manager, ZFS) plus a delete-proof object copy (S3 Object Lock in compliance mode, written by an instance role that may put but not delete).
> A Vault/OpenBao raft snapshot restored onto a new node seals itself after `snapshot-force` and opens only with the original unseal shares, so a snapshot without the
> escrowed shares restores nothing: the drill must use the escrow copy, and the escrow belongs apart from the snapshot. A bucket in the hosts' own Region shares that
> Region's failure domain; one copy outside the provider (a pull to a workstation) covers account loss.

```python
# bao_snapshot_drill.py step 6: the restored node answers only to the ORIGINAL shares
for _ in range(60):
  if json.loads(call(url, "GET", "/v1/sys/seal-status"))["sealed"]:
    unseal(url, shares[1:3])  # two original shares from escrow
    break
```

> **Learned 2026-11-25** · OpenBao raft snapshot jobs (adds to the 2026-11-24 entry above) · VERIFIED_PRIMARY (OpenBao 2.7.2, a throwaway server 2026-11-25 and the restore
> drill taking its snapshot with a token holding only this policy) · Source: continuum-app `deploy/nas/openbao/continuum-raft-snapshot.hcl`,
> `scripts/dev-stack/bao_snapshot_drill.py` (83c156b), continuum FR-248 · Falsifier: an OpenBao release refusing `GET sys/storage/raft/snapshot` without `sudo`.
> The original-shares rule held again on 2.7.2. `GET sys/storage/raft/snapshot` needs only `read` on that path, not `sudo`, so a scheduled snapshot job gets a
> token with one read rule and no secret access (the drill checks it cannot read a stored password). `auth/token/renew-self` comes with the `default` policy, so a
> periodic token (`-period=72h`, renewed by every run) lives while the timer runs and lapses after the job stops. Restore (`snapshot-force`) is never granted to a
> host token: it is an operator step with a root or recovery token.
>
> ```hcl
> # bao token create -orphan -policy=continuum-raft-snapshot -period=72h -field=token
> path "sys/storage/raft/snapshot" {
>   capabilities = ["read"]
> }
> ```

## Failure modes and tests

| Failure                                  | Symptom                              | Blast radius                     | Proving test                                                        |
| ---------------------------------------- | ------------------------------------ | -------------------------------- | ------------------------------------------------------------------- |
| Silent chunk corruption, missing catalog | restore fails or is partial          | every snapshot sharing the chunk | scheduled verify plus quarterly full restore to an isolated network |
| Off-site copy deletable from prod        | ransomware wipes all copies          | all data                         | attempt a delete from a prod admin account in a test; it must fail  |
| WAL archive gap                          | PITR stops short of the target time  | the database                     | restore to a timestamp; check WAL continuity and row counts         |
| Restore path slower than modelled        | RTO missed by hours                  | the service and its dependents   | timed full restore of the largest service over the real path        |
| Key only in production vault             | backups unreadable after a site loss | all encrypted backups            | recover a backup with the escrowed key on a clean host              |
| Old primary not fenced after failover    | two writable copies diverge          | the service's data               | failover drill confirms the old primary is fenced before cutover    |

## Worked example

Service with 1 TiB of data. RTO target 15 minutes (900 s). Off-site restore link 1 Gbit/s, efficiency assumed 1.0.

1. Transfer alone = 1,024 x 2^30 x 8 / 10^9 = 8,796 s (146.6 min). Already ten times the RTO.

```text
$ just capacity examples/capacity-plan.json        (restore block: 1024 GiB, 1000 Mbit/s, rto 900 s)
  restore: estimated_seconds 8796.1  rto_seconds 900  exceeds_rto true
  findings: [..., "serialized restore estimate exceeds RTO"]   (exit 1)

$ just capacity examples/capacity-plan-pass.json   (same data, 10000 Mbit/s, rto 1800 s)
  restore: estimated_seconds 879.6  rto_seconds 1800  exceeds_rto false   status pass (exit 0)
```

2. The 10 Gbit/s case leaves 1,800 - 880 = 920 s for detect, decide, provision, start and verify. The example timeline above spends 75 min on those.
3. Decision: the transfer fits, the whole budget does not. Move one rung up the ladder (pilot light: data already replicated), or agree a longer RTO.
4. Prove it with a timed drill using the [backup-and-restore-test](../templates/backup-and-restore-test.md) template.

## Review checklist

- [ ] RPO, RTO and MTD set per service and per scenario, including ransomware and operator deletion.
- [ ] DR rung chosen from the ladder; its uncovered failure is stated and accepted.
- [ ] 3-2-1 met; one copy offline or immutable where ransomware is in scope.
- [ ] Off-site copy pulled; production admin cannot delete or shorten its retention (tested).
- [ ] Keys, catalog and break-glass identity escrowed outside production.
- [ ] Restore estimate run (`just capacity`), then a timed drill recorded per phase.
- [ ] Databases use PITR or native backup; WAL continuity checked in the drill.
- [ ] Recovery order (identity, DNS, storage, databases, apps) and failback plan written.

Systems architect owns data and service restoration. The network architect owns recovery paths, effective throughput, DNS and traffic convergence. Use skill-smc for remote-site constraints,
skill-coder for backup automation and skill-openwisp for recovery telemetry.

## Further reading

Links checked 2026-10-29.

Primary sources cited above

- [nist-rpo] and [nist-rto]: NIST glossary, sourced to SP 800-34 Rev. 1. [cisa]: CISA #StopRansomware guide.
- [pg-archiving] and [pg-basebackup]: PostgreSQL 18.x docs. [pbs-overview] and [pbs-maint]: Proxmox Backup Server docs.
- [aws-dr]: AWS whitepaper, DR options in the cloud (strategy ladder; paraphrased, link only).

Continuity planning

- [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final): read this for business impact analysis, MTD/RTO/RPO and contingency plan structure.
- [CISA #StopRansomware guide](https://www.cisa.gov/stopransomware/ransomware-guide): read this for backup isolation and recovery order after ransomware.
- [NIST SP 800-209](https://csrc.nist.gov/pubs/sp/800/209/final): read this for protecting backup and storage infrastructure itself.

Proxmox backup

- [Proxmox VE backup and restore](https://pve.proxmox.com/pve-docs/chapter-vzdump.html): read this for backup modes (snapshot, suspend, stop), consistency and live-restore.
- [PBS technical overview](https://pbs.proxmox.com/docs/technical-overview.html): read this for chunking, deduplication and why each snapshot is a full backup.
- [PBS maintenance](https://pbs.proxmox.com/docs/maintenance.html): read this for prune, garbage collection and verify jobs.
- [PBS remotes and sync](https://pbs.proxmox.com/docs/managing-remotes.html): read this for pull-based off-site copies.
- [PBS tape backup](https://pbs.proxmox.com/docs/tape-backup.html): read this for offline media rotation.

PostgreSQL

- [Backup and restore overview](https://www.postgresql.org/docs/current/backup.html): read this for SQL dump vs file-level vs continuous archiving.
- [Continuous archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html): read this for WAL archiving setup and recovery targets.
- [pg_basebackup](https://www.postgresql.org/docs/current/app-pgbasebackup.html): read this for base and incremental backups.
- [High availability and replication](https://www.postgresql.org/docs/current/high-availability.html): read this for standby options and their failover semantics.

[nist-rpo]: https://csrc.nist.gov/glossary/term/recovery_point_objective
[nist-rto]: https://csrc.nist.gov/glossary/term/recovery_time_objective
[cisa]: https://www.cisa.gov/stopransomware/ransomware-guide
[pg-archiving]: https://www.postgresql.org/docs/current/continuous-archiving.html
[pg-basebackup]: https://www.postgresql.org/docs/current/app-pgbasebackup.html
[pbs-overview]: https://pbs.proxmox.com/docs/technical-overview.html
[pbs-maint]: https://pbs.proxmox.com/docs/maintenance.html
[aws-dr]: https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
