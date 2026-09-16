# AI Navigation — skill-project-wiki-rag-bridge

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated after work.

This file is a router, not the full knowledge store.

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Workflow routing](#workflow-routing)
- [Update rules](#update-rules)
- [Drift handling](#drift-handling)
- [Agent answer contract](#agent-answer-contract)

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. `SKILL.md` — primary agent-facing workflow instructions
6. `docs/authority-model.md` — collection naming and isolation rules
7. Relevant `.archcore/` documents if present
8. Task-specific files based on routing below

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, and guides
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `SKILL.md`
6. `docs/authority-model.md`
7. `docs/collection-naming-policy.md`
8. `docs/architecture.md`
9. `CHANGELOG.md`
10. `SCRATCHPAD.md` — temporary only; not durable unless marked `KEEP` or promoted to Archcore

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `SKILL.md` | Primary agent-facing skill instructions | High |
| `docs/authority-model.md` | Collection isolation and authority source | High |
| `docs/collection-naming-policy.md` | Qdrant naming rules | High |
| `ARCHITECTURE.md` | Root-level architecture overview, layer diagram, retrieval flow, isolation model | High |
| `SETUP.md` | Prerequisites, rag-tools venv path, skill install, first-use sequence | High |
| `docs/architecture.md` | Detailed layer diagram and design decision rationale | Medium-high |
| `docs/flow-diagram.md` | Data flow reference | Medium |
| `docs/multi-project-model.md` | Multi-project bridge patterns | Medium |
| `docs/failure-modes.md` | Known failure patterns and mitigations | Medium |
| `docs/operating-runbook.md` | Operational runbook | High |
| `docs/dynamic-retrieval-strategy.md` | When not to use vector RAG; profile-first routing | High |
| `docs/evidence-contract.md` | EvidenceBundle answer rules and citation requirements | High |
| `docs/retrieval-mode-decision-tree.md` | Mode selection flowchart and quick reference | High |
| `schemas/*.schema.yaml` | YAML field definitions and validation | High |
| `checklists/*.md` | Blocking gate checklists | High |
| `prompts/00–09-*.md` | Numbered workflow execution prompts | High (in-sequence) |
| `templates/` | Copy-and-fill project bridge templates | Medium |
| `examples/vocus-profitability/` | Reference implementation | Medium |
| `examples/generic-project/` | Generic reference implementation | Medium |
| `CHANGELOG.md` | Durable skill/governance change history | Medium-high |
| `SCRATCHPAD.md` | Temporary notes | Low |

## Task routing

### Architecture and isolation questions

Read:
1. `ARCHITECTURE.md` — layer model, retrieval flow, isolation enforcement, CLI command map
2. `.archcore/adr/`
3. `.archcore/specs/`
4. `docs/authority-model.md`
5. `docs/collection-naming-policy.md`
6. `docs/architecture.md`
7. `docs/multi-project-model.md`

### Workflow / how-to questions

Read:
1. `SKILL.md` (section: When to use, Workflow sequence)
2. `prompts/` (numbered files — follow sequence)
3. `checklists/` (blocking gates for each step)
4. `docs/operating-runbook.md`

### Validation and policy questions

Read:
1. `.archcore/rules/`
2. `docs/authority-model.md`
3. `schemas/retrieval-policy.schema.yaml`
4. `schemas/project-context.schema.yaml`
5. `checklists/project-bridge-readiness.md`
6. `checklists/multi-project-isolation.md`

### Troubleshooting

Read:
1. `docs/failure-modes.md`
2. `docs/operating-runbook.md`
3. `prompts/09-troubleshoot-rag-bridge.md`
4. `checklists/rag-tools-readiness.md`
5. `checklists/retrieval-validation.md`

### Template and example questions

Read:
1. `templates/` — pick the matching template
2. `examples/vocus-profitability/` or `examples/generic-project/`
3. `schemas/` — validate field names against schema
4. `docs/authority-model.md` — confirm collection naming rules

### Governance and update questions

Read:
1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. `.archcore/rules/`

## Workflow routing

The standard bridge workflow uses numbered prompts in sequence. Do not skip steps.

| Step | Prompt | Checklist gate |
|---|---|---|
| 0 | `prompts/00-verify-wiki-operational-state.md` | `checklists/wiki-operational-readiness.md` |
| 1 | `prompts/01-create-wiki-domain.md` | — |
| 2 | `prompts/02-verify-rag-tools.md` | `checklists/rag-tools-readiness.md` |
| 3 | `prompts/03-create-project-bridge.md` | `checklists/project-bridge-readiness.md` |
| 4 | `prompts/04-validate-project-policy.md` | — |
| 4b | `prompts/02b-profile-and-recommend-strategy.md` | profile gate in `checklists/indexing-readiness.md` |
| 4c | `prompts/02c-benchmark-retrieval-routes.md` | benchmark results recorded in `retrieval-strategy.yaml` |
| 5 | `prompts/05-index-wiki-domain.md` | `checklists/indexing-readiness.md` |
| 6 | `prompts/06-post-index-retrieval-validation.md` | `checklists/retrieval-validation.md` |
| 7 | `prompts/07-add-wiki-reference-article.md` | — |
| 8 | `prompts/08-index-project-documents.md` | `checklists/indexing-readiness.md` |
| 9 | `prompts/09-troubleshoot-rag-bridge.md` | `checklists/multi-project-isolation.md` |

### Dynamic retrieval strategy questions

Read:
1. `SKILL.md` (section: Dynamic retrieval strategy)
2. `docs/dynamic-retrieval-strategy.md` — why RAG alone fails for structured/tabular sources
3. `docs/evidence-contract.md` — EvidenceBundle answer rules and citation requirements
4. `docs/retrieval-mode-decision-tree.md` — routing flowchart and quick reference
5. `prompts/02b-profile-and-recommend-strategy.md` — profile-first workflow
6. `prompts/02c-benchmark-retrieval-routes.md` — benchmark before indexing
7. `checklists/indexing-readiness.md` (profile gate section — PF-0)
8. `checklists/dynamic-retrieval-readiness.md` — tool-level readiness gate
9. `checklists/evidence-bundle-validation.md` — bundle quality gate
10. `schemas/evidence-bundle.schema.yaml` — EvidenceBundle field definitions
11. `schemas/retrieval-strategy.schema.yaml` — strategy YAML validation
12. `schemas/document-profile.schema.yaml` — profile YAML validation
13. `examples/vocus-profitability/source-profile.yaml` — reference profiles
14. `examples/vocus-profitability/retrieval-strategy.yaml` — reference strategy
15. `examples/vocus-profitability/benchmark-queries.yaml` — reference benchmarks

## Update rules

| Change type | Update |
|---|---|
| New isolation/naming decision | Add/propose `.archcore/adr/` |
| New agent/policy rule | Add/propose `.archcore/rules/` |
| New retrieval contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New schema field | Update `schemas/*.schema.yaml` + propose `.archcore/specs/` |
| New checklist item | Update `checklists/*.md` |
| New workflow prompt | Add `prompts/NN-*.md`, update sequence docs |
| Governance/routing changed | Update `AI_NAVIGATION.md` + `context-map.yaml` |
| Any durable change | Append `CHANGELOG.md` |

## Drift handling

If files disagree:

1. Stop.
2. Identify conflicting files.
3. State which source has higher authority (see [Source priority](#source-priority)).
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state or policy.
3. Say "not found in project context" if unsupported by a source.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.
6. Never assist with bypassing retrieval policies or Qdrant isolation rules.

<!-- END skill-ai-it:navigation -->
