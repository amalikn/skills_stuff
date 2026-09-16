# Master Implementation Prompt — Business Intelligence Stack v2

## 1. Mission

Evolve the existing local `invoice-finance-analyst` project into a finance-control-safe analytical capability first, then use the proven architectural primitives from that project as the foundation for a broader local-first Business Intelligence skill ecosystem.

This is **not a greenfield build**.

Do not create a parallel finance framework.

Do not prematurely generalize the existing invoice project.

The implementation sequence is:

```text
Existing invoice-finance-analyst
            ↓
correct financial defects
            ↓
establish finance controls
            ↓
establish evidence / citation integrity
            ↓
establish lineage / reproducibility
            ↓
harden LLM reporting
            ↓
prove stability
            ↓
identify reusable primitives
            ↓
extract shared BI infrastructure
            ↓
build additional business skills
```

---

# 2. Current Baseline

The existing `invoice-finance-analyst` repository has been independently audited.

The reproduced state is:

```text
Python:       3.14.7
pytest:       219 collected
passed:       219
failed:       0
skipped:      0
warnings:     0

Overall verdict:
RUNNABLE / ANALYTIC USE ONLY
```

Do not interpret the passing suite as proof of financial correctness.

The current suite demonstrates that the existing nominal fixture pipeline behaves consistently.

It does not adequately validate the failure modes that matter for finance-control use.

---

# 3. Existing Architecture — Preserve by Default

The following existing design choices are considered sound starting points and must remain unless direct evidence demonstrates otherwise:

```text
plain Python
pandas-first calculations
Parquet intermediate/output tables
Markdown operational skill
provider-agnostic OpenAI-compatible LLM transport
deterministic phases separate from LLM reporting
offline deterministic operation
explicit mapping files
phase-oriented pipeline
```

Do NOT replace these merely to introduce a more fashionable framework.

Explicitly avoid during the remediation period:

```text
LangChain
LangGraph
LlamaIndex
vector databases
multi-agent swarms
microservices
MCP integration
new GUI
PostgreSQL
Redis
Kafka
framework rewrites
folder reorganizations
script renames
```

unless a specific approved requirement later justifies them.

---

# 4. Current Finance-Control Blockers

Treat the following as authoritative blocking classes.

## P0-01 — Reconciliation cardinality

Existing joins can multiply financial rows.

No ambiguous one-to-many, many-to-one, or many-to-many relationship may reach:

```text
cost
revenue
margin
variance
rate analysis
trend analysis
```

---

## P0-02 — Service-map reconciliation

The service map exists but is not currently incorporated into finance reconciliation.

Supplier and internal service identifiers may legitimately differ.

The system must not assume identical identifiers.

---

## P0-03 — Rate-card period validity

The existing rate resolver can select a future or otherwise period-invalid rate.

Every rate variance must reference exactly one eligible rate for the billing period.

---

## P0-04 — Date semantics

Short date strings may currently be interpreted ambiguously.

Date format must become explicit at mapping/input-contract level.

Ambiguous dates must fail closed.

---

## P0-05 — LLM numeric claim validation

The current LLM report writer can persist arbitrary model-generated numeric claims.

LLM text must never become an authoritative financial fact merely because it appears in a generated report.

---

## P0-06 — Prior-period margin cardinality

Prior-period margin joins can multiply rows.

Trend and margin movement must be subject to the same cardinality rules as current-period reconciliation.

---

# 5. Governing Principle

The core system invariant is:

```text
No uncertain financial relationship may silently become a calculated fact.
```

Examples:

```text
ambiguous join        → quarantine
multiple rates        → ambiguous_rate
missing rate          → no_period_valid_rate
unknown currency      → blocked / not comparable
unknown tax basis     → blocked / not comparable
ambiguous date        → reject
missing revenue       → missing
zero denominator      → not comparable
uncited LLM claim     → reject
```

Do not replace unknown states with:

```text
0
best guess
latest record
first matching record
most likely interpretation
```

---

# 6. Implementation Sequence

The existing remediation sequence is binding:

```text
Stage A — correctness
Stage B — controls
Stage C — evidence/citations
Stage D — lineage/reproducibility
Stage E — LLM hardening
Stage F — optional integration
```

