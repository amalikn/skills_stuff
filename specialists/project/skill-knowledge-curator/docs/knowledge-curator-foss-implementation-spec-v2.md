---
Title: Knowledge Curator v2 FOSS Implementation Specification
Category: design
Status: proposed
Authority: operator-supplied source document, 2026-10-27 (further research after v1); verbatim except front matter and Contents
Scope: >-
  Proposed v2 of skill-knowledge-curator: slurp Step 4c contract, FOSS tool matrix, code and diagram extraction, federated cross-project
  linking, claim record schema, output envelope, tests T01-T18 and execution stages
Last reviewed: 2026-10-27
Summary: >-
  Second-round design for the curator, written before the v1 kernel was seen; extends scope to code, Mermaid, draw.io and ASCII diagrams and
  cross-project relationships, and conflicts with several settled v1 decisions (see catalog.md, v2 section).
---

# Knowledge Curator v2 — FOSS Implementation Specification

**Status:** Implementation handoff; not an implemented or validated skill.  
**Scope:** Enhance the existing `skill-slurp-chat` and Knowledge Curator skills without replacing project governance, memory backends, or repository authority.  
**Constraints:** FOSS add-ons only; no Khoj, Serena, or CodeQL dependencies; support Codex, Claude Code and local LLM clients.

## Contents

