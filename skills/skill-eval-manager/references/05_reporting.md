# Reporting and operations

## Contents

- [Report content](#report-content)
- [Recording](#recording)
- [Review cadence](#review-cadence)
- [Interpretation](#interpretation)

## Report content

Render reports from the suite and JSONL history. A report must identify its render time, eval id, population slice, derived state, recorded verdict where present, observation time, and reason. It must
state that `stale` and `not_evaluated` are derived. Never maintain a scorecard by hand.

## Recording

Validate the suite before recording. The executor/operator retains its raw output at the evidence reference. Record the result with the correct eval and slice, then validate the history. Record a
correction as a new line and reference the earlier observation with `supersedes`. Record a validity invalidation after an applicable declared change; do not silently delete or rewrite a previous pass.

## Review cadence

Set `max_age` according to the decision the evidence supports. A live safety claim may expire in minutes; a controlled design review might remain valid for months. Review definitions whenever the
claim, population source, oracle, layer, executor, or safety boundary changes.

## Interpretation

A `pass` is current only if it has not gone stale. A `fail` is useful evidence, not a reason to alter history. `inconclusive`, `error`, and `blocked` require different follow-up: improve the oracle,
repair the evaluator, or obtain authorized execution conditions. `not_evaluated` is absence, not a negative result.
