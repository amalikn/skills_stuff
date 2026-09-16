---
title: Retrieval Isolation Rules
status: accepted
date: 20260524
provenance: SKILL.md, docs/authority-model.md, docs/multi-project-model.md, AGENTS.md
---

# Retrieval Isolation Rules

These rules govern agent and operator behaviour in the wiki/project RAG bridge. All rules are blocking — violation requires refusal or immediate stop, not a warning.

## Contents

- [Collection naming rules](#collection-naming-rules)
- [Query isolation rules](#query-isolation-rules)
- [Indexing rules](#indexing-rules)
- [Data segregation rules](#data-segregation-rules)
- [Embedding rules](#embedding-rules)
- [Agent refusal rules](#agent-refusal-rules)

## Collection naming rules

- **RULE-N1:** All project collections must be named `rag__project_<project_slug>`. No exceptions.
- **RULE-N2:** All wiki domain collections must be named `rag__wiki_<domain_slug>`. No exceptions.
- **RULE-N3:** Test collections must use `rag__test_<purpose>_<yyyymmdd>` and be deleted after use.
- **RULE-N4:** Forbidden collection names (`rag__global_all_docs`, `rag__wiki_all`, `rag__all`, `default`, `documents`, `knowledge`, `main`, `wiki`, `test`) must never exist in production. Any found must be deleted.
- **RULE-N5:** `<project_slug>` must be lowercase alphanumeric + underscores only. No hyphens, spaces, uppercase.
- **RULE-N6:** `<project_slug>` must match `project_slug` in `retrieval-policy.yaml`. Mismatches are policy violations.

## Query isolation rules

- **RULE-Q1:** A project may only query wiki domains declared in its `retrieval-policy.yaml` under `allowed_wiki_domains`. Undeclared domains are forbidden.
- **RULE-Q2:** Every query to a wiki collection must include a `wiki_domain` filter matching the domain slug. Unfiltered wiki queries are policy violations.
- **RULE-Q3:** Every query to a project collection must include a `project_slug` filter. Unfiltered project queries are policy violations.
- **RULE-Q4:** No project may query another project's `rag__project_*` collection. Cross-project fallback is forbidden.
- **RULE-Q5:** If a project's collection returns no results, the agent must ask the user — not fall back to another project or to a global search.

## Indexing rules

- **RULE-I1:** Always run `rag-index-domain-dry` (dry-run) before any live indexing operation. Do not skip.
- **RULE-I2:** Index exactly one wiki domain per operation. Multi-domain batching in a single run is forbidden.
- **RULE-I3:** Do not index raw or sensitive project data into wiki collections (`rag__wiki_*`).
- **RULE-I4:** Verify chunk count from dry-run matches vectors_count after live indexing. Mismatch indicates FM-02 (silent failure).
- **RULE-I5:** Work through `checklists/indexing-readiness.md` as a blocking gate before running any indexing operation.

## Data segregation rules

- **RULE-D1:** Project-specific facts belong in project-local files and `rag__project_<slug>`. They must not enter wiki collections.
- **RULE-D2:** Shared reference facts belong in wiki markdown (`_wiki/wiki_stuff/domains/<domain>/`) and `rag__wiki_<domain>`.
- **RULE-D3:** Qdrant payloads are retrieval artefacts only. When citing, always cite the source file — not the Qdrant payload.
- **RULE-D4:** Every indexed chunk must carry `authority` metadata: `shared_reference_authoritative_markdown`, `project_local`, `project_generated`, or `routing_metadata_only`.

## Embedding rules

- **RULE-E1:** The embedding model is locked to `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **RULE-E2:** Collections indexed with different models must not be queried together. Model mismatch silently degrades retrieval quality.
- **RULE-E3:** When re-indexing a collection after a model change, delete the old collection first — do not append to it.

## Agent refusal rules

- **RULE-R1:** Refuse any request for unrestricted global wiki search. Explain why isolation is required.
- **RULE-R2:** Refuse any request to bypass `retrieval-policy.yaml` or Qdrant isolation rules.
- **RULE-R3:** Refuse to create collections with forbidden names. Propose the correct name instead.
- **RULE-R4:** Refuse to run live indexing without a prior dry-run confirmation from the operator.
- **RULE-R5:** Refuse to skip checklist gates. State which checklist gate applies before proceeding.

## Related

- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
