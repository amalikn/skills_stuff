# Phase 0-4 Gap Review and Solutions

## Contents

- [What Changed Since the Previous Analysis](#what-changed-since-the-previous-analysis)
- [Validation Snapshot](#validation-snapshot)
- [Financial Logic Coverage Snapshot](#financial-logic-coverage-snapshot)
- [Gap 1: Phase 4 Context Selection Is Still a Stub](#gap-1-phase-4-context-selection-is-still-a-stub)
  - [Evidence](#evidence)
  - [Why This Matters](#why-this-matters)
  - [Recommended Solution](#recommended-solution)
- [Gap 2: Service Map Is Loaded but Not Used in Reconciliation](#gap-2-service-map-is-loaded-but-not-used-in-reconciliation)
  - [Evidence](#evidence-1)
  - [Why This Matters](#why-this-matters-1)
  - [Recommended Solution](#recommended-solution-1)
- [Gap 3: Phase 2 Rate Card Matching Ignores Effective Period](#gap-3-phase-2-rate-card-matching-ignores-effective-period)
  - [Evidence](#evidence-2)
  - [Why This Matters](#why-this-matters-2)
  - [Recommended Solution](#recommended-solution-2)
- [Gap 4: Ambient Environment Can Fail Despite the Governed Venv Passing](#gap-4-ambient-environment-can-fail-despite-the-governed-venv-passing)
  - [Evidence](#evidence-3)
  - [Why This Matters](#why-this-matters-3)
  - [Recommended Solution](#recommended-solution-3)
- [Gap 5: Generated Runtime Artifacts Are in the Source Folder](#gap-5-generated-runtime-artifacts-are-in-the-source-folder)
  - [Evidence](#evidence-4)
  - [Why This Matters](#why-this-matters-4)
  - [Recommended Solution](#recommended-solution-4)
- [Gap 6: Tests Depend on Shared `db/` State](#gap-6-tests-depend-on-shared-db-state)
  - [Evidence](#evidence-5)
  - [Why This Matters](#why-this-matters-5)
  - [Recommended Solution](#recommended-solution-5)
- [Gap 7: LLM Evidence Rule Is Prompted but Not Verified](#gap-7-llm-evidence-rule-is-prompted-but-not-verified)
  - [Evidence](#evidence-6)
  - [Why This Matters](#why-this-matters-6)
  - [Recommended Solution](#recommended-solution-6)
- [Gap 8: Phase 0-4 Claims Are Stronger Than Real-Data Validation](#gap-8-phase-0-4-claims-are-stronger-than-real-data-validation)
  - [Evidence](#evidence-7)
  - [Why This Matters](#why-this-matters-7)
  - [Recommended Solution](#recommended-solution-7)
- [Gap 9: Severity Scoring Is Documented but Not Implemented](#gap-9-severity-scoring-is-documented-but-not-implemented)
  - [Evidence](#evidence-8)
  - [Why This Matters](#why-this-matters-8)
  - [Recommended Solution](#recommended-solution-8)
- [Gap 10: Output Formats Still Do Not Match the Framework Fully](#gap-10-output-formats-still-do-not-match-the-framework-fully)
  - [Evidence](#evidence-9)
  - [Why This Matters](#why-this-matters-9)
  - [Recommended Solution](#recommended-solution-9)
- [Gap 11: Installable Skill Packaging Is Still Backlog](#gap-11-installable-skill-packaging-is-still-backlog)
  - [Evidence](#evidence-10)
  - [Why This Matters](#why-this-matters-10)
  - [Recommended Solution](#recommended-solution-10)
- [Gap 12: Missing Reference Docs and Templates](#gap-12-missing-reference-docs-and-templates)
  - [Evidence](#evidence-11)
  - [Why This Matters](#why-this-matters-11)
  - [Recommended Solution](#recommended-solution-11)
- [Gap 13: Credit, Reversal, Refund, and Adjustment Logic Is Not Implemented](#gap-13-credit-reversal-refund-and-adjustment-logic-is-not-implemented)
  - [Evidence](#evidence-12)
  - [Why This Matters](#why-this-matters-12)
  - [Recommended Solution](#recommended-solution-12)
- [Gap 14: GST/Tax Reconciliation Is Only Mentioned, Not Controlled](#gap-14-gsttax-reconciliation-is-only-mentioned-not-controlled)
  - [Evidence](#evidence-13)
  - [Why This Matters](#why-this-matters-13)
  - [Recommended Solution](#recommended-solution-13)
- [Gap 15: Expected Customer Revenue Is Mentioned but Not Implemented](#gap-15-expected-customer-revenue-is-mentioned-but-not-implemented)
  - [Evidence](#evidence-14)
  - [Why This Matters](#why-this-matters-14)
  - [Recommended Solution](#recommended-solution-14)
- [Gap 16: Quantity, Unit Rate, and Proration Logic Is Missing](#gap-16-quantity-unit-rate-and-proration-logic-is-missing)
  - [Evidence](#evidence-15)
  - [Why This Matters](#why-this-matters-15)
  - [Recommended Solution](#recommended-solution-15)
- [Gap 17: Period Boundary Logic Is Too Simple for Real Billing](#gap-17-period-boundary-logic-is-too-simple-for-real-billing)
  - [Evidence](#evidence-16)
  - [Why This Matters](#why-this-matters-16)
  - [Recommended Solution](#recommended-solution-16)
- [Gap 18: Product, Customer, and Supplier Master Data Is Not Modeled Enough](#gap-18-product-customer-and-supplier-master-data-is-not-modeled-enough)
  - [Evidence](#evidence-17)
  - [Why This Matters](#why-this-matters-17)
  - [Recommended Solution](#recommended-solution-17)
- [Gap 19: AR/AP Aging and Payment Status Are Not Implemented](#gap-19-arap-aging-and-payment-status-are-not-implemented)
  - [Evidence](#evidence-18)
  - [Why This Matters](#why-this-matters-18)
  - [Recommended Solution](#recommended-solution-18)
- [Gap 20: Finance Control Totals and Reconciliation Sign-Off Are Missing](#gap-20-finance-control-totals-and-reconciliation-sign-off-are-missing)
  - [Evidence](#evidence-19)
  - [Why This Matters](#why-this-matters-19)
  - [Recommended Solution](#recommended-solution-19)
- [Gap 21: Accounting Boundary and Advice Limits Need a Dedicated Section in `SKILL.md`](#gap-21-accounting-boundary-and-advice-limits-need-a-dedicated-section-in-skillmd)
  - [Evidence](#evidence-20)
  - [Why This Matters](#why-this-matters-20)
  - [Recommended Solution](#recommended-solution-20)
- [Gap 22: `SKILL.md` Needs a Finance-Specific Output Checklist](#gap-22-skillmd-needs-a-finance-specific-output-checklist)
  - [Evidence](#evidence-21)
  - [Why This Matters](#why-this-matters-21)
  - [Recommended Solution](#recommended-solution-21)
- [Recommended Fix Order](#recommended-fix-order)
- [Updated Readiness Assessment](#updated-readiness-assessment)

---

Status: gap review  
Created: 2026-05-21 18:24 Australia/Melbourne  
Scope: Current `invoice-finance-analyst` implementation through Phase 4  
Focus: Remaining gaps, risks, and recommended fixes

## What Changed Since the Previous Analysis

The project moved from a mostly planned skill package to a working Phase 4 implementation.

Major changes now present in the repo:

| Area | Current state |
|---|---|
| Skill instructions | `internal-invoice-analysis/SKILL.md` is now v0.4.0 and marked operational through Phase 4 |
| Phase 1A | `scripts/validate_inputs.py`, `docs/data_contract.md`, examples, and validator tests exist |
| Phase 1B | `scripts/load_inputs.py`, `scripts/invoice_analysis_skeleton.py`, output schema, parquet persistence, and reconciliation tests exist |
| Phase 2 | `scripts/rate_card_analysis.py`, rate-card fixtures, service-map fixtures, and margin/rate tests exist |
| Phase 3 | `scripts/trend_analysis.py`, prior-period fixtures, MoM trend outputs, and trend tests exist |
| Phase 4 | `scripts/llm_analyst.py`, mocked LLM tests, provider-agnostic OpenAI-compatible client support, and `analyst_report.md` schema exist |
| Test baseline | Governed venv test run: `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/` -> 219 passed |

The original high-priority gaps around missing `SKILL.md`, missing scripts, missing data contract, missing examples, and missing tests have largely been closed.

The remaining gaps are now split across two categories:

- **Implementation hardening:** environment reproducibility, service-map integration, output/state routing, prompt-context selection, install packaging, and real-data validation.
- **Financial-method completeness:** credit/reversal handling, GST/tax controls, proration and quantity logic, customer/product hierarchy, AR/AP aging, expected customer revenue validation, deterministic severity, and finance-grade control totals.

## Validation Snapshot

Two test runs were relevant:

| Command | Result | Interpretation |
|---|---:|---|
| `pytest tests/` | 196 passed, 23 errors | Ambient Python 3.11 environment is missing `tabulate`, so markdown-writing tests fail |
| `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/` | 219 passed | Governed Python 3.14.4 venv is valid and matches project policy |

The implementation passes in the intended venv, but the default shell command in `SETUP.md` is ambiguous because it says `pytest tests/` without forcing the governed venv. This can make a healthy project look broken when the wrong interpreter is active.

## Financial Logic Coverage Snapshot

The skill has the right finance-analysis spine: source-data-only reasoning, invoice-to-sales reconciliation, rate-card checks, direct margin, MoM trend detection, anomaly flags, and LLM commentary separated from calculated facts. Those are appropriate for a first internal invoice-analysis skill.

However, the current implementation does not yet cover the full finance/accounting logic expected from a mature invoice-finance analyst. The most important gaps are below.

| Required finance capability | Skill guidance | Python logic | Current adequacy |
|---|---|---|---|
| Source inventory and hashes | Covered | Covered for loaded files | Good |
| Schema/mapping validation | Covered | Covered | Good |
| Invoice-to-sales matching | Covered | Simplified exact key | Partial |
| Service mapping | Covered conceptually | Not used in reconciliation | Gap |
| Rate-card validation | Covered | Supplier cost only, service-type join | Partial |
| Expected customer revenue validation | Mentioned | Not implemented separately | Gap |
| Direct margin | Covered | Implemented | Good for direct margin only |
| Tax/GST separation | Mentioned | Not reconciled or checked | Gap |
| Credits/reversals/refunds | Mentioned | Not classified in outputs | Gap |
| Quantity/unit-rate/proration | Lightly mentioned | Not implemented | Gap |
| Period boundary and partial-month logic | Mentioned | Exact period key only | Gap |
| Product/customer hierarchy | Mentioned | Not implemented | Gap |
| AR/AP aging and payment status | Mentioned as Layer 7 | Not implemented | Gap |
| GL/accounting control totals | Not explicit enough | Not implemented | Gap |
| Deterministic severity/manual queue | Mentioned | Not implemented | Gap |
| Evidence-linked LLM narrative | Covered | Prompted, not validated | Partial |

Bottom line: the skill is strong as a tested CSV reconciliation prototype, but it is not yet a full finance analyst skill. The next design pass should add explicit finance controls to `SKILL.md`, `docs/data_contract.md`, `docs/output_schema.md`, and the scripts.

## Gap 1: Phase 4 Context Selection Is Still a Stub

### Evidence

`scripts/llm_analyst.py` has `_select_context_tables()` documented as a TODO and currently returns all loaded tables.

Current behavior:

```python
return tables  # stub: passes everything
```

### Why This Matters

Phase 4 is marked complete, but the LLM analyst layer still sends more context than necessary. This has four practical problems:

- higher token cost;
- weaker report focus;
- more chance the LLM cites low-signal support tables instead of exception tables;
- poor scaling when real datasets produce wider or larger outputs.

The tests only verify that the function returns a dict and preserves keys. They do not verify that the intended 6-10 priority exception tables are selected.

### Recommended Solution

Implement deterministic priority selection:

```python
priority = [
    "reconciliation_summary",
    "invoice_no_sales",
    "sales_no_invoice",
    "amount_mismatches",
    "rate_card_mismatches",
    "low_margin_exceptions",
    "usage_spikes",
    "recurring_changes",
    "margin_movement",
    "data_quality_issues",
]
return {name: tables.get(name) for name in priority if name in tables}
```

Then update tests to assert:

- selected keys are exactly the priority set when available;
- `run_summary`, `source_file_inventory`, and assumption tables are excluded from exception context;
- assumptions still appear through `_serialize_assumptions()`;
- missing optional Phase 2/3 tables are represented cleanly in data gaps.

## Gap 2: Service Map Is Loaded but Not Used in Reconciliation

### Evidence

The project now includes `service_map_sample.csv`, `mapping_service_map.yaml`, and `db/service_map.parquet`. However, `scripts/invoice_analysis_skeleton.py` still records these assumptions:

- `service_map not yet implemented`;
- `our_service_id_equals_supplier_service_id = True`.

The Phase 1 fixtures also make `Service Ref` values match supplier `LOC*` identifiers, which hides the real-world mapping case.

### Why This Matters

The source framework treats service mapping as strongly recommended, and the data contract defines `service_map` as the bridge between supplier IDs and internal service IDs. If the supplier invoice uses `LOC000001` but sales billing uses `SVC-0001`, current reconciliation will mark both sides unmatched unless the sales file also carries supplier IDs.

This is the highest functional gap for real invoice reconciliation.

### Recommended Solution

Add service-map-aware matching to `invoice_analysis_skeleton.py`:

- accept optional `--service-map db/service_map.parquet`;
- if present, map `sales_billing.our_service_id` to `supplier_service_id`;
- preserve both IDs in output tables;
- record `service_map_used = True` in `assumptions`;
- classify missing map rows as `unmapped_service`, not `sales_only` or `invoice_only`;
- add fixtures where sales uses `SVC-*` IDs and invoices use `LOC*` IDs.

Add tests for:

- mapped supplier/internal IDs match correctly;
- missing service-map entry creates `unmapped_service`;
- conflicting service-map rows fail clearly;
- inactive service-map rows can be flagged or excluded according to an explicit policy.

## Gap 3: Phase 2 Rate Card Matching Ignores Effective Period

### Evidence

`scripts/rate_card_analysis.py` resolves the rate card by sorting on `effective_date` and taking the most recent row per `service_type`.

The assumptions table states:

> Multiple effective dates allowed; most recent wins. Period-aware selection deferred to Phase 3.

Phase 3 is now complete, but period-aware rate selection is still not implemented.

### Why This Matters

Real rate cards are temporal. If an older invoice period is rerun after a later rate card has been loaded, the current logic may compare historical invoices against future rates.

This can create false rate-card mismatches or hide genuine overcharges.

### Recommended Solution

Implement period-aware rate-card selection:

- join matched lines to rate card on `service_type`;
- require `effective_date <= billing_period_start`;
- if `expiry_date` exists, require `billing_period_start <= expiry_date`;
- choose the latest effective rate within the valid window;
- if no valid rate exists, set `no_rate_card_entry = True`;
- update `phase2_assumptions` from `most_recent_effective_date_per_service_type` to `period_valid_rate_selection`.

Add tests for:

- current period uses current rate;
- prior period uses older rate;
- expired rate does not match;
- future effective rate does not match historical billing;
- overlapping rates fail or resolve by deterministic latest-effective policy.

## Gap 4: Ambient Environment Can Fail Despite the Governed Venv Passing

### Evidence

Running `pytest tests/` in the ambient shell used Python 3.11 and failed with 23 errors because `tabulate` was missing. Running the governed venv pytest passed all 219 tests.

### Why This Matters

The docs claim `pytest tests/` passes, but that is only true after activating or explicitly using the governed venv. Agents and users can easily run the wrong command and misdiagnose the project.

### Recommended Solution

Make validation commands venv-explicit:

```bash
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/
```

Also add one of:

- `requirements.txt` with exact runtime/test dependencies;
- `pyproject.toml` with dependencies and dev dependencies;
- a `run_tests.sh` wrapper that uses the governed venv;
- update `SETUP.md` to say ambient `pytest` is not authoritative.

Minimum dependency list:

- `pandas`;
- `pyarrow`;
- `pyyaml`;
- `tabulate`;
- `openai`;
- `pytest`;
- `openpyxl` only when Excel output is implemented.

## Gap 5: Generated Runtime Artifacts Are in the Source Folder

### Evidence

The repo now contains:

- `db/*.parquet`;
- `output/<run_id>/*.md`;
- `pytest-of-malik.ahmad/...` temp output;
- `.pytest_cache/`.

The folder has `.gitignore` files only under `.remember/` and `.pytest_cache/`, not a project-level `.gitignore`.

### Why This Matters

Local policy says ephemeral runtime state should go under:

```text
/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/
```

The current implementation writes operational artifacts into the authoring source folder. That increases the chance of committing generated outputs, polluting searches, and mixing source-of-truth code with run state.

### Recommended Solution

Move default runtime outputs out of the source tree:

```text
/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/db/
/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/output/
```

Then:

- add CLI flags or env vars for `--db` and `--output-dir` across all scripts;
- make tests use `tmp_path` or a temporary runtime root instead of project `db/`;
- add a project `.gitignore` for `db/`, `output/`, `.pytest_cache/`, `pytest-of-*`, and generated report artifacts if the source-tree fallback remains supported;
- document the runtime root in `SETUP.md`.

## Gap 6: Tests Depend on Shared `db/` State

### Evidence

`tests/test_reconciliation.py` reads `db/invoice.parquet` and `db/sales_billing.parquet`, skipping if missing. Phase 2 tests autoload some parquets but still require `matched_lines.parquet` to already exist.

### Why This Matters

The tests pass in the current environment because expected parquets already exist. That makes the suite partly stateful. A clean checkout or runtime-root move may fail or skip important tests unless setup steps are run in the right order.

### Recommended Solution

Make tests self-contained:

- use `tmp_path` for db/output paths;
- build required parquets from `examples/` inside fixtures;
- monkeypatch script-level `DB` values where needed;
- avoid reading project `db/` directly in tests;
- assert that a clean run can start from examples only.

This will also make CI or future agent validation more reliable.

## Gap 7: LLM Evidence Rule Is Prompted but Not Verified

### Evidence

The system prompt requires every statement to include citations in this format:

```text
[table: <name> | metric: <column_or_aggregate> | value: <value>]
```

The tests mock the LLM call and verify plumbing, report writing, and prompt content. They do not validate that returned analyst reports comply with the evidence citation rule.

### Why This Matters

The Phase 4 exit criteria depend on evidence-linked commentary. A model can ignore instructions or produce partial citations. Without post-generation validation, unsupported claims can enter `analyst_report.md`.

### Recommended Solution

Add a report validator:

- parse generated markdown by section;
- require citations on every non-heading, non-table prose sentence;
- check citation table names are among loaded tables;
- optionally verify cited metrics/values exist in the serialized context;
- fail the run or mark the report invalid if citation coverage is incomplete.

Add tests with mocked LLM output:

- fully cited report passes;
- uncited sentence fails;
- unknown table citation fails;
- missing required section fails;
- external-data language fails unless explicitly enabled.

## Gap 8: Phase 0-4 Claims Are Stronger Than Real-Data Validation

### Evidence

The implementation has strong fixture coverage and 219 tests passing in the governed venv. However, fixtures are intentionally small and simplified:

- sales IDs match supplier IDs in Phase 1;
- one supplier and one current/prior period shape;
- rate card matches by service type only;
- no mixed currencies;
- no tax edge cases;
- no large-file performance test;
- no ambiguous date parsing stress case beyond validator-level tests;
- no real API/provider run for Phase 4.

### Why This Matters

The phrase “operational” is defensible for fixture-backed local operation, but not yet for messy production exports.

### Recommended Solution

Add a real-data readiness gate:

- run the full pipeline on a copied real invoice/sales/rate-card export;
- record source hashes and row counts;
- inspect exception categories manually;
- compare totals against known accounting/source-system totals;
- validate Phase 4 report quality with a local/Ollama or chosen provider run;
- capture a dated outcome document under `docs/`.

Until then, describe status as:

> Operational on fixture-backed local pipeline; pending real-export validation.

## Gap 9: Severity Scoring Is Documented but Not Implemented

### Evidence

`SKILL.md`, `ARCHITECTURE.md`, and the framework describe deterministic severity scoring:

```text
severity_score = value_impact_score + recurrence_score + confidence_score + operational_risk_score
```

No Python implementation currently generates `exception_categories`, `manual_review_queue`, or deterministic severity scores across exceptions.

### Why This Matters

Phase 4 asks the analyst report to discuss highest-severity items. Without computed severity, the LLM either has to infer priority from raw tables or use vague language.

### Recommended Solution

Create `scripts/severity_analysis.py` or add a shared severity module:

- normalize exceptions from `invoice_no_sales`, `sales_no_invoice`, `amount_mismatches`, `rate_card_mismatches`, `low_margin_exceptions`, `usage_spikes`, and `recurring_changes`;
- compute value impact from dollar columns;
- compute recurrence from current/prior presence or repeated service/customer patterns;
- compute confidence from match type and data quality issues;
- compute operational risk from category;
- output `exception_categories.parquet` and `manual_review_queue.parquet`;
- make Phase 4 use these tables instead of asking the LLM to infer severity.

## Gap 10: Output Formats Still Do Not Match the Framework Fully

### Evidence

Current outputs include parquet and markdown. The roadmap still lists:

- Excel workbook output;
- CSV exports such as `exceptions.csv`, `matched_lines.csv`, `profitability_by_customer.csv`, `run_summary.json`.

`docs/output_schema.md` says CSV export was deferred.

### Why This Matters

Parquet is good for machine processing, but finance users often need Excel/CSV deliverables for review, dispute workflows, and handoff to operations.

### Recommended Solution

Add a dedicated export phase before or alongside Phase 5:

- `scripts/export_reports.py`;
- CSV output for every exception table;
- `run_summary.json`;
- optional Excel workbook with one tab per key table;
- README tab in the workbook with assumptions, thresholds, hashes, and run ID.

Do this after service-map and period-aware rate-card matching are fixed so the workbook does not freeze an incomplete data model.

## Gap 11: Installable Skill Packaging Is Still Backlog

### Evidence

`ROADMAP.md` still lists install to `~/.claude/skills/` and `~/.codex/skills/` as backlog. The README also shows the source folder, tests, examples, db, and output all together.

### Why This Matters

The authoring repo is now useful, but it is not yet cleanly packaged as a reusable installed skill. Runtime install surfaces should not include tests, generated outputs, old run artifacts, or project-management docs.

### Recommended Solution

Create an explicit package/export step:

```text
internal-invoice-analysis/
├── SKILL.md
├── scripts/
├── references/
│   ├── data_contract.md
│   ├── output_schema.md
│   └── assumptions_and_limits.md
└── templates/
```

Then:

- copy only runtime files to `~/.codex/skills/internal-invoice-analysis/`;
- copy only runtime files to `~/.claude/skills/internal-invoice-analysis/`;
- validate installed skill paths;
- record installed version and source commit/hash in `ROADMAP.md` or a dated outcome doc.

## Gap 12: Missing Reference Docs and Templates

### Evidence

Backlog items still include:

- `templates/`;
- `docs/analysis_layers.md`;
- `docs/assumptions_and_limits.md`.

### Why This Matters

The functionality exists, but some reusable guidance is still embedded across `SKILL.md`, `ARCHITECTURE.md`, and `output_schema.md`. That is okay for authoring, but installed-skill users need concise reference docs and templates.

### Recommended Solution

Create:

- `docs/analysis_layers.md` as a concise explanation of each layer and script;
- `docs/assumptions_and_limits.md` as the single reference for external-data ban, tax/accounting limits, no guessing, and visible assumptions;
- `templates/findings_report_template.md`;
- `templates/reconciliation_report_template.md`;
- `templates/supplier_dispute_template.md`;
- `templates/internal_ticket_template.md`.

Move detailed installed-skill references under `internal-invoice-analysis/references/` during packaging.

## Gap 13: Credit, Reversal, Refund, and Adjustment Logic Is Not Implemented

### Evidence

`SKILL.md` says negative values should be classified as credit, reversal, or error. The current scripts validate numeric values but do not create credit/reversal/adjustment classifications, link credits to prior overcharges, or separate credits from recurring charges in output tables.

### Why This Matters

Supplier invoice exports often include credits, reversals, backdated adjustments, rebates, refunds, once-off corrections, and negative usage lines. Treating all negative values as ordinary amounts can distort:

- direct margin;
- rate-card variance;
- MoM trend;
- low-margin exceptions;
- supplier dispute totals;
- customer profitability.

For example, a legitimate supplier credit can look like a negative cost anomaly, while an unmatched reversal may indicate a prior-period overcharge that should be tied to a previous exception.

### Recommended Solution

Add a deterministic charge classification layer:

- classify `charge_type` into `recurring`, `usage`, `once_off`, `credit`, `reversal`, `adjustment`, `tax`, and `unknown`;
- infer classification from explicit source fields first, then from sign/description heuristics;
- preserve raw description and raw amount;
- create `credits_and_reversals.parquet`;
- add `linked_prior_exception_id` or `linked_prior_service_period` when a credit maps to a previous overcharge;
- exclude credits/reversals from recurring-rate checks unless explicitly configured;
- include net and gross views: `gross_supplier_cost`, `credit_total`, `net_supplier_cost`.

Update `SKILL.md` with a rule that credits must be explained separately from recurring supplier cost and must not silently improve margin.

## Gap 14: GST/Tax Reconciliation Is Only Mentioned, Not Controlled

### Evidence

The skill requires tax/GST separation and says not to mix tax into ex-tax comparisons. The scripts primarily use ex-tax fields and do not verify that:

- `amount_inc_tax = amount_ex_tax + tax_amount`;
- tax rates are plausible;
- GST treatment is consistent between supplier invoice and sales billing;
- tax-only rows are excluded from margin;
- tax rounding differences are isolated from real amount mismatches.

### Why This Matters

Finance users will expect confidence that margin and rate variances are ex-GST and that GST rows are not corrupting profitability. In Australia, GST treatment is a recurring control point. A tax-inclusive amount mapped into an ex-tax field can generate false margin/rate exceptions.

### Recommended Solution

Add tax-control outputs:

- `tax_reconciliation.parquet`;
- `tax_anomalies.parquet`;
- `tax_treatment_assumptions.parquet`.

Rules:

- if `amount_inc_tax` and `tax_amount` exist, verify `amount_ex_tax + tax_amount` within rounding tolerance;
- flag tax rates outside configured GST tolerance, e.g. 10% where applicable;
- classify tax-only rows and exclude them from direct margin;
- record whether each source file is ex-tax, inc-tax, mixed, or unknown;
- fail or warn when the mapping uses likely inc-tax columns for ex-tax canonical fields.

Update tests with a fixture containing a tax-inclusive mapping mistake and a legitimate rounding-only GST difference.

## Gap 15: Expected Customer Revenue Is Mentioned but Not Implemented

### Evidence

`SKILL.md` says Step 7 should calculate `expected_customer_revenue`, and Step 9 mentions `revenue_rate_variance`. The current Phase 2 script validates expected supplier cost from `rate_card`, but there is no separate customer sell-rate card, product price book, contract price, or expected customer revenue table.

### Why This Matters

An invoice-finance analyst must answer two separate questions:

1. Did the supplier charge us the correct cost?
2. Did we bill the customer the correct sell price?

Current logic can compare supplier invoice cost to expected supplier cost and calculate actual direct margin. It cannot yet prove whether customer revenue is correct against a contract, plan, or sell-rate card.

### Recommended Solution

Add a `customer_rate_card` or `price_book` source type:

Required fields:

- `customer_id` or customer segment;
- `our_service_id` or product/plan key;
- `service_type` / `product_code`;
- `expected_revenue_ex_tax`;
- `effective_date`;
- optional `expiry_date`, `contract_id`, `discount_code`, `minimum_charge`.

Add outputs:

- `customer_revenue_variances.parquet`;
- `customer_price_card_mismatches.parquet`;
- `sell_rate_assumptions.parquet`.

Keep supplier cost rate-card checks separate from customer revenue checks. A supplier overcharge and a customer underbilling are different root causes and should not collapse into one variance type.

## Gap 16: Quantity, Unit Rate, and Proration Logic Is Missing

### Evidence

The data contract includes `quantity` and `unit_price_ex_tax`, and `SKILL.md` mentions quantity and usage spikes. The scripts currently calculate totals from line amounts and do not validate quantity × unit rate, partial-month proration, or usage-tier pricing.

### Why This Matters

Many invoice discrepancies are not line-total errors. They come from:

- wrong quantity;
- wrong unit rate;
- partial-month service activation/cancellation;
- usage overage billed at wrong tier;
- minimum charges;
- bundled services split across several rows.

Without unit-rate and proration checks, a line can appear to have the correct total only because two errors offset each other, or a legitimate partial charge can be incorrectly flagged.

### Recommended Solution

Add line-level rate math:

- compute `calculated_amount_ex_tax = quantity * unit_price_ex_tax`;
- compare calculated amount to source amount;
- support optional `billable_days`, `period_days`, and `proration_factor`;
- add `unit_rate_variances.parquet`;
- add `proration_exceptions.parquet`;
- distinguish recurring full-period charges from usage or once-off charges.

Update `SKILL.md` Step 7/9 to require validation at both total-line and unit-rate levels when quantity/rate fields are available.

## Gap 17: Period Boundary Logic Is Too Simple for Real Billing

### Evidence

Current reconciliation joins on `supplier_service_id + billing_period_start`. It does not reason about overlapping periods, partial overlaps, late invoices, backdated credits, billing-in-advance, billing-in-arrears, or period-end mismatches.

### Why This Matters

Supplier invoices and customer billing exports often do not align perfectly by period:

- supplier bills March usage in April;
- customer invoice is generated mid-month;
- a service is activated or cancelled mid-period;
- credits apply to prior periods;
- one supplier line spans multiple customer billing lines.

Exact period matching will overstate unmatched records in these cases.

### Recommended Solution

Add period matching modes:

- exact period;
- overlapping period;
- same calendar month;
- billing-in-advance;
- billing-in-arrears;
- manual override.

Add fields:

- `period_match_type`;
- `period_overlap_days`;
- `period_confidence`;
- `billing_lag_days`;
- `period_exception_reason`.

Keep exact matching as the default for Phase 1, but expose period mismatch as a first-class output instead of only an implied unmatched state.

## Gap 18: Product, Customer, and Supplier Master Data Is Not Modeled Enough

### Evidence

The framework mentions `customer_master.csv` and `product_master.csv`, but the implemented data contract and scripts focus on invoice, sales, rate card, and service map. There is no customer segment, account owner, product hierarchy, supplier account, region/site, or business-unit model.

### Why This Matters

Management-facing profitability and remediation need grouping beyond raw service IDs:

- customer;
- product family;
- technology type;
- supplier;
- region/site;
- account manager;
- business unit;
- service status.

Without master data, the system can find exceptions but cannot prioritize ownership, escalation, or recurring structural profitability issues properly.

### Recommended Solution

Add optional master-data source types:

- `customer_master`;
- `product_master`;
- `supplier_master`;
- `service_status`.

Add output aggregations:

- `profitability_by_product.parquet`;
- `profitability_by_customer_segment.parquet`;
- `exceptions_by_account_owner.parquet`;
- `exceptions_by_supplier_account.parquet`;
- `ceased_service_charges.parquet`.

Update `SKILL.md` to say master data is optional but should be used for ownership, grouping, and escalation when supplied.

## Gap 19: AR/AP Aging and Payment Status Are Not Implemented

### Evidence

Layer 7 exists in the architecture and `SKILL.md`, but there is no `payments` data contract, no aging script, and no outputs such as `ar_aging`, `ap_aging`, or `payment_mismatches`.

### Why This Matters

Invoice analysis is not only about whether charges match. Finance teams also need to know:

- which supplier invoices are unpaid;
- which customer invoices are overdue;
- whether credits have been received or applied;
- whether supplier disputes should hold payment;
- whether customer underbilling or non-payment affects cash flow.

Without aging/payment logic, the skill cannot support invoice run closeout, dispute hold decisions, or cash-impact prioritization.

### Recommended Solution

Add a later Phase 4B or Phase 5A before accounting MCP:

- define `payments` and `invoice_status` source types;
- add `scripts/aging_analysis.py`;
- output `ar_aging.parquet`, `ap_aging.parquet`, `payment_mismatches.parquet`, `dispute_hold_candidates.parquet`;
- compute days overdue, partial payments, unpaid balance, paid date, and payment reference matching;
- keep this CSV-first before adding live accounting-system MCP.

## Gap 20: Finance Control Totals and Reconciliation Sign-Off Are Missing

### Evidence

The pipeline records row counts and hashes, but it does not yet create finance-grade control totals across stages. There is no explicit sign-off table that proves source totals tie to normalized totals and output totals.

### Why This Matters

Finance users need to trust that transformation did not lose or duplicate money. A proper reconciliation workflow should prove:

- source invoice total equals normalized invoice total;
- source sales total equals normalized sales total;
- matched + unmatched + excluded totals reconcile to source totals;
- tax-only and credit lines are accounted for;
- every exclusion is visible.

### Recommended Solution

Add `control_totals.parquet` with rows such as:

- `source_invoice_amount_ex_tax_total`;
- `normalized_invoice_amount_ex_tax_total`;
- `matched_invoice_total`;
- `invoice_no_sales_total`;
- `duplicate_removed_total`;
- `credit_total`;
- `tax_only_total`;
- `excluded_total`;
- `reconciliation_difference`.

Add a final `run_signoff_status`:

- `pass` when totals tie within tolerance and no high-severity data-quality issue exists;
- `review_required` when totals tie but exceptions exist;
- `fail` when totals do not tie or required data is missing.

Make Phase 4 analyst reports cite `control_totals` before making any confidence claim.

## Gap 21: Accounting Boundary and Advice Limits Need a Dedicated Section in `SKILL.md`

### Evidence

The current hard rules correctly prevent external data use and invented values. The skill does not yet have a dedicated accounting-boundary section that states it is not final tax, audit, or accounting sign-off advice.

### Why This Matters

The tool is operationally close to accounting workflows. Without an explicit boundary, a generated report may be mistaken for final accounting treatment, audit evidence, or tax advice.

### Recommended Solution

Add a `Finance and Accounting Boundaries` section to `SKILL.md`:

- reports are operational analysis, not final accounting/tax/audit sign-off;
- GST/tax treatment must be verified by finance before lodgement or accounting entries;
- journal entries, write-offs, credits, and customer refunds require human approval;
- supplier dispute drafts are drafts only;
- confidence ratings reflect data completeness and reconciliation coverage, not audit assurance.

Mirror this in `docs/assumptions_and_limits.md` when that file is created.

## Gap 22: `SKILL.md` Needs a Finance-Specific Output Checklist

### Evidence

`SKILL.md` requires nine response sections, but it does not explicitly require finance-specific checks such as control totals, credit handling, GST status, rate-card coverage, service-map coverage, or payment/aging availability.

### Why This Matters

The LLM may produce a report with the right headings but omit critical finance review points.

### Recommended Solution

Add a required `Finance control checklist` inside the report, or include these bullets under `Calculated findings` / `Data gaps`:

- source invoice total and normalized invoice total tie-out;
- source sales total and normalized sales total tie-out;
- GST/tax status: ex-tax, inc-tax, mixed, or unknown;
- credit/reversal total and handling;
- rate-card coverage percentage;
- service-map coverage percentage;
- unmatched supplier cost exposure;
- unmatched customer revenue exposure;
- negative and low-margin exposure;
- AR/AP aging supplied or absent;
- manual review queue count by severity.

This checklist should be calculated by Python, not invented by the LLM.

## Recommended Fix Order

1. Make tests self-contained and venv-explicit.
2. Add a project `.gitignore` or move generated runtime state out of the source tree.
3. Implement service-map-aware reconciliation.
4. Add control totals and sign-off status.
5. Add credit/reversal/tax/GST classification before expanding reporting.
6. Implement period-aware rate-card selection.
7. Add expected customer revenue / sell-rate validation.
8. Implement `_select_context_tables()` and tighten Phase 4 tests.
9. Add LLM report citation validation.
10. Add deterministic severity and manual-review queue outputs.
11. Add quantity/unit-rate/proration logic.
12. Run a real-export validation and save a dated outcome doc.
13. Add CSV/JSON/Excel export layer.
14. Package and install the runtime skill into Codex/Claude skill directories.

## Updated Readiness Assessment

| Phase | Status | Assessment |
|---|---|---|
| Phase 0 | Complete | Skill instructions and hard rules are strong |
| Phase 1A | Complete | Validator/data contract/examples are in place; tests pass in governed venv |
| Phase 1B | Mostly complete | Reconciliation works for simplified ID-equal fixtures; service-map matching remains a real-world gap |
| Phase 2 | Partially complete | Supplier rate/margin outputs work; period-aware rates, expected customer revenue, tax/GST, credits, and proration remain unresolved |
| Phase 3 | Complete for fixture scope | MoM trend works on controlled prior-period fixtures; period overlap, credits, and product/customer hierarchy still need real-world handling |
| Phase 4 | Partially complete | LLM plumbing works; context selection, citation validation, finance checklist, and control-total confidence need implementation |
| Phase 5 | Backlog | Correctly deferred until CSV export becomes a bottleneck |

Overall: the project has advanced substantially and is now a tested local pipeline. The remaining work is less about scaffolding and more about making the skill finance-complete: service mapping, period-aware rates, customer sell-rate validation, GST/tax controls, credit/reversal handling, control totals, deterministic severity, aging/payment support, real-export validation, reproducible execution, and clean skill distribution.
