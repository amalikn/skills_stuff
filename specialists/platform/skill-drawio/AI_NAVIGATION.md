---
Title: AI Navigation
Category: navigation
Status: current
Authority: local-supplement
Scope: Context entrypoint for AI agents in skill-drawio
Last reviewed: 2026-10-19
Summary: Where project truth lives, what to read first, what is authoritative and what must be updated after work; a router, not the knowledge store.
---

# AI Navigation — skill-drawio

Purpose: the project's context entrypoint for AI agents: where project truth lives, what to read first, what is authoritative and what must be updated after work. A router, not the knowledge store.
Full tables and procedures: [navigation reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/readme.md).

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file, including any project-authored sections below the END marker, and the upgrader regenerates everything
between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Script and Task Navigation](#script-and-task-navigation)
- [Governance coherence checks](#governance-coherence-checks)
- [Companion consistency](#companion-consistency)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)
- [Pack routing](#pack-routing)

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Mandatory read order

`AGENTS.md`, then this file, then `context-map.yaml`, then the newest `CHANGELOG.md` entries, then relevant `.archcore/` and `memory-bank/` files if present, then the docs and code the task needs.
Triage before opening: `just docs <folder>` (one header line per file); `just stale` lists stale docs.

## Source priority

`.archcore/` accepted documents, then `AGENTS.md` / `CLAUDE.md`, this file, `context-map.yaml`, `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `memory-bank/`, `SCRATCHPAD.md`, then drafts and
archives. `SCRATCHPAD.md` is transient unless marked `KEEP` or promoted.

## Project context files

High: `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`; highest when present: `.archcore/`. Medium-high: `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`. Medium: `memory-bank/`. Low:
`SCRATCHPAD.md`. On need only: `docs/history/` (rotated records, `just history <term>`) and `docs/trackers/` (open items). Generated, never truth: `.ai-context/`. Full table:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/read-order-and-sources.md#project-context-files).

## Task routing

| Question               | Read first                                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------- |
| Architecture or design | `.archcore/adr/`, `.archcore/specs/`, `ARCHITECTURE.md`, `docs/`; never answer from the scratchpad alone |
| Planning or status     | `.archcore/plans/`, `ROADMAP.md`, `CHANGELOG.md`, `memory-bank/`; say so when they disagree              |
| Agents or governance   | `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`, `.archcore/rules/`                              |
| Implementation or code | `AGENTS.md`, `context-map.yaml`, `.archcore/specs/`, the source and its tests                            |
| Documentation          | `.archcore/`, `README.md`, `CHANGELOG.md`, `docs/`; leave companions consistent                          |

## Script and Task Navigation

`just --list` first, then `scripts/README.md`, then any other runner. Never run an uncatalogued script, or one marked `destructive`, `review-required` or `unknown`, without review; propose a catalogue
update when it is stale.

## Governance coherence checks

Run `just check` (or `scripts/check_governance.py`) before calling a durable change done and after adding, moving or retiring a file. When it fails, fix the project, not the check; a new artifact
class, generated output or restated constant extends the checker's registries in the same pass.

## Companion consistency

`AGENTS.md` goes with this file, `context-map.yaml` and `scripts/README.md`; a new script goes with `scripts/README.md`, `justfile` and the checker. `context-map.yaml` `update_rules` is authoritative
for this project.

## Drift handling

When files disagree: stop, name them, say which has higher authority, propose the smallest correction. Never merge conflicting assumptions silently.

## Update rules

Decision: `.archcore/adr/`. Rule: `.archcore/rules/` or `AGENTS.md`. Routing: this file and `context-map.yaml`. Any governance or navigation change: `CHANGELOG.md`. Records over budget: `just budget
--apply`. Full table: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/change-rules.md#update-rules).

## Generated context

`.ai-context/` packs help navigation and are never a source of truth; regenerate after large changes with `repomix --config repomix.config.json`.

## Context compaction recovery

Re-read this file, `.archcore/` and the newest `CHANGELOG.md` entries; check `SCRATCHPAD.md` against the memory backends; confirm companions agree. Steps:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#context-compaction-recovery).

## Audit procedure

`just check` and `just stale` cover the mechanical part; the ten manual checks are in the
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#audit-procedure).

## Agent answer contract

Cite file paths; never invent project state; say "not found in project context" when unsupported; separate confirmed facts from assumptions; ask only when required, otherwise proceed with stated
assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack routing

Mirrors `SKILL.md` for agents entering through this router; the project's own rules outrank it.

| Task                                                                                    | Read                                   |
| --------------------------------------------------------------------------------------- | -------------------------------------- |
| Start a diagram from data; map, schema, renderer, drift check; hand-edited drawings     | [references/data-first-diagrams.md](references/data-first-diagrams.md) |
| Write or parse the XML: mxfile, root cells, layers, UserObject, links, compressed pages | [references/file-format.md](references/file-format.md) |
| Place boxes and route arrows: rows, barycentre, channels, tracks, ports, labels, sizing | [references/layout-and-routing.md](references/layout-and-routing.md) |
| Check a routed drawing; the audits, their thresholds, proving each can fail             | [references/layout-audits.md](references/layout-audits.md) |
| Colours, contrast, thin grey, one layer per colour, legends, bold labels                | [references/visual-style.md](references/visual-style.md) |
| Export pages with the desktop CLI; review before showing anyone                         | [references/export-and-self-review.md](references/export-and-self-review.md) |
| Read an existing drawing as data; group offsets; port labels to lines                   | [references/reading-drawings.md](references/reading-drawings.md) |
| Closeout: record what this engagement taught                                            | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

Tools and packages: [scripts/README.md](scripts/README.md). Worked example: [examples/shop/flows.yaml](examples/shop/flows.yaml).
