Title: Rule 0011 — Gate errors are asymmetric
Category: durable-rule
Status: accepted
Proposed: 20260902_0930 direct, per .archcore/README.md step 2
Accepted: 20260902_0950 by operator
Source: scripts/evaluate_routing.py
Summary: A missing gate is a hard failure worth -20 and decides pass/fail; an unnecessary gate is a soft -5 that never does. Both classes are counted and stored
separately.

# Rule 0011 — Gate errors are asymmetric

## Rule

The two ways a route can get a gate wrong are **not the same defect** and are never scored as though they were.

| Case says | Route says | Class                 | Cost      | Decides pass/fail |
| --------- | ---------- | --------------------- | --------- | ----------------- |
| `true`    | `false`    | `gate_false_negative` | -20, hard | Yes               |
| `false`   | `true`     | `gate_false_positive` | -5, soft  | No                |

A false negative is an **omitted obligation** — the case requires the gate and the route does not carry it. A false positive is **over-routing** — wasteful, but
the work still gets done. Both counts are stored per case in every result row and totalled in the run summary, so any stored baseline can be re-analysed for
over-assertion without calling a model again.

`runtime_required` is scored against the computed value in both directions, so only the three judged gates can be over-asserted.

## Why neither extreme works

**Zero cost for over-assertion is a gaming hole.** That is what the scorer did until 2026-09-02: setting all four flags true could never lose a point and won
one on every case with a required gate. Claude did exactly this on `market-size` in Baseline v4 and paid nothing. Any holdout scored under that rule measures
how willing a model is to assert, not whether it routes well.

**Equal cost is the opposite error.** It makes a cautious route that fires a spare gate indistinguishable from one that skipped a required one, which inverts
the safety property the gates exist to provide.

## Consequence for measurement

A baseline measured under the old scorer is not comparable to one measured under this rule for any case where a route over-asserted. Compare stored rows by
re-scoring them (`--rescore`), never by putting the two published means side by side.
