---
Title: skill-drawio
Category: folder-index
Status: current
Authority: local-supplement
Scope: skill-drawio pack — draw.io practice and the data-first diagram engine for any project
Last reviewed: 2026-10-19
Summary: Entry index for skill-drawio, with what the pack is for, its folders and key files, and where governance lives.
Budget: 200 lines, 25 KB
---

# skill-drawio

Canonical, cross-project pack for draw.io work: diagrams rendered from a YAML map (validated, deterministic, drift-checked), the file format,
orthogonal layout and routing with layout audits, visual style, CLI export with self-review, and reading existing drawings as data.

## Purpose

Everything the operator's projects learned drawing with draw.io, in one place, with the engine that does it. The engine was built for
unified-network-controller's flow map and promoted here on 2026-10-19; that project now renders through it, byte-identical to before.

## Quick start

- Using the skill: invoke `skill-drawio`; it routes from [SKILL.md](SKILL.md).
- Drawing a project's flows: write a map like [examples/shop/flows.yaml](examples/shop/flows.yaml), then
  `<python> <this pack>/scripts/render_flowmap.py --map <map> --write` from the project root (see [scripts/README.md](scripts/README.md)).
- Working on the pack: `just bootstrap` once, then `just test` and `just check` before calling a change complete. Full setup: [SETUP.md](SETUP.md).

## Folder index

- [references/](references/) — one focused file per topic; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [scripts/](scripts/) — front ends, the `drawio` and `flowmap` packages, the governance checker. Index: [scripts/README.md](scripts/README.md)
- [schemas/](schemas/) — the generic flow-map JSON Schema
- [examples/](examples/) — a worked map and its rendered drawing
- [tests/](tests/) — contract and engine tests
- [documents/](documents/) — draw.io and WCAG sources pulled verbatim. Index: [documents/drawio-sources-20261019/readme.md](documents/drawio-sources-20261019/readme.md)

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence labels |
| [compatibility.yaml](compatibility.yaml) | draw.io versions and environments exercised |
| [code-map.toml](code-map.toml) | This pack's code decisions, checked by skill-coder's helpers |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record |
| [ROADMAP.md](ROADMAP.md) | Current phase and open milestones; done items rotate to `docs/history/` |
| [SETUP.md](SETUP.md) | Prerequisites, bootstrap, use from a project, troubleshooting |
| [justfile](justfile) | Task catalog: `just --list`; `just test` and `just check` gate completion |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
