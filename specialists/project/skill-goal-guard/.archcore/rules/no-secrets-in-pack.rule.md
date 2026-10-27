---
title: "No secrets in pack files"
type: rule
status: accepted
tags: [governance, records]
created: 2026-10-27
---

# Rule: No secrets in pack files

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Rule

No secrets, tokens, customer identifiers, or apn content in me material (or the reverse) in pack files. Vikunja tokens live in KeePassXC and reach the tools through the environment, never an argument or a log.

## Canonical source

[AGENTS.md](../../AGENTS.md#working-rules), section "Working rules".

## Enforced by

`vikunja.py` keeps the token out of error messages (tested).
