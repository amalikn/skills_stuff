---
name: skill-project-wiki-rag-bridge
description: "Bridges project repos to the shared LLM wiki + rag-tools, Qdrant-isolated."
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
