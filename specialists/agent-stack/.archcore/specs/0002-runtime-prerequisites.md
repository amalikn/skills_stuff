Title: Spec 0002 — Runtime prerequisite contract
Category: design-contract
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: RUNTIME.md
Summary: Pointer to the authoritative contract for tool-class skills and their requires_any prerequisites.

# Spec 0002 — Runtime prerequisite contract

## Contract

Authoritative text: [RUNTIME.md](../../RUNTIME.md).

A skill declaring `execution = "tool"` declares `requires_any` prerequisites. A route selecting it must confirm the prerequisite, route to an analysis-class
alternative, or report the blocker.

## Why it is enforced rather than advised

A route that cannot execute is not a cheaper route — it is a wrong answer delivered confidently. `[[route_invariants]]` states this as
`runtime-prerequisite-closure`.
