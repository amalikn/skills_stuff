# Agent Stack Orchestrator and Global Install Outcome

## Completed

- Added the English-only `orchestrator-follett` persona and the on-demand `orchestrator` skill.
- Added a symlink-only installer with collision preflight, idempotence, owned-link-only uninstall, and a canonical-checkout guard.
- Documented global use for Claude Code, Codex, and compatible agents that explicitly discover `~/.agents/skills`.

## Live Installation

The installer created 123 verified links from the canonical Agent Stack source:

- 15 Claude personas in `~/.claude/agents`.
- 36 skills in each of `~/.claude/skills`, `~/.codex/skills`, and `~/.agents/skills`.
- `frontend-design` uses a `SKILL.md` adapter symlink in each client directory.

The existing global Codex `skill-creator` directory remains intact and excluded from Agent Stack installation. Empty pre-existing frontend adapter directories were reused; no content was overwritten.

## Validation

- `just test` passed: 25 tests.
- Canonical real-home `just global-dry-run` reported 123 planned links and zero collisions.
- Canonical real-home `just global-install install` created all 123 links.
- Final `just global-status` audit reported 123 `correct` links, no worktree targets, and preserved `skill-creator`.

## Operating Model

Use `orchestrator` as the normal Agent Stack entry point for a bounded task. It selects the specialist library internally, respects project-local governance, leaves material decisions to the operator,
and does not start an autonomous loop, daemon, background job, or cross-project memory system.

Future updates remain reviewable through the Agent Stack upstream refresh commands. Global install or removal always runs from the canonical checkout at
`/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack`.
