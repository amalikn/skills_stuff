---
Title: skill-goal-guard Roadmap
Category: roadmap
Status: current
Authority: local-supplement; follows references/pilot-plan.md and references/feature-inventory.md
Scope: What comes next for skill-goal-guard, in order, with the gate for each step
Last reviewed: 2026-10-27
Summary: Vikunja is deployed and D1-D6 are answered (2026-10-27); next is the operator's Vikunja user and token, then the read-only pilot inventory; later phases L1-L5 open only after the pilot report.
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
---

# Roadmap

## Current phase

**2026-10-27.** Pilot step 0 done; step 4 built ahead of steps 1-3 (tools fixture-tested only). Next: operator creates the Vikunja user and API token; the open live checks in
[scripts/readme.md](scripts/readme.md); then step 1. Steps and owner decisions: [references/pilot-plan.md](references/pilot-plan.md).

## Then (pilot steps 3-9)

Owner approves the change list → approve the UNC MVP → Claude Code hook with an observed allowed and blocked action → one
milestone trace with an Excel sample → one snapshot and restore → pilot report.

## Housekeeping

- Remove the empty `docs/goal-guard/{scripts,tests,examples}` folders and their stale `__pycache__` (left after the move; the OPA gate blocks recursive deletes from the agent).
- Add `schemas/mvp.schema.json` with the rewrite.
- Done 2026-10-27: skill-ai-it bootstrap (`AI_NAVIGATION.md`, `context-map.yaml`, `scripts/check_governance.py`).
- Install by symlink into `~/.claude/skills`, `~/.codex/skills` (and the alias `/skill-gg` in `~/.claude/CLAUDE.md`) only when the operator asks.

## Later

Phases L1-L5 and their gates: [references/feature-inventory.md](references/feature-inventory.md).
