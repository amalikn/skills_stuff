---
title: Post-Index Retrieval Validation Guide
status: accepted
date: 20260524
provenance: prompts/06-post-index-retrieval-validation.md, checklists/retrieval-validation.md
---

# Post-Index Retrieval Validation Guide

Run after every indexing operation to confirm retrieval respects the project's policy. This guide validates: collection is non-empty, queries return results from declared collections only, citation metadata is complete, isolation filters work, and the system handles insufficient evidence correctly.

## Contents

- [Prerequisites](#prerequisites)
- [Step 1 — Pre-flight checks](#step-1--pre-flight-checks)
- [Step 2 — Run test queries](#step-2--run-test-queries)
- [Step 3 — Isolation check](#step-3--isolation-check)
- [Step 4 — Insufficient evidence behaviour](#step-4--insufficient-evidence-behaviour)
- [Step 5 — Forbidden collection audit](#step-5--forbidden-collection-audit)
- [Verdict output](#verdict-output)
- [Failure responses](#failure-responses)

## Prerequisites

- Indexing step completed for the target domain or project collection
- Qdrant running at `localhost:6333`
- rag-tools venv active: `tools-working-cache/rag-tools/.venv`
- Project's `retrieval-policy.yaml` available

## Step 1 — Pre-flight checks

```bash
# Load and display the retrieval policy
python3 -c "
import yaml
with open('<PROJECT_ROOT>/rag/retrieval-policy.yaml') as f:
    policy = yaml.safe_load(f)
print('Allowed wiki collections:', policy.get('allowed_wiki_collections'))
print('Forbidden:', policy.get('forbidden_collections'))
"

# Verify collection is non-empty
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_<DOMAIN_SLUG>')
print(f'Vectors count: {info.vectors_count}')
print('PASS' if info.vectors_count > 0 else 'FAIL: collection empty — indexing may have failed')
"
```

If collection is empty: stop and investigate (see `guides/failure-mode-reference.md` FM-01/FM-02).

## Step 2 — Run test queries

Run at least 3 test queries relevant to the domain content. For each result verify:
- `source_file` present and correct
- `heading` present
- `section_path` present
- `collection` matches expected `rag__wiki_<DOMAIN_SLUG>`
- `authority` is `shared_reference_authoritative_markdown`
- Result is NOT from a forbidden collection

```python
from qdrant_client import QdrantClient
from rag_tools.embeddings import get_embedding_model

client = QdrantClient(host='localhost', port=6333)
model = get_embedding_model()

FORBIDDEN = {'default', 'documents', 'knowledge', 'rag__all', 'rag__wiki_all', 'rag__global_all_docs'}
REQUIRED_FIELDS = {'source_file', 'heading', 'section_path', 'collection', 'authority'}

test_queries = [
    "<query-1-relevant-to-domain>",
    "<query-2-relevant-to-domain>",
    "<query-3-edge-case-or-boundary>",
]

for query in test_queries:
    vector = model.encode(query).tolist()
    results = client.search(
        collection_name="rag__wiki_<DOMAIN_SLUG>",
        query_vector=vector,
        query_filter={"must": [{"key": "wiki_domain", "match": {"value": "<DOMAIN_SLUG>"}}]},
        limit=3,
        with_payload=True,
    )
    for r in results:
        p = r.payload or {}
        missing = REQUIRED_FIELDS - set(p.keys())
        if missing:
            print(f"FAIL: missing citation fields: {missing}")
        if p.get('collection') in FORBIDDEN:
            print(f"FAIL: result from forbidden collection: {p.get('collection')}")
```

**Pass criteria:** All results have complete citation fields. No results from forbidden collections.

## Step 3 — Isolation check

Verify the `wiki_domain` filter correctly excludes wrong-domain results:

```python
# This should return 0 results
results_wrong = client.search(
    collection_name="rag__wiki_<DOMAIN_SLUG>",
    query_vector=vector,
    query_filter={"must": [{"key": "wiki_domain", "match": {"value": "WRONG_DOMAIN_TEST"}}]},
    limit=3,
)
print(f"Filter isolation: {'PASS' if len(results_wrong) == 0 else 'FAIL'} ({len(results_wrong)} results with wrong domain filter)")
```

**Pass criteria:** 0 results when filtering by a non-existent domain.

## Step 4 — Insufficient evidence behaviour

Run a query clearly outside the domain's scope:

```python
vector_unrelated = model.encode("completely unrelated topic outside domain scope").tolist()
results_unrelated = client.search(
    collection_name="rag__wiki_<DOMAIN_SLUG>",
    query_vector=vector_unrelated,
    limit=3,
)
if results_unrelated:
    top_score = results_unrelated[0].score
    if top_score > 0.7:
        print(f"WARN: high-score match ({top_score:.3f}) on unrelated query — collection may be noisy")
    else:
        print(f"OK: low score ({top_score:.3f}) on unrelated query (expected)")
else:
    print("OK: no match on unrelated query (expected)")
```

**Agent behaviour contract:** When scores are low (< 0.4), agents must say "insufficient evidence found in declared sources" — not speculate or blend sources.

## Step 5 — Forbidden collection audit

Verify no forbidden collections exist in Qdrant:

```python
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
FORBIDDEN = {'default', 'documents', 'knowledge', 'main', 'rag__all', 'rag__wiki_all', 'rag__global_all_docs'}
cols = [c.name for c in client.get_collections().collections]
hits = [c for c in cols if c in FORBIDDEN]
print('FAIL: forbidden collections found:', hits) if hits else print('PASS: no forbidden collections')
```

## Verdict output

```
Verdict: RETRIEVAL_VALIDATED | RETRIEVAL_PARTIAL | RETRIEVAL_NOT_READY

Collection:  rag__wiki_<DOMAIN_SLUG>
Vectors:     <count>

Query 1: <text>
  Results: <count>  Top score: <score>
  Citation complete: PASS | FAIL (missing: <fields>)
  Collection correct: PASS | FAIL

Query 2: <text>  (same format)
Query 3: <text>  (same format)

Filter isolation: PASS | FAIL
Forbidden collections in results: <list or "none">
Insufficient-evidence handling: PASS | WARN

Checks passed:  <list>
Checks failed:  <list or "none">
```

- `RETRIEVAL_VALIDATED` — all queries returned correct results, all citations complete, isolation confirmed
- `RETRIEVAL_PARTIAL` — some queries returned results but citation fields missing or scores low
- `RETRIEVAL_NOT_READY` — collection empty, isolation failed, or forbidden collections found

## Failure responses

| Failure | Guide |
|---|---|
| Collection empty | `guides/failure-mode-reference.md` FM-01/FM-02 |
| Citations missing fields | Re-index with correct metadata — check rag-tools indexer config |
| Filter isolation failure | Re-index with correct `wiki_domain` metadata on all chunks |
| Forbidden collection found | Delete it, re-index with correct name per ADR-001 |
| High score on unrelated query | Review and cull domain content — collection may have off-topic material |

## Related

- [prompts/06-post-index-retrieval-validation.md](../../prompts/06-post-index-retrieval-validation.md)
- [checklists/retrieval-validation.md](../../checklists/retrieval-validation.md)
- [guides/failure-mode-reference.md](failure-mode-reference.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
