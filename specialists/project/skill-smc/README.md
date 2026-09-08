# skill-smc

Canonical specialist pack for SMC (Site Management Controller) box operations and ansible-wifi authoring.

## Purpose

Provides structured operational knowledge for SMC appliances (x86 PC and ARM64 Raspberry Pi), the ansible-wifi repo, and related SMC workflows. Covers live incident triage, Ansible authoring, URL-capture PCAP processing, captive portal, content filtering, and hardware/overlayroot behavior.

## Folder index

- [references/](references/) — 13 numbered progressive-disclosure reference files (content source)
- [exports/](exports/) — client adapter and install documentation
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
| [SKILL.md](SKILL.md) | Agent activation surface — triggers, quick-reference, reference pointers |
| [RUNBOOK.md](RUNBOOK.md) | Navigation index — maps task types to numbered reference files |
| [PROFILE.md](PROFILE.md) | SMC box background context (not installed to clients) |
| [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) | Dedicated agent mode prompt |
| [manifest.json](manifest.json) | Machine-readable metadata: version, scope, stable facts, constraints |

## Install

See [exports/claude_code/project/skill-smc/install.md](exports/claude_code/project/skill-smc/install.md).
