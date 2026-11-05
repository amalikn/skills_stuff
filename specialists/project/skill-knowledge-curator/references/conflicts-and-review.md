---
Title: Conflicts and review
Category: reference
Status: current
Authority: local-supplement; design doc section 7 (adjudication core); handoff authority-and-conflicts contract; schemas/relation-input.schema.json
Scope: Candidate generation, pair classification, what may be decided automatically, severity, review cards, decision actions and records, answering with unresolved knowledge
Last reviewed: 2026-11-05
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
- [Amending a conflict](#amending-a-conflict)
- [Review prompts](#review-prompts)
- [Triage](#triage)
- [Root causes](#root-causes)
- [Refuting verifier](#refuting-verifier)
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
> project_stuff/me corpus project `ARCHITECTURE.md` (layers), `scripts/record_index.py` · Falsifier: a query over an amended document alone that returned the corrected answer without resolving its
> amending records Make amendment links machine-readable (an `Amends:` header on each decision record) and resolve them before citing any document: an accepted decision record outranks the policy text
> it amends until that text is updated, and a query that reads only the amended document still gets the pre-correction answer. A small index that prints which records bind a given document answers
> questions 3 and 6 above mechanically.


## Severity

| Severity | Typical issue                                                                              | While open                                                         |
| -------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| P0       | Security, destructive instruction, incompatible production runbook or current architecture | Blocks the page's promotion and every archive candidate citing it  |
| P1       | Conflicting requirements, implementation decisions, verified outcomes                      | Claims publish as `REVIEW_REQUIRED`; blocks promotion of that page |
| P2       | Terminology, alternative proposals, low-impact ambiguity                                   | Claims stay `CURRENT`, listed in open issues, `settled: false`     |
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

Many conflicts at once: put them to the operator as one tick-box sheet, not rounds of four questions (operator, Continuum 2026-11-05: "write all the questions in a markdown file ... options as
checkboxes ... an option for other as well"). `scripts/decision_sheet.py` builds it from the saved queue: one box per action, each carrying its claim id, plus Other and Notes. When the operator asks
for recommendations, mark one option `(Recommended)` per question with a one-line reason; it is advice, the operator still decides, and nothing is recorded until a box is ticked and `kc decide` runs.
Never regenerate a sheet the operator has started filling in: check for ticks first, then edit in place.

No answer means `REVIEW_REQUIRED`, never default approval; no scheduled run may simulate consent. A partial answer applies only to the conflict it names.

## Decision record

`kc decide` first re-checks every evidence span of both claims; a changed source stops it (exit 5). The record appended to `.kc/decisions.jsonl` holds `decision_id`, `conflict_id`, `action`, `actor`
(`--actor` or `KC_ACTOR`), `decided_at`, `reason`, `answer_text` (the operator's words when given), `scope_note`, `current_claims`, `superseded_claims` and `previous_decision_id`. A reversal is a new
decision naming the old one; nothing is overwritten (INV-016). Identity comes from the session, not from authentication: do not call it verified.

## Amending a conflict

A ruling can cover a claim the conflict did not list. `kc amend <cf> --add-claim <id> --supersede --reason ... --apply` adds it to a decided conflict and supersedes it under the ruling; `--keep` lists
it and leaves its disposition, on an open or decided conflict. Each records an `AMEND` decision naming the previous one. Record it only from the operator's own ruling. Identical `CORRECTED` wording on
a second conflict reuses the first operator claim.

`decide` refuses to make a claim current when another conflict or relation superseded it. If the operator means that, `--override-supersession` revives it and the decision records the override;
`validate` warns on any revival with no override. A claim already superseded elsewhere keeps its successor (`kept_successors` on the decision); `kc amend <cf> --set-successor <claim> --successor <id>
--reason ...` repairs a wrong link.

Trying `amend` on a scratch copy needs a real copy of the sources, because it re-checks the claim's evidence: missing sources exit 5, and a symlink to the live tree exits 1 (path escapes the project
root).

## Review prompts

`candidates.multi_valued_predicates` lists predicates that hold many values, so a differing object alone is no signal; negation and numbers still pair them, so they stay in conflict detection. Set it
in `.kc/config.yaml`; the list replaces the default. When a coordinator reads a decision point whole, `kc group-review <group_id> --reason ... --apply` records it as classified; a later claim reopens
only its own pairs. `decision-points` also returns `word_groups`: claims from different sources sharing a rare subject word, whatever their topic, for agents who worked apart. They share a word, not a
question, so read them after key groups; `candidates.subject_word_floor` and `subject_word_share` set the rarity limit, and `group-review` clears them too. `review` marks a card **Stale** when a
member or the recommendation is no longer live, and `kc report` lists these as `stale_conflicts`.

## Triage

`kc triage` sorts open conflicts into noise (a named gate fired, with its proof), proposed and needs_human, and P0 never clears. A path called gone that the other side still names goes to a person
whatever the banners say. A banner clears a value only when a later source speaks to it. `--apply` records the clearance with rule and run; `--undo <run>` reopens. History rules (`superseded-section`,
`sequential-steps`) record `documented-evolution`: the disagreement is real history, kept and queryable, not noise (research report 5; operator, 2026-11-05). The other rules record `dismissed`. Both
leave the queue, count as cleared in `recall`, and show apart in `kc report`. Until a blind sample of at least 40 clears is 95% right, it is the operator's bulk confirmation, never automatic.
Measured: 92.5%. Audit with `kc sample --status dismissed` (or `--status documented-evolution`).

## Root causes

`kc roots` groups open conflicts by cause, so a shared cause is read once (research B3). A conflict's cause tokens are identifiers (paths, names with a hyphen, dot, underscore or digit) that both
claims name, or that its question or topic names and one claim does. Tokens on more than `roots.max_token_share` of live claims (never fewer than `roots.token_floor`) and document names (file stems, a
numbered head such as `step12`) are dropped. Each conflict joins the group of its most widely shared token, so one bridging conflict cannot chain two causes together. A conflict with no token stands
alone, with a `near` hint when it shares a claim with a group: on the MCP pilot most such joins had another cause. Grouping never changes a status. Each group lists one explicit `kc decide` line per
member, and a person answers each, which keeps INV-007. `review` opens with a **Root causes** list of the groups with more than one member.

## Refuting verifier

`kc verify` tries to show an open conflict is not one before a person reads it (research B4). The verdict words are `conflict`, `not-conflict` (with a kind: `time-evolution`, `superseded-history`,
`different-scope`, `equivalent`, `proposal-vs-observation`, `extraction-error`, `other`) and `uncertain`. "Refuted" is refused because a model read it backwards in the first trial. A `not-conflict`
must quote words of the pair's own claims or excerpts, or it is downgraded to `uncertain`.

- **Agent mode:** `--export` prints tasks (claims, excerpts, document status, root group, instructions); `--export --apply` writes `.kc/verify/batch-NN.json`. The agent answers in
  [schemas/verify-verdict.schema.json](../schemas/verify-verdict.schema.json), then `--file verdicts.json [--verifier name] --apply`.
- **Local model:** `--model <id> [--limit N] --apply` asks an OpenAI-compatible server (oMLX by default, `verify.endpoint`) through `llm.py`, standard library only. The model must be on
  `verify.model_allowlist`, and the endpoint must be loopback unless `verify.allow_remote` is set. The key comes from `KC_LLM_API_KEY` and is never printed. Every run first answers two control pairs
  (one conflict, one dated replacement) and stops if either is wrong. A failed call or an off-vocabulary word is recorded `uncertain`, never "no conflict".
- **Proposal only:** verdicts add a `verify` note to the conflict, which stays open, and the card shows it as **Verifier (proposal only)**. `--confirm <run> --apply` is the operator's bulk
  confirmation. It clears that run's `not-conflict` pairs: `time-evolution` and `superseded-history` as `documented-evolution`, the rest as `dismissed`, each with rule `verify:<kind>`. P0 and
  same-identifier-opposite-status pairs are kept. `kc triage --undo <confirm run> --apply` reverses it. `--score labels.json` compares the notes with judge labels: real conflicts lost, noise cleared,
  precision of what is kept.

## Answering while unresolved

`kc query <text>` returns `settled: false` and the open conflict for a disputed claim, at any severity, and `unreviewed_pairs` for cross-source pairs nobody has classified (a prompt to look, not a
dispute). An agent answers: "Not settled: A says X, B says Y; conflict cf-... awaits a decision", never one side as fact (design 7.9). Superseded and historical claims appear only with `--history`,
marked as such (INV-013).
