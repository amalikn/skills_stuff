# Checklist: Retrieval Validation

**Use after:** indexing (prompt 05 or 08).
**Use with:** prompt 06 (post-index-retrieval-validation).

---

## Pre-query setup

- [ ] Collection exists in Qdrant
- [ ] Collection has vectors_count > 0
- [ ] Retrieval policy loaded and confirmed valid
- [ ] Embedding model loaded (same model used for indexing)

## Test queries

Run at least 3 queries. For each:

- [ ] At least 1 result returned (non-empty)
- [ ] Top result score > 0.4 (low scores suggest sparse/mismatched content)
- [ ] All results cite `collection` field
- [ ] All results cite `source_file` field
- [ ] All results cite `heading` field
- [ ] All results cite `section_path` field
- [ ] All results have `authority` field set

## Collection isolation

- [ ] All results come from the correct collection (`rag__wiki_<domain>` or `rag__project_<slug>`)
- [ ] No results from forbidden collections (`default`, `documents`, `rag__all`, etc.)
- [ ] `wiki_domain` filter correctly restricts results to declared domain only
- [ ] `project_slug` filter correctly restricts project collection results

## Filter enforcement

- [ ] Querying with `wiki_domain: WRONG_DOMAIN` returns 0 results
- [ ] Querying without required filters should not be possible (enforced by retrieval policy)

## Insufficient evidence behaviour

- [ ] Query on an unrelated topic returns low score (< 0.4) or no results
- [ ] Agent does NOT hallucinate an answer when no results found
- [ ] Agent explicitly states "insufficient evidence in declared sources" when results are poor
- [ ] Agent does NOT fall back to undeclared domains or global search

## Cross-collection contamination

- [ ] Results from `rag__wiki_nbn` contain only NBN-domain content
- [ ] Results from `rag__wiki_vocus` contain only Vocus-domain content
- [ ] Project collection does not contain wiki content (unless explicitly copied with source)

---

## Verdict

```
RETRIEVAL_VALIDATED    — all checks pass
RETRIEVAL_PARTIAL      — some queries succeed, some return empty or low quality
RETRIEVAL_NOT_READY    — all queries fail or forbidden collections appear in results
```
