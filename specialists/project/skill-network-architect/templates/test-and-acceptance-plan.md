---
Title: Test and acceptance plan template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Acceptance tests traced to requirements, with evidence layer, baseline, pass criterion, independent oracle, failure injection and sign-off.
---

# <scope> test and acceptance plan

Based on: Google SRE book, chapter 17 "Testing for Reliability" (https://sre.google/sre-book/testing-reliability/). Adapted: evidence layers and per-requirement traceability.
Failure-injection fields paraphrase the idea of Jeffallan/claude-skills chaos-engineer experiment design (MIT); no text copied.

## Contents

- [How to use](#how-to-use)
- [1. Scope and environment](#1-scope-and-environment)
- [2. Baseline](#2-baseline)
- [3. Test cases](#3-test-cases)
- [4. Failure injection](#4-failure-injection)
- [5. Entry and exit criteria](#5-entry-and-exit-criteria)
- [6. Defects and deviations](#6-defects-and-deviations)
- [7. Untested scope](#7-untested-scope)
- [8. Sign-off and review state](#8-sign-off-and-review-state)

## How to use

- Every requirement and every Severity 9-10 failure mode gets at least one test.
- A test passes on a measured observation at the user outcome, not on a configuration push.
- Say which evidence layer each test produces: static (review, lint, model script), lab, canary, or production.
- A lower layer never closes a higher-layer criterion.
- Use an independent oracle where possible: the measurement must not come from the component under test reporting on itself.

## 1. Scope and environment

| Field                            | Value                                                     |
| -------------------------------- | --------------------------------------------------------- |
| Design / change under test       | <DES-nnn> r<n> / <CHG-nnn>                                |
| Environments                     | lab <description>; canary <targets>; production <targets> |
| Test window and freeze           | <dates>                                                   |
| Tools and vantage points         | *probe locations, traffic generator, packet capture point* |
| Test lead / independent verifier | <role> / <role>                                           |

## 2. Baseline

| Metric | Population | Window | Value (p50 / p95) | Unit | Source | Captured     |
| ------ | ---------- | ------ | ----------------- | ---- | ------ | ------------ |
|        |            |        |                   |      |        | <YYYY-MM-DD> |

## 3. Test cases

| Test ID | REQ / FM / QS | Layer      | Preconditions        | Method (steps or command)        | Oracle                        | Pass criterion (measured)  | Result | Evidence path | Date | Tester |
| ------- | ------------- | ---------- | -------------------- | -------------------------------- | ----------------------------- | -------------------------- | ------ | ------------- | ---- | ------ |
| T-01    | REQ-01        | production | probe running 24 h   | synthetic transaction from       | external probe                | >= <n>% success over 7 d   |        |               |      |        |
|         |               |            |                      |   <vantage> every 60 s           |                               |                            |        |               |      |        |
| T-02    | FM-01, QS-01  | canary     | load at <n>% of peak | disable primary link             | external probe +              | loss <= <n> s, no          |        |               |      |        |
|         |               |            |                      |                                  |   flow counters               |   session reset            |        |               |      |        |
| T-03    | REQ-05        | lab        | policy applied       | connect user zone -> mgmt        | firewall log + client result  | blocked and logged         |        |               |      |        |
| T-04    | REQ-04        | lab        | backup <n> h old     | full restore of <dataset>        | restored service test         | service usable <= RTO      |        |               |      |        |
| T-05    | IF-<nnn>      | lab        |                      | DF-set probe at payload MTU      | packet capture                | no fragmentation, no drop  |        |               |      |        |

Negative tests: *list each denied flow or invalid input and the expected safe refusal.*

## 4. Failure injection

*One block per experiment. Run in lab first. Run in production only with the stop owner present and an approved window.*

| Field | Value |
| --- | --- |
| Experiment ID / linked test | FI-01 / T-02 |
| Hypothesis | *Given <steady state>, when <fault>, then <expected behaviour>, measured by <oracle>.* |
| Steady state | *metrics and normal ranges captured just before, e.g. p95 <n> ms, error ratio < <n>%* |
| Fault and method | *link down, power off, process kill, DNS failure, time skew, expired certificate; how injected* |
| Blast radius | *environment; share of traffic, hosts or sites; duration <n> min* |
| Abort triggers | *any of: <metric> beyond <n>; management access lost; user reports; error budget below <n> min* |
| Maximum rollback time | *<n> min from abort to steady state* |
| Success criteria | *measured result that confirms the hypothesis* |
| Stop authority | *<role> may stop at any time; implementer <role>* |
| Result and follow-up | *outcome, evidence path, action with owner* |


## 5. Entry and exit criteria

- Entry: *design accepted at r<n>; lab built; baseline captured; rollback rehearsed.*
- Exit: *all tests for in-scope REQ pass at the required layer; failures have an accepted risk or a fix with owner; untested items listed below.*

## 6. Defects and deviations

| ID  | Test | Observed | Expected | Severity | Decision (fix / accept / retest) | Owner |
| --- | ---- | -------- | -------- | -------- | -------------------------------- | ----- |
|     |      |          |          |          |                                  |       |

## 7. Untested scope

*List every requirement, failure mode or target not tested, with the reason and the risk register ID.*

## 8. Sign-off and review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
