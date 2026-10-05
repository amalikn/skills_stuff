---
title: CHANGELOG release heading is the version of record
type: rule
status: accepted
tags: [versioning, governance]
created: 2026-10-05
---

# Rule: CHANGELOG release heading is the version of record

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `AGENTS.md` (Working rules).

## Rule

The pack version is the newest release heading in `CHANGELOG.md` (`## x.y.z — date`). No other pack file restates it. Unreleased work, including every write-back line, goes under
`## Unreleased` until release reconciliation (`references/evolution-and-write-back.md`).

## Why

The package contract forbids a manifest JSON file, so there is no second metadata surface; restating the version elsewhere would create one by hand, and it would drift.

## Enforcement

The contract test requires a version-shaped heading in `CHANGELOG.md`. Restatement elsewhere is not yet checked: the candidate is a `CONSTANT_SURFACES` entry in
`scripts/check_governance.py` registering `CHANGELOG.md` as the only surface for this pack's version string.
