# Changelog

## Unreleased

## 0.4.0 — 2026-10-05

- New references, each verified against the installed 26.09.0 images and versioned docs: `configuration-management.md` (templates, variables,
  backends, agent, auto-registration, VPN), `connections-and-firmware.md`, `radius-and-captive-portal.md` and `deployment-and-recovery.md`; extending
  models through swappable models added to `customisation-and-upgrades.md`.
- Promoted helpers in `scripts/`: `openwisp_identity.py` (hardware_id, names, MACs, UTC backfill time) and `openwisp_probe.py` (workers, freshness,
  effective settings; read-only), with tests; the probe found a live week-long worker outage on its first run.
- `SKILL.md`: Orient section, routing for every reference, wider description.
- Fleet lessons from a measured capture corpus (liveness signals, SNMP gaps, identity) and two places where the 26.09 docs and the images disagree.
- Scenarios O-S25 to O-S27.

- 2026-10-05 `connections-and-firmware.md`: Learned entry, docs and installed image disagree (verified against the running URLconf / beat schedule).
- 2026-10-05 `radius-and-captive-portal.md`: Learned entry, docs and installed image disagree (verified against the running URLconf / beat schedule).

- 2026-10-05 `verification-and-troubleshooting.md`: 2 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `passive-ingestion.md`: 1 Learned entry from the capture corpus (measured fleet lessons).
- 2026-10-05 `identity-and-registration.md`: 1 Learned entry from the capture corpus (measured fleet lessons).

## 0.3.0 — 2026-10-05

- Added `references/operations-cookbook.md`: ten version-matched recipes with a summary table (REST auth and paging, controller devices and deletion, monitoring
  push and backfill, InfluxDB 1.8, Celery queues and workers, custom metrics and checks, notifications, organizations, docker-openwisp settings, management
  commands), cited to the installed 26.09.0 image; 13 versioned 26.09 doc snapshots.
- Evidence ladder promoted from UNC records: API accepted, worker processed and Metric persisted pass; recent point passed 2026-09-22 and is `stale` on 2026-10-05
  (no worker running); operator-visible remains pending.
- Replaced the five-file write-back rule with the standing contract and its test; SKILL.md description, cookbook route and project-conventions pointer. Claims
  O-C16, O-C17; scenarios O-S20 to O-S24.
- Evaluation 2026-10-05 (Claude Code, Sonnet, fresh contexts): O-S20 and O-S21/22 passed with the skill; the no-skill controls were partial.

- 2026-10-05 `identity-and-registration.md`: Learned entry, 1.3 REST serializers omit `hardware_id` (installed source).
- 2026-10-05 `verification-and-troubleshooting.md`: Learned entry, detached workers make container status meaningless for the worker rung.

## 0.2.0 — 2026-10-01

- Deepened registration, mapping, process, alert and topology decisions (O-C01–O-C15); split health and graph into independent consumers after fresh storage.
- Separated source classes and install/inspection/offline/pending-live compatibility; repaired O-C01 → O-S17 linkage.
- Added scenario O-S17–O-S19 and claim/scenario semantic validation. No runnable helpers or runtime install changes.

## 0.1.0 — 2026-10-01

- Added claims O-C01 through O-C15, scenarios O-S01 through O-S16, and the deterministic package contract.
- Recorded observed image/module rows, the explicit pending Monitoring evidence ladder, and local official-documentation snapshots.
- Hardened registration, passive ingestion, rung-by-rung verification, alert correlation, topology, capability, and upgrade guidance without promoting pending live behavior.
- No migrations or retirements.
