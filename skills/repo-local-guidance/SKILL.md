---
name: repo-local-guidance
description: Use this skill when a repository needs local-only guidance with a thin root AGENTS.md and longer support docs under .agents/.
metadata:
  short-description: Manage local repo guidance
---

# Repo Local Guidance

## Use When
Use this skill when a repository needs local-only guidance with a thin root `AGENTS.md` and longer support docs under `.agents/`.

Trigger this skill for:
- splitting a long repo `AGENTS.md` into a thin root file plus `.agents/` support docs
- setting up repo-local guidance that must not be pushed
- creating or maintaining `.git/info/exclude` entries for `AGENTS.md`, `.agents/`, and related local-only artifacts
- documenting repo-specific architecture, topology, validation, or task patterns outside the root `AGENTS.md`
- managing local `.vscode/` overrides that support repo-local guidance without polluting the remote repo

## Workflow
1. Inspect the repo and identify what must stay in the auto-loaded root `AGENTS.md`.
2. Move longer repo-specific detail into focused `.agents/*.md` support docs.
3. Keep the root `AGENTS.md` thin and reference the relevant `.agents/` docs explicitly.
4. Add `AGENTS.md` and `.agents/` to `.git/info/exclude` so the guidance stays local-only.
5. When local VS Code behavior matters, treat `.vscode/` as another local support artifact and either keep it local with git controls or remove it from repo tracking if the user wants it gone from the remote.
6. Save plan and outcome markdown with the canonical specialist source.

## Rules
- Root `AGENTS.md` stays at repo root because Codex auto-loads repo guidance only from `AGENTS.md` / `AGENTS.override.md` in the repo tree.
- `.agents/` is support material, not an auto-loaded replacement for root `AGENTS.md`.
- Use `.git/info/exclude`, not tracked `.gitignore`, for local-only repo guidance unless the user explicitly asks for repo-wide ignore behavior.
- Keep cross-repo policy in `~/.codex/AGENTS.md`, not in repo-local guidance.

## Stable Facts
- Root `AGENTS.md` stays at repo root because Codex auto-loads repo guidance from `AGENTS.md`, not from `.agents/`.
- `.agents/` is the correct place for longer repo-local support docs when root `AGENTS.md` should stay thin.
- `.git/info/exclude` is the correct local-only ignore mechanism for `AGENTS.md` and `.agents/` when they must not be pushed.
- `.vscode/` may also be part of local-only repo guidance when editor behavior is customized locally.

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/healthcheck.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/rollback.md
- references/CONTEXT/assumptions.md
- references/CONTEXT/dependencies.md
- references/CONTEXT/boundaries.md

## Source
- specialist_type: project
- slug: skill-repo-local-guidance
- version: 0.1.0
