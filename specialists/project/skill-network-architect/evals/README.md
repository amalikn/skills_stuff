---
Title: Behavioral eval protocol
Category: eval-guide
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Behavioral eval protocol.
---

# Behavioral eval protocol

## Purpose and execution
These are review scenarios, not an automated assertion that a model is correct.
Use [cases.json](cases.json) as the prompt set. Give the model the skill, the request and only the named raw evidence.
Run in a fresh context when testing discovery or application, with no production access and no actual changes.
Keep a transcript and artifact revisions. Read [rubric](rubric.md) only when grading; do not leak expected answers into the task prompt.
Run cases relevant to a changed module plus negative trigger tests. Use both hosts when validating actual host compatibility.

## Stages
1. Without-skill baseline: record actual response and omissions; a correct baseline is a finding, not a failed test to invent.
2. With-skill application: run the same request and assess decisions, references used and evidence distinctions.
3. Variation: alter an important premise or supply missing evidence; check the conclusion changes appropriately.
4. Pressure: add urgency, sunk cost or preferred vendor pressure; check scoped execution and honest limitations.
5. Regression: rerun affected cases after revisions, recording model/host/context and date.

## Trigger checks
Expected positive: a request to design/review/migrate this domain or diagnose a cross-layer architecture issue.
Expected cross-domain: networked storage, clustered hosts, identity dependencies or site recovery should invite peer review.
Expected negative: writing marketing copy, a pure algorithm implementation, arbitrary draw.io layout or a product-only API field lookup.
For a product-only task, prefer the corresponding specialist; call the architect back only for a domain decision.
Manual review cannot prove automatic host selection; record live discovery separately.

## Limits and records
[results.md](results.md) distinguishes authored cases, executed cases and untested environments.
Static checks, unit tests and a few agent responses cannot certify the full domain breadth or every model.
No paid API, cloud harness or automatic external orchestration is required to use this suite.
