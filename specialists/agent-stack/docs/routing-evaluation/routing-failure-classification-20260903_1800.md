Title: Production-shape failures — full classification of all 27
Category: evaluation-record
Status: current
Source: routing-results/prodshape-norepair-flash-20260903.jsonl
Last reviewed: 20260903_1800
Summary: What "fix it all" can and cannot honestly mean. 20 of 27 are already fixed; 2 boundaries fixed from holdout evidence; the rest is either an open contract decision or corpus-fitting the
  project forbids.

# Production-shape failures — full classification

The 20260903 production-shape run scored **30/60** with **27 hard failures across 18 cases**. This classifies every one, because "fix it all" has three very different answers depending on the class,
and only one of them is engineering.

## Contents

- [Class 1 — already fixed (20 failures)](#class-1-already-fixed-20-failures)
- [Class 2 — fixed here, from holdout evidence (2 cases)](#class-2-fixed-here-from-holdout-evidence-2-cases)
- [Class 3 — an open contract decision (10 corpus cases)](#class-3-an-open-contract-decision-10-corpus-cases)
- [Class 4 — router limitation, not fixable by editing anything](#class-4-router-limitation-not-fixable-by-editing-anything)
- [What was deliberately not done](#what-was-deliberately-not-done)
## Class 1 — already fixed (20 failures)

`gate_unsatisfied` 18 and `strength_insufficient` 2. Every one is "the route asserted a gate and equipped nothing declaring that capability": 9 research, 8 independent-challenge, 1 validation. **This
is exactly and only what `scripts/close_route.py` repairs**, and it was wired into the skill earlier the same day. They cannot recur in production. Nothing further to do.

## Class 2 — fixed here, from holdout evidence (2 cases)

Two ownership boundaries the precedence table did not cover. **Both are evidenced by the SPENT HOLDOUT, not by the development corpus**, which is what makes fixing them legitimate under [spec
0008](../../.archcore/specs/0008-replay-corpus-contract.md) rather than corpus-fitting.

| New rule                             | Boundary                                                                                        | Holdout case                  |
| ------------------------------------ | ----------------------------------------------------------------------------------------------- | ----------------------------- |
| `incident-explanation-vs-correction` | post-incident: explanation (CTO) vs corrective action (DevOps)                                  | `hnet-radius-postmortem`      |
| `policy-as-artefact`                 | the artefact IS the policy: posture decision (CTO) vs program over settled posture (Full-Stack) | `hnet-firewall-consolidation` |

In both, the model **cited the existing rule and reached the other answer with a stated rationale** — the signature of an underdetermined rule rather than a bad route.

## Class 3 — an open contract decision (10 corpus cases)

A mechanical test over the **whole** corpus, not just the failures: *does a case require a non-owner persona that is some gate's `default_persona`, on a case asserting that gate?* Ten cases do — and
**three of them currently pass**, which is the evidence that this was found by rule rather than by score.

```
infra-cicd-rollout · network-migration-go-no-go · repo-architecture-audit · frontend-workflow   -> qa-bach
jdm-landed-cost · jdm-go-no-go-car · atar-landed-cost · generic-import-pilot · ambiguous-best-nas -> research-thompson
weak-evidence-go-no-go                                                                          -> critic-munger
```

[Rule 0006](../../.archcore/rules/0006-required-personas-is-ownership.md) says `required_personas` means mandatory ownership or independent judgement, never an ideal team. But **the corpus has no `tags`
field**, so tag-driven escalation — the mechanism that legitimately makes a gate's persona mandatory — cannot be expressed, and it has been encoded in `required_personas` instead. Some of these are
therefore *correct in intent*: `weak-evidence-go-no-go` is literally thin-evidence-high-commitment, and `network-migration-go-no-go` is literally go-no-go, both of which are escalation tags.

**This is the decision left open on 2026-09-02** — author tags per case, or relax the assertions — and it is the operator's, because it edits a frozen corpus and because rule 0006 forbids deriving
tags from `required_personas`, which is the tempting shortcut. **Not done here.**

## Class 4 — router limitation, not fixable by editing anything

The router names the right owner and then under-equips: `atar-pricing` misses `financial-unit-economics` on a task that says "unit economics"; `ui-only` misses `frontend-design`; `release-readiness`
misses `senior-qa`; `atar-positioning` misses `content-strategy`; `infra-cicd-rollout` misses `devops`.

**Discoverability was checked and is not the cause.** The catalogue already carries the matching intents — `financial-unit-economics` declares `unit-economics` and `landed-cost`, `devops` declares
`cicd`. The skills are findable; the router does not select them.

Improving this by changing the catalogue or the corpus until these pass **is corpus-fitting**, which [spec 0005](../../.archcore/specs/0005-eval-corpus-contract.md) exists to forbid: past the freeze, a
better score on these 60 is evidence of fitting the corpus rather than of better routing. The legitimate path is a change justified on its own merits and confirmed on the NEXT unseen corpus.

Two ownership disagreements sit here too: `business-model` (CFO vs CEO) and `generic-import-pilot` (Research vs Operations). And two research cases returned **no owner at all** — which is notable,
because the spent holdout's `hdirect-competitor-pricing-scan` asserted the opposite: that a narrow evidence task legitimately routes to a skill with no persona. The corpus and the holdout disagree
about the same question.

## What was deliberately not done

- **No corpus assertion was relaxed to make a case pass.** Class 3 is recorded as a decision, not executed as a fix.
- **No catalogue description was tuned toward the failing cases.** Class 4's skills are already discoverable; the miss is the router's.
- **The two precedence rules added are evidenced by unseen holdout data**, not by these 60. They will be confirmed or refuted on the next unseen corpus, per spec 0008 — a rule added from evidence
  still has to survive contact with new evidence.
