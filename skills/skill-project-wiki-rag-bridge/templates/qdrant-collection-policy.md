# Qdrant Collection Policy — <Project Name>

Status: draft
Scope: This file documents the Qdrant collection policy for `<project-id>`.
Authority: Governed by `/Volumes/Data/_ai/_wiki/wiki-data/qdrant-collection-policy.md`.

## Project collection

```
rag__project_<project_slug>
```

Used for: indexed project documents declared with `index: true` in `rag/manifests/project-documents.yaml`.

## Allowed wiki collections

```
rag__wiki_<domain1>
rag__wiki_<domain2>
```

Access to these collections is declared in `rag/retrieval-policy.yaml` and governed by the domain registry.

## Forbidden collections

```
rag__global_all_docs
rag__wiki_all
rag__all
default
documents
knowledge
main
```

Any collection not matching `rag__project_<project_slug>` or a declared `rag__wiki_*` entry is forbidden for this project.

## Required chunk metadata

Every indexed chunk must carry:

```yaml
collection: <collection_name>
source_type: <wiki_markdown | project_doc | project_report>
project_id: <project-id>          # project collections only
project_slug: <project_slug>       # project collections only
wiki_domain: <domain>              # wiki collections only
document_id: <stable-id>
document_title: <title>
source_file: <path>
section_path: <H1 > H2 > H3>
heading: <immediate heading>
authority: <shared_reference_authoritative_markdown | project_local>
content_hash: <sha256>
created_at: <ISO 8601>
```

## Enforcement

Qdrant does not enforce these rules. Enforcement is the responsibility of:

1. `rag/retrieval-policy.yaml` — declares allowed/forbidden collections
2. `rag-tools validate-policy` — validates policy before indexing
3. This skill — guides the agent to respect policy at query time
