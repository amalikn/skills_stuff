---
title: Archcore index — skill-nautobot
status: accepted
tags: [index]
---

Durable index of everything promoted into `.archcore/` for skill-nautobot. Written by `skill-ai-it` in `promote` mode on 2026-10-05 from the candidates queue, which was then deleted: it was a
proposal queue, not a record. This index is the record.

Promotion wrote every document as `status: proposed`. **The operator accepted all 6 on 2026-10-05.** They are now the highest-authority statement of what this pack has
decided. Supersede an accepted document in place with a dated note naming its replacement rather than deleting it; a document's own Confidence line says what remains open.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | accepted |
| [governance-checker-in-test-suite.adr.md](adr/governance-checker-in-test-suite.adr.md) | accepted |

## rules/

| Document | Status |
|---|---|
| [capability-search-order.rule.md](rules/capability-search-order.rule.md) | accepted |
| [changelog-version-of-record.rule.md](rules/changelog-version-of-record.rule.md) | accepted |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | accepted |

## plans/

| Document | Status |
|---|---|
| [live-probes-then-client-matrix.plan.md](plans/live-probes-then-client-matrix.plan.md) | accepted |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py`; a prose spec would be a second, unenforced copy |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces and every engagement already loads |
| Rules from the parent `AGENTS.md` and the global policy | Governed upstream; restating them here would duplicate policy |

## Proposing another

Run `/skill-ai-it refresh`; it re-scans the governance files and writes a new `ARCHCORE_PROMOTION_CANDIDATES.md`. Check the table above first so a rejected area is not re-proposed.
