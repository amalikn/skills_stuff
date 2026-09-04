Title: Rule 0013 — Trim skill and persona prose against the frozen corpus as a gate, never a scoreboard
Category: durable-rule
Status: accepted
Proposed: 20260904_1145 direct, per .archcore/README.md step 2
Accepted: 20260904_1150 by operator
Source: docs/routing-evaluation/token-optimization-tools-and-strategy.md (Sentry Skills / Prompt Optimizer row, "ADAPT the method, not the tool"; Mem0 row, corrected),
  .archcore/specs/0005-eval-corpus-contract.md, AGENTS.md ("Do not enforce history")
Summary: When compacting a SKILL.md or persona file for token cost, run the existing routing eval against the frozen 60-case corpus before and after as a pass/fail regression gate on hard invariants
  only, and log rounds append-only rather than editing the log in place.

# Rule 0013 — Trim skill and persona prose against the frozen corpus as a gate, never a scoreboard

## Rule

Any edit to a `SKILL.md`, persona file, or `routing.toml` entry made **to reduce token cost** (not to change behaviour) is a candidate for regression, not just savings. Before merging such an edit:

1. Run `just routing-eval-check` (structural) and one behavioural pass — `just routing-eval-local` or `-remote` or `-hermes` — against the default corpus (`evals/routing-cases.toml`, the frozen 60) on
   the pre-edit file.
2. Make the edit.
3. Re-run the same command, same corpus, same limit.
4. Compare **hard invariants only** — required/forbidden personas and skills, decision ownership, gate assertions, team-size limits (per [spec 0005](../specs/0005-eval-corpus-contract.md)). A score
   change with the invariant set unchanged is not a regression. An invariant that flips is.
5. If an invariant flips, the edit cut something load-bearing — restore it or find a shorter phrasing that still carries it. Do not treat a higher score on the frozen 60 as license to cut further;
   spec 0005 already rules that out as fitting the corpus.

This is [getsentry/skills](https://github.com/getsentry/skills)' `prompt-optimizer` meta-optimization loop (baseline → edit → holdout replay → verify no regression on the happy path), adapted: their
loop scores an eval slice, ours gates on invariants because the frozen 60 is explicitly not a scoreboard past 2026-09-02. No external tool is adopted — `evaluate_routing.py` already does this; the
loop is discipline, not new machinery.

## The round log is append-only, not edited in place

Sentry's loop keeps a `Round | Hypothesis | Edit | Result | Keep?` table and says explicitly: "record deletions and compaction edits, not just additions." The naive reading is to prune that table as
rounds get superseded. Don't.

Mem0 dropped its write-time ADD/UPDATE/DELETE conflict resolution in its April 2026 memory algorithm specifically because resolving conflicts at write time cost latency and accuracy for no benefit —
their replacement is single-pass ADD-only extraction, with conflicting or superseded facts resolved at **retrieval time** by multi-signal ranking plus temporal reasoning, measured at +21 to +38 points
across LoCoMo/LongMemEval/BEAM. The old row for Mem0 in the token-optimization doc called this "retrieve-don't-dump" — that description is now stale; the current mechanism is *store everything dated,
don't-dump only shows up at read time*.

That is already this project's own convention: AGENTS.md says "do not enforce history... mark those lines `<!-- count:asat -->` rather than editing the record." Apply the same logic to a trim's round
log — append each round with a date, never rewrite or delete a prior round, and let "most recent round with `Keep: yes`" be the retrieval-time answer, the same way a reader resolves `count:asat` lines
by date rather than by an editor having gone back to update them.

## Where the log lives

The round log for an in-progress trim is SCRATCHPAD material, not `.archcore` material — it carries numbers a re-run moves. Once the trim is settled, promote one line to `CHANGELOG.md` (the outcome,
not the round-by-round path to it) per the existing division of labour in [`.archcore/README.md`](../README.md#division-of-labour-with-memorymd).

## Enforced by

`evaluate_routing.py`'s existing pass/fail on hard invariants (already the mechanism behind rules [0008](0008-execution-errors-are-not-scores.md) and [0011](0011-gate-errors-are-asymmetric.md)) — this
rule adds no new check, it specifies *when* to run the existing one: bracketing any token-cost-motivated edit to routed content.
