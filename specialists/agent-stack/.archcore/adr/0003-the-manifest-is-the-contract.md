Title: ADR 0003 — The manifest is the contract
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: Installer, validator and routing all derive from manifest.yaml, so an unregistered entry is invisible to all three at once.

# ADR 0003 — The manifest is the contract

## Decision

`manifest.yaml` is the single registration surface. Adding a persona or skill package means adding its capability row in the same pass.

## Rationale

Three mechanisms sharing one source of truth cannot disagree about what exists.

## Consequences

- An unregistered entry is invisible to the installer, the routing catalogue and the validator simultaneously — a silent, total failure rather than a loud
  partial one.
- Two governance checks enforce registration in both directions.
