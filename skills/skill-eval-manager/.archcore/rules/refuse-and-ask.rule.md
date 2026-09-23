---
title: Refuse and ask rather than record a dishonest result
type: rule
status: accepted
tags: [safety]
provenance: promoted from SKILL.md "Refuse and ask the operator" by skill-ai-it promote on 20260923_1311
---

# Rule: Refuse and ask rather than record a dishonest result

This is a refusal rule, not advice. Stop and ask the operator for direction; do not proceed on an assumption.

## Stop when a required element is unknown

The claim, denominator, oracle independence, required evidence layer, validity window, falsifiability evidence, or authority to run a live or manual tier.

## Stop unconditionally when

- The only proposed oracle routes through the path being evaluated. A system cannot verify itself through the path under evaluation.
- An unsafe fault injection is proposed. Falsifiability is never authorization to disturb production; an injected fault must name an approved environment and a rollback or recovery path.
- A result would be represented as current without an honest population. Coverage calculated over convenient successes is not coverage.

## Why it is a refusal and not a warning

Each of these produces a result that looks valid and is not. A warning attached to a recorded green verdict is read as a green verdict. The only honest outputs here are a question to the operator or a
`blocked` verdict.

## Source

[SKILL.md](../../SKILL.md) "Refuse and ask the operator"; [references/04_falsifiability.md](../../references/04_falsifiability.md) "Safety".
