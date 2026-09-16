# AI Navigation — Invoice Finance Analyst

Purpose: project context entrypoint for AI agents. Tells agents where project truth lives, what to read first, what is authoritative, and what must be updated after work.

This file is a router, not a knowledge store.

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md` (this file)
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `.archcore/` documents, if present
6. Relevant project docs/code based on the task

If available, also consult:
- `graphify-out/GRAPH_REPORT.md`
- `.ai-context/governance-pack.md`

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, guides, and plans
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `ARCHITECTURE.md`
7. `ROADMAP.md`
8. `SCRATCHPAD.md` (KEEP-marked content only)
9. `docs/` supporting documents
10. Old notes, drafts, archived feedback docs

`SCRATCHPAD.md` content is temporary unless marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory systems.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Hard constraints, venv routing, naming rules | High |
| `CLAUDE.md` | Claude Code bootstrap wrapper | High |
| `AI_NAVIGATION.md` | Human-readable AI routing entrypoint | High |
| `context-map.yaml` | Machine-readable task-to-context routing map | High |
| `.archcore/adr/` | Architecture decisions (promote from ROADMAP/SCRATCHPAD) | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHITECTURE.md` | 8-layer pipeline, severity model, component map | Medium-high |
| `ROADMAP.md` | Phase 0–5 plan, gap review decisions, acceptance log | Medium-high |
| `SETUP.md` | venv, dependencies, invocation patterns, CLI flags | Medium-high |
| `CHANGELOG.md` | Project/governance history ledger | Medium-high |
| `internal-invoice-analysis/SKILL.md` | Canonical skill behavior spec (source of truth for the built skill) | High |
| `docs/data_contract.md` | Canonical input schema for 4 source types | High |
| `docs/output_schema.md` | 22 parquet table definitions + analyst_report.md | High |
| `docs/feedback/` | Gap reviews, evaluations, planning artifacts | Low (reference only) |
| `scripts/README.md` | Pipeline script catalog — inputs, outputs, safety labels | Medium |
| `SCRATCHPAD.md` | Working memory — KEEP-marked content is durable | Low |
| `examples/` | Fixture CSVs and mapping YAMLs | Reference |

## Hard constraints (read before touching any file)

- **Do not use external market, CPI, inflation, or macroeconomic data** — blocked by default; explicit user request required.
- **Never invent missing values, service mappings, prices, or customer IDs** — flag as exceptions instead.
- **All numeric conclusions must trace to a Python/pandas calculation**, not LLM inference.
- **Source CSVs are read-only** — never modify inputs in `examples/`.
- **Python version: 3.14.4** (`/opt/homebrew/opt/python@3.14/bin/python3.14`).
- **venv location:** `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/` — never inside this folder.
- **Real-data gate:** do not run pipeline on production data until Phase 4b.1 (service-map reconciliation) + 4b.2 (control totals) are complete.

## Task routing

### Architecture or design questions

Read:
1. `.archcore/adr/`
2. `.archcore/specs/`
3. `ARCHITECTURE.md`
4. `docs/data_contract.md`, `docs/output_schema.md`

Do not answer from SCRATCHPAD alone.

### Planning or status questions

Read:
1. `.archcore/plans/`
2. `ROADMAP.md`
3. `CHANGELOG.md`
4. `SCRATCHPAD.md` (KEEP sections)

Report uncertainty if these disagree.

### Agent or governance questions

Read:
1. `AGENTS.md`
2. `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `.archcore/rules/`

### Implementation or code questions

Read:
1. `AGENTS.md`
2. `scripts/README.md`
3. Relevant script file under `scripts/`
4. Relevant test file under `tests/`
5. `docs/data_contract.md` or `docs/output_schema.md` if schema is involved

Use code navigation tools when available. Prefer `scripts/README.md` before running any script.

### Skill behavior questions

Read:
1. `internal-invoice-analysis/SKILL.md` — canonical skill behavior (source of truth)
2. `ARCHITECTURE.md` — pipeline layers and component map
3. `docs/data_contract.md` — input schema

Do not answer skill behavior questions from `docs/invoice_analysis_framework.md` alone — that is a planning/research artifact, not the operational spec.

### Script execution

Before running any script:
1. Read `justfile` — preferred task runner; `just --list` shows all tasks.
2. Read `scripts/README.md` — purpose, inputs, outputs, safety label for each script.
3. Read `SETUP.md` — venv activation and CLI flag patterns.
4. Confirm venv is active: `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/`.
5. Run in pipeline order: validate_inputs → load_inputs → invoice_analysis_skeleton → rate_card_analysis → trend_analysis → llm_analyst.

Prefer `just <task>` over raw `python scripts/...` invocations. Do not skip steps or run scripts out of order unless the relevant parquet files already exist in `db/`.

### Documentation updates

Before updating docs, check:
1. `.archcore/`
2. `ARCHITECTURE.md` (component map — update when adding/changing scripts)
3. `docs/output_schema.md` (table definitions — update when adding output tables)
4. `ROADMAP.md` (phase items — tick when complete)
5. `CHANGELOG.md` (append meaningful governance/navigation changes)

Keep `AGENTS.md` and `SETUP.md` current when adding dependencies or invocation patterns.

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority (see Source priority above).
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

Known tension: `docs/invoice_analysis_framework.md` is 884 lines of design survey that may conflict with what was actually built. Always prefer `ARCHITECTURE.md` + `internal-invoice-analysis/SKILL.md` over the framework doc.

## Update rules

| Change type | Update |
|---|---|
| New durable decision | Add/propose `.archcore/adr/` |
| New agent/project rule | Add/propose `.archcore/rules/` |
| New architecture contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New approved plan | Add/propose `.archcore/plans/` |
| New script or changed script | Update `scripts/README.md` and `ARCHITECTURE.md` component map |
| New parquet table | Update `docs/output_schema.md` |
| Phase complete | Tick in `ROADMAP.md` and update `SCRATCHPAD.md` current state |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance file changed | Append `CHANGELOG.md` |

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file | Purpose | Command to regenerate |
|---|---|---|
| `graphify-out/GRAPH_REPORT.md` | Relationship/navigation overview | `graphify update .` |
| `graphify-out/graph.json` | Machine-readable graph | `graphify update .` |
| `.ai-context/governance-pack.md` | Deterministic governance context bundle | `repomix --config repomix.config.json` |

Regenerate after large documentation, architecture, or source changes.

<!-- END skill-ai-it:navigation -->
