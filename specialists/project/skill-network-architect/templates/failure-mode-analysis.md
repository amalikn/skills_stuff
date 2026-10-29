---
Title: Failure mode analysis template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: FMEA-style table per component with detection, effect, blast radius, recovery and test, plus shared-risk groups and correlated failure scenarios.
---

# <scope> failure mode analysis

Worked example: `skill-network-architect/examples/filled/failure-mode-analysis.md` (filled for a fictional remote-site operator; lives in the network pack only).

Based on: Failure Mode and Effects Analysis as described by ASQ (https://asq.org/quality-resources/fmea). Adapted: adds blast radius, shared-risk groups and a test per row.

## How to use

- List components from the design, then every plausible way each fails (dead, degraded, flapping, wrong, slow, full, expired, misconfigured, unreachable for management).
- Score Severity, Occurrence and Detection 1-10 (10 = worst: most severe, most frequent, least detectable).
- RPN = S x O x D ranks work; it is not a probability.
- Severity 9-10 regardless of RPN gets an action.
- Every row needs a test that proves detection and recovery; an untested row stays UNVERIFIED.

## 1. Components and shared-risk groups

| Shared-risk group | Members                                    | Evidence it is shared or separate | Label      |
| ----------------- | ------------------------------------------ | --------------------------------- | ---------- |
| SRG-power-A       | <devices on feed A>                        | *PDU map, site photo*             |            |
| SRG-duct-<id>     | <links in one duct or carrier>             | *carrier records, path survey*    | UNVERIFIED |
| SRG-control       | <controller, inventory, automation>        |                                   |            |
| SRG-identity      | <directory, AAA, PKI, admin accounts>      |                                   |            |
| SRG-update        | <firmware or package channel, signing key> |                                   |            |

```text
SHARED-RISK GROUPS: everything inside one :::: zone can fail together; '?' = unverified

:::: SRG-power-A :::::::::::   :::: SRG-control ::::::::::::::::::::::
: +--------+   +-------+   :   : +--------------+                    :
: | edge A |   | agg A |   :   : | <controller> |  manages all edges :
: +--------+   +-------+   :   : +--------------+                    :
::::::::::::::::::::::::::::   :::::::::::::::::::::::::::::::::::::::

:::: SRG-duct-<id> ? :::::::   :::: SRG-identity :::::::::::::::::::::
: link A, link B ? (check) :   : AAA, PKI: every admin login         :
::::::::::::::::::::::::::::   :::::::::::::::::::::::::::::::::::::::
```

## 2. Failure modes

Detection = signal, threshold and time to detect. Recovery = action and time. Test = method and date last run.

| ID | Component | Failure mode | Cause | Detection | Local effect | Service effect | Blast radius | S | O | D | RPN | Recovery | Test | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FM-01 | <primary link> | down | fibre cut / | link-down trap + probe loss 3x10 s | traffic | none if | 1 site | 6 | 4 | 2 | 48 | automatic, <n> s | pull link in | <role> |
|  |  |  |   radio fade |  |   on |   capacity |  |  |  |  |  |  |   window, <date> |  |
|  |  |  |  |  |   secondary |   holds |  |  |  |  |  |  |  |  |
| FM-02 | <primary link> | degraded | interference | *often undetected* | retransmits | slow | 1 site | 5 | 5 | 8 | 200 | manual steer, <n> min | inject loss in lab |  |
|  |  |   (loss 2%) |  |  |  |   transactions |  |  |  |  |  |  |  |  |
| FM-03 | <controller> | unreachable | host or |  | no | none | fleet |  |  |  |  |  |  |  |
|  |  |  |   path fail |  |   config |   short term |  |  |  |  |  |  |  |  |
|  |  |  |  |  |   push |  |  |  |  |  |  |  |  |  |
| FM-04 | <certificate | expired | missed |  |  |  |  |  |  |  |  |  |  |  |
|  |   / licence> |  |   renewal |  |  |  |  |  |  |  |  |  |  |  |

## 3. Correlated failure scenarios

| Scenario | Shared-risk group lost | Components lost together | Remaining capacity vs demand | Service result           | Recovery path still available? | Test |
| -------- | ---------------------- | ------------------------ | ---------------------------- | ------------------------ | ------------------------------ | ---- |
| CF-01    | SRG-power-A            | edge A, agg A            | <n> of <n> Mbit/s            |                          | *is OOB on feed A too?*        |      |
| CF-02    | SRG-identity           | admin login everywhere   | n/a                          | service up, unmanageable | *break-glass account path*     |      |
| CF-03    | SRG-update             | bad firmware to a batch  |                              |                          | *rollback image held locally?* |      |

## 4. Actions

| Action | Rows addressed | Expected change (S/O/D, or recovery time) | Owner | Due | Status |
| ------ | -------------- | ------------------------ | ----- | --- | ------ |
|        | FM-02          | D 8 -> 3 (loss alert)    |       |     |        |

## 5. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
