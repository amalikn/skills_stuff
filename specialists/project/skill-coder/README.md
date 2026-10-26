---
Title: skill-coder
Category: folder-index
Status: current
Authority: local-supplement
Scope: skill-coder pack — language-agnostic programming practice with per-language overrides and stdlib checkers
Last reviewed: 2026-10-19
Summary: Entry index for skill-coder, with what the pack is for, its folders and key files, and where governance lives.
Budget: 200 lines
---

# skill-coder

Canonical, cross-project pack for writing, changing, reviewing and refactoring code in any language. The rules are language-agnostic; files under
`languages/` tighten, loosen (with a reason) or map them to each language's tools; a project's own rules outrank both.

## Purpose

Reusable, evidence-graded programming practice for any project, current or future, distilled from the operator's governed projects (rules first
proven in unified-network-controller) and primary sources. The pack also ships stdlib checkers that hold a project to the rules: they run with the
project's own interpreter and read its `code-map.toml`.

## Quick start

- Using the skill in a project: invoke `skill-coder`; it reads the project's own rules first, then routes from [SKILL.md](SKILL.md).
- Running a checker against a project: `<project python> <this pack>/scripts/code_size.py --project-root . --list` (any helper; see
  [scripts/README.md](scripts/README.md)); copy [templates/code-map.toml](templates/code-map.toml) to the project root to set its decisions.
- Working on the pack: `just bootstrap` once, then `just test` and `just check` before calling a change complete. Full setup: [SETUP.md](SETUP.md).

## Folder index

- [references/](references/) — one focused file per topic; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [languages/](languages/) — per-language overrides. Index: [languages/readme.md](languages/readme.md)
- [scripts/](scripts/) — the checkers and the pack's governance checker. Index: [scripts/README.md](scripts/README.md)
- [templates/](templates/) — `code-map.toml` for a project to copy
- [tests/](tests/) — contract and helper tests, scenarios
- [documents/](documents/) — research sources pulled verbatim, with their index

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence labels |
| [code-map.toml](code-map.toml) | This pack's own code decisions (it is held to its own rules) |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record |
| [ROADMAP.md](ROADMAP.md) | Current phase and open milestones; done items rotate to `docs/history/` |
| [SETUP.md](SETUP.md) | Prerequisites, bootstrap, use from a project, troubleshooting |
| [justfile](justfile) | Task catalog: `just --list`; `just test` and `just check` gate completion |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
