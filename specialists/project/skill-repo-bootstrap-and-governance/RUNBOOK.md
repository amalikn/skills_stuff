# RUNBOOK

> **Superseded in part (operator, 2026-11-09):** governance files (`AGENTS.md`, `CLAUDE.md`, `.agents/` and the rest listed in governance
> `categories/repo-structure-guide.md`, Git tracking) are always tracked in a clone of the operator's GitHub and never excluded there. In a company
> clone (Bitbucket `activ8me`) they are never committed: they stay in `.git/info/exclude` and are versioned in the operator's GitHub companion repo.
> Any other exclusion is confirmed with the operator first. Where this skill says otherwise, that rule wins.

## Use When
Use this specialist when onboarding a repo, deciding whether AGENTS guidance is missing or stale, splitting guidance across global versus repo scope, or deciding whether a reusable skill should be created instead of bloating repo instructions.

## Workflow
1. Inspect repo structure, docs, CI, validation entrypoints, and any existing AGENTS or skills.
2. Decide what belongs in global AGENTS, repo AGENTS, reusable skills, and any local-only support docs.
3. Prefer minimal non-duplicative guidance.
4. When repo guidance is detailed but should remain local-only, prefer a thin root `AGENTS.md` plus longer support docs under `.agents/`.
5. Implement in the correct source-of-truth location.
6. Verify there are no conflicting or redundant instructions.
