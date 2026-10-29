# Changelog

## 2026-10-07 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-07-snake-case-recipes-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-07-snake-case-recipes-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md, justfile

## Unreleased

- 20261013 Learned 2026-10-13 in `references/customisation-and-upgrades.md`: settings set from the environment in a custom Django settings file, and the
  OpenWISP notification type per alarm class (unified-network-controller); line backfilled 2026-10-29 for the write-back contract test.
- 20261029 Learned 2026-10-29 in `references/verification-and-troubleshooting.md`: three ways a successful push stores nothing (Celery abort at the first
  invalid value, no metric-producing field, Data Collected's 60 min window); done means healthy through one check interval (unified-network-controller).

- 20261029 Learned 2026-10-29 in `references/deployment-and-recovery.md`: beside another Django app on the same host, rename OpenWISP's CSRF cookie as well as its session cookie; a Secure `csrftoken`
  over HTTPS blocks the HTTP app's own (unified-network-controller, Nautobot "CSRF cookie not set").

- 20261020 Learned 2026-10-20 in `references/passive-ingestion.md`: the monitoring push is one device per request, `time` for late data; OpenWISP's monitoring agent is OpenWrt-only
  (unified-network-controller SMC push research).
- 20261020 Write-back contract: every entry recording how something is done carries a code excerpt (source path, commit) and, for a visual surface, a redacted screenshot under
  `references/screenshots/<YYYYMMDD>-<slug>/` (operator, 2026-10-20).
- 20261019 Learned 2026-10-16 (UNC backlog audit, OpenWISP dashboard by IP on UNC01, verified): `references/deployment-and-recovery.md` gains that the images' domain-scoped cookies lose the session on
  an IP URL; host-only cookies, a distinct session name and the exact HTTPS origin with port fix it.
- 20261015 Learned 2026-10-15 (b) (UNC SSoT read-only role, verified update): `references/identity-and-registration.md` gains the live check of the health query's columns and the column-level grants
  that keep device keys unreadable.
- 20261015 Learned 2026-10-15 (UNC SSoT OpenWISP health Job, verified update): `references/identity-and-registration.md` gains the monitoring device list's fields (no hardware_id) and the read-only
  database query that gives hardware_id-keyed health where no Django shell is available.
- 20261013 Learned 2026-10-13 (from UNC 2026-10-12/13, written back late after a write-back audit): `references/deployment-and-recovery.md` (openwisp-nginx resolves the API once: restart it after the
  API; Redis MISCONF while reloading), `references/customisation-and-upgrades.md` (admin title and header settings; a custom notification type needs a restart; candidate pattern: OpenWISP
  notifications as the transport for external alarm rules).
- 20261010_1805 Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains `ai_it`, a second `check` line running
  skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate` recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`,
  `just history`); `doc_freshness.py --write-baseline` grandfathers existing findings (scripts/doc-freshness-baseline.json, 20 entries), so only new ones fail.
- 20261010_1805 CHANGELOG.md (73) and SCRATCHPAD.md (94) are within budget; nothing rotated.
- 20261007_1205 `references/health-alerts-notifications.md`: Learned 2026-10-07 (reusable_candidate, UNVERIFIED): agents with `verify_ssl` go silent fleet-wide when the controller certificate expires;
  alert on certificate expiry and fleet-wide freshness, classify as a transport cause.
- 20261005_1936 Governance follow-ups (operator): the `justfile` merges this bootstrap's recipes with a parallel session's `helpers` and probe recipes, and `bootstrap` installs root `requirements.txt`
  (`-r tests/requirements.txt`, one PyYAML pin); `AGENTS.md` is tracked with `git add -f` because the repo's git info/exclude file ignores it repo-wide (the exclude rule is unchanged, so later edits
  need `git add -f` again); all 6 `.archcore/` documents accepted.
- 20261005_1931 `/skill-ai-it promote` for all candidates: `.archcore/` now holds 2 ADRs, 3 rules and 1 plan, indexed by `.archcore/index.guide.md`; the candidates queue was deleted and the governance
  checker now requires every Archcore document to be indexed. The operator accepted all 6 the same day.
- 2026-10-05 promoted from UNC: `scripts/openwisp_registry.py`, `scripts/openwisp_health_mirror.py`, `scripts/openwisp_alert_policy.py`, with tests.

- 20261005_1602 governance bootstrap (skill-ai-it): added `README.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `justfile`, `.mise.toml`, `scripts/README.md`
  and `scripts/check_governance.py` (run by `tests/test_helpers.py`, with a must-fail case), Repomix and markdownlint configs and `archcore init`; generated `.ai-context/` and `graphify-out/`. No
  reference, claim or helper content changed.

## 0.4.0 — 2026-10-05

- New references, each verified against the installed 26.09.0 images and versioned docs: `configuration-management.md` (templates, variables, backends, agent, auto-registration, VPN),
  `connections-and-firmware.md`, `radius-and-captive-portal.md` and `deployment-and-recovery.md`; extending models through swappable models added to `customisation-and-upgrades.md`.
- Promoted helpers in `scripts/`: `openwisp_identity.py` (hardware_id, names, MACs, UTC backfill time) and `openwisp_probe.py` (workers, freshness, effective settings; read-only), with tests; the
  probe found a live week-long worker outage on its first run.
- `SKILL.md`: Orient section, routing for every reference, wider description.
- Fleet lessons from a measured capture corpus (liveness signals, SNMP gaps, identity) and two places where the 26.09 docs and the images disagree.
- Scenarios O-S25 to O-S27.

- 2026-10-05 `connections-and-firmware.md`: Learned entry, docs and installed image disagree (verified against the running URLconf / beat schedule).
- 2026-10-05 `radius-and-captive-portal.md`: Learned entry, docs and installed image disagree (verified against the running URLconf / beat schedule).

- 2026-10-05 `verification-and-troubleshooting.md`: 2 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `passive-ingestion.md`: 1 Learned entry from the capture corpus (measured fleet lessons).
- 2026-10-05 `identity-and-registration.md`: 1 Learned entry from the capture corpus (measured fleet lessons).

## 0.3.0 — 2026-10-05

- Added `references/operations-cookbook.md`: ten version-matched recipes with a summary table (REST auth and paging, controller devices and deletion, monitoring push and backfill, InfluxDB 1.8, Celery
  queues and workers, custom metrics and checks, notifications, organizations, docker-openwisp settings, management commands), cited to the installed 26.09.0 image; 13 versioned 26.09 doc snapshots.
- Evidence ladder promoted from UNC records: API accepted, worker processed and Metric persisted pass; recent point passed 2026-09-22 and is `stale` on 2026-10-05 (no worker running); operator-visible
  remains pending.
- Replaced the five-file write-back rule with the standing contract and its test; SKILL.md description, cookbook route and project-conventions pointer. Claims O-C16, O-C17; scenarios O-S20 to O-S24.
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
