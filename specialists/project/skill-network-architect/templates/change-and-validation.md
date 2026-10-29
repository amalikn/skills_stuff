---
Title: Change, acceptance and recovery template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Method of Procedure for one change: scope, pre-checks with expected output, step table with per-step rollback, go/no-go gates, canary and bounded batches, post-checks and comms.
---

# CHG-<nnn>: <change title> method of procedure

Based on: no single public MOP standard exists; this form follows common operator MOP practice. Canary and staged rollout follow the Google SRE Workbook, chapter 16 "Canarying Releases"
(https://sre.google/workbook/canarying-releases/).

## Contents

- [How to use](#how-to-use)
- [1. Scope and authorization](#1-scope-and-authorization)
- [2. Impact and dependencies](#2-impact-and-dependencies)
- [3. Pre-checks](#3-pre-checks)
- [4. Procedure](#4-procedure)
- [5. Gates, canary and batches](#5-gates-canary-and-batches)
- [6. Rollback](#6-rollback)
- [7. Post-checks and acceptance](#7-post-checks-and-acceptance)
- [8. Communications](#8-communications)
- [9. Closure and review state](#9-closure-and-review-state)

## How to use

- Write the MOP so a qualified operator who did not design the change can run it without asking questions.
- Every command has an expected result and a verification.
- Every step has a rollback step or the words "no rollback: forward repair only" with the reason.
- Rehearse in a lab or on the canary before the window.
- Approval of this document does not authorize targets outside section 1.

## 1. Scope and authorization

| Field                                                                        | Value                                            |
| ---------------------------------------------------------------------------- | ------------------------------------------------ |
| Change ID / revision / ticket                                                | CHG-<nnn> / r<n> / <ticket>                      |
| Objective                                                                    | *One sentence tied to REQ-<nn> or ADR-<nnnn>.*   |
| Targets (exact list or selector + count)                                     | <site-code list or inventory query>, n = <count> |
| Excluded targets                                                             | *and why*                                        |
| Window (start-end, timezone) / approver                                      | <YYYY-MM-DD hh:mm-hh:mm TZ> / <role>             |
| Implementer / verifier (different person when possible) / on-call escalation | <role> / <role> / <role>                         |
| Expected interruption per target                                             | <n> s of <service>, or none                      |
| Runtime budget                                                               | canary <n> min; per batch <n> min; total <n> min |

## 2. Impact and dependencies

- Exact semantic diff: *link the reviewed diff or rendered config; state what changes in behaviour, not only text.*
- Affected consumers and interfaces: *IF-<nnn>, monitoring, inventory intent fields, automation that may revert the change.*
- Dependencies that must be healthy first: *DNS, identity, controller, backup, OOB path.*

## 3. Pre-checks

*Run on every target in the batch. Any mismatch is a no-go for that target.*

| #   | Check                               | Command or action         | Expected output                          | Actual | Pass |
| --- | ----------------------------------- | ------------------------- | ---------------------------------------- | ------ | ---- |
| P1  | Independent access works            | <OOB / console login>     | prompt reached within <n> s              |        |      |
| P2  | Baseline service                    | <probe/query>             | <metric> within <range>, saved to <path> |        |      |
| P3  | Running revision matches intent     | <show command / API read> | revision <id>, no drift                  |        |      |
| P4  | Backup / config snapshot taken      | <command>                 | file <path> size > 0, checksum recorded  |        |      |
| P5  | No open incident or alarm on target | <monitoring query>        | zero active                              |        |      |

## 4. Procedure

| Step | Command or action | Expected result   | Verify                        | Rollback step | Owner  | Time budget |
| ---- | ----------------- | ----------------- | ----------------------------- | ------------- | ------ | ----------- |
| 1    | <command>         | <output or state> | <read-back command and value> | R1            | <role> | <n> min     |
| 2    | <command>         |                   |                               | R2            |        |             |

*Query an uncertain write outcome before retrying. Record start/end time and result per target in a journal at <path>.*

## 5. Gates, canary and batches

```text
ROLLOUT GATES: a failed gate stops the run (no new targets start)

+------------+   +----+   +------------+   +------+   +----+   +-----------+   +----+   +-------------+
| pre-checks |-->| G0 |-->| canary n=1 |-->| soak |-->| G1 |-->| batch 1   |-->| G2 |-->| post-checks |
| all pass   |   +----+   | to 2       |   | <n>  |   +----+   | n=<k>,    |   +----+   | and close   |
+------------+            +------------+   | min  |            | conc. <c> |            +-------------+
                                           +------+            +-----------+
```

| Gate | Go criteria (all true)              | No-go / stop conditions (any true)                                                | Decision owner |
| ---- | ----------------------------------- | --------------------------------------------------------------------------------- | -------------- |
| G0   | all pre-checks pass on canary       | access or backup missing                                                          | <role>         |
| G1   | canary post-checks pass, soak clean | <metric> worse than baseline by <n>; new alarm; any unexplained output            | <role>         |
| G2+  | failed targets in batch <= <n>      | failures > <n>, or same failure on 2 targets, or window remaining < rollback time | <role>         |

Canary choice: *why these targets represent the population (model, firmware, topology, load).* Batch size and concurrency: *why bounded at this value.*

## 6. Rollback

| Trigger (measured)                           | Decide within      | Rollback steps            | Rollback time budget | Verified by          |
| -------------------------------------------- | ------------------ | ------------------------- | -------------------- | -------------------- |
| <service probe fails n consecutive>          | <n> min of trigger | R<n>..R1 in reverse       | <n> min per target   | P2 baseline restored |
| Window remaining < rollback budget + <n> min | immediately        | stop starting new targets |                      |                      |

Rollback limits: *what cannot be undone (data migration, firmware downgrade block, key rotation) and the forward-repair boundary.*

## 7. Post-checks and acceptance

| #   | Check                             | Expected (vs baseline)                                  | Actual and evidence | Time | Owner |
| --- | --------------------------------- | ------------------------------------------------------- | ------------------- | ---- | ----- |
| Q1  | User-outcome test from <vantage>  | <transaction succeeds, latency within n ms of baseline> |                     |      |       |
| Q2  | Intent and observation reconciled | inventory and device agree                              |                     |      |       |
| Q3  | Monitoring shows target healthy   | no new alarms for <n> min                               |                     |      |       |

## 8. Communications

| When                    | Audience                | Channel   | Message owner | Content                 |
| ----------------------- | ----------------------- | --------- | ------------- | ----------------------- |
| T-<n> days              | affected users / owners | <channel> | <role>        | window, impact, contact |
| Start / each gate / end | operations              | <channel> | implementer   | status, next gate       |
| On rollback             | owners + on-call        | <channel> | <role>        | trigger, state, ETA     |

## 9. Closure and review state

- Targets done / skipped / rolled back: <n> / <n> / <n>, journal at <path>. Untested areas: *list.*
- Follow-ups with owner and date. Lessons: *feed the post-incident review if any rollback occurred.*

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
