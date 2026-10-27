---
Title: GoalGuard Feature and Idea Inventory
Category: reference
Status: current
Authority: consolidated from every source document; dispositions follow the operator decisions of 2026-10-27 (Vikunja authority, full v1.7 pilot)
Scope: Every feature and idea proposed across the handoff, research pack, Thekedar matrix and v0.1 prototype, with one disposition each
Last reviewed: 2026-10-27
Summary: >-
  One table of 53 features and ideas, each marked Pilot, Later (L1-L5), Parked or Rejected, with its source; the pilot set is the v1.7 kickoff
  scope and nothing outside it is built until its gate passes.
---

# Feature and idea inventory

**Dispositions.** `Pilot` = in the v1.7 pilot ([pilot-plan.md](pilot-plan.md)). `L1`..`L5` = later phases, in order, each behind a gate. `Parked` = kept, no plan to build until a need is shown. `Rejected` = decided
against. GoalGuard applies its own rule here: a feature enters a phase only when it advances that phase's acceptance tests.

## Phases after the pilot

| Phase | Theme                                                                                           | Gate to enter                                                                              |
| ----- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| L1    | Second agent and resilience: Codex adapter, session brief, interrupt/resume, second spoke       | Pilot report PASS; owner approval                                                          |
| L2    | Durable observation and Vikunja writes: SQLite journal, leases, webhooks, mediated              | L1 PASS; read-only projection round-trips IDs and edges (pack 00 Gate C)                   |
|       |   writes, views                                                                                 |                                                                                            |
| L3    | Supervision: scheduled deterministic reviews, slip reports, weekly report                       | Crash, concurrency and reconciliation recovery proven (Gate D)                             |
| L4    | Semantic critic: independent model judgement with citations, offline fallback                   | ≥90% disposition agreement and zero missed critical expansions on ≥40 labelled cases       |
|       |                                                                                                 |   (Gate B)                                                                                 |
| L5    | Agent telemetry and hardening: live agent tree, backups, benchmarks                             | Measured weekly time saved (Gate E)                                                        |

## Inventory

