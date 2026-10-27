---
title: "Snapshot and manifests"
type: spec
status: accepted
tags: [contract, records]
created: 2026-10-27
---

# Spec: Snapshot and manifests

Status: accepted (operator, 2026-10-27)

Promoted by `skill-ai-it promote` on 2026-10-27 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates ("promote and approve all"). Pointer document (option A): the cited source stays canonical; this states it and links there.

## Contract

Provider-neutral task records, the project and parent manifests with checksums and completeness, and what is never exported.

## Canonical source

[references/snapshot-and-restore.md](../../references/snapshot-and-restore.md#snapshot), section "Snapshot".

## Notes

Implemented in `scripts/goal_guard_lib/snapshot.py` and `restore.py`.
