Title: Rule 0007 — Capability annotations describe what a provider does
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: MEMORY.md
Summary: Never relabel a provider to make a case pass; the strength distinction is what a relabel destroys.

# Rule 0007 — Capability annotations describe what a provider does

## Rule

Every capability claim describes what the skill or persona **genuinely does** — never what would raise a score.

## The test that was actually applied

All 22 unsatisfied-gate failures were checked against this before any catalogue edit, and **none** was relabelled: `financial-unit-economics` acquires no external
evidence and challenges no conclusion; `deep-analysis` analyses what is already present; `security-audit` and `senior-qa` are validation rather than challenge;
`devops` release checks are incidental.

Relabelling any of them would have raised the score and destroyed the `analysis != independent challenge` invariant that the critic gate rests on.
