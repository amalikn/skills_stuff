# GoalGuard v0.1 — design specification and runnable prototype

**Purpose:** Keep a solo operator focused on outcomes and MVP delivery while simultaneously tracking long-running projects (e.g., UNC, SMC Resiliency) and operational ad-hoc tasks. Compatible in principle with any AI client that can read local files and run a CLI. No additional model API is needed for the deterministic prototype.

## Architecture decision

- **GoalGuard** = agent skill + independent, stdlib Python validation/priority/scope engine.
- **Portfolio JSON** = canonical structured record in v0.1. Store under a controlled, backed-up local directory. For shared multi-agent writes use transactional storage in a later phase.
- **Vikunja** = preferred optional FOSS visual layer, *not* the source of authority until bidirectional sync and conflict handling are proven. Official MCP available in Vikunja >=2.7. Version/edition and API permissions must be checked before deployment.
- **Agent activity ledger / live session observability** = optional later integration; a Kanban board does not prove an agent is running.
- **Schedulers** = optional later automation for regular checks. A skill isn't a daemon.

### Goals before tasks

Each project declares *why*, its measurable finish condition, its non-goals and an MVP boundary. Every task declares an outcome and acceptance criteria IDs. A task may link to a milestone with target/date, dependencies (including tasks in other projects), priority, next physical action and verification evidence. Cross-project dependencies require one consistent task namespace. Portfolio-level decisions set the relative priorities.

### Modes

| Mode | Required | Optional |
|---|---|---|
| Ad-hoc | goal, outcome, first action, priority | deadline, dependencies, proof, escalation |
| Long project | goal, success criteria, MVP boundary, tasks, milestones/targets/deadlines | critical path, risk register, reviews |
| Portfolio | projects, focus/WIP rule, priority order | cross-project dependencies, capacity calendar |

Ad-hoc items must not require a PRD or ceremony. If an ad-hoc item develops multiple dependencies or requires more than a short bounded effort, promote it to project level with human approval. Avoid duplicating a task in several projects.

### Hierarchical **What's Next**

1. **Task level:** a concrete next action; if blocked, list unmet task IDs; if done, verification evidence and next dependent task. Next action is not the same as a vague objective.
2. **Project level:** select an executable task among completed prerequisites, factoring in task priority, deadlines, WIP continuity and project goals. If none is ready, name the blocker/decision. State the next milestone and its due date separately.
3. **Portfolio level:** recommend **one** immediate focus across UNC, SMC and ad-hoc tasks. Preempt only for an explicit urgency/incident threshold or owner approval. Do not open a new project merely because there is spare agent capacity. Parallel *agents* can execute independently while the owner's cognitive focus remains one decision.

`next` in v0.1 implements a simple transparent scoring rule: started work +40; overdue +50, due <=2 days +35, due <=7 days +20; task priority ×10 and project priority ×5 (priority 1–5). It deliberately **does not claim to compute a critical path or resource schedule**. Ties are deterministic. Safety incidents and hard external commitments should be owner-defined overrides in production.

### Drift classifier and gates

Drift can be: **goal**, **MVP scope**, **priority**, **schedule**, **execution**, **decision**, or **research** drift. Each candidate action is checked for an approved criterion, necessary blocker and dependency readiness. Agent reasoning judges semantic necessity, supported by links to code, tests or project evidence. The deterministic checker verifies only references and scope flags; it cannot infer whether a claimed criterion is truthful.

Decision categories:
- **PROCEED**: valid task and satisfied dependencies; work traceable to approved criterion or explicitly recorded necessary blocker, with semantic check still required.
- **PARK**: optional idea without a justified MVP link; preserve in parking lot for future review.
- **REVIEW**: unclear scope, missing task, unmet dependency, or proposed scope expansion. Owner approves change when materially altering objectives, dates or budget.
- **STOP** (production policy, not implemented in prototype): verified prohibited activity or clearly revoked authorization, handled by tool-specific synchronous hooks.

**Important false-positive protections:** Reliability/security defects, necessary foundational dependencies, small bounded investigations, and emergency incidents should not be mislabeled feature creep. Classify and document the reason.

### Anti-tangent checkpoints

Before starting work ask:
1. Which accepted outcome or criterion does this advance?
2. What would fail if we skipped it?
3. Is it needed *now* to reach the agreed MVP?
4. What is the smallest sufficient action and stop condition?
5. What current priority/deadline does it displace?

When 1–3 have no convincing justification: park; do not implement. When disputed: give owner a one-line decision with cost, risk and fallback.

### Cross-project governance

- IDs globally unique (e.g. `UNC-1`, `SMC-1`, `OPS-1`). Explicit dependency edges can cross projects.
- Project-to-project dependencies are informational in v0.1; the executable scheduler uses **task-level** edges. Future releases should enforce project-level gates explicitly.
- Milestones are gates with measurable targets and due dates, not arbitrary buckets.
- Track blocked or overdue milestones separately from blocked tasks.
- Handle urgent ad-hoc interruptions by capturing the interruption reason, pausing the former task and returning focus after incident closure.
- One-person WIP default = **one in-progress task across the portfolio**. Multiple background agents may support that task or work independently only by explicit exception; agent count is not personal capacity.

