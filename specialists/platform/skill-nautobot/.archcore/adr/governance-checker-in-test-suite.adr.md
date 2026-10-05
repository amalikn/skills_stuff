---
title: Governance checker runs inside the test suite
type: adr
status: accepted
tags: [governance, tests]
created: 2026-10-05
---

# ADR: Governance checker runs inside the test suite

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Recent decisions).

## Context

The skill-ai-it bootstrap (2026-10-05) added `scripts/check_governance.py`. The package contract (`tests/test_package_contract.py`) requires every `scripts/*.py` to be stdlib-only and named in
`tests/test_helpers.py`, so the checker could not sit in `scripts/` untested.

## Decision

`tests/test_helpers.py` runs the checker as a subprocess (`Governance.test_governance_claims_hold`) and proves it can fail on a copy of the pack with a broken reference
(`Governance.test_a_broken_reference_fails_the_gate`). `just test` is therefore the single completion gate; `just check` runs the checker alone.

## Consequences

- A governance drift (an uncataloged helper, an unrouted reference, a stale path) turns the pack's tests red, not just a side command.
- Trade-off: work that adds a helper is red until it is cataloged in `scripts/README.md`. Observed on 2026-10-05 while a parallel session added helpers; this is the intended behaviour.

Confidence: medium — new; revisit if the coupling blocks legitimate in-progress work more than it catches drift.
