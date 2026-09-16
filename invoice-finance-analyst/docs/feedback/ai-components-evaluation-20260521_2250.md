# AI Components for Invoice Finance Analyst

## Contents

- [Part 1: LangChain — Worth It or Not?](#part-1-langchain-worth-it-or-not)
  - [Where LangChain Could Help (Phase 4 Only)](#where-langchain-could-help-phase-4-only)
    - [1. Structured Output — The Biggest Win](#1-structured-output-the-biggest-win)
    - [2. Multi-Step Reasoning Chains](#2-multi-step-reasoning-chains)
    - [3. LangSmith for Observability](#3-langsmith-for-observability)
    - [4. Selective Context Retrieval](#4-selective-context-retrieval)
  - [Where LangChain Would Be a Mistake](#where-langchain-would-be-a-mistake)
  - [Verdict on LangChain](#verdict-on-langchain)
- [Part 2: If Not LangChain, What Else?](#part-2-if-not-langchain-what-else)
  - [1. Instructor — Structured Output](#1-instructor-structured-output)
  - [2. OpenLineage or Self-Contained lineage.json — Pipeline Observability](#2-openlineage-or-self-contained-lineagejson-pipeline-observability)
  - [3. Guardrails or Custom Post-Processing — Output Safety](#3-guardrails-or-custom-post-processing-output-safety)
  - [4. MLflow or run_history.parquet — Run Tracking](#4-mlflow-or-run_historyparquet-run-tracking)
  - [5. Embedding-Based Similarity — Cross-Run Exception Matching](#5-embedding-based-similarity-cross-run-exception-matching)
- [Pragmatic Recommendations](#pragmatic-recommendations)
- [Key Principle](#key-principle)

---

Status: design exploration  
Created: 2026-05-21 22:50 Australia/Melbourne  
Scope: Evaluation of AI frameworks and components for enhancing the `internal-invoice-analysis` skill  
Topics: LangChain suitability, alternative AI components, pragmatic recommendations

---

## Part 1: LangChain — Worth It or Not?

The honest answer: **Phases 1–3 don't need LangChain at all.** They are deterministic pandas joins, rate-card math, and trend calculations. Wrapping `pd.merge()` or `df.sort_values().drop_duplicates()` in a LangChain abstraction adds complexity with zero benefit.

### Where LangChain Could Help (Phase 4 Only)

Current Phase 4 is a raw OpenAI-compatible API call: build a string prompt → send it → get markdown back. That's fine for a first pass. The places LangChain would meaningfully improve this:

#### 1. Structured Output — The Biggest Win

The Evidence Rule says every statement must cite `[table | metric | value]`, but right now it's only a prompt instruction. The LLM can ignore it. LangChain's `PydanticOutputParser` or `.with_structured_output()` could enforce a typed schema:

```python
class CitedFinding(BaseModel):
    table: str          # must match a known table name
    metric: str         # must match a known column
    value: str          # the actual value
    statement: str      # the narrative

class AnalystReport(BaseModel):
    executive_summary: str
    calculated_findings: list[CitedFinding]
    data_gaps: list[str]
    confidence: str      # must be 'high' | 'medium' | 'low'
```

This turns the Evidence Rule from a prompt hope into a compile-time constraint. If the model hallucinates a table name that doesn't exist, the parser rejects it. For a finance tool, that's exactly the right level of enforcement.

#### 2. Multi-Step Reasoning Chains

Currently Phase 4 is a one-shot: "here are all 22 tables, write a report." A chain could break this into focused stages:

```
Step 1: Analyze exception tables → output: prioritized exception list
Step 2: Cross-reference with rate-card/margin data → output: root-cause classifications
Step 3: Draft findings with citations → output: validated cited findings
Step 4: Compile final report → output: structured AnalystReport
```

Each step gets only the relevant context (smaller prompts, lower token cost) and passes validated intermediate data to the next step.

#### 3. LangSmith for Observability

For a finance tool, you need to answer "why did the analyst say X?" LangSmith gives you exact prompt/response pairs per run, token counts, latency per step, and regression tracking across model versions. Your current setup is a black box — prompt goes in, markdown comes out.

#### 4. Selective Context Retrieval

Instead of the `_select_context_tables()` stub passing everything, LangChain's document retrieval patterns could dynamically choose which tables and rows the LLM sees. However, a simple priority list (like the gap review recommends) achieves 90% of this without LangChain.

### Where LangChain Would Be a Mistake

| Pattern | Why It's Wrong for This Project |
|---|---|
| **Agent loops** — letting the LLM decide what to analyse next | Finance needs deterministic, repeatable analysis. An agent that decides "hmm, I'll look at customer X first" produces different results each run. |
| **Tool-using agent** — LLM calls tools to fetch data | All data is already in parquet files. Adding tool calls adds latency and failure modes. |
| **Replacing Phase 1–3 logic** | Deterministic pandas > probabilistic LLM for joins and math. No contest. |
| **Conversation memory** | Phase 4 is a one-shot report generator, not a chat interface. Memory adds drag with no benefit. |
| **LangChain as a Prompt Manager** | Prompts already live in source control alongside the code. That's better than LangChain's prompt template system. |

### Verdict on LangChain

**Add it in one place only:** replace the raw OpenAI API call with `.with_structured_output()` on the Phase 4 analyst report. This gives you enforceable Evidence Rule, validated pydantic output compatible with your parquet pipeline, and LangSmith tracing.

**Skip chains and agent patterns** unless the one-shot prompt fundamentally can't produce good results. Chains add latency and debugging surface — add them only when you have evidence the simple approach fails.

---

## Part 2: If Not LangChain, What Else?

There is a whole ecosystem of purpose-built tools that solve specific problems better than a general-purpose framework:

### 1. Instructor — Structured Output

The strongest single recommendation. A lightweight pydantic wrapper around any OpenAI-compatible API that enforces structured response schemas.

```python
from pydantic import BaseModel
from instructor import from_openai
from openai import OpenAI

client = from_openai(OpenAI(
    base_url="https://api.deepseek.com",
    api_key="sk-..."
))

class EvidenceFinding(BaseModel):
    table: str
    metric: str
    value: str
    statement: str

report = client.chat.completions.create(
    model="deepseek-chat",
    response_model=EvidenceFinding,
    messages=[...]
)
```

**Why it's better than LangChain's equivalent:**
- One dependency vs LangChain's 40+ transitive deps
- Same code works with existing provider-agnostic pattern (OpenAI, DeepSeek, Ollama — just swap base_url)
- Returns a validated pydantic model you can write directly to parquet
- Retries, validation, and streaming work out of the box

**What it replaces:** 90% of the Phase 4 value LangChain would provide — enforced Evidence Rule, typed output, no hallucinated table names.

### 2. OpenLineage or Self-Contained lineage.json — Pipeline Observability

The current pipeline runs five scripts serially with no shared run ID, no lineage, and no guarantee that Phase 3 used the same data as Phase 2. OpenLineage is an open standard for data lineage.

**Lighter alternative:** A self-contained `lineage.json` per run. Each phase appends to it:

```json
{
  "run_id": "abc-123",
  "phases": [
    {"name": "load_inputs", "started": "T1", "completed": "T2",
     "inputs": ["invoice.csv"], "outputs": ["db/invoice.parquet"]},
    {"name": "reconciliation", "started": "T3", "completed": "T4",
     "inputs": ["db/invoice.parquet", "db/sales_billing.parquet"],
     "outputs": ["db/matched_lines.parquet", ...]}
  ]
}
```

**Why:** Zero extra dependencies, answers "what produced what" for audit trails, and each script already has the metadata needed to populate it.

### 3. Guardrails or Custom Post-Processing — Output Safety

The Evidence Rule is currently just a prompt instruction. NVIDIA NeMo Guardrails lets you define programmatic guardrails:

```python
rails:
  input:
    flows:
      - check for external data requests
  output:
    flows:
      - validate evidence citations
      - check for invented numbers
      - check for accounting sign-off language
```

**Lighter alternative:** A 50-line post-processing function that regex-parses markdown output and fails if:
- Citations reference unknown table names
- Dollar amounts don't match any calculated output
- Prohibited phrases ("audited", "final", "GAAP-compliant") appear

No extra dependency, runs in milliseconds.

### 4. MLflow or run_history.parquet — Run Tracking

Every monthly pipeline run is an "experiment" in MLflow terms. It already captures run_id, timestamps, source hashes, and row counts.

```python
with mlflow.start_run(run_name="2026-05-invoice-analysis"):
    mlflow.log_params({"invoice_file": "invoice_may.csv", ...})
    mlflow.log_metrics({"matched_count": 142, "amount_mismatch_count": 3, ...})
    mlflow.log_artifact("output/phase4_abc123/analyst_report.md")
```

**Lighter alternative:** A `run_history.parquet` appended by existing scripts. Each run writes one row with all metrics `run_summary` already captures. A 10-line pandas query replaces the MLflow UI.

### 5. Embedding-Based Similarity — Cross-Run Exception Matching

Phase 2/3 detect exceptions per run but can't say "this mismatch looks like the same issue from last month." Sentence transformers are a single-package solution:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")  # 80MB, CPU
this_embeddings = model.encode(["LOC000003: 108% usage spike", ...])
last_embeddings = model.encode(["LOC000003: 95% usage spike", ...])
similarity = np.dot(this_embeddings, last_embeddings.T)
```

**Lighter alternative:** Simple string matching on `supplier_service_id`. If the same ID had an exception last month, tag it as `recurring_exception`. No AI needed — just a join.

---

## Pragmatic Recommendations

| Component | What to Use | Lines of Code | Why It Wins |
|---|---|---|---|
| Structured output | **Instructor** | +1 import, +10 lines | Enforced Evidence Rule, validated pydantic, compatible with existing provider setup |
| Pipeline audit trail | **Self-contained `lineage.json`** | ~15 lines across 5 scripts | Zero deps, finance-appropriate traceability |
| Output safety | **Custom 50-line validator** | +1 script | Catches hallucinations and prohibited language without framework |
| Cross-run trending | **`run_history.parquet`** | ~20 lines per script | Dashboard-ready from what you already log |
| Exception dedup across months | **Simple `supplier_service_id` join** | ~5 lines | Recurring-exception tagging costs nothing, adds massive reporting value |

**Total new dependencies: 1** (Instructor — `pip install instructor`).  
**Total new code: ~100 lines spread across existing scripts.**

None of these require LangChain, an agent framework, a vector database, or any infrastructure change. They layer onto existing Phase 1–4 scripts as optional enhancements, not rewrites.

---

## Key Principle

The skill's core strength is that all financial numbers come from deterministic Python/pandas, not the LLM. Every AI component suggested here preserves that boundary — they validate, annotate, and trace the LLM output; they don't let the LLM touch the numbers.