Do not skip stages because later work appears easier.

Downstream controls must not be built on incorrect upstream financial semantics.

---

# 7. Stage A1 — Cardinality-Gated Service Reconciliation

This is the immediate implementation priority.

Target:

```text
cardinality-safe
service-map-aware
row-provenance-preserving reconciliation
```

Affected areas include:

```text
scripts/load_inputs.py
scripts/invoice_analysis_skeleton.py
scripts/trend_analysis.py
docs/data_contract.md
docs/output_schema.md
tests/
fixtures/
```

---

## 7.1 Source row identity

Every input row must receive an immutable source-row reference before joins occur.

Minimum concept:

```yaml
source_file:
source_file_hash:
source_row_number:
source_row_id:
```

Example conceptual identifier:

```text
SRC:<file-hash>:<row-number>
```

Do not rely on DataFrame index after transformations.

---

## 7.2 Reconciliation cardinality profiling

Before any financial join:

determine cardinality of the proposed key relationship.

Classify:

```text
ONE_TO_ONE
ONE_TO_MANY
MANY_TO_ONE
MANY_TO_MANY
DUPLICATE_SOURCE
UNMAPPED
CONFLICTING_MAP
INACTIVE_MAP
```

Only explicitly allowed relationships may proceed.

Initial finance-control rule:

```text
ONE_TO_ONE
```

may proceed directly.

All ambiguous relationships must be quarantined.

---

## 7.3 Terminal reconciliation status

Every source row must end in exactly one controlled terminal state.

Possible initial taxonomy:

```text
MATCHED
INVOICE_ONLY
SALES_ONLY
UNMAPPED_SERVICE
AMBIGUOUS_MAPPING
DUPLICATE_INVOICE
DUPLICATE_SALES
ONE_TO_MANY
MANY_TO_ONE
MANY_TO_MANY
INACTIVE_MAPPING
CONFLICTING_MAPPING
PERIOD_MISMATCH
BLOCKED
```

Do not permit the same authoritative source row to be counted in multiple terminal financial states.

---

## 7.4 Row-conservation invariant

Introduce a deterministic invariant equivalent to:

```text
source rows
=
matched
+ unmatched
+ duplicate/disposition
+ ambiguous
+ blocked
```

Adapt appropriately for each source type.

No financial row may disappear without disposition.

No row may multiply without an explicitly controlled relationship.

---

# 8. Service Map Design

The service map must become an authoritative reconciliation input where configured.

It should support at least:

```yaml
supplier_service_id:
internal_service_id:
active:
effective_from:
effective_to:
mapping_version:
mapping_source:
```

Potential later support:

```text
alias
description
location
service subtype
manual override
```

but do not implement speculative fields without an actual requirement.

---

## 8.1 Service-map rules

Must detect:

```text
missing mapping
duplicate active mapping
conflicting mapping
inactive mapping
overlapping mapping validity
unmapped identifier
```

Do not arbitrarily choose the first mapping.

---

# 9. Stage A2 — Explicit Date and Period Semantics

A mapping must specify date interpretation where source data is not unambiguous ISO format.

For example:

```yaml
billing_period_start:
  source: "Period Start"
  type: date
  format: "%d/%m/%Y"
```

or:

```yaml
format: "%m/%d/%Y"
```

Do not silently interpret ambiguous text such as:

```text
03/01/2026
```

without source-specific configuration.

---

## 9.1 Named period matching modes

Define explicit period semantics.

Potential initial modes:

```text
EXACT_PERIOD
CALENDAR_MONTH
OVERLAP
BILLING_LAG
```

Each non-exact match must record:

```text
period_match_type
period_match_status
```

Do not hide relaxed matching.

---

# 10. Stage A3 — Period-Valid Rate Resolution

Rate resolution must use the governed billing period.

A rate is eligible only if required dimensions match and its validity window covers the applicable billing date/period.

Conceptually:

```text
effective_from <= billing_date
AND
(
    effective_to IS NULL
    OR billing_date <= effective_to
)
```

Additional dimensions may include:

```text
service
service type
quantity band
product class
location
speed
```

