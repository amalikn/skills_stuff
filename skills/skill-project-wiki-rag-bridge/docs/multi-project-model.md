# Multi-Project Model

## How multiple projects share the wiki without polluting each other

```text
                         _wiki/wiki_stuff/domains/
                         ┌──────────┬──────────┬──────────┐
                         │  nbn/    │  vocus/  │  mcp/    │
                         └────┬─────┴────┬─────┴──────────┘
                              │           │
              ┌───────────────┤           ├────────────────┐
              │               │           │                │
              ▼               ▼           ▼                ▼
    Project A             Project B             Project C
    (declares nbn)        (declares nbn         (declares mcp)
                           + vocus)
              │               │                            │
              ▼               ▼                            ▼
    rag__project_A      rag__project_B             rag__project_C
    rag__wiki_nbn  ←────rag__wiki_nbn              rag__wiki_mcp
    (own copy of        (same shared               (own project col)
    project docs)        wiki collection)
```

### Key principle

Wiki domain collections are **shared indexes** over the same markdown source.
Project collections are **strictly isolated** — one per project, filtered by `project_slug`.

---

## Isolation mechanisms

### 1. Declaration gate

A project can only access wiki domains it has explicitly declared in `retrieval-policy.yaml`.
Undeclared domains are forbidden — even if the collection exists in Qdrant.

```yaml
# Project B — declares both nbn and vocus
allowed_wiki_domains:
  - "nbn"
  - "vocus"

# Project A — declares only nbn
allowed_wiki_domains:
  - "nbn"
# Project A cannot query rag__wiki_vocus even though it exists
```

### 2. Filter gate

Every query to a wiki collection must include a `wiki_domain` filter.
Every query to a project collection must include a `project_slug` filter.
Unfiltered queries are policy violations — even if the collection allows them technically.

### 3. Collection-per-project

No two projects share a project collection. If Project A accidentally indexes to
`rag__project_B`, that is a policy violation requiring immediate cleanup.

### 4. No cross-project fallback

A project must not fall back to another project's collection if its own collection returns
nothing. The correct fallback is to ask the user.

---

## Adding a new project

1. Assign a unique `project_slug` (check against all existing project slugs).
2. Run prompt/03 to create bridge files — `rag__project_<slug>` will be the isolated collection.
3. Declare only the wiki domains actually needed. Start with the minimum.
4. Run prompt/04 to validate policy — ensure no name collision with existing collections.
5. Check `checklists/multi-project-isolation.md` against all existing projects.

---

## What happens when a wiki domain gains new content

New articles indexed into `rag__wiki_nbn` are immediately available to all projects that
declare `nbn` as an allowed domain. No per-project re-indexing is needed.

This is the value of the shared wiki model — curated shared knowledge propagates automatically.

---

## What is NOT shared

| Not shared | Why |
|---|---|
| `rag__project_<slug>` | Strictly per-project |
| Project-local source files | Live only in the project repo |
| Project-specific interpretations | Stored in project collection only |
| Sensitive/raw project data | Never indexed into any shared layer |

---

## Audit: checking isolation holds

```bash
# List all collections and check naming
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Verify no forbidden global collections
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
forbidden = {'default','documents','knowledge','main','rag__all','rag__wiki_all','rag__global_all_docs'}
cols = [c.name for c in client.get_collections().collections]
hits = [c for c in cols if c in forbidden]
print('FAIL: forbidden collections found:', hits) if hits else print('PASS: no forbidden collections')
"
```
