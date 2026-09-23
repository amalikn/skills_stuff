---
name: skill-eval-manager
description: >-
  Define, review, record, and maintain durable evaluation or acceptance/verification suites for operational systems, including independent oracles,
  evidence layers, populations, validity, and falsifiability. Use for system-evaluation discipline and results history; do not use for ordinary unit
  testing, debugging, CI setup, or LLM/prompt evaluation.
metadata:
  version: 0.1.3
  aliases:
    - eval-manager
    - evaluation-suite
---

# Skill: Eval Manager

Use this skill to make a project's claims testable over time. An eval is a claim, an independently defined population, an independent oracle, evidence at a declared layer, a recorded verdict, and a
validity policy.

## Boundary

This skill defines, validates, records, invalidates, and reports. It does **not** execute an eval. Existing project tools, queries, test functions, and operator procedures produce observations. If the
work needs a scheduler, parallel runner, retry policy, executor plugin system, CI product, or assertion DSL, stop: that work is outside this skill.

It is not an LLM evaluator, test-runner replacement, monitoring/alerting system, or a dependency on a non-OSI-licensed tool. `type: manual` is a first-class executor: a procedure can produce a
recorded observation without becoming automated.

## Standing write-back contract (applies no matter which project invoked this skill)

This skill is the **shared, cross-project source of truth** for evaluation method — not something scoped to whichever project happens to be open. If, while defining, reviewing, recording, or
maintaining a suite in **any** project, you learn something about the *method* that this package does not yet state, write it back to the matching [references/](references/) file before ending the
session, regardless of whether the calling project governance says to. Invoking this skill at all carries that obligation, including the first time a project ever writes a suite.

**What flows back — method, never project content:**

- A falsifiability method that was genuinely needed and is not among the six permitted ones.
- A layer vocabulary or ranking pattern that generalizes beyond the project that coined it.
- A malformed suite that passed `scripts/validate_suite.py`, or a valid one it rejected — a validator gap is the highest-value thing a consuming project can find.
- A verdict the closed five could not express honestly, or a case where `inconclusive`, `error`, and `blocked` were hard to tell apart in practice.
- An oracle that looked independent and was not, and how that was discovered.
- A recordkeeping failure: a correction that did not supersede cleanly, or a report that disagreed with its history.

**What does not flow back:** the project suite itself, its thresholds, its executor wiring, its schedule, or its results. Those belong to the project. Absorbing them would make this a platform, which
[.archcore/adr/skill-not-platform.adr.md](.archcore/adr/skill-not-platform.adr.md) rules out.

**Steps:**

1. Route with the [References](#references) section below — it maps method areas to files. Add a reference file and a row there if a genuinely new area surfaces; do not force-fit.
2. If the finding changes a **closed set** — the five verdicts, the six falsifiability methods, the required contract elements — it is a change to the matching `.archcore/` rule or spec, not a prose
   note. Update the document and add or amend its row in [.archcore/index.guide.md](.archcore/index.guide.md).
3. If a validator gap was found, add the rule **and demonstrate a deliberate failure case**, per the quality gate below.
4. Bump the version across `SKILL.md`, `README.md`, and `CHANGELOG.md` in one pass, and append a `CHANGELOG.md` entry.
5. **Read the file back** after writing. A session note, a `SCRATCHPAD.md` claim, or a file timestamp is not proof the content is present — only reading the body counts.

A project's own governance may restate this obligation with local detail. That is reinforcement, not the source of the rule.

## Workflow

1. Read [the overview](references/01_overview.md), then the reference matching the task.
2. Define the suite in the consuming project's suite file, copied from `templates/evals.yaml`: claim, population and denominator source, independent oracle,
   ranked claim/evidence layers, executor reference, tier, validity, and falsifiability evidence.
3. Run `scripts/validate_suite.py --suite <evals.yaml>` before any observation is trusted.
4. Let the project executor or operator perform the work. Record its result using `scripts/record_result.py`; never put observations in the suite or append to a scorecard.
5. Record declared change invalidations when they occur. Do not compute basis hashes in v0.1.
6. Render a report with `scripts/render_report.py`. It derives `stale` and `not_evaluated` at read time.

## Refuse and ask the operator

Stop for direction when the claim, denominator, oracle independence, required evidence layer, validity window, falsifiability evidence, or authority to run a live/manual tier is unknown. Also stop if
the only proposed oracle routes through the path being evaluated, if an unsafe fault injection is proposed, or if a result would be represented as current without an honest population.

## Quality gate

- Every eval has an independently defined population, oracle path, claim layer, evidence layer, executor reference, validity policy, and falsifiability evidence.
- Evidence rank is at least the claim rank; lower-ranked evidence never proves a higher-ranked claim.
- Recorded verdicts are only `pass`, `fail`, `inconclusive`, `error`, or `blocked`.
- History is append-only; corrections supersede rather than overwrite; reports are derived.
- The relevant tier's execution authority and safety boundaries are respected.
- Validation has passed and a deliberate failure case has been demonstrated for new validator rules.

## References

- [Method and data model](references/01_overview.md)
- [Writing eval definitions](references/02_defining-evals.md)
- [Verdicts, history, and validity](references/03_verdicts-and-validity.md)
- [Falsifiability evidence](references/04_falsifiability.md)
- [Reporting and operations](references/05_reporting.md)
