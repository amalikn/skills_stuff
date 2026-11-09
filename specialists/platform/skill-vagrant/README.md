---
Title: skill-vagrant
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-vagrant
Last reviewed: 2026-11-07
Summary: "Canonical, cross-project platform pack for local lab VMs with Vagrant and the Parallels provider on macOS Apple silicon: boxes and pins, Vagrantfiles, networks, linked clones and..."
Review by: 2026-12-09
Budget: 200 lines, 25 KB
---

# skill-vagrant

Canonical, cross-project platform pack for local lab VMs with Vagrant and the Parallels provider on macOS Apple silicon: boxes and pins, Vagrantfiles, networks, linked clones and machine-id, prlctl,
lab guards, tool choice and licensing.

## Purpose

Reusable, evidence-graded Vagrant and Parallels knowledge for any project that runs a local lab. Each engagement writes verified reusable findings back here; VM names, lab addresses and stages stay in
the engaging project. The counterpart pack for the x86 lab is [skill-proxmox](../skill-proxmox/SKILL.md); the structure mirrors [skill-nautobot](../skill-nautobot/README.md).

## Folder index

- [references/](references/) — focused content files, one per domain; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [documents/](documents/) — verbatim research captures with provenance and sha256. Index: [documents/readme.md](documents/readme.md)
- [scripts/](scripts/) — tested stdlib-only read-only helpers and the governance checker. Index: [scripts/README.md](scripts/README.md)
- [tests/](tests/) — offline package contract, helper tests, scenarios, evaluation procedure
- [.archcore/](.archcore/) — durable decisions, rules and plans (accepted 2026-11-09). Index: [.archcore/index.guide.md](.archcore/index.guide.md)
- [docs/](docs/) — session records (`session-record-<stamp>.md`) and the flow map
- [docs/vagrant-flows/](docs/vagrant-flows/) — flow map: source in `parts/`, assembled `docs/vagrant-flows/vagrant_flows.yaml` and rendered `docs/vagrant-flows/vagrant_flows.drawio` are generated (`just flows`)

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
