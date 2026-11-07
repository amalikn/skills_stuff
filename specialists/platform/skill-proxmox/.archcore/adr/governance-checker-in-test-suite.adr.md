---
title: Governance checker runs inside the test suite
type: adr
status: proposed
tags: [governance, tests]
created: 2026-11-07
---

# ADR: Governance checker runs inside the test suite

Status: proposed (2026-11-07; carried over from skill-nautobot, where the operator accepted it on 2026-10-05)

## Context

The package contract (`tests/test_package_contract.py`) requires every `scripts/*.py` to be stdlib-only and named in `tests/test_helpers.py`,
so the governance checker cannot sit in `scripts/` untested.

## Decision

`tests/test_helpers.py` runs the checker as a subprocess (`Governance.test_governance_claims_hold`) and proves it can fail on a copy of the
pack with a broken reference (`Governance.test_a_broken_reference_fails_the_gate`). `just test` is the single completion gate; `just check`
runs the checker alone.

## Consequences

- A governance drift (an uncataloged helper, an unrouted reference, a stale path) turns the pack's tests red.
- Work that adds a helper is red until it is catalogued in `scripts/README.md`; that is intended.

Confidence: medium, as in skill-nautobot.