but only when defined by the actual rate contract.

---

## 10.1 Required outcomes

Exactly one valid rate:

```text
VALID_RATE
```

None:

```text
NO_PERIOD_VALID_RATE
```

Multiple:

```text
AMBIGUOUS_RATE
```

Do not resolve ambiguity using:

```text
latest row
first row
highest rate
lowest rate
```

unless an explicit governed business rule later defines such behaviour.

---

# 11. Stage B1 — Money Semantics

Before expanding finance analytics, explicitly classify:

```text
currency
tax basis
charge type
sign semantics
quantity
unit price
credits
reversals
```

Financial calculation must distinguish:

```text
tax exclusive
tax inclusive
unknown tax basis
```

and:

```text
charge
credit
reversal
adjustment
```

---

## 11.1 Currency

Never combine values across currencies without an explicit configured conversion process.

If currencies differ and no approved conversion exists:

```text
NOT_COMPARABLE
```

or:

```text
BLOCKED
```

must result.

---

## 11.2 Zero and missing denominators

Percentage calculations must explicitly handle:

```text
0
NULL
negative values
missing values
```

Do not emit misleading:

```text
inf
-inf
NaN interpreted as zero
```

into finance reports.

Use controlled states such as:

```text
NOT_COMPARABLE
UNDEFINED
MISSING_INPUT
```

---

# 12. Stage B2 — Finance-Control Framework

Only after Stage A and money semantics are stable, introduce deterministic controls.

Create run-scoped outputs including:

```text
control_totals
finance_control_checklist
run_signoff_status
```

Each control evaluation should support:

```yaml
run_id:
control_id:
control_name:
status:
severity:
blocking:
affected_records:
metric_name:
metric_value:
threshold_or_expected:
delta:
evidence_refs:
owner_module:
notes:
```

Allowed control status:

```text
PASS
FAIL
WARNING
NOT_APPLICABLE
NOT_RUN
BLOCKED
```

---

# 13. Finance-Control Completion

Define a controlled run-level status.

Example:

```text
FINANCE_CONTROL_COMPLETE
FINANCE_CONTROL_INCOMPLETE
FINANCE_CONTROL_BLOCKED
ANALYTIC_ONLY
```

A successful script exit is NOT equivalent to finance-control completion.

The run can execute successfully while remaining:

```text
FINANCE_CONTROL_BLOCKED
```

---

# 14. Control Totals

Implement source-to-output tie-outs.

At minimum track:

```text
source row count
normalized row count
matched row count
unmatched row count
blocked row count
duplicate/disposition count
source amount
included amount
excluded amount
blocked amount
```

The system must be able to explain where every source row and material amount went.

---

# 15. Stage B3 — Deterministic Severity

Severity must not be decided by an LLM.

One versioned configuration must own:

```text
formula
component weights
thresholds
boundary behaviour
missing-data handling
```

Every severity label must be explainable through deterministic inputs.

Possible output:

```yaml
finding_id:
severity_score:
severity:
components:
  financial_value:
  recurrence:
  confidence:
  control_failure:
threshold_version:
```

Do not adopt a scoring formula merely because one exists in documentation.

First verify the intended formula against current use cases and governance.

---

# 16. Stage C1 — Evidence Model

Every material numeric result must be traceable.

Target chain:

```text
source file
    ↓
source row
    ↓
mapping
    ↓
normalized value
    ↓
join/match
    ↓
calculation
    ↓
finding
    ↓
report claim
```

Minimum reusable evidence concepts:

```text
SourceRef
MappingRef
CalculationRef
FindingRef
EvidenceRef
```

Do not extract these into a general shared library yet.

Implement them inside the invoice project first.

---

# 17. Calculation Identity

Every material deterministic calculation should ultimately expose:

```yaml
calculation_id:
calculator:
calculator_version:
input_refs:
result:
units:
```

A reviewer must be able to determine:

```text
Where did this value come from?
Which source rows contributed?
Which rule produced it?
Which code/config version applied?
```

---

# 18. Stage C2 — LLM Citation Validator

The current prompt-level citation requirement is insufficient.

Introduce a deterministic validator.

A governed LLM claim is valid only if:

