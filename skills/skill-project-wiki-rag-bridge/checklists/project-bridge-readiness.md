# Checklist: Project Bridge Readiness

**Use after:** prompt 03 (create-project-bridge).
**Use before:** prompt 04 (validate-project-policy) and any indexing.

---

## Bridge files

- [ ] `<project>/rag/project-context.yaml` — exists
- [ ] `<project>/rag/retrieval-policy.yaml` — exists
- [ ] `<project>/rag/manifests/project-documents.yaml` — exists
- [ ] `<project>/docs/ai/wiki-bridge.md` — exists

## YAML validity

- [ ] `rag/project-context.yaml` parses without error
- [ ] `rag/retrieval-policy.yaml` parses without error
- [ ] `rag/manifests/project-documents.yaml` parses without error

## project-context.yaml content

- [ ] `global_search_allowed: false`
- [ ] `project.id` is set (not placeholder)
- [ ] `project.slug` matches `rag__project_<slug>` in project.collection
- [ ] `project.root` matches actual project directory
- [ ] `wiki_dependencies` has at least 1 entry
- [ ] Each dependency entry has: `domain`, `slug`, `collection`, `source_paths`, `reason`
- [ ] No placeholder `<>` values remain

## retrieval-policy.yaml content (flat validator keys)

- [ ] `version: 1`
- [ ] `project_slug` set and matches project_context slug
- [ ] `project_collection: rag__project_<slug>`
- [ ] `allowed_wiki_domains` has at least 1 entry
- [ ] `allowed_wiki_collections` matches domains 1:1 (`rag__wiki_<domain>`)
- [ ] `forbidden_collections` includes all globally forbidden names
- [ ] `required_filters` includes `project_slug` and `wiki_domain`
- [ ] `citation_rules` all set to `true`
- [ ] No placeholder `<>` values remain

## project-documents.yaml content

- [ ] `rules.default_index: false`
- [ ] `rules.require_explicit_index_true: true`
- [ ] `rules.raw_data_requires_explicit_approval: true`
- [ ] `rules.communications_requires_review_before_indexing: true`
- [ ] No document has `sensitive: true` AND `index: true` (contradiction)

## Governance file updates

- [ ] `AGENTS.md` — RAG bridge block added (or confirmed N/A if no AGENTS.md)
- [ ] `AI_NAVIGATION.md` — RAG bridge block added (or confirmed N/A)
- [ ] `README.md` — RAG/Wiki Bridge section added (or confirmed N/A)
- [ ] `CHANGELOG.md` — entry appended (or confirmed N/A)

## Justfile tasks (if justfile present)

- [ ] `rag-validate-policy` task present
- [ ] `rag-tools-doctor` task present
- [ ] `rag-index-domain-dry` task present
- [ ] `rag-index-domain` task present

---

## Verdict

```
PROJECT_WIKI_BRIDGE_READY    — all files exist, valid YAML, no placeholders
PROJECT_WIKI_BRIDGE_PARTIAL  — files exist but have placeholder values or YAML errors
PROJECT_WIKI_BRIDGE_NOT_READY — core files missing
```
