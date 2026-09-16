---
title: Qdrant Query Filter Contract
status: accepted
date: 20260524
provenance: docs/authority-model.md, docs/multi-project-model.md, SKILL.md
---

# Qdrant Query Filter Contract

## Purpose

Every Qdrant query in the RAG bridge must include a metadata filter to enforce isolation. Unfiltered queries are policy violations even if they return correct results — the isolation guarantee depends on the filter being present, not on Qdrant's access controls.

## Required filters by collection type

### Project collection query

```python
# Collection: rag__project_<slug>
filter = {
    "must": [
        {"key": "project_slug", "match": {"value": "<project_slug>"}}
    ]
}
```

### Wiki domain collection query

```python
# Collection: rag__wiki_<domain>
filter = {
    "must": [
        {"key": "wiki_domain", "match": {"value": "<domain_slug>"}}
    ]
}
```

## Required citation metadata

Every result returned to an agent must carry:

| Field | Description | Required |
|---|---|---|
| `source_file` | Absolute or repo-relative path to the indexed markdown file | Yes |
| `section_path` | Heading path within the file (e.g. `## Authority > Rule 1`) | Yes |
| `collection` | Name of the Qdrant collection the result came from | Yes |
| `authority` | Authority label (`shared_reference_authoritative_markdown`, `project_local`, etc.) | Yes |
| `wiki_domain` | Domain slug (wiki collections only) | Conditional |
| `project_slug` | Project slug (project collections only) | Conditional |

## Multi-collection query pattern

When a project declares multiple wiki domains, query each separately and merge results:

```python
# Correct — separate queries per collection
for domain in allowed_wiki_domains:
    collection = f"rag__wiki_{domain}"
    results = client.search(collection, query_vector, query_filter={
        "must": [{"key": "wiki_domain", "match": {"value": domain}}]
    })

# Wrong — single global search across all collections
# client.search("rag__all", ...) — FORBIDDEN
```

## Validation

Before returning results to an agent:

1. Confirm filter was applied (not None or empty)
2. Confirm collection name matches naming convention
3. Confirm all results include `source_file`, `section_path`, `collection`, `authority`
4. Confirm no results from collections not in `allowed_wiki_domains` or `project_collection`

## Related

- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
- [retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