### Visual strategy (Vikunja)

Recommended views:
- **Portfolio**: UNC, SMC, Ops; urgency/deadline, health, next action, blocked, parked.
- **Kanban**: Ready / In progress / Blocked / Review / Done / Parked.
- **Project timeline/Gantt**: milestones and deadlines (verify version support).
- **Focus**: a single top recommendation and reason; next per project and per task.
- **Agent activity**: desired future overlay (agent, parent session, subagent, assigned task, last heartbeat, evidence). Must use actual event/heartbeat telemetry, not merely task assignment.

Vikunja MCP supports agent task/project operations; verify the API fields for child tasks, dependencies and milestones before mapping. Keep one-way *read-only* dashboard sync initially. Later make task IDs immutable external IDs and use change versions/ETags or transactional reconciliation. Do not let two agents silently overwrite updates.

### Phase plan

**Phase 0 — contract and scenarios:** Define goals, non-goals, accepted MVP outcomes and realistic past tangents; classify expected allow/park/review behaviors.

**Phase 1 — portable skill + prototype (included):** JSON contract, validator, simple priority engine, drift gates, sample UNC/SMC/ad-hoc portfolio, unit tests. No daemon, no UI, no live agents.

**Phase 2 — integration:** Test native Codex/Claude hooks individually in advisory mode; add event ledger (task ID, agent/session ID, event timestamp, action/decision, evidence hash). Add safe read-only Vikunja visualization, avoid bidirectional sync initially.

**Phase 3 — autonomous supervision:** A local scheduler triggers review; detect overdue tasks, stagnant progress, agent drift and milestone slippage; propose recovery. Never silently change scope or deadlines. Require approval for interventions affecting scope or priorities.

**Phase 4 — visual agent tree:** Instrument actual Claude/Codex agent/subagent events and reconcile to task IDs. Expose `last_seen`, `running`, `needs_input`, `blocked`, `completed`; mark *unknown* when telemetry absent. Prefer existing observability tooling instead of inventing a custom dashboard until integrations are assessed.

### Required tests beyond v0.1

- Autonomous agent proposes future-proof abstraction unrelated to current MVP -> park.
- Required dependency looks like scope expansion -> allow with evidence.
- New user question is exploratory, not a directive -> park as idea.
- Critical security defect discovered -> review/allow essential repair, not park blindly.
- Multiple simultaneous sessions attempt one task -> concurrency conflict and dedupe.
- Task done without tests/evidence -> reject completion.
- Incomplete milestone after deadline -> schedule risk and proposed recovery.
- Deadline soon but prerequisite undone -> surface dependency as actual next action.
- Ad-hoc incident temporarily preempts project -> explicit pause, resume prior focus.
- Cross-project dependency cycle -> error.
- Stale activity telemetry -> status unknown, not falsely 'running'.

### Installation / use

Requires Python 3.9+. No pip dependencies.

```bash
python3 scripts/goal_guard.py validate --state examples/portfolio.json
python3 scripts/goal_guard.py next --state examples/portfolio.json --date 2026-10-27
python3 scripts/goal_guard.py assess --state examples/portfolio.json --proposal examples/proposal.json
python3 -m unittest discover -s tests -v
```

To try as a skill, place `SKILL.md` and supporting files under a directory discoverable by your installed agent, following its version-specific Agent Skills instructions. Do not install global hooks blindly. Enable advisory, then blocking behavior after tests and escape-hatch validation.

### Known limitations (explicit)

1. No live Vikunja synchronization, Kanban dashboard, autonomous scheduler or agent telemetry in this prototype.
2. Priority calculation is heuristic; doesn't estimate duration, critical path, slack or actual capacity.
3. Deadlines are parsed but no milestone slippage algorithm implemented; this belongs in Phase 2.
4. Scope assessment trusts *agent-supplied* `adds_scope` and criterion ID; malicious or confused agents could mislabel work. Independent semantic review is required before blocking decisions.
5. JSON writes require future locking/event journal for safe simultaneous agents. Start with read-only observer or one authorized writer.
6. Sample projects are illustrative, not verified real project state.

### Evaluation: go/no-go

Ship beyond prototype only if it correctly identifies genuine drift on a labeled set of actual cases, maintains <=1 owner-level active task by default, reduces unapproved features, provides one useful What's Next per task/project/portfolio, and doesn't routinely block necessary fixes. Review false positives, omissions, latency and manual overhead before choosing automation.

### Public sources consulted
- Vikunja MCP: https://vikunja.io/help/mcp/
- Vikunja docs: https://vikunja.io/docs/
- Claude hooks: https://claude.com/blog/how-to-configure-hooks
- Codex hooks: https://learn.chatgpt.com/docs/hooks
