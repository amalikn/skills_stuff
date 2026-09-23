---
title: Ship the method as a skill, not an executor or platform
type: adr
status: accepted
tags: [scope]
provenance: promoted from BRIEF.md by skill-ai-it promote on 20260923_1311
---

# ADR: Ship the method as a skill, not an executor or platform

## Status

Accepted 20260923_1331 by the operator. Promoted from [BRIEF.md](../../BRIEF.md) "Decision".

## Context

The work could have been shaped as an evaluation platform: a scheduler, a parallel runner, a retry policy, an executor plugin system, or an assertion DSL. Projects that need evaluation discipline
already own the tools that produce observations.

## Decision

> This is appropriately a skill: the durable value is a cross-project method and a small, transparent record format, not a new executor or platform. The scripts prevent routine clerical drift while
> external project tools remain responsible for measurement.

The package defines, validates, records, invalidates, and reports. It does not execute an eval.

## Alternative rejected

Build an executor or platform. Rejected because the portable value is the contract between a claim and its evidence, not the mechanics of running a check. A platform would have to absorb every
consuming project scheduler and safety boundary, and would stop being portable at that point.

## Consequences

- A request for a scheduler, parallel runner, retry policy, executor plugin system, CI product, or assertion DSL is out of scope and must be refused rather than absorbed.
- `type: manual` has to be a first-class executor, because the package cannot run anything itself. See [manual-executor-first-class](manual-executor-first-class.adr.md).
- Shipped scripts stay small and stdlib-only, so a consuming project can adopt them without taking a dependency.
