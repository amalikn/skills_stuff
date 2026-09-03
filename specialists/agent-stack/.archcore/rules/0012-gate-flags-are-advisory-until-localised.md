Title: Rule 0012 — Gate flags are advisory until the collapse is localised
Category: durable-rule
Status: proposed
Proposed: 20260902_1310 direct, per .archcore/README.md step 2
Source: docs/holdout24-analysis-20260902_1120.md, MEMORY.md
Summary: In real project use, treat research/critic/qa flags as noisy advice, never as authority to expand the team. Owner and skill selection remain trustworthy.

# Rule 0012 — Gate flags are advisory until the collapse is localised

## Rule

For **real project use**, until [spec 0007](../specs/0007-gate-only-evaluation.md) localises the gate collapse:

| Signal                                                | Standing                                               |
| ----------------------------------------------------- | ------------------------------------------------------ |
| `primary_owner`, `personas`, `skills`                 | **Trustworthy.** 84% on unseen cases, zero forbidden picks |
| `research_required`, `critic_required`, `qa_required` | **Advisory and noisy.** Not authority for anything         |
| `runtime_required`                                    | Computed, not judged — unaffected                      |

**When the gate set comes back broad or all-true:**

1. Do **not** expand the team from the gates alone.
2. Preserve the model-selected owner and skills — that is the part with evidence behind it.
3. Require human review before any gate-driven addition to the route.

## Why an always-true flag is worse than no flag

A flag that is always set carries no information, and it is not harmlessly cautious: it converts every task into the full apparatus — a researcher, a critic and a QA capability on a one-line refactor.
The cost is tokens, latency and a team larger than the work, and the second-order cost is worse: an operator who sees `critic_required = true` on everything stops reading it, including on the
irreversible decision where it was the point.

Measured, holdout 24: predicted-positive rate **1.00 on all four gates**, against corpus base rates of 0.32 / 0.21 / 0.05 / 0.32.

## This rule is policy first and code second, deliberately

The natural implementation — a degenerate-gate-set check inside route closure, or a paragraph in the orchestrator skill — edits a **stamped input** to the very experiment meant to localise this
defect. Changing team-expansion behaviour immediately before measuring team-expansion behaviour would make B1 and B2 uninterpretable and invalidate the freeze.

So the guard binds operators now and reaches the code after A/B1/B2 reports. If that experiment finds `B1 ≈ B2` — over-assertion real but costing the route nothing downstream — the code change may
prove unnecessary, and this rule narrows to advice rather than becoming a mechanism.

## Release blockers this rule stands in for

1. Gate discrimination must either work, or the gates concerned must become explicitly deterministic.
2. Runner qualification must pass, followed by a second clean unseen holdout.

Until both clear: **ready for controlled use by the operator, not justified for unattended or broad trust.**
