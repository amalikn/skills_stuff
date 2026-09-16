---
title: project-context.yaml Contract
status: accepted
date: 20260524
provenance: schemas/project-context.schema.yaml, templates/project-context.yaml
---

# project-context.yaml Contract

## Purpose

`project-context.yaml` is the primary project identity and dependency declaration file. It lives at `<project>/rag/project-context.yaml` and declares the project's identity, its wiki dependencies, canonical paths, tools, retrieval order, and isolation rules.

## Required top-level keys

| Key | Type | Constraint |
|---|---|---|
| `version` | integer | Must be `1` |
| `schema` | string | Must be `"wiki-project-dependency-model"` |
| `global_search_allowed` | boolean | Must always be `false` — global wiki search is forbidden |
| `project` | object | See required sub-keys below |
| `wiki` | object | See required sub-keys below |
| `tools` | object | See required sub-keys below |
| `wiki_dependencies` | list of objects | One entry per declared wiki domain |
| `retrieval_policy` | object | Must include `retrieval_order` |
| `rules` | object | All isolation rules should be `true` |
| `forbidden_collections` | list of string | Must include the globally forbidden set |
| `status` | object | Must include `lifecycle`, `owner`, `reviewed` |

## project object required sub-keys

| Key | Pattern | Notes |
|---|---|---|
| `id` | free string | Stable project identifier, e.g. `apn-vocus-profitability` |
| `slug` | `^[a-z0-9_]+$` | Used as Qdrant filter value — underscores only, no hyphens |
| `name` | free string | Human-readable project name |
| `root` | absolute path | Project root on this machine |
| `collection` | `^rag__project_[a-z0-9_]+$` | Must be `rag__project_<slug>` |

## wiki object required sub-keys

| Key | Expected value |
|---|---|
| `root` | `/Volumes/Data/_ai/_wiki` |
| `content_root` | `/Volumes/Data/_ai/_wiki/wiki_stuff` |
| `data_root` | `/Volumes/Data/_ai/_wiki/wiki-data` |
| `pattern` | `karpathy-llm-wiki` |
| `canonical_shared_knowledge` | `true` |

## tools object required sub-keys

| Key | Expected value |
|---|---|
| `rag_tools_root` | `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools` |
| `rag_tools_venv` | `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv` |

## wiki_dependencies list item required keys

Each declared wiki domain must have: `domain`, `slug`, `collection`, `source_paths`, `reason`, `source_authority`

## retrieval_policy

Must include `retrieval_order`. The final step in retrieval order must always be `ask_user` — there is no fallback to global search.

## Common failures

| Failure | Fix |
|---|---|
| `global_search_allowed: true` | Must always be `false` — no exceptions |
| `wiki.root` path doesn't exist on this machine | Verify paths; update to correct absolute path |
| `wiki_dependencies` entry missing `reason` field | Add a human-readable justification for each declared domain |
| `collection` in `wiki_dependencies` doesn't match `rag__wiki_<domain>` | Fix the collection slug to match exactly |
| `retrieval_order` missing `ask_user` as final step | Add explicit ask-user step — do not imply global fallback |

## Starter template

See `templates/project-context.yaml`.

## Related

- [schemas/project-context.schema.yaml](../../schemas/project-context.schema.yaml)
- [specs/retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
