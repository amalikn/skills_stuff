---
Title: ADR-0007 satellite plus LTE failover (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/decision-record.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  ADR-0007: LTE failover beside the satellite service at the 24 LTE-covered sites, compared with satellite only and with two satellite terminals;
  `just availability` gives each option's composite availability. All site facts are fictional.
---

# ADR-0007: satellite primary with LTE failover over two WireGuard tunnels

Fills template: [templates/decision-record.md](../../templates/decision-record.md).

- Fictional operator "Example Remote Networks" (ERN). Every ERN fact is invented and labelled USER_STATED; helper output is static (model) evidence on those inputs.
- Design: [DES-012](design.md). Requirements: [requirements-and-constraints.md](requirements-and-constraints.md).

## Contents

- [How to use](#how-to-use)
- [Context and problem statement](#context-and-problem-statement)
- [Decision drivers](#decision-drivers)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
- [Pros and cons of the options](#pros-and-cons-of-the-options)
- [More information](#more-information)

---

## How to use

How this example applied the template's rules: one decision (which backup WAN), one page of argument, value-neutral context, active-voice decision, bad consequences listed beside the good.

| Field                  | Value                                                                                  |
| ---------------------- | -------------------------------------------------------------------------------------- |
| Status                 | accepted                                                                               |
| Date (last updated)    | 2026-10-29                                                                             |
| Decision makers        | operations manager, network architect                                                  |
| Consulted (two-way)    | systems architect (hub-gw placement, RADIUS); skill-smc (site box WAN ports); NOC lead |
| Informed (one-way)     | clinic services manager, field technicians                                             |
| Requirements addressed | REQ-01, REQ-02, REQ-06, REQ-08                                                         |
| Related                | design DES-012, interface IF-004, change CHG-031 (tunnel MTU); supersedes none         |

## Context and problem statement

Every ERN site has one LEO satellite service and one WireGuard tunnel to one hub concentrator. At site-a the measured probe success is 98.8% over 30 days, below the 99.5% that the clinic service owner
set (REQ-01). 24 of the 40 sites have MNO-1 LTE coverage; an LTE router is already installed but unused at site-a. Which backup path, if any, should carry hub-routed traffic when the satellite path
fails, given one on-call engineer and a monthly data budget?

| Fact                                     | Value and unit                    | Source                                        | Label       | Date       |
| ---------------------------------------- | --------------------------------- | --------------------------------------------- | ----------- | ---------- |
| site-a probe success, satellite path     | 98.8% of 5-minute probes, 30 days | Grafana probe panel export                    | USER_STATED | 2026-10-06 |
| satellite service availability (model)   | 0.99                              | 90 days of probe history, ERN NOC             | USER_STATED | 2026-10-06 |
| LTE service availability (model)         | 0.97                              | 30-day probe at site-b, MNO-1 coverage report | USER_STATED | 2026-10-06 |
| SAT-1 network share of satellite outages | 0.992 network x 0.998 terminal    | ERN fault log split by cause                  | USER_STATED | 2026-10-06 |
| sites with LTE coverage                  | 24 of 40                          | MNO-1 coverage map, field survey              | USER_STATED | 2026-09-30 |
| LTE underlay MTU                         | 1428 bytes                        | MNO-1 APN sheet; DF probe pending             | USER_STATED | 2026-10-20 |

## Decision drivers

- REQ-01: at least 99.5% of 5-minute probes succeed over 30 days (216.0 min of failure allowed per 30 days).
- REQ-02: hub-routed service back within 60 s of a WAN loss, without a person acting.
- REQ-06: one on-call engineer reaches the site box during a satellite outage.
- CON-01 / REQ-08: LTE data within 50 GB per site per month in normal operation.
- Failures that share a provider network are one block in series, not two in parallel (pack rule, scripts/README.md, Availability).

## Considered options

1. A: satellite only, accept the gap (the simplest viable; current state).
2. B: satellite primary, LTE failover, one tunnel per WAN, each to a different hub concentrator.
3. C: two satellite terminals from the same provider, one tunnel each.

## Decision outcome

Chosen option: "B: satellite primary with LTE failover", because it is the only option that meets REQ-01 (model 0.998200 against 0.995) and REQ-02, at the lowest added cost of the options that reach
failover at all. It does not help the 16 sites without LTE coverage; we accept that and keep option A there until the reopen trigger below fires.

We will provision a second WireGuard tunnel over LTE to hub-gw-2 at each LTE-covered site, probe both tunnels continuously, and move route preference after 30 s of satellite probe loss.

Model runs (inputs USER_STATED, results static evidence):

```text
$ just availability examples/filled/design-current.json        # option A, exit 1
  "availability": 0.987527227, "downtime_minutes_per_year": 6560.18
  findings: composite availability 0.987527 misses target 0.995

$ just availability examples/filled/design.json                # option B, exit 0
  "availability": 0.998200201, "downtime_minutes_per_year": 946.62, "status": "pass"

$ just availability examples/filled/decision-record.json       # option C, exit 1
  "availability": 0.990507791, "downtime_minutes_per_year": 4992.52
  findings: composite availability 0.990508 misses target 0.995
```

Per 30 days (43,200 min): A 538.8 min, B 77.8 min, C 410.1 min of probe failure, against 216.0 min allowed. Option C fails because the SAT-1 network block (0.992) sits in series with both terminals: a
second terminal only removes terminal faults, which are the smaller share of satellite outages.

### Consequences

- Good, because the site keeps hub-routed service through the most common outage (satellite network or obstruction) without a site visit.
- Good, because each tunnel lands on a different concentrator, so a concentrator loss is covered by the same mechanism.
- Bad, because a silent LTE fault (suspended SIM, dead modem) would remove the backup without anyone noticing; continuous probing of the standby tunnel is now mandatory.
- Bad, because the LTE path has a smaller MTU (1428) than the satellite path; the tunnel MTU must drop fleet-wide to 1360 (CHG-031), lowering the payload ceiling on the satellite path too.
- Bad, because a long satellite outage can exhaust the 50 GB data plan; bulk traffic is best effort on LTE and an 80% usage alert is required.
- Neutral: a new runbook ("site WAN failover"), a quarterly failover drill per site, and SIM lifecycle in the lifecycle register.

### Confirmation

| Check                                | Pass criterion                                           | Falsifying observation                                           | Owner              | Due        |
| ------------------------------------ | -------------------------------------------------------- | ---------------------------------------------------------------- | ------------------ | ---------- |
| T-02 forced failover at site-a       | hub-routed probe back within 60 s, no voice call drop    | loss above 60 s, or the LTE tunnel was down when needed          | NOC lead           | 2026-11-18 |
| T-01 30-day probe success at site-a  | >= 99.5% of 5-minute probes                              | below 99.5% with both paths in service                           | NOC lead           | 2026-12-18 |
| LTE data use per site                | <= 50 GB per month without a satellite outage            | normal-month use above 50 GB (probe or keepalive cost mis-sized) | clinic svc manager | 2026-12-31 |
| Shared power check (DES-012 unknown) | LTE tower and satellite gateway region on                | both paths lost together in one power event                      | field technician   | 2026-11-11 |
|                                      |   separate supply                                        |                                                                  |                    |            |

## Pros and cons of the options

### A: satellite only

- Good, because nothing changes and nothing new can fail. Bad, because it misses REQ-01 by 322.8 min per 30 days (538.8 - 216.0) and REQ-02 entirely. Operating cost: none added. Exit cost: none.

### B: satellite + LTE failover

- Good, because it meets REQ-01 and REQ-02 and reuses the LTE router already on site. Bad, because it adds a SIM per site, a second tunnel and probe tuning, and only 24 sites qualify. Operating cost:
  one SIM and data plan per site; about 2 staff hours per site to provision and drill. Exit cost: low, remove the second tunnel and cancel the SIM.

### C: two satellite terminals

- Good, because it works at every site, including the 16 without LTE. Bad, because it misses REQ-01 (0.990508): both terminals share the SAT-1 network. Operating cost: a second terminal, mount and
  subscription per site, plus about 40 W more load on the UPS. Exit cost: medium, recover and return hardware.

## More information

- Reopen when: MNO-1 or another carrier reaches any of the 16 satellite-only sites; a second LEO provider with an independent ground network becomes available at ERN sites (re-run option C with that
  provider as a separate block); site-a probe success stays below 99.5% for 30 days with both paths in service; or LTE data use exceeds 50 GB in a month without a satellite outage.
- Evidence links and review notes per revision:

| Revision | Review state    | Date       | Reviewer (role)    | Notes                                                                 |
| -------- | --------------- | ---------- | ------------------ | --------------------------------------------------------------------- |
| r1       | proposed        | 2026-10-08 | network architect  | options A and B                                                       |
| r1       | evidence-needed | 2026-10-13 | systems architect  | add option C; split SAT-1 outages into network and terminal causes    |
| r2       | reviewed        | 2026-10-22 | NOC lead           | three `just availability` runs above                                  |
| r2       | accepted        | 2026-10-29 | operations manager | confirmation checks scheduled; CHG-031 raised for the MTU consequence |

Review states: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified; rejected and superseded keep their reasons.
