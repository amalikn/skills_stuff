---
Title: Databases, high availability and recovery
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  PostgreSQL HA and recovery architecture: streaming replication and commit levels, Patroni with a DCS and fencing, RPO/RTO trade-offs, split-brain
  avoidance, backup and PITR tools, logical vs physical replication, connection routing and upgrade paths; MySQL/MariaDB Galera and SQLite at the edge.
---

# Databases, high availability and recovery

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Replication and commit levels](#replication-and-commit-levels)
- [Patroni, DCS and fencing](#patroni-dcs-and-fencing)
- [Backup, PITR and replication types](#backup-pitr-and-replication-types)
- [Connection routing and upgrades](#connection-routing-and-upgrades)
- [MySQL, MariaDB and SQLite](#mysql-mariadb-and-sqlite)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- PostgreSQL high availability and recovery architecture: replication, failover, fencing, backup and PITR, routing and major upgrades.
- Version-specific facts are checked against the PostgreSQL 17 and 18 documentation; PostgreSQL 19 was at RC 1 on 2026-10-15 and is not covered.
- Storage under the database (fsync, WAL media, `pg_test_fsync`) lives in [storage-and-data][storage-and-data-url]; backup copy placement and restore drills live in
  [backup-disaster-recovery][backup-disaster-recovery-url].
- Short notes on MySQL/MariaDB Galera vs asynchronous replication and on SQLite for edge boxes.
- Network latency between nodes and sites comes from skill-network-architect; product commands belong to the product documentation.

## Decision rules

| Decision                  | Rule and threshold                                                                                          | Evidence                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Supported major version   | 18 supported to 2030-11-14, 17 to 2029-11-08, 16 to 2028-11-09, 15 to 2027-11-11, 14 to 2026-11-12          | VERIFIED_PRIMARY [pg-versioning]                 |
| PostgreSQL 14             | Final release 2026-11-12, two weeks after 2026-10-29: plan the upgrade now                                  | VERIFIED_PRIMARY [pg-versioning]                 |
| RPO zero on primary loss  | Synchronous replication with `synchronous_commit` on or remote_apply and at least one named standby         | VERIFIED_PRIMARY [pg-wal-config]                 |
| Write availability (sync) | Three or more PostgreSQL data nodes, so one host failure leaves a synchronous standby                       | VERIFIED_PRIMARY [patroni-repl]                  |
| Automatic failover        | A DCS with its own quorum (etcd 3 or 5 members) plus a watchdog in `required` mode on every data node       | [patroni-watchdog]; member counts: Raft majority |
| Async failover data loss  | Bound it with `maximum_lag_on_failover`; transactions beyond it stay on the old timeline and are lost       | VERIFIED_PRIMARY [patroni-repl]                  |
| Replication is not backup | Keep WAL archive plus base backups with PITR, independent of the replicas                                   | Design rule; [pg-archiving]                      |
| Major upgrade             | `pg_upgrade` (minutes, needs downtime) by default; logical replication when the outage budget is seconds    | VERIFIED_PRIMARY [pg-upgrade] [pg-logical]       |
| Checksums                 | 18 `initdb` enables data checksums by default; `pg_upgrade` needs matching settings on old and new clusters | VERIFIED_PRIMARY [pg18-release]                  |

## Replication and commit levels

`synchronous_commit` decides what a commit waits for. Values: `remote_apply`, `on` (default), `remote_write`, `local`, `off` (VERIFIED_PRIMARY [pg-wal-config], checked 2026-10-29). With
`synchronous_standby_names` empty, only `on` and `off` differ.

| Level          | Commit returns after                                      | Lost if the primary dies              | Lost if primary and standby OS both crash |
| -------------- | --------------------------------------------------------- | ------------------------------------- | ----------------------------------------- |
| `off`          | nothing; WAL flushed later (up to 3 x `wal_writer_delay`) | recent commits, even with no failover | recent commits                            |
| `local`        | local WAL flush only                                      | everything not yet streamed (async)   | the same                                  |
| `remote_write` | standby wrote WAL to its OS, not flushed                  | nothing                               | possible: standby had not flushed         |
| `on`           | standby flushed WAL to durable storage                    | nothing                               | nothing                                   |
| `remote_apply` | standby replayed the commit; visible to reads there       | nothing                               | nothing; highest commit latency           |

- `off` never corrupts the database; it loses the most recent commits after a crash, unlike `fsync = off` (VERIFIED_PRIMARY [pg-wal-config]).
- The level can be set per transaction (`SET LOCAL synchronous_commit TO OFF`), so a bulk job can be asynchronous while payments stay synchronous [pg-wal-config].
- `synchronous_standby_names` syntax: `[FIRST] n (s1, s2, ...)` waits for the n highest-priority standbys; `ANY n (s1, s2, ...)` is quorum commit and waits for any n of them (VERIFIED_PRIMARY
  [pg-repl-config], checked 2026-10-29).
- Quorum (`ANY 1 (s1, s2)`) hides one slow standby; priority (`FIRST 1`) always waits on the first listed one that is streaming.
- Every synchronous commit pays at least one network round trip to the standby. Ask the network architect for p99 RTT, not ping averages.

```text
Commit path with one synchronous standby (synchronous_commit = on)

+--------+  1 COMMIT   +-----------+  3 WAL stream   +-------------+
| client | ----------> | primary   | --------------> | standby A   |
|        |             | 2 flush   |                 | 4 flush WAL |
|        | <---------- | WAL local | <-------------- | (sync)      |
+--------+  6 success  +-----------+  5 ack flushed  +-------------+
                             |
                             +--- async WAL stream ---> standby B (may lag; loses its tail on promotion)

X standby A unreachable: commits wait (strict) or the primary goes standalone (non-strict), see Patroni modes
Legend: --> request or data   <-- acknowledgement   X failure and its effect
```

## Patroni, DCS and fencing

- Patroni (MIT) runs beside each PostgreSQL node and holds a leader lock in a distributed configuration store: etcd, Consul, ZooKeeper or Kubernetes (VERIFIED_PRIMARY [patroni-readme], checked
  2026-10-29). The node holding the lock is primary; losing it means demote.
- `ttl` (default 30 s, minimum 20) is the leader lock lifetime, roughly the time before automatic failover starts. `retry_timeout` (default 10 s) bounds DCS and PostgreSQL retries; outages shorter
  than it do not demote the leader (VERIFIED_PRIMARY [patroni-dynamic], checked 2026-10-29).
- Watchdog: in `required` mode a node will not become leader unless the watchdog is enabled; if Patroni hangs, the kernel watchdog resets the host before another node can be promoted (VERIFIED_PRIMARY
  [patroni-watchdog]). `softdog` is the software fallback; `soft_noboot=1` is for tests only.
- Modes (VERIFIED_PRIMARY [patroni-repl], checked 2026-10-29):
  - asynchronous (default): availability first; failover may lose up to `maximum_lag_on_failover` bytes, which stay on a forked timeline.
  - `synchronous_mode: on`: promotes only a synchronous standby. With no standby available the primary keeps accepting unreplicated writes.
  - `synchronous_mode_strict`: blocks writes until a synchronous standby returns. Even strict mode can lose a transaction whose backend was cancelled while waiting for the standby acknowledgement.
  - `synchronous_mode: quorum` maintains `ANY n (...)` and the voter set in the DCS; it reduces worst-case commit latency.
- DCS licence: etcd is Apache-2.0; Consul 1.17.0 and later is under the Business Source License, which is source-available, not FOSS (VERIFIED_PRIMARY, repository LICENSE files, checked 2026-10-29).
  Prefer etcd for a FOSS-first design.
- DCS sizing: a Raft store keeps working while a majority is up: 3 members tolerate 1 loss, 5 tolerate 2. Place members in 3 failure domains.

```text
Three-node Patroni cluster: who may write, who decides, who fences

          +-------------------- etcd (3 members, 3 failure domains) ---------------------+
          |   holds the leader key; a node that cannot renew it within ttl demotes        |
          +---------------------------------------------------------------------------------+
               ^ renew lock               ^ watch                     ^ watch
+--------------+----------+  +------------+------------+  +------------+------------+
| node 1: Patroni +       |  | node 2: Patroni +       |  | node 3: Patroni +       |
| PostgreSQL PRIMARY      |  | PostgreSQL sync standby |  | PostgreSQL standby      |
| watchdog armed          |  | watchdog armed          |  | watchdog armed          |
+-------------------------+  +-------------------------+  +-------------------------+
               ^ GET /primary = 200       ^ GET /replica = 200        ^
               +---------- HAProxy health checks to the Patroni REST API --+
                                       ^
                               clients (via PgBouncer)

X node 1 isolated from etcd: lock expires, node 1 demotes (or the watchdog resets it), node 2 promoted
Legend: ^ lock, watch or health check   X failure and its effect
```

Failover choices and what they cost (RPO and RTO here are design targets, not measurements):

| Design                            | RPO on primary loss                       | RTO (automatic)               | Write availability risk                    |
| --------------------------------- | ----------------------------------------- | ----------------------------- | ------------------------------------------ |
| Async, Patroni                    | up to `maximum_lag_on_failover`           | about `ttl` plus promotion    | none from replication                      |
| Sync on, non-strict               | zero while a sync standby is up           | about `ttl` plus promotion    | silently falls back to unreplicated writes |
| Sync strict, 3 nodes              | zero (cancelled-wait corner case aside)   | about `ttl` plus promotion    | writes stop if no standby is streaming     |
| Quorum `ANY 1` of 2 standbys      | zero while one standby acknowledges       | about `ttl` plus promotion    | tolerates one slow or lost standby         |
| Manual DR standby in another site | the replication lag at the moment of loss | human decision plus promotion | decided by the runbook, not by software    |

Split-brain avoidance:

- Only the DCS lock holder may be primary. Never run two PostgreSQL primaries on one timeline behind one service address.
- Fencing comes from the watchdog plus demotion on lock loss; a VIP or HAProxy check is routing, not fencing.
- Two data nodes and two DCS members have no majority after a split. Use 3 DCS members, or a third witness site for the DCS only.
- After a failover the old primary must rejoin as a standby (`pg_rewind` or reclone); Patroni does this, but test it with real write load.

## Backup, PITR and replication types

| Tool                    | Licence (checked 2026-10-29) | Latest release seen | Use for                                                                      |
| ----------------------- | ---------------------------- | ------------------- | ---------------------------------------------------------------------------- |
| pgBackRest              | MIT                          | 2.60.0, 2026-10-18  | full/differential/incremental, parallel, repository encryption, S3/Azure/GCS |
| WAL-G                   | Apache-2.0                   | v3.0.9, 2026-08-20  | WAL and base backups streamed to object storage                              |
| Barman                  | GPL-3.0                      | 3.20.1, 2026-09-29  | a central backup server for many PostgreSQL instances                        |
| pg_basebackup + archive | PostgreSQL licence           | PostgreSQL 17+      | built in; `--incremental` with `pg_combinebackup` since 17 [pg17-release]    |

- Feature descriptions in the "Use for" column are VERIFIED_SECONDARY (project READMEs); licences and releases are VERIFIED_PRIMARY from the repositories.
- PITR needs a base backup plus every WAL segment since it. Monitor archive failures; one missing segment ends the recovery there.
- Back up from a standby to spare the primary, but alert when that standby lags, or the backup is stale.

| Need                                              | Physical (streaming) | Logical (publication/subscription)                       |
| ------------------------------------------------- | -------------------- | -------------------------------------------------------- |
| HA standby, whole cluster, byte-identical         | yes                  | no                                                       |
| Different major versions on each side             | no                   | yes: the basis of near-zero-downtime upgrades            |
| Subset of tables, different indexes on the target | no                   | yes                                                      |
| DDL and sequence values replicated                | yes                  | no: copy schema by hand; set sequences before switchover |
| Failover keeps logical slots                      | -                    | 17+: `sync_replication_slots` syncs failover slots       |

- Logical replication does not replicate schema (DDL) or sequence data; before failing over to a subscriber, raise its sequences (VERIFIED_PRIMARY [pg-logical], checked 2026-10-29).
- PostgreSQL 17 added `pg_createsubscriber`, which turns a physical standby into a logical replica, and failover slot synchronisation (VERIFIED_PRIMARY [pg17-release], checked 2026-10-29).

## Connection routing and upgrades

- HAProxy (GPL-2.0-based licence) checks the Patroni REST API: `GET /primary` returns 200 only on the leader; `GET /replica?lag=10MB` returns 200 only on a running replica under that lag
  (VERIFIED_PRIMARY [patroni-rest], checked 2026-10-29). Route writes and reads to separate ports.
- PgBouncer (ISC licence, 1.26.1 released 2026-10-14) pools connections in front of PostgreSQL. Size the pool from Little's law ([capacity-and-performance][capacity-and-performance-url]), not from
  `max_connections`.
- Session state (prepared statements, temporary tables, advisory locks) behaves differently in transaction pooling; check the application.
- On failover, clients reconnect; set short TCP keepalives or client retry so they do not hang on a dead primary.

| Upgrade path                     | Downtime                    | Notes                                                                                              |
| -------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------- |
| `pg_dump` / restore              | proportional to data size   | simplest; also changes layout; slow for large databases                                            |
| `pg_upgrade` (copy, link, clone) | minutes with `--link`/clone | from 9.2 and later; `--link` shares files, so the old cluster is unusable after start [pg-upgrade] |
| Logical replication              | seconds at switchover       | schema and sequences by hand; 17+ upgrades keep logical slots and subscriptions [pg17-release]     |

- PostgreSQL 18 `pg_upgrade` retains optimizer statistics, so the post-upgrade `ANALYZE` is less urgent (VERIFIED_PRIMARY [pg18-release]).
- Upgrade the standbys first for a minor release; mixed major versions cannot stream physically (VERIFIED_PRIMARY [pg-warm-standby]).
- In a Patroni cluster a major upgrade is a planned procedure for the whole cluster; rehearse it on a clone and keep the old data until accepted.

## MySQL, MariaDB and SQLite

- MariaDB/MySQL asynchronous replication: the same trade-off as PostgreSQL async; a failover loses the unshipped tail.
- Galera Cluster (GPL-2.0 with an OpenSSL exception): virtually synchronous multi-writer replication. A component keeps quorum only if its weight is strictly more than half of the previous primary
  component, so use 3 nodes or
  a 2 + arbitrator layout (VERIFIED_PRIMARY [galera-quorum], checked 2026-10-29).
- Galera write latency follows the slowest node's round trip, and conflicting writes on two nodes fail at certification (VERIFIED_SECONDARY,
  Galera documentation; test with your workload). Prefer one writer node.
- SQLite on an edge box: WAL mode lets readers and one writer work concurrently, but every process must be on the same host; WAL does not work over a network filesystem (VERIFIED_PRIMARY [sqlite-wal],
  checked 2026-10-29).
- SQLite backup: use the online backup API or a streaming tool such as Litestream (Apache-2.0); never copy a live database file and its WAL apart.

## Patterns and anti-patterns

| Pattern                                       | Use when                     | Anti-pattern                                | Why it fails                                        |
| --------------------------------------------- | ---------------------------- | ------------------------------------------- | --------------------------------------------------- |
| Patroni + etcd (3) + watchdog required        | automatic failover           | keepalived VIP between two nodes            | no quorum, no fencing: both nodes become primary    |
| 3 data nodes with sync or quorum commit       | RPO zero with availability   | sync replication with one standby, strict   | one standby outage stops all writes                 |
| HAProxy checks `/primary` and `/replica?lag=` | routing                      | TCP check on port 5432                      | a demoted or lagging node still accepts connections |
| WAL archive + base backups + restore drill    | every production database    | replicas as the only copy                   | a `DROP TABLE` replicates in milliseconds           |
| Per-transaction `synchronous_commit`          | mixed critical and bulk work | cluster-wide `off` for speed                | loses recent commits for all data after a crash     |
| Logical replication for a major upgrade       | seconds of downtime allowed  | `pg_upgrade --link` with no tested rollback | after start the old cluster cannot be used          |
| etcd for the DCS                              | FOSS-first designs           | assuming Consul is open source              | Consul 1.17+ is Business Source licensed            |

## Failure modes and tests

| Failure                             | Signal                                              | Proving test                                                                   |
| ----------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------ |
| Primary host lost                   | leader key expires; new leader in `patronictl list` | power off the primary under write load; measure RTO and compare committed rows |
| Primary isolated from DCS only      | old primary demotes or watchdog resets it           | block the primary's DCS traffic; confirm no second writer accepts writes       |
| Sync standby lost (strict)          | commits hang                                        | stop the standby; measure write stall; confirm the alert fires                 |
| Async lag above budget              | `pg_stat_replication` replay lag; Patroni lag       | load test; record lag p99 against the RPO                                      |
| WAL archive failing                 | `pg_stat_archiver` failed_count rising              | break the archive target in a lab; the alert fires before WAL fills the disk   |
| Logical slot left behind            | `pg_replication_slots` retained WAL growing         | stop a subscriber; alert on retained bytes                                     |
| Router sends writes to a replica    | read-only errors in the application                 | fail over; confirm HAProxy moves the write port within the check interval      |
| PITR to a point before a bad change | restored row counts and checksums                   | restore to a timestamp in an isolated host; record time against RTO            |

## Worked example

Order database: 120 GiB, WAL 4 MiB/s at peak, RPO zero, RTO 5 minutes, three hosts in three racks, inter-rack RTT p99 0.5 ms (USER_STATED).

1. Commit cost: synchronous `on` adds at least one RTT plus the standby flush. 0.5 ms RTT + 0.3 ms flush (from `pg_test_fsync`) = about 0.8 ms per commit. A single session doing serial commits caps at
   about 1 / 0.0008 = 1,250 commits/s; concurrency raises the total, not the per-session rate.
2. Mode: quorum `ANY 1 (node2, node3)` through Patroni `synchronous_mode: quorum`. One standby can be lost without a write stall.
3. RTO: `ttl` 30 s + promotion and routing (assume 15 s, measure it) = about 45 s, inside 5 minutes. A full restore is the fallback: 120 GiB at 400 MB/s effective = 120 x 1.074 / 0.4 = about 322 s of
   transfer alone, before WAL replay, so a restore misses the 5-minute RTO.
4. Async alternative: at 4 MiB/s and 2 s lag, a failover could lose about 8 MiB of WAL; that breaks RPO zero, so async is rejected.
5. Backup: pgBackRest to object storage, weekly full and daily differential, WAL archived continuously; PITR drilled quarterly with the [backup and restore test][backup-and-restore-test-url] template.
6. The latency figures are illustrative; measure RTT, `pg_test_fsync` and promotion time on the real hosts before accepting the design.

## Review checklist

- [ ] Every database has a stated RPO and RTO, and the chosen `synchronous_commit` and standby set match them.
- [ ] Major version is inside its support window ([pg-versioning]); PostgreSQL 14 has an upgrade date before 2026-11-12.
- [ ] Automatic failover uses a DCS with 3 or 5 members in separate failure domains and a watchdog in `required` mode.
- [ ] Writes route through a check of `/primary`, reads through `/replica` with a lag bound; connection pools sized by Little's law.
- [ ] WAL archiving and base backups exist independently of replicas; archive failures alert; a PITR drill was timed this cycle.
- [ ] Logical slots and subscriptions are monitored for retained WAL; sequences are handled before any logical switchover.
- [ ] Major upgrade path chosen (pg_upgrade or logical), rehearsed on a clone, with a rollback point.
- [ ] Galera clusters have 3 nodes or an arbitrator; SQLite edge stores use WAL on local disk with a tested backup.

## Further reading

PostgreSQL (docs version 18 unless marked):
- [pg-versioning] [Versioning policy](https://www.postgresql.org/support/versioning/) - read this for supported versions and final release dates (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-wal-config] [WAL settings](https://www.postgresql.org/docs/18/runtime-config-wal.html) - read this for `synchronous_commit` levels (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-repl-config] [Replication settings](https://www.postgresql.org/docs/18/runtime-config-replication.html) - read this for `synchronous_standby_names` (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-warm-standby] [Log-shipping standby servers](https://www.postgresql.org/docs/18/warm-standby.html) - read this for streaming and synchronous replication (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-logical] [Logical replication restrictions](https://www.postgresql.org/docs/18/logical-replication-restrictions.html) - read this before a logical upgrade (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-upgrade] [pg_upgrade](https://www.postgresql.org/docs/18/pgupgrade.html) - read this for copy, link and clone modes (VERIFIED_PRIMARY, checked 2026-10-29).
- [pg-archiving] [Continuous archiving and PITR](https://www.postgresql.org/docs/18/continuous-archiving.html) - read this for WAL archiving and recovery targets.
- [pg17-release] [Release 17][release-17-url] and [pg18-release] [Release 18][release-18-url] - read these for incremental backup, failover slots, checksums and `pg_upgrade` changes (VERIFIED_PRIMARY,
  checked 2026-10-29).

Patroni and routing:
- [patroni-readme] [Patroni](https://github.com/patroni/patroni) - read this for supported DCS back ends (VERIFIED_PRIMARY, checked 2026-10-29).
- [patroni-repl] [Replication modes][patroni-repl-url] - read this for async, synchronous, strict and quorum modes (VERIFIED_PRIMARY, checked 2026-10-29).
- [patroni-dynamic] [Dynamic configuration][patroni-dyn-url] - read this for `ttl`, `loop_wait` and `retry_timeout` (VERIFIED_PRIMARY, checked 2026-10-29).
- [patroni-watchdog] [Watchdog support][patroni-wd-url] - read this for fencing (VERIFIED_PRIMARY, checked 2026-10-29).
- [patroni-rest] [REST API][patroni-rest-url] - read this for HAProxy health-check endpoints (VERIFIED_PRIMARY, checked 2026-10-29).
- [PgBouncer](https://www.pgbouncer.org/) - read this for pooling modes and their limits.

Backup tools:
- [pgBackRest user guide](https://pgbackrest.org/user-guide.html) - read this for repository, retention and restore options.
- [WAL-G](https://github.com/wal-g/wal-g) and [Barman](https://github.com/EnterpriseDB/barman) - read these for the alternatives.

Other engines:
- [galera-quorum] [Galera quorum with weighted votes][galera-url] - read this for quorum arithmetic (VERIFIED_PRIMARY, checked 2026-10-29).
- [sqlite-wal] [SQLite write-ahead logging](https://www.sqlite.org/wal.html) - read this for WAL limits (VERIFIED_PRIMARY, checked 2026-10-29).
- [Litestream](https://github.com/benbjohnson/litestream) - read this for streaming SQLite backup to object storage.

[patroni-repl-url]: https://patroni.readthedocs.io/en/latest/replication_modes.html

[patroni-dyn-url]: https://patroni.readthedocs.io/en/latest/dynamic_configuration.html

[patroni-wd-url]: https://patroni.readthedocs.io/en/latest/watchdog.html

[patroni-rest-url]: https://patroni.readthedocs.io/en/latest/rest_api.html

[galera-url]: https://mariadb.com/docs/galera-cluster/galera-architecture/quorum-control-with-weighted-votes

[storage-and-data-url]: storage-and-data.md

[backup-disaster-recovery-url]: backup-disaster-recovery.md

[capacity-and-performance-url]: capacity-and-performance.md

[backup-and-restore-test-url]: ../templates/backup-and-restore-test.md

[release-17-url]: https://www.postgresql.org/docs/17/release-17.html

[release-18-url]: https://www.postgresql.org/docs/18/release-18.html
