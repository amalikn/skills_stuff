# AI Navigation — {{PROJECT_NAME}}

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work.

This file is a router, not the full knowledge store.

<!-- BEGIN MANAGED: skill-ai-it:navigation --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Script and Task Navigation](#script-and-task-navigation)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)

---

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `.archcore/` documents, if present
6. Relevant `memory-bank/` files, if present
7. Relevant project docs/code based on the task

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
6. `ARCHITECTURE.md` / `architecture.md`
7. `ROADMAP.md` / `roadmap.md`
8. `memory-bank/activeContext.md`
9. `memory-bank/progress.md`
10. `SCRATCHPAD.md` / `scratchpad.md`
11. old notes, drafts, archived files

`SCRATCHPAD.md` is temporary unless promoted into Archcore, roadmap, memory-bank, or explicitly marked `KEEP`.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap file | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `CHANGELOG.md` | Durable project/governance change history | Medium-high |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHCORE_PROMOTION_CANDIDATES.md` | Generated list of Archcore promotion candidates from governance markdown. Read before running promote mode. | Generated support |
| `ARCHITECTURE.md` / `architecture.md` | Human-readable architecture overview | Medium-high |
| `ROADMAP.md` / `roadmap.md` | Human-readable roadmap | Medium-high |
| `memory-bank/activeContext.md` | Current working context | Medium |
| `memory-bank/progress.md` | Progress and current state | Medium |
| `memory-bank/decisionLog.md` | Decision notes before promotion | Medium |
| `SCRATCHPAD.md` / `scratchpad.md` | Temporary notes | Low |
| `docs/` | Supporting documentation | Depends on file |
| `graphify-out/` | Generated navigation graph | Generated support |
| `.ai-context/governance-pack.md` | Generated deterministic context pack | Generated support |

## Task routing

### Architecture/design questions

Read:

1. `.archcore/adr/`
2. `.archcore/specs/`
3. `ARCHITECTURE.md` / `architecture.md`
4. `docs/**/*.md`

Do not answer from scratchpad alone.

### Planning/status questions

Read:

1. `.archcore/plans/`
2. `ROADMAP.md` / `roadmap.md`
3. `CHANGELOG.md`
4. `memory-bank/progress.md`
5. `memory-bank/activeContext.md`
6. `SCRATCHPAD.md` / `scratchpad.md`

Report uncertainty if these disagree.

### Agent/governance questions

Read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `.archcore/rules/`

### Implementation/code questions

Read:

1. `AGENTS.md`
2. `context-map.yaml`
3. Relevant `.archcore/specs/`
4. Relevant source files
5. Relevant tests
6. `graphify-out/GRAPH_REPORT.md`, if present

Use code navigation tools where available.

## Script and Task Navigation

For script, task, or automation questions, read in this order:

1. Existing canonical task runner if documented
2. `justfile`
3. `scripts/README.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. Raw scripts under `scripts/` after inspection

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

### Governance coherence checks

If `scripts/check_governance.py` exists, run it before claiming any durable change is complete, and after any change that adds, moves, renames, or retires a file. It turns this project's governance
claims into assertions and exits non-zero on failure.

When it fails, fix the project — not the check. The check count is a coverage signal, not a score, and is expected to rise as the project acquires structure: a new artifact class, generated output, or
constant restated across files needs the checker's registries extended in the same pass.

### Documentation updates

Before updating docs, check:

1. `.archcore/`
2. `README.md`
3. `CHANGELOG.md`
4. `ARCHITECTURE.md` / `architecture.md`
5. `ROADMAP.md` / `roadmap.md`
6. `memory-bank/`
7. `docs/`

After updates, ensure related files are not left inconsistent.

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority.
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Update rules

| Change type | Update |
|---|---|
| New durable decision | Add/propose `.archcore/adr/` |
| New agent/project rule | Add/propose `.archcore/rules/` |
| New architecture contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New implementation plan | Add/propose `.archcore/plans/` |
| Progress change | Update `memory-bank/progress.md` |
| Current working state changed | Update `memory-bank/activeContext.md` |
| Temporary note | Add to `SCRATCHPAD.md` only if not durable |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance or navigation files changed | Append `CHANGELOG.md` |

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file | Purpose |
|---|---|
| `graphify-out/GRAPH_REPORT.md` | Relationship/navigation overview |
| `graphify-out/graph.json` | Machine-readable graph |
| `.ai-context/governance-pack.md` | Deterministic context bundle |
| `.ai-context/repo-pack.md` | Larger project/repo context bundle |

Regenerate these after large documentation, architecture, or source changes.

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. **Read `AI_NAVIGATION.md`** first — this file is the navigation map.
2. **Load `.archcore/`** — durable project truth (ADRs, rules, specs, guides, plans).
3. **Regenerate `graphify-out/`**: `graphify update .`
4. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
5. **Verify `SCRATCHPAD.md`** — if empty, populate from memory-keeper / mcp-project-context.
6. **Verify `CHANGELOG.md`** is current.
7. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Audit procedure

To verify project context coherence, run these checks:

1. Confirm `AGENTS.md` points to `AI_NAVIGATION.md`.
2. Confirm `AI_NAVIGATION.md` points to `context-map.yaml`.
3. Confirm `CHANGELOG.md` exists and recent governance/navigation changes are recorded.
4. Confirm `context-map.yaml` has routing for architecture, planning, governance, implementation, documentation, and scripts.
5. Confirm `.archcore/` is either present and routed, or absent and treated as optional.
6. Confirm generated context paths (`graphify-out/`, `.ai-context/`) are excluded from source-of-truth decisions.
7. Confirm `SCRATCHPAD.md` is marked transient.
8. Confirm repeat-run managed blocks exist where needed.
9. Confirm companion files in `context-map.yaml update_rules` were updated when source files changed.
10. Confirm drift/conflict policy says stop-and-report.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say “not found in project context” if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->
