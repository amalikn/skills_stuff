# Skill Dynamic Retrieval Readiness Audit

**Date:** 2026-05-25  
**Time:** 0003  
**Auditor:** Claude Code (Sonnet 4.6)  
**Skill audited:** skill-project-wiki-rag-bridge  
**Skill path:** `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-project-wiki-rag-bridge/`  
**rag-tools path:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/`

---

## Executive summary

**Verdict: SKILL_DYNAMIC_RETRIEVAL_OUTDATED**

The skill was built before rag-tools gained dynamic retrieval strategy selection (profiling, structured lookup, table-aware lookup, section/clause lookup, benchmarking, EvidenceBundle contract). The skill treats rag-tools as a RAG/Qdrant indexing-and-search tool only. It contains no mention of the dynamic retrieval router, no profiling step, no benchmark-before-route guidance, no direct/table lookup paths, and no EvidenceBundle output contract. The skill workflow goes straight to indexing without a document-profiling gate. Agents following the current skill will default to vector RAG for all sources, miss the deterministic lookup routes that rag-tools now provides, and produce answers that are not grounded in evidence bundles. The skill requires a substantive update across SKILL.md, prompts, templates, schemas/checklists, examples, and docs before it can be considered safe for production use on projects that include structured/tabular sources.

---

## 20-question audit matrix

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Does SKILL.md describe rag-tools as only RAG/Qdrant tooling? | **Yes — gap** | SKILL.md Core architecture section says "Shared reusable RAG tooling (Qdrant helpers, embeddings, policy validator, CLI, doctor)" with no mention of profiling, strategy selection, or direct lookup |
| 2 | Does SKILL.md mention dynamic retrieval strategy selection? | **No** | Zero occurrences of "dynamic", "strategy", "profile", "recommend-strategy" in SKILL.md |
| 3 | Does SKILL.md mention direct structured lookup? | **No** | No mention of `structured-lookup`, `lookup_query`, or deterministic lookup in SKILL.md |
| 4 | Does SKILL.md mention section/clause lookup? | **No** | No mention of `lookup-section`, section IDs, clause lookup in SKILL.md |
| 5 | Does SKILL.md mention table-aware lookup? | **No** | No mention of `lookup-table`, table-aware retrieval, rate cards in SKILL.md |
| 6 | Does SKILL.md mention EvidenceBundle as the required output contract? | **No** | No occurrence of "EvidenceBundle", "evidence bundle", or "output contract" in SKILL.md |
| 7 | Does SKILL.md explain when vector RAG is not the right default? | **No** | SKILL.md hardcodes retrieval order as: project-local → project Qdrant → wiki Qdrant → ask user. No RAG-vs-direct decision is described |
| 8 | Does SKILL.md explain that source files remain authoritative? | **Yes** | Authority model section (line 91–95): "Qdrant payloads are retrieval artefacts — not authoritative records; the markdown source file is always canonical" |
| 9 | Does SKILL.md define retrieval route selection before indexing? | **No** | Standard workflow (lines 163–173) goes directly from bridge creation to wiki indexing. No profiling or route-selection step exists |
| 10 | Does SKILL.md include dynamic readiness labels? | **No — partial** | Readiness labels exist for wiki operational state, RAG tools, project bridge, policy, indexing, and retrieval — but none for document profile, strategy recommendation, benchmark, or direct-lookup readiness |
| 11 | Do prompts include a project profiling step before project indexing? | **No** | Prompts 03→04→05→08 go directly to bridge creation and indexing. No prompt calls `profile-file` or `recommend-strategy` before indexing |
| 12 | Do prompts include benchmark-driven route selection? | **No** | No prompt references `benchmark-file`, benchmark YAML, or route selection before choosing vector RAG |
| 13 | Do templates include retrieval-strategy.yaml, document-inventory.yaml, source-profile.yaml, evidence-bundle.yaml? | **No** | Templates present: `project-context.yaml`, `retrieval-policy.yaml`, `project-documents.yaml`, `wiki-domain-registry-entry.yaml`, `wiki-domain-index.md`, `wiki-reference-article.md`, `qdrant-collection-policy.md`, AGENTS block, AI_NAVIGATION block, `project-wiki-bridge.md`, justfile snippet. None of the four named dynamic-retrieval templates exist |
| 14 | Do schemas/checklists reflect the new dynamic retrieval capability? | **No** | Four schemas exist: `retrieval-policy`, `project-context`, `project-documents`, `wiki-domain-registry`. No schema for strategy selection, document profile, or evidence bundle. Five checklists exist: `wiki-operational-readiness`, `rag-tools-readiness`, `project-bridge-readiness`, `indexing-readiness`, `retrieval-validation`, `multi-project-isolation`. No checklist for profile-before-index or route selection |
| 15 | Do examples demonstrate both wiki vector RAG AND structured direct lookup for long source files? | **No** | Two examples: `vocus-profitability/` and `generic-project/`. Both show only `project-context.yaml`, `retrieval-policy.yaml`, `project-documents.yaml` (and one `wiki-bridge.md`). No structured-lookup or table-lookup examples. No benchmark examples |
| 16 | Do docs explain the corrected model (not RAG for everything, dynamic retrieval router, evidence-first LLM answers)? | **No** | Seven docs exist: `architecture.md`, `flow-diagram.md`, `collection-naming-policy.md`, `authority-model.md`, `multi-project-model.md`, `failure-modes.md`, `operating-runbook.md`. Architecture hardcodes 4-step retrieval order (local → project Qdrant → wiki Qdrant → ask user). No doc covers dynamic strategy selection, direct lookup, or EvidenceBundle |
| 17 | Are there outdated instructions that encourage indexing first before profiling? | **Yes** | Standard workflow in SKILL.md (lines 163–173) and all prompt sequences go to indexing without any profile/recommend step. Prompt 05 and 08 have pre-flight checks but none call `profile-file` |
| 18 | Are there instructions implying curated wiki articles should duplicate full source files? | **No** | SKILL.md safety rules (line 190): "Never invent wiki content. All wiki articles must have a declared source reference." Wiki articles are framed as curated summaries with citations, not duplicates |
| 19 | Are there instructions that omit direct-source fallback? | **Yes — partial** | The retrieval order in `retrieval-policy.yaml` template and `docs/architecture.md` Step 4 says "ask user" when evidence is insufficient. No step says "fall back to direct structured lookup on the source file before asking user". For long structured files this is a critical omission |
| 20 | Are there contradictions between skill docs and actual rag-tools CLI commands? | **Yes** | SKILL.md lists rag-tools CLI as: `doctor`, `index-domain`, `index-project`, `validate-policy`. Actual CLI (justfile + cli.py) also has: `profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`. These are absent from SKILL.md, prompts, templates, checklists, and examples |

---

## Current skill summary

The skill covers well:

- Qdrant collection isolation naming policy (enforced throughout SKILL.md, schemas, checklists)
- Collection forbidden-names enforcement
- Retrieval policy YAML structure and flat-validator contract
- Source-of-truth authority hierarchy (markdown > Qdrant payloads)
- Multi-project isolation model
- Wiki domain creation, indexing, and post-index validation workflow
- Safety rules (no global collections, no raw data, no cross-domain mixing)
- Citation completeness requirements (source_file, heading, section_path, collection)
- Dry-run-before-live-index discipline
- Insufficient-evidence response behavior (say not found, do not speculate)

---

## Gap matrix

| Area | Current state | Required state | Gap severity | Recommended change |
|---|---|---|---|---|
| SKILL.md purpose | Describes rag-tools as "RAG/Qdrant tooling" | Describe as "retrieval engine with dynamic strategy router" | HIGH | Update description + Purpose section |
| SKILL.md core architecture | Lists CLI as doctor/index/validate-policy only | Include profile-file, recommend-strategy, structured-lookup, lookup-section, lookup-table, benchmark-file | HIGH | Add dynamic retrieval section to Core architecture |
| SKILL.md authority model | Present and correct | Add: source files are the fallback for direct lookup before Qdrant | LOW | Minor addition |
| SKILL.md standard workflow | Index-first after bridge creation | Profile → recommend → benchmark → then choose index OR direct-lookup | HIGH | Insert profiling step between Step 4 and Step 5 |
| SKILL.md safety rules | Good set for indexing safety | Add: "Profile documents before choosing retrieval route. Do not default to vector RAG for structured/tabular sources." | MEDIUM | Append 1-2 safety rules |
| SKILL.md agent behavior | Load governance, validate, report | Add: profile source files, run recommend-strategy, use EvidenceBundle output | HIGH | Expand agent behavior section |
| SKILL.md readiness labels | Wiki/RAG/Bridge/Policy/Index/Retrieval | Add: DOCUMENT_PROFILE_COMPLETE, STRATEGY_RECOMMENDED, BENCHMARK_PASSED, RETRIEVAL_ROUTE_SELECTED | MEDIUM | Add new label group |
| SKILL.md output contract | Structured report with verdict/files/commands | Add EvidenceBundle as required output for retrieval operations | HIGH | Update output contract section |
| Prompts | 00–09 present, no profile/benchmark step | Add prompt 02b (or revise 02): profile-file + recommend-strategy before indexing decision | HIGH | New prompt or expansion of prompt 03 pre-flight |
| Templates | 7 YAML + 4 MD templates, no dynamic-retrieval templates | Add: retrieval-strategy.yaml, source-profile.yaml, evidence-bundle.yaml, benchmark-queries.yaml | HIGH | Create 4 new templates |
| Schemas | 4 schemas for policy/context/documents/registry | Add: retrieval-strategy.schema.yaml, document-profile.schema.yaml, evidence-bundle.schema.yaml | MEDIUM | Create 3 new schemas |
| Checklists | 5 checklists (operational/rag-tools/bridge/indexing/retrieval/isolation) | Add: profile-before-index gate item to indexing-readiness.md; add strategy-selection checklist | MEDIUM | Modify indexing-readiness.md; new strategy-selection checklist |
| Examples | 2 examples, both vector-RAG-only | Add at minimum one example showing profile → structured-lookup path for a tabular/structured source | HIGH | Extend vocus-profitability or add generic-structured example |
| Docs | 7 docs, none covers dynamic retrieval | Add docs mirroring rag-tools docs: dynamic-retrieval-strategy.md, evidence-contract.md, retrieval-mode-decision-tree.md | HIGH | Create 3 new doc files (or copy from rag-tools with skill-specific context) |
| README.md | Documents architecture/workflow correctly for its scope | Add dynamic retrieval section mentioning profiling commands | MEDIUM | Update README dynamic retrieval section |
| CHANGELOG.md | Up to date for what the skill covers | Add entry when dynamic retrieval update is applied | LOW | Normal changelog discipline |

---

## Rag-tools capability alignment

### Actual CLI commands available (from justfile + cli.py)

| Command | What it does | Mentioned in skill? |
|---|---|---|
| `rag-tools doctor` | Health checks, readiness verdict | Yes (prompts/02) |
| `rag-tools validate-policy <file>` | Validate retrieval-policy.yaml | Yes (prompts/04) |
| `rag-tools index-domain <domain> [--dry-run]` | Index wiki domain into Qdrant | Yes (prompts/05) |
| `rag-tools index-project --project-slug --manifest` | Index project docs into Qdrant | Yes (prompts/08) |
| `rag-tools profile-file <file>` | Structural profile: section IDs, tables, headings, source class | **No** |
| `rag-tools recommend-strategy <file>` | Recommend retrieval modes based on profile | **No** |
| `rag-tools structured-lookup <file> <query>` | Deterministic heading/section lookup returning EvidenceBundle | **No** |
| `rag-tools lookup-section <file> <section-id>` | Exact section ID lookup returning EvidenceBundle | **No** |
| `rag-tools lookup-table <file> <query>` | Table-aware retrieval returning EvidenceBundle | **No** |
| `rag-tools benchmark-file <file> [--queries] [--modes]` | Benchmark direct/table/RAG modes before route selection | **No** |

### Dynamic retrieval modules (src/rag_tools/)

| Module | Purpose | Referenced in skill? |
|---|---|---|
| `evidence.py` — `EvidenceBundle` | Output contract for all retrieval modes | **No** |
| `document_profiler.py` — `profile_file()` | Classifies source files and recommends retrieval modes | **No** |
| `strategy_selector.py` — `recommend_strategy()` | Selects retrieval strategies from profile | **No** |
| `structured_lookup.py` — `lookup_query()`, `lookup_section()` | Deterministic lookup with EvidenceBundle output | **No** |
| `table_lookup.py` — `lookup_tables_in_markdown()` | Table-aware lookup with EvidenceBundle output | **No** |
| `retrieval_benchmark.py` — `benchmark_file()` | Benchmarks modes against query set | **No** |

### EvidenceBundle model

- Defined in `evidence.py` as a Pydantic model
- Fields: `query`, `retrieval_mode`, `document_id`, `source_file`, `source_type`, `authority`, `section_id`, `section_path`, `heading`, `table_id`, `row_keys`, `excerpt`, `matched_terms`, `score_or_confidence`, `context_chars`, `retrieval_warnings`
- Answer rule: LLM must answer only from evidence bundles, not from training knowledge
- Not referenced anywhere in the skill

### rag-tools docs (present in rag-tools, absent from skill)

| Doc | Status in rag-tools | Referenced in skill? |
|---|---|---|
| `docs/dynamic-retrieval-strategy.md` | Present | **No** |
| `docs/evidence-contract.md` | Present | **No** |
| `docs/retrieval-mode-decision-tree.md` | Present | **No** |

---

## Outdated or risky wording

### 1. "RAG tooling" description in SKILL.md

**Location:** `SKILL.md` line 64  
**Quote:** `_tool/tools_stuff/rag-tools — Shared reusable RAG tooling (Qdrant helpers, embeddings, policy validator, CLI, doctor)`  
**Problem:** Characterises rag-tools as Qdrant/RAG tooling only, omitting its dynamic retrieval router, document profiler, structured/table lookup, and benchmarking capabilities.

### 2. Workflow starts with indexing without profiling

**Location:** `SKILL.md` lines 163–173 (Standard workflow), prompts 03, 05, 08  
**Quote:** `Step 4 → prompts/03-create-project-bridge.md` / `Step 7 → prompts/05-index-wiki-domain.md`  
**Problem:** No document profiling or strategy recommendation step exists before the indexing decision. The agent is sent to create an index without knowing whether the source documents call for vector RAG, direct structured lookup, or table lookup.

### 3. Hardcoded vector RAG retrieval order

**Location:** `SKILL.md` "Output contract" section, `templates/retrieval-policy.yaml` lines 51–66, `docs/architecture.md` lines 75–82  
**Quote (retrieval-policy.yaml):** `step: 2 / source: "project_collection" / collection: "rag__project_<project_slug>"` — implies Qdrant lookup is the second stop for all queries, including exact structured facts  
**Problem:** For long structured documents (DCRs, rate cards, billing manifests, policy documents), direct structured lookup on the source file is faster, more accurate, and avoids semantic drift. The current retrieval order treats Qdrant as the universal second step.

### 4. Lack of EvidenceBundle anywhere

**Location:** All skill files  
**Problem:** `EvidenceBundle` is the mandatory output contract for all rag-tools retrieval operations. Agents answering from evidence bundles cannot hallucinate exact amounts, dates, or clauses. The skill defines its own output contract (Verdict/Files/Commands report) for operational steps, but this is a workflow report, not a retrieval evidence contract. No skill file instructs the agent to demand evidence bundles from rag-tools before generating answers.

### 5. No direct-source fallback before "ask user"

**Location:** `templates/retrieval-policy.yaml` lines 60–66, `docs/architecture.md` lines 75–82  
**Quote:** `step: 4 / source: "ask_user" / condition: "No sufficient evidence found in steps 1–3."`  
**Problem:** For structured documents, the correct fallback before asking the user is `structured-lookup` or `lookup-section` directly on the source file — not escalation to the user.

### 6. Indexing readiness checklist missing profile gate

**Location:** `checklists/indexing-readiness.md`  
**Problem:** The indexing-readiness checklist has 5 sections (domain content, collection names, policy, RAG tools, dry-run, content safety) with no item requiring that a document profile has been run and a retrieval strategy selected before proceeding to index.

---

## Missing files and templates

### Templates to create

| File | Purpose |
|---|---|
| `templates/retrieval-strategy.yaml` | Per-project retrieval strategy declaration: source-class, preferred modes, benchmark result, chosen route |
| `templates/source-profile.yaml` | Output of `profile-file` for a source document: section count, table count, source class, recommended modes |
| `templates/benchmark-queries.yaml` | Sample benchmark query file for `rag-tools benchmark-file` |
| `templates/evidence-bundle.yaml` | Reference schema for an EvidenceBundle (for agent and human consumers) |

### Schemas to create

| File | Purpose |
|---|---|
| `schemas/retrieval-strategy.schema.yaml` | Field definitions for retrieval-strategy.yaml |
| `schemas/document-profile.schema.yaml` | Field definitions for a document profile output |
| `schemas/evidence-bundle.schema.yaml` | Field definitions for EvidenceBundle (mirrors rag-tools Pydantic model) |

### Prompts to create or modify

| File | Action | Purpose |
|---|---|---|
| `prompts/02b-profile-and-recommend-strategy.md` | Create | Profile source documents with `profile-file`, run `recommend-strategy`, record results before choosing index vs direct-lookup |
| `prompts/02c-benchmark-retrieval-routes.md` | Create | Run `benchmark-file` for structured/tabular sources; record results to inform route selection |
| `prompts/05-index-wiki-domain.md` | Modify pre-flight | Add PF-0: confirm profile has been run; add conditional step for direct-lookup-capable domains |
| `prompts/08-index-project-documents.md` | Modify pre-flight | Add PF-0: profile each document in manifest; add step recommending direct-lookup for structured sources |

### Docs to create

| File | Purpose |
|---|---|
| `docs/dynamic-retrieval-strategy.md` | Explain why vector RAG is not the default; describe when to use each retrieval mode; reference rag-tools equivalents |
| `docs/evidence-contract.md` | Define EvidenceBundle as the required retrieval output; answer rules; how to cite |
| `docs/retrieval-mode-decision-tree.md` | Mirror rag-tools decision tree adapted to project-wiki-rag-bridge workflow |

### Checklists to modify

| File | Change |
|---|---|
| `checklists/indexing-readiness.md` | Add section: "Profile and strategy" — BLOCKING: `profile-file` run for each source; BLOCKING: retrieval strategy recorded in `retrieval-strategy.yaml`; WARN: benchmark run for structured sources |

---

## Update plan

### Phase 1: SKILL.md only

- Update the description line (frontmatter + Purpose) to drop "RAG tooling" and add "retrieval engine with dynamic strategy router"
- Add a new section "Dynamic retrieval strategy" between "Authority model" and "Collection isolation rules"
- Document the 6 new CLI commands: `profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`
- Explain when vector RAG is NOT the right route (exact facts, tables, amounts, clauses, IDs)
- Add EvidenceBundle as the required retrieval output contract
- Insert profile/recommend step into the Standard workflow (between Step 4 and current Step 5)
- Add 2 new safety rules: "Profile documents before indexing decision" and "Use direct-source lookup before Qdrant for structured/tabular facts"
- Add new readiness labels: `DOCUMENT_PROFILE_COMPLETE`, `STRATEGY_RECOMMENDED`, `BENCHMARK_PASSED`
- Expand agent behavior to include: profile files, run recommend-strategy, demand EvidenceBundle output

**Estimated file changes:** SKILL.md only. Low risk.

### Phase 2: prompts / templates / schemas / checklists

- Create `prompts/02b-profile-and-recommend-strategy.md`
- Create `prompts/02c-benchmark-retrieval-routes.md`
- Update `prompts/05-index-wiki-domain.md` pre-flight: add PF-0 profile gate
- Update `prompts/08-index-project-documents.md` pre-flight: add PF-0 profile gate per document
- Create `templates/retrieval-strategy.yaml`
- Create `templates/source-profile.yaml`
- Create `templates/benchmark-queries.yaml`
- Create `templates/evidence-bundle.yaml`
- Create `schemas/retrieval-strategy.schema.yaml`
- Create `schemas/document-profile.schema.yaml`
- Create `schemas/evidence-bundle.schema.yaml`
- Update `checklists/indexing-readiness.md`: add profile-and-strategy section

**Estimated file changes:** 2 prompts modified, 2 prompts created, 4 templates created, 3 schemas created, 1 checklist modified.

### Phase 3: examples / docs / README / CHANGELOG

- Create `docs/dynamic-retrieval-strategy.md`
- Create `docs/evidence-contract.md`
- Create `docs/retrieval-mode-decision-tree.md`
- Extend `examples/vocus-profitability/` with: `source-profile.yaml`, `retrieval-strategy.yaml`, `benchmark-queries.yaml` showing a structured-lookup path for a tabular source
- Update `README.md`: add "Dynamic retrieval strategy" section referencing new commands and docs
- Update `CHANGELOG.md`: add entry for the dynamic-retrieval update

**Estimated file changes:** 3 docs created, 3 example files created, 2 files modified.

### Phase 4: validation pass

- Grep all new files for "RAG tooling" and replace with "retrieval engine"
- Grep all prompts for index-before-profile anti-pattern; confirm no prompt sends agent to index without a profile step
- Confirm no template or schema encourages global collections
- YAML parse all new templates and schemas
- Confirm EvidenceBundle is mentioned in SKILL.md, at least one prompt, and at least one template
- Confirm `retrieve-strategy.yaml` template references `profile-file` and `recommend-strategy`
- Confirm the indexing-readiness checklist has a BLOCKING profile gate

---

## Proposed file change list

### Create (new files)

```
skill-project-wiki-rag-bridge/prompts/02b-profile-and-recommend-strategy.md
skill-project-wiki-rag-bridge/prompts/02c-benchmark-retrieval-routes.md
skill-project-wiki-rag-bridge/templates/retrieval-strategy.yaml
skill-project-wiki-rag-bridge/templates/source-profile.yaml
skill-project-wiki-rag-bridge/templates/benchmark-queries.yaml
skill-project-wiki-rag-bridge/templates/evidence-bundle.yaml
skill-project-wiki-rag-bridge/schemas/retrieval-strategy.schema.yaml
skill-project-wiki-rag-bridge/schemas/document-profile.schema.yaml
skill-project-wiki-rag-bridge/schemas/evidence-bundle.schema.yaml
skill-project-wiki-rag-bridge/docs/dynamic-retrieval-strategy.md
skill-project-wiki-rag-bridge/docs/evidence-contract.md
skill-project-wiki-rag-bridge/docs/retrieval-mode-decision-tree.md
skill-project-wiki-rag-bridge/examples/vocus-profitability/source-profile.yaml
skill-project-wiki-rag-bridge/examples/vocus-profitability/retrieval-strategy.yaml
skill-project-wiki-rag-bridge/examples/vocus-profitability/benchmark-queries.yaml
skill-project-wiki-rag-bridge/audit/skill-dynamic-retrieval-readiness-audit-20260525_0003.md  ← this file
```

### Modify (existing files)

```
skill-project-wiki-rag-bridge/SKILL.md
skill-project-wiki-rag-bridge/prompts/05-index-wiki-domain.md
skill-project-wiki-rag-bridge/prompts/08-index-project-documents.md
skill-project-wiki-rag-bridge/checklists/indexing-readiness.md
skill-project-wiki-rag-bridge/README.md
skill-project-wiki-rag-bridge/CHANGELOG.md
```

---

## Validation plan for follow-up update

Run these checks after applying Phase 1–3 changes:

1. **File existence:** `find skill-project-wiki-rag-bridge/ -name "*.md" -o -name "*.yaml" | sort` — confirm all 15 new files created
2. **YAML parse:** `python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ['templates/retrieval-strategy.yaml', 'templates/source-profile.yaml', 'templates/benchmark-queries.yaml', 'templates/evidence-bundle.yaml', 'schemas/retrieval-strategy.schema.yaml', 'schemas/document-profile.schema.yaml', 'schemas/evidence-bundle.schema.yaml']]"` — no parse errors
3. **Outdated wording grep:** `grep -rn "RAG tooling" SKILL.md` — expect 0 matches after update
4. **Required new sections in SKILL.md:** `grep -n "Dynamic retrieval\|EvidenceBundle\|profile-file\|recommend-strategy\|benchmark-file" SKILL.md` — expect all 5 present
5. **No index-before-profile:** `grep -n "index-domain\|index-project" prompts/05-index-wiki-domain.md prompts/08-index-project-documents.md` — confirm each is preceded by a profile gate (PF-0 section)
6. **No global collections:** `grep -rn "rag__global\|rag__all\|rag__wiki_all" templates/ schemas/` — expect 0 matches (or only in forbidden lists)
7. **RAG not as default:** `grep -n "vector.rag\|vector RAG" SKILL.md` — confirm occurrences explain RAG is one of multiple routes, not the default
8. **EvidenceBundle in output contract:** `grep -n "EvidenceBundle" SKILL.md` — expect at least 1 match
9. **Checklist profile gate:** `grep -n "profile\|DOCUMENT_PROFILE" checklists/indexing-readiness.md` — expect BLOCKING profile items
10. **Examples show direct-lookup path:** `grep -n "structured.lookup\|lookup.section\|lookup.table" examples/vocus-profitability/` — expect at least 1 match

