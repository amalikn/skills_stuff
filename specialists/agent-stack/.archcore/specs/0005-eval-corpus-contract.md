Title: Spec 0005 — Routing eval corpus contract
Category: design-contract
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ROUTING_EVALS.md, evals/routing-cases.toml
Summary: Hard invariants decide pass/fail; preferred selections affect the diagnostic score only. The 60-case set is frozen as a development corpus.

# Spec 0005 — Routing eval corpus contract

## Contract

Hard invariants — required/forbidden personas and skills, decision ownership, gate assertions and team-size limits — determine pass/fail. Preferred selections
affect the diagnostic score only.

`runtime_required` must be **earned**: it is computed from the selected skills, so a case asserting it must also require a tool-class skill. Asserting the flag
while only *preferring* the skill that causes it is a case contradicting itself.

## The 60 are frozen

The development corpus is frozen as of 2026-09-02. Past this point a better score on these 60 is evidence of fitting the corpus rather than of better routing.
Add a case only to cover a **new** routing concept. The next evidence comes from an unseen holdout and real-task replay.
