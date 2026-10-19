---
title: Front ends at the top of scripts/, library in packages
type: adr
status: accepted
tags: [layout, engine]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: Front ends at the top of scripts/, library in packages

Status: accepted (applies skill-coder's package rule, operator 2026-10-19; sources `AGENTS.md` working rules, `scripts/README.md`; candidate confidence medium; promoted 2026-10-19 on the operator's
instruction "promote and accept")

## Context

skill-coder sets the package rule for every project. This pack records how it applies here because consumers import the library by path and need a stable layout.

## Decision

Runnable front ends sit at the top of `scripts/`. The library is the `drawio` (file format) and `flowmap` (map model, profile, pages) packages beneath it.

## Consequences

- skill-coder `module_groups.py --strict` in `just self-check` enforces the layout.
- If skill-coder's rule changes, this ADR follows it; supersede it in place with a dated note rather than diverging.
