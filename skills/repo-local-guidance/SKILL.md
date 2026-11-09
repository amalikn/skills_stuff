---
name: repo-local-guidance
description: Use this skill when a repository needs thin root guidance: a short AGENTS.md plus longer support docs under .agents/, tracked on the operator's GitHub (company clones: excluded symlinks to a GitHub companion repo).
metadata:
  short-description: Manage thin repo guidance and where it is versioned
---

# Repo Local Guidance

## Use When
Use this skill when a repository needs a thin root `AGENTS.md` with longer support docs under `.agents/`, or when its governance files are excluded from Git.

Trigger this skill for:
- splitting a long repo `AGENTS.md` into a thin root file plus `.agents/` support docs
- deciding where a repo's governance files are versioned (the repo itself, or the operator's GitHub companion repo for a company clone)
- finding and removing an exclusion of `AGENTS.md`, `.agents/` or another governance file in an operator repo
- setting up the excluded-symlink pattern in a company clone (Bitbucket `activ8me`)

## Workflow
1. Inspect the repo and identify what must stay in the auto-loaded root `AGENTS.md` (always-on rules and pointers).
2. Move longer detail into focused `.agents/*.md` docs, one topic per file, linked from the root file.
3. Read the clone's `origin` remote.
   - Operator GitHub (`github.com/amalikn/...`): commit `AGENTS.md`, `CLAUDE.md` and `.agents/` in the repo; remove any exclusion of them and report it.
   - Company remote: never commit them there. Real files in the operator's GitHub companion repo (`local-knowledge-ansible/<repo>/<repo>-root-governance/`),
     symlinks in the clone, symlinks in the clone's `.git/info/exclude`; commit the real files in the companion repo.
4. Any other exclusion (`.vscode/`, caches, tool folders): ask the operator first, naming the path, the reason and the mechanism.
5. Save plan and outcome markdown with the canonical specialist source.

## Rules
- Governance files are tracked on the operator's GitHub and never excluded there (operator, 2026-11-09; governance `categories/repo-structure-guide.md`, Git tracking).
- Root `AGENTS.md` stays at the repo root because Codex auto-loads repo guidance only from `AGENTS.md` / `AGENTS.override.md` in the repo tree.
- `.agents/` is support material, not an auto-loaded replacement for the root `AGENTS.md`.
- An exclude pattern without a leading `/` matches at every depth: right for a company clone, a defect in an operator repo.
- Keep cross-repo policy in the global `~/.agents/AGENTS.md`, not in repo guidance.

## Stable Facts
- Root `AGENTS.md` stays at repo root because Codex auto-loads repo guidance from `AGENTS.md`, not from `.agents/`.
- `.agents/` is the place for longer repo support docs when root `AGENTS.md` should stay thin.
- A company clone holds symlinks to the real governance files in the operator's GitHub companion repo, listed in its `.git/info/exclude`.

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/triage.md
- references/CHECKLISTS/healthcheck.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/rollback.md
- references/CONTEXT/assumptions.md
- references/CONTEXT/dependencies.md
- references/CONTEXT/boundaries.md
- references/CONTEXT/relationships.md

## Source
- specialist_type: project
- slug: skill-repo-local-guidance
- version: 0.2.0
