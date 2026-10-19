---
title: The code map holds decisions only
type: rule
status: proposed
tags: [code-map, checkers]
created: 2026-10-19
---

# Rule: The code map holds decisions only

Status: proposed (operator decision in chat, 2026-10-19: "is there a need of code-map ... or is context-map enough?"; awaits promotion approval)

## Rule

A project's `code-map.toml` holds the human decisions the checkers act on: scan roots, the project's Python grammar, size limit overrides, import
layers, write-gate exceptions with reasons, timeout roots and each module's promotion status. It never holds facts the code states (line counts,
import edges, header text); the checkers measure those, and their shrink-only baselines are separate machine-written files. It is TOML so the
helpers read it with the project's own Python. `context-map.yaml` stays the routing map (skill-ai-it owns it) and only points to the code map.

## Enforcement

`scripts/code_map.py` refuses an unknown section (a typo would switch a rule off), a module entry with an unknown status, a promoted module with no
skill file, and an unpromoted one with no reason or needs; `tests/test_helpers.py` (CodeMap) proves each refusal.
