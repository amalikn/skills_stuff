---
Title: site-a WAN failure mode analysis (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/failure-mode-analysis.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  FMEA for the DES-012 target at site-a: eleven failure modes with S/O/D scores and RPN, seven shared-risk groups, five correlated scenarios and the
  actions that change the scores. All site facts are fictional.
---

# site-a WAN and hub path failure mode analysis

Fills template: [templates/failure-mode-analysis.md](../../templates/failure-mode-analysis.md).

- Fictional operator "Example Remote Networks" (ERN). Scores are the review team's judgement (USER_STATED); no row is tested yet, so every Test cell says what will prove it.
- Scope: the [DES-012](design.md) target from the site-a LAN edge to the hub-1 concentrators, plus the management and identity paths that recovery needs.

## Contents

- [How to use](#how-to-use)
- [1. Components and shared-risk groups](#1-components-and-shared-risk-groups)
- [2. Failure modes](#2-failure-modes)
- [3. Correlated failure scenarios](#3-correlated-failure-scenarios)
- [4. Actions](#4-actions)
- [5. Review state](#5-review-state)

## How to use

How this example applied the template's rules:

- Components came from the DES-012 target diagram; failure kinds walked per component: dead, degraded, wrong (MTU), expired (SIM plan), unreachable for management.
- RPN = S x O x D ranks work only. FM-05 ranks first (441); FM-04 has a low RPN (36) but Severity 9, so it gets an action anyway.
- Until T-01..T-08 run, every row is UNVERIFIED at the test layer.

## 1. Components and shared-risk groups

| Shared-risk group | Members                                                          | Evidence it is shared or separate                | Label       |
| ----------------- | ---------------------------------------------------------------- | ------------------------------------------------ | ----------- |
| SRG-power-site-a  | site box, switch, sat terminal, LTE router, OOB device, APs, PtP | site survey: one UPS, one mains feed             | USER_STATED |
| SRG-site-box      | wg-sat, wg-lte, zone policy, guest NAT                           | design: both tunnels terminate on one box        | USER_STATED |
| SRG-carrier-MNO-1 | LTE WAN (B), OOB device SIM                                      | both SIMs from MNO-1; no third carrier at site-a | USER_STATED |
| SRG-hub-duct      | both hub-1 internet uplinks, so every site's hub-routed traffic  | carrier records (hub-1 capacity model)           | USER_STATED |
| SRG-control       | Nautobot, OpenWISP, Grafana on the hub-1 Proxmox cluster         | one cluster (DES-014)                            | USER_STATED |
| SRG-identity      | RADIUS for ern-staff, admin AAA, secret store for break-glass    | all hosted at hub-1                              | USER_STATED |
| SRG-update        | site box firmware channel and signing key, 40 sites              | one vendor channel                               | UNVERIFIED  |

```text
SHARED-RISK GROUPS: everything inside one :::: zone can fail together; '?' = unverified

:::: SRG-power-site-a ::::::::::::::::::::::::   :::: SRG-control (hub-1 cluster) ::::::::::
: +----------+ +--------+ +---------------+  :   : +----------+ +----------+ +---------+ :
: | site box | | switch | | sat terminal  |  :   : | Nautobot | | OpenWISP | | Grafana | :
: +----------+ +--------+ +---------------+  :   : +----------+ +----------+ +---------+ :
: LTE router, OOB device, APs, PtP radio     :   ::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::
                                                 :::: SRG-identity (hub-1) :::::::::::::::::
:::: SRG-carrier-MNO-1 :::::::::::::::::::::::   : RADIUS, admin AAA, secret store        :
: LTE WAN B, OOB device SIM                  :   ::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::
                                                 :::: SRG-update ? ::::::::::::::::::::::::
:::: SRG-hub-duct ::::::::::::::::::::::::::::   : site box firmware for all 40 sites     :
: both hub-1 uplinks: all 40 sites           :   ::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::
```

## 2. Failure modes

Detection = signal, threshold and time to detect. Recovery = action and time. Test = method and date last run (none run yet; planned test IDs from the test plan).

| ID    | Component | Failure mode   | Cause            | Detection        | Local effect  | Service effect     | Blast radius | S   | O   | D   | RPN | Recovery        | Test        | Owner         |
| ----- | --------- | -------------- | ---------------- | ---------------- | ------------- | ------------------ | ------------ | --- | --- | --- | --- | --------------- | ----------- | ------------- |
| FM-01 | satellite | down           | network outage,  | probe loss 3 x   | traffic       | <= 60 s loss       | 1 site       | 6   | 5   | 2   | 60  | automatic, <=   | T-02,       | NOC lead      |
|       |           |                |   obstruction    |   10 s           |   to wg-lte   |                    |              |     |     |     |     |   60 s          |   planned   |               |
| FM-02 | satellite | degraded,      | partial          | often undetected | retransmits   | slow booking,      | 1 site       | 5   | 6   | 7   | 210 | manual steer,   | FI-02 lab,  | NOC lead      |
|       |           |   loss 2-5%    |   obstruction    |                  |               |   poor voice       |              |     |     |     |     |   30 min        |   planned   |               |
| FM-03 | LTE       | dead           | modem            | none today       | no backup     | outage on next     | 1 site       | 7   | 4   | 8   | 224 | site visit, 7 h | T-06,       | NOC lead      |
|       |   standby |   while unused |   hang, antenna  |                  |               |   sat loss         |              |     |     |     |     |                 |   planned   |               |
| FM-04 | site box  | dead           | hardware,        | both tunnels     | all LAN       | all services down  | 1 site       | 9   | 2   | 2   | 36  | spare + travel, | depot       | field         |
|       |           |                |   power surge    |   down +         |   cut off     |                    |              |     |     |     |     |   7 h           |   drill,    |   technician  |
|       |           |                |                  |   OOB alive      |               |                    |              |     |     |     |     |                 |   planned   |               |
| FM-05 | wg-lte    | MTU black hole | tunnel 1420 >    | none: small      | large packets | TLS stalls         | 24 sites     | 7   | 7   | 9   | 441 | CHG-031,        | T-05,       | network       |
|       |   tunnel  |                |   path 1368      |   probes pass    |   dropped     |   on failover      |              |     |     |     |     |   then          |   planned   |   architect   |
|       |           |                |                  |                  |               |                    |              |     |     |     |     |   automatic     |             |               |
| FM-06 | hub-gw-1  | down           | host or          | wg-sat           | site          | <= 60 s loss       | 40 sites     | 4   | 3   | 2   | 24  | automatic;      | T-04,       | systems       |
|       |           |                |   software fault |   handshake loss |   uses wg-lte |                    |              |     |     |     |     |   repair gw-1   |   planned   |   architect   |
| FM-07 | RADIUS    | unreachable    | both WANs down,  | auth failure log | new staff     | staff Wi-Fi only   | 1 site       | 5   | 4   | 6   | 120 | wait for WAN;   | T-09,       | systems       |
|       |           |                |   hub outage     |                  |   logins fail |   for              |              |     |     |     |     |   wired desks   |   planned   |   architect   |
|       |           |                |                  |                  |               |   already-joined   |              |     |     |     |     |                 |             |               |
| FM-08 | control   | unreachable    | hub-1            | Grafana itself   | no            | none short term    | fleet        | 3   | 3   | 3   | 27  | DES-014         | PIR-005     | systems       |
|       |   plane   |                |   cluster outage |   down: external |   config push |                    |              |     |     |     |     |   cluster       |   actions   |   architect   |
|       |           |                |                  |   check          |               |                    |              |     |     |     |     |   rebuild       |             |               |
|       |           |                |                  |   from hub-2     |               |                    |              |     |     |     |     |                 |             |               |
| FM-09 | UPS       | runtime <      | battery ageing   | none until a     | early         | outage in          | 1 site       | 7   | 4   | 7   | 196 | battery swap,   | T-08,       | field         |
|       |           |   30 min       |                  |   mains failure  |   shutdown    |   long blackout    |              |     |     |     |     |   next visit    |   planned   |   technician  |
| FM-10 | LTE SIM   | suspended      | plan lapse, 50   | none today       | wg-lte down   | as FM-03           | 1 site       | 7   | 3   | 8   | 168 | carrier call,   | T-06,       | clinic        |
|       |           |   or capped    |   GB used        |                  |               |                    |              |     |     |     |     |   1-24 h        |   planned   |   svc manager |
| FM-11 | PtP radio | fade below     | rain, tank       | RSSI < -62 dBm   | telemetry     | pump alarm missed  | 1 site       | 6   | 3   | 4   | 72  | realign or      | T-07,       | field         |
|       |           |   threshold    |   growth,        |                  |   lost        |                    |              |     |     |     |     |   lower rate,   |   planned   |   technician  |
|       |           |                |   alignment      |                  |               |                    |              |     |     |     |     |   7 h           |             |               |
|       |           |                |   drift          |                  |               |                    |              |     |     |     |     |                 |             |               |

RPN check: 6x5x2 = 60; 5x6x7 = 210; 7x4x8 = 224; 9x2x2 = 36; 7x7x9 = 441; 4x3x2 = 24; 5x4x6 = 120; 3x3x3 = 27; 7x4x7 = 196; 7x3x8 = 168; 6x3x4 = 72.

## 3. Correlated failure scenarios

| Scenario | Shared-risk group lost | Components lost together        | Remaining capacity vs demand    | Service result                 | Recovery path still available?             | Test           |
| -------- | ---------------------- | ------------------------------- | ------------------------------- | ------------------------------ | ------------------------------------------ | -------------- |
| CF-01    | SRG-power-site-a       | everything at site-a after 38   | 0 of 22 Mbit/s                  | all site-a services down       | no: OOB device is on the same UPS          | T-08           |
|          |                        |   min on UPS                    |                                 |                                |                                            |   UPS          |
|          |                        |                                 |                                 |                                |                                            |   self-test    |
| CF-02    | SRG-carrier-MNO-1 +    | WAN B and the OOB SIM           | 0 of 22 Mbit/s                  | all hub-routed services down;  | no remote path; site visit (accepted       | none: accepted |
|          |   satellite down       |                                 |                                 |   guest down                   |   in DES-012)                              |                |
| CF-03    | SRG-hub-duct           | both hub-1 uplinks, all         | 0 of 22 Mbit/s per              | booking, voice, telemetry      | yes: OOB reaches site boxes; hub services  | carrier        |
|          |                        |   40 sites                      |   site, hub-routed              |   down; guest Wi-Fi up         |   need the duct                            |   records only |
| CF-04    | SRG-update             | bad firmware on a batch of      | as FM-04 for each box in        | batch sites down               | rollback image held on each box?           | CHG            |
|          |                        |   site boxes                    |   the batch                     |   until rollback               |   UNVERIFIED (skill-smc)                   |   canary rules |
| CF-05    | SRG-identity           | RADIUS, admin AAA and the       | n/a                             | service up, unmanageable, new  | only if a sealed offline break-glass copy  | T-09 drill     |
|          |                        |   break-glass store             |                                 |   staff logins fail            |   exists (A-07)                            |                |

## 4. Actions

| Action                                                                | Rows addressed | Expected change in S/O/D                     | Owner              | Due        | Status      |
| --------------------------------------------------------------------- | -------------- | -------------------------------------------- | ------------------ | ---------- | ----------- |
| A-01 CHG-031: tunnel MTU 1360, MSS 1320, 1360-byte DF probe alert     | FM-05          | O 7 -> 1, D 9 -> 2: RPN 441 -> 14            | network architect  | 2026-11-10 | in progress |
| A-02 probe the standby tunnel continuously; handshake age alert 180 s | FM-03, FM-10   | D 8 -> 2: RPN 224 -> 56, 168 -> 42           | NOC lead           | 2026-11-18 | open        |
| A-03 loss-based steering: loss > 2% over 5 min moves to wg-lte        | FM-02          | D 7 -> 3: RPN 210 -> 90                      | network architect  | 2027-01-31 | open        |
| A-04 pre-configured spare site box at the regional depot              | FM-04          | no S/O/D change; recovery from 3 days to 7 h | field technician   | 2026-12-15 | open        |
| A-05 quarterly UPS self-test with runtime alert below 30 min          | FM-09          | D 7 -> 2: RPN 196 -> 56                      | field technician   | 2026-12-15 | open        |
| A-06 LTE data alert at 80% of 50 GB                                   | FM-10          | O 3 -> 2 (with A-02: RPN 168 -> 28)          | clinic svc manager | 2026-11-18 | open        |
| A-07 sealed offline break-glass copy held at the NOC                  | CF-05          | recovery path exists without hub-1           | systems architect  | 2026-12-15 | open        |

Arithmetic: 7x1x2 = 14; 7x4x2 = 56; 7x3x2 = 42; 5x6x3 = 90; 7x4x2 = 56; 7x2x2 = 28.

## 5. Review state

| Revision | State    | Date       | Reviewer (role)   | Evidence                                                    |
| -------- | -------- | ---------- | ----------------- | ----------------------------------------------------------- |
| r1       | proposed | 2026-10-20 | network architect | rows from the DES-012 r1 target                             |
| r2       | reviewed | 2026-10-29 | systems architect | added SRG-identity, CF-05 and A-07; FM-08 linked to PIR-005 |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
