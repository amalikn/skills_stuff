---
Title: hub-1 cluster quorum loss post-incident review (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/post-incident-review.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Blameless review PIR-005 of INC-0417: planned PDU feed A work took two of three Proxmox nodes down together, the cluster lost quorum and the
  management platform was down 47 min; `just quorum` shows the latent condition was detectable before the event. All site facts are fictional.
---

# PIR-005: hub-1 management platform outage during PDU feed A maintenance

Fills template: [templates/post-incident-review.md](../../templates/post-incident-review.md). Led to DES-014 (cluster rebuild, `host-and-cluster-build.md`) and drill RD-003.

## Contents

- [How to use](#how-to-use)
- [1. Summary](#1-summary)
- [2. Timeline](#2-timeline)
- [3. Contributing factors](#3-contributing-factors)
- [4. What went well, what went poorly, where we got lucky](#4-what-went-well-what-went-poorly-where-we-got-lucky)
- [5. Actions](#5-actions)
- [6. Follow-up and review state](#6-follow-up-and-review-state)

## How to use

How this example applied the template's rules:

- Triggers met: user-visible degradation (operators lost Nautobot, OpenWISP and Grafana), manual intervention (maintenance aborted) and a monitoring failure (no alert fired).
- Blameless: the maintenance followed the approved plan; the plan was written from the rack drawing, which showed dual-corded hosts.
- Times are UTC. Every ERN fact is fictional and therefore USER_STATED inside the example; the label column records how the fact was established in the story.

## 1. Summary

| Field                | Value                                                                                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Incident ID          | INC-0417 / sev-3 (internal tooling; no site service impact)                                                                                                                   |
|   / severity         |                                                                                                                                                                               |
| Status               | complete, actions in progress                                                                                                                                                 |
| Authors / reviewers  | systems architect / NOC lead, network architect, operations manager                                                                                                           |
| Summary              | Planned work on PDU feed A in rack-a powered off pve-1 and pve-2 together; pve-3 lost quorum and fenced itself, so Nautobot, OpenWISP and Grafana were down for 47 min.       |
| Impact               | 0 of 40 sites lost forwarding (WireGuard concentrators are separate hosts); operators had no inventory, no monitoring and no alerting for 47 min; 0 data lost (Ceph RPO 0,    |
|                      |   guests crash-consistent, Postgres recovered from WAL)                                                                                                                       |
| Trigger              | feed A switched off at 22:04 for a PDU firmware upgrade                                                                                                                       |
| Detection            | user report: the NOC lead found OpenWISP unreachable at 22:19; no alert fired because Grafana ran on the failed cluster                                                       |
| Resolution           | maintenance aborted; feed A restored at 22:31; nodes rebooted, quorum returned and HA guests started; service validated at 22:51                                              |

## 2. Timeline

All times 2026-09-16 UTC.

| Time (UTC) | Event                                                                                       | Source (log, alert, chat)       | Actor (role)     |
| ---------- | ------------------------------------------------------------------------------------------- | ------------------------------- | ---------------- |
| 22:00      | PDU feed A maintenance starts (approved change, rack-a only)                                | change ticket                   | field technician |
| 22:04      | feed A off; pve-1 and pve-2 lose power; first user-visible symptom (OpenWISP, Grafana down) | PDU log; pve-3 corosync log     | field technician |
| 22:05      | pve-3 not quorate (1 of 3 votes); HA watchdog fences pve-3 and it reboots                   | pve-3 journal                   | system           |
| 22:19      | NOC lead reports OpenWISP unreachable in the NOC chat; no page received                     | chat                            | NOC lead         |
| 22:24      | mitigation started: on-call asks the field technician to abort and restore feed A           | phone log, chat                 | on-call engineer |
| 22:31      | feed A restored                                                                             | PDU log                         | field technician |
| 22:38      | three nodes up, cluster quorate; Ceph peering complete at 22:41                             | corosync log; `ceph -s` capture | system           |
| 22:45      | HA guests started                                                                           | HA manager log                  | system           |
| 22:51      | service restored: Nautobot login and device list, OpenWISP map, Grafana dashboard checked   | on-call checklist               | on-call engineer |
| 23:30      | incident closed                                                                             | incident ticket                 | on-call engineer |

Durations: time to detect 15 min (22:04 to 22:19); time to mitigate 20 min (22:04 to 22:24); time to restore 47 min (22:04 to 22:51).

```text
CAUSAL CHAIN: read left to right; the latent condition existed before the trigger

+------------------+   +--------------------+   +---------------------+   +----------------------+
| feed A switched  |-->| pve-1 and pve-2    |-->| pve-3 holds 1 of 3  |-->| Nautobot, OpenWISP,  |
| off (planned)    |   | off together       |   | votes; self-fences  |   | Grafana down, no     |
+------------------+   +--------------------+   +---------------------+   | alert sent           |
                                ^                                         +----------------------+
                                |
                     +-------------------------------+
                     | latent: 2 of 3 nodes on one   |
                     | feed in rack-a since 2025-03; |
                     | alerting hosted on the same   |
                     | cluster                       |
                     +-------------------------------+
```

The latent condition was statically detectable. The as-was layout through the quorum helper:

```text
$ just quorum examples/filled/post-incident-review.json     # exit 1
  total_votes 3, quorum 2
  domain:rack-a  remaining_votes 1  quorate false
  domain:rack-b  remaining_votes 2  quorate true
  findings: "domain:rack-a: cluster loses quorum (2 of 3 votes needed)"
```

## 3. Contributing factors

| Factor                                        | Type (latent condition, trigger, detection gap, recovery gap, process, design) | Evidence                         | Label                            |
| --------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------- | -------------------------------- |
| pve-1 and pve-2 both in rack-a, whose two     | latent condition, design                                                       | rack-a PDU labels photographed   | USER_STATED (1)                  |
|   PDUs are both fed from feed A               |                                                                                |   2026-09-17; `just quorum` exit |                                  |
|                                               |                                                                                |   1 above                        |                                  |
| Rack drawing showed feeds A and B in rack-a;  | latent condition, process                                                      | drawing revision history         | USER_STATED (1)                  |
|   the second PDU was moved to feed A          |                                                                                |   vs photo                       |                                  |
|   in 2025-03                                  |                                                                                |                                  |                                  |
| Change review checked the drawing, not a      | process                                                                        | change ticket checklist          | USER_STATED (1)                  |
|   quorum model per power feed                 |                                                                                |                                  |                                  |
| Grafana alerting and its only notifier ran on | detection gap                                                                  | Grafana guest on pve-3 storage   | USER_STATED (1)                  |
|   the cluster it monitored                    |                                                                                |   pool; no external probe        |                                  |
| HA restart on pve-3 alone was impossible      | recovery gap                                                                   | runbook review                   | USER_STATED (1)                  |
|   without quorum; no documented manual path   |                                                                                |                                  |                                  |
| Why the second PDU was re-fed in 2025-03      | unknown                                                                        | no record found                  | UNVERIFIED (hypothesis: a feed B |
|                                               |                                                                                |                                  |   breaker fault)                 |

(1) In a real review these were observed on site and would be VERIFIED_PRIMARY; here the facts are fictional, so USER_STATED.

## 4. What went well, what went poorly, where we got lucky

- Went well: site traffic was untouched because the WireGuard concentrators run on separate hosts in both racks; the field technician restored feed A within 7 min of the request.
- Went well: Ceph recovered without data loss; Nautobot Postgres came back consistent from its WAL.
- Went poorly: detection relied on a person noticing (15 min); no alert path existed outside the failed cluster.
- Went poorly: the change plan treated "rack-a" as one item and did not ask which hosts depend on feed A.
- Got lucky: no site incident happened during the 47 min, so no operator needed Nautobot or OpenWISP for a fault; the window was at night.
- Got lucky: feed A was restorable on request; a failed PDU firmware update would have kept two nodes down for hours.

## 5. Actions

| ID   | Action                                                    | Type (prevent, mitigate, detect, process) | Factor addressed         | Owner           | Due        | Tracking       | Status     |
| ---- | --------------------------------------------------------- | ----------------------------------------- | ------------------------ | --------------- | ---------- | -------------- | ---------- |
| A-01 | Rebuild the cluster one node per power domain (pve-2 to   | prevent                                   | pve-1 and pve-2 on       | systems         | 2026-11-17 | DES-014        | in         |
|      |   rack-b feed B, pve-3 to comms-c feed C); `just quorum`  |                                           |   one feed               |   architect     |            |                |   progress |
|      |   exit 0 required for every domain                        |                                           |                          |                 |            |                |            |
| A-02 | Add an external probe and notifier outside hub-1 (hub-2)  | detect                                    | alerting on the          | NOC lead        | 2026-11-03 | CHG-033        | open       |
|      |   for Nautobot, OpenWISP and Grafana                      |                                           |   monitored cluster      |                 |            |                |            |
| A-03 | Add "run `just quorum` per power feed touched" to the     | process                                   | change review used       | operations      | 2026-10-31 | process doc    | done       |
|      |   change checklist for any hub-1 power work               |                                           |   the drawing            |   manager       |            |                |            |
| A-04 | Audit both hub racks: label each PDU with its feed and    | prevent                                   | drawing drift            | field           | 2026-11-10 | NB-power-audit | open       |
|      |   record it in Nautobot power feeds                       |                                           |                          |   technician    |            |                |            |
| A-05 | Write and drill the manual path for starting a guest on a | mitigate                                  | no recovery path         | systems         | 2026-12-15 | RB-hub-07      | open       |
|      |   non-quorate node                                        |                                           |                          |   architect     |            |                |            |

## 6. Follow-up and review state

- Design documents, ADRs, failure-mode rows or risks updated: DES-014 r2 and ADR-0009 (one node per domain, no QDevice), `host-and-cluster-build.md`; restore drill RD-003
  (`backup-and-restore-test.md`).
- Review meeting 2026-09-23, attendees: systems architect, network architect, NOC lead, field technician, operations manager.

| Revision | State    | Date       | Reviewer (role)                          | Notes                             |
| -------- | -------- | ---------- | ---------------------------------------- | --------------------------------- |
| r1       | proposed | 2026-09-19 | systems architect                        | draft from logs and chat          |
| r2       | reviewed | 2026-09-23 | NOC lead, network architect, ops manager | actions agreed; A-03 closed later |
