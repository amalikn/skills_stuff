---
Title: skill-goal-guard Roadmap
Category: roadmap
Status: current
Authority: local-supplement; follows references/pilot-plan.md and references/feature-inventory.md
Scope: What comes next for skill-goal-guard, in order, with the gate for each step
Last reviewed: 2026-10-27
Summary: Vikunja is deployed and D1-D6 are answered (2026-10-27); next is the operator's Vikunja user and token, then the read-only pilot inventory; later phases L1-L5 open only after the pilot report.
---
# Roadmap

## Now

Current step and open owner items live in [references/pilot-plan.md](references/pilot-plan.md) (steps table and D1-D6). As of 2026-10-27: step 0 done; operator creates the Vikunja user and API token; then step 1.

## Then (pilot steps 3-9)

Owner approves the change list → rewrite `scripts/goal_guard.py` under skill-coder (characterise first) → approve the UNC MVP → Claude Code hook with an observed allowed and blocked action → one
milestone trace with an Excel sample → one snapshot and restore → pilot report.

## Housekeeping

- Remove the empty `docs/goal-guard/{scripts,tests,examples}` folders and their stale `__pycache__` (left after the move; the OPA gate blocks recursive deletes from the agent).
- Add `schemas/mvp.schema.json` with the rewrite.
- Consider a skill-ai-it bootstrap for `AI_NAVIGATION.md`, `context-map.yaml` and a governance check once the pack stabilises.
- Install by symlink into `~/.claude/skills`, `~/.codex/skills` (and the alias `/skill-gg` in `~/.claude/CLAUDE.md`) only when the operator asks.

## Later

Phases L1-L5 and their gates: [references/feature-inventory.md](references/feature-inventory.md).
