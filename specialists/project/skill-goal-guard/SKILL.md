---
name: skill-goal-guard
description: >-
  GoalGuard (alias skill-gg): owner-approved MVP scope gate and solo portfolio focus for coding agents in project_stuff. Use before handing work to a
  coding agent, when an agent proposes new work or a design enlargement, to decide PROCEED / PARK / REVIEW / BLOCK against the approved MVP, to answer
  "what should I work on next" across apn and me projects from Vikunja, to trace a management milestone to an MVP criterion and a Vikunja task, or to
  check completion evidence ("is this in scope", "park this idea", "what should I work on now"). Not for brainstorming (left unrestricted), not a project
  manager (Vikunja owns live tasks), and never an approval source.
---

# GoalGuard

## Contents

- [Role and non-goals](#role-and-non-goals)
- [Orient first](#orient-first)
- [Route the task](#route-the-task)
- [Workflow at a handoff](#workflow-at-a-handoff)
- [The pack's tools](#the-packs-tools)
- [Related skills](#related-skills)
- [Output format](#output-format)
- [Standing rules](#standing-rules)
- [Standing write-back contract](#standing-write-back-contract)
- [Evidence and status](#evidence-and-status)

---

## Role and non-goals

GoalGuard keeps a one-person portfolio delivering small, tested MVPs: it checks every proposed piece of agent work against the owner-approved MVP contract, parks ideas without losing them, routes real
scope changes to the owner, and names one next action for the task, the project and the portfolio.

Non-goals: it does not own live tasks (Vikunja does), strategy (Enterprise-Strategy does) or technical rules (Archcore does); it never approves its own or an agent's scope change; it does not police
brainstorming; and a written rule or this file is not enforcement.

## Orient first

1. **Status.** Rules consolidated; pilot tools written 2026-10-27 (scope gate, What's Next, trace, snapshot/restore, Excel sample, doctor, draft hook), tested on fixtures only; Vikunja 2.7.1 runs
   locally (pilot step 0 done); no hook installed, nothing enforcing. Do not tell anyone a project is protected ([references/enforcement-and-hooks.md](references/enforcement-and-hooks.md)). Open live checks: [scripts/readme.md](scripts/readme.md) (Open
   checks). Pilot progress and owner decisions: [references/pilot-plan.md](references/pilot-plan.md).
2. Read the project's own `AGENTS.md`, Archcore rules and `.gg/` records (if any) first; project rules outrank this skill, but may not loosen an ancestor's scope, approval or privacy boundary.
3. Resolve the partition (`apn` or `me`) and stay inside it.
4. Find the approved MVP. None, draft or unreadable: scope-changing work is `BLOCK`; read-only inspection may continue.
5. For any code in this pack or an adapter, apply skill-coder.

## Route the task

| Task                                                                                      | Read                                          |
| ----------------------------------------------------------------------------------------- | --------------------------------------------- |
| Who owns which record; conflict order; trust levels                                       | [references/authority-and-sources-of-truth.md](references/authority-and-sources-of-truth.md) |
| Decide PROCEED / PARK / REVIEW / BLOCK; policy clause index                               | [references/decision-rules.md](references/decision-rules.md) |
| Write or change an MVP contract; planning exit; change requests; parked ideas; completion | [references/mvp-contract-and-change-control.md](references/mvp-contract-and-change-control.md) |
| What's Next for a task, project or the portfolio; ranking; interrupts                     | [references/whats-next-and-portfolio.md](references/whats-next-and-portfolio.md) |
| Hooks, Archcore rule, what is enforced vs advisory, Thekedar mechanisms                   | [references/enforcement-and-hooks.md](references/enforcement-and-hooks.md) |
| Vikunja: deployment, API, mapping, read and write stages                                  | [references/vikunja-integration.md](references/vikunja-integration.md) |
| Enterprise-Strategy hub, management baseline, the four dates, Excel                       | [references/hub-management-and-dates.md](references/hub-management-and-dates.md) |
| `.gg/` records, `target-map.yaml`, `code-map.toml`, storage, the shared `apn` repo        | [references/project-layout-and-storage.md](references/project-layout-and-storage.md) |
| Snapshots, offline read-only use, restore                                                 | [references/snapshot-and-restore.md](references/snapshot-and-restore.md) |
| Is a feature in scope for GoalGuard itself, and when                                      | [references/feature-inventory.md](references/feature-inventory.md) |
| The v1.7 pilot: steps, owner decisions, stop conditions                                   | [references/pilot-plan.md](references/pilot-plan.md) |
| Which tests gate what; duplicate test IDs                                                 | [references/test-catalog.md](references/test-catalog.md) |
| Closeout: record what this engagement taught                                              | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Workflow at a handoff

1. Read the approved MVP, relevant hub decisions (spokes) and the live Vikunja task.
2. Write the proposal: task ID, criterion or registered blocker, description, `adds_scope`, necessity rationale, smallest step, stop condition.
3. Decide in the order of [references/decision-rules.md](references/decision-rules.md); a matching criterion ID is not proof of relevance.
4. `PROCEED`: do only that. `PARK`: record the idea, keep the current task. `REVIEW`: state the trade-off and wait for the owner. `BLOCK`: name the clause and the remedy.
5. On completion, attach evidence per criterion; then recompute What's Next.

## The pack's tools

Run through `just` (pinned venv in the working-cache peer; `just bootstrap` once). Catalogue: [scripts/readme.md](scripts/readme.md).

| Recipe                                                | What it does                                                                     | Safety              |
| ----------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------- |
| `just validate [project]`                             | Check a project's `.gg/` records, the hash chain and the baseline                | read-only           |
| `just assess [proposal] [project] [tasks]`            | PROCEED / PARK / REVIEW / BLOCK in the order of decision-rules.md                | read-only           |
| `just assess-apply proposal project`                  | Same against live Vikunja, and append the verdict to `.gg/decisions.jsonl`       | writes one log line |
| `just next [project] [tasks] [date]`                  | Task, project and portfolio What's Next (`next-live` reads Vikunja)              | read-only           |
| `just vikunja-info`, `just vikunja-tasks id`          | Instance version; one project's tasks                                            | read-only           |
| `just trace [project] [tasks]`                        | Milestone → plan revision → criteria → target map → tasks                        | read-only           |
| `just snapshot-export project`, `-verify`, `-restore` | Snapshot with manifests, verify, clean-instance restore (`-apply` recipes write) | plan by default     |
| `just excel project out`                              | Management workbook sample (`excel-apply` writes the file)                       | plan by default     |
| `just doctor [project]`                               | Enforced versus advisory paths, hook wiring, captures                            | read-only           |
| `just hook-test payload [mode]`                       | Feed a payload to the draft PreToolUse hook                                      | read-only           |
| `just check`                                          | ruff, 71 tests, skill-coder helpers, fixture validate and trace                  | read-only           |

Where a tool's output and a reference disagree, the reference wins and the tool is fixed.

Vikunja itself is run from `/Volumes/Data/_ai/_tool/tools_stuff/vikunja` (`just up`, `just status`, `just doctor`, `just dump`; README there), not from this pack.

## Related skills

- **skill-coder** — practice for any code in this pack or a GoalGuard adapter (required).
- **skill-smc**, **skill-cambium** — domain facts for the SMC and UNC pilot work GoalGuard gates; GoalGuard decides whether work is in scope, never how the device behaves.
- **skill-walk-before-run** — when a GoalGuard proposal is itself expansion on an unverified assumption.

## Output format

- **Now**: one next physical action, its Vikunja ID, why.
- **Project next**: each active project's next ready task, or why none.
- **Task next**: the next action for the task in focus.
- **At risk**: commitments, internal targets, blockers, stale authority, unapproved expansion.
- **Parked**: ideas deferred this session.
- **Needs decision**: owner-level trade-offs only.

## Standing rules

- An agent, a model, a Vikunja task or a task file never approves scope; only an authenticated owner decision naming the revision does.
- Fail open for read-only inspection, closed for scope-changing or protected writes.
- Never copy Vikunja task state, target-map content or hub documents into GoalGuard records; reference them by ID, path and revision.
- Never move a management commitment; record variance instead.
- Keep `apn` and `me` apart.
- Claim enforcement only for an observed block on a supported hook; everything else is reported as advisory.
- Never fabricate estimates, forecasts or percent complete; say `unknown`.

## Standing write-back contract

A session that gated, ranked, traced or changed GoalGuard work owes, at closeout, a dated Learned entry in the reference a future reader would open plus one line under `## Unreleased` in [changelog.md](changelog.md),
with a code excerpt or screenshot as evidence; if this pack cannot be written, park the entry in the project under `## skill-goal-guard write-back candidates`. Format:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).

## Evidence and status

The references consolidate the source documents kept verbatim under [docs/](docs/catalog.md): the v1.7 handoff and kickoff, the v0.x research pack, and the v0.1 skill and readme. Each reference cites its sections. Live
captures are under [documents/](documents/) (Vikunja 2.7.1 OpenAPI and info, 2026-10-27). Hook capabilities stay `UNVERIFIED` until the pilot inventory captures real payloads.
