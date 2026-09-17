# skill-cambium

Canonical specialist pack for Cambium wireless device fleet operations.

## Purpose

Provides structured operational knowledge for APN's Cambium hardware fleet — device families and firmware, local-admin credential vault structure, the cnMaestro estate, site asset-register
conventions, and the `device-inventory.csv` schema. Complements `skill-smc`, which owns the SMC box / ansible-wifi provisioning layer around this hardware.

## Folder index

- [references/](references/) — 6 numbered reference files, progressive disclosure (content source)
- [.archcore/](.archcore/) — durable rules, ADR, and spec for this pack (initialized 2026-09-17; 6 documents accepted the same day, see [.archcore/README.md](.archcore/README.md))

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack version history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Key files

| File          | Role                                                                                  |
| ------------- | ------------------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md) | Agent activation surface — triggers, Standing Write-Back Contract, reference pointers |
| [RUNBOOK.md](RUNBOOK.md) | Navigation index — maps task types to numbered reference files                        |
| [manifest.json](manifest.json) | Machine-readable metadata: version, scope, stable facts, constraints                  |

## Related pack

[skill-smc](../skill-smc/README.md) — the SMC box / ansible-wifi layer this fleet is managed through. See each pack's `SKILL.md` Related Skills section for the boundary.
