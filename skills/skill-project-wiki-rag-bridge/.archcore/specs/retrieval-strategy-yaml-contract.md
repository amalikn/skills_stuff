---
title: retrieval-strategy.yaml Contract
status: accepted
date: 20260525
provenance: schemas/retrieval-strategy.schema.yaml, prompts/02b-profile-and-recommend-strategy.md
---

# retrieval-strategy.yaml Contract

## Purpose

`retrieval-strategy.yaml` is the per-project strategy configuration. It records the chosen primary, secondary, and fallback retrieval mode for each candidate document, along with RAG suitability, benchmark status, and the `index_allowed` gate. Produced by prompt 02b; updated by prompt 02c.

Lives at: `<project>/rag/retrieval-strategy.yaml`

## Required top-level structure

```yaml
version: 1
project:
  id: <string>
  slug: <lowercase_alphanumeric_underscores>    # matches Qdrant project slug
  name: <string>
strategy_defaults:
  exact_facts: <retrieval_mode>
  tables: <retrieval_mode>
  structured_sections: <retrieval_mode>
  cross_document_semantic: <retrieval_mode>
  invoices: <retrieval_mode>
  pdfs: <retrieval_mode>
documents:
  - <document_entry>   # one per candidate
rules:
  source_files_remain_authoritative: true    # must be true
  profile_before_index: true                 # must be true
  benchmark_before_default_route: true       # must be true
  evidence_bundle_required: true             # must be true
  vector_rag_not_universal_default: true     # must be true
```

## Required document entry fields

| Field | Type | Constraint |
|---|---|---|
| `document_id` | string | File stem (no extension) — must match source-profile filename |
| `path` | string | Relative path from project root |
| `document_class` | string | One of the 14 allowed values |
| `primary` | string | Primary retrieval mode |
| `rag_suitability` | string | `suitable` / `partially_suitable` / `not_suitable` |
| `benchmark_required` | boolean | Should be `true` for structured/tabular documents |
| `benchmark_status` | string | `not_run` / `passed` / `partial` / `failed` |
| `index_allowed` | boolean | Must be `false` unless `benchmark_status: passed` AND `rag_suitability` in (`suitable`, `partially_suitable`) |
| `reason` | string | Explains route selection — required for audit traceability |

## Optional document entry fields

- `authority`: `project_local` / `wiki_authoritative_markdown` / `external_reference`
- `secondary`: secondary retrieval mode
- `fallback`: fallback retrieval mode

## Forbidden combinations

- `index_allowed: true` without `benchmark_status: passed` — **forbidden**
- `rag_suitability: not_suitable` with `index_allowed: true` — **forbidden**
- `benchmark_required: false` for structured or tabular document — should be `true`
- Missing `reason` field — breaks audit traceability

## Template

See `templates/retrieval-strategy.yaml`.

## Example

See `examples/vocus-profitability/retrieval-strategy.yaml`.

## Related

- [schemas/retrieval-strategy.schema.yaml](../../schemas/retrieval-strategy.schema.yaml)
- [document-profile-contract.md](document-profile-contract.md)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
- [prompts/02c-benchmark-retrieval-routes.md](../../prompts/02c-benchmark-retrieval-routes.md)
