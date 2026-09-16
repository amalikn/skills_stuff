# Internal Financial AI for Multi-Layer Invoice Analysis

## Contents

- [1. Direct Recommendation](#1-direct-recommendation)
- [2. Why This Is the Right Direction](#2-why-this-is-the-right-direction)
- [3. Tool / Skill Candidates Found](#3-tool-skill-candidates-found)
  - [3.1 Open Accountant Skills](#31-open-accountant-skills)
  - [3.2 Anthropic Knowledge Work Plugins — Finance Skills](#32-anthropic-knowledge-work-plugins-finance-skills)
  - [3.3 Anthropic Financial Services Repository](#33-anthropic-financial-services-repository)
  - [3.4 Alireza Rezvani Claude Skills — Finance Skills](#34-alireza-rezvani-claude-skills-finance-skills)
  - [3.5 Composio Invoice Organizer Skill](#35-composio-invoice-organizer-skill)
  - [3.6 Market / External Financial Data MCPs](#36-market-external-financial-data-mcps)
- [4. Proposed Custom Skill: `invoice-finance-analyst`](#4-proposed-custom-skill-invoicefinanceanalyst)
  - [4.1 Skill Responsibilities](#41-skill-responsibilities)
  - [4.2 Skill Non-Responsibilities](#42-skill-non-responsibilities)
- [5. Multi-Layer Invoice Analysis Model](#5-multi-layer-invoice-analysis-model)
  - [Layer 0 — Source Inventory](#layer-0-source-inventory)
  - [Layer 1 — Schema Validation](#layer-1-schema-validation)
  - [Layer 2 — Normalization](#layer-2-normalization)
  - [Layer 3 — Invoice-to-Sales Reconciliation](#layer-3-invoice-to-sales-reconciliation)
  - [Layer 4 — Rate-Card Validation](#layer-4-rate-card-validation)
  - [Layer 5 — Profitability Analysis](#layer-5-profitability-analysis)
  - [Layer 6 — Trend and Variance Detection](#layer-6-trend-and-variance-detection)
  - [Layer 7 — Aging / Payment Status](#layer-7-aging-payment-status)
  - [Layer 8 — AI Reasoning and Explanation](#layer-8-ai-reasoning-and-explanation)
- [6. Recommended Report Output](#6-recommended-report-output)
- [7. Severity Model](#7-severity-model)
- [8. Data Governance Rules](#8-data-governance-rules)
- [9. Implementation Phases](#9-implementation-phases)
  - [Phase 0 — Tool and Skill Trial](#phase-0-tool-and-skill-trial)
  - [Phase 1 — Minimum Viable CSV Reconciliation](#phase-1-minimum-viable-csv-reconciliation)
  - [Phase 2 — Rate Card and Margin](#phase-2-rate-card-and-margin)
  - [Phase 3 — Trend Detection](#phase-3-trend-detection)
  - [Phase 4 — LLM Analyst Layer](#phase-4-llm-analyst-layer)
  - [Phase 5 — Optional Accounting System MCP](#phase-5-optional-accounting-system-mcp)
- [10. Local Skill Draft](#10-local-skill-draft)
- [Hard Rules](#hard-rules)
- [Standard Workflow](#standard-workflow)
- [Required Output Sections](#required-output-sections)
- [Evidence Rule](#evidence-rule)
- [11. Recommended Codex / Claude Prompt Pattern](#11-recommended-codex-claude-prompt-pattern)
- [12. Recommended Custom Metrics](#12-recommended-custom-metrics)
- [13. Final Tool Decision Matrix](#13-final-tool-decision-matrix)
- [14. Practical Next Step](#14-practical-next-step)
- [15. Source Notes](#15-source-notes)

---

Status: draft implementation guide  
Scope: internal CSV-based invoice, sales, rate-card, and profitability analysis  
Default rule: do not use external market, CPI, inflation, stock, or macro data unless explicitly requested

---

## 1. Direct Recommendation

Use a layered stack:

1. **Finance/accounting SKILL.md packages** for domain methodology and analyst behavior.
2. **Python + pandas** for deterministic calculations, joins, reconciliation, variance detection, and report generation.
3. **Excel output layer** for reviewable workbooks, exception tabs, pivot-style summaries, and graphs.
4. **Codex / Claude Code / local LLM** as the reasoning interface, using the finance skills and your project-specific rules.
5. **Do not use OpenBB as the primary tool** for this project. It is mainly useful for market/economic context, not for your first-stage internal CSV invoice reconciliation.

Recommended starting stack:

| Layer | Tool | Role | Use Now? |
|---|---|---:|---:|
| Finance skills | Open Accountant Skills | P&L, invoice aging, client profitability, pricing, cash-flow, CSV/manual mode | Yes |
| Finance skills | Anthropic Knowledge Work / Finance plugin skills | reconciliation, variance, close, financial statement workflow patterns | Yes, adapt manually |
| Finance skills | Alireza Rezvani finance-skills | ratio, DCF, budget variance, forecasting scripts | Trial |
| Invoice document handling | Composio invoice-organizer skill | organize/extract invoices/receipts from messy files | Later, only if PDFs/images are involved |
| Calculation engine | Python + pandas | source of truth for calculations | Yes |
| Report engine | openpyxl / xlsxwriter / existing Excel MCP | Excel workbook output | Yes |
| Market data MCP | Financial Datasets / Octagon / finance-tools-mcp | stock/market/macro data | No for Phase 1 |

Key decision: **build a custom `invoice-finance-analyst` skill that imports/adapts the useful finance skill logic, but forces all conclusions to come from your supplied CSVs.**

---

## 2. Why This Is the Right Direction

Your requirement is not generic “financial market analysis.” It is **internal financial analysis over your own operational data**.

The tool must answer questions like:

- Are supplier invoices matching expected service costs?
- Are all invoiced services present in the sales/customer billing data?
- Are we billing the customer more than we are being charged?
- Which services/customers/products have poor or negative margin?
- Which charges changed unexpectedly month-to-month?
- Which invoice lines are duplicates, missing, stale, or unmatched?
- Which exceptions need human review?

That means the core engine must be deterministic and auditable. The AI layer should explain, classify, and summarize; it should not invent financial numbers.

---

## 3. Tool / Skill Candidates Found

### 3.1 Open Accountant Skills

Repository: `openaccountant/skills`  
License: MIT  
Type: SKILL.md style skills  
Fit: high for your requirement

Relevant skills:

| Skill | Why it matters for your use case |
|---|---|
| `import-transactions` | CSV/OFX/QIF import thinking; useful for normalizing source files |
| `profit-loss` | Generates P&L-style summaries from supplied data |
| `invoice-aging` | Tracks unpaid invoices and collection timelines |
| `client-profitability` | Revenue and costs per client |
| `pricing-optimizer` | Analyze pricing against cost and margin |
| `cash-flow-forecast` | Useful later if you add payment timing |
| `revenue-concentration` | Customer concentration / dependency risk |
| `seasonal-patterns` | Detects recurring monthly/seasonal cost/revenue patterns |
| `custom-report` | Good base for your own invoice exception reports |
| `smart-categorize` | Can help classify messy descriptions/vendor lines |
| `monthly-digest` | Useful for management summaries |
| `month-end-close` | Useful if this becomes a recurring monthly process |

Important note: this repo is highly relevant, but at the time checked it had a low star count. I would still trial it because it directly targets SKILL.md finance workflows and supports CSV/manual mode.

Best use: install or copy selected skills, then create your own stricter internal skill that overrides assumptions and forces source-data-only analysis.

---

### 3.2 Anthropic Knowledge Work Plugins — Finance Skills

Repository: `anthropics/knowledge-work-plugins`  
License: Apache-2.0  
Type: Claude plugin / skills / commands  
Fit: high for reconciliation methodology, medium for direct Codex portability

Relevant pieces:

| Skill / Area | Usefulness |
|---|---|
| `finance/skills/reconciliation` | Strong methodology for GL-to-subledger, bank, intercompany, reconciling items, aging, escalation |
| Finance plugin | Covers journal entries, account reconciliation, financial statements, variance analysis, close support, audit support |
| Plugin structure | Useful as reference for building your own local skill bundle |

Best use: do not blindly install the whole plugin. Extract and adapt the reconciliation methodology into your local `invoice-finance-analyst` skill.

---

### 3.3 Anthropic Financial Services Repository

Repository: `anthropics/financial-services`  
License: Apache-2.0  
Type: reference agents, vertical plugins, financial services skills, commands, connectors  
Fit: medium for your use case

Useful components:

| Component | Relevance |
|---|---|
| `financial-analysis` | Core modeling, Excel, and deck QC patterns |
| `clean-data-xls` | Useful conceptually for Excel/table normalization |
| `audit-xls` | Useful for spreadsheet audit patterns, formula checks, balance checks |
| `3-statement-model`, `dcf`, `comps` | Mostly not needed for invoice reconciliation |
| `portfolio-monitoring`, `unit-economics` | Useful later if you map this to service/customer profitability reporting |

Best use: reference only. It is more investment-banking / equity-research / wealth-management oriented than your invoice reconciliation need.

---

### 3.4 Alireza Rezvani Claude Skills — Finance Skills

Repository: `alirezarezvani/claude-skills`  
Type: finance SKILL.md with Python tools  
Fit: medium-high for variance and forecasting; not invoice-specific

Relevant pieces:

| Capability | Relevance |
|---|---|
| budget variance analyzer | Useful for invoice vs expected cost or actual vs expected sales |
| forecast builder | Useful later for monthly cost/revenue forecasting |
| ratio calculator | Less important unless you create management KPIs |
| DCF valuation | Not relevant to invoice analysis |

Best use: trial only. Pull the budget variance / forecasting patterns, not the whole suite.

---

### 3.5 Composio Invoice Organizer Skill

Repository: `ComposioHQ/awesome-claude-skills/invoice-organizer`  
Type: SKILL.md  
Fit: low for CSV comparison, medium if you later ingest PDFs/images

This skill is designed to read invoice files, extract vendor/date/amount/invoice number, rename documents, and organize them for bookkeeping. It is not the main analysis engine for your CSV comparison, but it becomes useful if your source data includes messy invoice PDFs or receipt folders.

Best use: later-stage document ingestion, not Phase 1.

---

### 3.6 Market / External Financial Data MCPs

Do not use these for the first stage.

| Tool | Why not for Phase 1 |
|---|---|
| Financial Datasets MCP | Pulls stock market/company financials/news, not your internal invoice CSVs |
| Octagon Skills/MCP | Financial research/market-data oriented; requires external API key |
| finance-tools-mcp | Investor-agent / market/macro research orientation |
| OpenBB | Useful for external market/economic context, not core invoice reconciliation |

Use them only if you later ask questions like: “compare our margins against listed telco peers,” “adjust costs for CPI,” or “benchmark against public financials.”

---

## 4. Proposed Custom Skill: `invoice-finance-analyst`

Create a local skill with this role:

> Analyze supplied invoice, sales, rate-card, customer, service, and cost CSVs using finance/accounting reasoning. All numeric conclusions must come from provided files or explicitly declared assumptions. External market/inflation/macro data is prohibited unless the user explicitly asks for it.

### 4.1 Skill Responsibilities

The skill should handle:

- invoice normalization;
- sales data normalization;
- expected-charge reconstruction from rate cards;
- invoice-to-sales reconciliation;
- invoice-to-rate-card validation;
- margin and profitability analysis;
- variance analysis;
- duplicate/stale/missing service detection;
- exception prioritization;
- management summary generation;
- workbook/report output specification;
- audit trail and evidence preservation.

### 4.2 Skill Non-Responsibilities

The skill must not:

- use CPI/inflation/external financial market data by default;
- estimate missing prices without marking them as assumptions;
- invent service mappings;
- hide unmatched records;
- produce final accounting advice without human review;
- overwrite source data;
- make irreversible changes to accounting systems.

---

## 5. Multi-Layer Invoice Analysis Model

### Layer 0 — Source Inventory

Inputs expected:

| File | Required? | Purpose |
|---|---:|---|
| `supplier_invoices.csv` | Yes | Charges from supplier/vendor invoices |
| `sales.csv` or `customer_billing.csv` | Yes | Revenue/sales/customer billing data |
| `rate_card.csv` | Strongly recommended | Expected rates by service/product/plan |
| `service_mapping.csv` | Strongly recommended | Maps supplier service IDs to customer/service/account IDs |
| `customer_master.csv` | Optional | Customer names, segments, account ownership |
| `product_master.csv` | Optional | Product hierarchy and service type mapping |
| `network_cost_allocations.csv` | Later | Shared/network overhead allocation model |
| `payments.csv` | Later | Paid/unpaid/aged debt analysis |

Minimum viable Phase 1 input:

- supplier invoice CSV;
- customer sales/billing CSV;
- a mapping key between them.

---

### Layer 1 — Schema Validation

Checks:

- required columns present;
- dates parse correctly;
- currency/amount fields parse as numeric;
- invoice numbers are not blank;
- service/customer identifiers are not blank where required;
- duplicate primary keys are flagged;
- negative values are classified as credits, reversals, or errors;
- source file hashes are recorded.

Output tabs:

- `schema_validation`
- `source_file_inventory`
- `data_quality_issues`

---

### Layer 2 — Normalization

Normalize all datasets into canonical fields.

Canonical invoice fields:

| Canonical Field | Meaning |
|---|---|
| `source_file` | Original file name |
| `invoice_number` | Supplier invoice number |
| `invoice_date` | Invoice date |
| `billing_period_start` | Start of billing period |
| `billing_period_end` | End of billing period |
| `vendor` | Supplier/vendor name |
| `supplier_account` | Supplier account number |
| `supplier_service_id` | Service/circuit/line identifier from supplier |
| `customer_id` | Internal/customer ID after mapping |
| `customer_name` | Customer name after mapping |
| `product_code` | Internal product code |
| `service_type` | NBN, OptiComm, voice, hosting, transit, etc. |
| `charge_type` | recurring, usage, once-off, credit, adjustment, tax |
| `description` | Raw line description |
| `quantity` | Quantity/unit count |
| `unit_price` | Unit rate |
| `amount_ex_tax` | Amount before tax |
| `tax_amount` | Tax/GST |
| `amount_inc_tax` | Amount including tax |
| `currency` | Currency |

Output tabs:

- `normalized_invoices`
- `normalized_sales`
- `normalized_rate_card`
- `mapping_issues`

---

### Layer 3 — Invoice-to-Sales Reconciliation

Goal: prove every supplier charge has corresponding customer revenue or a valid reason why it does not.

Match logic priority:

1. exact service ID match;
2. service ID + billing period match;
3. customer ID + product + period match;
4. normalized description fuzzy match;
5. manual mapping override.

Exception categories:

| Category | Meaning |
|---|---|
| `invoice_no_sales` | Supplier charged us, but no matching customer revenue found |
| `sales_no_invoice` | Customer revenue exists, but no supplier charge found |
| `amount_mismatch` | Matched record but amount differs beyond tolerance |
| `period_mismatch` | Matched service but billing period differs |
| `duplicate_invoice_line` | Same invoice/service/period charged more than once |
| `duplicate_sales_line` | Same customer/service/period billed more than once |
| `unmapped_service` | Service ID not found in mapping table |
| `ceased_service_still_charged` | Invoice line exists after known service cancellation |
| `new_service_unmapped` | New service appears without approved mapping |

Output tabs:

- `reconciliation_summary`
- `matched_lines`
- `invoice_no_sales`
- `sales_no_invoice`
- `amount_mismatches`
- `period_mismatches`
- `duplicates`
- `unmapped_services`

---

### Layer 4 — Rate-Card Validation

Goal: check whether actual invoice and sales charges match expected rates.

Checks:

- supplier invoice amount vs expected supplier rate;
- customer sales amount vs expected customer sell price;
- product/service plan mapping correctness;
- once-off charges separated from recurring charges;
- usage charges separated from fixed charges;
- credits/reversals handled separately;
- tax/GST not mixed into ex-tax comparisons.

Useful metrics:

| Metric | Formula |
|---|---|
| Supplier variance | `actual_supplier_cost - expected_supplier_cost` |
| Supplier variance % | `supplier_variance / expected_supplier_cost` |
| Revenue variance | `actual_customer_revenue - expected_customer_revenue` |
| Revenue variance % | `revenue_variance / expected_customer_revenue` |
| Gross margin | `customer_revenue - supplier_cost` |
| Gross margin % | `gross_margin / customer_revenue` |

Output tabs:

- `rate_validation_summary`
- `supplier_rate_variances`
- `customer_rate_variances`
- `charge_type_breakdown`

---

### Layer 5 — Profitability Analysis

Start with direct margin only. Add network/shared cost later.

Phase 1 direct profitability:

`direct_margin = customer_revenue_ex_tax - supplier_cost_ex_tax`

`direct_margin_pct = direct_margin / customer_revenue_ex_tax`

Group by:

- customer;
- service ID;
- product/service type;
- supplier;
- region/site;
- billing period;
- account manager / business unit if available.

Exception categories:

| Category | Rule |
|---|---|
| `negative_margin` | Direct margin < 0 |
| `low_margin` | Margin % below threshold |
| `margin_drop` | Current margin materially lower than prior period |
| `high_cost_no_revenue` | Cost exists but no revenue |
| `high_revenue_no_cost` | Revenue exists but cost missing; may indicate mapping gap |

Output tabs:

- `profitability_summary`
- `customer_profitability`
- `service_profitability`
- `product_profitability`
- `negative_margin_services`
- `low_margin_services`

---

### Layer 6 — Trend and Variance Detection

Goal: find changes that need attention, not just current-period mismatches.

Checks:

- month-over-month cost changes;
- month-over-month revenue changes;
- margin trend by customer/product/service;
- new charges;
- disappeared charges;
- recurring amount changes;
- unusual one-off charges;
- abnormal quantity/usage spikes;
- recurring services charged after cancellation;
- credits that do not map to previous overcharges.

Output tabs:

- `trend_summary`
- `new_charges`
- `removed_charges`
- `recurring_charge_changes`
- `usage_spikes`
- `credits_and_reversals`

---

### Layer 7 — Aging / Payment Status

Only activate when payment data is available.

Checks:

- invoice due date;
- paid/unpaid status;
- days overdue;
- partial payments;
- customer invoice aging;
- supplier payable aging;
- mismatched payment references.

Output tabs:

- `ar_aging`
- `ap_aging`
- `payment_mismatches`
- `overdue_high_value_items`

---

### Layer 8 — AI Reasoning and Explanation

The LLM should receive calculated tables and exception summaries, not raw unbounded data only.

The LLM can:

- explain why exceptions matter;
- classify likely root causes;
- generate a management summary;
- suggest follow-up checks;
- draft supplier dispute notes;
- draft internal finance/ops tickets;
- identify where mappings or rate cards are missing;
- prioritize remediation by value and risk.

The LLM must not:

- change calculated amounts;
- infer missing data as fact;
- call external data sources;
- issue accounting sign-off;
- hide low-confidence joins.

---

## 6. Recommended Report Output

Produce one Excel workbook per analysis run:

`invoice_analysis_<yyyymm>_<run_id>.xlsx`

Recommended tabs:

1. `README`
2. `executive_summary`
3. `source_file_inventory`
4. `schema_validation`
5. `data_quality_issues`
6. `reconciliation_summary`
7. `matched_lines`
8. `invoice_no_sales`
9. `sales_no_invoice`
10. `amount_mismatches`
11. `period_mismatches`
12. `duplicates`
13. `rate_validation_summary`
14. `supplier_rate_variances`
15. `customer_rate_variances`
16. `profitability_summary`
17. `customer_profitability`
18. `service_profitability`
19. `negative_margin_services`
20. `low_margin_services`
21. `trend_summary`
22. `new_charges`
23. `removed_charges`
24. `usage_spikes`
25. `manual_review_queue`
26. `assumptions_and_rules`
27. `audit_log`

Also export machine-readable outputs:

- `exceptions.csv`
- `matched_lines.csv`
- `profitability_by_customer.csv`
- `profitability_by_service.csv`
- `run_summary.json`

---

## 7. Severity Model

Use deterministic severity scoring.

| Severity | Rule Example |
|---|---|
| Critical | Negative margin over threshold; high-value invoice without sales; duplicate high-value charges |
| High | Unmapped high-value service; amount variance above threshold; ceased service still charged |
| Medium | Low margin; period mismatch; new charge without mapping |
| Low | Minor variance under threshold; description-only mismatch; missing optional metadata |

Example score:

`severity_score = value_impact_score + recurrence_score + confidence_score + operational_risk_score`

Suggested thresholds:

| Score | Severity |
|---:|---|
| 80–100 | Critical |
| 60–79 | High |
| 35–59 | Medium |
| 0–34 | Low |

---

## 8. Data Governance Rules

Mandatory controls:

- preserve original CSV files read-only;
- record file hash, row count, column count, and load timestamp;
- write all transformations to a run folder;
- preserve exact rules version used for the run;
- separate calculated facts from LLM commentary;
- require human review for every exception above threshold;
- keep manual mapping overrides in a version-controlled file;
- never let the LLM silently create mappings without review.

Recommended folder layout:

```text
invoice-analysis/
  README.md
  AGENTS.md
  skills/
    invoice-finance-analyst/
      SKILL.md
      references/
      scripts/
  data/
    incoming/
    normalized/
    mappings/
    rate_cards/
  runs/
    2026-05-21_001/
      inputs/
      outputs/
      logs/
      audit/
  reports/
  tests/
```

---

## 9. Implementation Phases

### Phase 0 — Tool and Skill Trial

Install/trial:

```bash
npx skills add openaccountant/skills
```

Then inspect and copy only the useful skills into your project-local skill folder.

Start with:

- `import-transactions`
- `profit-loss`
- `invoice-aging`
- `client-profitability`
- `pricing-optimizer`
- `custom-report`
- `smart-categorize`
- `monthly-digest`

Also manually review and adapt:

- Anthropic `knowledge-work-plugins/finance/skills/reconciliation/SKILL.md`
- Anthropic `financial-services` `clean-data-xls` / `audit-xls` concepts
- Alireza finance budget variance / forecasting scripts

Exit criteria:

- you have one local `invoice-finance-analyst/SKILL.md`;
- it explicitly says source-data-only;
- it bans external data unless requested;
- it defines the invoice analysis layers above.

---

### Phase 1 — Minimum Viable CSV Reconciliation

Input:

- supplier invoice CSV;
- sales/customer billing CSV;
- simple mapping file.

Build:

- schema validation;
- normalization;
- invoice-to-sales matching;
- exception output;
- Excel workbook.

Exit criteria:

- identifies matched, unmatched, duplicate, and amount mismatch records;
- produces an exception workbook;
- records source file hashes and row counts.

---

### Phase 2 — Rate Card and Margin

Add:

- rate card input;
- expected supplier cost;
- expected customer revenue;
- actual vs expected variance;
- margin by customer/service/product.

Exit criteria:

- margin report works;
- negative/low margin exceptions generated;
- rate-card mismatches separated from mapping mismatches.

---

### Phase 3 — Trend Detection

Add prior periods.

Build:

- MoM trend analysis;
- new/removed recurring charges;
- usage spike detection;
- margin movement.

Exit criteria:

- monthly changes are explained;
- high-impact changes are prioritized.

---

### Phase 4 — LLM Analyst Layer

Feed calculated summaries to the LLM.

LLM outputs:

- executive summary;
- exception narrative;
- suspected root cause categories;
- recommended follow-up actions;
- supplier dispute draft;
- internal ticket draft.

Exit criteria:

- every LLM statement links back to a table, row, metric, or explicit assumption;
- no external factors are used unless requested.

---

### Phase 5 — Optional Accounting System MCP

Only consider if CSV export becomes a bottleneck.

Only consider if invoices are managed in an accounting system (e.g. Xero, Odoo) and CSV export becomes a bottleneck. Evaluate at that time.

Do not add in Phase 1–4.

---

## 10. Local Skill Draft

Create:

`skills/invoice-finance-analyst/SKILL.md`

Suggested content:

```markdown
---
name: invoice-finance-analyst
description: Analyze supplied invoice, sales, rate-card, and profitability CSVs using source-data-only finance/accounting reasoning. Use for invoice reconciliation, variance analysis, margin analysis, exception prioritization, and management summaries.
---

# Invoice Finance Analyst

Use this skill when the user provides internal CSVs for invoices, sales, billing, rate cards, payments, customer/service mappings, or profitability analysis.

## Hard Rules

- Use only user-supplied files and explicitly supplied assumptions.
- Do not use market data, inflation, CPI, stock data, macro data, or external benchmarks unless the user explicitly asks.
- Python/pandas calculations are the source of truth for numbers.
- LLM output is commentary, explanation, classification, and reporting only.
- Never invent missing mappings, prices, dates, service IDs, or customer names.
- Separate facts, assumptions, calculations, and commentary.
- Flag all unmatched or low-confidence records for human review.

## Standard Workflow

1. Inventory all input files.
2. Validate schemas and data quality.
3. Normalize invoice, sales, rate-card, and mapping datasets.
4. Reconcile invoice lines to sales/customer billing lines.
5. Validate actual charges against expected rate-card charges.
6. Calculate direct margin and margin percentage.
7. Detect duplicates, missing records, stale charges, new charges, and period mismatches.
8. Rank exceptions by value impact, recurrence, confidence, and operational risk.
9. Generate Excel workbook and CSV exception exports.
10. Produce a concise management summary linked to output tabs and metrics.

## Required Output Sections

- Executive summary
- Data quality summary
- Reconciliation summary
- Top exceptions by value impact
- Margin and profitability summary
- Manual review queue
- Assumptions and limitations
- Recommended next actions

## Evidence Rule

Every conclusion must reference a source file, output table, row count, metric, exception category, or declared assumption.
```

---

## 11. Recommended Codex / Claude Prompt Pattern

Use this prompt when running the analysis:

```text
Use the invoice-finance-analyst skill.

Analyze only the supplied CSV files. Do not use external financial, market, inflation, CPI, benchmark, or internet data.

Goal:
- reconcile supplier invoice lines against customer sales/billing data;
- validate rates against the supplied rate card if present;
- calculate direct margin by customer, service, product, and billing period;
- identify unmatched, duplicated, stale, and materially changed charges;
- produce a reviewable Excel workbook and exception CSVs;
- produce a concise management summary with all claims tied to calculated tables.

Rules:
- source data is authoritative;
- calculated outputs must be produced by Python/pandas;
- LLM commentary must not override calculated values;
- flag assumptions explicitly;
- create a manual review queue for low-confidence matches.
```

---

## 12. Recommended Custom Metrics

| Metric | Purpose |
|---|---|
| `total_supplier_cost_ex_tax` | Total cost from supplier invoices |
| `total_customer_revenue_ex_tax` | Total revenue from sales/billing CSV |
| `direct_margin` | Revenue minus supplier cost |
| `direct_margin_pct` | Margin percentage |
| `matched_cost_pct` | Percent of supplier cost matched to sales |
| `matched_revenue_pct` | Percent of revenue matched to supplier cost |
| `unmatched_invoice_value` | Supplier charges with no sales match |
| `unmatched_sales_value` | Revenue with no supplier cost match |
| `duplicate_invoice_value` | Duplicate supplier charge exposure |
| `rate_variance_value` | Actual-vs-expected charge difference |
| `negative_margin_value` | Total negative-margin exposure |
| `manual_review_value` | Total value of records needing review |

---

## 13. Final Tool Decision Matrix

| Candidate | Fit for Internal CSV Invoice Analysis | FOSS / Open Source | Use Decision |
|---|---:|---:|---|
| Open Accountant Skills | High | Yes, MIT | Use first |
| Anthropic Knowledge Work Finance Skills | High for reconciliation methodology | Yes, Apache-2.0 | Adapt manually |
| Anthropic Financial Services | Medium | Yes, Apache-2.0 | Reference selectively |
| Alireza finance-skills | Medium-high for variance/forecasting | Appears open-source; verify before production | Trial |
| Composio Invoice Organizer | Medium for PDFs, low for CSV comparison | Check repo license before production | Later |
| Financial Datasets MCP | Low for this use case | MIT per repo page | Avoid Phase 1 |
| Octagon Skills/MCP | Low for this use case | Skills MIT, external API required | Avoid Phase 1 |
| finance-tools-mcp | Low for this use case | License shown, investor-agent oriented | Avoid Phase 1 |
| OpenBB | Low for Phase 1 | Open-source ecosystem | Avoid Phase 1 unless external context is requested |

---

## 14. Practical Next Step

Build a small repo/project called:

`internal-invoice-finance-ai`

Initial deliverables:

1. `skills/invoice-finance-analyst/SKILL.md`
2. `data/mappings/service_mapping.csv`
3. `data/rate_cards/rate_card.csv`
4. `scripts/validate_inputs.py`
5. `scripts/reconcile_invoices.py`
6. `scripts/build_report.py`
7. `runs/<run_id>/outputs/invoice_analysis.xlsx`
8. `runs/<run_id>/outputs/exceptions.csv`
9. `runs/<run_id>/audit/run_summary.json`

First success test:

- provide one supplier invoice CSV and one sales CSV;
- produce matched/unmatched/mismatch tabs;
- generate management summary;
- confirm every number in the summary exists in a calculated output table.

---

## 15. Source Notes

Checked sources include:

- Open Accountant Skills: https://github.com/openaccountant/skills
- Anthropic Knowledge Work Plugins: https://github.com/anthropics/knowledge-work-plugins
- Anthropic Financial Services: https://github.com/anthropics/financial-services
- Anthropic financial modeling skill example: https://github.com/anthropics/claude-cookbooks/blob/main/skills/custom_skills/creating-financial-models/SKILL.md
- Alireza Rezvani Claude Skills finance skill: https://github.com/alirezarezvani/claude-skills/blob/main/finance/skills/finance-skills/SKILL.md
- Composio invoice organizer skill: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/invoice-organizer/SKILL.md
- Financial Datasets MCP: https://github.com/financial-datasets/mcp-server
- Octagon Skills: https://github.com/OctagonAI/skills
- VoxLink finance-tools-mcp: https://github.com/VoxLink-org/finance-tools-mcp

