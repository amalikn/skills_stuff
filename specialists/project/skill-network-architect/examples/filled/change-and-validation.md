---
Title: CHG-031 fleet tunnel MTU change (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/change-and-validation.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Method of procedure for lowering the WireGuard tunnel MTU from 1420 to 1360 on 40 site boxes and two hub concentrators: `just mtu` before and after,
  a stratum canary of 6, three bounded batches, gates, rollback and post-checks. All site facts are fictional.
---

# CHG-031: fleet tunnel MTU 1420 to 1360 method of procedure

Fills template: [templates/change-and-validation.md](../../templates/change-and-validation.md).

- Fictional operator "Example Remote Networks" (ERN). Site and device facts are invented and labelled USER_STATED; device commands are named by job, not invented CLI syntax.
- Inputs: [change-and-validation-before.json](change-and-validation-before.json), [change-and-validation.json](change-and-validation.json).
- Raised by [ADR-0007](decision-record.md) (consequence: LTE underlay MTU 1428) and failure mode FM-05 in [failure-mode-analysis.md](failure-mode-analysis.md).

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

How this example applied the template's rules:

- Written for the on-call engineer who did not design it: every step names the job or command, the expected result and the read-back.
- Rehearsed in the lab on 2026-10-28 on one rev-A and one rev-B site box; the Actual columns in section 3 record that rehearsal. Production results go to the journal.
- Why the change, in numbers:

```text
$ just mtu examples/filled/change-and-validation-before.json   # exit 1 (today's 1420 template)
  fleet-sat-wg-1420: underlay 1500, payload_mtu 1440  -> fits
  fleet-lte-wg-1420: underlay 1428, payload_mtu 1368  -> finding:
    "fleet-lte-wg-1420: payload MTU 1368 is 52 short of 1420;
     raise the underlay to 1480 or lower the inner MTU"

$ just mtu examples/filled/change-and-validation.json          # exit 0 (target 1360)
  site-a-sat-wg-1360: payload_mtu 1440, tcp_mss_ipv4 1400   margin 80 B
  site-a-lte-wg-1360: payload_mtu 1368, tcp_mss_ipv4 1328   margin 8 B
```

The LTE underlay cannot be raised (carrier), so the inner MTU drops. 1360 leaves 8 bytes of margin on LTE; MSS is clamped at 1360 - 40 = 1320 so TCP never depends on PMTUD.

## 1. Scope and authorization

| Field                                                                        | Value                                                                                                           |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Change ID / revision / ticket                                                | CHG-031 / r2 / NOC-2291                                                                                         |
| Objective                                                                    | Tunnel MTU 1360 and MSS clamp 1320 everywhere, so an LTE failover (ADR-0007) never black-holes packets (FM-05). |
| Targets (exact list or selector + count)                                     | group "site-boxes-active", n = 39 (40 less site-ah); hub-gw-1, hub-gw-2; template default           |
| Excluded targets                                                             | lab boxes (already done); site-ah (decommissioning 2026-11-30, tunnel removed then)                             |
| Window (start-end, timezone) / approver                                      | 2026-11-03 22:00-02:00 and 2026-11-10 22:00-02:00, local (UTC+10) / operations manager                          |
| Implementer / verifier (different person when possible) / on-call escalation | network architect / NOC lead / systems architect (hub-gw hosts)                                                 |
| Expected interruption per target                                             | none expected (lab: tunnel stayed up, 0 probe loss); budget 5 s                                                 |
| Runtime budget                                                               | hub 10 min; canary 18 min + 24 h soak; per batch 15-18 min; batches 66.45 min + 30 min of gates            |

site-ah is excluded, so 39 site boxes change in production: 6 canaries + 33 in batches (section 5).

## 2. Impact and dependencies

- Exact semantic diff (rendered by the `tunnel-provision` job, dry-run): `wg-sat mtu 1420 -> 1360`; `mss-clamp wg-sat absent -> 1320`; template default `tunnel_mtu 1420 -> 1360`. Behaviour: inner
  packets above 1360 bytes are fragmented by the sender or, with DF set, refused with ICMP fragmentation-needed at the site box; TCP sessions negotiate MSS 1320.
- Affected consumers and interfaces: IF-004 (tunnel MTU field); Nautobot intent field `tunnel_mtu` (writer: `tunnel-provision` only); the Golden Config compliance rule for tunnels; Prometheus DF probe
  added at 1360 bytes.
- Dependencies that must be healthy first: Nautobot and the job runner (hub-1 cluster), OOB device per site, config backup, hub-gw-1 and hub-gw-2 both in service.

## 3. Pre-checks

Run on every target in the batch. Any mismatch is a no-go for that target. Actual and Pass record the lab rehearsal on 2026-10-28 (lab-box-1 rev-A fw 4.3, lab-box-2 rev-B fw 4.2).

| #   | Check                               | Command or action                               | Expected output                                                | Actual (lab)                   | Pass |
| --- | ----------------------------------- | ----------------------------------------------- | -------------------------------------------------------------- | ------------------------------ | ---- |
| P1  | Independent access works            | OOB device console login to the site box        | prompt reached within 120 s                                    | 41 s / 55 s                    | yes  |
| P2  | Baseline service                    | Prometheus: probe success and RTT, last 60 min  | success 100%, RTT p95 within 10 ms of 7-day p95; saved         | 100% / 100%, p95 63 ms / 66 ms | yes  |
|     |                                     |                                                 |   to journal                                                   |                                |      |
| P3  | Running revision matches intent     | Golden Config compliance for the target         | compliant; tunnel_mtu 1420 on device and in Nautobot           | compliant / compliant          | yes  |
| P4  | Backup / config snapshot taken      | Golden Config backup job for the target         | file size > 0, SHA-256 recorded in the journal                 | 18.2 KiB / 17.9 KiB, recorded  | yes  |
| P5  | No open incident or alarm on target | Alertmanager: active alerts with the site label | zero active                                                    | 0 / 0                          | yes  |

## 4. Procedure

| Step | Command or action                                           | Expected result                      | Verify                                   | Rollback step | Owner           | Time budget |
| ---- | ----------------------------------------------------------- | ------------------------------------ | ---------------------------------------- | ------------- | --------------- | ----------- |
| H1   | hub-gw-2: set wg interfaces MTU 1360 (host config           | interfaces at 1360; tunnels stay up  | `ip link show` reads mtu 1360;           | RH1           | systems         | 5 min       |
|      |   management, one host)                                     |                                      |   handshakes fresh on all tunnels        |               |   architect     |             |
| H2   | hub-gw-1: same as H1, after 5 min clean on hub-gw-2         | as H1                                | as H1; fleet probe success unchanged     | RH2           | systems         | 5 min       |
|      |                                                             |                                      |                                          |               |   architect     |             |
| 1    | Nautobot: set `tunnel_mtu` = 1360 on the target (bulk edit  | intent changed, change log entry     | Nautobot API read shows 1360             | R1            | network         | 1 min       |
|      |   via change)                                               |                                      |                                          |               |   architect     |             |
| 2    | `tunnel-provision` job, dry-run, target only                | diff = exactly the 2 lines in        | diff line count 2; no other              | none needed   | network         | 1 min       |
|      |                                                             |   section 2                          |   object touched                         |               |   architect     |             |
| 3    | `tunnel-provision` job, apply, with timed auto-revert       | job success; operation ID recorded   | site box read-back: mtu 1360, clamp 1320 | R3            | network         | 2 min       |
|      |   10 min                                                    |                                      |                                          |               |   architect     |             |
| 4    | DF probe from the VLAN 10 probe                             | 20 of 20 replies (1332 + 28 =        | probe output saved to journal            | R3            | NOC lead        | 1 min       |
|      |   host: `ping -M do -s 1332 -c 20 10.10.0.21`               |   1360 bytes)                        |                                          |               |                 |             |
| 5    | Oversize probe: `ping -M do -s 1333 -c 3 10.10.0.21`        | no replies; ICMP                     | site box counter for ICMP type 3 code    | R3            | NOC lead        | 1 min       |
|      |                                                             |   fragmentation-needed seen          |   4 increments                           |               |                 |             |
| 6    | Confirm the change (cancel the auto-revert)                 | revert cancelled                     | device reports no pending revert         | R1            | network         | 1 min       |
|      |                                                             |                                      |                                          |               |   architect     |             |

Query an uncertain write outcome before retrying: if step 3 times out, read the device first; re-run only if the read-back shows 1420. Journal: `changes/CHG-031/journal.csv`, one row per target with
start, end, old and new value, operation ID and result.

## 5. Gates, canary and batches

```text
ROLLOUT GATES: a failed gate stops the run (no new targets start); G2+ follows every batch

+------------+   +----+   +----------+   +-----------+   +------+   +----+   +----------------+   +-----+
| pre-checks |-->| G0 |-->| hub H1,  |-->| canary 6, |-->| soak |-->| G1 |-->| B1 10, B2 12,  |-->| G2+ |
| all pass   |   +----+   | then H2  |   | conc. 2   |   | 24 h |   +----+   | B3 11, conc. 4 |   +-----+
+------------+            +----------+   +-----------+   +------+            +----------------+
```

| Gate | Go criteria (all true)                                                        | No-go / stop conditions (any true)                                                        | Decision owner    |
| ---- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ----------------- |
| G0   | all pre-checks pass on the canary; both hub-gw healthy                        | OOB or backup missing at any canary                                                       | NOC lead          |
| G1   | canary post-checks pass; 24 h soak: probe success >= 99.5%, no new alarms, DF | probe RTT p95 worse than baseline by 10 ms; new alarm; any oversize probe answered (MSS   | operations        |
|      |   probe clean                                                                 |   clamp missing)                                                                          |   manager         |
| G2+  | failed targets in batch <= 1                                                  | 2 or more failures, or the same failure on 2 targets, or window left < rollback 9 min +   | NOC lead          |
|      |                                                                               |   30 min                                                                                  |                   |

Canary choice: one site per stratum, so every combination of hardware, firmware and backhaul is exercised before any batch (USER_STATED counts from Nautobot):

| Stratum | Hardware | Firmware | Backhaul  | Sites in production | Canary  |
| ------- | -------- | -------- | --------- | ------------------- | ------- |
| S1      | rev-A    | 4.3      | sat + LTE | 14                  | site-a  |
| S2      | rev-A    | 4.2      | sat + LTE | 4                   | site-f  |
| S3      | rev-A    | 4.3      | sat only  | 10                  | site-k  |
| S4      | rev-B    | 4.3      | sat + LTE | 6                   | site-p  |
| S5      | rev-B    | 4.3      | sat only  | 3 (4 less site-ah)  | site-u  |
| S6      | rev-B    | 4.2      | sat only  | 2                   | site-ab |
| total   |          |          |           | 39                  | 6       |

Arithmetic (rules in the pack's automation and safety reference):

- A random 6 would see a defect on 20% of sites with probability 1 - (1 - 0.2)^6 = 0.738; 95% confidence at p = 20% needs ln(0.05) / ln(0.8) = 13.4, so 14 random sites. The stratum canary covers all 6
  strata with 6 sites, including S6, which is 2 of 39 sites (5.1%) and which a random sample would usually miss.
- Batches: 39 - 6 = 33 sites in B1 10, B2 12, B3 11, concurrency 4, p95 per target 6 min (lab rehearsal, USER_STATED). B1 10 / 4 x 6 = 15 min; B2 12 / 4 x 6 = 18 min; B3 11 / 4 x 6 = 16.5 min; sum
  49.5 min. Wall time = 49.5 + slowest target 12 min + 10% retries 4.95 min = 66.45 min, plus three 10-min G2 soaks = 96.45 min inside the 240-min window.
- Batch size and concurrency: bounded so a whole-batch rollback (12 / 4 x 3 min = 9 min) fits inside the window with 30 min to spare, and so one engineer can watch 4 sites at once.

## 6. Rollback

| Trigger (measured)                                | Decide within   | Rollback steps                                                            | Rollback time budget | Verified by                 |
| ------------------------------------------------- | --------------- | ------------------------------------------------------------------------- | -------------------- | --------------------------- |
| probe success < 100% for 3 consecutive minutes on | 5 min           | R3: let auto-revert fire, or re-apply 1420 by the job; R1: Nautobot       | 3 min per target     | P2 baseline restored        |
|   a target                                        |   of trigger    |   `tunnel_mtu` back to 1420                                               |                      |                             |
| oversize probe answered (MSS clamp or MTU         | immediately     | R3, R1 on that target; stop the batch                                     | 3 min per target     | P3 compliance at 1420       |
|   not applied)                                    |                 |                                                                           |                      |                             |
| hub-gw probe loss after H1 or H2                  | 5 min           | RH1 / RH2: set the hub interface back to 1420                             | 2 min per host       | fleet probe success         |
|                                                   |   of trigger    |                                                                           |                      |   at baseline               |
| window remaining < rollback budget + 30 min       | immediately     | stop starting new targets                                                 |                      |                             |

Rollback limits: none irreversible. Configuration rollback restores 1420, which is also the FM-05 exposure, so a rollback blocks DES-012 wave 1 until the cause is fixed.

## 7. Post-checks and acceptance

| #   | Check                                          | Expected (vs baseline)                                  | Actual and evidence      | Time       | Owner    |
| --- | ---------------------------------------------- | ------------------------------------------------------- | ------------------------ | ---------- | -------- |
| Q1  | User-outcome test from site VLAN 10 probe host | HTTPS to hub-1 VIP succeeds; RTT p95 within 10 ms of P2 | journal, per target      | +15 min    | NOC lead |
| Q2  | Intent and observation reconciled              | Golden Config compliant at 1360 for every target        | compliance report        | end of run | NOC lead |
| Q3  | Monitoring shows target healthy                | no new alarms for 60 min; DF probe at 1360 clean        | Alertmanager, Prometheus | +60 min    | NOC lead |
| Q4  | LTE path ready (LTE sites only)                | DES-012 T-05 later passes on wg-lte at 1360             | test plan                | wave 1     | NOC lead |

## 8. Communications

| When                    | Audience                               | Channel          | Message owner      | Content                                       |
| ----------------------- | -------------------------------------- | ---------------- | ------------------ | --------------------------------------------- |
| T-5 days                | clinic services manager, site owners   | email            | operations manager | window, "no interruption expected", contact   |
| Start / each gate / end | NOC and on-call                        | NOC chat channel | network architect  | gate result, next gate, targets done / failed |
| On rollback             | site owner + on-call systems architect | phone, then chat | NOC lead           | trigger, state, ETA, next decision time       |

## 9. Closure and review state

- Targets done / skipped / rolled back: planned 39 / 1 (site-ah) / 0; to be filled from `changes/CHG-031/journal.csv`. Untested areas: the LTE path itself (no wg-lte exists until DES-012 wave 1;
  covered by T-05 there); fw 4.2 MSS clamp behaviour under heavy load.
- Follow-ups: set `tunnel_mtu` default 1360 in the onboarding job (network architect, 2026-11-10); add the 1360-byte DF probe to the site dashboard (NOC lead, 2026-11-10). Any rollback feeds a PIR.

| Revision | State           | Date       | Reviewer (role)    | Evidence                                                       |
| -------- | --------------- | ---------- | ------------------ | -------------------------------------------------------------- |
| r1       | proposed        | 2026-10-22 | network architect  | `just mtu` before and after                                    |
| r1       | evidence-needed | 2026-10-24 | NOC lead           | asked for a stratum canary and a lab rehearsal on rev-B fw 4.2 |
| r2       | accepted        | 2026-10-29 | operations manager | lab rehearsal 2026-10-28 (section 3); canary table             |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
