Title: Rule 0008 — An execution error is not a routing score
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: scripts/evaluate_routing.py
Summary: Infrastructure faults are excluded from pass rate and mean, counted separately, with the uncorrected figure printed alongside.

# Rule 0008 — An execution error is not a routing score

## Rule

A mis-invoked CLI, a transport failure, a timeout or an unparsed reply is an **infrastructure fault**. It is excluded from the denominators, counted separately,
and the uncorrected figure is printed beside the corrected one so published numbers stay reconcilable.

## Measured cost of getting it wrong

A single 300-second timeout made one model read **77.8 mean against another's 80.8 (worse)** uncorrected, and **81.8 against 80.8 (better)** once excluded. One
timeout inverted the sign of the comparison. A separate parse flake cost an earlier baseline 1.4 points of mean and a case of pass rate.
