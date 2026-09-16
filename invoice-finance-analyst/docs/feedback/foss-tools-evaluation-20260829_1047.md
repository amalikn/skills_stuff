# FOSS Tools Evaluation and Readiness Assessment — 2026-08-29

## Contents

- [Scope](#scope)
- [Readiness verdict](#readiness-verdict)
- [Blocking gaps](#blocking-gaps)
- [FOSS tool decisions](#foss-tool-decisions)
- [Negative finding — no FOSS recon engine](#negative-finding-no-foss-recon-engine)
- [Skill vs tool decision](#skill-vs-tool-decision)
- [Sources register](#sources-register)
- [Unverified items](#unverified-items)

---

## Scope

Full readiness review of the `internal-invoice-analysis` skill (v0.4.0) plus online research into FOSS libraries worth pulling into the pipeline. Research performed 2026-08-29 via web search with page
retrieval through the local `all-scraper` tool (top-5 candidates spot-verified against live GitHub pages). Supersedes the tool-selection portions of `finance-ai-tools-evaluation-20260521_2250.md` and
`ai-components-evaluation-20260521_2250.md` where decisions below differ; all other content in those docs stands.

## Readiness verdict

**Runnable, not production-ready.** Test suite verified green this session: 219/219 passed in 2.38s (Python 3.14.4, governed venv, 2026-08-29). Architecture is sound — deterministic pandas authority,
LLM commentary separated, evidence rule defined. Four gaps block real-data use; AGENTS.md preflight rule 9 correctly blocks production runs until 4b.1 + 4b.2 complete.

## Blocking gaps

Restated from ROADMAP (no new gaps found in this review — the 2026-05-22 gap review remains accurate):

1. **Service-map-aware reconciliation** (4b Gap 6) — match key is `supplier_service_id` only; fails on real multi-supplier data. Highest functional gap.
2. **Control totals / run sign-off** (4b Gap 7) — no source→normalized→matched tie-out per run.
3. **`finance_control_checklist.parquet`** (4b Gap 2) — SKILL.md promises a checklist Python never computes.
4. **Citation validation** (4c Gap 3) — Evidence Rule is prompt-only; unenforced post-generation.

## FOSS tool decisions

All candidates verified real and active as of Aug 2026. Evidence labels per global source discipline.

### Adopt now (fold into Phase 4b/4d work as each lands naturally)

| Tool        | License | Fills                                       | Where                                                           | Evidence                                                     |
| ----------- | ------- | ------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| Pandera     | MIT     | Dataframe schema + quality checks           | 4d.2 — amends "hand-written assertions only" decision; use      | VERIFIED_PRIMARY (GitHub repo, all-scraper fetch 2026-08-29) |
|             |         |                                             |   Pandera schemas in `validate_inputs.py`                       |                                                              |
| DuckDB      | MIT     | Auditable SQL joins over parquet, zero-copy | 4b service-map + control-total joins                            | VERIFIED_PRIMARY (duckdb-python releases page, v1.5.x line,  |
|             |         |   with pandas                               |                                                                 |   all-scraper fetch 2026-08-29)                              |
| rapidfuzz   | MIT     | Deterministic fuzzy scores with explicit    | Step 8 rung 4 description matching; deferred near-dup detection | VERIFIED_SECONDARY (releases page fetched; version pin at    |
|             |         |   thresholds                                |                                                                 |   install)                                                   |
| XlsxWriter  | BSD-2   | Audit workbook export                       | 4d export layer                                                 | VERIFIED_SECONDARY (web search, changes page)                |
| statsmodels | BSD-3   | Robust MAD/z-score outlier flagging,        | Step 11 anomaly detection                                       | VERIFIED_SECONDARY (web search)                              |
|             |         |   deterministic                             |                                                                 |                                                              |

### Later phase (trigger-gated)

| Tool                 | License | Trigger                                                                                                          |
| -------------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| invoice2data         | MIT     | Supplier PDFs enter workflow — YAML regex templates per supplier are fully deterministic, best philosophical fit |
| pdfplumber           | MIT     | Same PDF phase — lightweight text/table geometry, first rung                                                     |
| docling              | MIT     | PDF phase fallback for hard layouts — strongest local table extraction, heavy (torch)                            |
| OCRmyPDF + Tesseract | MPL-2.0 | Scanned (image-only) PDFs appear                                                                                 |
| pointblank           | MIT     | If audit-grade HTML validation reports become a deliverable; explicitly Python 3.14-compatible                   |
| Polars               | MIT     | Official Python 3.14 wheels land (issue pola-rs/polars#25035 open as of Aug 2026)                                |
| Splink               | MIT     | Exact + rapidfuzz cascade proves insufficient — probabilistic weights are harder to defend as deterministic      |
| pyod                 | BSD-2   | Multivariate outlier scoring ever needed (3+ months history)                                                     |
| great-tables         | MIT     | Publication-grade HTML report tables wanted                                                                      |

### Skip (confirmed)

| Tool                                                | Reason                                                                                      |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Great Expectations                                  | 2026-05-21 REJECT stands — expectation store + checkpoint platform overhead for a CLI skill |
| recordlinkage                                       | Dormant — last release Oct 2023                                                             |
| csvmatch                                            | Thin dormant wrapper                                                                        |
| beancount / ERPNext / LedgerSMB / medici / Formance | Bookkeeping or platform tools, not AP invoice reconciliation libraries                      |
| Paperless-ngx                                       | Document-management application, not a library; GPL-3.0                                     |
| Prophet-style forecasting                           | Non-deterministic fitting; wrong problem for MoM variance                                   |
| Quarto                                              | External CLI dependency; overkill for report output                                         |

## Negative finding — no FOSS recon engine

Deliberate negative result: no actively maintained FOSS purpose-built invoice/AP reconciliation engine exists (searched Aug 2026 across PyPI/GitHub — beancount ecosystem, ledger tools, Formance,
medici all serve different problems). The bespoke pandas core is not reinventing an available wheel. Recorded so future reviews do not repeat the search from scratch.

## Skill vs tool decision

**Both, sequenced.** Keep `SKILL.md` as the judgment-layer contract (mapping confirmation, assumptions, hard rules, narrative). Wrap the 6-script pipeline as a single `analyze_invoices` MCP tool at
Phase 4e as already planned. Do **not** convert before 4b + 4c complete — packaging now freezes the control-total and service-map gaps into the tool surface.

## Sources register

| Key                    | Publisher / page                                                                                                                | Retrieved  | Method                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------- |
| pandera-repo           | github.com/unionai-oss/pandera                                                                                                  | 2026-08-29 | all-scraper (mcp-fetch rung) |
| duckdb-python-releases | github.com/duckdb/duckdb-python/releases — v1.5.0 (Mar 2026) + v1.4 LTS patches                                                 | 2026-08-29 | all-scraper (mcp-fetch rung) |
| rapidfuzz-releases     | github.com/rapidfuzz/RapidFuzz/releases                                                                                         | 2026-08-29 | all-scraper (mcp-fetch rung) |
| research-sweep         | Web search sweep: pointblank, Polars #25035, Splink, invoice2data, docling, pdfplumber, OCRmyPDF, pyod, great-tables,           | 2026-08-29 | WebSearch (subagent)         |
|                        |   XlsxWriter, statsmodels, beancount                                                                                            |            |                              |

## Unverified items

| Item                                               | Status                                                  | Settles it                                   |
| -------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------- |
| Exact latest versions: Splink, invoice2data        | UNVERIFIED (repos confirmed active; numbers not pinned) | PyPI check at install time                   |
| Python 3.14 wheel availability per adopted package | UNVERIFIED                                              | `pip install` into governed venv at adoption |
| PyPI project pages                                 | Inaccessible via all-scraper low rungs (Fastly wall)    | Use GitHub releases or higher stealth rung   |
