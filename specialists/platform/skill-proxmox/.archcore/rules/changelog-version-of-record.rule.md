---
title: CHANGELOG release heading is the version of record
type: rule
status: accepted
tags: [versioning, governance]
created: 2026-11-07
---

# Rule: CHANGELOG release heading is the version of record

Status: accepted (operator, 2026-11-09, after the archcore review that corrected it). Same rule as skill-nautobot.

## Rule

The pack version is the newest release heading in `CHANGELOG.md` (`## x.y.z — date`). No other pack file restates it. Unreleased work,
including every write-back line, goes under `## Unreleased` until release reconciliation (`references/evolution-and-write-back.md`).

## Why

The package contract forbids a manifest JSON file, so there is no second metadata surface to drift.

## Enforcement

- `tests/test_package_contract.py` asserts that `CHANGELOG.md` contains a `0.x.y` string somewhere (not specifically a heading).
- `scripts/check_governance.py` `check_version_restated` (2026-11-09) reads the newest release heading and fails when any other `.md`, `.py`
  or `.yaml` file states that version; verbatim captures under `documents/`, rotated history under `docs/history/`, dot folders and the
  checker itself are exempt. `Governance.test_a_restated_version_fails_the_gate` proves it can fail.
