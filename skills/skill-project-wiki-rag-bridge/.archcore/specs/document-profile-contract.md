---
title: Document Profile Contract
status: accepted
date: 20260525
provenance: schemas/document-profile.schema.yaml, SKILL.md
---

# Document Profile Contract

## Purpose

A document profile is the output of `rag-tools profile-file <path>`. It records structural features used by `rag-tools recommend-strategy` to select retrieval modes. Profiles are stored in `<project>/rag/source-profiles/<document_id>.yaml` and are required before any indexing or strategy decision.

## CLI command

```bash
source .venv/bin/activate
rag-tools profile-file <path> [--output <project>/rag/source-profiles/<document_id>.yaml]
```

## Required fields

| Field | Type | Description |
|---|---|---|
| `document_id` | string | File stem (no extension) — must match filename in `retrieval-strategy.yaml` |
| `title` | string | First heading text, or file stem if no headings |
| `path` | string | Absolute path to the source file — never a Qdrant collection path |
| `file_type` | string | Extension including dot (`.md`, `.csv`, `.pdf`, etc.) |
| `size_bytes` | integer | File size — zero if missing |
| `line_count` | integer | Number of lines |
| `estimated_tokens` | integer | Rough token count for chunking decisions |
| `document_class` | string | Classification from `_document_class()` — see allowed values |
| `has_headings` | boolean | |
| `heading_count` | integer | |
| `heading_levels` | list[integer] | Sorted heading depths (e.g. `[1, 2, 3]`) |
| `has_tables` | boolean | |
| `table_count` | integer | |
| `has_section_ids` | boolean | True if structured IDs like "C2.11" detected |
| `section_ids` | list[string] | Sorted list of detected section ID strings |
| `authoritative` | boolean | Always `true` for project source files |
| `recommended_retrieval_modes` | list[string] | Ordered list from `_recommended_modes()` |
| `index_allowed` | boolean | Always `false` from `profile-file` — only updated after benchmark decision |
| `notes` | list[string] | Optional profiler notes or manual annotations |

## Allowed `document_class` values

`structured_markdown_reference` | `legal_contract_or_terms` | `financial_rate_card` | `invoice_or_billing_report` | `operational_runbook` | `policy_document` | `meeting_notes` | `knowledge_article` | `source_code_docs` | `unstructured_pdf` | `scanned_pdf` | `tabular_dataset` | `mixed_content` | `unknown`

`unknown` requires manual classification before strategy can proceed.

## Critical constraints

- `contains_sensitive_data: true` always blocks indexing — `index_allowed` must remain `false`.
- `index_allowed` from `profile-file` is always `false`. Do not override at profile stage.
- `document_class: unknown` — re-run `profile-file` or classify manually before writing strategy.
- `document_id` must match the file stem exactly — mismatch breaks `retrieval-strategy.yaml` lookups.
- `path` must be absolute — required for reliable source citation.

## Storage convention

```
<project>/
  rag/
    source-profiles/
      <document_id>.yaml    # one file per profiled document
```

## Template

See `templates/source-profile.yaml`.

## Related

- [schemas/document-profile.schema.yaml](../../schemas/document-profile.schema.yaml)
- [schemas/retrieval-strategy.schema.yaml](../../schemas/retrieval-strategy.schema.yaml)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
