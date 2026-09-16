# Finance-Domain AI Tools for Invoice Finance Analyst

## Contents

- [Overview](#overview)
- [1. Great Expectations — Finance Data Quality Framework](#1-great-expectations-finance-data-quality-framework)
  - [How It Works](#how-it-works)
  - [Why for This Skill](#why-for-this-skill)
  - [Trade-offs](#trade-offs)
- [2. FinGPT / FinBERT — Finance-Specific Language Classification](#2-fingpt-finbert-finance-specific-language-classification)
  - [How It Would Fit](#how-it-would-fit)
  - [Concrete Applications in the Pipeline](#concrete-applications-in-the-pipeline)
  - [Trade-offs](#trade-offs-1)
- [3. Invoice2data — PDF Invoice Extraction](#3-invoice2data-pdf-invoice-extraction)
  - [How It Works](#how-it-works-1)
  - [Why for the Ecosystem](#why-for-the-ecosystem)
  - [Limitations](#limitations)
- [4. Anomaly Detection — Beyond Static Thresholds](#4-anomaly-detection-beyond-static-thresholds)
  - [How It Works](#how-it-works-2)
  - [Why Finance-Specific](#why-finance-specific)
  - [Trade-offs](#trade-offs-2)
- [5. Daft — Auditable DataFrame Engine](#5-daft-auditable-dataframe-engine)
  - [How It Works](#how-it-works-3)
  - [Why Finance-Specific](#why-finance-specific-1)
- [Summary — What to Add and When](#summary-what-to-add-and-when)
  - [Recommended Starting Point](#recommended-starting-point)

---

Status: design exploration  
Created: 2026-05-21 22:50 Australia/Melbourne  
Scope: Evaluation of finance-domain-specific AI tools for enhancing the `internal-invoice-analysis` skill  
Focus: Purpose-built finance tools, not general-purpose frameworks

---

## Overview

This document evaluates AI and data tools built specifically for the finance domain — invoice processing, data quality, classification, and anomaly detection. These are not general-purpose ML frameworks; they address concrete finance problems that the current skill either handles with heuristics or doesn't handle at all.

---

## 1. Great Expectations — Finance Data Quality Framework

Your current `data_quality_issues` table is already a mini implementation of this. **Great Expectations** is the mature open-source standard for data quality in finance/accounting pipelines.

### How It Works

```yaml
# expectations/supplier_invoice_expectations.json
{
  "expectations": [
    {"expectation_type": "expect_column_values_to_not_be_null",
     "kwargs": {"column": "supplier_service_id"}},
    {"expectation_type": "expect_column_values_to_be_between",
     "kwargs": {"column": "amount_ex_tax", "min_value": 0}},
    {"expectation_type": "expect_table_row_count_to_be_between",
     "kwargs": {"min_value": 1, "max_value": 50000}},
    {"expectation_type": "expect_column_values_to_be_unique",
     "kwargs": {"column": ["supplier_service_id", "billing_period_start"]}},
    {"expectation_type": "expect_column_values_to_match_regex",
     "kwargs": {"column": "billing_period_start", "regex": "^\\d{4}-\\d{2}-\\d{2}$"}},
    {"expectation_type": "expect_column_sum_to_be_between",
     "kwargs": {"column": "amount_ex_tax", "min_value": 1, "max_value": 100000000}},
  ]
}
```

### Why for This Skill

- **Replaces ad-hoc validation** — your hand-written if-statements in `validate_inputs.py` become a standardised, documented expectation suite
- **Finance-readable** — stakeholders can read the expectation file without understanding Python
- **HTML reports** — produces data quality reports you can email or attach to a run
- **Pipeline gating** — can fail the pipeline on critical failures (null supplier_service_id) vs warn on advisory ones (low row count)
- **Phase-appropriate** — expectations can be extended as the skill adds new source types (customer rate card, product master, payments)

### Trade-offs

- Another dependency and initial setup overhead
- Expectations need to be maintained as source data formats change
- Overkill if `validate_inputs.py` already covers everything you need

| Aspect | Detail |
|---|---|
| **Phase** | 1A |
| **When** | Now — directly improves the existing validation layer |
| **Replaces** | Hand-written validation if-statements in `validate_inputs.py` |
| **Install** | `pip install great_expectations` |

---

## 2. FinGPT / FinBERT — Finance-Specific Language Classification

**FinGPT** (by AI4Finance) is an open-source LLM fine-tuned on financial text. Not for market data — for understanding finance-specific language: invoice descriptions, contract terms, service categories, charge types.

Your current `validate_inputs.py` uses heuristic patterns for column mapping. A FinBERT-based classification layer could replace those heuristics with semantic understanding.

### How It Would Fit

**Charge classification (Gap 13):**

```python
from finbert_models import FinBERTClassifier

classifier = FinBERTClassifier()
charge_type = classifier.predict(
    "Monthly recurring charge for 10Mbps dedicated internet access - LOC000001"
)
# → "recurring_usage" with 0.94 confidence
```

**Service type mapping (Gap 2):**

When a supplier description doesn't match canonical service_type, FinBERT can suggest the closest match from your known service taxonomy — replacing the current assumption that `our_service_id_equals_supplier_service_id = True`.

**Root cause grouping (Phase 4):**

Group exceptions by semantic similarity ("these 3 mismatches are all MRC disputes") rather than just by service ID, producing more useful findings sections.

### Concrete Applications in the Pipeline

| Current approach | FinGPT-enhanced approach |
|---|---|
| Negative amount → flag as possible credit | Description + amount → classify as `credit`, `reversal`, `adjustment`, or `error` |
| Service type must match exactly | Supplier description → suggested service type with confidence |
| Exceptions grouped by supplier_service_id | Exceptions grouped by root cause (e.g. "rate dispute", "ceased service", "contract renegotiation") |

### Trade-offs

- 110M–7B parameter models — small enough for CPU but adds latency
- Needs a labelled dev set for your specific supplier descriptions to calibrate confidence thresholds
- Heuristic fallback when confidence is low — never let the model override a deterministic check

| Aspect | Detail |
|---|---|
| **Phase** | 1B (classification) / Phase 4 (root-cause grouping) |
| **When** | After Gaps 2 and 13 — service map and charge classification |
| **Replaces** | Heuristic charge-type rules, exact service-type matching |
| **Install** | `pip install transformers torch` + model weights (~400MB) |

---

## 3. Invoice2data — PDF Invoice Extraction

Purpose-built open-source tool for extracting structured fields from invoice PDFs and scanned documents. Uses template matching with OCR fallback.

### How It Works

```python
import invoice2data

result = invoice2data.extract_data(
    "supplier_invoice_202605.pdf",
    templates="templates/",
    input_module="pdf",
)
# → {
#   "amount": 1234.56,
#   "date": "2026-05-01",
#   "invoice_number": "INV-2026-789",
#   "description": "Managed internet service - LOC000001",
#   "supplier_name": "Vocus",
# }
```

### Why for the Ecosystem

Your APN suppliers may send PDF invoices. This bridges the gap between "we got a PDF in email" and "we have a structured CSV that matches the sales billing data." The extracted fields could feed directly into `load_inputs.py` as if they came from a CSV.

### Limitations

- Template-based — needs one template per supplier format
- Not relevant for CSV-only workflows
- No fuzzy matching across templates — one format change breaks extraction until the template is updated

| Aspect | Detail |
|---|---|
| **Phase** | Input layer (pre-1A) |
| **When** | Only when PDF invoices enter the workflow |
| **Replaces** | Manual data entry from PDF invoices |
| **Install** | `pip install invoice2data` |

---

## 4. Anomaly Detection — Beyond Static Thresholds

Your current exception detection uses fixed thresholds (0.02 abs, 5% margin, 2x spike). These are correct for Phase 1 but have known blind spots:

- A $50 variance on a $10k line (0.5%) passes but might be suspicious in context
- A $2 variance on a $2.5k item (0.08%) is ignored but might repeat across 100 lines adding up to $200
- Thresholds don't adapt to supplier-specific patterns

### How It Works

```python
from sklearn.ensemble import IsolationForest

# Train on 3 months of reconciled data
model = IsolationForest(contamination=0.01)
model.fit(historical_features)  # amount, qty, unit_rate, days_in_period, supplier_id

# Score new invoice lines
new_invoice["anomaly_score"] = model.decision_function(new_invoice[feature_cols])
new_invoice["is_anomaly"] = model.predict(new_invoice[feature_cols]) == -1
```

**Alternative — TabPFN:** A foundation model for small-to-medium tabular data that learns what "normal" looks like for your specific suppliers with very few training examples.

### Why Finance-Specific

- Thresholds are static — supplier behaviour changes over time (renegotiations, new pricing models)
- A model learns *this supplier's* normal rather than global rules
- Catches compound issues — small individual variances that collectively are significant

### Trade-offs

- Needs 3–6 months of reconciled history to train effectively
- Over-sensitive initially; requires threshold calibration
- Can't replace deterministic checks (nulls, schema violations) — augments them

| Aspect | Detail |
|---|---|
| **Phase** | Phase 4 (post-reconciliation) |
| **When** | After 3+ months of reconciled history available |
| **Replaces** | Static threshold-based exception detection (partially) |
| **Install** | `pip install scikit-learn` or `pip install tabpfn` |

---

## 5. Daft — Auditable DataFrame Engine

Not an AI tool per se, but addresses a real finance need: **pipeline outputs must be auditable, deterministic, and handle larger-than-memory datasets**. Pandas works for fixtures but has known pain points for production finance:

- No lazy evaluation — you can't inspect the plan before execution
- All in-memory — a 500MB supplier export causes OOM
- No built-in lineage tracking

### How It Works

```python
import daft

df = daft.read_parquet("db/invoice.parquet")
df = df.join(
    daft.read_parquet("db/sales_billing.parquet"),
    on="supplier_service_id",
    how="outer",
)

# df.explain() prints the full query plan — auditable
# Can spill to disk for datasets larger than RAM
# Parallel execution across CPU cores without extra config
```

### Why Finance-Specific

Finance teams need to see *how* a number was produced. Daft's `.explain()` gives you a reproducible query plan. Pandas's internal execution is opaque by comparison — you can't prove it didn't silently drop rows or mis-join.

| Aspect | Detail |
|---|---|
| **Phase** | Engine (affects all script phases) |
| **When** | When pandas becomes the bottleneck (memory, auditability, or scale) |
| **Replaces** | pandas (partially or fully) |
| **Install** | `pip install daft` |

---

## Summary — What to Add and When

| Tool | Purpose | Phase | When | Dependencies |
|---|---|---|---|---|
| **Great Expectations** | Replace ad-hoc validation with documented, finance-readable data quality contracts | 1A | Now | `great_expectations` |
| **FinGPT / FinBERT** | Classify charge types from descriptions; suggest service-map matches | 1B / Phase 4 | After Gaps 2 and 13 | `transformers`, `torch` |
| **Invoice2data** | Extract structured data from PDF invoices (suppliers that don't send CSV) | Input layer | When PDF invoices enter workflow | `invoice2data` |
| **Anomaly Detection** | Adaptive anomaly detection beyond static thresholds | Phase 4 | After 3+ months reconciled history | `scikit-learn` or `tabpfn` |
| **Daft** | Auditable query plans, larger-than-memory data, parallel execution | Engine | When pandas becomes a bottleneck | `daft` |

### Recommended Starting Point

**Install `great_expectations` today** — it directly improves your existing data quality layer with a standard that finance people understand, replaces ad-hoc validation code, and produces reports you can share without explanation.

Everything else should be added when the specific problem appears:

- PDF invoices arrive → add `invoice2data`
- Service-map and charge classification implementation starts → evaluate `FinBERT`
- 3 months of reconciled data accumulated → evaluate anomaly detection
- Pandas becomes a bottleneck or auditability requirement arises → evaluate `Daft`
