---
Title: site-a WAN test and acceptance plan (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/test-and-acceptance-plan.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Acceptance tests for DES-012 at site-a traced to requirements, failure modes and quality scenarios, with evidence layer, independent oracle, two
  failure-injection experiments, lab results so far, one defect and the untested scope. All site facts are fictional.
---

# site-a WAN redesign test and acceptance plan

Fills template: [templates/test-and-acceptance-plan.md](../../templates/test-and-acceptance-plan.md).

- Fictional operator "Example Remote Networks" (ERN). Baselines and lab results are invented and labelled USER_STATED.
- Traces to [requirements](requirements-and-constraints.md) (REQ, QS), [failure modes](failure-mode-analysis.md) (FM, CF) and [CHG-031](change-and-validation.md).

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

How this example applied the template's rules:

- Every REQ in scope has a test; the only Severity 9 failure mode (FM-04, site box dead) has T-13.
- Pass criteria are measured at the user outcome (probe to the hub-1 VIP from site-a VLAN 10), not from the site box reporting on itself.
- Lab results are filled where the lab run happened (2026-10-28); canary and production rows are planned. A lab pass never closes a canary or production criterion.

## 1. Scope and environment

| Field                            | Value                                                                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Design / change under test       | DES-012 r2 / CHG-031 (prerequisite)                                                                                       |
| Environments                     | lab: lab-box-1 rev-A, LTE simulator with MTU 1428, satellite emulation; canary: site-a; production: site-a 30 days        |
| Test window and freeze           | lab 2026-10-28; canary 2026-11-17 22:00 to 2026-11-18 18:00 (busy-hour test 11:00); freeze on site-a config 7 days after  |
| Tools and vantage points         | probe host on site-a VLAN 10; external probe at hub-2 (independent of hub-1); iperf3 server at hub-1; capture on hub-gw-2 |
| Test lead / independent verifier | network architect / NOC lead                                                                                              |

## 2. Baseline

| Metric                         | Population             | Window              | Value (p50 / p95)             | Unit        | Source                   | Captured   |
| ------------------------------ | ---------------------- | ------------------- | ----------------------------- | ----------- | ------------------------ | ---------- |
| probe success to hub-1 VIP     | site-a                 | 30 days             | 98.8 (single value)           | % of probes | Prometheus, 5-min probes | 2026-10-06 |
| RTT site-a to hub-1, satellite | site-a                 | busy hour, 30 days  | 48 / 62                       | ms          | probe RTT, 1-min samples | 2026-10-06 |
| RTT site-b to hub-1, LTE       | site-b (proxy for LTE) | busy hour, 30 days  | 64 / 88                       | ms          | probe RTT, 1-min samples | 2026-10-06 |
| demand, tunnel counters        | site-a                 | busy hour, 30 days  | 15 / 22                       | Mbit/s      | wg-sat interface, 5-min  | 2026-10-06 |
| satellite throughput, iperf3   | site-a                 | 3 runs, 10:00-11:00 | 96 down, 14 up (single value) | Mbit/s      | iperf3 to hub-1          | 2026-10-06 |

## 3. Test cases

| Test ID | REQ / FM / QS  | Layer      | Preconditions  | Method (steps or command)       | Oracle          | Pass criterion (measured)   | Result   | Evidence path      | Date       | Tester       |
| ------- | -------------- | ---------- | -------------- | ------------------------------- | --------------- | --------------------------- | -------- | ------------------ | ---------- | ------------ |
| T-01    | REQ-01         | production | both tunnels   | HTTPS probe every 5 min from    | hub-2 external  | >= 99.5% over 30 days       | planned  | tests/T-01/        | 2026-12-18 | NOC lead     |
|         |                |            |   up 24 h      |   VLAN 10 to hub-1 VIP          |   probe of the  |                             |          |                    |            |              |
|         |                |            |                |                                 |   same VIP      |                             |          |                    |            |              |
| T-02    | REQ-02,        | canary     | busy hour;     | unpower the satellite           | hub-2 probe at  | loss <= 60 s; call survives | planned  | tests/T-02/        | 2026-11-18 | field        |
|         |   FM-01, QS-01 |            |   test         |   terminal (FI-01)              |   1 s +         |   or redials once           |          |                    |            |   technician |
|         |                |            |   call active  |                                 |   call log      |                             |          |                    |            |              |
| T-03    | REQ-03         | canary     | each path      | 60 min of 1-min RTT samples on  | probe RTT from  | p95 <= 150 ms on each path  | planned  | tests/T-03/        | 2026-11-18 | NOC lead     |
|         |                |            |   carrying     |   wg-sat, then on wg-lte        |   hub-2 side    |                             |          |                    |            |              |
|         |                |            |   traffic      |                                 |                 |                             |          |                    |            |              |
| T-04    | QS-02, FM-06   | canary     | site-a         | reboot hub-gw-1                 | hub-2 probe at  | loss <= 60 s                | planned  | tests/T-04/        | 2026-11-18 | systems      |
|         |                |            |   on wg-sat    |                                 |   1 s           |                             |          |                    |            |   architect  |
| T-05    | IF-004,        | lab        | CHG-031        | `ping -M do -s 1332 -c 100`     | capture         | 100 of 100 at 1332; 0 of    | pass     | tests/T-05/lab/    | 2026-10-28 | network      |
|         |   QS-03, FM-05 |            |   applied; LTE |   over wg-lte; then `-s 1333`   |   on hub-gw-2   |   100 at 1333, ICMP         |          |                    |            |   architect  |
|         |                |            |   sim MTU 1428 |                                 |                 |   fragmentation-needed seen |          |                    |            |              |
| T-05c   | IF-004,        | canary     | wg-lte up      | as T-05 on the real LTE path    | capture         | as T-05                     | planned  | tests/T-05/canary/ | 2026-11-17 | NOC lead     |
|         |   QS-03, FM-05 |            |   at site-a    |                                 |   on hub-gw-2   |                             |          |                    |            |              |
| T-06    | FM-03, FM-10   | lab        | wg-lte idle    | block LTE simulator traffic     | Alertmanager    | alert within 180 s          | fail     | tests/T-06/lab/    | 2026-10-28 | NOC lead     |
|         |                |            |   as standby   |                                 |   alert time    |                             |   (D-01) |                    |            |              |
| T-07    | FM-11          | canary     | PtP aligned    | read RSSI, SNR and rate for     | OpenWISP from   | RSSI p50 within 3 dB of     | planned  | tests/T-07/        | 2026-11-18 | field        |
|         |                |            |                |   24 h                          |   the far       |   -55.73 dBm; no rate drops |          |                    |            |   technician |
|         |                |            |                |                                 |   end radio     |                             |          |                    |            |              |
| T-08    | REQ-09, FM-09  | canary     | load at 216 W  | UPS runtime self-test           | UPS log +       | projected runtime >= 30 min | planned  | tests/T-08/        | 2026-11-18 | field        |
|         |                |            |   or above     |                                 |   external      |                             |          |                    |            |   technician |
|         |                |            |                |                                 |   power meter   |                             |          |                    |            |              |
| T-09    | FM-07, CF-05   | lab        | both WAN       | new 802.1X login; existing      | client result + | new login refused; existing | pass     | tests/T-09/lab/    | 2026-10-28 | systems      |
|         |                |            |   links down   |   client; open the sealed       |   device        |   client works; break-glass |          |                    |            |   architect  |
|         |                |            |                |   break-glass copy              |   login log     |   login works               |          |                    |            |              |
| T-10    | REQ-05, QS-04  | lab        | zone           | from guest: TCP 22 and 443 to   | site box deny   | all refused and logged, 1   | pass     | tests/T-10/lab/    | 2026-10-28 | network      |
|         |                |            |   policy       |   10.80.0.65; from users: same  |   log +         |   line per attempt          |          |                    |            |   architect  |
|         |                |            |   applied      |                                 |   client result |                             |          |                    |            |              |
| T-11    | REQ-06, QS-05  | canary     | satellite      | on-call logs in through wg-lte, | session log     | prompt within 120 s by      | planned  | tests/T-11/        | 2026-11-18 | NOC lead     |
|         |                |            |   unpowered    |   then through the OOB device   |                 |   each path                 |          |                    |            |              |
|         |                |            |   (during      |                                 |                 |                             |          |                    |            |              |
|         |                |            |   T-02)        |                                 |                 |                             |          |                    |            |              |
| T-12    | REQ-04         | canary     | off-peak       | iperf3 to hub-1, 3 runs         | hub-1 iperf3    | >= 22 Mbit/s on wg-sat; >=  | planned  | tests/T-12/        | 2026-11-18 | NOC lead     |
|         |                |            |                |   per path                      |   server report |   10 Mbit/s on wg-lte       |          |                    |            |              |
| T-13    | FM-04          | lab        | spare box from | swap the box, restore config    | probe success   | service back <= 60 min      | pass     | tests/T-13/lab/    | 2026-10-28 | field        |
|         |                |            |   the          |   from backup, bring up         |   from the      |   after arrival on site     |   (41    |                    |            |   technician |
|         |                |            |   depot pack   |   both tunnels                  |   probe host    |                             |   min)   |                    |            |              |

Negative tests: guest to corp and users to management (T-10); an oversize DF packet must be refused with ICMP, not silently dropped (T-05); a tunnel from an unknown key must not come up (lab, folded
into T-10: handshake refused, logged on hub-gw-2).

## 4. Failure injection

| Field                      | Value                                                                                                                                                                   |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Experiment ID /            | FI-01 / T-02                                                                                                                                                            |
|   linked test              |                                                                                                                                                                         |
| Hypothesis                 | Given site-a on wg-sat with a live test call and probes at 100%, when the satellite terminal loses power, then traffic moves to wg-lte within 60 s, measured by the     |
|                            |   hub-2 1-s probe.                                                                                                                                                      |
| Steady state               | probe success 100% over the previous 15 min; RTT p95 <= 62 ms; error ratio 0%                                                                                           |
| Fault and method           | satellite terminal PoE injector unplugged by the field technician on a phone call with the stop owner                                                                   |
| Blast radius               | site-a only; all of its hub-routed traffic; duration 10 min, then restore power                                                                                         |
| Abort triggers             | no failover after 90 s; management lost on both wg-lte and OOB; clinic staff report a dropped urgent call                                                               |
| Maximum rollback time      | 5 min from abort (re-plug, terminal boot about 3 min)                                                                                                                   |
| Success criteria           | measured loss <= 60 s; failback after 5 min of clean satellite probes once power returns, with no flap                                                                  |
| Stop authority             | NOC lead may stop at any time; implementer field technician                                                                                                             |
| Result and follow-up       | planned 2026-11-18 11:00                                                                                                                                                |

| Field                       | Value                                                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Experiment ID / linked test | FI-02 / FM-02 (A-03)                                                                                                                                                   |
| Hypothesis                  | Given the lab site box on emulated satellite, when 3% packet loss is injected, then the loss-based steering (A-03) moves traffic to wg-lte within 5 min, measured by   |
|                             |   the lab probe.                                                                                                                                                       |
| Steady state                | lab probe 100%; RTT 50 ms emulated                                                                                                                                     |
| Fault and method            | netem loss 3% on the emulated satellite link                                                                                                                           |
| Blast radius                | lab only; 30 min                                                                                                                                                       |
| Abort triggers              | lab probe host unreachable                                                                                                                                             |
| Maximum rollback time       | 1 min (remove netem rule)                                                                                                                                              |
| Success criteria            | traffic on wg-lte within 5 min; returns after 5 min of loss < 0.5%                                                                                                     |
| Stop authority              | network architect                                                                                                                                                      |
| Result and follow-up        | not run: A-03 due 2027-01-31                                                                                                                                           |

## 5. Entry and exit criteria

- Entry: DES-012 accepted at r2; CHG-031 done at site-a; SIM active and LTE MTU measured (DES-012 unknowns closed); baseline captured (section 2); FI-01 rollback rehearsed in the lab.
- Exit: T-01 to T-04, T-05c, T-07, T-08, T-11 and T-12 pass at canary or production layer; D-01 fixed and T-06 re-run; FI-02 and the untested items below are in the risk register.

## 6. Defects and deviations

| ID   | Test | Observed          | Expected           | Severity | Decision (fix / accept / retest)                                 | Owner    |
| ---- | ---- | ----------------- | ------------------ | -------- | ---------------------------------------------------------------- | -------- |
| D-01 | T-06 | alert after 246 s | alert within 180 s | medium   | fix: alert on handshake age > 150 s (keepalive 25 s x 6), retest | NOC lead |

## 7. Untested scope

- CF-02 (MNO-1 down while the satellite is down) and CF-03 (hub-1 duct cut): not tested, too wide a blast radius; accepted in DES-012 and listed in the risk register (RSK-012-02, RSK-012-03).
- REQ-07 (lifecycle) and REQ-08 (LTE data per month): checked by monthly reports, not by a test; first reading due 2026-12-31.
- SRG-update (bad firmware to a batch): covered by the CHG canary rules, not by this plan.
- FI-02 / FM-02: waits for action A-03.

## 8. Sign-off and review state

| Revision | State           | Date       | Reviewer (role)   | Evidence                                                      |
| -------- | --------------- | ---------- | ----------------- | ------------------------------------------------------------- |
| r1       | proposed        | 2026-10-22 | network architect | test list traced to REQ, FM, QS                               |
| r1       | evidence-needed | 2026-10-29 | NOC lead          | lab results in; D-01 open; canary rows waiting for 2026-11-17 |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
