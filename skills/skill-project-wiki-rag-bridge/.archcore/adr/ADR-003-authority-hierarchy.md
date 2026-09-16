---
id: ADR-003
title: Source Authority Hierarchy for Retrieval
status: accepted
date: 20260524
provenance: docs/authority-model.md
---

# ADR-003 — Source Authority Hierarchy for Retrieval

## Status

Accepted

## Context

During retrieval, agents may encounter information from multiple sources: project-local files, wiki markdown, Qdrant payloads, generated reports, and routing YAML. Without an explicit authority hierarchy, agents might cite Qdrant payloads as authoritative (they are not — they are search artefacts pointing to source files) or use routing YAML as factual content.

## Decision

The following authority hierarchy is accepted and enforced:

| Priority | Source | Scope |
|---|---|---|
| 1 | Project-local files | Project-specific facts only |
| 2 | Wiki authoritative markdown (`_wiki/wiki_stuff/domains/`) | Shared reference facts only |
| 3 | Qdrant retrieval results | Search results — cite original source, do not treat as canonical |
| 4 | Generated summaries / reports | Secondary — do not override primary sources |
| 5 | Nav YAML (`context-map.yaml`, `project-context.yaml`, etc.) | Routing metadata only — never factual content |

**Conflict resolution:**
- Project-local vs wiki general reference → project-local wins
- Wiki standard vs project interpretation → report conflict, ask user
- Two wiki articles disagree → report conflict, cite both, ask user
- Qdrant result vs source markdown → source markdown wins — re-read the file

**Insufficient evidence rule:** If retrieved evidence is insufficient, agents must say so explicitly. Speculation or source-blending without labelling is forbidden.

## Consequences

- Qdrant payloads must always include citation metadata: `source_file`, `section_path`, `collection`
- Agents must never answer a factual question by citing a routing file
- `authority` metadata field in indexed documents must use standard labels: `shared_reference_authoritative_markdown`, `project_local`, `project_generated`, `routing_metadata_only`
- Conflict reports must name both conflicting files and state resolution intent

## Related

- [docs/authority-model.md](../../docs/authority-model.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
