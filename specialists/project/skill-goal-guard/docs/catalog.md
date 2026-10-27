---
Title: skill-goal-guard Catalog
Category: catalog
Status: current
Authority: local-supplement; operator decisions recorded 2026-10-27, workspace facts read on disk 2026-10-27
Scope: Every file in skill-goal-guard, the operator decisions, where each source conflict was settled and the checked workspace facts
Last reviewed: 2026-10-27
Summary: >-
  Index of the skill pack (SKILL.md, references, scripts, tests) and of the verbatim source documents under docs/, with the operator decisions and a
  pointer to where each of the eight source conflicts is settled.
---

# skill-goal-guard catalog

Goal Guard (alias skill-gg): owner-approved MVP scope gate and solo portfolio focus for coding agents working in `project_stuff/`. Current status: [../SKILL.md](../SKILL.md) (Orient first, item 1).

## Decisions (operator, 2026-10-27)

- Vikunja owns live task state (priority, status, due dates, dependencies). Goal Guard owns scope, approvals, decisions, deferred ideas, internal targets and forecasts.
- Vikunja runs locally: 2.7.1 deployed 2026-10-27 from `tools_stuff/vikunja` (status: [../SKILL.md](../SKILL.md), Orient first).
- The first build is the full v1.7 kickoff pilot ([../references/pilot-plan.md](../references/pilot-plan.md)).
- Skill at the folder root (`SKILL.md`, `name: skill-goal-guard`); the consolidated rules in `references/`; source documents kept verbatim under `docs/`.
- Naming: folders `goal-guard`, `goal-guard-research-pack`; documents and Python files `goal_guard`; markdown filenames lower case except tool-mandated `SKILL.md`, `AGENTS.md`, `CLAUDE.md`.
- All code is written under skill-coder.
- Pilot decisions D1-D6: one `apn` repository scoped by path; pilot spoke `unified-network-controller`; approvals by signed Git commit; plan and Excel found in `enterprise-strategy` (to confirm);
  Vikunja on OrbStack with SQLite; folder name `.gg/` ([../references/pilot-plan.md](../references/pilot-plan.md)).

## Skill pack

| Path                                             | Kind         | What it holds                                                                          |
| ------------------------------------------------ | ------------ | -------------------------------------------------------------------------------------- |
| [../SKILL.md](../SKILL.md)                       | skill        | Activation, routing table, handoff workflow, output format, standing rules, write-back |
| [../AGENTS.md](../AGENTS.md), [../CLAUDE.md](../CLAUDE.md) | agent policy | Layout, working rules, done checks                                                     |
| [../references/authority-and-sources-of-truth.md](../references/authority-and-sources-of-truth.md) | reference    | Ownership table, conflict order, trust levels                                          |
| [../references/decision-rules.md](../references/decision-rules.md) | reference    | Verdicts, evaluation order, settled conflicts 2-3, clause index                        |
| [../references/mvp-contract-and-change-control.md](../references/mvp-contract-and-change-control.md) | reference    | Contract fields, planning exit, change control, parked ideas, completion               |
| [../references/whats-next-and-portfolio.md](../references/whats-next-and-portfolio.md) | reference    | Three-level next, ranking pipeline (conflict 4), WIP, interrupts                       |
| [../references/enforcement-and-hooks.md](../references/enforcement-and-hooks.md) | reference    | Enforcement honesty, clients, Archcore rule, Thekedar mechanisms                       |
| [../references/vikunja-integration.md](../references/vikunja-integration.md) | reference    | Deployment, facts to verify, mapping, stages (conflict 6), degraded mode               |
| [../references/hub-management-and-dates.md](../references/hub-management-and-dates.md) | reference    | Hub/spokes, management trace, four dates, Excel, cutover gate                          |
| [../references/project-layout-and-storage.md](../references/project-layout-and-storage.md) | reference    | Workspace facts, shared `apn` repo, `.gg/` records and two logs (conflict 5), maps     |
| [../references/snapshot-and-restore.md](../references/snapshot-and-restore.md) | reference    | Snapshot, offline use, restore, what is not captured                                   |
| [../references/feature-inventory.md](../references/feature-inventory.md) | reference    | 53 features and ideas with dispositions; phases L1-L5                                  |
| [../references/pilot-plan.md](../references/pilot-plan.md) | plan         | Owner decisions D1-D6, steps 0-9, prototype gaps, stop conditions                      |
| [../references/test-catalog.md](../references/test-catalog.md) | reference    | Test series, merged duplicates, pilot set, ID collision (conflict 7)                   |
| [../references/evolution-and-write-back.md](../references/evolution-and-write-back.md) | reference    | Write-back trigger and entry format                                                    |
| [../scripts/readme.md](../scripts/readme.md) | catalog | Seven front ends, the `goal_guard_lib` modules, exit codes, measured runtime, open live checks, moved paths |
| [../scripts/](../scripts/) | code | `goal_guard.py`, `goal_guard_vikunja.py`, `_trace`, `_snapshot`, `_excel`, `_doctor`, `_hook`; package `goal_guard_lib/` (written 2026-10-27 under skill-coder) |
| [../tests/](../tests/) | tests | 71 tests: decide, rank, decisions log, Vikunja seam and snapshot/restore (fake instance), hook and doctor, trace and seams, CLI exit codes; `helpers.py`, `fake_vikunja.py` |
| [../examples/](../examples/) | fixtures | `project_stuff/` (apn demo-spoke with `.gg/` records, demo-hub plan, me demo-personal), `vikunja-tasks.json`, `proposals/`; `v0.1/` prototype fixtures |
| [../requirements.txt](../requirements.txt), [../ruff.toml](../ruff.toml) | tooling | Pinned PyYAML 6.0.3, openpyxl 3.1.5, ruff 0.17.3 with seams; ruff two-space config |
| [../justfile](../justfile), [../.mise.toml](../.mise.toml), [../code-map.toml](../code-map.toml) | tooling      | Task catalog, Python 3.14 pin, code intent                                             |
| [../readme.md](../readme.md) | index | Folder index and run commands |
| [../SCRATCHPAD.md](../SCRATCHPAD.md) | state | Working state, open items, next actions |
| [../documents/vikunja-2.7.1-20261027/readme.md](../documents/vikunja-2.7.1-20261027/readme.md) | capture | Vikunja 2.7.1 OpenAPI and info, verbatim, 2026-10-27 |
| [../changelog.md](../changelog.md), [../roadmap.md](../roadmap.md) | records      | History; what comes next                                                               |

