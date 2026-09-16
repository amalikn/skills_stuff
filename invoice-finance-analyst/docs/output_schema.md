# Output Schema — Internal Invoice Analysis

## Contents

- [Design Principle](#design-principle)
- [Tables](#tables)
  - [`run_summary`](#run_summary)
  - [`source_file_inventory`](#source_file_inventory)
  - [`data_quality_issues`](#data_quality_issues)
  - [`reconciliation_summary`](#reconciliation_summary)
  - [`matched_lines`](#matched_lines)
  - [`invoice_no_sales`](#invoice_no_sales)
  - [`sales_no_invoice`](#sales_no_invoice)
  - [`amount_mismatches`](#amount_mismatches)
  - [`assumptions`](#assumptions)
- [Output Formats](#output-formats)
- [Phase 2 Tables](#phase-2-tables)
  - [`rate_variances`](#rate_variances)
  - [`rate_card_mismatches`](#rate_card_mismatches)
  - [`margin_by_customer`](#margin_by_customer)
  - [`margin_by_service_type`](#margin_by_service_type)
  - [`low_margin_exceptions`](#low_margin_exceptions)
  - [`phase2_assumptions`](#phase2_assumptions)
- [Phase 3 Tables](#phase-3-tables)
  - [`mom_variance`](#mom_variance)
  - [`new_services`](#new_services)
  - [`removed_services`](#removed_services)
  - [`usage_spikes`](#usage_spikes)
  - [`recurring_changes`](#recurring_changes)
  - [`margin_movement`](#margin_movement)
  - [`phase3_assumptions`](#phase3_assumptions)
- [Phase 4 Output](#phase-4-output)
  - [`analyst_report.md`](#analyst_reportmd)
- [Phase Scope](#phase-scope)

---

Status: Current — covers Phase 1B (9 tables), Phase 2 (6 tables), Phase 3 (7 tables), Phase 4 (analyst_report.md)
Created: 2026-05-21  
Scope: All 22 output parquet tables + LLM analyst report. Column names locked after Phase 1B implementation.

---

## Design Principle

All output tables are derived entirely from source parquet files and declared assumptions.
No values are invented. Every aggregate links to source rows via `supplier_service_id` +
`billing_period_start`. Column names here are canonical and must match what the skeleton writes.

---

## Tables

### `run_summary`

One row per analysis run. Written last after all other tables are complete.

| Column | Type | Description |
|---|---|---|
| `run_id` | string | UUID for this run |
| `run_timestamp` | datetime | When the run started |
| `invoice_file` | string | Source invoice CSV filename |
| `sales_file` | string | Source sales billing CSV filename |
| `invoice_hash` | string | SHA-256 of invoice parquet source file |
| `sales_hash` | string | SHA-256 of sales billing parquet source file |
| `invoice_row_count` | int | Total rows in invoice parquet (including duplicates) |
| `sales_row_count` | int | Total rows in sales parquet |
| `matched_count` | int | Rows classified as matched |
| `invoice_only_count` | int | Invoice rows with no sales match |
| `sales_only_count` | int | Sales rows with no invoice match |
| `duplicate_invoice_count` | int | Duplicate invoice rows removed before reconciliation |
| `amount_mismatch_count` | int | Matched rows where cost variance exceeds tolerance |
| `tolerance_abs` | decimal | Absolute tolerance used (from AMOUNT_MATCH_TOLERANCE_ABS) |
| `tolerance_pct` | decimal | Percentage tolerance used (from AMOUNT_MATCH_TOLERANCE_PCT) |
| `match_key` | string | Join key used, e.g. `supplier_service_id+billing_period_start` |

---

### `source_file_inventory`

One row per loaded source file.

| Column | Type | Description |
|---|---|---|
| `source_type` | string | `supplier_invoice` or `sales_billing` |
| `file_name` | string | Original CSV filename |
| `file_hash` | string | SHA-256 at load time |
| `row_count` | int | Total rows loaded |
| `duplicate_row_count` | int | Exact duplicate rows detected |
| `null_counts_json` | string | JSON: `{canonical_field: null_count, ...}` |
| `loaded_at` | datetime | Load timestamp |

---

### `data_quality_issues`

One row per detected data quality problem. Empty if no issues.

| Column | Type | Description |
|---|---|---|
| `source_type` | string | Which file the issue came from |
| `field` | string | Canonical field name |
| `issue_type` | string | `null_in_required`, `duplicate_row`, `unparseable_date`, `unparseable_numeric` |
| `count` | int | Number of affected rows |
| `severity` | string | `high` (required field), `medium` (optional field with nulls), `low` |
| `detail` | string | Human-readable description |

---

### `reconciliation_summary`

One row per match status — aggregate view.

| Column | Type | Description |
|---|---|---|
| `match_status` | string | `matched`, `invoice_only`, `sales_only`, `duplicate_removed`, `amount_mismatch` |
| `row_count` | int | Number of rows in this category |
| `invoice_amount_total` | decimal | Sum of `amount_ex_tax` for rows in this category (null if not applicable) |
| `sales_revenue_total` | decimal | Sum of `revenue_ex_tax` for rows in this category (null if not applicable) |
| `pct_of_invoice_rows` | decimal | Proportion of total invoice rows |

---

### `matched_lines`

One row per successfully matched invoice↔sales pair.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Join key — supplier's service identifier |
| `billing_period_start` | date | Join key — start of billing period |
| `billing_period_end` | date | End of billing period |
| `invoice_number` | string | From invoice source |
| `service_type` | string | From invoice source |
| `invoice_amount_ex_tax` | decimal | Supplier charge |
| `sales_revenue_ex_tax` | decimal | Customer revenue |
| `sales_cost_ex_tax` | decimal | Cost recorded in billing system (null if absent) |
| `variance_abs` | decimal | `invoice_amount_ex_tax - sales_cost_ex_tax` (null if cost absent) |
| `variance_pct` | decimal | `variance_abs / invoice_amount_ex_tax` (null if cost absent) |
| `direct_margin_ex_tax` | decimal | `sales_revenue_ex_tax - invoice_amount_ex_tax` |
| `direct_margin_pct` | decimal | `direct_margin_ex_tax / sales_revenue_ex_tax` |
| `customer_id` | string | From sales source |
| `amount_mismatch_flag` | bool | True if `abs(variance_abs) > tolerance_abs` |

---

### `invoice_no_sales`

Invoice rows with no matching sales record.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier from invoice |
| `billing_period_start` | date | Billing period start |
| `billing_period_end` | date | Billing period end |
| `invoice_number` | string | Invoice reference |
| `service_type` | string | Product/service type |
| `amount_ex_tax` | decimal | Unmatched supplier charge |
| `description` | string | Line description |

---

### `sales_no_invoice`

Sales rows with no matching invoice record.

| Column | Type | Description |
|---|---|---|
| `our_service_id` | string | Internal service identifier |
| `billing_period_start` | date | Billing period start |
| `billing_period_end` | date | Billing period end |
| `customer_id` | string | Customer identifier |
| `customer_name` | string | Customer name |
| `service_type` | string | Service category |
| `revenue_ex_tax` | decimal | Revenue with no corresponding supplier cost |
| `cost_ex_tax` | decimal | Cost recorded (null if absent) |

---

### `amount_mismatches`

Matched rows where cost variance exceeds configured tolerance.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `billing_period_start` | date | Billing period |
| `invoice_amount_ex_tax` | decimal | What supplier charged |
| `sales_cost_ex_tax` | decimal | What billing system recorded as cost |
| `variance_abs` | decimal | `invoice_amount_ex_tax - sales_cost_ex_tax` |
| `variance_pct` | decimal | `variance_abs / invoice_amount_ex_tax` |
| `exceeds_abs_tolerance` | bool | `abs(variance_abs) > AMOUNT_MATCH_TOLERANCE_ABS` |
| `exceeds_pct_tolerance` | bool | `abs(variance_pct) > AMOUNT_MATCH_TOLERANCE_PCT` |
| `customer_id` | string | Affected customer |

---

### `assumptions`

Declared assumptions used in this run. Every threshold and mapping decision is recorded here.

| Column | Type | Description |
|---|---|---|
| `assumption_key` | string | Stable identifier, e.g. `tolerance.abs` |
| `value` | string | Value used |
| `rationale` | string | Why this value was chosen |
| `source` | string | Where value came from: `config`, `default`, `user_supplied` |

---

## Output Formats

Phase 1B writes two formats per table:

| Format | Path | Purpose |
|---|---|---|
| Parquet | `db/<table_name>.parquet` | Machine-readable, queryable, auditable |
| Markdown | `output/<run_id>/<table_name>.md` | Human-readable, LLM-consumable (Phase 4) |

CSV export (`output/<run_id>/<table_name>.csv`) deferred to Phase 1C or Phase 2.

---

## Phase 2 Tables

### `rate_variances`

One row per matched invoice line, joined to rate card on `service_type`.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `billing_period_start` | date | Billing period |
| `service_type` | string | Service category used for rate card lookup |
| `customer_id` | string | Customer identifier |
| `invoice_amount_ex_tax` | decimal | Actual supplier charge |
| `expected_cost_ex_tax` | decimal | Expected cost from rate card (null if no entry) |
| `rate_variance_abs` | decimal | `invoice_amount_ex_tax - expected_cost_ex_tax` |
| `rate_variance_pct` | decimal | `rate_variance_abs / expected_cost_ex_tax` |
| `rate_card_mismatch_flag` | bool | True if `abs(rate_variance_abs) > RATE_VARIANCE_TOLERANCE_ABS` |
| `no_rate_card_entry` | bool | True if no rate card row matched this service_type |

---

### `rate_card_mismatches`

Subset of `rate_variances` where `rate_card_mismatch_flag = True`. Separate from `amount_mismatches` (which compares invoice to sales cost, not rate card).

Columns: same as `rate_variances`.

---

### `margin_by_customer`

One row per customer. Aggregated from `matched_lines`.

| Column | Type | Description |
|---|---|---|
| `customer_id` | string | Customer identifier |
| `service_count` | int | Number of matched service lines |
| `revenue_total` | decimal | Sum of `sales_revenue_ex_tax` |
| `cost_total` | decimal | Sum of `invoice_amount_ex_tax` |
| `margin_total` | decimal | `revenue_total - cost_total` |
| `margin_pct` | decimal | `margin_total / revenue_total` |
| `low_margin_flag` | bool | True if `margin_pct < LOW_MARGIN_PCT_THRESHOLD` (5%) |

---

### `margin_by_service_type`

One row per service type. Aggregated from `matched_lines`. Same column structure as `margin_by_customer` with `service_type` replacing `customer_id`.

---

### `low_margin_exceptions`

Matched service lines where `direct_margin_pct < LOW_MARGIN_PCT_THRESHOLD`.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `billing_period_start` | date | Billing period |
| `service_type` | string | Service category |
| `customer_id` | string | Customer identifier |
| `invoice_amount_ex_tax` | decimal | Supplier charge |
| `sales_revenue_ex_tax` | decimal | Customer revenue |
| `direct_margin_ex_tax` | decimal | `revenue - cost` |
| `direct_margin_pct` | decimal | `margin / revenue` |

---

### `phase2_assumptions`

Declared Phase 2 thresholds. Same column structure as Phase 1B `assumptions` table.

Key entries: `low_margin_threshold`, `rate_variance_tolerance_abs`, `rate_variance_tolerance_pct`, `rate_card_temporal`.

---

---

## Phase 3 Tables

### `mom_variance`

Per-service MoM invoice amount comparison. Only services present in **both** periods
(inner join on `supplier_service_id`).

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `current_amount` | decimal | Invoice amount ex-tax in current period |
| `prior_amount` | decimal | Invoice amount ex-tax in prior period |
| `abs_change` | decimal | `current_amount - prior_amount` |
| `pct_change` | decimal | `abs_change / prior_amount` |
| `spike_flag` | bool | True if `current_amount > prior_amount × USAGE_SPIKE_MULTIPLIER` (strict >) |
| `recurring_change_flag` | bool | True if `abs(pct_change) > RECURRING_CHANGE_THRESHOLD_PCT` |

---

### `new_services`

Services in current period not present in prior period. One row per `supplier_service_id`.

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `billing_period_start` | date | Current billing period start |
| `service_type` | string | Service category |
| `amount_ex_tax` | decimal | Current period charge |

---

### `removed_services`

Services in prior period not present in current period. One row per `supplier_service_id`.

Same column structure as `new_services` but sourced from prior period data.

---

### `usage_spikes`

Subset of `mom_variance` where `spike_flag = True`. Threshold: `current > prior × 2.0`.

Columns: same as `mom_variance`.

---

### `recurring_changes`

Subset of `mom_variance` where `recurring_change_flag = True`. Threshold: `abs(pct_change) > 5%`.

A service can appear in both `usage_spikes` and `recurring_changes` — the flags are independent.

Columns: same as `mom_variance`.

---

### `margin_movement`

Per-service margin delta for services matched in current period that also appeared in prior
period. Prior margin computed inline from prior invoice + prior sales (no prior skeleton run).

| Column | Type | Description |
|---|---|---|
| `supplier_service_id` | string | Service identifier |
| `billing_period_start` | date | Current billing period start |
| `direct_margin_ex_tax` | decimal | Current period direct margin |
| `direct_margin_pct` | decimal | Current period margin % |
| `prior_margin` | decimal | Prior period margin (computed inline) |
| `prior_margin_pct` | decimal | Prior period margin % |
| `margin_delta_abs` | decimal | `direct_margin_ex_tax - prior_margin` |
| `margin_delta_pct_pts` | decimal | `direct_margin_pct - prior_margin_pct` (percentage-point change) |
| `margin_declined` | bool | True if `margin_delta_abs < 0` |

---

### `phase3_assumptions`

Declared Phase 3 thresholds. Same column structure as `assumptions`.

Key entries: `usage_spike_multiplier`, `recurring_change_threshold_pct`,
`mom_comparison_key`, `prior_margin_source`.

---

## Phase 4 Output

### `analyst_report.md`

Written to `output/phase4_<run_id>/analyst_report.md`. This is a markdown document, not a
parquet table.

| Section | Source | Content |
|---|---|---|
| Summary | SKILL.md Step 13 | ≤300 words, period, totals, top exceptions |
| Files Analyzed | `run_summary` parquet | Filenames, row counts, period |
| Assumptions | `*_assumptions` parquets | Tolerances, thresholds, mappings |
| Calculated Findings | All phase parquets | Key metrics table |
| Variances | Exception tables | Top exceptions by $ value, root-cause grouped |
| Suspected Causes | SKILL.md Step 12 | Root-cause categories with rationale |
| Recommended Checks | Exception tables | Specific next actions |
| Data Gaps | Missing/None tables | Skipped phases, unmapped columns |
| Confidence Rating | All tables | Low/Medium/High + one-sentence justification |

Every statement in the report is required to carry an inline evidence citation:
`[table: <name> | metric: <column_or_aggregate> | value: <value>]`

Provider-agnostic: any OpenAI-compatible endpoint (OpenAI, DeepSeek, Groq, Ollama, etc.).

---

## Phase Scope

| Table | Phase |
|---|---|
| `run_summary`, `source_file_inventory`, `data_quality_issues` | Phase 1B |
| `reconciliation_summary`, `matched_lines`, `invoice_no_sales`, `sales_no_invoice` | Phase 1B |
| `amount_mismatches` | Phase 1B (requires `cost_ex_tax` in sales data) |
| `assumptions` | Phase 1B |
| `rate_variances`, `rate_card_mismatches` | Phase 2 |
| `margin_by_customer`, `margin_by_service_type`, `low_margin_exceptions` | Phase 2 |
| `phase2_assumptions` | Phase 2 |
| `mom_variance`, `new_services`, `removed_services` | Phase 3 |
| `usage_spikes`, `recurring_changes` | Phase 3 |
| `margin_movement`, `phase3_assumptions` | Phase 3 |
| `analyst_report.md` (markdown) | Phase 4 |
