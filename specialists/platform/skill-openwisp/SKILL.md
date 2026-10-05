---
name: skill-openwisp
description: >-
  Operate, diagnose and extend OpenWISP: device registration and hardware_id, organisations and device groups, REST API and tokens, NetJSON DeviceMonitoring
  pushes and backfill, custom metrics and charts, InfluxDB storage and retention, Celery workers and queues, health checks, alerts and notifications,
  docker-openwisp settings and upgrades. Use for OpenWISP monitoring and presentation work; not as the primary skill for Nautobot inventory or lifecycle intent.
---

# OpenWISP

## Role and non-goals

Use OpenWISP for registration, monitoring, metrics, health, notifications, OpenWrt-oriented controller capabilities, topology/NetJSON integration where version-supported, and extensions through
Django, settings, modules and APIs.
Do not assume a closed-firmware device has native configuration control or turn a project-specific shim into product behaviour.

## Read, write, and evidence boundaries

**HTTP/API acceptance is only an early evidence stage.**
Trace `offline mapping → API accepted → worker processed → Metric metadata → fresh point`; health evaluation and graph presentation branch independently from fresh data.
Obtain project authorization for writes, retain source/version/evidence, and never infer a later rung from an earlier one.
Keep observation source, timestamp, freshness and unit semantics available to the consuming policy.
Do not embed client credentials, customer topology, or equipment-specific commands in reusable guidance.

## Route the task

Choose the primary skill by the object or failure **being changed**: OpenWISP registration, worker, metric, health, notification or graph starts here; Nautobot
Device/IPAM/ownership/lifecycle starts in `skill-nautobot`. A synchronization task uses the owner of the requested change as primary, then reads the other skill's
contract. Observed topology collection/presentation starts with its affected component; intended inventory topology starts with Nautobot. Vendor commands, OIDs,
RF interpretation and transport execution begin with equipment/transport expertise. Ordinary single-platform tasks load one pack.

| Task                                                                | Read first                                     |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| Exact syntax: REST, tokens, InfluxDB, Celery, settings, commands    | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Logical identity, adoption, duplicate prevention, replacement       | [references/identity-and-registration.md](references/identity-and-registration.md) |
| Passive observations, NetJSON and closed-firmware metrics           | [references/passive-ingestion.md](references/passive-ingestion.md) |
| Accepted payload, worker, storage, freshness and graph triage       | [references/verification-and-troubleshooting.md](references/verification-and-troubleshooting.md) |
| Health, policy, suppression, correlation and notification transport | [references/health-alerts-notifications.md](references/health-alerts-notifications.md) |
| Observed topology, NetJSON NetworkGraph and complementary FOSS      | [references/topology-and-foss.md](references/topology-and-foss.md) |
| Missing capability, modules, supported seams and FOSS               | [references/capability-extension.md](references/capability-extension.md) |
| Django settings, metrics, workers, overlays and upgrades            | [references/customisation-and-upgrades.md](references/customisation-and-upgrades.md) |
| Reusable learning capture and engagement closeout                   | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Verify version-sensitive facts

Before asserting a current endpoint, model field, setting, timestamp format, supported module or release behaviour, inspect version-matched official documentation and record source/date in
[sources.yaml](sources.yaml).
Read [compatibility.yaml](compatibility.yaml) as a bounded evidence ledger; an observed image or module version does not prove ingestion or a graph.
Record unknowns as unknown rather than extrapolating a support range.

## Search before building

```text
desired operator outcome
  ↓ existing OpenWISP core capability
  ↓ installed or maintained product modules and relevant NTC tooling
  ↓ supported extension points of those components
  ↓ compatible external FOSS and its supported seams
  ↓ from-scratch component only when the acceptance test still cannot be met
```

At every downward transition, explain why the preceding level cannot meet the acceptance test.
Recheck maintenance, license, compatibility, reachability and supported extension mechanisms; do not maintain a static best-tools ranking.
Prefer the narrowest supported seam and cover the behaviour it relies on with a regression test.

## Project and equipment boundary

Keep exact customer, site and device state in its governing project.
Route vendor commands, OIDs and device access details to equipment expertise; do not include credentials or device-specific operations here.
For a cross-platform task, load another skill only when the task actually crosses its ownership boundary.

## Project conventions

A project that runs OpenWISP may keep a platform-conventions file (its field owners, writer accounts, naming, safety tiers and evidence vocabulary). Check the
engaging project's `AGENTS.md` for it before any write; project rules outrank the generic guidance here. For UNC that file is
`docs/engineering/platform-skills-project-layer-20261005_1349.md` in the unified-network-controller project.

## Standing write-back contract

Invoking this skill obliges you to write back what the engagement taught, in any project, before the session ends: a dated Learned entry in the focused reference
plus one CHANGELOG line under `## Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate,
contradiction, project-only, equipment-only). Skill use never authorizes editing a live system, and editing this source only when the task permits it; otherwise
leave the entry in the engaging project. Format, classes and release reconciliation:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).
