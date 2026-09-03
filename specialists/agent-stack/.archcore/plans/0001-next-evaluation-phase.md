Title: Plan 0001 — Next evaluation phase
Category: approved-plan
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: SCRATCHPAD.md
Summary: Unseen holdout, real-task replay, then shadow mode. Approved direction with an explicit stopping rule.

# Plan 0001 — Next evaluation phase

## Plan

1. **Unseen holdout** — 20–30 cases authored without reference to the frozen 60.
2. **Real-task replay** — historical project tasks routed and compared against what actually happened.
3. **Shadow mode** — routing runs alongside normal work without driving it.

## Stopping rule, stated up front

Do **not** tune against the frozen 60 further. At ~80% on production-tier models with deterministic closure, the remaining failures are no longer dominated by one
architectural defect, which is exactly the condition under which further optimisation overfits.

## Only after this phase

Decide whether additional routing taxonomy or personas are needed. Not before.
