# Prompt 06 — Post-Index Retrieval Validation

**Purpose:** Validate that retrieval from indexed collections respects the project's policy.
Run test queries. Verify citation completeness. Confirm no forbidden collections queried.

**Parameters:**

```
PROJECT_ROOT:    <PROJECT_ROOT>    # e.g. "/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability"
PROJECT_SLUG:    <PROJECT_SLUG>    # e.g. "vocus_profitability"
DOMAIN:          <domain_slug>     # e.g. "nbn"  (the domain just indexed)
COLLECTION:      rag__wiki_<domain_slug>
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Pre-flight

```bash
# Load the retrieval policy
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
info = client.get_collection('rag__wiki_<domain_slug>')
print(f'Vectors count: {info.vectors_count}')
if info.vectors_count == 0:
    print('FAIL: collection is empty — indexing may have failed')
else:
    print('PASS: collection has content')
"
```

---

## Test queries

Run at least 3 test queries relevant to the domain content. For each query:
1. Emit the query text
2. Show the top 3 results with: `source_file`, `heading`, `section_path`, `collection`, `authority`
3. Verify all results come from `rag__wiki_<domain_slug>` (or the project collection if applicable)
4. Verify no result comes from a forbidden collection

```python
from qdrant_client import QdrantClient
from rag_tools.embeddings import get_embedding_model

client = QdrantClient(host='localhost', port=6333)
model = get_embedding_model()

test_queries = [
    "<query-1-relevant-to-this-domain>",
    "<query-2-relevant-to-this-domain>",
    "<query-3-edge-case-or-boundary>",
]

for query in test_queries:
    print(f"\nQuery: {query!r}")
    vector = model.encode(query).tolist()
    results = client.search(
        collection_name="rag__wiki_<domain_slug>",
        query_vector=vector,
        query_filter={
            "must": [{"key": "wiki_domain", "match": {"value": "<domain_slug>"}}]
        },
        limit=3,
        with_payload=True,
    )
    if not results:
        print("  WARN: no results returned")
        continue
    for r in results:
        p = r.payload or {}
        print(f"  score={r.score:.3f}")
        print(f"  collection:   {p.get('collection', 'MISSING')}")
        print(f"  source_file:  {p.get('source_file', 'MISSING')}")
        print(f"  heading:      {p.get('heading', 'MISSING')}")
        print(f"  section_path: {p.get('section_path', 'MISSING')}")
        print(f"  authority:    {p.get('authority', 'MISSING')}")
        # Check no forbidden collections
        if p.get('collection') in ['default', 'documents', 'knowledge', 'rag__all', 'rag__wiki_all', 'rag__global_all_docs']:
            print("  FAIL: result from FORBIDDEN collection!")
```

---

## Isolation check

Verify the project policy's `required_filters` are being applied:

```python
# Verify wiki_domain filter works
results_filtered = client.search(
    collection_name="rag__wiki_<domain_slug>",
    query_vector=vector,
    query_filter={
        "must": [{"key": "wiki_domain", "match": {"value": "WRONG_DOMAIN"}}]
    },
    limit=3,
)
print(f"Filter test (wrong domain): {len(results_filtered)} results (expected: 0)")
```

---

## Insufficient evidence behaviour

Run a query that should NOT match the domain:

```python
vector_unrelated = model.encode("completely unrelated topic outside domain scope").tolist()
results_unrelated = client.search(
    collection_name="rag__wiki_<domain_slug>",
    query_vector=vector_unrelated,
    limit=3,
)
if results_unrelated:
    top_score = results_unrelated[0].score
    print(f"Unrelated query: top score = {top_score:.3f}")
    if top_score > 0.7:
        print("WARN: high-score match on unrelated query — may indicate noisy collection")
    else:
        print("OK: low score on unrelated query (expected)")
else:
    print("OK: no match on unrelated query")
```

Agents should say "insufficient evidence found in declared sources" when scores are low — not hallucinate answers.

---

## Output format

```
Verdict: RETRIEVAL_VALIDATED | RETRIEVAL_PARTIAL | RETRIEVAL_NOT_READY

Collection:  rag__wiki_<domain_slug>
Vectors:     <count>

Query 1: <text>
  Results: <count>  Top score: <score>
  Citation complete: PASS | FAIL (missing: source_file / heading / section_path / collection)
  Collection correct: PASS | FAIL

Query 2: <text>
  (same format)

Query 3: <text>
  (same format)

Filter isolation: PASS | FAIL
Forbidden collections in results: <list or "none">
Insufficient-evidence handling: PASS | WARN

Checks passed:  <list>
Checks failed:  <list or "none">

Next prompt: 08-index-project-documents.md  (if project doc indexing is needed)
             Done — retrieval validated
```
