# Hermes Skill Review — Invoice Finance Analyst

## Contents

- [Context](#context)
- [What's Excellent](#whats-excellent)
  - [Cleanest architectural separation for a skill this young](#cleanest-architectural-separation-for-a-skill-this-young)
  - [The core design principle is right](#the-core-design-principle-is-right)
  - [219 tests at this stage is impressive](#219-tests-at-this-stage-is-impressive)
  - [Output schema locked before implementation](#output-schema-locked-before-implementation)
  - [Thresholds calibrated from real data](#thresholds-calibrated-from-real-data)
  - [Provider-agnostic LLM layer](#provider-agnostic-llm-layer)
- [What's a Concern](#whats-a-concern)
  - [1. The matching key is too narrow for production](#1-the-matching-key-is-too-narrow-for-production)
  - [2. No error handling or partial-output strategy](#2-no-error-handling-or-partial-output-strategy)
  - [3. The naming split will cause confusion](#3-the-naming-split-will-cause-confusion)
  - [4. The framework doc is a planning artifact](#4-the-framework-doc-is-a-planning-artifact)
  - [5. No historical run management](#5-no-historical-run-management)
  - [6. Duplicate handling is row-exact only](#6-duplicate-handling-is-row-exact-only)
  - [7. No performance characteristics documented](#7-no-performance-characteristics-documented)
- [What I'd Prioritise Differently Than the Gap Review](#what-id-prioritise-differently-than-the-gap-review)
- [Overall Verdict](#overall-verdict)

---

Status: external review  
Created: 2026-05-21 22:50 Australia/Melbourne  
Reviewer: Hermes Agent  
Scope: `invoice-finance-analyst` authoring folder through Phase 4  
Focus: Architectural assessment, strengths, concerns, and priority observations

---

## Context

This document captures a review of the `invoice-finance-analyst` skill (built name: `internal-invoice-analysis`) performed by Hermes Agent alongside a separate gap-review document. This is not a gap audit — it is a subjective architectural and strategic assessment of the skill's design, strengths, and risks.

---

## What's Excellent

### Cleanest architectural separation for a skill this young

Phases 0→4 are genuinely modular. You could extract Phase 3 (trend analysis) or Phase 4 (LLM analyst) without breaking Phases 1–2. Each phase has:

- A single-purpose Python script with a clear docstring, CLI, and output contract
- Its own test module with phase-specific fixtures
- Clear exit criteria in ROADMAP.md

This is rare at this stage of maturity. Most skills start as a monolithic script with a "Phase 1" label; this one was designed modularly from the start.

### The core design principle is right

> All numeric conclusions must be traceable to a source file, calculated table, or declared assumption — never to LLM inference alone.

This is the hardest constraint to enforce in an LLM-driven system, and it's baked into the architecture at every layer. The Evidence Rule (`[table: <name> | metric: <column_or_aggregate> | value: <value>]`) in Phase 4 is exactly the right control. The external-data ban is smart — block first, opt-in later.

### 219 tests at this stage is impressive

Not the raw count — the structure. Five test modules, each corresponding to a phase, with clear boundaries:

- `test_validate_inputs.py` (33) — schema validation, duplicates, mapping YAML
- `test_reconciliation.py` (41) — outer join, match classification, amount tolerance
- `test_rate_card_analysis.py` (47) — rate variance, margin, low-margin exceptions
- `test_trend_analysis.py` (48) — MoM variance, spikes, recurring changes
- `test_llm_analyst.py` (50) — mocked API, prompt content, report writing

No cross-module test leakage. Each module can run independently.

### Output schema locked before implementation

`docs/output_schema.md` defines column names, types, and descriptions for all 22 parquet tables before any script writes them. This prevents the common pattern where output columns drift across script versions and downstream consumers break silently.

### Thresholds calibrated from real data

Not invented:

| Threshold | Value | Source |
|---|---|---|
| `AMOUNT_MATCH_TOLERANCE_ABS` | 0.02 | House rounding standard |
| `AMOUNT_MATCH_TOLERANCE_PCT` | 0.001 | Float drift |
| `LOW_MARGIN_PCT_THRESHOLD` | 0.05 | Below APN adjusted target (~8.4%) |
| `USAGE_SPIKE_MULTIPLIER` | 2.0 | Operational judgment |
| `RECURRING_CHANGE_THRESHOLD_PCT` | 0.05 | Operational judgment |

### Provider-agnostic LLM layer

The OpenAI-compatible client (`base_url` pattern) means Phase 4 works with OpenAI, DeepSeek, Groq, Mistral, Ollama, Together AI, and LM Studio through the same interface. No provider lock-in.

---

## What's a Concern

### 1. The matching key is too narrow for production

Current join: `supplier_service_id + billing_period_start`

This works beautifully for the fixtures. In real APN multi-supplier data, you will hit:

- Different suppliers using the same internal service ID (collision)
- Invoice lines that span periods (partial-month billing)
- Services without explicit billing period fields
- One supplier invoice covering multiple customer services
- Services mapped differently in different periods (renegotiation)

The architecture doc describes a fallback chain (exact → service-type → fuzzy → manual) but only the first link is implemented. The first real-data discovery run will likely surface this within minutes.

### 2. No error handling or partial-output strategy

What happens when:

- Phase 2 crashes halfway through writing parquet outputs?
- Phase 4 gets an API 500 at row 42 of context serialisation?
- A source file is truncated mid-import?

There is no retry, no fallback, no "here's what we have so far" output. For an automated pipeline that a finance user might run unsupervised, this is a risk. A minimal approach: wrap each phase in `try/except` that writes a `phase_N_status: failed | partial | complete` marker before re-raising.

### 3. The naming split will cause confusion

| Context | Name |
|---|---|
| Authoring folder | `invoice-finance-analyst` |
| Built skill | `internal-invoice-analysis` |
| CLI paths | `db/`, `output/`, `scripts/` |

The folder name describes an agent role ("someone who analyses invoice finance"). The built skill name describes a process ("internal analysis of invoices"). This split is already visible in the docs and will compound as packaging and installation targets multiply.

### 4. The framework doc is a planning artifact

`docs/invoice_analysis_framework.md` is 884 lines of survey research — candidate tools, why-not-OpenBB, 10-row "fit" rating tables, skills from Open Accountant and Anthropic knowledge-work-plugins that were trialled but not used.

It is valuable as a design-decision record but not as an authoring reference. No developer or agent reaching for it will find the actual implemented architecture. Options:

- Archive it as `docs/framework_research.md` and replace with a concise 2-page spec
- Or keep it and add a one-paragraph "what was actually built vs what was surveyed" summary at the top

### 5. No historical run management

Every pipeline run produces:

- `db/*.parquet` (overwritten on next run, with 2 archived copies)
- `output/<run_id>/*.md` (UUID-tagged, no retention policy)
- `output/phase4_<run_id>/analyst_report.md` (UUID-tagged)

There is no way to say "show me what changed between March and April runs" without manually diffing two UUID'd output directories. For a finance pipeline that runs monthly, this becomes a problem around run 3.

A lightweight approach: maintain a `run_history.json` or `run_history.parquet` with run_id, timestamp, phase statuses, source hashes, and output directory path. Cross-run diffing is then a query, not a filesystem scavenger hunt.

### 6. Duplicate handling is row-exact only

Current dedup: `exact_row_match` on canonical fields.

Real invoice exports often have semantically identical rows with different line numbers, minor description differences, or split tax rows. A row-exact dedup will let near-duplicates through, which then appear as separate unmatched or matched lines and inflate exception counts.

### 7. No performance characteristics documented

For the fixture datasets (5–10 rows), pandas is instant. For a real APN monthly export (potentially thousands of lines per supplier, multiple suppliers, with rate-card and trend joins), the current approach is likely fine for tens of thousands of rows but there is no documented memory limit, chunking strategy, or guidance on when to switch to a database-style pipeline.

---

## What I'd Prioritise Differently Than the Gap Review

The gap review's 14-step fix order is sensible. My reorder for the top five:

| Priority | Item | Why earlier |
|---|---|---|
| 1 | Service-map-aware reconciliation | The #1 blocker between "works on fixtures" and "works on real data". Period-aware rates matter less if you can't match the lines at all. |
| 2 | Implement `_select_context_tables` | A 5-line change that costs ~30 tokens per run. Currently all 22 tables go to the LLM. Do this before the next real Phase 4 invocation. |
| 3 | Control totals and sign-off status | Finance teams will not trust the pipeline without "source total = normalized total = output total" tie-out. More important than GST logic or severity scoring. |
| 4 | GST, credit/reversal, and quantity-rate together | These three touch the same code paths (line-level classification and validation). Doing them separately means twice the fixture updates and twice the test churn. |
| 5 | Real-export validation | One run on a copy of real APN data will surface more issues than 100 fixture-only test cycles. Schedule before the packaging push. |

---

## Overall Verdict

This is a genuinely well-built skill. Most skills at this phase level have one working script and a half-baked SKILL.md. This one has:

- 5 production-quality scripts, each independently testable
- 219 tests across 5 modules with phase-specific fixtures
- A locked output schema defined before any code was written
- Thresholds calibrated from real APN/Vocus data, not invented
- Provider-agnostic LLM integration (OpenAI, DeepSeek, Groq, Ollama)
- Clear governance docs (AGENTS.md, ARCHITECTURE.md, ROADMAP.md, SETUP.md)
- A well-understood gap between "passes on fixtures" and "works on real data"

The most telling observation: every gap the review identifies is already known and documented — in ROADMAP.md backlog items, in ARCHITECTURE.md TODO markers, in assumption tables, in commented-out skeleton code. Nothing in the external review would have been a surprise discovered by running the pipeline. That is the mark of a project that is honest with itself about its maturity.

The work remaining is less about scaffolding and more about making the skill **finance-complete** — service mapping, period-aware rates, GST/tax controls, credit/reversal handling, control totals, real-export validation, and clean distribution. The bones are solid.
