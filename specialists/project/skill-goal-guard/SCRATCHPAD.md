---
Title: skill-goal-guard Scratchpad
Category: scratchpad
Kind: state
Status: current
Authority: working state only; durable rules live in references/, decisions in changelog.md and project-context
Scope: Current state, open items, next actions and memory pointers for skill-goal-guard
Last reviewed: 2026-10-27
Summary: Working state after the 2026-10-27 build session; pilot step 0 done (Vikunja 2.7.1 local), step 1 inventory next.
---
# SCRATCHPAD

## Current state — KEEP

- Skill pack built 2026-10-27: root `SKILL.md` (skill-goal-guard, alias skill-gg), 13 references, v0.1 prototype CLI (`just check` green), sources verbatim in `docs/`.
- Vikunja 2.7.1 running at http://localhost:3456 from `/Volumes/Data/_ai/_tool/tools_stuff/vikunja`; no user or token yet.
- Pilot: step 0 done; D1-D6 answered ([references/pilot-plan.md](references/pilot-plan.md)).

## Open items — KEEP

- D3 risk: a signing key in the ssh-agent could let an agent sign approvals; settle before pilot step 5 (proposed: hardware key or per-use prompt; not decided).
- D4: confirm which plan revision was issued (2026-10-14 email) before registering a baseline.
- Housekeeping deferred by the operator: install symlinks and `/skill-gg` alias, skill-ai-it bootstrap, empty `docs/goal-guard/{scripts,tests,examples}` folders, odd-named test dump in
  `tools-data/vikunja/dumps`.
- `tools_stuff/vikunja` and `tools_stuff/CHANGELOG.md` not committed (commit request was scoped to skills_stuff).
- Write-back owed next session (operator, 2026-10-27: "capture them both for the next chat session"):
  1. OPA tool (`/Volumes/Data/_ai/_tool/tools_stuff/opa`): record the traps hit 2026-10-27 per its AGENTS.md feedback rule (ROADMAP or troubleshooting): recursive delete of `__pycache__` blocked even
     without a force flag; a pipe into the SHA-sum tool is read as pipe-to-shell (the next word after the pipe starts with `sh`); the words alone inside heredoc prose or a changelog body also trigger
     it. Workarounds: `md5` or Python `hashlib`; Edit/Write tools for text naming it. Today only in auto-memory `reference_opa_ledger_gate.md`.
  2. skill-coder candidate (`reusable_candidate`, references/refactoring-and-promotion.md "Moving code"): prove a move unchanged with per-file sha256 plus a hash of the CLI's stdout for fixed inputs,
     before and after; an untracked prototype with no callers needs no shim, only a moved-paths table. Evidence: skill-goal-guard commit 1dff9c8, `scripts/readme.md` Moved paths, output hash
     `2504fb41c7e48f1f` unchanged.

## Recent decisions — KEEP

Vikunja owns live tasks; full v1.7 pilot; one `apn` repo scoped by path; pilot spoke UNC; signed-commit approvals; `.gg/`; Vikunja on OrbStack with SQLite in `tools_stuff` (all 2026-10-27, details in
[changelog.md](changelog.md)).

## Next actions — KEEP

1. Operator: `cd /Volumes/Data/_ai/_tool/tools_stuff/vikunja && just create-user <username> <email>`; API token in KeePassXC; share the entry name.
2. Pilot step 1: read-only inventory of `apn/unified-network-controller` and `apn/enterprise-strategy`; capture Claude Code hook payloads.
3. Settle the D3 risk; then step 4 rewrite of `scripts/goal_guard.py` under skill-coder.

## Session history — KEEP

- 2026-10-27: reviewed sources (8 conflicts), restructured and renamed, consolidated 13 references, deployed Vikunja 2.7.1, answered D1-D6, independent structure review applied.

## Memory pointers — KEEP

- memory-keeper channel `skill-goal-guard`: keys `skill-goal-guard.{review-conflicts,structure,decisions,vikunja-ops,incidents,next,writeback-owed}`, `session.closeout.20261027.skill-goal-guard`.
- project-context project `skill-goal-guard` (ed1a3a1b-0252-4ac9-a368-3b7d8fcdad17): 16 decisions, notes on review, restructure, Vikunja, incidents, next actions, write-backs owed.
- Checkpoints: `slurp-20261027-skill-goal-guard`, `slurp-20261027-skill-goal-guard-writeback-defer` (both backends).
