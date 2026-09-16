# Checklist: Indexing Readiness

**Use before:** running prompt 05 (index-wiki-domain) or 08 (index-project-documents).
All items marked BLOCKING must pass before live indexing. WARN items should be resolved.

---

## Profile and strategy gate

**This section must be checked first. All BLOCKING items here take precedence.**

- [ ] BLOCKING: `profile-file` or `profile-project` has been run on the candidate source(s).
- [ ] BLOCKING: A source profile exists for every candidate document or wiki article being indexed.
- [ ] BLOCKING: `recommend-strategy` has been run on every candidate document.
- [ ] BLOCKING: `rag/retrieval-strategy.yaml` exists in the project root where project-side
  indexing is planned.
- [ ] BLOCKING: Vector RAG is marked `suitable` or `partially_suitable` for every candidate before
  its `index: true` flag is set in the manifest.
- [ ] BLOCKING: For any document classified `structured_markdown_reference`, `financial_rate_card`,
  `invoice_or_billing_report`, or `tabular_dataset`: benchmark has been run (prompt 02c) or
  indexing is explicitly deferred to direct/table lookup.
- [ ] BLOCKING: Direct or table lookup is preferred as primary route where the benchmark shows it
  outperforms vector RAG.
- [ ] BLOCKING: EvidenceBundle output path is documented in `rag/retrieval-strategy.yaml`.
- [ ] WARN: Scaffold-only wiki domain indexing (no body content, no source references) produces
  low-value retrieval — add curated content (prompt 07) before indexing.
- [ ] WARN: Do not duplicate full source files into wiki summaries just to make RAG work. Use
  direct/structured lookup on the authoritative source instead.
- [ ] WARN: If RAG context reduction is needed for a structured source, it is a signal that
  structured lookup is more appropriate than vector RAG for that file.

---

## Domain content (wiki domain indexing)

- [ ] BLOCKING: `wiki_stuff/domains/<domain>/` exists
- [ ] BLOCKING: At least 1 `.md` file in domain directory
- [ ] WARN: `wiki_stuff/domains/<domain>/index.md` exists
- [ ] WARN: Each article has frontmatter with `domain:`, `title:`, `authority:` fields
- [ ] BLOCKING: At least 1 article has a `source:` reference (not scaffold-only)
- [ ] Spot-check: 3 random articles have `## Source references` section with content

## Collection name validity (both domain and project)

- [ ] BLOCKING: Collection name matches `rag__project_<slug>` or `rag__wiki_<domain>`
- [ ] BLOCKING: Collection name is NOT in forbidden list
- [ ] BLOCKING: Collection slug is lowercase alphanumeric + underscores only

## Policy validated

- [ ] BLOCKING: `rag/retrieval-policy.yaml` passes rag-tools validator (prompt 04)
- [ ] BLOCKING: `allowed_wiki_collections` includes the collection being indexed
- [ ] No forbidden collection names in policy

## RAG tools operational

- [ ] BLOCKING: External venv exists at `tools-working-cache/rag-tools/.venv`
- [ ] BLOCKING: `rag_tools.cli doctor` passes or reports PARTIAL with Qdrant-only issues
- [ ] BLOCKING: Qdrant running and reachable on localhost:6333

## Dry-run passed

- [ ] BLOCKING: Dry-run executed before live index
- [ ] BLOCKING: Dry-run chunk count > 0
- [ ] WARN: Dry-run chunk count is not suspiciously high (may indicate cross-domain bleed)
- [ ] BLOCKING: No files from other domains or projects in dry-run output
- [ ] BLOCKING: Collection name shown in dry-run matches target

## Content safety (project documents)

- [ ] BLOCKING: `rules.default_index: false` in project-documents.yaml
- [ ] BLOCKING: No `type: communication` or `type: raw` documents with `index: true` without approval notes
- [ ] BLOCKING: No `sensitive: true` document with `index: true`

---

## Verdict

```
INDEXING_READY    — all BLOCKING checks pass
INDEXING_NOT_READY — one or more BLOCKING checks fail
```

**Do not proceed to live indexing if any BLOCKING check fails.**
