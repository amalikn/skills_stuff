---
title: Specialist Pack File Roles
type: spec
status: accepted
provenance: promoted from AI_NAVIGATION.md + exports/claude_code/project/skill-smc/adapter.md on 20260626
---

# Spec: Specialist Pack File Roles

Defines the role and install treatment of every file in the skill-smc specialist pack.

## File role table

| File | Role | Installed to clients? | Notes |
|---|---|---|---|
| `SKILL.md` | Agent-facing activation surface | Yes — `~/.claude/skills/skill-smc/SKILL.md` | Primary skill file loaded by Claude Code |
| `RUNBOOK.md` | Navigation index only | Yes — `~/.claude/skills/skill-smc/RUNBOOK.md` | 48-line routing table; not a content source |
| `references/01_` – `13_` | Numbered content source files | Yes — `~/.claude/skills/skill-smc/references/` | Load on demand per task |
| `manifest.json` | Machine-readable specialist metadata | No | Consumed by skill tooling; not needed at runtime |
| `PROFILE.md` | Background context; canonical source | No | Content summarised in SKILL.md and references/01_overview.md |
| `SYSTEM_PROMPT.md` | Dedicated agent mode prompt | No (default) | Use only when deploying skill-smc as a dedicated agent |
| `exports/claude_code/` | Client adapter and install docs | No | Governance only; describes what gets installed and how |
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

The Claude Code install surface is exactly:
```
~/.claude/skills/skill-smc/
├── SKILL.md
├── RUNBOOK.md
└── references/
    ├── 01_overview.md
    ├── ...
    └── 13_known-issues.md
```

All other pack files stay in the canonical source (`skills_stuff/specialists/project/skill-smc/`) and are not copied to the install surface.
