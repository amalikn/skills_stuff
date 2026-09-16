# Changelog — Invoice Finance Analyst

## Contents

- [20260829 — FOSS tools evaluation and readiness re-verification](#20260829-foss-tools-evaluation-and-readiness-re-verification)
- [20260526 — Wiki RAG bridge and coherence sweep](#20260526-wiki-rag-bridge-and-coherence-sweep)
- [20260522_Phase4a — Phase 4a context selection hardening](#20260522_phase4a-phase-4a-context-selection-hardening)
- [20260523_1040 — Archcore promotion candidate report](#20260523_1040-archcore-promotion-candidate-report)
- [20260523_1039 — Repeat-safe skill-ai-it bootstrap refresh](#20260523_1039-repeat-safe-skill-ai-it-bootstrap-refresh)
- [20260522_1754 — AI Navigation + Script Catalog bootstrap](#20260522_1754-ai-navigation-script-catalog-bootstrap)
- [2026-05-21 — Phase 0–4 implementation](#2026-05-21-phase-04-implementation)

---

## 20260829 — FOSS tools evaluation and readiness re-verification

### Added

- `docs/feedback/foss-tools-evaluation-20260829_1047.md` — FOSS library research (web search + all-scraper page fetches), readiness verdict, sources register, unverified-items table. Supersedes
  tool-selection portions of `finance-ai-tools-evaluation-20260521_2250.md` and `ai-components-evaluation-20260521_2250.md`.
- `ROADMAP.md` — 2026-08-29 FOSS Tools Review section in Feedback Review Log: ACCEPT Pandera (4d.2, amends hand-written-assertions decision), DuckDB (4b joins), rapidfuzz (Step 8 rung 4), XlsxWriter
  (4d export), statsmodels (Step 11); DEFER PDF stack + pointblank/Polars/Splink/pyod/great-tables; REJECT reconfirmed for Great Expectations, recordlinkage, csvmatch, platform tools.

### Verified

- Test suite re-verified green: 219/219 passed, 2.38s, Python 3.14.4, governed venv (2026-08-29).
- Negative finding recorded: no actively maintained FOSS purpose-built AP/invoice reconciliation engine exists (Aug 2026) — bespoke pandas core justified.
- Skill-vs-tool decision reconfirmed: SKILL.md stays the judgment layer; MCP `analyze_invoices` wrapper remains Phase 4e, blocked on 4b + 4c.

## 20260526 — Wiki RAG bridge and coherence sweep

### Added

- `retrieval-policy.yaml` — project wiki RAG bridge contract. Declares allowed collections (`rag__wiki_vocus`, `rag__wiki_nbn`, `rag__project_invoice_finance_analyst`), authority order, document
  manifest with sensitivity flags, and profiling next steps. Initial pre-profiling status was `PROJECT_WIKI_BRIDGE_PARTIAL`; final status after profiling is recorded below as ready/validated.
- `AGENTS.md` — Wiki RAG bridge section added (hard rules: isolation, EvidenceBundle requirement, forbidden collections).

### Fixed

- `ROADMAP.md` — Gap 4 Phase 4a item checked `[x]` (was incorrectly unchecked despite implementation completing 2026-05-22).
- `SCRATCHPAD.md` — Next actions section updated to remove `data_quality_issues` from pending list (Gap 4 done).
- `CHANGELOG.md` — Added missing entry for 2026-05-22 Phase 4a context selection work.
- `.ai-context/governance-pack.md` — Regenerated via repomix after above fixes.

### Profiling results (2026-05-26)

All three project documents profiled. All classified `financial_rate_card` with `index_allowed: false`:

| Document                             | Tables | Headings | Route selected      |
| ------------------------------------ | ------ | -------- | ------------------- |
| `docs/data_contract.md`              | 9      | 20       | `lookup-table`      |
| `docs/output_schema.md`              | 18     | 32       | `lookup-table`      |
| `internal-invoice-analysis/SKILL.md` | 8      | 68       | `structured-lookup` |

**`rag__project_invoice_finance_analyst` collection: not needed.** All project docs use direct file lookup. Qdrant layer is wiki-only.

Final readiness: `PROJECT_WIKI_BRIDGE_READY` / `PROJECT_RAG_POLICY_VALIDATED` / `RETRIEVAL_ROUTE_SELECTED`.

### Notes

- Wiki queries → `rag-tools vector_rag` against `rag__wiki_vocus` or `rag__wiki_nbn`.
- Project doc queries → `rag-tools lookup-table docs/output_schema.md <query>` or `rag-tools structured-lookup internal-invoice-analysis/SKILL.md <query>`.
- Wiki: `rag__wiki_vocus` (WS207 billing mechanics, invoice record types, CVC/AVC) + `rag__wiki_nbn` both indexed.
- Coherence correction: `AGENTS.md` and `context-map.yaml` updated from the initial partial bridge state to the final ready/validated state after profiling completed.

---

## 20260522_Phase4a — Phase 4a context selection hardening

### Changed

- `scripts/llm_analyst.py` — `_select_context_tables()` implemented with 9-table priority list (`run_summary`, `source_file_inventory`, `data_quality_issues`, `reconciliation_summary`,
  `amount_mismatches`, `rate_card_mismatches`, `low_margin_exceptions`, `usage_spikes`, `recurring_changes`); `if k in tables` guard preserves None semantics without fabricating absent-phase keys.
- `scripts/llm_analyst.py` — Gap 4: `data_quality_issues` added to context selection priority list; high-value for finance confidence signals.

### Notes

- All 50 `test_llm_analyst.py` tests pass after change.
- ROADMAP.md Phase 4a item Gap 4 ticked; SCRATCHPAD.md open items updated.

---

## 20260523_1040 — Archcore promotion candidate report

### Added

- `ARCHCORE_PROMOTION_CANDIDATES.md` — report-first Archcore candidate inventory grouped by ADRs, rules, specs, guides, and plans.
- `repomix.config.json` — added `ARCHCORE_PROMOTION_CANDIDATES.md` to the default governance context pack.

### Skipped

- `.archcore/` content files were not created. Promotion requires explicit authorization via `/skill-ai-it promote` or a direct request naming which candidates to promote.

### Notes

- Candidate extraction used `ARCHITECTURE.md`, `ROADMAP.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `README.md`, `docs/data_contract.md`, `docs/output_schema.md`, `SETUP.md`, and `scripts/README.md`.
- Generated files, feedback docs, changelog history, and the planning framework document were excluded as direct promotion sources.

---

## 20260523_1039 — Repeat-safe skill-ai-it bootstrap refresh

### Changed

- `justfile` — aligned validation and loading recipes with the current `validate_inputs.py` and `load_inputs.py` CLIs.
- `justfile` — changed `pipeline` to run the deterministic Phase 1A/1B/2/3 workflow only; Phase 4 LLM analyst remains a separate `just analyse` task because it requires credentials/provider config.
- `scripts/README.md` — corrected validation/loading usage examples and test commands to match current CLIs and the governed venv path.
- `repomix.config.json` — removed broad `docs/*.md` include so low-authority planning/research docs are not packed into the default governance context; added `justfile`.

### Skipped

- Base governance files (`README.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SETUP.md`) already existed and were not
  regenerated.
- `.archcore/` already existed; no `archcore init` rerun was needed.

### Notes

- Generated by `skill-ai-it` in repeat-safe `bootstrap` mode on 2026-05-23.

---

## 20260522_1754 — AI Navigation + Script Catalog bootstrap

### Added

- `AI_NAVIGATION.md` — human-readable AI context router for the project.
- `context-map.yaml` — machine-readable task-to-context routing map.
- `scripts/README.md` — catalogued inventory of all 6 pipeline scripts with safety labels and invocation patterns.
- `repomix.config.json` — deterministic AI context pack configuration.
- `.archcore/` — initialized structured project truth backend (Archcore CLI).
- `CHANGELOG.md` — project governance history ledger.

### Changed

- `AGENTS.md` — added `skill-ai-it:navigation` managed block (AI navigation/context preflight rules).
- `README.md` — added AI navigation pointer in Governance pointers section.

### Skipped

- `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SETUP.md` — all present and well-populated; no overwrite.

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode on 2026-05-22.
- Archcore initialized; populate `.archcore/adr/`, `.archcore/rules/`, `.archcore/specs/` when decisions, rules, or contracts are ready to promote from SCRATCHPAD/ROADMAP.

---

## 2026-05-21 — Phase 0–4 implementation

### Added

- Full governance scaffold: `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SETUP.md`, `README.md`.
- `internal-invoice-analysis/SKILL.md` — Phase 0 workflow, 15 steps, 7 hard rules, thresholds.
- `scripts/validate_inputs.py` (Phase 1A), `scripts/load_inputs.py` (Phase 1B), `scripts/invoice_analysis_skeleton.py` (Phase 1B).
- `scripts/rate_card_analysis.py` (Phase 2), `scripts/trend_analysis.py` (Phase 3), `scripts/llm_analyst.py` (Phase 4).
- `tests/` — 219 tests across 5 modules (all passing, Python 3.14.4).
- `docs/data_contract.md`, `docs/output_schema.md`, `docs/feedback/` review documents.
- `examples/` — 6 CSV fixtures + 4 mapping YAMLs + README.
- `.gitignore` — excludes db/, output/, pytest-of-*/, etc.

### Notes

- Phases 0–4 runnable as of 2026-05-21.
- Phase 4 finance controls (checklist, citation validator, deterministic severity) pending Phases 4b–4c.
- See `ROADMAP.md` for Phase 4a–4e task breakdown and gap review decisions.
