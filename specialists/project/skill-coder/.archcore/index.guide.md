---
title: Archcore index — skill-coder
status: accepted
tags: [index]
---

Durable index of the decisions and rules recorded for skill-coder. Both documents record operator decisions made in chat on 2026-10-19 but were written
outside skill-ai-it's `promote` mode, so they stay `proposed` until the operator approves the promotion. Accepted documents are the highest-authority
statement of what the pack has decided; supersede one in place with a dated note naming its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [helpers-run-in-target-environment.adr.md](adr/helpers-run-in-target-environment.adr.md) | proposed |

## rules/

| Document | Status |
|---|---|
| [code-map-holds-decisions-only.rule.md](rules/code-map-holds-decisions-only.rule.md) | proposed |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim ledger and code-map schemas | Specified executably by `tests/test_package_contract.py` and `scripts/code_map.py` |
| Rules from the global policy, governance `coding-guide.md` and project code designs | Governed at their source; the pack cites them |
