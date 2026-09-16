---
id: ADR-002
title: Multi-Project Isolation Model
status: accepted
date: 20260524
provenance: docs/multi-project-model.md, SKILL.md
---

# ADR-002 — Multi-Project Isolation Model

## Status

Accepted

## Context

Multiple projects need access to shared wiki knowledge (e.g., NBN standards, Vocus rate cards) without polluting each other's data. A naive global search would allow Project A to see Project B's documents, or mix project-specific facts with shared reference knowledge.

## Decision

The isolation model uses four enforcement gates:

**Gate 1 — Declaration gate:** A project may only query wiki domains it has explicitly declared in `retrieval-policy.yaml` under `allowed_wiki_domains`. Undeclared domains are forbidden even if the collection exists in Qdrant.

**Gate 2 — Filter gate:** Every query to a wiki collection must include a `wiki_domain` filter. Every query to a project collection must include a `project_slug` filter. Unfiltered queries are policy violations.

**Gate 3 — Collection-per-project:** No two projects share a project collection. Each project gets exactly one `rag__project_<slug>` collection. Cross-project indexing is a policy violation requiring immediate cleanup.

**Gate 4 — No cross-project fallback:** If a project's own collection returns no results, the correct action is to ask the user — not to fall back to another project's collection.

**Shared wiki model:** Wiki domain collections (`rag__wiki_<domain>`) are shared indexes. All projects declaring a domain query the same collection. New wiki content becomes available to all declaring projects immediately without per-project re-indexing.

## Consequences

- Wiki knowledge propagates to all projects without re-indexing
- Project data never leaks across project boundaries
- `retrieval-policy.yaml` is the single declaration of what a project is allowed to query
- Agents must enforce all four gates; refusing requests that would violate any gate
- `checklists/multi-project-isolation.md` must be run when adding new projects

## Related

- [docs/multi-project-model.md](../../docs/multi-project-model.md)
- [ADR-001-qdrant-collection-naming-convention.md](ADR-001-qdrant-collection-naming-convention.md)
- [specs/retrieval-policy-yaml-contract.md](../specs/retrieval-policy-yaml-contract.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
