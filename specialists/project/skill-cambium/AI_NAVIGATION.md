# AI Navigation — skill-cambium

Purpose: context entrypoint for AI agents working on the skill-cambium specialist pack. Tells agents where knowledge lives, what to read first, what is authoritative, and what to update after work.

This file is a router, not the knowledge store.

<!-- BEGIN skill-ai-it:navigation --> <!-- skill-ai-it:manual reason="task->reference routing table (6 files) and the skill-smc cross-pack boundary are project-specific; the generic template has no
equivalent and would delete them" -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Reference routing (task → file)](#reference-routing-task--file)
- [Project context files](#project-context-files)
- [Cross-pack boundary](#cross-pack-boundary)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)

---

## Mandatory read order

1. `AGENTS.md`
2. `AI_NAVIGATION.md` (this file)
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `references/*.md` for the task at hand (via `RUNBOOK.md`'s Reference Routing table)
6. Relevant `.archcore/` documents, if any exist yet

## Source priority

1. `.archcore/` accepted ADRs, rules, specs — 6 documents accepted 2026-09-17; see [`.archcore/README.md`](.archcore/README.md) for the index
2. `SKILL.md` (Standing Write-Back Contract, Use When, Related Skills)
3. `references/*.md` (content source — the numbered files)
4. `AGENTS.md` / `CLAUDE.md`
5. `AI_NAVIGATION.md` / `context-map.yaml`
6. `CHANGELOG.md`
7. `manifest.json` `stable_facts` (a snapshot, not the live source — see below)
8. `SCRATCHPAD.md` (temporary unless marked `KEEP` or promoted)

**`manifest.json`'s `stable_facts` and this pack's `references/` are themselves not the live device data.** For anything about a specific model or device, the live source is
`cambium-swap/inventory/device-family-matrix.csv` and `cambium-swap/inventory/device-inventory.csv` — read those files, don't rely on this pack's summary of them.

## Reference routing (task → file)

| Task                                                                                               | Read                                          |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Device families, models, firmware/EoL snapshot, evidence-state discipline                          | `references/01_overview.md`                   |
| Device local-admin access, KeePassXC vault structure, `kp` wrapper gotchas                         | `references/02_device-access-and-vault.md`    |
| Asset-register naming convention, per-site drift, site-name convention, R195P IP-derivation rule   | `references/03_asset-register-conventions.md` |
| `device-inventory.csv` schema, `UNKNOWN` discipline, extraction workflow                           | `references/04_device-inventory-schema.md`    |
| Coverage gaps, unverified assumptions, staleness risks                                             | `references/05_known-issues.md`               |
| Device REST API / SSH CLI data points per adapter method, config-backup source, write-ops boundary | `references/06_device-api-cli-reference.md`   |

## Project context files

| File / Path       | Role                                                   | Authority   |
| ----------------- | ------------------------------------------------------ | ----------- |
| `SKILL.md`        | Agent activation surface, Standing Write-Back Contract | Highest     |
| `references/*.md` | Content source                                         | Highest     |
| `.archcore/`      | Durable rules/ADR/spec — 6 accepted 2026-09-17         | Highest     |
| `AGENTS.md`       | Universal agent instruction file                       | High        |
| `CLAUDE.md`       | Claude-specific bootstrap file                         | High        |
| `RUNBOOK.md`      | Navigation index only — not a content source           | Routing     |
| `manifest.json`   | Machine-readable metadata + fact snapshot              | Medium      |
| `CHANGELOG.md`    | Durable pack change history                            | Medium-high |
| `SCRATCHPAD.md`   | Temporary notes                                        | Low         |

## Cross-pack boundary

If a task is about the SMC box, Ansible authoring, or provisioning roles rather than the Cambium hardware itself, this is the wrong pack — route to `skill-smc` (see its own `AI_NAVIGATION.md`). If a
fact spans both (e.g. a `site_name` value, a `smc_cnmaestro_provisioning` behaviour), write it to both packs' matching reference files in the same session.

## Generated context

`.ai-context/governance-pack.md` (Repomix) is disposable generated support, not canonical truth. Regenerate after significant reference-file changes:
```
repomix --config /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-cambium/repomix.config.json
```

## Context compaction recovery

When recovering agent context after compaction (new session, cleared context window):

1. Read this file (`AI_NAVIGATION.md`) first for the mandatory read order and routing table above.
2. Read `context-map.yaml` for the machine-readable routing map.
3. Load `.archcore/` context if present — no longer empty: 6 documents (2 ADRs, 3 rules, 1 spec) accepted 2026-09-17, see [`.archcore/README.md`](.archcore/README.md) for the index. Re-check the
   count, it may have grown further.
4. Regenerate `.ai-context/governance-pack.md`: `repomix --config repomix.config.json`.
5. Verify `SCRATCHPAD.md` has current state; if empty or stale, populate from memory-keeper / mcp-project-context.
6. Verify `CHANGELOG.md` is current with recent governance/content changes.
7. Verify this file and `context-map.yaml` agree — see Update rules below for which companion files move together.

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Drift handling

If sources disagree: stop, name the conflicting files, state which has higher authority per the priority list above, propose the smallest correction, and do not silently merge assumptions.

## Update rules

| Change type                  | Update                                                        |
| ---------------------------- | ------------------------------------------------------------- |
| New durable Cambium fact     | The matching `references/*.md` file (see routing table above) |
| New durable rule/decision    | Propose `.archcore/rules/` or `.archcore/adr/`                |
| Routing changed              | `AI_NAVIGATION.md` and `context-map.yaml`                     |
| Any content/structure change | `manifest.json` version bump + `CHANGELOG.md` entry           |
| Temporary note               | `SCRATCHPAD.md` only, mark `KEEP` if it should survive        |

**Companion files** — `context-map.yaml`'s `update_rules.governance_navigation` names which files move together. In short: a change to `AGENTS.md` also touches `AI_NAVIGATION.md`, `context-map.yaml`,
and `scripts/README.md`; a change to this file also touches `context-map.yaml`; a new script also touches `scripts/README.md`, `AGENTS.md`, and `justfile`. Check that map before treating a
governance/routing edit as complete.

<!-- END skill-ai-it:navigation -->
