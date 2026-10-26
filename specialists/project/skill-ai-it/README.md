---
Title: skill-ai-it
Category: readme
Status: current
Authority: canonical
Scope: Front door for people using or maintaining the skill-ai-it package
Last reviewed: 2026-10-14
Summary: >-
  What skill-ai-it does (bootstrap, refresh and audit a project's AI governance and navigation files), how to set it up and run it, how the
  package is laid out, and where the detail lives.
Budget: 200 lines, 25 KB
---

# skill-ai-it

## Contents

- [Purpose](#purpose)
- [Quick start](#quick-start)
- [Modes](#modes)
- [What it gives a project](#what-it-gives-a-project)
- [Package layout](#package-layout)
- [Key rules](#key-rules)
- [Tool stack](#tool-stack)
- [Where to read more](#where-to-read-more)

Reusable AI governance and navigation bootstrap skill for project folders.

## Purpose

`skill-ai-it` analyzes a target folder and creates or refreshes its governance, context-routing and AI navigation files, repeat-safely. It suits mixed projects: code, scripts, design notes,
architecture docs, roadmaps, scratchpads, changelogs and planning documents. What each of those files is for is defined once, in [references/governed-file-roles.md](references/governed-file-roles.md).

## Quick start

- **Use it:** ask for it by name (`/skill-ai-it`) with a mode, e.g. "skill-ai-it refresh this project". The agent follows [SKILL.md](SKILL.md).
- **Set up the package's own tooling:** `just bootstrap` builds the venv from the runtimes pinned in `.mise.toml` (in the skills working cache, never in this folder); `just runtimes` shows what the
  recipes will use.
- **Before calling a change done:** `just check` (governance checks, document freshness, file roles); `just stale` and `just roles` list findings.
- **Bring a project up to standard:** `just govern <project>` here, or `just govern` inside the project; then `/skill-ai-it refresh` for content.
- **All tasks:** `just --list`; each script is catalogued in [scripts/README.md](scripts/README.md).

## Modes

| Mode             | Purpose                                                                                                        |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| `bootstrap`      | Create the initial governance scaffold for a new or light project                                              |
| `navigation-add` | Add AI navigation starter files to an existing project                                                         |
| `refresh` | Run `govern`, then fix content by the role findings, without overwriting custom content |
| `govern` | Governance only, scripted: adoption, record budgets with `just check`, role findings (`/skill-ai-it govern`, or `just govern`) |
| `audit`          | Report missing, stale or conflicting governance and context files, and files outside their role                |
| `promote`        | Promote candidates from `ARCHCORE_PROMOTION_CANDIDATES.md`, or explicitly requested content, into `.archcore/` |

## What it gives a project

- **AI navigation map:** `AI_NAVIGATION.md`, the read order, authority and routing for agents.
- **File relationships:** `context-map.yaml` authority order, companion files and update rules.
- **Coherence checks:** a project-local, stdlib-only `scripts/check_governance.py` run by `just check`, plus the drift-audit checklist.
- **Governed records:** loading tiers, budgets, rotation and freshness, so agents read little by default and fetch detail on need (`just rotate`,
  `just budget`, `just stale`); file roles checked by `just roles`.
- **Machine-readable context:** `context-map.yaml` as a structured file registry.

How these fit together, the managed-block format, upgrade behaviour and compaction recovery: [ARCHITECTURE.md](ARCHITECTURE.md).

## Package layout

```text
skill-ai-it/
├── SKILL.md             orchestration contract (loaded on invocation)
├── README.md            this file
├── AGENTS.md            rules for agents maintaining the package (CLAUDE.md wraps it)
├── AI_NAVIGATION.md     agent router; context-map.yaml is its machine-readable twin
├── ARCHITECTURE.md      how the skill works and why
├── ROADMAP.md           current phase and open milestones
├── CHANGELOG.md         dated change history (older entries in docs/history/)
├── SCRATCHPAD.md        working state between sessions
├── justfile             task catalog; .mise.toml pins runtimes; requirements.txt
├── references/          on-need detail moved out of SKILL.md, one topic per file
├── templates/           files generated into target projects (incl. govcheck/)
├── patterns/            optional guidance modules
├── scripts/             tooling, catalogued in scripts/README.md
├── tests/               tests for the scripts
├── docs/                plans, reviews, history/, trackers/, archive/
└── governance/          watchman event log for historical context recovery
```

Full layout with each template: [references/package-layout.md](references/package-layout.md).

## Key rules

- `SKILL.md` owns orchestration; `templates/` owns generated-file content; `patterns/` owns optional guidance; `CHANGELOG.md` owns history.
- Repeat runs are safe: managed blocks are updated in place, user content outside them is preserved, risky YAML/JSON changes go to `.proposed` files.
- Target projects do not depend on this package at runtime; repo-local preflight scripts are explicit opt-in only.
- Agents run catalogued tasks (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety until inspected.
- `.archcore/` is durable structured truth when present, and only `promote` writes its content. `.ai-context/` and `graphify-out/` are generated support, never truth.

## Tool stack

| Tool     | Role                                                                                    | Status here                                                                                     |
| -------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Archcore | Durable decisions, rules, specs, guides and plans under `.archcore/`                    | Initialized when the CLI exists; content only via `promote`                                     |
| Repomix  | Deterministic AI context pack in `.ai-context/` from `repomix.config.json`              | Run on bootstrap, navigation-add and refresh when the CLI exists                                |
| Graphify | Relationship graph in `graphify-out/`                                                   | Disabled 2026-10-10 (0 graph queries in 30 days); kept for re-enabling                          |
|          |                                                                                         |   with `GRAPHIFY_ENABLED=1`                                                                     |
| just     | Task catalog; existing runners (Taskfile, Makefile, package.json) stay canonical        | Preferred for new projects                                                                      |
|          |   where present                                                                         |                                                                                                 |

Authority runs one way: `.archcore/` + governed markdown + source → task runner + `scripts/README.md` → `AI_NAVIGATION.md` + `context-map.yaml` → generated outputs → agent context. Generated output
never flows back without review and promotion.

## Where to read more

| Question                          | File                              |
| --------------------------------- | --------------------------------- |
| What each governed file is for    | [references/governed-file-roles.md](references/governed-file-roles.md) |
| How the skill works               | [ARCHITECTURE.md](ARCHITECTURE.md) |
| What the agent does, step by step | [SKILL.md](SKILL.md) and [references/](references/readme.md) |
| What changed recently             | [CHANGELOG.md](CHANGELOG.md)      |
| What is planned                   | [ROADMAP.md](ROADMAP.md)          |
