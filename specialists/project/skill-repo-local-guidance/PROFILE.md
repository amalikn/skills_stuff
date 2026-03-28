# PROFILE

## Subject
- Type: project
- Name: repo_local_guidance
- Slug: skill-repo-local-guidance

## Stable Facts
- Root AGENTS.md stays at repo root because Codex auto-loads repo guidance from AGENTS.md, not from .agents/.
- `.agents/` is the correct place for longer repo-local support docs when root AGENTS.md should stay thin.
- `.git/info/exclude` is the correct local-only ignore mechanism for AGENTS.md and `.agents/` when they must not be pushed.
