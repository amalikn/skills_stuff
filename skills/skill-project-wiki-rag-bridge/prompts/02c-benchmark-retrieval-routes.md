# Prompt 02c — Benchmark Retrieval Routes

**Purpose:** Benchmark applicable retrieval modes against a representative query set, then choose
the default retrieval route for each document before any indexing decision. Read-only.

**Codex-ready:** yes — all steps are shell commands or file reads.

**Run from:** project root.

**Prerequisite:** Prompt 02b (`retrieval-strategy.yaml` must exist with `benchmark_required: true`
on at least one document).

---

## Context

Choosing a retrieval route without evidence is guesswork. The benchmark runs structured lookup,
section lookup, table lookup, and (optionally) vector RAG against a set of representative queries
and reports pass/fail, latency, context chars, citation metadata coverage, and false positives.

The benchmark output maps directly to a route recommendation label used in `retrieval-strategy.yaml`.

**Output of this prompt: `RETRIEVAL_BENCHMARK_PASSED`, `RETRIEVAL_BENCHMARK_PARTIAL`, or
`RETRIEVAL_BENCHMARK_FAILED`.**

---

## Step 1 — Identify documents requiring benchmark

From `rag/retrieval-strategy.yaml`, list every document where:

```yaml
benchmark_required: true
benchmark_status: not_run
```

These are the benchmark candidates. Benchmark only these — do not re-benchmark documents already
at `RETRIEVAL_BENCHMARK_PASSED`.

---

## Step 2 — Prepare benchmark query file

For each candidate document, create a benchmark query file at:

```
rag/benchmarks/queries/<document_id>-queries.yaml
```

Use `skill-project-wiki-rag-bridge/templates/benchmark-queries.yaml` as the starting template.

Rules for writing queries:

- Include at least 5 queries that test the document's actual content.
- Include queries for:
  - Exact fact extraction (amounts, dates, section references)
  - Table cell lookups (rate card values, period values)
  - Section navigation (find clause X, find heading Y)
  - Cross-section reasoning (only if vector RAG is being tested)
- For each query, populate `expected_source` with the expected `section_id` or `heading_contains`
  so the benchmark can score correctness.
- For rate-card / invoice documents, weight queries toward table lookups.
- For long structured reference documents, weight queries toward section/clause lookups.

---

## Step 3 — Run benchmark-file

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin

# Benchmark with default modes (structured + table):
$VENV/rag-tools benchmark-file <path/to/file> \
  --queries rag/benchmarks/queries/<document_id>-queries.yaml

# Benchmark with RAG mode if a collection exists (optional):
$VENV/rag-tools benchmark-file <path/to/file> \
  --queries rag/benchmarks/queries/<document_id>-queries.yaml \
  --modes structured,table,rag
```

The benchmark command is read-only. It does not index or write to Qdrant.

Note: `rag` mode in `--modes` will mark RAG results as skipped unless an active collection is
provided. The benchmark still reports `RAG_FIRST` or `HYBRID_*` labels when RAG results are
present.

---

## Step 4 — Interpret benchmark output

The benchmark returns a JSON object:

```json
{
  "source_file": "<path>",
  "enabled_modes": ["structured", "table"],
  "results": [
    {
      "query": "<query>",
      "mode": "structured",
      "pass": true,
      "latency_ms": 12.4,
      "context_chars": 820,
      "correct_section_found": true,
      "correct_expected_terms_found": true,
      "citation_metadata_present": true,
      "false_positive_notes": [],
      "fallback_needed": false,
      "evidence": [...]
    }
  ],
  "recommendation": "DIRECT_FIRST"
}
```

Route recommendation labels from the benchmark engine:

| Label | Meaning |
|---|---|
| `DIRECT_FIRST` | Structured lookup wins — use as primary |
| `TABLE_LOOKUP_FIRST` | Table lookup wins — use as primary |
| `HYBRID_DIRECT_FIRST` | Direct primary, RAG secondary |
| `HYBRID_RAG_FIRST` | RAG primary, direct fallback |
| `RAG_FIRST` | RAG outperforms direct modes |
| `NOT_READY_NEEDS_EXTRACTION` | PDF — extraction required before any lookup |
| `NOT_READY_NEEDS_MORE_INDEXED_CONTENT` | No mode passed — source needs rework or chunking |

---

## Step 5 — Save benchmark report

Save the benchmark JSON output as a report:

```
rag/benchmarks/retrieval-route-benchmark-<YYYYMMDD_hhmm>.md
```

Report format:

```markdown
# Retrieval Route Benchmark — <YYYYMMDD_hhmm>

