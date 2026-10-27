---
name: goalguard
description: Goal-oriented MVP scope control and solo portfolio focus for ad-hoc tasks and long projects.
---

# GoalGuard skill

## Activate when
The user asks to plan, execute, review, prioritize, or update project/portfolio tasks, or to determine whether an agent's proposed work is necessary.

## Authority and constraints
- The human owner sets goals, MVP scope, targets, dates, and approves changes. Agents must not silently amend them.
- The project state file is authoritative for work tracking; source code and logs are evidence, not automatically task completion.
- Do not confuse discussing an idea with approval to implement it.
- Never silently spawn work or change another project's priority.
- A new feature or architecture must map to an accepted criterion or necessary registered blocker; otherwise park it and ask only if urgent.
- Avoid feature creep, but never suppress safety/security/reliability defects required for the MVP. Record and escalate rather than silently ignore.

## Required workflow
1. Read the portfolio state and call `scripts/goal_guard.py validate --state <path>`.
2. Use `next` to report: *task next action*, *each project's next ready task*, and *one portfolio-wide focus*.
3. Before nontrivial new work, write a proposal including task_id, criterion_id or necessary_blocker_id, description, adds_scope. Call `assess`.
4. If `proceed`, still evaluate semantic relevance to the criterion; don't treat a matching ID as proof.
5. If `park`, record the idea without changing the plan. If `review`, surface the trade-off and wait for owner authorization.
6. Start only the approved task. Keep portfolio WIP at 1 by default; planned parallel background agents must still have explicit task assignments and owner-approved concurrency.
7. At task completion, check each criterion with actual evidence, update state and calculate next again.
8. On any deadline breach, blocked dependency, new requirement, or stale task, produce a concise impact report and recommended recovery action.
9. Distinguish scoped investigation (bounded question and stop condition) from open-ended research.

## Output format
- **Now**: single best next physical action, ID, reason.
- **Project next**: each active project's next ready task; blocked reason if none.
- **Task next**: next action for the task in focus.
- **At risk**: dates, blockers, divergence, unapproved expansion.
- **Parked**: opportunities deferred without changing MVP.
- **Needs decision**: only owner-level trade-offs.

## CLI
`python3 scripts/goal_guard.py validate --state examples/portfolio.json`
`python3 scripts/goal_guard.py next --state examples/portfolio.json --date 2026-10-27`
`python3 scripts/goal_guard.py assess --state examples/portfolio.json --proposal examples/proposal.json`

## Important
This is an agent guidance skill plus prototype rules engine, not a background worker or a ready-made Vikunja connector. AI agents must execute the workflow, and hook integrations should be tested individually.
