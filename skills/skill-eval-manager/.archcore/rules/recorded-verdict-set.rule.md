---
title: Recorded verdicts are a closed set of five
type: rule
status: accepted
tags: [recordkeeping, contract]
provenance: promoted from SKILL.md quality gate by skill-ai-it promote on 20260923_1311
---

# Rule: Recorded verdicts are a closed set of five

> Recorded verdicts are only `pass`, `fail`, `inconclusive`, `error`, or `blocked`.

## Meanings

`pass` means the claim held at its stated layer. `fail` means it did not. `inconclusive` means the eval ran but the oracle could not establish truth. `error` means the evaluator broke. `blocked`
means preconditions or authority were absent.

**The last three are not failures of the system.** Collapsing them into `fail` reports ignorance, evaluator breakage, or missing authority as a defect in the thing being evaluated.

## Derived states are not verdicts

`stale` and `not_evaluated` are computed at render time and are deliberately excluded from the observation schema verdict enum. See [derived-states](../specs/derived-states.spec.md).

## Adding a verdict

The set is closed. Widening it is a change to this rule and to the observation schema, made deliberately, not an ad-hoc value in a record.

## Source

[SKILL.md](../../SKILL.md) quality gate; [references/03_verdicts-and-validity.md](../../references/03_verdicts-and-validity.md) "Recorded verdicts".
