---
title: Archcore index — skill-proxmox
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-proxmox. Written at creation on 2026-11-07, mirroring skill-nautobot's six documents;
reviewed, corrected and accepted by the operator on 2026-11-09.

Accepted documents are durable decisions and outrank `AGENTS.md` prose where they differ. Supersede an accepted document in place with a
dated note naming its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | accepted 2026-11-09 |
| [governance-checker-in-test-suite.adr.md](adr/governance-checker-in-test-suite.adr.md) | accepted 2026-11-09 |

## rules/

| Document | Status |
|---|---|
| [capability-search-order.rule.md](rules/capability-search-order.rule.md) | accepted 2026-11-09 |
| [changelog-version-of-record.rule.md](rules/changelog-version-of-record.rule.md) | accepted 2026-11-09 |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | accepted 2026-11-09 |

## plans/

| Document | Status |
|---|---|
| [live-probes-then-client-matrix.plan.md](plans/live-probes-then-client-matrix.plan.md) | accepted 2026-11-09 |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py`; a prose spec would be a second, unenforced copy |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces |
| Verbatim captures with sha256 | Enforced by the contract test and stated in `AGENTS.md`; a rule here would duplicate it |
| Rules from the parent `AGENTS.md` and the global policy | Governed upstream; restating them here would duplicate policy |

## Proposing another

Candidates wait in `ARCHCORE_PROMOTION_CANDIDATES.md` at the pack root until the operator promotes or rejects each one; `/skill-ai-it refresh`
re-scans and updates it. Check the table above first so a rejected area is not re-proposed.
