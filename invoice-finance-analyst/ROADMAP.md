# ROADMAP — Invoice Finance Analyst

## Contents

- [Current phase](#current-phase)
- [Milestones](#milestones)
- [Completed](#completed)
- [Current backlog (ordered by phase)](#current-backlog-ordered-by-phase)
- [Feedback Review Log](#feedback-review-log)
- [Reference docs](#reference-docs)

---

## Current phase

**Phase 4 — LLM Analyst Layer** (partially complete — see assessment below)

Phase 0–3 complete 2026-05-21. Phase 4 scripts and tests exist. Context selection implemented 2026-05-22. Two exit criteria remain: citation validation missing, severity scoring documented but not
implemented.

## Milestones

### Phase 0 — Tool and Skill Trial ✓ *completed 2026-05-21*
- [x] `internal-invoice-analysis/SKILL.md` created with 15-step workflow
- [x] External data banned by default; thresholds calibrated from vocus-profitability data (`AMOUNT_MATCH_TOLERANCE_ABS = 0.02`, `AMOUNT_MATCH_TOLERANCE_PCT = 0.001`, `LOW_MARGIN_PCT_THRESHOLD =
  0.05`, `USAGE_SPIKE_MULTIPLIER = 2.0`, `RECURRING_CHANGE_THRESHOLD_PCT = 0.05`)
- [x] Open Accountant Skills / Anthropic knowledge-work-plugins not available locally — methodology synthesised from framework
- *Exit criteria met:* SKILL.md exists; 15-step workflow defined; external data banned

### Phase 0 Cleanup ✓ *completed 2026-05-21*
- [x] Draft label removed; frontmatter `status` field + visible callout block naming missing scripts
- *Exit criteria met:* SKILL.md does not imply unavailable scripts are operational; no install has occurred

### Phase 1A — Validator, Data Contract, and Examples ✓ *completed 2026-05-21*
- [x] `docs/data_contract.md` — canonical fields for all 4 source types, heuristic detection patterns, mapping validation rules, ambiguity protocol
- [x] `examples/` — `supplier_invoice_sample.csv` (5 rows), `sales_billing_sample.csv` (4 rows), mapping YAMLs, fixture README
- [x] `scripts/validate_inputs.py` — hash before/after, null counts, duplicate detection, numeric/date column detection, mapping validation, `--suggest-mapping` mode, JSON output flag
- [x] `tests/test_validate_inputs.py` — 33 tests, 9 classes
- *Exit criteria met:* `pytest tests/test_validate_inputs.py` → 33 passed, 0 failed (Python 3.14.4, 2026-05-21)

### Phase 1B — Minimal Reconciliation Skeleton ✓ *completed 2026-05-21*
- [x] `scripts/load_inputs.py` — validate → dtype=str load → mapping rename → type cast → snappy parquet to `db/`; archive-before-overwrite, 2 most recent kept
- [x] `docs/output_schema.md` — 9 tables, column names locked
- [x] `scripts/invoice_analysis_skeleton.py` — deduplicate → outer join on `supplier_service_id+billing_period_start` → classify → 9 output tables
- [x] Deterministic outputs verified — run c1100ec4: matched=3, invoice_only=1, sales_only=1, mismatch=1, duplicate_removed=1
- [x] `tests/test_reconciliation.py` — 41 tests, all passed
- *Exit criteria met:* `pytest tests/` → 74 passed, 0 failed (Python 3.14.4, 2026-05-21)

### Phase 1B Issue — Reconciled ID-Only ✓ *known limitation*
- Match key is `supplier_service_id + billing_period_start` only — no service-map bridging
- Assumptions table records: `"our_service_id_equals_supplier_service_id = True"`
- Works for fixtures where supplier and sales IDs match; will fail on real multi-supplier data
- Tracked in *Phase 4b — Functional Gaps*

### Phase 2 — Rate Card and Margin ✓ *completed 2026-05-21*
- [x] Rate card + service map fixtures — `examples/rate_card_sample.csv`, `examples/service_map_sample.csv`, mapping YAMLs
- [x] Heuristic patterns for rate_card and service_map fields added to `validate_inputs.py`
- [x] `scripts/rate_card_analysis.py` — 6 output tables: rate_variances, rate_card_mismatches, margin_by_customer, margin_by_service_type, low_margin_exceptions, phase2_assumptions
- [x] `docs/output_schema.md` extended with 6 Phase 2 tables (15 total)
- [x] `tests/test_rate_card_analysis.py` — 47 tests, 8 classes; full suite 121/121 passing
- *Exit criteria met:* margin report works; rate-card mismatches (2) separated from amount mismatches (1); low-margin exception detection verified

### Phase 2 Issue — Period-Unaware Rate Selection ✓ *known limitation*
- `_resolve_rate_card()` takes most recent effective date per service_type, regardless of billing period
- Does not check `effective_date <= billing_period_start` or `expiry_date`
- Can compare historical invoices against future rates if rerun after a rate card update
- Tracked in *Phase 4b — Functional Gaps*

### Phase 3 — Trend Detection ✓ *completed 2026-05-21*
- [x] Prior period fixtures — `examples/prior_invoice_sample.csv` (4 rows), `examples/prior_sales_billing_sample.csv` (3 rows)
- [x] `scripts/trend_analysis.py` — 7 output tables: mom_variance, new_services, removed_services, usage_spikes, recurring_changes, margin_movement, phase3_assumptions
- [x] `docs/output_schema.md` extended with 7 Phase 3 table definitions (22 total)
- [x] `tests/test_trend_analysis.py` — 48 tests, 9 classes; full suite 169/169 passing
- Fixture outcomes: 1 new service, 1 removed, 1 usage spike (108%), 2 recurring changes, 2 margin movements
- *Exit criteria met:* monthly changes detected and classified; spike/change thresholds verified; prior margin computed inline

### Phase 4 — LLM Analyst Layer ◐ *partially complete — exit criteria not all met*
- [x] `scripts/llm_analyst.py` — provider-agnostic (OpenAI SDK `base_url`): OpenAI, DeepSeek, Groq, Ollama, Mistral, etc.
- [x] System prompt with Evidence Rule — every LLM statement must cite `[table | metric | value]`
- [x] 9-section structured output — Summary, Files, Assumptions, Calculated Findings, Variances, Suspected Causes, Checks, Gaps, Confidence
- [x] `tests/test_llm_analyst.py` — 50 tests (mocked API), 11 classes; full suite 219/219 passing
- [x] `docs/output_schema.md` — Phase 4 `analyst_report.md` schema added
- [x] ~~`_select_context_tables()` is a stub~~ — implemented 2026-05-22 (9-table priority list)
- [ ] Citation validation — Evidence Rule is prompt-only; no post-generation check *(Phase 4c Gap 3)*
- [ ] `finance_control_checklist.parquet` — not yet calculated by Python *(Phase 4b Gap 2)*
- [ ] Deterministic severity scoring — flags exist but no unified severity model *(Phase 4c Gap 5)*
- [ ] Custom JSON schema validator (50-line) for structured output *(Phase 4c Gap 19 — Instructor rejected)*

### Phase 4a — Immediate Hardening ◐ *not started*
- [x] Implement `_select_context_tables()` — 9-table priority list (exception + aggregate tables); `if k in tables` guard preserves None semantics without fabricating absent-phase keys *(Gap 1 — done
  2026-05-22)*
- [ ] Add `lineage.json` append to each script — run_id, phase, inputs, outputs, timestamps *(zero-dependency audit trail)*
- [ ] Add minimal phase-status marker — each script writes `phase_N_status: failed | partial | complete` before re-raising exceptions *(5 lines per script; turns silent failures visible without full
  error-handling framework)*
- [ ] Make tests self-contained — use `tmp_path`, build parquets from `examples/` in fixtures, avoid direct `db/` reads *(Gap 6)*
- [x] Add project `.gitignore` — `db/`, `output/`, `.pytest_cache/`, `pytest-of-*/` *(Gap 5 — minimal fix)* *(done 2026-05-21)*
- [ ] Add `--db` and `--output-dir` CLI flags to all scripts — default to `skills-runtime/invoice-finance-analyst/` per local policy; keeps source tree clean *(Gap 5 — full fix; policy requires
  runtime state under `skills-runtime/` not source folder)*
- [x] Fix venv-explicit test commands in SETUP.md — use governed venv path, not bare `pytest` *(Gap 4 — done 2026-05-21)*
- [x] Align phase status language — "Phase 4 runnable — not finance-control complete" in README.md, SKILL.md; SCRATCHPAD.md current state already correct; ARCHITECTURE.md severity invariant annotated
  *(2026-05-22 review Gap 1 — done 2026-05-22)*
- [ ] Split README build-spec section — separate current implementation from accepted backlog from historical spec; remove old function-level requirements that no longer apply *(2026-05-22 review Gap
  1A)*
- [x] Add status column to ARCHITECTURE.md capability table — `implemented` / `runnable` / `planned` with ★ footnote for finance-controls partial *(2026-05-22 review Gap 1B — done 2026-05-22)*
- [x] Add `data_quality_issues` to `_select_context_tables()` context — high-value for finance confidence *(2026-05-22 review Gap 4 — done 2026-05-22)*
- [ ] Add `pyproject.toml` + `.python-version` — runtime deps: pandas, pyarrow, pyyaml, tabulate, openai; test: pytest; optional: openpyxl; replaces hand-maintained SETUP.md package lists *(2026-05-22
  review Gap 16)*
- [x] Verify parent AGENTS.md registry entry — promoted to Regular Skills as `skill-ifa`; installed to Claude Code/Codex/Hermes 2026-05-26 *(2026-05-22 review Gap 22B — done 2026-05-26)*
- *Exit criteria:* all tests run from clean checkout; artifact routing is clear; LLM receives exception tables + data_quality_issues; each run produces a lineage record with phase status; status
  language consistent across all docs; dependency manifest can recreate environment

### Phase 4b — Functional Gaps ◐ *not started*
- [ ] Service-map-aware reconciliation *(Gap 2 — highest functional gap)*
  - Accept optional `--service-map` flag
  - Map `sales.our_service_id` ↔ `supplier.supplier_service_id`
  - Add `unmapped_service` classification
  - Add fixtures with divergent IDs (SVC-* vs LOC*)
- [ ] Control totals + `run_signoff_status` *(Gap 20)*
  - Source → normalized → matched → unmatched → excluded tie-out
  - `pass` / `review_required` / `fail` status
- [ ] Period-aware rate-card selection *(Gap 3)*
  - `effective_date <= billing_period_start`, `expiry_date` check
- [ ] Period boundary matching modes *(Gap 17)*
  - Expose overlapping-period, same-calendar-month, billing-in-advance/arrears as named modes
  - Add `period_match_type`, `period_overlap_days`, `period_confidence`, `billing_lag_days` to output
  - Exact-match remains default; period mismatch becomes first-class output rather than implied unmatched
- [ ] Credit/reversal/GST/tax classification *(Gaps 13, 14)*
  - Deterministic `charge_type` (recurring, usage, once_off, credit, reversal, adjustment, tax)
  - `tax_reconciliation.parquet` + `tax_anomalies.parquet`
  - Credits excluded from recurring-rate checks unless explicitly configured
- [ ] Deterministic `finance_control_checklist.parquet` *(2026-05-22 review Gap 2 — critical prerequisite for 4c)*
  - Columns: `control_name`, `status` (pass/fail/warning/not_supplied/not_applicable), `metric_name`, `metric_value`, `threshold_or_expected`, `delta`, `source_table`, `source_column`, `severity`,
    `requires_manual_review`, `notes`
  - Controls: invoice tie-out, sales tie-out, GST/tax status, credit/reversal classification, rate-card coverage, service-map coverage, unmatched cost/revenue exposure, negative and low-margin
    exposure, manual review queue count by severity
  - Must exist before LLM prompt can claim checklist section; updating SYSTEM_PROMPT (4c Gap 18) is blocked on this
- *Exit criteria:* service-map matching works with divergent ID fixtures; control totals prove pipeline integrity; rate-card respects billing period; period mismatch is explicit, not silent; charge
  types classified deterministically; deterministic finance_control_checklist.parquet written per run

### Phase 4c — LLM Layer Enhancement ◐ *not started*
- [ ] Add custom JSON schema validator (50-line) — JSON schema → validate → render markdown; enforces Evidence Rule at schema level post-generation *(2026-05-22 review Gap 19 — Instructor REJECTED:
  conflicts with vendor-agnostic openai SDK design; revisit only if custom validator proves insufficient and Instructor is tested against Ollama + DeepSeek)*
- [ ] Add custom citation validator — post-processing check that every non-heading sentence has valid `[table | metric | value]`; fail-closed for governed output; `--allow-uncited-draft` escape flag
  for local experimentation; write `citation_validation.json` + `.md` *(Gap 7 — 50-line script, no framework needed; 2026-05-22 review Gap 3)*
- [x] Add finance control checklist to SKILL.md — required report section calculated by Python, not invented by LLM *(Gap 22 — done 2026-05-21)*
- [x] Add accounting boundary section to SKILL.md — reports are operational analysis, not final tax/audit sign-off; credits/journal entries require human approval *(Gap 21 — done 2026-05-21)*
- [ ] Update SYSTEM_PROMPT to 10-section format — add "Finance Control Checklist" as section 3; add `finance_control_checklist` to `_select_context_tables()`; add tests asserting checklist in prompt
  and context *(2026-05-22 review Gap 18 — BLOCKED on 4b finance_control_checklist.parquet existing first)*
- [ ] Implement deterministic severity scoring — `value_impact + recurrence + confidence + operational_risk`; outputs: `manual_review_queue.parquet`, `exception_severity_summary.parquet`; all
  thresholds written to assumptions table *(Gap 9; 2026-05-22 review Gap 5)*
- [ ] Run real-export validation — full pipeline on copied real APN data; capture dated outcome doc in `docs/feedback/`; create redacted pack in `examples/redacted_real/` *(Gap 8 — BLOCKED on 4b.1
  service-map + 4b.2 control totals; 2026-05-22 review Gap 21)*
- *Exit criteria:* LLM output validated via JSON schema; citations fail-closed by default; every report includes deterministic finance checklist section; accounting limits explicit in SKILL.md;
  severity computed, not guessed; SYSTEM_PROMPT matches SKILL.md section requirements; real-data run documented

### Phase 4d — Hardening + Developer Experience ◐ *not started*
- [ ] Extend `docs/output_schema.md` with planned 4b/4c table schemas **before implementing them** — add stable schemas for: `control_totals`, `run_signoff_status`, `finance_control_checklist`,
  `manual_review_queue`, `exception_severity_summary`, `service_map_coverage`, `tax_status_summary`, `credit_reversal_summary`, `citation_validation`, `lineage.json`; add tests asserting runtime
  columns match schema *(2026-05-22 review Gap 20 — schema-first prevents drift; do this before any 4b code is written)*
- [ ] Add `run_history.parquet` — each run appends row with metrics for cross-run trending *(AI Components recommendation — note: also a dependency for meaningful multi-run trend comparison in Phase
  3)*
- [ ] Extend `validate_inputs.py` with explicit type/range assertions — add column-type enforcement, range checks, and business-rule assertions inline *(Gap 4d.2 — replaces Great Expectations
  recommendation: GX adds expectation store + checkpoint overhead not warranted at this scale; existing hand-written validation covers 90% of GX value; **amended 2026-08-29**: implement via Pandera
  schemas rather than purely hand-written assertions — see FOSS review below)*
- [ ] Archive or annotate `docs/invoice_analysis_framework.md` — add 1-paragraph "what was built vs what was surveyed" summary at the top *(Skill Review concern #4)*
- [ ] Add export layer — CSV/JSON output for every exception table; optional Excel workbook with one tab per key table *(Gap 10 — do after 4b service-map and rate-card fixes so workbook doesn't freeze
  an incomplete data model)*
- [ ] Add quantity/unit-rate/proration checks — `calculated_amount = quantity × unit_price_ex_tax`, partial-month proration *(Gap 16)*
- [ ] Document performance characteristics — note in ARCHITECTURE.md or SETUP.md: pandas RAM limits for this pipeline, when to consider chunking, at what row count to evaluate Daft *(Skill Review
  concern #7 — currently zero guidance on scale limits)*
- [x] Fix `output_schema.md` status header — currently says "Phase 1B design artifact" but doc covers 22 tables across Phases 1B–4; update to reflect actual scope *(coherence gap — misleading to
  readers)* *(done 2026-05-22)*
- [x] Add CLI flag reference to SETUP.md — many flags undocumented: `--json` (validate_inputs), `--db`/`--quiet` (load_inputs), `--invoice`/`--sales` (invoice_analysis_skeleton + trend_analysis),
  `--matched`/`--rate-card` (rate_card_analysis), `--prior-invoice`/`--prior-sales` (trend_analysis) *(DevX gap — scripts are more flexible than SETUP.md implies)* *(done 2026-05-22)*
- *Exit criteria:* cross-run queries possible; type/range assertions cover all canonical fields; framework doc accurately describes what exists; exports work for handoff; line-level rate math
  validated; performance limits are documented; output_schema.md header is accurate; all script CLI flags are documented

### Phase 4e — Packaging and Distribution ◐ *not started*
- [ ] Resolve naming split — `invoice-finance-analyst` (folder) vs `internal-invoice-analysis` (built skill) must converge *(Skill Review concern #3 — decide and apply before install paths
  proliferate; default: rename folder to match built skill)*
- [ ] Create reference docs — `docs/analysis_layers.md`, `docs/assumptions_and_limits.md` *(Gap 12 — needed for installed-skill users)*
- [ ] Create report templates — `templates/findings_report_template.md`, `templates/reconciliation_report_template.md`, `templates/supplier_dispute_template.md`,
  `templates/internal_ticket_template.md` *(Gap 12)*
- [ ] Package runtime skill — `SKILL.md` + `scripts/` + `references/` + `templates/`; tests and project-management docs stay in authoring folder
- [ ] Install to `~/.claude/skills/internal-invoice-analysis/`
- [ ] Install to `~/.codex/skills/internal-invoice-analysis/`
- [ ] Add MCP server wrapper — single `analyze_invoices` tool replacing 6-step CLI process
- *Exit criteria:* naming split resolved; reference docs exist for installed-skill users; clean install package without tests or generated artifacts; agent can invoke pipeline as a single tool call

### Phase 4 Issues — Deferred to Post-Packaging
- [ ] Full error handling / partial-output strategy — retry logic, fallback outputs, "here's what we have so far" on mid-run failure *(minimal phase-status marker already added in 4a; this item covers
  the full recovery and partial-output contract)*
- [ ] Near-duplicate detection — row-exact dedup is conservative; add fuzzy dedup when real data shows unexpected duplicate-like rows
- [ ] Framework doc full rewrite — currently 884 lines of survey research; replace with 2-page engineering spec when time permits
- [ ] FinBERT charge classification — evaluate after Gaps 2 and 13 (service-map + credit/reversal) are implemented; heuristic sign+description rules will cover 80% of cases first *(Finance Tools
  recommendation — trigger: heuristic misses obvious misclassifications on real data)*

### Phase 5 — Optional Accounting System MCP ◐ *backlog*
- [ ] AR/AP aging and payment status — `scripts/aging_analysis.py`, `ar_aging.parquet`, `ap_aging.parquet`, `payment_mismatches.parquet` *(Gap 19)*
- [ ] Customer sell-rate / price book — `customer_rate_card` source type, `customer_revenue_variances.parquet`, `customer_price_card_mismatches.parquet` *(Gap 15)*
- [ ] Product/customer/supplier master data — `customer_master`, `product_master`, `supplier_master` source types; profitability aggregations *(Gap 18)*
- [ ] Anomaly detection beyond static thresholds — IsolationForest or TabPFN after 3+ months reconciled history *(Finance Tools recommendation)*
- [ ] PDF invoice support via Invoice2data — when supplier PDFs enter the workflow *(Finance Tools recommendation)*
- [ ] Evaluate Daft for auditable query plans — when pandas becomes a memory or auditability bottleneck *(Finance Tools recommendation)*
- *Trigger:* CSV export becomes a bottleneck (Phase 5) OR payment/master data becomes available (Gaps 19, 18, 15)

## Completed

| Phase                                         | Date       | Status                                      |
| --------------------------------------------- | ---------- | ------------------------------------------- |
| Phase 0 — Tool and Skill Trial                | 2026-05-21 | ✓                                           |
| Phase 0 Cleanup                               | 2026-05-21 | ✓                                           |
| Phase 1A — Validator, Data Contract, Examples | 2026-05-21 | ✓                                           |
| Phase 1B — Minimal Reconciliation Skeleton    | 2026-05-21 | ✓ (ID-equal fixtures only — see 4b.1)       |
| Phase 2 — Rate Card and Margin                | 2026-05-21 | ✓ (period-unaware — see 4b.3)               |
| Phase 3 — Trend Detection                     | 2026-05-21 | ✓                                           |
| Phase 4 — LLM Analyst Layer                   | 2026-05-21 | ◐ (3 exit criteria unmet — see Phase 4a/4c) |

## Current backlog (ordered by phase)

| Phase | Item                                                                                                                                                     | Blocked by                        |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| 4a    | Status alignment (Gaps 1/1A/1B), data_quality_issues in context (Gap 4), pyproject.toml (Gap 16), parent registry (Gap 22B), lineage.json, phase-status    | Nothing — start now               |
|       |   marker, test isolation, runtime CLI flags                                                                                                              |                                   |
| 4b    | output_schema.md extension (Gap 20, do first), service-map (Gap 6), control totals (Gap 7), finance_control_checklist.parquet (Gap 2), period-aware rates  | Gap 20 first; rest unblocked      |
|       |   (Gap 8), period boundary modes (Gap 9), credit/GST (Gap 10)                                                                                            |                                   |
| 4c    | JSON schema validator (Gap 19), citation validator (Gap 3), SYSTEM_PROMPT 10-section update (Gap 18, after Gap 2), severity scoring (Gap 5), real-export | 4b (Gap 18 blocked on Gap 2; Gap  |
|       |   validation (Gap 21)                                                                                                                                    |   21 blocked on Gaps 6+7)         |
| 4d    | Run history, validate_inputs.py assertions, framework doc, export layer (Gap 17), quantity/proration (Gap 12), performance docs                          | Partially parallel with 4c        |
| 4e    | Naming split, reference docs, templates, packaging, install, MCP server                                                                                  | 4b + 4c both complete             |
| 5     | AR/AP aging, customer price book, master data, anomaly detection, FinBERT (conditional), PDF, Daft                                                       | Payment/master data OR CSV        |
|       |                                                                                                                                                          |   bottleneck                      |

## Feedback Review Log

All 6 docs in `docs/feedback/` reviewed 2026-05-21. Decisions below are final unless re-opened.

| Recommendation                       | Source doc                   | Decision                         | Rationale                                                                                   |
| ------------------------------------ | ---------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------- |
| `_select_context_tables()` fix first | unified-plan, gap-review     | **ACCEPT** (4a)                      | 5-min fix; reduces token cost immediately                                                   |
| `lineage.json` audit trail           | hermes-review, unified-plan  | **ACCEPT** (4a)                      | Zero-dependency; bumped to day-1 work                                                       |
| Minimal phase-status marker          | hermes-review                | **ACCEPT** (4a)                      | 5 lines/script; turns silent failures visible                                               |
| Test self-containment (`tmp_path`)   | gap-review                   | **ACCEPT** (4a)                      | Portability; ROADMAP 4a                                                                     |
| Service-map-aware reconciliation     | all docs                     | **ACCEPT** (4b.1, blocker)           | Highest functional gap; real-data prereq                                                    |
| Control totals +                     | gap-review, unified-plan     | **ACCEPT** (4b.2, blocker)           | Finance trust signal; real-data prereq                                                      |
|   `run_signoff_status`               |                              |                                  |                                                                                             |
| Period-aware rate-card selection     | gap-review                   | **ACCEPT** (4b)                      | Prevents historical/future rate mismatches                                                  |
| Period boundary matching modes       | gap-review                   | **ACCEPT** (4b)                      | Gap 17; first-class output, not silent unmatch                                              |
| Credit/reversal/GST classification   | gap-review                   | **ACCEPT** (4b)                      | Gaps 13, 14                                                                                 |
| ~~Instructor for structured output~~     | ai-components                | ~~**ACCEPT** (4c)~~ → **REJECT** (Gap 19 | Conflicts with vendor-agnostic openai SDK; replaced by custom 50-line JSON schema validator |
|                                      |                              |   reversal 2026-05-22)           |                                                                                             |
| 50-line citation validator           | hermes-review                | **ACCEPT** (4c)                      | No framework needed; validates Evidence Rule post-gen                                       |
| Deterministic severity scoring       | gap-review                   | **ACCEPT** (4c)                      | Gap 9; formula defined in ARCHITECTURE.md                                                   |
| `run_history.parquet`                | ai-components                | **ACCEPT** (4d)                      | Enables cross-run trending                                                                  |
| Extend `validate_inputs.py`          | hermes-review                | **ACCEPT** (4d)                      | Replaces Great Expectations; lighter weight                                                 |
|   assertions                         |                              |                                  |                                                                                             |
| Accounting boundary in SKILL.md      | gap-review                   | **ACCEPT** ✓ done                    | Gap 21; added 2026-05-21                                                                    |
| Finance control checklist in         | gap-review                   | **ACCEPT** ✓ done                    | Gap 22; added 2026-05-21                                                                    |
|   SKILL.md                           |                              |                                  |                                                                                             |
| LangChain integration                | ai-components                | **REJECT**                           | Framework overhead not warranted for batch workflow                                         |
| Great Expectations                   | ai-components, unified-plan  | **REJECT**                           | GX expectation store + checkpoint overkill; extend validate_inputs.py instead               |
| Embedding similarity matching        | ai-components                | **REJECT**                           | Simpler deterministic join sufficient for service-map                                       |
| FinBERT charge classification        | finance-tools                | **DEFER**                            | Trigger: heuristic misses obvious misclassification on real data                            |
| Daft migration                       | finance-tools, ai-components | **DEFER**                            | Trigger: pandas becomes memory/auditability bottleneck                                      |
| Full error handling / retry logic    | unified-plan                 | **DEFER**                            | Minimal phase-status marker in 4a; full recovery post-packaging                             |
| PDF invoice support (Invoice2data)   | finance-tools                | **DEFER**                            | Trigger: supplier PDFs enter workflow                                                       |
| Near-duplicate / fuzzy dedup         | gap-review                   | **DEFER**                            | Trigger: real data shows unexpected duplicate-like rows                                     |
| MCP server wrapper                   | unified-plan                 | **DEFER** (4e)                       | Single `analyze_invoices` tool; post-packaging                                              |
| Naming split resolution              | hermes-review                | **DEFER** (4e)                       | Decide before install paths proliferate                                                     |

### 2026-05-22 — Current Implementation Gap Review

Source: `docs/feedback/current-implementation-gap-review-20260522_0053.md`
Reviewed: Malik Ahmad + Claude Code
Test baseline at review: 219/219 passed

| Gap | Title                                                 | Decision                  | Sequencing / Notes                                                                                         |
| --- | ----------------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | Phase status inconsistent across docs                 | **ACCEPT** — Immediate        | Use "Phase 4 runnable, not finance-control complete" language; separate "tests pass" from "phase complete" |
| 1A  | README mixes build spec with current implementation   | **ACCEPT** — Immediate        | Split into current / accepted backlog / historical spec                                                    |
| 1B  | Architecture describes target behavior as if          | **ACCEPT** — Immediate        | Add status column per capability: `implemented` / `partial` / `planned` / `deferred`                       |
|     |   implemented                                         |                           |                                                                                                            |
| 2   | Finance control checklist documented but not computed | **ACCEPT** — 4b critical      | `finance_control_checklist.parquet` must exist before LLM prompt claims checklist                          |
| 3   | LLM citation rule is prompt-only                      | **ACCEPT** — 4c critical      | Post-generation validator; fail-closed for governed output; `--allow-uncited-draft` escape flag            |
| 4   | Context selection: stale TODO + missing               | **ACCEPT** — Immediate        | Remove stale docstring; add `data_quality_issues`; add `finance_control_checklist` once created            |
|     |   `data_quality_issues`                               |                           |                                                                                                            |
| 5   | Deterministic severity scoring missing                | **ACCEPT** — 4c               | `manual_review_queue.parquet` + `exception_severity_summary.parquet`; thresholds written to assumptions    |
| 6   | Service-map-aware reconciliation not implemented      | **ACCEPT** — 4b (#1 gap)      | Mapping status: `mapped_active`, `mapped_inactive`, `no_mapping`, `duplicate_mapping`,                     |
|     |                                                       |                           |   `conflicting_mapping`                                                                                    |
| 7   | Control totals and run sign-off missing               | **ACCEPT** — 4b               | `control_totals.parquet` + `run_signoff_status.parquet` + `.md`; `pass` / `pass_with_warnings` / `fail`    |
| 8   | Rate-card selection not period-aware                  | **ACCEPT** — 4b               | `effective_date <= billing_period_start` AND `expiry_date` check; flag `no_period_valid_rate` +            |
|     |                                                       |                           |   `ambiguous_rate_card`                                                                                    |
| 9   | Period boundary matching modes                        | **ACCEPT** — 4b/4c (lower     | `exact_period_start` + `same_month` in 4b; `overlap` + `prorated_overlap` defer to 4c                      |
|     |                                                       |   priority)               |                                                                                                            |
| 10  | Credit / reversal / GST / tax classification missing  | **ACCEPT** — 4b               | Deterministic before reconciliation; `tax_status_summary.parquet` + `credit_reversal_summary.parquet`      |
| 11  | Customer sell-rate / price book logic                 | **DEFER** — Phase 5           | Requires contract data not yet in scope; margin can be correct while customer billing is wrong             |
| 12  | Quantity / unit price / proration checks              | **DEFER** — 4d (optional)     | Only when source fields are supplied                                                                       |
| 13  | Tests depend on shared `db/` state                    | **ACCEPT** — 4a               | `tmp_path` isolation; pass explicit paths into scripts; regression test from empty workspace               |
| 14  | Runtime path routing incomplete                       | **ACCEPT** — 4a (not trivial) | `--db` + `--output-dir` on all four remaining scripts; larger than "immediate cleanup" implies             |
| 15  | Lineage and phase-status artifacts missing            | **ACCEPT** — 4a               | `lineage.json` per run with inputs, mappings, outputs, assumptions, phase status                           |
| 16  | Dependency manifest missing                           | **ACCEPT** — Immediate        | `pyproject.toml` + `.python-version`; `openpyxl` → optional extras until export layer exists               |
| 17  | Output export layer still incomplete                  | **DEFER** — 4d                | After 4b tables settle; `scripts/export_outputs.py`; Excel optional                                        |
| 18  | LLM prompt doesn't match new finance control          | **ACCEPT** — 4c (after Gap 2) | Must sequence after `finance_control_checklist` exists; add Finance Control Checklist as section 3         |
|     |   requirements                                        |                           |                                                                                                            |
| 19  | Structured LLM output not implemented                 | **ACCEPT concept, REJECT**    | Custom 50-line JSON schema validator preferred; Instructor adds dependency conflicting with                |
|     |                                                       |   **Instructor**              |   vendor-agnostic `openai` SDK design; re-evaluate Instructor only if custom validator proves insufficient |
| 20  | Output schema behind planned new tables               | **ACCEPT** — Before 4b        | Extend `docs/output_schema.md` with stable schemas for all 4b/4c tables before writing code                |
| 21  | Real-export validation still missing                  | **DEFER** — after 4b.1+4b.2   | Redacted real-export pack in `examples/redacted_real/`; blocked on service-map + control totals            |
| 22  | Skill package boundary not final                      | **DEFER** — 4e                | Define authoring vs installable boundary; `scripts/package_skill.py` or checklist                          |
| 22A | User-facing reference docs and templates missing      | **DEFER** — 4e                | After 4b/4c controls settle; templates must not encode incomplete report structure                         |
| 22B | Parent registry / install readiness                   | **ACCEPT** — Immediate        | Verify `../AGENTS.md` already includes this project; close SCRATCHPAD item                                 |
| 23  | MCP / accounting-system integration                   | **KEEP DEFERRED**             | Gating criteria unchanged: CSV workflow must be proven before MCP design begins                            |

**Decisions with nuance from this review:**

- **Gap 19 mechanism**: Instructor rejected in favour of a custom 50-line JSON schema validator to preserve the vendor-agnostic `openai` SDK design chosen in Phase 4. Instructor must be tested against
  Ollama and DeepSeek before being reconsidered.
- **Gap 9 priority**: Period boundary modes split across 4b (`exact_period_start`, `same_month`) and 4c (`overlap`, `prorated_overlap`) — lower priority than Gaps 6 and 7.
- **Gap 14 placement**: Moved from "immediate cleanup" to 4a — it requires touching four scripts and updating tests, not a config-only change.
- **Gap 18 sequencing**: LLM prompt update must follow Gap 2 (deterministic checklist table) — updating prompt first re-creates the same prompt-only problem.
- **`--allow-uncited-draft` flag**: Operator decision needed — should local Ollama runs default to draft mode or also fail-closed? Pending.
- **Naming split**: `invoice-finance-analyst` (folder) vs `internal-invoice-analysis` (skill) — operator decision needed before Phase 4e. Default proposal: rename folder to match built skill.

### 2026-08-29 — FOSS Tools Review

Source: `docs/feedback/foss-tools-evaluation-20260829_1047.md`
Reviewed: Malik Ahmad + Claude Code. Test baseline at review: 219/219 passed (2026-08-29). Verification: web search + all-scraper page fetches; top-5 spot-verified on GitHub.

| Tool                                                                     | Decision             | Placement / trigger                                                                                |
| ------------------------------------------------------------------------ | -------------------- | -------------------------------------------------------------------------------------------------- |
| Pandera (MIT)                                                            | **ACCEPT**               | 4d.2 — schema/quality checks in `validate_inputs.py`; amends hand-written-assertions-only decision |
| DuckDB (MIT, v1.5.x)                                                     | **ACCEPT**               | 4b — auditable SQL joins for service-map matching and control totals                               |
| rapidfuzz (MIT)                                                          | **ACCEPT**               | 4b/deferred — Step 8 rung-4 description matching; near-duplicate detection                         |
| XlsxWriter (BSD-2)                                                       | **ACCEPT**               | 4d — export-layer audit workbook                                                                   |
| statsmodels (BSD-3)                                                      | **ACCEPT**               | Step 11 — deterministic MAD/z-score outlier flagging                                               |
| invoice2data + pdfplumber + docling + OCRmyPDF                           | **DEFER**                | PDF phase (Phase 5 trigger unchanged); invoice2data YAML templates preferred first rung            |
| pointblank, Polars, Splink, pyod, great-tables                           | **DEFER**                | Triggers in evaluation doc; Polars blocked on official 3.14 wheels                                 |
| recordlinkage, csvmatch, Paperless-ngx, beancount/ERP platforms,         | **REJECT**               | Dormant, wrong problem, or platform overhead                                                       |
|   Prophet-style, Quarto                                                  |                      |                                                                                                    |
| Great Expectations                                                       | **REJECT** (reconfirmed) | 2026-05-21 decision stands                                                                         |

Negative finding recorded: no actively maintained FOSS purpose-built AP/invoice reconciliation engine exists (Aug 2026 search) — bespoke pandas/DuckDB core is justified.
Skill-vs-tool decision reconfirmed: keep SKILL.md judgment layer; MCP `analyze_invoices` wrapper stays at 4e, blocked on 4b + 4c.

## Reference docs

- `docs/feedback/unified-plan-of-action-20260521_2250.md` — detailed plan with dependency diagram and work streams
- `docs/feedback/phase0-phase4-gap-review-20260521_1824.md` — original 22-gap analysis
- `docs/feedback/hermes-skill-review-20260521_2250.md` — architectural assessment and priority reorder
- `docs/feedback/ai-components-evaluation-20260521_2250.md` — LangChain and lightweight AI framework evaluation
- `docs/feedback/finance-ai-tools-evaluation-20260521_2250.md` — finance-domain-specific tool evaluation
- `docs/feedback/project-analysis-and-gap-plan-20260521_1636.md` — pre-Phase 1 origin analysis (historical only)
- `docs/feedback/current-implementation-gap-review-20260522_0053.md` — Phase 0–5 gap review against actual implementation; 23 gaps; acceptance log above
- `docs/feedback/foss-tools-evaluation-20260829_1047.md` — FOSS library research + readiness re-verification; supersedes tool-selection portions of the two 20260521_2250 evaluation docs
