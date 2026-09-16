---
title: Failure Mode Reference
status: accepted
date: 20260524
provenance: docs/failure-modes.md
---

# Failure Mode Reference

Quick reference for diagnosing RAG bridge failures. For each failure mode: detection command and fix.

## Contents

- [FM-01 Scaffold-only collection](#fm-01-scaffold-only-collection)
- [FM-02 Silent indexing failure](#fm-02-silent-indexing-failure)
- [FM-03 Policy valid but no retrieval](#fm-03-policy-valid-but-no-retrieval)
- [FM-04 Embedding model mismatch](#fm-04-embedding-model-mismatch)
- [FM-05 Naming violation](#fm-05-naming-violation)
- [FM-06 Cross-project contamination](#fm-06-cross-project-contamination)

## FM-01 Scaffold-only collection

**Symptom:** Collection exists, policy validates, queries return nothing.
**Cause:** `rag-tools index-domain` was never run or exited before indexing.
**Detect:** `client.get_collection('rag__wiki_nbn').vectors_count` returns 0.
**Fix:** Re-run `prompts/05-index-wiki-domain.md`. Verify domain directory has markdown files first.

## FM-02 Silent indexing failure

**Symptom:** Index command appeared to succeed but collection has 0 or very low vector count.
**Cause:** Domain directory had no eligible files, or embedding failed quietly.
**Detect:** Compare dry-run chunk count with actual `vectors_count` after indexing.
**Fix:** Check domain markdown files for frontmatter errors. Run embedding smoke test. Re-dry-run then re-index.

## FM-03 Policy valid but no retrieval

**Symptom:** `rag-tools validate-policy` passes. Qdrant running. Queries return 0 results.
**Cause:** Collection empty (FM-01/FM-02), `wiki_domain` filter excludes all results, or embedding model mismatch.
**Detect:** Check `vectors_count`. Run test query without filter (diagnostic only). Confirm model match.
**Fix:** Depends on cause — see FM-01/FM-02/FM-04.

## FM-04 Embedding model mismatch

**Symptom:** Queries return results but with very low similarity scores (< 0.2).
**Cause:** Collection indexed with one model, queried with another.
**Detect:** Check model metadata on collection vs current rag-tools config.
**Fix:** Delete collection, re-index with correct model (`sentence-transformers/all-MiniLM-L6-v2`). See RULE-E3.

## FM-05 Naming violation

**Symptom:** Collection exists but does not match naming convention.
**Cause:** Manual collection creation or misconfigured template.
**Detect:** `validate_collection_name(name)` returns False.
**Fix:** Delete the non-compliant collection. Re-create and re-index with correct name. See RULE-N1–N6.

## FM-06 Cross-project contamination

**Symptom:** Project queries return results from another project's documents.
**Cause:** Missing `project_slug` filter, or documents indexed without project_slug metadata.
**Detect:** Inspect `source_file` and `project_slug` metadata on returned results.
**Fix:** Delete contaminated collection. Re-index with correct filters. Add `project_slug` metadata to all indexed documents.

## Troubleshooting prompt

See `prompts/09-troubleshoot-rag-bridge.md` for the full interactive diagnostic workflow.

## Related

- [docs/failure-modes.md](../../docs/failure-modes.md)
- [checklists/rag-tools-readiness.md](../../checklists/rag-tools-readiness.md)
- [checklists/retrieval-validation.md](../../checklists/retrieval-validation.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
