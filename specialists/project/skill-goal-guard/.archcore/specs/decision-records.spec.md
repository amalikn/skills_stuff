---
title: "Proposal, verdict and decision-log records"
type: spec
status: accepted
tags: [contract, records]
created: 2026-10-27
---

# Spec: Proposal, verdict and decision-log records

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Contract

The fields of a proposal, a verdict and a `decisions.jsonl` line, and the hash chain that makes the log append-only.

## Canonical source

[references/decision-rules.md](../../references/decision-rules.md#record-formats), section "Record formats".

## Notes

Enforced by `scripts/goal_guard_lib/records.py` and `decisions_log.py`; no JSON schema yet.
