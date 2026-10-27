---
Title: GoalGuard What's Next and Portfolio Focus
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §17.3-17.4, research pack 00, 02 and the v0.1 readme; conflict 4 (ranking) settled here
Scope: Task, project and portfolio What's Next, the deterministic ranking pipeline, WIP and interrupt/resume
Last reviewed: 2026-10-27
Summary: >-
  Three-level What's Next from live Vikunja data: filter to eligible work, honour owner overrides and incidents, then deadline, Vikunja priority,
  dependency order, due date and stable ID; one operator focus, agents counted separately; the v0.1 weighted score is retired.
---

# What's Next and portfolio focus

## Three levels

| Level     | Returns                                                                                                           | Never                                                                |
| --------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Task      | The concrete next physical action; if blocked, the unmet task IDs; if done, the evidence and the next             | A vague objective ("work on controller") — that is REVIEW (GG-106)   |
|           |   dependent task                                                                                                  |                                                                      |
| Project   | The next ready task and, separately, the next milestone and its date; if none ready, the blocker or decision      | An impossible task due tomorrow whose prerequisites are              |
|           |                                                                                                                   |   open (GG-105)                                                      |
| Portfolio | **One** recommended focus with Vikunja ID, why it is eligible, why it outranks the alternatives, its next action  | Opening a new project because agents are idle                        |

When nothing is ready the answer is an explicit `NO_ACTION` or `BLOCKED` with the waiting approvals (pack 00 rule 6, GG-107).

## Ranking pipeline (replaces the v0.1 weighted score)

The prototype scored +40 started, +50 overdue, +35/+20 near due, priority ×10/×5. The handoff asks for no weighted score until trials show ordering is wrong (handoff §17.3). The pipeline:

1. **Filter.** Context access, approved MVP mapping, open status, all blocking prerequisites done (PORT-002/003/005).
2. **Owner first.** Explicit human-selected context, fixed commitments, authorised incidents.
3. **Deadline pressure.** Committed management deadlines and genuine imminent due dates, and tasks that unblock them.
4. **Vikunja priority**, through a configured field mapping (no assumption about the integer scale).
5. **Order constraints.** Dependency/precedence relations; a view's manual order is a tie-break only and never a global rank (PORT-009).
6. **Tie-break.** Due date, then stable task ID.

Prefer finishing started work over a slightly higher-ranked switch unless a threshold is met (GG-101): verified incident, materially closer committed deadline, or a high-impact unblocking step (pack
02). Log the factors and exclusions so a ranking can be replayed (PORT-006). The human may override with a logged reason; GoalGuard never edits Vikunja priority to justify itself (PORT-007, §17.3).

## Capacity

- One operator focus item at a time, plus an explicitly authorised interruption (PORT-004, GG-108).
- Agent capacity is not operator bandwidth: parallel agents need an explicit task each and never count as extra human WIP (GG-109).
- No fabricated durations, percent complete or forecasts; `unknown` when data is missing (pack 00 rule 7, DATE-003).

## Interrupt and resume

Record `interruption_reason`, `paused_task_id`, `resume_trigger`; checkpoint the paused task; return focus when the incident closes (pack 02, P10, GG-102, GG-415). An ad-hoc item that grows several
dependencies or days is proposed for promotion to a project, with owner approval (GG-112).

## Operator questions

- *What should I work on now?* — context, one task, its Vikunja ID, eligibility, why it beats the rest, the next demonstrable action.
- *Interrupt* — confirm urgency, checkpoint, record, propose the resume point.
- *Complete* — attach evidence to the MVP record, then update Vikunja through the authorised path.
- *Reprioritise* — the owner edits Vikunja; GoalGuard re-reads (P09, F08). (handoff §17.4)
