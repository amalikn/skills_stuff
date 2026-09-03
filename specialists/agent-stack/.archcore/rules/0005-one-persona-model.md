Title: Rule 0005 — One persona model
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: routing.toml
Summary: routing_rules are advisory hints; mandatory routing lives only in gates, precedence and route invariants.

# Rule 0005 — One persona model

## Rule

`[[routing_rules]]` entries are **advisory keyword hints**. Mandatory-ness lives in exactly three places:

- `[[gates]]` — what the route owes
- `[[precedence]]` — who owns a contested decision
- `[[route_invariants]]` — what makes a finished route invalid

No `require_personas` in `routing_rules`, and no `*-gate` id there.

## What went wrong without it

For one day the catalogue carried two contradictory persona models at once. Seven rules **required** a persona on keyword match while `[[gates]]` said
`persona_mandatory = false`; two were even named `*-gate`. `architecture-owner` versus `implementation-owner` was the very conflict `[[precedence]]` had just been
written to rank, still asserted unranked three lines apart. The whole catalogue goes into the routing prompt, so the model received both instruction sets.

It was found by per-artifact reasoning, not by grep — nothing was stale as a string and the suite was green — and it retroactively explained an ownership
disagreement nobody had connected to it. Two validator checks now reject both forms.
