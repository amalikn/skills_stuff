# CHANGELOG — skill-project-wiki-rag-bridge

All notable changes to this skill are documented here. Format: date, summary, files changed.

---

## 20260531_0300 — Coherence sweep: venv path fix + AI_NAVIGATION routing update

**Mode:** project-coherence sweep (triggered by ARCHITECTURE.md + SETUP.md addition)

### Fixed

- `prompts/02b-profile-and-recommend-strategy.md` — `RAG_TOOLS=tools_stuff` + `VENV=$RAG_TOOLS/.venv/bin` collapsed to `VENV=tools-working-cache/rag-tools/.venv/bin` (stale venv path)
- `prompts/02c-benchmark-retrieval-routes.md` — same fix
- `prompts/05-index-wiki-domain.md` — same fix

### Updated

- `AI_NAVIGATION.md` — added `ARCHITECTURE.md` and `SETUP.md` to project context files table; added `ARCHITECTURE.md` as first read in architecture routing section

### Notes

- `tools_stuff/rag-tools` references for source-level ops (cd, uv sync, scripts/) confirmed correct — not changed
- `prompts/02-verify-rag-tools.md` already had the correct split (`RAG_TOOLS_ROOT` vs `RAG_TOOLS_VENV`) — not changed
- `.ai-context/governance-pack.md` regenerated (repomix) after fix

---

## 20260531_0202 — Add ARCHITECTURE.md and SETUP.md

**Mode:** feature addition

### Created

- `ARCHITECTURE.md` — root-level architecture overview: layer model, dynamic retrieval layer, retrieval mode routing table, EvidenceBundle contract summary, component map, links to detailed docs
- `SETUP.md` — prerequisites, rag-tools verification (corrected venv path: `tools-working-cache/rag-tools/.venv/`), skill install commands for Claude Code / Codex / Hermes, first-use prompt sequence, Qdrant setup, validation commands

### Updated

- `README.md` — directory layout updated to include `ARCHITECTURE.md` and `SETUP.md` entries

### Notes

- SETUP.md documents the corrected rag-tools venv path (`tools-working-cache` not `tools_stuff`) — resolves a known path discrepancy in prompts 02b/02c
- `docs/architecture.md` (detailed) is referenced from root `ARCHITECTURE.md`; no duplication

---

## 20260531_0200 — skill-ai-it bootstrap refresh

**Mode:** bootstrap (repeat-safe — existing governance preserved)

### Changed

- `SCRATCHPAD.md` — updated Current state to reflect all phases complete + skill installed; updated Next actions to remove stale Phase 2–4 items (all done); updated memory pointers with correct session references

### Generated support (regenerated)

- `.ai-context/governance-pack.md` — repomix context pack refreshed

### Skipped

