# <Project Name> Wiki Bridge

## Purpose

Defines how this project may query the shared Karpathy-style LLM wiki at `/Volumes/Data/_ai/_wiki`
without blindly searching all wiki content or mixing unrelated domains.

This is a policy document only — no indexing or Qdrant collections are created here.

## What this bridge allows

- Querying declared wiki domains (see table below) for shared reference knowledge.
- Searching project-local files, reports, and analysis as the first retrieval step.
- Using the project Qdrant collection `rag__project_<project_slug>` as a secondary local layer.

## What this bridge forbids

- Global wiki search across all domains or all content.
- Querying wiki domains not declared in `rag/project-context.yaml`.
- Using global collection names: `rag__global_all_docs`, `rag__wiki_all`, `default`, `documents`, `knowledge`, `main`.
- Moving project documents into shared wiki collections.
- Moving wiki documents into the project collection without explicit source attribution.
- Treating nav YAML as authoritative source text.

## Allowed wiki domains

| Domain | Collection | Use |
|---|---|---|
| `<domain>` | `rag__wiki_<domain>` | <What this domain provides for this project> |

## Retrieval order

1. Project-local files (reports, manifests, communications, analysis)
2. Project Qdrant collection (`rag__project_<project_slug>`)
3. Declared wiki domain collections (listed above)
4. Ask user if insufficient evidence found in steps 1–3

## Authority rules

- Project-specific facts come from this project's local files.
- Shared reference facts come from the declared wiki domains.
- Nav YAML is routing metadata only — not authoritative source text.

## Collection policy

Every query must include:
- Project identity filter: `project_slug: <project_slug>`
- Wiki domain filter when querying wiki collections: `wiki_domain: <domain>`

Every result must cite:
- Source file
- Section path
- Heading
- Document ID
- Collection name

## How to add another wiki domain safely

1. Confirm the domain exists under `_wiki/wiki_stuff/domains/<domain>/`.
2. Confirm the domain is registered in `_wiki/wiki-data/domain-registry.yaml`.
3. Confirm the Qdrant collection `rag__wiki_<domain>` exists and is indexed (or plan to index it).
4. Add the domain to `rag/project-context.yaml` and `rag/retrieval-policy.yaml`.
5. Update this document.
6. Re-run `rag-tools validate-policy rag/retrieval-policy.yaml`.
