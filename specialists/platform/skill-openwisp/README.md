# skill-openwisp

Canonical, cross-project platform pack for OpenWISP: device registration and identity, passive NetJSON monitoring, metrics, workers, health, alerts and presentation.

## Purpose

Reusable, evidence-graded OpenWISP knowledge for any project that runs it. Each engagement writes verified reusable findings back here; project, customer and equipment
specifics stay in the engaging project. The counterpart pack is [skill-nautobot](../skill-nautobot/README.md).

## Folder index

- [references/](references/) — focused content files, one per domain; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [documents/](documents/) — version-matched official doc snapshots. Index: [documents/readme.md](documents/readme.md)
- [scripts/](scripts/) — tested stdlib-only helpers and the governance checker. Index: [scripts/README.md](scripts/README.md)
- [tests/](tests/) — offline package contract, helper tests, scenarios, evaluation procedure
- [.archcore/](.archcore/) — durable decisions, rules and plans (6 documents, accepted 2026-10-05). Index: [.archcore/index.guide.md](.archcore/index.guide.md)

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Activation surface — role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence rungs |
| [compatibility.yaml](compatibility.yaml) | Environment ledger |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record |
| [justfile](justfile) | Task catalog — `just --list`; `just test` is the completion gate |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
