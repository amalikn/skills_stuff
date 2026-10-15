# Changelog

## 2026-10-07 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-07-snake-case-recipes-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-07-snake-case-recipes-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md, justfile, scripts/README.md

## Unreleased

- 20261015 Learned 2026-10-15 (n, o, p) (UNC load and review batch, verified update): `references/operations-and-recovery.md` healthcheck cost and the beat heartbeat check; `references/config-backup-compliance.md` GC 3.0.7's compliance list returns nothing when filtered by location; `references/apps-jobs-validation.md` Collector refuses a PROTECT chain, preview by rollback.
- 20261015 Learned 2026-10-15 (l, m) (UNC UI features page, verified update): `references/app-development.md` gains hiding menus per audience (HIDE_RESTRICTED_UI gone since 2.1, per-request nav_menu wrapped by an app context processor, core apps not removable, app constance keys `<app>__<KEY>`, `is_staff` nav permission); `references/data-model.md` gains Namespace.location PROTECT blocking a Location delete.
- 20261015 Learned 2026-10-15 (k) (UNC as-built workbook probe, verified update): `references/api-and-writers.md` gains which `location` filters take a subtree (Devices) and which do not (interfaces, wireless links; Cables reject it), the port endpoints' `device` filter, and depth-1 Cables resolved locally (three times faster).
- 20261015 Learned 2026-10-15 (j) (UNC Golden Config backups on unc01, verified update): `references/config-backup-compliance.md` gains GC 3.0.7's reverse accessor `device.goldenconfig`, the backup view's URL name, the API-fed backup path with no driver, an app Device tab for it, and the device `location` filter including child Locations.
- 20261015 Learned 2026-10-15 (i) (UNC SSoT schedule step, verified update): `references/apps-jobs-validation.md` gains ScheduledJob.create_schedule for a machine-owned schedule (start from crontab, no permission check on the owner).
- 20261015 Learned 2026-10-15 (i) (UNC IPAM Services for SMCs, verified update): `references/authority-and-modeling.md` gains the 3.2.3 Service shape (no Status, protocol tcp or udp only), so listener presence is carried by tags on the Service and differences on the Device.
- 20261015 Learned 2026-10-15 (h) (UNC SSoT OpenWISP health Job, verified update): `references/integrations.md` gains a flat field-mirror DataSource pattern, quieter diffsync flags for an hourly mirror, schedulable Jobs need has_sensitive_variables False, the writer is the schedule's owner via the change context, DataMapping's shape and the pydantic Optional gotcha in path-loaded tests.
- 20261015 Learned 2026-10-15 (g) (UNC 0.8.23, verified update): `references/apps-jobs-validation.md` gains DLM's Validated Software REST shape and uniqueness, a global default Saved View's redirect and clear_view, and a Device-page tab from an app.
- 20261015 Learned 2026-10-14 (f) (UNC platform features plan, verified update): `references/apps-jobs-validation.md` gains DLM validity by exact SoftwareVersion match (all Invalid with none), Golden Config 3.0.7's compliance-only Device tab, core LLDP/Configuration tabs as live NAPALM calls, and Data Compliance registration.
- 20261014 Learned 2026-10-14 (e) (UNC 0.8.22, verified update): `references/apps-jobs-validation.md` gains Run Now held by a matching approval workflow (dryrun skips it), hiding one Job's schedule card, Job result logs not filterable by grouping, and a conditional object tab.
- 20261014 Learned 2026-10-14 (d) (UNC 0.8.15 to 0.8.19, verified update): `references/apps-jobs-validation.md` gains DNS Models zone tags not writable over REST, banners on every tab of an object page, an htmx poll filter stuck after Back, Job log retention as a history source, and badge text colours.
- 20261014 Learned 2026-10-14 (c) (UNC 0.8.12, verified update): `references/apps-jobs-validation.md` gains a per-user view switch kept in user preferences and drawn in the app banner, and nbshell's interactive-prompt pitfall.
- 20261014 Learned 2026-10-14 (b) (UNC dependent new-site fields and RPZ option A, candidate): `references/apps-jobs-validation.md` gains dependent Job fields through `Meta.template_name`, DNS Models' constance key for CNAME exclusivity, and an htmx poll filter that pauses while a modal is open.
- 20261014 Learned 2026-10-14 (UNC 0.8.8, verified update): `references/apps-jobs-validation.md` gains clearing a superseded approval request from the approved Job (`ScheduledJob.task` = `class_path`, no `approval_required` field, `JobResult.scheduled_job`).
- 20261014 Learned 2026-10-14 (UNC onboarding page, verified update): `references/app-development.md` gains four 3.2.3 seams: answering an approval stage from any page via its own approve/deny view with `return_url`, app banners, app Jinja filters for Job Button text, and htmx polling that stops itself.
- 20261013 Learned 2026-10-13 (UNC app 0.8.6, verified update): `references/app-development.md` gains a site panel's Relationship query (`destination_id__in` an Interface `.values("pk")` subquery works on 3.2.3 where `descendants()` does not).
- 20261013 Learned 2026-10-13 (reusable_candidate patterns from UNC, operator: write the out-of-the-box ideas back): `references/capability-extension.md` gains four: a host runner for Jobs that need reach the worker lacks; workflow state from Job log groupings with approval-held gate Jobs; a reference beside inventory as a Config Context with drift computed at read time; Django-free panel modules previewed in both themes.
- 20261013 Learned 2026-10-13 (backlog from UNC 2026-10-12/13, verified update, recorded late after a write-back audit): `references/operations-and-recovery.md` (banner variables; health_check slower than the image timeout), `references/app-development.md` (no hyphen in app labels; overlayfs refuses a rename across layers), `references/data-model.md` (row colour from cable status only at default colours; Bridge field only on members; Circuit description 255; find Interfaces by name, not label).
- 20261013 Learned (UNC onboarding flow, verified update): `references/apps-jobs-validation.md` gains two Learned 2026-10-13 entries (a Job stopping at an approval by queuing a ScheduledJob; definitions, constraints and the shipped example; callable ChoiceVar, logger levels, JobButtonReceiver, time limits) and `references/api-and-writers.md` one (Cables by `location_id` are exact-location only; repeated device ids per query).
- 20261012_1756 promoted from UNC (apn-unc01 deployment): `scripts/nautobot_web_login.py` and `just web_login`, a read-only check that a username and
  password open the web UI through the login form (CSRF, session cookie); offline tests in `tests/test_helpers.py`; smoke-run against apn-unc01 (LOGIN OK).
