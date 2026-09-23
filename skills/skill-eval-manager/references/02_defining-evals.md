# Defining evals

## Contents

- [Minimum contract](#minimum-contract)
- [A well-formed example](#a-well-formed-example)
- [Common failures](#common-failures)
- [Layer design](#layer-design)

## Minimum contract

Every eval needs an id, one-sentence claim, population definition and denominator source, slices, independent oracle, claim and evidence layers, executor reference, tier/runner, validity policy, and
falsifiability evidence. `executor.ref` points at work that already exists; it is not code for this package to run.

## A well-formed example

```yaml
id: payments.settlement-visible
claim: Every settled payment is visible to an operator after the next sync window.
population:
  definition: Settled payments in the acquiring-bank settlement file.
  denominator_source: bank/settlements-YYYY-MM-DD.csv
  slices: [{id: all, denominator: 84}]
oracle:
  description: Operator display export joined to the independent bank settlement file.
  path: bank file vs operator display export
  independent: true
  routes_through_evaluated_path: false
observation_layer: {id: rendered, rank: 30}
evidence: {ref: reports/payment-visibility.csv, layer: {id: rendered, rank: 30}}
executor: {type: query, ref: queries/payment-visibility.sql}
tier: {id: production-read-only, runner: operator}
validity: {max_age: 1d, invalidate_on: [implementation_change, population_change]}
falsifiability: {method: counterexample, ref: fixtures/missing-payment.csv, verified_at: 2026-09-23}
```

The bank file defines the denominator; a list emitted by the sync path could not. The operator display is the claim layer, so an API acknowledgement at transport rank cannot prove it.

## Common failures

- “All processed records succeeded” has no declared population, so its denominator can silently shrink.
- “API returned 201” is transport evidence and cannot prove a stored/rendered/durable claim.
- “The application API says it is correct” is not an independent oracle when the API path is what is judged.
- A free-text “tested manually” is not falsifiability evidence without a method, reference, and date.
- A result value is not a suite definition. Put it in history, not `evals.yaml`.

## Layer design

Use project-specific names and monotonic ranks. The default vocabulary is transport 10, stored 20, rendered 30, durable 40. A finance suite may instead use parsed, posted, reconciled, and signed-off.
The validator checks only the general rule: evidence at a lower rank cannot establish a higher-rank claim.
