---
title: "The hook ships as a draft with file-scoped verdicts"
type: adr
status: accepted
tags: [decision, enforcement]
created: 2026-10-27
---

# ADR: The hook ships as a draft with file-scoped verdicts

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Decision

The Claude Code PreToolUse hook is advisory by default and blocks only in `--mode blocking`; it fails closed on an unrecognised payload or its own crash. A PROCEED verdict covers only the files its proposal listed, for two hours, against the current contract revision. Nothing is called enforced until a block has been observed.

## Canonical source

[references/enforcement-and-hooks.md](../../references/enforcement-and-hooks.md#learned), section "Learned".
