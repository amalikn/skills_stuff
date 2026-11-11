---
title: "A layout or routing change updates its companions in the same pass"
status: accepted
tags: [governance]
---

Moved 2026-11-11 from [AGENTS.md](../../AGENTS.md) (Working rules), where one line now points here.

## Rule

When `SKILL.md` changes the package layout, update `README.md`, `AI_NAVIGATION.md` and `context-map.yaml` in the same pass. A material change to
`SKILL.md`, a template, a pattern or governance routing gets a short `CHANGELOG.md` entry (`just changelog-entry`). `CLAUDE.md` stays a thin
wrapper of `AGENTS.md`.

## Rationale

The navigation files are what the next agent reads first; a layout they do not describe is invisible.
