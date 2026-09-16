# Project Wiki RAG Bridge

Reusable AI skill for connecting project repos to the shared Karpathy-style LLM wiki and rag-tools safely, with strict Qdrant collection isolation.

## Why this exists

The shared wiki (`_wiki/wiki_stuff`) is a growing cross-project knowledge base. Projects need selective, controlled access to wiki domains — not a free-for-all global search. This skill standardises:

- How projects declare which wiki domains they may query
- How wiki domains are created, indexed, and validated
- How Qdrant collection naming isolation is enforced
- How retrieval policies are authored and validated
- How to audit and troubleshoot the full bridge

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│  SOURCE OF TRUTH LAYER                                          │
│                                                                 │
│  _wiki/wiki_stuff/domains/<domain>/   ← shared reference facts │
│  _project/project_stuff/<proj>/       ← project-specific facts │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  POLICY / METADATA LAYER                                        │
│                                                                 │
│  _wiki/wiki-data/domain-registry.yaml                          │
│  _wiki/wiki-data/qdrant-collection-policy.md                   │
│  <project>/rag/project-context.yaml                            │
│  <project>/rag/retrieval-policy.yaml                           │
│  <project>/rag/manifests/project-documents.yaml                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  TOOLING LAYER                                                  │
│                                                                 │
│  _tool/tools_stuff/rag-tools/   ← shared Python tooling        │
│  tools-working-cache/rag-tools/.venv/  ← external venv         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  INDEX LAYER  (search artefact, not source of truth)           │
│                                                                 │
│  Qdrant: rag__wiki_<domain>          ← per-domain wiki index   │
│  Qdrant: rag__project_<slug>         ← per-project doc index   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  RETRIEVAL LAYER                                                │
│                                                                 │
│  Project policy → allowed wiki domains → isolated collections  │
│  → cited results → agent answer                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data flow

```text
Project repo
  ├── rag/retrieval-policy.yaml
  │     └── declared wiki domains: [nbn, vocus]
  │
  ├── rag-tools validate-policy rag/retrieval-policy.yaml
  │     └── checks: collection names, forbidden list, required filters
  │
  └── Agent query
        ├── Step 1: project-local files
        ├── Step 2: rag__project_<slug>  (filtered by project_slug)
        ├── Step 3: rag__wiki_nbn        (filtered by wiki_domain=nbn)
        │   rag__wiki_vocus      (filtered by wiki_domain=vocus)
        └── Step 4: ask user if insufficient evidence
              └── all results cite: source_file, section_path, collection
```

## Directory layout

```
project-wiki-rag-bridge/
  SKILL.md                      ← primary agent-facing instructions
  README.md                     ← this file (for human maintainers)
  ARCHITECTURE.md               ← layer model, component map, design decisions
  SETUP.md                      ← prerequisites, rag-tools verification, skill install
  AGENTS.md                     ← universal agent instruction file (@-imports parent)
  CLAUDE.md                     ← Claude Code wrapper over AGENTS.md
  AI_NAVIGATION.md              ← human-readable AI context router
  context-map.yaml              ← machine-readable routing and authority map
  CHANGELOG.md                  ← version history
  SCRATCHPAD.md                 ← agent working memory (cleared between sessions)
  ARCHCORE_PROMOTION_CANDIDATES.md ← promotion tracking (all promoted; run audit to refresh)
  repomix.config.json           ← deterministic AI context pack config
  .archcore/                    ← durable structured project truth (archcore-managed)
    adr/                        ← architecture decision records
    rules/                      ← durable project/agent rules
    specs/                      ← technical design contracts
    guides/                     ← operational guides
  .ai-context/                  ← generated AI context pack (repomix output; regenerable)
  templates/                    ← copy-and-fill templates
  prompts/                      ← numbered workflow prompt scripts
  schemas/                      ← YAML field definitions
  checklists/                   ← blocking gate checklists
  examples/                     ← concrete examples
    vocus-profitability/
    generic-project/
  docs/                         ← architecture, flows, failure modes, runbook
```

---

## How to use with Codex

1. Load the skill: reference `SKILL.md` in your Codex session context.
2. Pick the relevant prompt from `prompts/` for your current step.
3. Paste the prompt text into the Codex session. Adjust the `PROJECT_*` parameters at the top.
4. Work through the checklist in `checklists/` to confirm readiness before proceeding.

## How to use with Claude Code

1. The skill auto-loads when activated via `/project-wiki-rag-bridge` or by name in slash-command routing.
2. Claude Code reads `SKILL.md` and follows the standard workflow sequence.
3. Use the prompts in `prompts/` as the execution layer — paste them for each step.

---

## Common tasks

### Set up a new project bridge

