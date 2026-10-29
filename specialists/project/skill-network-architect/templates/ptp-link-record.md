---
Title: Point-to-point radio link record template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: >-
  Per-link record for a point-to-point radio: path profile, predicted (just link-budget) versus measured RSL, SNR and MCS, fade margin, alignment,
  grounding, regulatory class and acceptance.
---

# <link-id> point-to-point link record

Based on (checked 2026-10-29):

- ITU-R [P.530](https://www.itu.int/rec/R-REC-P.530/en) (clearance, fade, availability) and [P.525](https://www.itu.int/rec/R-REC-P.525/en) (free-space loss).
- The pack model [link_budget.py](../scripts/link_budget.py), which implements those two.
- Australian classes: [LIPD Class Licence 2025](https://www.legislation.gov.au/F2025L01047/asmade/2025-09-05/text/original/pdf) Schedule 1 Table 8.

## Contents

- [How to use](#how-to-use)
- [1. Link identity](#1-link-identity)
- [2. Path profile](#2-path-profile)
- [3. Regulatory class](#3-regulatory-class)
- [4. Predicted versus measured](#4-predicted-versus-measured)
- [5. Capacity per direction](#5-capacity-per-direction)
- [6. Installation record](#6-installation-record)
- [7. Acceptance](#7-acceptance)
- [8. Review state](#8-review-state)

## How to use

- One record per link, kept for its life; re-measure after any change to antennas, firmware, channel or the path (growth, new buildings).
- Predict with `just link-budget <file>` (input shape: `examples/link-budget.json`); paste exit code, FSPL, RSL, margin and clearance.
- The model is free space plus earth bulge only (no rain, multipath, diffraction or EIRP check). Rain and multipath allowances come from P.530 or the vendor planning tool; say which.
- State fade margin against the sensitivity of the MCS the service needs, not the lowest MCS.
- Method and worked example: [wireless-and-radio](../references/wireless-and-radio.md#usable-throughput-from-phy-rate).
- Device facts (sensitivity per MCS, capacity tables, sync, firmware): skill-cambium or the vendor's version-matched datasheet, labelled.
- Accept on measured values both ends, under load, and over a weather cycle where rain or ducting matters.

```text
Link geometry (fill in; X marks any obstruction inside 60% of F1)
 site A                                                              site B
 [ant h_A m]                                                         [ant h_B m]
     |\                                                                 /|
     | \______________ line of sight, d = <n> km _____________________/  |
     |      .  .  first Fresnel zone F1 (radius <n> m at midpoint) .  .  |
     |                    X <obstacle, d1 = <n> km, <n> m below LOS>      |
 ground <n> m AMSL     earth bulge at k = 4/3: <n> m             ground <n> m AMSL
```

## 1. Link identity

| Field                                | Value                                  | Label |
| ------------------------------------ | -------------------------------------- | ----- |
| Link ID / service carried            | <link-id> / <service, REQ IDs>         |       |
| End A / End B (site, structure)      |                                        |       |
| Radio model / firmware (both ends)   |                                        |       |
| Antenna model / gain (dBi) both ends |                                        |       |
| Frequency / channel width            | <n> MHz / <n> MHz                      |       |
| TDD ratio / sync source              | <75/25, 50/50, flexible> / <GPS, none> |       |
| Availability target                  | <n>% (<n> min/year)                    |       |

## 2. Path profile

| Item                                        | Value                | Source (map, survey, lidar) |
| ------------------------------------------- | -------------------- | --------------------------- |
| Distance                                    | <n> km               |                             |
| Ground elevation A / B                      | <n> / <n> m AMSL     |                             |
| Antenna height above ground A / B           | <n> / <n> m          |                             |
| Highest obstacle: distance from A, height   | <n> km, <n> m        |                             |
| Clearance at obstacle / F1 radius / % of F1 | <n> m / <n> m / <n>% |                             |
| Clearance rule applied                      | >= 60% F1 (P.530)    |                             |
| Climate notes (rain zone, water, ducting)   |                      |                             |

## 3. Regulatory class

| Field                                     | Value                                                                   | Label |
| ----------------------------------------- | ----------------------------------------------------------------------- | ----- |
| Authorisation                             | Class licence (LIPD 2025 Table 8 item <n>) / apparatus licence <number> |       |
| Band limits (EIRP, PSD, indoor-only, DFS) | *copy from the instrument item and clause*                              |       |
| Planned EIRP (Tx power + gain - losses)   | <n> dBm vs limit <n> dBm                                                |       |
| DFS channel?                              | *yes: CAC and radar moves logged / no*                                  |       |
| Interference protection needed?           | *yes: apparatus licence; a class licence gives none*                    |       |

## 4. Predicted versus measured

| Quantity                  | Predicted (`just link-budget`) | Measured end A | Measured end B | Difference | Within tolerance? |
| ------------------------- | ------------------------------ | -------------- | -------------- | ---------- | ----------------- |
| FSPL                      | <n> dB                         | n/a            | n/a            |            |                   |
| RSL                       | <n> dBm                        | <n> dBm        | <n> dBm        | <n> dB     |                   |
| SNR / CINR                | n/a or vendor tool             | <n> dB         | <n> dB         |            |                   |
| MCS (DL / UL)             | <MCS> at clear sky             |                |                |            |                   |
| Fade margin to needed MCS | <n> dB                         | <n> dB         | <n> dB         |            |                   |
| Fade margin to lowest MCS | <n> dB                         |                |                |            |                   |
| Model exit code           | 0 / 1                          | n/a            | n/a            |            |                   |

Tolerance: *state it before measuring (for example within a few dB of predicted RSL); a larger gap means misalignment, obstruction or a wrong input.*

## 5. Capacity per direction

| State       | RSL (dBm) | MCS | Aggregate (vendor table) | Downlink | Uplink | Needed DL / UL | Meets? |
| ----------- | --------- | --- | ------------------------ | -------- | ------ | -------------- | ------ |
| Clear sky   |           |     |                          |          |        |                |        |
| Design fade |           |     |                          |          |        |                |        |

## 6. Installation record

| Item                                      | End A | End B | Evidence (photo, report) |
| ----------------------------------------- | ----- | ----- | ------------------------ |
| Azimuth / tilt set                        |       |       |                          |
| Alignment method and final RSL            |       |       |                          |
| Polarisation                              |       |       |                          |
| Mount and structure loading checked       |       |       |                          |
| Earthing and bonding to building earth    |       |       |                          |
| Surge protection at cable entry           |       |       |                          |
| Drip loops, weatherproofing, cable labels |       |       |                          |
| Power source (PoE injector, UPS feed)     |       |       |                          |
| Config backup taken                       |       |       |                          |

## 7. Acceptance

| Test                                | Method                                       | Expected                           | Result | Pass |
| ----------------------------------- | -------------------------------------------- | ---------------------------------- | ------ | ---- |
| RSL both ends vs prediction         | Read from both radios                        | Within the stated tolerance        |        |      |
| Throughput per direction under load | Traffic test through the link (not on-radio) | >= needed DL / UL                  |        |      |
| Stability                           | <n> h soak; errors, MCS changes, drops       | No drops; MCS within plan          |        |      |
| Fade behaviour                      | Over a weather cycle where relevant          | Needed MCS held at design fade     |        |      |
| Monitoring                          | RSL, SNR, MCS, link state alerting           | Alerts reach the owner             |        |      |
| DFS event (if DFS channel)          | Check logs after a radar move or simulate    | Logged; service impact as designed |        |      |

## 8. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
