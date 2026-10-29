---
Title: Systems red flags
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture: review and incident triage
Last reviewed: 2026-10-29
Summary: Symptom-to-question index for systems reviews and incidents; each signal gives its usual meaning, the first question, the data to pull and the owning reference.
---

# Systems red flags

## Contents

- [Scope](#scope)
- [How to use](#how-to-use)
- [Cluster and virtualisation](#cluster-and-virtualisation)
- [Storage](#storage)
- [Backup and recovery](#backup-and-recovery)
- [Compute and facilities](#compute-and-facilities)
- [Operating system, identity and lifecycle](#operating-system-identity-and-lifecycle)
- [Capacity and platforms](#capacity-and-platforms)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- An index from an observed signal to the question that tests it. Use it in review and incident modes.
- Not a rulebook: the owning reference holds the rule, threshold, evidence label and source.
- Format adapted in our own words from the red-flag catalogue idea in the similar-skills survey (adoption A1).

## How to use

- Scan a design, inventory or incident timeline for each signal.
- A signal is a hypothesis, not a finding. Ask the first question, pull the data, then record the result with an evidence label.
- Report a confirmed flag with its blast radius and the proving test from the owning reference.
- Thresholds marked "practice" are operator conventions, not cited standards.

## Cluster and virtualisation

Owning module: [virtualization-and-proxmox](virtualization-and-proxmox.md).

| Signal                                   | Usually means                                     | First question                                 | Data to pull                                    |
| ---------------------------------------- | ------------------------------------------------- | ---------------------------------------------- | ----------------------------------------------- |
| QDevice on an odd node count             | QDevice holds N-1 votes; its loss leaves no spare | Why is the QDevice here, and what if it fails? | node count, `pvecm status` votes, `just quorum` |
| Two nodes, no QDevice or witness         | either node loss freezes management and HA        | What decides quorum when one node is down?     | expected votes, HA resources                    |
| Most votes in one rack or site           | losing that domain stops the whole cluster        | Which domain loss must the cluster survive?    | vote map per rack; `just quorum` per domain     |
| One corosync link, or both on one switch | one switch fault splits or flaps membership       | Which physical switches carry each link?       | corosync link config, cabling, latency          |
| HA enabled, fencing never tested         | split-brain or stuck recovery on a real isolation | When did an isolated node last self-fence?     | watchdog type, isolation test record            |
| `pvecm expected 1` in a routine runbook  | quorum override used as a fix, not a last resort  | Under what conditions is this step allowed?    | runbook, change history                         |

## Storage

Owning module: [storage-and-data](storage-and-data.md).

| Signal                              | Usually means                                            | First question                                    | Data to pull                                  |
| ----------------------------------- | -------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------- |
| Ceph pool min_size 1                | writes accepted on one copy; next failure loses data     | Who set it, and when was it meant to revert?      | pool size/min_size per pool; `just ceph`      |
| Ceph on exactly three nodes, size 3 | stays degraded after a node loss                         | What happens to PGs while a node is out?          | node count, CRUSH failure domain              |
| Ceph used above the plan limit      | recovery will hit backfillfull or full                   | Is usage measured against raw/size or the plan?   | usage per pool vs plan from `just ceph`       |
| ZFS pool above ~80% full (practice) | write slowdown and fragmentation; no room to rewrite     | What is the growth rate and the cleanup plan?     | pool capacity and fragmentation, growth trend |
| Hardware RAID under ZFS             | ZFS cannot see or repair disk errors                     | Is the controller in HBA (IT) mode?               | controller model and mode                     |
| No scrub in the agreed interval     | latent corruption undetected                             | When did the last scrub finish, with what errors? | scrub history, checksum error counters        |
| Consumer SSD for SLOG, WAL or DB    | high sync latency; acknowledged writes lost on power cut | Does the device have power-loss protection?       | model, fio sync 4k QD1, `pg_test_fsync`       |

## Backup and recovery

Owning module: [backup-disaster-recovery](backup-disaster-recovery.md).

| Signal                                      | Usually means                                 | First question                                      | Data to pull                               |
| ------------------------------------------- | --------------------------------------------- | --------------------------------------------------- | ------------------------------------------ |
| Backups never restored                      | recoverability and RTO are unknown            | When was the last timed full restore, and of what?  | drill records, measured phase times        |
| No restore estimate against RTO             | transfer time alone may exceed the RTO        | How many bytes over which link, at what efficiency? | dataset sizes, link rate;                  |
|                                             |                                               |                                                     | `just capacity` restore                    |
| Off-site copy pushed with prod credentials  | ransomware with prod admin deletes every copy | Can a prod admin delete the off-site copy?          | sync direction, credentials, a delete test |
| Encryption key only in the production vault | intact backups unreadable after a site loss   | Where is the escrowed key, and who can reach it?    | key custody record, recovery test          |
| Replication or snapshots called "backup"    | corruption and deletion copy across instantly | Which copy is independent and point-in-time?        | copy inventory per dataset (3-2-1 check)   |
| Database backed up by copying a live volume | torn, unrestorable database                   | Is the backup taken through the database?           | backup method, PITR config, WAL continuity |

## Compute and facilities

Owning module: [compute-and-facilities](compute-and-facilities.md).

| Signal                                             | Usually means                               | First question                                  | Data to pull                               |
| -------------------------------------------------- | ------------------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| Single PSU feed (both PSUs on one PDU or UPS)      | one breaker trip drops the "redundant" host | Which feed, UPS and PDU does each PSU use?      | power map per host, per-PSU draw           |
| OOB reached through production DNS or IdP          | no console in the outage that needs it      | Can OOB be reached with production isolated?    | OOB network path, auth dependency          |
| UPS load above ~80% (practice) or untested runtime | hard power-off before shutdown completes    | Does measured runtime cover the shutdown chain? | UPS load, discharge test, shutdown timings |

## Operating system, identity and lifecycle

Owning modules: [linux-unix](linux-unix.md), [security-and-service-identity](security-and-service-identity.md), [provisioning-and-lifecycle](provisioning-and-lifecycle.md).

| Signal                                        | Usually means                                   | First question                                     | Data to pull                                 |
| --------------------------------------------- | ----------------------------------------------- | -------------------------------------------------- | -------------------------------------------- |
| Clock skew between hosts                      | auth, TLS, cluster and log-correlation failures | Which time sources does each host use?             | time-sync status and offset per host         |
| Certificate expiring soon, or no expiry alert | an outage on the expiry date                    | Who renews it, and is renewal automated?           | certificate inventory with expiry dates      |
| Unpatched or end-of-life OS                   | no security fixes; exploits stay open           | What is the support end date and replacement plan? | OS versions per host vs vendor support dates |
| Shared admin accounts or no break-glass       | no attribution; lockout during an IdP outage    | How does an admin log in with the IdP down?        | account inventory, break-glass test record   |

## Capacity and platforms

Owning modules: [capacity-and-performance](capacity-and-performance.md), [containers-and-platforms](containers-and-platforms.md).

| Signal                                | Usually means                                        | First question                                    | Data to pull                               |
| ------------------------------------- | ---------------------------------------------------- | ------------------------------------------------- | ------------------------------------------ |
| Swap storms, high memory PSI          | memory overcommit beyond what the workload tolerates | What is committed vs usable after reserve?        | swap-in rate, memory PSI, committed RAM    |
| OOM kills in kernel or pod events     | limits too low, or host overcommitted                | Which process, and what were its limit and usage? | kernel log, pod events, requests vs limits |
| N+1 claimed from pooled RAM only      | largest guest has nowhere to go after host loss      | Does the largest guest fit one survivor?          | guest sizes, `just capacity` per scenario  |
| Images on `latest` or unpinned tags   | rollback and DR pull a different image               | Which digest is running in production now?        | running image digests vs manifests         |
| etcd even-sized or 2 of 3 in one zone | one zone loss stops the control plane                | Which zone loss must the control plane survive?   | etcd member placement; `just quorum`       |
| Dashboards green, newest sample old    | pipeline stalled; absence reads as healthy           | When did the newest sample for this target land?  | scrape age, `up`, ingest lag, push logs    |

## Review checklist

- [ ] Every table scanned against the design, inventory or incident timeline.
- [ ] Each hit recorded as a hypothesis with its first question and data source.
- [ ] Each confirmed flag carries an evidence label, blast radius and the owning reference's proving test.
- [ ] Practice thresholds (ZFS ~80%, UPS ~80%) stated as practice, not standards.

## Further reading

- Rules, thresholds and sources live in the owning references above; each ends with its own Further reading.
- [Brendan Gregg, USE method](https://www.brendangregg.com/usemethod.html): read this for a per-resource checklist that turns signals into questions.
- [Google SRE book: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/): read this for symptom-based alerting.
