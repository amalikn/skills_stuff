---
Title: Conflicts and review
Category: reference
Status: current
Authority: local-supplement; design doc section 7 (adjudication core); handoff authority-and-conflicts contract; schemas/relation-input.schema.json
Scope: Candidate generation, pair classification, what may be decided automatically, severity, review cards, decision actions and records, answering with unresolved knowledge
Last reviewed: 2026-10-27
Summary: >-
  Candidates come from FTS5 blocking plus RapidFuzz and deterministic signals; the agent classifies each pair; only duplicates and evidenced supersessions
  are automatic; every true or uncertain conflict becomes a review card the operator answers with one of five actions, recorded append-only.
---

# Conflicts and review

## Contents

- [Pipeline](#pipeline)
- [Pair classification](#pair-classification)
- [Authority questions to ask](#authority-questions-to-ask)
- [Severity](#severity)
- [Review card and actions](#review-card-and-actions)
- [Decision record](#decision-record)
- [Answering while unresolved](#answering-while-unresolved)

## Pipeline

1. `kc candidates`: each claim is compared only with its SQLite FTS5 neighbours and claims sharing its subject (near-linear, not all pairs). A pair is kept when RapidFuzz token-set similarity reaches
   `candidates.min_ratio` (default 80) or a deterministic signal fires: `same-key-different-object`, `same-key-different-scope`, `numeric-mismatch`, `negation-asymmetry`, `kind-differs`. With
   `requirements-nli.txt` installed, an NLI contradiction score is added for ranking only. Pairs already classified are left out.
2. The agent reads both claims' primary spans and surrounding paragraphs (a second, independent pass), then writes one `relation` record per pair.
3. `kc relate --file ... --apply` records them and applies only the automatic outcomes below.
4. `kc review` prints the queue (exit 2 while anything is open); the operator answers; `kc decide ... --apply` records each answer.

Similarity is never contradiction, and no match is never proof of no conflict.

## Pair classification

| Relation                                     | Effect                                                                    | Needs                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `equivalent`                                 | The claim with fewer independent sources becomes `DUPLICATE` with         | reason                                                                    |
|                                              |   `duplicate_of`; its evidence stays                                      |                                                                           |
| `corroborating`, `refinement`,               | Recorded only; both claims keep their dispositions                        | reason                                                                    |
|   `different-scope`,                         |                                                                           |                                                                           |
|   `proposal-vs-observation`                  |                                                                           |                                                                           |
| `time-evolution`                             | The older claim becomes `SUPERSEDED` with `successor`                     | `superseded`, `successor` and a verified `supersession_evidence` span: an |
|                                              |                                                                           |   explicit statement such as "this replaces ..."                          |
| `true-conflict`, `uncertain`                 | Opens a conflict; both claims stay; nothing is promoted                   | `severity` (P0-P2), `question`, optional `recommended_current`,           |
|                                              |                                                                           |   `hypotheses`, `conflict_type`                                           |

Automatic outcomes are limited to exact or semantic duplicates and explicit, evidenced supersession (design 7.2). Human confirmation is required for: conflicting approved requirements, incompatible
current deployment facts without corroboration, security-sensitive facts, unclear authoritative version, and anything that would invalidate a live architecture, runbook or acceptance criterion. When
unsure, classify `uncertain`.

## Authority questions to ask

Before recommending, the agent checks (design 7.2):

1. Is one text explicitly marked superseded, retracted or historical (the source's `declared_status` is recorded)?
2. Is the newer statement an observation backed by a current test, or only a proposal?
3. Is there a recorded human decision with matching scope and effective date?
4. Do the texts concern different versions, environments or periods (then `different-scope`)?
5. Is the evidence first-hand and reproducible, or a derived summary?
6. Did the later document explicitly incorporate and invalidate the earlier one?

A higher step number, a longer text, a more confident tone or more copies decide nothing (INV-008; ten copies of one file are one independent source).

> **Learned 2026-10-29** · amendments and binding records · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal corpus project) · Source:
> project_stuff/me corpus project `ARCHITECTURE.md` (layers), `scripts/record_index.py` · Falsifier: a query over an amended document
> alone that returned the corrected answer without resolving its amending records
> Make amendment links machine-readable (an `Amends:` header on each decision record) and resolve them before citing any document: an
> accepted decision record outranks the policy text it amends until that text is updated, and a query that reads only the amended document
> still gets the pre-correction answer. A small index that prints which records bind a given document answers questions 3 and 6 above
> mechanically.


## Severity

| Severity | Typical issue                                                                              | While open                                                         |
| -------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| P0       | Security, destructive instruction, incompatible production runbook or current architecture | Blocks the page's promotion and every archive candidate citing it  |
| P1       | Conflicting requirements, implementation decisions, verified outcomes                      | Claims publish as `REVIEW_REQUIRED`; blocks promotion of that page |
| P2       | Terminology, alternative proposals, low-impact ambiguity                                   | Claims stay `CURRENT`, listed in open issues                       |
| P3       | Duplicate or style difference                                                              | Not a conflict: classify `equivalent`                              |

## Review card and actions

`kc review` groups open conflicts by `topic_key` (one decision per concept), P0 first. Each card shows both claims, their kinds, dispositions and source lines, the assessment, the hypotheses and the
recommendation, then the five actions:

| Action                  | Effect                                                                                           | Extra argument                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| `ACCEPT_RECOMMENDATION` | Recommended claim `CURRENT`, the other `SUPERSEDED`                                              | none (fails if there is no recommendation)                              |
| `USE_OTHER`             | Chosen claim `CURRENT`, the other `SUPERSEDED`                                                   | `--current <claim>`                                                     |
| `BOTH_APPLY_SCOPED`     | Both stay `CURRENT`; conflict resolved as different scope                                        | `--scope-note` naming the separating condition (then revise the         |
|                         |                                                                                                  |   claims' scopes)                                                       |
| `CORRECTED`             | New operator-authored `decision` claim, `APPROVED`, backed by the decision ID; both old          | `--corrected-text`                                                      |
|                         |   claims `SUPERSEDED`                                                                            |                                                                         |
| `DEFER`                 | Answer logged, conflict stays open, neither claim settled                                        | none                                                                    |

The design's "use earlier statement" is `USE_OTHER`, because earlier and later are not always the right frame. When the operator chooses a target policy over a live observation, record that in
`--reason`; the observation is not rewritten as false, and a fresh verification may be needed.

No answer means `REVIEW_REQUIRED`, never default approval; no scheduled run may simulate consent. A partial answer applies only to the conflict it names.

## Decision record

`kc decide` first re-checks every evidence span of both claims; a changed source stops it (exit 5). The record appended to `.kc/decisions.jsonl` holds `decision_id`, `conflict_id`, `action`, `actor`
(`--actor` or `KC_ACTOR`), `decided_at`, `reason`, `answer_text` (the operator's words when given), `scope_note`, `current_claims`, `superseded_claims` and `previous_decision_id`. A reversal is a new
decision naming the old one; nothing is overwritten (INV-016). Identity comes from the session, not from authentication: do not call it verified.

## Answering while unresolved

`kc query <text>` returns `settled: false` and the open conflict for a disputed claim. An agent answers: "Not settled: A says X, B says Y; conflict cf-... awaits a decision", never one side as fact
(design 7.9). Superseded and historical claims appear only with `--history`, marked as such (INV-013).
