---
title: "Run catalogued tasks only; a new script is catalogued"
status: accepted
tags: [scripts]
---

Moved 2026-11-11 from [AGENTS.md](../../AGENTS.md) (Working rules), where one line now points here.

## Rule

Before running a project's automation, read its task catalog in this order: `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`,
`package.json`; prefer `just <task>`. An uncatalogued script is unknown safety: do not run destructive, review-required or unknown-safety tasks
without review. A script added, changed or removed here updates `scripts/README.md` and its recipe in the same pass.
