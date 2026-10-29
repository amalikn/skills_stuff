---
Title: Behavioral scoring rubric
Category: eval-rubric
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Behavioral scoring rubric.
---

# Behavioral scoring rubric

Score each criterion 0 (missing/wrong), 1 (partial) or 2 (explicit and correct), maximum 16.
- Scope: identifies service objective, limits and owner.
- Evidence: preserves timestamps/versions/provenance and unknowns.
- Domain reasoning: correct mechanism, units and relevant failure modes.
- Trade-offs: compares viable options without vendor/tool foundation.
- Interfaces: identifies peer/specialist ownership and return contract.
- Automation: bounded execution, uncertain-outcome reconciliation and recovery where applicable.
- Validation: measurable acceptance with actual/estimated/planned distinctions.
- Operability: ownership, lifecycle, cost/effort and recoverability proportionate to task.

Suggested local acceptance: at least 12/16 and zero critical failures. This threshold is authored for the pack, not a universal standard.
Do not award a criterion merely for mentioning a keyword; tie it to a concrete decision or artifact.
Any case-specific critical failure in cases.json fails the case regardless of aggregate score.
Record not-applicable criteria explicitly and normalize to applicable points; do not inflate scores by giving irrelevant boilerplate credit.
Retain exact excerpts supporting a finding. Quantitative cases have independent arithmetic oracles in the offline tests.
