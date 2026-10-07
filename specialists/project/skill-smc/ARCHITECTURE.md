# Architecture — skill-smc

## Overview

skill-smc is a multi-file specialist pack following the canonical `specialists/project/` pattern. It separates an agent-facing activation surface (SKILL.md) from a progressive-disclosure reference
layer (references/01–13) via a navigation index (RUNBOOK.md). Durable pack rules, the structural ADR, and a file-roles spec live in `.archcore/`.

## Components

| Component | Role |
|---|---|
| `SKILL.md` | Agent activation surface: triggers, the write-back contract, a short access paragraph and decision tree, and pointers to numbered references |
| `RUNBOOK.md` | Navigation index: 48-line table mapping task types to specific reference files. Not a content source. |
| `references/01_overview.md` – `references/13_known-issues.md` | Numbered progressive-disclosure content files. Each covers one domain. Loaded on demand. |
| `manifest.json` | Machine-readable specialist metadata: version, scope boundary, stable facts, known constraints |
| `justfile` + `.mise.toml` | Task catalog; recipes run Python from the working-cache venv pinned by `.mise.toml` (`just bootstrap`, `just check`) |
| `.archcore/` | Durable pack truth: 3 rules, 1 ADR, 1 spec |
| `AGENTS.md` | Pack maintenance policy for contributors |
| `AI_NAVIGATION.md` | Human-readable context router for agents working on the pack |
| `context-map.yaml` | Machine-readable routing map |
| `.ai-context/governance-pack.md` | Generated repomix bundle (~470k chars as of 2026-08-03, 35 files) — regenerable |

## Information flow

```text
Agent invoked with SMC task
  └── reads SKILL.md (activation surface, decision tree)
        └── reads RUNBOOK.md (navigation index, identifies relevant reference)
              └── reads references/<nn>_*.md (focused content for the task)
```

## Installed surface (Claude Code)

`~/.claude/skills/skill-smc` is a symlink to this canonical folder, so the whole pack is visible to Claude Code; `SKILL.md` is what activates, everything else loads on demand. There is no copy step
and no separate adapter document; those, the profile file and the dedicated-agent system prompt were retired on 2026-10-07.

## Key decisions

- **Progressive disclosure (ADR v0.1.2):** monolithic RUNBOOK.md split into 13 numbered references to reduce per-task token cost. See
  [.archcore/adr/progressive-disclosure-structure.adr.md](.archcore/adr/progressive-disclosure-structure.adr.md).
- **RUNBOOK.md as index only:** never holds content; is always a routing table. See [.archcore/rules/progressive-disclosure-loading.rule.md](.archcore/rules/progressive-disclosure-loading.rule.md).
- **SKILL.md stays short (2026-10-07):** detail lives in the reference that owns it; SKILL.md keeps only what decides which reference to open.

## Related workspaces

| Repo | Relationship |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible source governed by this skill |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting consuming SMC PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans and investigation notes |
