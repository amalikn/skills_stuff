# Architecture

## Overview

The project-wiki-rag-bridge connects three distinct systems through a policy-governed layer:

```text
┌────────────────────────────────────────────────────────────────────────┐
│  AUTHORING LAYER (source of truth — never Qdrant)                      │
│                                                                        │
│  ┌─────────────────────────────┐  ┌────────────────────────────────┐   │
│  │  _wiki/wiki_stuff/          │  │  _project/project_stuff/<proj> │   │
│  │  domains/nbn/               │  │  reports/                      │   │
│  │  domains/vocus/             │  │  docs/csv/                     │   │
│  │  domains/mcp/               │  │  manifests/                    │   │
│  │  ...                        │  │  rag/                          │   │
│  └──────────────┬──────────────┘  └───────────────┬────────────────┘   │
│                 │ shared reference facts            │ project-specific   │
└─────────────────┼──────────────────────────────────┼────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  POLICY LAYER (governs what goes where and who may access what)          │
│                                                                          │
│  _wiki/wiki-data/domain-registry.yaml      ← domain declaration         │
│  _wiki/wiki-data/qdrant-collection-policy  ← naming and metadata rules  │
│  <project>/rag/project-context.yaml        ← project wiki dependencies  │
│  <project>/rag/retrieval-policy.yaml       ← flat validator contract     │
│  <project>/rag/manifests/project-docs.yaml ← document index manifest    │
└─────────────────┬──────────────────────────────────┬────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  TOOLING LAYER (does the actual indexing and retrieval)                  │
│                                                                          │
│  _tool/tools_stuff/rag-tools/               ← shared Python tooling     │
│    src/rag_tools/cli.py                     ← CLI (doctor, index, etc.) │
│    src/rag_tools/policy.py                  ← validator                 │
│    src/rag_tools/embeddings.py              ← local embedding model     │
│    scripts/qdrant-up, qdrant-status, etc.   ← Docker lifecycle          │
│  tools-working-cache/rag-tools/.venv/       ← isolated venv             │
└─────────────────┬──────────────────────────────────┬────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  INDEX LAYER (Qdrant — retrieval artefact, not source of truth)          │
│                                                                          │
│  rag__wiki_nbn              ← wiki domain nbn, scoped, filtered          │
│  rag__wiki_vocus            ← wiki domain vocus, scoped, filtered        │
│  rag__wiki_mcp              ← wiki domain mcp, scoped, filtered          │
│  rag__project_vocus_profitability  ← project vocus, project-filtered     │
│  rag__project_<other_slug>         ← other project, own collection       │
│                                                                          │
│  FORBIDDEN: rag__all, rag__wiki_all, default, documents, knowledge, main │
└──────────────────────────────────────────────────────────────────────────┘
```

## Key design decisions

### 1. Qdrant is not the source of truth

Markdown files are the source of truth. Qdrant is a search index over them.
If a Qdrant collection is deleted, the knowledge is not lost — re-index from the markdown source.

### 2. Policy is enforced in software, not in Qdrant

Qdrant has no multi-tenant enforcement. Isolation is enforced by:
- `retrieval-policy.yaml` — declares allowed/forbidden collections
- `rag-tools validate-policy` — validates policy before any indexing
- This skill's guidance — constrains agent behaviour at query time

### 3. One collection per domain / one collection per project

No collection serves multiple domains or projects. This prevents cross-domain and cross-project
retrieval bleed. Sharing is achieved by declaring wiki domain access in project policy, not by
sharing collections.

### 4. Retrieval order

Every project follows this retrieval order:
1. Project-local files (fastest, most authoritative for project facts)
2. Project Qdrant collection (indexed project documents — secondary)
3. Declared wiki domain collections (shared reference knowledge)
4. Ask user (when no sufficient evidence found)

### 5. External venv

rag-tools uses an isolated venv at `tools-working-cache/rag-tools/.venv`.
Project justfiles reference this venv by absolute path. The venv is not in the source tree.

### 6. Local embeddings only

All embeddings use `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) loaded locally
from HuggingFace cache. No external API calls. This is a hard constraint — do not mix
collections indexed with different models.
