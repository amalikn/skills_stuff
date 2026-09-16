# Current Implementation Gap Review — Phase 0 to Phase 5

Created: 2026-05-22 00:53 Australia/Melbourne  
Scope: Current repository implementation of the `internal-invoice-analysis` skill, including docs, skill instructions, scripts, examples, and tests.  
Purpose: Identify what has changed since the prior gap review, assess implementation maturity across all phases, and provide gap-focused remediation guidance.

## Contents

- [Executive Summary](#executive-summary)
- [What Has Changed Since The Last Analysis](#what-has-changed-since-the-last-analysis)
  - [Implemented Or Substantially Improved](#implemented-or-substantially-improved)
  - [Root Governance Files Reviewed In This Pass](#root-governance-files-reviewed-in-this-pass)
- [Current Phase Assessment](#current-phase-assessment)
- [Gap Ledger And Recommended Solutions](#gap-ledger-and-recommended-solutions)
  - [Gap 1 — Phase Status Is Inconsistent Across Repository Docs](#gap-1--phase-status-is-inconsistent-across-repository-docs)
  - [Gap 1A — README Still Mixes Original Build Spec With Current Implementation](#gap-1a--readme-still-mixes-original-build-spec-with-current-implementation)
  - [Gap 1B — Architecture Diagram Describes Target Behavior As If It Exists](#gap-1b--architecture-diagram-describes-target-behavior-as-if-it-exists)
  - [Gap 2 — Finance Control Checklist Is Documented But Not Computed](#gap-2--finance-control-checklist-is-documented-but-not-computed)
  - [Gap 3 — LLM Citation Rule Is Prompt-Only](#gap-3--llm-citation-rule-is-prompt-only)
  - [Gap 4 — Phase 4 Context Selection Still Misses Some Control Inputs](#gap-4--phase-4-context-selection-still-misses-some-control-inputs)
  - [Gap 5 — Deterministic Severity Scoring Is Missing](#gap-5--deterministic-severity-scoring-is-missing)
  - [Gap 6 — Service-Map-Aware Reconciliation Is Not Implemented](#gap-6--service-map-aware-reconciliation-is-not-implemented)
  - [Gap 7 — Control Totals And Run Sign-Off Are Missing](#gap-7--control-totals-and-run-sign-off-are-missing)
  - [Gap 8 — Rate-Card Selection Is Not Period-Aware](#gap-8--rate-card-selection-is-not-period-aware)
  - [Gap 9 — Period Boundary Matching Modes Are Missing](#gap-9--period-boundary-matching-modes-are-missing)
  - [Gap 10 — Credit, Reversal, GST, And Tax Classification Are Not Implemented](#gap-10--credit-reversal-gst-and-tax-classification-are-not-implemented)
  - [Gap 11 — Customer Sell-Rate / Price Book Logic Is Missing](#gap-11--customer-sell-rate--price-book-logic-is-missing)
  - [Gap 12 — Quantity, Unit Price, And Proration Checks Are Not Implemented](#gap-12--quantity-unit-price-and-proration-checks-are-not-implemented)
  - [Gap 13 — Tests Depend On Shared `db/` State](#gap-13--tests-depend-on-shared-db-state)
  - [Gap 14 — Runtime Path Routing Is Only Partially Implemented](#gap-14--runtime-path-routing-is-only-partially-implemented)
  - [Gap 15 — Lineage And Phase Status Artifacts Are Missing](#gap-15--lineage-and-phase-status-artifacts-are-missing)
  - [Gap 16 — Dependency Manifest Is Missing](#gap-16--dependency-manifest-is-missing)
  - [Gap 17 — Output Export Layer Is Still Incomplete](#gap-17--output-export-layer-is-still-incomplete)
  - [Gap 18 — LLM Prompt Does Not Yet Match The New Finance Control Requirements](#gap-18--llm-prompt-does-not-yet-match-the-new-finance-control-requirements)
  - [Gap 19 — Structured LLM Output Is Not Implemented](#gap-19--structured-llm-output-is-not-implemented)
  - [Gap 20 — Output Schema Is Ahead Of Some Runtime Tables](#gap-20--output-schema-is-ahead-of-some-runtime-tables)
  - [Gap 21 — Real-Export Validation Is Still Missing](#gap-21--real-export-validation-is-still-missing)
  - [Gap 22 — Skill Package Boundary Is Still Not Final](#gap-22--skill-package-boundary-is-still-not-final)
  - [Gap 22A — Missing User-Facing Reference Docs And Templates Are Still Open](#gap-22a--missing-user-facing-reference-docs-and-templates-are-still-open)
  - [Gap 22B — Parent Registry / Install Readiness Needs Final Verification](#gap-22b--parent-registry--install-readiness-needs-final-verification)
  - [Gap 23 — MCP / Accounting-System Integration Should Remain Deferred](#gap-23--mcp--accounting-system-integration-should-remain-deferred)
- [Recommended Remediation Order](#recommended-remediation-order)
  - [Immediate Cleanup](#immediate-cleanup)
  - [Phase 4b — Finance Control Foundation](#phase-4b--finance-control-foundation)
  - [Phase 4c — Governed LLM Analyst](#phase-4c--governed-llm-analyst)
  - [Phase 4d — Production Usability](#phase-4d--production-usability)
  - [Phase 4e / Phase 5 — Packaging And Integrations](#phase-4e--phase-5--packaging-and-integrations)
- [Acceptance Criteria For Closing The Main Remaining Gaps](#acceptance-criteria-for-closing-the-main-remaining-gaps)
- [Validation Performed For This Review](#validation-performed-for-this-review)
- [Contradiction Check](#contradiction-check)

---

## Executive Summary

The project has advanced significantly since the earlier analysis. It is no longer only an instruction draft and framework document. The repository now has a runnable CSV-to-parquet pipeline, deterministic reconciliation logic, rate-card and margin analysis, MoM trend analysis, an LLM analyst wrapper, examples, output schema documentation, feedback artifacts, and a passing pytest suite.

The core design remains sound:

- Source files are treated as read-only.
- Numeric findings are calculated by Python/pandas.
- LLM output is positioned as commentary, not the source of numeric truth.
- External market, CPI, inflation, stock, and macro data remain prohibited by default.
- The skill now includes explicit finance/accounting boundaries and a finance control checklist.

The main remaining risk is not basic project direction. The risk is **claiming finance-grade completeness before the deterministic controls exist**. The tests prove the current fixture workflow works. They do not yet prove readiness for messy production invoice exports, real service identifier mapping, rate-card validity periods, tax/credit handling, finance control sign-off, citation validation, or repeatable packaging as an installed skill.

---

## What Has Changed Since The Last Analysis

### Implemented Or Substantially Improved

1. **Phase 1A validator exists and is tested**
   - `scripts/validate_inputs.py` validates CSV existence, extension, mapping presence, required fields, numeric/date parseability, duplicates, null counts, source hash integrity, and heuristic mapping suggestions.
   - `tests/test_validate_inputs.py` covers the original Phase 1A acceptance criteria.

2. **Phase 1B reconciliation skeleton exists**
   - `scripts/load_inputs.py` loads CSVs into canonical parquet.
   - `scripts/invoice_analysis_skeleton.py` writes the Phase 1B output tables documented in `docs/output_schema.md`.
   - Deterministic outputs include `run_summary`, `source_file_inventory`, `data_quality_issues`, `reconciliation_summary`, `matched_lines`, `invoice_no_sales`, `sales_no_invoice`, `amount_mismatches`, and `assumptions`.

3. **Phase 2 rate-card and margin analysis exists**
   - `scripts/rate_card_analysis.py` produces `rate_variances`, `rate_card_mismatches`, `margin_by_customer`, `margin_by_service_type`, `low_margin_exceptions`, and `phase2_assumptions`.
   - Tests cover expected fixture outcomes and synthetic low-margin cases.

4. **Phase 3 trend analysis exists**
   - `scripts/trend_analysis.py` compares current and prior invoice/sales periods.
   - It detects new services, removed services, usage spikes, recurring changes, and margin movement.

5. **Phase 4 LLM analyst wrapper exists**
   - `scripts/llm_analyst.py` loads Phase 1B/2/3 parquet tables.
   - It supports OpenAI-compatible providers through `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and model CLI flags.
   - LLM tests are offline and mock the API call.
   - `_select_context_tables()` has been implemented, which closes a previous high-priority TODO.

6. **Governance and documentation have improved**
   - `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `SETUP.md`, `docs/data_contract.md`, `docs/output_schema.md`, and `internal-invoice-analysis/SKILL.md` now reflect much more of the intended pipeline.
   - `docs/feedback/` now holds previous review and plan artifacts.
   - `.gitignore` excludes `db/`, `output/`, pytest cache, Python bytecode, and local memory artifacts.

7. **Tests currently pass**
   - Validation run: `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/`
   - Result: `219 passed in 1.59s`.

### Root Governance Files Reviewed In This Pass

The review was checked against the root project governance and status files, not only the scripts:

| File | Current Role | Notes From Review |
|---|---|---|
| `AGENTS.md` | Local policy | Confirms this folder is the canonical authoring surface; `SKILL.md` is source of truth for skill behavior; runtime state belongs outside the source tree. |
| `CLAUDE.md` | Claude wrapper | Correctly thin: imports `AGENTS.md` and has no local duplication. |
| `README.md` | Status and build spec | Useful folder overview, but overstates Phase 4 completion and still contains older build-spec requirements that do not match the current implementation. |
| `ROADMAP.md` | Forward plan | Most accurate current plan. It already classifies Phase 4 as partial and lists 4a-4e remediation. |
| `ARCHITECTURE.md` | Target architecture | Strong design reference, but several layers describe intended behavior that is not yet implemented. |
| `SETUP.md` | Runtime setup | Good invocation reference; still depends on manual package installation and mentions Excel dependency before the export layer exists. |
| `SCRATCHPAD.md` | Current working state | Contains useful next actions, but the current-state section still says Phase 4 complete. |
| `.claude/settings.local.json` | Local Claude permissions | Local-only permissions exist for selected commands; no issue, but this should not be treated as portable project setup. |

---

## Current Phase Assessment

| Phase | Current State | Assessment |
|---|---|---|
| Phase 0 — instruction-only skill and repo cleanup | Mostly complete | Core rules, docs, and skill instructions exist. Some status claims are inconsistent across docs. |
| Phase 1A — CSV validator | Implemented and tested | Good foundation. Needs stronger business-rule validation before production use. |
| Phase 1B — minimal reconciliation | Implemented for fixture shape | Works for exact service ID and period joins. Not yet production-grade because service mapping, control totals, and period boundary modes are missing. |
| Phase 2 — rate-card and margin | Implemented for simple service-type rates | Useful first version. Needs period-aware rates, customer sell-rate logic, tax/credit handling, and coverage/sign-off controls. |
| Phase 3 — trend/anomaly | Implemented for prior/current period comparisons | Good deterministic baseline. Needs persistent run history and richer classification before it becomes a monitoring layer. |
| Phase 4 — LLM analyst layer | Partially implemented | Wrapper and prompt exist. Citation validation, structured output, deterministic severity, and finance-control checklist enforcement are missing. |
| Phase 5 — optional integrations/backlog | Not implemented | Correctly left as backlog. Should remain deferred until Phase 4b/4c controls are implemented. |

---

## Gap Ledger And Recommended Solutions

### Gap 1 — Phase Status Is Inconsistent Across Repository Docs

**Evidence**

- `ROADMAP.md` says the current phase is **Phase 4 — partially complete**.
- `README.md`, `SCRATCHPAD.md`, and `internal-invoice-analysis/SKILL.md` still describe Phase 4 as complete or operational.
- `SKILL.md` says `pytest 219/219` and "Phase 4 complete", while `ROADMAP.md` still lists missing Phase 4 exit criteria such as citation validation and deterministic severity scoring.
- `ARCHITECTURE.md` marks the LLM analyst as Phase 4 complete while also stating deterministic severity is an invariant, even though severity scoring is not implemented.

**Why It Matters**

This is a governance and user-trust issue. A skill can be runnable without being complete. The repo should not tell users the LLM analyst phase is complete while core Phase 4 finance controls remain prompt-only.

**Recommended Solution**

Normalize all status language:

- Use "Phase 4 runnable, not finance-control complete" until citation validation, structured output, and deterministic severity are implemented.
- Add a single status table in `README.md` and point `SCRATCHPAD.md`, `ROADMAP.md`, and `SKILL.md` to it.
- Separate "tests pass" from "phase complete". Passing fixture tests should be reported as validation evidence, not as full phase completion.
- In `ARCHITECTURE.md`, distinguish "implemented now" from "target architecture" inside the layer diagram.

---

### Gap 1A — README Still Mixes Original Build Spec With Current Implementation

**Evidence**

`README.md` has a "Build spec" section that still asks for older or not-yet-created artifacts:

- `templates/`
- `docs/analysis_layers.md`
- `docs/assumptions_and_limits.md`
- functions such as `load_csv`, `profile_dataframe`, `normalize_money_columns`, `compare_invoice_to_rate_card`, and `export_findings_markdown` under `scripts/invoice_analysis_skeleton.py`

The current implementation has a different, more mature script split:

- `validate_inputs.py`
- `load_inputs.py`
- `invoice_analysis_skeleton.py`
- `rate_card_analysis.py`
- `trend_analysis.py`
- `llm_analyst.py`

**Why It Matters**

The README is the likely first document for a new maintainer. Mixing original build requirements with current implementation details makes it hard to know whether missing templates/docs are defects, backlog, or stale requirements.

**Recommended Solution**

Split the README into:

- **Current implementation**: what exists and how to run it.
- **Accepted backlog**: templates, reference docs, packaging, MCP wrapper.
- **Historical build spec**: move to `docs/feedback/` or compress into a short provenance note.

Do not leave old function-level requirements in README unless the code is expected to implement those names.

---

### Gap 1B — Architecture Diagram Describes Target Behavior As If It Exists

**Evidence**

`ARCHITECTURE.md` describes the intended layer flow with items such as:

- match priority: exact service ID → service+period → customer+product+period → fuzzy → manual,
- exception categories including `period_mismatch`, `unmapped_service`, `ceased_service_still_charged`,
- customer revenue variance,
- aging/payment status,
- deterministic severity as an invariant.

The current scripts do not yet implement those behaviors.

**Why It Matters**

The architecture file is useful, but it can mislead implementation decisions if target-state behavior is not clearly marked. A maintainer may assume service-map matching, customer price validation, aging, or severity already exists.

**Recommended Solution**

Update `ARCHITECTURE.md` with a status column for every layer capability:

- `implemented`
- `partial`
- `planned`
- `deferred`

Example:

| Capability | Status | Runtime Evidence |
|---|---|---|
| Exact service ID + period match | implemented | `MATCH_KEY` in `invoice_analysis_skeleton.py` |
| Service-map bridging | planned | ROADMAP 4b |
| Fuzzy/manual matching | deferred | No implementation |
| Deterministic severity | planned | ROADMAP 4c |

---

### Gap 2 — Finance Control Checklist Is Documented But Not Computed

**Evidence**

`SKILL.md` now requires every report to include a finance control checklist with items such as:

- invoice tie-out,
- sales tie-out,
- GST/tax status,
- credit/reversal classification,
- rate-card coverage,
- service-map coverage,
- unmatched cost/revenue exposure,
- negative and low-margin exposure,
- AR/AP aging supplied/not supplied,
- manual review queue count by severity.

The current scripts do not yet produce a dedicated `finance_control_checklist` table or equivalent deterministic output. The LLM prompt also does not require a separate finance control checklist section.

**Why It Matters**

This is the biggest finance-readiness gap. The skill instruction has moved ahead of the implementation. If a report says the checklist exists but the checklist values are produced by the LLM or implied from scattered tables, the anti-hallucination boundary weakens.

**Recommended Solution**

Add a deterministic `finance_control_checklist.parquet` and markdown output in Phase 4b before making any report claim that "every report includes" the checklist.

Suggested columns:

| Column | Meaning |
|---|---|
| `control_name` | Stable control identifier |
| `status` | `pass`, `fail`, `warning`, `not_supplied`, `not_applicable` |
| `metric_name` | Metric being checked |
| `metric_value` | Calculated value as string/decimal |
| `threshold_or_expected` | Expected value or rule |
| `delta` | Difference where applicable |
| `source_table` | Table used for the calculation |
| `source_column` | Column used for the calculation |
| `severity` | Deterministic severity |
| `requires_manual_review` | Boolean |
| `notes` | Short explanation |

Then update `llm_analyst.py` so the checklist table is always included in the LLM context and the required report format includes a "Finance Control Checklist" section.

---

### Gap 3 — LLM Citation Rule Is Prompt-Only

**Evidence**

`scripts/llm_analyst.py` tells the model: "Every statement in your response MUST include an inline citation." There is no post-generation validator that rejects unsupported sentences or malformed citations.

**Why It Matters**

Prompt instructions are not enforcement. Finance-facing reports need a deterministic citation gate. Without it, the LLM can produce uncited conclusions, cite a table that was not loaded, cite a metric that does not exist, or quote a value that differs from the calculated output.

**Recommended Solution**

Implement a citation validator after `call_llm()` and before `_write_analyst_report()`.

Minimum validator:

- Parse all citations matching `[table: ... | metric: ... | value: ...]`.
- Fail the report if any paragraph contains numeric claims without citations.
- Fail if a cited table was not loaded.
- Warn or fail if a cited metric is not a column, known row count, or declared aggregate.
- Fail if a cited scalar value cannot be found in the relevant table, run metadata, or assumption table.
- Write `citation_validation.json` and `citation_validation.md`.

Policy recommendation:

- For local experimentation, allow `--allow-uncited-draft`.
- For governed output, default to fail-closed.

---

### Gap 4 — Phase 4 Context Selection Still Misses Some Control Inputs

**Evidence**

`_select_context_tables()` now includes:

- `reconciliation_summary`
- `invoice_no_sales`
- `sales_no_invoice`
- `amount_mismatches`
- `rate_card_mismatches`
- `low_margin_exceptions`
- `usage_spikes`
- `recurring_changes`
- `margin_movement`

It does not include `data_quality_issues`, `run_summary`, `source_file_inventory`, `rate_variances`, `margin_by_customer`, `margin_by_service_type`, `new_services`, or `removed_services`. Some of these are reasonable exclusions for prompt size, but `data_quality_issues` is high-value for finance confidence and should not be omitted.

Also, the `_select_context_tables()` docstring still says `TODO — implement this function`, even though it is implemented.

**Why It Matters**

The LLM analyst can understate data quality problems because a key exception table is not in the selected context. The stale TODO creates maintenance confusion.

**Recommended Solution**

- Remove the stale TODO from the docstring.
- Add `data_quality_issues` to the selected context.
- Once created, add `finance_control_checklist` and `manual_review_queue`.
- Consider including summarized aggregates from `run_summary` and `source_file_inventory` in metadata rather than full tables.

---

### Gap 5 — Deterministic Severity Scoring Is Missing

**Evidence**

The roadmap lists severity scoring as a remaining Phase 4 exit criterion. Current scripts have flags such as `amount_mismatch_flag`, `rate_card_mismatch_flag`, `low_margin_flag`, `spike_flag`, and `recurring_change_flag`, but there is no unified severity model.

**Why It Matters**

LLM wording should not decide whether an item is Critical, High, Medium, or Low. Finance review queues need consistent rules based on exposure, control failure type, and data completeness.

**Recommended Solution**

Create `scripts/severity_scoring.py` or add a deterministic severity builder to the pipeline.

Suggested scoring inputs:

- dollar exposure,
- percentage variance,
- source type,
- exception category,
- missing mapping,
- missing rate card,
- negative margin,
- tax/credit uncertainty,
- duplicate or required-field nulls,
- repeated issue across periods.

Suggested output tables:

- `manual_review_queue.parquet`
- `exception_severity_summary.parquet`

Suggested severity defaults:

- `Critical`: negative margin with material exposure, supplier charge with no customer billing above configured threshold, missing required mapping that prevents reconciliation, or tax/credit ambiguity affecting totals.
- `High`: rate-card mismatch or amount mismatch above materiality threshold.
- `Medium`: service mapping gaps, recurring changes above threshold, low margin above de minimis exposure.
- `Low`: small rounding variance, low-dollar optional-field quality issue, informational new/removed service.

All thresholds should be written to an assumptions table.

---

### Gap 6 — Service-Map-Aware Reconciliation Is Not Implemented

**Evidence**

`invoice_analysis_skeleton.py` still matches on:

```text
supplier_service_id + billing_period_start
```

If sales has `our_service_id`, the code renames it to `supplier_service_id`. The assumptions table explicitly says `service_map not yet implemented` and `our_service_id_equals_supplier_service_id=True`.

**Why It Matters**

This is acceptable for a fixture, but risky for real supplier/customer data. Supplier service IDs and internal billing IDs often diverge. Without `service_map`, the pipeline will misclassify valid services as `invoice_no_sales` or `sales_no_invoice`.

**Recommended Solution**

Implement service-map resolution before reconciliation:

1. Load `service_map.parquet` when supplied.
2. Validate uniqueness of active mappings.
3. Resolve supplier IDs to internal IDs or vice versa before matching.
4. Track mapping status per row:
   - `mapped_active`
   - `mapped_inactive`
   - `no_mapping`
   - `duplicate_mapping`
   - `conflicting_mapping`
5. Add `service_map_coverage_pct` to the finance control checklist.
6. Keep exact-ID matching as an explicit fallback mode, not as the silent default for real runs.

---

### Gap 7 — Control Totals And Run Sign-Off Are Missing

**Evidence**

Current outputs include row counts and summaries, but there is no single deterministic run sign-off artifact that says whether source totals tie to normalized totals and whether reconciliation coverage is acceptable.

**Why It Matters**

Finance users need a concise "can this run be used?" signal. Right now, a user or LLM must infer that from multiple tables.

**Recommended Solution**

Add:

- `control_totals.parquet`
- `run_signoff_status.parquet`
- `run_signoff_status.md`

Suggested sign-off fields:

- `run_id`
- `invoice_source_total`
- `invoice_normalized_total`
- `invoice_total_delta`
- `sales_source_total`
- `sales_normalized_total`
- `sales_total_delta`
- `matched_invoice_total`
- `unmatched_invoice_total`
- `unmatched_sales_revenue_total`
- `rate_card_coverage_pct`
- `service_map_coverage_pct`
- `critical_count`
- `high_count`
- `signoff_status`: `pass`, `pass_with_warnings`, `fail`
- `blocking_reasons`

---

### Gap 8 — Rate-Card Selection Is Not Period-Aware

**Evidence**

`rate_card_analysis.py` resolves one rate per `service_type` by selecting the most recent `effective_date`. It ignores the billing period of the matched invoice line and does not use `expiry_date`.

**Why It Matters**

If a supplier rate changed after the billed period, the current implementation can compare March invoice lines to an April or later rate. That will create false mismatches or hide true overcharges.

**Recommended Solution**

Change rate matching from "most recent rate per service type" to "valid rate for billing period".

Matching rule:

- `service_type` must match.
- `effective_date <= billing_period_start`.
- `expiry_date` is null or `billing_period_start <= expiry_date`.
- If multiple rows qualify, select the most recent `effective_date`.
- If no row qualifies, flag `no_period_valid_rate`.
- If overlapping rate rows qualify, flag `ambiguous_rate_card`.

Add tests for:

- future rate should not apply to earlier billing period,
- expired rate should not apply,
- open-ended rate should apply,
- overlapping rates should produce an exception.

---

### Gap 9 — Period Boundary Matching Modes Are Missing

**Evidence**

Reconciliation joins on exact `billing_period_start`. It does not support overlap, inclusive/exclusive boundary logic, mid-month service starts, credits across periods, or prior-month adjustments.

**Why It Matters**

Supplier invoices often include partial periods, adjustments, late charges, and credit notes. Exact period start matching will misclassify legitimate lines as unmatched.

**Recommended Solution**

Add configurable period matching modes:

- `exact_period_start`: current behavior.
- `same_month`: match by service ID and invoice month.
- `overlap`: match when supplier and customer billing periods overlap.
- `prorated_overlap`: calculate expected prorated amount based on overlap days.

The active mode must be recorded in assumptions and surfaced in the finance control checklist.

---

### Gap 10 — Credit, Reversal, GST, And Tax Classification Are Not Implemented

**Evidence**

The validator recognizes tax-related columns such as `tax_amount` and `amount_inc_tax`, but the analysis scripts do not classify GST status, credits, reversals, or mixed ex/inc-tax sources.

**Why It Matters**

Supplier invoices and billing exports frequently contain credits, reversals, GST-inclusive totals, and negative lines. Margin and variance results can be materially wrong if credit lines are treated as ordinary charges or if ex-tax/inc-tax bases are mixed.

**Recommended Solution**

Add deterministic classification before reconciliation:

- `tax_basis`: `ex_tax`, `inc_tax`, `mixed`, `unknown`
- `line_polarity`: `charge`, `credit`, `reversal`, `zero`
- `credit_reason`: if derivable from description or source field
- `amount_basis_conflict_flag`

Add output tables:

- `tax_status_summary.parquet`
- `credit_reversal_summary.parquet`
- `credit_reversal_lines.parquet`

Do not let the LLM infer tax treatment. It can only explain classifications produced by Python.

---

### Gap 11 — Customer Sell-Rate / Price Book Logic Is Missing

**Evidence**

The Phase 2 margin logic calculates direct margin from supplied sales revenue and supplier invoice cost. It does not validate whether the customer was billed at the expected sell rate.

**Why It Matters**

Margin can be positive while customer billing is still wrong. For example, a service may be billed below contracted customer price but still above wholesale cost.

**Recommended Solution**

Introduce an optional `customer_price_book` / `sell_rate_card` input in Phase 5 or late Phase 4d:

- match by `customer_id`, `our_service_id` or product/service type, and billing period,
- compare `revenue_ex_tax` to expected sell price,
- output `sell_rate_variances`,
- distinguish supplier overcharge from customer underbilling.

This should remain behind the current reconciliation/rate-card controls because it adds another contract-data dependency.

---

### Gap 12 — Quantity, Unit Price, And Proration Checks Are Not Implemented

**Evidence**

`data_contract.md` and validator patterns include `quantity` and `unit_price_ex_tax`. The current analysis primarily compares line totals.

**Why It Matters**

A total amount can match while quantity or unit price is wrong, especially where bundles, partial periods, or multiple units exist. Conversely, a total mismatch may be explainable by proration.

**Recommended Solution**

Add optional line-level checks when fields are supplied:

- `quantity * unit_price_ex_tax == amount_ex_tax` within tolerance,
- expected unit price from rate card,
- prorated expected amount based on service days,
- missing quantity/unit price status.

Output:

- `unit_price_variances.parquet`
- `proration_exceptions.parquet`

---

### Gap 13 — Tests Depend On Shared `db/` State

**Evidence**

Several tests read from `db/*.parquet` and some module fixtures load examples into `db/` if missing. `db/` is git-ignored runtime state.

**Why It Matters**

The tests currently pass, but they rely on a mutable shared runtime directory. This can create order sensitivity, stale parquet contamination, and confusion when a previous run used different source files.

**Recommended Solution**

Make tests self-contained:

- Use `tmp_path` or `tmp_path_factory` for all generated parquet files.
- Add helper fixtures that ingest example CSVs into a temporary db path.
- Pass db/output paths into script functions instead of relying on global `DB`.
- Add regression tests that run from an empty temp workspace.

This will also make it easier to support the planned `--db` flag consistently.

---

### Gap 14 — Runtime Path Routing Is Only Partially Implemented

**Evidence**

`load_inputs.py` supports `--db`. `invoice_analysis_skeleton.py`, `rate_card_analysis.py`, `trend_analysis.py`, and `llm_analyst.py` still default to repo-local `db/` and `output/`. The roadmap already identifies `--db` / `--output-dir` and skills-runtime routing as pending.

**Why It Matters**

The repo policy says ephemeral runtime state should go under `/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/`. Repo-local `db/` and `output/` are git-ignored, but still mix runtime state into the authoring surface.

**Recommended Solution**

Add consistent CLI flags to every script:

- `--db`
- `--output-dir`
- optionally `--run-id`

Recommended default:

- Authoring/dev examples can use repo-local paths when explicitly requested.
- Installed skill runtime should default to `/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/`.

Update tests so they pass explicit temp paths.

---

### Gap 15 — Lineage And Phase Status Artifacts Are Missing

**Evidence**

The roadmap lists `lineage.json` and phase-status markers as pending. Current outputs contain source hashes and metadata in individual tables, but there is no single machine-readable lineage manifest.

**Why It Matters**

Lineage is essential for auditability and reruns. A future user should be able to answer: exactly which inputs, mappings, script versions, assumptions, and outputs produced this report?

**Recommended Solution**

Write `lineage.json` per run:

```json
{
  "run_id": "...",
  "generated_at": "...",
  "phase_status": {
    "phase1_validator": "complete",
    "phase1_reconciliation": "complete",
    "phase2_rate_card": "complete",
    "phase3_trend": "skipped",
    "phase4_llm": "draft"
  },
  "inputs": [
    {"source_type": "supplier_invoice", "path": "...", "sha256": "...", "rows": 123}
  ],
  "mappings": [
    {"path": "...", "sha256": "..."}
  ],
  "outputs": [
    {"table": "matched_lines", "path": "...", "rows": 100}
  ],
  "assumptions": [
    {"key": "tolerance.abs", "value": "0.02"}
  ]
}
```

Also add `phase_status.md` for human-readable reporting.

---

### Gap 16 — Dependency Manifest Is Missing

**Evidence**

No `pyproject.toml`, `requirements.txt`, or `.python-version` file was found at repo depth 2. `SETUP.md` documents installation commands, but the dependency set is not machine-locked in the repo.

`SETUP.md` also lists `openpyxl` for Excel output even though the export layer and Excel workbook are still planned, not implemented.

**Why It Matters**

The tests pass in the existing working-cache venv, but another environment cannot reproduce the project from a manifest. This matters for an installable skill with scripts.

The Excel dependency also blurs current runtime requirements versus future optional export support.

**Recommended Solution**

Add either:

- `pyproject.toml` with runtime/test dependencies, or
- `requirements.txt` plus `requirements-dev.txt`.

Given repo governance prefers Python 3.14.4 / uv for new environments, the clean path is:

- `.python-version` containing `3.14`
- `pyproject.toml` with dependencies:
  - `pandas`
  - `pyarrow`
  - `pyyaml`
  - `tabulate`
  - `openai`
  - `pytest`

Then update `SETUP.md` to use the manifest rather than hand-maintained package lists.

Keep optional export dependencies separate:

- core runtime: pandas, pyarrow, pyyaml, tabulate, openai
- test/runtime-dev: pytest
- optional export: openpyxl

---

### Gap 17 — Output Export Layer Is Still Incomplete

**Evidence**

The current scripts write parquet and markdown. `docs/output_schema.md` notes CSV export is deferred. ROADMAP mentions CSV/JSON/Excel exports as pending.

**Why It Matters**

Finance users often need CSV/Excel packs for review, filtering, sign-off, and dispute workflows. Markdown is useful for the LLM, not sufficient as the operational handoff.

**Recommended Solution**

Add `scripts/export_outputs.py`:

- reads a run output manifest or db directory,
- writes CSV for all output tables,
- writes JSON for lineage and summary metadata,
- optionally writes a formatted Excel workbook with one sheet per table,
- includes a README sheet or `index.md` listing each table and purpose.

Keep Excel optional if dependency footprint matters for the installable skill.

---

### Gap 18 — LLM Prompt Does Not Yet Match The New Finance Control Requirements

**Evidence**

`SKILL.md` now requires a finance control checklist. `SYSTEM_PROMPT` in `llm_analyst.py` still requires exactly these 9 sections:

1. Summary
2. Files Analyzed
3. Assumptions
4. Calculated Findings
5. Variances
6. Suspected Causes
7. Recommended Checks
8. Data Gaps
9. Confidence Rating

There is no required "Finance Control Checklist" section.

**Why It Matters**

The skill instruction and the actual LLM report format disagree. The LLM can produce a report that passes the current tests while failing the skill’s current finance-control expectation.

**Recommended Solution**

After the deterministic checklist table exists, update `SYSTEM_PROMPT` to require 10 sections or replace one existing section with a checklist section.

Recommended section order:

1. Summary
2. Files Analyzed
3. Finance Control Checklist
4. Assumptions
5. Calculated Findings
6. Variances
7. Suspected Causes
8. Recommended Checks
9. Data Gaps
10. Confidence Rating

Add tests asserting the prompt includes the checklist section and that `finance_control_checklist` is selected into context.

---

### Gap 19 — Structured LLM Output Is Not Implemented

**Evidence**

The LLM analyst returns free-form markdown. The roadmap mentions Instructor / structured output as pending.

**Why It Matters**

Free-form markdown is hard to validate. Citation validation, severity summaries, and report completeness checks are much easier when the model returns a typed schema.

**Recommended Solution**

Introduce structured output in stages:

1. Keep markdown report generation for humans.
2. Add a JSON schema for report sections, cited findings, recommended checks, data gaps, and confidence rating.
3. Validate JSON first.
4. Render markdown from validated JSON.

This allows deterministic enforcement without losing readability.

---

### Gap 20 — Output Schema Is Ahead Of Some Runtime Tables

**Evidence**

`docs/output_schema.md` describes tables that exist today, but it does not yet include future controls such as `finance_control_checklist`, `manual_review_queue`, `control_totals`, `run_signoff_status`, `lineage.json`, citation validation outputs, tax/credit summaries, or period-aware rate matching status.

**Why It Matters**

As soon as these controls are implemented, schema drift will become likely unless the output schema is treated as a contract.

**Recommended Solution**

Before implementing Phase 4b/4c, extend `docs/output_schema.md` with planned but stable schemas for:

- `control_totals`
- `run_signoff_status`
- `finance_control_checklist`
- `manual_review_queue`
- `exception_severity_summary`
- `service_map_coverage`
- `tax_status_summary`
- `credit_reversal_summary`
- `citation_validation`
- `lineage.json`

Then make tests assert that runtime columns match the schema.

---

### Gap 21 — Real-Export Validation Is Still Missing

**Evidence**

All tests use examples and synthetic fixtures. ROADMAP correctly says real-export validation should wait until service-map and control-total work is complete.

**Why It Matters**

The fixture data is intentionally small and clean. Real exports will expose:

- alternate date formats,
- empty rows,
- duplicate invoice numbers with distinct line items,
- service ID formatting differences,
- GST-inclusive fields,
- negative lines,
- multiple rate-card effective dates,
- overlapping periods,
- missing customer IDs,
- inactive services,
- product naming variants.

**Recommended Solution**

After Phase 4b.1 and 4b.2, create a redacted real-export validation pack:

- `examples/redacted_real/`
- mapping files,
- expected high-level control totals,
- a validation note describing redaction and assumptions.

Add tests that can run against the redacted pack without exposing sensitive values.

---

### Gap 22 — Skill Package Boundary Is Still Not Final

**Evidence**

The current authoring repo contains docs, examples, tests, scripts, feedback files, and the skill folder. The installable skill boundary is not yet clearly separated.

`README.md` and `SETUP.md` already mention Claude and Codex install paths, while `ROADMAP.md` says packaging and installation are still Phase 4e backlog.

**Why It Matters**

Installed skills should be compact and operational. Authoring docs and historical feedback should not necessarily ship into the runtime skill package.

**Recommended Solution**

Define packaging boundaries:

- Authoring surface:
  - `README.md`
  - `ROADMAP.md`
  - `ARCHITECTURE.md`
  - `SETUP.md`
  - `docs/feedback/`
  - tests
  - examples
- Installable skill:
  - `internal-invoice-analysis/SKILL.md`
  - required scripts
  - minimal `docs/data_contract.md`
  - minimal `docs/output_schema.md`
  - optional templates

Add a `scripts/package_skill.py` or documented packaging checklist to copy only the runtime-relevant files.

---

### Gap 22A — Missing User-Facing Reference Docs And Templates Are Still Open

**Evidence**

Root governance and README still list these as required or planned:

- `docs/analysis_layers.md`
- `docs/assumptions_and_limits.md`
- `templates/findings_report_template.md`
- `templates/reconciliation_report_template.md`
- `templates/supplier_dispute_template.md`
- `templates/internal_ticket_template.md`

They do not currently exist.

**Why It Matters**

The current scripts can run without these files, so they are not blockers for Phase 1-3. They are blockers for a polished installed skill because users need concise references and report templates without reading the entire authoring repo.

**Recommended Solution**

Create these after the Phase 4b/4c controls settle:

- `docs/analysis_layers.md`: explain what each script/table does and which phase owns it.
- `docs/assumptions_and_limits.md`: source-data-only rule, tax/audit boundary, no invented mappings, external-data policy, confidence limits.
- `templates/`: report/dispute/ticket templates that consume deterministic tables and require citation placeholders.

Do not build elaborate templates before `finance_control_checklist`, `manual_review_queue`, and citation validation exist, otherwise templates will encode incomplete report structure.

---

### Gap 22B — Parent Registry / Install Readiness Needs Final Verification

**Evidence**

`SCRATCHPAD.md` still lists "Add `internal-invoice-analysis` to skills_stuff AGENTS.md skill registry" as open. The parent governance shown in the session context appears to already include `invoice-finance-analyst/` in the Skill Authoring Projects table, but the local scratchpad has not been reconciled with that fact.

**Why It Matters**

This is a small governance consistency gap, but install readiness depends on clear source-of-truth tracking. Stale open items make it unclear whether the parent repo knows about this skill.

**Recommended Solution**

Verify the parent `../AGENTS.md` directly before packaging:

- if the registry already includes this project, mark the SCRATCHPAD item done;
- if not, update the parent registry;
- do not install to `~/.claude/skills` or `~/.codex/skills` until Phase 4e packaging criteria are met.

---

### Gap 23 — MCP / Accounting-System Integration Should Remain Deferred

**Evidence**

Phase 5 mentions optional accounting-system MCP only if CSV export becomes a bottleneck. No MCP wrapper is currently implemented.

**Why It Matters**

This is the right sequencing. Direct accounting-system integration would increase risk before the CSV reconciliation semantics are proven.

**Recommended Solution**

Keep MCP integration behind explicit gates:

- Phase 1-4 deterministic CSV pipeline passes real-export validation.
- Control totals and sign-off exist.
- Citation validator exists.
- Manual review queue exists.
- User confirms CSV export/import is the bottleneck.

Only then design read-only MCP access first. Do not write back to accounting systems from this skill without a separate approval and control workflow.

---

## Recommended Remediation Order

### Immediate Cleanup

1. Align phase status language across `README.md`, `ROADMAP.md`, `SCRATCHPAD.md`, and `SKILL.md`.
2. Remove the stale `_select_context_tables()` TODO docstring.
3. Add `data_quality_issues` to the LLM context.
4. Add a dependency manifest.
5. Add `--db` and consistent runtime path controls to all scripts.

### Phase 4b — Finance Control Foundation

1. Implement service-map-aware reconciliation.
2. Implement control totals and run sign-off.
3. Implement deterministic finance control checklist.
4. Implement period-aware rate-card selection.
5. Implement tax basis and credit/reversal classification.

### Phase 4c — Governed LLM Analyst

1. Add deterministic severity scoring and manual review queue.
2. Add structured LLM output or a strict markdown validation layer.
3. Add citation validator.
4. Update LLM prompt to include the finance control checklist.
5. Fail closed for governed reports unless `--allow-uncited-draft` is set.

### Phase 4d — Production Usability

1. Make tests self-contained and temp-path based.
2. Add lineage and phase-status artifacts.
3. Add CSV/JSON/Excel export pack.
4. Add real-export validation pack after control totals are in place.
5. Add performance notes for large CSVs.

### Phase 4e / Phase 5 — Packaging And Integrations

1. Define installable skill package boundary.
2. Add packaging checklist or script.
3. Add templates and reference docs.
4. Defer MCP/accounting-system integration until CSV workflow proves insufficient.

---

## Acceptance Criteria For Closing The Main Remaining Gaps

The project should not call Phase 4 "complete" until these are true:

- `pytest tests/` passes from a clean temp-runtime setup.
- All scripts accept explicit `--db` and `--output-dir` paths.
- A run writes `lineage.json`.
- A run writes `control_totals`, `run_signoff_status`, and `finance_control_checklist`.
- Service-map-aware reconciliation is implemented and tested.
- Period-aware rate-card matching is implemented and tested.
- Tax basis and credit/reversal classification are implemented or explicitly reported as not supplied.
- Deterministic severity scoring creates a manual review queue.
- The LLM analyst includes the finance control checklist in context and report format.
- Citation validation rejects unsupported LLM report claims.
- The dependency manifest can recreate the environment.
- The installed skill does not claim unavailable outputs, scripts, or controls exist.

---

## Validation Performed For This Review

Repository inspection:

- Reviewed current docs and governance surfaces: `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `SETUP.md`, `SCRATCHPAD.md`, `docs/output_schema.md`, and `internal-invoice-analysis/SKILL.md`.
- Reviewed implementation scripts: `validate_inputs.py`, `load_inputs.py`, `invoice_analysis_skeleton.py`, `rate_card_analysis.py`, `trend_analysis.py`, and `llm_analyst.py`.
- Reviewed test coverage: `tests/test_validate_inputs.py`, `tests/test_reconciliation.py`, `tests/test_rate_card_analysis.py`, `tests/test_trend_analysis.py`, and `tests/test_llm_analyst.py`.
- Checked for dependency manifests at shallow repo depth; none were found.

Test run:

```bash
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/
```

Result:

```text
219 passed in 1.59s
```

No source CSV files were modified as part of this review.

---

## Contradiction Check

The implementation is legitimately runnable and tested for the current examples. The gap list above should not be read as saying the project is weak or unusable. It is a strong Phase 1-3 implementation with a Phase 4 draft analyst layer.

The contradiction is in completion language: the repo can truthfully say "the pipeline is runnable and the fixture tests pass." It should not yet say "finance-control-complete" or "Phase 4 complete" until deterministic checklist, severity, lineage, and citation validation are implemented.
