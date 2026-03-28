# RUNBOOK

## Use When
Use this specialist when onboarding a repo, deciding whether AGENTS guidance is missing or stale, splitting guidance across global versus repo scope, or deciding whether a reusable skill should be created instead of bloating repo instructions.

## Workflow
1. Inspect repo structure, docs, CI, validation entrypoints, and any existing AGENTS or skills.
2. Decide what belongs in global AGENTS, repo AGENTS, reusable skills, and any local-only support docs.
3. Prefer minimal non-duplicative guidance.
4. When repo guidance is detailed but should remain local-only, prefer a thin root `AGENTS.md` plus longer support docs under `.agents/`.
5. Implement in the correct source-of-truth location.
6. Verify there are no conflicting or redundant instructions.
