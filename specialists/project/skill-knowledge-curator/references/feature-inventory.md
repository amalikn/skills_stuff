---
Title: Feature inventory
Category: reference
Status: current
Authority: local-supplement; both source documents, operator decisions 2026-10-27, enhancements added in the first build
Scope: Every feature from the two source documents and the enhancements added beyond them, with disposition (built, deferred, rejected) and invariant coverage
Last reviewed: 2026-10-27
Summary: >-
  What exists now, what was added beyond the documents and why, what is deferred and on what trigger, and where each design invariant is enforced.
---

# Feature inventory

## Contents

- [Built in v1](#built-in-v1)
- [Added beyond the source documents](#added-beyond-the-source-documents)
- [Deferred](#deferred)
- [Invariants and where they are enforced](#invariants-and-where-they-are-enforced)

## Built in v1

Inventory with hashes, renames, removals, exclusions and byte-duplicate groups; Markdown block parsing with line spans; agent claim intake with verified evidence; coverage accounting; candidate
generation (FTS5, RapidFuzz, signals, optional NLI); relation intake with policy-limited automatic dispositions; conflicts with P0-P3; review cards; five decision actions, append-only, revalidated;
deterministic rendering of category, history, open-issues and index pages plus `index.json`; promotion with four gates and revocation; archive plan with referrers and restore rehearsal; query;
slurp-style intake; validate; report; single-writer lock; path containment; secret scan on output.

## Added beyond the source documents

| Feature                                                                            | Why                                                                                          |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Promotion stage (derived -> promoted -> archive) with digest-bound approval        | Operator, 2026-10-27: start derived, promote by a process, then archive                      |
| `evidence_verified` promotion gate on by default                                   | A source edited after render would otherwise be promoted stale (review, 2026-10-27)          |
| `kc worksheet`: pending sections in bounded batches with an `imperative-text` flag | Makes extraction incremental and resumable, and keeps injection text visibly data            |
| Automatic `context` for front matter and lone `Status:` lines                      | Removes busywork without guessing: only certain cases                                        |
| `kc query` with `settled` and `--history`                                          | Agent retrieval that cannot present a disputed or superseded claim as current (T07, INV-013) |
| `kc intake` implemented now                                                        | The slurp contract is testable before slurp is wired                                         |
| Rename detection keeps `source_id`                                                 | Moving a file must not orphan its claims                                                     |
| Section IDs keyed on content, not line numbers                                     | Unchanged blocks keep their coverage when the file changes elsewhere                         |
| `USE_OTHER` instead of "use earlier"                                               | Earlier or later is not always the frame; the operator names the claim                       |
| `elapsed_s` on every command                                                       | Efficiency is part of done                                                                   |

## Deferred

| Item                                                         | Trigger to build                                                  |
| ------------------------------------------------------------ | ----------------------------------------------------------------- |
| Real archive run (`archive --apply`, restore command, T-008) | Pilot passes and the operator asks ([archive-safety.md](archive-safety.md)) |
| skill-slurp-chat Step 4b wiring                              | Pilot passes (operator, 2026-10-27)                               |
| Gold-set semantic evaluation harness                         | Before release ([evaluation.md](evaluation.md))                   |
| Topic-level locks for concurrent writers (design 11)         | A second writer actually appears; one project lock today          |
| Persisted FTS cache under `.kc/cache/`                       | Candidate runs exceed the 2 s budget                              |
| SilverBullet, Quartz, LLM Wiki one-way compile, MCP facade   | A usability test shows a gap; never a second writable truth store |
| CI workflow for structural checks                            | A project asks for it                                             |
| Non-Markdown formats beyond inventory (`unsupported` today)  | A pilot project needs one                                         |

Rejected for v1: vector database, daemon or crawler, knowledge graph, autonomous fact approval, edits to governing files, cross-portfolio federation (apn and personal records are never cross-indexed;
INV-015).

## Invariants and where they are enforced

| Invariant                                | Enforced by                                                                  |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| INV-001 immutable originals              | Sources only read; hashes and sizes recorded; archive is plan-only           |
| INV-002 source accounting                | `inventory`: every in-scope file has a state; exclusions listed with reasons |
| INV-003 section accounting               | `coverage`, `worksheet`, `validate` warning                                  |
| INV-004 one disposition                  | Fold keeps the last disposition event per claim                              |
| INV-005 evidence                         | `claims` intake refusal; `validate`                                          |
| INV-006 conflict blocking                | `State.effective`; render's Not settled; promotion gate                      |
| INV-007 human authority                  | Only `decide` resolves conflicts; only explicit answers                      |
| INV-008 no newest-wins                   | Claim IDs include the object; candidates pair same-key claims                |
| INV-009 no loss by dedupe                | Restatements merge evidence; DUPLICATE keeps its evidence and link           |
| INV-010 safe archive                     | Plan only, rehearsal, referrers                                              |
| INV-011 idempotence                      | Content-derived IDs; skip-if-recorded in every intake; deterministic render  |
| INV-012 fail closed                      | Whole-batch rejection, write lock, atomic replace, exit 5 on changed sources |
| INV-013 read precedence                  | `query` hides history unless asked; `settled` flag                           |
| INV-014 no exhaustiveness claim          | Coverage is accounting; semantic recall measured separately                  |
| INV-015 no cross-project contamination   | Ledgers per project; IDs include `project_id`                                |
| INV-016 attributed, reversible decisions | `previous_decision_id`; revocation records; nothing overwritten              |
