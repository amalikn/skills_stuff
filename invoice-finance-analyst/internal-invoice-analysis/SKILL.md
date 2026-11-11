---
name: internal-invoice-analysis
description: >
  Use when the user provides invoice, sales, rate-card, billing, cost, margin,
  or profitability CSVs and asks for financial comparison, reconciliation,
  variance analysis, anomaly detection, margin review, or multi-layer invoice analysis.
trigger: >
  User mentions: invoice reconciliation, supplier invoice, rate card validation,
  margin analysis, billing discrepancy, unmatched charges, cost vs revenue,
  profitability by customer/service, invoice exceptions, CSV analysis, telco billing.
version: "0.5.0"
phase: "Phase 4 runnable — not finance-control complete"
status: "runnable — Phase 1+2+3+4 scripts validated (pytest 219/219, 2026-05-21); finance_control_checklist.parquet, citation validator, and deterministic severity scoring pending (4b–4c)"
---

# Internal Invoice Analysis

<!-- toc-depth: 3 -->
## Contents

- [Hard Rules](#hard-rules)
- [15-Step Workflow](#15-step-workflow)
  - [Step 1 — Input Inventory](#step-1--input-inventory)
  - [Step 2 — Schema Detection](#step-2--schema-detection)
  - [Step 3 — Column Mapping](#step-3--column-mapping)
  - [Step 4 — Data Quality Checks](#step-4--data-quality-checks)
  - [Step 5 — Invoice Normalization](#step-5--invoice-normalization)
  - [Step 6 — Sales / Revenue Normalization](#step-6--sales--revenue-normalization)
  - [Step 7 — Rate-Card Matching](#step-7--rate-card-matching)
  - [Step 8 — Reconciliation](#step-8--reconciliation)
  - [Step 9 — Variance Analysis](#step-9--variance-analysis)
  - [Step 10 — Margin / Profitability Analysis](#step-10--margin--profitability-analysis)
  - [Step 11 — Anomaly Detection](#step-11--anomaly-detection)
  - [Step 12 — Root-Cause Grouping](#step-12--root-cause-grouping)
  - [Step 13 — Executive Summary](#step-13--executive-summary)
  - [Step 14 — Evidence Table](#step-14--evidence-table)
  - [Step 15 — Open Questions / Missing Data](#step-15--open-questions--missing-data)
- [Required Response Sections](#required-response-sections)
- [Analysis Layers Reference](#analysis-layers-reference)
- [Telco Wholesale Reconciliation Patterns](#telco-wholesale-reconciliation-patterns)
  - [Parse record types before analysis](#parse-record-types-before-analysis)
  - [Billing timing and service-period attribution](#billing-timing-and-service-period-attribution)
  - [Rate cards, discounts and rebates](#rate-cards-discounts-and-rebates)
  - [Reconciliation sources and standing checks](#reconciliation-sources-and-standing-checks)
  - [Voice usage reconciliation](#voice-usage-reconciliation)
  - [Margin outputs](#margin-outputs)
- [Script Integration](#script-integration)
- [External Data Policy](#external-data-policy)
- [Finance and Accounting Boundaries](#finance-and-accounting-boundaries)
- [Finance Control Checklist](#finance-control-checklist)
- [Evidence Rule](#evidence-rule)

---

Source-data-only multi-layer CSV invoice reconciliation, rate-card validation, margin analysis, and anomaly detection.

---

## Hard Rules

These rules are absolute and apply to every analysis run without exception:

1. **Source-data-only by default.** Use only user-supplied CSV files and explicitly declared assumptions. Do not fetch external market, CPI, inflation, FX, stock, or macroeconomic data unless the user
   explicitly asks for it.
2. **Never invent missing values.** Missing mappings, prices, dates, service IDs, or customer names must be flagged as exceptions, not guessed.
3. **Do not assume column meanings.** If column names are ambiguous or non-standard, present a best-guess mapping and ask the user to confirm before proceeding.
4. **Python/pandas is the calculation authority.** All numeric results — totals, variances, margins, counts — must come from deterministic script execution, not LLM arithmetic.
5. **Separate facts from interpretation.** Calculated findings and LLM commentary must appear in distinct sections. LLM commentary must never override a calculated value.
6. **Record every assumption.** Every assumption — column mapping, tolerance threshold, currency, tax treatment, period — must appear in the Assumptions section of the report.
7. **Flag all unmatched and low-confidence records.** Do not silently drop unresolvable lines. Every unmatched or low-confidence record goes to the manual review queue.

---

## 15-Step Workflow

Execute steps in order. Skip a step only when the required input is confirmed absent (e.g. no rate card supplied → skip Steps 7 and 9). Document any skipped step and reason.

---

### Step 1 — Input Inventory

- List all supplied files: name, path, size, encoding.
- Record SHA-256 hash and row count for each file.
- Classify each file: supplier invoice | customer billing/sales | rate card | service mapping | customer master | payment data | other.
- Note any missing recommended inputs (rate card, service mapping).

Output: `source_file_inventory` table.

---

### Step 2 — Schema Detection

- Detect column names, inferred data types, null counts, duplicate row counts.
- Identify candidate columns for: invoice number, date, amount, service ID, customer ID, description, charge type, currency.
- Flag columns where amounts are stored as text (currency symbols, commas).
- Flag columns with > 20% null rate on fields expected to be populated.

Output: `schema_validation` table, `data_quality_issues` list.

---

### Step 3 — Column Mapping

- Map detected columns to canonical field names (see Data Contract in `docs/data_contract.md`).
- If column names are ambiguous, present the best-guess mapping and ask the user to confirm or correct **before proceeding to Step 4**.
- Record the confirmed mapping as a named assumption.

Canonical invoice fields: `invoice_number`, `invoice_date`, `billing_period_start`, `billing_period_end`, `vendor`, `supplier_account`, `supplier_service_id`, `customer_id`, `customer_name`,
`product_code`, `service_type`, `charge_type`, `description`, `quantity`, `unit_price`, `amount_ex_tax`, `tax_amount`, `amount_inc_tax`, `currency`.

---

### Step 4 — Data Quality Checks

- Blank primary keys (invoice number, service ID, customer ID).
- Duplicate primary keys within the same file.
- Date parse failures.
- Non-numeric amount fields after coercion.
- Negative values — classify as credit, reversal, or error.
- Mixed currencies without explicit handling.
- Billing periods that do not overlap with the stated analysis period.

Output: append to `data_quality_issues`; add `dq_exception_count` summary row.

---

### Step 5 — Invoice Normalization

- Apply column mapping to produce canonical invoice dataset.
- Coerce all amount fields to numeric (strip currency symbols, commas).
- Parse and standardize all date fields to ISO 8601 (`YYYY-MM-DD`).
- Classify `charge_type` as: recurring | usage | once-off | credit | adjustment | tax.
- Separate tax/GST from ex-tax amounts; do not mix in comparisons.
- Telco wholesale files: parse record types and set each charge type's service period first ([Telco Wholesale Reconciliation Patterns](#telco-wholesale-reconciliation-patterns)).

Output: `normalized_invoices`.

---

### Step 6 — Sales / Revenue Normalization

- Apply column mapping to produce canonical sales/billing dataset.
- Same coercion and date standardization as Step 5.

Output: `normalized_sales`.

---

### Step 7 — Rate-Card Matching

*(Skip if no rate card supplied — record skip as assumption.)*

- Join each normalized invoice line and sales line to the rate card on `service_type`, `product_code`, and/or plan code.
- Calculate `expected_supplier_cost` and `expected_customer_revenue` per line.
- Flag lines with no rate-card match as `unmapped_rate`.

Output: `normalized_rate_card`, `rate_card_match_summary`.

---

### Step 8 — Reconciliation

Match invoice lines to sales lines using this priority order:

1. Exact `supplier_service_id` match
2. `supplier_service_id` + `billing_period` match
3. `customer_id` + `product_code` + `billing_period` match
4. Normalised description match (strip punctuation, lowercase, collapse whitespace)
5. Manual mapping override from `service_mapping.csv`

Classify each line:

| Category                 | Meaning                                                       |
| ------------------------ | ------------------------------------------------------------- |
| `matched`                | Invoice line paired to sales line within tolerance            |
| `invoice_no_sales`       | Supplier charged; no customer revenue found                   |
| `sales_no_invoice`       | Customer revenue exists; no supplier charge found             |
| `amount_mismatch`        | Matched on service/period but amount differs beyond tolerance |
| `period_mismatch`        | Matched service but billing period differs                    |
| `duplicate_invoice_line` | Same invoice/service/period charged more than once            |
| `duplicate_sales_line`   | Same customer/service/period billed more than once            |
| `unmapped_service`       | Service ID absent from mapping table                          |
| `ceased_service`         | Invoice line appears after known service cancellation         |

```python
# Match tolerance — calibrated against APN/Vocus billing data (2026-05-21).
#
# A line is classified 'matched' when:
#   abs(invoice_amount - sales_amount) <= max(AMOUNT_MATCH_TOLERANCE_ABS,
#                                             invoice_amount * AMOUNT_MATCH_TOLERANCE_PCT)
#
# Basis:
#   ABS = 0.02 — mirrors the rounding tolerance already used in vocus-profitability
#     analyse_rate_accuracy.py (DISCOUNT_TOLERANCE = 0.02). Smallest real invoice
#     lines observed: $0.63 (WS207 Miscellaneous Debit). 2¢ is consistent with the
#     house standard for this exact data.
#   PCT = 0.001 — on a typical $58 AVC charge, allows $0.06 float drift while
#     still flagging any real $5+ discrepancy as an amount_mismatch.

AMOUNT_MATCH_TOLERANCE_ABS = 0.02   # $0.02 absolute — house rounding standard
AMOUNT_MATCH_TOLERANCE_PCT = 0.001  # 0.1% proportional — float drift on larger charges
```

Output: `reconciliation_summary`, `matched_lines`, `invoice_no_sales`, `sales_no_invoice`, `amount_mismatches`, `period_mismatches`, `duplicates`, `unmapped_services`.

---

### Step 9 — Variance Analysis

*(Skip if no rate card was matched in Step 7.)*

- For each `amount_mismatch`: `variance = invoice_amount - sales_amount`; `variance_pct = variance / invoice_amount`.
- If rate card matched: `supplier_rate_variance = actual_supplier_cost - expected_supplier_cost`; `revenue_rate_variance = actual_customer_revenue - expected_customer_revenue`.
- Group variances by service type, customer, charge type, and billing period.

Output: `rate_validation_summary`, `supplier_rate_variances`, `customer_rate_variances`.

---

### Step 10 — Margin / Profitability Analysis

For each matched pair:

```
direct_margin     = sales_amount_ex_tax - invoice_amount_ex_tax
direct_margin_pct = direct_margin / sales_amount_ex_tax
```

Group by: customer, service ID, product/service type, supplier, billing period.

Exception flags:

| Flag                   | Rule                                           |
| ---------------------- | ---------------------------------------------- |
| `negative_margin`      | `direct_margin < NEGATIVE_MARGIN_THRESHOLD`    |
| `low_margin`           | `direct_margin_pct < LOW_MARGIN_PCT_THRESHOLD` |
| `high_cost_no_revenue` | Supplier cost exists but no matched revenue    |
| `high_revenue_no_cost` | Revenue exists but supplier cost missing       |

```python
# Margin thresholds — calibrated against APN/Vocus profitability data (2026-05-21).
#
# Observed margin profile (Mar–Apr 2026, ~18k–20k services):
#   Overall margin (incl. zero-revenue svcs):   1.8% – 3.6%
#   Adjusted margin (excl. zero-revenue svcs):  8.3% – 8.5%  ← business target band
#   Copper (structural loss):                  −$2.29 to −$3.50 per service
#   Fibre:                                      $1.54 to $3.06 per service (~2–4%)
#   Wireless:                                   $2.35 to $3.36 per service
#
# LOW_MARGIN_PCT_THRESHOLD = 0.05 flags anything below 5% — roughly half the
# adjusted target. Catches structural losers (copper, compressed fibre) without
# swamping the queue with normal high-volume services.

NEGATIVE_MARGIN_THRESHOLD  = 0     # direct_margin < 0 → always flag
LOW_MARGIN_PCT_THRESHOLD   = 0.05  # 5% — below half of APN's ~8.4% adjusted target
```

Output: `profitability_summary`, `customer_profitability`, `service_profitability`, `negative_margin_services`, `low_margin_services`.

---

### Step 11 — Anomaly Detection

If prior period data is supplied:

- New charges: service IDs in current period absent from prior period.
- Removed charges: service IDs in prior period absent from current period.
- Recurring amount changes: same service ID with materially different amount vs prior.
- Usage spikes: quantity or amount exceeds `USAGE_SPIKE_MULTIPLIER` × prior period average.
- Credits not matching prior overcharges.

If no prior period: flag service IDs absent from the mapping file as `new_service_unmapped`.

```python
# Anomaly thresholds — calibrated against APN/Vocus billing data (2026-05-21).
#
# NBN is stable recurring billing; speedpack rates are locked by contract. Normal
# MoM service count growth is ~5.8%. Anything 2× prior is a billing anomaly or
# mass provisioning error, not organic growth.
#
# USAGE_SPIKE_MULTIPLIER = 2.0:
#   61% of services incur overage each month (normal baseline). Flag only when
#   current-month usage/amount is 2× the prior-month average — clearly anomalous.
#
# RECURRING_CHANGE_THRESHOLD_PCT = 0.05:
#   Contractual rates (AVC per speedpack, CVC) should not drift >5% MoM without
#   a rate card update or plan change. The Mar→Apr margin drop of 48% at portfolio
#   level was driven by structural product mix, not per-service rate drift — a 5%
#   per-service threshold would have caught any individual billing errors early.

USAGE_SPIKE_MULTIPLIER         = 2.0   # 2× prior average — NBN stable; 2× = investigate
RECURRING_CHANGE_THRESHOLD_PCT = 0.05  # 5% — contractual rates; >5% MoM needs explanation
```

Output: `trend_summary`, `new_charges`, `removed_charges`, `usage_spikes`.

---

### Step 12 — Root-Cause Grouping

Group all exceptions by likely cause category:

| Category          | Examples                                                     |
| ----------------- | ------------------------------------------------------------ |
| `mapping_gap`     | Unmapped service, missing rate card entry                    |
| `billing_error`   | Duplicate charge, wrong amount, ceased service still charged |
| `timing`          | Period mismatch, charge in wrong month                       |
| `rate_change`     | Supplier rate changed without rate card update               |
| `new_service`     | New service not yet mapped                                   |
| `data_quality`    | Blank key, parse failure, mixed currency                     |
| `requires_review` | Low-confidence match, manual override needed                 |

Assign severity score per exception:

```
severity_score = value_impact_score + recurrence_score + confidence_score + operational_risk_score
```

| Score  | Severity |
| -----: | -------- |
| 80–100 | Critical |
| 60–79  | High     |
| 35–59  | Medium   |
| 0–34   | Low      |

Output: `exception_categories`, `manual_review_queue` (all Critical and High items).

---

### Step 13 — Executive Summary

Write a concise summary (≤ 300 words) covering:

- Files analyzed and analysis period.
- Total supplier cost, total customer revenue, overall direct margin.
- Top 3–5 exception categories by value impact.
- Highest-severity items requiring immediate action.
- Overall confidence level in the reconciliation.

Every statement must reference a calculated metric, output table row count, or declared assumption. No free-floating claims.

---

### Step 14 — Evidence Table

Produce a flat table linking every finding in the executive summary to its source:

| Finding                               | Source Table               | Metric / Row Count | Value   |
| ------------------------------------- | -------------------------- | ------------------ | ------- |
| e.g. "3 unmatched supplier charges"   | `invoice_no_sales`         | row_count          | 3       |
| e.g. "Total negative-margin exposure" | `negative_margin_services` | sum(direct_margin) | −$X,XXX |

---

### Step 15 — Open Questions / Missing Data

List all items that blocked or reduced confidence:

- Missing input files (no rate card, no mapping file, no prior period).
- Columns that could not be mapped with confidence.
- Unresolved duplicate primary keys.
- Services present in invoices but absent from every mapping source.
- Assumptions requiring operator confirmation before re-running.

---

## Required Response Sections

Every analysis response must include these sections in order:

| #   | Section             | Source                                                       |
| --: | ------------------- | ------------------------------------------------------------ |
| 1   | **Summary**         | Step 13                                                      |
| 2   | **Files analyzed**  | Step 1 (names, hashes, row counts, period)                   |
| 3   | **Assumptions**     | All steps (column mapping, tolerances, thresholds, currency) |
| 4   | **Calculated findings** | Key metrics table (totals, match rates, margin)              |
| 5   | **Variances**       | Top exceptions by value, grouped by category                 |
| 6   | **Suspected causes** | Step 12 root-cause grouping                                  |
| 7   | **Recommended checks** | Specific actions for top exceptions                          |
| 8   | **Data gaps**       | Step 15 open questions                                       |
| 9   | **Confidence rating** | Low / Medium / High with one-sentence justification          |

---

## Analysis Layers Reference

| Layer | Name                            | Active from                            |
| ----: | ------------------------------- | -------------------------------------- |
| 0     | Source Inventory                | Phase 1                                |
| 1     | Schema Validation               | Phase 1                                |
| 2     | Normalization                   | Phase 1                                |
| 3     | Invoice-to-Sales Reconciliation | Phase 1                                |
| 4     | Rate-Card Validation            | Phase 2                                |
| 5     | Profitability Analysis          | Phase 2                                |
| 6     | Trend and Variance Detection    | Phase 3                                |
| 7     | Aging / Payment Status          | Phase 3+ (when payment data available) |
| 8     | AI Reasoning and Explanation    | Phase 4                                |

---

## Telco Wholesale Reconciliation Patterns

Apply when the supplier is a telco wholesaler or aggregator (access circuits, shared capacity, voice usage). These are procedures, not figures: derive each supplier's record-type codes, pro-rata
divisor, discount base and rebate rules from its own files and contract, and record them as named assumptions. All money is ex-GST.

### Parse record types before analysis

- Parse every supplier file into a typed record-type model first; analysis rules hang off record types. Typical access record types: full-month recurring billed in advance; partial-month catch-up
  (activation, churn, resize); one-offs, rebates and clawbacks; credits; separate discount lines. Typical voice billing-file record types: header, outbound call records, per-department recurring,
  per-service recurring, inbound 13/1300/1800 usage, mobile usage, metadata.
- Classify access technology from the supplier's own line descriptor (the authoritative source) with an ordered pattern map, specific patterns before generic ones (FTTB/FTTN before a generic "Fibre").
  Joining to a separate report classifies fewer rows than parsing the descriptor. Exclude capacity lines from connection counts.
- Name each network's charge components in that network's own terms (access charge, per-service capacity, aggregated capacity) in the data dictionary; never relabel one network's capacity charge with
  another network's term. Label every margin with the cost layers it includes.

### Billing timing and service-period attribution

- **Advance plus catch-up, not credit-back.** Full months are billed in advance; partial months arrive later as a positive catch-up line rather than a negative reconciliation credit. The cost of
  service month M can appear on invoices M and M+1, and an activation month may show no charge until the next invoice.
- **Arrears.** Usage and overage are often billed in arrears on the same invoice as advance rental; a charge stamped with a first-of-month from-date and no to-date can be the prior month's usage. Give
  every charge type an explicit service-period rule (advance | arrears | point-in-time); never derive the service month from the charge from-date alone.
- **Event date for usage.** Usage joins use the event (call) date; bill month is only for invoice totals. Late-billed usage appears in the following month's file.
- **Pro-rata divisor.** Do not assume days-in-month. Recompute observed partial-month charges under each candidate divisor (days-in-month, a fixed 30 or 31 days, 365/12) and encode the one that
  reproduces the supplier's lines, per supplier.

### Rate cards, discounts and rebates

- **Effective-dated rate cards.** A rate-card row carries billing type, included allowance and floor/ceiling/flat columns with an effective date, not a single price column; joins pick the row
  effective on the service date.
- **Price frequency.** Tag every price column once-off or recurring, per month or per event; never sum mixed-frequency columns (an activation fee added to a monthly price overstates recurring cost).
- **Rate-card identity before variance.** Verify the product, supplier and effective date of a rate card before any variance analysis; a variance against the wrong product's card is not a finding.
  Treat a rate-card change as one coordinated change set across every file that carries it.
- **Net unit rate before a billing query.** Compute unit rates net across all record types (gross, discount lines, credits) before raising a query. Discounts can sit on separate lines at different
  percentages per product; reading gross alone manufactures phantom overcharges.
- **Discount base.** Record which record types a discount applies to (advance only, or advance plus catch-up) in the contract data model and test it; two systems computing the same percentage on
  different bases never reconcile.
- **Contracted vs applied rate (two oracles).** Check every invoice against (1) internal correctness: the rate the supplier says it applies, and (2) contract compliance: the signed contract. An
  invoice can pass the first and fail the second when a newly signed rate was never loaded into supplier billing. Store contract rates as slabs with effective dates, not a blended rate.
- **Rebates and pass-through.** Model rebates as effective-dated programmes with eligibility, earning month (usually activation month), stacking and end-date rules. Where the contract requires
  pass-through, reconcile supplier-received vs passed-through per service, and forecast the cost step when a programme ends. Regulated products can carry mandated rebates: state whether a margin uses
  the list rate card or the actual invoice net of rebates.
- **Tax basis.** Store money ex-GST with an explicit tax flag per source column; convert inc-GST sources at ingestion using the declared rate assumption.

### Reconciliation sources and standing checks

- **Three-source reconciliation.** The minimum set is supplier invoice x supplier service list or report x own billing (BSS) service book. Exceptions (active in one source only, product or speed
  profile mismatch) form the work queue.
- **Ghost services.** Reconcile service and capacity inventories against the supplier's latest invoice every cycle (an independent oracle), never against their own derived data; a check that validates
  a list against itself proves nothing. Ghost-circuit detection is a standing check, and a confirmed ghost is a retroactive credit claim.
- **Cost without revenue.** Run a standing wholesale-cost-no-retail-revenue check each cycle; split the result into subsidised, churned (catch-up only) and unexplained. Batch migrations where
  wholesale billing starts before retail billing are the usual cause of the unexplained set.
- **Validation gate.** Run invoice validation as a script with an exit code before any analysis, with internal-correctness and contract-compliance checks kept separate: totals tie; rate vs effective
  card (with scatter detection); capacity gross and net; resize pro-rata recompute; discount integrity; double billing; ghost and churned services vs own book; overage; contracted vs billed rate.

### Voice usage reconciliation

- **Call-record matching.** Normalise both sides to one timezone and format, then match on phone number + call date + start minute within +/-1 minute (carriers may truncate to the minute) + duration
  within tolerance, with one-to-one greedy assignment and confidence tiers. Unmatched rows are a review queue, not a margin conclusion; prefer phone-month aggregates for margin.
- **Split carrier charges by product line.** One carrier account can carry several product lines (VoIP usage, resold PSTN line rentals and voicemail, inbound numbers, data circuits, number ranges).
  Join each charge's service number to each product's inventory before computing margin; misattributed rentals make a product look loss-making.
- **Internal-number register.** Keep a register of own numbers (call-centre DDIs, inbound support lines) so own usage is reported as named platform overhead, not orphaned or customer cost.
- **Flat-rate plan risk.** Monitor unlimited-plan usage by destination class (mobile termination usually dominates cost) and pair it with fair-use controls.

### Margin outputs

- Define ARPU variants explicitly (plan price x service count vs received revenue after pro-rata and offers) and never mix them across carriers in one table.
- Model per-tier profitability as access cost plus shared capacity, backhaul, transit and data-centre cost allocated by measured average bandwidth, not by service count; keep a what-if rate-card lane
  that holds revenue constant.
- Every financial export carries its population filters, currency basis (ex-GST) and column definitions in an Assumptions sheet, and fails fast on unmapped categories rather than dropping them.

---

## Script Integration

Scripts in `scripts/` — run in this order for a full analysis:

| Script                         | Layers | Purpose                                                                                |
| ------------------------------ | ------ | -------------------------------------------------------------------------------------- |
| `validate_inputs.py`           | 0–1    | Schema check, null counts, type profiling — read-only                                  |
| `load_inputs.py`               | 2      | CSV → canonical parquet with mapping translation                                       |
| `invoice_analysis_skeleton.py` | 3      | Reconciliation: matched, invoice_only, sales_only, mismatches                          |
| `rate_card_analysis.py`        | 4–5    | Rate variance, margin by customer/service, low-margin exceptions                       |
| `trend_analysis.py`            | 6      | MoM trend: new/removed services, usage spikes, recurring changes, margin movement      |
| `llm_analyst.py`               | 8      | LLM commentary: executive summary, exception narrative, evidence table, open questions |

**Pipeline for a new supplier CSV (single period):**

```bash
# Step 1 — generate mapping suggestion (first run with a new CSV only)
python scripts/validate_inputs.py --csv invoice.csv --suggest-mapping --source-type supplier_invoice

# Step 2 — load to parquet (edit mapping YAML first to confirm column names)
python scripts/load_inputs.py --csv invoice.csv --mapping mapping_supplier_invoice.yaml --name invoice
python scripts/load_inputs.py --csv sales.csv   --mapping mapping_sales_billing.yaml   --name sales_billing
python scripts/load_inputs.py --csv rate_card.csv --mapping mapping_rate_card.yaml     --name rate_card

# Step 3 — run analysis
python scripts/invoice_analysis_skeleton.py
python scripts/rate_card_analysis.py
python scripts/trend_analysis.py  # optional — requires prior period CSVs

# Step 4 — generate analyst report (any OpenAI-compatible provider)
# OpenAI (default)
python scripts/llm_analyst.py
# DeepSeek
OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=sk-... \
    python scripts/llm_analyst.py --model deepseek-chat
# Ollama (local, no key)
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama \
    python scripts/llm_analyst.py --model llama3.2
```

**Full pipeline including MoM trend (prior period required):**

```bash
# Load prior period first
python scripts/load_inputs.py --csv prior_invoice.csv --mapping mapping_supplier_invoice.yaml --name prior_invoice
python scripts/load_inputs.py --csv prior_sales.csv   --mapping mapping_sales_billing.yaml   --name prior_sales_billing

# Then run trend analysis
python scripts/trend_analysis.py
```

All numeric output from these scripts is authoritative. LLM interpretation runs **after** script output is available, not instead of it.

---

## External Data Policy

**Default: no external data.**

External data sources — market prices, CPI, inflation indices, FX rates, stock data, industry benchmarks, public company financials — are **prohibited by default**.

If the user explicitly requests external context (e.g. "compare our margins against listed telco peers" or "adjust for CPI"), acknowledge the request, state what external data would be needed, and ask
for confirmation before fetching anything.

---

## Finance and Accounting Boundaries

These boundaries apply to every report produced by this skill:

- Reports are **operational analysis**, not final accounting, tax, or audit sign-off.
- GST/tax treatment must be verified by a finance professional before lodgement or accounting entries.
- Journal entries, write-offs, supplier credits, and customer refunds require human approval — the skill identifies candidates, not decisions.
- Supplier dispute drafts produced by this skill are drafts only. They have not been reviewed for legal accuracy.
- Confidence ratings reflect data completeness and reconciliation coverage, not audit assurance.
- Margin and variance figures are direct calculations from supplied data. They do not account for accruals, provisions, or off-system adjustments unless those are in the supplied files.

---

## Finance Control Checklist

Every report must include a finance control checklist section with the following items calculated by Python (not invented by the LLM). Items without data should be reported as "not supplied":

- Source invoice total and normalized invoice total tie-out (pass / fail / delta)
- Source sales total and normalized sales total tie-out (pass / fail / delta)
- GST/tax status per source file (ex-tax / inc-tax / mixed / unknown)
- Credit/reversal total and classification method
- Rate-card coverage percentage (lines with a matched rate / total lines)
- Service-map coverage percentage (lines with a mapped service / total lines)
- Unmatched supplier cost exposure (sum of `invoice_no_sales` amounts)
- Unmatched customer revenue exposure (sum of `sales_no_invoice` amounts)
- Negative and low-margin exposure (sum of negative + below-threshold margin lines)
- AR/AP aging data: supplied / not supplied
- Manual review queue count by severity (Critical / High / Medium / Low)

---

## Evidence Rule

Every number, percentage, count, or dollar amount in the output must be traceable to one of:

- A row or aggregate from a calculated output table.
- A value in a supplied source file.
- A declared assumption with an explicit value.

If a claim cannot be traced, it must not appear in the output.
