---
title: project-documents.yaml Contract
status: accepted
date: 20260524
provenance: schemas/project-documents.schema.yaml, templates/project-documents.yaml
---

# project-documents.yaml Contract

## Purpose

`project-documents.yaml` is the explicit opt-in manifest for project document indexing. It lives at `<project>/rag/manifests/project-documents.yaml`. No document is indexed unless it appears here with `index: true` and is not marked `sensitive: true`. This manifest is the primary guard against accidental indexing of sensitive or raw project data.

## Required top-level keys

| Key | Type | Constraint |
|---|---|---|
| `version` | integer | Must be `1` |
| `project_slug` | string | Must match `project_slug` in `retrieval-policy.yaml` — pattern `^[a-z0-9_]+$` |
| `rules` | object | See rule keys below — all must be present and correct |
| `documents` | list of objects | May be empty; each entry is one document |

## rules object — all keys mandatory

| Key | Required value | Notes |
|---|---|---|
| `default_index` | `false` | **Must be false.** No document is indexed unless explicitly opted in. |
| `require_explicit_index_true` | `true` | Every document entry must have an explicit `index:` key. |
| `raw_data_requires_explicit_approval` | `true` | Raw-type documents need explicit approval notes before indexing. |
| `communications_requires_review_before_indexing` | `true` | Communication-type documents require documented human review. |

## documents list item required keys

| Key | Type | Allowed values | Notes |
|---|---|---|---|
| `id` | string | — | Stable unique ID used as `document_id` in Qdrant |
| `title` | string | — | Human-readable title |
| `path` | string | — | Relative path from project root |
| `type` | string | `report`, `manifest`, `reference`, `analysis`, `communication`, `raw` | Determines caution level |
| `index` | boolean | — | Must be explicitly set — no default |
| `sensitive` | boolean | — | If `true`, never index regardless of `index` flag |
| `notes` | string | — | Required when `index: true` or `sensitive: true` |

## Document type caution levels

| Type | Caution | Guidance |
|---|---|---|
| `report` | Low | Curated output — usually safe to index |
| `manifest` | Low | Structured metadata — usually safe |
| `reference` | Low | Reference material — usually safe |
| `analysis` | Medium | May contain derived sensitive data — review before indexing |
| `communication` | High | Requires explicit review — never index by default |
| `raw` | High | Raw data — never index without explicit approval and notes |

## Indexing gate rules

- `sensitive: true` + `index: true` — indexing is blocked; both flags may co-exist but the sensitive flag wins
- `type: communication` or `type: raw` with `index: true` — requires `notes` field explaining review/approval
- `index: true` with no `notes` for high-caution types — policy violation; add notes before indexing

## Common failures

| Failure | Fix |
|---|---|
| `default_index: true` | Must be `false` — this is a hard rule |
| Document entry missing `index:` key | Add explicit `index: false` or `index: true` — no implicit defaults |
| `sensitive: true` but `index: true` — both flags present | The sensitive flag blocks indexing; this is correct but add a note |
| `communication` or `raw` with `index: true` and no `notes` | Add a `notes:` field documenting who approved and when |
| `path` doesn't exist relative to project root | Fix the path or remove the entry |
| `project_slug` doesn't match `retrieval-policy.yaml` | Fix slug to match — Qdrant filter depends on consistency |

## Starter template

See `templates/project-documents.yaml`.

## Related

- [schemas/project-documents.schema.yaml](../../schemas/project-documents.schema.yaml)
- [specs/retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md) — RULE-D1, RULE-D3
