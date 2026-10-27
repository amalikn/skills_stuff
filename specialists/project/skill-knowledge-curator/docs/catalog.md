---
Title: skill-knowledge-curator Catalog
Category: catalog
Status: current
Authority: local-supplement; operator decisions 2026-10-27 (naming, C1, C2, C4-C6, promotion, folder, slurp timing); conflict analysis of the two source documents
Scope: Source documents under docs/ for skill-knowledge-curator, the operator decisions, and how each conflict between the two documents was settled
Last reviewed: 2026-10-27
Summary: >-
  Index of the two operator-supplied design documents for skill-knowledge-curator (alias skill-kc), the operator decisions, and where each of the
  twelve conflicts between them is settled in references/.
---

# skill-knowledge-curator catalog

Knowledge Curator (alias skill-kc): evidence-linked classification, deduplication and conflict review of project Markdown knowledge. Status: v1 kernel built
and tested on a synthetic fixture 2026-10-27; see [../SKILL.md](../SKILL.md) (Orient first) and [../references/evaluation.md](../references/evaluation.md).

## Decisions (operator, 2026-10-27)

- Skill name `skill-knowledge-curator`, alias `skill-kc`. This replaces `project-knowledge-curator` (design doc) and "Knowledge Curator" (handoff).
- Source documents live under `docs/` with hyphenated lower-case filenames; kept verbatim except front matter, Contents and the redrawn handoff section 4.1 diagram.
- Combine both documents; ask where they conflict; add features where the definition is incomplete; write the scripts under skill-coder.
- `knowledge/` starts as a derived view; a gated, recorded promotion makes a page authoritative, after which its absorbed sources can be archived.
- Promotion unit: one topic (category) page. Gates: no open P0/P1 conflict, a recorded operator decision bound to the page, governing files updated. `evidence_verified` added by
  default after a review note (a project may drop it).
- Archival: plan only in v1. Storage: append-only JSONL ledgers plus rendered Markdown views. Dependencies: the full design stack (NLI optional install).
- Project folder `.kc/`. skill-slurp-chat Step 4b is wired only after the pilot passes.

## Source documents

| Path                                                 | Kind         | What it holds                                                                                                                  |
| ---------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| [knowledge-curator-skill-implementation-handoff-v1.md](knowledge-curator-skill-implementation-handoff-v1.md) | agent        | Read-only MVP: taxonomy, record schema, slurp Step 4b contract, derived `knowledge/` index, tests T01-T14, stages 0-3          |
|                                                      |   handoff    |                                                                                                                                |
| [project-knowledge-curator-design-v1.md](project-knowledge-curator-design-v1.md) | design       | Invariants INV-001-016, atomic claim model, conflict severity P0-P3, review cards, JSONL decision ledger, `pkc` CLI,           |
|                                                      |              |   reversible archive, tests T-001-012                                                                                          |

## Skill pack

| Path | What it holds |
| --- | --- |
| [../SKILL.md](../SKILL.md) | Activation, workflow, tools, standing rules, write-back |
| [../references/](../references/) | workflow, claim-model-and-taxonomy, conflicts-and-review, authority-and-promotion, archive-safety, invocation-contract, evaluation, feature-inventory |
| [../scripts/readme.md](../scripts/readme.md) | `kc` commands, library modules, exit codes, runtime |
| [../schemas/](../schemas/) | Agent input schemas (claim, section status, relation, intake payload) |
| [../tests/](../tests/) | 42 tests; `fixtures/pilot` with `pilot-claims.json` and `pilot-relations.json` |

## Conflicts between the documents

All twelve settled 2026-10-27.

| # | Settled as | Where |
| --- | --- | --- |
| C1 | Derived by default; promotable per page through gates (operator) | [authority-and-promotion.md](../references/authority-and-promotion.md) |
| C2 | Plan only in v1; never moves sources (operator) | [archive-safety.md](../references/archive-safety.md) |
| C3 | Design's separate axes; handoff kind folded in, mapping given | [claim-model-and-taxonomy.md](../references/claim-model-and-taxonomy.md) |
| C4 | JSONL ledgers are the record; Markdown pages are views (operator) | [workflow.md](../references/workflow.md) |
| C5 | Operator answers; `kc decide` records it append-only; five actions | [conflicts-and-review.md](../references/conflicts-and-review.md) |
| C6 | Full design stack, each behind a seam; NLI optional (operator) | [workflow.md](../references/workflow.md) |
| C7 | Read-only by default; `--apply` writes only `.kc/` and `knowledge/` | [authority-and-promotion.md](../references/authority-and-promotion.md) |
| C8 | One `kc` front end with the design's commands plus five more; renderer replaces templates | [workflow.md](../references/workflow.md) |
| C9 | Handoff IDs primary, design IDs mapped; synthetic fixture now, MCP audit corpus (found on disk) next | [evaluation.md](../references/evaluation.md) |
| C10 | Documented now, wired after the pilot (operator) | [invocation-contract.md](../references/invocation-contract.md) |
| C11 | Handoff taxonomy enforced; namespaced extensions | [claim-model-and-taxonomy.md](../references/claim-model-and-taxonomy.md) |
| C12 | Python 3.14 via mise; venv in skills-working-cache | [workflow.md](../references/workflow.md) |

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

Not conflicts but gaps: severity P0-P3 and dirty-tree refusal exist only in the design; taxonomy and slurp trace exist only in the handoff. P0-P3 is adopted. Dirty-tree refusal is
not adopted for v1: the curator never writes a source, so a dirty tree cannot be overwritten; it returns with the deferred archive run.
