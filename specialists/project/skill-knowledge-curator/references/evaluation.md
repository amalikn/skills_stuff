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
- [Pilot on the Continuum corpus (2026-10-30)](#pilot-on-the-continuum-corpus-2026-10-30)
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

> **Learned 2026-10-29** · curated lookup data and model-proposed entries · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal decision-support
> project) · Source: project_stuff/me decision-support project `decisions/vocabulary-layer-20260913_1621.md` · Falsifier: a harvested or
> model-proposed vocabulary that matched a curated one without review, negation included
> Harvesting is not curation. Three routes to a synonym layer were measured: a general lexical resource failed on register; an automated
> harvest kept 513 of 542 phrases after filtering, with misspellings and topic drift surviving; a domain embedding model scored 48% top-1
> and 69% top-3 against the curated table and inverted polarity on negated phrases. Keep curated entries primary, let harvested or
> model-proposed entries in only as reviewable candidates, measure any model against the curated set before trusting it, and test
> negation explicitly. This is the same rule as agent-extracted claims needing verified excerpts, applied to lookup data.


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

## Pilot on the Continuum corpus (2026-10-30)

> **Learned 2026-10-30** · first real-corpus run, curation capability · VERIFIED_PRIMARY (run in a scratch copy of the project, ledgers discarded) ·
> Source: `tools_stuff/continuum` (44 sources, 904 sections; canary on 2 files, 32 sections); `scripts/knowledge_curator_lib/candidates.py:73-85` at `cdce4fa` ·
> Falsifier: two sources stating the same position in different predicate wording that `kc candidates` pairs without a shared vocabulary
> The kernel is sound; cross-source curation is not yet. Excerpt verification held (15 of 15 random claims exact; dry run and `--apply` agree; 31 of 31 canary
> sections covered). But conflict recall depends on the extracting agents wording subject and predicate identically across batches, and nothing gives them a
> shared vocabulary.

Corpus: a product design collection (Markdown specifications and two extracted ZIP packs, byte duplicates removed first). Canary: an implementation proposal (v0.3) and a
same-day reuse assessment, extracted by one agent with external-fact checks.

Measured: 338 claims from 31 sections (10.9 per section; 195 proposal, 64 decision, 62 requirement, 13 external_fact, 5 hypothesis); extraction 8.8 min and about 166k agent
tokens; kernel `claims --apply` 0.22 s, `candidates` 0.1 s, `render` 0.16 s, `validate` 0.15 s. Linear projection for the corpus: about 9,800 claims, about 4.7M tokens.

Probe (the deciding test). The second source's README states, as its current position, that it "preserves … existing Fastify/TypeScript coordinator"; the first source decides
an Axum coordinator. Added as a claim with subject `continuum coordinator`, predicate `implementation`: **0 candidate pairs**. Same claim with the predicate worded as the
Axum claim's (`uses framework`): paired at once (`same-key-different-object`, similarity 50). The signal logic needs equal subject and predicate, or text similarity of at
least 70-80; real cross-document disagreements rarely share wording:

```python
# scripts/knowledge_curator_lib/candidates.py:73-85 (cdce4fa)
same_key = ids.norm(a["subject"]) == ids.norm(b["subject"]) and ids.norm(a["predicate"]) == ids.norm(b["predicate"])
overlap = scope_overlaps(a["scope"], b["scope"])
if same_key and overlap and ids.norm(a["object"]) != ids.norm(b["object"]):
  out.append("same-key-different-object")
...
if (same_key or ratio >= 70) and nums_a and nums_b and nums_a != nums_b:
  out.append("numeric-mismatch")
```

Findings (fixes are listed in [feature-inventory.md](feature-inventory.md), "Fixes from the Continuum pilot"):