```text
citation syntax is valid
referenced artifact exists
referenced row/finding exists
reported numeric value matches evidence
claim semantics are compatible with evidence
```

For governed reports:

```text
invalid numeric citation
uncited numeric claim
fabricated value
missing evidence
```

must cause validation failure.

---

# 19. Structured Analyst Output

Replace unrestricted governed report output with a structured intermediate representation.

Conceptually:

```yaml
summary:
findings:
  - claim:
    evidence_refs:
    confidence:
suspected_causes:
  - statement:
    evidence_refs:
recommended_checks:
data_gaps:
```

The LLM may:

```text
summarize
group
explain
prioritize
rewrite
```

It must not:

```text
invent calculations
change deterministic values
create authoritative uncited numbers
silently resolve missing data
```

Rendering Markdown should occur only after structured validation.

---

# 20. Stage D — Run Lineage

Introduce one run-level manifest.

Example conceptual schema:

```yaml
run_id:
started_at:
completed_at:
status:

code:
  commit:
  version:

runtime:
  python:
  dependencies_digest:

inputs:
  - path:
    sha256:
    mapping_digest:

config_digest:

phases:
  validation:
  loading:
  reconciliation:
  rate_analysis:
  trend_analysis:
  controls:
  llm_analysis:

outputs:
  - path:
    sha256:
```

Do not create multiple competing provenance systems.

---

# 21. Atomic Run Publishing

Stop treating mutable repository-wide `db/` output as the identity of a run.

Move toward:

```text
runs/
└── <run_id>/
    ├── db/
    ├── output/
    └── lineage.json
```

or an equivalent structure consistent with existing project constraints.

Write a run into an isolated location.

Only expose it as complete after all required stages and control checks finish successfully.

Do not mix generations.

---

# 22. Dependency Reproducibility

Introduce one machine-readable dependency source.

Possible implementation:

```text
pyproject.toml
```

if compatible with current repository conventions.

Pin or constrain dependencies appropriately.

Resolve the current documented runtime mismatch:

```text
documented: Python 3.14.4
actual audited venv: Python 3.14.7
```

The project must have one authoritative runtime policy.

---

# 23. Stage E — LLM Provider Policy

Preserve provider-agnostic transport.

Add provider governance around it.

Record:

```text
provider
endpoint
model
local_or_remote
data_transfer_allowed
redaction_policy
consent_state
```

Remote provider use must not be equivalent to local deterministic analysis.

The deterministic pipeline must remain usable without network or LLM access.

---

# 24. Tests — New Priority

Do not optimize for increasing test count.

Optimize for invariant coverage.

The existing 219 tests are a baseline, not a target.

First create self-contained fixtures that build required input artifacts under temporary paths.

Tests should not rely on mutable repository `db/` state.

---

# 25. Mandatory A1 Tests

Before accepting Stage A1, test:

```text
one-to-one
one-to-many
many-to-one
many-to-many
duplicate invoice
duplicate sales
divergent supplier/internal IDs
missing map
duplicate map
inactive map
conflicting map
```

Required invariant:

```text
No ambiguous relationship emits matched authoritative financial rows.
```

Also test row and amount conservation.

---

# 26. Mandatory Date Tests

Test:

```text
ISO date
AU short date with explicit format
US short date with explicit format
ambiguous short date without format
invalid date
period boundary
partial period
overlap
billing lag
```

Ambiguous input without explicit format must fail.

---

# 27. Mandatory Rate Tests

Test:

```text
historical rate
current rate
future rate
expired rate
open-ended rate
overlapping rates
no rate
zero rate
service-specific rate
quantity-specific rate
```

Expected outcome must be derived independently in tests.

Do not encode production implementation logic into the expected-value calculation.

---

# 28. Mandatory Financial Semantic Tests

Add coverage for:

```text
tax inclusive
tax exclusive
unknown tax state
credit
reversal
negative value
zero revenue
missing revenue
zero cost
missing cost
mixed currency
currency symbols
thousands separators
parentheses negatives
```

---

# 29. Mandatory LLM Safety Tests

Test a mocked model producing:

