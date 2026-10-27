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

- Skill pack built 2026-10-27: root `SKILL.md` (skill-goal-guard, alias skill-gg), 13 references, sources verbatim in `docs/`.
- Pilot tools written 2026-10-27 under skill-coder (step 4 plus tools for steps 6-8): seven front ends over `scripts/goal_guard_lib/`, 71 tests, `just check` green; fixtures only, uncommitted.
- Vikunja 2.7.1 running at http://localhost:3456 from `/Volumes/Data/_ai/_tool/tools_stuff/vikunja`; no user or token yet.
- Pilot: step 0 done; D1-D6 answered ([references/pilot-plan.md](references/pilot-plan.md)).

## Open items — KEEP

- D3 risk: a signing key in the ssh-agent could let an agent sign approvals; settle before pilot step 5 (proposed: hardware key or per-use prompt; not decided).
- D4: confirm which plan revision was issued (2026-10-14 email) before registering a baseline.
- Housekeeping deferred by the operator: install symlinks and `/skill-gg` alias, skill-ai-it bootstrap, empty `docs/goal-guard/{scripts,tests,examples}` folders, odd-named test dump in
  `tools-data/vikunja/dumps`.
- Open live checks for the new tools (need the owner's Vikunja token): relation direction (GG-305), hook captures plus one observed block, restore read-back; list in `scripts/readme.md`.
- SKILL.md Contents: "File '#...' not found" and dead TOC links come from VS Code's chat prompt-file validator, which opens SKILL.md as a skill file, not Markdown (message found in VS Code
  1.135 `nls.metadata.json`). The anchors are correct (10/10). Operator choice, not decided: switch that tab to Markdown, or `"files.associations": {"**/SKILL.md": "markdown"}` (loses VS Code's
  skill checks). The markdown hook rebuilds the linked Contents, so the file stays as it is.
- Proposed, not decided (review note 2026-10-27): cover shell writes the hook cannot see before relying on the pilot, e.g. a git pre-commit check of protected `.gg/` records and changed files
  against the last PROCEED, and read-only file modes on the protected records (doctor already reports them writable).
- `tools_stuff/vikunja` and `tools_stuff/CHANGELOG.md` not committed (commit request was scoped to skills_stuff).
- Write-backs owed from the 15:03 session, done 2026-10-27 evening: skill-coder "Moving code" entry written and committed with this session; OPA gate traps written to
  `tools_stuff/opa/ROADMAP.md` Backlog but NOT committed (that file holds another session's uncommitted M8 work; the commit request was scoped to skills_stuff).

## Recent decisions — KEEP

Vikunja owns live tasks; full v1.7 pilot; one `apn` repo scoped by path; pilot spoke UNC; signed-commit approvals; `.gg/`; Vikunja on OrbStack with SQLite in `tools_stuff` (all 2026-10-27, details in
[changelog.md](changelog.md)).

## Next actions — KEEP

1. Operator: `cd /Volumes/Data/_ai/_tool/tools_stuff/vikunja && just create-user <username> <email>`; API token in KeePassXC; share the entry name.
2. Pilot step 1: read-only inventory of `apn/unified-network-controller` and `apn/enterprise-strategy`; capture Claude Code hook payloads.
3. Settle the D3 risk before pilot step 5.
4. Run the open live checks in `scripts/readme.md` once a token exists; write the results back as Learned entries.

## Session history — KEEP

- 2026-10-27 (evening): pilot tools written and tested; hook scoped to the verdict's files after a review note; SKILL.md and AGENTS.md table alignment fixed.
- 2026-10-27: reviewed sources (8 conflicts), restructured and renamed, consolidated 13 references, deployed Vikunja 2.7.1, answered D1-D6, independent structure review applied.

## Memory pointers — KEEP

- memory-keeper channel `skill-goal-guard`: keys `skill-goal-guard.{review-conflicts,structure,decisions,vikunja-ops,incidents,next,writeback-owed,pilot-tools,findings-20261027-evening}`, `session.closeout.20261027.skill-goal-guard`,
  `session.closeout.20261027.skill-goal-guard-pilot-tools`.
- project-context project `skill-goal-guard` (ed1a3a1b-0252-4ac9-a368-3b7d8fcdad17): 19 decisions, notes on review, restructure, Vikunja, incidents, next actions, write-backs, pilot tools, findings.
- Checkpoints: `slurp-20261027-skill-goal-guard`, `slurp-20261027-skill-goal-guard-writeback-defer`, `slurp-20261027-skill-goal-guard-pilot-tools` (both backends).
