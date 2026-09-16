---
title: Workflow Sequencing Rules
status: accepted
date: 20260524
provenance: SKILL.md, checklists/
---

# Workflow Sequencing Rules

These rules govern the sequencing and gating of the bridge setup workflow. Each step has a corresponding prompt and optional checklist gate that must be passed before proceeding.

## Sequence enforcement

- **RULE-W1:** Execute prompts in sequence (00 → 01 → 02 → 03 → 04 → 04b → 04c → 05 → 06). Do not skip steps or run them out of order.
- **RULE-W2:** Each checklist gate is a blocking gate — work through every item before marking it passed. Do not treat checklists as post-hoc review.
- **RULE-W3:** Steps 00 and 02 (wiki operational state, rag-tools verification) must pass before any indexing or bridge creation.
- **RULE-W4:** Step 04 (validate policy) must pass before any indexing (step 05).
- **RULE-W5:** Step 05 requires a dry-run confirmation before live indexing. The operator must explicitly confirm after reviewing dry-run output.
- **RULE-W6:** Step 04b (profile-and-recommend-strategy) must complete before deciding whether to index a project document or use direct structured/table lookup. Do not default to vector RAG for structured or tabular sources.
- **RULE-W7:** Every retrieval operation must return an EvidenceBundle. Answer only from the bundle's `excerpt` and `section_path` fields — never from training knowledge. If no bundle is returned, report `RETRIEVAL_NOT_READY` and stop.

## Checklist gate mapping

| Step | Prompt | Blocking checklist |
|---|---|---|
| 0 | `prompts/00-verify-wiki-operational-state.md` | `checklists/wiki-operational-readiness.md` |
| 2 | `prompts/02-verify-rag-tools.md` | `checklists/rag-tools-readiness.md` |
| 3 | `prompts/03-create-project-bridge.md` | `checklists/project-bridge-readiness.md` |
| 4b | `prompts/02b-profile-and-recommend-strategy.md` | profile gate in `checklists/indexing-readiness.md` |
| 4c | `prompts/02c-benchmark-retrieval-routes.md` | benchmark results in `retrieval-strategy.yaml` |
| 5 | `prompts/05-index-wiki-domain.md` | `checklists/indexing-readiness.md` |
| 6 | `prompts/06-post-index-retrieval-validation.md` | `checklists/retrieval-validation.md` |
| New project | Multi-project audit | `checklists/multi-project-isolation.md` |

## Template and schema rules

- **RULE-T1:** Always start bridge files from `templates/` — never write from scratch.
- **RULE-T2:** Validate all YAML bridge files against `schemas/` before accepting them.
- **RULE-T3:** Do not edit template files when working in a project context. Use templates as copy-and-fill starting points.
- **RULE-T4:** Schema validation is mandatory before running `rag-tools validate-policy`.

## Related

- [SKILL.md](../../SKILL.md)
- [checklists/](../../checklists/)
- [prompts/](../../prompts/)
- [retrieval-isolation-rules.md](retrieval-isolation-rules.md)
