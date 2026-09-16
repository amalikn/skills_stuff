# skill-repomix SCRATCHPAD <!-- KEEP -->

## Current state

v0.2.0 shipped 2026-06-18. Behavioral contract fully strengthened. Generator (create-skill-repomix.sh) is canonical source of truth — all content lives there, generated files are outputs. Validation suite passes cleanly including ShellCheck.

## Open items

- None currently — v0.2.0 complete

## Key anchors

| Item | Value |
|---|---|
| Skill root | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-repomix/` |
| Generator | `create-skill-repomix.sh` (source of truth for all generated files) |
| Temp-dir gen pattern | `./create-skill-repomix.sh --target-dir /tmp/sr-regen && cp /tmp/sr-regen/<file> ./<file>` |
| ShellCheck path | `/opt/homebrew/bin/shellcheck` |
| Validate | `scripts/validate-skill.sh` |
| Full test | `tests/test-skill-repomix.sh` (includes idempotency check) |
| PC project | `skills_stuff` (b8c5525e) channel `skill-repomix` |
| MK channel | `skill-repomix` |

## Recent decisions

- **2026-06-18** — Shell profiles merged: bash.json + shell-infrastructure.json → single bash.json (Bash and Shell, 90K budget). Rationale: many repos mix library + deployment scripts; single profile avoids ambiguous detection.
- **2026-06-18** — Generator-first rule adopted: all skill changes go to create-skill-repomix.sh first, then regenerate into temp dir and copy back. Never edit generated files for persistent changes.
- **2026-06-18** — v0.2.0 strengthening: token-budget thresholds, pack-too-large retry (max 3), run report schema, ambiguous routing escalation, audience/authority split.

## Session history

- **2026-06-18** — v0.2.0 shipped: 5 new SKILL.md sections (thresholds, retry, report, routing, audience), pattern updates (4 files), ShellCheck integration in validator, justfile + bash profiles added, shell-infrastructure merged into bash, claude-repomix-review wrapper created, idempotency test added. All validation green.

## Next actions

- None — consider bumping to v0.3.0 when next profile or pattern addition is needed

## Memory pointers

- MK channel: `skill-repomix` — keys: `skill-repomix.v0.2.0-strengthening`, `skill-repomix.generator-source-of-truth`, `skill-repomix.profile-consolidation`, `skill-repomix.shellcheck-integration`, `skill-repomix.files-changed`
- PC: `skills_stuff` project, channel `skill-repomix`, checkpoint `slurp-20260618-skill-repomix-v0.2.0`
