---
title: Eval definition contract
type: spec
status: accepted
tags: [contract, evidence]
provenance: promoted from references/02_defining-evals.md and schemas/ by skill-ai-it promote on 20260923_1311
---

# Spec: Eval definition contract

The portable contract a consuming project depends on. It is stated across `schemas/*.json` and [references/02_defining-evals.md](../../references/02_defining-evals.md); this document is the single
statement of what the contract requires and why each element is mandatory.

## Required elements

| Element | Requirement | Failure it prevents |
|---|---|---|
| `id` | Stable identifier for the eval | Records that cannot be joined to a definition |
| `claim` | One sentence, stating what must hold | An eval nobody can judge as met or unmet |
| `population.definition` | What the set is | A denominator that silently shrinks |
| `population.denominator_source` | Where the count comes from, independently of the evaluated path | Coverage computed over convenient successes |
| `population.slices` | The slices reported, each with a denominator | A whole-estate pass hiding a failing segment |
| `oracle` | Description, path, `independent`, `routes_through_evaluated_path` | A system verifying itself |
| `observation_layer` | The claim layer and its rank | A claim with no declared altitude |
| `evidence` | A reference and its layer | An assertion with no artifact behind it |
| `executor` | `type` and `ref` pointing at work that already exists | This package being asked to run something |
| `tier` | `id` and `runner` | An agent running an unsafe live check |
| `validity` | `max_age` and `invalidate_on` | Historical truth presented as current truth |
| `falsifiability` | `method`, `ref`, `verified_at` | A green check that has never shown it can fail |

## Notes on two elements that are commonly got wrong

**`executor.ref` points at work that already exists.** It is not code for this package to run. This follows from [skill-not-platform](../adr/skill-not-platform.adr.md).

**The denominator source must be independent of the evaluated path.** In the worked example in
[references/02_defining-evals.md](../../references/02_defining-evals.md), the bank settlement file defines the denominator; a list emitted by the sync path could not, because the sync path is what is
being judged.

## Enforcement

Executable. `scripts/validate_suite.py` rejects a suite missing any required element. A result value in `evals.yaml` is a definition error, not an observation: observations belong in history.