---

## Recommended follow-up prompt

Update the skill to add dynamic retrieval strategy awareness. Make these changes:

**Phase 1 (SKILL.md only):** In `SKILL.md`, update the rag-tools description from "RAG tooling" to "retrieval engine with dynamic strategy router". Add a new "Dynamic retrieval strategy" section that: (a) lists the 6 new CLI commands (`profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`) with one-line descriptions; (b) explains when vector RAG should NOT be the default (exact facts, tables, amounts, dates, clauses, section IDs); (c) defines EvidenceBundle as the required output contract for all retrieval operations. Insert a profiling step into the Standard workflow between the current Step 4 (validate-project-policy) and Step 5 (add-wiki-reference-article): "Step 4b → profile source documents and recommend strategy". Add 2 new safety rules and 3 new readiness labels. Update the agent behavior section to require profile-before-index.

**Phase 2 (prompts/templates/schemas/checklists):** Create prompts `02b-profile-and-recommend-strategy.md` and `02c-benchmark-retrieval-routes.md`. Add PF-0 profile gate to prompts 05 and 08. Create 4 new templates (`retrieval-strategy.yaml`, `source-profile.yaml`, `benchmark-queries.yaml`, `evidence-bundle.yaml`). Create 3 new schemas. Add profile-and-strategy section to `checklists/indexing-readiness.md`.

