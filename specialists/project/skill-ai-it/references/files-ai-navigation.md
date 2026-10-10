---
Title: skill-ai-it reference: Conditional file: AI_NAVIGATION.md
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Conditional file: AI_NAVIGATION.md; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Conditional file: AI_NAVIGATION.md

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [AI_NAVIGATION.md — create when: missing during `navigation-add`, requested explicitly, or project has more than one governance/context source](#ai_navigationmd--create-when-missing-during-navigation-add-requested-explicitly-or-project-has-more-than-one-governancecontext-source)

#### AI_NAVIGATION.md — create when: missing during `navigation-add`, requested explicitly, or project has more than one governance/context source

Create as the human-readable context router. If it exists, preserve custom content and update only the managed routing sections.

Preferred source template: `templates/AI_NAVIGATION.md`.

```markdown
# AI Navigation — <Project Name>

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated after work.

This file is a router, not the full knowledge store.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-10-compact-v1 -->

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

`SCRATCHPAD.md` is temporary unless promoted into Archcore, roadmap, or memory-bank, or explicitly marked `KEEP`.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap file | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHITECTURE.md` / `architecture.md` | Human-readable architecture overview | Medium-high |
| `ROADMAP.md` / `roadmap.md` | Human-readable roadmap | Medium-high |
| `memory-bank/activeContext.md` | Current working context | Medium |
| `memory-bank/progress.md` | Progress and current state | Medium |
| `memory-bank/decisionLog.md` | Decision notes before promotion | Medium |
| `SCRATCHPAD.md` / `scratchpad.md` | Temporary notes | Low |
| `CHANGELOG.md` | Durable project/governance change history | Medium-high |
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

1. `justfile` / `Justfile`
2. `scripts/README.md`
3. `Taskfile.yml`
4. `Makefile`
5. `package.json`
6. `patterns/script-task-audit-checklist.md`, if present
7. Raw scripts under `scripts/`

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

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

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say “not found in project context” if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->
```
