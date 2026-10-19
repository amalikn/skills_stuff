---
title: A drawing a person edited by hand is source
type: rule
status: accepted
tags: [drawings, write-safety]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: A drawing a person edited by hand is source

Status: accepted (operator, enterprise-strategy 2026-10-12 and feedback 2026-10-05; sources `SKILL.md` "Orient first", `references/data-first-diagrams.md`, `sources.yaml` C-D03; promoted 2026-10-19 on
the operator's instruction "promote and accept")

## Rule

Patch or append only, keep a backup, and never regenerate over it. State what was touched.

## Enforcement

`scripts/flowmap/pages.py` `write_drawing` refuses an existing file without the generated banner; `tests/test_helpers.py` `test_write_refuses_a_hand_made_drawing` proves it.
