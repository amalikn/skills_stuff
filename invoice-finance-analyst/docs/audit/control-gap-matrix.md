# Control Gap Matrix: Internal Invoice Analysis

## Contents

- [Scope](#scope)
- [Control matrix](#control-matrix)
- [Proposed finance-control checklist schema](#proposed-finance-control-checklist-schema)
- [Interpretation](#interpretation)

## Scope

This matrix records the controls that the current implementation either performs, performs incompletely, or lacks. It derives from local code and fixtures, not external accounting standards.
`Blocking` means a finance-control report must not claim completion while the gap remains.

## Control matrix

| ID | Control | Current state | Evidence | Gap | Risk | Severity | Blocking | Required remediation | Owner module |
|---|---|---|---|---|---|---|---|---|---|
| C-01 | Source file integrity | PARTIAL | Loader records SHA-256 | No immutable input manifest across all | Inputs cannot be | P1 | Yes | Record all inputs, | `load_inputs.py` |
|  |  |  |   before load; |   phases. |   tied to a |  |  |   mappings, hashes, and |  |
|  |  |  |   validator compares |  |   complete run. |  |  |   run ID in lineage. |  |
|  |  |  |   before/after. |  |  |  |  |  |  |
| C-02 | Source row identity | MISSING | Output rows omit source | No finding can trace to exact input | Reviewers cannot | P1 | Yes | Add immutable | `load_inputs.py` |
|  |  |  |   line number and row |   records. |   reperform |  |  |   source-row ID and |  |
|  |  |  |   ID. |  |   calculations. |  |  |   preserve it through |  |
|  |  |  |  |  |  |  |  |   joins. |  |
| C-03 | Mapping approval and | PARTIAL | YAML mapping is | Version, hash, date format, | A changed mapping | P1 | Yes | Persist mapping | `validate_inputs.py`, |
|  |   version |  |   explicit and required |   confidence, and transformation |   can silently |  |  |   identity and explicit |   `load_inputs.py` |
|  |  |  |   for loading. |   metadata are absent. |   change finance |  |  |   parsing options. |  |
|  |  |  |  |  |   results. |  |  |  |  |
| C-04 | Empty/malformed/encoding | PARTIAL | Missing files and | Empty CSV, malformed YAML, encoding | Partial or misread | P1 | Yes | Add validation gates | `validate_inputs.py` |
|  |   input fail-closed |  |   mapped bad |   errors, and unknown source type lack |   input can look |  |  |   and explicit error |  |
|  |  |  |   numeric/date values |   safe controlled outcomes. |   valid. |  |  |   status. |  |
|  |  |  |   fail in covered |  |  |  |  |  |  |
|  |  |  |   cases. |  |  |  |  |  |  |
| C-05 | Currency and tax state | MISSING | Ex-tax field names | No currency field enforcement, | Incomparable | P1 | Yes | Add source-level | validation + Phase 4b |
|  |  |  |   exist; optional GST |   tax-status classification, GST |   values can enter |  |  |   currency/tax status |  |
|  |  |  |   fields can load. |   reconciliation, credit, or reversal |   totals. |  |  |   and block |  |
|  |  |  |  |   logic. |  |  |  |   mixed/unknown state. |  |
| C-06 | Reconciliation join | FAIL | Outer merge has no | Ambiguous keys proceed as matched | Cartesian | P0 | Yes | Validate key | `invoice_analysis_skeleton.py` |
|  |   cardinality |  |   uniqueness |   rows. |   expansion |  |  |   cardinality; |  |
|  |  |  |   validation; synthetic |  |   inflates finance |  |  |   quarantine ambiguous |  |
|  |  |  |   one-to-many produced |  |   totals. |  |  |   candidates. |  |
|  |  |  |   two matches. |  |  |  |  |  |  |
| C-07 | Service-map reconciliation | FAIL | `service_map.parquet` | Internal and supplier IDs must already | False unmatched | P0 | Yes | Versioned map, | reconciliation |
|  |  |  |   loads but no analysis |   match. |   records and |  |  |   active/effective |  |
|  |  |  |   script reads it. |  |   omitted margins. |  |  |   status, coverage and |  |
|  |  |  |  |  |  |  |  |   ambiguity outputs. |  |
| C-08 | Period validity | PARTIAL | Primary reconciliation | No explicit | False matches and | P0 | Yes | Explicit date format | validation + reconciliation |
|  |  |  |   includes period |   period-end/overlap/billing-lag |   false |  |  |   and named |  |
|  |  |  |   start. |   policy; date parsing is ambiguous. |   non-matches. |  |  |   period-matching |  |
|  |  |  |  |  |  |  |  |   modes. |  |
| C-09 | Duplicate treatment | PARTIAL | Exact invoice | Sales duplicates are unchecked; | Charges can be | P0 | Yes | Duplicate queue and | reconciliation |
|  |  |  |   duplicates are |   removed invoice rows have no review |   hidden or |  |  |   disposition; reject |  |
|  |  |  |   removed and counted. |   table. |   matched many |  |  |   ambiguous keys. |  |
|  |  |  |  |  |   times. |  |  |  |  |
| C-10 | Rate-card eligibility | FAIL | Latest effective rate | No rate | Historical or | P0 | Yes | Select one period-valid | `rate_card_analysis.py` |
|  |  |  |   wins by service type. |   date/expiry/service/quantity/overlap |   incorrect rates |  |  |   rate or report |  |
|  |  |  |  |   control. |   create false |  |  |   no/ambiguous valid |  |
|  |  |  |  |  |   variances. |  |  |   rate. |  |
| C-11 | Margin semantics | PARTIAL | Implemented direct | Unsafe upstream joins; no credit, | Margin can be | P0 | Yes | Fix joins then classify | reconciliation + rate/trend |
|  |  |  |   margin is ex-tax |   rebate, tax, or zero-revenue status. |   materially |  |  |   inputs and |  |
|  |  |  |   revenue less invoice |  |   wrong. |  |  |   denominators. |  |
|  |  |  |   cost. |  |  |  |  |  |  |
| C-12 | Trend comparability | PARTIAL | Current/prior amounts | Service-only prior joins, no | Movement flags can | P0 | Yes | Cardinality-safe period | `trend_analysis.py` |
|  |  |  |   and flags are |   zero/null/negative/partial-period |   mislead or |  |  |   matching and |  |
|  |  |  |   deterministic. |   statuses. |   multiply |  |  |   comparability status. |  |
|  |  |  |  |  |   amounts. |  |  |  |  |
| C-13 | Deterministic severity | MISSING | Isolated labels and | No unified score, range, evidence, or | Prioritization | P1 | Yes | Implement documented | Phase 4c |
|  |  |  |   thresholds exist. |   review queue. |   changes with |  |  |   scoring with |  |
|  |  |  |  |  |   prose/model |  |  |   configurable source. |  |
|  |  |  |  |  |   behavior. |  |  |  |  |
| C-14 | Control totals and signoff | MISSING | Aggregate summaries | No source-to-output tie-out or result | No proof of | P1 | Yes | Add control totals and | Phase 4b |
|  |  |  |   exist. |   status. |   completeness. |  |  |   `run_signoff_status`. |  |
| C-15 | Output evidence and lineage | MISSING | File hashes and | No per-record lineage, calculation | Findings cannot be | P1 | Yes | Add a single run | all phases |
|  |  |  |   selected business |   IDs, output manifest, code version, |   audited or |  |  |   manifest and |  |
|  |  |  |   fields survive. |   or phase status. |   reproduced. |  |  |   reference columns. |  |
| C-16 | LLM numeric-claim grounding | FAIL | System prompt requires | Output writes arbitrary response text; | Narrative can | P0 | Yes | Structured response | `llm_analyst.py` |
|  |  |  |   citations. |   controlled mock wrote an uncited |   contradict |  |  |   plus citation and |  |
|  |  |  |  |   fabricated value. |   finance facts. |  |  |   numeric-claim |  |
|  |  |  |  |  |  |  |  |   validator, fail |  |
|  |  |  |  |  |  |  |  |   closed. |  |
| C-17 | Provider/privacy policy | WARNING | OpenAI-compatible | No redaction, endpoint allowlist, | Customer/service | P1 | Yes | Provider policy, | `llm_analyst.py` |
|  |  |  |   interface supports |   consent record, or safe offline |   data can leave |  |  |   redaction option, and |  |
|  |  |  |   local providers. |   error handling. |   the environment. |  |  |   explicit |  |
|  |  |  |  |  |  |  |  |   external-transfer |  |
|  |  |  |  |  |  |  |  |   status. |  |
| C-18 | Reproducibility/idempotency | PARTIAL | Fixture tables match | UUIDs/timestamps make bytes differ; | A reviewer cannot | P1 | Yes | Run-scoped directories, | all writers |
|  |  |  |   across two runs after |   fixed db paths permit |   identify an |  |  |   manifest, atomic |  |
|  |  |  |   excluding volatile |   mixed-generation outputs. |   exact immutable |  |  |   publish, stable |  |
|  |  |  |   metadata. |  |   result set. |  |  |   config digest. |  |
| C-19 | Dependency/configuration | WARNING | Governed venv works; | No manifest/lockfile; docs state | Rebuilds may vary. | P2 | No | Add a dependency | project root |
|  |   control |  |   `pip check` passes. |   3.14.4 but venv is 3.14.7. |  |  |  |   manifest and |  |
|  |  |  |  |  |  |  |  |   runtime-version |  |
|  |  |  |  |  |  |  |  |   verification. |  |

## Proposed finance-control checklist schema

The proposed table should be a deterministic, run-scoped parquet output. It should report one row per control evaluation and form an input to the LLM only after validation.

| Field                   | Purpose                                                               |
| ----------------------- | --------------------------------------------------------------------- |
| `run_id`                | Links the control result to an immutable run manifest.                |
| `control_id`            | Stable identifier such as `C-06`.                                     |
| `control_name`          | Human-readable control name.                                          |
| `status`                | `PASS`, `FAIL`, `WARNING`, `NOT_APPLICABLE`, `NOT_RUN`, or `BLOCKED`. |
| `severity`              | Deterministic `Critical`, `High`, `Medium`, or `Low`.                 |
| `blocking`              | Whether the control prevents finance-control completion.              |
| `affected_records`      | Count of input/output rows affected.                                  |
| `metric_name`           | Measured metric.                                                      |
| `metric_value`          | Measured numeric or enumerated value.                                 |
| `threshold_or_expected` | Rule used for evaluation.                                             |
| `delta`                 | Difference from the expected value where relevant.                    |
| `evidence_refs`         | Stable source/output/calculation references.                          |
| `owner_module`          | Producing module or stage.                                            |
| `notes`                 | Controlled explanatory text, not LLM reasoning.                       |

## Interpretation

**Observed fact.** C-06, C-07, C-08, C-09, C-10, C-11, C-12, and C-16 block finance-control use. The project can still provide analyst-facing exploratory tables if the output clearly marks
`FINANCE_CONTROL_INCOMPLETE` and retains the unresolved exception data.

**Recommendation.** Implement the checklist only after the core calculation defects are fixed. A checklist that merely reports known failures without preventing unsafe calculations would improve
disclosure but would not make the existing outputs finance-safe.
