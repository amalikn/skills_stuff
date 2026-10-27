---
Title: GoalGuard Decision Rules
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §4, §6-8, §17.5, §26, research pack 02 and 06, and the v0.1 prototype; conflicts 2 and 3 settled here
Scope: PROCEED / PARK / REVIEW / BLOCK, the order checks run in, fail modes and the policy clause index
Last reviewed: 2026-10-27
Summary: >-
  One ordered rule set for the four verdicts: deterministic contract checks first, then semantic necessity; pre-registered blockers proceed, newly
  discovered dependencies go to REVIEW; missing or unapproved baselines BLOCK scope-changing work while read-only inspection stays open.
---

# Decision rules

## Verdicts

| Verdict   | Meaning                                                                                                       | Agent may execute?      | Record                                         |
| --------- | ------------------------------------------------------------------------------------------------------------- | ----------------------- | ---------------------------------------------- |
| `PROCEED` | In approved scope, or a dependency already registered as necessary in the approved baseline                   | Yes                     | criterion or blocker ID, rationale,            |
|           |                                                                                                               |                         |   contract revision                            |
| `PARK`    | Useful but not needed for this baseline                                                                       | No                      | deferred idea with context and possible        |
|           |                                                                                                               |                         |   future milestone                             |
| `REVIEW`  | Possibly needed but not approved: scope change, ambiguity, stale or conflicting authority                     | No, for the             | evidence, alternatives, the owner              |
|           |                                                                                                               |   affected work         |   decision requested                           |
| `BLOCK`   | Missing or unapproved baseline, a task mapped to no approved MVP, excluded feature, self-approval, protected  | No                      | failed clause and remedy                       |
|           |   change, cross-context access                                                                                |                         |                                                |

Every verdict carries `reason_code`, `contract_revision`, evidence references and `requires_owner_approval` (pack 06 §4). `UNKNOWN` is a diagnostic state for telemetry and unparseable input, not a
verdict (pack 02).

## Evaluation order

Run in this order and stop at the first verdict:

1. **Context.** Resolve partition (`apn` / `me`) and project; access outside the authorised partition → `BLOCK` (PORT-005).
2. **Baseline.** No baseline, draft baseline, or unreadable baseline → `BLOCK` for scope-changing work (MVP-001, MVP-003, MVP-012, T01, T02, T11). Read-only inspection may continue (pack 00 rule 4).
3. **Task.** No task for nontrivial work → `REVIEW` (GG-406). A Vikunja task (the work item itself) that maps to no approved MVP criterion → `BLOCK` (PORT-002, P03). Unmet dependency → `REVIEW` with the blockers named.
4. **Exclusion.** Work matching an exclusion → `BLOCK`, whatever it is called ("future-proofing", "while we're here") (MVP-004, T05).
5. **Self-approval.** An approval field written by an agent, in a task file, hook payload or Vikunja → `BLOCK`; record it as a proposal (MVP-007, T07, GG-403, GG-418).
6. **Protected change.** Edits to goal, MVP, committed date, management baseline or hub decision outside the change-control path → `BLOCK` (MVP-011, DATE-001, DATE-004).
7. **Criterion link.** On a task that does map to the MVP, a proposed action citing no accepted criterion and no registered blocker → `PARK` (MVP-005, T04). Rule of thumb: an unmapped *task* blocks; an unmapped *idea* parks.
8. **Necessity (semantic).** Cited criterion but the work does not advance it → `REVIEW`, flag false linkage (GG-007, GG-412). Work inside an allowed file that adds an unrelated feature → `PARK` or
   `REVIEW`; a file allowlist alone never yields `PROCEED` (GG-401).
9. **Scope growth.** `adds_scope` true, or a newly discovered dependency not in the baseline → `REVIEW` (MVP-006, T06, GG-008).
10. **Otherwise** → `PROCEED`, still recording the agent's necessity rationale for later audit.

## Settled conflicts

- **Necessary dependency** (prototype vs handoff). A blocker already registered in the *approved* baseline proceeds (T15, GG-002, the prototype's intent). A dependency found during execution is
  `REVIEW` until the owner approves a baseline revision (MVP-006, T06). A registered blocker with `adds_scope` true is `REVIEW`, never `PROCEED`; the v0.1 prototype gets this wrong.
- **Missing baseline** (prototype vs handoff). The prototype has no baseline and no `BLOCK`; the rewrite adds both per steps 2-6 above.
- **Fail mode.** Fail open for read-only inspection, fail closed for scope-changing or protected writes (pack 00 rule 4, MVP-012, PORT-008).

## Permitted without fresh approval

Low-level refactoring, bug fixes and tests that change no observable scope and are needed to meet an accepted criterion (handoff §4); bounded investigations with a question, timebox and stop condition
(GG-010; one discretionary spike at a time, pack 02); minor file-list discoveries inside an approved task when a pre-approved policy allows them, with an audit event (pack 06 §3B). A genuine critical
security or reliability defect is never blindly parked: `REVIEW` with a bounded urgent repair (GG-004).

## Intent is not approval

`discuss`, `investigate`, `approve` and `execute` are different intents (pack 02). A user question, a brainstorm, a Curator extraction or a task priority never changes scope (T12, T13, GG-005, P03).

## Anti-tangent questions (before nontrivial work)

1. Which accepted criterion does this advance? 2. What fails if we skip it? 3. Is it needed now for the MVP? 4. What is the smallest sufficient action and stop condition? 5. What does it displace?
No convincing answer to 1-3 → park (v0.1 readme).

## Record formats (pilot contract; field names follow pack 06 §4 and handoff §31)

| Record                 | Fields                                                                                                                                                                      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Proposal               | `proposal_id`, `task_id` (Vikunja ID), `project_id`, `criterion_id` or `necessary_blocker_id`, `description`, `adds_scope`, `claimed_necessity`, `smallest_step`,           |
|                        |   `stop_condition`, `evidence_refs`, `proposed_files` (optional), `proposer` (agent/session)                                                                                |
| Verdict                | `proposal_id`, `verdict` (PROCEED/PARK/REVIEW/BLOCK), `reason_code`, `clause` (MVP-/PORT-/DATE- ID), `contract_revision`, `evidence_refs`, `requires_owner_approval`,       |
|                        |   `decided_at` (ISO-8601 with offset)                                                                                                                                       |
| `decisions.jsonl` line | `decision_id`, `kind` (verdict, approval, override, revision, park), `actor`, `contract_revision` before and after, `rationale`, `refs`, `at`, `prev_hash` (hash            |
|                        |   chain, append-only)                                                                                                                                                       |

Schemas (`schemas/`) are not written yet (2026-10-27); the step-4 code enforces this table in `scripts/goal_guard_lib/records.py` and `mvp.py`, and a PROCEED verdict also carries the proposal's `proposed_files`, which the hook uses as its file allowlist.

## Policy clause index

Full text stays in the handoff; cite by ID.

| Series        | Topic                                                                 | Location      |
| ------------- | --------------------------------------------------------------------- | ------------- |
| MVP-001..012  | Baseline, approval, scope, completion, fail-closed                    | handoff §4    |
| PORT-001..009 | Vikunja authority, eligibility, WIP, isolation, overrides, stale data | handoff §17.5 |
| DATE-001..008 | Protected deadline, internal target, forecast, timezones              | handoff §26   |
