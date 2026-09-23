---
title: Report expired and invalidated as separate staleness reasons
type: adr
status: accepted
tags: [validity, reporting]
provenance: promoted from CHANGELOG.md (20260923) and SCRATCHPAD.md by skill-ai-it promote on 20260923_1311
---

# ADR: Report expired and invalidated as separate staleness reasons

## Status

Accepted 20260923_1331 by the operator. Reverses the original renderer design. Source: [CHANGELOG.md](../../CHANGELOG.md), entry of 2026-09-23.

## Context

`scripts/render_report.py` originally collapsed two distinct causes of staleness into a single reason string: an observation that had aged past `validity.max_age`, and an observation killed by a
declared invalidation event. A separate verification session found the collapse and treated it as a defect.

## Decision

A verdict that died of age reads `expired: older than <max_age>`. One killed by a declared invalidation reads `invalidated: <trigger> (<reference>)`, naming the trigger from the invalidation record.
When both apply, both are listed.

## Rationale

The two states call for different actions. An expired observation needs a re-run. An invalidated one needs the change understood first, because re-running against a changed implementation,
configuration, oracle, or population may answer a different question than the one recorded. Merging them hid that difference behind one word.

## Consequences

- Any renderer or downstream consumer must keep the causes as a list, not a single string, so both can be reported together.
- Adding a new staleness cause means adding a new named reason rather than widening an existing one.
- Worked evidence exists in both directions: [examples/network-controller/report.md](../../examples/network-controller/report.md) shows the expired form and
  [examples/recording-demo/invalidation-report.md](../../examples/recording-demo/invalidation-report.md) shows the invalidated form.
