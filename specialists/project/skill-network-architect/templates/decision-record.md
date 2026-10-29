---
Title: Architecture decision record template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: One architecturally significant decision per record, in MADR 4.0 form with Nygard status semantics, evidence labels, confirmation and reopen conditions.
---

# ADR-<nnnn>: <short noun phrase naming the problem and chosen solution>

Worked example: `skill-network-architect/examples/filled/decision-record.md` (filled for a fictional remote-site operator; lives in the network pack only).

Based on: Michael Nygard, "Documenting Architecture Decisions" (2011, https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) and MADR 4.0.0 (https://adr.github.io/madr/).
Sections follow MADR; status values follow Nygard and MADR; evidence labels and reopen conditions are additions for this pack.

## How to use

- Write one ADR per decision that affects structure, non-functional behaviour, dependencies, interfaces or construction technique.
- Keep it to one or two pages.
- Number sequentially; never reuse a number.
- Never rewrite an accepted ADR: supersede it with a new one and link both ways.
- Write Context in value-neutral language (facts and forces); write Decision in active voice ("We will ...").
- List all consequences, not only good ones.

| Field                  | Value                                                                  |
| ---------------------- | ---------------------------------------------------------------------- |
| Status                 | proposed / accepted / rejected / deprecated / superseded by ADR-<nnnn> |
| Date (last updated)    | <YYYY-MM-DD>                                                           |
| Decision makers        | <roles>                                                                |
| Consulted (two-way)    | <network architect, systems architect, specialist skills or roles>     |
| Informed (one-way)     | <roles>                                                                |
| Requirements addressed | REQ-<nn>, REQ-<nn>                                                     |
| Related                | design <DES-nnn>, interface <IF-nnn>, supersedes ADR-<nnnn>            |

## Context and problem statement

*Two to four sentences, or a question. What forces are in tension (cost, resilience, staffing, vendor support, lifecycle)? What triggered the decision now?*

| Fact                           | Value and unit | Source             | Label            | Date         |
| ------------------------------ | -------------- | ------------------ | ---------------- | ------------ |
| *e.g. measured peak on backhaul* | <n> Mbit/s p95 | <collector, query> | VERIFIED_PRIMARY | <YYYY-MM-DD> |

## Decision drivers

- *Driver tied to a requirement, e.g. "REQ-02: restore within <n> min without the primary path".*
- *Constraint, e.g. "one operator on call; no specialist out of hours".*

## Considered options

1. <option A, the simplest viable>
2. <option B, higher resilience>
3. <option C, phased or do nothing>

## Decision outcome

Chosen option: "<option>", because *it satisfies drivers <list> with the lowest <cost/complexity>; it fails driver <x> and we accept that because <reason>.*

### Consequences

- Good, because *<positive consequence>*.
- Bad, because *<negative consequence, accepted single point of failure, new skill needed, lock-in>*.
- Neutral: *<operational change, new runbook, monitoring addition>*.

### Confirmation

*How compliance is confirmed after implementation: a measurement, test or review with pass criteria. Also state the observation that would falsify the decision.*

| Check           | Pass criterion                | Falsifying observation                    | Owner  | Due    |
| --------------- | ----------------------------- | ----------------------------------------- | ------ | ------ |
| <failover test> | <service restored within n s> | <loss exceeds n s, or path B shares duct> | <role> | <date> |

## Pros and cons of the options

### <option A>

- Good, because *<argument>*. Bad, because *<argument>*. Operating cost: *<staff hours, licences, energy>*. Exit cost: *<effort to leave>*.

### <option B>

- Good, because *<argument>*. Bad, because *<argument>*. Operating cost: *<...>*. Exit cost: *<...>*.

## More information

- Reopen when: *a concrete trigger, e.g. "demand exceeds <n> Mbit/s p95 for 7 days", "vendor EOL announced", "staffing changes".*
- Evidence links and review notes per revision:

| Revision | Review state | Date         | Reviewer (role) | Notes  |
| -------- | ------------ | ------------ | --------------- | ------ |
| r1       | proposed     | <YYYY-MM-DD> | <role>          | <link> |

Review states: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified; rejected and superseded keep their reasons.
