---
title: "Templates are the source; SKILL.md fallbacks follow them"
status: accepted
tags: [templates]
---

Moved 2026-11-11 from [AGENTS.md](../../AGENTS.md) (Working rules), where one line now points here.

## Rule

`templates/` is the source of every generated file's content; `patterns/` holds optional guidance modules; `SKILL.md` is the orchestration
contract. When a template changes, check the matching fallback or example in `SKILL.md` in the same pass, so an embedded copy never drifts.
A file this skill generates for projects starts from a template here, never from text written inline in a mode's steps.

## Rationale

Projects are bootstrapped and refreshed from these files; a fallback that drifted from its template produces two versions of the same file.
