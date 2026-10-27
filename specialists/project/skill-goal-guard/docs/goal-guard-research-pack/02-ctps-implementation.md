---
Title: Goal Guard CTPS Execution Register
Category: plan
Status: proposed, not decided
Authority: research proposal; task-ownership sections superseded by the v1.7 handoff (Vikunja owns live tasks; operator, 2026-10-27)
Scope: Component/task register C01-C20, sequencing, priority rules, data design and decision classes
Last reviewed: 2026-10-27
Summary: Stable work IDs C01-C20 with dependencies and effort, the minimal execution path and the policy classification model.
---

# CTPS — Components, Tasks, Priorities, Sequence

Use this as the execution register. IDs are stable, globally unique. `Blocked by` is an engineering ordering constraint, not a claim of completed implementation.

| ID | Component / Task | Priority | Depends on | Outputs / checks | Effort |
|---|---|---|---|---|---:|
| C01 | Freeze MVP goals, exclusions, acceptance IDs | P0 | — | Versioned human-approved contracts | 3–5 h |
| C02 | Label genuine drift/necessary-work scenarios | P0 | C01 | Golden eval corpus, including difficult counterexamples | 3–5 h |
| C03 | Normalize schema for tasks, milestones, target/due dates, exceptions | P0 | C01 | Explicit schema + validation | 4–6 h |
| C04 | Model task/project and cross-project edges | P0 | C03 | Missing edge/cycle tests | 3–5 h |
| C05 | Core scope checker | P0 | C02,C03 | Deterministic policy, evidence request, approval routing | 4–6 h |
| C06 | Hierarchical What's Next | P0 | C03,C04 | Task, project, portfolio focus + reasons | 5–8 h |
| C07 | Portfolio interruption/resumption state | P0 | C06 | Pause, urgent ad-hoc, resume current context | 3–5 h |
| C08 | Eval/test harness and CLI UX | P0 | C02,C05,C06 | Tests + explainable JSON/human output | 4–6 h |
| C09 | SQLite journal + migrations | P1 | C03 | Transactional single-writer state, dedupe | 4–7 h |
| C10 | Claude hook adapter | P1 | C05,C09 | Advisory then blocking with opt-out safety | 3–5 h |
| C11 | Codex hook adapter | P1 | C05,C09 | Same contract semantics; test real hook payloads | 3–5 h |
| C12 | Evidence ingestion and attestation | P1 | C09 | Agent observation != human approval | 3–5 h |
| C13 | Vikunja API schema inventory and permissions | P1 | C03 | Instance-specific routes, permissions & projection schema | 2–4 h |
| C14 | One-way Vikunja projection | P1 | C09,C13 | Idempotent upserts; task ID map | 5–8 h |
| C15 | Webhook inbox + polling reconciliation | P1 | C14 | Signed, deduped, recoverable | 3–5 h |
| C16 | Board and saved-filter conventions | P1 | C14 | Single operator view and project views | 2–3 h |
| C17 | Review scheduler | P2 | C09,C12 | Idempotent periodic project audit | 3–5 h |
| C18 | Semantic critic integration | P2 | C02,C17 | Evidence-based scope judgments; offline fallback | 4–7 h |
| C19 | Milestone slip and focus recommendation reports | P2 | C06,C17 | Transparent rationale, no fake precision | 4–6 h |
| C20 | Pilot, backup/restore & security gates | P0 at release | C10–C19 | Exit test, restore proof, documented limitations | 8–12 h |

The task-level estimates are **decomposition guides**, not additive commitments; some overlap and should not be summed mechanically against milestone estimates.

## Contents

