# Architecture — skill-project-wiki-rag-bridge

## Contents

- [Purpose](#purpose)
- [Layer model](#layer-model)
- [Dynamic retrieval layer](#dynamic-retrieval-layer)
- [Key design decisions](#key-design-decisions)
- [Component map](#component-map)
- [Detailed reference](#detailed-reference)

## Purpose

This skill is a policy-governed bridge between project repositories, shared wiki domains, and Qdrant RAG tooling. It enforces collection isolation, authority ordering, and retrieval discipline. It does not own wiki content, Qdrant data, or embedding models — it governs how they are accessed.

## Layer model

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║  AUTHORING LAYER  (source of truth — never Qdrant)                          ║
║                                                                              ║
║  ┌────────────────────────────┐   ┌────────────────────────────────────────┐ ║
║  │  _wiki/wiki_stuff/         │   │  _project/project_stuff/<proj>/        │ ║
║  │  domains/nbn/              │   │  docs/           ← references, reports  │ ║
║  │  domains/vocus/            │   │  docs/csv/       ← rate cards, datasets │ ║
║  │  domains/mcp/              │   │  rag/            ← bridge YAML files    │ ║
║  │  ...                       │   │  manifests/      ← project-documents.md │ ║
║  └────────────────────────────┘   └────────────────────────────────────────┘ ║
║        shared reference facts             project-specific facts              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  POLICY LAYER  (governs access, naming, and isolation)                       ║
║                                                                              ║
║  domain-registry.yaml          ← which domains exist and their slugs        ║
║  qdrant-collection-policy.md   ← allowed/forbidden collection names         ║
║  project-context.yaml          ← which wiki domains this project may query  ║
║  retrieval-policy.yaml         ← flat validator contract (per-project)      ║
║  project-documents.yaml        ← index:true/false gate per document         ║
║  retrieval-strategy.yaml       ← chosen retrieval route per document        ║
║                                                                              ║
║  Enforcement: rag-tools validate-policy <project>/rag/retrieval-policy.yaml ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  DYNAMIC RETRIEVAL LAYER  (profile-first; runs before any indexing)         ║
║                                                                              ║
║  rag-tools profile-file <path>        → document_class + recommended modes  ║
║  rag-tools profile-project <root>     → bulk profile all project docs       ║
║  rag-tools recommend-strategy <path>  → primary / secondary / fallback      ║
║                                                                              ║
║  Decision tree per document:                                                 ║
║                                                                              ║
║  document_class?                                                             ║
║  ├─ structured_markdown_reference  →  direct_structured_lookup (CLI)        ║
║  │    rag-tools structured-lookup <file> "<query>"                           ║
║  ├─ legal_contract_or_terms        →  section_clause_lookup (CLI)           ║
║  │    rag-tools lookup-section <file> <section-id>                           ║
║  ├─ financial_rate_card            →  table_aware_lookup (CLI)              ║
║  │    rag-tools lookup-table <file> "<query>"                                ║
║  ├─ invoice_or_billing_report      →  table_aware_lookup (CLI)              ║
║  │    rag-tools lookup-table <file> "<query>"                                ║
║  ├─ tabular_dataset                →  table_aware_lookup (CLI)              ║
║  │    rag-tools lookup-table <file> "<query>"                                ║
║  └─ knowledge_article              →  vector_rag (Python API, not CLI)      ║
║       qdrant_client.query_points(collection, embedding, filter=project_slug) ║
║                                                                              ║
║  NOTE: vector_rag has no CLI command — use Python qdrant_client directly.   ║
║  CLI covers all deterministic modes. See docs/evidence-contract.md.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  TOOLING LAYER                                                               ║
║                                                                              ║
║  Canonical source:  _tool/tools_stuff/rag-tools/                            ║
║  Runtime venv:      tools-working-cache/rag-tools/.venv/bin/rag-tools       ║
║                     ^^^^^ always use this path; never tools_stuff            ║
║                                                                              ║
║  CLI commands (13 total):                                                    ║
║  ┌─ Infrastructure ─────────────────────────────────────────────────────┐   ║
║  │  doctor               health check (venv, Qdrant, model)             │   ║
║  │  qdrant-status        connectivity check                              │   ║
║  │  collections          list indexed collections                        │   ║
║  │  embedding-smoke-test verify sentence-transformers model loads        │   ║
║  │  validate-policy      parse + validate retrieval-policy.yaml          │   ║
║  │  index-domain         index one wiki domain into Qdrant               │   ║
║  └───────────────────────────────────────────────────────────────────────┘  ║
║  ┌─ Dynamic Retrieval (all read-only) ──────────────────────────────────┐   ║
║  │  profile-file         classify one file; output document_class       │   ║
║  │  profile-project      bulk-profile a directory                       │   ║
║  │  recommend-strategy   recommend primary/secondary/fallback route     │   ║
║  │  structured-lookup    deterministic heading/section lookup            │   ║
║  │  lookup-section       exact section-ID lookup (e.g. C2.11)           │   ║
║  │  lookup-table         table-aware lookup (rate cards, invoices)       │   ║
║  │  benchmark-file       compare modes against a query set              │   ║
║  └───────────────────────────────────────────────────────────────────────┘  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  INDEX LAYER  (Qdrant — retrieval artefact, never source of truth)          ║
║                                                                              ║
║  rag__wiki_nbn                  ← wiki domain nbn  (wiki_domain=nbn filter) ║
║  rag__wiki_vocus                ← wiki domain vocus                         ║
║  rag__wiki_mcp                  ← wiki domain mcp                           ║
║  rag__project_vocus_profitability  ← project docs (project_slug= filter)    ║
║  rag__project_<other_slug>         ← other project, fully isolated          ║
║                                                                              ║
║  FORBIDDEN NAMES: rag__all, rag__wiki_all, default, documents, knowledge    ║
║  ISOLATION: enforced by policy + validate-policy CLI; not by Qdrant itself  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Full retrieval flow

```text
USER QUERY
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1 — Project-local files  (fastest; highest authority for project facts)│
│                                                                              │
│  Read markdown directly. No Qdrant. No rag-tools.                           │
│  rag/project-context.yaml, docs/, reports/, rag/source-profiles/            │
│                                                                              │
│  Found sufficient evidence?  →  YES: go to EvidenceBundle                   │
│                                  NO: continue to Step 2                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │ (not found)
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2 — Dynamic retrieval  (mode determined by document_class)            │
│                                                                              │
│  Consult rag/retrieval-strategy.yaml for the target document.               │
│                                                                              │
│  ┌─ DIRECT_FIRST or HYBRID_DIRECT_FIRST ──────────────────────────────┐    │
│  │  rag-tools structured-lookup <file> "<query>"                       │    │
│  │  rag-tools lookup-section <file> <section-id>                       │    │
│  │  Fallback to vector_rag only if lookup returns empty.               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─ TABLE_LOOKUP_FIRST ───────────────────────────────────────────────┐    │
│  │  rag-tools lookup-table <file> "<query>"                            │    │
│  │  No vector fallback — table docs are not RAG-suitable.             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─ VECTOR_RAG ───────────────────────────────────────────────────────┐    │
│  │  Python: qdrant_client.query_points(                                │    │
│  │    collection_name="rag__project_<slug>",                           │    │
│  │    query=embed(query_text),                                         │    │
│  │    query_filter={"project_slug": "<slug>"}  ← REQUIRED             │    │
│  │  )                                                                  │    │
│  │  No CLI vector command exists — Python only.                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Found sufficient evidence?  →  YES: go to EvidenceBundle                   │
│                                  NO: continue to Step 3                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │ (not found)
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3 — Wiki domain collections  (shared reference knowledge)             │
│                                                                              │
│  Check retrieval-policy.yaml → allowed_wiki_domains.                        │
│  For each allowed domain:                                                    │
│    query rag__wiki_<domain>  (filter: wiki_domain=<domain>)                 │
│                                                                              │
│  Wiki collections are knowledge_article class → vector_rag via Python.      │
│                                                                              │
│  Found sufficient evidence?  →  YES: go to EvidenceBundle                   │
│                                  NO: continue to Step 4                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │ (not found)
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4 — Ask user                                                          │
│                                                                              │
│  Report: RETRIEVAL_NOT_READY or evidence gap. Do not infer or hallucinate.  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EVIDENCEBUNDLE  (all retrieval paths produce this structure)               │
│                                                                              │
│  {                                                                           │
│    query:              "<original query text>",                              │
│    retrieval_mode:     "direct_structured_lookup | section_clause_lookup     │
│                         | table_aware_lookup | vector_rag",                  │
│    document_id:        "<slug or identifier>",                               │
│    source_file:        "<path/to/source.md>",         ← REQUIRED CITATION   │
│    authority:          "primary | secondary | wiki",                         │
│    section_path:       "<heading chain>",             ← for lookup modes     │
│    heading:            "<nearest section heading>",                          │
│    excerpt:            "<exact text passage>",        ← ANSWER ONLY FROM HERE│
│    matched_terms:      ["<term1>", "<term2>"],                               │
│    score_or_confidence: 0.0–1.0,                                             │
│    context_chars:      256,                                                  │
│    retrieval_warnings: []                             ← check before answer  │
│  }                                                                           │
│                                                                              │
│  AGENT RULES:                                                                │
│  • Answer ONLY from excerpt field — never from training knowledge            │
│  • Always cite source_file + section_path                                    │
│  • If excerpt is empty or bundle is missing → report RETRIEVAL_NOT_READY    │
│  • If retrieval_warnings not empty → disclose before answering              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
AGENT ANSWER  (cited, evidence-grounded, no inference on exact facts)
```

## Collection isolation enforcement

```text
                        ┌─────────────────────┐
                        │   project-context    │
                        │   .yaml declares:    │
                        │   wiki_domains:      │
                        │     - nbn            │
                        │     - vocus          │
                        └──────────┬──────────┘
                                   │  governs
                                   ▼
                        ┌─────────────────────┐
                        │  retrieval-policy    │    ◄── validate-policy CLI
                        │  .yaml:              │        blocks invalid names
                        │  allowed_collections │        and forbidden patterns
                        │   - rag__wiki_nbn    │
                        │   - rag__wiki_vocus  │
                        │   - rag__project_    │
                        │     vocus_profit...  │
                        └──────────┬──────────┘
                                   │  enforces at query time
                         ┌─────────┴───────────┐
                         │                     │
                ┌────────▼────────┐   ┌────────▼────────┐
                │ rag__wiki_nbn   │   │ rag__project_   │
                │ (filter:        │   │ vocus_profit... │
                │  wiki_domain    │   │ (filter:        │
                │  = nbn)         │   │  project_slug   │
                │                 │   │  = vocus_pr...) │
                └────────────────┘   └─────────────────┘

NEVER ALLOWED:  rag__wiki_vocus  ←  from nbn project context
                rag__project_X   ←  from project Y's policy
                rag__all, default, documents, knowledge
```

## Dynamic retrieval layer

`rag-tools` is a retrieval engine, not only a vector RAG indexer. Documents are profiled before any indexing decision:

| Step | Command | Output |
|---|---|---|
| Profile a file | `rag-tools profile-file <path>` | `document_class`, heading/table counts, recommended modes |
| Profile a project | `rag-tools profile-project <root>` | per-file profiles |
| Recommend strategy | `rag-tools recommend-strategy <path>` | `retrieval_strategy` label |
| Lookup (no Qdrant) | `rag-tools structured-lookup <file> "<query>"` | EvidenceBundle |
| Section lookup | `rag-tools lookup-section <file> <id>` | EvidenceBundle |
| Table lookup | `rag-tools lookup-table <file> "<query>"` | EvidenceBundle |

### Retrieval mode routing

| Document class | Preferred mode | Vector RAG suitability |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` | partially_suitable |
| `financial_rate_card` | `table_aware_lookup` | not_suitable |
| `invoice_or_billing_report` | `table_aware_lookup` | not_suitable |
| `legal_contract_or_terms` | `section_clause_lookup` | partially_suitable |
| `knowledge_article` | `vector_rag` | suitable |
| `tabular_dataset` | `table_aware_lookup` | not_suitable |

### EvidenceBundle contract

Every retrieval path returns an `EvidenceBundle`. Agents must answer only from the `excerpt` field — no training knowledge fill-in. See `.archcore/specs/evidence-bundle-contract.md` for the full field contract.

## Key design decisions

1. **Qdrant is not the source of truth.** Markdown files are. Re-indexing always re-derives from source.
2. **Isolation is enforced by policy, not Qdrant.** Qdrant has no built-in multi-tenant enforcement. `retrieval-policy.yaml` + `rag-tools validate-policy` are the enforcement layer.
3. **One collection per domain, one per project.** No collection serves multiple domains or projects.
4. **Profile before indexing.** Direct lookup and table lookup are used without Qdrant when the document class supports it. Vector RAG is one path, not the default.
5. **Local embeddings only.** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). Do not mix collections indexed with different models.
6. **External venv.** `tools-working-cache/rag-tools/.venv/` — never create a venv inside this skill folder.

## Component map

```text
skill-project-wiki-rag-bridge/
  SKILL.md              ← primary agent-facing workflow instructions
  ARCHITECTURE.md       ← this file
  SETUP.md              ← prerequisites and first-use install steps
  docs/
    architecture.md     ← detailed layer diagram and design decision rationale
    authority-model.md  ← collection naming, authority order, isolation rules
    dynamic-retrieval-strategy.md  ← profile-first model, mode routing
    evidence-contract.md           ← EvidenceBundle answer rules
    retrieval-mode-decision-tree.md ← quick routing reference
  .archcore/
    adr/                ← accepted architecture decision records
    rules/              ← durable agent/project rules (retrieval isolation, sequencing)
    specs/              ← design contracts (EvidenceBundle, document profile, strategy YAML)
    guides/             ← operational guides (dynamic routing, evidence-first answering)
  prompts/00–09         ← numbered workflow execution scripts
  checklists/           ← blocking gate checklists (run before proceeding)
  schemas/              ← YAML field definitions (validate user-supplied YAML against these)
  templates/            ← copy-and-fill starting points
  examples/             ← vocus-profitability and generic-project reference implementations
```

## Detailed reference

- Full layer diagram: [docs/architecture.md](docs/architecture.md)
- Collection naming and isolation rules: [docs/authority-model.md](docs/authority-model.md)
- Dynamic retrieval strategy: [docs/dynamic-retrieval-strategy.md](docs/dynamic-retrieval-strategy.md)
- EvidenceBundle answer contract: [docs/evidence-contract.md](docs/evidence-contract.md)
- Retrieval mode decision tree: [docs/retrieval-mode-decision-tree.md](docs/retrieval-mode-decision-tree.md)
- Archcore accepted specs: [.archcore/specs/](.archcore/specs/)
