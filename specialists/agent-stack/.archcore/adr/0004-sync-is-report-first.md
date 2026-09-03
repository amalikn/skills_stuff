Title: ADR 0004 — Upstream sync is report-first
Category: architecture-decision
Status: superseded
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: Only English additions and unchanged canonical replacements apply automatically; everything else becomes a review proposal.
> **SUPERSEDED 20260903 — upstream sync retired.** Agent Stack is maintained as its own project now; there is no upstream to sync from, so `scripts/sync_auto_company.py`, `upstream-state.json` and
> `translation-memory.json` are removed. Kept as the record of a decision that was made and implemented, not as a live rule. The reasoning about report-first application, atomic promotion and symlink
> refusal remains correct for any future tool that copies files into this tree.


# ADR 0004 — Upstream sync is report-first

## Decision

`safe_add` and `safe_replace` apply automatically. `translation_required`, `manual_merge` and `remove_review` are written as review proposals only.

## Rationale

Automatic application is restricted to the cases where correctness is decidable without judgement.

## Consequences

- Never hand-copy from an Auto Company checkout; the classification is the safety mechanism.
- See [the sync guide](../guides/0001-upstream-sync.md) for the workflow and
  [ADR 0009](0009-sync-apply-is-atomic.md) for the transaction model.
