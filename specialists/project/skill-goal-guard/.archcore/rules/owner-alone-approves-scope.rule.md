---
title: "Only the owner approves scope"
type: rule
status: accepted
tags: [decision-rules, governance]
created: 2026-10-27
---

# Rule: Only the owner approves scope

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Rule

An agent, a model, a Vikunja task or a task file never approves scope; only an authenticated owner decision naming the revision does.

## Canonical source

[SKILL.md](../../SKILL.md#standing-rules), section "Standing rules".

## Enforced by

`decide.py` blocks approval fields on proposals (MVP-007); `decisions_log.append` refuses to write approval entries.
