This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, SKILL.md, CHANGELOG.md, context-map.yaml, SCRATCHPAD.md, docs/**/*.md, schemas/**/*.yaml, checklists/**/*.md, templates/**/*.md, templates/**/*.yaml, .archcore/**/*.md, .archcore/**/*.yaml
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.archcore/
  adr/
    ADR-001-qdrant-collection-naming-convention.md
    ADR-002-multi-project-isolation-model.md
    ADR-003-authority-hierarchy.md
  guides/
    dynamic-retrieval-routing.md
    evidence-first-answering.md
    failure-mode-reference.md
    new-project-onboarding.md
    post-index-retrieval-validation.md
    wiki-domain-creation.md
  rules/
    retrieval-isolation-rules.md
    workflow-sequencing-rules.md
  specs/
    document-profile-contract.md
    evidence-bundle-contract.md
    project-context-yaml-contract.md
    project-documents-yaml-contract.md
    qdrant-query-filter-contract.md
    retrieval-policy-yaml-contract.md
    retrieval-strategy-yaml-contract.md
    wiki-domain-registry-contract.md
checklists/
  dynamic-retrieval-readiness.md
  evidence-bundle-validation.md
  indexing-readiness.md
  multi-project-isolation.md
  project-bridge-readiness.md
  rag-tools-readiness.md
  retrieval-validation.md
  wiki-operational-readiness.md
docs/
  architecture.md
  authority-model.md
  collection-naming-policy.md
  dynamic-retrieval-strategy.md
  evidence-contract.md
  failure-modes.md
  flow-diagram.md
  multi-project-model.md
  operating-runbook.md
  retrieval-mode-decision-tree.md
schemas/
  document-profile.schema.yaml
  evidence-bundle.schema.yaml
  project-context.schema.yaml
  project-documents.schema.yaml
  retrieval-policy.schema.yaml
  retrieval-strategy.schema.yaml
  wiki-domain-registry.schema.yaml
templates/
  AGENTS-project-wiki-bridge-block.md
  AI_NAVIGATION-project-wiki-bridge-block.md
  benchmark-queries.yaml
  evidence-bundle.yaml
  project-context.yaml
  project-documents.yaml
  project-wiki-bridge.md
  qdrant-collection-policy.md
  retrieval-policy.yaml
  retrieval-strategy.yaml
  source-profile.yaml
  wiki-domain-index.md
  wiki-domain-registry-entry.yaml
  wiki-reference-article.md
AGENTS.md
AI_NAVIGATION.md
CHANGELOG.md
CLAUDE.md
context-map.yaml
README.md
SCRATCHPAD.md
SKILL.md
```

# Files

## File: .archcore/adr/ADR-001-qdrant-collection-naming-convention.md
````markdown
---
id: ADR-001
title: Qdrant Collection Naming Convention
status: accepted
date: 20260524
provenance: docs/collection-naming-policy.md, SKILL.md
---

# ADR-001 — Qdrant Collection Naming Convention

## Status

Accepted

## Context

Qdrant has no built-in multi-tenancy. Collections can be created with any name, and without a naming policy, agents or operators could accidentally create global or ambiguous collections that mix project and wiki data. Silent naming violations would break retrieval isolation without raising errors.

## Decision

All collections in the wiki/project RAG bridge follow a three-prefix naming scheme:

| Pattern | Usage |
|---|---|
| `rag__project_<project_slug>` | Per-project document index |
| `rag__wiki_<domain_slug>` | Per-wiki-domain shared index |
| `rag__test_<purpose>_<yyyymmdd>` | Ephemeral test collections only |

**Constraints:**
- `<project_slug>` and `<domain_slug>` must be lowercase alphanumeric + underscores only (no hyphens, spaces, uppercase)
- `<project_slug>` must match the `project_slug` field in `retrieval-policy.yaml`
- `<domain_slug>` must match the `slug` field in `domain-registry.yaml`
- Test collections must have a date suffix and be deleted after use

**Forbidden names (must never exist in production):**

`rag__global_all_docs`, `rag__wiki_all`, `rag__all`, `default`, `documents`, `knowledge`, `main`, `wiki`, `test` (bare)

## Consequences

- Every collection is immediately identifiable as wiki, project, or test by name alone
- Naming violations are detectable via regex: `^rag__(project|wiki|test)_[a-z0-9_]+$`
- `rag-tools validate-policy` enforces the forbidden list on policy files
- Agents must refuse to create collections outside this pattern

## Validation pattern

```python
import re
ALLOWED = re.compile(r'^rag__(project|wiki|test)_[a-z0-9_]+$')
FORBIDDEN = {
    'rag__global_all_docs', 'rag__wiki_all', 'rag__all',
    'default', 'documents', 'knowledge', 'main',
}
def validate_collection_name(name: str) -> bool:
    return bool(ALLOWED.match(name)) and name not in FORBIDDEN
```

## Related

- [docs/collection-naming-policy.md](../../docs/collection-naming-policy.md)
- [ADR-002-multi-project-isolation-model.md](ADR-002-multi-project-isolation-model.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
````

## File: .archcore/adr/ADR-002-multi-project-isolation-model.md
````markdown
---
id: ADR-002
title: Multi-Project Isolation Model
status: accepted
date: 20260524
provenance: docs/multi-project-model.md, SKILL.md
---

# ADR-002 — Multi-Project Isolation Model

## Status

Accepted

## Context

Multiple projects need access to shared wiki knowledge (e.g., NBN standards, Vocus rate cards) without polluting each other's data. A naive global search would allow Project A to see Project B's documents, or mix project-specific facts with shared reference knowledge.

## Decision

The isolation model uses four enforcement gates:

**Gate 1 — Declaration gate:** A project may only query wiki domains it has explicitly declared in `retrieval-policy.yaml` under `allowed_wiki_domains`. Undeclared domains are forbidden even if the collection exists in Qdrant.

**Gate 2 — Filter gate:** Every query to a wiki collection must include a `wiki_domain` filter. Every query to a project collection must include a `project_slug` filter. Unfiltered queries are policy violations.

**Gate 3 — Collection-per-project:** No two projects share a project collection. Each project gets exactly one `rag__project_<slug>` collection. Cross-project indexing is a policy violation requiring immediate cleanup.

**Gate 4 — No cross-project fallback:** If a project's own collection returns no results, the correct action is to ask the user — not to fall back to another project's collection.

**Shared wiki model:** Wiki domain collections (`rag__wiki_<domain>`) are shared indexes. All projects declaring a domain query the same collection. New wiki content becomes available to all declaring projects immediately without per-project re-indexing.

## Consequences

- Wiki knowledge propagates to all projects without re-indexing
- Project data never leaks across project boundaries
- `retrieval-policy.yaml` is the single declaration of what a project is allowed to query
- Agents must enforce all four gates; refusing requests that would violate any gate
- `checklists/multi-project-isolation.md` must be run when adding new projects

## Related

- [docs/multi-project-model.md](../../docs/multi-project-model.md)
- [ADR-001-qdrant-collection-naming-convention.md](ADR-001-qdrant-collection-naming-convention.md)
- [specs/retrieval-policy-yaml-contract.md](../specs/retrieval-policy-yaml-contract.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
````

## File: .archcore/adr/ADR-003-authority-hierarchy.md
````markdown
---
id: ADR-003
title: Source Authority Hierarchy for Retrieval
status: accepted
date: 20260524
provenance: docs/authority-model.md
---

# ADR-003 — Source Authority Hierarchy for Retrieval

## Status

Accepted

## Context

During retrieval, agents may encounter information from multiple sources: project-local files, wiki markdown, Qdrant payloads, generated reports, and routing YAML. Without an explicit authority hierarchy, agents might cite Qdrant payloads as authoritative (they are not — they are search artefacts pointing to source files) or use routing YAML as factual content.

## Decision

The following authority hierarchy is accepted and enforced:

| Priority | Source | Scope |
|---|---|---|
| 1 | Project-local files | Project-specific facts only |
| 2 | Wiki authoritative markdown (`_wiki/wiki_stuff/domains/`) | Shared reference facts only |
| 3 | Qdrant retrieval results | Search results — cite original source, do not treat as canonical |
| 4 | Generated summaries / reports | Secondary — do not override primary sources |
| 5 | Nav YAML (`context-map.yaml`, `project-context.yaml`, etc.) | Routing metadata only — never factual content |

**Conflict resolution:**
- Project-local vs wiki general reference → project-local wins
- Wiki standard vs project interpretation → report conflict, ask user
- Two wiki articles disagree → report conflict, cite both, ask user
- Qdrant result vs source markdown → source markdown wins — re-read the file

**Insufficient evidence rule:** If retrieved evidence is insufficient, agents must say so explicitly. Speculation or source-blending without labelling is forbidden.

## Consequences

- Qdrant payloads must always include citation metadata: `source_file`, `section_path`, `collection`
- Agents must never answer a factual question by citing a routing file
- `authority` metadata field in indexed documents must use standard labels: `shared_reference_authoritative_markdown`, `project_local`, `project_generated`, `routing_metadata_only`
- Conflict reports must name both conflicting files and state resolution intent

## Related

- [docs/authority-model.md](../../docs/authority-model.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
````

## File: .archcore/guides/dynamic-retrieval-routing.md
````markdown
---
title: Dynamic Retrieval Routing Guide
status: accepted
date: 20260525
provenance: docs/dynamic-retrieval-strategy.md, docs/retrieval-mode-decision-tree.md, SKILL.md
---

# Dynamic Retrieval Routing Guide

## Core principle

Vector RAG is not the universal default. Retrieval mode must be selected based on the document class, its structural features, and benchmark results. Always profile before deciding to index.

## Profile-first workflow

```
profile-file → recommend-strategy → (benchmark-file) → index_allowed decision
```

Never set `index_allowed: true` without a completed benchmark for structured or tabular sources.

## CLI commands

```bash
source tools-working-cache/rag-tools/.venv/bin/activate

# Profile a document
rag-tools profile-file <path>

# Recommend retrieval strategy from profile
rag-tools recommend-strategy <source-profile.yaml>

# Structured section lookup (no indexing required)
rag-tools structured-lookup <path> --section <id>

# Section/clause lookup by heading
rag-tools lookup-section <path> --heading <text>

# Table-aware lookup
rag-tools lookup-table <path> --query <text>

# Benchmark retrieval modes against query set
rag-tools benchmark-file <path> <benchmark-queries.yaml>
```

## Retrieval mode routing table

| `document_class` | Primary route | When to RAG |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` / `section_clause_lookup` | Only for cross-document semantic search — not for exact-fact queries |
| `financial_rate_card` | `table_aware_lookup` | Not suitable — exact prices require deterministic lookup |
| `invoice_or_billing_report` | `tabular_analytics` | Not suitable — amounts must come from source |
| `legal_contract_or_terms` | `section_clause_lookup` | Partially suitable — only after benchmark confirms |
| `knowledge_article` | `vector_rag` | Suitable — knowledge-style content designed for RAG |
| `meeting_notes` | `keyword_lookup` | Partially suitable |
| `unstructured_pdf` | `extraction_required` | Not suitable without prior extraction |
| `tabular_dataset` | `tabular_analytics` | Not suitable for RAG |

## When NOT to index

Do not index (leave `index_allowed: false`) when:
- `benchmark_status` is `not_run` or `failed`
- `rag_suitability` is `not_suitable`
- `contains_sensitive_data: true`
- Benchmark returned label `NOT_READY_NEEDS_EXTRACTION`
- Document contains exact financial amounts or legal clause text (deterministic lookup is always more reliable)

## Benchmark route labels

| Label | Meaning |
|---|---|
| `DIRECT_FIRST` | Use `direct_structured_lookup` as primary; RAG is fallback only |
| `TABLE_LOOKUP_FIRST` | Use `table_aware_lookup`; RAG not suitable |
| `HYBRID_DIRECT_FIRST` | Deterministic lookup first; RAG for semantic cross-doc queries |
| `HYBRID_RAG_FIRST` | RAG acceptable as primary; structured as fallback |
| `RAG_FIRST` | RAG is appropriate primary mode |
| `NOT_READY_NEEDS_EXTRACTION` | Source requires pre-processing before any retrieval |
| `NOT_READY_NEEDS_MORE_INDEXED_CONTENT` | Insufficient indexed content for reliable RAG |

## Source files remain authoritative

Qdrant collections are retrieval artifacts, not authoritative records. The `source_file` in every EvidenceBundle is the canonical citation target. Never cite a Qdrant collection name as the source of truth.

## Related

- [docs/dynamic-retrieval-strategy.md](../../docs/dynamic-retrieval-strategy.md)
- [docs/retrieval-mode-decision-tree.md](../../docs/retrieval-mode-decision-tree.md)
- [retrieval-strategy-yaml-contract.md](../specs/retrieval-strategy-yaml-contract.md)
- [document-profile-contract.md](../specs/document-profile-contract.md)
- [checklists/dynamic-retrieval-readiness.md](../../checklists/dynamic-retrieval-readiness.md)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
- [prompts/02c-benchmark-retrieval-routes.md](../../prompts/02c-benchmark-retrieval-routes.md)
````

## File: .archcore/guides/evidence-first-answering.md
````markdown
---
title: Evidence-First Answering Guide
status: accepted
date: 20260525
provenance: docs/evidence-contract.md, schemas/evidence-bundle.schema.yaml, SKILL.md
---

# Evidence-First Answering Guide

## Principle

Every answer must be grounded in a retrieved EvidenceBundle. The agent must never answer a factual question about project documents, contracts, rates, or wiki articles from training knowledge. If there is no valid bundle, report `RETRIEVAL_NOT_READY` and stop.

## Required answer discipline

1. **Retrieve first.** Run the appropriate rag-tools command before answering.
2. **Answer only from `excerpt`.** The `excerpt` field is the only permitted answer source.
3. **Do not infer.** If an amount, date, clause reference, or identifier is not in the excerpt, do not state it.
4. **Say "not found."** If the evidence does not support the question, say "not found in retrieved evidence" — do not guess.
5. **Surface warnings.** If `retrieval_warnings` is non-empty, surface it in the answer — do not silently use low-confidence evidence.
6. **Cite the source.** Minimum citation is `source_file`. Preferred: `source_file` + (`section_id` OR `heading`).

## Bundle validity check

Before answering from a bundle, verify:

- [ ] `source_file` is present and is an absolute file path (not a Qdrant collection name)
- [ ] `excerpt` is non-empty
- [ ] `retrieval_mode` matches the mode actually used
- [ ] `retrieval_warnings` inspected — warn the user if populated

If `excerpt` is empty → bundle is invalid → do not answer → report `RETRIEVAL_NOT_READY`.

## Good answer pattern

```
Retrieved from: /path/to/source.md § C2.11 (direct_structured_lookup)

The rebate period 3 credit rate is [exact text from excerpt].
```

## Bad answer pattern (forbidden)

```
The rebate credit rate is approximately 12% based on typical wholesale billing agreements.
```
(Invented; not from excerpt — forbidden even if plausible.)

## When multiple bundles conflict

- Do not merge conflicting excerpts into a single answer.
- Report both excerpts and their sources.
- State: "Sources conflict. [Source A] states [X]. [Source B] states [Y]. Manual review required."

## Retrieval warning handling

| Warning | Required action |
|---|---|
| `source file missing` | Report file missing; do not answer |
| `vector RAG score < 0.5` | Flag as low-confidence; do not treat as authoritative |
| `fallback used` | State which mode was used; note fallback in citation |
| `partial match` | Limit claim to what is actually in the excerpt |
| `structured lookup — no exact section ID match` | State section was not found; do not guess nearby content |

## Checklist

See `checklists/evidence-bundle-validation.md` for the full bundle validation gate.

## Related

- [specs/evidence-bundle-contract.md](../specs/evidence-bundle-contract.md)
- [schemas/evidence-bundle.schema.yaml](../../schemas/evidence-bundle.schema.yaml)
- [docs/evidence-contract.md](../../docs/evidence-contract.md)
- [checklists/evidence-bundle-validation.md](../../checklists/evidence-bundle-validation.md)
- [dynamic-retrieval-routing.md](dynamic-retrieval-routing.md)
````

## File: .archcore/guides/failure-mode-reference.md
````markdown
---
title: Failure Mode Reference
status: accepted
date: 20260524
provenance: docs/failure-modes.md
---

# Failure Mode Reference

Quick reference for diagnosing RAG bridge failures. For each failure mode: detection command and fix.

## Contents

