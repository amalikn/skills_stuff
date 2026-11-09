# RUNBOOK

Use this specialist to give a repository thin root guidance: a short auto-loaded `AGENTS.md` plus longer support docs under `.agents/`. Governance files are
tracked in Git (operator, 2026-11-09; governance `categories/repo-structure-guide.md`, Git tracking).

## Workflow

1. Inspect the repo and identify what must stay in the auto-loaded root `AGENTS.md` (always-on rules and pointers).
2. Move longer repo-specific detail into focused `.agents/*.md` support docs, one topic per file.
3. Keep the root `AGENTS.md` thin and link each `.agents/` doc at the point an agent needs it.
4. Decide where the files are versioned, from the clone's `origin` remote:
   - **Operator GitHub** (`github.com/amalikn/...`): commit `AGENTS.md`, `CLAUDE.md` and `.agents/` in the repo itself. Remove any exclusion of them
     from `.git/info/exclude` or `.gitignore` and report it.
   - **Company remote** (Bitbucket `activ8me` and any other non-operator host): never commit them there. Keep the real files in the operator's GitHub
     companion repo (`local-knowledge-ansible/<repo>/<repo>-root-governance/` for the Ansible repos), symlink them into the clone, and keep the
     symlinks in the clone's `.git/info/exclude`. Commit the real files in the companion repo.
5. Any other exclusion (`.vscode/`, caches, tool folders): ask the operator first, naming the path, the reason and the mechanism.
6. Save plan and outcome markdown with the canonical specialist source.

## Rules

- Root `AGENTS.md` stays at the repo root because Codex auto-loads repo guidance only from `AGENTS.md` / `AGENTS.override.md` in the repo tree.
- `.agents/` is support material, not an auto-loaded replacement for the root `AGENTS.md`.
- An exclude pattern without a leading `/` matches at every depth: `AGENTS.md` in `.git/info/exclude` hides every nested `AGENTS.md` too. That is wanted in a
  company clone and is the defect this specialist removes from an operator repo.
- Keep cross-repo policy in the global `~/.agents/AGENTS.md`, not in repo guidance.

## Stable Facts

- Root `AGENTS.md` stays at the repo root because Codex auto-loads repo guidance from `AGENTS.md`, not from `.agents/`.
- `.agents/` is the place for longer repo support docs when the root `AGENTS.md` should stay thin.
- Governance files are tracked on the operator's GitHub; in a company clone they are symlinks into the GitHub companion repo, excluded locally.
