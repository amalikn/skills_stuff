---
Title: Capacity model template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Demand, supply and headroom per resource under normal, maintenance, largest-unit loss and correlated-domain loss, with growth horizon and triggers.
---

# <scope> capacity model

Worked example: `skill-systems-architect/examples/filled/capacity-model.md` (filled for a fictional remote-site operator; lives in the systems pack only).

## How to use

- Model each limiting resource separately (link bandwidth, airtime, PPS/sessions, CPU, memory, storage capacity and IOPS, power, PoE, rack space, licences, staff hours).
- Carry units through every number; distinguish Mbit/s from MB/s and GB from GiB.
- Use measured demand where it exists and label it; label forecasts USER_STATED or UNVERIFIED.
- Check normal, maintenance (one unit drained), largest-unit loss and correlated-domain loss.
- The worst case that must still meet the requirement sets the size.
- Offline helpers: `just availability` (both packs); network `just link-budget`, `just mtu`.
- Systems `just capacity` checks the memory pool per failure scenario and serialized restore time.

## 1. Demand

| Resource     | Population | Measured p95 | Peak / burst | Window and source            | Growth rate (per year) | Horizon | Forecast at horizon | Label            |
| ------------ | ---------- | ------------ | ------------ | ---------------------------- | ---------------------- | ------- | ------------------- | ---------------- |
| WAN per site | <n> sites  | <n> Mbit/s   | <n> Mbit/s   | busy hour, 30 d, <collector> | <n>%                   | <n> yr  | <n> Mbit/s          | VERIFIED_PRIMARY |
| Memory pool  | <cluster>  | <n> GiB      |              |                              |                        |         |                     |                  |

## 2. Supply and failure scenarios

| Resource | Unit | Units | Usable per unit (after reserve; pools: `just ceph` plan) | Normal supply | Maintenance (N-1) | Largest unit lost | Correlated domain lost (which) | Unit   |
| -------- | ---- | ----- | ------------------------------- | ------------- | ----------------- | ----------------- | ------------------------------ | ------ |
| WAN      | link | 2     | <n> Mbit/s                      | <n>           | <n>               | <n>               | duct <id>: <n>                 | Mbit/s |
| Memory   | host | <n>   | <n> GiB                         |               |                   |                   | rack <id>:                     | GiB    |

## 3. Headroom

| Resource | Scenario                | Demand | Supply | Headroom = supply - demand | Headroom % | Policy minimum | Meets? |
| -------- | ----------------------- | ------ | ------ | -------------------------- | ---------- | -------------- | ------ |
|          | normal                  |        |        |                            |            | <n>%           |        |
|          | worst required scenario |        |        |                            |            | 0%             |        |

*State which requirement allows degraded service in which scenario, e.g. "on duct loss, voice only, best-effort data".*

## 4. Limiting resource and economics

- Limiting resource now / at horizon: *...*
- Options to add capacity: *unit, lead time, cost basis (no invented prices), operational effort.*

## 5. Triggers and monitoring

| Trigger          | Measurement            | Threshold                       | Lead time needed | Action        | Owner  |
| ---------------- | ---------------------- | ------------------------------- | ---------------- | ------------- | ------ |
| *upgrade backhaul* | p95 utilisation, 7-day | > <n>% of worst-scenario supply | <n> weeks        | order upgrade | <role> |

## 6. Assumptions and review state

| ID  | Assumption | Sensitivity (what changes if wrong) | Label      |
| --- | ---------- | ----------------------------------- | ---------- |
|     |            |                                     | UNVERIFIED |

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
