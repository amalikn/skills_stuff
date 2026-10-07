# skill-smc

Canonical specialist pack for SMC (Site Management Controller) box operations and ansible-wifi authoring.

## Purpose

Provides structured operational knowledge for SMC appliances (x86 PC and ARM64 Raspberry Pi), the ansible-wifi repo, and related SMC workflows. Covers live incident triage, Ansible authoring,
URL-capture PCAP processing, captive portal, content filtering, and hardware/overlayroot behavior.

## Folder index

- [references/](references/) — numbered progressive-disclosure reference files (`01_` to `16_`) plus machine-readable registries (content source)
- [scripts/](scripts/) — read-only diagnostics and the governance checker; catalog in [scripts/README.md](scripts/README.md)
- [.archcore/](.archcore/) — durable rules, ADR, and spec for this pack

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Pack version history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Agent activation surface — triggers, access, decision tree, reference pointers |
| [RUNBOOK.md](RUNBOOK.md) | Navigation index — maps task types to numbered reference files |
| [justfile](justfile) | Task catalog: `just bootstrap`, `just runtimes`, `just check`, `just fleet`, `just routing` |
| [manifest.json](manifest.json) | Machine-readable metadata: version, scope, stable facts, constraints |

## Install

`~/.claude/skills/skill-smc` is a symlink to this canonical folder, so the whole pack is visible to Claude Code; `SKILL.md` is what activates, everything else loads on demand. To install on a new
machine: `ln -s <this folder> ~/.claude/skills/skill-smc`, then `just bootstrap`.
