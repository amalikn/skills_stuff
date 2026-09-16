# SCRATCHPAD

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries-full-detail-in-memory-keeper)
  - [2026-08-29: Current-state audit](#2026-08-29-current-state-audit)
  - [2026-05-26 — Coherence sweep + wiki RAG bridge + skill-ifa install](#2026-05-26-coherence-sweep-wiki-rag-bridge-skill-ifa-install)
  - [2026-05-23 — skill-ai-it refresh + Archcore guardrail](#2026-05-23-skill-ai-it-refresh--archcore-guardrail)
  - [2026-05-22 — Governance coherence check (post-gap-review)](#2026-05-22-governance-coherence-check-post-gap-review)
  - [2026-05-22 — _select_context_tables() + governance refs updated](#2026-05-22-_select_context_tables-governance-refs-updated)
  - [2026-05-22 — Post-compaction: governance scan + 4d items](#2026-05-22-post-compaction-governance-scan-4d-items)
  - [2026-05-21 — Governance coherence + TOC + watchman + feedback log](#2026-05-21-governance-coherence-toc-watchman-feedback-log)
  - [2026-05-21 — Feedback review + ROADMAP hardening (late session)](#2026-05-21-feedback-review-roadmap-hardening-late-session)
  - [2026-05-21 — Phase 4 complete](#2026-05-21-phase-4-complete)
  - [2026-05-21 — Phase 3 complete](#2026-05-21-phase-3-complete)
  - [2026-05-21 — Phase 2 complete](#2026-05-21-phase-2-complete)
  - [2026-05-21 — Phase 1B complete](#2026-05-21-phase-1b-complete)
  - [2026-05-21 — Phase 1A start](#2026-05-21-phase-1a-start)
  - [2026-05-21 — Phase 0 execution](#2026-05-21-phase-0-execution)
  - [2026-05-21 — Bootstrap + governance](#2026-05-21-bootstrap-governance)
- [Next actions](#next-actions)
- [Memory pointers (navigation only)](#memory-pointers-navigation-only)

---

Agent working memory for invoice-finance-analyst.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: updated 2026-05-26 after wiki RAG bridge + skill-ifa install session -->
<!-- claude-mem: README.md indexed as observation #4769; related NBN/Vocus profitability work obs #4682/#4715/#4716/#4761 -->
<!-- claude-mem 2026-05-26: skill-ifa install obs #5719, AGENTS.md update obs #5720, CHANGELOG profiling obs #5713 -->

## Current state

<!-- KEEP -->
**Phase:** Phase 4 runnable: not finance-control complete. Phase 5 in backlog. Current-state audit completed 2026-08-29; the audit verdict is `RUNNABLE / ANALYTIC USE ONLY`.

Phase 0–4 scripts and tests complete 2026-05-21. 219 tests passing. Phase 4 exit criteria NOT all met: finance_control_checklist.parquet, citation validator, and deterministic severity scoring still missing. Do not call Phase 4 "complete" until ROADMAP acceptance criteria are satisfied.

| Deliverable | Status |
|---|---|
| `internal-invoice-analysis/SKILL.md` | ✓ done — v0.4.0, all 4 phases documented |
| `docs/data_contract.md` | ✓ done — 4 source types, mapping protocol, heuristics |
| `examples/` — CSVs, mapping YAMLs, README | ✓ done — invoice, sales, rate_card, service_map, prior_invoice, prior_sales fixtures |
| `scripts/validate_inputs.py` | ✓ done — rate_card + service_map heuristics added Phase 2 |
| `scripts/load_inputs.py` | ✓ done — handles all 4 source types + prior period |
| `scripts/invoice_analysis_skeleton.py` | ✓ done — 9 Phase 1B output tables |
| `scripts/rate_card_analysis.py` | ✓ done — 6 Phase 2 output tables |
| `scripts/trend_analysis.py` | ✓ done — 7 Phase 3 output tables |
| `scripts/llm_analyst.py` | ✓ done — Phase 4 LLM layer, provider-agnostic, 9-section report |
| `tests/test_validate_inputs.py` | ✓ done — 33 tests, 9 classes |
| `tests/test_reconciliation.py` | ✓ done — 41 tests, 8 classes |
| `tests/test_rate_card_analysis.py` | ✓ done — 47 tests, 8 classes |
| `tests/test_trend_analysis.py` | ✓ done — 48 tests, 9 classes |
| `tests/test_llm_analyst.py` | ✓ done — 50 tests, 11 classes |
| `docs/output_schema.md` | ✓ done — Phase 1B/2/3 tables + Phase 4 analyst_report.md |

---

## Open items

<!-- KEEP -->
- [x] ~~Build the `internal-invoice-analysis` skill folder per build spec~~ ✓
- [x] ~~Phase 1A–4 scripts, tests, output schema~~ ✓ 219/219 passing 2026-05-21
- [ ] **Phase 4a — Immediate Hardening**
  - [x] `_select_context_tables()` — 9-table priority list, `if k in tables` guard *(done 2026-05-22)*
  - [x] Align phase status language — README.md + SKILL.md frontmatter updated; ARCHITECTURE.md severity invariant annotated *(Gap 1 — done 2026-05-22)*
  - [ ] Split README build-spec section — current vs backlog vs historical spec *(Gap 1A)*
  - [x] Add Status column to ARCHITECTURE.md component map (implemented/runnable ★/planned) + 3 planned component rows added *(Gap 1B — done 2026-05-22)*
  - [x] Add `data_quality_issues` to `_select_context_tables()` context *(Gap 4 remainder — done 2026-05-22)*
  - [ ] `pyproject.toml` + `.python-version` — openpyxl → optional extras *(Gap 16)*
  - [x] Verify parent AGENTS.md registry entry — moved to Regular Skills as `skill-ifa`; installed to Claude Code/Codex/Hermes *(Gap 22B — done 2026-05-26)*
  - [ ] `lineage.json` append + phase-status marker (5 lines/script)
  - [ ] Tests self-contained (`tmp_path`, no `db/` reads) *(Gap 13)*
  - [x] Add `.gitignore` *(done 2026-05-21)*
  - [ ] `--db`/`--output-dir` CLI flags → `skills-runtime/` (4 scripts + tests) *(Gap 14)*
  - [x] Fix venv-explicit test commands in SETUP.md *(done 2026-05-21)*
  - [x] CLI flag reference added to SETUP.md *(done 2026-05-22)*
  - [x] `output_schema.md` stale status header fixed *(done 2026-05-22)*
  - [x] `pytest-of-malik.ahmad/` removed from project root *(done 2026-05-22)*
- [ ] **Phase 4b — Functional Gaps** *(do Gap 20 first — schema before code)*
  - [ ] Extend `output_schema.md` with planned 4b/4c table schemas *(Gap 20 — do before any 4b code)*
  - [ ] Service-map-aware reconciliation *(Gap 6 — #1 functional gap)*
  - [ ] Control totals + `run_signoff_status` *(Gap 7)*
  - [ ] Deterministic `finance_control_checklist.parquet` *(Gap 2 — blocks 4c Gap 18)*
  - [ ] Period-aware rate-card selection *(Gap 8)*
  - [ ] Period boundary matching modes: `exact_period_start` + `same_month` in 4b; `overlap` + `prorated_overlap` in 4c *(Gap 9)*
  - [ ] Credit/reversal/GST/tax classification *(Gap 10)*
- [ ] **Phase 4c — LLM Layer** *(after 4b; Gap 18 blocked on Gap 2)*
  - [ ] Custom JSON schema validator (50-line) — JSON schema → validate → render markdown *(Gap 19 — Instructor REJECTED)*
  - [ ] Citation validator — fail-closed default; `--allow-uncited-draft` flag *(Gap 3)*
  - [ ] Update SYSTEM_PROMPT to 10-section format — BLOCKED on Gap 2 *(Gap 18)*
  - [ ] Deterministic severity scoring (`manual_review_queue.parquet`) *(Gap 5)*
  - [ ] Real-export validation — BLOCKED on 4b.1 + 4b.2 *(Gap 21)*
- [ ] **Phase 4d — Hardening + DevX**
  - [ ] `run_history.parquet`
  - [ ] Extend `validate_inputs.py` with type/range assertions
  - [ ] Export layer — CSV/JSON/Excel *(Gap 17)*
  - [ ] Quantity/unit-rate/proration checks *(Gap 12)*
  - [ ] Performance characteristics doc
- [ ] **Phase 4e — Packaging**
  - [ ] Resolve naming split (operator decision pending)
  - [ ] `docs/analysis_layers.md`, `docs/assumptions_and_limits.md`
  - [ ] Report templates
  - [ ] Package + install runtime skill
- [ ] Add `internal-invoice-analysis` to skills_stuff AGENTS.md skill registry *(Gap 22B quick check)*

---

## Key anchors

<!-- KEEP -->
| Item | Detail |
|---|---|
| Folder | `/Volumes/Data/_ai/_skills/skills_stuff/invoice-finance-analyst/` |
| Skill folder | `internal-invoice-analysis/` |
| SKILL.md | `internal-invoice-analysis/SKILL.md` (Phase 0 — complete) |
| Framework source | `docs/invoice_analysis_framework.md` |
| Build spec | `README.md` |
| Python version | 3.14.4 — `/opt/homebrew/opt/python@3.14/bin/python3.14` |
| venv | `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/` |
| Internal domain | `apn.net.au` |
| Related work | `project_stuff/apn/vocus-profitability/` (NBN/rebate analysis, threshold source) |
| Archcore candidate report | `ARCHCORE_PROMOTION_CANDIDATES.md` — generated 2026-05-23; review before `/skill-ai-it promote` |
| Canonical `skill-ai-it` | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/` |

---

## Recent decisions

<!-- KEEP -->
- 2026-05-23 — `skill-ai-it` Archcore safeguard: candidate reporting is now a completion gate, not only workflow guidance. Future bootstrap/refresh runs with `.archcore/` present must verify/read back `ARCHCORE_PROMOTION_CANDIDATES.md`; only `promote` may write `.archcore/adr|rules|specs|guides|plans`.
- 2026-05-22 — Gap 19: **Instructor REVERSED to REJECT** — conflicts with vendor-agnostic openai SDK. Custom 50-line JSON schema validator adopted instead. Instructor may be reconsidered only if tested against Ollama + DeepSeek.
- 2026-05-22 — 23-gap review accepted/deferred. Key sequencing: Gap 18 (SYSTEM_PROMPT) blocked on Gap 2 (finance_control_checklist.parquet); Gap 20 (output schema extension) must precede 4b code; Gap 14 reclassified from immediate to 4a.
- 2026-05-22 — Two operator decisions pending: (1) `--allow-uncited-draft` scope for Ollama local runs; (2) naming split resolution before 4e.
- 2026-05-21 — Feedback review: Instructor ADOPT (4c) ~~— REVERSED 2026-05-22~~, lineage.json ADOPT (4a), LangChain REJECT (framework overhead), Great Expectations REJECT (extend validate_inputs.py instead), FinBERT DEFER (trigger: misclassification on real data), Daft DEFER (trigger: pandas bottleneck).
- 2026-05-21 — Real-data gate established: do not run pipeline on production data until 4b.1 (service-map) + 4b.2 (control totals) complete.
- 2026-05-21 — `invoice_analysis_framework.md` confirmed as planning/research artifact (884 lines), not operational spec. Annotate top with "what was built vs surveyed" summary in 4d.
- 2026-05-21 — Threshold calibration: ABS=$0.02, PCT=0.1%, margin=5%, spike=2×, recurring=5% (from vocus-profitability data). Full rationale in `invoice-finance-analyst.thresholds` MK key.
- 2026-05-21 — Skill scope locked to source-data-only; Python/pandas is calculation authority; LLM is commentary only.

---

## Session history (summaries — full detail in memory-keeper)

<!-- KEEP -->
### 2026-08-29: Current-state audit

- Produced `docs/audit/` deliverables: current-state audit, control gap matrix, implementation-versus-governance matrix, test coverage audit, and dependency-ordered remediation plan.
- Reproduced the full suite: 219 collected and 219 passed under the governed venv's Python 3.14.7; project docs still state Python 3.14.4.
- Audit result: six P0 findings (unguarded reconciliation and trend joins, unused service map, period-invalid rate selection, ambiguous date parsing, unvalidated LLM claims) and eight P1 findings.
- Immediate next remediation: cardinality-gated, service-map-aware reconciliation with source-row provenance. No production code, schema, or input data was changed.

### 2026-05-26 — Coherence sweep + wiki RAG bridge + skill-ifa install
- Coherence sweep: Gap 4 ROADMAP checkbox fixed (`[ ]`→`[x]`), SCRATCHPAD next-actions de-staled, missing CHANGELOG Phase 4a entry added, repomix regenerated.
- Wiki RAG bridge: `retrieval-policy.yaml` created; all 3 project docs profiled (`financial_rate_card`, `index_allowed: false`); no Qdrant project collection needed — direct file lookup only. `PROJECT_WIKI_BRIDGE_READY`.
- `skill-ifa` installed to Claude Code / Codex / Hermes; `skills_stuff/AGENTS.md` registry updated; Gap 22B closed.
- Follow-up project-coherence pass: `AGENTS.md` and `context-map.yaml` corrected from initial partial bridge wording to final ready/validated state; `.ai-context/governance-pack.md` regenerated.
- PC checkpoint: `slurp-20260526-ifa-rag-bridge-install` (ID: 5abc4579); MK unavailable this session.

### 2026-05-23 — skill-ai-it refresh + Archcore guardrail
- `skill-ai-it` bootstrap/refresh pass corrected governance support surfaces: `justfile`, `scripts/README.md`, `repomix.config.json`, `CHANGELOG.md`, and `ARCHCORE_PROMOTION_CANDIDATES.md`.
- Archcore candidate report created with adr/rules/specs/guides/plans candidates; no `.archcore/` content files were promoted.
- Canonical `skill-ai-it` hardened so future Archcore-enabled bootstrap/refresh runs must verify `ARCHCORE_PROMOTION_CANDIDATES.md` before completion.
- MK keys: `invoice-finance-analyst.skill-ai-it-bootstrap-refresh.20260523`, `skill-ai-it.archcore-candidate-report-completion-gate.20260523`; checkpoint: `slurp-20260523-skill-ai-it-archcore-guard-final` (MK: 3d64a3e4, PC: fcc81014)

### 2026-05-22 — Governance coherence check (post-gap-review)
- Grepped all *.md for stale "Phase 4 complete" and Instructor ACCEPT (4c); found 5 issues across 4 files.
- Fixed: README.md status language (×2 + ★ footnote on Phase 4 row), SKILL.md frontmatter, ROADMAP.md old backlog Instructor row struck through, ARCHITECTURE.md severity invariant annotated + Status column added (Gap 1B with 3 new planned component rows).
- Gap 1 + Gap 1B ticked in ROADMAP.md; TOC check passed (all files >100 lines have TOC).
- MK key: `invoice-finance-analyst.coherence-check.20260522`; checkpoint: `slurp-20260522-coherence-check` (MK: ad93eb67, PC: 265e0ee9)

### 2026-05-22 — Gap review acceptance + ROADMAP phase updates
- Reviewed `current-implementation-gap-review-20260522_0053.md` — 23 gaps; all decisions captured in ROADMAP.md Feedback Review Log.
- Instructor reversed: REJECTED; custom 50-line JSON schema validator adopted for Gap 19.
- ROADMAP phases 4a/4b/4c/4d updated: +6 items to 4a, finance_control_checklist to 4b, Gap 18 + JSON validator to 4c, Gap 20 schema-first to 4d.
- Global MEMORY.md updated: governance-scan rule added to `/Users/malik.ahmad/.claude/projects/-Volumes-Data--ai/memory/`.
- MK keys: `invoice-finance-analyst.gap-review.acceptance.20260522`, `invoice-finance-analyst.roadmap.phase-updates.20260522`; checkpoint: `slurp-20260522-gap-review-acceptance` (MK: 13a5a1cb, PC: 5ab499a3)

### 2026-05-22 — _select_context_tables() + governance refs updated
- Implemented `_select_context_tables()` in llm_analyst.py: 9-table priority list, `if k in tables` guard (not `.get()`).
- All 50 llm_analyst tests passing; ROADMAP 4a item ticked.
- README.md, ROADMAP.md, SCRATCHPAD.md stale "next action" refs updated.
- MK key: `invoice-finance-analyst.select-context-tables-20260522`; checkpoint: `slurp-20260522-invoice-finance-analyst-4a-context-selection` (MK: 5b8a64f8, PC: 540e8a4c)

### 2026-05-22 — Post-compaction: governance scan + 4d items
- Resumed from compaction; completed SCRATCHPAD.md memory pointers (prior slurp close).
- `output_schema.md` status header fixed (was "Phase 1B design artifact", now reflects all 22 tables + Phase 4).
- CLI flag reference section added to SETUP.md — all 6 scripts fully documented with table format.
- `pytest-of-malik.ahmad/` removed from project root.
- ROADMAP: `.gitignore`, `output_schema.md` header, CLI flag ref, venv commands all ticked [x].
- MK key: `invoice-finance-analyst.session-resume-20260522`; checkpoint: `slurp-20260522-invoice-finance-analyst-resume` (MK: 477d2072, PC: 2c7c8392)

### 2026-05-21 — Governance coherence + TOC + watchman + feedback log
- Full coherence audit: test counts (219 ✓), table names (22 ✓), stubs confirmed, 3 ROADMAP items ticked (done but unchecked), 2 new 4d items added (output_schema.md header, CLI flag reference).
- Feedback Review Log added to ROADMAP.md — 26-row accept/reject/defer table covering all 6 docs/feedback/ files.
- TOCs added to 16 files; global governance rule added to markdown-guide.md (100-line threshold + maintain-on-edit rule).
- .gitignore created (db/, output/, pytest-of-*/, etc.); watchman registered (fsevents, governance/watchman-events/ created).
- MK keys: `invoice-finance-analyst.governance.coherence-20260521`, `invoice-finance-analyst.watchman`, `invoice-finance-analyst.feedback-decisions`, `invoice-finance-analyst.toc-gitignore-governance-20260521`; checkpoint: `slurp-20260521-invoice-finance-analyst-governance` (MK: 1e9d13a3, PC: d6d46864)

### 2026-05-21 — Feedback review + ROADMAP hardening (late session)
- Reviewed 6 docs in docs/feedback/ (unified plan, gap review, Hermes review, AI components, finance tools, origin analysis).
- Tooling decisions locked: Instructor ✓, lineage.json ✓, GX ✗, LangChain ✗.
- ROADMAP.md updated: 9 additions/corrections including Gap 17 (period boundary), Gap 21 (accounting boundary), Gap 5 full fix (CLI flags), Hermes Concern #7 (performance docs), FinBERT in deferred.
- SKILL.md: Gap 21 (Finance and Accounting Boundaries) + Gap 22 (Finance Control Checklist) sections added.
- ARCHITECTURE.md: Primary output format corrected — Excel was aspirational, current is parquet + markdown.
- MK key: `invoice-finance-analyst.feedback-review-20260521`; checkpoint: `slurp-20260521-feedback-review-roadmap-hardening`

### 2026-05-21 — Phase 4 complete
- scripts/llm_analyst.py: provider-agnostic LLM layer using openai SDK (base_url configurable for DeepSeek, Groq, Ollama, etc.)
- System prompt: Evidence Rule (every statement cites table/metric/value), 9-section format, no external data.
- _select_context_tables: documented TODO stub — user implements table selection strategy (6–10 priority tables).
- tests/test_llm_analyst.py: 50 tests, 11 classes (all offline/mocked); full suite 219/219 passing.
- SKILL.md v0.4.0; output_schema.md Phase 4 section added; ROADMAP.md Phase 4 checked.

### 2026-05-21 — Phase 3 complete
- Prior period fixtures: examples/prior_invoice_sample.csv (Feb 2026, 4 rows), examples/prior_sales_billing_sample.csv (3 rows); reuse existing mapping YAMLs.
- scripts/trend_analysis.py: 7 output tables — mom_variance, new_services, removed_services, usage_spikes, recurring_changes, margin_movement, phase3_assumptions.
- Fixture results: 1 new (LOC000001), 1 removed (LOC000006), 1 spike (LOC000003), 2 recurring changes (LOC000002 +18.75%, LOC000003 +108%), 2 margin movements (LOC000003 declined, LOC000004 improved).
- tests/test_trend_analysis.py: 48 tests, 9 classes; full suite 169/169 passing (Python 3.14.4, 2026-05-21).
- docs/output_schema.md extended with 7 Phase 3 table definitions (22 total).
- SKILL.md v0.3.0; ROADMAP.md Phase 3 checked; examples/README.md Phase 3 scenarios added.

### 2026-05-21 — Phase 2 complete
- Rate card + service map fixtures created (examples/); heuristic patterns extended in validate_inputs.py.
- scripts/rate_card_analysis.py: 6 output tables — rate_variances, rate_card_mismatches, margin_by_customer, margin_by_service_type, low_margin_exceptions, phase2_assumptions.
- Fixture results: 2 rate card mismatches (LOC000003/4 overcharged $2 each), 0 low-margin exceptions, 3 customers/service types with healthy margins.
- tests/test_rate_card_analysis.py: 47 tests; full suite 121/121 passing (Python 3.14.4, 2026-05-21).
- docs/output_schema.md extended with 6 Phase 2 table definitions.

### 2026-05-21 — Phase 1B complete
- Gap plan reviewed; 6/8 gaps actioned; Phase 1 split into 0 Cleanup → 1A → 1B.
- docs/output_schema.md created (9 tables, column names locked — Gap 8).
- scripts/load_inputs.py: CSV → parquet with archive pattern (vocus-profitability pattern).
- scripts/invoice_analysis_skeleton.py: deduplicate → outer join → 9 output tables → db/*.parquet + output/<run_id>/*.md.
- tests/test_reconciliation.py: 41 tests; full suite 74/74 passing.
- MK checkpoint: slurp-20260521-invoice-finance-analyst-phase1ab (ID: e15df8e6, 426 items).
- PC checkpoint: slurp-20260521-invoice-finance-analyst-phase1ab (ID: 2d0464d9).

### 2026-05-21 — Phase 1A start
- Gap analysis doc created: `docs/project-analysis-and-gap-plan-20260521_1636.md` — 8 gaps identified, 6 actioned.
- ROADMAP.md restructured: Phase 1 split into Phase 0 Cleanup, 1A, 1B; gaps embedded as exit criteria.
- Phase 0 Cleanup done: SKILL.md draft-labelled (frontmatter + visible callout).
- `docs/data_contract.md` created: canonical fields for all 4 source types, heuristic patterns, ambiguity protocol.
- `examples/` created: `supplier_invoice_sample.csv` (5 rows), `sales_billing_sample.csv` (4 rows), 2 mapping YAMLs, README.
- Writing `scripts/validate_inputs.py` next.

### 2026-05-21 — Phase 0 execution
- `internal-invoice-analysis/SKILL.md` created: 15-step workflow, 7 hard rules, threshold constants with inline vocus-profitability rationale.
- Framework doc moved to `docs/`; §3.6 Xero and §3.7 Odoo removed (multiple rounds); all downstream references cleaned.
- Thresholds calibrated from vocus-profitability: $0.02 rounding, 5% margin, 2× spike, 5% recurring.
- ROADMAP.md: Phase 0 checked off, Phase 1 set as current.
- MK checkpoint: `slurp-20260521-invoice-finance-analyst-phase0` (ID: 45cc1b97, 421 items).

### 2026-05-21 — Bootstrap + governance
- Governance files created: AGENTS.md, CLAUDE.md, SCRATCHPAD.md, ARCHITECTURE.md, SETUP.md, ROADMAP.md.
- README.md reformatted; parent skills_stuff/README.md updated with folder index entry.
- MK checkpoint: `slurp-20260521-invoice-finance-analyst-bootstrap` (ID: 8d8911bc).

---

## Next actions

<!-- KEEP -->
1. **Remaining 4a cleanup**: README split (Gap 1A), `pyproject.toml` + `.python-version` (Gap 16), `lineage.json` + phase-status marker — Gaps 1/1B/4/22B done.
2. **Extend `output_schema.md`** with 4b/4c table schemas (Gap 20) — schema-first before any 4b code.
3. **Service-map reconciliation (4b.1)** — #1 functional gap; required before real data.
4. **Control totals + `run_signoff_status` (4b.2)** — finance trust signal; required before real data.
5. **Do not run on production data** until 4b.1 + 4b.2 both complete.
6. **Archcore promotion**: review `ARCHCORE_PROMOTION_CANDIDATES.md`; run `/skill-ai-it promote` only after explicitly approving which candidates become durable `.archcore/` content.
7. **When updating SKILL.md**: sync to `~/.claude/skills/skill-ifa/`, `~/.codex/skills/skill-ifa/`, `~/.hermes/skills/domain/skill-ifa/` after every change.

---

## Memory pointers (navigation only)

<!-- KEEP -->
- **2026-05-26 — memory-keeper unavailable this session** (server not reachable); all session content saved to mcp-project-context only
  - PC note: Coherence Sweep — Gap 4 + CHANGELOG repair (progress, 2026-05-26)
  - PC note: Wiki RAG Bridge — PROJECT_WIKI_BRIDGE_READY (decision, 2026-05-26)
  - PC note: skill-ifa installed + Gap 22B closed (progress, 2026-05-26)
  - PC checkpoint: `slurp-20260526-ifa-rag-bridge-install` (ID: 5abc4579-0a40-47d4-9dbb-6feab0baa2f7)
- memory-keeper channel: `invoice-finance-anal` (server-truncated from `invoice-finance-analyst`)
  - key: `invoice-finance-analyst.skill-ai-it-bootstrap-refresh.20260523` — repeat-safe governance refresh, candidate report, validation run details
  - key: `skill-ai-it.archcore-candidate-report-completion-gate.20260523` — root cause and canonical skill guardrail fix
  - checkpoint: `slurp-20260523-skill-ai-it-archcore-guard-final` (MK: 3d64a3e4, PC: fcc81014)
  - key: `invoice-finance-analyst.feedback-review-20260521` — tooling decisions, ROADMAP changes (this session)
  - key: `invoice-finance-analyst.phase4.implementation` — Phase 4 llm_analyst.py, 219 tests
  - key: `invoice-finance-analyst.phase4.vendor_agnostic_decision` — openai SDK choice rationale
  - key: `invoice-finance-analyst.phase4.evidence_rule_and_prompt` — system prompt design, 9-section format
  - key: `session.closeout.20260521.invoice-finance-analyst-phase4` — full closeout entry
  - checkpoint: `slurp-20260521-feedback-review-roadmap-hardening` (ID: dd83770f, 433 items)
  - checkpoint: `slurp-20260521-invoice-finance-analyst-phase4` (ID: 5f2c9e76, 431 items)
  - checkpoint: `slurp-20260521-invoice-finance-analyst-phase2-3` (ID: 12771043, 428 items)
  - checkpoint: `slurp-20260521-invoice-finance-analyst-phase0` (ID: 45cc1b97)
- mcp-project-context: `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c) / channel: `invoice-finance-analyst`
  - note: skill-ai-it Bootstrap Refresh + Archcore Candidate Report (progress, 2026-05-23)
  - note: skill-ai-it Archcore Completion Gate (decision, 2026-05-23)
  - checkpoint: `slurp-20260523-skill-ai-it-archcore-guard-final` (ID: fcc81014-5f08-496a-b4e9-3665c3a8cfd7)
  - note: Feedback Review + ROADMAP Hardening (decision, 2026-05-21 late)
  - note: Phase 4 Complete — LLM Analyst Layer (progress, 2026-05-21)
  - note: Phase 2 + Phase 3 Complete (progress, 2026-05-21)
  - checkpoint: `slurp-20260521-feedback-review-roadmap-hardening` (ID: a5b2202b-a6b6-4654-83ba-eb65be0dd88f)
  - checkpoint: `slurp-20260521-invoice-finance-analyst-phase4` (ID: 20a7a6e2-4ad2-4e85-814c-ada3ebde66d2)
  - checkpoint: `slurp-20260521-invoice-finance-analyst-governance` (PC: d6d46864)
- memory-keeper channel: `invoice-finance-anal` (2026-05-22 keys)
  - key: `invoice-finance-analyst.select-context-tables-20260522` — implementation details, guard rationale, test fix
  - key: `invoice-finance-analyst.session-resume-20260522` — post-compaction resume; SCRATCHPAD memory pointers + 4d fixes
  - checkpoint: `slurp-20260522-invoice-finance-analyst-4a-context-selection` (MK: 5b8a64f8, PC: 540e8a4c)
  - checkpoint: `slurp-20260522-invoice-finance-analyst-resume` (MK: 477d2072, PC: 2c7c8392)
  - key: `invoice-finance-analyst.gap-review.acceptance.20260522` — 23 gap decisions, Instructor reversal
  - key: `invoice-finance-analyst.roadmap.phase-updates.20260522` — phase 4a/4b/4c/4d changes
  - checkpoint: `slurp-20260522-gap-review-acceptance` (MK: 13a5a1cb, PC: 5ab499a3)
  - key: `invoice-finance-analyst.coherence-check.20260522` — 5 governance coherence fixes: phase status language in README/SKILL/ARCHITECTURE, Instructor REJECT in old backlog, ARCHITECTURE Status column
  - checkpoint: `slurp-20260522-coherence-check` (MK: ad93eb67, PC: 265e0ee9)
- memory-keeper channel: `invoice-finance-anal` (governance session keys)
  - key: `invoice-finance-analyst.governance.coherence-20260521` — script/test/governance coherence audit findings
  - key: `invoice-finance-analyst.watchman` — watchman setup, fsevents, .watchmanconfig
  - key: `invoice-finance-analyst.feedback-decisions` — 6-doc feedback stack, accept/reject/defer table
  - key: `invoice-finance-analyst.toc-gitignore-governance-20260521` — TOC rule, .gitignore, global governance
  - key: `session.closeout.20260521.invoice-finance-analyst-governance` — full closeout entry
  - checkpoint: `slurp-20260521-invoice-finance-analyst-governance` (MK: 1e9d13a3, 438 items)
- claude-mem: obs #4769 (README.md), obs #4682/#4715/#4716/#4761 (Vocus profitability)
