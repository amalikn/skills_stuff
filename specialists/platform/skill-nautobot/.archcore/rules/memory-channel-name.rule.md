---
title: Memory channel is exactly nautobot
type: rule
status: accepted
tags: [memory]
created: 2026-10-05
---

# Rule: Memory channel is exactly `nautobot`

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `AGENTS.md` (Working rules). USER_STATED 2026-10-01.

## Rule

memory-keeper entries about this pack use the channel `nautobot` — exactly that string, no prefix or suffix. Project-specific engagement notes may also go to the engaging project's channel.

## Why

The operator named the channels explicitly so that recall for Nautobot work is one query across projects.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `nautobot` is unaffected by either.
