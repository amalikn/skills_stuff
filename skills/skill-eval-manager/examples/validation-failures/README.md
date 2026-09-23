# Validation failures

These deliberately invalid fixtures demonstrate the five non-negotiable rejection paths. They are examples only and must never be copied into a project's suite.

Run the commands recorded in `evidence/validation-transcript-20260923_1148.md`. Each fixture must exit non-zero and name its specific violation.

## The fixtures

Each file below must FAIL `scripts/validate_suite.py`, **and must fail cleanly**. `just validate-negatives` asserts three things: the validator exits non-zero, it prints `INVALID:`, and it does
not print a `Traceback`. A fixture that starts passing is a validator regression, not a fixture to repair; a fixture that starts crashing is one too, and until 2026-09-23 the loop tested only
the exit code, so a crash was indistinguishable from a clean rejection.

Where a fixture has a `<name>.history.jsonl` sibling, the loop passes it with `--history`, so rejection paths that only run during history validation are covered.

| Fixture | Rejection path it proves |
|---|---|
| [bad-altitude.yaml](bad-altitude.yaml) | Evidence ranked below the claim it is offered for — a low-level acknowledgement standing in for a user-visible outcome. |
| [missing-oracle.yaml](missing-oracle.yaml) | No independent oracle declared, so nothing outside the system can confirm the result. |
| [no-falsifiability.yaml](no-falsifiability.yaml) | No falsifiability evidence, so the check has never been shown capable of failing. |
| [oracle-through-path.yaml](oracle-through-path.yaml) | The declared oracle routes through the path under evaluation — the system verifying itself. |
| [malformed-suite-block.yaml](malformed-suite-block.yaml) | A `suite` block that is a bare string instead of a mapping. Paired with [malformed-suite-block.history.jsonl](malformed-suite-block.history.jsonl) so history validation runs in the same pass — which is where it used to raise `AttributeError` instead of reporting the structural error. Found on first real use, 2026-09-23. |
| [recorded-stale.history.jsonl](recorded-stale.history.jsonl) | A history that records `stale` as an observed verdict, when `stale` is derived at read time and is not a recordable verdict. |
