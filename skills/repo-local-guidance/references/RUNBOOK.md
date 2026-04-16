# RUNBOOK

## Use When
Use this specialist when a repo needs local-only guidance, the root `AGENTS.md` is getting too long, or the guidance should be split into a thin auto-loaded root file plus `.agents/` support docs.

## Workflow
1. Inspect the current repo guidance and decide which rules are always-on versus support material.
2. Keep the root `AGENTS.md` thin so it remains readable and auto-loaded.
3. Move longer repo-specific guidance into focused docs under `.agents/`.
4. Add `AGENTS.md` and `.agents/` to `.git/info/exclude` when the guidance must stay local-only.
5. Keep cross-repo rules in `~/.codex/AGENTS.md`, not in repo-local docs.
6. When guidance changes are implemented, save plan and outcome markdown with the canonical skill source.
