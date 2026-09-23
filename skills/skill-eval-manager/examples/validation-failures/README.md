# Validation failures

These deliberately invalid fixtures demonstrate the five non-negotiable rejection paths. They are examples only and must never be copied into a project's suite.

Run the commands recorded in `evidence/validation-transcript-20260923_1148.md`. Each fixture must exit non-zero and name its specific violation.

## The fixtures

Each file below must FAIL `scripts/validate_suite.py`. Run them with `just validate-negatives`, which fails the build if any of them is accepted — a fixture that starts passing is a validator
regression, not a fixture to repair.

| Fixture | Rejection path it proves |
|---|---|
| [bad-altitude.yaml](bad-altitude.yaml) | Evidence ranked below the claim it is offered for — a low-level acknowledgement standing in for a user-visible outcome. |
| [missing-oracle.yaml](missing-oracle.yaml) | No independent oracle declared, so nothing outside the system can confirm the result. |
| [no-falsifiability.yaml](no-falsifiability.yaml) | No falsifiability evidence, so the check has never been shown capable of failing. |
| [oracle-through-path.yaml](oracle-through-path.yaml) | The declared oracle routes through the path under evaluation — the system verifying itself. |
| [recorded-stale.history.jsonl](recorded-stale.history.jsonl) | A history that records `stale` as an observed verdict, when `stale` is derived at read time and is not a recordable verdict. |