**Phase 3 (examples/docs/README/CHANGELOG):** Create 3 docs (`dynamic-retrieval-strategy.md`, `evidence-contract.md`, `retrieval-mode-decision-tree.md`) mirroring the rag-tools docs but framed for the skill workflow. Extend `examples/vocus-profitability/` with structured-lookup path example files. Update README and CHANGELOG.

Do not modify the existing collection isolation rules, retrieval-policy.yaml structure, or any checklists beyond the indexing-readiness profile gate addition. Those are correct and should remain unchanged.

---

## Audit notes

- Grep of the skill folder for `EvidenceBundle`, `structured.lookup`, `profile.file`, `recommend.strategy`, `benchmark` returned **zero matches** — confirming the dynamic retrieval capability is entirely unrepresented.
- Grep of rag-tools confirmed `EvidenceBundle` is used in `evidence.py`, `structured_lookup.py`, `table_lookup.py`; `profile_file` and `recommend_strategy` are in `document_profiler.py` and `strategy_selector.py`; benchmark in `retrieval_benchmark.py`. All 6 dynamic CLI commands are wired in `cli.py` and `justfile`.
- The rag-tools README "Dynamic retrieval strategy" section (lines 188–211) explicitly documents these commands. The skill was created before rag-tools added this section.
- `docs/dynamic-retrieval-strategy.md`, `docs/evidence-contract.md`, and `docs/retrieval-mode-decision-tree.md` exist in rag-tools and are absent from the skill.
- CHANGELOG entry `20260524_2252` confirms rag-tools gained dynamic retrieval capability on 2026-05-24 — the same day the skill was created (per skill CHANGELOG entry "2026-05-24 — Initial creation"). The skill predates the rag-tools dynamic retrieval addition and was never updated.
