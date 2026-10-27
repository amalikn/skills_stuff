---
title: "Settled conflicts between the source documents"
type: adr
status: accepted
tags: [decision, decision-rules]
created: 2026-10-27
---

# ADR: Settled conflicts between the source documents

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Decision

A blocker registered in the approved baseline proceeds; a registered blocker with `adds_scope` is REVIEW, never PROCEED; a missing or draft baseline blocks scope-changing work; fail open for read-only inspection and closed for scope-changing or protected writes.

## Canonical source

[references/decision-rules.md](../../references/decision-rules.md#settled-conflicts), section "Settled conflicts".