## Source documents (verbatim, under docs/)

| Path                                                 | Kind                | Status                                       | What it holds                                                            |
| ---------------------------------------------------- | ------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| [goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md](goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md) | handoff-spec        | current source                               | Layered v1.0-v1.7 policy                                                 |
| [goal_guard_agent_kickoff_v1_7.md](goal_guard_agent_kickoff_v1_7.md) | agent-kickoff       | current source                               | Pilot tasks, stop conditions, completion gate                            |
| [goal-guard-research-pack/](goal-guard-research-pack/readme.md) | research            | proposed, not decided                        | v0.x architecture, roadmap, CTPS, GG tests, Vikunja design,              |
|                                                      |                     |                                              |   backlog, Thekedar                                                      |
| [goal-guard/SKILL.md](goal-guard/SKILL.md), [goal-guard/readme.md](goal-guard/readme.md) | v0.1 skill and spec | superseded by the root SKILL.md              | Kept for history; its CLI examples use the old layout, run `just` at     |
|                                                      |                     |   and references                             |   the root                                                               |

## Where each source conflict is settled

| #   | Conflict                                | Settled in                                                           |
| --- | --------------------------------------- | -------------------------------------------------------------------- |
| 1   | Who owns live tasks                     | operator decision; [../references/authority-and-sources-of-truth.md](../references/authority-and-sources-of-truth.md) |
| 2   | Necessary dependency: PROCEED or REVIEW | [../references/decision-rules.md](../references/decision-rules.md)   |
| 3   | Missing baseline and BLOCK              | [../references/decision-rules.md](../references/decision-rules.md)   |
| 4   | Weighted score vs ordered pipeline      | [../references/whats-next-and-portfolio.md](../references/whats-next-and-portfolio.md) |
| 5   | `.gg/` vs no new folders vs SQLite      | [../references/project-layout-and-storage.md](../references/project-layout-and-storage.md) |
| 6   | When Vikunja arrives                    | operator decision (full pilot); [../references/vikunja-integration.md](../references/vikunja-integration.md) |
| 7   | `GG-01` backlog vs `GG-001` tests       | [../references/test-catalog.md](../references/test-catalog.md) (backlog cited as `B-01`..) |
| 8   | Kickoff says "1.6 supersedes 1.5"       | Stale label in the kickoff; v1.7 controls (handoff header); the source stays verbatim                                     |

## Workspace facts checked 2026-10-27

- Real folders: `project_stuff/apn/{enterprise-strategy,unified-network-controller,smc-resiliency}` (lower case).
- `apn/` is one Git repository holding all three projects (owner decision D1 in the pilot plan).
- `target-map.yaml` and `code-map.toml` exist in `unified-network-controller` and `smc-resiliency`.
- `.archcore/` exists in `enterprise-strategy` and `unified-network-controller`, not in `smc-resiliency`. No `.gg/` exists anywhere.
