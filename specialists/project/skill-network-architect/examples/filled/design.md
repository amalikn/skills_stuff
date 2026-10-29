---
Title: site-a WAN redesign (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/design.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  DES-012: one satellite-connected remote site moves from a single satellite path and one hub concentrator to satellite plus LTE failover over two
  WireGuard tunnels to two hub concentrators; `just availability` compares current and target. All site facts are fictional.
---

# site-a WAN architecture design

Fills template: [templates/design.md](../../templates/design.md).

- Fictional operator "Example Remote Networks" (ERN). Every ERN fact below is invented and therefore labelled USER_STATED.
- Helper results are static (model) evidence on those inputs.
- Companion examples: [requirements](requirements-and-constraints.md), [decision record](decision-record.md), [site build sheet](site-network-design.md).
- Also: [failure modes](failure-mode-analysis.md), [tests](test-and-acceptance-plan.md), [MTU change](change-and-validation.md).

## Contents

- [How to use](#how-to-use)
- [1. Decision and outcome](#1-decision-and-outcome)
- [2. Requirements and constraints](#2-requirements-and-constraints)
- [3. Context and current state](#3-context-and-current-state)
- [4. Target state](#4-target-state)
- [5. Failure domains and trust zones](#5-failure-domains-and-trust-zones)
- [6. Interfaces, options and decisions](#6-interfaces-options-and-decisions)
- [7. Capacity, risk and recovery](#7-capacity-risk-and-recovery)
- [8. Implementation, acceptance and operations](#8-implementation-acceptance-and-operations)
- [9. Review state](#9-review-state)

## How to use

How this example applied the template's rules:

- The decision changes failure behaviour and cost across the site box, two WAN services and two hub concentrators, so it is a design, not an ADR alone. The option choice itself is ADR-0007.
- Sections 1-3 were filled before the target was drawn. The one UNVERIFIED fact that could change the decision (does the LTE tower share power with the satellite gateway region?) has a test in section
  3.

## 1. Decision and outcome

| Field                        | Value                                                                                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Design ID / revision         | DES-012 / r2                                                                                                                       |
| Decision requested           | Approve the site-a WAN target (satellite primary, LTE failover, two hub concentrators) by the operations manager by 2026-11-14.    |
| Service outcome              | site-a staff keep clinic booking, voice and pump telemetry through loss of the satellite service or of one hub concentrator.       |
| Service owner / design owner | clinic services manager / network architect                                                                                        |
| Peer reviewers               | network: NOC lead; systems: systems architect (hub-1 concentrators, RADIUS); specialists: skill-smc, skill-mikrotik, skill-cambium |
| Out of scope                 | hub-1 cluster rebuild (DES-014); the 16 sites without LTE coverage; guest Wi-Fi (local satellite breakout, unchanged); site power  |

## 2. Requirements and constraints

Summary; the full table is in [requirements-and-constraints.md](requirements-and-constraints.md).

| ID     | Service            | Requirement  | Target and unit                                  | Window    | Measurement method                       | Owner                   | Source label |
| ------ | ------------------ | ------------ | ------------------------------------------------ | --------- | ---------------------------------------- | ----------------------- | ------------ |
| REQ-01 | hub-routed service | Availability | >= 99.5% of 5-minute probes succeed              | 30 days   | probe from site-a mgmt host to hub-1 VIP | clinic services manager | USER_STATED  |
| REQ-02 | hub-routed service | Failover     | service back within 60 s of WAN loss             | per event | external probe + tunnel state log        | NOC lead                | USER_STATED  |
| REQ-03 | voice              | Latency      | RTT p95 <= 150 ms site-a to hub-1                | busy hour | probe RTT, 1-minute samples              | NOC lead                | USER_STATED  |
| REQ-06 | management         | Operability  | on-call reaches the site box with satellite down | quarterly | drill record                             | NOC lead                | USER_STATED  |

Constraints: LTE data budget 50 GB per site per month in normal operation (CON-01, USER_STATED, carrier plan); site box has two WAN ports only (CON-02, USER_STATED, skill-smc to confirm); one change
window per week, Tuesday 22:00-02:00 local (CON-03, USER_STATED); one network on-call engineer (CON-05, USER_STATED).

## 3. Context and current state

```text
CONTEXT: who uses hub-routed services at site-a and what they depend on (arrow = depends on)

+-------------------------+   +-------------------------+   +--------------------------------+
| site-a staff, phones,   |-->| hub-routed services     |-->| hub-1: DNS, RADIUS, PBX trunk, |
| pump telemetry          |   | (booking SaaS via hub   |   | internet breakout, hub-gw-1/2  |
+-------------------------+   | breakout, voice, telem) |   +--------------------------------+
                              +-------------------------+
                                          ^
                                          | manages, via the management plane
                              +-------------------------+   +-------------------------------+
                              | NOC on-call engineer    |-->| Nautobot, OpenWISP, Grafana   |
                              +-------------------------+   | on the hub-1 Proxmox cluster  |
                                                            +-------------------------------+
```

```text
CURRENT (observed 2026-10-06, source: site survey and site box tunnel table, USER_STATED)

+---------------+  A   +-------------------+  WG   +-----------+   +-------------------+
| site-a box    |----->| SAT-1 LEO service |------>| hub-gw-1  |-->| hub-1 services    |
| (rev-A)       |      | CGNAT, MTU 1500   |       | (single)  |   | and breakout      |
+---------------+      +-------------------+       +-----------+   +-------------------+
        |
        |  B ?   +---------------------------+
        +------->| MNO-1 LTE router, cabled, |   not used for tunnels; SIM status UNKNOWN
                 +---------------------------+

Legend: A = satellite, 100/15 Mbit/s plan (USER_STATED); B ? = LTE router on site, idle, UNKNOWN state
```

| Unknown                                                    | Why it matters                                 | Discriminating test                                    | Owner            | Due        |
| ---------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------ | ---------------- | ---------- |
| Is the LTE SIM active and is the data plan the 50 GB one?  | LTE failover is useless on a suspended SIM     | carrier portal read for the SIM; one 10 MB transfer    | NOC lead         | 2026-11-04 |
|                                                            |                                                |   on LTE                                               |                  |            |
| What is the LTE underlay MTU?                              | sets the tunnel MTU (CHG-031)                  | DF probe ladder on the LTE WAN port to 203.0.113.10    | field technician | 2026-11-04 |
| Do the LTE tower and the satellite terminal share          | a shared power block removes the               | carrier tower record; site survey of the terminal feed | field technician | 2026-11-11 |
|   site-a mains?                                            |   parallel benefit                             |                                                        |                  |            |

Current-state availability (static model, inputs USER_STATED: satellite 0.99 from 90 days of probe history, other blocks from the operator's fault log):

```text
$ just availability examples/filled/design-current.json        # exit 1
  "availability": 0.987527227,
  "downtime_minutes_per_year": 6560.18,
  "target": 0.995,
  "findings": ["composite availability 0.987527 misses target 0.995"]
```

0.987527 is (1 - 0.987527) x 43,200 min = 538.8 min of probe failure per 30 days against the 216.0 min that REQ-01 allows. Measured probe success over the last 30 days was 98.8% (USER_STATED, Grafana
panel export), consistent with the model.

## 4. Target state

Planned unless marked otherwise.

```text
TARGET (planned): two WAN services, two tunnels, two concentrators; OOB on a separate path

                       +-------------------+  WG wg-sat (10.10.200.0/31)   +----------+
                  +--->| SAT-1 LEO service |------------------------------>| hub-gw-1 |---+
+------------+    |    +-------------------+                               +----------+   |   +-----------+
| site-a box |----+                                                                       +-->| hub-1     |
| (rev-A)    |----+                                                                       |   | services  |
+------------+    |    +-------------------+  WG wg-lte (10.10.201.0/31)   +----------+   |   +-----------+
      |           +--->| MNO-1 LTE service |------------------------------>| hub-gw-2 |---+
      |                +-------------------+                               +----------+
      |  trunk
+------------------+   +------------------------+
| MikroTik switch  |-->| APs, phones, PtP radio |
+------------------+   +------------------------+

+--------------------+   +-------------------+   +-----------------+
| OOB console device |-->| MNO-1, own SIM,   |-->| hub-1 mgmt net  |   independent of the site box
+--------------------+   | not via site box  |   +-----------------+
```

- Tunnel preference: wg-sat carries traffic while its probe passes; wg-lte is up and probed continuously (keepalive 25 s) so a dead standby path is detected before it is needed.
- Failover trigger: 3 consecutive probe losses at 10 s spacing on wg-sat (30 s), then route preference moves to wg-lte; failback after 5 minutes of clean probes (hold-down against flapping).
- Each tunnel lands on a different concentrator, so one concentrator loss is the same event as one WAN loss.
- Tunnel interface MTU 1360 on both tunnels (CHG-031; `just mtu` results in [site-network-design.md](site-network-design.md#4-mtu-budget)).

Target availability (static model, same USER_STATED inputs plus LTE 0.97 from the carrier coverage report and the 30-day LTE probe at the neighbouring site-b):

```text
$ just availability examples/filled/design.json                # exit 0
  "availability": 0.998200201,
  "downtime_minutes_per_year": 946.62,
  "target": 0.995,
  "status": "pass"
```

0.998200 is 77.8 min per 30 days against 216.0 min allowed. The model assumes independent failures; the shared-risk groups in section 5 are where that assumption can break.

## 5. Failure domains and trust zones

```text
FAILURE DOMAINS: members of a :::: zone fail together; '?' = shared risk not verified

:::: site-a mains + UPS ::::::::::::::::::::::   :::: MNO-1 carrier ::::::::::::::::
: +------------+ +----------+ +-------------+ :   : LTE service, OOB console modem :
: | site box   | | switch   | | sat terminal| :   : (no third carrier at site-a)   :
: +------------+ +----------+ +-------------+ :   ::::::::::::::::::::::::::::::::::
: LTE router ?  (same UPS: verify)            :
:::::::::::::::::::::::::::::::::::::::::::::::   :::: hub-1 uplink duct :::::::::::::
                                                  : both hub internet uplinks, all :
:::: hub-1 rack-a :::::   :::: hub-1 rack-b ::::  : 40 sites (capacity model)      :
: hub-gw-1            :   : hub-gw-2          :   ::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::   :::::::::::::::::::::

Shared by both WAN paths: site box, site mains and UPS, hub-1 uplink duct, RADIUS on hub-1, firmware channel
```

```text
TRUST ZONES: each ==== line is an enforcement point and states its rule

+------------------------------------------+
| untrusted: SAT-1 and MNO-1 underlay      |
+------------------------------------------+
==== site box WAN policy: only UDP to 203.0.113.10/11 WireGuard; logged to Loki ====
+------------------------------------------+
| guest zone (VRF guest-site-a)            |   local NAT to satellite; no route to corp
+------------------------------------------+
==== site box zone policy: guest -> corp denied; user -> mgmt denied ================
+------------------------------------------+
| user, voice and IoT zones (VRF corp)     |   to hub-1 over the tunnels only
+------------------------------------------+
==== management policy: mgmt -> all (SSH, HTTPS, SNMP); others -> mgmt denied =======
+------------------------------------------+
| management zone (VLAN 10)                |
+------------------------------------------+
```

Correlated failures and their effect (full analysis in [failure-mode-analysis.md](failure-mode-analysis.md)):

- site mains beyond UPS runtime: everything at site-a stops; no design in scope changes this (CF-01).
- MNO-1 outage while the satellite is down: no WAN and no OOB. No third carrier reaches site-a, so the OOB shares a carrier with one WAN in every option; it is kept on MNO-1 with its own SIM, which
  covers site-box failure and satellite loss. Accepted (CF-02).
- hub-1 uplink duct cut: every site loses hub-routed service; guest Wi-Fi survives on local breakout (CF-03; owned by the capacity model risk, outside this design).

## 6. Interfaces, options and decisions

- Interfaces: IF-004 site-to-hub tunnel (tunnel MTU 1360, keepalive 25 s, /31 addressing from the hub pools). Authoritative writer of tunnel keys and addresses: Nautobot intent pushed by the
  `tunnel-provision` job; the site box never edits its own tunnel table.
- Options compared (detail and arithmetic in [ADR-0007](decision-record.md)):

| Option                     | Meets REQ                         | Failure coverage                         | Operating cost / staff effort          | Exit cost | Verdict and ADR   |
| -------------------------- | --------------------------------- | ---------------------------------------- | -------------------------------------- | --------- | ----------------- |
| A satellite only (current) | REQ-01 no (0.987527), REQ-02 no   | single path, single concentrator         | lowest                                 | none      | rejected ADR-0007 |
| B satellite + LTE failover | REQ-01 yes (0.998200), REQ-02 yes | either WAN, either concentrator          | SIM per site, 50 GB plan, probe tuning | low       | chosen ADR-0007   |
| C two satellite terminals  | REQ-01 no (0.990508), REQ-02 yes  | terminal loss only; SAT-1 network shared | second terminal, second subscription   | medium    | rejected ADR-0007 |

## 7. Capacity, risk and recovery

- Capacity: site-a busy-hour demand 22 Mbit/s (18 down, 4 up; USER_STATED, 30-day tunnel counters). Satellite plan 100/15 Mbit/s holds it. On LTE (30/10 Mbit/s, USER_STATED) demand fits but leaves 8
  Mbit/s down; voice and telemetry get priority by QoS, bulk data is best effort (accepted in REQ-04). Hub-side capacity: the hub-1 capacity model (systems pack).
- Risks (owner): LTE standby fails silently (NOC lead, mitigated by continuous probing); LTE data budget exhausted during a long satellite outage (clinic services manager, alert at 80% of 50 GB); fade
  margin of the clinic PtP link is 0.27 dB above requirement (network architect, see site sheet).
- Recovery: bootstrap order site box -> wg-sat -> wg-lte -> switch -> APs. Independent access: OOB console device on its own MNO-1 SIM, not through the site box. Tunnel private keys live only on the
  device and in the secret store used by `tunnel-provision`; none appear in this design. Config backup nightly to hub-1 by Nautobot Golden Config (owner: NOC lead).

## 8. Implementation, acceptance and operations

| Wave     | Scope                              | Entry criteria                             | Acceptance test (REQ)                         | Rollback trigger                     | Owner            |
| -------- | ---------------------------------- | ------------------------------------------ | --------------------------------------------- | ------------------------------------ | ---------------- |
| 0 lab    | lab site box rev-A + LTE simulator | ADR-0007 accepted; CHG-031 MTU in lab      | T-02, T-05 in lab (REQ-02, IF-004)            | any lab failure                      | network          |
|          |                                    |                                            |                                               |                                      |   architect      |
| 1 canary | site-a                             | lab pass; SIM test passed; CHG-031 done    | T-01 7 days, T-02 forced failover,            | probe success < 99% for 1 h          | NOC lead         |
|          |                                    |   at site-a                                |   T-03 (REQ-01..03)                           |   after cutover                      |                  |
| 2 fleet  | remaining 23 LTE-covered sites,    | wave 1 accepted; one rev-B site in the     | T-01 per site 7 days (REQ-01)                 | 2 sites fail T-02 in one wave        | NOC lead         |
|          |   3 waves                          |   first wave                               |                                               |                                      |                  |

Operations after go-live: tunnel and probe alerts route to the NOC on-call; runbook "site WAN failover" in the NOC wiki; failover drill quarterly per site (REQ-06); next review when LTE coverage
reaches any of the 16 satellite-only sites, or on any PIR involving a WAN path.

## 9. Review state

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded). Acceptance binds to one revision.

| Revision | State           | Date       | Reviewer (role)   | Evidence or reason                                                   |
| -------- | --------------- | ---------- | ----------------- | -------------------------------------------------------------------- |
| r1       | proposed        | 2026-10-08 | network architect | first draft, option A vs B only                                      |
| r1       | evidence-needed | 2026-10-13 | systems architect | asked for option C and for concentrator placement; LTE MTU unknown   |
| r2       | reviewed        | 2026-10-29 | NOC lead          | option C added, `just availability` runs above, MTU handled by CHG-031 |