| ID  | Finding | Evidence |
| --- | ------- | -------- |
| P1  | Cross-source conflict recall depends on agent wording; disagreements the canary agent found by reading (checkpoint/restore scope, atomicity wording, gateway role, continuity modes) produced no cross-source pair | probe above; 1 of 178 pairs crossed sources |
| P2  | Candidate output is dominated by same-source enumerations: 178 of 178 pairs shared source bytes, most `numeric-mismatch` between parallel rows ("phase P6 is 5-9 weeks" against "phase P8 ...") | `kc candidates` on the canary |
| P3  | Retrieval and pages show contradictory claims both `CURRENT` with no flag while candidate pairs are unclassified (`kc query coordinator`: "keeps Fastify" and "uses Rust Axum", `conflicts: []`) | `kc query` |
| P4  | `HISTORICAL` is accepted with no relation or successor; `history.md` lists "in v0.2 the coordinator used Fastify" with no link to the Axum decision on another page | `render` output |
| P5  | Pages group by the five primary categories only: 963 lines for 338 claims; about 28,000 projected; project subcategories do not shape pages | `render` output |
| P6  | No granularity rule: table rows split into three claims each; 10.9 claims per section floods candidates and review | canary counts |
| P7  | `topic_key` collides across sources (both sources number ADR-001 to ADR-006); the agent improvised namespaces | canary report |
| P8  | `validate` passes (`ok: true`) with 870 sections pending; a done-gate needs a strict mode | `kc validate` |
| P9  | `claims` dry run reports no coverage effect, so an agent cannot see which sections a batch would close | canary report |
| P10 | A blank-line off-by-one rejects the whole batch with `evidence/0/excerpt: '' is too short` and no source line shown | canary report |
| P11 | No link or external-fact verification in the kernel (recorded in Deferred) | operator, 2026-10-30 |
| P12 | A provenance key in `scope` (`{"source": ...}`) makes every cross-source pair non-overlapping, so `same-key-different-object` never fires between sources: 11,313 of 13,341 cross-source pairs carried only `same-key-different-scope`. The coordinator caused it by instructing agents to put the source in scope; the kernel gave no warning | full run, `kc candidates` |
| P13 | At 3,491 claims `candidates` returns 18,129 pairs (13,341 cross-source) in 5.2 s, over the 2 s budget and far beyond what an agent can classify pair by pair. Grouping by subject and predicate across two or more sources with differing objects gave 283 decision points (1,707 claims), a reviewable unit | full run |
| P14 | `decide CORRECTED` inherits each conflict's scope, so one operator wording recorded on three conflicts made three identical APPROVED claims (`cl-e9af230d5a50`, `cl-5818d486e678`, `cl-c9b26284d37f`) | Continuum decisions, 2026-11-01 |
| P15 | The default `exclude_dirs` drops any folder named `archive`, so a source pack's `archive/` was silently skipped; the exclusion shows only in the inventory report | Continuum inventory |
| P16 | A pack of parallel agents needs a shared file: three `kc` steps have no path filter (`worksheet`), no coverage in dry run (P9), and no way to list ids by file, so every agent wrote its own helpers; six near-identical `coverage.py` scripts resulted | Continuum batches |
| P17 | Derived pages are not the deliverable for design corpora: operators want authored pages; a page-to-ledger coverage gate (`check_architecture_coverage.py`) and per-area registers (`render_claim_registers.py`) gave the proof without `kc render` | Continuum 2026-11-01 |
| P18 | Agent claim text can be lossy against its own excerpt: rewrite agents reading the sources corrected truncated and relabelled claims, though every excerpt had verified. Excerpt checks prove the quote, not the paraphrase | Continuum rewrite pass, 2026-11-01 |

Full run (same day, option "shared vocabulary + coarser granularity"): 8 extraction agents, 904 of 904 sections accounted for (876 claims-extracted, 28 context), 3,491 claims
(3.86 per section, down from 10.9 in the canary), every batch's dry run and apply exit 0 with zero vocabulary-conformance issues; agent cost about 1.66M tokens, 9-16 minutes
per batch in parallel; each batch applied in under 1 s; `validate` ok. Three of eight agents first put the bare topic name in `subcategories` and got
`subcategory '<x>' not in <category> taxonomy` for the whole batch: the extraction guide's wording, fixed in the project.

Interim practice until the fixes land: give every extraction batch one shared vocabulary file (subjects, predicates, topic-key namespaces per source), and run a
cross-source conflict pass by topic in addition to `kc candidates`.

## Release gate

All deterministic items pass, the real-corpus pilot gives useful evidence-backed retrieval reviewed by the operator, semantic targets are measured (or exceptions accepted), and no high-severity
correctness or confidentiality defect is open. Then wire slurp Step 4b, and stop.