```
1. Confirm wiki is operational:   prompts/00-verify-wiki-operational-state.md
2. Confirm wiki domains exist:    prompts/01-create-wiki-domain.md  (if needed)
3. Confirm rag-tools works:       prompts/02-verify-rag-tools.md
4. Create bridge files:           prompts/03-create-project-bridge.md
5. Validate policy:               prompts/04-validate-project-policy.md
```

### Add a new wiki domain

```
1. prompts/00-verify-wiki-operational-state.md
2. prompts/01-create-wiki-domain.md
3. prompts/07-add-wiki-reference-article.md  (add curated content)
4. prompts/05-index-wiki-domain.md           (dry-run, then live)
```

### Validate rag-tools

```
prompts/02-verify-rag-tools.md
```

Full doctor + Qdrant status + embedding smoke test. No destructive operations.

### Validate retrieval policy

```
prompts/04-validate-project-policy.md
```

YAML parse + rag-tools validate-policy + collection audit. No indexing.

### Index one wiki domain

```
prompts/05-index-wiki-domain.md  →  dry-run first, then confirm, then live
```

Indexes exactly one domain. Never indexes multiple domains in one operation.

### Test retrieval

```
prompts/06-post-index-retrieval-validation.md
```

Runs test queries. Verifies only allowed collections queried. Checks citation completeness.

---

## Dynamic retrieval strategy

`rag-tools` is now a retrieval engine, not just a vector RAG indexer. Before any indexing
decision, it profiles source files and recommends a retrieval route.

### Profile commands (read-only)

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin

# Classify a file: document_class, heading/table counts, recommended modes
$VENV/rag-tools profile-file <path/to/file>

# Profile all files in a directory
$VENV/rag-tools profile-project <project-root>

# Recommend retrieval strategy (primary / secondary / fallback / rag_suitability)
$VENV/rag-tools recommend-strategy <path/to/file>
```

### Lookup commands (read-only, no Qdrant needed)

```bash
# Deterministic heading/section lookup
$VENV/rag-tools structured-lookup <file> "<query>"

# Exact section ID lookup (e.g. C2.11)
$VENV/rag-tools lookup-section <file> <section-id>

# Table-aware lookup (rate cards, invoices)
$VENV/rag-tools lookup-table <file> "<query>"

# Benchmark all applicable modes against a query set
$VENV/rag-tools benchmark-file <file> --queries <queries.yaml>
```

### EvidenceBundle answer contract

Every retrieval command returns an `EvidenceBundle`. The LLM **must answer only from the
`excerpt` field** — no training knowledge fill-in. Key fields: `source_file`, `excerpt`,
`section_id`, `heading`, `table_id`, `retrieval_warnings`.

If no bundle is returned or `excerpt` is empty: report `RETRIEVAL_NOT_READY`.

See `docs/evidence-contract.md` for full answer rules and citation requirements.

### When not to use vector RAG

| Document class | Preferred route | RAG suitability |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` | partially_suitable |
| `financial_rate_card` | `table_aware_lookup` | not_suitable |
| `invoice_or_billing_report` | `table_aware_lookup` | not_suitable |
| `legal_contract_or_terms` | `section_clause_lookup` | partially_suitable |
| `knowledge_article` | `vector_rag` | suitable |
| `tabular_dataset` | `table_aware_lookup` | not_suitable |
| `unstructured_pdf` | extraction required | not_suitable |

### Relationship with the project/wiki bridge

The dynamic retrieval strategy layer adds per-document routing on top of the existing bridge:

1. `rag/retrieval-strategy.yaml` — records chosen route per document (new, from prompt 02b)
2. `rag/retrieval-policy.yaml` — governs Qdrant collection access and filters (existing)
3. `rag/manifests/project-documents.yaml` — controls `index: true` gate (existing)
4. `rag/source-profiles/` — per-file profiler output (new, from prompt 02b)
5. `rag/benchmarks/` — benchmark reports (new, from prompt 02c)

Profiling and strategy selection happen before any indexing. Direct and table lookup are
used without Qdrant when the document class supports it.

---

## Rollback guidance

If a collection is incorrectly named or populated:

```bash
# List collections
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Delete a collection (requires Qdrant HTTP access)
curl -X DELETE http://localhost:6333/collections/<collection_name>

# Re-index after cleanup
just rag-index-domain-dry <domain>   # verify dry-run first
just rag-index-domain <domain>
```

Do not delete collections in production without a dry-run of the re-index.

---

## Limitations

- This skill documents and governs the bridge workflow. It does not install rag-tools.
- It does not own Qdrant data. Qdrant is managed by `tools_stuff/rag-tools`.
- It does not create wiki markdown content. It only guides where and how to place it.
- Collection isolation is enforced by policy only. Qdrant has no built-in multi-tenant enforcement.
- The rag-tools `validate-policy` CLI validates flat top-level keys only (see `schemas/retrieval-policy.schema.yaml`).
- Local embeddings use `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). Do not mix with collections indexed with different models.
