---
title: Archcore index — skill-drawio
status: accepted
tags: [index]
---

Durable index of the decisions and rules recorded for skill-drawio. Accepted documents are the highest-authority statement of what the pack has decided; supersede one in place with a dated note naming
its replacement rather than deleting it. All eleven were promoted 2026-10-19 through skill-ai-it `promote` mode on the operator's instruction "promote and accept", from the reviewed candidate list
(review and corrections recorded in `CHANGELOG.md`, 2026-10-19). To propose another, run skill-ai-it `refresh`, review the candidates file it writes, then `promote`.

## adr/

| Document                                   | Status   |
| ------------------------------------------ | -------- |
| [flow-maps-are-data.adr.md](adr/flow-maps-are-data.adr.md) | accepted |
| [profile-holds-project-values.adr.md](adr/profile-holds-project-values.adr.md) | accepted |
| [engine-runs-in-consumer-interpreter.adr.md](adr/engine-runs-in-consumer-interpreter.adr.md) | accepted |
| [front-ends-and-library-packages.adr.md](adr/front-ends-and-library-packages.adr.md) | accepted |

## rules/

| Document                                             | Status   |
| ---------------------------------------------------- | -------- |
| [hand-edited-drawings-are-source.rule.md](rules/hand-edited-drawings-are-source.rule.md) | accepted |
| [engine-changes-keep-consumers-byte-identical.rule.md](rules/engine-changes-keep-consumers-byte-identical.rule.md) | accepted |
| [routed-pages-pass-layout-audits.rule.md](rules/routed-pages-pass-layout-audits.rule.md) | accepted |
| [review-renders-before-showing.rule.md](rules/review-renders-before-showing.rule.md) | accepted |
| [drawings-written-uncompressed.rule.md](rules/drawings-written-uncompressed.rule.md) | accepted |
| [cross-project-write-back.rule.md](rules/cross-project-write-back.rule.md) | accepted |
| [pack-text-stays-generic.rule.md](rules/pack-text-stays-generic.rule.md) | accepted |

## Deferred until a second project adopts the engine

| Candidate                                                                    | Reason                                                                                                            |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| specs/ — the flow-map contract (`schemas/flowmap.schema.json`, `model.py`)   | One consumer only; the schema file is the contract and `test_schema_subset`, `test_reference_problems` enforce it |
| guides/ — adopting the engine in a project (`SKILL.md`, `scripts/README.md`) | Too short to stand alone; promote when the steps are proven in a second project                                   |

## Never promoted, and why

| Candidate area                                                                    | Reason                                                                     |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| draw.io version facts (pages from 1, `--layers` takes indexes, `--crop` PDF only) | Version-specific evidence, kept in `sources.yaml` and `compatibility.yaml` |
| Code-practice rules (sizes, docstrings, timeouts, write gates)                    | Governed upstream by skill-coder; not duplicated                           |
| Layout constants (head room 24 and 22, `ARC_GAP` 6)                               | Audit parameters, recorded in `references/layout-audits.md` and the code   |
| plans/                                                                            | The pack has no approved plan or roadmap                                   |
