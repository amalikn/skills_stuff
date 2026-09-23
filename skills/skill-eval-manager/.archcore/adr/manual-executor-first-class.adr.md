---
title: Treat type manual as a first-class executor
type: adr
status: accepted
tags: [scope, safety]
provenance: promoted from SKILL.md "Boundary" by skill-ai-it promote on 20260923_1311
---

# ADR: Treat type manual as a first-class executor

## Status

Accepted 20260923_1331 by the operator. Source: [SKILL.md](../../SKILL.md) "Boundary".

## Context

Evaluation tooling usually treats an unautomated check as a gap to be closed. For operational systems, several honest evaluations are procedures an operator performs: a live read against a production
boundary, an accounting judgement, a sign-off.

## Decision

> `type: manual` is a first-class executor: a procedure can produce a recorded observation without becoming automated.

A manual executor reference is as valid as a query or script reference, and its observation is recorded through the same path.

## Rationale

This follows from [skill-not-platform](skill-not-platform.adr.md): a package that executes nothing has no basis for ranking an automated executor above a procedural one. Treating manual as
second-class would push operators to either fake automation or leave the claim unevaluated, and the unevaluated claim is the worse outcome.

## Consequences

- The tier model carries the safety boundary instead: `tier.runner` says whether an agent or only an operator may run a given eval.
- A manual eval still owes everything every other eval owes — population, independent oracle, evidence layer, validity, falsifiability.
- "Tested manually" as free text remains insufficient; see [references/02_defining-evals.md](../../references/02_defining-evals.md) "Common failures".
