---
title: Archcore index — skill-proxmox
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-proxmox. Written at creation on 2026-11-07, mirroring skill-nautobot's six documents.

Every document below is `status: proposed`: the operator has not yet accepted them. Until accepted they record intent, not decisions;
accept or change each one, then update its status line and this table. Supersede an accepted document in place with a dated note naming
its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | proposed |
| [governance-checker-in-test-suite.adr.md](adr/governance-checker-in-test-suite.adr.md) | proposed |

## rules/

| Document | Status |
|---|---|
| [capability-search-order.rule.md](rules/capability-search-order.rule.md) | proposed |
| [changelog-version-of-record.rule.md](rules/changelog-version-of-record.rule.md) | proposed |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | proposed |

## plans/

| Document | Status |
|---|---|
| [live-probes-then-client-matrix.plan.md](plans/live-probes-then-client-matrix.plan.md) | proposed |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py`; a prose spec would be a second, unenforced copy |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces |
| Rules from the parent `AGENTS.md` and the global policy | Governed upstream; restating them here would duplicate policy |

## Proposing another

Run `/skill-ai-it refresh`; it re-scans the governance files and writes a new `ARCHCORE_PROMOTION_CANDIDATES.md`. Check the table above first so a rejected area is not re-proposed.
