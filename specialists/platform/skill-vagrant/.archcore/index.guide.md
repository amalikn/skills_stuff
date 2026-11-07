---
title: Archcore index — skill-vagrant
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-vagrant. Written at creation on 2026-11-07. Every document below is `proposed` until the operator accepts it; supersede an accepted
document in place with a dated note naming its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | proposed |

## rules/

| Document | Status |
|---|---|
| [lab-writes-stay-in-the-project.rule.md](rules/lab-writes-stay-in-the-project.rule.md) | proposed |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | proposed |

## plans/

| Document | Status |
|---|---|
| [keep-the-pinned-box-before-registry-eol.plan.md](plans/keep-the-pinned-box-before-registry-eol.plan.md) | proposed |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py` |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces |
| Version-of-record rule | Same rule as skill-nautobot's `changelog-version-of-record`; stated once in `AGENTS.md` here |
