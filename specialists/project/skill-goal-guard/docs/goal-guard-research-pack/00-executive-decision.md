---
Title: GoalGuard Research-Backed Implementation Decision
Category: design-decision
Status: proposed, not decided
Authority: research proposal; task-ownership sections superseded by the v1.7 handoff (Vikunja owns live tasks; operator, 2026-10-27)
Scope: GoalGuard v0.x architecture, authorities, product rules and go/no-go gates
Last reviewed: 2026-10-27
Summary: Recommends a portable skill plus deterministic policy CLI, an event journal and a later Vikunja projection; adds the Thekedar selective-extraction decision.
---

# GoalGuard — Research-backed implementation decision

Date: 2026-10-27 (Australia/Sydney)
Status: design proposal; **not** a deployed integration.
Baseline: `goalguard-v0.1.zip` and its README/CLI; do not mistake proposal capabilities for implemented functionality.

## Single recommendation

Create a small, portable GoalGuard skill and deterministic policy CLI as the **decision authority**, add an event journal with a single controlled writer, and then project a read-only task view into
**Vikunja 2.7+**. Only after evidence-based validation, enable mediated bidirectional updates. Add a recurring supervisor after that; add live agent/subagent telemetry last. This order prevents
GoalGuard becoming a feature-creep project itself.

**Do not fork** a complete project manager. Take interoperable ideas from existing projects only after verifying their licenses. Don't duplicate Vikunja's Kanban, Gantt, task API or MCP. The agent's
main purpose is to *reduce unnecessary work*, not produce more plans.

## Problem definition

One person works concurrently across UNC, SMC Resiliency, and ad-hoc jobs. Codex, Claude Code and other agents execute subtasks. The user needs one defensible recommendation for *what to do next*,
while agents can work on bounded tasks in parallel. Every action must trace to an approved outcome, an essential dependency or an authorized incident. New feature ideas are captured without changing
the MVP.

## Authorities

| Domain | Authoritative system | Notes |
|---|---|---|
| Goal, MVP, exclusions, acceptance criteria | GoalGuard signed/versioned contract | Human-owned changes only |
| Decision outcomes, exception approvals, drift classification | GoalGuard append-only journal | Every judgement cites evidence |
| Task execution state, dependencies, milestone edges | GoalGuard canonical store initially | Vikunja is a read projection during pilot |
| Kanban, lists, Gantt, filtering | Vikunja | Not evidence that an agent is running |
| Agent/subagent running state | Instrumented session telemetry | 'Unknown' when telemetry is missing/stale |
| Technical verification | Test/review artifacts | AI claims do not themselves prove completion |

## Nonnegotiable product rules

1. **One operator-level focus** at any moment, plus limited agent parallelism on independent, bounded tasks.
2. The system cannot unilaterally expand MVP scope, move committed external deadlines, rewrite the approved goal, or mark unverified work complete.
3. If a task is unnecessary for the current milestone, **park it with rationale**. Preserve ideas without executing them.
4. Distinguish **necessary repair/incident** from feature creep; fail-open for read-only inspection, fail-safe for irreversible or scope-expanding changes.
5. Every automatic block needs a human-readable reason and an override path with an audit record.
6. A project must always expose **task / project / portfolio What's Next**, including an explicit `BLOCKED` or `NO_ACTION` result when appropriate.
7. No fabricated schedule estimates or percent-complete; label confidence and evidence.

## Research findings that change the plan

- Vikunja ≥2.7: `/api/v2/mcp`, token permission presets and official instructions for Claude Code/Codex (https://vikunja.io/help/mcp/).
- Vikunja ≥2.4: `/api/v2`, PATCH, conditional requests, live OpenAPI (`/api/v2/openapi.json`), v1 migration strategy (https://vikunja.io/docs/api-v2/).
- Vikunja task relations: parent/subtask, blocking/blocked by, preceding/following, duplicate (https://vikunja.io/help/task-relations/).
- Vikunja saved filters can span projects; projects can be nested (https://vikunja.io/help/projects/).
- Webhooks have HMAC signatures but are sent **once** without retry; use periodic reconciliation (https://vikunja.io/docs/webhooks/).
- Vikunja is AGPLv3; a self-hosted installation can run in one container with bundled SQLite for pilot, or PostgreSQL for higher concurrency (https://vikunja.io/ and
  https://vikunja.io/docs/installing/).
- Plane's dedicated milestones are Pro, not FOSS CE (https://docs.plane.so/projects/milestones).
- Agent Skills is an open portable `SKILL.md` format, with scripts/references (https://github.com/agentskills/agentskills).
- Claude Code supports blocking synchronous PreToolUse hooks, but prompt-based semantic judgement is separate from deterministic enforcement
  (https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more).
- Codex documents hooks for SessionStart, UserPromptSubmit, PreToolUse, Stop and SubagentStop; asynchronous hooks cannot block operations (https://learn.chatgpt.com/docs/hooks).

## Recommended go/no-go decisions

- **Gate A:** Validate the goal contract using real UNC/SMC examples before writing integrations.
- **Gate B:** On a labelled drift evaluation set, reach at least 90% correct case dispositions with *zero* critical missed unauthorized changes. Treat thresholds as acceptance targets, not predicted
  performance.
- **Gate C:** Verify read-only Vikunja projection round-trips IDs and task edges before enabling writes.
- **Gate D:** Verify crash/concurrency/reconciliation recovery before autonomous operation.
- **Gate E:** Require demonstrated weekly time saved by the operator before adding observability UI.

## Cost and deployment

GoalGuard core: Python stdlib + SQLite (FOSS). Vikunja: self-hosted AGPLv3. Reuse existing Codex/Claude subscriptions; API charges are *not* inherently needed for agent-initiated operations, but an
unattended LLM supervisor needs an available inference backend (local model, already-authorized API, or another supported runtime). Do not claim a CLI subscription automatically grants unattended
external API use.

## v0.2 decision addendum — Thekedar extraction (2026-10-27)

**Decision:** Selective extraction, **not a fork**. Thekedar is an MIT-licensed coding execution-governance project: useful for edit-scope checks, per-task evidence, agent session resume and audit
records. Its hooks do *not* decide whether a task is necessary for the goal, its file scope can be self-expanded, its guards do not gate every shell write, and its own documentation warns of
concurrent-session races. Therefore GoalGuard remains the only authority for the approved MVP/priority/acceptance contract.

**Reference:** [06-Thekedar-Extraction-Matrix.md](06-thekedar-extraction-matrix.md) maps inspected upstream source paths to GoalGuard's existing CTPS IDs, adaptations, test cases and MIT reuse requirements. Additions are absorbed by M1
and M2 rather than generating a new release or workstream. Regression suite GG-401–425 is **specified, not implemented**. The baseline v0.1 CLI continues to have only its previously verified tests.

**Go/no-go amendment:** The semantic scope decision must distinguish (a) necessary MVP activity (including evidenced repairs) from (b) technically valid but optional activity **within the same allowed
source file**. No material contract revision or external deadline mutation may originate from untrusted agent task file edits. Hooks provide advisory/limited enforcement; the trusted writer owns
approvals. No Thekedar specialists, full orchestrator or new GUI are introduced.
