# PROFILE

## Subject
- Type: project
- Name: repo_local_guidance
- Slug: skill-repo-local-guidance

## Stable Facts
- Root AGENTS.md stays at repo root because Codex auto-loads repo guidance from AGENTS.md, not from .agents/.
- `.agents/` is the place for longer repo support docs when root AGENTS.md should stay thin.
- Governance files are tracked in Git on the operator's GitHub; a company clone holds excluded symlinks to the real files in the operator's GitHub companion repo
  (operator, 2026-11-09).
