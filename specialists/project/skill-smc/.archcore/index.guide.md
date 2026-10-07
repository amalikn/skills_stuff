---
title: Archcore index — skill-smc
status: accepted
tags: [index]
---

Durable pack truth: decisions that are settled, rules that are enforced, contracts other work must satisfy. All five documents were promoted on 20260626 from `AGENTS.md`,
`AI_NAVIGATION.md` and the CHANGELOG, accepted on 20260908, and renamed to the `<slug>.<type>.md` form on 20261007. This index was added on 20261007 to match the
other project packs.

An accepted document is not immutable: amend it in place with a dated note naming what changed and what still stands, rather than deleting it.

## Contents

- [Decisions](#decisions)
- [Rules](#rules)
- [Contracts](#contracts)
- [Proposing another](#proposing-another)

## Decisions

| Document                                                                         | Governs                                                                     |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| [Progressive disclosure reference structure](adr/progressive-disclosure-structure.adr.md) | Why the pack is split into numbered references behind a routing index |

## Rules

| Document                                                                    | Enforced by                                                                          |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [Manifest version discipline](rules/manifest-version-discipline.rule.md)    | `scripts/check_governance.py` version-stamp check (no duplicate of the pack version) |
| [Progressive disclosure loading](rules/progressive-disclosure-loading.rule.md) | Operator review: `RUNBOOK.md` stays an index, never a content source              |
| [Reference update discipline](rules/reference-update-discipline.rule.md)    | `scripts/check_governance.py` catalog check across the four index surfaces          |

## Contracts

| Document                                                             | Defines                                                  |
| -------------------------------------------------------------------- | -------------------------------------------------------- |
| [Specialist pack file roles](specs/specialist-pack-file-roles.spec.md) | Role and install treatment of every file in this pack |

## Proposing another

1. Write the candidate into the source it belongs to first: `AGENTS.md`, `SCRATCHPAD.md` (marked `KEEP`), or a reference file.
2. Run `/skill-ai-it refresh` to regenerate a candidate queue, or add the document here directly with a provenance header, starting at `status: proposed`.
3. Apply the test: would it still read as true after the next real SMC incident or ansible-wifi change? If not, it belongs in `SCRATCHPAD.md` or a reference.
