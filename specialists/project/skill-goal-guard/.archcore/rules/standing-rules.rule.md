---
title: "Standing rules: commitments, partitions, enforcement claims, estimates"
type: rule
status: accepted
tags: [enforcement, governance]
created: 2026-10-27
---

# Rule: Standing rules: commitments, partitions, enforcement claims, estimates

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Rule

Never move a management commitment (record variance instead); keep `apn` and `me` apart; claim enforcement only for an observed block on a supported hook; never fabricate estimates, forecasts or percent complete (say `unknown`).

## Canonical source

[SKILL.md](../../SKILL.md#standing-rules), section "Standing rules".

## Enforced by

`rank.py` (forecast always unknown, partitions never ranked together), `doctor.py` (no "enforced" without an observed block).
