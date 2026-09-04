Title: Spec 0007 — Gate-only evaluation and precision/recall scoring
Category: design-contract
Status: accepted
Proposed: 20260902_1210 direct, per .archcore/README.md step 2
Accepted: 20260904_1150 by operator
Source: docs/routing-evaluation/holdout24-analysis-20260902_1120.md, MEMORY.md
Summary: Measure gate classification in isolation from route construction, score it as precision and recall rather than as pass/fail, against thresholds pre-registered before the first run.
# Spec 0007 — Gate-only evaluation and precision/recall scoring

## Contents

- [The question this answers](#the-question-this-answers)
- [Design — three measurements, one corpus](#design-three-measurements-one-corpus)
- [What the three measurements localise](#what-the-three-measurements-localise)
- [Scoring: precision and recall, not pass/fail](#scoring-precision-and-recall-not-passfail)
- [Corpus](#corpus)
- [Pre-registered thresholds — recorded 20260902_1225, BEFORE any run](#pre-registered-thresholds-recorded-20260902_1225-before-any-run)
- [Sequencing — runner qualification comes first](#sequencing-runner-qualification-comes-first)
- [What a result licenses](#what-a-result-licenses)
- [Not licensed](#not-licensed)

---

## The question this answers

Every scored route in holdout 24 set all four gates true, and 53–58 of 60 did the same in every stored run since the gates were defined. What is unknown is **where in the pipeline that happens**. Two
candidate causes produce identical output today:

| Hypothesis       | Claim                                                                                                                       | Distinguishing prediction                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **Gate semantics** | The gate definitions or their catalogue prose make "true" the defensible answer for almost any task                         | Gate-only classification is ALSO all-true           |
| **Instruction load** | Gate judgement is fine in isolation and degrades when judged jointly with ownership, skills, closure and an invariant       | Gate-only classification is good; integrated is not |
|                  |   to walk                                                                                                                   |                                                     |

The current harness cannot separate them, because it only ever observes gates as a by-product of a full route.

## Design — three measurements, one corpus

**A — gate-only.** Task in, three booleans out. No personas, no skills, no owner, no closure, no invariant paragraph. The prompt carries the task, the `[[gates]]` definitions, and nothing else that
implies a team.

```json
{"research_required": false, "critic_required": true, "qa_required": false, "reason": "..."}
```

`runtime_required` is excluded by construction: it is computed from the selected skills and there are no skills in this stage. Asking for it would measure a guess at a value the system never wants.

**B1 — route with the model's own gates.** A's output supplied as fact; the model routes owner, personas and skills against it; deterministic closure runs as normal. This is the production pipeline,
split in two.

**B2 — route with ground-truth gates.** The same, but the CORPUS's gate labels are supplied instead of A's. This is the counterfactual the current harness can never produce: how well does the router
route when gate judgement is simply correct?

A, B1 and B2 use the same corpus and the same scorer, and each stamps its own provenance and its own row in the run index.

## What the three measurements localise

| Result                       | Meaning                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| A poor                       | Gate definitions, their prose, or model classification. Fix the definitions                                             |
| A good · B1 poor · B2 good   | Integration / multi-task instruction load. The two-stage split becomes a candidate architecture, not just an instrument |
| A good · B1 and B2 both poor | Routing, ownership or skill selection — not gates                                                                       |
| B2 materially better than B1 | Gate judgement is contaminating otherwise-good routing                                                                  |
| B1 ≈ B2                      | Gate errors are not the dominant downstream problem, whatever A says                                                    |

The last row deserves stating plainly in advance: it is entirely possible that gate over-assertion is real, measurable, ugly — and costs the route almost nothing downstream, because closure satisfies
whatever was asserted. If B1 ≈ B2, the finding is recalibrated from "the top routing question" to "a precision defect with no downstream cost", and the queue changes accordingly.

## Scoring: precision and recall, not pass/fail

Pass/fail is the wrong instrument for a classifier. Report, per gate and in aggregate over the judged three:

| Metric      | Definition     | What it catches                                                                     |
| ----------- | -------------- | ----------------------------------------------------------------------------------- |
| **Recall**  | TP / (TP + FN) | Missed obligations. Today's routers score ~1.0 and that number is meaningless alone |
| **Precision** | TP / (TP + FP) | Over-assertion. **This is the number the project has never measured**               |
| **F1**      | harmonic mean  | The single figure that cannot be gamed by answering always-true or always-false     |
| **Specificity** | TN / (TN + FP) | Performance on the 13-of-24 cases where the right answer is "no gate"               |

A router answering always-true scores recall 1.0, precision ≈ 0.25 and F1 ≈ 0.40. A router answering always-false scores recall 0.0 and F1 0.0. **Only a discriminating classifier scores well on F1**,
which is exactly the property pass/fail lacked and why the collapse survived four baselines.

Report the confusion matrix per gate. Aggregate F1 hides a classifier that is good at two gates and constant on a third — and `qa_required` (18 FP in holdout
24) and `critic_required` (17 FP) are the two most likely to be constant.


### The anti-degeneracy check: predicted-positive rate

Report **predicted-positive rate** per gate — the share of cases answered `true` — beside the base rate the corpus carries. It is the one number class imbalance cannot flatter, and it exposes an
always-true, always-false or near-constant classifier at a glance even when another metric looks acceptable. On holdout 24 the predicted-positive rate was **1.00 on all four gates**. Any run where it
sits within a few points of 0 or 1 is degenerate, and its other metrics are not worth reading.

## Corpus

**Not the spent 24, and not a new blind corpus.** Gate-only classification is cheap and needs many labelled examples, so run it against the **frozen development 60**, whose gate labels are already
authored and stable. Fitting risk is low: this measures a classifier the project has never tuned, and no gate definition may be changed on the strength of a development-corpus result without
confirming it on the next holdout.

## Pre-registered thresholds — recorded 20260902_1225, BEFORE any run

Registered in advance so the bar cannot move to meet the result. The exact values matter less than their being fixed first; they are set where a classifier is genuinely useful, not where this system
is expected to land.

| Metric                    | Threshold                                  |
| ------------------------- | -----------------------------------------: |
| Per-gate recall           | >= 0.80                                    |
| Per-gate precision        | >= 0.75                                    |
| Per-gate specificity      | >= 0.80                                    |
| Macro F1 across the three | >= 0.78                                    |
| Predicted-positive rate   | strictly inside (0.05, 0.95) on every gate |

A predicted-positive rate outside that interval means the classifier is degenerate and **the run fails regardless of the other four metrics**.

**A gate missing ANY threshold fails, and a failing gate fails the measurement** — no aggregate may rescue it, because aggregate F1 is precisely what would hide a classifier that discriminates two
gates and is constant on a third. `qa_required` (18 false positives in holdout 24) and `critic_required` (17) are the two most likely to be constant.

Moving a threshold after seeing a result is permitted only as an explicit, dated, reasoned amendment to this spec, recorded before the next run. Silently relaxing one is the failure this section
exists to prevent.

## Sequencing — runner qualification comes first

**[Spec 0006](0006-runner-qualification.md) qualification precedes this experiment**, even though the development 60 is not unseen evidence and cannot be spent. Runner instability does not merely lose
cases here: an execution error is excluded from the denominators, so an unstable runner silently changes WHICH cases precision and recall are computed over. A metric computed on a shifting subset
needs an interpretive layer that a pre-registered threshold cannot survive. Qualify first, then measure.

## What a result licenses

- **Gate-only is also all-true** → the defect is in the gate semantics or their prose. Fix the definitions, not the prompt. Re-measure gate-only before touching the integrated route.
- **Gate-only is good, integrated is all-true** → the defect is instruction load. The two-stage split is then not merely an instrument but a candidate architecture, and it should be evaluated as one.
- **Both are good on the 60** → the holdout's constant is corpus-specific and the finding narrows sharply. Least likely, given `full` versus everything after it.

## Not licensed

Changing any gate definition, prompt rule or case on the strength of this experiment alone. It is a diagnostic. It says where to look, and the fix is evidenced on the next unseen corpus, per [plan
0003](../plans/0003-holdout-two-protocol.md).
