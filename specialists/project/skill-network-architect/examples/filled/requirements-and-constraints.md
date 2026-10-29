---
Title: site-a WAN requirements and constraints (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/requirements-and-constraints.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Measurable requirements, quality scenarios, constraints and open assumptions behind DES-012, the site-a WAN redesign, each with unit, window,
  method, owner and evidence label. All site facts are fictional.
---

# site-a hub-routed services requirements and constraints

Fills template: [templates/requirements-and-constraints.md](../../templates/requirements-and-constraints.md).

- Fictional operator "Example Remote Networks" (ERN). Owner-decided targets are USER_STATED; measured baselines are fictional and therefore also USER_STATED.
- Used by [DES-012](design.md), [ADR-0007](decision-record.md) and the [test plan](test-and-acceptance-plan.md).

## Contents

- [How to use](#how-to-use)
- [1. Stakeholders and services](#1-stakeholders-and-services)
- [2. Requirements](#2-requirements)
- [3. Quality scenarios](#3-quality-scenarios)
- [4. Constraints](#4-constraints)
- [5. Assumptions and open questions](#5-assumptions-and-open-questions)
- [6. Review state](#6-review-state)

## How to use

How this example applied the template's rules:

- Filled on 2026-10-06, before any option was drawn in DES-012.
- REQ-01 was derived from the consequence column, not copied: about 12 bookings move per hour of outage and the clinic accepts roughly half a working day per month (216 min per 30 days).
- Kind: "business" = the owner decided it; "baseline" = observed now; "assumption" = to be confirmed.

## 1. Stakeholders and services

| Service                     | Users and count                  | Critical journey                        | Consequence of failure (per hour)                     | Service owner         | Ops owner |
| --------------------------- | -------------------------------- | --------------------------------------- | ----------------------------------------------------- | --------------------- | --------- |
| clinic booking (SaaS        | clinic staff, 9 at peak          | look up and book an appointment         | about 12 appointments rescheduled by phone            | clinic                | NOC lead  |
|   via hub-1)                |                                  |                                         |                                                       |   services manager    |           |
| voice (hosted PBX           | staff handsets 4, after-hours    | inbound call from a patient or          | missed urgent calls; after-hours line diverted to     | clinic                | NOC lead  |
|   via hub-1)                |   line 1                         |   the ambulance                         |   a mobile                                            |   services manager    |           |
| pump telemetry (to hub-1)   | 1 pump station, 12 sensors       | low-level alarm reaches the             | no alarm; a dry pump can burn out within about 2 h    | water services lead   | NOC lead  |
|                             |                                  |   duty operator                         |                                                       |                       |           |
| guest Wi-Fi                 | visitors, up to 60               | internet access in the waiting room     | inconvenience only                                    | clinic                | NOC lead  |
|   (local breakout)          |                                  |                                         |                                                       |   services manager    |           |

All values USER_STATED (service owners, 2026-10-06).

## 2. Requirements

| ID     | Service          | Category       | Requirement                       | Target and unit         | Window     | Measurement method              | Kind     | Owner            | Source label |
| ------ | ---------------- | -------------- | --------------------------------- | ----------------------- | ---------- | ------------------------------- | -------- | ---------------- | ------------ |
| REQ-01 | hub-routed       | availability   | reachable from site-a             | >= 99.5% of             | 30         | HTTPS probe from site-a mgmt    | business | clinic           | USER_STATED  |
|        |   service        |                |                                   |   5-min probes          |   d        |   host to hub-1 VIP             |          |   svc manager    |              |
|        |                  |                |                                   |                         |   rolling  |                                 |          |                  |              |
| REQ-02 | hub-routed       | failover       | service back after loss of        | <= 60 s, no             | per event  | 1-s external probe + tunnel     | business | NOC lead         | USER_STATED  |
|        |   service        |                |   one WAN                         |   person acting         |            |   state log                     |          |                  |              |
| REQ-03 | voice            | latency        | round trip site-a to hub-1        | p95 <= 150 ms on        | busy hour  | probe RTT, 1-min samples        | business | NOC lead         | USER_STATED  |
|        |                  |                |                                   |   either WAN            |            |                                 |          |                  |              |
| REQ-04 | hub-routed       | throughput     | sustained per site                | >= 22 Mbit/s on         | busy hour  | tunnel interface                | baseline | NOC lead         | USER_STATED  |
|        |   service        |                |                                   |   satellite; >= 10      |            |   counters, 5-min               |          |                  |              |
|        |                  |                |                                   |   Mbit/s on LTE with    |            |                                 |          |                  |              |
|        |                  |                |                                   |   voice priority        |            |                                 |          |                  |              |
| REQ-05 | all              | security       | no guest-to-corp and no           | 0 permitted flows       | continuous | policy test + site box deny     | business | network          | USER_STATED  |
|        |                  |                |   user-to-mgmt flows              |                         |            |   log review                    |          |   architect      |              |
| REQ-06 | management       | operability    | on-call reaches the site box,     | drill passes            | quarterly  | drill record                    | business | NOC lead         | USER_STATED  |
|        |                  |                |   satellite down                  |                         |            |                                 |          |                  |              |
| REQ-07 | site equipment   | lifecycle      | supported firmware and            | 0 EOL components        | monthly    | lifecycle register              | business | NOC lead         | USER_STATED  |
|        |                  |                |   hardware only                   |                         |            |                                 |          |                  |              |
| REQ-08 | LTE backup       | cost           | data use in a month without       | <= 50 GB per site       | monthly    | carrier usage report            | business | clinic           | USER_STATED  |
|        |                  |                |   satellite outage                |                         |            |                                 |          |   svc manager    |              |
| REQ-09 | site power       | recoverability | equipment rides through a         | >= 30 min at full load  | per event  | UPS self-test runtime +         | business | field technician | USER_STATED  |
|        |                  |                |   mains outage                    |                         |            |   load reading                  |          |                  |              |

Baselines measured 2026-10-06 (USER_STATED): probe success 98.8% over 30 days; satellite RTT p95 62 ms; busy-hour demand 22 Mbit/s (18 down, 4 up).

## 3. Quality scenarios

| Scenario | Source and stimulus                                 | Environment   | Expected response                                   | Response measure                                | REQ         |
| -------- | --------------------------------------------------- | ------------- | --------------------------------------------------- | ----------------------------------------------- | ----------- |
| QS-01    | satellite service lost (terminal unpowered)         | busy hour     | traffic moves to the LTE tunnel                     | service loss <= 60 s; active calls survive      | REQ-02,     |
|          |                                                     |               |                                                     |   or redial                                     |   REQ-03    |
| QS-02    | hub-gw-1 rebooted                                   | normal load   | site traffic moves to the LTE tunnel on hub-gw-2    | service loss <= 60 s                            | REQ-02      |
| QS-03    | 1360-byte packet with DF set while on LTE           | after CHG-031 | delivered without fragmentation                     | 100 of 100 probes answered                      | REQ-01      |
| QS-04    | guest client opens a connection to                  | any           | refused at the site box and logged                  | 0 connections, 1 deny log line per attempt      | REQ-05      |
|          |   10.80.0.65 (mgmt)                                 |               |                                                     |                                                 |             |
| QS-05    | on-call engineer must log in with satellite down    | out of hours  | login through the LTE tunnel, or the OOB device     | prompt reached within 120 s                     | REQ-06      |
|          |                                                     |               |   if not                                            |                                                 |             |

## 4. Constraints

| ID     | Constraint                                            | Type        | Fixed or negotiable | Source and label                  | Effect on design                                   |
| ------ | ----------------------------------------------------- | ----------- | ------------------- | --------------------------------- | -------------------------------------------------- |
| CON-01 | LTE plan 50 GB per site per month                     | commercial  | negotiable (cost)   | carrier contract, USER_STATED     | LTE is standby only; bulk best effort on failover  |
| CON-02 | site box has two WAN ports                            | physical    | fixed (hardware)    | skill-smc to confirm, USER_STATED | no third WAN without a new box                     |
| CON-03 | change window Tuesday 22:00-02:00 local               | operational | negotiable          | operations manager, USER_STATED   | fleet changes in 4-hour windows                    |
| CON-04 | radio and LTE equipment within the regulator's limits | legal       | fixed               | regulator instrument, UNVERIFIED  | PtP EIRP to be confirmed before survey sign-off    |
| CON-05 | one network on-call engineer; field visit 6 h travel  | people      | fixed this year     | operations manager, USER_STATED   | failover must be automatic; spares held regionally |

## 5. Assumptions and open questions

| ID     | Assumption or question                                | Why it matters                             | How to confirm                            | Owner           | Due        | Label       |
| ------ | ----------------------------------------------------- | ------------------------------------------ | ----------------------------------------- | --------------- | ---------- | ----------- |
| ASM-01 | LTE underlay MTU is 1428 bytes                        | sets the tunnel MTU (CHG-031)              | DF probe ladder on the LTE port           | field           | 2026-11-04 | USER_STATED |
|        |                                                       |                                            |                                           |   technician    |            |             |
| ASM-02 | LTE tower and satellite terminal do not share a       | shared power turns parallel paths into     | carrier tower record; terminal            | field           | 2026-11-11 | UNVERIFIED  |
|        |   power source                                        |   one block                                |   feed survey                             |   technician    |            |             |
| ASM-03 | standby keepalives and probes use under 2 GB          | REQ-08 budget                              | 7-day usage on the canary SIM, scaled to  | NOC lead        | 2026-11-25 | UNVERIFIED  |
|        |   per month                                           |                                            |   30 days                                 |                 |            |             |
| ASM-04 | the hosted PBX tolerates a 30-60 s path change        | REQ-03 call survival                       | T-02 with a live test call                | NOC lead        | 2026-11-18 | UNVERIFIED  |

## 6. Review state

| Revision | State    | Date       | Reviewer (role)         | Evidence or reason                  |
| -------- | -------- | ---------- | ----------------------- | ----------------------------------- |
| r1       | proposed | 2026-10-06 | network architect       | first draft from owner interviews   |
| r1       | reviewed | 2026-10-13 | clinic services manager | REQ-01 and REQ-08 targets confirmed |
| r1       | accepted | 2026-10-29 | operations manager      | accepted with DES-012 r2            |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