- [FM-01 Scaffold-only collection](#fm-01-scaffold-only-collection)
- [FM-02 Silent indexing failure](#fm-02-silent-indexing-failure)
- [FM-03 Policy valid but no retrieval](#fm-03-policy-valid-but-no-retrieval)
- [FM-04 Embedding model mismatch](#fm-04-embedding-model-mismatch)
- [FM-05 Naming violation](#fm-05-naming-violation)
- [FM-06 Cross-project contamination](#fm-06-cross-project-contamination)

## FM-01 Scaffold-only collection

**Symptom:** Collection exists, policy validates, queries return nothing.
**Cause:** `rag-tools index-domain` was never run or exited before indexing.
**Detect:** `client.get_collection('rag__wiki_nbn').vectors_count` returns 0.
**Fix:** Re-run `prompts/05-index-wiki-domain.md`. Verify domain directory has markdown files first.

## FM-02 Silent indexing failure

**Symptom:** Index command appeared to succeed but collection has 0 or very low vector count.
**Cause:** Domain directory had no eligible files, or embedding failed quietly.
**Detect:** Compare dry-run chunk count with actual `vectors_count` after indexing.
**Fix:** Check domain markdown files for frontmatter errors. Run embedding smoke test. Re-dry-run then re-index.

## FM-03 Policy valid but no retrieval

**Symptom:** `rag-tools validate-policy` passes. Qdrant running. Queries return 0 results.
**Cause:** Collection empty (FM-01/FM-02), `wiki_domain` filter excludes all results, or embedding model mismatch.
**Detect:** Check `vectors_count`. Run test query without filter (diagnostic only). Confirm model match.
**Fix:** Depends on cause — see FM-01/FM-02/FM-04.

## FM-04 Embedding model mismatch

**Symptom:** Queries return results but with very low similarity scores (< 0.2).
**Cause:** Collection indexed with one model, queried with another.
**Detect:** Check model metadata on collection vs current rag-tools config.
**Fix:** Delete collection, re-index with correct model (`sentence-transformers/all-MiniLM-L6-v2`). See RULE-E3.

## FM-05 Naming violation

**Symptom:** Collection exists but does not match naming convention.
**Cause:** Manual collection creation or misconfigured template.
**Detect:** `validate_collection_name(name)` returns False.
**Fix:** Delete the non-compliant collection. Re-create and re-index with correct name. See RULE-N1–N6.

## FM-06 Cross-project contamination

**Symptom:** Project queries return results from another project's documents.
**Cause:** Missing `project_slug` filter, or documents indexed without project_slug metadata.
**Detect:** Inspect `source_file` and `project_slug` metadata on returned results.
**Fix:** Delete contaminated collection. Re-index with correct filters. Add `project_slug` metadata to all indexed documents.

## Troubleshooting prompt

See `prompts/09-troubleshoot-rag-bridge.md` for the full interactive diagnostic workflow.

## Related

- [docs/failure-modes.md](../../docs/failure-modes.md)
- [checklists/rag-tools-readiness.md](../../checklists/rag-tools-readiness.md)
- [checklists/retrieval-validation.md](../../checklists/retrieval-validation.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
````

## File: .archcore/guides/new-project-onboarding.md
````markdown
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
````

## File: .archcore/guides/post-index-retrieval-validation.md
````markdown
---
title: Post-Index Retrieval Validation Guide
status: accepted
date: 20260524
provenance: prompts/06-post-index-retrieval-validation.md, checklists/retrieval-validation.md
---

# Post-Index Retrieval Validation Guide

Run after every indexing operation to confirm retrieval respects the project's policy. This guide validates: collection is non-empty, queries return results from declared collections only, citation metadata is complete, isolation filters work, and the system handles insufficient evidence correctly.

## Contents

- [Prerequisites](#prerequisites)
- [Step 1 — Pre-flight checks](#step-1--pre-flight-checks)
- [Step 2 — Run test queries](#step-2--run-test-queries)
- [Step 3 — Isolation check](#step-3--isolation-check)
- [Step 4 — Insufficient evidence behaviour](#step-4--insufficient-evidence-behaviour)
- [Step 5 — Forbidden collection audit](#step-5--forbidden-collection-audit)
- [Verdict output](#verdict-output)
- [Failure responses](#failure-responses)

## Prerequisites

- Indexing step completed for the target domain or project collection
- Qdrant running at `localhost:6333`
- rag-tools venv active: `tools-working-cache/rag-tools/.venv`
- Project's `retrieval-policy.yaml` available

## Step 1 — Pre-flight checks

```bash
# Load and display the retrieval policy
python3 -c "
import yaml
with open('<PROJECT_ROOT>/rag/retrieval-policy.yaml') as f:
    policy = yaml.safe_load(f)
print('Allowed wiki collections:', policy.get('allowed_wiki_collections'))
print('Forbidden:', policy.get('forbidden_collections'))
"

# Verify collection is non-empty
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_<DOMAIN_SLUG>')
print(f'Vectors count: {info.vectors_count}')
print('PASS' if info.vectors_count > 0 else 'FAIL: collection empty — indexing may have failed')
"
```

If collection is empty: stop and investigate (see `guides/failure-mode-reference.md` FM-01/FM-02).

## Step 2 — Run test queries

Run at least 3 test queries relevant to the domain content. For each result verify:
- `source_file` present and correct
- `heading` present
- `section_path` present
- `collection` matches expected `rag__wiki_<DOMAIN_SLUG>`
- `authority` is `shared_reference_authoritative_markdown`
- Result is NOT from a forbidden collection

```python
from qdrant_client import QdrantClient
from rag_tools.embeddings import get_embedding_model

client = QdrantClient(host='localhost', port=6333)
model = get_embedding_model()

FORBIDDEN = {'default', 'documents', 'knowledge', 'rag__all', 'rag__wiki_all', 'rag__global_all_docs'}
REQUIRED_FIELDS = {'source_file', 'heading', 'section_path', 'collection', 'authority'}

test_queries = [
    "<query-1-relevant-to-domain>",
    "<query-2-relevant-to-domain>",
    "<query-3-edge-case-or-boundary>",
]

for query in test_queries:
    vector = model.encode(query).tolist()
    results = client.search(
        collection_name="rag__wiki_<DOMAIN_SLUG>",
        query_vector=vector,
        query_filter={"must": [{"key": "wiki_domain", "match": {"value": "<DOMAIN_SLUG>"}}]},
        limit=3,
        with_payload=True,
    )
    for r in results:
        p = r.payload or {}
        missing = REQUIRED_FIELDS - set(p.keys())
        if missing:
            print(f"FAIL: missing citation fields: {missing}")
        if p.get('collection') in FORBIDDEN:
            print(f"FAIL: result from forbidden collection: {p.get('collection')}")
```

**Pass criteria:** All results have complete citation fields. No results from forbidden collections.

## Step 3 — Isolation check

Verify the `wiki_domain` filter correctly excludes wrong-domain results:

```python
# This should return 0 results
results_wrong = client.search(
    collection_name="rag__wiki_<DOMAIN_SLUG>",
    query_vector=vector,
    query_filter={"must": [{"key": "wiki_domain", "match": {"value": "WRONG_DOMAIN_TEST"}}]},
    limit=3,
)
print(f"Filter isolation: {'PASS' if len(results_wrong) == 0 else 'FAIL'} ({len(results_wrong)} results with wrong domain filter)")
```

**Pass criteria:** 0 results when filtering by a non-existent domain.

## Step 4 — Insufficient evidence behaviour

Run a query clearly outside the domain's scope:

```python
vector_unrelated = model.encode("completely unrelated topic outside domain scope").tolist()
results_unrelated = client.search(
    collection_name="rag__wiki_<DOMAIN_SLUG>",
    query_vector=vector_unrelated,
    limit=3,
)
if results_unrelated:
    top_score = results_unrelated[0].score
    if top_score > 0.7:
        print(f"WARN: high-score match ({top_score:.3f}) on unrelated query — collection may be noisy")
    else:
        print(f"OK: low score ({top_score:.3f}) on unrelated query (expected)")
else:
    print("OK: no match on unrelated query (expected)")
```

**Agent behaviour contract:** When scores are low (< 0.4), agents must say "insufficient evidence found in declared sources" — not speculate or blend sources.

## Step 5 — Forbidden collection audit

Verify no forbidden collections exist in Qdrant:

```python
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
FORBIDDEN = {'default', 'documents', 'knowledge', 'main', 'rag__all', 'rag__wiki_all', 'rag__global_all_docs'}
cols = [c.name for c in client.get_collections().collections]
hits = [c for c in cols if c in FORBIDDEN]
print('FAIL: forbidden collections found:', hits) if hits else print('PASS: no forbidden collections')
```

## Verdict output

```
Verdict: RETRIEVAL_VALIDATED | RETRIEVAL_PARTIAL | RETRIEVAL_NOT_READY

Collection:  rag__wiki_<DOMAIN_SLUG>
Vectors:     <count>

Query 1: <text>
  Results: <count>  Top score: <score>
  Citation complete: PASS | FAIL (missing: <fields>)
  Collection correct: PASS | FAIL

Query 2: <text>  (same format)
Query 3: <text>  (same format)

Filter isolation: PASS | FAIL
Forbidden collections in results: <list or "none">
Insufficient-evidence handling: PASS | WARN

Checks passed:  <list>
Checks failed:  <list or "none">
```

- `RETRIEVAL_VALIDATED` — all queries returned correct results, all citations complete, isolation confirmed
- `RETRIEVAL_PARTIAL` — some queries returned results but citation fields missing or scores low
- `RETRIEVAL_NOT_READY` — collection empty, isolation failed, or forbidden collections found

## Failure responses

| Failure | Guide |
|---|---|
| Collection empty | `guides/failure-mode-reference.md` FM-01/FM-02 |
| Citations missing fields | Re-index with correct metadata — check rag-tools indexer config |
| Filter isolation failure | Re-index with correct `wiki_domain` metadata on all chunks |
| Forbidden collection found | Delete it, re-index with correct name per ADR-001 |
| High score on unrelated query | Review and cull domain content — collection may have off-topic material |

## Related

- [prompts/06-post-index-retrieval-validation.md](../../prompts/06-post-index-retrieval-validation.md)
- [checklists/retrieval-validation.md](../../checklists/retrieval-validation.md)
- [guides/failure-mode-reference.md](failure-mode-reference.md)
- [specs/qdrant-query-filter-contract.md](../specs/qdrant-query-filter-contract.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
````

## File: .archcore/guides/wiki-domain-creation.md
````markdown
---
title: Wiki Domain Creation Guide
status: accepted
date: 20260524
provenance: prompts/01-create-wiki-domain.md, schemas/wiki-domain-registry.schema.yaml
---

# Wiki Domain Creation Guide

Step-by-step guide for creating a new wiki domain. This guide creates the directory structure and registers the domain. It does **not** index the domain into Qdrant — that is a separate step (see `guides/new-project-onboarding.md` Step 7, or `prompts/05-index-wiki-domain.md`).

## Contents

- [Prerequisites](#prerequisites)
- [Pre-flight check](#pre-flight-check)
- [Step 1 — Create domain directory structure](#step-1--create-domain-directory-structure)
- [Step 2 — Create domain index page](#step-2--create-domain-index-page)
- [Step 3 — Register domain in domain-registry.yaml](#step-3--register-domain-in-domain-registryyaml)
- [Step 4 — Update wiki index.md](#step-4--update-wiki-indexmd)
- [Step 5 — Update wiki log.md](#step-5--update-wiki-logmd)
- [Step 6 — Validate](#step-6--validate)
- [Output and next steps](#output-and-next-steps)

## Prerequisites

- `DOMAIN_SLUG` chosen: lowercase alphanumeric, e.g. `nbn`, `vocus`, `mcp`
- `DOMAIN_NAME` chosen: human-readable, e.g. `NBN`, `Vocus`
- `DOMAIN_DESCRIPTION` written: one sentence describing what knowledge the domain contains
- Wiki operational state confirmed (see `checklists/wiki-operational-readiness.md`)

## Pre-flight check

```bash
# Verify domain does not already exist
ls /Volumes/Data/_ai/_wiki/wiki_stuff/domains/
grep "domain: \"<DOMAIN_SLUG>\"" /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml 2>/dev/null \
  && echo "WARN: domain already in registry — stop" || echo "OK: not yet registered"
```

If domain already exists and has content: stop, do not recreate.

## Step 1 — Create domain directory structure

```bash
DOMAIN="<DOMAIN_SLUG>"
WIKI_DOMAINS="/Volumes/Data/_ai/_wiki/wiki_stuff/domains"

mkdir -p "$WIKI_DOMAINS/$DOMAIN/references"
```

Creates:
- `domains/<DOMAIN_SLUG>/` — domain root
- `domains/<DOMAIN_SLUG>/references/` — curated reference articles directory

## Step 2 — Create domain index page

Create: `/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<DOMAIN_SLUG>/index.md`

Use `templates/wiki-domain-index.md` as the template. Populate:
- `title`: `<Domain Name> Domain Index`
- `domain`: `<DOMAIN_SLUG>`
- `updated`: today's date (YYYYMMDD)
- Purpose, scope, and exclusions appropriate to this domain

Do not invent content. Write only what is known from governance context or explicit instruction.

## Step 3 — Register domain in domain-registry.yaml

Read the current registry first:

```bash
cat /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml
```

Append under the `domains:` list — **do not modify existing entries**:

```yaml
  - domain: "<DOMAIN_SLUG>"
    slug: "<DOMAIN_SLUG>"
    description: "<DOMAIN_DESCRIPTION>"
    source_paths:
      - "domains/<DOMAIN_SLUG>"
    qdrant_collection: "rag__wiki_<DOMAIN_SLUG>"
    status: "active"
```

Confirm `qdrant_collection` exactly matches `rag__wiki_<DOMAIN_SLUG>`. See `specs/wiki-domain-registry-contract.md`.

## Step 4 — Update wiki index.md

Append a line for the new domain to `/Volumes/Data/_ai/_wiki/wiki_stuff/index.md` under the domains section.

## Step 5 — Update wiki log.md

Append an entry to `/Volumes/Data/_ai/_wiki/wiki_stuff/log.md`:

```
YYYY-MM-DD  Created domain: <DOMAIN_SLUG> — <DOMAIN_DESCRIPTION>
```

## Step 6 — Validate

```bash
python3 -c "
import yaml
with open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)
found = [d for d in reg['domains'] if d['slug'] == '<DOMAIN_SLUG>']
print('PASS: domain registered' if found else 'FAIL: domain not found in registry')
"

test -f /Volumes/Data/_ai/_wiki/wiki_stuff/domains/<DOMAIN_SLUG>/index.md \
  && echo "PASS: index.md exists" || echo "FAIL: index.md missing"
```

## Output and next steps

After successful creation:

```
Files created:
  - domains/<DOMAIN_SLUG>/index.md
  - domains/<DOMAIN_SLUG>/references/  (empty)

Files modified:
  - wiki-data/domain-registry.yaml  (appended entry)
  - wiki_stuff/index.md             (appended line)
  - wiki_stuff/log.md               (appended entry)
```

Next: add curated reference articles to `domains/<DOMAIN_SLUG>/references/`, then index the domain (Step 7 of `guides/new-project-onboarding.md`, or `prompts/05-index-wiki-domain.md`).

## Related

- [prompts/01-create-wiki-domain.md](../../prompts/01-create-wiki-domain.md)
- [specs/wiki-domain-registry-contract.md](../specs/wiki-domain-registry-contract.md)
- [templates/wiki-domain-index.md](../../templates/wiki-domain-index.md)
- [templates/wiki-domain-registry-entry.yaml](../../templates/wiki-domain-registry-entry.yaml)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
````

## File: .archcore/rules/retrieval-isolation-rules.md
````markdown
---
title: Retrieval Isolation Rules
status: accepted
date: 20260524
provenance: SKILL.md, docs/authority-model.md, docs/multi-project-model.md, AGENTS.md
---

# Retrieval Isolation Rules

These rules govern agent and operator behaviour in the wiki/project RAG bridge. All rules are blocking — violation requires refusal or immediate stop, not a warning.

## Contents

- [Collection naming rules](#collection-naming-rules)
- [Query isolation rules](#query-isolation-rules)
- [Indexing rules](#indexing-rules)
- [Data segregation rules](#data-segregation-rules)
- [Embedding rules](#embedding-rules)
- [Agent refusal rules](#agent-refusal-rules)

## Collection naming rules

- **RULE-N1:** All project collections must be named `rag__project_<project_slug>`. No exceptions.
- **RULE-N2:** All wiki domain collections must be named `rag__wiki_<domain_slug>`. No exceptions.
- **RULE-N3:** Test collections must use `rag__test_<purpose>_<yyyymmdd>` and be deleted after use.
- **RULE-N4:** Forbidden collection names (`rag__global_all_docs`, `rag__wiki_all`, `rag__all`, `default`, `documents`, `knowledge`, `main`, `wiki`, `test`) must never exist in production. Any found must be deleted.
- **RULE-N5:** `<project_slug>` must be lowercase alphanumeric + underscores only. No hyphens, spaces, uppercase.
- **RULE-N6:** `<project_slug>` must match `project_slug` in `retrieval-policy.yaml`. Mismatches are policy violations.

## Query isolation rules

- **RULE-Q1:** A project may only query wiki domains declared in its `retrieval-policy.yaml` under `allowed_wiki_domains`. Undeclared domains are forbidden.
- **RULE-Q2:** Every query to a wiki collection must include a `wiki_domain` filter matching the domain slug. Unfiltered wiki queries are policy violations.
- **RULE-Q3:** Every query to a project collection must include a `project_slug` filter. Unfiltered project queries are policy violations.
- **RULE-Q4:** No project may query another project's `rag__project_*` collection. Cross-project fallback is forbidden.
- **RULE-Q5:** If a project's collection returns no results, the agent must ask the user — not fall back to another project or to a global search.

## Indexing rules

- **RULE-I1:** Always run `rag-index-domain-dry` (dry-run) before any live indexing operation. Do not skip.
- **RULE-I2:** Index exactly one wiki domain per operation. Multi-domain batching in a single run is forbidden.
- **RULE-I3:** Do not index raw or sensitive project data into wiki collections (`rag__wiki_*`).
- **RULE-I4:** Verify chunk count from dry-run matches vectors_count after live indexing. Mismatch indicates FM-02 (silent failure).
- **RULE-I5:** Work through `checklists/indexing-readiness.md` as a blocking gate before running any indexing operation.

## Data segregation rules

- **RULE-D1:** Project-specific facts belong in project-local files and `rag__project_<slug>`. They must not enter wiki collections.
- **RULE-D2:** Shared reference facts belong in wiki markdown (`_wiki/wiki_stuff/domains/<domain>/`) and `rag__wiki_<domain>`.
- **RULE-D3:** Qdrant payloads are retrieval artefacts only. When citing, always cite the source file — not the Qdrant payload.
- **RULE-D4:** Every indexed chunk must carry `authority` metadata: `shared_reference_authoritative_markdown`, `project_local`, `project_generated`, or `routing_metadata_only`.

## Embedding rules

- **RULE-E1:** The embedding model is locked to `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **RULE-E2:** Collections indexed with different models must not be queried together. Model mismatch silently degrades retrieval quality.
- **RULE-E3:** When re-indexing a collection after a model change, delete the old collection first — do not append to it.

## Agent refusal rules

- **RULE-R1:** Refuse any request for unrestricted global wiki search. Explain why isolation is required.
- **RULE-R2:** Refuse any request to bypass `retrieval-policy.yaml` or Qdrant isolation rules.
- **RULE-R3:** Refuse to create collections with forbidden names. Propose the correct name instead.
- **RULE-R4:** Refuse to run live indexing without a prior dry-run confirmation from the operator.
- **RULE-R5:** Refuse to skip checklist gates. State which checklist gate applies before proceeding.

## Related

- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
````

## File: .archcore/rules/workflow-sequencing-rules.md
````markdown
---
title: Workflow Sequencing Rules
status: accepted
date: 20260524
provenance: SKILL.md, checklists/
---

# Workflow Sequencing Rules

These rules govern the sequencing and gating of the bridge setup workflow. Each step has a corresponding prompt and optional checklist gate that must be passed before proceeding.

## Sequence enforcement

- **RULE-W1:** Execute prompts in sequence (00 → 01 → 02 → 03 → 04 → 04b → 04c → 05 → 06). Do not skip steps or run them out of order.
- **RULE-W2:** Each checklist gate is a blocking gate — work through every item before marking it passed. Do not treat checklists as post-hoc review.
- **RULE-W3:** Steps 00 and 02 (wiki operational state, rag-tools verification) must pass before any indexing or bridge creation.
- **RULE-W4:** Step 04 (validate policy) must pass before any indexing (step 05).
- **RULE-W5:** Step 05 requires a dry-run confirmation before live indexing. The operator must explicitly confirm after reviewing dry-run output.
- **RULE-W6:** Step 04b (profile-and-recommend-strategy) must complete before deciding whether to index a project document or use direct structured/table lookup. Do not default to vector RAG for structured or tabular sources.
- **RULE-W7:** Every retrieval operation must return an EvidenceBundle. Answer only from the bundle's `excerpt` and `section_path` fields — never from training knowledge. If no bundle is returned, report `RETRIEVAL_NOT_READY` and stop.

## Checklist gate mapping

| Step | Prompt | Blocking checklist |
|---|---|---|
| 0 | `prompts/00-verify-wiki-operational-state.md` | `checklists/wiki-operational-readiness.md` |
| 2 | `prompts/02-verify-rag-tools.md` | `checklists/rag-tools-readiness.md` |
| 3 | `prompts/03-create-project-bridge.md` | `checklists/project-bridge-readiness.md` |
| 4b | `prompts/02b-profile-and-recommend-strategy.md` | profile gate in `checklists/indexing-readiness.md` |
| 4c | `prompts/02c-benchmark-retrieval-routes.md` | benchmark results in `retrieval-strategy.yaml` |
| 5 | `prompts/05-index-wiki-domain.md` | `checklists/indexing-readiness.md` |
| 6 | `prompts/06-post-index-retrieval-validation.md` | `checklists/retrieval-validation.md` |
| New project | Multi-project audit | `checklists/multi-project-isolation.md` |

## Template and schema rules

- **RULE-T1:** Always start bridge files from `templates/` — never write from scratch.
- **RULE-T2:** Validate all YAML bridge files against `schemas/` before accepting them.
- **RULE-T3:** Do not edit template files when working in a project context. Use templates as copy-and-fill starting points.
- **RULE-T4:** Schema validation is mandatory before running `rag-tools validate-policy`.

## Related

- [SKILL.md](../../SKILL.md)
- [checklists/](../../checklists/)
- [prompts/](../../prompts/)
- [retrieval-isolation-rules.md](retrieval-isolation-rules.md)
````

## File: .archcore/specs/document-profile-contract.md
````markdown
---
title: Document Profile Contract
status: accepted
date: 20260525
provenance: schemas/document-profile.schema.yaml, SKILL.md
---

# Document Profile Contract

## Purpose

A document profile is the output of `rag-tools profile-file <path>`. It records structural features used by `rag-tools recommend-strategy` to select retrieval modes. Profiles are stored in `<project>/rag/source-profiles/<document_id>.yaml` and are required before any indexing or strategy decision.

## CLI command

```bash
source .venv/bin/activate
rag-tools profile-file <path> [--output <project>/rag/source-profiles/<document_id>.yaml]
```

## Required fields

| Field | Type | Description |
|---|---|---|
| `document_id` | string | File stem (no extension) — must match filename in `retrieval-strategy.yaml` |
| `title` | string | First heading text, or file stem if no headings |
| `path` | string | Absolute path to the source file — never a Qdrant collection path |
| `file_type` | string | Extension including dot (`.md`, `.csv`, `.pdf`, etc.) |
| `size_bytes` | integer | File size — zero if missing |
| `line_count` | integer | Number of lines |
| `estimated_tokens` | integer | Rough token count for chunking decisions |
| `document_class` | string | Classification from `_document_class()` — see allowed values |
| `has_headings` | boolean | |
| `heading_count` | integer | |
| `heading_levels` | list[integer] | Sorted heading depths (e.g. `[1, 2, 3]`) |
| `has_tables` | boolean | |
| `table_count` | integer | |
| `has_section_ids` | boolean | True if structured IDs like "C2.11" detected |
| `section_ids` | list[string] | Sorted list of detected section ID strings |
| `authoritative` | boolean | Always `true` for project source files |
| `recommended_retrieval_modes` | list[string] | Ordered list from `_recommended_modes()` |
| `index_allowed` | boolean | Always `false` from `profile-file` — only updated after benchmark decision |
| `notes` | list[string] | Optional profiler notes or manual annotations |

## Allowed `document_class` values

`structured_markdown_reference` | `legal_contract_or_terms` | `financial_rate_card` | `invoice_or_billing_report` | `operational_runbook` | `policy_document` | `meeting_notes` | `knowledge_article` | `source_code_docs` | `unstructured_pdf` | `scanned_pdf` | `tabular_dataset` | `mixed_content` | `unknown`

`unknown` requires manual classification before strategy can proceed.

## Critical constraints

- `contains_sensitive_data: true` always blocks indexing — `index_allowed` must remain `false`.
- `index_allowed` from `profile-file` is always `false`. Do not override at profile stage.
- `document_class: unknown` — re-run `profile-file` or classify manually before writing strategy.
- `document_id` must match the file stem exactly — mismatch breaks `retrieval-strategy.yaml` lookups.
- `path` must be absolute — required for reliable source citation.

## Storage convention

```
<project>/
  rag/
    source-profiles/
      <document_id>.yaml    # one file per profiled document
```

## Template

See `templates/source-profile.yaml`.

## Related

- [schemas/document-profile.schema.yaml](../../schemas/document-profile.schema.yaml)
- [schemas/retrieval-strategy.schema.yaml](../../schemas/retrieval-strategy.schema.yaml)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
````

## File: .archcore/specs/evidence-bundle-contract.md
````markdown
---
title: EvidenceBundle Contract
status: accepted
date: 20260525
provenance: schemas/evidence-bundle.schema.yaml, docs/evidence-contract.md, SKILL.md
---

# EvidenceBundle Contract

## Purpose

`EvidenceBundle` is the required output of every rag-tools retrieval operation. The LLM must answer only from EvidenceBundle content — never from training knowledge. Exact amounts, dates, clause references, and identifiers must not be inferred; they must come from the `excerpt` field. If no valid EvidenceBundle is returned, the agent must report `RETRIEVAL_NOT_READY` and stop.

## Required fields

| Field | Type | Description |
|---|---|---|
| `query` | string | The exact original query or lookup term submitted |
| `retrieval_mode` | string | Mode that produced this bundle (must reflect actual mode used) |
| `excerpt` | string | Verbatim text extracted from the source file — the ONLY field the LLM may answer from |
| `source_file` | string | Absolute path to the canonical source file — never a Qdrant collection name |

## Allowed `retrieval_mode` values

- `direct_structured_lookup`
- `section_clause_lookup`
- `heading_aware_lookup`
- `table_aware_lookup`
- `tabular_analytics`
- `keyword_lookup`
- `vector_rag`
- `hybrid_direct_first`
- `hybrid_rag_first`

## Notable optional fields

| Field | Type | Use |
|---|---|---|
| `document_id` | string | File stem — strongly recommended for citation |
| `authority` | string | `source` / `wiki_article` / `external_reference` / `derived` |
| `section_id` | string | Structured section ID (e.g. "C2.11") — enables exact clause-level citation |
| `section_path` | list[string] | Heading chain from root to matched section |
| `heading` | string | Nearest heading above matched text |
| `table_id` | string | Table identifier — required for `table_aware_lookup` results |
| `row_keys` | list[string] | Short row-key preview for matched table rows |
| `score_or_confidence` | float | Cosine similarity (RAG) or 1.0 (exact match) |
| `retrieval_warnings` | list[string] | Populated when: source missing, fallback used, low score, partial match |

## Answer rules

1. Answer only from `excerpt` content — never from training knowledge.
2. Do not infer amounts, dates, identifiers, or clause text not present in the excerpt.
3. If evidence is missing for a fact, state "not found in retrieved evidence" — do not guess.
4. Qdrant payloads are retrieval artifacts. `source_file` is the authority, not the collection name.
5. When multiple bundles are returned, cite each separately by `source_file` + `section_id`/`heading`.
6. Do not merge conflicting excerpts into a single answer — report the conflict.
7. `retrieval_warnings` must be surfaced in the answer when present.

## Citation requirements

- **Minimum:** `source_file` (required)
- **Preferred:** `source_file` + (`section_id` OR `heading` OR `table_id`)
- **Full:** `source_file` + `section_path` + `section_id` + excerpt snippet
- For table results: include `table_id` and relevant `row_keys`

## Invalid bundle conditions

- `excerpt` is empty with no `retrieval_warning` — do not answer from it
- `source_file` is a Qdrant collection name, not a file path — invalid citation
- `retrieval_warnings` missing despite fallback or low score — silent failure

## Validation checklist

See `checklists/evidence-bundle-validation.md`.

## Related

- [schemas/evidence-bundle.schema.yaml](../../schemas/evidence-bundle.schema.yaml)
- [docs/evidence-contract.md](../../docs/evidence-contract.md)
- [checklists/evidence-bundle-validation.md](../../checklists/evidence-bundle-validation.md)
- [templates/evidence-bundle.yaml](../../templates/evidence-bundle.yaml)
````

## File: .archcore/specs/project-context-yaml-contract.md
````markdown
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
````

## File: .archcore/specs/project-documents-yaml-contract.md
````markdown
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
````

## File: .archcore/specs/qdrant-query-filter-contract.md
````markdown
---
title: Qdrant Query Filter Contract
status: accepted
date: 20260524
provenance: docs/authority-model.md, docs/multi-project-model.md, SKILL.md
---

# Qdrant Query Filter Contract

## Purpose

Every Qdrant query in the RAG bridge must include a metadata filter to enforce isolation. Unfiltered queries are policy violations even if they return correct results — the isolation guarantee depends on the filter being present, not on Qdrant's access controls.

## Required filters by collection type

### Project collection query

```python
# Collection: rag__project_<slug>
filter = {
    "must": [
        {"key": "project_slug", "match": {"value": "<project_slug>"}}
    ]
}
```

### Wiki domain collection query

```python
# Collection: rag__wiki_<domain>
filter = {
    "must": [
        {"key": "wiki_domain", "match": {"value": "<domain_slug>"}}
    ]
}
```

## Required citation metadata

Every result returned to an agent must carry:

| Field | Description | Required |
|---|---|---|
| `source_file` | Absolute or repo-relative path to the indexed markdown file | Yes |
| `section_path` | Heading path within the file (e.g. `## Authority > Rule 1`) | Yes |
| `collection` | Name of the Qdrant collection the result came from | Yes |
| `authority` | Authority label (`shared_reference_authoritative_markdown`, `project_local`, etc.) | Yes |
| `wiki_domain` | Domain slug (wiki collections only) | Conditional |
| `project_slug` | Project slug (project collections only) | Conditional |

## Multi-collection query pattern

When a project declares multiple wiki domains, query each separately and merge results:

```python
# Correct — separate queries per collection
for domain in allowed_wiki_domains:
    collection = f"rag__wiki_{domain}"
    results = client.search(collection, query_vector, query_filter={
        "must": [{"key": "wiki_domain", "match": {"value": domain}}]
    })

# Wrong — single global search across all collections
# client.search("rag__all", ...) — FORBIDDEN
```

## Validation

Before returning results to an agent:

1. Confirm filter was applied (not None or empty)
2. Confirm collection name matches naming convention
3. Confirm all results include `source_file`, `section_path`, `collection`, `authority`
4. Confirm no results from collections not in `allowed_wiki_domains` or `project_collection`

## Related

- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [ADR-003-authority-hierarchy.md](../adr/ADR-003-authority-hierarchy.md)
- [retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
````

## File: .archcore/specs/retrieval-policy-yaml-contract.md
````markdown
---
title: retrieval-policy.yaml Contract
status: accepted
date: 20260524
provenance: schemas/retrieval-policy.schema.yaml, SKILL.md, docs/multi-project-model.md
---

# retrieval-policy.yaml Contract

## Purpose

`retrieval-policy.yaml` is the single declaration of what a project is allowed to query. It lives at `<project>/rag/retrieval-policy.yaml`. It is validated by `rag-tools validate-policy` before any indexing or retrieval operation.

## Required fields

```yaml
project_slug: <lowercase_alphanumeric_underscores>      # unique project identifier
project_collection: rag__project_<project_slug>         # must follow naming convention
allowed_wiki_domains:                                   # explicit domain allowlist
  - <domain_slug_1>
  - <domain_slug_2>
wiki_collections:                                       # derived from allowed_wiki_domains
  - rag__wiki_<domain_slug_1>
  - rag__wiki_<domain_slug_2>
forbidden_collections:                                  # must include all globally forbidden names
  - rag__global_all_docs
  - rag__wiki_all
  - rag__all
  - default
  - documents
  - knowledge
  - main
```

## Constraints

- `project_slug` must be unique across all projects — check before creating
- `project_collection` must exactly match `rag__project_<project_slug>`
- `allowed_wiki_domains` must list only domain slugs that exist in `domain-registry.yaml`
- `wiki_collections` must be the derived set from `allowed_wiki_domains`
- `forbidden_collections` must include at minimum the globally forbidden set
- Do not add other projects' `rag__project_*` collections anywhere in this file

## Validation command

```bash
rag-tools validate-policy <project>/rag/retrieval-policy.yaml
```

The validator checks:
- All required fields present
- `project_collection` naming pattern valid
- All `wiki_collections` naming patterns valid
- No forbidden collection names used
- `allowed_wiki_domains` entries exist in registry

## Starter template

See `templates/retrieval-policy.yaml`.

## Related

- [schemas/retrieval-policy.schema.yaml](../../schemas/retrieval-policy.schema.yaml)
- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [ADR-002-multi-project-isolation-model.md](../adr/ADR-002-multi-project-isolation-model.md)
- [qdrant-query-filter-contract.md](qdrant-query-filter-contract.md)
````

## File: .archcore/specs/retrieval-strategy-yaml-contract.md
````markdown
---
title: retrieval-strategy.yaml Contract
status: accepted
date: 20260525
provenance: schemas/retrieval-strategy.schema.yaml, prompts/02b-profile-and-recommend-strategy.md
---

# retrieval-strategy.yaml Contract

## Purpose

`retrieval-strategy.yaml` is the per-project strategy configuration. It records the chosen primary, secondary, and fallback retrieval mode for each candidate document, along with RAG suitability, benchmark status, and the `index_allowed` gate. Produced by prompt 02b; updated by prompt 02c.

Lives at: `<project>/rag/retrieval-strategy.yaml`

## Required top-level structure

```yaml
version: 1
project:
  id: <string>
  slug: <lowercase_alphanumeric_underscores>    # matches Qdrant project slug
  name: <string>
strategy_defaults:
  exact_facts: <retrieval_mode>
  tables: <retrieval_mode>
  structured_sections: <retrieval_mode>
  cross_document_semantic: <retrieval_mode>
  invoices: <retrieval_mode>
  pdfs: <retrieval_mode>
documents:
  - <document_entry>   # one per candidate
rules:
  source_files_remain_authoritative: true    # must be true
  profile_before_index: true                 # must be true
  benchmark_before_default_route: true       # must be true
  evidence_bundle_required: true             # must be true
  vector_rag_not_universal_default: true     # must be true
```

## Required document entry fields

| Field | Type | Constraint |
|---|---|---|
| `document_id` | string | File stem (no extension) — must match source-profile filename |
| `path` | string | Relative path from project root |
| `document_class` | string | One of the 14 allowed values |
| `primary` | string | Primary retrieval mode |
| `rag_suitability` | string | `suitable` / `partially_suitable` / `not_suitable` |
| `benchmark_required` | boolean | Should be `true` for structured/tabular documents |
| `benchmark_status` | string | `not_run` / `passed` / `partial` / `failed` |
| `index_allowed` | boolean | Must be `false` unless `benchmark_status: passed` AND `rag_suitability` in (`suitable`, `partially_suitable`) |
| `reason` | string | Explains route selection — required for audit traceability |

## Optional document entry fields

- `authority`: `project_local` / `wiki_authoritative_markdown` / `external_reference`
- `secondary`: secondary retrieval mode
- `fallback`: fallback retrieval mode

## Forbidden combinations

- `index_allowed: true` without `benchmark_status: passed` — **forbidden**
- `rag_suitability: not_suitable` with `index_allowed: true` — **forbidden**
- `benchmark_required: false` for structured or tabular document — should be `true`
- Missing `reason` field — breaks audit traceability

## Template

See `templates/retrieval-strategy.yaml`.

## Example

See `examples/vocus-profitability/retrieval-strategy.yaml`.

## Related

- [schemas/retrieval-strategy.schema.yaml](../../schemas/retrieval-strategy.schema.yaml)
- [document-profile-contract.md](document-profile-contract.md)
- [prompts/02b-profile-and-recommend-strategy.md](../../prompts/02b-profile-and-recommend-strategy.md)
- [prompts/02c-benchmark-retrieval-routes.md](../../prompts/02c-benchmark-retrieval-routes.md)
````

## File: .archcore/specs/wiki-domain-registry-contract.md
````markdown
---
title: wiki-domain-registry.yaml Contract
status: accepted
date: 20260524
provenance: schemas/wiki-domain-registry.schema.yaml, docs/collection-naming-policy.md
---

# wiki-domain-registry.yaml Contract

## Purpose

`domain-registry.yaml` is the canonical registry of all wiki domains. It lives at `/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml`. Every valid wiki domain must be declared here before it can be referenced in any project's `retrieval-policy.yaml` or indexed into Qdrant.

## Required top-level keys

| Key | Type | Constraint |
|---|---|---|
| `version` | integer | Must be `1` |
| `wiki_root` | string | Must be `/Volumes/Data/_ai/_wiki` |
| `content_root` | string | Must be `/Volumes/Data/_ai/_wiki/wiki_stuff` |
| `domains` | list of objects | Each entry declares one wiki domain |
| `rules` | object | All four isolation rule flags must be present and `true` |

## rules object — all keys mandatory and must be true

| Key | Value |
|---|---|
| `disallow_global_collection` | `true` |
| `require_declared_domain` | `true` |
| `require_source_path` | `true` |
| `require_collection_per_domain` | `true` |

## domains list item required keys

| Key | Pattern | Notes |
|---|---|---|
| `domain` | lowercase string | Domain name, e.g. `nbn` |
| `slug` | `^[a-z0-9_]+$` | Used in collection names and filter values — usually matches `domain` |
| `description` | free string | Required — what knowledge this domain contains |
| `source_paths` | list of strings | Paths relative to `content_root`, e.g. `['domains/nbn']` |
| `qdrant_collection` | `^rag__wiki_[a-z0-9_]+$` | Must be `rag__wiki_<slug>` — one collection per domain |
| `status` | `active`, `draft`, `deprecated` | Only `active` domains are eligible for indexing |

## Domain status rules

- `active` — eligible for indexing and project declaration
- `draft` — not yet ready for indexing; may be declared but should not be queried
- `deprecated` — must not be queried by projects unless explicitly grandfathered

## Common failures

| Failure | Fix |
|---|---|
| `slug` and `qdrant_collection` suffix mismatch (e.g. `slug=nbn` but `collection=rag__wiki_nbn_v2`) | Fix collection to exactly match `rag__wiki_<slug>` |
| `status: active` but `source_paths` directory doesn't exist | Create the directory or set status to `draft` |
| `qdrant_collection: rag__wiki_all` | Forbidden global name — fix to `rag__wiki_<slug>` |
| Domain entry with no `description` | Add a description — required for human review and agent understanding |
| Adding a domain without updating wiki `index.md` and `log.md` | Update both files as part of domain creation (see prompt 01) |

## Modification rules

- Never modify existing domain entries without explicit operator authorization
- New domains are appended — do not reorder existing entries
- Slug must be globally unique across all domains
- `source_paths` must exist as directories under `wiki_stuff/` before indexing
- Deprecated domains keep their entries — do not delete them (projects may still reference them in history)

## Validation

```python
import yaml
with open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)

for d in reg['domains']:
    slug = d['slug']
    expected_col = f"rag__wiki_{slug}"
    assert d['qdrant_collection'] == expected_col, f"FAIL: {slug} collection mismatch"
    assert d['description'], f"FAIL: {slug} missing description"
    assert d['source_paths'], f"FAIL: {slug} missing source_paths"
print("PASS: all domain entries valid")
```

## Related

- [schemas/wiki-domain-registry.schema.yaml](../../schemas/wiki-domain-registry.schema.yaml)
- [prompts/01-create-wiki-domain.md](../../prompts/01-create-wiki-domain.md)
- [ADR-001-qdrant-collection-naming-convention.md](../adr/ADR-001-qdrant-collection-naming-convention.md)
- [specs/retrieval-policy-yaml-contract.md](retrieval-policy-yaml-contract.md)
````

## File: checklists/dynamic-retrieval-readiness.md
````markdown
# Checklist: Dynamic Retrieval Readiness

**Use before:** attempting any rag-tools dynamic retrieval command (profile-file,
recommend-strategy, structured-lookup, lookup-section, lookup-table, benchmark-file).

All items marked BLOCKING must pass. WARN items should be resolved before production use.

---

## rag-tools dynamic commands available

- [ ] BLOCKING: rag-tools venv exists at `tools-working-cache/rag-tools/.venv`
- [ ] BLOCKING: `rag-tools --help` runs without error
- [ ] BLOCKING: `rag-tools profile-file --help` is listed (dynamic retrieval layer present)
- [ ] BLOCKING: `rag-tools recommend-strategy --help` is listed
- [ ] BLOCKING: `rag-tools structured-lookup --help` is listed
- [ ] BLOCKING: `rag-tools lookup-section --help` is listed
- [ ] BLOCKING: `rag-tools lookup-table --help` is listed
- [ ] BLOCKING: `rag-tools benchmark-file --help` is listed

Verify with:

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin
$VENV/rag-tools --help | grep -E "profile|recommend|structured|lookup|benchmark"
```

Expected output includes: `profile-file`, `profile-project`, `recommend-strategy`,
`structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`.

---

## EvidenceBundle model available

- [ ] BLOCKING: `from rag_tools.evidence import EvidenceBundle` imports without error
- [ ] BLOCKING: EvidenceBundle has required fields: `query`, `retrieval_mode`, `source_file`,
  `excerpt`, `retrieval_warnings`

Verify with:

```bash
$VENV/python -c "
from rag_tools.evidence import EvidenceBundle
b = EvidenceBundle(query='test', retrieval_mode='direct_structured_lookup')
print('OK:', b.model_fields.keys())
"
```

---

## profile-file / profile-project working

- [ ] BLOCKING: `rag-tools profile-file <file>` returns JSON with `document_class` and
  `recommended_retrieval_modes`
- [ ] BLOCKING: `rag-tools profile-project <dir>` returns a list of profile dicts
- [ ] WARN: profile-file on a missing file returns a zero-field profile (not an exception)

---

## recommend-strategy working

- [ ] BLOCKING: `rag-tools recommend-strategy <file>` returns JSON with `primary`, `secondary`,
  `fallback`, `rag_suitability`, and `reason`
- [ ] BLOCKING: `rag_suitability` is one of: `suitable`, `partially_suitable`, `not_suitable`

---

## structured-lookup working

- [ ] BLOCKING: `rag-tools structured-lookup <file> <query>` returns a JSON list of
  EvidenceBundle dicts
- [ ] BLOCKING: Each bundle has `source_file`, `excerpt`, `heading` or `section_id`
- [ ] WARN: Empty list is valid for a query with no match — confirms fallback behavior

---

## lookup-section working

- [ ] BLOCKING: `rag-tools lookup-section <file> <section-id>` returns a JSON list
- [ ] BLOCKING: Result bundle has `section_id` matching the requested ID when found
- [ ] WARN: Missing section returns a bundle with `retrieval_warnings: ["source file missing"]`
  or an empty list — check which your version returns

---

## lookup-table working

- [ ] BLOCKING: `rag-tools lookup-table <file> <query>` returns a JSON list of EvidenceBundle
  dicts for table matches
- [ ] BLOCKING: Each bundle has `table_id` and `row_keys`
- [ ] WARN: Empty list is valid when no table rows match the query terms

---

## benchmark-file working

- [ ] BLOCKING: `rag-tools benchmark-file <file> --queries <query-file>` returns JSON with
  `source_file`, `results`, `recommendation`
- [ ] BLOCKING: `recommendation` is one of the valid route labels:
  `DIRECT_FIRST`, `TABLE_LOOKUP_FIRST`, `HYBRID_DIRECT_FIRST`, `HYBRID_RAG_FIRST`,
  `RAG_FIRST`, `NOT_READY_NEEDS_EXTRACTION`, `NOT_READY_NEEDS_MORE_INDEXED_CONTENT`
- [ ] WARN: Running with `--modes rag` when no Qdrant collection exists results in `pass: false`
  and `fallback_needed: true` for all RAG rows — this is expected, not an error

---

## Project has retrieval-strategy.yaml

- [ ] BLOCKING (for project-side indexing): `rag/retrieval-strategy.yaml` exists in project root
- [ ] BLOCKING: Every candidate document has `document_class` and `rag_suitability` recorded
- [ ] BLOCKING: Every `index_allowed: true` entry has `benchmark_status: passed`
- [ ] WARN: Documents with `document_class: unknown` require manual classification

---

## Answers are evidence-bundle constrained

- [ ] BLOCKING: Agent answers from `excerpt` field only — no training-knowledge fill-in
- [ ] BLOCKING: `retrieval_warnings` are surfaced when present — not silently consumed
- [ ] BLOCKING: `source_file` is cited in every answer
- [ ] WARN: When no bundle is returned, agent reports `RETRIEVAL_NOT_READY` and stops

---

## Verdict

```
DYNAMIC_RETRIEVAL_READY    — all BLOCKING checks pass
DYNAMIC_RETRIEVAL_PARTIAL  — one or more WARN items unresolved; dynamic retrieval usable with care
DYNAMIC_RETRIEVAL_NOT_READY — one or more BLOCKING checks fail; do not use dynamic retrieval
```
````

## File: checklists/evidence-bundle-validation.md
````markdown
# Checklist: Evidence Bundle Validation

**Use when:** reviewing retrieval results before passing them to an LLM for answer generation,
or auditing whether a rag-tools retrieval command produced valid evidence.

All items marked BLOCKING must pass before the evidence is used in an answer.

---

## Required fields present

- [ ] BLOCKING: `source_file` is present and is an absolute path to a real file (not a
  Qdrant collection name, not a relative path, not a URL)
- [ ] BLOCKING: `excerpt` is present and non-empty
- [ ] BLOCKING: `retrieval_mode` is present and is one of the allowed values
- [ ] BLOCKING: `query` is present and matches the original query

---

## Source grounding

- [ ] BLOCKING: `excerpt` is verbatim text from the source file — no generated conclusions
- [ ] BLOCKING: `excerpt` contains no invented amounts, dates, identifiers, or clause text
  that cannot be verified in the source
- [ ] BLOCKING: `source_file` points to the canonical authoritative source (not a derived
  wiki article when the project source is available)
- [ ] BLOCKING: If `retrieval_mode` is `vector_rag`, the `source_file` is cited (not the
  Qdrant collection name)

---

## Heading or section location present

- [ ] BLOCKING (for structured/section/table modes): At least one of the following is present:
  `section_id`, `heading`, `section_path` (non-empty), or `table_id`
- [ ] WARN: For `vector_rag` mode, `heading` or `section_path` may be absent — acceptable,
  but should be present if the source supports it
- [ ] WARN: For `keyword_lookup` mode, `section_id` and `heading` may be absent — acceptable

---

## Citation usable by LLM

- [ ] BLOCKING: A citation can be constructed from the bundle that includes at minimum:
  `source_file` + one of (`section_id`, `heading`, `table_id`)
- [ ] WARN: If only `source_file` is present (no section/heading/table), the citation is
  file-level only — acceptable but imprecise; note in answer
- [ ] BLOCKING: `document_id` matches the file stem of `source_file` when both are present

---

## Context chars calculated

- [ ] BLOCKING: `context_chars` equals `len(excerpt)` (or 0 if excerpt is empty)
- [ ] WARN: `context_chars` of 0 with no `retrieval_warnings` is suspicious — should have
  a warning like "no matching content found"

---

## Warnings populated when needed

- [ ] BLOCKING: `retrieval_warnings` is populated (not missing) for any of these conditions:
  - source file was missing at retrieval time
  - retrieval fell back from primary to secondary mode
  - RAG score < 0.5
  - structured lookup found no exact section ID match
  - table match is header-only with no row match
  - `fallback_needed: true` in benchmark result
- [ ] WARN: An empty `retrieval_warnings` list is valid when retrieval succeeded cleanly

---

## No generated conclusions inside evidence

- [ ] BLOCKING: `excerpt` does not contain LLM-synthesized text (i.e. text that was not in
  the source file)
- [ ] BLOCKING: `excerpt` does not start with phrases like "Based on...", "This suggests...",
  "According to the data..." — these are LLM answer patterns, not source excerpts
- [ ] BLOCKING: Amounts, percentages, dates, and identifiers in `excerpt` must appear verbatim
  in the source file at `source_file`

---

## Verdict

```
EVIDENCE_VALID       — all BLOCKING checks pass; bundle may be used for answer generation
EVIDENCE_PARTIAL     — WARN items unresolved; usable with explicit caveats in the answer
EVIDENCE_INVALID     — one or more BLOCKING checks fail; do not answer from this bundle;
                       report RETRIEVAL_NOT_READY
```

**When EVIDENCE_INVALID:** report the specific blocking failure, state "not found in retrieved
evidence" for any fact that depends on the failed bundle, and do not substitute training knowledge.
````

## File: checklists/indexing-readiness.md
````markdown
# Checklist: Indexing Readiness

**Use before:** running prompt 05 (index-wiki-domain) or 08 (index-project-documents).
All items marked BLOCKING must pass before live indexing. WARN items should be resolved.

---

## Profile and strategy gate

**This section must be checked first. All BLOCKING items here take precedence.**

- [ ] BLOCKING: `profile-file` or `profile-project` has been run on the candidate source(s).
- [ ] BLOCKING: A source profile exists for every candidate document or wiki article being indexed.
- [ ] BLOCKING: `recommend-strategy` has been run on every candidate document.
- [ ] BLOCKING: `rag/retrieval-strategy.yaml` exists in the project root where project-side
  indexing is planned.
- [ ] BLOCKING: Vector RAG is marked `suitable` or `partially_suitable` for every candidate before
  its `index: true` flag is set in the manifest.
- [ ] BLOCKING: For any document classified `structured_markdown_reference`, `financial_rate_card`,
  `invoice_or_billing_report`, or `tabular_dataset`: benchmark has been run (prompt 02c) or
  indexing is explicitly deferred to direct/table lookup.
- [ ] BLOCKING: Direct or table lookup is preferred as primary route where the benchmark shows it
  outperforms vector RAG.
- [ ] BLOCKING: EvidenceBundle output path is documented in `rag/retrieval-strategy.yaml`.
- [ ] WARN: Scaffold-only wiki domain indexing (no body content, no source references) produces
  low-value retrieval — add curated content (prompt 07) before indexing.
- [ ] WARN: Do not duplicate full source files into wiki summaries just to make RAG work. Use
  direct/structured lookup on the authoritative source instead.
- [ ] WARN: If RAG context reduction is needed for a structured source, it is a signal that
  structured lookup is more appropriate than vector RAG for that file.

---

## Domain content (wiki domain indexing)

- [ ] BLOCKING: `wiki_stuff/domains/<domain>/` exists
- [ ] BLOCKING: At least 1 `.md` file in domain directory
- [ ] WARN: `wiki_stuff/domains/<domain>/index.md` exists
- [ ] WARN: Each article has frontmatter with `domain:`, `title:`, `authority:` fields
- [ ] BLOCKING: At least 1 article has a `source:` reference (not scaffold-only)
- [ ] Spot-check: 3 random articles have `## Source references` section with content

## Collection name validity (both domain and project)

- [ ] BLOCKING: Collection name matches `rag__project_<slug>` or `rag__wiki_<domain>`
- [ ] BLOCKING: Collection name is NOT in forbidden list
- [ ] BLOCKING: Collection slug is lowercase alphanumeric + underscores only

## Policy validated

- [ ] BLOCKING: `rag/retrieval-policy.yaml` passes rag-tools validator (prompt 04)
- [ ] BLOCKING: `allowed_wiki_collections` includes the collection being indexed
- [ ] No forbidden collection names in policy

## RAG tools operational

- [ ] BLOCKING: External venv exists at `tools-working-cache/rag-tools/.venv`
- [ ] BLOCKING: `rag_tools.cli doctor` passes or reports PARTIAL with Qdrant-only issues
- [ ] BLOCKING: Qdrant running and reachable on localhost:6333

## Dry-run passed

- [ ] BLOCKING: Dry-run executed before live index
- [ ] BLOCKING: Dry-run chunk count > 0
- [ ] WARN: Dry-run chunk count is not suspiciously high (may indicate cross-domain bleed)
- [ ] BLOCKING: No files from other domains or projects in dry-run output
- [ ] BLOCKING: Collection name shown in dry-run matches target

## Content safety (project documents)

- [ ] BLOCKING: `rules.default_index: false` in project-documents.yaml
- [ ] BLOCKING: No `type: communication` or `type: raw` documents with `index: true` without approval notes
- [ ] BLOCKING: No `sensitive: true` document with `index: true`

---

## Verdict

```
INDEXING_READY    — all BLOCKING checks pass
INDEXING_NOT_READY — one or more BLOCKING checks fail
```

**Do not proceed to live indexing if any BLOCKING check fails.**
````

## File: checklists/multi-project-isolation.md
````markdown
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
````

## File: checklists/project-bridge-readiness.md
````markdown
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
````

## File: checklists/rag-tools-readiness.md
````markdown
# Checklist: RAG Tools Readiness

**Use before:** any indexing or retrieval operation.
**Blocks:** indexing if NOT_READY.

---

## External venv

- [ ] `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/` — exists
- [ ] `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python` — executable
- [ ] `python -c "import rag_tools"` — imports without error
- [ ] All core modules import: `paths`, `config`, `collections`, `policy`, `embeddings`

## UV sync

- [ ] `uv sync` with `UV_PROJECT_ENVIRONMENT` set runs without error
- [ ] Lock file (`uv.lock`) is present and current
- [ ] No conflicting `VIRTUAL_ENV` shell variable causing warnings (warn only — UV still works)

## Doctor

- [ ] `rag_tools.cli doctor` exits 0 or reports `RAG_TOOLS_READY`
- [ ] All 10 health checks pass:
  - Canonical directories
  - Config file (live or example fallback)
  - Python imports
  - LlamaIndex availability
  - Docker daemon
  - Qdrant connectivity
  - Embedding model (384-dim output)
  - Collection policy functions
  - Wiki roots
  - Domain registry

## Qdrant

- [ ] Docker context is set correctly (OrbStack, Colima, or Docker Desktop — whichever is running)
- [ ] `qdrant-status` confirms container running
- [ ] `localhost:6333` HTTP API responds (200 OK)
- [ ] `qdrant-collections` lists existing collections without error

## Embedding smoke test

- [ ] `scripts/embedding-smoke-test` completes without error
- [ ] Output confirms 384-dimensional vectors
- [ ] Model (`all-MiniLM-L6-v2`) loads from HuggingFace cache (no download required)

## Collection audit (no forbidden names)

- [ ] No collection named `default`, `documents`, `knowledge`, `main`
- [ ] No collection named `rag__all`, `rag__wiki_all`, `rag__global_all_docs`
- [ ] All existing collections match `rag__project_*`, `rag__wiki_*`, or `rag__test_*` patterns

## pytest

- [ ] `pytest tests/ -v` passes (all tests green) — WARN if skipped, FAIL if red

---

## Verdict

```
RAG_TOOLS_READY    — all checks pass
RAG_TOOLS_PARTIAL  — some checks failing (Qdrant down, venv issues, but imports work)
RAG_TOOLS_NOT_READY — venv missing, imports fail, or Qdrant unreachable
```
````

## File: checklists/retrieval-validation.md
````markdown
# Checklist: Retrieval Validation

**Use after:** indexing (prompt 05 or 08).
**Use with:** prompt 06 (post-index-retrieval-validation).

---

## Pre-query setup

- [ ] Collection exists in Qdrant
- [ ] Collection has vectors_count > 0
- [ ] Retrieval policy loaded and confirmed valid
- [ ] Embedding model loaded (same model used for indexing)

## Test queries

Run at least 3 queries. For each:

- [ ] At least 1 result returned (non-empty)
- [ ] Top result score > 0.4 (low scores suggest sparse/mismatched content)
- [ ] All results cite `collection` field
- [ ] All results cite `source_file` field
- [ ] All results cite `heading` field
- [ ] All results cite `section_path` field
- [ ] All results have `authority` field set

## Collection isolation

- [ ] All results come from the correct collection (`rag__wiki_<domain>` or `rag__project_<slug>`)
- [ ] No results from forbidden collections (`default`, `documents`, `rag__all`, etc.)
- [ ] `wiki_domain` filter correctly restricts results to declared domain only
- [ ] `project_slug` filter correctly restricts project collection results

## Filter enforcement

- [ ] Querying with `wiki_domain: WRONG_DOMAIN` returns 0 results
- [ ] Querying without required filters should not be possible (enforced by retrieval policy)

## Insufficient evidence behaviour

- [ ] Query on an unrelated topic returns low score (< 0.4) or no results
- [ ] Agent does NOT hallucinate an answer when no results found
- [ ] Agent explicitly states "insufficient evidence in declared sources" when results are poor
- [ ] Agent does NOT fall back to undeclared domains or global search

## Cross-collection contamination

- [ ] Results from `rag__wiki_nbn` contain only NBN-domain content
- [ ] Results from `rag__wiki_vocus` contain only Vocus-domain content
- [ ] Project collection does not contain wiki content (unless explicitly copied with source)

---

## Verdict

```
RETRIEVAL_VALIDATED    — all checks pass
RETRIEVAL_PARTIAL      — some queries succeed, some return empty or low quality
RETRIEVAL_NOT_READY    — all queries fail or forbidden collections appear in results
```
````

## File: checklists/wiki-operational-readiness.md
````markdown
# Checklist: Wiki Operational Readiness

**Use before:** any bridge creation, domain indexing, or retrieval work.
**Blocks:** all downstream prompts if NOT_READY.

---

## Directory structure

- [ ] `/Volumes/Data/_ai/_wiki/wiki_stuff/` — content vault exists
- [ ] `/Volumes/Data/_ai/_wiki/wiki-data/` — metadata layer exists
- [ ] `/Volumes/Data/_ai/_wiki/wiki-runtime/` — runtime area exists (WARN if absent)
- [ ] `/Volumes/Data/_ai/_wiki/wiki-working-cache/` — cache area exists (WARN if absent)

## Governance files

- [ ] `wiki_stuff/README.md` — exists
- [ ] `wiki_stuff/AGENTS.md` — exists
- [ ] `wiki_stuff/AI_NAVIGATION.md` — exists
- [ ] `wiki_stuff/SCHEMA.md` — exists
- [ ] `wiki_stuff/context-map.yaml` — exists and parses
- [ ] `wiki_stuff/index.md` — exists
- [ ] `wiki_stuff/log.md` — exists
- [ ] `wiki_stuff/CHANGELOG.md` — exists (WARN if absent)

## Metadata layer

- [ ] `wiki-data/domain-registry.yaml` — exists and parses as valid YAML
- [ ] `wiki-data/domain-registry.yaml` — has at least 1 active domain
- [ ] `wiki-data/domain-registry.yaml` — `disallow_global_collection: true` is set
- [ ] `wiki-data/qdrant-collection-policy.md` — exists
- [ ] `wiki-data/project-dependency-model.schema.yaml` — exists (WARN if absent)

## Domain directories

For each domain in the registry:
- [ ] `wiki_stuff/domains/<domain>/` — directory exists
- [ ] `wiki_stuff/domains/<domain>/index.md` — exists (WARN if absent)
- [ ] `wiki_stuff/domains/<domain>/` — contains at least 1 markdown file other than index

## Frontmatter hygiene

- [ ] Spot-check: at least 5 random wiki domain files parse frontmatter without error
- [ ] No domain file has `domain:` field set to a different domain

## Wikilinks

- [ ] Wikilinks (`[[...]]`) use valid slugs that correspond to existing files (spot-check)
- [ ] No broken `[[...]]` references in domain index files

## Obsidian compatibility

- [ ] Files use `.md` extension throughout
- [ ] No absolute paths in wikilinks (use relative or bare slugs)

## Raw memory immutability

- [ ] `wiki_stuff/memories/raw/` — not modified since last ingestion
- [ ] No project-specific data mixed into domain directories

---

## Verdict

```
WIKI_OPERATIONAL_READY    — all required checks pass
WIKI_OPERATIONAL_PARTIAL  — some required checks fail or WARN checks flagged
WIKI_OPERATIONAL_NOT_READY — critical components absent
```
````

## File: docs/architecture.md
````markdown
# Architecture

## Overview

The project-wiki-rag-bridge connects three distinct systems through a policy-governed layer:

```text
┌────────────────────────────────────────────────────────────────────────┐
│  AUTHORING LAYER (source of truth — never Qdrant)                      │
│                                                                        │
│  ┌─────────────────────────────┐  ┌────────────────────────────────┐   │
│  │  _wiki/wiki_stuff/          │  │  _project/project_stuff/<proj> │   │
│  │  domains/nbn/               │  │  reports/                      │   │
│  │  domains/vocus/             │  │  docs/csv/                     │   │
│  │  domains/mcp/               │  │  manifests/                    │   │
│  │  ...                        │  │  rag/                          │   │
│  └──────────────┬──────────────┘  └───────────────┬────────────────┘   │
│                 │ shared reference facts            │ project-specific   │
└─────────────────┼──────────────────────────────────┼────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  POLICY LAYER (governs what goes where and who may access what)          │
│                                                                          │
│  _wiki/wiki-data/domain-registry.yaml      ← domain declaration         │
│  _wiki/wiki-data/qdrant-collection-policy  ← naming and metadata rules  │
│  <project>/rag/project-context.yaml        ← project wiki dependencies  │
│  <project>/rag/retrieval-policy.yaml       ← flat validator contract     │
│  <project>/rag/manifests/project-docs.yaml ← document index manifest    │
└─────────────────┬──────────────────────────────────┬────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  TOOLING LAYER (does the actual indexing and retrieval)                  │
│                                                                          │
│  _tool/tools_stuff/rag-tools/               ← shared Python tooling     │
│    src/rag_tools/cli.py                     ← CLI (doctor, index, etc.) │
│    src/rag_tools/policy.py                  ← validator                 │
│    src/rag_tools/embeddings.py              ← local embedding model     │
│    scripts/qdrant-up, qdrant-status, etc.   ← Docker lifecycle          │
│  tools-working-cache/rag-tools/.venv/       ← isolated venv             │
└─────────────────┬──────────────────────────────────┬────────────────────┘
                  │                                  │
┌─────────────────▼──────────────────────────────────▼────────────────────┐
│  INDEX LAYER (Qdrant — retrieval artefact, not source of truth)          │
│                                                                          │
│  rag__wiki_nbn              ← wiki domain nbn, scoped, filtered          │
│  rag__wiki_vocus            ← wiki domain vocus, scoped, filtered        │
│  rag__wiki_mcp              ← wiki domain mcp, scoped, filtered          │
│  rag__project_vocus_profitability  ← project vocus, project-filtered     │
│  rag__project_<other_slug>         ← other project, own collection       │
│                                                                          │
│  FORBIDDEN: rag__all, rag__wiki_all, default, documents, knowledge, main │
└──────────────────────────────────────────────────────────────────────────┘
```

## Key design decisions

### 1. Qdrant is not the source of truth

Markdown files are the source of truth. Qdrant is a search index over them.
If a Qdrant collection is deleted, the knowledge is not lost — re-index from the markdown source.

### 2. Policy is enforced in software, not in Qdrant

Qdrant has no multi-tenant enforcement. Isolation is enforced by:
- `retrieval-policy.yaml` — declares allowed/forbidden collections
- `rag-tools validate-policy` — validates policy before any indexing
- This skill's guidance — constrains agent behaviour at query time

### 3. One collection per domain / one collection per project

No collection serves multiple domains or projects. This prevents cross-domain and cross-project
retrieval bleed. Sharing is achieved by declaring wiki domain access in project policy, not by
sharing collections.

### 4. Retrieval order

Every project follows this retrieval order:
1. Project-local files (fastest, most authoritative for project facts)
2. Project Qdrant collection (indexed project documents — secondary)
3. Declared wiki domain collections (shared reference knowledge)
4. Ask user (when no sufficient evidence found)

### 5. External venv

rag-tools uses an isolated venv at `tools-working-cache/rag-tools/.venv`.
Project justfiles reference this venv by absolute path. The venv is not in the source tree.

### 6. Local embeddings only

All embeddings use `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) loaded locally
from HuggingFace cache. No external API calls. This is a hard constraint — do not mix
collections indexed with different models.
````

## File: docs/authority-model.md
````markdown
# Authority Model

## Source of truth hierarchy

When an agent needs to answer a question or retrieve a fact, it must apply this hierarchy:

```
Priority  Source                              Scope
────────  ──────────────────────────────────  ─────────────────────────────────────────
1         Project-local files                 Project-specific facts ONLY
2         Wiki authoritative markdown         Shared reference facts ONLY
3         Qdrant retrieval results            Search results — cite original, don't treat as canonical
4         Generated summaries / reports       Secondary — do not override primary sources
5         Nav YAML                            Routing metadata ONLY — never factual content
```

## Rules

### Rule 1 — Project-specific facts come from project-local files

If the question is about this project's invoices, calculated profitability, internal decisions,
customer mappings, or analysis results, the answer must come from:

```
<project>/reports/
<project>/docs/
<project>/db/
<project>/scripts/
<project>/communications/ (if reviewed and indexed)
```

Do NOT use the wiki for project-specific facts — the wiki does not know this project's data.

### Rule 2 — Shared reference facts come from wiki markdown

If the question is about a standard, a policy definition, a rate card interpretation, or any
knowledge that applies across multiple projects, the answer comes from:

```
_wiki/wiki_stuff/domains/<domain>/references/*.md
_wiki/wiki_stuff/domains/<domain>/index.md
```

The markdown source file is always authoritative — not the Qdrant payload.

### Rule 3 — Qdrant payloads are retrieval artefacts

A Qdrant result is a pointer back to a source file. When citing, cite:
- The source file (`source_file` metadata field)
- The section (`section_path`, `heading` fields)
- The collection it came from

Never treat a Qdrant payload as more authoritative than the markdown source it was indexed from.

### Rule 4 — Nav YAML is routing metadata only

Files such as `context-map.yaml`, `project-context.yaml`, `AI_NAVIGATION.md`, and domain
`index.md` routing tables define WHERE to look — they are not factual sources themselves.

An agent must never answer a factual question by citing a routing file.

### Rule 5 — No unsupported conclusions

If the retrieved evidence is insufficient or ambiguous, the agent must say so explicitly:

> "I searched project-local files, the project Qdrant collection, and wiki domains [nbn, vocus].
> I found insufficient evidence to answer this question confidently. Can you point me to the
> relevant document or provide additional context?"

Do not speculate or blend sources without clearly labelling each.

### Rule 6 — Conflict resolution

When project-local files and wiki markdown disagree:

| Conflict type | Resolution |
|---|---|
| Project fact vs wiki general reference | Project-local wins |
| Wiki standard vs project interpretation | Report the conflict; ask user |
| Two wiki articles disagree | Report the conflict; cite both; ask user |
| Qdrant result vs source markdown | Source markdown wins — re-read the file |

---

## Source labels used in metadata

| `authority` value | Meaning |
|---|---|
| `shared_reference_authoritative_markdown` | Wiki domain article — shared, curated, sourced |
| `project_local` | Project-specific document — authoritative for that project |
| `project_generated` | Output of a script or pipeline — secondary, verify source |
| `routing_metadata_only` | Nav YAML or context file — not a factual source |
````

## File: docs/collection-naming-policy.md
````markdown
# Collection Naming Policy

This document defines the Qdrant collection naming rules for the wiki/project RAG bridge.
These rules are enforced by `retrieval-policy.yaml`, `rag-tools validate-policy`, and this skill.
Qdrant itself has no naming enforcement — violations are silent without policy enforcement.

---

## Allowed patterns

### Project collections

```
rag__project_<project_slug>
```

- `<project_slug>` must be lowercase alphanumeric + underscores only
- No hyphens, no spaces, no uppercase
- Slug must match `project_slug` in `retrieval-policy.yaml`

Examples:
```
rag__project_vocus_profitability   ✓
rag__project_apn_sip_setup         ✓
rag__project_podbng_lab            ✓
```

### Wiki domain collections

```
rag__wiki_<domain_slug>
```

- `<domain_slug>` must match the `slug` field in `domain-registry.yaml`
- One collection per domain — no exceptions

Examples:
```
rag__wiki_nbn     ✓
rag__wiki_vocus   ✓
rag__wiki_mcp     ✓
```

### Test / ephemeral collections

```
rag__test_<purpose>_<yyyymmdd>
```

- Used for unit tests and one-off validation only
- Must be deleted after use or given a date suffix to signal ephemerality
- Never used in production retrieval policy

Examples:
```
rag__test_policy_20260524   ✓
rag__test_embeddings_20260601  ✓
```

---

## Forbidden names

These names are absolutely forbidden. Any collection with these names must be deleted.

| Forbidden name | Why forbidden |
|---|---|
| `rag__global_all_docs` | Implies global/mixed scope |
| `rag__wiki_all` | Implies all-wiki scope |
| `rag__all` | No scoping at all |
| `default` | Qdrant default — no identity |
| `documents` | Generic, no identity |
| `knowledge` | Generic, no identity |
| `main` | Generic, no identity |
| `test` (bare) | No date suffix — could be permanent |
| `wiki` (bare) | No domain scoping |

---

## Naming validation

### In rag-tools

```python
import re
ALLOWED = re.compile(r'^rag__(project|wiki|test)_[a-z0-9_]+$')
FORBIDDEN = {
    'rag__global_all_docs', 'rag__wiki_all', 'rag__all',
    'default', 'documents', 'knowledge', 'main',
}

def validate_collection_name(name: str) -> bool:
    return bool(ALLOWED.match(name)) and name not in FORBIDDEN
```

### In retrieval-policy.yaml

The `forbidden_collections` key must include all globally forbidden names.
The `rag-tools validate-policy` CLI checks this.

---

## Common mistakes

| Mistake | Correct form |
|---|---|
| `vocus_profitability` (no prefix) | `rag__project_vocus_profitability` |
| `rag__nbn` (missing wiki_ infix) | `rag__wiki_nbn` |
| `rag__project-vocus` (hyphen) | `rag__project_vocus_profitability` |
| `rag__wiki_ALL` (uppercase) | `rag__wiki_all` — and this is also forbidden |
| `rag__test` (no suffix) | `rag__test_purpose_20260524` |
````

## File: docs/dynamic-retrieval-strategy.md
````markdown
# Dynamic Retrieval Strategy

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/dynamic-retrieval-strategy.md`
**Purpose:** Explains the profile-first retrieval model for skill users and agents.

---

## Why Pure Vector RAG Is Not Always Correct

Vector RAG works by embedding chunks of text and matching query embeddings to document chunk
embeddings. This works well for broad, semantic, cross-document questions where the answer does
not have a single canonical location.

It does not work well for:

- **Exact fact extraction** — a rate card amount, a contract clause, a rebate percentage, a date.
  Vector similarity finds "nearby" chunks, not the exact row.
- **Structured document navigation** — a long reference doc with section IDs (C2.11, 3.4.2).
  The relevant clause might not be the highest-similarity chunk.
- **Table lookups** — invoice line items, rate grids, pricing tables. Vector RAG does not
  understand row/column structure; it treats table text as undifferentiated prose.
- **Short documents** — a YAML config or a small policy file may return high-confidence chunks
  that are not the most relevant row or field.

Using vector RAG by default for all sources increases hallucination risk for exact facts because
the model may construct a plausible answer from adjacent chunks without verifying the exact value.

---

## Direct Lookup vs Table Lookup vs Vector RAG

### Direct (structured) lookup

`rag-tools structured-lookup` or `rag-tools lookup-section` parses the document's heading tree
and section IDs, then scores sections by term overlap with the query.

**Best for:**
- Long structured markdown with headings and section IDs
- Legal contracts and policy documents (clause navigation)
- Reference documents with numbered sections
- Questions with a known section reference ("what does clause C2.11 say?")

**Not for:**
- Cross-document semantic search
- Summarization questions

### Table lookup

`rag-tools lookup-table` extracts markdown tables, tokenizes headers and rows, and scores by
query term overlap against header text and cell values.

**Best for:**
- Rate cards with period/tier rows
- Invoice line items
- Rebate tables, discount grids
- Pricing schedules

**Not for:**
- Non-tabular content
- Questions requiring row aggregation or arithmetic (use tabular_analytics)

### Vector RAG

Best for knowledge articles, wiki content, meeting notes, broad cross-document questions.

**Best for:**
- Questions whose answer spans multiple sections or documents
- Semantic questions without a precise term match ("what generally applies to service X?")
- Wiki domain content (knowledge_article class)

**Not for:**
- Exact amounts, dates, identifiers
- Structured clause references
- Invoice line items
- Any document where table or section lookup is available

---

## Source Files as Authority

Source files are always authoritative. Qdrant collections and wiki articles are retrieval
artifacts — they are search indices built from source files, not replacements for them.

Rules:
- Answer from `source_file` content in the EvidenceBundle, not from the collection name.
- If a source file and a Qdrant result conflict, prefer the source file.
- Do not duplicate full source files into wiki articles to make RAG work. Use direct lookup.

---

## Profile-First Workflow

Before choosing a retrieval route:

1. Run `rag-tools profile-file <file>` → get `document_class` and `recommended_retrieval_modes`
2. Run `rag-tools recommend-strategy <file>` → get `primary`, `secondary`, `fallback`, `rag_suitability`
3. For structured/tabular/exact-fact documents: run `rag-tools benchmark-file` before committing
   to a default route
4. Record the strategy in `rag/retrieval-strategy.yaml`
5. Only consider vector RAG indexing if strategy says `rag_suitability: suitable` or
   `partially_suitable` AND benchmark supports it

This profile-before-index pattern prevents the most common mistake: indexing everything into
vector RAG and then getting unreliable answers for structured/exact-fact content.

---

## Benchmark Before Default Route

The benchmark runs all applicable modes against a representative query set and returns a
recommendation label:

| Label | Meaning |
|---|---|
| `DIRECT_FIRST` | Structured lookup wins — use as primary |
| `TABLE_LOOKUP_FIRST` | Table lookup wins — use as primary |
| `HYBRID_DIRECT_FIRST` | Direct primary, RAG secondary |
| `HYBRID_RAG_FIRST` | RAG primary, direct fallback |
| `RAG_FIRST` | RAG outperforms direct modes |
| `NOT_READY_NEEDS_EXTRACTION` | PDF — extraction required |
| `NOT_READY_NEEDS_MORE_INDEXED_CONTENT` | No mode passed — source needs rework |

A `DIRECT_FIRST` or `TABLE_LOOKUP_FIRST` result means vector RAG is not needed for that document.
Indexing it into Qdrant would add operational cost with no retrieval benefit.

---

## Wiki Domains

Wiki domains contain `knowledge_article` class content — curated reference articles written
for broad semantic retrieval. These are the right content type for vector RAG.

Wiki articles should:
- Be written as standalone reference material, not as extracts of long source files
- Have `source:` references linking back to authoritative sources
- Not duplicate full source file content (rate cards, contract clauses)

If a wiki domain contains only scaffold pages (headings, no body), indexing it will produce
low-value retrieval. Add curated content (prompt 07) before indexing.

---

## How the Project Bridge Uses Strategy Output

The `rag/retrieval-strategy.yaml` file records the chosen route per document. Agents use it to:

1. Route exact-fact queries to `rag-tools structured-lookup` or `rag-tools lookup-table`
2. Route semantic/cross-document queries to vector RAG (if index exists)
3. Respect the `index_allowed` flag before calling any indexing command
4. Select the appropriate EvidenceBundle-returning command for each query type

The retrieval policy (`rag/retrieval-policy.yaml`) continues to govern which Qdrant collections
are accessible and with what filters. The strategy file adds per-document routing on top.
````

## File: docs/evidence-contract.md
````markdown
# Evidence Contract

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/evidence-contract.md`
**Purpose:** Explains the EvidenceBundle contract, answer rules, and citation requirements
for skill users and agents.

---

## What Is EvidenceBundle?

`EvidenceBundle` is a Pydantic model defined in `rag_tools.evidence`. Every rag-tools retrieval
command (`structured-lookup`, `lookup-section`, `lookup-table`, and vector RAG) returns a list
of EvidenceBundle objects.

The bundle contains:

- The verbatim excerpt from the source file
- The source file path (authoritative citation)
- The retrieval mode used
- Section ID, heading, table ID (where applicable)
- Matched terms
- Score or confidence
- Retrieval warnings

The LLM must answer only from evidence bundle content. It must not fill gaps with training
knowledge.

---

## Required Fields

| Field | Required | Purpose |
|---|---|---|
| `query` | Yes | The original lookup query |
| `retrieval_mode` | Yes | Mode that produced this bundle |
| `source_file` | Yes | Absolute path to the canonical source |
| `excerpt` | Yes | Verbatim text from source — only basis for answer |
| `retrieval_warnings` | Yes (list) | Populated when evidence is partial or low-confidence |

---

## How Agents Should Answer From EvidenceBundle

**Rule 1: Answer only from `excerpt`.**

Do not add facts from training knowledge. Do not infer amounts, dates, rates, clause text, or
identifiers that are not present verbatim in the excerpt.

**Rule 2: Cite the source.**

Every answer must include at minimum `source_file`. Preferred citation includes
`section_id` or `heading` or `table_id`.

**Rule 3: Surface warnings.**

If `retrieval_warnings` is non-empty, include a note in the answer. Low-confidence or fallback
evidence must be flagged, not silently used.

**Rule 4: Report gaps honestly.**

If no EvidenceBundle is returned, or if the excerpt is empty, state:
"not found in retrieved evidence" — do not synthesize a plausible answer.

**Rule 5: Do not merge conflicting excerpts.**

If two bundles contain conflicting values, report the conflict rather than resolving it.

---

## What to Do When Evidence Is Weak

| Situation | Response |
|---|---|
| No bundle returned | Report `RETRIEVAL_NOT_READY` and stop |
| Bundle returned but excerpt is empty | Report "not found in retrieved evidence"; surface warning |
| `score_or_confidence < 0.5` (RAG) | Flag as low-confidence; do not answer as fact |
| `retrieval_warnings` contains fallback note | Surface the warning; qualify the answer |
| Multiple bundles with conflicting excerpts | Report conflict; cite both sources |
| Exact amount not in excerpt | State "exact value not found in retrieved evidence" |

---

## Citation Requirements

Minimum citation (required):
```
Source: <source_file>
```

Preferred citation:
```
Source: <source_file>
Section: <section_id> — <heading>
```

Full citation:
```
Source: <source_file>
Path: <section_path as breadcrumb>
Section: <section_id>
Excerpt: "<verbatim excerpt>"
Mode: <retrieval_mode>
```

For table results:
```
Source: <source_file>
Table: <table_id>
Row: <row_keys>
Excerpt: "<verbatim cell content>"
```

---

## Examples of Good and Bad Answers

### Good answer — grounded in evidence

Query: "What is the rebate for period 3?"

EvidenceBundle excerpt:
```
| Period | Rebate |
|---|---|
| Period 3 | $18,420 |
```

Answer:
> The rebate for period 3 is $18,420.
> Source: /project/rag/docs/rate-card.md | Table: rate-rebate-table

---

### Bad answer — invented value not in evidence

Query: "What is the rebate for period 3?"

EvidenceBundle excerpt:
```
Rate adjustments are applied quarterly based on volume thresholds.
```

Bad answer:
> The rebate for period 3 is approximately $18,000 based on typical quarterly rates.

Problem: The amount "$18,000" is not in the excerpt. The answer uses training knowledge to
fill a gap. This is forbidden.

Good answer:
> The retrieved evidence does not contain the period 3 rebate amount. The nearest evidence
> found was: "Rate adjustments are applied quarterly based on volume thresholds."
> Source: /project/rag/docs/rate-card.md

---

### Good answer — warning surfaced

Query: "What is the grace period for late payment?"

EvidenceBundle excerpt:
```
Payment terms are described in Schedule B.
```

retrieval_warnings: ["no exact section ID match; nearest heading used"]

Answer:
> The retrieved evidence references Schedule B for payment terms but does not include the grace
> period value. The retrieval used the nearest heading match (not an exact section ID).
> Warning: no exact section ID match; nearest heading used.
> Source: /project/docs/agreement.md | Heading: Payment Terms

---

### Bad answer — warning silenced

Same situation as above, but the answer states:
> The grace period is 14 days.

Problem: The value is invented. The warning was not surfaced.
````

## File: docs/failure-modes.md
````markdown
# Failure Modes

## FM-01 — Scaffold-only collection

**What:** Collection exists in Qdrant with 0 vectors. Policy validates. Queries return nothing.

**Cause:** `rag-tools index-domain` was never run, or it exited before indexing any chunks.

**Detection:**
```python
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_nbn')
print(info.vectors_count)  # 0
```

**Fix:** Re-run prompt/05. Check domain directory has markdown files before indexing.

---

## FM-02 — Empty collection (indexing failed silently)

**What:** Index command appeared to succeed but collection has 0 or very low vector count.

**Cause:** Domain directory had no eligible files, or embedding failed quietly on all chunks.

**Detection:** Compare dry-run chunk count with actual vectors_count after indexing.

**Fix:** Check domain markdown files for frontmatter errors. Run embedding smoke test.
Re-run with `--dry-run` to confirm chunk count, then live index.

---

## FM-03 — Policy validates but no retrieval

**What:** `rag-tools validate-policy` passes. Qdrant is running. Queries return 0 results.

**Cause:** Collection is empty (FM-01/FM-02), or wiki_domain filter excludes all results,
or embedding model mismatch between index time and query time.

**Detection:** Query without domain filter. Check if any results come back.
```python
results = client.search(collection_name='rag__wiki_nbn', query_vector=vector, limit=3)
# vs
results_filtered = client.search(..., query_filter={"must":[{"key":"wiki_domain","match":{"value":"nbn"}}]}, ...)
```

**Fix:** Re-index with correct metadata. Confirm model is `all-MiniLM-L6-v2` at both index and query.

---

## FM-04 — Global collection pollution

**What:** A collection named `default`, `documents`, `rag__all`, etc. exists in Qdrant.

**Cause:** Tooling defaults, an external experiment, or a policy violation during indexing.

**Detection:**
```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections
# Look for names not matching rag__project_* | rag__wiki_* | rag__test_*
```

**Fix:** Delete the offending collection immediately:
```bash
curl -X DELETE http://localhost:6333/collections/<forbidden_name>
```
Update any project policy that references it. Re-index under the correct name.

---

## FM-05 — Ambiguous wikilinks

**What:** Articles reference `[[some-page]]` but `some-page.md` does not exist or the slug is wrong.

**Cause:** Wikilink slug not matching filename, or referenced article not yet created.

**Detection:**
```bash
grep -r '\[\[' /Volumes/Data/_ai/_wiki/wiki_stuff/domains/ --include='*.md' | \
  grep -v '\.md\]\]' | head -20
```

**Impact:** Broken links don't break retrieval but reduce knowledge graph navigability.

**Fix:** Either create the missing article or correct the wikilink slug.

---

## FM-06 — Missing frontmatter

**What:** A wiki article has no YAML frontmatter or invalid frontmatter.

**Cause:** Article was added without following the template.

**Detection:**
```python
import pathlib, yaml
for f in pathlib.Path('/Volumes/Data/_ai/_wiki/wiki_stuff/domains').rglob('*.md'):
    t = f.read_text()
    if not t.startswith('---'):
        print(f'NO FRONTMATTER: {f}')
    else:
        try: yaml.safe_load(t.split('---')[1])
        except: print(f'INVALID FRONTMATTER: {f}')
```

**Impact:** Indexing may succeed but metadata fields will be missing, breaking citation.

**Fix:** Add or fix frontmatter using `templates/wiki-reference-article.md` as the structure.

---

## FM-07 — Qdrant missing / unreachable

**What:** All Qdrant operations fail with `Connection refused` on localhost:6333.

**Cause:** Qdrant container not running. Docker context pointing to wrong runtime.

**Fix:** See prompt/09 Symptom C. Run `qdrant-up`. Check `docker context ls`.

---

## FM-08 — Missing external venv

**What:** `No module named 'rag_tools'` or `python: command not found` from justfile tasks.

**Cause:** Venv at `tools-working-cache/rag-tools/.venv` was not created or was deleted.

**Fix:** See prompt/09 Symptom A.
```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools
UV_PROJECT_ENVIRONMENT=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv uv sync
```

---

## FM-09 — Wrong UV environment

**What:** UV installs packages to wrong location. Shell `VIRTUAL_ENV` conflicts.

**Cause:** `VIRTUAL_ENV` env var set to a different venv. UV warns but proceeds to `UV_PROJECT_ENVIRONMENT`.

**Detection:** UV warning: `Ignoring existing virtual environment linked to...`

**Fix:** Set `UV_PROJECT_ENVIRONMENT` explicitly. The warning is safe to ignore if the target venv is correct.

---

## FM-10 — Project accidentally indexed raw data

**What:** Sensitive file paths (CSV, raw invoices, communications) appear in project collection payloads.

**Cause:** Project manifest had `index: true` on a raw or sensitive document, or `default_index` was set to `true`.

**Detection:** See prompt/09 Symptom J.

**Fix:**
1. Delete the project collection: `curl -X DELETE http://localhost:6333/collections/rag__project_<slug>`
2. Fix manifest: set `index: false` on all sensitive/raw/communications documents.
3. Confirm `rules.default_index: false`.
4. Re-run prompt/08 with corrected manifest.
5. Verify collection no longer contains sensitive paths.
````

## File: docs/flow-diagram.md
````markdown
# Flow Diagrams

All diagrams use plain text. No rendering dependency.

---

## 1. Wiki Authoring Flow

```text
Human author
  │
  ├─► writes markdown article
  │     with frontmatter (title, domain, type, source, authority)
  │     under wiki_stuff/domains/<domain>/references/<slug>.md
  │
  ├─► adds source reference in ## Source references section
  │
  ├─► updates domain index.md (Contents table)
  │
  └─► appends to wiki_stuff/log.md
          │
          ▼
     wiki_stuff/domains/<domain>/   ← source of truth, immutable after commit
```

---

## 2. Project Bridge Setup Flow

```text
Agent (using this skill)
  │
  ├─ Step 1: prompt/00 ─► verify wiki operational state
  │                         WIKI_OPERATIONAL_READY? → continue
  │                         NOT_READY? → fix first
  │
  ├─ Step 2: prompt/01 ─► create wiki domain (if missing)
  │                         mkdir domains/<domain>/
  │                         update domain-registry.yaml
  │
  ├─ Step 3: prompt/02 ─► verify rag-tools
  │                         doctor + Qdrant + embeddings
  │                         RAG_TOOLS_READY? → continue
  │
  ├─ Step 4: prompt/03 ─► create project bridge files
  │                         rag/project-context.yaml
  │                         rag/retrieval-policy.yaml
  │                         rag/manifests/project-documents.yaml
  │                         docs/ai/wiki-bridge.md
  │                         update AGENTS/AI_NAVIGATION/README/CHANGELOG
  │
  ├─ Step 5: prompt/04 ─► validate project policy
  │                         YAML parse → flat keys → rag-tools validate-policy
  │                         PROJECT_RAG_POLICY_VALIDATED? → continue
  │
  └─► PROJECT_WIKI_BRIDGE_READY
```

---

## 3. Indexing Flow

```text
Agent (using this skill)
  │
  ├─ checklists/indexing-readiness.md ─► all BLOCKING checks pass?
  │                                         NO → fix → re-check
  │
  ├─ Step 6: prompt/07 ─► add wiki reference articles
  │                          curated content with source references
  │                          under domains/<domain>/references/
  │
  ├─ Step 7: prompt/05 ─► index wiki domain
  │   │
  │   ├─► DRY-RUN: rag_tools.cli index-domain --domain <d> --dry-run
  │   │       chunk count OK? no cross-domain bleed? → confirm
  │   │
  │   ├─► LIVE: rag_tools.cli index-domain --domain <d>
  │   │       upserts idempotently to rag__wiki_<d>
  │   │
  │   └─► verify: Qdrant collection vectors_count > 0
  │           WIKI_DOMAIN_INDEXED → continue
  │
  └─► (optional) prompt/08 ─► index project documents
          manifest check: only index: true, not sensitive
          DRY-RUN first → LIVE → verify
```

---

## 4. Retrieval Flow

```text
Agent query: "What is the DCR eligibility rule for FWA services?"
  │
  ├─ Step 1: search project-local files
  │     grep, find, read reports/ manifests/ analysis/
  │     found relevant? → cite, return, done
  │     not found? → continue
  │
  ├─ Step 2: query project collection
  │     rag__project_vocus_profitability
  │     filter: project_slug = vocus_profitability
  │     top results + scores → relevant? → cite, return
  │     not found / low score? → continue
  │
  ├─ Step 3: query declared wiki domains
  │     rag__wiki_nbn  (filter: wiki_domain = nbn)
  │     rag__wiki_vocus (filter: wiki_domain = vocus)
  │     results → cite source_file, heading, section_path, collection
  │     relevant? → return with citation
  │     not found? → continue
  │
  └─ Step 4: ask user
        "I searched project-local files, project collection, and wiki domains
         [nbn, vocus]. Insufficient evidence found. Can you provide additional
         context or point me to the relevant document?"
```

---

## 5. Troubleshooting Flow

```text
Problem observed
  │
  ├─ venv missing / import error
  │     → prompt/09 Symptom A or B
  │     → rebuild: uv sync with UV_PROJECT_ENVIRONMENT
  │
  ├─ Qdrant unreachable
  │     → prompt/09 Symptom C
  │     → qdrant-up → check Docker context
  │
  ├─ policy validator fails
  │     → prompt/09 Symptom E
  │     → check flat validator keys (schemas/retrieval-policy.schema.yaml)
  │
  ├─ empty collection after indexing
  │     → prompt/09 Symptom H
  │     → check domain content exists, re-run index
  │
  ├─ no useful retrieval (low scores)
  │     → prompt/09 Symptom I
  │     → check embedding model match (384-dim, all-MiniLM-L6-v2)
  │
  └─ sensitive data in collection
        → prompt/09 Symptom J
        → delete collection → fix manifest → re-index
```
````

## File: docs/multi-project-model.md
````markdown
# Multi-Project Model

## How multiple projects share the wiki without polluting each other

```text
                         _wiki/wiki_stuff/domains/
                         ┌──────────┬──────────┬──────────┐
                         │  nbn/    │  vocus/  │  mcp/    │
                         └────┬─────┴────┬─────┴──────────┘
                              │           │
              ┌───────────────┤           ├────────────────┐
              │               │           │                │
              ▼               ▼           ▼                ▼
    Project A             Project B             Project C
    (declares nbn)        (declares nbn         (declares mcp)
                           + vocus)
              │               │                            │
              ▼               ▼                            ▼
    rag__project_A      rag__project_B             rag__project_C
    rag__wiki_nbn  ←────rag__wiki_nbn              rag__wiki_mcp
    (own copy of        (same shared               (own project col)
    project docs)        wiki collection)
```

### Key principle

Wiki domain collections are **shared indexes** over the same markdown source.
Project collections are **strictly isolated** — one per project, filtered by `project_slug`.

---

## Isolation mechanisms

### 1. Declaration gate

A project can only access wiki domains it has explicitly declared in `retrieval-policy.yaml`.
Undeclared domains are forbidden — even if the collection exists in Qdrant.

```yaml
# Project B — declares both nbn and vocus
allowed_wiki_domains:
  - "nbn"
  - "vocus"

# Project A — declares only nbn
allowed_wiki_domains:
  - "nbn"
# Project A cannot query rag__wiki_vocus even though it exists
```

### 2. Filter gate

Every query to a wiki collection must include a `wiki_domain` filter.
Every query to a project collection must include a `project_slug` filter.
Unfiltered queries are policy violations — even if the collection allows them technically.

### 3. Collection-per-project

No two projects share a project collection. If Project A accidentally indexes to
`rag__project_B`, that is a policy violation requiring immediate cleanup.

### 4. No cross-project fallback

A project must not fall back to another project's collection if its own collection returns
nothing. The correct fallback is to ask the user.

---

## Adding a new project

1. Assign a unique `project_slug` (check against all existing project slugs).
2. Run prompt/03 to create bridge files — `rag__project_<slug>` will be the isolated collection.
3. Declare only the wiki domains actually needed. Start with the minimum.
4. Run prompt/04 to validate policy — ensure no name collision with existing collections.
5. Check `checklists/multi-project-isolation.md` against all existing projects.

---

## What happens when a wiki domain gains new content

New articles indexed into `rag__wiki_nbn` are immediately available to all projects that
declare `nbn` as an allowed domain. No per-project re-indexing is needed.

This is the value of the shared wiki model — curated shared knowledge propagates automatically.

---

## What is NOT shared

| Not shared | Why |
|---|---|
| `rag__project_<slug>` | Strictly per-project |
| Project-local source files | Live only in the project repo |
| Project-specific interpretations | Stored in project collection only |
| Sensitive/raw project data | Never indexed into any shared layer |

---

## Audit: checking isolation holds

```bash
# List all collections and check naming
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Verify no forbidden global collections
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
forbidden = {'default','documents','knowledge','main','rag__all','rag__wiki_all','rag__global_all_docs'}
cols = [c.name for c in client.get_collections().collections]
hits = [c for c in cols if c in forbidden]
print('FAIL: forbidden collections found:', hits) if hits else print('PASS: no forbidden collections')
"
```
````

## File: docs/operating-runbook.md
````markdown
# Operating Runbook

Step-by-step commands and sequences for all standard operations.
All commands assume you are in the project root unless stated otherwise.

---

## 1. New wiki domain

```bash
# Verify wiki is ready
# Run: prompts/00-verify-wiki-operational-state.md

DOMAIN="<domain_slug>"
WIKI_STUFF="/Volumes/Data/_ai/_wiki/wiki_stuff"
WIKI_DATA="/Volumes/Data/_ai/_wiki/wiki-data"

# 1. Create directory
mkdir -p "$WIKI_STUFF/domains/$DOMAIN/references"

# 2. Create index.md (use templates/wiki-domain-index.md)

# 3. Register in domain-registry.yaml (append entry from templates/wiki-domain-registry-entry.yaml)

# 4. Update wiki log
echo "$(date +%Y-%m-%d)  Created domain: $DOMAIN" >> "$WIKI_STUFF/log.md"

# 5. Validate
python3 -c "
import yaml
with open('$WIKI_DATA/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)
found = [d for d in reg['domains'] if d['slug'] == '$DOMAIN']
print('PASS' if found else 'FAIL: not registered')
"
```

---

## 2. New project bridge

```bash
# Run after: prompts/00, 01 (if domain needed), 02
# Use: prompts/03-create-project-bridge.md

PROJECT_ROOT="<absolute-path-to-project>"
PROJECT_SLUG="<project_slug>"

# Create dirs
mkdir -p "$PROJECT_ROOT/rag/manifests" "$PROJECT_ROOT/docs/ai"

# Create files (fill from templates):
#   rag/project-context.yaml
#   rag/retrieval-policy.yaml
#   rag/manifests/project-documents.yaml
#   docs/ai/wiki-bridge.md

# Validate
python3 -c "
import yaml, pathlib
root = pathlib.Path('$PROJECT_ROOT')
for f in ['rag/retrieval-policy.yaml', 'rag/project-context.yaml', 'rag/manifests/project-documents.yaml']:
    try: yaml.safe_load((root/f).read_text()); print(f'PASS: {f}')
    except Exception as e: print(f'FAIL: {f} — {e}')
"
```

---

## 3. Validate project policy

```bash
cd <PROJECT_ROOT>

# YAML parse + flat key check
python3 -c "
import yaml
required = ['version','project_slug','project_collection','allowed_wiki_domains',
            'allowed_wiki_collections','forbidden_collections','required_filters','citation_rules']
with open('rag/retrieval-policy.yaml') as f:
    p = yaml.safe_load(f)
missing = [k for k in required if k not in p]
print('FAIL: missing keys:', missing) if missing else print('PASS: all flat keys present')
"

# rag-tools validator
/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli validate-policy rag/retrieval-policy.yaml
```

---

## 4. Index wiki domain

```bash
RAG_BIN="/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python"
RAG_ROOT="/Volumes/Data/_ai/_tool/tools_stuff/rag-tools"
DOMAIN="<domain_slug>"

# Dry-run first (REQUIRED)
cd "$RAG_ROOT" && $RAG_BIN -m rag_tools.cli index-domain --domain $DOMAIN --dry-run

# Review output — chunk count reasonable? No cross-domain bleed?
# Then live index:
cd "$RAG_ROOT" && $RAG_BIN -m rag_tools.cli index-domain --domain $DOMAIN

# Verify
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_$DOMAIN')
print(f'rag__wiki_$DOMAIN: {info.vectors_count} vectors, status={info.status}')
"
```

---

## 5. Add reference article

```bash
DOMAIN="<domain_slug>"
ARTICLE_SLUG="<article-slug>"
WIKI_STUFF="/Volumes/Data/_ai/_wiki/wiki_stuff"

mkdir -p "$WIKI_STUFF/domains/$DOMAIN/references"

# Create article using templates/wiki-reference-article.md
# Required frontmatter: title, type, domain, status, authority, source, tags, updated
# Required sections: Purpose, Summary, Key rules/facts, Eligibility/scope,
#                    Exclusions/caveats, Interactions, Source references, Related pages

# Validate frontmatter
python3 -c "
import yaml, pathlib
path = pathlib.Path('$WIKI_STUFF/domains/$DOMAIN/references/$ARTICLE_SLUG.md')
text = path.read_text()
end = text.index('---', 3)
fm = yaml.safe_load(text[3:end])
required = ['title','type','domain','status','authority','source','updated']
missing = [k for k in required if k not in fm]
print('FAIL: missing:', missing) if missing else print('PASS: frontmatter valid')
"

# Append to log
echo "$(date +%Y-%m-%d)  Added reference: $DOMAIN/$ARTICLE_SLUG" >> \
  "$WIKI_STUFF/log.md"
```

---

## 6. Run retrieval validation

```bash
# Run: prompts/06-post-index-retrieval-validation.md
# Ensure Qdrant is running and collection is indexed first

/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status

python3 -c "
from qdrant_client import QdrantClient
from rag_tools.embeddings import get_embedding_model

client = QdrantClient(host='localhost', port=6333)
model = get_embedding_model()

query = '<your test query>'
vector = model.encode(query).tolist()
results = client.search(
    collection_name='rag__wiki_<domain>',
    query_vector=vector,
    query_filter={'must':[{'key':'wiki_domain','match':{'value':'<domain>'}}]},
    limit=3, with_payload=True
)
for r in results:
    p = r.payload or {}
    print(f'score={r.score:.3f} | {p.get(\"source_file\")} | {p.get(\"heading\")}')
"
```

---

## 7. Rollback / remove bad collection

```bash
BAD_COLLECTION="<collection_name>"

# Confirm before deleting
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('$BAD_COLLECTION')
print(f'About to delete: $BAD_COLLECTION ({info.vectors_count} vectors)')
print('Confirm with: curl -X DELETE http://localhost:6333/collections/$BAD_COLLECTION')
"

# Delete
curl -X DELETE "http://localhost:6333/collections/$BAD_COLLECTION"

# Re-index under correct name (if needed)
# Run: prompts/05-index-wiki-domain.md or prompts/08-index-project-documents.md
```

---

## 8. Full health check

```bash
# Wiki
python3 -c "import yaml; yaml.safe_load(open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml'))" \
  && echo "PASS: domain registry" || echo "FAIL: domain registry"

# RAG tools
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python -m rag_tools.cli doctor

# Qdrant
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Embeddings
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/embedding-smoke-test
```
````

## File: docs/retrieval-mode-decision-tree.md
````markdown
# Retrieval Mode Decision Tree

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/retrieval-mode-decision-tree.md`
**Purpose:** Text diagram for agents and skill users to choose the correct retrieval mode.

---

## Decision Tree

```
User query
│
├── Identify intent
│     ├── Exact fact: amount, date, clause reference, identifier, rate
│     ├── Section navigation: "what does clause X say?", "find section Y"
│     ├── Table lookup: rate card value, billing line item, pricing tier
│     ├── Semantic search: broad question, cross-document, knowledge-style
│     └── Aggregation/analytics: sum, compare, trend across table rows
│
├── Identify target source
│     ├── Known structured source (long markdown, section IDs) → check profile
│     ├── Known tabular source (CSV, rate card, invoice) → check profile
│     ├── Wiki domain (knowledge articles) → vector RAG path
│     └── Unknown → run profile-file first
│
├── Check source profile (rag/retrieval-strategy.yaml or run profile-file)
│     ├── document_class = structured_markdown_reference → direct/section lookup
│     ├── document_class = financial_rate_card → table_aware_lookup
│     ├── document_class = invoice_or_billing_report → table_aware_lookup
│     ├── document_class = legal_contract_or_terms → section_clause_lookup
│     ├── document_class = policy_document → section_clause_lookup
│     ├── document_class = knowledge_article → vector_rag
│     ├── document_class = operational_runbook → heading_aware_lookup / keyword_lookup
│     ├── document_class = tabular_dataset → table_aware_lookup (no RAG)
│     ├── document_class = unstructured_pdf | scanned_pdf → extraction_required (stop)
│     └── document_class = unknown → run profile-file before proceeding
│
├── Choose retrieval mode
│     │
│     ├── Intent = exact fact AND source has section IDs
│     │     └── rag-tools lookup-section <file> <section-id>
│     │           → EvidenceBundle with section_id + excerpt
│     │
│     ├── Intent = exact fact AND source is structured (headings, no section IDs)
│     │     └── rag-tools structured-lookup <file> "<query>"
│     │           → EvidenceBundle with heading + section_path + excerpt
│     │
│     ├── Intent = table lookup (rate, amount, tier, period)
│     │     └── rag-tools lookup-table <file> "<query>"
│     │           → EvidenceBundle with table_id + row_keys + excerpt
│     │
│     ├── Intent = broad semantic / cross-document AND wiki collection exists
│     │     └── vector RAG query against rag__wiki_<domain>
│     │           (must have policy, filters, and valid collection)
│     │           → EvidenceBundle with source_file + heading + excerpt
│     │
│     ├── Intent = broad semantic AND no collection exists
│     │     └── rag-tools structured-lookup <file> "<query>"
│     │           → use as fallback; flag in retrieval_warnings if low-confidence
│     │
│     └── Intent = aggregation / analytics
│           └── tabular_analytics (not yet a CLI command; use table lookup + manual aggregation)
│
└── Retrieve EvidenceBundle
      ├── excerpt present and non-empty → answer from excerpt only
      ├── excerpt empty → report "not found in retrieved evidence"
      ├── retrieval_warnings present → surface in answer; qualify confidence
      └── score_or_confidence < 0.5 (RAG) → flag as low-confidence
```

---

## Retrieval Mode Outputs

| Mode | CLI command | Key output fields |
|---|---|---|
| `direct_structured_lookup` | `rag-tools structured-lookup <file> <query>` | heading, section_path, excerpt |
| `section_clause_lookup` | `rag-tools lookup-section <file> <section-id>` | section_id, heading, excerpt |
| `heading_aware_lookup` | `rag-tools structured-lookup <file> <query>` | heading, excerpt |
| `table_aware_lookup` | `rag-tools lookup-table <file> <query>` | table_id, row_keys, excerpt |
| `vector_rag` | Qdrant query (requires collection) | source_file, heading, score_or_confidence, excerpt |
| `keyword_lookup` | structured-lookup fallback | matched_terms, excerpt |
| `extraction_required` | none — PDF/binary | retrieval_warnings: ["source requires extraction"] |

---

## Quick Reference: When to Use Each Mode

| Scenario | Recommended mode |
|---|---|
| "What is the rate for service X in period 3?" | `table_aware_lookup` |
| "What does clause C2.11 require?" | `section_clause_lookup` |
| "Find the section about rebate calculations" | `direct_structured_lookup` |
| "What are the key NBN WBA concepts?" | `vector_rag` (wiki domain) |
| "What is the total invoice amount for Q1?" | `tabular_analytics` (manual) |
| "What does the payment terms section say?" | `direct_structured_lookup` or `section_clause_lookup` |
| "Is there any policy on late fees?" | `vector_rag` (wiki) or `keyword_lookup` (project) |
| "Profile this file" | `profile-file` (not a retrieval mode — pre-step) |
````

## File: schemas/document-profile.schema.yaml
````yaml
# Schema: document-profile.schema.yaml
# Purpose: Defines the structure of profile-file output saved to source-profiles/.
# Authority: skill-project-wiki-rag-bridge / archcore specs layer
# Source: mirrors rag_tools.document_profiler.profile_file() return shape

schema_name: document-profile
version: 1
applies_to: "<project-root>/rag/source-profiles/<document_id>.yaml"

purpose: >
  Source document profile produced by `rag-tools profile-file`. Records structural features
  used by strategy_selector to recommend retrieval modes. Stored in project-local rag/
  directory for audit and strategy derivation.

required_fields:
  document_id:
    type: string
    description: File stem (no extension). Must match the filename used in retrieval-strategy.yaml.

  title:
    type: string
    description: First heading text, or file stem if no headings. Used for display and citation.

  path:
    type: string
    description: Absolute path to the source file. Never a Qdrant collection path.

  file_type:
    type: string
    allowed_values: [".md", ".txt", ".csv", ".tsv", ".json", ".yaml", ".yml", ".pdf", ".xlsx"]
    description: File extension including the dot.

  size_bytes:
    type: integer
    description: File size in bytes. Zero if file is missing.

  line_count:
    type: integer
    description: Number of lines in the file.

  estimated_tokens:
    type: integer
    description: Rough token count estimate. Used for chunking decisions.

  document_class:
    type: string
    allowed_values:
      - structured_markdown_reference
      - legal_contract_or_terms
      - financial_rate_card
      - invoice_or_billing_report
      - operational_runbook
      - policy_document
      - meeting_notes
      - knowledge_article
      - source_code_docs
      - unstructured_pdf
      - scanned_pdf
      - tabular_dataset
      - mixed_content
      - unknown
    description: >
      Document classification from document_profiler._document_class(). Drives strategy
      selection. "unknown" is a valid output but requires manual classification before indexing.

  has_headings:
    type: boolean

  heading_count:
    type: integer

  heading_levels:
    type: list[integer]
    description: Sorted list of heading depths found (e.g. [1, 2, 3]).

  has_tables:
    type: boolean

  table_count:
    type: integer

  has_section_ids:
    type: boolean
    description: True if structured IDs like "C2.11" or "1.2.3" were detected.

  section_ids:
    type: list[string]
    description: Sorted list of detected section ID strings.

  authoritative:
    type: boolean
    description: Always true from profile-file output. Reflects that source files are authoritative.

  recommended_retrieval_modes:
    type: list[string]
    description: Ordered list of preferred retrieval modes from _recommended_modes().

  index_allowed:
    type: boolean
    description: Always false from profile-file. Only updated after strategy + benchmark decisions.

  notes:
    type: list[string]
    description: Optional profiler notes or manual annotations.

optional_fields:
  has_toc:
    type: boolean

  has_frontmatter:
    type: boolean

  has_repeated_entities:
    type: boolean

  has_dates:
    type: boolean

  has_amounts:
    type: boolean

  has_definitions:
    type: boolean

  has_cross_references:
    type: boolean

  contains_sensitive_data:
    type: boolean
    description: >
      If true, index_allowed must remain false. Profiler detects api_key, password, secret,
      token patterns. Manual review required before considering any indexing.

validation_notes:
  - document_id must match the file stem exactly
  - path must be an absolute path to the actual source file
  - index_allowed from profile-file is always false; do not override at profile stage
  - contains_sensitive_data: true always blocks indexing
  - recommended_retrieval_modes must be a non-empty list for any supported file type
  - document_class unknown requires manual classification before strategy can proceed

common_failure_cases:
  - "document_id does not match file stem — misalignment breaks retrieval-strategy.yaml lookups"
  - "contains_sensitive_data: true with index_allowed: true — forbidden"
  - "document_class: unknown — re-run profile-file or classify manually before writing strategy"
  - "recommended_retrieval_modes is empty — profiler found an unsupported file type"
  - "path is relative, not absolute — must be full path for reliable source citation"
````

## File: schemas/evidence-bundle.schema.yaml
````yaml
# Schema: evidence-bundle.schema.yaml
# Purpose: Defines the EvidenceBundle contract for retrieval results.
# Authority: skill-project-wiki-rag-bridge / archcore specs layer
# Source: mirrors rag_tools.evidence.EvidenceBundle (Pydantic model)

schema_name: evidence-bundle
version: 1
applies_to: "any rag-tools retrieval command output"

purpose: >
  EvidenceBundle is the required output of every rag-tools retrieval operation. The LLM must
  answer only from evidence bundle content — never from training knowledge. Exact amounts, dates,
  clause references, and IDs must not be inferred; they must come from the excerpt field. If no
  valid EvidenceBundle is returned, the agent must report RETRIEVAL_NOT_READY and stop.

required_fields:
  query:
    type: string
    description: The exact original query or lookup term submitted to the retrieval function.

  retrieval_mode:
    type: string
    allowed_values:
      - direct_structured_lookup
      - section_clause_lookup
      - heading_aware_lookup
      - table_aware_lookup
      - tabular_analytics
      - keyword_lookup
      - vector_rag
      - hybrid_direct_first
      - hybrid_rag_first
    description: >
      The retrieval mode that produced this bundle. Must reflect the actual mode used, not the
      intended mode. Used for citation and routing audit.

  excerpt:
    type: string
    description: >
      Verbatim text extracted from the source file. This is the ONLY field the LLM may use to
      construct an answer. Rules:
        - Must be source-grounded; no generated conclusions.
        - Must not contain invented amounts, dates, rates, identifiers, or clause text.
        - If blank or missing, the bundle is invalid — do not answer from it.
        - Do not paraphrase the excerpt in the answer; cite it directly.

  source_file:
    type: string
    description: >
      Absolute path to the canonical source file. Required. Never a Qdrant collection name.
      Qdrant results are retrieval artifacts, not authoritative records. The source_file
      is the authoritative reference for citation.

optional_fields:
  document_id:
    type: string
    description: File stem without extension. Strongly recommended for citation traceability.

  source_type:
    type: string
    description: File extension without dot (e.g. "md", "csv").

  authority:
    type: string
    allowed_values: [source, wiki_article, external_reference, derived]
    description: Authority level of the source. Default is "source" for project files.

  section_id:
    type: string
    description: >
      Structured section ID from the source (e.g. "C2.11", "1.2.3"). When present, enables
      exact clause-level citations. Should be populated for section_clause_lookup results.

  section_path:
    type: list[string]
    description: >
      Heading chain from document root to the matched section (e.g. ["Agreement", "Rates",
      "Period 3"]). Should be present for structured and section lookup results.

  heading:
    type: string
    description: The single nearest heading above the matched text. For display in citations.

  table_id:
    type: string
    description: Table identifier within the source. Present for table_aware_lookup results.

  row_keys:
    type: list[string]
    description: Short row-key preview for matched table rows. For citation and debugging.

  matched_terms:
    type: list[string]
    description: Query terms that matched in the source. Supports citation transparency.

  score_or_confidence:
    type: float
    description: >
      Relevance score from the retrieval function. For deterministic lookup may be 1.0 (exact
      match) or term-overlap score. For vector RAG this is the cosine similarity. Low values
      (< 0.5 for RAG) should trigger a retrieval_warning.

  context_chars:
    type: integer
    description: Auto-calculated as len(excerpt). Zero if excerpt is empty.

  retrieval_warnings:
    type: list[string]
    description: >
      Must be populated when any of the following apply:
        - source file was missing ("source file missing")
        - retrieval fell back from primary to secondary mode
        - evidence is low-confidence or partial
        - vector RAG score < 0.5
        - structured lookup found no exact section ID match
        - table match is partial (header only, no row match)
        - fallback was needed and used
      An empty list is valid when retrieval succeeded cleanly.

answer_rules:
  - The LLM must answer only from excerpt content.
  - Do not infer amounts, dates, identifiers, or clause text not present in the excerpt.
  - If evidence is missing for a fact, state "not found in retrieved evidence" — do not guess.
  - Qdrant payloads are retrieval artifacts. They cite the source_file; they are not the authority.
  - When multiple bundles are returned, cite each separately by source_file + section_id/heading.
  - Do not merge conflicting excerpts into a single answer — report the conflict.
  - retrieval_warnings must be surfaced in the answer when present; low-confidence evidence must
    be flagged, not silently used.

citation_requirements:
  - Minimum citation: source_file (required).
  - Preferred citation: source_file + (section_id OR heading OR table_id).
  - Full citation: source_file + section_path + section_id + excerpt snippet.
  - For table results: include table_id and relevant row_keys in citation.

validation_notes:
  - excerpt must be source-grounded — no generated conclusions, no invented values
  - source_file is required; a bundle without it is invalid
  - heading or section_path should be present where possible for structured lookup results
  - retrieval_warnings must be populated for low-confidence or fallback cases
  - a bundle with an empty excerpt must include a retrieval_warning explaining why

common_failure_cases:
  - "excerpt is empty with no retrieval_warning — invalid bundle; do not answer from it"
  - "source_file is a Qdrant collection name, not a file path — invalid citation"
  - "LLM synthesizes an amount not present in excerpt — forbidden"
  - "section_id or heading absent for section_clause_lookup result — citation incomplete"
  - "retrieval_warnings missing despite fallback_needed: true in benchmark — silent failure"
  - "vector RAG score 0.3 with no warning — low-confidence result should be flagged"
````

## File: schemas/project-context.schema.yaml
````yaml
# project-context.schema.yaml
# Schema for <project>/rag/project-context.yaml

schema_name: project-context
version: 1
applies_to: "<project>/rag/project-context.yaml"

top_level_keys:
  version:
    type: integer
    required: true
    value: 1

  schema:
    type: string
    required: true
    value: "wiki-project-dependency-model"

  global_search_allowed:
    type: boolean
    required: true
    value: false
    notes: "Must always be false. Global wiki search is forbidden."

  project:
    type: object
    required: true
    required_keys:
      id:
        type: string
        notes: "Stable project identifier. e.g. 'apn-vocus-profitability'"
      slug:
        type: string
        pattern: "^[a-z0-9_]+$"
        notes: "Used as Qdrant filter value. Underscores only."
      name:
        type: string
        notes: "Human-readable project name."
      root:
        type: string
        notes: "Absolute path to project root on this machine."
      collection:
        type: string
        pattern: "^rag__project_[a-z0-9_]+$"
        notes: "Must be rag__project_<slug>."

  wiki:
    type: object
    required: true
    required_keys:
      root:
        value: "/Volumes/Data/_ai/_wiki"
      content_root:
        value: "/Volumes/Data/_ai/_wiki/wiki_stuff"
      data_root:
        value: "/Volumes/Data/_ai/_wiki/wiki-data"
      pattern:
        value: "karpathy-llm-wiki"
      canonical_shared_knowledge:
        type: boolean
        value: true

  tools:
    type: object
    required: true
    required_keys:
      rag_tools_root:
        value: "/Volumes/Data/_ai/_tool/tools_stuff/rag-tools"
      rag_tools_venv:
        value: "/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv"

  wiki_dependencies:
    type: list of objects
    required: true
    notes: "One entry per declared wiki domain. Empty list means no wiki access."
    item_required_keys:
      - domain
      - slug
      - collection
      - source_paths
      - reason
      - source_authority

  retrieval_policy:
    type: object
    required: true
    required_keys:
      - retrieval_order

  rules:
    type: object
    required: true
    notes: "All isolation rules should be true. Deviations require justification."

  forbidden_collections:
    type: list of string
    required: true
    notes: "Must include the globally forbidden set."

  status:
    type: object
    required: true
    required_keys:
      - lifecycle
      - owner
      - reviewed

common_failures:
  - "global_search_allowed: true  # must always be false"
  - "wiki.root path doesn't exist on this machine"
  - "wiki_dependencies entry missing 'reason' field"
  - "collection slug in wiki_dependencies doesn't match rag__wiki_<domain>"
  - "retrieval_order missing 'ask_user' step as final fallback"

example:
  project:
    id: "apn-vocus-profitability"
    slug: "vocus_profitability"
    name: "Vocus Profitability"
    root: "/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability"
    collection: "rag__project_vocus_profitability"
````

## File: schemas/project-documents.schema.yaml
````yaml
# project-documents.schema.yaml
# Schema for <project>/rag/manifests/project-documents.yaml

schema_name: project-documents
version: 1
applies_to: "<project>/rag/manifests/project-documents.yaml"

top_level_keys:
  version:
    type: integer
    required: true
    value: 1

  project_slug:
    type: string
    required: true
    pattern: "^[a-z0-9_]+$"
    notes: "Must match project_slug in retrieval-policy.yaml."

  rules:
    type: object
    required: true
    required_keys:
      default_index:
        type: boolean
        required: true
        value: false
        notes: "MUST be false. No document is indexed unless explicitly opted in."
      require_explicit_index_true:
        type: boolean
        required: true
        value: true
      raw_data_requires_explicit_approval:
        type: boolean
        required: true
        value: true
      communications_requires_review_before_indexing:
        type: boolean
        required: true
        value: true

  documents:
    type: list of objects
    required: true
    notes: "May be empty. Each entry represents one document."
    item_required_keys:
      id:
        type: string
        notes: "Stable unique ID for this document. Used as document_id in Qdrant."
      title:
        type: string
        notes: "Human-readable title."
      path:
        type: string
        notes: "Relative path from project root."
      type:
        type: string
        allowed_values:
          - report
          - manifest
          - reference
          - analysis
          - communication
          - raw
        notes: "Determines default caution level."
      index:
        type: boolean
        required: true
        notes: "Must be explicitly set. Defaults to false by rule."
      sensitive:
        type: boolean
        required: true
        notes: "If true, never index regardless of index flag."
      notes:
        type: string
        notes: "Required for any document with index: true or sensitive: true."

document_type_caution_levels:
  report: "Low — curated output, usually safe to index"
  manifest: "Low — structured metadata, usually safe"
  reference: "Low — reference material, usually safe"
  analysis: "Medium — may contain derived sensitive data, review before indexing"
  communication: "High — requires explicit review; never index by default"
  raw: "High — raw data; never index without explicit approval and notes"

common_failures:
  - "default_index: true  # must be false"
  - "document entry missing 'index' key (defaults are not safe — must be explicit)"
  - "sensitive: true but index: true — indexing blocked but both flags present"
  - "communication or raw type with index: true and no notes explaining approval"
  - "path doesn't exist relative to project root"

example_document:
  id: "report-margin-analysis-2026-q1"
  title: "Q1 2026 Margin Analysis Report"
  path: "reports/margin-analysis-2026-q1.md"
  type: "report"
  index: true
  sensitive: false
  notes: "Curated analysis report. Reviewed and approved for indexing 2026-05-24."
````

## File: schemas/retrieval-policy.schema.yaml
````yaml
# retrieval-policy.schema.yaml
# Schema for <project>/rag/retrieval-policy.yaml
#
# The rag-tools validate-policy CLI currently validates the flat top-level keys
# listed in the "Flat validator contract" section below. All other fields are
# validated only by human/agent review.

schema_name: retrieval-policy
version: 1
applies_to: "<project>/rag/retrieval-policy.yaml"

# --- Flat validator contract (validated by rag-tools validate-policy) ---

flat_validator_keys:
  version:
    type: integer
    required: true
    value: 1
    notes: "Must be integer 1."

  project_slug:
    type: string
    required: true
    pattern: "^[a-z0-9_]+$"
    notes: "Underscores only. No spaces, hyphens, or uppercase."
    example: "vocus_profitability"
    failure_cases:
      - "project_slug: vocus-profitability  # hyphens not allowed"
      - "project_slug: VocusProfitability   # uppercase not allowed"

  project_collection:
    type: string
    required: true
    pattern: "^rag__project_[a-z0-9_]+$"
    notes: "Must use rag__project_ prefix. Must match project_slug."
    example: "rag__project_vocus_profitability"
    failure_cases:
      - "rag__vocus_profitability   # missing project_ prefix"
      - "vocus_profitability        # no rag__ prefix at all"

  allowed_wiki_domains:
    type: list of string
    required: true
    item_pattern: "^[a-z0-9_]+$"
    notes: "List of domain slugs. Each must exist in domain-registry.yaml."
    example:
      - "nbn"
      - "vocus"
    failure_cases:
      - "allowed_wiki_domains: []       # empty list — no wiki access"
      - "allowed_wiki_domains: [ALL]    # not a valid slug"

  allowed_wiki_collections:
    type: list of string
    required: true
    item_pattern: "^rag__wiki_[a-z0-9_]+$"
    notes: "Must correspond 1:1 with allowed_wiki_domains. Each = rag__wiki_<domain>."
    example:
      - "rag__wiki_nbn"
      - "rag__wiki_vocus"
    failure_cases:
      - "rag__wiki_ALL           # forbidden"
      - "rag__nbn                # missing wiki_ infix"

  forbidden_collections:
    type: list of string
    required: true
    notes: "Must include at minimum all globally forbidden collection names."
    minimum_required:
      - "rag__global_all_docs"
      - "rag__wiki_all"
      - "rag__all"
      - "default"
      - "documents"
      - "knowledge"
      - "main"

  required_filters:
    type: list of string
    required: true
    notes: "Filters that must be applied to every query. Minimum: project_slug and wiki_domain."
    minimum_required:
      - "project_slug"
      - "wiki_domain"

  citation_rules:
    type: object
    required: true
    required_keys:
      - cite_sources
      - cite_collection_name
      - cite_source_file
      - cite_section_path
      - cite_heading
    notes: "All citation flags should be true. Setting any to false must have justification."

# --- Common validation failures ---

common_failures:
  - "project_slug and project_collection slug don't match"
  - "allowed_wiki_collections contains a name not in allowed_wiki_domains"
  - "allowed_wiki_collections contains a forbidden name"
  - "missing required_filters key"
  - "YAML parse error due to unquoted colon in values"
  - "version field missing or wrong type (must be integer, not string)"
````

## File: schemas/retrieval-strategy.schema.yaml
````yaml
# Schema: retrieval-strategy.schema.yaml
# Purpose: Validates <project>/rag/retrieval-strategy.yaml files.
# Authority: skill-project-wiki-rag-bridge / archcore specs layer

schema_name: retrieval-strategy
version: 1
applies_to: "<project-root>/rag/retrieval-strategy.yaml"

purpose: >
  Per-project retrieval strategy configuration. Records the chosen primary, secondary, and
  fallback retrieval mode for each candidate document, along with RAG suitability, benchmark
  status, and the index_allowed gate. Produced by prompt 02b; updated by prompt 02c.

required_top_level_keys:
  - version       # integer, must be 1
  - project       # object with id, slug, name
  - strategy_defaults  # object with mode keys
  - documents     # list of document strategy entries
  - rules         # object with boolean policy flags

required_project_keys:
  - id            # string; unique project identifier
  - slug          # string; lowercase alphanumeric + underscores; matches Qdrant slug
  - name          # string; human-readable project name

required_strategy_defaults_keys:
  - exact_facts
  - tables
  - structured_sections
  - cross_document_semantic
  - invoices
  - pdfs

required_document_entry_keys:
  - document_id           # string; file stem (no extension)
  - path                  # string; relative path from project root
  - document_class        # string; one of the allowed document_class values
  - primary               # string; primary retrieval mode
  - rag_suitability       # string; suitable | partially_suitable | not_suitable
  - benchmark_required    # boolean
  - benchmark_status      # string; not_run | passed | partial | failed
  - index_allowed         # boolean; must be false unless benchmark_status: passed AND rag_suitability in (suitable, partially_suitable)
  - reason                # string; explains route selection

optional_document_entry_keys:
  - authority             # string; project_local | wiki_authoritative_markdown | external_reference
  - secondary             # string; secondary retrieval mode
  - fallback              # string; fallback retrieval mode

allowed_document_class_values:
  - structured_markdown_reference
  - legal_contract_or_terms
  - financial_rate_card
  - invoice_or_billing_report
  - operational_runbook
  - policy_document
  - meeting_notes
  - knowledge_article
  - source_code_docs
  - unstructured_pdf
  - scanned_pdf
  - tabular_dataset
  - mixed_content
  - unknown

allowed_retrieval_modes:
  - direct_structured_lookup
  - section_clause_lookup
  - heading_aware_lookup
  - table_aware_lookup
  - tabular_analytics
  - keyword_lookup
  - vector_rag
  - extraction_required
  - hybrid_direct_first
  - hybrid_rag_first

required_rules_keys:
  - source_files_remain_authoritative   # must be true
  - profile_before_index                # must be true
  - benchmark_before_default_route      # must be true
  - evidence_bundle_required            # must be true
  - vector_rag_not_universal_default    # must be true

validation_notes:
  - index_allowed must be false when rag_suitability is not_suitable
  - index_allowed must be false when benchmark_status is not_run or failed
  - index_allowed may be true only when both rag_suitability is suitable or partially_suitable AND benchmark_status is passed
  - document_class must be one of the allowed values; unknown triggers a warning
  - strategy_defaults values are free strings but should match allowed_retrieval_modes
  - version must be the integer 1

common_failure_cases:
  - "index_allowed: true without benchmark_status: passed — forbidden"
  - "rag_suitability: not_suitable with index_allowed: true — forbidden"
  - "benchmark_required: false for a structured or tabular document — should be true"
  - "missing reason field — required for audit traceability"
  - "document_class: unknown — profile-file must be re-run or classification done manually"
  - "document_id does not match file stem — misalignment causes retrieval routing failures"
````

## File: schemas/wiki-domain-registry.schema.yaml
````yaml
# wiki-domain-registry.schema.yaml
# Schema for /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml

schema_name: wiki-domain-registry
version: 1
applies_to: "/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml"

top_level_keys:
  version:
    type: integer
    required: true
    value: 1

  wiki_root:
    type: string
    required: true
    value: "/Volumes/Data/_ai/_wiki"

  content_root:
    type: string
    required: true
    value: "/Volumes/Data/_ai/_wiki/wiki_stuff"

  domains:
    type: list of objects
    required: true
    notes: "Each entry declares one wiki domain."
    item_required_keys:
      domain:
        type: string
        required: true
        notes: "Domain name, lowercase. e.g. 'nbn'"
      slug:
        type: string
        required: true
        pattern: "^[a-z0-9_]+$"
        notes: "Used in collection names and filter values. Usually matches domain."
      description:
        type: string
        required: true
        notes: "What knowledge this domain contains."
      source_paths:
        type: list of string
        required: true
        notes: "Paths relative to content_root. e.g. ['domains/nbn']"
      qdrant_collection:
        type: string
        required: true
        pattern: "^rag__wiki_[a-z0-9_]+$"
        notes: "Must be rag__wiki_<slug>."
      status:
        type: string
        required: true
        allowed_values:
          - active
          - draft
          - deprecated
        notes: "Only 'active' domains are eligible for indexing."

  rules:
    type: object
    required: true
    required_keys:
      disallow_global_collection:
        type: boolean
        value: true
      require_declared_domain:
        type: boolean
        value: true
      require_source_path:
        type: boolean
        value: true
      require_collection_per_domain:
        type: boolean
        value: true

validation_notes:
  - "Each domain must have its own Qdrant collection — no sharing."
  - "qdrant_collection must always be rag__wiki_<slug>, never rag__wiki_all or similar."
  - "source_paths must exist as directories under wiki_stuff/."
  - "deprecated domains must not be queried by projects unless explicitly grandfathered."

common_failures:
  - "slug and qdrant_collection suffix mismatch (e.g. slug='nbn' but collection='rag__wiki_nbn_v2')"
  - "status: active but source_paths directory doesn't exist"
  - "qdrant_collection: rag__wiki_all  # forbidden global name"
  - "domain entry with no description — fails human review"

example_entry:
  - domain: "nbn"
    slug: "nbn"
    description: "NBN/WBA/DCR rebate, credit, discount, campaign, and eligibility reference."
    source_paths:
      - "domains/nbn"
    qdrant_collection: "rag__wiki_nbn"
    status: "active"
````

## File: templates/AGENTS-project-wiki-bridge-block.md
````markdown
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
````

## File: templates/AI_NAVIGATION-project-wiki-bridge-block.md
````markdown
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
````

## File: templates/benchmark-queries.yaml
````yaml
# benchmark-queries.yaml — benchmark query set for rag-tools benchmark-file
# Template: copy to <project-root>/rag/benchmarks/queries/<document_id>-queries.yaml
# Usage: rag-tools benchmark-file <path> --queries <this-file>
# Schema: skill-project-wiki-rag-bridge/schemas/benchmark-queries (inline below)

version: 1

document_id: "<document-id>"           # must match retrieval-strategy.yaml document_id
document_class: "<class>"              # structured_markdown_reference | financial_rate_card | etc.

# Minimum 5 queries. Weight toward the primary retrieval mode:
# - structured_markdown_reference → section/heading queries
# - financial_rate_card / invoice_or_billing_report → table queries
# - knowledge_article → semantic/cross-section queries

queries:
  - id: "Q1"
    query: "<question that tests exact section or fact extraction>"
    expected_source:
      section_id: "<section-ID or null>"           # e.g. "C2.11" or null
      heading_contains: "<heading text or null>"   # e.g. "Rebate Calculation" or null
      table_contains: "<table header or value or null>"
    expected_terms:
      - "<term-that-must-appear-in-excerpt>"
    expected_answer_contains:
      - "<value or phrase — for human review>"
    retrieval_modes:
      - structured          # test structured heading/section lookup
      - table               # test table-aware lookup
      # - vector_rag        # uncomment only if Qdrant collection exists
    notes: "<why this query matters — e.g. tests rebate period 3 amount>"

  - id: "Q2"
    query: "<question that tests table retrieval>"
    expected_source:
      section_id: null
      heading_contains: null
      table_contains: "<header cell text>"
    expected_terms:
      - "<column header>"
      - "<expected cell value>"
    expected_answer_contains:
      - "<expected amount or rate>"
    retrieval_modes:
      - table
      - structured
    notes: "<e.g. tests rate card lookup for service X in period Y>"

  - id: "Q3"
    query: "<question that tests heading navigation>"
    expected_source:
      section_id: null
      heading_contains: "<heading text>"
      table_contains: null
    expected_terms:
      - "<term expected in that section>"
    expected_answer_contains:
      - "<phrase or value>"
    retrieval_modes:
      - structured
    notes: "<e.g. tests heading-level navigation for clause lookup>"

  - id: "Q4"
    query: "<cross-section or semantic question>"
    expected_source:
      section_id: null
      heading_contains: null
      table_contains: null
    expected_terms:
      - "<key term>"
    expected_answer_contains:
      - "<expected concept>"
    retrieval_modes:
      - structured
      # - vector_rag
    notes: "<e.g. tests whether structured lookup handles cross-section intent>"

  - id: "Q5"
    query: "<negative or edge-case query — tests fallback behavior>"
    expected_source:
      section_id: null
      heading_contains: null
      table_contains: null
    expected_terms: []
    expected_answer_contains: []
    retrieval_modes:
      - structured
      - table
    notes: "Expect fallback_needed: true — confirms benchmark detects retrieval gaps"
````

## File: templates/evidence-bundle.yaml
````yaml
# evidence-bundle.yaml — EvidenceBundle output contract reference
# Template: reference or copy to show expected output structure.
# Schema: skill-project-wiki-rag-bridge/schemas/evidence-bundle.schema.yaml
#
# EvidenceBundle is the required output of every rag-tools retrieval command.
# LLM answers must be grounded in evidence from these fields — no training knowledge.

query: "<the original user query or lookup term>"
# Required. The exact query submitted to the retrieval function.

retrieval_mode: "<mode>"
# Required. One of:
#   direct_structured_lookup | section_clause_lookup | heading_aware_lookup |
#   table_aware_lookup | tabular_analytics | keyword_lookup | vector_rag | hybrid

document_id: "<document stem>"
# Optional but strongly recommended.
# The stem of the source file (without extension).

source_file: "<absolute path to source file>"
# Required. The canonical authoritative source.
# Never a Qdrant collection name — always the actual file.

source_type: "<file extension without dot>"
# Optional. e.g. "md", "csv", "yaml".

authority: "source"
# Optional. Indicates the authority level of this evidence.
# Values: source | wiki_article | external_reference | derived

section_id: "<section ID or null>"
# Optional. Structured section ID detected in the source (e.g. "C2.11", "1.2.3").
# Presence enables direct citation by clause ID.

section_path:
  - "<H1 heading>"
  - "<H2 heading>"
  - "<H3 heading>"
# Optional list. Heading chain from document root to the matched section.
# Should be present for structured/section lookup results.

heading: "<nearest heading above the matched text>"
# Optional. The single nearest heading label for display in citations.

table_id: "<table ID or null>"
# Optional. Present for table_aware_lookup results.
# Identifies which table in the document was matched.

row_keys:
  - "<first few cells of matched rows for identification>"
# Optional list. Short row-key preview for table match identification.

excerpt: "<verbatim extracted text from source — no paraphrase>"
# Required. The LLM must answer ONLY from this field.
# Rules:
#   - Must be verbatim from the source file
#   - Must not contain generated conclusions or LLM-synthesized text
#   - Must not contain invented amounts, dates, or identifiers
#   - If blank, the bundle is invalid — do not answer from it

matched_terms:
  - "<terms from the query that matched in the source>"
# Optional list. Supports citation transparency and debugging.

score_or_confidence: 0.0
# Optional float. Relevance score or confidence from the retrieval function.
# For deterministic lookup, may be 1.0 (exact match) or based on term overlap.

context_chars: 0
# Auto-calculated as len(excerpt). Used to estimate retrieval coverage.

retrieval_warnings:
  - "<warning string or empty list>"
# Optional list. Must be populated when:
#   - source file was missing at retrieval time
#   - retrieval mode fell back from primary to secondary
#   - evidence is low-confidence or partial
#   - vector RAG result had low score and fallback was used
#   - structured lookup found no exact section match
# Examples:
#   "source file missing"
#   "no exact section ID match; nearest heading used"
#   "vector RAG score < 0.5; fallback to structured lookup"
#   "table match is partial; only header row matched"
````

## File: templates/project-context.yaml
````yaml
# project-context.yaml — RAG bridge configuration for a project
# Copy to: <project>/rag/project-context.yaml
# This file is ROUTING METADATA ONLY — not an authoritative source of facts.
# Replace all <placeholder> values before use.

version: 1
schema: "wiki-project-dependency-model"
global_search_allowed: false

project:
  id: "<project-id>"                            # e.g. "apn-vocus-profitability"
  slug: "<project_slug>"                        # e.g. "vocus_profitability" (underscores, no spaces)
  name: "<Project Name>"                        # e.g. "Vocus Profitability"
  root: "<absolute-project-root>"              # e.g. "/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability"
  collection: "rag__project_<project_slug>"    # e.g. "rag__project_vocus_profitability"

wiki:
  root: "/Volumes/Data/_ai/_wiki"
  content_root: "/Volumes/Data/_ai/_wiki/wiki_stuff"
  data_root: "/Volumes/Data/_ai/_wiki/wiki-data"
  pattern: "karpathy-llm-wiki"
  canonical_shared_knowledge: true

tools:
  rag_tools_root: "/Volumes/Data/_ai/_tool/tools_stuff/rag-tools"
  rag_tools_venv: "/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv"

# Declare ONLY the wiki domains this project is allowed to query.
# Do not list domains you do not need — undeclared domains are forbidden.
wiki_dependencies:
  - domain: "<domain>"                          # e.g. "nbn"
    slug: "<domain>"
    collection: "rag__wiki_<domain>"           # e.g. "rag__wiki_nbn"
    source_paths:
      - "domains/<domain>"                     # relative to wiki_stuff
    reason: "<why this project may use this domain>"
    source_authority: "shared_reference_authoritative_markdown"
    allowed_topics:
      - "<topic-1>"
      - "<topic-2>"
  # Add more domains below. Keep the list minimal.
  # - domain: "<domain2>"
  #   slug: "<domain2>"
  #   collection: "rag__wiki_<domain2>"
  #   source_paths:
  #     - "domains/<domain2>"
  #   reason: "<why>"
  #   source_authority: "shared_reference_authoritative_markdown"
  #   allowed_topics: []

retrieval_policy:
  retrieval_order:
    - step: 1
      source: "project_local_files"
      description: "Use project-local source files, reports, manifests, and analysis first."
    - step: 2
      source: "project_collection"
      collection: "rag__project_<project_slug>"
      required_filters:
        project_slug: "<project_slug>"
    - step: 3
      source: "declared_wiki_domains"
      collections:
        - "rag__wiki_<domain>"
      required_filters:
        wiki_domain:
          allowed:
            - "<domain>"
    - step: 4
      source: "ask_user"
      condition: "No sufficient evidence found in project-local or declared wiki sources."

rules:
  require_project_filter: true
  require_wiki_domain_filter: true
  disallow_global_wiki_search: true
  disallow_undeclared_wiki_domains: true
  disallow_cross_project_fallback: true
  disallow_project_data_in_wiki_collection: true
  disallow_wiki_data_in_project_collection_unless_copied_with_source: true
  cite_sources: true
  cite_collection_name: true
  cite_source_file: true
  cite_section_path: true
  cite_heading: true
  prefer_project_local_for_project_specific_facts: true
  prefer_wiki_authoritative_markdown_for_shared_reference_facts: true
  nav_yaml_is_routing_metadata_only: true
  no_unsupported_conclusions: true

forbidden_collections:
  - "rag__global_all_docs"
  - "rag__wiki_all"
  - "rag__all"
  - "default"
  - "documents"
  - "knowledge"
  - "main"

conflict_resolution:
  project_specific_fact:
    prefer: "project_local"
    examples:
      - invoices
      - internal_reports
      - customer_mappings
      - calculated_output
  shared_reference_fact:
    prefer: "wiki_authoritative_markdown"
    examples:
      - standards
      - rate_card_interpretations
      - policy_definitions
  unresolved_conflict:
    action: "report_conflict_and_ask_user"

status:
  lifecycle: "draft"            # draft | active | deprecated
  owner: "project"
  reviewed: false
````

## File: templates/project-documents.yaml
````yaml
# project-documents.yaml — manifest declaring which project documents may be indexed
# Copy to: <project>/rag/manifests/project-documents.yaml
#
# IMPORTANT: default_index is false. Every document must have index: true explicitly set
# before it will be indexed. Raw, sensitive, and communications data requires
# extra approval before setting index: true.

version: 1

project_slug: "<project_slug>"

rules:
  default_index: false                              # NO document is indexed unless index: true
  require_explicit_index_true: true                 # Explicit opt-in required for every document
  raw_data_requires_explicit_approval: true         # Raw/sensitive data needs approval note
  communications_requires_review_before_indexing: true  # Comms must be reviewed first

documents:
  - id: "<doc-id-1>"
    title: "<Document Title>"
    path: "<relative-path-from-project-root>"      # e.g. "docs/reports/analysis-2026.md"
    type: "report"                                 # report | manifest | reference | analysis | communication | raw
    index: false                                   # Set to true ONLY after review
    sensitive: false                               # true = never index regardless of index flag
    notes: "<reason for current index setting>"

  - id: "<doc-id-2>"
    title: "<Another Document>"
    path: "<relative-path>"
    type: "analysis"
    index: false
    sensitive: false
    notes: "Pending review before indexing."

  # Communications — require explicit review note
  # - id: "comms-email-001"
  #   title: "Email thread re: billing dispute"
  #   path: "communications/email-thread-001.md"
  #   type: "communication"
  #   index: false
  #   sensitive: true
  #   notes: "Contains customer PII. Do not index without legal review."

  # Raw data — require explicit approval
  # - id: "raw-invoice-data"
  #   title: "Invoice CSV export"
  #   path: "docs/csv/invoices.csv"
  #   type: "raw"
  #   index: false
  #   sensitive: true
  #   notes: "Raw financial data. Do not index."

status:
  lifecycle: "draft"
  reviewed: false
  last_reviewed: null
````

## File: templates/project-wiki-bridge.md
````markdown
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
````

## File: templates/qdrant-collection-policy.md
````markdown
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
````

## File: templates/retrieval-policy.yaml
````yaml
# retrieval-policy.yaml — flat retrieval policy for rag-tools validator
# Copy to: <project>/rag/retrieval-policy.yaml
# Replace all <placeholder> values before use.
#
# NOTE: The rag-tools validate-policy CLI currently validates the flat top-level keys
# listed below. The richer nested project-context.yaml carries additional detail.
# Both files are required; keep them consistent.

version: 1

# --- Flat validator contract keys (required by rag-tools validate-policy) ---

project_slug: "<project_slug>"
project_collection: "rag__project_<project_slug>"

allowed_wiki_domains:
  - "<domain>"
  # Add more declared domains here. Remove any domain you do not actually need.

allowed_wiki_collections:
  - "rag__wiki_<domain>"
  # Must correspond 1:1 with allowed_wiki_domains entries above.

forbidden_collections:
  - "rag__global_all_docs"
  - "rag__wiki_all"
  - "rag__all"
  - "default"
  - "documents"
  - "knowledge"
  - "main"

required_filters:
  - "project_slug"
  - "wiki_domain"

citation_rules:
  cite_sources: true
  cite_collection_name: true
  cite_source_file: true
  cite_section_path: true
  cite_heading: true

# --- Rich agent/human guidance (not currently parsed by validator) ---

project:
  id: "<project-id>"
  name: "<Project Name>"

retrieval_order:
  - step: 1
    source: "project_local_files"
    description: "Project-local source files, reports, manifests, and analysis first."
  - step: 2
    source: "project_collection"
    collection: "rag__project_<project_slug>"
    filter_required: "project_slug = <project_slug>"
  - step: 3
    source: "declared_wiki_domains"
    collections:
      - "rag__wiki_<domain>"
    filter_required: "wiki_domain in [<domain>]"
  - step: 4
    source: "ask_user"
    condition: "No sufficient evidence found in steps 1–3."

authority_rules:
  project_specific_facts: "project_local"
  shared_reference_facts: "wiki_authoritative_markdown"
  nav_yaml: "routing_metadata_only"

hard_rules:
  - "Never query undeclared wiki domains."
  - "Never query global or mixed collections."
  - "Never mix project data into wiki collections."
  - "Never treat nav YAML as authoritative source text."
  - "Every result must cite source_file, section_path, heading, and collection."
  - "If insufficient evidence found, say so — do not speculate."

status:
  lifecycle: "draft"
  reviewed: false
````

## File: templates/retrieval-strategy.yaml
````yaml
# retrieval-strategy.yaml — per-project retrieval strategy routing
# Template: copy to <project-root>/rag/retrieval-strategy.yaml and fill in.
# Schema: skill-project-wiki-rag-bridge/schemas/retrieval-strategy.schema.yaml

version: 1

project:
  id: "<project-id>"                  # e.g. "apn-vocus-profitability"
  slug: "<project_slug>"              # e.g. "vocus_profitability" (matches Qdrant collection slug)
  name: "<Project Name>"              # human-readable

# Default retrieval routes by query intent.
# Override per-document in the documents list below.
strategy_defaults:
  exact_facts: "direct_structured_lookup"     # amounts, dates, IDs, clause references
  tables: "table_aware_lookup"                # rate cards, pricing grids, invoice line items
  structured_sections: "section_clause_lookup" # clause X.Y, section heading navigation
  cross_document_semantic: "vector_rag"       # broad questions spanning multiple articles
  invoices: "tabular_analytics"               # aggregate invoice/billing calculations
  pdfs: "extract_first"                       # PDFs require extraction before any lookup

# Per-document routing decisions.
# Generated by: rag-tools profile-file + rag-tools recommend-strategy + optional benchmark-file
documents:
  - document_id: "<document-id>"          # stem of the file (without extension)
    path: "<relative-path>"               # relative to project root
    document_class: "<class>"             # from profile-file output:
                                          # structured_markdown_reference | legal_contract_or_terms |
                                          # financial_rate_card | invoice_or_billing_report |
                                          # operational_runbook | policy_document | meeting_notes |
                                          # knowledge_article | source_code_docs | unstructured_pdf |
                                          # scanned_pdf | tabular_dataset | mixed_content | unknown
    authority: "project_local"            # project_local | wiki_authoritative_markdown | external_reference
    primary: "<retrieval-mode>"           # direct_structured_lookup | section_clause_lookup |
                                          # table_aware_lookup | heading_aware_lookup |
                                          # tabular_analytics | keyword_lookup | vector_rag |
                                          # extraction_required
    secondary: "<retrieval-mode>"
    fallback: "<retrieval-mode>"
    rag_suitability: "not_suitable"       # suitable | partially_suitable | not_suitable
    benchmark_required: true              # true for structured/tabular/exact-fact docs
    benchmark_status: "not_run"          # not_run | passed | partial | failed
    index_allowed: false                  # always false at profile time; only true after benchmark + approval
    reason: "<why this route was selected — include benchmark label if run>"

rules:
  source_files_remain_authoritative: true       # source files are never replaced by RAG results
  profile_before_index: true                    # profile-file must run before index_allowed: true
  benchmark_before_default_route: true          # benchmark-file required for structured/tabular docs
  evidence_bundle_required: true                # all answers must be grounded in EvidenceBundle
  vector_rag_not_universal_default: true        # vector RAG is one path, not the default for all files
````

## File: templates/source-profile.yaml
````yaml
# source-profile.yaml — document profile output from rag-tools profile-file
# Template: copy to <project-root>/rag/source-profiles/<document_id>.yaml
# Populate from: rag-tools profile-file <path> output (JSON → YAML)
# Schema: skill-project-wiki-rag-bridge/schemas/document-profile.schema.yaml

document_id: "<stem-of-file>"          # path.stem — no extension
title: "<document title>"              # first heading or file stem if no heading
path: "<absolute-path-to-file>"        # full path as returned by profile-file

# File structure
file_type: "<extension>"               # .md | .txt | .csv | .tsv | .json | .yaml | .pdf | .xlsx
size_bytes: 0
line_count: 0
estimated_tokens: 0

# Classification (set by rag-tools document_profiler._document_class)
document_class: "unknown"              # structured_markdown_reference | legal_contract_or_terms |
                                       # financial_rate_card | invoice_or_billing_report |
                                       # operational_runbook | policy_document | meeting_notes |
                                       # knowledge_article | source_code_docs | unstructured_pdf |
                                       # scanned_pdf | tabular_dataset | mixed_content | unknown

# Structural features (all booleans from profile-file output)
has_headings: false
heading_count: 0
heading_levels: []                     # e.g. [1, 2, 3]
has_tables: false
table_count: 0
has_section_ids: false                 # e.g. "C2.11", "1.2.3" style IDs
section_ids: []                        # list of detected section ID strings
has_toc: false
has_frontmatter: false
has_repeated_entities: false           # recurring named entities (suggests reference doc)

# Content signals
has_dates: false
has_amounts: false                     # currency, percentages, numeric amounts
has_definitions: false
has_cross_references: false            # links or section-ID references to other parts

# Safety flag
contains_sensitive_data: false         # api_key, password, secret, token patterns detected

# Authority and retrieval
authoritative: true                    # true = source of truth; false = derived/secondary
recommended_retrieval_modes:           # ordered list from profile-file / recommend-strategy
  - "<mode>"

# Index gate (set by strategy, not by profiler directly)
index_allowed: false                   # always false at profile stage; update after strategy + benchmark

# Notes (populated by profile-file or manually)
notes: []
````

## File: templates/wiki-domain-index.md
````markdown
---
title: "<Domain Name> Domain Index"
type: "domain-index"
domain: "<domain_slug>"
status: "active"
updated: "YYYY-MM-DD"
---

# <Domain Name> Domain Index

## Purpose

<One paragraph: what knowledge this domain contains, what projects may use it, and what it is authoritative for.>

## Scope

This domain covers:

- <topic 1>
- <topic 2>
- <topic 3>

Out of scope for this domain:

- <excluded topic 1>
- <excluded topic 2>

## Contents

| File | Description |
|---|---|
| `references/<article>.md` | <Brief description> |

## Qdrant collection

Collection: `rag__wiki_<domain_slug>`

Indexed by: `rag-tools index-domain --domain <domain_slug>`

## Projects with declared access

| Project | Reason |
|---|---|
| `<project-slug>` | <why this project may use this domain> |

## Related domains

- [[<related-domain>]] — <relationship>

## Notes

- All articles in this domain must have `domain: <domain_slug>` frontmatter.
- Do not add project-specific data to this domain — keep it shared reference only.
- Source references are mandatory for all articles.
````

## File: templates/wiki-domain-registry-entry.yaml
````yaml
# wiki-domain-registry-entry.yaml — single domain entry for domain-registry.yaml
# Append this block under the `domains:` list in:
#   /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml
# Replace all <placeholder> values before use.

# --- Paste this block into domain-registry.yaml under domains: ---
#
#   - domain: "<domain>"
#     slug: "<domain_slug>"
#     description: "<What knowledge this domain contains and its purpose>"
#     source_paths:
#       - "domains/<domain_slug>"              # relative to wiki_stuff content_root
#     qdrant_collection: "rag__wiki_<domain_slug>"
#     status: "active"                        # active | draft | deprecated

# --- Example (NBN domain, already exists) ---
#
#   - domain: "nbn"
#     slug: "nbn"
#     description: "NBN/WBA/DCR rebate, credit, discount, campaign, and eligibility reference."
#     source_paths:
#       - "domains/nbn"
#     qdrant_collection: "rag__wiki_nbn"
#     status: "active"

# --- Template entry ---

  - domain: "<domain>"
    slug: "<domain_slug>"
    description: "<Concise description of what knowledge this domain contains>"
    source_paths:
      - "domains/<domain_slug>"
    qdrant_collection: "rag__wiki_<domain_slug>"
    status: "active"
````

## File: templates/wiki-reference-article.md
````markdown
---
title: "<Title>"
type: "reference"
domain: "<domain_slug>"
status: "active"
authority: "shared_reference"
source:
  type: "<source-type>"                          # document | url | extract | derived
  path: "<source-path-or-url>"                  # e.g. "raw/nbn-wba-annexure-20260101.md"
tags:
  - wiki
  - "<domain_slug>"
  - "<topic-tag>"
updated: "YYYY-MM-DD"
---

# <Title>

## Purpose

<One paragraph: what this article is, why it exists in this wiki domain, and what agents should use it for.>

## Summary

<2–5 sentence summary of the key information. Write for retrieval — dense, factual, no filler.>

## Key rules / facts

- <Fact or rule 1>
- <Fact or rule 2>
- <Fact or rule 3>

## Eligibility / scope

<Who or what this applies to. Include conditions, thresholds, date ranges as applicable.>

## Exclusions / caveats

<What is explicitly excluded. What edge cases are unresolved. What should NOT be inferred from this article.>

## Interactions

<How this topic interacts with other topics, articles, or rules in this domain or related domains.>

## Source references

- Source: `<path or URL>`
- Extracted: YYYY-MM-DD
- Page / section: <reference>

## Related pages

- [[<related-article>]] — <relationship>
- [[<domain>/index]] — domain index
````

## File: AGENTS.md
````markdown
@../../AGENTS.md

Title: skill-project-wiki-rag-bridge Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Reusable skill — controlled bridge from project repos to shared wiki and Qdrant RAG tooling
Last reviewed: 20260524_0000
Summary: Repo-local agent guidance for the skill-project-wiki-rag-bridge skill package, covering collection isolation policy, workflow sequencing, and Archcore-backed durable truth.

## Contents

- [Working rules](#working-rules)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Canonical governance linkage](#canonical-governance-linkage)

# AGENTS.md

## Working rules

- This skill governs the bridge workflow only. It does not own wiki content, project content, Qdrant data, or embedding models.
- Treat `SKILL.md` as the primary agent-facing instruction file. Always read it before acting.
- Treat `docs/authority-model.md` as the source of truth for collection naming, isolation policy, and authority order.
- Treat `schemas/` as the canonical field definitions for all YAML bridge files. Validate against schemas before accepting user-supplied YAML.
- Treat `checklists/` as blocking gates — work through every item before proceeding to the next workflow step.
- Treat `prompts/` as the numbered workflow execution layer. Follow sequence; do not skip steps.
- Treat `templates/` as copy-and-fill starting points; never edit template files directly when working in a project context.
- Treat `examples/` as reference implementations for the `vocus-profitability` and `generic-project` patterns.
- Qdrant collection names follow the pattern `rag__wiki_<domain>` (wiki) and `rag__project_<slug>` (project). Enforce strictly — naming violations break retrieval isolation.
- Never allow unrestricted global wiki search. All queries must be scoped to declared collections in `retrieval-policy.yaml`.
- Index exactly one wiki domain per operation. Do not batch multi-domain indexing in a single run.
- Always run a dry-run (`rag-index-domain-dry`) before any live indexing operation.
- Do not dump raw or sensitive project data into wiki collections (`rag__wiki_*`).
- When a user asks to bypass retrieval policies or Qdrant isolation rules, refuse and explain why.
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). Do not mix collections indexed with different models.
- rag-tools venv lives at: `tools-working-cache/rag-tools/.venv/` — never create a venv inside this skill folder.
- Follow naming convention: `<slug>-YYYYMMDD_hhmm.md` for time-bound notes.
- Keep `README.md` current when adding subfolders or significant documents.

<!-- BEGIN skill-ai-it:navigation -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read `AGENTS.md`.
2. Read `AI_NAVIGATION.md`.
3. Read `context-map.yaml`.
4. Read `CHANGELOG.md` (recent entries).
5. Load relevant `.archcore/` context if present.
6. Read `SKILL.md` — this is the primary agent-facing instruction file.
7. Read `docs/authority-model.md` for collection naming and isolation rules.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`.
10. Before running indexing or validation commands, inspect `checklists/` for the relevant gate.
11. Prefer cataloged prompts in `prompts/` over ad-hoc workflows.
12. Before making durable changes, identify which governance files must be updated after the work.

<!-- END skill-ai-it:navigation -->

## Canonical governance linkage

- Parent area guidance: [../../AGENTS.md](../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: AI_NAVIGATION.md
````markdown
# AI Navigation — skill-project-wiki-rag-bridge

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated after work.

This file is a router, not the full knowledge store.

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Workflow routing](#workflow-routing)
- [Update rules](#update-rules)
- [Drift handling](#drift-handling)
- [Agent answer contract](#agent-answer-contract)

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. `SKILL.md` — primary agent-facing workflow instructions
6. `docs/authority-model.md` — collection naming and isolation rules
7. Relevant `.archcore/` documents if present
8. Task-specific files based on routing below

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, and guides
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `SKILL.md`
6. `docs/authority-model.md`
7. `docs/collection-naming-policy.md`
8. `docs/architecture.md`
9. `CHANGELOG.md`
10. `SCRATCHPAD.md` — temporary only; not durable unless marked `KEEP` or promoted to Archcore

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `SKILL.md` | Primary agent-facing skill instructions | High |
| `docs/authority-model.md` | Collection isolation and authority source | High |
| `docs/collection-naming-policy.md` | Qdrant naming rules | High |
| `ARCHITECTURE.md` | Root-level architecture overview, layer diagram, retrieval flow, isolation model | High |
| `SETUP.md` | Prerequisites, rag-tools venv path, skill install, first-use sequence | High |
| `docs/architecture.md` | Detailed layer diagram and design decision rationale | Medium-high |
| `docs/flow-diagram.md` | Data flow reference | Medium |
| `docs/multi-project-model.md` | Multi-project bridge patterns | Medium |
| `docs/failure-modes.md` | Known failure patterns and mitigations | Medium |
| `docs/operating-runbook.md` | Operational runbook | High |
| `docs/dynamic-retrieval-strategy.md` | When not to use vector RAG; profile-first routing | High |
| `docs/evidence-contract.md` | EvidenceBundle answer rules and citation requirements | High |
| `docs/retrieval-mode-decision-tree.md` | Mode selection flowchart and quick reference | High |
| `schemas/*.schema.yaml` | YAML field definitions and validation | High |
| `checklists/*.md` | Blocking gate checklists | High |
| `prompts/00–09-*.md` | Numbered workflow execution prompts | High (in-sequence) |
| `templates/` | Copy-and-fill project bridge templates | Medium |
| `examples/vocus-profitability/` | Reference implementation | Medium |
| `examples/generic-project/` | Generic reference implementation | Medium |
| `CHANGELOG.md` | Durable skill/governance change history | Medium-high |
| `SCRATCHPAD.md` | Temporary notes | Low |

## Task routing

### Architecture and isolation questions

Read:
1. `ARCHITECTURE.md` — layer model, retrieval flow, isolation enforcement, CLI command map
2. `.archcore/adr/`
3. `.archcore/specs/`
4. `docs/authority-model.md`
5. `docs/collection-naming-policy.md`
6. `docs/architecture.md`
7. `docs/multi-project-model.md`

### Workflow / how-to questions

Read:
1. `SKILL.md` (section: When to use, Workflow sequence)
2. `prompts/` (numbered files — follow sequence)
3. `checklists/` (blocking gates for each step)
4. `docs/operating-runbook.md`

### Validation and policy questions

Read:
1. `.archcore/rules/`
2. `docs/authority-model.md`
3. `schemas/retrieval-policy.schema.yaml`
4. `schemas/project-context.schema.yaml`
5. `checklists/project-bridge-readiness.md`
6. `checklists/multi-project-isolation.md`

### Troubleshooting

Read:
1. `docs/failure-modes.md`
2. `docs/operating-runbook.md`
3. `prompts/09-troubleshoot-rag-bridge.md`
4. `checklists/rag-tools-readiness.md`
5. `checklists/retrieval-validation.md`

### Template and example questions

Read:
1. `templates/` — pick the matching template
2. `examples/vocus-profitability/` or `examples/generic-project/`
3. `schemas/` — validate field names against schema
4. `docs/authority-model.md` — confirm collection naming rules

### Governance and update questions

Read:
1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. `.archcore/rules/`

## Workflow routing

The standard bridge workflow uses numbered prompts in sequence. Do not skip steps.

| Step | Prompt | Checklist gate |
|---|---|---|
| 0 | `prompts/00-verify-wiki-operational-state.md` | `checklists/wiki-operational-readiness.md` |
| 1 | `prompts/01-create-wiki-domain.md` | — |
| 2 | `prompts/02-verify-rag-tools.md` | `checklists/rag-tools-readiness.md` |
| 3 | `prompts/03-create-project-bridge.md` | `checklists/project-bridge-readiness.md` |
| 4 | `prompts/04-validate-project-policy.md` | — |
| 4b | `prompts/02b-profile-and-recommend-strategy.md` | profile gate in `checklists/indexing-readiness.md` |
| 4c | `prompts/02c-benchmark-retrieval-routes.md` | benchmark results recorded in `retrieval-strategy.yaml` |
| 5 | `prompts/05-index-wiki-domain.md` | `checklists/indexing-readiness.md` |
| 6 | `prompts/06-post-index-retrieval-validation.md` | `checklists/retrieval-validation.md` |
| 7 | `prompts/07-add-wiki-reference-article.md` | — |
| 8 | `prompts/08-index-project-documents.md` | `checklists/indexing-readiness.md` |
| 9 | `prompts/09-troubleshoot-rag-bridge.md` | `checklists/multi-project-isolation.md` |

### Dynamic retrieval strategy questions

Read:
1. `SKILL.md` (section: Dynamic retrieval strategy)
2. `docs/dynamic-retrieval-strategy.md` — why RAG alone fails for structured/tabular sources
3. `docs/evidence-contract.md` — EvidenceBundle answer rules and citation requirements
4. `docs/retrieval-mode-decision-tree.md` — routing flowchart and quick reference
5. `prompts/02b-profile-and-recommend-strategy.md` — profile-first workflow
6. `prompts/02c-benchmark-retrieval-routes.md` — benchmark before indexing
7. `checklists/indexing-readiness.md` (profile gate section — PF-0)
8. `checklists/dynamic-retrieval-readiness.md` — tool-level readiness gate
9. `checklists/evidence-bundle-validation.md` — bundle quality gate
10. `schemas/evidence-bundle.schema.yaml` — EvidenceBundle field definitions
11. `schemas/retrieval-strategy.schema.yaml` — strategy YAML validation
12. `schemas/document-profile.schema.yaml` — profile YAML validation
13. `examples/vocus-profitability/source-profile.yaml` — reference profiles
14. `examples/vocus-profitability/retrieval-strategy.yaml` — reference strategy
15. `examples/vocus-profitability/benchmark-queries.yaml` — reference benchmarks

## Update rules

| Change type | Update |
|---|---|
| New isolation/naming decision | Add/propose `.archcore/adr/` |
| New agent/policy rule | Add/propose `.archcore/rules/` |
| New retrieval contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New schema field | Update `schemas/*.schema.yaml` + propose `.archcore/specs/` |
| New checklist item | Update `checklists/*.md` |
| New workflow prompt | Add `prompts/NN-*.md`, update sequence docs |
| Governance/routing changed | Update `AI_NAVIGATION.md` + `context-map.yaml` |
| Any durable change | Append `CHANGELOG.md` |

## Drift handling

If files disagree:

1. Stop.
2. Identify conflicting files.
3. State which source has higher authority (see [Source priority](#source-priority)).
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state or policy.
3. Say "not found in project context" if unsupported by a source.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.
6. Never assist with bypassing retrieval policies or Qdrant isolation rules.

<!-- END skill-ai-it:navigation -->
````

## File: CHANGELOG.md
````markdown
# CHANGELOG — skill-project-wiki-rag-bridge

All notable changes to this skill are documented here. Format: date, summary, files changed.

---

## 20260531_0300 — Coherence sweep: venv path fix + AI_NAVIGATION routing update

**Mode:** project-coherence sweep (triggered by ARCHITECTURE.md + SETUP.md addition)

### Fixed

- `prompts/02b-profile-and-recommend-strategy.md` — `RAG_TOOLS=tools_stuff` + `VENV=$RAG_TOOLS/.venv/bin` collapsed to `VENV=tools-working-cache/rag-tools/.venv/bin` (stale venv path)
- `prompts/02c-benchmark-retrieval-routes.md` — same fix
- `prompts/05-index-wiki-domain.md` — same fix

### Updated

- `AI_NAVIGATION.md` — added `ARCHITECTURE.md` and `SETUP.md` to project context files table; added `ARCHITECTURE.md` as first read in architecture routing section

### Notes

- `tools_stuff/rag-tools` references for source-level ops (cd, uv sync, scripts/) confirmed correct — not changed
- `prompts/02-verify-rag-tools.md` already had the correct split (`RAG_TOOLS_ROOT` vs `RAG_TOOLS_VENV`) — not changed
- `.ai-context/governance-pack.md` regenerated (repomix) after fix

---

## 20260531_0202 — Add ARCHITECTURE.md and SETUP.md

**Mode:** feature addition

### Created

- `ARCHITECTURE.md` — root-level architecture overview: layer model, dynamic retrieval layer, retrieval mode routing table, EvidenceBundle contract summary, component map, links to detailed docs
- `SETUP.md` — prerequisites, rag-tools verification (corrected venv path: `tools-working-cache/rag-tools/.venv/`), skill install commands for Claude Code / Codex / Hermes, first-use prompt sequence, Qdrant setup, validation commands

### Updated

- `README.md` — directory layout updated to include `ARCHITECTURE.md` and `SETUP.md` entries

### Notes

- SETUP.md documents the corrected rag-tools venv path (`tools-working-cache` not `tools_stuff`) — resolves a known path discrepancy in prompts 02b/02c
- `docs/architecture.md` (detailed) is referenced from root `ARCHITECTURE.md`; no duplication

---

## 20260531_0200 — skill-ai-it bootstrap refresh

**Mode:** bootstrap (repeat-safe — existing governance preserved)

### Changed

- `SCRATCHPAD.md` — updated Current state to reflect all phases complete + skill installed; updated Next actions to remove stale Phase 2–4 items (all done); updated memory pointers with correct session references

### Generated support (regenerated)

- `.ai-context/governance-pack.md` — repomix context pack refreshed

### Skipped

- All governance files (`AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `README.md`) — already complete and correct; no gaps found
- `.archcore/` — no new promotion candidates; all candidates already promoted (2026-05-25)
- `graphify-out/` — docs-only project, no code files to graph

### Notes

- Skill status: `SKILL_DYNAMIC_RETRIEVAL_ALIGNED`; all phases complete
- Two open items remain: second-project validation; rag-tools venv path confirmation

---

## 20260525_0130 — Coherence sweep + Archcore promotion (skill-project-coherence)

**Mode:** coherence sweep + archcore promotion
**Trigger:** post-Phases-2–9 coherence sweep; user request to promote archcore candidates

### Summary

- Removed stale `(Phase 2 — pending creation)` and `(once created — Phase 2)` markers from active routing files
- Expanded `dynamic_retrieval` routing in `AI_NAVIGATION.md` and `context-map.yaml` to include all new Phase 2–9 docs, schemas, checklists, and templates
- Promoted 5 new archcore candidates from Phases 2–9: 3 specs + 2 guides
- Updated `ARCHCORE_PROMOTION_CANDIDATES.md` to record promotion; no remaining candidates

### Updated

- `AI_NAVIGATION.md` — removed `(once created — Phase 2)` from dynamic retrieval section; expanded dynamic retrieval routing to 15 items; added 3 new docs to project context files table
- `context-map.yaml` — removed `# Phase 2 — pending creation` comments; expanded `dynamic_retrieval` routing with 12 new entries; added `includes:` list to archcore guides entry
- `.archcore/rules/workflow-sequencing-rules.md` — removed `(Phase 2)` labels from steps 4b/4c
- `ARCHCORE_PROMOTION_CANDIDATES.md` — remaining candidates → promoted (3 specs, 2 guides, 20260525)

### Created (archcore)

- `.archcore/specs/evidence-bundle-contract.md` — EvidenceBundle required fields, answer rules, citation requirements, invalid bundle conditions
- `.archcore/specs/document-profile-contract.md` — profile_file output shape, allowed document_class values, indexing gates, storage convention
- `.archcore/specs/retrieval-strategy-yaml-contract.md` — required YAML structure, document entry fields, forbidden combinations, validation rules
- `.archcore/guides/dynamic-retrieval-routing.md` — profile-first workflow, CLI commands, retrieval mode routing table, benchmark route labels, when not to index
- `.archcore/guides/evidence-first-answering.md` — answer discipline rules, bundle validity check, good/bad answer patterns, warning handling table

### Stale-reference check

- grep `pending creation`: 0 hits in active files (CHANGELOG hits are historical — correct)
- grep `once created`: 0 hits in active files
- grep `(Phase 2)`: 0 hits in active files (CHANGELOG hits are historical — correct)

### Notes

- `.ai-context/governance-pack.md` regeneration pending (repomix pass at end of session)
- Skill install to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/` follows this entry

---

## 20260525 — Dynamic retrieval alignment (Phases 2–9)

**Mode:** full update
**Trigger:** audit verdict SKILL_DYNAMIC_RETRIEVAL_OUTDATED → target SKILL_DYNAMIC_RETRIEVAL_ALIGNED

### Summary

- Updated skill to align with rag-tools dynamic retrieval capabilities
- Added profile-before-index workflow (prompts 02b/02c)
- Added EvidenceBundle answer contract (schema, template, checklist)
- Added retrieval strategy and source profile templates and schemas
- Added direct/table/structured lookup guidance throughout
- Preserved existing project/wiki/Qdrant isolation model

### Created

- `prompts/02b-profile-and-recommend-strategy.md` — profile source files and recommend retrieval strategy; Codex-ready; run from project root; produces rag/retrieval-strategy.yaml + rag/source-profiles/
- `prompts/02c-benchmark-retrieval-routes.md` — benchmark retrieval modes against query set; outputs benchmark report with route recommendation label; Codex-ready
- `templates/retrieval-strategy.yaml` — per-project strategy routing template with per-document fields, rules block
- `templates/source-profile.yaml` — document profile template mirroring rag-tools profile-file output shape
- `templates/benchmark-queries.yaml` — benchmark query set template with expected_source, expected_terms, retrieval_modes
- `templates/evidence-bundle.yaml` — EvidenceBundle output contract reference with field-level comments
- `schemas/retrieval-strategy.schema.yaml` — validation schema for retrieval-strategy.yaml; documents allowed values, forbidden combinations, common failures
- `schemas/document-profile.schema.yaml` — validation schema for source-profile.yaml; mirrors document_profiler.profile_file() output
- `schemas/evidence-bundle.schema.yaml` — validation schema for EvidenceBundle; defines required fields, answer rules, citation requirements, common failure cases
- `checklists/dynamic-retrieval-readiness.md` — checklist confirming rag-tools dynamic commands available and EvidenceBundle functional
- `checklists/evidence-bundle-validation.md` — checklist for validating individual EvidenceBundle results before LLM answer generation
- `docs/dynamic-retrieval-strategy.md` — explains profile-first retrieval model, when direct/table/RAG is correct, wiki domains, how strategy output flows to the bridge
- `docs/evidence-contract.md` — explains EvidenceBundle, answer rules, citation requirements, good/bad answer examples
- `docs/retrieval-mode-decision-tree.md` — text decision tree from user query → intent → source profile → mode → EvidenceBundle → answer; quick reference table
- `examples/vocus-profitability/source-profile.yaml` — three example profiles: DCR (structured_markdown_reference), rate card (financial_rate_card), NBN wiki article (knowledge_article)
- `examples/vocus-profitability/retrieval-strategy.yaml` — example strategy routing for DCR (HYBRID_DIRECT_FIRST), rate card (TABLE_LOOKUP_FIRST), NBN wiki (vector_rag suitable)
- `examples/vocus-profitability/benchmark-queries.yaml` — 8-query DCR benchmark set illustrating section-ID, heading, table, and negative queries

### Modified

- `prompts/05-index-wiki-domain.md` — added PF-0 (profile/strategy gate) before PF-1; requires domain profiling and strategy confirmation before wiki indexing; warns against scaffold-only indexing
- `prompts/08-index-project-documents.md` — added PF-0 (profile/strategy gate) before PF-1; requires retrieval-strategy.yaml; blocks structured/tabular docs from indexing unless benchmark_status: passed
- `checklists/indexing-readiness.md` — added "Profile and strategy gate" section at top with 9 blocking/warn items covering profile, strategy, benchmark, EvidenceBundle path, and scaffold warnings
- `README.md` — added "Dynamic retrieval strategy" section documenting profile/lookup/benchmark commands, EvidenceBundle contract, when-not-to-use-RAG table, bridge integration

### Stale-reference check

- grep `"RAG tooling"` in SKILL.md, README.md, docs: 0 hits
- grep `"vector RAG only"` or `"only vector RAG"`: 0 hits in active files
- `index.*before.*profile` in prompts/checklists: 0 hits
- PF-0 present in prompt 05 and 08: confirmed

### Notes

- Phase 1 (SKILL.md) was completed in a prior session (20260525_1200)
- Phase 10 (validation) is the next step: YAML parse all templates/schemas/examples; grep checks
- Recommended first use: run prompts/02b on the Vocus project, then prompts/02c for DCR before any project-document indexing

---

## 20260525_1200 — Phase 1: Dynamic retrieval strategy integration (skill-project-coherence)

**Mode:** coherence sweep
**Trigger:** post-SKILL.md Phase 1 update (dynamic retrieval strategy)

### Updated

- `SKILL.md` — 8 edits; 290 → 367 lines. New `## Dynamic retrieval strategy` section with routing decision table, all 6 CLI commands (`profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-section`, `lookup-table`, `benchmark-file`), EvidenceBundle contract (key fields, answer-only-from-excerpt rule), `RAG_TOOLS_DYNAMIC_RETRIEVAL_READY` readiness label, 4 dynamic retrieval route labels (`DOCUMENT_PROFILE_COMPLETE`, `STRATEGY_RECOMMENDED`, `BENCHMARK_PASSED`, `RETRIEVAL_ROUTE_SELECTED`). Steps 4b/4c added to workflow. 2 new safety rules (profile-before-index, no-default-vector-RAG-for-structured). 3 new agent behavior items (7–9). EvidenceBundle contract subsection in Output contract. Updated Core architecture description.
- `AI_NAVIGATION.md` — workflow routing table updated with steps 4b/4c; new `Dynamic retrieval strategy questions` routing section added
- `context-map.yaml` — workflow sequence updated with `02b`/`02c` entries (Phase 2 pending); new `dynamic_retrieval` routing category added
- `.archcore/rules/workflow-sequencing-rules.md` — RULE-W1 updated with 04b/04c in sequence; RULE-W6 (profile-before-index-decision) and RULE-W7 (EvidenceBundle mandatory) added; checklist gate table updated with steps 4b/4c
- `SCRATCHPAD.md` — current state (Phase 1 complete), open items (Phases 2–4), session history (2026-05-25 entry), next actions updated
- `mcp-working-cache/context-mode/` — better-sqlite3 upgraded 12.6.2 → 12.10.0 for Node 26 compatibility; Node 22.22.0 pinned via `bin/node` symlink; plugin.json patched to use symlink path

### Stale-reference check

- grep `"RAG tooling"` in active files: 0 hits
- grep `"vector RAG only"` or `"vector-RAG-only"`: 0 hits in active files
- Steps 4b/4c referenced in SKILL.md, AI_NAVIGATION.md, context-map.yaml, archcore rules: consistent

### Notes

- prompts/02b and 02c not yet created (Phase 2). References marked `(Phase 2 — pending creation)` in routing files.
- checklists/indexing-readiness.md profile gate not yet added (Phase 2).
- Repomix re-run needed to refresh `.ai-context/governance-pack.md` after these changes.

---

## 20260525_0000 — Coherence sweep (skill-project-coherence)

**Mode:** coherence sweep
**Trigger:** post-bootstrap + post-archcore-promote

### Updated

- `README.md` — directory layout updated to include all governance files added by skill-ai-it bootstrap: `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `ARCHCORE_PROMOTION_CANDIDATES.md`, `repomix.config.json`, `.archcore/`, `.ai-context/`
- `context-map.yaml` — `graphify.enabled` set to `false` (pure-markdown skill; graphify found no code files at bootstrap; re-enable if code is added)

### Stale-reference check

- grep for `graphify.*enabled.*true`: clean
- No stale path or figure references found in active files

### Notes

- Tier 1–3 files coherent. No scripts, reports, or task runners in this skill.
- `.archcore/` fully populated (3 ADRs, 2 rules, 5 specs, 4 guides) — no rule updates needed.
- Repomix re-run queued to refresh `.ai-context/governance-pack.md`.

---

## 20260524_2359 — Archcore full population (skill-ai-it promote)

**Mode:** promote
**Generated by:** `skill-ai-it promote`

### Created

- `.archcore/specs/project-context-yaml-contract.md` — full contract for `project-context.yaml` (10 required keys, sub-key constraints, common failures)
- `.archcore/specs/project-documents-yaml-contract.md` — full contract for `project-documents.yaml` (opt-in indexing manifest, caution levels, gate rules)
- `.archcore/specs/wiki-domain-registry-contract.md` — full contract for `domain-registry.yaml` (domain status rules, validation script, modification rules)
- `.archcore/guides/wiki-domain-creation.md` — 6-step domain creation procedure with pre-flight, validation, and output format
- `.archcore/guides/post-index-retrieval-validation.md` — 5-step retrieval validation with isolation check, citation audit, forbidden collection sweep

### Updated

- `ARCHCORE_PROMOTION_CANDIDATES.md` — all remaining candidates promoted; no remaining items

### Notes

- `.archcore/` is now fully populated: 3 ADRs, 2 rules, 5 specs, 4 guides
- Repomix re-run to refresh `.ai-context/governance-pack.md`

---

## 20260524_2345 — AI governance bootstrap (skill-ai-it)

**Mode:** bootstrap
**Generated by:** `skill-ai-it`

### Created

- `AGENTS.md` — agent instruction file with @-import chain, working rules, navigation block
- `CLAUDE.md` — thin wrapper over AGENTS.md
- `SCRATCHPAD.md` — working memory (no prior session data; created today)
- `AI_NAVIGATION.md` — human-readable context router with workflow routing table
- `context-map.yaml` — machine-readable authority and routing map
- `repomix.config.json` — deterministic governance context pack config
- `.archcore/` — initialized by `archcore init`
- `.archcore/adr/ADR-001-qdrant-collection-naming-convention.md`
- `.archcore/adr/ADR-002-multi-project-isolation-model.md`
- `.archcore/adr/ADR-003-authority-hierarchy.md`
- `.archcore/rules/retrieval-isolation-rules.md`
- `.archcore/rules/workflow-sequencing-rules.md`
- `.archcore/specs/retrieval-policy-yaml-contract.md`
- `.archcore/specs/qdrant-query-filter-contract.md`
- `.archcore/guides/new-project-onboarding.md`
- `.archcore/guides/failure-mode-reference.md`
- `ARCHCORE_PROMOTION_CANDIDATES.md`
- `.ai-context/governance-pack.md` (repomix generated)

### Skipped

- `graphify-out/` — graphify CLI found no code files (pure markdown skill); skipped
- `scripts/README.md` — no scripts or task runners present

### Notes

- Archcore initialized and populated in bootstrap + promote mode (user authorized)
- Repomix ran successfully; `.ai-context/governance-pack.md` generated
- No prior memory in memory-keeper, mcp-project-context, or claude-mem (skill created same day)

---

## 2026-05-24 — Initial creation

**Summary:** Created the `skill-project-wiki-rag-bridge` reusable skill from scratch, based on:
- Existing Vocus profitability project bridge pattern (`project-dependency-model.schema.yaml`)
- wiki-data governance files (`domain-registry.yaml`, `qdrant-collection-policy.md`)
- rag-tools infrastructure established in the same session
- Global collection isolation policy from `qdrant-collection-policy.md`

**Scope:** Multi-project capable. Not Vocus-specific.

**Files created:**
- `SKILL.md` — primary agent-facing instructions
- `README.md` — human maintainer guide
- `CHANGELOG.md` — this file
- `templates/project-context.yaml`
- `templates/retrieval-policy.yaml`
- `templates/project-documents.yaml`
- `templates/wiki-domain-registry-entry.yaml`
- `templates/wiki-domain-index.md`
- `templates/wiki-reference-article.md`
- `templates/qdrant-collection-policy.md`
- `templates/AGENTS-project-wiki-bridge-block.md`
- `templates/AI_NAVIGATION-project-wiki-bridge-block.md`
- `templates/project-wiki-bridge.md`
- `templates/justfile-rag-bridge-snippet.just`
- `prompts/00-verify-wiki-operational-state.md`
- `prompts/01-create-wiki-domain.md`
- `prompts/02-verify-rag-tools.md`
- `prompts/03-create-project-bridge.md`
- `prompts/04-validate-project-policy.md`
- `prompts/05-index-wiki-domain.md`
- `prompts/06-post-index-retrieval-validation.md`
- `prompts/07-add-wiki-reference-article.md`
- `prompts/08-index-project-documents.md`
- `prompts/09-troubleshoot-rag-bridge.md`
- `schemas/retrieval-policy.schema.yaml`
- `schemas/project-context.schema.yaml`
- `schemas/project-documents.schema.yaml`
- `schemas/wiki-domain-registry.schema.yaml`
- `checklists/wiki-operational-readiness.md`
- `checklists/rag-tools-readiness.md`
- `checklists/project-bridge-readiness.md`
- `checklists/indexing-readiness.md`
- `checklists/retrieval-validation.md`
- `checklists/multi-project-isolation.md`
- `examples/vocus-profitability/project-context.yaml`
- `examples/vocus-profitability/retrieval-policy.yaml`
- `examples/vocus-profitability/project-documents.yaml`
- `examples/vocus-profitability/wiki-bridge.md`
- `examples/generic-project/project-context.yaml`
- `examples/generic-project/retrieval-policy.yaml`
- `examples/generic-project/project-documents.yaml`
- `docs/architecture.md`
- `docs/flow-diagram.md`
- `docs/collection-naming-policy.md`
- `docs/authority-model.md`
- `docs/multi-project-model.md`
- `docs/failure-modes.md`
- `docs/operating-runbook.md`
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
````

## File: context-map.yaml
````yaml
version: 1

project:
  name: skill-project-wiki-rag-bridge
  context_policy: "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."

bootstrap:
  required_first_read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md
    - SKILL.md
    - docs/authority-model.md

authority_order:
  - path: ".archcore/adr"
    type: architecture_decisions
    authority: highest
  - path: ".archcore/rules"
    type: durable_rules
    authority: highest
  - path: ".archcore/specs"
    type: design_contracts
    authority: highest
  - path: ".archcore/guides"
    type: operating_guides
    authority: high
    includes:
      - "new-project-onboarding.md"
      - "failure-mode-reference.md"
      - "wiki-domain-creation.md"
      - "post-index-retrieval-validation.md"
      - "dynamic-retrieval-routing.md"
      - "evidence-first-answering.md"
  - path: "AGENTS.md"
    type: agent_instructions
    authority: high
  - path: "CLAUDE.md"
    type: claude_specific_instructions
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "SKILL.md"
    type: skill_instructions
    authority: high
  - path: "docs/authority-model.md"
    type: isolation_policy
    authority: high
  - path: "docs/collection-naming-policy.md"
    type: naming_rules
    authority: high
  - path: "docs/architecture.md"
    type: architecture_overview
    authority: medium_high
  - path: "docs/operating-runbook.md"
    type: operational_guide
    authority: high
  - path: "docs/failure-modes.md"
    type: troubleshooting_reference
    authority: medium
  - path: "schemas"
    type: yaml_field_definitions
    authority: high
  - path: "checklists"
    type: blocking_gate_checklists
    authority: high
  - path: "CHANGELOG.md"
    type: project_history
    authority: medium_high
  - path: "SCRATCHPAD.md"
    type: transient_notes
    authority: low

context_sources:
  archcore:
    enabled: true
    root: ".archcore"
    read_first_for:
      - architecture_decision
      - isolation_policy
      - governance_rule
      - design_contract
      - operating_procedure
      - durable_project_truth

  generated:
    graphify:
      enabled: false
      root: "graphify-out"
      note: "skipped — pure-markdown skill, no code files; re-run graphify if code added"
      preferred_files:
        - "graphify-out/GRAPH_REPORT.md"
        - "graphify-out/graph.json"

    repomix:
      enabled: true
      root: ".ai-context"
      preferred_files:
        - ".ai-context/governance-pack.md"

routing:
  architecture:
    description: "Qdrant collection isolation, wiki/project separation, authority boundaries."
    read:
      - ".archcore/adr"
      - ".archcore/specs"
      - "docs/authority-model.md"
      - "docs/collection-naming-policy.md"
      - "docs/architecture.md"
      - "docs/multi-project-model.md"
    avoid_as_authority:
      - "SCRATCHPAD.md"

  workflow:
    description: "How to execute the bridge setup workflow end-to-end."
    read:
      - "SKILL.md"
      - "prompts"
      - "checklists"
      - "docs/operating-runbook.md"
    sequence:
      - "prompts/00-verify-wiki-operational-state.md"
      - "prompts/01-create-wiki-domain.md"
      - "prompts/02-verify-rag-tools.md"
      - "prompts/03-create-project-bridge.md"
      - "prompts/04-validate-project-policy.md"
      - "prompts/02b-profile-and-recommend-strategy.md"   # Phase 2 — profile docs; choose retrieval route
      - "prompts/02c-benchmark-retrieval-routes.md"       # Phase 2 — benchmark structured/table/RAG
      - "prompts/05-index-wiki-domain.md"
      - "prompts/06-post-index-retrieval-validation.md"
      - "prompts/07-add-wiki-reference-article.md"
      - "prompts/08-index-project-documents.md"
      - "prompts/09-troubleshoot-rag-bridge.md"

  dynamic_retrieval:
    description: "Document profiling, retrieval strategy selection, EvidenceBundle grounding."
    read:
      - "SKILL.md"                                        # section: Dynamic retrieval strategy
      - "prompts/02b-profile-and-recommend-strategy.md"
      - "prompts/02c-benchmark-retrieval-routes.md"
      - "checklists/indexing-readiness.md"                # profile gate section
      - "checklists/dynamic-retrieval-readiness.md"
      - "checklists/evidence-bundle-validation.md"
      - "docs/dynamic-retrieval-strategy.md"
      - "docs/evidence-contract.md"
      - "docs/retrieval-mode-decision-tree.md"
      - "schemas/document-profile.schema.yaml"
      - "schemas/retrieval-strategy.schema.yaml"
      - "schemas/evidence-bundle.schema.yaml"
      - "templates/retrieval-strategy.yaml"
      - "templates/source-profile.yaml"
      - "templates/benchmark-queries.yaml"
      - "templates/evidence-bundle.yaml"

  validation:
    description: "Retrieval policy, collection naming, schema validation, multi-project isolation."
    read:
      - ".archcore/rules"
      - "docs/authority-model.md"
      - "schemas/retrieval-policy.schema.yaml"
      - "schemas/project-context.schema.yaml"
      - "checklists/project-bridge-readiness.md"
      - "checklists/multi-project-isolation.md"

  troubleshooting:
    description: "RAG pipeline issues, Qdrant errors, retrieval failures."
    read:
      - "docs/failure-modes.md"
      - "docs/operating-runbook.md"
      - "prompts/09-troubleshoot-rag-bridge.md"
      - "checklists/rag-tools-readiness.md"
      - "checklists/retrieval-validation.md"

  templates:
    description: "Bridge file templates, YAML starting points, registry entries."
    read:
      - "templates"
      - "examples/vocus-profitability"
      - "examples/generic-project"
      - "schemas"

  governance:
    description: "Agent behaviour, project rules, file update rules."
    read:
      - "AGENTS.md"
      - "CLAUDE.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"
      - ".archcore/rules"

update_rules:
  isolation_decision:
    update:
      - ".archcore/adr"
    also_consider:
      - "docs/authority-model.md"
      - "docs/collection-naming-policy.md"

  durable_rule:
    update:
      - ".archcore/rules"
    also_consider:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"

  retrieval_contract:
    update:
      - ".archcore/specs"
    also_consider:
      - "schemas/retrieval-policy.schema.yaml"
      - "docs/authority-model.md"

  operating_procedure:
    update:
      - ".archcore/guides"
    also_consider:
      - "docs/operating-runbook.md"
      - "prompts"

  schema_change:
    update:
      - "schemas"
    also_consider:
      - ".archcore/specs"
      - "templates"

  routing_change:
    update:
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "AGENTS.md"

  governance_history:
    update:
      - "CHANGELOG.md"

  temporary_note:
    update:
      - "SCRATCHPAD.md"

drift_policy:
  on_conflict:
    action: "stop_and_report"
    required_output:
      - conflicting_files
      - higher_authority_source
      - recommended_fix
      - assumptions

  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true

  isolation_rule:
    never_bypass: true
    on_violation: "refuse and explain"

generated_context_policy:
  regenerate_after:
    - schema_change
    - new_archcore_documents
    - major_doc_change
    - workflow_restructure
  commands:
    graphify: "graphify update ."
    repomix_governance: "repomix --config repomix.config.json"

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in project context"
  distinguish_assumptions: true
  do_not_invent_state: true
  never_bypass_isolation: true
````

## File: README.md
````markdown
# Project Wiki RAG Bridge

Reusable AI skill for connecting project repos to the shared Karpathy-style LLM wiki and rag-tools safely, with strict Qdrant collection isolation.

## Why this exists

The shared wiki (`_wiki/wiki_stuff`) is a growing cross-project knowledge base. Projects need selective, controlled access to wiki domains — not a free-for-all global search. This skill standardises:

- How projects declare which wiki domains they may query
- How wiki domains are created, indexed, and validated
- How Qdrant collection naming isolation is enforced
- How retrieval policies are authored and validated
- How to audit and troubleshoot the full bridge

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│  SOURCE OF TRUTH LAYER                                          │
│                                                                 │
│  _wiki/wiki_stuff/domains/<domain>/   ← shared reference facts │
│  _project/project_stuff/<proj>/       ← project-specific facts │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  POLICY / METADATA LAYER                                        │
│                                                                 │
│  _wiki/wiki-data/domain-registry.yaml                          │
│  _wiki/wiki-data/qdrant-collection-policy.md                   │
│  <project>/rag/project-context.yaml                            │
│  <project>/rag/retrieval-policy.yaml                           │
│  <project>/rag/manifests/project-documents.yaml                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  TOOLING LAYER                                                  │
│                                                                 │
│  _tool/tools_stuff/rag-tools/   ← shared Python tooling        │
│  tools-working-cache/rag-tools/.venv/  ← external venv         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  INDEX LAYER  (search artefact, not source of truth)           │
│                                                                 │
│  Qdrant: rag__wiki_<domain>          ← per-domain wiki index   │
│  Qdrant: rag__project_<slug>         ← per-project doc index   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  RETRIEVAL LAYER                                                │
│                                                                 │
│  Project policy → allowed wiki domains → isolated collections  │
│  → cited results → agent answer                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data flow

```text
Project repo
  ├── rag/retrieval-policy.yaml
  │     └── declared wiki domains: [nbn, vocus]
  │
  ├── rag-tools validate-policy rag/retrieval-policy.yaml
  │     └── checks: collection names, forbidden list, required filters
  │
  └── Agent query
        ├── Step 1: project-local files
        ├── Step 2: rag__project_<slug>  (filtered by project_slug)
        ├── Step 3: rag__wiki_nbn        (filtered by wiki_domain=nbn)
        │   rag__wiki_vocus      (filtered by wiki_domain=vocus)
        └── Step 4: ask user if insufficient evidence
              └── all results cite: source_file, section_path, collection
```

## Directory layout

```
project-wiki-rag-bridge/
  SKILL.md                      ← primary agent-facing instructions
  README.md                     ← this file (for human maintainers)
  ARCHITECTURE.md               ← layer model, component map, design decisions
  SETUP.md                      ← prerequisites, rag-tools verification, skill install
  AGENTS.md                     ← universal agent instruction file (@-imports parent)
  CLAUDE.md                     ← Claude Code wrapper over AGENTS.md
  AI_NAVIGATION.md              ← human-readable AI context router
  context-map.yaml              ← machine-readable routing and authority map
  CHANGELOG.md                  ← version history
  SCRATCHPAD.md                 ← agent working memory (cleared between sessions)
  ARCHCORE_PROMOTION_CANDIDATES.md ← promotion tracking (all promoted; run audit to refresh)
  repomix.config.json           ← deterministic AI context pack config
  .archcore/                    ← durable structured project truth (archcore-managed)
    adr/                        ← architecture decision records
    rules/                      ← durable project/agent rules
    specs/                      ← technical design contracts
    guides/                     ← operational guides
  .ai-context/                  ← generated AI context pack (repomix output; regenerable)
  templates/                    ← copy-and-fill templates
  prompts/                      ← numbered workflow prompt scripts
  schemas/                      ← YAML field definitions
  checklists/                   ← blocking gate checklists
  examples/                     ← concrete examples
    vocus-profitability/
    generic-project/
  docs/                         ← architecture, flows, failure modes, runbook
```

---

## How to use with Codex

1. Load the skill: reference `SKILL.md` in your Codex session context.
2. Pick the relevant prompt from `prompts/` for your current step.
3. Paste the prompt text into the Codex session. Adjust the `PROJECT_*` parameters at the top.
4. Work through the checklist in `checklists/` to confirm readiness before proceeding.

## How to use with Claude Code

1. The skill auto-loads when activated via `/project-wiki-rag-bridge` or by name in slash-command routing.
2. Claude Code reads `SKILL.md` and follows the standard workflow sequence.
3. Use the prompts in `prompts/` as the execution layer — paste them for each step.

---

## Common tasks

### Set up a new project bridge

```
1. Confirm wiki is operational:   prompts/00-verify-wiki-operational-state.md
2. Confirm wiki domains exist:    prompts/01-create-wiki-domain.md  (if needed)
3. Confirm rag-tools works:       prompts/02-verify-rag-tools.md
4. Create bridge files:           prompts/03-create-project-bridge.md
5. Validate policy:               prompts/04-validate-project-policy.md
```

### Add a new wiki domain

```
1. prompts/00-verify-wiki-operational-state.md
2. prompts/01-create-wiki-domain.md
3. prompts/07-add-wiki-reference-article.md  (add curated content)
4. prompts/05-index-wiki-domain.md           (dry-run, then live)
```

### Validate rag-tools

```
prompts/02-verify-rag-tools.md
```

Full doctor + Qdrant status + embedding smoke test. No destructive operations.

### Validate retrieval policy

```
prompts/04-validate-project-policy.md
```

YAML parse + rag-tools validate-policy + collection audit. No indexing.

### Index one wiki domain

```
prompts/05-index-wiki-domain.md  →  dry-run first, then confirm, then live
```

Indexes exactly one domain. Never indexes multiple domains in one operation.

### Test retrieval

```
prompts/06-post-index-retrieval-validation.md
```

Runs test queries. Verifies only allowed collections queried. Checks citation completeness.

---

## Dynamic retrieval strategy

`rag-tools` is now a retrieval engine, not just a vector RAG indexer. Before any indexing
decision, it profiles source files and recommends a retrieval route.

### Profile commands (read-only)

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin

# Classify a file: document_class, heading/table counts, recommended modes
$VENV/rag-tools profile-file <path/to/file>

# Profile all files in a directory
$VENV/rag-tools profile-project <project-root>

# Recommend retrieval strategy (primary / secondary / fallback / rag_suitability)
$VENV/rag-tools recommend-strategy <path/to/file>
```

### Lookup commands (read-only, no Qdrant needed)

```bash
# Deterministic heading/section lookup
$VENV/rag-tools structured-lookup <file> "<query>"

# Exact section ID lookup (e.g. C2.11)
$VENV/rag-tools lookup-section <file> <section-id>

# Table-aware lookup (rate cards, invoices)
$VENV/rag-tools lookup-table <file> "<query>"

# Benchmark all applicable modes against a query set
$VENV/rag-tools benchmark-file <file> --queries <queries.yaml>
```

### EvidenceBundle answer contract

Every retrieval command returns an `EvidenceBundle`. The LLM **must answer only from the
`excerpt` field** — no training knowledge fill-in. Key fields: `source_file`, `excerpt`,
`section_id`, `heading`, `table_id`, `retrieval_warnings`.

If no bundle is returned or `excerpt` is empty: report `RETRIEVAL_NOT_READY`.

See `docs/evidence-contract.md` for full answer rules and citation requirements.

### When not to use vector RAG

| Document class | Preferred route | RAG suitability |
|---|---|---|
| `structured_markdown_reference` | `direct_structured_lookup` | partially_suitable |
| `financial_rate_card` | `table_aware_lookup` | not_suitable |
| `invoice_or_billing_report` | `table_aware_lookup` | not_suitable |
| `legal_contract_or_terms` | `section_clause_lookup` | partially_suitable |
| `knowledge_article` | `vector_rag` | suitable |
| `tabular_dataset` | `table_aware_lookup` | not_suitable |
| `unstructured_pdf` | extraction required | not_suitable |

### Relationship with the project/wiki bridge

The dynamic retrieval strategy layer adds per-document routing on top of the existing bridge:

1. `rag/retrieval-strategy.yaml` — records chosen route per document (new, from prompt 02b)
2. `rag/retrieval-policy.yaml` — governs Qdrant collection access and filters (existing)
3. `rag/manifests/project-documents.yaml` — controls `index: true` gate (existing)
4. `rag/source-profiles/` — per-file profiler output (new, from prompt 02b)
5. `rag/benchmarks/` — benchmark reports (new, from prompt 02c)

Profiling and strategy selection happen before any indexing. Direct and table lookup are
used without Qdrant when the document class supports it.

---

## Rollback guidance

If a collection is incorrectly named or populated:

```bash
# List collections
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Delete a collection (requires Qdrant HTTP access)
curl -X DELETE http://localhost:6333/collections/<collection_name>

# Re-index after cleanup
just rag-index-domain-dry <domain>   # verify dry-run first
just rag-index-domain <domain>
```

Do not delete collections in production without a dry-run of the re-index.

---

## Limitations

- This skill documents and governs the bridge workflow. It does not install rag-tools.
- It does not own Qdrant data. Qdrant is managed by `tools_stuff/rag-tools`.
- It does not create wiki markdown content. It only guides where and how to place it.
- Collection isolation is enforced by policy only. Qdrant has no built-in multi-tenant enforcement.
- The rag-tools `validate-policy` CLI validates flat top-level keys only (see `schemas/retrieval-policy.schema.yaml`).
- Local embeddings use `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). Do not mix with collections indexed with different models.
````

## File: SCRATCHPAD.md
````markdown
# SCRATCHPAD

Agent working memory for skill-project-wiki-rag-bridge.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: updated 20260531 — all phases complete, governance refreshed -->

## Current state <!-- KEEP -->

**Phase:** All phases complete — `SKILL_DYNAMIC_RETRIEVAL_ALIGNED`. Skill installed.

Skill created 2026-05-24 (governance-ready). 2026-05-25: audit SKILL_DYNAMIC_RETRIEVAL_OUTDATED → full dynamic retrieval update applied (Phases 1–10). Prompts 02b/02c, 4 templates, 3 schemas, 2 checklists, 3 docs, 3 examples created. Coherence sweep + Archcore promotion complete (5 candidates promoted: 3 specs, 2 guides). Skill installed to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/`. Repomix regenerated. 2026-05-31: skill-ai-it bootstrap run — SCRATCHPAD next-actions updated, repomix refreshed.

---

## Open items <!-- KEEP -->

- [x] Run `skill-project-coherence` sweep — complete 20260525_0130
- [x] Install skill to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/` — complete 20260525
- [x] Regenerate `.ai-context/governance-pack.md` via repomix — complete 20260525
- [x] Archcore promotion for new schemas/docs — 5 candidates promoted (3 specs, 2 guides) 20260525
- [ ] Validate skill against a second real project (beyond vocus-profitability)
- [ ] Confirm rag-tools venv path is current: `tools-working-cache/rag-tools/.venv/`

---

## Key anchors

| Item | Detail |
|---|---|
| Skill entry | `SKILL.md` |
| Human guide | `README.md` |
| Workflow prompts | `prompts/00–09-*.md` |
| Gate checklists | `checklists/*.md` |
| Authority model | `docs/authority-model.md` |
| Collection policy | `docs/collection-naming-policy.md` |
| Schemas | `schemas/*.schema.yaml` |
| Templates | `templates/` |
| Examples | `examples/vocus-profitability/`, `examples/generic-project/` |
| rag-tools venv | `tools-working-cache/rag-tools/.venv/` |
| Qdrant wiki prefix | `rag__wiki_<domain>` |
| Qdrant project prefix | `rag__project_<slug>` |

---

## Recent decisions

- 2026-05-24 — Skill scoped to multi-project (not Vocus-specific). Vocus is reference example only.
- 2026-05-24 — Collection naming enforced by policy only (Qdrant has no built-in multi-tenancy).
- 2026-05-24 — Embedding model locked to `sentence-transformers/all-MiniLM-L6-v2` (384 dims) — cannot mix.
- 2026-05-24 — Archcore initialized; durable rules/ADRs/specs extracted from existing skill content.

---

## Session history (summaries — full detail in mcp-project-context)

### 2026-05-31 — Governance refresh + ARCHITECTURE.md + SETUP.md <!-- KEEP -->
- skill-ai-it bootstrap: SCRATCHPAD next-actions cleaned; repomix regenerated; CHANGELOG appended
- ARCHITECTURE.md created: 3 detailed text diagrams (layer model, retrieval flow, collection isolation); vector_rag Python-only constraint documented; all 13 CLI commands annotated
- SETUP.md created: corrected rag-tools venv path (tools-working-cache not tools_stuff); install commands for all 3 runtimes; first-use sequence
- Evidence basis: mcp-project-context note (slurp-20260531-skill-pwrb-architecture-setup)

### 2026-05-25 — Dynamic retrieval audit + Phase 1 SKILL.md update <!-- KEEP -->
- context-mode Node.js fix: better-sqlite3 upgraded to 12.10.0; Node 22 pinned via `mcp-working-cache/context-mode/bin/node` symlink; plugin.json patched to use symlink
- Audit confirmed `SKILL_DYNAMIC_RETRIEVAL_OUTDATED`; all 6 dynamic CLI commands missing, no EvidenceBundle contract, no profiling step, vector-RAG-only framing
- Phase 1 SKILL.md: 8 edits applied; new Dynamic retrieval strategy section (routing table, all 6 CLI commands, EvidenceBundle contract, readiness label); Steps 4b/4c added to workflow; 2 new safety rules; 3 new agent behavior items; 4 readiness labels; 290→367 lines
- Evidence basis: mcp-project-context notes (checkpoint: slurp-20260525-phase1-skill-md-complete)

### 2026-05-24 — Full governance + archcore (bootstrap + promote)
- Created full skill package: SKILL.md, README.md, CHANGELOG.md, prompts, checklists, schemas, templates, examples, docs
- skill-ai-it bootstrap: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, SCRATCHPAD.md, repomix.config.json; archcore init + 3 ADRs, 2 rules, 2 specs, 2 guides
- skill-ai-it promote: 3 more specs + 2 more guides; all ARCHCORE_PROMOTION_CANDIDATES.md items promoted — no remaining candidates
- Evidence basis: CHANGELOG.md + mcp-project-context notes (slurp-20260524)

---

## Next actions <!-- KEEP: updated 20260531 -->

- Validate skill against a second real project (beyond vocus-profitability)
- Confirm rag-tools venv path still current: `tools-working-cache/rag-tools/.venv/`

---

## Memory pointers (navigation only — content is above)

- memory-keeper: worker mode — writes unavailable; read via search tool
- project-context: skills_stuff project (b8c5525e); channel skill-project-wiki-rag-bridge; checkpoint slurp-20260531-skill-pwrb-architecture-setup
- claude-mem observations: 5509–5536 (Phase 1–9), S1444–S1535 (session records); get_observations([IDs]) for details
````

## File: SKILL.md
````markdown
---
name: skill-project-wiki-rag-bridge
description: >-
  Connects project repos to the shared Karpathy-style LLM wiki and rag-tools
  safely. Covers wiki setup, domain creation, project bridge files, retrieval
  policy validation, Qdrant collection isolation, dynamic retrieval strategy
  selection, structured/table/section lookup, EvidenceBundle-grounded answers,
  indexing readiness, and post-index retrieval validation. Multi-project
  capable. Conservative and audit-first.
---

# Project Wiki RAG Bridge Skill

## Purpose

This skill helps AI agents create, validate, and operate a controlled bridge between:

1. A project repo under `/Volumes/Data/_ai/_project/project_stuff/...`
2. The shared Karpathy-style LLM wiki under `/Volumes/Data/_ai/_wiki/wiki_stuff`
3. The shared retrieval engine under `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools` (dynamic retrieval router: vector RAG, structured lookup, section lookup, table lookup, document profiling, benchmarking)
4. Qdrant collections using strict project/domain isolation

It does **not** own wiki content, project content, Qdrant data, or embeddings. It standardizes and governs the bridge workflow.

---

## When to use this skill

Use when the user asks to:

- Set up a project-to-wiki bridge for any project
- Validate wiki operational state or RAG tools readiness
- Create a new wiki domain
- Index a wiki domain into Qdrant
- Connect a project to selected wiki domains
- Validate Qdrant collection isolation and naming
- Troubleshoot retrieval policy or RAG pipeline problems
- Create reusable shared reference articles under a wiki domain
- Prepare a project for policy-aware vector retrieval
- Audit whether a project's RAG setup follows isolation rules

---

## When not to use this skill

Do not use when:

- The user only wants standard markdown editing with no RAG component
- The user wants unrestricted global wiki search (that is a policy violation — refuse, do not assist)
- The user wants to dump raw, sensitive project data into wiki collections
- The user asks for unrelated RAG framework research or API comparison
- The user asks to bypass retrieval policies or Qdrant isolation rules
- The task is bootstrapping project governance files from scratch (use `skill-ai-it` for that)

---

## Core architecture

```text
_wiki/wiki_stuff      — Source markdown wiki / Obsidian vault (authoritative for shared knowledge)
_wiki/wiki-data       — Durable metadata and policy (domain registry, collection policy, schemas)
_wiki/wiki-runtime    — Runtime reports, indexing status, audit logs
_wiki/wiki-working-cache — Generated/cache artefacts (rebuildable)

_tool/tools_stuff/rag-tools — Retrieval engine with dynamic strategy router (Qdrant vector RAG,
                               structured/section/table direct lookup, document profiler,
                               strategy selector, benchmarking, policy validator, CLI, doctor)

_project/project_stuff/<project> — Project source of truth (project-specific facts, reports,
                                    manifests, local docs, retrieval policy)

Qdrant               — Isolated index layer only. Not a source of truth. Collections are scoped
                        strictly per project and per wiki domain.
```

### Canonical paths

| Component | Path |
|---|---|
| Wiki vault | `/Volumes/Data/_ai/_wiki/wiki_stuff` |
| Wiki metadata | `/Volumes/Data/_ai/_wiki/wiki-data` |
| RAG tools source | `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools` |
| RAG tools venv | `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv` |
| Domain registry | `/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml` |
| Collection policy | `/Volumes/Data/_ai/_wiki/wiki-data/qdrant-collection-policy.md` |

---

## Authority model

Rules (highest to lowest):

1. **Project-local documents** win for all project-specific facts (invoices, reports, mappings, calculated output)
2. **Wiki markdown** wins for shared reference knowledge (standards, rate cards, policy interpretations)
3. **Generated summaries** are secondary — never override primary sources
4. **Nav YAML** (`context-map.yaml`, `project-context.yaml`) is routing metadata only — not authoritative source text
5. **Qdrant payloads** are retrieval artefacts — not authoritative records; the markdown source file is always canonical

When authority is ambiguous: report the conflict and ask the user. Never blend sources silently.

---

## Dynamic retrieval strategy

rag-tools is **not** a vector-RAG-only system. The correct retrieval model is:

| Source type | Primary retrieval route | When to fall back to vector RAG |
|---|---|---|
| Exact structured doc (DCR, rate card, manifest, policy) | `structured-lookup` / `lookup-section` | Only if no section ID or heading matches |
| Tabular financial data (rates, margins, invoice rows) | `lookup-table` | Only if table parse fails |
| Broad semantic / cross-document question | Vector RAG (Qdrant) | Default route |
| Curated wiki articles | Vector RAG (Qdrant) | Default route — wiki is written for semantic search |

**Source files remain authoritative.** Qdrant payloads are retrieval artefacts, not records.

**Retrieval route must be benchmarked** before treating it as default for a project's documents.

### CLI commands

| Command | Purpose |
|---|---|
| `rag-tools profile-file <file>` | Classify source: section count, table count, source class, recommended modes |
| `rag-tools recommend-strategy <file>` | Output ordered retrieval mode list based on profile |
| `rag-tools structured-lookup <file> <query>` | Deterministic heading/section lookup → EvidenceBundle |
| `rag-tools lookup-section <file> <section-id>` | Exact section ID lookup → EvidenceBundle |
| `rag-tools lookup-table <file> <query>` | Table-aware retrieval → EvidenceBundle |
| `rag-tools benchmark-file <file> [--queries <file>]` | Compare direct/table/RAG modes; pick best route |

The four commands above the benchmark line existed before the dynamic retrieval upgrade. The four new commands (`profile-file`, `recommend-strategy`, `structured-lookup`, `lookup-table`, `lookup-section`, `benchmark-file`) are the dynamic retrieval layer.

### EvidenceBundle — required output contract

Every retrieval operation must return an `EvidenceBundle`. The LLM **must answer only from evidence bundle content**, never from training knowledge.

Key fields: `query`, `retrieval_mode`, `document_id`, `source_file`, `source_type`, `authority`, `section_id`, `section_path`, `heading`, `table_id`, `row_keys`, `excerpt`, `matched_terms`, `score_or_confidence`, `retrieval_warnings`.

If retrieval returns no bundle or an empty bundle, report `RETRIEVAL_NOT_READY` — do not answer from memory.

### Dynamic readiness label

| Label | Meaning |
|---|---|
| `RAG_TOOLS_DYNAMIC_RETRIEVAL_READY` | All 6 dynamic CLI commands available; tests pass |

---

## Collection isolation rules

### Allowed collection name patterns

Project collections:
```
rag__project_<project_slug>
```

Wiki domain collections:
```
rag__wiki_<domain_slug>
```

Test/ephemeral collections:
```
rag__test_<purpose>_<yyyymmdd>
```

### Forbidden collection names

```
rag__global_all_docs
rag__wiki_all
rag__all
default
documents
knowledge
main
```

Any collection not matching an allowed pattern is forbidden. Qdrant does not enforce this — the retrieval policy and this skill must enforce it.

---

## Required metadata per indexed chunk

Every indexed chunk must include, where applicable:

| Field | Required for | Notes |
|---|---|---|
| `collection` | all | Exact collection name |
| `source_type` | all | `wiki_markdown`, `project_doc`, `project_report` |
| `project_id` | project collections | Full project ID string |
| `project_slug` | project collections | Filter key |
| `wiki_domain` | wiki collections | Filter key |
| `document_id` | all | Stable unique ID for the source file |
| `document_title` | all | Human-readable title |
| `source_file` | all | Absolute or repo-relative path |
| `nav_file` | wiki chunks | Path to nav YAML if applicable |
| `section_path` | all | Heading hierarchy (e.g. `H1 > H2 > H3`) |
| `heading` | all | Immediate section heading |
| `authority` | all | `shared_reference_authoritative_markdown`, `project_local`, etc. |
| `content_hash` | all | SHA-256 of chunk text for idempotent upsert |
| `created_at` | all | ISO 8601 timestamp |

---

## Standard workflow

Run prompts in this order. Do not skip steps or run them out of sequence.

```
Step 1  →  prompts/00-verify-wiki-operational-state.md
Step 2  →  prompts/01-create-wiki-domain.md           (if domain missing)
Step 3  →  prompts/02-verify-rag-tools.md
Step 4  →  prompts/03-create-project-bridge.md
Step 4b →  prompts/02b-profile-and-recommend-strategy.md  (profile source docs; choose retrieval route)
Step 4c →  prompts/02c-benchmark-retrieval-routes.md      (benchmark structured/table/RAG; record result)
Step 5  →  prompts/04-validate-project-policy.md
Step 6  →  prompts/07-add-wiki-reference-article.md   (add curated content)
Step 7  →  prompts/05-index-wiki-domain.md            (dry-run first, then live)
Step 8  →  prompts/06-post-index-retrieval-validation.md
Step 9  →  prompts/08-index-project-documents.md      (only if explicitly needed)
Step 10 →  prompts/09-troubleshoot-rag-bridge.md      (on failure at any step)
```

---

## Safety rules

These are hard rules. Violation requires explicit operator approval with written justification.

- **Always dry-run before live indexing.** Never index without a passing dry-run.
- **Never index raw data** unless the manifest entry has `index: true` and the document is not flagged `sensitive: true`.
- **Never create global collections.** Any collection named `default`, `documents`, `knowledge`, `rag__wiki_all`, `rag__all`, or `rag__global_all_docs` is forbidden.
- **Never index all wiki domains at once.** Index one domain at a time with explicit confirmation.
- **Never mix project data into wiki domain collections.**
- **Never mix wiki content into project collections** unless explicitly copied with full source reference.
- **Never modify `memories/raw/`.** That directory is immutable source material.
- **Never assume Qdrant enforces policy.** Policy is enforced by the retrieval-policy.yaml and this skill's guidance only.
- **Never invent wiki content.** All wiki articles must have a declared source reference.
- **Communications data requires review before indexing.** Mark all communications documents `index: false` by default.
- **Profile documents before choosing retrieval route.** Run `rag-tools profile-file` and `recommend-strategy` on each source document before deciding whether to index into Qdrant or use direct structured/table lookup.
- **Do not default to vector RAG for structured or tabular sources.** DCRs, rate cards, billing manifests, and policy documents must be evaluated with `profile-file` first. Vector RAG on exact-fact documents produces slower and hallucination-prone results compared to deterministic structured lookup.

---

## Agent behavior when invoked

When this skill is loaded, the agent must:

1. **Detect current root** — determine whether the working directory is in wiki, tools_stuff, or a project repo.
2. **Read relevant governance files** — `AGENTS.md`, `AI_NAVIGATION.md`, `SCHEMA.md`, `domain-registry.yaml`, `qdrant-collection-policy.md` as applicable.
3. **Validate before mutating** — run checks before creating or modifying files.
4. **Report exactly** — list every file created or modified, every command run, every check passed or failed.
5. **Use prompts as the execution layer** — do not improvise steps; use the numbered prompts.
6. **Emit readiness labels** at the end of every operation (see below).
7. **Profile source documents before indexing decisions** — run `rag-tools profile-file` on each project document to determine source class and recommended retrieval modes. Do not assume vector RAG.
8. **Run `recommend-strategy` before committing to an index** — use the strategy recommendation to decide: index into Qdrant, or route to structured/table lookup directly.
9. **Demand EvidenceBundle from retrieval operations** — never answer a user question from training knowledge. All retrieval must return an EvidenceBundle; answer only from its `excerpt` and `section_path` fields.

---

## Readiness labels

### Wiki operational state
| Label | Meaning |
|---|---|
| `WIKI_OPERATIONAL_READY` | All wiki roots exist, governance files present, domain registry valid |
| `WIKI_OPERATIONAL_PARTIAL` | Some components missing or invalid |
| `WIKI_OPERATIONAL_NOT_READY` | Critical components absent |

### Wiki domains
| Label | Meaning |
|---|---|
| `WIKI_DOMAINS_READY` | All declared domains have content and registry entries |
| `WIKI_DOMAINS_PARTIAL` | Some domains ready, some missing content or registry entry |
| `WIKI_DOMAINS_NOT_READY` | No valid domains |

### RAG tools
| Label | Meaning |
|---|---|
| `RAG_TOOLS_READY` | Doctor passes all checks, Qdrant reachable, embeddings confirmed |
| `RAG_TOOLS_PARTIAL` | Some checks failing (e.g. Qdrant down, venv missing) |
| `RAG_TOOLS_NOT_READY` | Tools not installed or venv absent |

### Project bridge
| Label | Meaning |
|---|---|
| `PROJECT_WIKI_BRIDGE_READY` | All bridge files present and valid |
| `PROJECT_WIKI_BRIDGE_PARTIAL` | Some bridge files missing or invalid |
| `PROJECT_WIKI_BRIDGE_NOT_READY` | Bridge files absent |

### Retrieval policy
| Label | Meaning |
|---|---|
| `PROJECT_RAG_POLICY_VALIDATED` | Policy YAML parses, rag-tools validates, all keys present |
| `PROJECT_RAG_POLICY_PARTIAL` | Policy exists but has missing keys or validator warnings |
| `PROJECT_RAG_POLICY_NOT_READY` | Policy file missing or unparseable |

### Indexing
| Label | Meaning |
|---|---|
| `WIKI_DOMAIN_INDEXED` | Collection exists with chunks, metadata verified |
| `WIKI_DOMAIN_INDEX_PARTIAL` | Collection created but chunk count low or metadata gaps |
| `WIKI_DOMAIN_INDEX_FAILED` | Indexing command failed or collection empty |

### Retrieval
| Label | Meaning |
|---|---|
| `RETRIEVAL_VALIDATED` | Test queries return results citing allowed collections only |
| `RETRIEVAL_PARTIAL` | Some queries succeed, some return empty or cite wrong sources |
| `RETRIEVAL_NOT_READY` | All queries fail or cite forbidden collections |

### Dynamic retrieval route
| Label | Meaning |
|---|---|
| `DOCUMENT_PROFILE_COMPLETE` | `profile-file` run; source class and section/table counts recorded |
| `STRATEGY_RECOMMENDED` | `recommend-strategy` run; ordered mode list recorded |
| `BENCHMARK_PASSED` | `benchmark-file` run; best route confirmed against query set |
| `RETRIEVAL_ROUTE_SELECTED` | Route chosen (vector RAG / structured / table / section); recorded in retrieval-strategy.yaml |

---

## Output contract

### Workflow report

Every operation using this skill must end with a structured report:

```
Verdict:          <READINESS_LABEL>
Files created:    <list or "none">
Files modified:   <list or "none">
Commands run:     <list of exact commands>
Checks passed:    <list>
Checks failed:    <list or "none">
Indexing status:  <WIKI_DOMAIN_INDEXED / not applicable>
Collection status: <collection name + chunk count, or "not applicable">
Next prompt:      <recommended next step from prompts/>
```

### EvidenceBundle contract

Every retrieval answer must be grounded in an EvidenceBundle. Do not answer from training knowledge.

```
retrieval_mode:    <structured | section | table | vector_rag>
source_file:       <absolute path>
authority:         <source authority level>
section_path:      <H1 > H2 > H3 heading chain>
excerpt:           <verbatim retrieved text — answer comes only from here>
score_or_confidence: <float>
retrieval_warnings: <list or empty>
```

If no EvidenceBundle is returned: report `RETRIEVAL_NOT_READY` and stop.

---

## Reference

| File | Purpose |
|---|---|
| `templates/` | Copy-and-fill templates for project bridge and wiki files |
| `prompts/` | Copy-paste-ready prompt scripts for each workflow step |
| `schemas/` | Field-level schema definitions for YAML files |
| `checklists/` | Blocking gate checklists for each readiness stage |
| `examples/` | Concrete examples (Vocus profitability, generic project) |
| `docs/` | Architecture, flow diagrams, failure modes, operating runbook |
````
