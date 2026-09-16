# Checklist: Multi-Project Isolation

**Use when:** adding a second or subsequent project to the bridge ecosystem.
**Use for:** auditing that projects do not pollute each other's collections.

---

## Per-project collection isolation

- [ ] Each project has its own Qdrant collection: `rag__project_<slug>`
- [ ] No two projects share a project collection
- [ ] Each project's `project_slug` is unique across all projects
- [ ] Each project collection contains only content declared in that project's manifest

## Wiki domain collection sharing (allowed, but controlled)

- [ ] Wiki domain collections (`rag__wiki_<domain>`) are shared across projects
- [ ] A project may only query wiki domains declared in its `retrieval-policy.yaml`
- [ ] A project that has NOT declared domain X must not query `rag__wiki_X`
- [ ] Each query to a wiki collection includes `wiki_domain` filter

## Cross-project fallback (forbidden)

- [ ] No project's retrieval policy references another project's collection
- [ ] No project uses `rag__project_*` wildcard or undeclared project collection
- [ ] No "fallback to any project collection" logic present

## Deny list present

- [ ] Each project's `retrieval-policy.yaml` has a `forbidden_collections` list
- [ ] The forbidden list includes all globally forbidden names
- [ ] The forbidden list is validated by rag-tools before any indexing

## No global collection

- [ ] No collection named `rag__global_all_docs` exists in Qdrant
- [ ] No collection named `rag__wiki_all` exists in Qdrant
- [ ] No collection named `rag__all`, `default`, `documents`, `knowledge`, or `main` exists
- [ ] Collection audit confirms all collections match allowed patterns

## Shared wiki content safety

- [ ] Wiki domain content is shared reference knowledge only (no project-specific data)
- [ ] No project has written its own facts into a wiki domain collection
- [ ] Wiki articles include `authority: shared_reference_authoritative_markdown`

## Audit trail

- [ ] Each project's `rag/project-context.yaml` documents its allowed wiki domains and reasons
- [ ] The domain registry documents all active domains and their Qdrant collections
- [ ] Any change to allowed domains is reflected in both project-context and retrieval-policy

---

## Verdict

```
ISOLATION_CONFIRMED — all checks pass
ISOLATION_PARTIAL   — some isolation checks fail
ISOLATION_VIOLATED  — cross-project contamination or forbidden collections found
```
