---
title: "Front-end exit codes"
type: spec
status: accepted
tags: [contract, enforcement]
created: 2026-10-27
---

# Spec: Front-end exit codes

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Contract

Every front end exits 0 on success, 3 on a negative answer to act on, 2 on bad input and 1 on a Vikunja failure or refused write; the hook exits 0 (pass or advisory) or 2 (blocked).

## Canonical source

[scripts/readme.md](../../scripts/readme.md#exit-codes-and-settings), section "Exit codes and settings".

## Notes

`scripts/goal_guard_lib/cli.py`; tested in `tests/test_cli.py`.
