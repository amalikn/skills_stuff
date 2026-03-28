# RUNBOOK

## Use When
Use this specialist when a repository needs local-only guidance with a thin root `AGENTS.md` and longer support docs under `.agents/`.

## Workflow
1. Inspect the repo and identify what must stay in the auto-loaded root `AGENTS.md`.
2. Move longer repo-specific detail into focused `.agents/*.md` support docs.
3. Keep the root `AGENTS.md` thin and reference the relevant `.agents/` docs explicitly.
4. Add `AGENTS.md` and `.agents/` to `.git/info/exclude` so the guidance stays local-only.
5. When local VS Code explorer behavior must also be kept local, use repo-local `.vscode/settings.json` overrides and protect them from pushes with local git controls such as `skip-worktree`, or remove `.vscode` from repo tracking if the user wants it gone from the remote.
6. Capture `.vscode/` with the repo knowledge workflow if those local overrides matter and should be restorable.
7. Save plan and outcome markdown with the canonical specialist source.

## Rules
- Root `AGENTS.md` stays at repo root because Codex auto-loads repo guidance only from `AGENTS.md` / `AGENTS.override.md` in the repo tree.
- `.agents/` is support material, not an auto-loaded replacement for root `AGENTS.md`.
- Use `.git/info/exclude`, not tracked `.gitignore`, for local-only repo guidance.
- Keep cross-repo policy in `~/.codex/AGENTS.md`, not in repo-local guidance.

## Stable Facts
- Root `AGENTS.md` stays at repo root because Codex auto-loads repo guidance from `AGENTS.md`, not from `.agents/`.
- `.agents/` is the correct place for longer repo-local support docs when root `AGENTS.md` should stay thin.
- `.git/info/exclude` is the correct local-only ignore mechanism for `AGENTS.md` and `.agents/` when they must not be pushed.
- `.vscode/` may also be part of local-only repo guidance when VS Code explorer behavior is customized locally.
