---
Title: GoalGuard Milestones and Release Gates
Category: roadmap
Status: proposed, not decided
Authority: research proposal; Vikunja placement at M3 conflicts with the v1.7 pilot scope
Scope: M0-M5 milestone gates, deliverables, acceptance and effort ranges
Last reviewed: 2026-10-27
Summary: Six outcome-based gates from contract freeze to hardening, estimated at 70-120 h, with a Thekedar refinement inside M1/M2.
---
# Detailed milestones and release gates

**Scheduling assumption:** Weeks are *relative to project start*, not committed calendar dates. Engineering estimates are ranges and must be refined after pilot evidence. This is **one person's** side
project, so calendar duration depends on focused hours available. Every milestone is outcome-based, not feature-count-based.

| Gate | Target period | Output | Exit test | Estimated effort |
|---|---|---|---|---:|
| M0 Contract freeze | W1 | Objective, MVP boundaries, acceptance IDs, priority policy, real drift cases | Operator explicitly approves baseline | 6–10 h |
| M1 Reliable goal guard | W2–3 | Validated task/dependency model, preflight scope decisions, 3-level What's Next | Regression set passes; correct reason and next action | 16–24 h |
| M2 Agent evidence/advisory | W4–5 | Codex/Claude session hooks, evidence journal, controlled writer | No dropped/doubled task change; no unsafe hidden scope edits | 12–20 h |
| M3 Visual pilot | W6–7 | Vikunja read-only projection, filters, Kanban, Gantt conventions | Reconciliation consistency and manual audit pass | 12–20 h |
| M4 Autonomous oversight | W8–9 | Scheduled deterministic reviews, optional LLM semantic assessment, drift/risk alerts | Idempotent alerts and coherent recoveries with approvals | 16–24 h |
| M5 Hardening and decision | W10+ | Backup/restore, security tests, incident/runbook, usage evaluation | Restore exercised; benefit exceeds admin burden | 8–12 h |

Total indicative direct implementation: **70–120 engineering hours**, excluding substantial real-case analysis and changes required by external SDK/version instability. A strict 10-week calendar
requires 7–12 dedicated h/week; otherwise adjust the calendar, not the gates.

## Contents

