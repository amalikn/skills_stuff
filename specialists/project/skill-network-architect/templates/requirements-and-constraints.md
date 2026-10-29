---
Title: Requirements and constraints template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Measurable per-service requirements, constraints and quality scenarios with owner, window, method and evidence label for each target.
---

# <service or programme> requirements and constraints

Based on: arc42 sections 1, 2 and 10 (goals, constraints, quality scenarios; https://arc42.org/overview).

## How to use

- Fill before any option is drawn.
- Every requirement needs a unit, an observation window, a measurement method and an owner; a target without these is a wish.
- Mark the kind of each target: business requirement (owner decided), measured baseline (observed), or illustrative assumption (to be confirmed).
- Do not copy universal percentages; derive each target from the consequence of failure.
- Label sources VERIFIED_PRIMARY / VERIFIED_SECONDARY / USER_STATED / UNVERIFIED.

## 1. Stakeholders and services

| Service   | Users and count | Critical journey              | Consequence of failure (per hour) | Service owner | Ops owner |
| --------- | --------------- | ----------------------------- | --------------------------------- | ------------- | --------- |
| <service> | <who, n>        | *e.g. payment at point of sale* | *revenue, safety, contract penalty* | <role>        | <role>    |

## 2. Requirements

| ID     | Service   | Category     | Requirement                        | Target and unit         | Window       | Measurement method       | Kind     | Owner  | Source label     |
| ------ | --------- | ------------ | ---------------------------------- | ----------------------- | ------------ | ------------------------ | -------- | ------ | ---------------- |
| REQ-01 | <service> | availability | reachable from <vantage>           | >= <n>% of 1-min probes | 30 d rolling | <probe tool, path>       | business | <role> | USER_STATED      |
| REQ-02 | <service> | latency      | user transaction                   | p95 <= <n> ms           | busy hour    | <synthetic / flow data>  | baseline |        | VERIFIED_PRIMARY |
| REQ-03 | <service> | throughput   | sustained per site                 | >= <n> Mbit/s           | busy hour    | interface counters 5-min |          |        |                  |
| REQ-04 | <dataset> | recovery     | RTO / RPO                          | <n> min / <n> min       | per event    | restore drill            |          |        |                  |
| REQ-05 | <service> | security     | *e.g. no user-zone access to mgmt* | 0 permitted flows       | continuous   | policy test + log review |          |        |                  |
| REQ-06 | <service> | operability  | *e.g. one on-call can recover alone* | runbook drill passes    | quarterly    | drill record             |          |        |                  |
| REQ-07 | <service> | lifecycle    | supported versions only            | 0 EOL components        | monthly      | lifecycle register       |          |        |                  |

Categories to consider: availability, latency, throughput, concurrency, RTO, RPO, maintenance windows, security, privacy, recoverability, lifecycle, cost, operability.

## 3. Quality scenarios

*Turn the important requirements into stimulus-response tests that acceptance can run.*

| Scenario | Source and stimulus  | Environment | Expected response          | Response measure                        | REQ    |
| -------- | -------------------- | ----------- | -------------------------- | --------------------------------------- | ------ |
| QS-01    | primary backhaul cut | busy hour   | traffic moves to secondary | service loss <= <n> s, no session reset | REQ-01 |

## 4. Constraints

| ID     | Constraint                     | Type        | Fixed or negotiable | Source and label | Effect on design |
| ------ | ------------------------------ | ----------- | ------------------- | ---------------- | ---------------- |
| CON-01 | *budget ceiling*               | commercial  |                     |                  |                  |
| CON-02 | *power available at site: <n> W* | physical    |                     |                  |                  |
| CON-03 | *change window only <day hh-hh>* | operational |                     |                  |                  |
| CON-04 | *regulatory, licence, spectrum* | legal       |                     |                  |                  |
| CON-05 | *staff skills and on-call size* | people      |                     |                  |                  |

## 5. Assumptions and open questions

| ID     | Assumption or question | Why it matters | How to confirm | Owner | Due | Label      |
| ------ | ---------------------- | -------------- | -------------- | ----- | --- | ---------- |
| ASM-01 |                        |                |                |       |     | UNVERIFIED |

## 6. Review state

| Revision | State    | Date | Reviewer (role) | Evidence or reason |
| -------- | -------- | ---- | --------------- | ------------------ |
| r1       | proposed |      |                 |                    |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
