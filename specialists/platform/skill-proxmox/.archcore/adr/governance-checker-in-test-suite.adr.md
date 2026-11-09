---
title: Governance checker runs inside the test suite
type: adr
status: accepted
tags: [governance, tests]
created: 2026-11-07
---

# ADR: Governance checker runs inside the test suite

Status: accepted (operator, 2026-11-09, after the archcore review that corrected it). Carried over from skill-nautobot, where the operator accepted it on 2026-10-05.

## Context

The package contract (`tests/test_package_contract.py`) requires every `scripts/*.py` to be stdlib-only and named in `tests/test_helpers.py`,
so the governance checker cannot sit in `scripts/` untested.

## Decision

`tests/test_helpers.py` runs the checker as a subprocess (`Governance.test_governance_claims_hold`) and proves on a copy of the pack that it
can fail: a broken reference (`Governance.test_a_broken_reference_fails_the_gate`) and a restated release version
(`Governance.test_a_restated_version_fails_the_gate`, added 2026-11-09). `just test` is the single completion gate; `just check` runs the
checker alone, with the skill-ai-it doc-freshness and role checks.

## Consequences

- A governance drift (an uncataloged helper, an unrouted reference, a stale path, a restated version) turns the pack's tests red.
- Work that adds a helper is red until it is catalogued in `scripts/README.md`; that is intended.
- Each new check family gets a test that breaks a copy of the pack and expects red, so no check scans an empty set unnoticed.

Confidence: high; both tests ran red on a broken copy before the gate was trusted (2026-11-07 and 2026-11-09).
