---
title: Specialist Pack File Roles
type: spec
status: accepted
provenance: promoted from AI_NAVIGATION.md + exports/claude_code/project/skill-smc/adapter.md on 20260626
---

# Spec: Specialist Pack File Roles

Defines the role and install treatment of every file in the skill-smc specialist pack.

> **Amended 2026-10-07.** The profile file, the dedicated-agent system prompt and the `exports/claude_code/` adapter were retired: their facts moved into
> `references/`, and the install became a symlink, so there is nothing left for an adapter to describe. The pack gained a root `justfile`, `.mise.toml`,
> `.markdownlint-cli2.jsonc` and `.gitignore`. Everything else below still stands.

## File role table

| File | Role | Installed to clients? | Notes |
|---|---|---|---|
| `SKILL.md` | Agent-facing activation surface | Yes | Primary skill file loaded by Claude Code; kept short, detail lives in references |
| `RUNBOOK.md` | Navigation index only | Yes | 48-line routing table; not a content source |
| `references/01_` – `16_` + registries | Numbered content source files, YAML/CSV registries | Yes | Load on demand per task |
| `manifest.json` | Machine-readable specialist metadata | No | Consumed by skill tooling; not needed at runtime |
| `scripts/` | Read-only diagnostics, governance checker, scoped justfiles | Yes | Catalogued with safety labels in `scripts/README.md` |
| `justfile` | Task catalog | No (pack tooling) | Python recipes use the venv pinned by `.mise.toml` |
| `.mise.toml` | Runtime pin (Python) | No (pack tooling) | Copied into the working-cache peer by `just bootstrap` |
| `.markdownlint-cli2.jsonc` | Markdown lint config | No (pack tooling) | 200-column prose, tables and code exempt |
| `AGENTS.md` | Agent policy for pack maintenance | No | Governs contributors, not end-users |
| `CLAUDE.md` | Claude Code governance wrapper | No | Pack maintenance only |
| `AI_NAVIGATION.md` | Human-readable context router | No | Pack maintenance only |
| `context-map.yaml` | Machine-readable routing map | No | Pack maintenance only |
| `CHANGELOG.md` | Pack version history | No | Pack maintenance only |
| `README.md` | Pack orientation and folder index | No | Human entry point; canonical source only |
| `ARCHITECTURE.md` | Pack structure, component table, information flow | No | Canonical source only |
| `SCRATCHPAD.md` | Agent working memory for pack maintenance sessions | No | Pack maintenance only |
| `repomix.config.json` | Context bundle configuration for repomix | No | Pack maintenance only |
| `.archcore/` | Durable rules, ADR, spec for this pack | No | Canonical source only; not installed |

## Authority

`manifest.json` is the highest-authority metadata source. `SKILL.md` is the highest-authority agent-facing surface. References are content truth for their domain. No other file overrides these.

## Install surface

`~/.claude/skills/skill-smc` is a symlink to the canonical folder (`skills_stuff/specialists/project/skill-smc/`), so every file is present; "installed: yes" above means an
agent at runtime is expected to read it, "no" means it serves pack maintenance only. There is no copy step to keep in sync.
