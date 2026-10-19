---
Title: Efficiency and measurement
Category: reference
Status: current
Authority: local-supplement
Scope: Anything that runs repeatedly or at scale - jobs, collectors, loops over many items, page views over many records, check suites
Last reviewed: 2026-10-19
Summary: >-
  Runtime is an acceptance criterion: state a budget, measure per phase on a real run, design for scale in the first slice
  (reuse connections, batch per host, bounded parallelism, probe first), count failure paths and re-measure when input grows.
---

# Efficiency and measurement

Source: governance `validation-and-change-discipline-guide.md` "Efficiency Is Part of Done" (operator, 2026-10-09). The cause was a scheduled job that grew from one site to 37 and from minutes to a
76-minute cycle while every check stayed green, because nothing measured runtime; after the measured fix it ran in 12.5 minutes.

## Rules

| Rule                                                                                                                               | Why                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| State a budget when building (cycle time, per-unit cost, page time); keep it in settings                                           | Without a number, "slow" is never a failure                     |
| Report the measured runtime next to the correctness evidence; green with an unmeasured or over-budget runtime is not done          | Correct and too slow is still broken                            |
| Time each phase on a real run before optimising or claiming a cost; record before and after in the change log                      | Guessing optimises the wrong phase                              |
| Reuse connections: one HTTP session, one SSH master connection, one database session per run or per host, not per item             | Set-up cost dominates small calls                               |
| Batch many reads into one session per host                                                                                         | Round trips cost more than bytes                                |
| Run independent units in parallel with a bounded worker count, and keep a serial switch for diagnosis                              | Unbounded parallelism overloads targets; serial mode makes      |
|                                                                                                                                    |   logs readable                                                 |
| Ask a cheap question before an expensive one (one probe before walking a table)                                                    | A silent unit costs one short timeout                           |
| Never start an interpreter, container exec or remote session per item when one per host or per run will do                         | Process start-up is seconds, not milliseconds                   |
| Re-measure when the input grows; report an unmeasured or over-budget job unprompted with a fix                                     | Growth is when budgets break                                    |
| A measured cause with a fix is merged or recorded as an open item with its numbers, never left only on a branch or in a report     | Findings that do not land are lost                              |
| Optimisation never drops a check, a safety guard or evidence; parallel work keeps one log block per unit and shared state under    | Fast and wrong is worse than slow                               |
|   a lock                                                                                                                           |                                                                 |

## Making it a by-product

Every front end creates a run context (run id, start time, budget); services log structured lines with the run id and time their phases; the run record carries the totals. A breach of budget raises
the project's staleness or monitoring warning. Why: when measurement is built into running, the rule needs no reviewer (a governed project's design, section 13.3 and 13.6).

## Check suites count

A governance check suite has a budget too (the skill-ai-it doctrine sets 10 seconds, with a `--timings` view per family). Why: a slow check gets skipped.
