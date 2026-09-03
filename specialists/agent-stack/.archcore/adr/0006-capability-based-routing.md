Title: ADR 0006 — Capability-based routing
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: MEMORY.md, routing.toml
Summary: A gate is an obligation on the route discharged by any provider declaring the required capability; supporting strength never discharges one.

# ADR 0006 — Capability-based routing

## Decision

Three rules, adopted together on 2026-09-01:

1. **A gate is an obligation on the route, not an instruction to add a persona.** It is discharged by any selected skill or persona declaring the gate's
   `required_capability` at its `minimum_strength`.
2. **A capability is declared once, on its provider.** Gates name a `required_capability`; they never enumerate skills.
3. **`supporting` strength never discharges a gate.**

## Rationale

The inverse of (1) caused measurable persona inflation. (2) replaced a hand-maintained `satisfied_by_skills` list that was a second copy of the taxonomy and could
drift from the first. (3) is the rule that keeps `analysis != independent challenge` true — without it, any skill that touches risk eventually reads as a critic.

## Consequences

- Migration was verified behaviour-preserving before the old form was deleted: resolving each gate through the new metadata reproduced its old skill list exactly.
- Nine validator checks enforce the shape. See [the routing catalogue contract](../specs/0003-routing-catalogue-contract.md).