| #   | Feature or idea                                                                                      | Source                       | Disposition                                 |
| --- | ---------------------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------- |
| 1   | MVP contract with criteria, exclusions, NOT-in-scope, approval                                       | handoff §5, pack 06          | Pilot                                       |
| 2   | Owner approval and append-only baseline revisions                                                    | handoff §8, MVP-011          | Pilot                                       |
| 3   | `assess` with PROCEED/PARK/REVIEW/BLOCK and reason codes                                             | handoff §7, pack 02          | Pilot (rewrite of prototype)                |
| 4   | Deferred-ideas register                                                                              | handoff §10                  | Pilot                                       |
| 5   | Completion and evidence gate with completion record                                                  | handoff §6E, pack 06         | Pilot                                       |
| 6   | Fail closed on missing or unreadable baseline                                                        | MVP-012, T11                 | Pilot                                       |
| 7   | Agent-recorded necessity rationale per proposal                                                      | pack 02, 05 B-03            | Pilot                                       |
| 8   | Independent semantic critic                                                                          | pack 02 C18, 05 B-18        | L4                                          |
| 9   | File-scope allowlist with path canonicalisation (second line)                                        | pack 06 scope-guard          | L1                                          |
| 10  | Claude Code PreToolUse adapter, advisory then blocking                                               | handoff §12, pack 02 C10     | Pilot                                       |
| 11  | Codex adapter with `apply_patch` parsing                                                             | pack 02 C11, GG-413          | L1                                          |
| 12  | Minimal doctor: report enforced vs advisory paths                                                    | F14, GG-421                  | Pilot (minimal); full doctor L1             |
| 13  | Session-start brief and revalidation                                                                 | handoff §32.6, GG-414        | L1                                          |
| 14  | Three-level What's Next from Vikunja                                                                 | handoff §17, pack 01 M1      | Pilot                                       |
| 15  | Deterministic ranking pipeline                                                                       | handoff §17.3                | Pilot                                       |
| 16  | Weighted priority score                                                                              | v0.1 prototype               | Rejected (until trials show ordering fails) |
| 17  | One operator focus, WIP validation                                                                   | PORT-004                     | Pilot                                       |
| 18  | Interrupt/resume with checkpoint                                                                     | pack 02 C07, P10             | L1                                          |
| 19  | Ad-hoc to project promotion                                                                          | GG-112                       | L1                                          |
| 20  | Local Vikunja deployment and OpenAPI inventory                                                       | operator 2026-10-27, pack 04 | Pilot (operator deploys)                    |
| 21  | Read-only Vikunja task and relation fetch for one project                                            | handoff §17.2                | Pilot                                       |
| 22  | ID mapping (`mappings.yaml`)                                                                         | handoff §36.2, pack 04       | Pilot                                       |
| 23  | Saved filters, Kanban and Gantt conventions                                                          | pack 04, 05 B-15            | L2                                          |
| 24  | Signed webhook inbox and poll reconciliation                                                         | pack 04 stage B              | L2                                          |
| 25  | Mediated Vikunja writes (status, notes)                                                              | pack 04 stage C              | L2                                          |
| 26  | Bidirectional sync of protected fields                                                               | pack 04                      | Rejected                                    |
| 27  | Vikunja MCP for agents, read-only token                                                              | pack 00, 04                  | L2                                          |
| 28  | Hub registration and freshness read receipt                                                          | handoff §22.2                | Pilot (one hub, one spoke)                  |
| 29  | Cross-project impact proposals to the hub                                                            | handoff §22.2                | L1                                          |
| 30  | AI-inferred cross-project dependencies                                                               | handoff §22.2, H05           | Parked (candidates only)                    |
| 31  | Protected management baseline reference for one milestone                                            | handoff §23, §25             | Pilot                                       |
| 32  | Owner internal target stored separately                                                              | DATE-002                     | Pilot                                       |
| 33  | Forecast with `unknown` when data is missing                                                         | DATE-003                     | Pilot (rule only)                           |
| 34  | One generated management Excel sample                                                                | handoff §25.1, D09           | Pilot                                       |
| 35  | Retire Markdown operational scheduling after cutover                                                 | handoff §25.1                | L2 (gated)                                  |
| 36  | OpenProject Community fallback                                                                       | handoff §27                  | Parked (exit gate only)                     |
| 37  | Root / partition / project policy resolution                                                         | handoff §18.2, §32           | Pilot (root, `apn`, one project)            |
| 38  | `apn` / `me` isolation                                                                               | PORT-005                     | Pilot (tested denial)                       |
| 39  | Archcore rule in the pilot project                                                                   | handoff §9, §28              | Pilot                                       |
| 40  | Read-only `target-map.yaml` / `code-map.toml` trace                                                  | handoff §36                  | Pilot                                       |
| 41  | GoalGuard maintaining target maps                                                                    | handoff §36                  | Parked                                      |
| 42  | One project snapshot, manifest, dry-run and clean restore                                            | handoff §37, kickoff         | Pilot                                       |
| 43  | Full Vikunja disaster recovery inside GoalGuard                                                      | handoff §37.5                | Rejected (instance backup instead)          |
| 44  | SQLite observation journal, single writer, leases                                                    | pack 02 C09                  | L2                                          |
| 45  | Task-start Git baseline drift audit                                                                  | pack 06 drift-check          | L2                                          |
| 46  | Bounded fix-loop budget                                                                              | pack 06, GG-420              | L2                                          |
| 47  | Scheduled reviews, slip reports, weekly report                                                       | pack 02 C17/C19, 05 B-17/B-19 | L3                                          |
| 48  | Live agent/subagent telemetry and tree                                                               | pack 00, readme Phase 4      | L5                                          |
| 49  | Guarded vs unguarded benchmark                                                                       | GG-424                       | L5                                          |
| 50  | Custom UI or dashboard, swarm executor, model router, probabilistic forecasting, several PM backends | pack 01, 05                  | Rejected until a need is shown              |
| 51  | Thekedar orchestrator, specialist catalogue, reviewer pipeline                                       | pack 06                      | Rejected                                    |
| 52  | Knowledge Curator changes                                                                            | handoff §10, §15             | Rejected                                    |
| 53  | Restricting brainstorming                                                                            | handoff §2                   | Rejected                                    |
