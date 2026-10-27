# goal-guard-research-pack

Research proposal for GoalGuard (v0.x line, 2026-10-27): architecture decision, roadmap, work register, tests, Vikunja design, backlog and the Thekedar extraction. All files are `proposed, not
decided`. Where they say GoalGuard owns live task state and Vikunja is only a projection, the v1.7 handoff ([../goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md](../goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md)) controls: Vikunja owns live tasks
(operator, 2026-10-27).

This readme replaced a byte-identical copy of `00-executive-decision.md` (2026-10-27); no content was lost.

## Catalog

| File                             | Category           | What it holds                                                                                    | IDs defined                               |
| -------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| [00-executive-decision.md](00-executive-decision.md) | design-decision    | Single recommendation, authorities, product rules, research findings, gates A-E,                 | Gates A-E                                 |
|                                  |                    |   Thekedar decision                                                                              |                                           |
| [01-milestones-and-roadmap.md](01-milestones-and-roadmap.md) | roadmap            | M0-M5 deliverables, acceptance and effort (70-120 h)                                             | M0-M5                                     |
| [02-ctps-implementation.md](02-ctps-implementation.md) | plan               | Component/task register, sequence, priority rules, data design, decision classes                 | C01-C20                                   |
| [03-acceptance-test-matrix.md](03-acceptance-test-matrix.md) | test-matrix        | Decision, portfolio, robustness, Vikunja and Thekedar-derived tests; release gates               | GG-001..GG-425                            |
| [04-vikunja-integration-design.md](04-vikunja-integration-design.md) | integration-design | Entity mapping, API v2/MCP, sync stages A-C, deployment, security                                | Sync stages A-C                           |
| [05-implementation-backlog.md](05-implementation-backlog.md) | backlog            | Sprints A-D for Codex/Claude Code                                                                | GG-01..GG-19 (backlog items, not          |
|                                  |                    |                                                                                                  |   GG-0xx tests)                           |
| [06-thekedar-extraction-matrix.md](06-thekedar-extraction-matrix.md) | source-extraction  | Thekedar (MIT) mechanisms to adapt, mandatory adaptations, licence duties                        | none new                                  |

## Reading order

`00` for the decision, `01` and `02` for sequencing, `03` for what must pass, then `04`-`06` as needed.
