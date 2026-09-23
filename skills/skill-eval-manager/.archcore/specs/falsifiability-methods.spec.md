---
title: The six permitted falsifiability methods
type: spec
status: accepted
tags: [evidence, safety]
provenance: promoted from references/04_falsifiability.md by skill-ai-it promote on 20260923_1311
---

# Spec: The six permitted falsifiability methods

A closed set. An addition is a deliberate change to this spec, not an ad-hoc value in a suite file.

The suite must name a permitted method, a durable reference, and the date that evidence was verified. The validator requires evidence; it does not demand destructive testing.

## Methods

| Method | What it establishes |
|---|---|
| `injected_fault` | A safe, scoped fault is deliberately created and the expected failure is observed |
| `fixture` | Captured bad input is supplied |
| `mutation` | An input or implementation condition is changed in a controlled test |
| `counterexample` | A known case that must be rejected is demonstrated |
| `historical_failure` | A real defect the eval caught is referenced |
| `analytical_proof` | A reviewable argument showing a countercondition is rejected is recorded |

## Choosing a method

Injection is not the default and is not the strongest. For production financial reconciliation, legal provenance, external API behaviour, and historical evidence, a historical failure or
counterexample can be more honest and safer than injection. State the environment and approval conditions in the referenced artifact.

## What does not count

"It passed once", unreferenced confidence, a test that only reaches the same path it evaluates, or a fault that an operator cannot safely reproduce.

## Safety boundary

An injected fault must name the approved environment and a rollback or recovery path in its referenced procedure. Where live access is operator-only, the tier must say so and an agent must stop
rather than run it. See [refuse-and-ask](../rules/refuse-and-ask.rule.md).
