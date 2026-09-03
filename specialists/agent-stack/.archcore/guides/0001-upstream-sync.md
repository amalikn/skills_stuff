Title: Guide 0001 — Upstream sync workflow
Category: operating-guide
Status: superseded
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: AGENTS.md
Summary: status, dry-run, fetch-dry-run, apply — and the classification that decides what applies automatically.

> **SUPERSEDED 20260903 — upstream sync retired.** Every recipe this guide names (`upstream-status`, `upstream-dry-run`, `upstream-fetch-dry-run`, `upstream-apply`, `record-current`) was
> removed with `scripts/sync_auto_company.py`; the guide was left at `accepted` in that pass and went on describing a workflow that no longer exists, which is how a reader would have found
> it. Kept as the record of how imports were governed while there was an upstream. See [ADR 0004](../adr/0004-sync-is-report-first.md).

# Guide 0001 — Upstream sync workflow

## Workflow

1. `just upstream-status` — configured state, no network, no mirror.
2. `just upstream-dry-run` — compare the existing mirror without fetching.
3. `just upstream-fetch-dry-run` — fetch into the disposable working cache and report proposed changes.
4. `just upstream-apply apply` — applies **only** `safe_add` and `safe_replace`.

## Rules

- Never hand-copy from an Auto Company checkout.
- Never run `just record-current` against a checkout already symlinked to Agent Stack — see [rule 0003](../rules/0003-manifest-registration.md).
- Everything not classified safe is written as a review proposal. See [ADR 0004](../adr/0004-sync-is-report-first.md).
