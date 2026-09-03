Title: ADR 0004 — Upstream sync is report-first
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: Only English additions and unchanged canonical replacements apply automatically; everything else becomes a review proposal.

# ADR 0004 — Upstream sync is report-first

## Decision

`safe_add` and `safe_replace` apply automatically. `translation_required`, `manual_merge` and `remove_review` are written as review proposals only.

## Rationale

Automatic application is restricted to the cases where correctness is decidable without judgement.

## Consequences

- Never hand-copy from an Auto Company checkout; the classification is the safety mechanism.
- See [the sync guide](../guides/0001-upstream-sync.md) for the workflow and
  [ADR 0009](0009-sync-apply-is-atomic.md) for the transaction model.
