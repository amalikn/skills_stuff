Title: Rule 0003 — Registration and upstream baseline hygiene
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: AGENTS.md
Summary: Every capability is registered in the manifest in the same pass that creates it; never record an already-symlinked checkout as the upstream baseline.

# Rule 0003 — Registration and upstream baseline hygiene

## Rules

- Adding a persona or skill package means adding its `manifest.yaml` capability row in the same pass. See [ADR 0003](../adr/0003-the-manifest-is-the-contract.md).
- **Never run `just record-current` against a checkout that has already been symlinked to Agent Stack.**

## Why the second rule is here despite being narrow

Its failure is silent and total: it records Agent Stack's own content as the upstream baseline, after which every genuine upstream change reads as a local
modification and the sync tool stops being able to tell them apart.
