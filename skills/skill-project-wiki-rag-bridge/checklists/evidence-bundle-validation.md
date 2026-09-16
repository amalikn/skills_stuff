# Checklist: Evidence Bundle Validation

**Use when:** reviewing retrieval results before passing them to an LLM for answer generation,
or auditing whether a rag-tools retrieval command produced valid evidence.

All items marked BLOCKING must pass before the evidence is used in an answer.

---

## Required fields present

- [ ] BLOCKING: `source_file` is present and is an absolute path to a real file (not a
  Qdrant collection name, not a relative path, not a URL)
- [ ] BLOCKING: `excerpt` is present and non-empty
- [ ] BLOCKING: `retrieval_mode` is present and is one of the allowed values
- [ ] BLOCKING: `query` is present and matches the original query

---

## Source grounding

- [ ] BLOCKING: `excerpt` is verbatim text from the source file — no generated conclusions
- [ ] BLOCKING: `excerpt` contains no invented amounts, dates, identifiers, or clause text
  that cannot be verified in the source
- [ ] BLOCKING: `source_file` points to the canonical authoritative source (not a derived
  wiki article when the project source is available)
- [ ] BLOCKING: If `retrieval_mode` is `vector_rag`, the `source_file` is cited (not the
  Qdrant collection name)

---

## Heading or section location present

- [ ] BLOCKING (for structured/section/table modes): At least one of the following is present:
  `section_id`, `heading`, `section_path` (non-empty), or `table_id`
- [ ] WARN: For `vector_rag` mode, `heading` or `section_path` may be absent — acceptable,
  but should be present if the source supports it
- [ ] WARN: For `keyword_lookup` mode, `section_id` and `heading` may be absent — acceptable

---

## Citation usable by LLM

- [ ] BLOCKING: A citation can be constructed from the bundle that includes at minimum:
  `source_file` + one of (`section_id`, `heading`, `table_id`)
- [ ] WARN: If only `source_file` is present (no section/heading/table), the citation is
  file-level only — acceptable but imprecise; note in answer
- [ ] BLOCKING: `document_id` matches the file stem of `source_file` when both are present

---

## Context chars calculated

- [ ] BLOCKING: `context_chars` equals `len(excerpt)` (or 0 if excerpt is empty)
- [ ] WARN: `context_chars` of 0 with no `retrieval_warnings` is suspicious — should have
  a warning like "no matching content found"

---

## Warnings populated when needed

- [ ] BLOCKING: `retrieval_warnings` is populated (not missing) for any of these conditions:
  - source file was missing at retrieval time
  - retrieval fell back from primary to secondary mode
  - RAG score < 0.5
  - structured lookup found no exact section ID match
  - table match is header-only with no row match
  - `fallback_needed: true` in benchmark result
- [ ] WARN: An empty `retrieval_warnings` list is valid when retrieval succeeded cleanly

---

## No generated conclusions inside evidence

- [ ] BLOCKING: `excerpt` does not contain LLM-synthesized text (i.e. text that was not in
  the source file)
- [ ] BLOCKING: `excerpt` does not start with phrases like "Based on...", "This suggests...",
  "According to the data..." — these are LLM answer patterns, not source excerpts
- [ ] BLOCKING: Amounts, percentages, dates, and identifiers in `excerpt` must appear verbatim
  in the source file at `source_file`

---

## Verdict

```
EVIDENCE_VALID       — all BLOCKING checks pass; bundle may be used for answer generation
EVIDENCE_PARTIAL     — WARN items unresolved; usable with explicit caveats in the answer
EVIDENCE_INVALID     — one or more BLOCKING checks fail; do not answer from this bundle;
                       report RETRIEVAL_NOT_READY
```

**When EVIDENCE_INVALID:** report the specific blocking failure, state "not found in retrieved
evidence" for any fact that depends on the failed bundle, and do not substitute training knowledge.
