Title: Holdout 24 — result analysis, Claude arm
Category: evaluation-record
Status: current
Source: routing-results/holdout24-claude-20260902.{jsonl,log,freeze.txt}
Last reviewed: 20260902_1120
Summary: 16/19 scored passes, 5 runner failures, zero missed gates and 62 over-asserted ones. Gate judgement is the finding; ownership precedence is the second.

# Holdout 24 — result analysis, Claude arm

**Nothing in this document changes an expectation, a catalogue entry, the scorer, the closure module or a case.** The 24 are spent. This is classification.

## Contents

- [What was run](#what-was-run)
- [Headline](#headline)
- [Finding 1 — gate judgement has collapsed to always-true, on every arm, since gates were defined](#finding-1--gate-judgement-has-collapsed-to-always-true-on-every-arm-since-gates-were-defined)
- [Finding 2 — all three genuine failures are ownership, and two cite the precedence table](#finding-2--all-three-genuine-failures-are-ownership-and-two-cite-the-precedence-table)
- [Finding 3 — the runner failed silently on five consecutive cases](#finding-3--the-runner-failed-silently-on-five-consecutive-cases)
- [What this run does and does not license](#what-this-run-does-and-does-not-license)

## What was run

24 blind-authored cases, `--repair` enabled, `claude -p` as the runner, under a freeze verified immediately before launch and captured beside the results: `routing_catalogue ec907ac6af38a61b ·
eval_corpus cb548b83cf203346 · orchestrator 283664a753137a61 · harness 5f15fb18ffed3f3b · closure bdb17d3c8fbd0e7c · holdout_corpus 7470773e7212933d`, git HEAD `1201e42`.

## Headline

| Measure                           | Value                                     |
| --------------------------------- | ----------------------------------------- |
| Scored                            | 19 of 24 — 5 excluded as execution errors |
| Passed                            | **16/19 (84.2%)**                             |
| Mean score                        | 71.1                                      |
| `gate_false_negative`             | **0**                                         |
| `gate_false_positive`             | **62** across 19 cases — 3.3 per case         |
| Cases setting all four gates true | **19 of 19**                                  |

The pass rate lands in the pre-registered strong band. **The pass rate is the least informative number in the table.** Every scored case asserted every gate, so the mean sits at 71.1 rather than ~88
purely on the soft penalty, and the pass rate survives only because over-assertion is soft by design.

## Finding 1 — gate judgement has collapsed to always-true, on every arm, since gates were defined

Re-analysing every stored result set for over-assertion — no model calls, exactly the use [rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) was written to enable:

| Result set  | Model               | Rows | All four gates true | FP  | FN  | FP/row |
| ----------- | ------------------- | ---: | ------------------: | --: | --: | -----: |
| `full`      | pre-gate-definition | 60   | **0**                   | 13  | 41  | 0.22   |
| `baseline2` | deepseek-v4-flash   | 59   | 53                  | 154 | 1   | 2.61   |
| `baseline3` | deepseek-v4-flash   | 60   | 56                  | 162 | 2   | 2.70   |
| `after`     | deepseek-v4-flash   | 60   | 58                  | 167 | 1   | 2.78   |
| `v4`        | deepseek-v4-pro     | 19   | 17                  | 46  | 0   | 2.42   |
| `v4`/`v5`   | claude-code-default | 20   | 20                  | 52  | 0   | 2.60   |
| holdout 24  | claude-opus-5       | 19   | **19**                  | 62  | 0   | 3.30   |

This is not a property of the holdout, of Claude, or of model tier. **Defining the gates on 2026-09-01 converted a systematic false-negative problem into a systematic false-positive one**, and it
stayed invisible for a day because the scorer only penalised one direction. `full` is the before picture: 41 missed gates, almost no over-assertion. Everything after it inverts.

The v4 headline of 79–80% is not wrong, and it is not what it appeared to be: it measured a router that discriminates **ownership and skill selection** well and does not discriminate **gates** at all.
A route that asserts everything can never miss a required gate, and until 2026-09-02 that cost nothing.

Rule 0011 was written on the strength of a single observed case. It found a system-wide constant on first contact.

## Finding 2 — all three genuine failures are ownership, and two cite the precedence table

Zero forbidden selections, zero missing required skills, one team inflation. Every failure is *who owns it*.

| Case                          | Expected         | Chosen       | Class                                                                                                                           |
| ----------------------------- | ---------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `hnet-radius-postmortem`      | devops-hightower | cto-vogels   | **Boundary the table does not cover**: incident root-cause (platform behaviour) vs operational corrective action. Also inflated 3>2 |
| `hnet-firewall-consolidation` | fullstack-dhh    | cto-vogels   | **Underdetermined rule**: `artefact-vs-domain-review` reads both ways when the artefact IS policy                                   |
| `hjdm-workshop-channel`       | sales-ross       | cfo-campbell | **Known ambiguity, pre-registered before the run.** Model cited `research-vs-economics`; classify, do not fix                       |

The second and third are the model applying the precedence table and reaching a different answer from the author, with a stated rationale, not ignoring it. That is a contract question, not a routing
defect. The first is a genuine gap: nothing in the table says whether a post-incident analysis is owned by the platform specialist who explains it or the operator who must prevent it.

## Finding 3 — the runner failed silently on five consecutive cases

The last five invocations exited 1 with **empty stderr and no stdout captured**, so `execution-error:command exited 1:` is the entire diagnostic. Consecutive, at the end of a 24-call sequence, is
consistent with a quota or session limit rather than anything case-specific — but the harness cannot say so, because it records only stderr on a non-zero exit.

The scorer handled it correctly: excluded from both denominators, printed uncorrected figures alongside, per [rule 0008](.archcore/rules/0008-execution-errors-are-not-scores.md). The defect is that a
single-use corpus lost 21% of its cases to a fault the evidence cannot even characterise.

## What this run does and does not license

**Licensed:** recording the result; classifying the failures; treating gate judgement as the top routing question; building runner qualification.

**Not licensed, and not done:** editing any of the 24 cases, the precedence table, the gates, the closure module or the scorer in response to what was observed. The three failing cases stay exactly as
authored. If the ownership boundaries are worth resolving, they are resolved on their own merits and evidenced by the *next* corpus — not by adjusting this one until it agrees.
