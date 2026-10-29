---
Title: Network Architect skill
Category: package-guide
Status: current
Authority: authored-guidance
Scope: skill-network-architect pack in skills_stuff
Last reviewed: 2026-10-29
Summary: What the pack holds, how to install it, how to run its checks and how it is maintained.
---

# Network Architect skill

Start with [SKILL.md](SKILL.md); task routing is in [RUNBOOK.md](RUNBOOK.md). A vendor-neutral domain architecture skill, independent of AI provider and equipment vendor. Canonical source is this folder in
`skills_stuff/specialists/project/`; installs are symlinks back to it. Its peer is `skill-systems-architect` (same layout).

## Layout

```text
skill-network-architect/
  SKILL.md              discovery, write-back contract, routing summary
  RUNBOOK.md            reference routing table and recipes
  AGENTS.md             maintenance and operating boundaries
  CLAUDE.md             thin adapter to AGENTS.md and SKILL.md
  CHANGELOG.md          dated change log (version lives in SKILL.md metadata)
  SCRATCHPAD.md         current state and next actions
  sources.json          evidence ledger: curated labels plus every cited URL (`just ledger`)
  sources/              local copies of cited sources, index.json (shared store, `just fetch-sources`)
  docs/research/        research reports (similar-skills survey)
  agents/openai.yaml    optional Codex UI metadata
  references/           domain modules; six shared modules are canonical here
  templates/            design, ADR, interface, handoff and change forms
  examples/             offline helper inputs
  scripts/              read-only stdlib helpers (catalogue: scripts/README.md)
  tests/                CLI and negative tests
  evals/                behavioural cases, trigger cases, rubric and observed results
  justfile .mise.toml   task runner and pinned runtime
  requirements.txt      lint-only dependency (ruff)
```

## Shared references

The six cross-domain modules (architecture method, automation and safety, collaboration protocol, diagrams and deliverables, FOSS tool selection, research and attribution) and
`scripts/check_package.py` live here. `skill-systems-architect` symlinks to them, so edit them here only and run `just check` in both packs.

## Install

Symlink the folder, never copy it (copies drift across hosts):

- Claude Code user scope: `~/.claude/skills/skill-network-architect -> <this folder>`.
- Codex user scope: `~/.agents/skills/skill-network-architect -> <this folder>`.
- Explicit invocation: `/skill-network-architect` (Claude Code), `Use $skill-network-architect ...` (Codex).

Install `skill-systems-architect` beside it: its shared references resolve through `../skill-network-architect/`. Sources for the discovery paths: [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills).

## Checks

```sh
just bootstrap   # once: venv in skills-working-cache/skill-network-architect
just check       # tests, expected findings, ruff, package structure
```

The helpers are standard library only and touch no network, device or controller. Tests prove local arithmetic and input handling, not infrastructure suitability. Behavioural validation:
[evals/README.md](evals/README.md).

## Generic agents and local LLMs

Provide SKILL.md explicitly and let the model read the referenced files relative to this folder. If the runtime cannot read files, supply only the selected references and templates. No local LLM
runtime was tested.
