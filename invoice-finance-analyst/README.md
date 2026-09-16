# Invoice Finance Analyst

## Contents

- [Current status](#current-status)
- [Governance pointers](#governance-pointers)
- [Folder index](#folder-index)
- [Build spec — `internal-invoice-analysis` skill](#build-spec-internalinvoiceanalysis-skill)
  - [Context](#context)
  - [Core requirements](#core-requirements)
  - [Target folder structure](#target-folder-structure)
  - [SKILL.md requirements](#skillmd-requirements)
  - [`scripts/validate_inputs.py` requirements](#scriptsvalidate_inputspy-requirements)
  - [`scripts/invoice_analysis_skeleton.py` requirements](#scriptsinvoice_analysis_skeletonpy-requirements)
  - [`templates/` requirements](#templates-requirements)
  - [`docs/data_contract.md` requirements](#docsdata_contractmd-requirements)
  - [`docs/analysis_layers.md` requirements](#docsanalysis_layersmd-requirements)
  - [`docs/assumptions_and_limits.md` requirements](#docsassumptions_and_limitsmd-requirements)
  - [`tests/test_validate_inputs.py` requirements](#teststest_validate_inputspy-requirements)
  - [Quality rules](#quality-rules)
  - [After creating files](#after-creating-files)

---

Authoring folder for the `internal-invoice-analysis` skill — a production-ready, agent-agnostic skill for multi-layer internal CSV invoice reconciliation, rate-card validation, margin analysis, and anomaly detection.

## Current status

**Phase 4 runnable — not finance-control complete.** All 4 phases operational; `pytest tests/` → **219/219** (Python 3.14.4, 2026-05-21). Finance control checklist, citation validator, and deterministic severity scoring still pending (Phases 4b–4c).

| Phase | Deliverable | Status |
|---|---|---|
| 0 | `SKILL.md` — 15-step workflow, thresholds, Evidence Rule | ✓ |
| 1A | `validate_inputs.py`, `data_contract.md`, fixtures | ✓ |
| 1B | `load_inputs.py`, `invoice_analysis_skeleton.py`, output schema | ✓ |
| 2 | `rate_card_analysis.py` — rate variance, margin, low-margin exceptions | ✓ |
| 3 | `trend_analysis.py` — MoM variance, spikes, recurring changes, margin movement | ✓ |
| 4 | `llm_analyst.py` — provider-agnostic LLM report (Evidence Rule enforced) | runnable ★ |
| 5 | Accounting system MCP | backlog |

★ Phase 4 runnable: finance_control_checklist.parquet, citation validator, and deterministic severity scoring pending (Phase 4b–4c).

Next: `lineage.json` append + phase-status marker across all 5 scripts (Phase 4a), then service-map reconciliation (Phase 4b.1).

---

## Governance pointers

| Document | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Local agent rules — hard constraints, venv routing |
| [AI_NAVIGATION.md](AI_NAVIGATION.md) | AI context entrypoint — what to read first, task routing |
| [context-map.yaml](context-map.yaml) | Machine-readable task-to-context routing map |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 8-layer pipeline, severity model, invariants |
| [SETUP.md](SETUP.md) | venv, dependencies, invocation patterns |
| [ROADMAP.md](ROADMAP.md) | Phase 0–5 implementation plan, gap review decisions |
| [scripts/README.md](scripts/README.md) | Pipeline script catalog — inputs, outputs, safety labels |
| [CHANGELOG.md](CHANGELOG.md) | Project and governance history ledger |
| [../AGENTS.md](../AGENTS.md) | Parent area guidance |
| [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md) | Canonical governance root |

## Folder index

| Path | Role |
|---|---|
| [docs/invoice_analysis_framework.md](docs/invoice_analysis_framework.md) | Planning/research artifact — 884-line design survey; see ARCHITECTURE.md for what was actually built |
| [docs/feedback/](docs/feedback/) | Feedback and review docs — gap review, unified plan, Hermes review, tool evaluations |
| [.remember/](.remember/) | Session memory buffer (auto-managed, git-ignored) |

---

## Build spec — `internal-invoice-analysis` skill

### Context

This folder contains the design materials for a reusable AI skill for internal multi-layer invoice analysis. Use the source design document as the authority for the workflow, but improve it into a clean operational skill.

- **Planning/research artifact:** [`docs/invoice_analysis_framework.md`](docs/invoice_analysis_framework.md) — original design survey (884 lines). Use ARCHITECTURE.md and SKILL.md as the authoritative implementation references.
- **Skill name:** `internal-invoice-analysis`
- **Primary purpose:** Analyze user-provided invoice CSVs, sales CSVs, rate cards, and profitability/export reports using internal financial/accounting reasoning only. Do not use external market, inflation, FX, CPI, stock, or macroeconomic data unless the user explicitly asks for it.

### Core requirements

The skill must combine:

1. Deterministic Python/pandas calculation layer
2. Finance/accounting reasoning layer from the skill instructions
3. Explicit anti-hallucination rules
4. Clear input/output contracts
5. Multi-layer invoice analysis workflow

### Target folder structure

```
internal-invoice-analysis/
└── SKILL.md                          ← v0.4.0, Phase 4 runnable (not finance-control complete)

scripts/                              ← run in this order
├── validate_inputs.py                ← Phase 1A: schema check, suggest-mapping
├── load_inputs.py                    ← Phase 1B: CSV → parquet (all 4 source types)
├── invoice_analysis_skeleton.py      ← Phase 1B: reconciliation → 9 output tables
├── rate_card_analysis.py             ← Phase 2:  rate variance + margin → 6 tables
├── trend_analysis.py                 ← Phase 3:  MoM trend → 7 tables (optional)
└── llm_analyst.py                    ← Phase 4:  LLM analyst report (provider-agnostic)

tests/
├── test_validate_inputs.py           ← 33 tests
├── test_reconciliation.py            ← 41 tests
├── test_rate_card_analysis.py        ← 47 tests
├── test_trend_analysis.py            ← 48 tests
└── test_llm_analyst.py               ← 50 tests (mocked API)

examples/
├── supplier_invoice_sample.csv       ← current period fixtures
├── sales_billing_sample.csv
├── rate_card_sample.csv
├── service_map_sample.csv
├── prior_invoice_sample.csv          ← prior period (Phase 3)
├── prior_sales_billing_sample.csv
├── mapping_*.yaml                    ← column mapping configs
└── README.md

docs/
├── invoice_analysis_framework.md    ← planning/research artifact (not operational spec)
├── data_contract.md                 ← canonical schema, 4 source types
├── output_schema.md                 ← 22 parquet tables + analyst_report.md
└── feedback/                        ← gap review, unified plan, tool evaluations

db/                                  ← parquet outputs (git-ignored)
output/                              ← run outputs: markdown + analyst_report.md (git-ignored)
```

---

### SKILL.md requirements

**Metadata:**

```yaml
name: internal-invoice-analysis
description: >
  Use when the user provides invoice, sales, rate-card, billing, cost, margin,
  or profitability CSVs and asks for financial comparison, reconciliation,
  variance analysis, anomaly detection, margin review, or multi-layer invoice analysis.
```

**Hard rules to include:**

- Do not fetch external financial/market/macro data by default.
- Do not invent missing values.
- Do not assume column meanings without mapping.
- Ask for column mapping only when needed.
- Prefer deterministic calculations over LLM-only reasoning.
- Separate calculated facts from interpretation.
- Record assumptions in every report.

**15-step workflow:**

1. Input inventory
2. Schema detection
3. Column mapping
4. Data quality checks
5. Invoice normalization
6. Sales/revenue normalization
7. Rate-card matching
8. Reconciliation
9. Variance analysis
10. Margin/profitability analysis
11. Anomaly detection
12. Root-cause grouping
13. Executive summary
14. Evidence table
15. Open questions / missing data

**Required response sections:**

- Summary
- Files analyzed
- Assumptions
- Calculated findings
- Variances
- Suspected causes
- Recommended checks
- Data gaps
- Confidence rating

---

### `scripts/validate_inputs.py` requirements

- Python 3.11+ (use 3.14.4 for this project — see [SETUP.md](SETUP.md))
- Accept one or more CSV paths as arguments
- Print per file: row count, column names, null counts, duplicate row count, numeric-looking columns, date-looking columns
- Do not modify any file
- Fail clearly if a file is missing or not CSV

### `scripts/invoice_analysis_skeleton.py` requirements

- Python 3.11+ / pandas
- Provide functions:

| Function | Purpose |
|---|---|
| `load_csv` | Load and profile a CSV file |
| `profile_dataframe` | Row count, column types, nulls, dupes |
| `normalize_money_columns` | Coerce to numeric, handle currency symbols |
| `normalize_date_columns` | Parse and standardize date fields |
| `compare_invoice_to_sales` | Match invoice lines to sales lines |
| `compare_invoice_to_rate_card` | Validate actual vs expected charges |
| `calculate_margin` | `revenue_ex_tax − cost_ex_tax` per record |
| `detect_variances` | Flag amount/period/rate mismatches |
| `export_findings_markdown` | Write structured findings to markdown |

- Keep implementation conservative and safe
- Include `# TODO:` markers where business-specific mapping is required
- Do not hardcode fake business logic

---

### `templates/` requirements

Practical markdown templates the agent fills after analysis. Each must include:

- Evidence table (source file, row reference, calculated value)
- Assumptions section
- Data gaps section

### `docs/data_contract.md` requirements

Define recommended input columns for: invoices, sales, rate cards, profitability reports.
Mark each column as **required**, *optional*, or _derived_. Include column mapping examples.

### `docs/analysis_layers.md` requirements

Explain each layer: schema, data quality, reconciliation, rate validation, margin, trend, anomaly, executive interpretation.

### `docs/assumptions_and_limits.md` requirements

- No external financial data unless user requests it
- No tax/legal/accounting compliance advice as final authority
- No guessing missing costs
- No hidden normalization
- Every assumption must be visible in the output

### `tests/test_validate_inputs.py` requirements

- Basic pytest tests for CSV validation behavior
- Use temporary CSV fixtures (no network access required)

---

### Quality rules

- FOSS-friendly — no paid API dependencies
- Do not add OpenBB as a default dependency
- Do not add LangChain/LlamaIndex unless the framework doc explicitly requires them; if mentioned, keep optional only
- Prefer plain Python + pandas + markdown skill instructions
- Usable without internet access
- Outputs deterministic where possible
- `# TODO:` markers only where real business-specific mapping is required

---

### After creating files

1. Show the final directory tree.
2. Summarize what was created.
3. Identify any assumptions made.
4. Give exact next commands to test the skill.
5. Do not perform external web searches.
