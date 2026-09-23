---
title: Reserve validity.basis in v0.1 without implementing it
type: adr
status: accepted
tags: [validity, scope]
provenance: promoted from SKILL.md and BRIEF.md "Deferred to v0.2" by skill-ai-it promote on 20260923_1311
---

# ADR: Reserve validity.basis in v0.1 without implementing it

## Status

Accepted 20260923_1331 by the operator. Source: [BRIEF.md](../../BRIEF.md) "Deferred to v0.2" and [SKILL.md](../../SKILL.md) step 5.

## Context

Automatic invalidation by basis hashing would detect that an implementation, configuration, or oracle changed without an operator declaring it. It is the obvious next step beyond explicit
invalidation events, and the schema anticipates it.

## Decision

`validity.basis` is schema-reserved but not computed, hashed, compared, or invalidated automatically in v0.1. Invalidation stays explicit: a project script or operator records an event with one
declared label and a reference.

## Rationale

> Per-project decisions about implementation boundaries, configuration scope, and oracle versions must precede basis hashing.

Hashing something requires first agreeing what "something" is. A basis computed over the wrong boundary invalidates constantly or never, and both failures are quiet. The decision is deferred until a
consuming project has stated those boundaries, which is the trigger for revisiting this ADR.

## Consequences

- The schema keeps the field so adding the behaviour later is not a breaking change.
- Agents must not compute basis hashes in v0.1, and [SKILL.md](../../SKILL.md) states so as a workflow step.
- The rest of the v0.2 deferred set stays in [BRIEF.md](../../BRIEF.md) as a waiting list, not an approved plan. It is not promoted to `.archcore/plans/` until v0.2 is scheduled.
