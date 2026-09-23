---
title: Derived states, computed at read time
type: spec
status: accepted
tags: [validity, reporting]
provenance: promoted from references/03_verdicts-and-validity.md by skill-ai-it promote on 20260923_1311
---

# Spec: Derived states, computed at read time

Behaviour consumers must not re-implement differently. Two states exist in a report that never exist in a record.

## not_evaluated

No observation exists for a declared eval and population slice.

## stale

An observation exists but is older than `validity.max_age`, or a later declared invalidation event applies. The two causes are reported separately and both are listed when both apply — see
[split-expired-and-invalidated](../adr/split-expired-and-invalidated.adr.md):

- `expired: older than <max_age>`
- `invalidated: <trigger> (<reference>)`

## Derivation rules

- Both are computed only when rendering. Neither is ever written to `history.jsonl`.
- The observation schema deliberately excludes them from the verdict enum. See [recorded-verdict-set](../rules/recorded-verdict-set.rule.md).
- An invalidation event counts only when it is later than the observation it would invalidate.
- The newest `recorded_at` per eval and slice is the one evaluated; superseded records stay in history but do not drive the report.

## Why derivation rather than recording

A recorded `stale` is a snapshot of staleness at write time, which is the one moment it is guaranteed not to be stale. Deriving it means the report answers the question at the moment it is asked.

## Reference implementation

`scripts/render_report.py`. A consuming project that renders its own report must reproduce these rules rather than invent its own.