- 20261010_1805 Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains
  `ai_it`, a second `check` line running skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate`
  recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`, `just history`); `doc_freshness.py --write-baseline`
  grandfathers existing findings (scripts/doc-freshness-baseline.json, 22 entries), so only new ones fail.
- 20261010_1805 CHANGELOG.md (84) and SCRATCHPAD.md (94) are within budget; nothing rotated.
- 2026-10-09 Learned (from UNC, D10 link discovery): `references/data-model.md` an Interface has no `cable` field in 3.2 (CableToCableTermination); `Location.descendants()` fails as a subquery; a Device has no coordinates, a position belongs to its Location. `references/app-development.md` an app tab on a core object (DistinctViewTab and its view), app static served by its own view, choices kept out of migrations.
- 2026-10-08: three Learned entries in `references/data-model.md` from unified-network-controller: list views omit many-to-many fields
  without `exclude_m2m=false`; a cable trace crosses a device only through front/rear ports and never a VLAN interface or a switch; a `Panel` can
  return `render_markdown` from `render_body_content`.

- 2026-10-08 Learned (from UNC): `references/data-model.md` §4 an interface template added to an existing Device Type does not reach its existing Devices (3.2.3); back-fill with the new helper.
- 2026-10-08 promoted from UNC session code: `scripts/nautobot_template_sync.py` (missing template interfaces on existing Devices; plans unless `--apply`) and `scripts/nautobot_app_compat.py` (PyPI app metadata against a Nautobot and Python version, read-only), both stdlib-only with offline tests in `tests/test_helpers.py`; recipes `just template_sync` and `just app_compat`. Smoke: nautobot-ssot 4.7.0, nautobot-device-lifecycle-mgmt 4.2.0 and nautobot-capacity-metrics 4.1.1 all compatible with Nautobot 3.2.3 / Python 3.13.
- 2026-10-08 Learned (from UNC): `references/data-model.md` the two-ended Cable POST works on 3.2.3, and interfaces have no `cabled` filter.
- 2026-10-08 Learned (from UNC): `references/authority-and-modeling.md` custom field keys are immutable, a rename is copy then delete; `references/upgrade-and-troubleshooting.md` SSoT 4.7.0, DLM 4.2.0 and Capacity Metrics 4.1.1 on 3.2.3 / Python 3.13, and post_upgrade must run in the recreated container.
- 2026-10-08 Learned (from UNC, Raspberry Pi SMC canary): `references/data-model.md` a host's radio takes a wireless interface type, decided from the host; `references/api-and-writers.md` get-or-create above a dry-run branch writes, and `custom_fields` ride on the create POST.
- 20261005_1936 Governance follow-ups (operator): the `justfile` merges this bootstrap's recipes with a parallel session's `helpers` and probe recipes, and `bootstrap`
  installs root `requirements.txt` (`-r tests/requirements.txt`, one PyYAML pin); `AGENTS.md` is tracked with `git add -f` because the repo's git info/exclude file ignores it
  repo-wide (the exclude rule is unchanged, so later edits need `git add -f` again); all 6 `.archcore/` documents accepted.
