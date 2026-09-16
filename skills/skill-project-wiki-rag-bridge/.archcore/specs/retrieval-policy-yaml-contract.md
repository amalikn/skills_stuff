---
title: retrieval-policy.yaml Contract
status: accepted
date: 20260524
provenance: schemas/retrieval-policy.schema.yaml, SKILL.md, docs/multi-project-model.md
---

# retrieval-policy.yaml Contract

## Purpose

`retrieval-policy.yaml` is the single declaration of what a project is allowed to query. It lives at `<project>/rag/retrieval-policy.yaml`. It is validated by `rag-tools validate-policy` before any indexing or retrieval operation.

## Required fields

```yaml
project_slug: <lowercase_alphanumeric_underscores>      # unique project identifier
project_collection: rag__project_<project_slug>         # must follow naming convention
allowed_wiki_domains:                                   # explicit domain allowlist
  - <domain_slug_1>
  - <domain_slug_2>
wiki_collections:                                       # derived from allowed_wiki_domains
  - rag__wiki_<domain_slug_1>
  - rag__wiki_<domain_slug_2>
forbidden_collections:                                  # must include all globally forbidden names
  - rag__global_all_docs
  - rag__wiki_all
  - rag__all
  - default
  - documents
  - knowledge
  - main
```

## Constraints

- `project_slug` must be unique across all projects — check before creating
- `project_collection` must exactly match `rag__project_<project_slug>`
- `allowed_wiki_domains` must list only domain slugs that exist in `domain-registry.yaml`
- `wiki_collections` must be the derived set from `allowed_wiki_domains`
- `forbidden_collections` must include at minimum the globally forbidden set
- Do not add other projects' `rag__project_*` collections anywhere in this file

## Validation command

```bash
rag-tools validate-policy <project>/rag/retrieval-policy.yaml
```

The validator checks:
- All required fields present
- `project_collection` naming pattern valid
- All `wiki_collections` naming patterns valid
- No forbidden collection names used
- `allowed_wiki_domains` entries exist in registry

## Starter template

See `templates/retrieval-policy.yaml`.

## Related

- [schemas/retrieval-policy.schema.yaml](../../schemas/retrieval-policy.schema.yaml)
- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [qdrant-query-filter-contract.md](qdrant-query-filter-contract.md)
