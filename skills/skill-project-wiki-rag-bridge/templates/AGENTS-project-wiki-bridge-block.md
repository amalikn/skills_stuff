## RAG / Wiki Bridge

<!-- BEGIN project-wiki-rag-bridge:agents -->
This project uses the shared wiki and rag-tools for policy-governed vector retrieval.

RAG bridge files:
- `rag/project-context.yaml` — wiki dependency declarations and retrieval routing
- `rag/retrieval-policy.yaml` — flat policy validated by rag-tools
- `rag/manifests/project-documents.yaml` — document index manifest (default_index: false)
- `docs/ai/wiki-bridge.md` — human-readable bridge policy summary

Collection: `rag__project_<project_slug>`

Allowed wiki domains:
- `<domain>` → `rag__wiki_<domain>`

Retrieval order: project-local → project-collection → declared-wiki-domains → ask-user

Forbidden: global collections, undeclared wiki domains, raw/sensitive data without explicit approval.

Load `project-wiki-rag-bridge` skill for any RAG setup, indexing, or troubleshooting work.
<!-- END project-wiki-rag-bridge:agents -->
