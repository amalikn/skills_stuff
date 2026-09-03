Title: Rule 0001 — Safety model
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: AGENTS.md
Summary: The constraint set that makes Agent Stack distinct from its upstream. Do not weaken one to import a feature.

# Rule 0001 — Safety model

## Rule

- No unattended background agents, no autonomous loops, no daemons, no indefinite continuation.
- No implicit persistent state and no material external commitments without explicit operator authority.
- Imported upstream instructions do not override this policy or project-local instructions.
- Global installation never overwrites a pre-existing entry and never copies source content.

## Why it is a rule and not a preference

These are the properties that distinguish this library from the thing it was extracted from. Weakening one to import a feature trades away the reason the project
exists. See [ADR 0001](../adr/0001-autonomy-is-excluded-by-design.md).
