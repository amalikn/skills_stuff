---
title: Dynamic Retrieval Routing Guide
status: accepted
date: 20260525
provenance: docs/dynamic-retrieval-strategy.md, docs/retrieval-mode-decision-tree.md, SKILL.md
---

# Dynamic Retrieval Routing Guide

## Core principle

Vector RAG is not the universal default. Retrieval mode must be selected based on the document class, its structural features, and benchmark results. Always profile before deciding to index.

## Profile-first workflow

```
profile-file → recommend-strategy → (benchmark-file) → index_allowed decision
```

Never set `index_allowed: true` without a completed benchmark for structured or tabular sources.

## CLI commands

```bash
source tools-working-cache/rag-tools/.venv/bin/activate

# Profile a document
rag-tools profile-file <path>

# Recommend retrieval strategy from profile
rag-tools recommend-strategy <source-profile.yaml>

# Structured section lookup (no indexing required)
rag-tools structured-lookup <path> --section <id>

# Section/clause lookup by heading
rag-tools lookup-section <path> --heading <text>

# Table-aware lookup
rag-tools lookup-table <path> --query <text>

# Benchmark retrieval modes against query set
rag-tools benchmark-file <path> <benchmark-queries.yaml>
```

## Retrieval mode routing table

| `document_class` | Primary route | When to RAG |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` / `section_clause_lookup` | Only for cross-document semantic search — not for exact-fact queries |
| `financial_rate_card` | `table_aware_lookup` | Not suitable — exact prices require deterministic lookup |
| `invoice_or_billing_report` | `tabular_analytics` | Not suitable — amounts must come from source |
| `legal_contract_or_terms` | `section_clause_lookup` | Partially suitable — only after benchmark confirms |
| `knowledge_article` | `vector_rag` | Suitable — knowledge-style content designed for RAG |
| `meeting_notes` | `keyword_lookup` | Partially suitable |
| `unstructured_pdf` | `extraction_required` | Not suitable without prior extraction |
| `tabular_dataset` | `tabular_analytics` | Not suitable for RAG |

## When NOT to index

Do not index (leave `index_allowed: false`) when:
- `benchmark_status` is `not_run` or `failed`
- `rag_suitability` is `not_suitable`
- `contains_sensitive_data: true`
- Benchmark returned label `NOT_READY_NEEDS_EXTRACTION`
- Document contains exact financial amounts or legal clause text (deterministic lookup is always more reliable)

## Benchmark route labels

| Label | Meaning |
|---|---|
| `DIRECT_FIRST` | Use `direct_structured_lookup` as primary; RAG is fallback only |
| `TABLE_LOOKUP_FIRST` | Use `table_aware_lookup`; RAG not suitable |
| `HYBRID_DIRECT_FIRST` | Deterministic lookup first; RAG for semantic cross-doc queries |
| `HYBRID_RAG_FIRST` | RAG acceptable as primary; structured as fallback |
| `RAG_FIRST` | RAG is appropriate primary mode |
| `NOT_READY_NEEDS_EXTRACTION` | Source requires pre-processing before any retrieval |
| `NOT_READY_NEEDS_MORE_INDEXED_CONTENT` | Insufficient indexed content for reliable RAG |

## Source files remain authoritative

Qdrant collections are retrieval artifacts, not authoritative records. The `source_file` in every EvidenceBundle is the canonical citation target. Never cite a Qdrant collection name as the source of truth.

## Related

- [docs/dynamic-retrieval-strategy.md](../../docs/dynamic-retrieval-strategy.md)
- [docs/retrieval-mode-decision-tree.md](../../docs/retrieval-mode-decision-tree.md)
- [retrieval-strategy-yaml-contract.md](../specs/retrieval-strategy-yaml-contract.md)
- [document-profile-contract.md](../specs/document-profile-contract.md)
- [checklists/dynamic-retrieval-readiness.md](../../checklists/dynamic-retrieval-readiness.md)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
- [prompts/02c-benchmark-retrieval-routes.md](../../prompts/02c-benchmark-retrieval-routes.md)
