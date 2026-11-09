---
Title: skill-proxmox
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-proxmox
Last reviewed: 2026-11-07
Summary: "Canonical, cross-project platform pack for Proxmox VE 9.x: nodes and clusters, storage, networking and SDN, VMs and containers, access control and API tokens, the API and CLIs, backups,..."
Review by: 2026-12-09
Budget: 200 lines, 25 KB
---

# skill-proxmox

Canonical, cross-project platform pack for Proxmox VE 9.x: nodes and clusters, storage, networking and SDN, VMs and containers, access control and API tokens, the API and CLIs, backups, HA, upgrades,
security, metrics, and OpenTofu with the bpg/proxmox provider.

## Purpose

Reusable, evidence-graded Proxmox VE knowledge for any project that runs it. Each engagement writes verified reusable findings back here; node names, addresses, VMIDs and lab inventories stay in the
engaging project. Its structure mirrors [skill-nautobot](../skill-nautobot/README.md).

## Folder index

- [references/](references/) — focused content files, one per domain; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [documents/](documents/) — verbatim source captures. Index: [documents/readme.md](documents/readme.md); per-date folder index: [documents/research-sources-20261107/readme.md](documents/research-sources-20261107/readme.md)
- [scripts/](scripts/) — tested stdlib-only helpers and the governance checker. Index: [scripts/README.md](scripts/README.md)
- [tests/](tests/) — offline package contract, helper tests, scenarios, evaluation procedure
- [.archcore/](.archcore/) — durable decisions, rules and plans (6 documents, proposed 2026-11-07). Index: [.archcore/index.guide.md](.archcore/index.guide.md)

## Key files

| File               | Role                                                                |
| ------------------ | ------------------------------------------------------------------- |
| [SKILL.md](SKILL.md) | Activation surface — role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence rungs                                    |
| [compatibility.yaml](compatibility.yaml) | Environment ledger                                                  |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record                                  |
| [justfile](justfile) | Task catalog — `just --list`; `just test` is the completion gate    |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
