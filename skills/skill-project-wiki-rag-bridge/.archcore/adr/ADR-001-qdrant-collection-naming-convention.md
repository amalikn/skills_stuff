---
id: ADR-001
title: Qdrant Collection Naming Convention
status: accepted
date: 20260524
provenance: docs/collection-naming-policy.md, SKILL.md
---

# ADR-001 — Qdrant Collection Naming Convention

## Status

Accepted

## Context

Qdrant has no built-in multi-tenancy. Collections can be created with any name, and without a naming policy, agents or operators could accidentally create global or ambiguous collections that mix project and wiki data. Silent naming violations would break retrieval isolation without raising errors.

## Decision

All collections in the wiki/project RAG bridge follow a three-prefix naming scheme:

| Pattern | Usage |
|---|---|
| `rag__project_<project_slug>` | Per-project document index |
| `rag__wiki_<domain_slug>` | Per-wiki-domain shared index |
| `rag__test_<purpose>_<yyyymmdd>` | Ephemeral test collections only |

**Constraints:**
- `<project_slug>` and `<domain_slug>` must be lowercase alphanumeric + underscores only (no hyphens, spaces, uppercase)
- `<project_slug>` must match the `project_slug` field in `retrieval-policy.yaml`
- `<domain_slug>` must match the `slug` field in `domain-registry.yaml`
- Test collections must have a date suffix and be deleted after use

**Forbidden names (must never exist in production):**

`rag__global_all_docs`, `rag__wiki_all`, `rag__all`, `default`, `documents`, `knowledge`, `main`, `wiki`, `test` (bare)

## Consequences

- Every collection is immediately identifiable as wiki, project, or test by name alone
- Naming violations are detectable via regex: `^rag__(project|wiki|test)_[a-z0-9_]+$`
- `rag-tools validate-policy` enforces the forbidden list on policy files
- Agents must refuse to create collections outside this pattern

## Validation pattern

```python
import re
ALLOWED = re.compile(r'^rag__(project|wiki|test)_[a-z0-9_]+$')
FORBIDDEN = {
    'rag__global_all_docs', 'rag__wiki_all', 'rag__all',
    'default', 'documents', 'knowledge', 'main',
}
def validate_collection_name(name: str) -> bool:
    return bool(ALLOWED.match(name)) and name not in FORBIDDEN
```

## Related

- [docs/collection-naming-policy.md](../../docs/collection-naming-policy.md)
- [ADR-002-multi-project-isolation-model.md](ADR-002-multi-project-isolation-model.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
