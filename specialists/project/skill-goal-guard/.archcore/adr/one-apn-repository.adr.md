---
title: "D1: one apn repository, scoped by path"
type: adr
status: accepted
tags: [decision, pilot]
created: 2026-10-27
---

# ADR: D1: one apn repository, scoped by path

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Decision

The three apn projects keep one Git repository. Hooks, rules and `.gg/` records are scoped by project path inside it, each project keeps its own decision log, and approval commits touch one project each (operator, 2026-10-27).

## Canonical source

[references/project-layout-and-storage.md](../../references/project-layout-and-storage.md#shared-repository), section "Shared repository".
