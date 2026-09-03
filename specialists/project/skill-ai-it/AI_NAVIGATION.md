# AI Navigation — skill-ai-it

Purpose: this file is the context entrypoint for agents maintaining `skill-ai-it`.

This package is a reusable AI governance/navigation bootstrap skill. It must remain repeat-safe, template-driven, changelog-aware, and tool-agnostic.

<!-- BEGIN MANAGED: skill-ai-it:navigation --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Context map](#context-map)
- [Task routing](#task-routing)
- [Script and Task Navigation](#script-and-task-navigation)
- [Historical context recovery](#historical-context-recovery)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)

---

## Mandatory read order

Before editing this skill package, read:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `SKILL.md`
5. Recent entries in `CHANGELOG.md`
6. `ARCHITECTURE.md`
7. Relevant files under `templates/`
8. Relevant files under `patterns/`

## Source priority

When sources conflict, use this priority:

1. `SKILL.md` orchestration rules
2. External files under `templates/`
3. External files under `patterns/`
4. `AGENTS.md`
5. `CHANGELOG.md`
6. `ARCHITECTURE.md`
7. `AI_NAVIGATION.md`
8. `context-map.yaml`
9. `README.md`

Note: for generated output content, external template files win over embedded fallback examples in `SKILL.md`.

## Context map

| Path | Role | Authority |
|---|---|---|
| `SKILL.md` | Main skill contract and orchestration logic | Highest |
| `CHANGELOG.md` | Durable package history and governance/navigation change ledger | High |
| `ARCHITECTURE.md` | Package architecture and tool-stack policy | High |
| `templates/AI_NAVIGATION.md` | Target-project AI navigation template | High |
| `templates/context-map.yaml` | Target-project routing-map template | High |
| `templates/repomix.config.json` | Target-project Repomix config template | High |
| `templates/AGENTS-navigation-block.md` | Managed AGENTS navigation block | High |
| `templates/justfile` | Preferred lightweight target-project task catalog template | High |
| `templates/scripts-README.md` | Target-project script/task inventory template | High |
| `templates/check_governance.py` | Target-project governance coherence checker template (stdlib-only, self-contained per project) | High |
| `templates/AGENTS-governance-checks-block.md` | Managed AGENTS block carrying the checker-maintenance obligation | High |
| `templates/context-preflight.sh` | Optional repo-local preflight script template, explicit request only | High |
| `patterns/archcore-routing.md` | Archcore integration guidance | Medium-high |
| `patterns/memory-bank-structure.md` | Memory Bank guidance | Medium-high |
| `patterns/drift-audit.md` | Drift audit guidance | Medium-high |
| `patterns/script-task-audit-checklist.md` | Script/task inventory audit checklist | Medium-high |
| `patterns/governance-checks.md` | Check families, artifact-to-check inference table, coverage self-policing doctrine | Medium-high |
| `patterns/navigation-control-automation.md` | Deterministic navigation-control upgrade/validate scripts guidance | Medium-high |
| `templates/update_rules.yaml` | Default companion-file update rules template | High |
| `README.md` | Human overview | Medium |
| `AGENTS.md` | Agent maintenance rules | High |
| `CLAUDE.md` | Claude wrapper | Medium |
| `SCRATCHPAD.md` | Ephemeral working notes and open follow-up items | Low |
| `ARCHCORE_PROMOTION_CANDIDATES.md` | Generated in target projects by bootstrap/refresh — durable content candidates for Archcore promotion | Generated artifact |
| `governance/watchman-events/` | Filesystem event log for historical context recovery; use when memory backends lack session detail | Low |
| `.watchmanconfig` | Watchman root config — settle 100ms, ignores `.git`, `graphify-out`, `.ai-context` | Low |
| `graphify-out/` | Generated relationship/navigation graph | Generated support |
| `.ai-context/` | Generated Repomix context packs | Generated support |

## Task routing

### Change skill behaviour

Read:

1. `SKILL.md`
2. `CHANGELOG.md`
3. `AGENTS.md`
4. `context-map.yaml`
5. Affected template/pattern files

### Change generated project output

Read:

1. Matching file under `templates/`
2. Matching fallback/example section in `SKILL.md`
3. `patterns/` file if behaviour is conceptual rather than a direct template

### Change Archcore/memory/Graphify/Repomix guidance

Read:

1. `patterns/archcore-routing.md`
2. `patterns/memory-bank-structure.md`
3. `patterns/drift-audit.md`
4. `SKILL.md`
5. `ARCHITECTURE.md`
6. affected template files

Note: changes to Archcore extraction heuristics affect `ARCHCORE_PROMOTION_CANDIDATES.md` output in target projects. Validate candidate report content after heuristic changes.

## Script and Task Navigation

For script, task, or automation questions, read in this order:

1. `justfile`
2. `scripts/README.md`
3. `patterns/script-task-audit-checklist.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. Raw scripts under `scripts/` after inspection

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

### Audit package consistency

Check:

1. Package layout in `SKILL.md`
2. Files listed in `README.md`
3. Files listed in `context-map.yaml`
4. Actual files under `templates/` and `patterns/`
5. `ARCHITECTURE.md`
6. Recent entries in `CHANGELOG.md`

## Historical context recovery

When memory backends (memory-keeper, mcp-project-context) lack detail about prior sessions, exhaust these sources in order:

1. `SCRATCHPAD.md` — current state, open items, recent session summaries
2. `CHANGELOG.md` — durable package history with timestamps
3. `governance/watchman-events/` — filesystem event timestamps; run `ls -lt governance/watchman-events/` or `watchman query . '{"fields":["name","mtime_ms"]}'` to identify session timing
4. `git log --oneline -20` — commit history as corroborating timestamp evidence

Label every reconstructed entry with its evidence basis (e.g. `Evidence basis: watchman mtime + CHANGELOG`).

## Drift handling

If `SKILL.md` and external templates disagree:

1. Identify the conflict.
2. Decide whether orchestration or template content is authoritative.
3. Update both if needed.
4. Append `CHANGELOG.md` if the change is meaningful.
5. Do not silently leave mismatched examples.

## Update rules

| Change type | Update |
|---|---|
| New operating mode | `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| New template | `templates/`, `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| New pattern | `patterns/`, `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| Repeat-safety change | `SKILL.md`, `AGENTS.md`, relevant templates, `CHANGELOG.md` |
| Context-routing change | `AI_NAVIGATION.md`, `context-map.yaml`, `AGENTS.md`, `CHANGELOG.md` |
| Any meaningful governance/navigation change | `CHANGELOG.md` |

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. **Read `AI_NAVIGATION.md`** first — this file is the navigation map.
2. **Load `.archcore/`** — durable project truth if present.
3. **Regenerate `graphify-out/`**: `graphify update .`
4. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
5. **Verify `SCRATCHPAD.md`** — if empty, populate from memory-keeper / mcp-project-context.
6. **Verify `CHANGELOG.md`** is current.
7. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Audit procedure

To verify package coherence, run these checks:

1. Package layout in `SKILL.md`
2. Files listed in `README.md`
3. Files listed in `context-map.yaml`
4. Actual files under `templates/` and `patterns/`
5. `ARCHITECTURE.md`
6. Recent entries in `CHANGELOG.md`
7. Confirm companion files in `context-map.yaml update_rules` were updated when source files changed
8. Confirm managed block version strings match current skill version
9. Confirm no duplicate managed blocks exist

<!-- END MANAGED: skill-ai-it:navigation -->
