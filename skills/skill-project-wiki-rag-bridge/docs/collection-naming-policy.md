# Collection Naming Policy

This document defines the Qdrant collection naming rules for the wiki/project RAG bridge.
These rules are enforced by `retrieval-policy.yaml`, `rag-tools validate-policy`, and this skill.
Qdrant itself has no naming enforcement — violations are silent without policy enforcement.

---

## Allowed patterns

### Project collections

```
rag__project_<project_slug>
```

- `<project_slug>` must be lowercase alphanumeric + underscores only
- No hyphens, no spaces, no uppercase
- Slug must match `project_slug` in `retrieval-policy.yaml`

Examples:
```
rag__project_vocus_profitability   ✓
rag__project_apn_sip_setup         ✓
rag__project_podbng_lab            ✓
```

### Wiki domain collections

```
rag__wiki_<domain_slug>
```

- `<domain_slug>` must match the `slug` field in `domain-registry.yaml`
- One collection per domain — no exceptions

Examples:
```
rag__wiki_nbn     ✓
rag__wiki_vocus   ✓
rag__wiki_mcp     ✓
```

### Test / ephemeral collections

```
rag__test_<purpose>_<yyyymmdd>
```

- Used for unit tests and one-off validation only
- Must be deleted after use or given a date suffix to signal ephemerality
- Never used in production retrieval policy

Examples:
```
rag__test_policy_20260524   ✓
rag__test_embeddings_20260601  ✓
```

---

## Forbidden names

These names are absolutely forbidden. Any collection with these names must be deleted.

| Forbidden name | Why forbidden |
|---|---|
| `rag__global_all_docs` | Implies global/mixed scope |
| `rag__wiki_all` | Implies all-wiki scope |
| `rag__all` | No scoping at all |
| `default` | Qdrant default — no identity |
| `documents` | Generic, no identity |
| `knowledge` | Generic, no identity |
| `main` | Generic, no identity |
| `test` (bare) | No date suffix — could be permanent |
| `wiki` (bare) | No domain scoping |

---

## Naming validation

### In rag-tools

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

### In retrieval-policy.yaml

The `forbidden_collections` key must include all globally forbidden names.
The `rag-tools validate-policy` CLI checks this.

---

## Common mistakes

| Mistake | Correct form |
|---|---|
| `vocus_profitability` (no prefix) | `rag__project_vocus_profitability` |
| `rag__nbn` (missing wiki_ infix) | `rag__wiki_nbn` |
| `rag__project-vocus` (hyphen) | `rag__project_vocus_profitability` |
| `rag__wiki_ALL` (uppercase) | `rag__wiki_all` — and this is also forbidden |
| `rag__test` (no suffix) | `rag__test_purpose_20260524` |