- [M0 — contract freeze](#m0--contract-freeze)
- [M1 — goal and What's Next MVP](#m1--goal-and-whats-next-mvp)
- [M2 — agent adapters](#m2--agent-adapters)
- [M3 — Vikunja visual pilot](#m3--vikunja-visual-pilot)
- [M4 — autonomous reviewer](#m4--autonomous-reviewer)
- [M5 — hardening and benefit assessment](#m5--hardening-and-benefit-assessment)
- [Deliberately deferred](#deliberately-deferred)
- [v0.2 integration refinement: Thekedar execution patterns (2026-10-27)](#v02-integration-refinement-thekedar-execution-patterns-2026-10-27)

---

## M0 — contract freeze

CTPS: objective -> measurable outcomes -> exclusions -> model -> real scenarios -> approve.

Deliverables:
- Versioned `goal-contract.yaml` for each long project with explicit finish-line and non-goals.
- `ad-hoc` compact contract: outcome, reason, next action, urgency, stop condition and optional deadline.
- Portfolio context: one-person capacity, project policy priorities, interrupt/resume rules.
- Golden labels on real examples: `PROCEED`, `PARK`, `REVIEW`, `BLOCK` with explanatory evidence.

Acceptance:
- Every initially active task maps to an accepted criterion or an explicitly authorized operational exception.
- No question-only exploration is silently converted into implementation scope.
- Distinguish fixed *external deadline* from tentative internal target.

## M1 — goal and What's Next MVP

Deliverables:
- Unique IDs; goals, criteria, milestones, tasks, subtasks and edges, status/evidence fields.
- Acyclic cross-project task dependencies and detection of missing references.
- Explicit `READY`, `BLOCKED`, `ACTIVE`, `WAITING_APPROVAL`, `DONE`, `PARKED` semantics.
- Task next action; project next ready task and next milestone; portfolio one focus + alternatives and explainable preemption.
- Scope classifier interface plus deterministic validator; never trust an agent's self-asserted necessity as sole proof.

Acceptance:
- One proposed operator focus or a reason why there is none.
- Candidate not necessary to goal is parked without touching accepted contract.
- A genuine blocking security/reliability repair can proceed through controlled exception.
- Work marked Done requires required evidence.
- Ranking is deterministic and rationale is replayable.

**Stop here and use it for a real project before adding features.**

## M2 — agent adapters

Deliverables:
- Native hook adapters for Codex and Claude only; local CLI works without hooks.
- Preflight uses approved contract version and immutable current task ID.
- Observation journal: provider, agent/session ID, parent agent ID (if available), task ID, event type, timestamp, evidence URI/hash, policy verdict, version.
- Single controlled writer: SQLite transactions + optimistic revision on task update; duplicate event keys deduplicated.
- End-of-session summary and interrupted-task checkpoint.

Acceptance:
- Unknown task assignment produces `REVIEW`, never an invented task.
- Simultaneous writes cannot silently clobber one another.
- Hooks never transmit project data to a third party by default.
- Critical blocked operation is explainable and reversible by human approval.

## M3 — Vikunja visual pilot

Deliverables:
- Confirm installed Vikunja version ≥2.7 and inspect `/api/v2/openapi.json` for actual instance fields/routes.
- Authenticated read/limited-write service accounts and token rotation.
- Materialized task projection with immutable GoalGuard ID present in task description or an integration mapping table.
- Saved portfolio filters: `Current Focus`, `Ready`, `Blocked`, `Approval Needed`, `Overdue`, `Parked`.
- Per-project Kanban and Gantt conventions; structured milestone tasks with `milestone` label while ensuring dates/criteria remain canonical in GoalGuard.
- Webhook signature validation, deduplication and scheduled reconciliation.

Acceptance:
- Relation directions and cross-project task mapping correct.
- Re-import is idempotent and never duplicates tasks.
- Editing a protected target in Vikunja does not silently change GoalGuard's approved scope.
- UI never conflates assignee with current live agent activity.

## M4 — autonomous reviewer

Deliverables:
- Scheduled reviews and deterministic triggers: milestone due soon, slipped blocker, no verified activity, priorities displaced, new scope proposal.
- Optional semantic critic with independent evaluation context, bounded tokens/cost and evidence citations.
- Suggested smallest recovery action and owner approval queue.
- Interrupt/resume semantics for urgent ad-hoc operational tasks.

Acceptance:
- Report includes current approved objective, deviation, evidence, impact, and recommendation.
- Repeated runs generate no duplicate alerts for same unresolved event.
- Without model inference, deterministic checks and scheduler still work.
- No autonomous unapproved mutation of goals, scope, external deadlines or approvals.

## M5 — hardening and benefit assessment

Deliverables:
- DB and Vikunja backup and restore scripts, restore drill results, corrupt-event quarantine.
- Auth/scoping tests, telemetry freshness checks, API throttling, degraded-mode behavior.
- Weekly solo dashboard: one focus, closest milestone, tasks blocked, reviewer decisions, optional work deliberately parked.
- User feedback measure: time spent planning per week before/after.

Acceptance:
- Forced crash at journal write or webhook delivery recoverable through replay and reconciliation.
- No unapproved protected changes over pilot.
- Operator finds the recommended focus consistently useful without excessive false alarms.

## Deliberately deferred

Custom web UI, probabilistic critical-path prediction, automatic code changes by the PM agent, full-time agent orchestration, more than one project manager backend, and integration into unrelated
services. Must pass an evidence-based need gate before adding any.

## v0.2 integration refinement: Thekedar execution patterns (2026-10-27)

This is a **refinement of M1/M2**, not an extra phase or a separate project. Reuse reference source files via [06-Thekedar-Extraction-Matrix.md](06-thekedar-extraction-matrix.md).

- **M0:** task format adds explicit *NOT in scope* and acceptance criteria (optional file list for coding projects). Owner still owns goal/targets/deadlines.
- **M1 / C05+C08:** semantic MVP relevance checked **before** file allowlist. Add path canonicalization tests and self-authored-scope counterexamples. Nontrivial work with no approved task yields
  review, not implicit permission. Include legitimate necessary repairs.
- **M2 / C09–C12:** facts-only activity ledger with task/session IDs, source event idempotency, session brief, independent completion verification, baseline-based code-drift audit and bounded retries.
  Concurrent sessions cannot directly edit authoritative state.
- **M3–M5:** unchanged deliverables; use drift evidence/journal to populate *existing* Vikunja projection and scheduled reviews. No new UI or Thekedar agent catalogue.

**Required no-go:** reject any version in which an agent can amend material MVP scope simply by editing its task Markdown or where the only proof of conformity is an allowed file path. The 'no extra
project' constraint applies to all extracted features.

**Effort effect:** The original phase estimates remain provisional; adaptation of useful patterns may reduce design effort but multi-agent integrity and hook fixture validation could increase test
effort. Do not claim the overall 70–120 h estimate is more precise without measured implementation results.
