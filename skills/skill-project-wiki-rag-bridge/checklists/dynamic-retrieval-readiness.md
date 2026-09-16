# Checklist: Dynamic Retrieval Readiness

**Use before:** attempting any rag-tools dynamic retrieval command (profile-file,
recommend-strategy, structured-lookup, lookup-section, lookup-table, benchmark-file).

All items marked BLOCKING must pass. WARN items should be resolved before production use.

---

## rag-tools dynamic commands available

- [ ] BLOCKING: rag-tools venv exists at `tools-working-cache/rag-tools/.venv`
- [ ] BLOCKING: `rag-tools --help` runs without error
- [ ] BLOCKING: `rag-tools profile-file --help` is listed (dynamic retrieval layer present)
- [ ] BLOCKING: `rag-tools recommend-strategy --help` is listed
- [ ] BLOCKING: `rag-tools structured-lookup --help` is listed
- [ ] BLOCKING: `rag-tools lookup-section --help` is listed
- [ ] BLOCKING: `rag-tools lookup-table --help` is listed
- [ ] BLOCKING: `rag-tools benchmark-file --help` is listed

Verify with:

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin
$VENV/rag-tools --help | grep -E "profile|recommend|structured|lookup|benchmark"
```

Expected output includes: `profile-file`, `profile-project`, `recommend-strategy`,
`structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`.

---

## EvidenceBundle model available

- [ ] BLOCKING: `from rag_tools.evidence import EvidenceBundle` imports without error
- [ ] BLOCKING: EvidenceBundle has required fields: `query`, `retrieval_mode`, `source_file`,
  `excerpt`, `retrieval_warnings`

Verify with:

```bash
$VENV/python -c "
from rag_tools.evidence import EvidenceBundle
b = EvidenceBundle(query='test', retrieval_mode='direct_structured_lookup')
print('OK:', b.model_fields.keys())
"
```

---

## profile-file / profile-project working

- [ ] BLOCKING: `rag-tools profile-file <file>` returns JSON with `document_class` and
  `recommended_retrieval_modes`
- [ ] BLOCKING: `rag-tools profile-project <dir>` returns a list of profile dicts
- [ ] WARN: profile-file on a missing file returns a zero-field profile (not an exception)

---

## recommend-strategy working

- [ ] BLOCKING: `rag-tools recommend-strategy <file>` returns JSON with `primary`, `secondary`,
  `fallback`, `rag_suitability`, and `reason`
- [ ] BLOCKING: `rag_suitability` is one of: `suitable`, `partially_suitable`, `not_suitable`

---

## structured-lookup working

- [ ] BLOCKING: `rag-tools structured-lookup <file> <query>` returns a JSON list of
  EvidenceBundle dicts
- [ ] BLOCKING: Each bundle has `source_file`, `excerpt`, `heading` or `section_id`
- [ ] WARN: Empty list is valid for a query with no match — confirms fallback behavior

---

## lookup-section working

- [ ] BLOCKING: `rag-tools lookup-section <file> <section-id>` returns a JSON list
- [ ] BLOCKING: Result bundle has `section_id` matching the requested ID when found
- [ ] WARN: Missing section returns a bundle with `retrieval_warnings: ["source file missing"]`
  or an empty list — check which your version returns

---

## lookup-table working

- [ ] BLOCKING: `rag-tools lookup-table <file> <query>` returns a JSON list of EvidenceBundle
  dicts for table matches
- [ ] BLOCKING: Each bundle has `table_id` and `row_keys`
- [ ] WARN: Empty list is valid when no table rows match the query terms

---

## benchmark-file working

- [ ] BLOCKING: `rag-tools benchmark-file <file> --queries <query-file>` returns JSON with
  `source_file`, `results`, `recommendation`
- [ ] BLOCKING: `recommendation` is one of the valid route labels:
  `DIRECT_FIRST`, `TABLE_LOOKUP_FIRST`, `HYBRID_DIRECT_FIRST`, `HYBRID_RAG_FIRST`,
  `RAG_FIRST`, `NOT_READY_NEEDS_EXTRACTION`, `NOT_READY_NEEDS_MORE_INDEXED_CONTENT`
- [ ] WARN: Running with `--modes rag` when no Qdrant collection exists results in `pass: false`
  and `fallback_needed: true` for all RAG rows — this is expected, not an error

---

## Project has retrieval-strategy.yaml

- [ ] BLOCKING (for project-side indexing): `rag/retrieval-strategy.yaml` exists in project root
- [ ] BLOCKING: Every candidate document has `document_class` and `rag_suitability` recorded
- [ ] BLOCKING: Every `index_allowed: true` entry has `benchmark_status: passed`
- [ ] WARN: Documents with `document_class: unknown` require manual classification

---

## Answers are evidence-bundle constrained

- [ ] BLOCKING: Agent answers from `excerpt` field only — no training-knowledge fill-in
- [ ] BLOCKING: `retrieval_warnings` are surfaced when present — not silently consumed
- [ ] BLOCKING: `source_file` is cited in every answer
- [ ] WARN: When no bundle is returned, agent reports `RETRIEVAL_NOT_READY` and stops

---

## Verdict

```
DYNAMIC_RETRIEVAL_READY    — all BLOCKING checks pass
DYNAMIC_RETRIEVAL_PARTIAL  — one or more WARN items unresolved; dynamic retrieval usable with care
DYNAMIC_RETRIEVAL_NOT_READY — one or more BLOCKING checks fail; do not use dynamic retrieval
```
