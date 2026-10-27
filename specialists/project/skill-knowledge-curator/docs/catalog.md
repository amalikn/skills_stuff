---
Title: skill-knowledge-curator Catalog
Category: catalog
Status: current
Authority: local-supplement; operator decisions 2026-10-27 (naming, C1, C2, C4-C6, promotion, folder, slurp timing); conflict analysis of the source documents
Scope: Source documents under docs/ for skill-knowledge-curator, the operator decisions, how each v1 conflict was settled, and the open v2 conflicts
Last reviewed: 2026-10-27
Summary: >-
  Index of the three operator-supplied design documents for skill-knowledge-curator (alias skill-kc), the operator decisions, where each of the
  twelve v1 conflicts is settled in references/, and the open conflicts between the v2 spec and the built v1.
---

# skill-knowledge-curator catalog

Knowledge Curator (alias skill-kc): evidence-linked classification, deduplication and conflict review of project Markdown knowledge. Status: v1 kernel built and tested on a synthetic fixture
2026-10-27; see [../SKILL.md](../SKILL.md) (Orient first) and [../references/evaluation.md](../references/evaluation.md).

## Contents

- [Decisions (operator, 2026-10-27)](#decisions-operator-2026-10-27)
- [Source documents](#source-documents)
- [Skill pack](#skill-pack)
- [Conflicts between the documents](#conflicts-between-the-documents)
- [v2 specification against the built v1 (open)](#v2-specification-against-the-built-v1-open)
- [Gaps in v1 (not conflicts)](#gaps-in-v1-not-conflicts)

---

## Decisions (operator, 2026-10-27)

- Skill name `skill-knowledge-curator`, alias `skill-kc`. This replaces `project-knowledge-curator` (design doc) and "Knowledge Curator" (handoff).
- Source documents live under `docs/` with hyphenated lower-case filenames; kept verbatim except front matter, Contents and the redrawn handoff section 4.1 diagram.
- Combine both documents; ask where they conflict; add features where the definition is incomplete; write the scripts under skill-coder.
- `knowledge/` starts as a derived view; a gated, recorded promotion makes a page authoritative, after which its absorbed sources can be archived.
- Promotion unit: one topic (category) page. Gates: no open P0/P1 conflict, a recorded operator decision bound to the page, governing files updated. `evidence_verified` added by default after a review
  note (a project may drop it).
- Archival: plan only in v1. Storage: append-only JSONL ledgers plus rendered Markdown views. Dependencies: the full design stack (NLI optional install).
- Project folder `.kc/`. skill-slurp-chat Step 4b is wired only after the pilot passes.

## Source documents

| Path                                                 | Kind         | What it holds                                                                                                                  |
| ---------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| [knowledge-curator-skill-implementation-handoff-v1.md](knowledge-curator-skill-implementation-handoff-v1.md) | agent        | Read-only MVP: taxonomy, record schema, slurp Step 4b contract, derived `knowledge/` index, tests T01-T14, stages 0-3          |
|                                                      |   handoff    |                                                                                                                                |
| [project-knowledge-curator-design-v1.md](project-knowledge-curator-design-v1.md) | design       | Invariants INV-001-016, atomic claim model, conflict severity P0-P3, review cards, JSONL decision ledger, `pkc` CLI,           |
|                                                      |              |   reversible archive, tests T-001-012                                                                                          |
| [knowledge-curator-foss-implementation-spec-v2.md](knowledge-curator-foss-implementation-spec-v2.md) | design v2    | Slurp Step 4c, FOSS tool matrix, code and diagram parsing, federated cross-project links, claim schema, run envelope, tests    |
|                                                      |              |   T01-T18 (own numbering), stages 1-7                                                                                          |

## Skill pack

| Path                 | What it holds                                                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [../SKILL.md](../SKILL.md) | Activation, workflow, tools, standing rules, write-back                                                                                               |
| [../references/](../references/) | workflow, claim-model-and-taxonomy, conflicts-and-review, authority-and-promotion, archive-safety, invocation-contract, evaluation, feature-inventory |
| [../scripts/readme.md](../scripts/readme.md) | `kc` commands, library modules, exit codes, runtime                                                                                                   |
| [../schemas/](../schemas/) | Agent input schemas (claim, section status, relation, intake payload)                                                                                 |
| [../tests/](../tests/) | 42 tests; `fixtures/pilot` with `pilot-claims.json` and `pilot-relations.json`                                                                        |

## Conflicts between the documents

All twelve settled 2026-10-27.

| #   | Settled as                                                                                           | Where                       |
| --- | ---------------------------------------------------------------------------------------------------- | --------------------------- |
| C1  | Derived by default; promotable per page through gates (operator)                                     | [authority-and-promotion.md](../references/authority-and-promotion.md) |
| C2  | Plan only in v1; never moves sources (operator)                                                      | [archive-safety.md](../references/archive-safety.md) |
| C3  | Design's separate axes; handoff kind folded in, mapping given                                        | [claim-model-and-taxonomy.md](../references/claim-model-and-taxonomy.md) |
| C4  | JSONL ledgers are the record; Markdown pages are views (operator)                                    | [workflow.md](../references/workflow.md) |
| C5  | Operator answers; `kc decide` records it append-only; five actions                                   | [conflicts-and-review.md](../references/conflicts-and-review.md) |
| C6  | Full design stack, each behind a seam; NLI optional (operator)                                       | [workflow.md](../references/workflow.md) |
| C7  | Read-only by default; `--apply` writes only `.kc/` and `knowledge/`                                  | [authority-and-promotion.md](../references/authority-and-promotion.md) |
| C8  | One `kc` front end with the design's commands plus five more; renderer replaces templates            | [workflow.md](../references/workflow.md) |
| C9  | Handoff IDs primary, design IDs mapped; synthetic fixture now, MCP audit corpus (found on disk) next | [evaluation.md](../references/evaluation.md) |
| C10 | Documented now, wired after the pilot (operator)                                                     | [invocation-contract.md](../references/invocation-contract.md) |
| C11 | Handoff taxonomy enforced; namespaced extensions                                                     | [claim-model-and-taxonomy.md](../references/claim-model-and-taxonomy.md) |
| C12 | Python 3.14 via mise; venv in skills-working-cache                                                   | [workflow.md](../references/workflow.md) |

The original comparison, kept for reference:

| #   | Topic                 | Handoff says                                                     | Design says                                                                                         |
| --- | --------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| C1  | Authority             | Derived index and view; "not a competing authoritative database" | "Curated current truth"; `.knowledge-curator/` is "authoritative metadata"                          |
|     |   of `knowledge/`     |                                                                  |                                                                                                     |
| C2  | Archival              | Never mutate originals; archive not in scope                     | Core goal: move originals to `archive/`, `git mv`, restore command (Phase F, Milestone 5)           |
| C3  | Status vocabulary     | One `lifecycle` (current, proposed, disputed, unverified,        | Two axes: epistemic status and disposition (CURRENT ... REVIEW_REQUIRED); warns against one         |
|     |                       |   superseded) plus `kind`                                        |   overloaded field                                                                                  |
| C4  | Record storage        | Markdown records with YAML front matter                          | Append-only JSONL ledgers (sources, sections, claims, conflicts, decisions)                         |
|     |                       |   plus `knowledge/index.json`                                    |                                                                                                     |
| C5  | Human decisions       | Curator never approves; flags `review_required`; who records the | `decisions.jsonl` append-only, five-choice review card, curator writes the answer                   |
|     |                       |   answer is not defined                                          |                                                                                                     |
| C6  | Dependencies          | Local scripts; vector store and semantic search deferred         | markdown-it-py, jsonschema, SQLite FTS5, RapidFuzz, optional NLI models                             |
| C7  | Writes into projects  | Read-only by default; outputs only in an explicitly              | `extract` writes `.knowledge-curator/` metadata into the project                                    |
|     |                       |   permitted location                                             |                                                                                                     |
| C8  | Package layout        | `templates/`, `curate.py`,                                       | `schemas/`, `pkc.py` with eleven subcommands and exit codes 0-6                                     |
|     |   and CLI             |   `validate_records.py`, `build_index.py`                        |                                                                                                     |
| C9  | Test IDs and          | T01-T14 on a 20-document synthetic fixture                       | T-001-012 plus semantic targets on the MCP post-migration audit (step10-13); location of that       |
|     |   pilot corpus        |                                                                  |   corpus unverified                                                                                 |
| C10 | slurp integration     | Central: optional Step 4b, one-to-one item trace for Step 6b     | Not mentioned                                                                                       |
| C11 | Taxonomy              | Five shared categories plus namespaced project subcategories     | None; `topic_key` only                                                                              |
| C12 | Runtime               | Unstated                                                         | "Python 3.11+"; workspace rule is Python 3.14 via mise with the venv                                |
|     |                       |                                                                  |   in `skills-working-cache/skill-knowledge-curator/`                                                |

## v2 specification against the built v1

Added 2026-10-27 20:05 (renamed from `knowledge_curator_v2_implementation_spec.md` at the pack root). The spec was written without sight of the v1 kernel (its section 13 says so). Its test IDs T01-T18
reuse the handoff's T01-T14 numbers with different meanings; cited here as `V2-T01` to `V2-T18`. Settled 2026-10-27 in two rounds below; nothing built yet.

| #   | Topic          | Built v1 (settled)                                                          | v2 says                                                                                         |
| --- | -------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| V1  | Source formats | Markdown only; other formats `unsupported` in inventory                     | Code (Tree-sitter, ast-grep), Mermaid, draw.io, ASCII diagrams, PDF/Office                      |
|     |                |                                                                             |   (MarkItDown, Docling)                                                                         |
| V2  | Cross-project  | Rejected: knowledge graph and cross-portfolio federation (INV-015)          | Federated discovery, NetworkX graph, alias table, per-project ACLs, proposals to owners         |
| V3  | Dependencies   | jsonschema, RapidFuzz, markdown-it-py, FTS5; NLI optional (no torch)        | Pydantic required; Sentence Transformers required when semantic on; GLiNER, LightRAG pilot      |
| V4  | Claim schema   | Nine kinds; two axes, epistemic and disposition (C3)                        | Seven kinds; one `status` field; subject-predicate-object triple; `confidence`                  |
| V5  | Curator role   | Agent extracts, `kc` validates; `--apply` writes `.kc/`, `knowledge/`;      | Emits proposals only; LLM synthesis inside the curator via a model adapter; no promotion        |
|     |                |   promotion gates                                                           |   or archive                                                                                    |
| V6  | slurp hook     | Step 4b, wired after the pilot (C10); neither 4b nor 4c exists in           | Conditional Step 4c; `curator status` column in the slurp coverage table                        |
|     |                |   slurp today                                                               |                                                                                                 |
| V7  | Test IDs       | Handoff T01-T14 primary, design T-001-012 mapped (C9)                       | T01-T18, different scenarios under the same numbers                                             |
| V8  | Package layout | One `kc` front end, `knowledge_curator_lib/` package                        | Seven scripts; section 9 defers to existing conventions, so v1 layout stands                    |
| V9  | Output         | `kc intake` returns one outcome per slurp item                              | Run envelope: claims, relationships, conflicts, `proposed_updates`, `unresolved`, `audit`       |

Answers (operator, 2026-10-27, round 1):

- Role: staged roadmap. v1 is the base; each v2 item starts only after the real-corpus pilot passes.
- V1 formats: all four adopted as stages: Mermaid and draw.io, source code, PDF and Office, ASCII diagrams. Diagram and static-code findings stay candidate.
- V2 federation: within one portfolio only (all apn, or all personal), never across; references and candidate relations only, proposals to the owning project.
  INV-015 is narrowed, not dropped.
- V3/V4 schema and libraries: keep v1 (two-axis model C3, jsonschema, RapidFuzz); add optional subject/predicate/object fields and a v2-to-v1 kind and status
  mapping; embeddings behind an optional install, as NLI is.
- V7 test IDs and V8 layout: agent defaults, not asked (the operator may override): v2 tests cited as `V2-T01` to `V2-T18`; v1 layout stands, as v2
  section 9 defers to existing conventions.

Answers (operator, 2026-10-27, round 2):

- V5 LLM: optional model adapter in `kc` (default local Ollama), off unless configured; agent-extracted claim JSON stays the default path and every adapter
  output passes the same schema and evidence checks.
- V5 promotion: both paths kept. Own project: v1 promotion gates. Cross-project or slurp-driven: proposals only, the owning project decides.
- V6 slurp: Step 4b, conditional, with v2's invoke and skip triggers and a curator-status column in the coverage table; wired only after the pilot.
- V9 output: `kc intake` also writes the v2 run envelope beside the per-item outcomes. Per-project `.kc/` config gains an offline-only flag (no cloud model,
  no embedding download) and a model allowlist naming which models may read the project.

All nine v2 rows settled; none built yet. Build order follows v2 section 12 after the real-corpus pilot.

## Gaps in v1 (not conflicts)

Not conflicts but gaps: severity P0-P3 and dirty-tree refusal exist only in the design; taxonomy and slurp trace exist only in the handoff. P0-P3 is adopted. Dirty-tree refusal is
not adopted for v1: the curator never writes a source, so a dirty tree cannot be overwritten; it returns with the deferred archive run.
