# Scripts — Invoice Finance Analyst Pipeline

Pipeline scripts run in the order listed below. Each script is standalone but builds on the outputs of prior stages. Validation is read-only; loader and analysis scripts write to `db/` (parquet) or `output/` (markdown). Source CSVs in `examples/` are never modified.

## Contents

- [Prerequisites](#prerequisites)
- [Pipeline run order](#pipeline-run-order)
- [Script catalog](#script-catalog)
- [Test runner](#test-runner)
- [Safety labels](#safety-labels)

---

## Prerequisites

Preferred: use `just` to run tasks (see [justfile](../justfile)):

```bash
just --list          # see all available tasks
just test            # run all 219 tests
just pipeline        # deterministic pipeline: validate + load examples + Phase 1B/2/3
just analyse         # optional Phase 4 LLM analyst report; requires credentials/provider config
```

Manual venv activation (if running scripts directly):

```bash
source /Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/activate
```

Python version: **3.14.4** (`/opt/homebrew/opt/python@3.14/bin/python3.14`)

For `llm_analyst.py`: set `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL` for non-OpenAI providers).

---

## Pipeline run order

```
validate_inputs.py       ← schema check (read-only, no output files)
load_inputs.py           ← CSV → db/*.parquet
invoice_analysis_skeleton.py  ← reconciliation → db/*.parquet + output/<run_id>/*.md
rate_card_analysis.py    ← rate variance + margin → db/*.parquet
trend_analysis.py        ← MoM trend → db/*.parquet  [optional: requires prior period data]
llm_analyst.py           ← LLM analyst report → output/phase4_<run_id>/analyst_report.md
```

---

## Script catalog

### `validate_inputs.py`

| Field | Value |
|---|---|
| Phase | 1A |
| Safety | `review-required` — prints validation report; no file writes |
| Inputs | One CSV path and mapping YAML per invocation |
| Outputs | Stdout only (row counts, column names, null counts, duplicate counts, type profiling) |
| Side effects | None — read-only |
| Idempotent | Yes |

**Usage:**

```bash
python scripts/validate_inputs.py --csv examples/supplier_invoice_sample.csv --mapping examples/mapping_supplier_invoice.yaml
python scripts/validate_inputs.py --csv examples/sales_billing_sample.csv --mapping examples/mapping_sales_billing.yaml
python scripts/validate_inputs.py --csv examples/rate_card_sample.csv --mapping examples/mapping_rate_card.yaml
python scripts/validate_inputs.py --csv examples/service_map_sample.csv --mapping examples/mapping_service_map.yaml
```

**Purpose:** Profile input CSVs before loading. Detects schema issues, column mismatches, null/duplicate problems. Does not modify any file. Run first on any new input CSV set.

---

### `load_inputs.py`

| Field | Value |
|---|---|
| Phase | 1B |
| Safety | `modifies-files` — writes to `db/` |
| Inputs | One CSV path, one mapping YAML, and one parquet output name per invocation |
| Outputs | One named parquet per invocation, e.g. `db/invoice.parquet`, `db/sales_billing.parquet`, `db/rate_card.parquet`, `db/service_map.parquet`, `db/prior_invoice.parquet`, or `db/prior_sales_billing.parquet` |
| Side effects | Writes parquet files and archives prior run copies with timestamp suffix |
| Idempotent | Yes (overwrites + archives) |

**Usage:**

```bash
python scripts/load_inputs.py --csv examples/supplier_invoice_sample.csv --mapping examples/mapping_supplier_invoice.yaml --name invoice
python scripts/load_inputs.py --csv examples/sales_billing_sample.csv --mapping examples/mapping_sales_billing.yaml --name sales_billing
python scripts/load_inputs.py --csv examples/rate_card_sample.csv --mapping examples/mapping_rate_card.yaml --name rate_card
python scripts/load_inputs.py --csv examples/service_map_sample.csv --mapping examples/mapping_service_map.yaml --name service_map
python scripts/load_inputs.py --csv examples/prior_invoice_sample.csv --mapping examples/mapping_supplier_invoice.yaml --name prior_invoice
python scripts/load_inputs.py --csv examples/prior_sales_billing_sample.csv --mapping examples/mapping_sales_billing.yaml --name prior_sales_billing
```

**Purpose:** Reads raw CSVs, applies column mapping (via `mapping_*.yaml`), normalizes to canonical schema, and writes canonical parquet. Archives prior parquet with `_YYYYMMDD_HHMM` suffix for audit trail.

---

### `invoice_analysis_skeleton.py`

| Field | Value |
|---|---|
| Phase | 1B |
| Safety | `modifies-files` — writes to `db/` and `output/` |
| Inputs | `db/invoice.parquet`, `db/sales_billing.parquet` (from `load_inputs.py`) |
| Outputs | 9 parquet tables in `db/`; per-table markdown in `output/<run_id>/` |
| Side effects | Creates `output/<run_id>/` folder; writes run summary |
| Idempotent | Yes (new run ID each time) |

**Output tables:**

| Table | Description |
|---|---|
| `reconciliation_summary.parquet` | Totals: matched, invoice_no_sales, sales_no_invoice, amount_mismatches |
| `matched_lines.parquet` | Invoice lines matched to sales lines |
| `invoice_no_sales.parquet` | Invoice lines with no matching sales record |
| `sales_no_invoice.parquet` | Sales lines with no matching invoice record |
| `amount_mismatches.parquet` | Matched lines where invoice ≠ sales amount |
| `data_quality_issues.parquet` | Validation failures and anomalies flagged during reconciliation |
| `run_summary.parquet` | Run metadata, file hashes, timestamp, row counts |
| `assumptions.parquet` | All assumptions recorded during this run |
| `source_file_inventory.parquet` | Hashes and metadata for all loaded source files |

**Usage:**

```bash
python scripts/invoice_analysis_skeleton.py
```

---

### `rate_card_analysis.py`

| Field | Value |
|---|---|
| Phase | 2 |
| Safety | `modifies-files` — writes to `db/` and `output/` |
| Inputs | `db/matched_lines.parquet`, `db/rate_card.parquet` |
| Outputs | 6 parquet tables in `db/`; per-table markdown in `output/phase2_<run_id>/` |
| Side effects | Writes to `db/` and creates `output/phase2_<run_id>/` folder |
| Idempotent | Yes |

**Output tables:**

| Table | Description |
|---|---|
| `rate_variances.parquet` | Actual vs expected rate differences per service line |
| `rate_card_mismatches.parquet` | Lines where charged rate does not match rate card |
| `margin_by_customer.parquet` | Gross margin (revenue − cost) grouped by customer |
| `margin_by_service_type.parquet` | Gross margin grouped by service type |
| `low_margin_exceptions.parquet` | Lines where margin < 5% threshold |
| `phase2_assumptions.parquet` | Assumptions recorded during rate card analysis |

**Usage:**

```bash
python scripts/rate_card_analysis.py
```

---

### `trend_analysis.py`

| Field | Value |
|---|---|
| Phase | 3 |
| Safety | `modifies-files` — writes to `db/` and `output/` |
| Inputs | `db/invoice.parquet`, `db/prior_invoice.parquet`, `db/sales_billing.parquet`, `db/prior_sales_billing.parquet`, `db/matched_lines.parquet` |
| Outputs | 7 parquet tables in `db/`; per-table markdown in `output/phase3_<run_id>/` |
| Side effects | Writes to `db/` and creates `output/phase3_<run_id>/` folder |
| Idempotent | Yes |
| Notes | Optional — skip if no prior period data is available |

**Output tables:**

| Table | Description |
|---|---|
| `mom_variance.parquet` | Month-over-month cost/revenue change per service line |
| `new_services.parquet` | Services present in current period but absent in prior |
| `removed_services.parquet` | Services present in prior period but absent now |
| `usage_spikes.parquet` | Lines with usage > 2× prior period (spike threshold) |
| `recurring_changes.parquet` | Lines with recurring delta ≥ 5% MoM (recurring threshold) |
| `margin_movement.parquet` | Margin change per service from prior to current period |
| `phase3_assumptions.parquet` | Assumptions recorded during trend analysis |

**Usage:**

```bash
python scripts/trend_analysis.py
```

---

### `llm_analyst.py`

| Field | Value |
|---|---|
| Phase | 4 |
| Safety | `modifies-files`, `requires-credentials`, `long-running` |
| Inputs | All parquet tables in `db/`; LLM API key via `OPENAI_API_KEY` env var |
| Outputs | `output/phase4_<run_id>/analyst_report.md` — 9-section LLM analyst report |
| Side effects | Calls LLM API (billable); writes report to `output/` |
| Idempotent | Yes (new run ID per call) |
| Notes | Provider-agnostic: OpenAI, DeepSeek, Groq, Ollama (set `OPENAI_BASE_URL`) |

**Usage (OpenAI):**

```bash
OPENAI_API_KEY=sk-... python scripts/llm_analyst.py
```

**Usage (Ollama local):**

```bash
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama \
  python scripts/llm_analyst.py --model llama3.1:8b
```

**Usage (DeepSeek):**

```bash
OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=sk-... \
  python scripts/llm_analyst.py --model deepseek-chat
```

**Phase 4 status:** Runnable. Finance control checklist, citation validator, and deterministic severity scoring are pending (Phase 4b–4c). Do not treat the analyst report as finance-control complete until those phases are implemented.

---

## Test runner

All 219 tests run with:

```bash
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/
```

Individual test modules:

```bash
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/test_validate_inputs.py      # 33 tests — Phase 1A
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/test_reconciliation.py       # 41 tests — Phase 1B
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/test_rate_card_analysis.py   # 47 tests — Phase 2
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/test_trend_analysis.py       # 48 tests — Phase 3
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/test_llm_analyst.py          # 50 tests — Phase 4 (mocked API, offline)
```

---

## Safety labels

| Label | Meaning |
|---|---|
| `safe` | No file writes, no external calls, fully reversible |
| `review-required` | Check inputs/outputs before running on real data |
| `modifies-files` | Writes to `db/` or `output/`; prior parquets archived, not deleted |
| `requires-credentials` | Needs `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL`) |
| `long-running` | May take seconds to minutes depending on data size and LLM provider latency |
| `unknown` | Not yet catalogued — treat as unsafe until inspected |

All scripts in this pipeline are `modifies-files`. `llm_analyst.py` additionally requires credentials and is long-running.

**Real-data gate:** Do not run any script against production invoice data until Phase 4b.1 (service-map reconciliation) and Phase 4b.2 (control totals) are complete.
