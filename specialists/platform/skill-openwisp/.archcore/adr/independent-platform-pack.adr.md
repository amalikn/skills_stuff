---
title: Independent OpenWISP platform pack
type: adr
status: accepted
tags: [pack-boundary, openwisp]
created: 2026-10-05
---

# ADR: Independent OpenWISP platform pack

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Recent decisions).

## Context

OpenWISP knowledge was first gathered inside project work and the equipment packs (`skill-smc`, `skill-cambium`). On 2026-10-01 the operator stated (USER_STATED, memory-keeper
`unc.nautobot-openwisp-skill-operator-contract.20261001_1724`) that Nautobot and OpenWISP deserve separate, reusable, evolving skills rather than sections of those packs, learning from
each engaging project while preserving evidence, project boundaries and permission limits.

## Decision

`skill-openwisp` is a standalone, cross-project pack for registration, passive monitoring, metrics, workers, health, alerts and presentation. It is not a section of `skill-smc` or `skill-cambium`, and it is separate from its counterpart `skill-nautobot`.

## Consequences

- The primary pack for a task is chosen by the object being changed; the other pack is read only for its contract (`SKILL.md`, Route the task).
- Customer, site and equipment specifics stay in the engaging project; vendor commands and OIDs stay with the equipment packs.
- Every engagement owes a write-back here (`references/evolution-and-write-back.md`), which is what keeps a separate pack from going stale.

Confidence: high — operator-stated, and the pack has shipped four releases on this basis.
