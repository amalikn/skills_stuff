# Agent Stack Global Install Design

## Goal

Make the reusable Agent Stack available from every Claude Code and Codex session, plus compatible agents that discover `~/.agents/skills`, without copying it into each project. Add an opt-in
Orchestrator that coordinates its specialists while keeping
project-level governance and human decision ownership local.

## Decision

Agent Stack remains the single canonical source at `specialists/agent-stack/`. A new installer will create individual symlinks from the global client directories to canonical persona and skill entries.
No persona or skill content is copied into a client directory.

It will not replace, copy, rename, or overwrite existing global entries. The install is atomic at the selected client scope: a collision stops the operation before any new link is created.

## Orchestrator

`skills/orchestrator/SKILL.md` is the normal single entry point to Agent Stack. The operator gives it the task rather than selecting specialists directly. It first reads project constraints and
available evidence, then uses the manifest and `team` skill to select the smallest useful set of roles and procedures. It must state its selected team, decision gates, and synthesis contract before
asking specialists to contribute.

The coordination flow is: frame the task; select skills and personas; run bounded specialist passes; distinguish evidence, inference, and disagreement; return one recommendation, residual risks, and
the next action. Direct specialist use is an explicit exception for a requested narrow task. It detects circular work and reports a blocker rather than inventing progress. It never starts a daemon,
forces a GO decision, writes cross-project state, or overrides a project’s own instructions and permissions.

`personas/orchestrator-follett.md` is coordination persona guidance for runtimes that support it. Inspired by Mary Parker Follett, it favours shared purpose, integration of genuine disagreement,
clear decision rights, and "power with" specialists rather than command over them. It does not substitute its judgment for the user’s on material decisions.

## Client Mapping

| Client | Global destination | Entries |
| --- | --- | --- |
| Claude Code | `~/.claude/agents` | 15 persona Markdown files |
| Claude Code | `~/.claude/skills` | 36 skill links; existing `skill-creator` is retained |
| Codex | `~/.codex/skills` | 36 skill links; existing `skill-creator` is retained |
| Compatible `.agents` clients | `~/.agents/skills` | 36 skill links; existing `skill-creator` is retained |

The `frontend-design.md` single-file source requires a small client adapter directory whose `SKILL.md` is itself a symlink to the canonical file; all package skills are installed as direct directory
symlinks. An empty pre-existing frontend adapter directory may be reused; a nonempty directory is a collision. Personas are intentionally not installed into `.agents`, because it has no universal
persona-discovery convention.

## Commands

`just global-status` reports the expected links and their current state without changes. `just global-dry-run` previews a complete install. `just global-install install` creates links only after preflight succeeds. `just global-uninstall uninstall` removes only links that still resolve exactly to Agent Stack sources.

The underlying script accepts an alternate home directory for automated tests. It refuses global installation from a secondary Git worktree, reports `missing`, `correct`, `collision`, and
`stale-agent-stack-link` states, and treats a stale link as an error until reviewed; it is never silently replaced.

## Safety and Recovery

The installer creates parent directories only when absent. It rejects a regular file, directory, or non-Agent-Stack symlink at any target path. It verifies every link after creation. Uninstall removes no canonical content and skips unexpected targets, so recovery is simply re-running the installer after resolving a collision.

## Validation

Automated tests will cover the full expected inventory, dry-run no-write behavior, successful installation, idempotence, preflight atomicity on collision, safe uninstall, and refusal to remove a changed target. `just test` remains the overall verification entry point; a real-home `global-dry-run` provides non-mutating integration validation.