```text
uncited number
wrong citation
nonexistent finding ID
correct citation but wrong value
fabricated number
missing required section
invalid response schema
```

All must fail governed validation where appropriate.

Also test:

```text
valid fully cited response
```

---

# 30. Governance Ownership

Do not allow the same financial rule to have multiple authoritative implementations.

Use the following ownership model unless existing governance explicitly requires otherwise:

```text
Data semantics
→ docs/data_contract.md

Join/cardinality rules
→ docs/data_contract.md + executable implementation

Output schema
→ docs/output_schema.md

Workflow/user-facing rules
→ SKILL.md

Architectural invariants
→ ARCHITECTURE.md

Roadmap / implementation status
→ ROADMAP.md

Executable thresholds
→ versioned configuration

Tests
→ verify all of the above
```

Scripts should consume governed configuration rather than independently repeating thresholds.

---

# 31. Correct Existing Governance Drift

Known governance inconsistencies must be corrected as part of the relevant remediation stage, not through wholesale documentation rewrite.

In particular:

### Variance semantics

The current data contract disagrees with code/output/tests over `variance_abs`.

Determine and establish one canonical definition.

Do not maintain both definitions under the same field name.

### Severity

Documentation currently describes deterministic severity partly as though implemented while roadmap correctly records it as pending.

Clarify current versus target state.

### Mapping

Documentation promises candidate/confidence behaviour not implemented by current heuristic mapping suggestion.

Either implement it at the relevant stage or correctly label it as future behaviour.

---

# 32. Definition of Finance-Control Candidate

Do not call the invoice project finance-control ready merely when Stage A is complete.

Minimum candidate state requires:

```text
cardinality-safe reconciliation
service-map reconciliation
explicit date semantics
period-valid rate resolution
money/tax comparability controls
control totals
blocking finance-control checklist
deterministic severity
row-level evidence
citation validation
immutable run lineage
phase completion status
LLM governed-output validation
```

Only then assess whether:

```text
FINANCE_CONTROL_READY
```

is justified.

---

# 33. No Shared BI Framework Yet

Do NOT presently create:

```text
business-intelligence/shared/
```

or move invoice internals into a common package.

The invoice project is still discovering the right interfaces.

Premature extraction will freeze incorrect abstractions.

---

# 34. Extraction Gate

Shared infrastructure may be considered only after:

1. Stages A–E pass their acceptance criteria.
2. Invoice analysis has run successfully on realistic controlled datasets.
3. Evidence/provenance interfaces remain stable.
4. At least one second business skill demonstrates genuine reuse need.

Only then evaluate extraction.

---

# 35. Candidate Reusable Primitives

After the extraction gate, assess these for generalization:

```text
Money
EvidenceRef
SourceRef
CalculationRef
FindingRef
run manifest
control evaluation
severity framework
LLM structured-output validation
provider abstraction
citation validator
configuration/version digest
```

Do not assume every invoice primitive is generic.

---

# 36. Invoice-Specific Logic Must Remain Domain-Specific

These should normally remain within `internal-invoice-analysis`:

```text
invoice schema
sales-billing schema
rate cards
service maps
invoice/sales matching
invoice duplicate policy
billing-period matching
supplier charge reconciliation
invoice trend rules
```

Do not pollute generic infrastructure with invoice terminology.

---

# 37. Future Business Intelligence Architecture

After the invoice control foundation is proven, the target may evolve toward:

```text
business-intelligence/
│
├── shared/
│   ├── evidence/
│   ├── provenance/
│   ├── controls/
│   ├── calculations/
│   ├── llm/
│   └── reporting/
│
└── skills/
    ├── internal-invoice-analysis/
    ├── unit-economics/
    ├── cash-flow/
    ├── scenario-analysis/
    ├── model-auditor/
    ├── market-research/
    ├── competitor-analysis/
    ├── decision-memo/
    ├── listing-generator/
    ├── listing-validator/
    └── business-pulse/
```

This is a target hypothesis, not authorization to restructure the repository now.

---

# 38. External FOSS Skill Sources — Use Later

After invoice controls are stable, evaluate and selectively adapt methodology from:

```text
Anthropic knowledge-work-plugins
Anthropic financial-services
OpenBusiness
Enthusiast
```

