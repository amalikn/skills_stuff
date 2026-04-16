---
name: repo-bootstrap-and-governance
description: Use this skill when onboarding a repository, deciding whether global versus repo guidance is missing or stale, or deciding whether a skill, root AGENTS.md, or local-only .agents/ support docs are the right home for guidance.
metadata:
  short-description: Bootstrap repo governance
---

# Repo Bootstrap and Governance

## Use When
Use this skill when onboarding a repository, deciding whether global versus repo guidance is missing or stale, or deciding whether a skill, root `AGENTS.md`, or local-only `.agents/` support docs are the right home for guidance.

Trigger this skill for:
- repo onboarding
- missing or stale repo `AGENTS.md`
- deciding global vs repo vs skill scope
- introducing a thin root `AGENTS.md` plus `.agents/` support docs
- separating tracked governance docs from local-only operator guidance

## Workflow
1. Inspect repo structure, docs, CI, validation entrypoints, generated artifacts, and existing AGENTS/skills.
2. Decide what belongs in global `~/.codex/AGENTS.md`, repo root `AGENTS.md`, reusable skills, and local-only `.agents/` docs.
3. Prefer minimal, non-duplicative guidance.
4. When repo guidance is detailed but should remain local-only, prefer a thin root `AGENTS.md` plus longer support docs under `.agents/`.
5. Implement in the correct canonical source-of-truth location, then update runtime installs if needed.

## Rules
- Do not restate global guidance in repo `AGENTS.md` unless repo context changes the rule materially.
- Prefer improving an existing strong skill over creating a duplicate.
- Author reusable skills in canonical source repos when that workflow exists.
- Distinguish tracked repo governance from local-only operator guidance.

## Stable Facts
- Do not restate global guidance in repo AGENTS unless it changes materially in repo context.
- Prefer improving an existing strong skill over creating a duplicate.
- Author reusable skills in canonical source repos when that workflow exists.

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
- slug: skill-repo-bootstrap-and-governance
- version: 0.1.0
