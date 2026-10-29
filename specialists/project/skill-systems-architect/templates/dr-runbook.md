---
Title: DR failover runbook template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: >-
  Site or service failover runbook: invocation criteria, roles, prerequisites, ordered steps with expected output and rollback, data authority and
  point of no return, communications, failback and a drill record with measured times against RTO and RPO.
---

# <service or site> DR failover runbook

Based on: NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems (https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final), for the Activation and Notification, Recovery and
Reconstitution phases, order of succession and test, training and exercise (VERIFIED_PRIMARY, publication page and PDF, May 2010, updated 2010-11-11, checked 2026-10-29).

## Contents

- [How to use](#how-to-use)
- [1. Scope and targets](#1-scope-and-targets)
- [2. Invocation criteria](#2-invocation-criteria)
- [3. Roles and contacts](#3-roles-and-contacts)
- [4. Prerequisites (check before any step)](#4-prerequisites-check-before-any-step)
- [5. Data authority and point of no return](#5-data-authority-and-point-of-no-return)
- [6. Failover steps](#6-failover-steps)
- [7. Communications](#7-communications)
- [8. Failback (reconstitution)](#8-failback-reconstitution)
- [9. Drill record](#9-drill-record)
- [10. Findings and actions](#10-findings-and-actions)
- [11. Review state](#11-review-state)

---

## How to use

- One runbook per failover unit (a service, or a site with its services). It is executed under stress: short imperative steps, one action each.
- Every step has an expected output an operator can compare, a check, and a rollback until the point of no return.
- Fill the targets from the [backup and restore test][backup-and-restore-test-url] and the [DR strategy ladder][backup-disaster-recovery-url]; databases from [databases-and-ha][databases-and-ha-url].
- A runbook nobody has drilled is a draft. Record every drill in section 9 and fix the runbook before closing the drill.
- Label every load-bearing fact (addresses, capacities, timings) VERIFIED_PRIMARY, USER_STATED or UNVERIFIED, with the date checked.

## 1. Scope and targets

| Field                                  | Value                                                           |
| -------------------------------------- | --------------------------------------------------------------- |
| Service(s) / site covered              | <name, owner role>                                              |
| Primary location -> recovery location  | <site A> -> <site B> (separate power, network, identity?)       |
| DR rung                                | *backup and restore / pilot light / warm standby / active-active* |
| RTO / RPO / maximum tolerable downtime | <n> min / <n> min / <n> h (USER_STATED by the business owner)   |
| Dependencies that must already be in B | *identity, DNS, secrets, licences, certificates, monitoring*    |
| Runbook version / last drill           | <rN> / <YYYY-MM-DD, drill ID>                                   |

## 2. Invocation criteria

| Trigger                                                             | Who may declare      | Wait before invoking |
| ------------------------------------------------------------------- | -------------------- | -------------------- |
| Primary site loss confirmed (power, fire, access) by two sources    | <incident commander> | none                 |
| Service down longer than <n> min with no repair estimate inside RTO | <incident commander> | <n> min              |
| Data corruption or ransomware in primary (restore, not replicate)   | <IC + security lead> | after isolation      |
| Planned failover (maintenance, drill)                               | <change authority>   | change window        |

- Do not invoke on a single monitoring signal; confirm from a second path (another site, a person on site, the provider).
- If replication may carry the corruption, stop replication first (step 6.2) and go to a clean restore point instead.

## 3. Roles and contacts

| Role                      | Primary     | Deputy (order of succession)  | Reach by                  |
| ------------------------- | ----------- | ----------------------------- | ------------------------- |
| Incident commander (IC)   | <role/name> | <role/name>, then <role/name> | <phone, out-of-band chat> |
| Systems operator          |             |                               |                           |
| Database / data authority |             |                               |                           |
| Network operator          |             |                               |                           |
| Communications lead       |             |                               |                           |
| Business owner (sign-off) |             |                               |                           |

- Contacts and this runbook must be readable when the primary site, identity and email are down (printed or offline copy, USER_STATED location).

## 4. Prerequisites (check before any step)

| #   | Check                                                     | Expected                                  | Result |
| --- | --------------------------------------------------------- | ----------------------------------------- | ------ |
| 1   | Break-glass access to recovery site hosts and consoles    | login works without primary-site identity |        |
| 2   | Replication or backup state at recovery site              | lag <n> s, or newest restore point <time> |        |
| 3   | Recovery capacity (compute, storage, licences)            | headroom for the services in scope        |        |
| 4   | DNS / load balancer change access and TTLs                | TTL <= <n> s already in place             |        |
| 5   | Secrets, keys and certificates available at recovery site | present and in date                       |        |
| 6   | Clients and integrations know the recovery endpoints      | listed in section 1                   |        |

## 5. Data authority and point of no return

```text
Who is authoritative for writes, and the moment the old primary must not come back

  time ---->
  [A writes] ---- replication A -> B ----X (A lost or fenced)
                                         |
                                         v
                       step 6.3: fence A (power off, revoke routes, demote)
                                         |
                       step 6.4: promote B ==== POINT OF NO RETURN ====
                                         |
                                         v
                       [B writes] ... A must rejoin as a copy of B, never as primary

X A returns unfenced after B is promoted: two writers, diverged data (split-brain)
Legend: ----> time and replication   ==== irreversible step   X failure and its effect
```

- Authoritative copy before failover: <site A>. After step 6.4: <site B>, until failback completes.
- Data at risk at failover = replication lag at the moment of loss (async) or zero (synchronous, verified). Record it in section 9.
- The point of no return is the first write accepted at B. Before it, rollback is "stop and stay on A". After it, only failback (section 7).
- The IC and the data authority both approve crossing it; record the time and the last replicated position (LSN, binlog position, snapshot ID).

## 6. Failover steps

| Step | Action (one per row)                               | Expected output                                    | Check                                | Rollback (until 6.4)       | Owner | Done at |
| ---- | -------------------------------------------------- | -------------------------------------------------- | ------------------------------------ | -------------------------- | ----- | ------- |
| 6.1  | Declare the incident; open the bridge; start       | IC named; timeline started                         | log entry with time                  | n/a                        | IC    |         |
|      |   the log                                          |                                                    |                                      |                            |       |         |
| 6.2  | Freeze changes; stop replication if corruption     | replication paused or confirmed healthy            | status command output recorded       | resume replication         |       |         |
| 6.3  | Fence the primary                                  | primary cannot accept writes (off,                 | write attempt to A fails             | unfence A, stay on A       |       |         |
|      |                                                    |   isolated, demoted)                               |                                      |                            |       |         |
| 6.4  | Promote recovery copy (POINT OF NO RETURN)         | B accepts writes; position recorded                | test write and read-back at B        | none: failback only        |       |         |
| 6.5  | Start dependent services in order                  | each health check green                            | <health URL or command> per service  | stop services at B         |       |         |
| 6.6  | Switch traffic (DNS, load balancer, routes)        | clients resolve and reach B                        | probe from an external vantage point | revert record (TTL         |       |         |
|      |                                                    |                                                    |                                      |   wait applies)            |       |         |
| 6.7  | Validate user outcomes                             | business test cases pass                           | named test list signed by the owner  | n/a                        |       |         |
| 6.8  | Confirm backups and monitoring now protect B       | first backup at B succeeded; alerts point at B     | backup job and alert test            | n/a                        |       |         |

## 7. Communications

| When                  | Audience                     | Channel               | Message owner | Template                                   |
| --------------------- | ---------------------------- | --------------------- | ------------- | ------------------------------------------ |
| Invocation            | staff, stakeholders          | <out-of-band channel> | comms lead    | *what happened, impact, next update time*  |
| Every <n> min         | the same                     |                       |               | *progress, ETA, workarounds*               |
| Service restored at B | users, customers if external |                       |               | *restored, data-loss window if any, actions* |
| Failback window       | users                        |                       |               | *planned outage time and duration*         |

## 8. Failback (reconstitution)

- Preconditions: A repaired and tested; root cause understood; A resynchronised from B as a replica, not from its own old data.
- Plan it as a planned failover from B to A in a change window, with the same steps, checks and a new point of no return.
- Before failback, compare data at A against B (row counts, checksums, last position); anything written only at old A goes to the data authority for reconciliation, never auto-merged.
- Return backups, monitoring and DNS TTLs to their normal state; record the end of the incident.

## 9. Drill record

| Field                | Value                                                        |
| -------------------- | ------------------------------------------------------------ |
| Drill ID / date / IC | <DR-nnn> / <YYYY-MM-DD> / <role>                             |
| Scenario             | *site loss, primary DB loss, ransomware restore, planned move* |
| Type                 | *tabletop / functional test in isolation / full failover*    |
| Runbook version used | <rN>                                                         |

| Phase (NIST SP 800-34)                   | Start | End | Measured | Target  | Notes       |
| ---------------------------------------- | ----- | --- | -------- | ------- | ----------- |
| Activation and notification (6.1-6.3)    |       |     |          |         |             |
| Recovery: promote and start (6.4-6.5)    |       |     |          |         |             |
| Recovery: traffic and validate (6.6-6.7) |       |     |          |         |             |
| **Total vs RTO**                         |       |     | <n> min  | <n> min | pass / fail |
| Reconstitution: failback (section 8)     |       |     |          |         |             |

Data loss measured vs RPO: *<n> s of writes lost (last position at A vs first at B) vs <n> s allowed.* Steps that deviated from the runbook: *list.*

## 10. Findings and actions

| Finding | Effect on RTO/RPO | Action (runbook, design or training) | Owner | Due |
| ------- | ----------------- | ------------------------------------ | ----- | --- |
|         |                   |                                      |       |     |

## 11. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).

[backup-and-restore-test-url]: backup-and-restore-test.md

[backup-disaster-recovery-url]: ../references/backup-disaster-recovery.md#dr-strategy-ladder

[databases-and-ha-url]: ../references/databases-and-ha.md
