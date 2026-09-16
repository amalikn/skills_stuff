# Flow Diagrams

All diagrams use plain text. No rendering dependency.

---

## 1. Wiki Authoring Flow

```text
Human author
  │
  ├─► writes markdown article
  │     with frontmatter (title, domain, type, source, authority)
  │     under wiki_stuff/domains/<domain>/references/<slug>.md
  │
  ├─► adds source reference in ## Source references section
  │
  ├─► updates domain index.md (Contents table)
  │
  └─► appends to wiki_stuff/log.md
          │
          ▼
     wiki_stuff/domains/<domain>/   ← source of truth, immutable after commit
```

---

## 2. Project Bridge Setup Flow

```text
Agent (using this skill)
  │
  ├─ Step 1: prompt/00 ─► verify wiki operational state
  │                         WIKI_OPERATIONAL_READY? → continue
  │                         NOT_READY? → fix first
  │
  ├─ Step 2: prompt/01 ─► create wiki domain (if missing)
  │                         mkdir domains/<domain>/
  │                         update domain-registry.yaml
  │
  ├─ Step 3: prompt/02 ─► verify rag-tools
  │                         doctor + Qdrant + embeddings
  │                         RAG_TOOLS_READY? → continue
  │
  ├─ Step 4: prompt/03 ─► create project bridge files
  │                         rag/project-context.yaml
  │                         rag/retrieval-policy.yaml
  │                         rag/manifests/project-documents.yaml
  │                         docs/ai/wiki-bridge.md
  │                         update AGENTS/AI_NAVIGATION/README/CHANGELOG
  │
  ├─ Step 5: prompt/04 ─► validate project policy
  │                         YAML parse → flat keys → rag-tools validate-policy
  │                         PROJECT_RAG_POLICY_VALIDATED? → continue
  │
  └─► PROJECT_WIKI_BRIDGE_READY
```

---

## 3. Indexing Flow

```text
Agent (using this skill)
  │
  ├─ checklists/indexing-readiness.md ─► all BLOCKING checks pass?
  │                                         NO → fix → re-check
  │
  ├─ Step 6: prompt/07 ─► add wiki reference articles
  │                          curated content with source references
  │                          under domains/<domain>/references/
  │
  ├─ Step 7: prompt/05 ─► index wiki domain
  │   │
  │   ├─► DRY-RUN: rag_tools.cli index-domain --domain <d> --dry-run
  │   │       chunk count OK? no cross-domain bleed? → confirm
  │   │
  │   ├─► LIVE: rag_tools.cli index-domain --domain <d>
  │   │       upserts idempotently to rag__wiki_<d>
  │   │
  │   └─► verify: Qdrant collection vectors_count > 0
  │           WIKI_DOMAIN_INDEXED → continue
  │
  └─► (optional) prompt/08 ─► index project documents
          manifest check: only index: true, not sensitive
          DRY-RUN first → LIVE → verify
```

---

## 4. Retrieval Flow

```text
Agent query: "What is the DCR eligibility rule for FWA services?"
  │
  ├─ Step 1: search project-local files
  │     grep, find, read reports/ manifests/ analysis/
  │     found relevant? → cite, return, done
  │     not found? → continue
  │
  ├─ Step 2: query project collection
  │     rag__project_vocus_profitability
  │     filter: project_slug = vocus_profitability
  │     top results + scores → relevant? → cite, return
  │     not found / low score? → continue
  │
  ├─ Step 3: query declared wiki domains
  │     rag__wiki_nbn  (filter: wiki_domain = nbn)
  │     rag__wiki_vocus (filter: wiki_domain = vocus)
  │     results → cite source_file, heading, section_path, collection
  │     relevant? → return with citation
  │     not found? → continue
  │
  └─ Step 4: ask user
        "I searched project-local files, project collection, and wiki domains
         [nbn, vocus]. Insufficient evidence found. Can you provide additional
         context or point me to the relevant document?"
```

---

## 5. Troubleshooting Flow

```text
Problem observed
  │
  ├─ venv missing / import error
  │     → prompt/09 Symptom A or B
  │     → rebuild: uv sync with UV_PROJECT_ENVIRONMENT
  │
  ├─ Qdrant unreachable
  │     → prompt/09 Symptom C
  │     → qdrant-up → check Docker context
  │
  ├─ policy validator fails
  │     → prompt/09 Symptom E
  │     → check flat validator keys (schemas/retrieval-policy.schema.yaml)
  │
  ├─ empty collection after indexing
  │     → prompt/09 Symptom H
  │     → check domain content exists, re-run index
  │
  ├─ no useful retrieval (low scores)
  │     → prompt/09 Symptom I
  │     → check embedding model match (384-dim, all-MiniLM-L6-v2)
  │
  └─ sensitive data in collection
        → prompt/09 Symptom J
        → delete collection → fix manifest → re-index
```
