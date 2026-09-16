# Remediation Plan: Internal Invoice Analysis

## Contents

- [Principles and sequence](#principles-and-sequence)
- [Stage A: correctness defects](#stage-a-correctness-defects)
- [Stage B: control completeness](#stage-b-control-completeness)
- [Stage C: evidence and citation integrity](#stage-c-evidence-and-citation-integrity)
- [Stage D: lineage and reproducibility](#stage-d-lineage-and-reproducibility)
- [Stage E: LLM hardening](#stage-e-llm-hardening)
- [Stage F: optional integrations](#stage-f-optional-integrations)
- [Explicit non-changes](#explicit-non-changes)

## Principles and sequence

This plan orders work by dependency and financial risk. It does not authorize implementation. Each stage should complete its acceptance tests before the next stage changes downstream behavior.

## Stage A: correctness defects

### A1: Cardinality-gated, service-map-aware reconciliation

| Field             | Requirement                                                                                                                                                                      |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem           | The primary reconciliation merge and prior-margin merge can multiply rows; service maps are unused.                                                                              |
| Affected files    | `scripts/invoice_analysis_skeleton.py`, `scripts/trend_analysis.py`, `scripts/load_inputs.py`, `docs/data_contract.md`, `docs/output_schema.md`, tests and fixtures.             |
| Required behavior | Preserve source-row IDs; profile invoice, sales, and map cardinality; resolve a versioned active service map; emit one-to-one matches only; quarantine one-to-many, many-to-one, |
|                   |   many-to-many, duplicate, unmapped, inactive, and conflicting-map candidates.                                                                                                   |
| Tests required    | Controlled one-to-one, one-to-many, many-to-one, many-to-many, duplicate invoice, duplicate sales, divergent IDs, missing/duplicate/inactive map, and conservation/tie-out       |
|                   |   tests.                                                                                                                                                                         |
| Acceptance        | No ambiguous join reaches margin, variance, rate, or trend calculations. Every input row has one terminal reconciliation status and evidence reference.                          |
|   criteria        |                                                                                                                                                                                  |
| Dependencies      | None.                                                                                                                                                                            |

### A2: Explicit date and period semantics

| Field               | Requirement                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem             | AU/US short-date handling is ambiguous; matching only uses start date with no explicit period policy.                                                                          |
| Affected files      | Mapping format, validator, loader, reconciliation, trend analysis, data contract, tests.                                                                                       |
| Required behavior   | Require mapping-level date format for non-ISO input; reject ambiguous dates; define named exact, calendar-month, overlap, and billing-lag modes; record period-match type and  |
|                     |   confidence.                                                                                                                                                                  |
| Tests required      | AU and US parsing, ambiguity rejection, period-end mismatch, partial periods, boundary overlap, timezone-free serialization.                                                   |
| Acceptance criteria | The same source text cannot map to different dates without a configuration change; every non-exact period outcome is visible.                                                  |
| Dependencies        | A1 for output/evidence fields.                                                                                                                                                 |

### A3: Period-valid rate-card resolution

| Field               | Requirement                                                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem             | Latest rate by service type can select a future/expired/overlapping rate.                                                                                                  |
| Affected files      | `scripts/rate_card_analysis.py`, data contract, output schema, tests.                                                                                                      |
| Required behavior   | Resolve rates using service attributes and billing date; require exactly one valid rate; emit `no_period_valid_rate` or `ambiguous_rate` rather than choosing arbitrarily. |
| Tests required      | Historical/current/future rates, expiry boundary, open-ended range, overlapping ranges, zero rate, no rate, service-specific rate, quantity/rate semantics.                |
| Acceptance criteria | Each calculated rate variance cites exactly one eligible rate or carries a blocking non-rate status.                                                                       |
| Dependencies        | A1 and A2.                                                                                                                                                                 |

## Stage B: control completeness

### B1: Input classification and money semantics

| Field               | Requirement                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem             | Tax, credits, reversals, negative values, currencies, quantities, and zero denominators lack controlled status.                                                                |
| Affected files      | Validator, loader, data contract, skill, output schema, tests.                                                                                                                 |
| Required behavior   | Add explicit currency, tax basis, charge type, sign, quantity/unit-price, and denominator-comparability fields. Reject or block mixed/unknown money state unless a configured  |
|                     |   conversion/control exists.                                                                                                                                                   |
| Tests required      | Tax-inclusive/exclusive, credits, reversals, negative/zero values, currency symbols, thousands separators, parentheses, missing cost/revenue, and zero/negative denominator.   |
| Acceptance criteria | Margin, rate, and trend outputs report `NOT_COMPARABLE` where arithmetic would mislead.                                                                                        |
| Dependencies        | A1 and A2.                                                                                                                                                                     |

### B2: Control totals and finance-control checklist

| Field               | Requirement                                                                                                                                                      |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem             | The system cannot tie source, normalized, matched, exception, and excluded amounts together or declare blocked status.                                           |
| Affected files      | New control module, output schema, roadmap, skill, tests, reporting.                                                                                             |
| Required behavior   | Produce run-scoped `control_totals`, `run_signoff_status`, and `finance_control_checklist` from deterministic tables. Use the schema in `control-gap-matrix.md`. |
| Tests required      | Conservation of row counts and amounts across all terminal states; each blocking failure must prevent `FINANCE_CONTROL_COMPLETE`.                                |
| Acceptance criteria | A run proves why each source row/amount is included, excluded, unmatched, or blocked.                                                                            |
| Dependencies        | A1–A3 and B1.                                                                                                                                                    |

### B3: Deterministic severity and manual-review queue

| Field               | Requirement                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem             | Severity formula is documented but no executable score or review queue exists.                                                                         |
| Affected files      | New deterministic severity module/config, architecture, skill, output schema, tests.                                                                   |
| Required behavior   | Put score components, thresholds, and policy in one versioned configuration. Emit `manual_review_queue` and severity summary with evidence references. |
| Tests required      | Boundary values, repeatability, missing-evidence downgrade/block, recurrence and value-impact cases.                                                   |
| Acceptance criteria | The model does not determine severity; every label resolves to deterministic inputs.                                                                   |
| Dependencies        | B2 and stable evidence identifiers from A1.                                                                                                            |

## Stage C: evidence and citation integrity

### C1: Row-level evidence model

| Field               | Requirement                                                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem             | Source hashes do not identify a source row, mapping, transformation, calculation, or output row.                                                         |
| Affected files      | Loader and all analysis writers, data/output contracts, tests.                                                                                           |
| Required behavior   | Carry source file hash, source-row ID, mapping digest, original/normalized field references, calculation ID, and output finding ID through the pipeline. |
| Tests required      | Trace any output row back to source bytes and line identity; test duplicate and joined records.                                                          |
| Acceptance criteria | Every numeric finding has resolvable evidence references without reading free-form prose.                                                                |
| Dependencies        | A1.                                                                                                                                                      |

### C2: Citation validator

| Field               | Requirement                                                                                                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem             | LLM citation syntax is prompt-only.                                                                                                                                     |
| Affected files      | New validator, `llm_analyst.py`, report schema, tests.                                                                                                                  |
| Required behavior   | Validate each claim reference against the run manifest; confirm referenced record/value and claim semantics; write validation result; fail closed for governed reports. |
| Tests required      | Missing citation, malformed citation, absent table/record, wrong value, valid citation, nonnumeric statement, and `allow-uncited-draft` behavior.                       |
| Acceptance criteria | No governed report publishes when any numeric claim lacks valid evidence.                                                                                               |
| Dependencies        | C1 and B2.                                                                                                                                                              |

## Stage D: lineage and reproducibility

### D1: Run manifest and atomic publish

| Field               | Requirement                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem             | Outputs share a mutable db directory and have no run-level provenance or complete/partial status.                                                                         |
| Affected files      | All writers, CLI interfaces, setup, scripts README, tests.                                                                                                                |
| Required behavior   | Write to a unique run directory, create one lineage manifest with inputs/config/code/dependency/output digests and phase states, then atomically publish a completed run. |
| Tests required      | Same-input deterministic content hash excluding approved volatile fields, write-failure recovery, interrupted phase, rerun, and concurrent run isolation.                 |
| Acceptance criteria | A reviewer can select one immutable run and know which phases completed, failed, or were not run.                                                                         |
| Dependencies        | B2 and C1.                                                                                                                                                                |

### D2: Dependency and configuration manifest

| Field               | Requirement                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Problem             | Dependencies and runtime version are prose-only and drifted.                                                              |
| Affected files      | Project root, setup, justfile, CI/test instructions.                                                                      |
| Required behavior   | Add one machine-readable dependency/version manifest; have test commands verify it; remove unsupported dependency claims. |
| Tests required      | Clean environment install and runtime version assertion.                                                                  |
| Acceptance criteria | A clean checkout reproduces the documented deterministic test suite.                                                      |
| Dependencies        | None, but complete before a finance-control claim.                                                                        |

## Stage E: LLM hardening

### E1: Structured response and provider policy

| Field               | Requirement                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem             | Phase 4 accepts arbitrary text and sends data to any configured compatible endpoint.                                                                                           |
| Affected files      | `scripts/llm_analyst.py`, skill, setup, tests.                                                                                                                                 |
| Required behavior   | Define structured response fields, validate them before rendering, restrict LLM roles to summarization/grouping/prioritization, record endpoint/model/consent, and provide     |
|                     |   local/offline behavior.                                                                                                                                                      |
| Tests required      | API error, retry policy, unsupported response, provider policy denial, redaction, local mode, and validator rejection.                                                         |
| Acceptance criteria | LLM output cannot change deterministic results or publish a governed claim without C2 approval.                                                                                |
| Dependencies        | B2, C1, C2, D1.                                                                                                                                                                |

## Stage F: optional integrations

Only after Stages A–E pass:

- Add controlled CSV/JSON/XLSX export.
- Add an accounting-system MCP wrapper only around validated, run-scoped results.
- Evaluate shared `evidence`, `provenance`, `controls`, `llm`, and `reporting` modules after invoice-domain interfaces remain stable through real controlled runs.

## Explicit non-changes

Do not rewrite `SKILL.md`, move folders, rename scripts, replace pandas, add LangChain/LangGraph/vector databases, introduce an MCP, or extract shared libraries during Stages A–E. The current
pandas-first implementation and provider-agnostic transport are sound starting points. Correct the financial control boundaries before changing architecture.
