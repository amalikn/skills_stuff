# Test Coverage Audit: Internal Invoice Analysis

## Contents

- [Reproduced test state](#reproduced-test-state)
- [Configuration and discovery](#configuration-and-discovery)
- [Module assessment](#module-assessment)
- [Critical missing cases](#critical-missing-cases)
- [Fixture assessment](#fixture-assessment)
- [Controlled audit probes](#controlled-audit-probes)
- [Test strategy recommendation](#test-strategy-recommendation)

## Reproduced test state

| Item              | Result                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------ |
| Command           | `/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/python -m pytest -ra tests` |
| Python            | 3.14.7                                                                                                       |
| Dependency health | `pip check`: no broken requirements found                                                                    |
| Discovered        | 219                                                                                                          |
| Executed          | 219                                                                                                          |
| Passed            | 219                                                                                                          |
| Failed            | 0                                                                                                            |
| Skipped           | 0                                                                                                            |
| Xfail/xpass       | 0 / 0                                                                                                        |
| Pytest warnings   | 0                                                                                                            |
| Collection time   | 1.12 seconds                                                                                                 |
| Execution time    | 1.14 seconds                                                                                                 |

## Configuration and discovery

**Observed fact.** The repository has no `pyproject.toml`, `pytest.ini`, `tox.ini`, `setup.cfg`, requirements file, or lockfile. Pytest uses default discovery and the explicit `tests` path. The
absence of filters means the 219 collected tests are the complete current `tests/` suite, but not evidence of test completeness outside that directory.

**Observed fact.** `test_reconciliation.py`, `test_rate_card_analysis.py`, and `test_trend_analysis.py` read or create repository `db/` files. They skip only when selected inputs are absent. A clean
checkout test was not demonstrated because the fixtures do not bootstrap the full input graph within each test session.

## Module assessment

| Module                       | Covered behavior         | Financial invariants covered | Failure states covered     | Assessment | Major limitation                                                  |
| ---------------------------- | ------------------------ | ---------------------------- | -------------------------- | ---------- | ----------------------------------------------------------------- |
| `test_validate_inputs.py`    | Mapping presence, source | Mapped data remains          | Missing file, non-CSV      | ADEQUATE   | No                                                                |
|                              |   column existence,      |   source-unmodified; basic   |   extension, bad mapped    |            |   empty/malformed/encoding/currency/ambiguous-date/unknown-source |
|                              |   basic numeric/date     |   required fields parse.     |   numeric/date values.     |            |   tests.                                                          |
|                              |   validation,            |                              |                            |            |                                                                   |
|                              |   duplicates, read-only  |                              |                            |            |                                                                   |
|                              |   source hash,           |                              |                            |            |                                                                   |
|                              |   suggestions.           |                              |                            |            |                                                                   |
| `test_reconciliation.py`     | Fixture loading, exact   | Fixture totals and simple    | No key-missing, duplicate  | WEAK       | Assertions mirror the one-to-one fixture and accept duplicate     |
|                              |   duplicate removal,     |   direct margin/variance     |   sales, or join ambiguity |            |   removal.                                                        |
|                              |   exact-key outer join,  |   values.                    |   failures.                |            |                                                                   |
|                              |   summaries, output      |                              |                            |            |                                                                   |
|                              |   writing.               |                              |                            |            |                                                                   |
| `test_rate_card_analysis.py` | Single latest rate       | Ex-tax totals and low-margin | No no-rate, zero-rate,     | WEAK       | Tests certify the known period-unaware algorithm.                 |
|                              |   selection, variance,   |   flag on narrow examples.   |   multiple-rate, overlap,  |            |                                                                   |
|                              |   aggregate margins,     |                              |   expiry, or historical    |            |                                                                   |
|                              |   low-margin threshold,  |                              |   period state.            |            |                                                                   |
|                              |   output writing.        |                              |                            |            |                                                                   |
| `test_trend_analysis.py`     | Service-level MoM        | Fixture movement arithmetic  | No zero/null/negative      | WEAK       | Tests certify service-ID-only joins.                              |
|                              |   values, new/removed    |   and thresholds.            |   denominator, period      |            |                                                                   |
|                              |   labels, threshold      |                              |   boundary, rename,        |            |                                                                   |
|                              |   flags, prior margin    |                              |   duplicate, or            |            |                                                                   |
|                              |   movement, outputs.     |                              |   many-to-many cases.      |            |                                                                   |
| `test_llm_analyst.py`        | Markdown serialization,  | No authoritative numeric     | Missing parquet is         | WEAK       | No test rejects an uncited or fabricated LLM statement.           |
|                              |   context selection,     |   invariant.                 |   represented; transport   |            |                                                                   |
|                              |   prompt strings, mocked |                              |   errors/retries/output    |            |                                                                   |
|                              |   SDK parameters, report |                              |   validation are absent.   |            |                                                                   |
|                              |   writer.                |                              |                            |            |                                                                   |

## Critical missing cases

| Risk area                  | Required test                                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reconciliation cardinality | One-to-many, many-to-one, many-to-many, and duplicate keys must produce an ambiguity/control result, never matched financial rows.                                      |
| Service mapping            | Divergent `LOC…` and `SVC…` IDs, inactive map rows, duplicate map rows, missing maps, effective dates, and aliases.                                                     |
| Date semantics             | Explicit AU and US parsing, ambiguous short dates rejected without source format, period-end and partial-period behavior.                                               |
| Rate cards                 | Historical versus future rates, expiry, overlapping effective ranges, rate by service ID/speed/quantity, no rate, zero rate, and ambiguity.                             |
| Money/tax                  | Currency symbols, thousands separators, parentheses negatives, credits, reversals, zero values, tax-inclusive/exclusive mismatch, mixed currencies, and missing         |
|                            |   cost/revenue.                                                                                                                                                         |
| Trend comparability        | Zero/null/negative baseline, partial period, new/ceased/renamed services, duplicated period rows, and services with multiple line items.                                |
| Output integrity           | Control totals, row conservation, source-row lineage, schema validation, atomic writes, rerun behavior, and concurrent run isolation.                                   |
| LLM grounding              | Uncited text, nonexistent table/row IDs, incorrect cited values, invented numeric values, missing data state, API errors, unsupported response shape, and provider      |
|                            |   refusal.                                                                                                                                                              |
| Security/privacy           | Prompt redaction, local provider mode, remote-provider consent state, logs free of keys and raw data, and report failure behavior.                                      |

## Fixture assessment

**Observed fact.** Fixtures are small, synthetic, and useful for a deterministic smoke path: five current invoice rows, four current sales rows, one exact duplicate invoice row, a rate card with one
row per service type, a service map, and prior-period data. They establish expected nominal values independently enough for basic arithmetic assertions.

**Inference.** They lack realistic ambiguity. The service map is especially revealing: it maps `LOC…` supplier IDs to different `SVC…` internal IDs while the sales fixture uses `LOC…` values, which
lets the unimplemented service-map branch pass unnoticed. Rate cards have no historical rows or overlap. No fixture contains a tax-inclusive amount, currency field, zero denominator, credit,
duplicate sales record, or mapped alias.

## Controlled audit probes

| Probe                                                          | Result                                          | Interpretation                                    |
| -------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| One invoice row and two sales rows sharing the exact match key | `reconcile()` returned two matched rows.        | Confirms Cartesian expansion risk.                |
| 2025 matched line with 2024 and 2026 rates                     | Rate analysis selected the 2026 rate.           | Confirms rate-period defect.                      |
| Two prior invoices and two prior sales rows for one service    | Prior margin became 100 from four joined pairs. | Confirms trend Cartesian expansion.               |
| Mocked LLM output `Fabricated $999.`                           | Writer persisted it unchanged.                  | Confirms prompt-only Evidence Rule.               |
| Two full fixture runs in isolated temporary directories        | All non-volatile Phase 1B–3 DataFrames equal.   | Supports deterministic fixture calculations only. |

## Test strategy recommendation

1. Make tests self-contained. Each test must build its parquets in `tmp_path` from explicit fixtures and pass database/output paths rather than changing repository `db/`.
2. Add invariant tests before feature work: no ambiguous join may emit matched financial values; source-row count and amount conservation must reconcile through each stage.
3. Add property-style tables of date, tax, quantity, rate, and duplicate cases. Each expected result should be derived in the test from a compact fixture statement, not copied from production logic.
4. Add negative tests for every finance control. A failure must expose `BLOCKED`, `FAIL`, or `NOT_COMPARABLE`, rather than only returning an empty table or NaN.
5. Test an LLM validator as a pure deterministic component. Mocked model text should be rejected when citations fail resolution or reported numeric values differ from evidence.

**Recommendation.** Do not increase the 219 count by adding superficial unit tests. Replace the DB-coupled fixtures with isolated integration fixtures, then add the control-invariant tests that
currently have no representation.
