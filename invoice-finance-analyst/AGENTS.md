@../AGENTS.md

Title: Invoice Finance Analyst — Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Skill authoring folder for the internal-invoice-analysis skill
Last reviewed: 2026-05-26
Summary: Local agent guidance for authoring, testing, and maintaining the invoice-finance-analyst skill and its implementation scripts.

# AGENTS.md

This folder is the **canonical authoring surface** for the `internal-invoice-analysis` skill and its supporting scripts, templates, docs, and tests.

## Working rules

- The source of truth for skill behavior is `SKILL.md` inside the built skill folder. All numeric conclusions in the skill must come from Python/pandas calculations, not LLM inference.
- The source framework document is [`docs/invoice_analysis_framework.md`](docs/invoice_analysis_framework.md) — this is a **planning/research artifact** (884-line design survey), not the operational spec. Use `ARCHITECTURE.md` and `internal-invoice-analysis/SKILL.md` as the authoritative implementation references. Do not contradict the framework doc's core methodology without operator approval.
- **Hard constraint baked into the skill:** do not use external market, CPI, inflation, stock, or macroeconomic data unless the user explicitly asks for it.
- Never invent missing values, service mappings, prices, or customer IDs — flag them as exceptions instead.
- Python scripts in `scripts/` must use **Python 3.14.4** (`/opt/homebrew/opt/python@3.14/bin/python3.14`) per the parent AGENTS.md venv rule.
- If a venv is needed, place it at `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/` — never inside this folder.
- Ephemeral runtime state (logs, pid files) goes under `/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/`.
- Internal domain for APN-related data: `apn.net.au`. Mark external senders/recipients accordingly when processing comms.
- Keep [`SETUP.md`](SETUP.md) current when adding dependencies, venv steps, or invocation patterns.
- Keep [`ARCHITECTURE.md`](ARCHITECTURE.md) current when adding or changing analysis layers.
- Follow naming convention: `<slug>-YYYYMMDD_hhmm.md` for time-bound notes and output docs.
- Do not modify source CSV files — treat all inputs as read-only.

<!-- BEGIN skill-ai-it:navigation -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
6. If sources conflict, stop and report the conflict instead of guessing.
7. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory systems.
8. Before running scripts, read `scripts/README.md` and `SETUP.md`. Run scripts in pipeline order. Treat all scripts as `modifies-files`.
9. Do not run on production data until Phase 4b.1 (service-map) + 4b.2 (control totals) complete.
10. Before making durable changes, identify which governance files must be updated after the work.

<!-- END skill-ai-it:navigation -->

## Wiki RAG bridge

A `retrieval-policy.yaml` governs all Qdrant access for this project. Read it before any retrieval operation.

- **Retrieval policy**: [`retrieval-policy.yaml`](retrieval-policy.yaml) — allowed collections, authority order, document manifest, profiling status
- **Allowed wiki domains**: `rag__wiki_vocus` (indexed ✓), `rag__wiki_nbn` (indexed ✓)
- **Project collection**: `rag__project_invoice_finance_analyst` — not needed; all profiled project docs use direct lookup, not Qdrant
- **Readiness**: `PROJECT_WIKI_BRIDGE_READY` / `PROJECT_RAG_POLICY_VALIDATED` — wiki access ready; project docs profiled and routed
- **Retrieval route**: wiki queries use `rag-tools vector_rag` against `rag__wiki_vocus` or `rag__wiki_nbn`; project doc queries use `rag-tools lookup-table` or `rag-tools structured-lookup` directly on source files

Hard rules:
- Never query `rag__project_vocus_profitability` from this project — different project boundary
- Never use global collections (`rag__all`, `rag__wiki_all`, `default`, etc.)
- All retrieval must return an EvidenceBundle; answer only from `excerpt` + `section_path` fields
- Numeric conclusions must trace to parquet source, not wiki retrieval

## Canonical governance linkage

- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Project change/governance history: [CHANGELOG.md](CHANGELOG.md)
- Wiki RAG bridge policy: [retrieval-policy.yaml](retrieval-policy.yaml)
- Watchman event logs: [governance/watchman-events/](governance/watchman-events/) — filesystem change records for session recovery
- Watchman cheatsheet: [/Volumes/Data/_ai/governance/watchman-cheatsheet.md](/Volumes/Data/_ai/governance/watchman-cheatsheet.md)
