# Retrieval Mode Decision Tree

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/retrieval-mode-decision-tree.md`
**Purpose:** Text diagram for agents and skill users to choose the correct retrieval mode.

---

## Decision Tree

```
User query
│
├── Identify intent
│     ├── Exact fact: amount, date, clause reference, identifier, rate
│     ├── Section navigation: "what does clause X say?", "find section Y"
│     ├── Table lookup: rate card value, billing line item, pricing tier
│     ├── Semantic search: broad question, cross-document, knowledge-style
│     └── Aggregation/analytics: sum, compare, trend across table rows
│
├── Identify target source
│     ├── Known structured source (long markdown, section IDs) → check profile
│     ├── Known tabular source (CSV, rate card, invoice) → check profile
│     ├── Wiki domain (knowledge articles) → vector RAG path
│     └── Unknown → run profile-file first
│
├── Check source profile (rag/retrieval-strategy.yaml or run profile-file)
│     ├── document_class = structured_markdown_reference → direct/section lookup
│     ├── document_class = financial_rate_card → table_aware_lookup
│     ├── document_class = invoice_or_billing_report → table_aware_lookup
│     ├── document_class = legal_contract_or_terms → section_clause_lookup
│     ├── document_class = policy_document → section_clause_lookup
│     ├── document_class = knowledge_article → vector_rag
│     ├── document_class = operational_runbook → heading_aware_lookup / keyword_lookup
│     ├── document_class = tabular_dataset → table_aware_lookup (no RAG)
│     ├── document_class = unstructured_pdf | scanned_pdf → extraction_required (stop)
│     └── document_class = unknown → run profile-file before proceeding
│
├── Choose retrieval mode
│     │
│     ├── Intent = exact fact AND source has section IDs
│     │     └── rag-tools lookup-section <file> <section-id>
│     │           → EvidenceBundle with section_id + excerpt
│     │
│     ├── Intent = exact fact AND source is structured (headings, no section IDs)
│     │     └── rag-tools structured-lookup <file> "<query>"
│     │           → EvidenceBundle with heading + section_path + excerpt
│     │
│     ├── Intent = table lookup (rate, amount, tier, period)
│     │     └── rag-tools lookup-table <file> "<query>"
│     │           → EvidenceBundle with table_id + row_keys + excerpt
│     │
│     ├── Intent = broad semantic / cross-document AND wiki collection exists
│     │     └── vector RAG query against rag__wiki_<domain>
│     │           (must have policy, filters, and valid collection)
│     │           → EvidenceBundle with source_file + heading + excerpt
│     │
│     ├── Intent = broad semantic AND no collection exists
│     │     └── rag-tools structured-lookup <file> "<query>"
│     │           → use as fallback; flag in retrieval_warnings if low-confidence
│     │
│     └── Intent = aggregation / analytics
│           └── tabular_analytics (not yet a CLI command; use table lookup + manual aggregation)
│
└── Retrieve EvidenceBundle
      ├── excerpt present and non-empty → answer from excerpt only
      ├── excerpt empty → report "not found in retrieved evidence"
      ├── retrieval_warnings present → surface in answer; qualify confidence
      └── score_or_confidence < 0.5 (RAG) → flag as low-confidence
```

---

## Retrieval Mode Outputs

| Mode | CLI command | Key output fields |
|---|---|---|
| `direct_structured_lookup` | `rag-tools structured-lookup <file> <query>` | heading, section_path, excerpt |
| `section_clause_lookup` | `rag-tools lookup-section <file> <section-id>` | section_id, heading, excerpt |
| `heading_aware_lookup` | `rag-tools structured-lookup <file> <query>` | heading, excerpt |
| `table_aware_lookup` | `rag-tools lookup-table <file> <query>` | table_id, row_keys, excerpt |
| `vector_rag` | Qdrant query (requires collection) | source_file, heading, score_or_confidence, excerpt |
| `keyword_lookup` | structured-lookup fallback | matched_terms, excerpt |
| `extraction_required` | none — PDF/binary | retrieval_warnings: ["source requires extraction"] |

---

## Quick Reference: When to Use Each Mode

| Scenario | Recommended mode |
|---|---|
| "What is the rate for service X in period 3?" | `table_aware_lookup` |
| "What does clause C2.11 require?" | `section_clause_lookup` |
| "Find the section about rebate calculations" | `direct_structured_lookup` |
| "What are the key NBN WBA concepts?" | `vector_rag` (wiki domain) |
| "What is the total invoice amount for Q1?" | `tabular_analytics` (manual) |
| "What does the payment terms section say?" | `direct_structured_lookup` or `section_clause_lookup` |
| "Is there any policy on late fees?" | `vector_rag` (wiki) or `keyword_lookup` (project) |
| "Profile this file" | `profile-file` (not a retrieval mode — pre-step) |
