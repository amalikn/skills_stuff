---
Title: skill-ai-it reference: Phases 1 to 3: inventory, understand, infer
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Phases 1 to 3: inventory, understand, infer; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Phases 1 to 3: inventory, understand, infer

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Phase 1 — Inventory

1. List the target folder's contents 3 levels deep (files and subdirectories), excluding heavy/generated folders such as `.git`, `node_modules`, `.venv`, `dist`, `build`, `__pycache__`, `.ai-context`,
   and `graphify-out` unless the user asks to inspect them.

2. Classify what you find:

   | Signal | Inference |
   | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
   | `.py`, `.ts`, `.js`, `.go`, `.rb`, `.rs`, `.java` files | Code project |
   | `docker-compose.yml`, `Dockerfile`, `Makefile`, `*.tf` | Infrastructure / ops |
   | `*.eml`, `communications/` folder | Communications tracking |
   | `*.md` files only, no code | Docs / knowledge base |
   | Mix of the above | Mixed project |
   | `AI_NAVIGATION.md`, `context-map.yaml` | AI navigation module already present |
   | `.archcore/` | Structured durable project truth present |
   | `archcore` CLI available and `.archcore/` missing | Initialize `.archcore/` with `archcore init` in bootstrap/navigation-add/refresh mode |
   | `justfile`, `Justfile` | just task catalog present — preferred lightweight runnable task catalog |
   | `scripts/`, `Makefile`, `Taskfile.yml`, `justfile`, `package.json` scripts, or common automation files | Script/task inventory useful; create or refresh `scripts/README.md` |
   | `memory-bank/` | Memory Bank-style project memory present |
   | `graphify-out/`, `.ai-context/` | Generated AI context/navigation artifacts present |
   | `repomix.config.json` | Deterministic context-pack config present |
   | `.markdownlint-cli2.jsonc`, `.markdownlint.json(c)`, `.markdownlint.yaml`, or a `markdownlint-cli2` key | Markdown lint config already owned by the project — do not create/overwrite |
   |   in `package.json` |  |
   | `README.md` exists | Read it first before generating |
   | `CHANGELOG.md` exists | Read recent entries to understand project evolution and governance changes |
   | `AGENTS.md` exists | Update, do not overwrite |

3. Check the **parent folder** for:
   - `AGENTS.md` — read it to inherit conventions, routing patterns, internal domain
   - `README.md` — note its Folder index section for later update
   - `AI_NAVIGATION.md` — read it to inherit context routing patterns
   - `context-map.yaml` — read it to inherit machine-readable routing conventions
   - `CHANGELOG.md` — read recent entries to inherit project/package evolution context

## Phase 2 — Understand

Read the **3–5 most informative files** in the target folder. Priority order:

1. Existing `AI_NAVIGATION.md` and `context-map.yaml` (if present — navigation authority)
2. Existing `README.md` (if present)
3. Existing `CHANGELOG.md` (if present — recent project/governance evolution)
4. Existing `AGENTS.md` or `CLAUDE.md` (if present — update mode, not create)
5. Existing `.archcore/` index/status/context files, if present
6. Existing `memory-bank/activeContext.md`, `memory-bank/progress.md`, and `memory-bank/decisionLog.md`, if present
7. Primary code entry point (`main.*`, `index.*`, `app.*`, `__init__.py`)
8. Key config (`package.json`, `pyproject.toml`, `go.mod`, `*.yaml` service config)
9. Most recently modified `.md` file (captures active work context)

Read parent AGENTS.md to extract:

- `@` import chain (for AGENTS.md inheritance)
- Internal domain (e.g. `apn.net.au`)
- Naming conventions, routing rules

Read parent `AI_NAVIGATION.md` / `context-map.yaml` if present to extract:

- Authority order
- Existing routing categories
- Archcore, memory-bank, Graphify, and Repomix conventions
- Generated context locations
- Drift/conflict handling rules

Read parent `CHANGELOG.md` if present to extract:

- Recent governance or routing changes
- Recent template/pattern changes
- Migration notes that affect repeat-run safety
- Deprecated or superseded behaviours

**If content is insufficient to infer purpose**, ask:
> "What is the purpose of this folder? One sentence is enough."

## Phase 3 — Infer

From inventory + content reads, determine:

| Field                 | How to infer                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Project name          | Folder name, formatted (e.g. `aurukun-fni` → "Aurukun FNI")                                                                                                                  |
| Purpose               | From README, code comments, config descriptions, or folder name semantics                                                                                                    |
| Technology stack      | From file extensions, package manifests, imports                                                                                                                             |
| Participants          | From git log (`git log --format="%an" \| sort -u`), email headers in EML files, or existing docs                                                                             |
| Internal domain       | From parent AGENTS.md; default `apn.net.au` for APN projects                                                                                                                 |
| Subfolder roles       | From subfolder names and their contents                                                                                                                                      |
| Project type          | Code / docs / ops / comms / mixed (drives conditional file creation)                                                                                                         |
| Governance            | Presence/quality of README, AGENTS, CLAUDE, SCRATCHPAD, CHANGELOG, AI_NAVIGATION, context-map, roadmap, architecture docs                                                    |
|   completeness        |                                                                                                                                                                              |
| Navigation maturity   | Whether task-to-file routing, source priority, drift policy, and generated-context rules exist                                                                               |
| Structured            | Presence of `.archcore/`, ADRs, rules, specs, guides, plans, memory-bank, Graphify, Repomix                                                                                  |
|   truth backend       |                                                                                                                                                                              |
| Script/task inventory | Presence of `justfile`, `scripts/README.md`, other task runners (Taskfile.yml, Makefile, package.json), raw scripts, safety labels, inputs/outputs, and stale/missing        |
|                       |   catalog entries                                                                                                                                                            |
| Coherence invariants  | Claims the governance surfaces make that the filesystem can contradict: counts, index links, path references, catalogs, generated artifacts and their sources, and any       |
|                       |   threshold or canonical value restated in more than one file. Each becomes a check — see `patterns/governance-checks.md` for the artifact-to-check inference table          |
| Repeat-run risk       | Existing custom sections, `KEEP` blocks, managed blocks, user-authored YAML/JSON, and generated artifacts                                                                    |
| Runtime requirements  | Interpreters the scripts/recipes actually invoke (`python3`, `node`, `npx`), and whether each is pinned in `.mise.toml`. Derive the working-cache peer path from the source  |
|                       |   root — see *Runtime isolation*                                                                                                                                             |
| Active development?   | Presence of TODOs, WIP markers, incomplete docs, recent git commits                                                                                                          |