- All governance files (`AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `README.md`) — already complete and correct; no gaps found
- `.archcore/` — no new promotion candidates; all candidates already promoted (2026-05-25)
- `graphify-out/` — docs-only project, no code files to graph

### Notes

- Skill status: `SKILL_DYNAMIC_RETRIEVAL_ALIGNED`; all phases complete
- Two open items remain: second-project validation; rag-tools venv path confirmation

---

## 20260525_0130 — Coherence sweep + Archcore promotion (skill-project-coherence)

**Mode:** coherence sweep + archcore promotion
**Trigger:** post-Phases-2–9 coherence sweep; user request to promote archcore candidates

### Summary

- Removed stale `(Phase 2 — pending creation)` and `(once created — Phase 2)` markers from active routing files
- Expanded `dynamic_retrieval` routing in `AI_NAVIGATION.md` and `context-map.yaml` to include all new Phase 2–9 docs, schemas, checklists, and templates
- Promoted 5 new archcore candidates from Phases 2–9: 3 specs + 2 guides
- Updated `ARCHCORE_PROMOTION_CANDIDATES.md` to record promotion; no remaining candidates

### Updated

- `AI_NAVIGATION.md` — removed `(once created — Phase 2)` from dynamic retrieval section; expanded dynamic retrieval routing to 15 items; added 3 new docs to project context files table
- `context-map.yaml` — removed `# Phase 2 — pending creation` comments; expanded `dynamic_retrieval` routing with 12 new entries; added `includes:` list to archcore guides entry
- `.archcore/rules/workflow-sequencing-rules.md` — removed `(Phase 2)` labels from steps 4b/4c
- `ARCHCORE_PROMOTION_CANDIDATES.md` — remaining candidates → promoted (3 specs, 2 guides, 20260525)

### Created (archcore)

- `.archcore/specs/evidence-bundle-contract.md` — EvidenceBundle required fields, answer rules, citation requirements, invalid bundle conditions
- `.archcore/specs/document-profile-contract.md` — profile_file output shape, allowed document_class values, indexing gates, storage convention
- `.archcore/specs/retrieval-strategy-yaml-contract.md` — required YAML structure, document entry fields, forbidden combinations, validation rules
- `.archcore/guides/dynamic-retrieval-routing.md` — profile-first workflow, CLI commands, retrieval mode routing table, benchmark route labels, when not to index
- `.archcore/guides/evidence-first-answering.md` — answer discipline rules, bundle validity check, good/bad answer patterns, warning handling table

### Stale-reference check

- grep `pending creation`: 0 hits in active files (CHANGELOG hits are historical — correct)
- grep `once created`: 0 hits in active files
- grep `(Phase 2)`: 0 hits in active files (CHANGELOG hits are historical — correct)

### Notes

- `.ai-context/governance-pack.md` regeneration pending (repomix pass at end of session)
- Skill install to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/` follows this entry

---

## 20260525 — Dynamic retrieval alignment (Phases 2–9)

**Mode:** full update
**Trigger:** audit verdict SKILL_DYNAMIC_RETRIEVAL_OUTDATED → target SKILL_DYNAMIC_RETRIEVAL_ALIGNED

### Summary

- Updated skill to align with rag-tools dynamic retrieval capabilities
- Added profile-before-index workflow (prompts 02b/02c)
- Added EvidenceBundle answer contract (schema, template, checklist)
- Added retrieval strategy and source profile templates and schemas
- Added direct/table/structured lookup guidance throughout
- Preserved existing project/wiki/Qdrant isolation model

### Created

- `prompts/02b-profile-and-recommend-strategy.md` — profile source files and recommend retrieval strategy; Codex-ready; run from project root; produces rag/retrieval-strategy.yaml + rag/source-profiles/
- `prompts/02c-benchmark-retrieval-routes.md` — benchmark retrieval modes against query set; outputs benchmark report with route recommendation label; Codex-ready
- `templates/retrieval-strategy.yaml` — per-project strategy routing template with per-document fields, rules block
- `templates/source-profile.yaml` — document profile template mirroring rag-tools profile-file output shape
- `templates/benchmark-queries.yaml` — benchmark query set template with expected_source, expected_terms, retrieval_modes
- `templates/evidence-bundle.yaml` — EvidenceBundle output contract reference with field-level comments
- `schemas/retrieval-strategy.schema.yaml` — validation schema for retrieval-strategy.yaml; documents allowed values, forbidden combinations, common failures
- `schemas/document-profile.schema.yaml` — validation schema for source-profile.yaml; mirrors document_profiler.profile_file() output
- `schemas/evidence-bundle.schema.yaml` — validation schema for EvidenceBundle; defines required fields, answer rules, citation requirements, common failure cases
- `checklists/dynamic-retrieval-readiness.md` — checklist confirming rag-tools dynamic commands available and EvidenceBundle functional
- `checklists/evidence-bundle-validation.md` — checklist for validating individual EvidenceBundle results before LLM answer generation
- `docs/dynamic-retrieval-strategy.md` — explains profile-first retrieval model, when direct/table/RAG is correct, wiki domains, how strategy output flows to the bridge
- `docs/evidence-contract.md` — explains EvidenceBundle, answer rules, citation requirements, good/bad answer examples
- `docs/retrieval-mode-decision-tree.md` — text decision tree from user query → intent → source profile → mode → EvidenceBundle → answer; quick reference table
- `examples/vocus-profitability/source-profile.yaml` — three example profiles: DCR (structured_markdown_reference), rate card (financial_rate_card), NBN wiki article (knowledge_article)
- `examples/vocus-profitability/retrieval-strategy.yaml` — example strategy routing for DCR (HYBRID_DIRECT_FIRST), rate card (TABLE_LOOKUP_FIRST), NBN wiki (vector_rag suitable)
- `examples/vocus-profitability/benchmark-queries.yaml` — 8-query DCR benchmark set illustrating section-ID, heading, table, and negative queries

### Modified

- `prompts/05-index-wiki-domain.md` — added PF-0 (profile/strategy gate) before PF-1; requires domain profiling and strategy confirmation before wiki indexing; warns against scaffold-only indexing
- `prompts/08-index-project-documents.md` — added PF-0 (profile/strategy gate) before PF-1; requires retrieval-strategy.yaml; blocks structured/tabular docs from indexing unless benchmark_status: passed
- `checklists/indexing-readiness.md` — added "Profile and strategy gate" section at top with 9 blocking/warn items covering profile, strategy, benchmark, EvidenceBundle path, and scaffold warnings
- `README.md` — added "Dynamic retrieval strategy" section documenting profile/lookup/benchmark commands, EvidenceBundle contract, when-not-to-use-RAG table, bridge integration

### Stale-reference check

- grep `"RAG tooling"` in SKILL.md, README.md, docs: 0 hits
- grep `"vector RAG only"` or `"only vector RAG"`: 0 hits in active files
- `index.*before.*profile` in prompts/checklists: 0 hits
- PF-0 present in prompt 05 and 08: confirmed

### Notes

- Phase 1 (SKILL.md) was completed in a prior session (20260525_1200)
- Phase 10 (validation) is the next step: YAML parse all templates/schemas/examples; grep checks
- Recommended first use: run prompts/02b on the Vocus project, then prompts/02c for DCR before any project-document indexing

---

## 20260525_1200 — Phase 1: Dynamic retrieval strategy integration (skill-project-coherence)

**Mode:** coherence sweep
**Trigger:** post-SKILL.md Phase 1 update (dynamic retrieval strategy)

### Updated

- `SKILL.md` — 8 edits; 290 → 367 lines. New `## Dynamic retrieval strategy` section with routing decision table, all 6 CLI commands (`profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`), EvidenceBundle contract (key fields, answer-only-from-excerpt rule), `RAG_TOOLS_DYNAMIC_RETRIEVAL_READY` readiness label, 4 dynamic retrieval route labels (`DOCUMENT_PROFILE_COMPLETE`, `STRATEGY_RECOMMENDED`, `BENCHMARK_PASSED`, `RETRIEVAL_ROUTE_SELECTED`). Steps 4b/4c added to workflow. 2 new safety rules (profile-before-index, no-default-vector-RAG-for-structured). 3 new agent behavior items (7–9). EvidenceBundle contract subsection in Output contract. Updated Core architecture description.
- `AI_NAVIGATION.md` — workflow routing table updated with steps 4b/4c; new `Dynamic retrieval strategy questions` routing section added
- `context-map.yaml` — workflow sequence updated with `02b`/`02c` entries (Phase 2 pending); new `dynamic_retrieval` routing category added
- `.archcore/rules/workflow-sequencing-rules.md` — RULE-W1 updated with 04b/04c in sequence; RULE-W6 (profile-before-index-decision) and RULE-W7 (EvidenceBundle mandatory) added; checklist gate table updated with steps 4b/4c
- `SCRATCHPAD.md` — current state (Phase 1 complete), open items (Phases 2–4), session history (2026-05-25 entry), next actions updated
- `mcp-working-cache/context-mode/` — better-sqlite3 upgraded 12.6.2 → 12.10.0 for Node 26 compatibility; Node 22.22.0 pinned via `bin/node` symlink; plugin.json patched to use symlink path

### Stale-reference check

- grep `"RAG tooling"` in active files: 0 hits
- grep `"vector RAG only"` or `"vector-RAG-only"`: 0 hits in active files
- Steps 4b/4c referenced in SKILL.md, AI_NAVIGATION.md, context-map.yaml, archcore rules: consistent

### Notes

- prompts/02b and 02c not yet created (Phase 2). References marked `(Phase 2 — pending creation)` in routing files.
- checklists/indexing-readiness.md profile gate not yet added (Phase 2).
- Repomix re-run needed to refresh `.ai-context/governance-pack.md` after these changes.

---

## 20260525_0000 — Coherence sweep (skill-project-coherence)

**Mode:** coherence sweep
**Trigger:** post-bootstrap + post-archcore-promote

### Updated

- `README.md` — directory layout updated to include all governance files added by skill-ai-it bootstrap: `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `ARCHCORE_PROMOTION_CANDIDATES.md`, `repomix.config.json`, `.archcore/`, `.ai-context/`
- `context-map.yaml` — `graphify.enabled` set to `false` (pure-markdown skill; graphify found no code files at bootstrap; re-enable if code is added)

### Stale-reference check

- grep for `graphify.*enabled.*true`: clean
- No stale path or figure references found in active files

### Notes

- Tier 1–3 files coherent. No scripts, reports, or task runners in this skill.
- `.archcore/` fully populated (3 ADRs, 2 rules, 5 specs, 4 guides) — no rule updates needed.
- Repomix re-run queued to refresh `.ai-context/governance-pack.md`.

---

## 20260524_2359 — Archcore full population (skill-ai-it promote)

**Mode:** promote
**Generated by:** `skill-ai-it promote`

### Created

- `.archcore/specs/project-context-yaml-contract.md` — full contract for `project-context.yaml` (10 required keys, sub-key constraints, common failures)
- `.archcore/specs/project-documents-yaml-contract.md` — full contract for `project-documents.yaml` (opt-in indexing manifest, caution levels, gate rules)
- `.archcore/specs/wiki-domain-registry-contract.md` — full contract for `domain-registry.yaml` (domain status rules, validation script, modification rules)
- `.archcore/guides/wiki-domain-creation.md` — 6-step domain creation procedure with pre-flight, validation, and output format
- `.archcore/guides/post-index-retrieval-validation.md` — 5-step retrieval validation with isolation check, citation audit, forbidden collection sweep

### Updated

- `ARCHCORE_PROMOTION_CANDIDATES.md` — all remaining candidates promoted; no remaining items

### Notes

- `.archcore/` is now fully populated: 3 ADRs, 2 rules, 5 specs, 4 guides
- Repomix re-run to refresh `.ai-context/governance-pack.md`

---

## 20260524_2345 — AI governance bootstrap (skill-ai-it)

**Mode:** bootstrap
**Generated by:** `skill-ai-it`

### Created

- `AGENTS.md` — agent instruction file with @-import chain, working rules, navigation block
- `CLAUDE.md` — thin wrapper over AGENTS.md
- `SCRATCHPAD.md` — working memory (no prior session data; created today)
- `AI_NAVIGATION.md` — human-readable context router with workflow routing table
- `context-map.yaml` — machine-readable authority and routing map
- `repomix.config.json` — deterministic governance context pack config
- `.archcore/` — initialized by `archcore init`
- `.archcore/adr/ADR-001-qdrant-collection-naming-convention.md`
- `.archcore/adr/ADR-002-multi-project-isolation-model.md`
- `.archcore/adr/ADR-003-authority-hierarchy.md`
- `.archcore/rules/retrieval-isolation-rules.md`
- `.archcore/rules/workflow-sequencing-rules.md`
- `.archcore/specs/retrieval-policy-yaml-contract.md`
- `.archcore/specs/qdrant-query-filter-contract.md`
- `.archcore/guides/new-project-onboarding.md`
- `.archcore/guides/failure-mode-reference.md`
- `ARCHCORE_PROMOTION_CANDIDATES.md`
- `.ai-context/governance-pack.md` (repomix generated)

### Skipped

- `graphify-out/` — graphify CLI found no code files (pure markdown skill); skipped
- `scripts/README.md` — no scripts or task runners present

### Notes

- Archcore initialized and populated in bootstrap + promote mode (user authorized)
- Repomix ran successfully; `.ai-context/governance-pack.md` generated
- No prior memory in memory-keeper, mcp-project-context, or claude-mem (skill created same day)

---

## 2026-05-24 — Initial creation

**Summary:** Created the `skill-project-wiki-rag-bridge` reusable skill from scratch, based on:
- Existing Vocus profitability project bridge pattern (`project-dependency-model.schema.yaml`)
- wiki-data governance files (`domain-registry.yaml`, `qdrant-collection-policy.md`)
- rag-tools infrastructure established in the same session
- Global collection isolation policy from `qdrant-collection-policy.md`

**Scope:** Multi-project capable. Not Vocus-specific.

**Files created:**
- `SKILL.md` — primary agent-facing instructions
- `README.md` — human maintainer guide
- `CHANGELOG.md` — this file
- `templates/project-context.yaml`
- `templates/retrieval-policy.yaml`
- `templates/project-documents.yaml`
- `templates/wiki-domain-registry-entry.yaml`
- `templates/wiki-domain-index.md`
- `templates/wiki-reference-article.md`
- `templates/qdrant-collection-policy.md`
- `templates/AGENTS-project-wiki-bridge-block.md`
- `templates/AI_NAVIGATION-project-wiki-bridge-block.md`
- `templates/project-wiki-bridge.md`
- `templates/justfile-rag-bridge-snippet.just`
- `prompts/00-verify-wiki-operational-state.md`
- `prompts/01-create-wiki-domain.md`
- `prompts/02-verify-rag-tools.md`
- `prompts/03-create-project-bridge.md`
- `prompts/04-validate-project-policy.md`
- `prompts/05-index-wiki-domain.md`
- `prompts/06-post-index-retrieval-validation.md`
- `prompts/07-add-wiki-reference-article.md`
- `prompts/08-index-project-documents.md`
- `prompts/09-troubleshoot-rag-bridge.md`
- `schemas/retrieval-policy.schema.yaml`
- `schemas/project-context.schema.yaml`
- `schemas/project-documents.schema.yaml`
- `schemas/wiki-domain-registry.schema.yaml`
- `checklists/wiki-operational-readiness.md`
- `checklists/rag-tools-readiness.md`
- `checklists/project-bridge-readiness.md`
- `checklists/indexing-readiness.md`
- `checklists/retrieval-validation.md`
- `checklists/multi-project-isolation.md`
- `examples/vocus-profitability/project-context.yaml`
- `examples/vocus-profitability/retrieval-policy.yaml`
- `examples/vocus-profitability/project-documents.yaml`
- `examples/vocus-profitability/wiki-bridge.md`
- `examples/generic-project/project-context.yaml`
- `examples/generic-project/retrieval-policy.yaml`
- `examples/generic-project/project-documents.yaml`
- `docs/architecture.md`
- `docs/flow-diagram.md`
- `docs/collection-naming-policy.md`
- `docs/authority-model.md`
- `docs/multi-project-model.md`
- `docs/failure-modes.md`
- `docs/operating-runbook.md`
