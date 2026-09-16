---
title: wiki-domain-registry.yaml Contract
status: accepted
date: 20260524
provenance: schemas/wiki-domain-registry.schema.yaml, docs/collection-naming-policy.md
---

# wiki-domain-registry.yaml Contract

## Purpose

`domain-registry.yaml` is the canonical registry of all wiki domains. It lives at `/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml`. Every valid wiki domain must be declared here before it can be referenced in any project's `retrieval-policy.yaml` or indexed into Qdrant.

## Required top-level keys

| Key | Type | Constraint |
|---|---|---|
| `version` | integer | Must be `1` |
| `wiki_root` | string | Must be `/Volumes/Data/_ai/_wiki` |
| `content_root` | string | Must be `/Volumes/Data/_ai/_wiki/wiki_stuff` |
| `domains` | list of objects | Each entry declares one wiki domain |
| `rules` | object | All four isolation rule flags must be present and `true` |

## rules object — all keys mandatory and must be true

| Key | Value |
|---|---|
| `disallow_global_collection` | `true` |
| `require_declared_domain` | `true` |
| `require_source_path` | `true` |
| `require_collection_per_domain` | `true` |

## domains list item required keys

| Key | Pattern | Notes |
|---|---|---|
| `domain` | lowercase string | Domain name, e.g. `nbn` |
| `slug` | `^[a-z0-9_]+$` | Used in collection names and filter values — usually matches `domain` |
| `description` | free string | Required — what knowledge this domain contains |
| `source_paths` | list of strings | Paths relative to `content_root`, e.g. `['domains/nbn']` |
| `qdrant_collection` | `^rag__wiki_[a-z0-9_]+$` | Must be `rag__wiki_<slug>` — one collection per domain |
| `status` | `active`, `draft`, `deprecated` | Only `active` domains are eligible for indexing |

## Domain status rules

- `active` — eligible for indexing and project declaration
- `draft` — not yet ready for indexing; may be declared but should not be queried
- `deprecated` — must not be queried by projects unless explicitly grandfathered

## Common failures

| Failure | Fix |
|---|---|
| `slug` and `qdrant_collection` suffix mismatch (e.g. `slug=nbn` but `collection=rag__wiki_nbn_v2`) | Fix collection to exactly match `rag__wiki_<slug>` |
| `status: active` but `source_paths` directory doesn't exist | Create the directory or set status to `draft` |
| `qdrant_collection: rag__wiki_all` | Forbidden global name — fix to `rag__wiki_<slug>` |
| Domain entry with no `description` | Add a description — required for human review and agent understanding |
| Adding a domain without updating wiki `index.md` and `log.md` | Update both files as part of domain creation (see prompt 01) |

## Modification rules

- Never modify existing domain entries without explicit operator authorization
- New domains are appended — do not reorder existing entries
- Slug must be globally unique across all domains
- `source_paths` must exist as directories under `wiki_stuff/` before indexing
- Deprecated domains keep their entries — do not delete them (projects may still reference them in history)

## Validation

```python
import yaml
with open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)

for d in reg['domains']:
    slug = d['slug']
    expected_col = f"rag__wiki_{slug}"
    assert d['qdrant_collection'] == expected_col, f"FAIL: {slug} collection mismatch"
    assert d['description'], f"FAIL: {slug} missing description"
    assert d['source_paths'], f"FAIL: {slug} missing source_paths"
print("PASS: all domain entries valid")
```

## Related

- [schemas/wiki-domain-registry.schema.yaml](../../schemas/wiki-domain-registry.schema.yaml)
- [prompts/01-create-wiki-domain.md](../../prompts/01-create-wiki-domain.md)
- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [specs/retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
