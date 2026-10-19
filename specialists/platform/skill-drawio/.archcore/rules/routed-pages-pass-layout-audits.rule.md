---
title: Pages the generator routes pass every layout audit
type: rule
status: accepted
tags: [layout, audits]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Pages the generator routes pass every layout audit

Status: accepted (sources `SKILL.md` standing rules, `references/layout-audits.md`; promoted 2026-10-19 on the operator's instruction "promote and accept")

## Rule

Every page the generator routes itself (Overview and End-to-end) passes every layout audit before it ships, and every audit has a test that makes it fail. Flow pages use draw.io's own router and are
not audited.

## Enforcement

`tests/test_helpers.py` `Audits.test_each_fault_fires`; `just example-check --audit` in `just check`.
