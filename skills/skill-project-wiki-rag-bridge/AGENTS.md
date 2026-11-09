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
