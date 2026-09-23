---
title: History is append-only and reports are derived
type: rule
status: accepted
tags: [recordkeeping]
provenance: promoted from SKILL.md quality gate by skill-ai-it promote on 20260923_1311
---

# Rule: History is append-only and reports are derived

> History is append-only; corrections supersede rather than overwrite; reports are derived.

## Why

An overwritten record destroys the evidence that a belief was once held and later corrected. That evidence is the part an audit needs, and it is exactly the part a convenient edit removes. A derived
report can always be rebuilt; a rewritten history cannot.

## How a correction works

Record a newer observation and set `supersedes` to the prior observation id. `scripts/record_result.py` only appends. Renderers use the newest `recorded_at` per eval and slice, so the correction
wins at read time while the original belief stays on the record.

## Consequences

- Never edit or delete a line in `history.jsonl`.
- Never hand-edit a `report.md`; regenerate it with `scripts/render_report.py`.
- Never put an observation in the suite file. A result value is not a suite definition.

## Enforcement

Executable for the checked-in examples: `scripts/check_governance.py` fails when a report is older than the suite or history it derives from. The append-only property of a consuming project history
is a discipline this document states and the recording script preserves.

## Source

[SKILL.md](../../SKILL.md) quality gate; [references/03_verdicts-and-validity.md](../../references/03_verdicts-and-validity.md) "Append-only history".
