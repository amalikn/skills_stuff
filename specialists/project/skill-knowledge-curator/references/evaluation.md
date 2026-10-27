---
Title: Evaluation
Category: reference
Status: current
Authority: local-supplement; handoff section 8 (T01-T14), design doc sections 12-13 (T-001 to T-012, semantic targets, metamorphic tests), merged; results measured 2026-10-27
Scope: The merged acceptance catalog, which test covers each item and its status, the semantic evaluation still owed, and the pilot plan on the MCP audit corpus
Last reviewed: 2026-10-27
Summary: >-
  One catalog with handoff IDs as primary and design IDs mapped beside them; deterministic items pass on the synthetic pilot fixture (42 tests);
  semantic recall and the real-corpus pilot are not yet measured. Settles source conflict C9.
---

# Evaluation

## Contents

- [Deterministic catalog](#deterministic-catalog)
- [Semantic evaluation (not yet measured)](#semantic-evaluation-not-yet-measured)
- [Pilot on the MCP post-migration audit](#pilot-on-the-mcp-post-migration-audit)
- [Release gate](#release-gate)

## Deterministic catalog

IDs: handoff `Tnn` primary, design `T-nnn` mapped; they number different things, so both are kept. Status as of 2026-10-27: `just test` (42 tests, all pass) on `tests/fixtures/pilot` (8 synthetic
documents seeded with a byte copy, a supersession, two P1 conflicts, a scope split, a proposal, an injection line).

| ID  | Design       | Test                                                             | Pass criterion                                                   | Status                                    |
| --- | ------------ | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------- |
| T01 | T-001, T-003 | test_inventory_claims (counts, coverage)                         | Every file and section accounted for                             | pass (fixture)                            |
| T02 | T-004        | test_inventory_claims (merge), test_conflicts_decisions (equivalent) | Duplicates grouped, sources kept, byte copies one                | pass                                      |
|     |              |                                                                  |   independent source                                             |                                           |
| T03 | T-006        | test_conflicts_decisions (both kept and blocked)                 | Both sides kept; REVIEW_REQUIRED; no silent choice               | pass                                      |
| T04 | -            | test_conflicts_decisions (supersession), test_contract_seams     | Supersession only with a verified excerpt; successor linked      | pass                                      |
| T05 | -            | test_inventory_claims (taxonomy)                                 | Shared category, namespaced extension, labels                    | pass                                      |
| T06 | T-005, T-011 | test_inventory_claims (bad excerpt, INV-005)                     | Evidence resolves or the batch is refused                        | pass                                      |
| T07 | -            | test_publish_promote (query)                                     | Topic gives claim, settlement, conflicts, source lines           | pass                                      |
| T08 | -            | test_publish_promote (navigation)                                | index.md -> page -> source line                                  | pass                                      |
| T09 | T-010        | inventory rerun, render twice, candidates after relate           | No new records, identical bytes, no repeat questions             | pass                                      |
| T10 | -            | test_publish_promote (intake trace)                              | One outcome per item                                             | pass (kernel); slurp wiring pending       |
| T11 | -            | intake skips routine items                                       | Routine items skip curation                                      | pass (kernel)                             |
| T12 | -            | intake rejects bad payload; slurp failure path documented        | Failure reported, nothing promoted                               | partial: slurp side pending               |
| T13 | -            | worksheet flags imperative text; render refuses secrets          | Not executed, not published                                      | pass                                      |
| T14 | -            | sources byte-identical after a full run                          | Curator never edits sources or governing files                   | pass                                      |
| -   | T-002, T-009 | archive-plan rehearsal                                           | Hashes match both ways                                           | pass (rehearsal only; no real archive     |
|     |              |                                                                  |                                                                  |   in v1)                                  |
| -   | T-007        | promote with a wrong digest                                      | Approval bound to exact body                                     | pass                                      |
| -   | T-008        | -                                                                | Rollback under injected interruption                             | not built: needs the deferred archive run |
| -   | T-012        | symlink outside root, `..` path, second writer                   | Fail closed                                                      | pass                                      |
| -   | metamorphic  | step99 opposite claim; changed evidence before decide            | Number never wins; decision stops on change                      | pass                                      |

## Semantic evaluation (not yet measured)

Structural gates do not prove the agent extracted every important fact (INV-014). Owed before release (design 13.2): a gold set of at least 30 source pairs (15 real conflicts, 10 time or context
changes, 5 duplicates) and 100 labelled claims, with targets of 100% recall on P0/P1 conflicts and zero auto-promoted winners, at least 95% recall on high-value claims with no dropped numeric
threshold, at least 90% precision for conflict prompts, and 100% evidence validity (the last is enforced by code). Reruns across models and prompt variants; one good run is not enough.

## Pilot on the MCP post-migration audit

Corpus: `/Volumes/Data/_ai/_project/project_stuff/mcp-post-migration-audit` (24 Markdown files). A read-only inventory on 2026-10-27 found 213 sections and five byte-identical pairs between
`final-audit-pack/` and the step reports (design case F, found automatically). Next, read-only with ledgers in a scratch copy first:

| Case | Expectation                                                                                               |
| ---- | --------------------------------------------------------------------------------------------------------- |
| A    | step10 "retained" -> step11/step12 "retired": time-evolution with step11's excerpt; step10 historical     |
| B    | step12 `CURRENT AUTHORITATIVE` versus step13 `CURRENT SUPPORTING`: step13 never replaces step12 by number |
| C    | VoiceMode no-shim failure and with-shim recovery both kept as test results; shims retained                |
| D    | A synthetic "shims can be removed" file opens a conflict; never published as approved                     |
| E    | Step10's original text retrieved through the ledger with matching SHA-256                                 |
| F    | Curated copies count as one independent source                                                            |

## Release gate

All deterministic items pass, the real-corpus pilot gives useful evidence-backed retrieval reviewed by the operator, semantic targets are measured (or exceptions accepted), and no high-severity
correctness or confidentiality defect is open. Then wire slurp Step 4b, and stop.
