---
title: "Front matter, a blank line after it, and a catalog row"
type: rule
status: accepted
tags: [governance, records]
created: 2026-10-27
---

# Rule: Front matter, a blank line after it, and a catalog row

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Rule

Every markdown file except readme, SKILL and CLAUDE carries the governance front matter followed by one blank line, and every file has a row in docs/catalog.md (operator, 2026-10-27).

## Canonical source

[AGENTS.md](../../AGENTS.md#working-rules), section "Working rules".

## Enforced by

`scripts/check_governance.py` (records and catalog families), run by `just check`.
