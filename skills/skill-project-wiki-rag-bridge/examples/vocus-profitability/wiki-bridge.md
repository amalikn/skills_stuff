# Vocus Profitability — Wiki Bridge

## Purpose

Defines how this project may query the shared Karpathy-style LLM wiki at `/Volumes/Data/_ai/_wiki`
without blindly searching all wiki content or mixing unrelated domains.

This is a policy document only — no indexing or Qdrant collections are created here.

## What this bridge allows

- Querying wiki domain `nbn` (collection `rag__wiki_nbn`) for NBN/WBA/DCR rebate, discount,
  campaign, eligibility, and clawback reference.
- Querying wiki domain `vocus` (collection `rag__wiki_vocus`) for shared Vocus invoice,
  rate-card, billing, and profitability interpretation notes.
- Searching project-local files, reports, and analysis as the first retrieval step.
- Using the project Qdrant collection `rag__project_vocus_profitability` as a secondary local layer.

## What this bridge forbids

- Global wiki search across all domains or all content.
- Querying unrelated domains: `mcp`, `career`, `network_design`, `personal`, or any domain
  not declared in `rag/project-context.yaml`.
- Using global collection names: `rag__global_all_docs`, `rag__wiki_all`, `default`,
  `documents`, `knowledge`, `main`.
- Moving project documents (invoices, CSV, reports) into shared wiki collections.
- Moving wiki documents into the project collection without explicit source attribution.
- Treating nav YAML as authoritative source text.

## Allowed wiki domains

| Domain | Collection | Use |
|---|---|---|
| `nbn` | `rag__wiki_nbn` | NBN WBA/DCR pricing, rebates, credits, campaign terms, eligibility, exclusions, clawbacks |
| `vocus` | `rag__wiki_vocus` | Vocus invoice/rate-card interpretation, billing mechanics, product mapping, rebate passthrough |

## Retrieval order

1. Project-local files (reports, manifests, communications, analysis)
2. Project Qdrant collection (`rag__project_vocus_profitability`)
3. Declared wiki domain collections (`rag__wiki_nbn`, `rag__wiki_vocus`)
4. Ask user if insufficient evidence found in steps 1–3

## Authority rules

- Project-specific invoice and profitability facts come from this project's local files.
- Shared NBN/DCR/WBA reference facts come from `_wiki/wiki_stuff/domains/nbn`.
- Shared Vocus interpretation notes come from `_wiki/wiki_stuff/domains/vocus`.
- Nav YAML (`context-map.yaml`, `rag/project-context.yaml`) is routing metadata only.

## Collection policy

Every query must include:
- Project identity filter: `project_slug: vocus_profitability`
- Wiki domain filter when querying wiki collections: `wiki_domain: nbn` or `wiki_domain: vocus`

Every result must cite: source file, section path, heading, document ID, collection name.

## How to add another wiki domain

1. Confirm the domain exists under `_wiki/wiki_stuff/domains/<domain>/`.
2. Confirm the domain is in `_wiki/wiki-data/domain-registry.yaml`.
3. Confirm the Qdrant collection `rag__wiki_<domain>` is indexed (or plan to index it).
4. Add to `rag/project-context.yaml` under `wiki_dependencies`.
5. Add to `rag/retrieval-policy.yaml` under `allowed_wiki_domains` and `allowed_wiki_collections`.
6. Update this document.
7. Run `just rag-validate-policy` to confirm.
