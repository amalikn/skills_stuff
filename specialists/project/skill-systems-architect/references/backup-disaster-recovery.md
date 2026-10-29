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

## Patterns and anti-patterns

| Pattern                                | Use when                         | Anti-pattern                             | Why it fails                                              |
| -------------------------------------- | -------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| Pull-based off-site copy               | any off-site store               | production pushes with write credentials | ransomware with prod admin deletes the off-site copy too  |
| Timed full restore drill               | quarterly, and after big changes | trusting "job succeeded"                 | catalog gaps, corrupt chunks and slow paths stay hidden   |
| Restore in dependency order            | site and service recovery        | restoring apps first                     | apps fail without identity, DNS and databases             |
| Database-native backup or PITR         | every database                   | copying a live volume                    | torn files; restore will not start or loses data silently |
| Keys and catalog escrowed off-prod     | encrypted backups                | key only in the production vault         | intact backup that nobody can decrypt                     |
| Failback planned as a second migration | any failover                     | "we will just switch back"               | split-brain or lost writes made during the DR period      |

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

[nist-rpo]: https://csrc.nist.gov/glossary/term/recovery_point_objective [nist-rto]: https://csrc.nist.gov/glossary/term/recovery_time_objective [cisa]:
https://www.cisa.gov/stopransomware/ransomware-guide [pg-archiving]: https://www.postgresql.org/docs/current/continuous-archiving.html [pg-basebackup]:
https://www.postgresql.org/docs/current/app-pgbasebackup.html [pbs-overview]: https://pbs.proxmox.com/docs/technical-overview.html [pbs-maint]: https://pbs.proxmox.com/docs/maintenance.html [aws-dr]:
https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
