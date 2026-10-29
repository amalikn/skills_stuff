---
Title: Current-state discovery template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Evidence-led record of what exists now: sources, coverage, inventory, dependencies, diagrams, intent-versus-observation drift and unknowns.
---

# <scope> current-state discovery

## How to use

- Record only what was observed, with source, method and time.
- Keep intended or proposed state out of this document; drift goes in section 5.
- State coverage honestly: a sample is a scout, not a survey.
- List every unread target as unknown.
- Use read-only methods unless a write is separately authorized.
- Label facts VERIFIED_PRIMARY (read from the system), VERIFIED_SECONDARY (inventory, report, document), USER_STATED (told), UNVERIFIED (inferred).

## 1. Scope and method

| Field                      | Value                                                           |
| -------------------------- | --------------------------------------------------------------- |
| Population                 | <n> sites / hosts / devices, selector <query>                   |
| Collection window          | <YYYY-MM-DD hh:mm> to <YYYY-MM-DD hh:mm TZ>                     |
| Methods                    | *read-only commands, API reads, exports, interviews, site photos* |
| Runtime per target / total | <n> s / <n> min (measured)                                      |
| Collector and journal      | <role> / <path>                                                 |

## 2. Evidence sources and coverage

| Source             | What it claims             | Freshness     | Targets read / total | Trust and known gaps | Label              |
| ------------------ | -------------------------- | ------------- | -------------------- | -------------------- | ------------------ |
| <inventory system> | intended devices and links | <age>         | <n>/<n>              | *manual entry, lag*  | VERIFIED_SECONDARY |
| <device read>      | running config, neighbours | at collection | <n>/<n>              | *timeouts on <n>*    | VERIFIED_PRIMARY   |
| <monitoring>       | health, counters           | <interval>    |                      |                      |                    |

## 3. Inventory summary

| Class                   | Model / version     | Count | EOL / support state | Role | Notes | Label |
| ----------------------- | ------------------- | ----- | ------------------- | ---- | ----- | ----- |
| <router/switch/AP/host> | <model> / <version> | <n>   | <date or unknown>   |      |       |       |

## 4. Topology and dependencies

```text
OBSERVED <YYYY-MM-DD> (source: <neighbour tables / flow data / interview>); ? = UNKNOWN

+------------------+  <rate>  +-----+   +------+   +-----------+
| <site-code> edge |--------->| agg |-->| core |-->| <service> |
+------------------+          +-----+   +------+   +-----------+
          |                                              |
          v                                              v
+------------------+                       depends: DNS <role>, time <source>
| mgmt path ?      |
+------------------+
```

| Dependency     | Consumer  | Provider        | Observed how         | Single instance? | Label |
| -------------- | --------- | --------------- | -------------------- | ---------------- | ----- |
| DNS            | <service> | <provider role> | resolver config read | yes / no         |       |
| Time           |           |                 |                      |                  |       |
| Identity / AAA |           |                 |                      |                  |       |
| Power / UPS    |           |                 |                      |                  |       |

## 5. Drift between intent and observation

| Object         | Intended (source)     | Observed (source, time) | Impact | Proposed owner of correction |
| -------------- | --------------------- | ----------------------- | ------ | ---------------------------- |
| <VLAN on port> | <value> (<inventory>) | <value> (<device read>) |        |                              |

*Do not correct intent from observation silently; raise each row to the authoritative writer.*

## 6. Observed behaviour and baselines

| Metric                      | Population | Window   | p50 / p95 / max | Unit   | Source |
| --------------------------- | ---------- | -------- | --------------- | ------ | ------ |
| Utilisation on <link class> | <n> links  | <n> days |                 | Mbit/s |        |

## 7. Unknowns

| Unknown | Targets affected | Why it matters | Cheapest discriminating check | Owner | Due |
| ------- | ---------------- | -------------- | ----------------------------- | ----- | --- |
|         |                  |                |                               |       |     |

## 8. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