Do not import these during Stage A–E remediation.

The first priority is to make the existing internal financial pipeline correct.

---

# 39. Future Finance Skills

After the extraction gate, prioritize:

```text
unit-economics
cash-flow
scenario-analysis
model-auditor
```

These should reuse proven:

```text
Money
evidence
provenance
controls
calculation identity
LLM validation
run status
```

but implement their own domain calculations.

---

# 40. Future Business Analysis Skills

Then implement:

```text
market-research
competitor-analysis
decision-memo
```

Use explicit claim states:

```text
VERIFIED
INFERRED
ASSUMED
MISSING
CONFLICTING
STALE
```

These claim states are separate from finance-control statuses.

Do not conflate:

```text
claim confidence
```

with:

```text
financial control PASS/FAIL
```

---

# 41. Future Listing Skills

Later implement:

```text
listing-generator
listing-validator
```

against a canonical product record.

The generator may change prose.

The validator controls facts.

No generated listing becomes publishable when it contains:

```text
invented features
unsupported specifications
price mismatch
model mismatch
odometer mismatch
unsupported superlatives
missing governed disclosures
```

---

# 42. Future Business Pulse

`business-pulse` should be built only after authoritative sources exist for the relevant metrics.

It should summarize rather than manufacture management data.

Conceptually:

```text
accounting/finance outputs
inventory
sales
pipeline
business controls
        ↓
business-pulse
        ↓
management summary
```

Missing metrics should remain:

```text
N/A
UNKNOWN
NOT_AVAILABLE
```

---

# 43. AI Architecture

Do not create one autonomous agent for every skill.

Target:

```text
Primary orchestrator
      │
      ├── invoice analysis
      ├── finance skills
      ├── business analysis
      ├── listing skills
      └── management skills
```

Separate processes/agents only where justified by:

```text
permissions
model choice
independent validation
security boundary
long-running execution
```

The model auditor or financial validator may eventually justify separation.

---

# 44. Deterministic / LLM Boundary

Across the eventual BI system:

```text
LLM:
research
classification
summarization
interpretation
drafting
prioritization

Deterministic code:
money
totals
rates
margin
ROI
cash flow
scenario tables
control states
severity where governed
citation validation
lineage
```

Never use the LLM as the sole calculator for authoritative financial output.

---

# 45. Immediate Task

Do **Stage A1 only**.

Do not proceed to later stages in the same implementation cycle.

Implement:

```text
cardinality-gated
service-map-aware
row-provenance-preserving
reconciliation
```

Requirements:

1. Preserve immutable source-row identity.
2. Profile reconciliation-key cardinality before joining.
3. Integrate active service-map resolution.
4. Prevent all ambiguous relationships from producing matched financial values.
5. Produce explicit terminal reconciliation statuses.
6. Ensure every source row receives exactly one controlled disposition.
7. Add row-count and financial-amount conservation tests.
8. Add one-to-one, one-to-many, many-to-one, many-to-many tests.
9. Add duplicate invoice and duplicate sales tests.
10. Add missing/duplicate/inactive/conflicting service-map tests.
11. Update only governance documents directly affected by A1.
12. Do not implement A2 or later stages.

---

# 46. A1 Acceptance Gate

A1 is complete only when:

```text
No ambiguous join reaches:
    margin
    variance
    rate analysis
    trend analysis
```

and:

```text
every source row
→ one traceable terminal reconciliation status
```

and:

```text
row conservation passes
amount conservation passes
all existing applicable tests pass
all new A1 control tests pass
```

---

# 47. Required A1 Completion Report

At completion report:

```text
FILES CHANGED

TEST RESULT

NEW TESTS

CARDINALITY RULES

SERVICE-MAP RULES

TERMINAL STATUSES

ROW CONSERVATION RESULT

AMOUNT CONSERVATION RESULT

KNOWN LIMITATIONS

GOVERNANCE CHANGES

NEXT UNBLOCKED STAGE
```

Clearly distinguish:

```text
implemented
tested
documented
still pending
```

Do not call the project finance-control ready.

The expected next stage after successful A1 is:

```text
A2 — explicit date and period semantics
```