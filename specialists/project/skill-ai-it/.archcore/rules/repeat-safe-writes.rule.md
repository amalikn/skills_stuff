---
title: "Every write into a project is repeat-safe"
status: accepted
tags: [safety]
---

Moved 2026-11-11 from [AGENTS.md](../../AGENTS.md) (Working rules), where one line now points here.

## Rule

No wholesale overwrite of a project's file: write inside managed blocks, write `.proposed` files for risky YAML or JSON changes, and report
created, updated, skipped and proposed files separately. Plan by default; `--apply` writes. User content outside managed blocks is preserved.

## Rationale

Bootstrap and refresh run again and again on the same projects; a second run must change nothing a person wrote.