- [1. Purpose and non-goals](#1-purpose-and-non-goals)
- [2. Integration contract with `skill-slurp-chat`](#2-integration-contract-with-skill-slurp-chat)
- [3. Proposed topology](#3-proposed-topology)
- [4. Tool selection (FOSS-only)](#4-tool-selection-foss-only)
- [5. Multi-format extraction](#5-multi-format-extraction)
- [6. Knowledge record schema](#6-knowledge-record-schema)
- [7. Reconciliation algorithm](#7-reconciliation-algorithm)
- [8. Cross-project sharing contract](#8-cross-project-sharing-contract)
- [9. Skill directory hierarchy](#9-skill-directory-hierarchy)
- [10. Output contract](#10-output-contract)
- [11. Acceptance tests / gates](#11-acceptance-tests--gates)
- [12. Execution stages for coding agent](#12-execution-stages-for-coding-agent)
- [13. Engineering decisions still to verify on the actual repos](#13-engineering-decisions-still-to-verify-on-the-actual-repos)

---

## 1. Purpose and non-goals

The Curator converts evidence from sessions, documents, code and diagrams into **atomic, attributable knowledge claims**, reconciles claims against existing governed records, finds relationships
within/across projects and proposes targeted updates. It does **not** blindly concatenate summaries, autonomously edit unrelated repositories, or elevate inferred relationships to verified facts.

**Non-goals for MVP:** production graph service; large-scale autonomous crawling; rewriting all project files; replacing memory-keeper, project-context, SCRATCHPAD, change logs, status sources, or the
existing wiki generator.

## 2. Integration contract with `skill-slurp-chat`

Existing slurp Steps 0–4 remain unchanged. Insert a **conditional Step 4c** after the Zone B item list and Zone A comparison and before Step 5 writes. The Curator consumes the extracted item list,
relevant source files, current record pointers and project authority metadata.

### Invoke when
- Items contain potentially reusable technical knowledge or a cross-project dependency.
- New claims conflict with existing facts, or status/version/decision chronology is ambiguous.
- A changed code or diagram artifact may invalidate documented behavior.
- The user expressly requests curation.

### Skip when
- Pure chitchat or simple progress memory has no durable knowledge value.
- No source or relevant context exists for meaningful reconciliation. Skip must be reported, not silently guessed.

### Preserve slurp invariants
- Capture operational events and undecided proposals even when curation cannot resolve them.
- Step 5a scripts, Step 5b skill write-backs, Step 6 governed records, Step 6b self-audit, Step 7 checkpoints and wiki generation retain their existing ownership and completion conditions.
- Existing `record_decision` only records confirmed operator decisions; Curator proposals are never decisions.
- No commits/pushes by the Curator; existing slurp rules apply.

## 3. Proposed topology

```text
User/session + repo files + diagram sources
                    |
          skill-slurp-chat Steps 0–4
                    |
            Zone B item inventory
                    |
              Knowledge Curator
                    |
      +-------------+---------------+
      |             |               |
  Ingest/parser   Retrieval    Authority index
  docs/code/      lexical +     project rules,
  diagrams         semantic      chronology
      |             |               |
      +-------------+---------------+
                    |
         LLM claim synthesis & check
                    |
      Structured, source-linked findings
                    |
           skill-slurp-chat Step 5+
                    |
      +-------------+---------------+
      |             |               |
 Memory Keeper  Project Context  Governed files
                    |
              Existing self-audit
```

Cross-project discovery is **federated**: projects retain authority; shared indexes contain references, aliases, metadata and candidate relationships, not shadow copies of authoritative facts.

## 4. Tool selection (FOSS-only)

| Component                        | Proposed implementation             | Tier                            | Why / constraints                                                                         |
| -------------------------------- | ----------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------- |
| Markdown/text ingestion          | native Markdown parser +            | Required                        | Preserve headings, front matter, line ranges, code fences and identifiers.                |
|                                  |   standard libraries                |                                 |                                                                                           |
| Common document conversion       | MarkItDown                          | Conditional                     | Useful for office/web-type sources; preserve link to original and extractor version.      |
| Layout-sensitive                 | Docling                             | Conditional                     | Tables and structure; only invoke for matching formats.                                   |
|   PDF/Office parsing             |                                     |                                 |                                                                                           |
| Source code parsing              | Tree-sitter                         | Required for code               | Syntax-aware nodes and stable source spans; language grammars selected per repo.          |
| Structural code search           | ast-grep                            | Conditional                     | Pattern and AST matching; complements Tree-sitter.                                        |
| Semantic similarity              | Sentence Transformers               | Required when semantic          | Rank candidate equivalents; fuzzy score is not proof.                                     |
|                                  |                                     |   matching enabled              |                                                                                           |
| Lexical retrieval                | SQLite FTS5                         | Required                        | Fast, portable baseline and audit-friendly exact lookup.                                  |
| Relationship analysis            | NetworkX                            | Required when cross-project     | In-process graph over versioned relationship records.                                     |
|                                  |                                     |   graph enabled                 |                                                                                           |
| LLM structured synthesis         | Existing Codex/Claude/local model   | Required                        | Extract, reconcile and summarize using cited evidence.                                    |
|                                  |   via adapter                       |                                 |                                                                                           |
| Schema validation                | Pydantic                            | Required                        | Fail closed on invalid outputs and source identifiers.                                    |
| Entity extraction                | GLiNER                              | Optional                        | Use only if benchmark beats LLM/rule extraction.                                          |
| Graph-assisted retrieval         | LightRAG                            | **Pilot, not mandatory**        | Evaluate against SQLite+NetworkX baseline for explainability, licensing, costs            |
|                                  |                                     |                                 |   and complexity.                                                                         |
| Large-scale vector store         | Qdrant                              | Optional later                  | Add only if measured retrieval needs exceed baseline.                                     |
| Deep code property graphs        | Joern                               | Optional later                  | Heavy analysis for cross-function data-flow; not required for architecture curation.      |
| Analytical tabulation            | DuckDB                              | Optional                        | Useful for large structured extracts; unnecessary for initial record store.               |
| CodeQL                           | Excluded                            | No                              | Does not satisfy unrestricted strict FOSS requirement for analysis engine.                |

Before installation, pin exact versions and verify each selected dependency's current upstream license, distribution terms, supported platforms and transitive runtime requirements. Do not infer
compliance from a GitHub repository alone.

## 5. Multi-format extraction

### 5.1 Documents
1. Detect format and route to parser.
2. Preserve original path, revision/hash, section heading, line/page ranges, extracted tables and link targets.
3. Separate direct quotations/observations from interpretations.
4. Extract individual candidate claims rather than whole-page summaries.

### 5.2 Source code
1. Discover repository language and manifest/dependency boundaries.
2. Tree-sitter extracts definitions, imports, references and explicit configuration values; ast-grep searches targeted structures.
3. Optionally use LSP/compiler indexes **only where present and authoritative** for symbol resolution; Tree-sitter syntax alone does not establish runtime call graphs.
4. Record `repo`, `commit`, `path`, source span, symbol name and analysis method.
5. Label static inferences as *candidate*, not verified runtime behavior.

### 5.3 Mermaid diagrams
- Parse supported Mermaid source syntax to nodes, edges, labels and subgraphs; keep parser version and text spans.
- Not all diagram types share the same graph semantics. Unsupported types produce `unparsed`, never fabricated structure.
- Compare extracted relationships with code/config/docs before promoting them.

### 5.4 Draw.io / diagrams.net
- Read `.drawio` XML (`mxfile` and `mxGraphModel`), including decompression/decoding of compressed diagram payloads when applicable.
- Extract vertices, edges, labels, page/layer context and embedded links.
- XML edges show drawing connections, **not automatically proven technical dependencies**.

### 5.5 ASCII diagrams
- Heuristic text/box/arrow extraction with original monospace span retained.
- Low-confidence edge interpretations stay `proposed`; require corroboration or human review.
- Never OCR source-available diagrams; for image-only diagrams, clearly mark the limitation and require an appropriate approved image-understanding route.

## 6. Knowledge record schema

Every finding should include:

```yaml
id: claim:<stable-hash>
project_id: smc-resiliency
kind: requirement  # fact|decision|requirement|constraint|proposal|incident|relationship
subject: SMC OS update
predicate: requires
object: power-cut-safe rollback
summary: "SMC OS updates must tolerate interrupted installation and recover safely."
status: supported  # supported|conflicted|inferred|proposed|superseded|unresolved
confidence: 0.92   # heuristic only, never substitutes for evidence
observed_at: null # populated only from sourced timestamp
effective_at: null
sources:
  - repo: smc-resiliency
    revision: <git-commit-or-content-hash>
    path: docs/requirements.md
    locator: "section: Recovery"
    exact_excerpt: "..."
relations:
  - target: claim:<other-id>
    type: depends_on # references|equivalent_to|depends_on|conflicts_with|supersedes
    status: candidate
owner_project: smc-resiliency
action: propose_update # no_change|propose_update|request_review
```

**Rules:** valid `sources` required for `supported`; do not manufacture timestamps, commit hashes, file paths, owners or citations; every relation has evidence and explicit epistemic status; avoid
copying large source passages into indexes.

## 7. Reconciliation algorithm

1. **Retrieve:** lexical search, then semantic reranking, scoped to candidate projects and authorized sources.
2. **Normalize:** align entity aliases and terminology; avoid merging coincidental names.
3. **Partition:** classify by claim type, scope, environment, platform/version and effective time.
4. **Compare:** detect near-duplicates, complementary claims, genuine contradictions and supersession.
5. **Determine authority:** apply repository-declared authority/status hierarchy and operator decisions; newer timestamps alone are insufficient.
6. **Synthesize:** write the minimal consolidated explanation plus supporting source pointers and dissenting/conflicting references.
7. **Validate:** source-locator existence, schema, support coverage and no unsupported promotion.
8. **Route:** generate a per-owner **proposal**, not a cross-repo write.

### Contradiction example
A historical audit reports a compatibility symlink retained; a later authoritative audit states it was removed. Curator records both as an evolving timeline and outputs the later authoritative current
state; it does not erase the earlier observation or flag a false simultaneous contradiction.

## 8. Cross-project sharing contract

- Use stable global claim and project identifiers; alias table maps labels like `SMC`, `site management controller`, and repository component names with source evidence.
- Supported relationship types: `depends_on`, `implements`, `exposes_interface`, `consumes_interface`, `constrains`, `supersedes`, `duplicates`, `conflicts_with`, `related_to`.
- Relationship evidence includes references from **both ends** where possible; one-sided inferred links remain candidates.
- Direct cross-project discovery is allowed even when governance routes write-back through a hub.
- The owning project decides whether an update is committed; changes follow its `AGENTS.md`, `context-map.yaml`, status and companion rules.
- Enforce per-project ACLs. A shared index must not leak private project content to another agent or project.

## 9. Skill directory hierarchy

```text
skill-knowledge-curator/
├── SKILL.md                          # Triggers, orchestration contract, stop conditions
├── references/
│   ├── taxonomy.md                  # Shared classes + project-specific labels
│   ├── evidence-and-authority.md    # Provenance, status, precedence rules
│   ├── schemas.md                   # Claim/relation/input-output schemas
│   ├── parsing.md                   # Documents, code, Mermaid, Draw.io, ASCII
│   ├── reconciliation.md            # Conflict, equivalence, supersession
│   ├── cross-project.md             # Discovery, ownership, ACL and write-back
│   ├── llm-prompts.md               # Extraction/reconciliation prompts and safeguards
│   ├── tool-matrix.md               # FOSS licenses, versions, fallbacks
│   └── evaluation.md                # Benchmark methodology and gold cases
├── scripts/
│   ├── ingest.py
│   ├── extract_claims.py
│   ├── parse_code.py
│   ├── parse_diagrams.py
│   ├── find_related.py
│   ├── reconcile.py
│   └── validate_proposals.py
├── schemas/
│   ├── claim.schema.json
│   └── proposal.schema.json
├── tests/
│   ├── fixtures/
│   ├── test_parsing.py
│   ├── test_reconciliation.py
│   ├── test_cross_project.py
│   ├── test_provenance.py
│   └── test_slurp_integration.py
└── README.md                         # Developer setup only
```

Follow the actual conventions found in the existing skills repository. Do **not** create every proposed file if existing structures already meet the purpose.

## 10. Output contract

Curator emits a machine-readable envelope:

```json
{
  "run_id": "<generated-id>",
  "input_boundary": "<slurp-boundary-id>",
  "claims": [],
  "relationships": [],
  "conflicts": [],
  "proposed_updates": [
    {"owner_project": "smc-resiliency", "target": "<governed-file>", "reason": "<evidence-backed-impact>", "source_ids": []}
  ],
  "unresolved": [],
  "sources_checked": [],
  "audit": {"schema_valid": false, "citations_resolved": false, "unapproved_cross_project_writes": 0}
}
```

The slurp coverage table gains a `curator status` or reference field, without changing its mandatory existing destination columns. Conflicted and unresolved items remain visible and findable.

## 11. Acceptance tests / gates

| ID  | Scenario                                    | Expected behavior                                                    |
| --- | ------------------------------------------- | -------------------------------------------------------------------- |
| T01 | Two paraphrases of one requirement          | One normalized claim, two citations.                                 |
| T02 | Same acronym, two different systems         | No false entity merge.                                               |
| T03 | Conflicting current claims                  | Both retained, flagged, no invented resolution.                      |
| T04 | Historical vs later authoritative audit     | Correct current state, historical timeline preserved.                |
| T05 | Proposal vs operator decision               | Proposal stays unresolved, never `record_decision`.                  |
| T06 | Markdown + PDF table                        | Source-located values, no lost table relationship.                   |
| T07 | Python import and function definition       | Correct source spans; no false runtime flow claim.                   |
| T08 | Cross-project symbol/dependency             | Traceable proposed relationship; no automatic write.                 |
| T09 | Mermaid graph                               | Correct nodes/edges; unsupported syntax surfaced.                    |
| T10 | Draw.io multi-page graph                    | Correct page-scoped vertices/edges; no false operational authority.  |
| T11 | Ambiguous ASCII arrow                       | Candidate only; original diagram preserved.                          |
| T12 | Source removed/renamed                      | Citation validation fails, proposal withheld.                        |
| T13 | Repeat same run                             | Stable IDs, no duplicate records or slurp notes.                     |
| T14 | Unavailable model/embedding backend         | Deterministic fallback or explicit unresolved, no phantom success.   |
| T15 | Restricted cross-project record             | No unauthorized retrieval/output.                                    |
| T16 | Engaged skill write-back + script promotion | Existing Step 5a/5b checks still run.                                |
| T17 | One production operational event            | Always reaches change log even if Curator skips.                     |
| T18 | Low-quality related-document match          | Doesn't become a supported dependency merely from cosine similarity. |

**Exit gate:** all mandatory tests pass on one representative project pair; measure false merges, false contradictions, evidence coverage, latency and duplicate publication against a human-annotated
benchmark. No acceptance based only on a plausible-looking synthesis.

## 12. Execution stages for coding agent

1. **Inspect first:** existing `skill-slurp-chat`, Knowledge Curator implementation, memory skills, repo conventions and project governance. Produce a gap matrix before editing.
2. **Build deterministic baseline:** parsing, SQLite FTS5, stable IDs, Pydantic schemas, source locator checks. Implement minimal tool adapters, not a new service.
3. **Add semantic reasoning:** embeddings/reranking + LLM extraction and synthesis. Run against gold fixtures.
4. **Add code and diagrams:** Tree-sitter and Mermaid; then Draw.io and ASCII with explicit uncertainty; ast-grep only for demonstrated need.
5. **Enable federated project linking:** NetworkX graph and ownership/ACL checks. No cross-repo writes.
6. **Integrate with slurp:** conditional Step 4c, existing Steps 5–7 preserved; regression coverage.
7. **Evaluate optional engines:** trial LightRAG versus baseline on identical fixtures; adopt only if retrieval/relationship quality improves sufficiently without violating provenance and ownership
   requirements.

## 13. Engineering decisions still to verify on the actual repos

- How Knowledge Curator was implemented after the previous v1 handoff, and its existing APIs/contracts.
- Whether a shared SQLite index already exists and how it maps onto `_ai` canonical data/cache/runtime policy.
- Which Mermaid syntax family and Draw.io encoding are prevalent in your projects.
- Which models are permitted to read each project and whether an offline-only mode is required.
- Whether any current slurp step already indexes extracted symbols/relations (avoid overlap).

**Delivery rule:** Coding agent must report what it inspected, changes made, benchmark results, remaining gaps and precise file paths; it must not claim the whole architecture is implemented merely
because the specification exists.
