Title: Gate-only evaluation — A / B1 / B2 result
Category: evaluation-record
Status: current
Source: routing-results/gate-only-{A,B1,B2}-flash-20260902.json, gate-only-A-claude-20260902.json
Last reviewed: 20260903_0030
Summary: Isolated gate judgement is a real classifier on two arms; integrated it is a constant. The collapse costs routing nothing, because its error type is the harmless one.

# Gate-only evaluation — A / B1 / B2 result

Run under [spec 0007](../.archcore/specs/0007-gate-only-evaluation.md), against the frozen development 60, on DeepSeek Flash via Hermes, with a realistic-payload runner qualification passed
immediately beforehand. Thresholds were pre-registered on 20260902_1225 and are not moved here.

## Contents

- [Stage A — can the model judge gates at all?](#stage-a--can-the-model-judge-gates-at-all)
- [B1 vs B2 — does getting them wrong cost anything?](#b1-vs-b2--does-getting-them-wrong-cost-anything)
- [The conditional breakdown, which reverses the aggregate reading](#the-conditional-breakdown-which-reverses-the-aggregate-reading)
- [What this settles](#what-this-settles)
- [What it does not settle](#what-it-does-not-settle)

## Stage A — can the model judge gates at all?

| Arm                            | research PPR / base | critic PPR / base | qa PPR / base | macro F1 | Verdict         |
| ------------------------------ | ------------------- | ----------------- | ------------- | -------: | --------------- |
| deepseek-v4-flash              | 0.48 / 0.50         | 0.37 / 0.37       | 0.20 / 0.22   | 0.738    | FAIL thresholds |
| claude-opus-5                  | 0.37 / 0.50         | 0.53 / 0.37       | 0.38 / 0.22   | 0.782    | FAIL thresholds |
| **integrated router (holdout 24)** | **1.00**                | **1.00**              | **1.00**          | —        | **degenerate**      |

Both arms fail the pre-registered bar, and both are **non-degenerate**: predicted-positive rate tracks the corpus base rate instead of pinning at 1.00. Flash tracks it almost exactly.

**The gate-semantics hypothesis is dead.** The definitions are learnable — a model handed them alone produces a genuine, if mediocre, classification. Something about judging them *while* constructing
a route destroys the signal. That is instruction load, and it replicates across two model tiers.

Flash scores lower than Claude on F1 while being better calibrated on PPR. Aggregate quality and degeneracy are orthogonal properties, which is why both were pre-registered.

## B1 vs B2 — does getting them wrong cost anything?

Paired, all 60 cases scored in both stages, same arm, same freeze, same qualification.

| Stage                               | Passed        | Mean  |
| ----------------------------------- | ------------- | ----: |
| B1 — route on the model's own gates | 37/60 (61.7%) | 80.74 |
| B2 — route on ground-truth gates    | 46/60 (76.7%) | 86.11 |
| **delta**                               | **+9 cases**      | **+5.38** |

Taken alone this says gate errors contaminate routing badly. Taken alone it is **wrong**.

## The conditional breakdown, which reverses the aggregate reading

Split the same 60 by whether stage A got that case's gates right, and by WHICH kind of error it made:

| Stage-A gates           | n   | B1 failure rate |
| ----------------------- | --: | --------------: |
| Correct                 | 36  | 17% ← baseline  |
| **FP only** — over-asserted | 10  | **30%**             |
| **FN only** — missed a gate | 11  | **100%**            |
| Both                    | 3   | **100%**            |

And where A was correct, B1 and B2 are indistinguishable: **30/36 versus 29/36**, mean 86.6 versus 86.9. The entire +9 comes from the 24 cases A got wrong, and within those, from the false negatives.
`missing gate` hard failures: **B1 17, B2 1**.

**Over-assertion is not detectably costly. Under-assertion is fatal, 14 of 14.**

Production makes only the harmless error. The integrated router asserts everything, so its recall is ~1.0 and it has zero false negatives by construction. For production's actual error profile this is
the **B1 ≈ B2** row of spec 0007's matrix, reached conditionally rather than in aggregate — the +9 is an artifact of stage A introducing an error type production does not make.

## What this settles

- **The gate collapse is real, measurable, and is not costing routing accuracy.** Its costs are the ones [rule 0012](../.archcore/rules/0012-gate-flags-are-advisory-until-localised.md) already named:
  tokens, oversized teams, and a signal that has gone dead for the operator.
- **It drops down the queue.** Ahead of it now: replay and shadow-mode evidence, and Holdout 2.
- **The naive fix is dangerous and must not be attempted.** "Make the router less trigger-happy" trades precision for recall — trading a free error for a fatal one. Any future work on gate calibration
  must hold recall at 1.0 and buy precision only where it costs no recall.
- **[Rule 0011](../.archcore/rules/0011-gate-errors-are-asymmetric.md) is independently confirmed.** Its −20 hard / −5 soft asymmetry was chosen on judgement before any of this was measured. The
  measured downstream cost ratio is 100%-failure versus indistinguishable-from-baseline. The asymmetry we picked matches the asymmetry that exists.

## What it does not settle

- **Whether over-assertion is truly free, or merely cheap at n=10.** 30% against a 17% baseline is not a signal at that sample size, and it is not a demonstration of zero effect either.
- **Whether the two-stage architecture is worth building.** It is a good instrument. As a production architecture it would have to beat integrated routing on the error profile production actually has,
  and this experiment did not test that: B1 routed on gates that were wrong in a way production's never are.
- **Anything about ownership.** B1 and B2 both carry ~10 `missing required persona` failures, unchanged between them. That is a separate defect and this experiment says nothing new about it.
