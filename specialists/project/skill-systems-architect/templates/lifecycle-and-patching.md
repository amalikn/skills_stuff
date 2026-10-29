---
Title: Lifecycle and patching template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: End-of-life tracking, patch rings with soak and stop rules, maintenance windows, emergency patch path and compliance measurement for a platform estate.
---

# <estate> lifecycle and patching

Based on: NIST SP 800-40 Rev. 4, Guide to Enterprise Patch Management Planning (https://csrc.nist.gov/pubs/sp/800/40/r4/final).

## How to use

- Track every platform (firmware, OS, hypervisor, application, controller) against vendor support dates from primary sources. Record the date checked.
- Roll patches through rings. Each ring soaks and passes its checks before the next starts.
- Treat a fleet-wide patch as a change: method of procedure, canary, stop rules.
- Measure compliance per class: targets on a supported, current-ring version / total targets. Name the population source.

```text
Patch rings: each gate passes before the next ring starts

  +--------+  soak  +----------+  soak  +---------+  soak  +----------+
  | 0 lab  |--gate->| 1 canary |--gate->| 2 early |--gate->| 3 broad  |
  +--------+   |    +----------+   |    +---------+   |    +----------+
               X                   X                  X
          stop rule hit: halt, roll back the ring, record the finding
  Legend: --gate-> exit checks passed   X stop condition
```

## 1. Lifecycle register

| Component class   | Model / product | Running versions (count each) | Vendor support end (security) | Source and date checked | Replacement plan | Owner | Label            |
| ----------------- | --------------- | ----------------------------- | ----------------------------- | ----------------------- | ---------------- | ----- | ---------------- |
| <hypervisor>      |                 | <ver>: <n>                    | <YYYY-MM-DD>                  | <vendor page>, <date>   |                  |       | VERIFIED_PRIMARY |
| <switch firmware> |                 |                               |                               |                         |                  |       |                  |
| <endpoint OS>     |                 |                               |                               |                         |                  |       |                  |

Trigger to plan replacement: *support end within <n> months, or no fix for a known exploited vulnerability.*

## 2. Patch rings

| Ring     | Population (selector, count)            | Purpose       | Starts after    | Soak  | Exit checks                            | Stop conditions            |
| -------- | --------------------------------------- | ------------- | --------------- | ----- | -------------------------------------- | -------------------------- |
| 0 lab    | <n>                                     | function test | release + <n> d | <n> h | user-outcome tests pass                | any regression             |
| 1 canary | <n>, representative of models and roles | real load     | ring 0 pass     | <n> d | no new alarms, metrics within baseline | failure on > <n> target(s) |
| 2 early  | <n>%                                    | breadth       | ring 1 pass     | <n> d |                                        |                            |
| 3 broad  | remainder, batches of <n>               | completion    | ring 2 pass     |       |                                        |                            |

Excluded or pinned targets: *with reason, owner and review date.*

## 3. Maintenance windows

| Class / site group | Window (day, time, TZ) | Max duration | Max concurrent targets | User notice | Approver |
| ------------------ | ---------------------- | ------------ | ---------------------- | ----------- | -------- |
|                    |                        |              |                        |             |          |

## 4. Emergency patching

| Item                                          | Value                                                                      |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| Trigger                                       | *vendor critical advisory, known exploited vulnerability, active incident* |
| Shortened rings and soak                      | *e.g. lab 2 h, canary 4 h, then batches*                                   |
| Decision owner and record                     |                                                                            |
| Compensating controls if patch is unavailable |                                                                            |

## 5. Rollback and recovery

| Platform | Rollback method (snapshot, dual image, package downgrade) | Downgrade blocked? | Time per target | Tested on |
| -------- | --------------------------------------------------------- | ------------------ | --------------- | --------- |
|          |                                                           |                    |                 |           |

## 6. Compliance measurement

| Class | Population source | Targets | On supported version | On current ring version | Compliance % | Measured     |
| ----- | ----------------- | ------- | -------------------- | ----------------------- | ------------ | ------------ |
|       |                   |         |                      |                         |              | <YYYY-MM-DD> |

## 7. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