Project: <name>
Date: <YYYY-MM-DD HH:MM>

## Per-Document Results

### <document_id>

Source: <path>
Recommendation: <LABEL>

| Query | Mode | Pass | Latency ms | Context chars | Section found | Terms found | Citation present |
|---|---|---|---|---|---|---|---|
| <query> | structured | yes/no | <ms> | <chars> | yes/no | yes/no | yes/no |
| <query> | table | yes/no | <ms> | <chars> | yes/no | yes/no | yes/no |

False positives: <notes or none>
Fallback needed: yes/no

Summary: <DIRECT_FIRST | TABLE_LOOKUP_FIRST | ...>

## Verdicts

| Document | Recommendation | Route update |
|---|---|---|
| <document> | <LABEL> | <primary>/<secondary>/<fallback> |

## Overall benchmark status: RETRIEVAL_BENCHMARK_PASSED | _PARTIAL | _FAILED
```

---

## Step 6 — Update retrieval-strategy.yaml

Based on benchmark verdicts, update `rag/retrieval-strategy.yaml` for each benchmarked document:

```yaml
documents:
  - document_id: "<id>"
    primary: "<updated from benchmark>"
    secondary: "<updated from benchmark>"
    fallback: "vector_rag"
    rag_suitability: "<confirmed or downgraded>"
    benchmark_required: true
    benchmark_status: passed   # or: partial | failed
    index_allowed: false        # still false unless strategy explicitly approves
    reason: "<benchmark label + evidence e.g. DIRECT_FIRST — 8/8 structured queries passed>"
```

Rules:

- If `recommendation: NOT_READY_NEEDS_EXTRACTION` → set `index_allowed: false`, document note
  says extraction required.
- If `recommendation: NOT_READY_NEEDS_MORE_INDEXED_CONTENT` → set `benchmark_status: failed`,
  investigate source quality.
- If `recommendation: RAG_FIRST` or `HYBRID_RAG_FIRST` → only then consider setting
  `index_allowed: true` (still requires explicit approval, not automatic).
- If `recommendation: DIRECT_FIRST` or `TABLE_LOOKUP_FIRST` → set `index_allowed: false`,
  no indexing needed.

---

## Step 7 — Output summary

```
RETRIEVAL BENCHMARK SUMMARY
============================
Project: <name>
Date: <YYYY-MM-DD>

Document                 | Recommendation          | Route selected                    | Index allowed
<document>               | DIRECT_FIRST            | direct_structured_lookup          | false
<document>               | TABLE_LOOKUP_FIRST      | table_aware_lookup                | false
<document>               | HYBRID_RAG_FIRST        | direct_structured_lookup + rag    | pending approval

Files updated:
  rag/retrieval-strategy.yaml                       — benchmark_status updated per document
  rag/benchmarks/retrieval-route-benchmark-<ts>.md  — full report

Overall status: RETRIEVAL_BENCHMARK_PASSED | RETRIEVAL_BENCHMARK_PARTIAL | RETRIEVAL_BENCHMARK_FAILED

Next step:
  DIRECT_FIRST / TABLE_LOOKUP_FIRST documents → no indexing required; use rag-tools lookups directly
  HYBRID_* / RAG_FIRST documents → get approval for index_allowed: true → proceed to prompt 08
  NOT_READY_* documents → resolve extraction/content issue before continuing
```

---

## Safety rules

- Do not index anything in this prompt.
- Do not create Qdrant collections.
- Do not set `index_allowed: true` automatically — benchmark result is a recommendation, not an
  automatic approval.
- Do not use `rag` mode in benchmark unless a real Qdrant collection exists.
- Do not skip benchmark for structured/tabular documents just because they are short.
- If a document fails benchmark with all modes, report `RETRIEVAL_BENCHMARK_FAILED` and stop —
  do not proceed to indexing.
