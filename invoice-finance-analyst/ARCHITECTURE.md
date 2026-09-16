# Architecture — Invoice Finance Analyst

## Contents

- [Overview](#overview)
- [Component map](#component-map)
- [Analysis layers (data / request flow)](#analysis-layers-data-request-flow)
- [Severity scoring model](#severity-scoring-model)
- [Primary output format](#primary-output-format)
- [Key design decisions](#key-design-decisions)
- [Invariants — do not change without understanding](#invariants-do-not-change-without-understanding)

---

## Overview

Multi-layer internal CSV invoice analysis system. Deterministic Python/pandas calculation engine produces structured outputs; the LLM layer interprets, classifies, and summarizes those outputs. All numeric conclusions must be traceable to a source file, calculated table, or declared assumption — never to LLM inference alone.

## Component map

| Component | Path | Phase | Status | Role |
|---|---|---|---|---|
| Skill instructions | `internal-invoice-analysis/SKILL.md` | 0+ | implemented | Defines workflow, hard rules, response format |
| Input validator | `scripts/validate_inputs.py` | 1A ✓ | implemented | Schema check, null counts, type profiling — read-only |
| CSV loader | `scripts/load_inputs.py` | 1B ✓ | implemented | CSV → canonical parquet, mapping translation, archive |
| Reconciliation engine | `scripts/invoice_analysis_skeleton.py` | 1B ✓ | implemented | Dedup, outer join, 9 output tables |
| Rate card analysis | `scripts/rate_card_analysis.py` | 2 ✓ | implemented | Rate variance, margin by customer/service, low-margin exceptions |
| Trend analysis | `scripts/trend_analysis.py` | 3 ✓ | implemented | MoM variance, new/removed services, usage spikes, recurring changes, margin movement |
| LLM analyst | `scripts/llm_analyst.py` | 4 ✓ | runnable — finance controls partial ★ | Provider-agnostic LLM commentary: executive summary, exception narrative, evidence table |
| Finance control checklist | `db/finance_control_checklist.parquet` | 4b | planned | Deterministic Python output; must precede LLM prompt claiming checklist |
| Citation validator | (Phase 4c) | 4c | planned | Post-generation Evidence Rule enforcement; fail-closed |
| JSON schema validator | (Phase 4c) | 4c | planned | 50-line custom validator; replaces Instructor |
| Data contract | `docs/data_contract.md` | 1A ✓ | implemented | Canonical column definitions for all 4 source types |
| Output schema | `docs/output_schema.md` | 1B–4 ✓ | implemented (4b/4c extension pending) | 22 parquet table definitions + analyst_report.md (Phase 4) |
| Analysis layers doc | `docs/analysis_layers.md` | backlog | planned | Explains each processing layer |
| Assumptions doc | `docs/assumptions_and_limits.md` | backlog | planned | Hard limits and disclosure rules |
| Templates | `templates/` | backlog | planned | Markdown report templates the agent fills after analysis |
| Examples | `examples/` | 1A+3 ✓ | implemented | Fixture CSVs: invoice, sales, rate_card, service_map, prior_invoice, prior_sales |
| Tests | `tests/` | 1A–4 ✓ | implemented | 219 tests (33+41+47+48+50) across 5 test modules |

★ LLM analyst runnable: finance_control_checklist.parquet, citation validator, and deterministic severity scoring not yet implemented (Phase 4b–4c).

## Analysis layers (data / request flow)

```
Input CSVs (read-only)
    │
    ▼
Layer 0 — Source Inventory
    File hashes, row counts, column counts, load timestamps
    │
    ▼
Layer 1 — Schema Validation
    Required columns, date parsing, numeric parsing,
    duplicate keys, negative value classification
    Output: schema_validation, data_quality_issues
    │
    ▼
Layer 2 — Normalization
    Canonical invoice fields, sales fields, rate-card fields
    Output: normalized_invoices, normalized_sales, normalized_rate_card, mapping_issues
    │
    ▼
Layer 3 — Invoice-to-Sales Reconciliation
    Match priority: exact service ID → service+period → customer+product+period → fuzzy → manual
    Exception categories: invoice_no_sales, sales_no_invoice, amount_mismatch,
    period_mismatch, duplicate_invoice_line, unmapped_service, ceased_service_still_charged
    Output: reconciliation_summary, matched_lines, exception tabs
    │
    ▼
Layer 4 — Rate-Card Validation
    Actual vs expected supplier cost; actual vs expected customer revenue
    Metrics: supplier_variance, revenue_variance, gross_margin, gross_margin_pct
    Output: rate_validation_summary, supplier_rate_variances, customer_rate_variances
    │
    ▼
Layer 5 — Profitability Analysis
    direct_margin = customer_revenue_ex_tax − supplier_cost_ex_tax
    Grouped by: customer, service ID, product/service type, supplier, period
    Exception categories: negative_margin, low_margin, margin_drop, high_cost_no_revenue
    Output: profitability_summary, customer_profitability, service_profitability
    │
    ▼
Layer 6 — Trend and Variance Detection
    MoM cost/revenue changes, new/removed charges, usage spikes, credits
    Output: trend_summary, new_charges, removed_charges, usage_spikes
    │
    ▼
Layer 7 — Aging / Payment Status  (activate when payment data is available)
    AR/AP aging, overdue items, payment mismatches
    Output: ar_aging, ap_aging, payment_mismatches
    │
    ▼
Layer 8 — AI Reasoning and Explanation
    LLM receives calculated tables + exception summaries
    LLM produces: management summary, root-cause classification,
    follow-up recommendations, supplier dispute drafts
    LLM must NOT: change calculated amounts, infer missing data as fact,
    call external data, issue accounting sign-off
```

## Severity scoring model

```
severity_score = value_impact_score + recurrence_score + confidence_score + operational_risk_score

80–100 → Critical
60–79  → High
35–59  → Medium
0–34   → Low
```

## Primary output format

Current (Phases 1–4):
- `db/*.parquet` — all calculated tables (snappy-compressed, overwritten each run with 2 archived copies)
- `output/<run_id>/*.md` — per-table markdown summaries
- `output/phase4_<run_id>/analyst_report.md` — LLM analyst report (9-section format)

Planned (Phase 4d backlog):
- `exceptions.csv`, `matched_lines.csv`, `profitability_by_customer.csv`, `run_summary.json` — CSV/JSON exports
- Optional Excel workbook: one tab per key table with README assumptions tab

## Key design decisions

- Python/pandas is the calculation authority — not the LLM. LLM receives summaries, not raw unbounded data.
- All transformations are written to a run folder; source CSVs are never modified.
- Source file hashes are recorded at Layer 0 for audit reproducibility.
- Manual mapping overrides are version-controlled, never silently created by the LLM.
- Severity is deterministic — no LLM judgment in exception ranking. (Formula defined in Severity scoring model section; Python implementation pending Phase 4c Gap 5.)

## Invariants — do not change without understanding

- `direct_margin = customer_revenue_ex_tax − supplier_cost_ex_tax` — never include tax in margin calculations.
- Unmatched records are always preserved in exception tabs — never silently dropped.
- LLM commentary sections are always clearly separated from calculated fact sections in every report.
- External data sources are blocked by default; the user must explicitly enable them.