- 20261005_1931 `/skill-ai-it promote` for all candidates: `.archcore/` now holds 2 ADRs, 3 rules and 1 plan, indexed by
  `.archcore/index.guide.md`; the candidates queue was deleted and the governance checker now requires every Archcore document to be indexed. The operator accepted all 6 the same day.
- 2026-10-05 promoted from UNC: `scripts/nautobot_masks.py` (from fix_address_masks) and `scripts/nautobot_linkage.py` (from site_linkage), with tests; listings now fail closed.

- 20261005_1602 governance bootstrap (skill-ai-it): added `README.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`,
  `justfile`, `.mise.toml`, `scripts/README.md` and `scripts/check_governance.py` (run by `tests/test_helpers.py`, with a must-fail case), Repomix and
  markdownlint configs and `archcore init`; generated `.ai-context/` and `graphify-out/`. No reference, claim or helper content changed.

## 0.4.0 — 2026-10-05

- New references, each verified against the installed 3.2.3 source and bundled docs: `data-model.md` (Locations, Platforms and `network_driver`,
  interfaces and VLANs, modules, contacts and teams), `app-development.md` (an app from skeleton to tests), `integrations.md` (pynautobot, SSoT/DiffSync,
  Git data, export templates, Ansible and Nornir inventories, Golden Config) and `operations-and-recovery.md` (backup and restore, health, metrics,
  performance, security settings).
- Promoted helpers in `scripts/`: `nautobot_paging.py` (fail-closed traversal) and `nautobot_ipam.py` (mask rule), with tests; the contract test now
  allows `scripts/` and requires each helper to be tested and stdlib-only.
- `SKILL.md`: Orient section, routing for every reference, wider description.
- Fleet lessons from a measured capture corpus (identity signals, address overlap, DNS and sysName) and installed-source Learned entries.
- Scenarios N-S24 to N-S26. Independent assessment: UNC `docs/reports/project-reviews/nautobot-openwisp-skills-independent-assessment-20261005_1427.md`.

- 2026-10-05 `integrations.md`: Learned entry from the installed source (pynautobot 3.2.0).
- 2026-10-05 `integrations.md`: Learned entry from the installed source (nornir-nautobot 4.4.2).
- 2026-10-05 `operations-and-recovery.md`: Learned entry from the installed source (Nautobot 3.2.3).

- 2026-10-05 `staged-onboarding.md`: 3 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `discovery-and-topology.md`: 2 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `authority-and-modeling.md`: 2 Learned entries from the capture corpus (measured fleet lessons).

## 0.3.0 — 2026-10-05

- Added `references/operations-cookbook.md`: twelve version-matched recipes with a summary table (GraphQL, REST, Dynamic Groups, computed/custom fields, Config
  Contexts, Secrets, webhooks/Job Hooks/events, approvals, data validation, permissions and change log, nautobot-server, Jobs, Circuits), cited to the installed 3.2.3
  source; 27 bundled 3.2.3 doc snapshots in `documents/`.
- Replaced the five-file write-back rule with a standing contract: a dated Learned entry plus one CHANGELOG line, checked by the contract test; release reconciliation
  and a version trigger keep the cookbook current.
- SKILL.md: trigger-rich description, cookbook route, project-conventions pointer. Claims N-C18, N-C19; scenarios N-S19 to N-S23; compatibility row for 3.2.3 docs.
- Contract test: snapshots verified from the index table, Learned entries parsed and tied to CHANGELOG lines, cookbook version tied to `compatibility.yaml`, fixed a
  private-address false positive.
- Evaluation 2026-10-05 (Claude Code, Sonnet, fresh contexts): N-S19 and N-S20 passed with the skill; the no-skill controls were partial.

- 2026-10-05 `operations-cookbook.md`: Learned entry, REST create accepts a client-supplied `id` (installed source); found by the skill evaluation.
- 2026-10-05 `authority-and-modeling.md`: Learned entry, deleted built-in Statuses/Roles are not recreated by migrate or post_upgrade (installed source).

## 0.2.0 — 2026-10-01

- Deepened ownership, paging/writer, onboarding, replacement, Wireless Link, Job, backup and upgrade decisions with synthetic failure cases (N-C01–N-C17).
- Split official, implementation, test, synthesis, policy and install evidence; repaired N-C13 → N-S16 and N-C03 → N-S17 links.
- Added scenario N-S16–N-S18, claim/scenario semantic validation and a mixed-primary routing rule. No runnable helpers or runtime install changes.

## 0.1.0 — 2026-10-01

- Added claims N-C01 through N-C17, scenarios N-S01 through N-S15, and the deterministic package contract.
- Recorded the observed Nautobot 3.2.3/application baseline, the version-bounded 3.2 Job source, and local official-documentation snapshots.
- Hardened authority, pagination, staged onboarding, replacement, topology, worker, backup, extension, and upgrade guidance with Phase 1 worked patterns.
- No migrations or retirements.
