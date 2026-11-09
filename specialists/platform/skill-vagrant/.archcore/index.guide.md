---
title: Archcore index — skill-vagrant
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-vagrant. Written at creation on 2026-11-07; reviewed 2026-11-09 (scope widened to every provider, plan status, new rule). All documents below were accepted by the operator on 2026-11-09; supersede an accepted
document in place with a dated note naming its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | accepted |

## rules/

| Document | Status |
|---|---|
| [lab-writes-stay-in-the-project.rule.md](rules/lab-writes-stay-in-the-project.rule.md) | accepted |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | accepted |
| [name-the-provider.rule.md](rules/name-the-provider.rule.md) | accepted |

## plans/

| Document | Status |
|---|---|
| [keep-the-pinned-box-before-registry-eol.plan.md](plans/keep-the-pinned-box-before-registry-eol.plan.md) | accepted |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py` |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces |
| Version-of-record rule | Same rule as skill-nautobot's `changelog-version-of-record`; stated once in `AGENTS.md` here |
