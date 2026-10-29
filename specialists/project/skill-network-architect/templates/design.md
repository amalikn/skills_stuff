---
Title: Architecture design template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Working architecture design document from service outcome through requirements, views, failure model, decision status and sign-off.
---

# <service> architecture design

Worked example: `skill-network-architect/examples/filled/design.md` (filled for a fictional remote-site operator; lives in the network pack only).

Based on: arc42 section structure (https://arc42.org/overview) and C4 context/container views (https://c4model.com/). Adapted: network and infrastructure views replace code views.

## Contents

- [How to use](#how-to-use)
- [1. Decision and outcome](#1-decision-and-outcome)
- [2. Requirements and constraints](#2-requirements-and-constraints)
- [3. Context and current state](#3-context-and-current-state)
- [4. Target state](#4-target-state)
- [5. Failure domains and trust zones](#5-failure-domains-and-trust-zones)
- [6. Interfaces, options and decisions](#6-interfaces-options-and-decisions)
- [7. Capacity, risk and recovery](#7-capacity-risk-and-recovery)
- [8. Implementation, acceptance and operations](#8-implementation-acceptance-and-operations)
- [9. Review state](#9-review-state)

## How to use

- Use for a decision that changes structure, failure behaviour, ownership or cost of more than one component.
- For a single-component question write an ADR only.
- Fill sections 1-3 before drawing any target.
- Replace every `<placeholder>` and italic prompt.
- Delete a section only with a one-line reason (`Not applicable: <reason>`).
- Label every load-bearing fact VERIFIED_PRIMARY, VERIFIED_SECONDARY, USER_STATED or UNVERIFIED (meanings in the architecture method).
- An UNVERIFIED fact that changes the decision needs a discriminating test in section 3.

## 1. Decision and outcome

| Field                        | Value                                                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Design ID / revision         | <DES-nnn> / r<n>                                                                                           |
| Decision requested           | *One sentence: what must be decided, by whom, by when.*                                                    |
| Service outcome              | *User-visible result, e.g. "<site-code> users keep voice and payment service through loss of one backhaul".* |
| Service owner / design owner | <role> / <role>                                                                                            |
| Peer reviewers               | network: <role>; systems: <role>; specialists: <skill or role>                                             |
| Out of scope                 | *List explicit exclusions so reviewers do not assume coverage.*                                            |

## 2. Requirements and constraints

*Summarise here; keep the full table in `requirements-and-constraints.md`. Every target has a unit, window and measurement method.*

| ID     | Service   | Requirement  | Target and unit                 | Window    | Measurement method   | Owner  | Source label |
| ------ | --------- | ------------ | ------------------------------- | --------- | -------------------- | ------ | ------------ |
| REQ-01 | <service> | Availability | <n>% of 5-minute probes succeed | 30 days   | <probe from vantage> | <role> | USER_STATED  |
| REQ-02 | <service> | Recovery     | RTO <n> min, RPO <n> min        | per event | restore drill        | <role> | UNVERIFIED   |

Constraints (budget, power, space, licences, staffing, regulatory, change windows): *list each with source label.*

## 3. Context and current state

*Context: who uses the service and what it depends on. Current state: observed, with collection date and method. Do not draw intent as fact.*

```text
CONTEXT: who uses <service> and what it depends on (arrow = depends on)

+---------------------+   +-----------+   +----------------------+
| users @ <site-code> |-->| <service> |-->| DNS, time, identity, |
+---------------------+   +-----------+   | <upstream>           |
                                ^         +----------------------+
                                | manages, via the management plane
                          +-----------+   +--------------------+
                          | operators |-->| <management plane> |
                          +-----------+   +--------------------+
```

```text
CURRENT (observed <YYYY-MM-DD>, source <tool/command>)

+-----------------+  A   +-------------+   +------+   +-----------+
| <site-code> CPE |----->| aggregation |-->| core |-->| <service> |
+-----------------+      +-------------+   +------+   +-----------+
         |                      ^
         |          B ?         |
         +----------------------+

Legend: A = backhaul A, rate unverified; B ? = backhaul B suspected, UNKNOWN
```

| Unknown                            | Why it matters    | Discriminating test                                 | Owner  | Due    |
| ---------------------------------- | ----------------- | --------------------------------------------------- | ------ | ------ |
| *Is path B a separate duct/carrier?* | *Shared-risk group* | *Carrier circuit records + traceroute under failover* | <role> | <date> |

## 4. Target state

*Draw physical, logical and traffic views separately when combining hides meaning. Mark each item planned / observed / unknown / retired in text.*

```text
TARGET (planned): separate edges, aggregation and paths; independent management

+--------+   +-------+
| edge A |-->| agg A |---+
+--------+   +-------+   |   +-------------+   +-----------+
                         +-->| core/fabric |-->| <service> |
+--------+   +-------+   |   +-------------+   +-----------+
| edge B |-->| agg B |---+
+--------+   +-------+

+------------+   +--------------+
| OOB device |-->| mgmt network |   independent path and power
+------------+   +--------------+
```

## 5. Failure domains and trust zones

```text
FAILURE DOMAINS: members of a :::: zone fail together; '?' = shared risk not verified

:::: power feed A ::::::::   :::: power feed B ::::::::
: +--------+   +-------+ :   : +--------+   +-------+ :
: | edge A |   | agg A | :   : | edge B |   | agg B | :
: +--------+   +-------+ :   : +--------+   +-------+ :
::::::::::::::::::::::::::   ::::::::::::::::::::::::::

Shared by both zones: duct <id> ?, DNS, identity, update channel
```

```text
TRUST ZONES: each ==== line is an enforcement point and states its rule

+-----------------------+
| untrusted (internet)  |
+-----------------------+
==== edge policy at <device/function>, logged at <collector> ====
+-----------------------+
| user zone             |
+-----------------------+
==== service policy: user -> server <ports> allowed ===============
+-----------------------+
| server zone           |
+-----------------------+
==== management policy: mgmt -> all <ports>; user -> mgmt denied =
+-----------------------+
| management zone       |
+-----------------------+
```

*List correlated failures (rack, power, duct, carrier, control plane, identity, update channel) and the effect of losing each; full analysis in `failure-mode-analysis.md`.*

## 6. Interfaces, options and decisions

- Interfaces: *list interface-contract IDs and the authoritative writer of each shared field.*
- Options compared: *simplest viable, higher resilience, phased. One row each.*

| Option     | Meets REQ             | Failure coverage | Operating cost / staff effort | Exit cost | Verdict and ADR  |
| ---------- | --------------------- | ---------------- | ----------------------------- | --------- | ---------------- |
| A simplest | REQ-01 no, REQ-02 yes | single path      | low                           | low       | rejected ADR-<n> |

## 7. Capacity, risk and recovery

- Capacity: *demand, peak, growth horizon, N-1 behaviour and limiting resource; link `capacity-model.md`.*
- Risks: *top 3 with owner; full list in `risk-register.md`.*
- Recovery: *bootstrap order, independent access path, key/secret custody, backup and restore owner.*

## 8. Implementation, acceptance and operations

| Wave     | Scope            | Entry criteria | Acceptance test (REQ)   | Rollback trigger | Owner  |
| -------- | ---------------- | -------------- | ----------------------- | ---------------- | ------ |
| 0 canary | <1 site or host> | lab pass       | REQ-01 probe 24 h clean | <threshold>      | <role> |

Operations after go-live: alert owner, runbook link, recovery drill cadence, next review trigger.

## 9. Review state

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded). Acceptance binds to one revision.

| Revision | State    | Date         | Reviewer (role) | Evidence or reason |
| -------- | -------- | ------------ | --------------- | ------------------ |
| r1       | proposed | <YYYY-MM-DD> | <role>          | <link>             |
