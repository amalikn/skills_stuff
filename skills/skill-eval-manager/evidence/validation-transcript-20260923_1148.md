# Validation transcript — 2026-09-23 11:48 AEST

## Contents

- [Positive validation](#positive-validation)
- [Deliberate failures](#deliberate-failures)
- [Recording and rendering](#recording-and-rendering)
- [Interpretation](#interpretation)

## Positive validation

```text
VALID: suite=starter-evaluation-suite evals=2 layers=4 history_records=0
VALID: suite=network-controller-evaluation-framework evals=14 layers=4 history_records=3
VALID: suite=financial-reconciliation-example evals=3 layers=4 history_records=1
```

Python compilation of all four Python modules exited 0.

## Deliberate failures

```text
ERROR: eval[1]: oracle needs description and path
INVALID: 1 error(s)
ERROR: eval[1]: evidence rank 10 cannot prove claim rank 20
INVALID: 1 error(s)
ERROR: eval[1]: falsifiability needs a supported method and reference
INVALID: 1 error(s)
ERROR: eval[1]: oracle must be independent and must not route through the evaluated path
INVALID: 1 error(s)
ERROR: history:1: recorded verdict must be one of blocked, error, fail, inconclusive, pass; derived states are forbidden
INVALID: 1 error(s)
```

Each command exited 1, as intended. The fixtures respectively omit an oracle, make a stored claim using transport evidence, omit falsifiability, route the oracle through the evaluated path, and
attempt to record `stale`.

## Recording and rendering

```text
APPENDED: observation=demo-initial verdict=fail
APPENDED: observation=demo-correction verdict=pass
VALID: suite=starter-evaluation-suite evals=2 layers=4 history_records=2
RENDERED: skill-eval-manager/examples/recording-demo/report.md rows=2
RENDERED: skill-eval-manager/examples/network-controller/report.md rows=14
RENDERED: skill-eval-manager/examples/financial-reconciliation/report.md rows=3
APPENDED: observation=demo-before-invalidation verdict=pass
APPENDED: invalidation eval=example.durable-state slice=all
VALID: suite=starter-evaluation-suite evals=2 layers=4 history_records=2
RENDERED: skill-eval-manager/examples/recording-demo/invalidation-report.md rows=2
```

The recording-demo report shows one current `pass` and one `not_evaluated` row despite two retained observations. The network report shows `stale` and `not_evaluated` as derived states. The
invalidation report shows a recorded pass rendered as `stale` after a declared config-change event.

## Interpretation

This demonstrates package mechanics with synthetic records only. It does not establish live behavior of the referenced network controller or a real financial reconciliation process.
