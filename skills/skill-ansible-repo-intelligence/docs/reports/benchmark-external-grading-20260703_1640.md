# External Benchmark Grading — Result

Date: 2026-07-03_1640
Repo under test: `/Volumes/Data/_ansible/ansible-wifi` (94 roles)
Method: `tests/benchmark/RUNBOOK.md` — two isolated agent sessions + blind grader.

## How it was run (isolation satisfied)

Three independent subagent contexts, per the RUNBOOK's "same session must not
execute and grade both sides" rule:

- **Baseline** — a fresh agent answering 22 questions with ordinary repo search
  only; no `.ai-context`, no `ansible-repo-intelligence` CLI.
- **Indexed** — a separate fresh agent using `ANSIBLE_REPO_MAP.md` + bounded
  `query`/`explain`/`impact`, opening only pointed-to source.
- **Blind grader** — a third agent, not told which run was which (labelled
  Run X / Run Y). It read the gold source files to establish ground truth, then
  scored correctness and counted unsupported claims.

Same model/tooling/repo revision for both answer runs. 22-question gold set:
`tests/benchmark/questions.ansible_wifi.yaml`.

## Result (honest scorecard)

| Metric | Baseline | Indexed | Target | Met? |
|---|---|---|---|---|
| source files opened | 36 | 29 | ≥60% fewer | **NO** — 19% fewer |
| input tokens | 79.1k | 85.4k | ≥40% lower | **NO** — +8% |
| answer correctness (blind) | 22/22 | 21/22 | no reduction | **NO** — −1 (marginal) |
| unsupported claims (blind) | 0 | 1 | no increase | **NO** — +1 (marginal) |
| retrieval recall (harness, deterministic) | 95.5% | 100% | ≥95% | YES |

The single indexed error (q05): claimed Asterisk is installed "from packages"
when `smc_asterisk` compiles it from source. One material miss out of 22; within
noise, but it is a real regression, not a pass.

## Verdict: NOT READY by benchmark (thresholds not met)

The efficiency thesis **holds against naive keyword search** (the harness's
grep proxy: 96.7% fewer files, 100% recall) but **does not hold against a
capable LLM agent** on this repo. Cause:

1. **Files opened** — a strong agent navigates straight to the right role
   (36 files) rather than grepping thousands, so the index's file-reduction edge
   shrinks from ~97% (vs naive grep) to ~19% (vs a smart agent).
2. **Tokens** — the CLI query overhead (reading the map + 33 tool calls) cost
   *more* tokens than the baseline's direct file reads (+8%).
3. **Correctness/claims** — statistically flat; the indexed run was marginally
   worse (21 vs 22, 1 vs 0), not better.

## What this means (do not overclaim)

- The prior "96.7% fewer files / 100% recall" figures are a **naive-search
  proxy**, not evidence of a win over a competent agent. Documentation that
  cited them as the efficiency result has been corrected to say so.
- On this repo, for a strong model with good code-navigation tools, the indexed
  workflow did **not** pay for itself.
- Where the tool is still likely to help (not measured here, stated as
  hypotheses): weaker/smaller models that navigate less efficiently;
  repository-wide audits; and relationship questions ordinary grep answers
  poorly (handler notify chains, blast-radius `impact`, `explain`) — these were
  under-represented in this question set (mostly "how is X configured", which
  favours direct role lookup).

## Recommended next steps

1. Do **not** promote to Regular Skills on efficiency grounds alone.
2. Re-scope the benchmark toward the tool's genuine differentiators
   (handler-chain / impact / cross-flavor questions) and re-run.
3. Optionally test with a smaller model as the answer agent, where index
   navigation should help more.
4. Keep the tool as strong deterministic **navigation + relationship
   intelligence** (its verified strengths), not as a token-savings claim.
