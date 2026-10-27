---
Title: GoalGuard Project Layout and Storage
Category: reference
Status: current
Authority: >-
  consolidated from the v1.7 handoff §5, §18, §30-37 and research pack 02 (C09) and 06; workspace facts read on disk 2026-10-27; conflict 5 (storage)
  settled here
Scope: The skill package, .gg/ records per level, existing target-map.yaml and code-map.toml, runtime state placement, and the shared apn repository
Last reviewed: 2026-10-27
Summary: >-
  One canonical skill package; small reviewable .gg/ records holding references, approvals and decisions; volatile state and caches outside the
  repos; target-map.yaml and code-map.toml read only. The apn projects share one Git repository, which the per-project design must account for.
---
# Project layout and storage

## Workspace facts (read 2026-10-27)

| Fact                                                                                                | Consequence                                                                                    |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Root is `/Volumes/Data/_ai/_project/project_stuff`; it holds `apn/`, `me/` and other folders        | The two-partition model (`apn`, `me`) does not cover everything; unregistered folders are      |
|   (`aws/`, `governance/`, ...)                                                                      |   simply not governed                                                                          |
| `apn/enterprise-strategy`, `apn/unified-network-controller`, `apn/smc-resiliency` are lower case    | Use the real names in every config; the documents' `APN/UNC/...` spellings are illustrative    |
| **`apn/` is one Git repository** containing all three projects                                      | See "Shared repository" below                                                                  |
| `target-map.yaml` and `code-map.toml` exist in UNC and SMC; not checked in Enterprise-Strategy      | Read them in place                                                                             |
| `.archcore/` in Enterprise-Strategy and UNC, not in SMC                                             | The Archcore rule path does not exist for SMC yet                                              |
| No `.gg/` anywhere                                                                                  | Nothing to migrate; create only what the pilot needs                                           |
| No `me` project is registered with GoalGuard | `me` portfolio work starts after the pilot (L1, second context); isolation is still tested in the pilot |

## Shared repository (operator, 2026-10-27: keep one repository, scope by path)

The handoff assumes each project is its own repository with its own rules, decision log and hook (handoff §18, F04, P08). In the shared `apn` repository: a hook or rule set up for UNC may fire for
every `apn` project; an agent working in UNC can read the hub's files directly; one commit can mix approval records from several projects. Decision: keep the one repository; scope hooks, rules and `.gg/` records by project path inside it, keep one decision log per project folder, and keep approval commits to one project each ([pilot-plan.md](pilot-plan.md), D1).

## Skill package

This pack is the one canonical GoalGuard implementation (handoff §30.1): `SKILL.md`, `references/`, `scripts/`, `tests/`, `examples/`, later `schemas/` and adapters. Projects never copy its code or
hold a writable database.

## `.gg/` records (pilot creates only what it needs)

| Level                 | Records                                            | Holds                                                                                  | Never holds                    |
| --------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------ |
| `project_stuff/.gg/`  | `config.yaml`, `policy.yaml`, `portfolios.yaml`    | Policy IDs, inheritance pointers, portfolio registry                                   | Live task copies               |
| `apn/.gg/`, `me/.gg/` | `config.yaml`, `projects.yaml`, `priorities.yaml`  | Membership, access partition, ranking **rules**                                        | Priority values, APN data      |
|                       |                                                    |                                                                                        |   in `me`                      |
| Hub project `.gg/`    | `project.yaml`, `hub.yaml`, `links.yaml`           | Hub role, approved relations, revision acknowledgements                                | Copies of hub documents        |
| Spoke project `.gg/`  | `project.yaml`, `mvp.yaml`, `mappings.yaml`,       | Identity, approved contract, references to target-map/code-map/milestones/Vikunja IDs, | Target-map content, task       |
|                       |   `decisions.jsonl`,                               |   decisions, parked ideas                                                              |   state, secrets               |
|                       |   `deferred.yaml`, `snapshots/manifest.json`       |                                                                                        |                                |

All names are proposals (handoff §37.1); existing `AGENTS.md`, Archcore and project conventions win. Handoff §5 ("no new folder convention solely for this policy") and §30-37 (`.gg/`) disagree; the
consolidated rule: `.gg/` is created only after the pilot inventory shows no existing equivalent, and only the files the pilot uses.

## Two logs, two places (settles pack vs handoff)

- **Decisions and approvals** — `decisions.jsonl` in the project's `.gg/`, append-only, small, reviewed in Git (handoff §31): what was decided, by whom, against which revision.
- **Observations** — agent events, leases, deduplication keys, the outbox: a SQLite journal with a single writer and optimistic revisions (pack 02 C09), outside every repository. Not in the pilot.

## Runtime, data and cache placement

| Kind                                                                 | Place                                                                                                   |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Venv                                                                 | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-goal-guard/.venv` (`just bootstrap`)              |
| Logs, pid files, sockets                                             | `/Volumes/Data/_ai/_skills/skills-runtime/skill-goal-guard/{logs,run}/`                                 |
| Durable state (SQLite journal, large or sensitive snapshot payloads) | `/Volumes/Data/_ai/_skills/skills-data/skill-goal-guard/` (proposed; follows the storage-routing guide) |
| Tokens                                                               | Secret store, never files in a repo                                                                     |

Add narrow `.gitignore` entries for local state, never `/.gg/` wholesale (handoff §33). A `.gg/` manifest may point to an external payload when Git is the wrong place for it (handoff §37.3.6).

## Existing maps (handoff §36)

- `target-map.yaml`: the project's target catalogue. A target is a candidate, not approval; it may be executed only when it maps to the approved MVP. Read-only in the pilot; changes produce a
  reconciliation proposal; its existing writer stays its writer.
- `code-map.toml`: the scripts index. Evidence for impact analysis; never permission. If tooling regenerates it, use that flow.
- `mappings.yaml` stores `target_source_ref`, `target_id` (only if the map provides one), `target_source_revision`, `mvp_baseline_id`, `acceptance_criterion_id`, `vikunja_task_id` (once approved). No
  invented IDs; propose an ID strategy to the owner when the map has none.

## Lifecycle (handoff §33)

Enrol with a dry-run inventory before creating files; register stable IDs and type (`hub` / `spoke` / `standalone`); approvals append-only; volatile state external with atomic writes and locking;
stable IDs survive renames; two roots claiming one ID is an error; unregister only by owner action with archival.

## Path safety

Normalise and resolve paths; reject traversal, glob tricks and symlink escapes; an unresolvable target is REVIEW, not approval (GG-404, GG-405, F12).
