# Unified Plan of Action — Invoice Finance Analyst

## Contents

- [Synthesis: What the Four Documents Say Together](#synthesis-what-the-four-documents-say-together)
  - [Agreement (every document converges on these)](#agreement-every-document-converges-on-these)
  - [Tension / Divergence](#tension-divergence)
  - [Items Only One Document Flags (but are real)](#items-only-one-document-flags-but-are-real)
- [Consolidated Priority Map](#consolidated-priority-map)
- [Sequence Diagram (Dependencies)](#sequence-diagram-dependencies)
- [Work Streams (parallelisable)](#work-streams-parallelisable)
- [Recommendations Not Yet Addressed (deferred)](#recommendations-not-yet-addressed-deferred)
- [Immediate Next Steps (the first day's work)](#immediate-next-steps-the-first-days-work)

---

Created: 2026-05-21 22:50 Australia/Melbourne  
Source documents:
- `docs/phase0-phase4-gap-review-20260521_1824.md` — 22 gaps, 14-step fix order
- `docs/hermes-skill-review-20260521_2250.md` — architectural concerns, reordered priorities
- `docs/ai-components-evaluation-20260521_2250.md` — LangChain assessment, 5 lightweight AI enhancements
- `docs/finance-ai-tools-evaluation-20260521_2250.md` — 5 finance-domain tools with timing guidance

---

## Synthesis: What the Four Documents Say Together

### Agreement (every document converges on these)

| Item | Gap Review | Skill Review | AI Components | Finance Tools |
|---|---|---|---|---|
| Service-map matching is the #1 functional gap | Step 3 of 14 | Priority 1 | Not mentioned | FinBERT can assist classification |
| `_select_context_tables()` should be fixed immediately | Step 8 of 14 | Priority 2 | Structured output (Instructor) is the Phase 4 fix | Not mentioned |
| Control totals are essential for finance trust | Step 4 of 14 | Priority 3 | lineage.json supports audit trail | Great Expectations provides data quality cert |
| GST/credits/quantity-rate should be tackled as one | Steps 5, 11, 14 | Priority 4 (together) | Not mentioned | FinBERT aids classification |
| Real-export validation is overdue | Step 12 of 14 | Priority 5 | Not mentioned | Invoice2data for PDF fallback |
| Test isolation and venv-explicit commands | Step 1 of 14 | Infra concern | Not mentioned | Great Expectations provides standardised quality |
| `.gitignore` and runtime artifact routing | Step 2 of 14 | Infra concern | Not mentioned | Not mentioned |
| No run history / cross-run comparison | Not covered (outside scope) | Concern #5 | run_history.parquet recommended | Not mentioned |

### Tension / Divergence

| Issue | Gap Review says | Skill Review says | Resolution |
|---|---|---|---|
| Fix order | Serial: tests → gitignore → service-map → control totals → GST/credits → ... | Service-map first, _select_context_tables second, control totals third, GST/credits/quantity together | Adopt Skill Review order for top 5, keep Gap Review order for the rest |
| Phase 4 LLM layer | Add citation validation + context selection + severity scoring | Add Instructor for structured output + 50-line validator for output safety | They're complementary — do both |
| Great Expectations | Not mentioned | Not mentioned | Recommended for "now" in Finance Tools doc |
| Framework doc | Not called out as a concern | Concern #4: it's a planning artifact, not a spec | Archive or annotate it |

### Items Only One Document Flags (but are real)

| Item | Source | Why it matters |
|---|---|---|
| Narrow match key (`supplier_service_id + billing_period_start` only) | Skill Review | Will break on first real multi-supplier dataset |
| Error handling / partial-output strategy | Skill Review | Pipeline can fail mid-run with no recovery |
| Naming split (`invoice-finance-analyst` vs `internal-invoice-analysis`) | Skill Review | Compounds as packaging and install targets multiply |
| Explicit-row-only dedup | Skill Review | Near-duplicates inflate exception counts |
| Undocumented performance characteristics | Skill Review | No guidance on when pandas hits memory limits |
| No packaging / install target | Gap Review (step 14) | Blocked until functional gaps are closed |
| Instructor for structured output | AI Components | Enforces Evidence Rule at compile time |
| `lineage.json` for audit trail | AI Components | Zero-dependency traceability |
| FinBERT for charge classification | Finance Tools | Replaces heuristic charge-type rules |
| Daft for auditable query plans | Finance Tools | When pandas becomes a bottleneck |

---

## Consolidated Priority Map

```
Phase 4a — Immediate Hardening (this week)
├── 4a.1  Make tests self-contained (tmp_path, fixtures, no db/ dependence)
├── 4a.2  Add project .gitignore (db/, output/, .pytest_cache/, pytest-of-*)
├── 4a.3  Fix venv-explicit test commands in SETUP.md
├── 4a.4  Implement _select_context_tables() priority list (~5 min)
└── 4a.5  Add lineage.json append to each script (~15 lines)

Phase 4b — Functional Gaps (next 1–2 weeks)
├── 4b.1  Service-map-aware reconciliation (Gap 2)
│   ├── Accept optional --service-map flag
│   ├── Map sales.our_service_id ↔ supplier.supplier_service_id
│   ├── Add unmapped_service classification
│   └── Add fixtures with divergent IDs (SVC-* vs LOC*)
├── 4b.2  Control totals + run_signoff_status (Gap 20)
│   └── Source → normalized → matched → unmatched → excluded tie-out
├── 4b.3  Period-aware rate-card selection (Gap 3)
│   └── effective_date <= billing_period_start, expiry_date check
└── 4b.4  Credit/reversal/GST/tax classification (Gaps 13, 14)
    ├── Deterministic charge_type classification
    └── tax_reconciliation.parquet + tax_anomalies.parquet

Phase 4c — Phase 4 LLM Layer (next 1–2 weeks)
├── 4c.1  Add Instructor for structured output (Evidence Rule enforcement)
├── 4c.2  Add custom 50-line citation validator (post-processing)
├── 4c.3  Add finance control checklist to SKILL.md
├── 4c.4  Add deterministic severity scoring (Gap 9)
└── 4c.5  Run real-export validation + dated outcome doc (Gap 8)

Phase 4d — Hardening + DevX (within first month)
├── 4d.1  Add run_history.parquet (cross-run comparison)
├── 4d.2  Refactor validate_inputs.py with Great Expectations
├── 4d.3  Archive or annotate invoice_analysis_framework.md
├── 4d.4  Export layer — CSV/JSON/Excel (Gap 10, Gap 16)
└── 4d.5  Quantity/unit-rate/proration checks (Gap 16)

Phase 4e — Packaging + Distribution (after functional gaps closed)
├── 4e.1  Package runtime skill (SKILL.md + scripts/ + references/)
├── 4e.2  Install to ~/.claude/skills/ and ~/.codex/skills/
├── 4e.3  Add MCP server wrapper for agent-driven invocation
└── 4e.4  Resolve naming split (folder vs built skill)

Phase 5 — Finance-Complete (next quarter)
├── 5.1   AR/AP aging layer (Gap 19)
├── 5.2   Customer sell-rate / price book (Gap 15)
├── 5.3   Product/customer/supplier master data (Gap 18)
├── 5.4   Anomaly detection beyond static thresholds (Finance Tools doc)
├── 5.5   PDF invoice support via Invoice2data (when needed)
└── 5.6   Evaluate Daft for auditable query plans (when pandas bottlenecks)
```

---

## Sequence Diagram (Dependencies)

```
Week 1                    Week 2                    Week 3+                  Month 2+
─────                    ─────                    ──────                  ───────

4a.1 Tests self-contained
4a.2 .gitignore
4a.3 venv-explicit commands
4a.4 _select_context_tables()
4a.5 lineage.json
        │
        ├─────────────────────────────────────────────────────────►
        │                                                          │
4b.1 Service-map ──────► 4c.5 Real-export validation              │
4b.2 Control totals                                              │
4b.3 Period-aware rates                                           │
4b.4 Credit/GST/tax                                               │
        │                                                          │
        ├──────────► 4c.1 Instructor structured output             │
        │           4c.2 Citation validator                        │
        │           4c.3 Finance checklist in SKILL.md              │
        │           4c.4 Severity scoring                          │
        │                                                          │
        └──────────► 4d.1 run_history.parquet                     │
                    4d.2 Great Expectations                         │
                    4d.3 Framework doc cleanup                      │
                    4d.4 Export layer (CSV/JSON/Excel)              │
                    4d.5 Quantity/proration                         │
                             │                                      │
                             └────────► 4e.1–4 Packaging ──────────► 5.1–5.6 Finance-complete
```

---

## Work Streams (parallelisable)

| Stream | Phases | Can start when | Estimated effort | Key risk |
|---|---|---|---|---|
| **Infrastructure** | 4a.1–4a.5 | Now | 1 day | None — mostly config and small code changes |
| **Matching & reconciliation** | 4b.1–4b.4 | After 4a | 3–5 days | Service-map logic may reveal edge cases not covered by current fixtures |
| **LLM layer** | 4c.1–4c.5 | After 4b completes | 2–3 days | Need real LLM API access to validate Instructor prompts |
| **Hardening & DevX** | 4d.1–4d.5 | Partially parallel with 4c | 3–5 days | Great Expectations learning curve |
| **Packaging** | 4e.1–4e.4 | After 4b AND 4c both complete | 1 day | Naming split decision needs to be made first |
| **Finance-complete** | 5.1–5.6 | After 4e | 2–4 weeks | Depends on when payment/master data becomes available |

---

## Recommendations Not Yet Addressed (deferred)

| Item | Why deferred | Trigger to revisit |
|---|---|---|
| Error handling / partial-output strategy | Pipeline is run by an agent, not a human clicking "go" — agent can detect failures | First time a pipeline failure loses data or requires manual recovery |
| Near-duplicate detection | Row-exact dedup is conservative; adding fuzzy dedup without real-data testing may cause more problems than it solves | First real-data run shows unexpected duplicate-like rows |
| Daft engine migration | Pandas is adequate for current data volumes | Invoice/sales datasets exceed RAM or an audit finding questions pandas opacity |
| Anomaly detection | Requires 3+ months of reconciled data for training | After 3 monthly runs |
| FinBERT charge classification | Heuristic rules (sign + description matching) will cover 80% of cases; model adds dev overhead | When heuristic approach misses obvious misclassifications |
| MCP server wrapper | Dependency — requires Hermes/Claude/Codex to be running with MCP | After packaging phase, as a convenience layer |
| Naming split resolution | Needs operator decision (rename folder or rename built skill?) | Before packaging (Phase 4e) — install paths depend on this |
| Invoice2data | No PDF invoices in current workflow | First PDF invoice received from a supplier |

---

## Immediate Next Steps (the first day's work)

1. **Read and confirm this plan** — does the ordering feel right?
2. **Start 4a.1** — make `tests/test_reconciliation.py` self-contained (use `tmp_path`, build parquets from `examples/` in fixtures). This is the highest-ROI change because it unblocks all future test additions.
3. **Start 4a.2** — add project `.gitignore` for `db/`, `output/`, `.pytest_cache/`, `pytest-of-*/`, generated report artifacts.
4. **Start 4a.4** — `_select_context_tables()` is literally uncommenting the skeleton and deleting `return tables`.
5. **Start 4b.1** — service-map matching is the critical path. Everything else in 4b and 4c depends on matching being realistic.
