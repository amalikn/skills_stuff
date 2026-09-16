# Prompt 02b — Profile Source Documents and Recommend Retrieval Strategy

**Purpose:** Profile project source files and recommend a retrieval strategy before any indexing
decision. This prompt is purely read-only. No Qdrant collections are created or written to.

**Codex-ready:** yes — all steps are shell commands or file reads.

**Run from:** project root (e.g. `/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability`)

**Prerequisite:** Prompt 02 (verify rag-tools readiness) must be complete.

---

## Context

`rag-tools` profiles source files before any retrieval route is chosen. The profile captures:

- file type and size
- heading count, heading levels, section IDs
- table count
- whether amounts, dates, definitions, cross-references are present
- `document_class` — the classification used by `strategy_selector`
- `recommended_retrieval_modes` — ordered list of preferred modes

A `retrieval-strategy.yaml` is then created (or updated) to record the chosen route per document.

**Output of this prompt: `RETRIEVAL_STRATEGY_RECOMMENDED` or `RETRIEVAL_STRATEGY_PARTIAL`.**

---

## Step 1 — Identify candidate source files

List the files in the project that are candidates for retrieval (docs, references, rate cards, etc.).

```bash
# Run from project root
find . -type f \( -name "*.md" -o -name "*.txt" -o -name "*.csv" -o -name "*.yaml" -o -name "*.yml" \) \
  | grep -v ".git\|.venv\|node_modules\|__pycache__\|rag/" \
  | sort
```

Record the candidate list. Do not include:
- Raw communications (email, Teams transcripts, Slack exports)
- Files marked `contains_sensitive_data: true` by profiler
- Transient runtime files

---

## Step 2 — Run profile-file on each candidate

For each candidate, run:

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin
$VENV/rag-tools profile-file <path/to/file>
```

Record the JSON output. Key fields to capture per file:

| Field | Why it matters |
|---|---|
| `document_class` | Drives strategy selection |
| `has_headings` / `has_section_ids` | Enables structured/section lookup |
| `has_tables` | Enables table-aware lookup |
| `has_amounts` / `has_dates` | Signals exact-fact retrieval needs |
| `contains_sensitive_data` | Blocks indexing |
| `recommended_retrieval_modes` | Direct output from profiler |
| `index_allowed` | Always `false` at profile time; only set `true` after strategy confirms suitable |

Alternatively, profile the whole project at once:

```bash
$VENV/rag-tools profile-project .
```

---

## Step 3 — Run recommend-strategy on each candidate

```bash
$VENV/rag-tools recommend-strategy <path/to/file>
```

This combines `profile-file` output with `strategy_selector` to produce:

- `primary` retrieval mode
- `secondary` retrieval mode
- `fallback` retrieval mode
- `rag_suitability`: `suitable` | `partially_suitable` | `not_suitable`
- `reason`
- `risks`
- `required_tools`

Record the strategy output per file.

---

## Step 4 — Create project-local output files

Create the `rag/` directory inside the project root if it does not exist:

```bash
mkdir -p rag/source-profiles
```

### 4a — Save individual source profiles

For each profiled file, save the JSON output as YAML to:

```
rag/source-profiles/<document_id>.yaml
```

Copy the template from `skill-project-wiki-rag-bridge/templates/source-profile.yaml` as a
starting point, then fill in all fields from `profile-file` output.

### 4b — Create or update document-inventory.yaml

Create `rag/document-inventory.yaml`:

```yaml
version: 1
project_id: "<project-id>"
generated: "<YYYY-MM-DD>"

documents:
  - document_id: "<stem>"
    path: "<relative-path>"
    document_class: "<class>"
    has_headings: <bool>
    has_tables: <bool>
    has_section_ids: <bool>
    contains_sensitive_data: <bool>
    recommended_retrieval_modes:
      - "<mode>"
    index_allowed: false
    profile_status: DOCUMENT_PROFILE_COMPLETE
```

Default `index_allowed: false` for every document. Do not set `true` here — that is done in
`retrieval-strategy.yaml` only after benchmark and explicit approval.

### 4c — Create or update retrieval-strategy.yaml

Copy the template from `skill-project-wiki-rag-bridge/templates/retrieval-strategy.yaml`.
Fill in one entry per document using the `recommend-strategy` output.

Key rules:

- `rag_suitability` comes directly from `recommend-strategy` output — do not invent it.
- `index_allowed: false` by default.
- `benchmark_required: true` for any document with `rag_suitability: partially_suitable` or
  documents that are structured/tabular.
- `reason` must explain why the route was chosen.

---

## Step 5 — Classify each document and flag edge cases

For each document, apply the classification below and record in `retrieval-strategy.yaml`:

| Class | Primary route | RAG suitability |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` | `partially_suitable` |
| `legal_contract_or_terms` | `section_clause_lookup` | `partially_suitable` |
| `financial_rate_card` | `table_aware_lookup` | `partially_suitable` |
| `invoice_or_billing_report` | `table_aware_lookup` | `not_suitable` (usually) |
| `operational_runbook` | `heading_aware_lookup` | `partially_suitable` |
| `policy_document` | `section_clause_lookup` | `partially_suitable` |
| `meeting_notes` | `keyword_lookup` | `not_suitable` — do not index |
| `knowledge_article` | `vector_rag` | `suitable` |
| `source_code_docs` | `direct_structured_lookup` | `not_suitable` |
| `unstructured_pdf` | `extraction_required` | `not_suitable` — extraction needed first |
| `scanned_pdf` | `extraction_required` | `not_suitable` — OCR needed first |
| `tabular_dataset` | `table_aware_lookup` | `not_suitable` for RAG |
| `mixed_content` | `hybrid_direct_first` | `partially_suitable` |
| `unknown` | investigate manually | `not_suitable` until classified |

---

## Step 6 — Review and approve

Before saving `retrieval-strategy.yaml`, verify:

- [ ] Every candidate document has a `document_class`
- [ ] Every `rag_suitability: not_suitable` document has `index_allowed: false`
- [ ] Every `rag_suitability: partially_suitable` document has `benchmark_required: true`
- [ ] Meeting notes, raw comms, sensitive files are excluded
- [ ] No document has `index_allowed: true` at this stage

---

## Output format

At the end, output a strategy summary table:

```
RETRIEVAL STRATEGY SUMMARY
==========================
Project: <name>
Date: <YYYY-MM-DD>

Document                 | Class                        | Primary route            | RAG suitability    | Benchmark needed
<document>               | <class>                      | <mode>                   | <suitability>      | yes/no

Files created:
  rag/document-inventory.yaml           — full document inventory
  rag/retrieval-strategy.yaml           — per-document strategy routing
  rag/source-profiles/<id>.yaml         — per-file profiler output

Status: RETRIEVAL_STRATEGY_RECOMMENDED | RETRIEVAL_STRATEGY_PARTIAL | RETRIEVAL_STRATEGY_NOT_READY

Next step:
  If any document has benchmark_required: true → run prompt 02c
  Otherwise → proceed to prompt 05 (index wiki domain) with strategy in hand
```

---

## Safety rules

- Do not index anything in this prompt.
- Do not create Qdrant collections.
- Do not set `index_allowed: true` in this prompt.
- Do not use `rag_suitability: suitable` for structured/tabular/exact-fact documents unless the
  profiler explicitly outputs it.
- If `contains_sensitive_data: true`, set `index_allowed: false` and add a note — do not override.
