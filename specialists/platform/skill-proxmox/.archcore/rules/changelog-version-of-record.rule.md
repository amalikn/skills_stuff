---
title: CHANGELOG release heading is the version of record
type: rule
status: proposed
tags: [versioning, governance]
created: 2026-11-07
---

# Rule: CHANGELOG release heading is the version of record

Status: proposed (2026-11-07; same rule as skill-nautobot)

## Rule

The pack version is the newest release heading in `CHANGELOG.md` (`## x.y.z — date`). No other pack file restates it. Unreleased work,
including every write-back line, goes under `## Unreleased` until release reconciliation (`references/evolution-and-write-back.md`).

## Why

The package contract forbids a manifest JSON file, so there is no second metadata surface to drift.

## Enforcement

The contract test requires a version-shaped heading in `CHANGELOG.md`. Restatement elsewhere is not yet checked.
