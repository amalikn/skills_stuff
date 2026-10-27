---
title: "Vikunja owns live tasks; Goal Guard owns scope"
type: adr
status: accepted
tags: [authority, decision]
created: 2026-10-27
---

# ADR: Vikunja owns live tasks; Goal Guard owns scope

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Decision

Vikunja is the authority for live task state (priority, status, due dates, dependencies). Goal Guard owns scope, approvals, decisions, deferred ideas, internal targets and forecasts, and never keeps a second task database (operator, 2026-10-27; PORT-001).

## Canonical source

[references/vikunja-integration.md](../../references/vikunja-integration.md#position), section "Position".
