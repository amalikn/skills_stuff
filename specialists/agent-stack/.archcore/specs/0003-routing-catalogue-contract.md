Title: Spec 0003 — The four-table routing catalogue
Category: design-contract
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: routing.toml
Summary: capabilities declares, gates obligates, precedence ranks ownership, route_invariants defines validity.

# Spec 0003 — The four-table routing catalogue

## Contract

`routing.toml` carries four cooperating tables:

| Table                 | Answers                                                        |
| --------------------- | -------------------------------------------------------------- |
| `[[capabilities]]`    | What can be provided, and by whom, at what strength            |
| `[[gates]]`           | What the route owes, as a `required_capability` + `minimum_strength` |
| `[[precedence]]`      | Who owns a decision two personas both plausibly own            |
| `[[route_invariants]]` | What makes a **finished** route invalid rather than merely thin |

Plus `[[routing_rules]]`, which are advisory only — see [rule 0005](../rules/0005-one-persona-model.md).

## Enforcement

Nine validator checks: unknown capability references, primary/supporting overlap, `tool-execution` disagreeing with a skill's execution class in either direction,
a persona claiming `tool-execution`, a gate no provider serves at primary strength, a leftover `satisfied_by_skills`, precedence branches that are unreal or
identical, an invariant naming a violation the scorer never reports, and an unearned `runtime_required` assertion. Each was proven able to fail.
