---
title: EvidenceBundle Contract
status: accepted
date: 20260525
provenance: schemas/evidence-bundle.schema.yaml, docs/evidence-contract.md, SKILL.md
---

# EvidenceBundle Contract

## Purpose

`EvidenceBundle` is the required output of every rag-tools retrieval operation. The LLM must answer only from EvidenceBundle content — never from training knowledge. Exact amounts, dates, clause references, and identifiers must not be inferred; they must come from the `excerpt` field. If no valid EvidenceBundle is returned, the agent must report `RETRIEVAL_NOT_READY` and stop.

## Required fields

| Field | Type | Description |
|---|---|---|
| `query` | string | The exact original query or lookup term submitted |
| `retrieval_mode` | string | Mode that produced this bundle (must reflect actual mode used) |
| `excerpt` | string | Verbatim text extracted from the source file — the ONLY field the LLM may answer from |
| `source_file` | string | Absolute path to the canonical source file — never a Qdrant collection name |

## Allowed `retrieval_mode` values

- `direct_structured_lookup`
- `section_clause_lookup`
- `heading_aware_lookup`
- `table_aware_lookup`
- `tabular_analytics`
- `keyword_lookup`
- `vector_rag`
- `hybrid_direct_first`
- `hybrid_rag_first`

## Notable optional fields

| Field | Type | Use |
|---|---|---|
| `document_id` | string | File stem — strongly recommended for citation |
| `authority` | string | `source` / `wiki_article` / `external_reference` / `derived` |
| `section_id` | string | Structured section ID (e.g. "C2.11") — enables exact clause-level citation |
| `section_path` | list[string] | Heading chain from root to matched section |
| `heading` | string | Nearest heading above matched text |
| `table_id` | string | Table identifier — required for `table_aware_lookup` results |
| `row_keys` | list[string] | Short row-key preview for matched table rows |
| `score_or_confidence` | float | Cosine similarity (RAG) or 1.0 (exact match) |
| `retrieval_warnings` | list[string] | Populated when: source missing, fallback used, low score, partial match |

## Answer rules

1. Answer only from `excerpt` content — never from training knowledge.
2. Do not infer amounts, dates, identifiers, or clause text not present in the excerpt.
3. If evidence is missing for a fact, state "not found in retrieved evidence" — do not guess.
4. Qdrant payloads are retrieval artifacts. `source_file` is the authority, not the collection name.
5. When multiple bundles are returned, cite each separately by `source_file` + `section_id`/`heading`.
6. Do not merge conflicting excerpts into a single answer — report the conflict.
7. `retrieval_warnings` must be surfaced in the answer when present.

## Citation requirements

- **Minimum:** `source_file` (required)
- **Preferred:** `source_file` + (`section_id` OR `heading` OR `table_id`)
- **Full:** `source_file` + `section_path` + `section_id` + excerpt snippet
- For table results: include `table_id` and relevant `row_keys`

## Invalid bundle conditions

- `excerpt` is empty with no `retrieval_warning` — do not answer from it
- `source_file` is a Qdrant collection name, not a file path — invalid citation
- `retrieval_warnings` missing despite fallback or low score — silent failure

## Validation checklist

See `checklists/evidence-bundle-validation.md`.

## Related

- [schemas/evidence-bundle.schema.yaml](../../schemas/evidence-bundle.schema.yaml)
- [docs/evidence-contract.md](../../docs/evidence-contract.md)
- [checklists/evidence-bundle-validation.md](../../checklists/evidence-bundle-validation.md)
- [templates/evidence-bundle.yaml](../../templates/evidence-bundle.yaml)
