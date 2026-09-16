# Project Analysis and Gap Plan

## Contents

- [Executive Summary](#executive-summary)
- [Current State](#current-state)
  - [Existing Files and Artifacts](#existing-files-and-artifacts)
  - [Missing Files and Capabilities](#missing-files-and-capabilities)
  - [Stale State](#stale-state)
- [Strengths](#strengths)
  - [Correct Calculation Authority](#correct-calculation-authority)
  - [Strong Anti-Hallucination Rules](#strong-anti-hallucination-rules)
  - [Clear External Data Boundary](#clear-external-data-boundary)
  - [Good Auditability Direction](#good-auditability-direction)
  - [Sensible Layered Model](#sensible-layered-model)
- [Gap Analysis](#gap-analysis)
  - [Gap 1: Project State Is Internally Inconsistent](#gap-1-project-state-is-internally-inconsistent)
  - [Gap 2: `SKILL.md` References Scripts That Do Not Exist](#gap-2-skillmd-references-scripts-that-do-not-exist)
  - [Gap 3: Installable Skill Package Is Too Broad](#gap-3-installable-skill-package-is-too-broad)
  - [Gap 4: Data Contract Is Missing](#gap-4-data-contract-is-missing)
  - [Gap 5: Threshold Policies Are Under-Specified](#gap-5-threshold-policies-are-under-specified)
  - [Gap 6: Phase 1 Scope Is Too Wide](#gap-6-phase-1-scope-is-too-wide)
  - [Gap 7: No Tests or Runnable Examples Exist Yet](#gap-7-no-tests-or-runnable-examples-exist-yet)
  - [Gap 8: Output Contract Is Not Yet Formal Enough](#gap-8-output-contract-is-not-yet-formal-enough)
- [Recommended Solutions](#recommended-solutions)
  - [1. Update State Docs First](#1-update-state-docs-first)
  - [2. Treat Current `SKILL.md` as a Phase 0 Instruction Draft](#2-treat-current-skillmd-as-a-phase-0-instruction-draft)
  - [3. Build Minimal Phase 1 Runnable CSV Core Before Installation](#3-build-minimal-phase-1-runnable-csv-core-before-installation)
  - [4. Separate Authoring Docs From Installable Skill Package](#4-separate-authoring-docs-from-installable-skill-package)
  - [5. Create the Data Contract Before Matching Logic](#5-create-the-data-contract-before-matching-logic)
  - [6. Add Validator Tests Before Broad Analysis Logic](#6-add-validator-tests-before-broad-analysis-logic)
  - [7. Defer Excel and LLM Drafting Until Reconciliation Core Is Proven](#7-defer-excel-and-llm-drafting-until-reconciliation-core-is-proven)
- [Recommended Phase Plan](#recommended-phase-plan)
  - [Phase 0: State Cleanup and Instruction Draft Completion](#phase-0-state-cleanup-and-instruction-draft-completion)
  - [Phase 1A: Validator, Data Contract, and Examples](#phase-1a-validator-data-contract-and-examples)
  - [Phase 1B: Minimal Reconciliation Skeleton](#phase-1b-minimal-reconciliation-skeleton)
  - [Phase 2: Rate Card and Margin](#phase-2-rate-card-and-margin)
  - [Phase 3: Trend and Anomaly Detection](#phase-3-trend-and-anomaly-detection)
  - [Phase 4: LLM Analyst Layer](#phase-4-llm-analyst-layer)
  - [Phase 5: Optional Accounting-System MCP](#phase-5-optional-accounting-system-mcp)
- [Acceptance Criteria](#acceptance-criteria)
- [Risks and Caveats](#risks-and-caveats)
  - [External Reference Trial Risk](#external-reference-trial-risk)
  - [Business-Specific Mapping Risk](#business-specific-mapping-risk)
  - [Threshold Precision Risk](#threshold-precision-risk)
  - [Installed-Skill Readiness Risk](#installed-skill-readiness-risk)
- [Final Recommendation](#final-recommendation)

---

Status: planning artifact  
Created: 2026-05-21 16:36 Australia/Melbourne  
Scope: `invoice-finance-analyst` skill authoring folder  
Primary subject: `internal-invoice-analysis` skill

## Executive Summary

The project is directionally strong. The core design choice is correct: analyze internal invoice, sales, billing, rate-card, and profitability CSVs using deterministic Python/pandas calculations, then use the LLM only for explanation, classification, and management-facing narrative.

The strongest part of the current design is the hard boundary between calculated facts and interpretation. Numeric conclusions are required to come from source files, calculated output tables, or explicit assumptions. The project also correctly blocks external financial, market, CPI, inflation, FX, stock, benchmark, and macroeconomic data by default.

The main risk is now project-state mismatch. The repo contains an `internal-invoice-analysis/SKILL.md`, but the roadmap and scratchpad still describe the project as if no skill implementation exists. The skill also references runnable scripts that have not been created yet. If installed now, the skill would overstate its readiness and could direct an agent to run unavailable tooling.

The next step should not be a broad feature build. It should be a small state-correction and runnable-MVP pass: update state docs, keep the current skill positioned as a Phase 0 instruction draft, then build the minimum CSV validation and reconciliation core with tests.

## Current State

### Existing Files and Artifacts

The current authoring folder includes:

| Path | Current role |
|---|---|
| `README.md` | Build spec and project overview for creating the `internal-invoice-analysis` skill |
| `ROADMAP.md` | Phase 0-5 implementation roadmap |
| `ARCHITECTURE.md` | Layered analysis architecture, severity model, and invariants |
| `SETUP.md` | Python, venv, dependency, invocation, and runtime-path guidance |
| `SCRATCHPAD.md` | Current-state memory and recent-session summary |
| `docs/invoice_analysis_framework.md` | Source framework document and methodology reference |
| `internal-invoice-analysis/SKILL.md` | Phase 0 skill instruction draft with hard rules and 15-step workflow |

### Missing Files and Capabilities

The project does not yet include:

- `scripts/validate_inputs.py`
- `scripts/invoice_analysis_skeleton.py`
- `tests/test_validate_inputs.py`
- minimal CSV examples under `examples/`
- markdown report templates under `templates/`
- `docs/data_contract.md`
- `docs/analysis_layers.md`
- `docs/assumptions_and_limits.md`
- a runnable validation workflow
- deterministic reconciliation output
- machine-readable exports
- Excel workbook output

### Stale State

`ROADMAP.md` still says Phase 0 is not started and that no implementation files exist. That is no longer accurate because `internal-invoice-analysis/SKILL.md` exists.

`SCRATCHPAD.md` also says no `SKILL.md`, scripts, templates, docs, or tests have been built yet. That is partially stale: scripts, templates, docs, and tests are still missing, but `SKILL.md` has been created.

The practical risk is that future agents may rely on the stale state and either recreate the skill unnecessarily or miss the need to reconcile the existing skill with the planned scripts.

## Strengths

### Correct Calculation Authority

The project consistently treats Python/pandas as the source of truth for numeric work. This is the right design for invoice reconciliation because totals, variances, margins, duplicate counts, and exception values must be reproducible.

The LLM layer is correctly limited to:

- explaining calculated exceptions;
- grouping suspected causes;
- drafting management summaries;
- suggesting follow-up checks;
- preparing dispute or internal-ticket language.

It must not invent values, change calculated amounts, or perform unverified arithmetic.

### Strong Anti-Hallucination Rules

The skill draft explicitly blocks invented service mappings, prices, dates, service IDs, and customer names. Missing values must be exceptions, not assumptions silently filled by the model.

This is important because invoice analysis often has ambiguous descriptions, inconsistent service identifiers, and partial rate-card coverage. The correct behavior is to preserve ambiguity and route it to review, not to force a tidy answer.

### Clear External Data Boundary

The source framework, local AGENTS policy, and skill draft all agree: no external market, CPI, inflation, FX, stock, benchmark, or macroeconomic data should be used unless the user explicitly asks.

That is the right default. The first version is an internal financial reconciliation tool, not a market-research or benchmarking agent.

### Good Auditability Direction

The architecture requires source file hashes, row counts, calculated output tables, and visible assumptions. This supports repeatability and review.

The proposed evidence table is also a strong requirement. Every executive-summary claim should map back to a source row, aggregate table, or declared assumption.

### Sensible Layered Model

The layer breakdown is sound:

1. source inventory;
2. schema validation;
3. normalization;
4. invoice-to-sales reconciliation;
5. rate-card validation;
6. profitability analysis;
7. trend and anomaly detection;
8. aging/payment status when payment data exists;
9. LLM reasoning and explanation.

This creates a good path from simple profiling to operational analysis without forcing every advanced feature into the first release.

## Gap Analysis

### Gap 1: Project State Is Internally Inconsistent

The live file tree and the status docs disagree. `internal-invoice-analysis/SKILL.md` exists, while `ROADMAP.md` and `SCRATCHPAD.md` still say no implementation files exist.

Impact:

- future agents may duplicate work;
- Phase 0 exit criteria are unclear;
- progress cannot be trusted without re-reading the tree;
- install readiness is easy to overstate.

Solution:

- update `ROADMAP.md` to mark Phase 0 as partially complete;
- move `SKILL.md exists` into completed work;
- keep external skill trials and script scaffolding as open items;
- update `SCRATCHPAD.md` to say only the instruction draft exists.

### Gap 2: `SKILL.md` References Scripts That Do Not Exist

The skill says it works with:

- `scripts/validate_inputs.py`;
- `scripts/invoice_analysis_skeleton.py`.

Those files are not present. That means the installed skill would currently direct an agent to run unavailable commands.

Impact:

- the skill is not operationally honest;
- agents may claim deterministic validation without actually running it;
- user-facing workflows would fail at runtime.

Solution:

- either revise `SKILL.md` to label scripts as planned until created;
- or create the two scripts before installing the skill to `~/.claude/skills/` or `~/.codex/skills/`.

Recommended path: create the scripts in Phase 1 and do not install the skill until tests pass.

### Gap 3: Installable Skill Package Is Too Broad

The README target structure includes `README.md`, examples, docs, tests, scripts, and templates inside `internal-invoice-analysis/`.

That is useful for the authoring repo, but installed Codex/Claude skills should stay lean. The runtime skill should not carry project-management docs unless they directly improve execution.

Impact:

- more context bloat when agents load or inspect the skill;
- unclear boundary between authoring documentation and runtime skill behavior;
- harder installation and maintenance.

Solution:

Use two surfaces:

| Surface | Contents |
|---|---|
| Authoring folder | roadmap, architecture, setup, tests, examples, implementation notes |
| Installable skill package | `SKILL.md`, `scripts/`, `references/`, `templates/`, optional `agents/openai.yaml` |

The authoring folder can remain detailed. The installed skill should expose only the minimum materials an agent needs to perform invoice analysis.

### Gap 4: Data Contract Is Missing

The workflow depends on canonical fields such as `invoice_number`, `supplier_service_id`, `customer_id`, `amount_ex_tax`, and `billing_period_start`, but `docs/data_contract.md` has not been created.

Impact:

- matching logic cannot be implemented safely;
- required vs optional fields are unclear;
- column-mapping prompts will vary between agents;
- tests cannot lock expected behavior.

Solution:

Create `docs/data_contract.md` before implementing reconciliation logic. It should define:

- invoice input fields;
- sales/customer billing input fields;
- rate-card fields;
- service mapping fields;
- customer/product master fields;
- optional payment fields;
- derived output fields;
- mapping examples for common column-name variants.

Each field should be marked as required, optional, or derived.

### Gap 5: Threshold Policies Are Under-Specified

The skill intentionally leaves several thresholds as business-specific TODOs:

- amount-match absolute tolerance;
- amount-match percentage tolerance;
- low-margin percentage threshold;
- recurring-charge change threshold;
- usage-spike multiplier;
- severity component scoring.

This is appropriate for design honesty, but it blocks deterministic implementation unless the Phase 1 behavior is narrowed.

Impact:

- agents could choose inconsistent defaults;
- different runs may classify the same records differently;
- severity outputs may look more precise than they really are.

Solution:

For Phase 1:

- use strict exact or rounding-only amount matching;
- do not emit low-margin flags unless a threshold is explicitly supplied;
- do not emit trend or anomaly flags without prior-period data and configured thresholds;
- include all unresolved threshold values in the assumptions/data gaps section.

For later phases, move thresholds into a config file or explicit CLI arguments.

### Gap 6: Phase 1 Scope Is Too Wide

The roadmap currently includes schema validation, normalization, reconciliation, exception output, Excel workbook output, source hashes, examples, templates, docs, tests, and scaffolding.

That is more than a clean first executable release.

Impact:

- high chance of partially working code;
- tests may lag behind features;
- Excel generation can distract from core matching correctness;
- business-specific matching decisions may get buried in output formatting work.

Solution:

Split Phase 1 into two sub-phases:

| Sub-phase | Goal |
|---|---|
| Phase 1A | CSV profiling, validation, source hashing, data contract, examples, validator tests |
| Phase 1B | Minimal invoice-to-sales matching, deterministic markdown/json output, reconciliation tests |

Excel workbook output should move to Phase 1C or Phase 2 after the core tables are stable.

### Gap 7: No Tests or Runnable Examples Exist Yet

There are no minimal CSV fixtures or pytest tests. The project cannot currently prove validator behavior, read-only input handling, duplicate detection, or failure paths.

Impact:

- no regression protection;
- no clear acceptance test for the first runnable version;
- agents may implement logic that looks plausible but fails on simple CSVs.

Solution:

Create minimal examples early:

- one invoice line that matches one sales line;
- one invoice line with no sales match;
- one sales line with no invoice match;
- one duplicate invoice line;
- one amount mismatch;
- one malformed/non-CSV test file generated in pytest temp storage.

Then add tests for:

- valid CSV profiling;
- missing file failure;
- non-CSV extension failure;
- duplicate row count;
- null counts;
- numeric-looking column detection;
- date-looking column detection;
- no source-file mutation.

### Gap 8: Output Contract Is Not Yet Formal Enough

The project mentions Excel workbook tabs and machine-readable exports, but no minimum output schema is defined.

Impact:

- different implementations may produce incompatible tables;
- LLM report evidence links may break;
- downstream automation cannot rely on stable column names.

Solution:

Define minimum output tables before implementation:

- `source_file_inventory`;
- `schema_validation`;
- `data_quality_issues`;
- `reconciliation_summary`;
- `matched_lines`;
- `invoice_no_sales`;
- `sales_no_invoice`;
- `amount_mismatches`;
- `assumptions`;
- `run_summary`.

For Phase 1, write markdown and JSON/CSV outputs first. Add Excel after the table contracts settle.

## Recommended Solutions

### 1. Update State Docs First

Before adding logic, update the project state:

- `ROADMAP.md`: Phase 0 is partially complete because `SKILL.md` exists.
- `SCRATCHPAD.md`: current state should say the instruction draft exists, but scripts/tests/examples/templates are still missing.

This prevents future work from starting from stale assumptions.

### 2. Treat Current `SKILL.md` as a Phase 0 Instruction Draft

The current `SKILL.md` is useful and mostly well-framed. It should not yet be treated as a fully operational skill because it references unavailable scripts.

Recommended label:

> Phase 0 instruction draft. Do not install as an operational skill until Phase 1 scripts and tests exist.

### 3. Build Minimal Phase 1 Runnable CSV Core Before Installation

The first operational milestone should be small:

- validate input CSVs;
- record file hashes and row counts;
- profile columns, nulls, duplicates, numeric-looking fields, and date-looking fields;
- load invoice and sales CSVs;
- perform basic exact-key reconciliation when mapping fields are provided;
- emit deterministic output tables;
- run pytest successfully.

Do not install the skill to runtime skill folders until this passes.

### 4. Separate Authoring Docs From Installable Skill Package

Keep detailed planning and project docs in the authoring folder. Keep runtime skill content lean.

Recommended runtime package:

```text
internal-invoice-analysis/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── data_contract.md
│   ├── analysis_layers.md
│   └── assumptions_and_limits.md
├── scripts/
│   ├── validate_inputs.py
│   └── invoice_analysis_skeleton.py
└── templates/
    ├── findings_report_template.md
    ├── reconciliation_report_template.md
    └── variance_report_template.md
```

Keep tests and examples in the authoring repo unless the installed skill genuinely needs them at runtime.

### 5. Create the Data Contract Before Matching Logic

`docs/data_contract.md` should be the next design artifact after state cleanup. It should lock the minimum field names and explain mapping behavior.

The data contract should include:

- required fields for Phase 1;
- optional fields for later phases;
- derived fields;
- examples of source-column mapping;
- how missing required columns are reported;
- how ambiguous columns trigger confirmation instead of silent mapping.

### 6. Add Validator Tests Before Broad Analysis Logic

The validator is the lowest-risk deterministic layer. It should be test-driven first because every later phase depends on trustworthy source profiling.

Minimum tests:

- accepts a valid CSV;
- rejects missing file;
- rejects non-CSV extension;
- reports row count;
- reports columns;
- reports null counts;
- reports duplicate row count;
- detects numeric-looking columns;
- detects date-looking columns;
- does not modify source input.

### 7. Defer Excel and LLM Drafting Until Reconciliation Core Is Proven

Excel workbook generation and LLM analyst summaries are valuable, but they are not the first correctness problem.

Defer:

- workbook formatting;
- charts;
- pivot-style summaries;
- supplier dispute drafts;
- internal ticket drafts;
- full trend detection;
- full margin automation.

Build those after deterministic tables are stable.

## Recommended Phase Plan

### Phase 0: State Cleanup and Instruction Draft Completion

Goal: make the repo state truthful and keep the skill draft internally consistent.

Work:

- update `ROADMAP.md`;
- update `SCRATCHPAD.md`;
- revise `SKILL.md` if necessary so it does not imply missing scripts are available;
- decide which docs belong in authoring vs installed package;
- optionally capture notes from external finance skill references, but do not block local progress on them.

Exit criteria:

- state docs match the live file tree;
- `SKILL.md` clearly says whether it is runnable or draft-only;
- no installation to runtime skill folders has occurred.

### Phase 1A: Validator, Data Contract, and Examples

Goal: build the deterministic source-inventory and schema-profiling base.

Work:

- create `docs/data_contract.md`;
- create minimal invoice, sales, and rate-card examples;
- implement `scripts/validate_inputs.py`;
- add pytest coverage for validator behavior.

Exit criteria:

- `pytest tests/` passes;
- validator profiles valid CSVs;
- validator fails clearly for missing and non-CSV files;
- source file hashes, row counts, column names, null counts, duplicates, numeric-looking columns, and date-looking columns are reported.

### Phase 1B: Minimal Reconciliation Skeleton

Goal: produce the first deterministic reconciliation output.

Work:

- implement `scripts/invoice_analysis_skeleton.py`;
- load invoice and sales CSVs;
- normalize configured amount/date columns;
- match invoice and sales rows using exact service/period keys where available;
- classify matched, invoice-only, sales-only, duplicate, and amount-mismatch rows;
- export markdown and machine-readable outputs.

Exit criteria:

- minimal examples produce expected output;
- no source CSVs are modified;
- each output metric is traceable to source rows or a declared assumption.

### Phase 2: Rate Card and Margin

Goal: add rate-card validation and direct-margin reporting.

Work:

- add rate-card input support;
- calculate expected supplier cost and expected customer revenue;
- separate supplier-rate variance from customer-revenue variance;
- calculate direct margin and margin percentage;
- flag negative and low-margin services when thresholds are configured.

Exit criteria:

- rate-card mismatches are separated from mapping mismatches;
- direct-margin outputs exclude tax;
- negative-margin exceptions are deterministic.

### Phase 3: Trend and Anomaly Detection

Goal: compare current-period data to prior-period data.

Work:

- support prior-period inputs;
- detect new and removed recurring services;
- detect recurring charge changes;
- detect usage spikes when thresholds are configured;
- identify margin movement.

Exit criteria:

- monthly changes are explained through calculated tables;
- high-impact changes are prioritized without LLM-only scoring.

### Phase 4: LLM Analyst Layer

Goal: generate management-ready interpretation from calculated outputs.

Work:

- feed only calculated summaries and exception tables to the LLM;
- generate executive summary;
- classify suspected root causes;
- recommend checks;
- draft supplier dispute notes or internal tickets when requested.

Exit criteria:

- every LLM statement links to a table, row count, metric, or explicit assumption;
- no external data is used unless explicitly requested.

### Phase 5: Optional Accounting-System MCP

Goal: reduce CSV export friction only if manual exports become the bottleneck.

Work:

- evaluate Xero MCP, Odoo MCP, or another accounting integration only if the workflow requires it;
- keep CSV mode as the stable fallback.

Exit criteria:

- integration is justified by repeated CSV export pain;
- external system access does not weaken source traceability or review controls.

## Acceptance Criteria

The next implementation pass should be considered complete only when:

- `pytest tests/` passes;
- validator handles valid CSV input;
- validator fails clearly on missing files;
- validator fails clearly on non-CSV files;
- validator reports null counts;
- validator reports duplicate row counts;
- validator reports numeric-looking columns;
- validator reports date-looking columns;
- analysis skeleton can load invoice and sales CSVs;
- analysis skeleton can produce deterministic summary output;
- source CSVs are not modified;
- `SKILL.md` does not claim unavailable scripts or outputs exist;
- every numeric report claim is traceable to source data, calculated output, or declared assumption.

## Risks and Caveats

### External Reference Trial Risk

The roadmap mentions trialing Open Accountant Skills and reviewing finance plugins. That can be useful, but it should not block the local MVP.

External references may provide good workflow ideas, but this project has stricter constraints:

- source-data-only by default;
- no external financial data;
- no invented mappings;
- deterministic calculations first.

Any borrowed method should be adapted, not imported wholesale.

### Business-Specific Mapping Risk

Invoice and sales exports often vary by supplier, system, and reporting period. The tool should not pretend there is one universal schema.

Mitigation:

- keep canonical fields stable;
- require explicit column mapping when confidence is low;
- preserve unmapped records;
- treat mapping overrides as reviewed configuration, not LLM guesses.

### Threshold Precision Risk

Severity and anomaly thresholds can create false confidence if not grounded in business policy.

Mitigation:

- make thresholds explicit;
- default to conservative behavior;
- disclose thresholds in every report;
- avoid automated severity scoring until component scores are defined.

### Installed-Skill Readiness Risk

Installing the skill before scripts and tests exist would create a misleading operational surface.

Mitigation:

- keep install as a backlog item until Phase 1 passes;
- install only from the canonical authoring folder;
- verify installed files match source files after copy.

## Final Recommendation

Do the next pass in this order:

1. Correct `ROADMAP.md` and `SCRATCHPAD.md`.
2. Mark the existing `SKILL.md` as a Phase 0 instruction draft unless scripts are built immediately.
3. Create `docs/data_contract.md`.
4. Implement and test `scripts/validate_inputs.py`.
5. Add minimal CSV examples.
6. Implement the smallest useful reconciliation skeleton.
7. Install the skill only after tests and example runs pass.

This keeps the project honest, runnable, and aligned with its most important constraint: calculated financial facts must come from source data and deterministic processing, not from model inference.