- [Execution sequence, minimal path](#execution-sequence-minimal-path)
- [Priority rules for a one-person operator](#priority-rules-for-a-one-person-operator)
- [Contract and data design](#contract-and-data-design)
- [Structured policy classification](#structured-policy-classification)
- [Change-control protocol](#change-control-protocol)
- [Failure and rollback](#failure-and-rollback)
- [GoalGuard v0.2 — Thekedar extraction overlay (2026-10-27)](#goalguard-v02--thekedar-extraction-overlay-2026-10-27)

---

## Execution sequence, minimal path

C01 → C02/C03 → C04 → C05/C06 → C07/C08 → **ship M1** → C09 → C10/C11/C12 → **ship M2** → C13/C14/C15/C16 → **ship M3** → C17/C18/C19 → **ship M4** → C20.

## Priority rules for a one-person operator

- An urgent incident may preempt portfolio focus, but records `interruption_reason`, `paused_task_id`, `resume_trigger`, `estimated attention` (if available).
- Background agents can work concurrently, but are never counted as additional human owners.
- Distinguish **agent capacity** (parallel sessions) from **operator bandwidth** (one decision stream).
- Only preempt for verified incident, materially closer committed deadline, or a high-impact unblocking step; otherwise prefer finishing the current task.
- Park optional improvements. Allow only one discretionary research spike at a time, each with scope, timebox and evidence deliverable.
- Re-plan on verified change, not after every tool call.

## Contract and data design

Core entities: `GoalContract`, `AcceptanceCriterion`, `Project`, `Milestone`, `Task`, `Dependency`, `Decision`, `Approval`, `AgentObservation`, `Evidence`, `FocusSession`, `ScheduleAssessment`,
`SyncMapping`.

Recommended immutable identifiers: `portfolio_id`, `project_id`, `task_id`, `milestone_id`, `criterion_id`, `decision_id`, `event_id`, `agent_session_id`. Every record must carry `revision` (or
monotonic sequence) and timestamps with timezone. All approval decisions identify actor and exact contract revision.

Date semantics: `target_at` (aspirational), `due_at` (operational), `committed_at` (external commitment), `completed_at` (verified), `last_evidence_at`; no implicit conversion among them. Store UTC
timestamps, present Australia/Sydney where relevant.

## Structured policy classification

- `PROCEED`: approved task, prerequisites satisfied, and evidence-supported link to MVP/required repair.
- `PARK`: not essential to MVP; store rationale and possible later milestone.
- `REVIEW`: ambiguous goal link, threatened deadline, changed scope or missing approval.
- `BLOCK`: verified forbidden operation / revoked authorization / an unapproved protected change; reserve blocking for high-confidence cases.

Deterministic gates: contract version valid, task ID exists, prerequisites closed, no cycle, allowed scope class, approval present, status transition legal, required evidence present.

Semantic review: whether a newly proposed technical investigation is *actually necessary*; whether a new abstraction materially advances the acceptance criterion; whether a smaller implementation
suffices. Return classification + citations to concrete artifacts + uncertainty. Never allow the proposing agent to be its own final approver on scope expansion.

## Change-control protocol

`propose` → `explain goal linkage` → `scope decision` → (`proceed` or `park` or `request human approval`) → `execute bounded task` → `verify` → `record` → `update What's Next`.

A new human inquiry is not a scope-change command. Distinguish `discuss`, `investigate`, `approve` and `execute` intents; do not infer approval from agent output.

## Failure and rollback

Use one DB writer, append-only journal and periodic durable backups. Webhook delivery loss is recovered by pull reconciliation. An agent crash must not mark task complete. If Vikunja is offline,
continue in GoalGuard and queue projection; if policy service is unavailable, read-only queries continue and protected writes require human intervention. No silent automatic rewrite of protected
project goals.

## GoalGuard v0.2 — Thekedar extraction overlay (2026-10-27)

**Decision:** no new implementation track and **no new CTPS IDs**. Reuse selected Thekedar patterns within existing work items. The exact source-to-target file matrix, limits and test mapping live in
[06-Thekedar-Extraction-Matrix.md](06-thekedar-extraction-matrix.md).

| Existing ID | Source(s) used as reference | Precise sub-deliverable (same scope / estimate family) | Verification |
|---|---|---|---|
| **C03** | `templates/task.md` | Add optional expected-files/NOT-in-scope sections without making coding files mandatory for ad-hoc work | GG-401, GG-408 |
| **C05** | `hooks/scope-guard.sh`, `templates/config.md` | Two independent decisions: (1) task/criterion/necessity gate; (2) file scope for coding activity. No self-approved goal expansion, bounded scope adjustments, explicit verdicts. | GG-401–408, GG-412–413, GG-420 |
| **C06/C07** | `templates/PROJECT_STATE.md` | Expose one owner focus across projects, per-project next and active task's next; retain interrupted-task resume pointer | GG-101–112, GG-415 |
| **C08** | `tests/test-scope-guard.sh`, `scripts/doctor.sh` | Port safe behavioural cases; invert unsafe expectations (agent-editable scope addition, unassigned task); add real hook fixture parsing and deterministic doctor | GG-402–407, GG-421, GG-424 |
| **C09** | `hooks/munshi.sh`, `docs/TROUBLESHOOTING.md` | Journal with immutable event IDs, single writer, optimistic task revision, task lease; no Markdown append races | GG-416–418 |
| **C10** | `hooks/session-brief.sh`, `hooks/scope-guard.sh`, `install.sh` | Claude session brief and advisory pre-edit adapter. Test actual payloads; owner contract changes protected at writer even when hook bypassed | GG-401, GG-414, GG-422–423 |
| **C11** | `scripts/install-codex.sh`, `.codex/hooks/hooks.json` | Codex hook/skill installation adapter using current runtime schema; test `apply_patch` differently from `Edit`; never blindly reuse Claude parser | GG-413, GG-422–423 |
| **C12** | `hooks/drift-check.sh`, `templates/changelog-entry.md`, `hooks/munshi.sh` | Capture task-start Git baseline, changed-file attribution, verification evidence and 'deliberately not changed'; non-code evidence fallback | GG-409–411, GG-419 |
| **C20** | `scripts/doctor.sh`, `LICENSE`, `docs/BENCHMARKS.md` | Safe installer/rollback, attributed source reuse, live-hook and conflict tests, guard efficacy and token/interrupt benchmarking | GG-421, GG-424–425 |

**Implementation sequencing inside existing work:** C03/C05/C08 in M1 → C09/C10/C11/C12 in M2 → C20 verifies each gate. No agent catalogue, new MCP, new UI, or Thekedar runtime dependency is
introduced. If detailed estimates require extra time, revise the existing M1/M2 estimates explicitly; do not silently add scope.

**Policy note:** A hook can warn/block only on events it receives. Material contract mutations are always controlled by GoalGuard's writer; model instructions and file-scope hook checks are not an
OS-level sandbox. Diagnostic `UNKNOWN` and risk `REVIEW` are first-class outcomes.
