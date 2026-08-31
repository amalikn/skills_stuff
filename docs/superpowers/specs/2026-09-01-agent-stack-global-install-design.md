# Agent Stack Global Install Design

## Goal

Make the reusable Agent Stack available from every Claude Code and Codex session without copying it into each project. Keep project-level instructions and governance local to their projects.

## Decision

Agent Stack remains the single canonical source at `specialists/agent-stack/`. A new installer will create individual symlinks from the global client directories to canonical persona and skill entries.

It will not replace, copy, rename, or overwrite existing global entries. The install is atomic at the selected client scope: a collision stops the operation before any new link is created.

## Client Mapping

| Client | Global destination | Entries |
| --- | --- | --- |
| Claude Code | `~/.claude/agents` | 14 persona Markdown files |
| Claude Code | `~/.claude/skills` | 36 skill entries |
| Codex | `~/.codex/skills` | 36 skill entries |

The `frontend-design.md` single-file source requires a small client adapter directory containing `SKILL.md`; all package skills are installed as direct symlinks. Personas are intentionally not installed into Codex because Codex has no corresponding persona discovery directory in this stack.

## Commands

`just global-status` reports the expected links and their current state without changes. `just global-dry-run` previews a complete install. `just global-install install` creates links only after preflight succeeds. `just global-uninstall uninstall` removes only links that still resolve exactly to Agent Stack sources.

The underlying script accepts an alternate home directory for automated tests. It reports `missing`, `correct`, `collision`, and `stale-agent-stack-link` states. A stale link is treated as an error until reviewed; it is never silently replaced.

## Safety and Recovery

The installer creates parent directories only when absent. It rejects a regular file, directory, or non-Agent-Stack symlink at any target path. It verifies every link after creation. Uninstall removes no canonical content and skips unexpected targets, so recovery is simply re-running the installer after resolving a collision.

## Validation

Automated tests will cover the full expected inventory, dry-run no-write behavior, successful installation, idempotence, preflight atomicity on collision, safe uninstall, and refusal to remove a changed target. `just test` remains the overall verification entry point; a real-home `global-dry-run` provides non-mutating integration validation.
