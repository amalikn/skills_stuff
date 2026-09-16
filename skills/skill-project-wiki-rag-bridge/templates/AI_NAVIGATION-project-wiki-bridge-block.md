## RAG and Wiki Access

<!-- BEGIN project-wiki-rag-bridge:ai-nav -->
**Retrieval policy:** `rag/retrieval-policy.yaml`
**Wiki bridge summary:** `docs/ai/wiki-bridge.md`
**Document manifest:** `rag/manifests/project-documents.yaml`

Retrieval order:
1. Project-local files (first)
2. `rag__project_<project_slug>` (filtered by `project_slug`)
3. `rag__wiki_<domain>` (filtered by `wiki_domain`, declared only)
4. Ask user if insufficient evidence

Allowed wiki domains: `<domain>`
Forbidden: global collections, undeclared domains, raw/sensitive data

All results must cite: `source_file`, `section_path`, `heading`, `collection`
<!-- END project-wiki-rag-bridge:ai-nav -->
