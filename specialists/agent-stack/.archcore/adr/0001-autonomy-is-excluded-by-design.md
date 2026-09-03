Title: ADR 0001 — Autonomy is excluded by design
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: The upstream loop, consensus mechanism and daemon are deliberately absent; that exclusion is the reason this extraction exists.

# ADR 0001 — Autonomy is excluded by design

## Decision

Agent Stack does not carry Auto Company's autonomous loop, consensus mechanism, or daemon.

## Rationale

They are not missing features. Leaving them out is the reason the extraction exists — an operator-controlled library with no unattended execution is a different
product from the upstream, and the difference is the point.

## Consequences

- An imported upstream skill implying autonomy is **adapted**, not carried across. `websh` and `deep-research` are the worked examples.
- A proposal to add background execution is a proposal to end the project's reason for existing, and should be evaluated on those terms.
- The [Safety model](../rules/0001-safety-model.md) is the enforceable form of this decision.
