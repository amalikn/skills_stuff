# AI Navigation — Agent Stack

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work.

This file is a router, not the full knowledge store.

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Script and task navigation](#script-and-task-navigation)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Agent answer contract](#agent-answer-contract)

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. [AGENTS.md](AGENTS.md)
2. [AI_NAVIGATION.md](AI_NAVIGATION.md)
3. [context-map.yaml](context-map.yaml)
4. [CHANGELOG.md](CHANGELOG.md)
5. The contract that governs the layer you are touching — [manifest.yaml](manifest.yaml), [routing.toml](routing.toml), [SKILL_STANDARD.md](SKILL_STANDARD.md), or [RUNTIME.md](RUNTIME.md)

## Source priority

When sources conflict, use this priority:

1. [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md) — including the safety model, which nothing imported may override
2. [manifest.yaml](manifest.yaml) — the install contract; the authority on what the library contains
3. [routing.toml](routing.toml) — the routing catalogue; the authority on how work is dispatched
4. [SKILL_STANDARD.md](SKILL_STANDARD.md) and [RUNTIME.md](RUNTIME.md) — the skill quality and runtime contracts
5. [AI_NAVIGATION.md](AI_NAVIGATION.md) and [context-map.yaml](context-map.yaml)
6. [.archcore/README.md](.archcore/README.md) — durable decisions, rules and contracts, promoted 2026-09-02. **Highest authority.**
7. [MEMORY.md](MEMORY.md) — measured baselines, metric definitions and traps already hit; read before changing anything in the routing layer
8. [CHANGELOG.md](CHANGELOG.md) and [REVISION_NOTES.md](REVISION_NOTES.md)
9. [ARCHITECTURE.md](ARCHITECTURE.md)
10. `docs/audits/audit-agent-stack-full-20260901_1010.md` — findings and recommendations, not settled decisions
11. [SCRATCHPAD.md](SCRATCHPAD.md)

`SCRATCHPAD.md` is temporary unless explicitly marked `KEEP`.

**The audit is evidence, not policy.** It records findings and recommends changes; `REVISION_NOTES.md` records which were acted on and which were deliberately deferred. Do not treat an audit
recommendation as an accepted decision without checking the revision notes first.

## Project context files

| File / Path                               | Role                                                                                                                    | Authority                    |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `AGENTS.md`                               | Agent policy, safety model, runtime placement                                                                           | High                         |
| `CLAUDE.md`                               | Claude-specific wrapper over AGENTS.md                                                                                  | High                         |
| `manifest.yaml`                           | Capability inventory and install contract                                                                               | Highest for library contents |
| `routing.toml`                            | Routing catalogue: capabilities, gates by required capability, ownership precedence, route invariants, execution class, | Highest for dispatch         |
|                                           |   prerequisites                                                                                                         |                              |
| `SKILL_STANDARD.md`                       | Local skill quality/trigger/runtime/safety contract                                                                     | High                         |
| `RUNTIME.md`                              | Root environment and consumer-isolation policy                                                                          | High                         |
| `AI_NAVIGATION.md`                        | Human-readable AI routing file                                                                                          | High                         |
| `context-map.yaml`                        | Machine-readable routing map                                                                                            | High                         |
| `ARCHITECTURE.md`                         | Component and data-flow overview                                                                                        | Medium-high                  |
| `CHANGELOG.md`                            | Durable project/governance change history                                                                               | Medium-high                  |
| `REVISION_NOTES.md`                       | What the last revision changed and deliberately did not change                                                          | Medium-high                  |
| `evals/routing-cases.toml`                | 60-case routing regression corpus across 6 workload families                                                            | Medium-high                  |
| `ROUTING_EVALS.md`                        | Corpus coverage, case assertion types, static vs behavioural running                                                    | Medium-high                  |
| `docs/audits/audit-agent-stack-full-20260901_1010.md` | Full repository audit and findings                                                                                      | Evidence                     |
| `docs/audits/audit-agent-stack.md`                    | Earlier audit — check supersession before citing                                                                        | Evidence                     |
| `.archcore/`                              | Durable decisions, rules, contracts, guides, plans — **29 accepted 20260902**                                               | Highest                      |
| `MEMORY.md`                               | Measured baselines, metric definitions, traps already hit                                                               | High                         |
| `SCRATCHPAD.md`                           | Temporary notes and open items                                                                                          | Low                          |
| `personas/`                               | 15 specialist judgement contracts — indexed in [personas/README.md](personas/README.md)                                 | Source                       |
| `skills/`                                 | Skill packages and one single-file skill                                                                                | Source                       |

## Task routing

### Library changes — adding, removing, or editing a persona or skill

Read [manifest.yaml](manifest.yaml), [routing.toml](routing.toml), [SKILL_STANDARD.md](SKILL_STANDARD.md).

A library change is not complete until the manifest row, the routing entry, and the skill's own `SKILL.md` all agree. `just check` asserts the manifest side; `just governance` asserts the
documentation side.

### Orchestration and routing behaviour

Read [routing.toml](routing.toml), `skills/skill-agent-stack/SKILL.md`, `skills/team/SKILL.md`, `personas/orchestrator-follett.md`, then [ROUTING_EVALS.md](ROUTING_EVALS.md) and
[evals/routing-cases.toml](evals/routing-cases.toml).

Routing changes need a regression case. Do not change dispatch behaviour without adding or updating an eval. The corpus holds 60 cases across six workload families — `networking-infrastructure`,
`software-ai-engineering`, `jdm-import`, `atar-import`, `business-research`, and `direct-adversarial` — asserting primary ownership, forbidden skills, maximum team size, and gate firing.

`just routing-eval-check` validates the corpus against `routing.toml` with no model call and belongs in every preflight. `just routing-eval "<cli>"` is the behavioural run: it invokes an
operator-supplied local agent CLI once per case and scores the returned plan. Treat the behavioural run as `review-required` and `long-running`.

### Upstream sync and translation


Sync is report-first. `translation_required`, `manual_merge`, and `remove_review` are proposals for a human, never automatic. Audit findings A1 and A2 concern this tool's failure behaviour and are
open — read them before changing apply logic.

### Installation and runtime

Read [RUNTIME.md](RUNTIME.md), `scripts/install_global.py`, [.mise.toml](.mise.toml), [justfile](justfile).

Installation is symlink-only and never overwrites a pre-existing global entry. The venv belongs in the working-cache peer, never in this repo.

### Governance and agent behaviour

Read [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), [AI_NAVIGATION.md](AI_NAVIGATION.md), [context-map.yaml](context-map.yaml), [CHANGELOG.md](CHANGELOG.md).

## Script and task navigation

For script, task, or automation questions, read in this order:

1. [justfile](justfile)
2. [scripts/README.md](scripts/README.md)
3. Raw scripts under `scripts/`

Prefer `just --list` and `just <task>`. Treat uncataloged scripts as `unknown` safety until inspected. Do not run a task labelled `destructive`, `review-required`, or `unknown` without review — in
this project that includes every `global-install` and `global-uninstall` invocation.

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority.
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Update rules

| Change type                                 | Update                                                                                                     |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Persona or skill added, removed, or renamed | `manifest.yaml`, `routing.toml`, the skill's `SKILL.md`, then `just check` and `just governance`           |
| Routing or dispatch behaviour changed       | `routing.toml`, `skills/skill-agent-stack/SKILL.md`, `evals/routing-cases.toml`, then `just routing-eval-check` |
| Skill quality rule changed                  | `SKILL_STANDARD.md`, and `skills/skill-creator/scripts/quick_validate.py` if the accepted key set moved    |
| Runtime or environment rule changed         | `RUNTIME.md`, `.mise.toml`, `justfile`                                                                     |
| Script or task added/changed                | `scripts/README.md` and `justfile`                                                                         |
| Context routing changed                     | `AI_NAVIGATION.md` and `context-map.yaml`                                                                  |
| Any durable governance/navigation change    | `CHANGELOG.md`                                                                                             |

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file                   | Purpose                                                         |
| -------------------------------- | --------------------------------------------------------------- |
| `.ai-context/governance-pack.md` | Deterministic context bundle — rebuild with `just context-pack` |
| `graphify-out/GRAPH_REPORT.md`   | Relationship/navigation overview — OPTIONAL, never generated here; absent is normal |

Regenerate after large documentation, contract, or library changes.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say "not found in project context" if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.
