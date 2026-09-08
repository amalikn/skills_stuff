# Architecture — skill-smc

## Overview

skill-smc is a multi-file specialist pack following the canonical `specialists/project/` pattern. It separates an agent-facing activation surface (SKILL.md) from a progressive-disclosure reference layer (references/01–13) via a navigation index (RUNBOOK.md). Client adapter docs in `exports/` describe what gets installed and where. Durable pack rules, the structural ADR, and a file-roles spec live in `.archcore/`.

## Components

| Component | Role |
|---|---|
| `SKILL.md` | Agent activation surface: trigger conditions, inline quick-reference tables, and pointers to numbered references |
| `RUNBOOK.md` | Navigation index: 48-line table mapping task types to specific reference files. Not a content source. |
| `references/01_overview.md` – `references/13_known-issues.md` | Numbered progressive-disclosure content files. Each covers one domain. Loaded on demand. |
| `manifest.json` | Machine-readable specialist metadata: version, scope boundary, stable facts, known constraints |
| `PROFILE.md` | Background context (hardware, flavors, access pattern). Content summarised in SKILL.md and 01_overview.md. Not installed to clients. |
| `SYSTEM_PROMPT.md` | Dedicated agent mode prompt. Not loaded in normal skill invocations. |
| `exports/claude_code/` | Claude Code adapter: source→install mapping (`adapter.md`) and install steps (`install.md`) |
| `.archcore/` | Durable pack truth: 3 rules, 1 ADR, 1 spec |
| `AGENTS.md` | Pack maintenance policy for contributors |
| `AI_NAVIGATION.md` | Human-readable context router for agents working on the pack |
| `context-map.yaml` | Machine-readable routing map |
| `.ai-context/governance-pack.md` | Generated repomix bundle (~470k chars as of 2026-08-03, 35 files) — regenerable |

## Information flow

```
Agent invoked with SMC task
  └── reads SKILL.md (activation surface, inline quick-ref)
        └── reads RUNBOOK.md (navigation index, identifies relevant reference)
              └── reads references/<nn>_*.md (focused content for the task)
```

## Installed surface (Claude Code)

```
~/.claude/skills/skill-smc/
├── SKILL.md
├── RUNBOOK.md
└── references/
    ├── 01_overview.md
    ├── 02_service-map.md
    ├── ...
    └── 13_known-issues.md
```

Everything else (PROFILE.md, SYSTEM_PROMPT.md, manifest.json, exports/, .archcore/, governance files) stays in the canonical source at `skills_stuff/specialists/project/skill-smc/` and is not installed to clients.

## Key decisions

- **Progressive disclosure (ADR v0.1.2):** monolithic RUNBOOK.md split into 13 numbered references to reduce per-task token cost. See [.archcore/adr/adr-progressive-disclosure-structure.md](.archcore/adr/adr-progressive-disclosure-structure.md).
- **RUNBOOK.md as index only:** never holds content; is always a routing table. See [.archcore/rules/rule-progressive-disclosure-loading.md](.archcore/rules/rule-progressive-disclosure-loading.md).
- **PROFILE.md not installed:** content is summarised in SKILL.md and 01_overview.md to avoid a dangling reference in the client install surface.
- **manifest.json not installed:** consumed by skill tooling at build/validate time, not needed at agent runtime.

## Related workspaces

| Repo | Relationship |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible source governed by this skill |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting consuming SMC PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans and investigation notes |
