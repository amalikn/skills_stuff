---
title: New Project Onboarding Guide
status: accepted
date: 20260524
provenance: SKILL.md, docs/operating-runbook.md, docs/multi-project-model.md
---

# New Project Onboarding Guide

Step-by-step guide for connecting a new project repo to the wiki/rag bridge. Follow in order. Do not skip steps.

## Contents

- [Prerequisites](#prerequisites)
- [Step 1 — Verify wiki operational state](#step-1--verify-wiki-operational-state)
- [Step 2 — Verify rag-tools](#step-2--verify-rag-tools)
- [Step 3 — Assign project slug](#step-3--assign-project-slug)
- [Step 4 — Create bridge files](#step-4--create-bridge-files)
- [Step 5 — Validate policy](#step-5--validate-policy)
- [Step 6 — Create wiki domains (if new)](#step-6--create-wiki-domains-if-new)
- [Step 7 — Index wiki domains](#step-7--index-wiki-domains)
- [Step 8 — Index project documents](#step-8--index-project-documents)
- [Step 9 — Validate retrieval](#step-9--validate-retrieval)
- [Rollback](#rollback)

## Prerequisites

- rag-tools installed at `_tool/tools_stuff/rag-tools/`
- rag-tools venv active at `tools-working-cache/rag-tools/.venv/`
- Qdrant running locally at `localhost:6333`
- Chosen wiki domains exist in `_wiki/wiki-data/domain-registry.yaml`

## Step 1 — Verify wiki operational state

Run: `prompts/00-verify-wiki-operational-state.md`
Gate: `checklists/wiki-operational-readiness.md`

All checklist items must pass before proceeding.

## Step 2 — Verify rag-tools

Run: `prompts/02-verify-rag-tools.md`
Gate: `checklists/rag-tools-readiness.md`

Confirm: `rag-tools doctor` passes, Qdrant is reachable, embedding smoke test succeeds.

## Step 3 — Assign project slug

- Choose a unique `project_slug`: lowercase alphanumeric + underscores, e.g. `vocus_profitability`
- Check all existing `retrieval-policy.yaml` files to confirm no slug collision
- The slug will become the collection name suffix: `rag__project_<slug>`

## Step 4 — Create bridge files

Run: `prompts/03-create-project-bridge.md`
Gate: `checklists/project-bridge-readiness.md`

Files to create at `<project>/rag/`:
```
rag/
  project-context.yaml          # from templates/project-context.yaml
  retrieval-policy.yaml         # from templates/retrieval-policy.yaml
  manifests/
    project-documents.yaml      # from templates/project-documents.yaml
```

See `examples/vocus-profitability/` for a complete reference implementation.

## Step 5 — Validate policy

Run: `prompts/04-validate-project-policy.md`

```bash
rag-tools validate-policy <project>/rag/retrieval-policy.yaml
```

Policy must pass before any indexing. Fix all validation errors before continuing.

## Step 6 — Create wiki domains (if new)

Only needed if declaring a wiki domain that does not yet exist.

Run: `prompts/01-create-wiki-domain.md`

Creates:
- Entry in `_wiki/wiki-data/domain-registry.yaml`
- Domain directory at `_wiki/wiki_stuff/domains/<domain>/`
- Domain index file

## Step 7 — Index wiki domains

For each declared wiki domain, one at a time:

Run: `prompts/05-index-wiki-domain.md`
Gate: `checklists/indexing-readiness.md`

**Always dry-run first:**
```bash
just rag-index-domain-dry <domain>
```
Confirm chunk count looks correct. Then:
```bash
just rag-index-domain <domain>
```

Never batch multiple domains in one operation.

## Step 8 — Index project documents

Run: `prompts/08-index-project-documents.md`
Gate: `checklists/indexing-readiness.md`

```bash
rag-tools index-project <project>/rag/manifests/project-documents.yaml
```

Verify `vectors_count` matches dry-run chunk count.

## Step 9 — Validate retrieval

Run: `prompts/06-post-index-retrieval-validation.md`
Gate: `checklists/retrieval-validation.md`

Confirm:
- Test queries return results from expected collections only
- All results include `source_file`, `section_path`, `collection` citation
- No results from undeclared collections
- `checklists/multi-project-isolation.md` passes for all existing projects

## Rollback

If a collection is incorrectly named or populated:

```bash
# List collections
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Delete a collection
curl -X DELETE http://localhost:6333/collections/<collection_name>

# Re-index (dry-run first)
just rag-index-domain-dry <domain>
just rag-index-domain <domain>
```

Never delete a collection without a dry-run of the re-index plan first.

## Related

- [SKILL.md](../../SKILL.md)
- [docs/operating-runbook.md](../../docs/operating-runbook.md)
- [docs/multi-project-model.md](../../docs/multi-project-model.md)
- [rules/workflow-sequencing-rules.md](../rules/workflow-sequencing-rules.md)
- [specs/retrieval-policy-yaml-contract.md](../specs/retrieval-policy-yaml-contract.md)
