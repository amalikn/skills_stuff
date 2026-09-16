# Current-State Audit: Internal Invoice Analysis

## Contents

- [Audit scope and method](#audit-scope-and-method)
- [Executive status](#executive-status)
- [Overall verdict](#overall-verdict)
- [What exists](#what-exists)
- [What works](#what-works)
- [What is partial](#what-is-partial)
- [What is documented only](#what-is-documented-only)
- [P0 findings](#p0-findings)
- [P1 findings](#p1-findings)
- [P2 findings](#p2-findings)
- [Finance-control readiness](#finance-control-readiness)
- [LLM safety](#llm-safety)
- [Evidence and lineage readiness](#evidence-and-lineage-readiness)
- [Test quality](#test-quality)
- [Architecture conformance](#architecture-conformance)
- [Inventory](#inventory)
- [Broader BI foundation assessment](#broader-bi-foundation-assessment)
- [Recommended next step](#recommended-next-step)

---

## Audit scope and method

**Observed fact.** This audit inspected the local repository only. It used no web sources or external financial data. The audit reviewed the governance hierarchy specified in
[`internal-invoice-analysis-audit-01.md`](../../internal-invoice-analysis-audit-01.md), implementation, fixtures, generated parquet schemas, and all five test modules.

**Observed fact.** The documented venv command reproduced a clean dependency check and a complete test run: Python 3.14.7, `pip check` passed, 219 tests collected, 219 passed, no skips, xfails,
or pytest warnings. The project documentation claims Python 3.14.4; that specific runtime version did not reproduce.

**Observed fact.** The deterministic fixture pipeline ran twice in isolated temporary directories. Every non-volatile Phase 1B–3 table compared equal. `run_summary.run_id`, timestamps, output paths,
and loader timestamps differ by design, so raw artifact bytes do not form a stable reproducibility target.

**Inference.** The deterministic calculations are repeatable for the narrow fixture shape. The test result does not establish financial correctness for duplicate keys, divergent identifiers,
historical rate cards, ambiguous dates, tax states, or multi-currency data.

## EXECUTIVE STATUS

| Area                 | Status                     | Evidence                                                                                                                                  |
| -------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Input validation     | Partial                    | `validate_inputs.py` validates mapped fields and source hashes, but accepts empty files and lacks robust encoding and ambiguity controls. |
| Canonical loading    | Partial                    | `load_inputs.py` normalizes mapped fields and persists source-file hashes, but retains no source row identity or mapping version.         |
| Reconciliation       | Unsafe for finance control | `invoice_analysis_skeleton.py` performs an outer merge without join-cardinality validation.                                               |
| Rate-card analysis   | Unsafe for finance control | `_resolve_rate_card()` selects the latest rate by service type without billing-period or expiry validation.                               |
| Margin analysis      | Analytic only              | Ex-tax direct margin formula is consistent in implemented Phase 1B–3 paths, but rests on unsafe joins and lacks tax/credit controls.      |
| Trend analysis       | Unsafe for finance control | Trend and prior-margin joins use service ID alone and can multiply rows.                                                                  |
| LLM reporting        | Runnable draft output      | The prompt requires citations, but no validator rejects uncited or invented report text.                                                  |
| Evidence and lineage | Partial                    | Source file hashes exist; row-level provenance, transformation trace, run manifest, phase status, and claim validation do not.            |

## OVERALL VERDICT

**Verdict: RUNNABLE / ANALYTIC USE ONLY.**

**Observed fact.** The repository contains a functioning fixture-backed pandas pipeline for validation, loading, exact-key reconciliation, rate variance, margin aggregation, trends, and a mocked
provider-agnostic LLM call.

**Inference.** A user may use the deterministic outputs for exploratory analysis after reviewing mappings and results. They must not use them as finance-control evidence, accounting sign-off, tax
support, or an automated basis for commercial decisions because the P0 issues below can inflate, suppress, or misclassify financial findings.

## WHAT EXISTS

- Phase 0: [`internal-invoice-analysis/SKILL.md`](../../internal-invoice-analysis/SKILL.md) defines hard rules, the intended 15-step workflow, report sections, accounting boundary, and planned
  finance controls.
- Phase 1A: [`scripts/validate_inputs.py`](../../scripts/validate_inputs.py), mappings, a data contract, and synthetic fixtures.
- Phase 1B: [`scripts/load_inputs.py`](../../scripts/load_inputs.py) plus
  [`scripts/invoice_analysis_skeleton.py`](../../scripts/invoice_analysis_skeleton.py) produce nine reconciliation tables.
- Phase 2: [`scripts/rate_card_analysis.py`](../../scripts/rate_card_analysis.py) produces six rate and margin tables.
- Phase 3: [`scripts/trend_analysis.py`](../../scripts/trend_analysis.py) produces seven trend tables.
- Phase 4: [`scripts/llm_analyst.py`](../../scripts/llm_analyst.py) builds a prompt from selected parquet tables and writes a free-form Markdown report.
- Tests: five pytest modules. The current fixture-backed suite reproduces as 219 passing tests.

## WHAT WORKS

- Source CSVs are read without editing them. Validator tests and the loader’s before/after SHA-256 checks support that claim.
- Mapped required fields, mapped missing columns, malformed numeric values, and unsupported filename extensions fail in covered cases.
- The loader intentionally reads strings first, strips whitespace, then applies explicit number and date coercion.
- On the supplied fixtures, Phase 1B produces three matched rows, one invoice-only row, one sales-only row, one amount mismatch, and removes one exact invoice duplicate.
- The Phase 1B–3 semantic outputs are reproducible with the supplied fixtures.
- The implemented direct-margin formula uses ex-tax revenue less ex-tax invoice cost. It appears consistently in the Phase 1B matched-line, Phase 2 aggregate, and Phase 3 current-margin paths.
- The LLM interface is provider-agnostic at the OpenAI-compatible API boundary and testable offline through mocks.
- The skill explicitly states that reports are operational analysis rather than accounting, tax, or audit sign-off.

## WHAT IS PARTIAL

| Capability         | Current implementation                                    | Missing control                                                                                          |
| ------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Column mapping     | User-supplied mapping validates field presence.           | No mapping ID, version, confidence, explicit date format, or source-to-canonical transformation ledger.  |
| Duplicate handling | Exact duplicate invoice rows are removed and counted.     | Sales duplicates are not handled; duplicates lack a row-level exception queue and reasoned disposition.  |
| Service mapping    | A fixture, mapping schema, and loader support exist.      | Neither reconciliation nor rate/trend calculations use `service_map.parquet`.                            |
| Rate validation    | Variance against one rate per service type is calculated. | No service-specific rate, quantity, effective period, expiry, overlap, or no-valid-rate handling.        |
| Trends             | Current/prior values and simple flags are calculated.     | No comparability state for zero, negative, null, partial-period, renamed, or period-misaligned services. |
| Severity           | Low-margin and data-quality labels exist.                 | No canonical deterministic severity score, thresholds, review queue, or severity evidence.               |
| Finance controls   | Some data-quality and mismatch signals exist.             | No control totals, signoff status, control checklist, blocking control semantics, or taxonomy.           |

## WHAT IS DOCUMENTED ONLY

| Declared contract or architecture                                                    | Audit classification | Evidence                                                                               |
| ------------------------------------------------------------------------------------ | -------------------- | -------------------------------------------------------------------------------------- |
| Reconciliation priority ladder through service map, description matching, and manual | DOCUMENTED_ONLY      | The implementation joins one exact two-column key after renaming `our_service_id`.     |
|   overrides                                                                          |                      |                                                                                        |
| Duplicate invoice and duplicate sales classifications                                | DOCUMENTED_ONLY      | Exact invoice duplicates are removed; sales duplicates and duplicate match statuses    |
|                                                                                      |                      |   are not generated.                                                                   |
| Period mismatch, unmapped service, ceased service, and charge-type outputs           | DOCUMENTED_ONLY      | No corresponding implementation outputs exist.                                         |
| Tax/GST separation, charge classification, and mixed-currency controls               | DOCUMENTED_ONLY      | Optional tax values load but downstream control logic does not classify or reconcile   |
|                                                                                      |                      |   them.                                                                                |
| Deterministic severity formula                                                       | DOCUMENTED_ONLY      | Formula appears in `ARCHITECTURE.md` and `SKILL.md`; no script calculates it.          |
| Evidence table with enforceable citations                                            | DOCUMENTED_ONLY      | The LLM prompt asks for citations; output is written without validation.               |
| `finance_control_checklist.parquet`, citation validation, lineage append, and        | DOCUMENTED_ONLY      | The roadmap marks all as pending and no implementation files exist.                    |
|   phase-status marker                                                                |                      |                                                                                        |

## P0 FINDINGS

| ID    | Finding                        | Observed evidence                                                                                   | Financial consequence                                 |
| ----- | ------------------------------ | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| P0-01 | Reconciliation permits         | `DataFrame.merge()` has no `validate=` argument or pre-merge uniqueness gate. A synthetic           | Cost, revenue, margin, mismatch counts, and summaries |
|       |   Cartesian expansion.         |   one-invoice/two-sales case produced two `matched_lines`.                                          |   can be inflated.                                    |
| P0-02 | Service mapping is unused      | `service_map.parquet` is loaded but never read by the reconciliation, rate, or trend engines.       | Real feeds with divergent IDs will produce false      |
|       |   despite divergent identifier |   Fixtures map `LOC…` supplier IDs to `SVC…` internal IDs.                                          |   unmatched rows and omit valid margin/rate/trend     |
|       |   design.                      |                                                                                                     |   findings.                                           |
| P0-03 | Rate selection ignores billing | `_resolve_rate_card()` sorts descending on `effective_date` and drops duplicates by `service_type`. | Historical invoices can be compared with future or    |
|       |   period and expiry.           |   A 2025 invoice selected a 2026 rate in the controlled probe.                                      |   expired rates, producing false rate variances.      |
| P0-04 | Ambiguous dates can be         | Contract accepts US and AU short dates. Loader calls                                                | Billing-period joins, rate eligibility, and trend     |
|       |   silently reinterpreted.      |   `pd.to_datetime(..., format="mixed", dayfirst=True)`, so an unlabelled `03/01/2026` follows AU    |   periods can be wrong without an error.              |
|       |                                |   interpretation regardless of source convention.                                                   |                                                       |
| P0-05 | The LLM report accepts         | `_write_analyst_report()` writes returned text verbatim. A controlled mocked response containing    | A report can include uncited invented values while    |
|       |   unsupported numeric claims.  |   `Fabricated $999.` was written unchanged.                                                         |   appearing as pipeline output.                       |
| P0-06 | Prior-period margin can also   | `build_margin_movement()` joins prior invoice and sales on service ID only. A two-by-two synthetic  | Margin movement can be materially overstated or       |
|       |   multiply rows.               |   case calculated prior margin of 100 from four joined pairs.                                       |   understated.                                        |

## P1 FINDINGS

| ID    | Finding                                                                                                  | Consequence                                                                       |
| ----- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| P1-01 | No control-total or signoff output.                                                                      | The pipeline cannot prove source-to-normalized-to-output completeness or state    |
|       |                                                                                                          |   whether results require review.                                                 |
| P1-02 | No row-level provenance, mapping version, calculation identifier, lineage manifest, or phase status.     | A reviewer cannot trace a finding to a CSV line or distinguish complete from      |
|       |                                                                                                          |   partial runs.                                                                   |
| P1-03 | Tax, credits, reversals, negative amounts, zero denominators, and currency state lack deterministic      | Totals and exception logic can include semantically incomparable values without a |
|       |   classification.                                                                                        |   visible status.                                                                 |
| P1-04 | `data_contract.md` defines `variance_abs` against revenue, while code and output schema calculate it     | A governed financial metric has contradictory definitions.                        |
|       |   against sales-recorded cost.                                                                           |                                                                                   |
| P1-05 | No-valid-rate rows set `no_rate_card_entry`, but they do not enter `rate_card_mismatches`; zero expected | Missing or unusable rate data can be understated rather than treated as a         |
|       |   cost produces non-finite percentage variance.                                                          |   blocking exception.                                                             |
| P1-06 | Tests rely on mutable repository `db/` state for reconciliation, rate, and trend setup.                  | A green suite does not prove a clean checkout can recreate all required inputs.   |
| P1-07 | Phase 4 sends customer/service data and exception tables to any configured compatible endpoint.          | The code offers no data minimization, PII redaction, provider allowlist, or       |
|       |                                                                                                          |   consent control.                                                                |
| P1-08 | Analysis scripts write fixed repo-local `db/` outputs and do not use atomic writes or a run manifest.    | Concurrent or interrupted runs can leave a mixed-generation output set.           |

## P2 FINDINGS

- No `pyproject.toml`, lockfile, requirements file, or pytest configuration exists. `SETUP.md` is the only dependency manifest and includes `openpyxl` although no Excel export exists.
- The active venv reports Python 3.14.7, while governance and setup documents require 3.14.4.
- `_select_context_tables()` retains a stale TODO docstring despite an implemented priority list.
- Output-schema prose says `run_summary` is written last. The code constructs it before writes and writes it first in the table dictionary.
- The architecture describes several planned layers in present-tense flow language. The component table and roadmap correct most of that ambiguity, but the documents still require joint reading.
- Archiving uses a minute-resolution filename and moves the current parquet before a new write. Two same-minute reloads can collide, and no archive manifest proves which copy supplied a run.

## FINANCE-CONTROL READINESS

**Observed fact.** The project lacks all of the following blocking controls: cardinality-safe joins, service-map reconciliation, period-valid rate selection, control totals, deterministic severity,
citation validation, per-row evidence, lineage, and phase-completeness status.

**Recommendation.** Treat finance-control readiness as **BLOCKED**. Do not promote the LLM report, rate validation, margin movement, or reconciliation summary to a control artifact until P0-01 through
P0-06 are remediated and the Stage B–E controls in [`remediation-plan.md`](remediation-plan.md) pass their acceptance tests.

## LLM SAFETY

**Observed fact.** The prompt constrains the model to table-derived citations, fixed sections, and a small root-cause taxonomy. Context selection avoids raw unbounded CSVs and caps each selected table
at 50 rows.

**Observed fact.** The code has no structured response parser, citation validator, numeric-claim check, retry policy, provider capability check, or fail-closed output gate.

**Recommendation.** Keep the LLM as an optional draft-summarization stage. A governed report should render only from a validated structured response with evidence references resolved against a
run-local manifest. The deterministic tables must remain authoritative.

## EVIDENCE / LINEAGE READINESS

| Requirement             | Status  | Evidence                                                                                      |
| ----------------------- | ------- | --------------------------------------------------------------------------------------------- |
| Source file identity    | Partial | `_source_file` and SHA-256 are stored by loader.                                              |
| Source row identity     | Missing | No source row number or immutable row ID survives loading.                                    |
| Mapping identity        | Missing | Mapping path/version/hash is not persisted.                                                   |
| Transformation trail    | Missing | No per-field transformation or original-value ledger exists.                                  |
| Finding-to-source trace | Missing | Output rows retain selected business fields but not source row references.                    |
| Run lineage             | Missing | No `lineage.json`, code version, input set, output list, or dependency version record exists. |
| Claim validation        | Missing | LLM citations are prompt instructions only.                                                   |
| Phase completeness      | Missing | No `complete`, `partial`, `failed`, or `blocked` marker is written.                           |

## TEST QUALITY

**Observed fact.** The suite has meaningful unit coverage of fixture calculations, constants, basic validation failures, file creation, and mocked provider calls. It does not exercise the critical
failure classes listed in the audit prompt: many-to-many joins, service-map bridging, overlapping rate dates, ambiguous dates, tax states, mixed currencies, zero/negative denominator states,
unsupported providers, output-write failures, or uncited LLM responses.

**Assessment: WEAK for finance-control correctness; ADEQUATE for the implemented happy-path fixture pipeline.** Details are in
[`test-coverage-audit.md`](test-coverage-audit.md).

## ARCHITECTURE CONFORMANCE

| Layer                     | Declared | Implemented | Tested      | Finance-safe | Notes                                                                                     |
| ------------------------- | -------: | ----------: | ----------: | -----------: | ----------------------------------------------------------------------------------------- |
| Input/schema              | Yes      | Partial     | Yes         | No           | Mapping validation exists; empty, encoding, ambiguity, tax, and currency controls do not. |
| Normalization             | Yes      | Partial     | Yes         | No           | Explicit casts exist; date semantics and row identity do not.                             |
| Reconciliation            | Yes      | Partial     | Yes         | No           | Exact two-key outer join only; cardinality and service maps absent.                       |
| Rate validation           | Yes      | Partial     | Yes         | No           | Latest service-type rate only; no period validity.                                        |
| Margin                    | Yes      | Partial     | Yes         | No           | Formula is coherent but upstream joins are unsafe.                                        |
| Trend/anomaly             | Yes      | Partial     | Yes         | No           | Threshold flags exist; comparability and cardinality controls do not.                     |
| Severity                  | Yes      | No          | No          | No           | Formula is documented but absent from code.                                               |
| Evidence                  | Yes      | Partial     | Prompt only | No           | File hashes exist; no row lineage or citation enforcement.                                |
| LLM interpretation        | Yes      | Yes         | Yes         | No           | Mocked provider integration works; report text has no safety gate.                        |
| Reporting                 | Yes      | Partial     | Yes         | No           | Markdown/parquet outputs exist; no controlled report schema or completion state.          |
| Lineage/control checklist | Yes      | No          | No          | No           | Roadmap correctly marks these items pending.                                              |

## Inventory

### Relevant project tree and classification

```text
AGENTS.md                                      GOVERNANCE
AI_NAVIGATION.md                               GOVERNANCE
context-map.yaml                               GOVERNANCE
ARCHITECTURE.md                                GOVERNANCE
ROADMAP.md                                     GOVERNANCE
SETUP.md                                       GOVERNANCE
CHANGELOG.md                                   GOVERNANCE
README.md                                      REFERENCE (contains stale build-spec material)
internal-invoice-analysis/SKILL.md             GOVERNANCE / operational contract
scripts/validate_inputs.py                     IMPLEMENTATION
scripts/load_inputs.py                         IMPLEMENTATION
scripts/invoice_analysis_skeleton.py           IMPLEMENTATION
scripts/rate_card_analysis.py                  IMPLEMENTATION
scripts/trend_analysis.py                      IMPLEMENTATION
scripts/llm_analyst.py                         IMPLEMENTATION
scripts/README.md                              GOVERNANCE / implementation guide
tests/test_validate_inputs.py                  TEST
tests/test_reconciliation.py                   TEST
tests/test_rate_card_analysis.py               TEST
tests/test_trend_analysis.py                   TEST
tests/test_llm_analyst.py                      TEST
examples/*.csv                                 FIXTURE
examples/mapping_*.yaml                        FIXTURE
examples/README.md                             REFERENCE
docs/data_contract.md                          GOVERNANCE / data contract
docs/output_schema.md                          GOVERNANCE / output contract
docs/invoice_analysis_framework.md             LEGACY / planning reference
docs/feedback/*.md                             REFERENCE / historical reviews
db/*.parquet                                   GENERATED runtime artifacts
output/**                                      GENERATED runtime artifacts
graphify-out/**                                GENERATED
.ai-context/governance-pack.md                 GENERATED
.archcore/settings.json                        GOVERNANCE configuration
.claude/settings*.json                         GOVERNANCE configuration
internal-invoice-analysis-audit-01.md          REFERENCE / supplied audit prompt
```

### Referenced paths that do not exist

| Referencing document                                 | Missing path                                                                                     | Status                            |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------- |
| `ARCHITECTURE.md` and historical build specification | `docs/analysis_layers.md`                                                                        | Planned/backlog, not implemented. |
| `ARCHITECTURE.md` and historical build specification | `docs/assumptions_and_limits.md`                                                                 | Planned/backlog, not implemented. |
| `ARCHITECTURE.md` and historical build specification | `templates/`                                                                                     | Planned/backlog, not implemented. |
| `ARCHITECTURE.md`, roadmap, and skill                | `finance_control_checklist.parquet`, citation validator, JSON schema validator, lineage manifest | Explicitly pending.               |

### Undocumented or stale surfaces

- `README.md` retains a build specification that mixes historical requested behavior with current implementation. `AI_NAVIGATION.md` correctly assigns it lower authority.
- The repository has no packaging/dependency manifest despite documented runtime dependencies.
- Current `db/` contains 22 documented derived tables plus six loaded source parquets. The source parquets are operational inputs but lack an explicit generated-input schema and provenance contract.
- `service_map.parquet` exists as a generated input but no consuming calculation documents its non-use prominently enough for a finance user.

## Broader BI foundation assessment

**Recommendation: do not use the current project as the finance-control foundation yet.** Use it as a bounded invoice-analysis prototype and preserve its deterministic pandas-first pattern.

### Generalize later, after control remediation

- Evidence references: run ID, dataset ID, source-file hash, source-row ID, calculation ID, output row ID, and claim ID.
- Run lineage and phase-status model.
- Control evaluation model, including blocking status and deterministic severity.
- Citation/claim validation and structured LLM response validation.
- Provider abstraction, provider policy, redaction, and offline-mode behavior.
- Deterministic pipeline conventions: immutable inputs, explicit configuration, run-scoped outputs, and control totals.

### Keep invoice-specific

- Canonical invoice, sales, rate-card, and service-map schemas.
- Supplier/invoice-to-sales matching and period semantics.
- Rate-card eligibility and price/quantity/proration rules.
- Invoice-specific anomaly, margin, and credit/reversal logic.

**Inference.** Extracting shared modules before the invoice domain proves their contracts would freeze untested abstractions. The correct sequence is to fix invoice-domain controls, observe stable
interfaces, then extract the narrow common parts into a future `business-intelligence/shared` layer.

## RECOMMENDED NEXT STEP

**Exact next remediation task: Stage A1: replace the reconciliation merge with a cardinality-gated, service-map-aware matching stage.**

The task must reject or quarantine duplicate/ambiguous join keys before calculating any matched row, preserve original row identities, distinguish one-to-one, one-to-many, many-to-one, and
many-to-many candidates, and use a versioned service map for divergent supplier/internal IDs. Its test suite must include controlled Cartesian-expansion cases and prove that no margin or total is
calculated from an ambiguous match. The complete dependency-ordered plan appears in [`remediation-plan.md`](remediation-plan.md).
