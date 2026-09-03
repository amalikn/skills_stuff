Title: ADR 0005 — The governance gate is stdlib-only
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: A check that cannot run is indistinguishable from a check that passes, so the gate must never fail for environment reasons.

# ADR 0005 — The governance gate is stdlib-only

## Decision

`scripts/check_governance.py` imports only the standard library, and `just governance` falls back to the system interpreter when the venv is absent.

## Rationale

A check that cannot run is indistinguishable from a check that passes.

## Consequences

- Third-party test dependencies live in `requirements-dev.txt` and never in the gate.
- Evidenced 2026-09-01: a staleness-audit gate that could not parse a JSONC file reported **SKIPPED**, not passed — the same principle applied by a different
  tool.
