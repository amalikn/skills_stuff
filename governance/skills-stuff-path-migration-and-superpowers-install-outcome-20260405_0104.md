# skills_stuff Path Migration And Superpowers Install Outcome

Date: 2026-04-05 01:04

## Completed
- Moved the canonical repo from `/Volumes/Data/_ai/_mcp/skills_stuff` to `/Volumes/Data/_ai/_skills/skills_stuff`.
- Renamed the umbrella directory from `/Volumes/Data/_ai/_skill` to `/Volumes/Data/_ai/_skills`.
- Updated current live references in Codex config, governance indexes, `mcp-skill-builder` docs/config, the current governance verification script, and current repo-local files.
- Promoted `superpowers` from `/Volumes/Data/_ai/_skills/skills_stuff/pending_skills/superpowers` to `/Volumes/Data/_ai/_skills/skills_stuff/superpowers`.
- Installed `superpowers` for Codex native discovery via:
  - `~/.agents/skills/superpowers -> /Volumes/Data/_ai/_skills/skills_stuff/superpowers/skills`

## Validation Performed
- Verified `/Volumes/Data/_ai/_skills/skills_stuff` exists.
- Verified targeted live surfaces no longer contain `/_mcp/skills_stuff` or `/_skill/skills_stuff` references.
- Verified the symlink exists and resolves to the promoted skills directory.
- Verified the discovered skill files through the symlink:
  - `brainstorming`
  - `dispatching-parallel-agents`
  - `executing-plans`
  - `finishing-a-development-branch`
  - `receiving-code-review`
  - `requesting-code-review`
  - `subagent-driven-development`
  - `systematic-debugging`
  - `test-driven-development`
  - `using-git-worktrees`
  - `using-superpowers`
  - `verification-before-completion`
  - `writing-plans`
  - `writing-skills`

## Intentional Non-Edits
- Historical backups such as `AGENTS.md.bak-20260329` were left unchanged.
- Timestamped historical audits and outcome records outside the active surface were not rewritten.

## Remaining Caveat
- Codex restart is still required before a new session will discover the newly installed `superpowers` skills.
