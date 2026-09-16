# Audit Prompt — Existing `internal-invoice-analysis` Skill

## Objective

Perform a **strict implementation audit** of the existing local project:

```text
internal-invoice-analysis
```

This is **not a greenfield build**.

Do not redesign or rewrite the project until the current implementation has been fully inspected, tested, and compared against its own governance and stated architecture.

The goal is to determine:

1. What is actually implemented
2. What is only documented
3. What is incomplete
4. What is incorrect
5. What is duplicated or contradictory
6. What is unsafe for finance-control use
7. What should remain unchanged
8. What should be corrected before further feature development
9. Whether this project should become the finance foundation for a wider Business Intelligence skill stack

---

# 1. Current Declared State

The project claims:

```text
Phase 4 runnable — not finance-control complete
```

Reported implementation:

```text
Phase 0   SKILL.md
Phase 1A  input validation + data contract
Phase 1B  loading + reconciliation
Phase 2   rate-card analysis
Phase 3   trend analysis
Phase 4   provider-agnostic LLM analyst
Phase 5   accounting-system MCP backlog
```

Reported test state:

```text
219 / 219 tests passing
```

Reported known gaps:

```text
finance_control_checklist.parquet
citation validator
deterministic severity scoring
lineage.json append
phase-status marker
service-map reconciliation
```

Do NOT assume these claims are correct.

Verify them from code and tests.

---

# 2. Governance Hierarchy

Inspect governance in this order:

```text
1. AGENTS.md
2. AI_NAVIGATION.md
3. context-map.yaml
4. ARCHITECTURE.md
5. SKILL.md
6. ROADMAP.md
7. SETUP.md
8. scripts/README.md
9. CHANGELOG.md
10. parent ../AGENTS.md
```

Also inspect any referenced canonical governance material that is locally available and explicitly applicable.

Determine:

- which document owns architecture
- which document owns workflow semantics
- which document owns data contracts
- which document owns severity logic
- which document owns evidence rules
- which document owns roadmap/status
- whether ownership is clear or duplicated

Do not silently choose between conflicting governance documents.

Record all conflicts.

---

# 3. Audit Rules

## Hard rule 1 — inspect before editing

Do not modify any file during the initial audit.

## Hard rule 2 — code beats status prose

If README/ROADMAP says a feature exists but code does not implement it, classify it as:

```text
DOCUMENTED_ONLY
```

If code implements behaviour that is not governed/documented, classify it as:

```text
UNGOVERNED_IMPLEMENTATION
```

## Hard rule 3 — tests do not prove correctness

Passing tests prove conformance to the test suite, not financial correctness.

Audit:

```text
implementation
tests
fixtures
governance
financial semantics
```

independently.

## Hard rule 4 — no external research

Do not browse the web.

Use only local project content and supplied fixtures.

## Hard rule 5 — preserve financial uncertainty

Do not invent:

```text
column meanings
tax treatment
rate semantics
service relationships
business mappings
missing costs
severity thresholds
```

Mark unresolved semantics explicitly.

---

# 4. First Deliverable — Actual Project Inventory

Produce a complete relevant directory tree.

Classify every significant file as one of:

```text
GOVERNANCE
IMPLEMENTATION
TEST
FIXTURE
REFERENCE
GENERATED
LEGACY
UNKNOWN
```

Pay particular attention to:

```text
SKILL.md
ARCHITECTURE.md
ROADMAP.md
scripts/*
tests/*
docs/*
examples/*
templates/*
db/*
output/*
```

Identify:

- files referenced by governance that do not exist
- files that exist but are undocumented
- stale files
- apparent superseded implementations
- duplicate ownership of the same rule

---

# 5. Validate Claimed Test State

Use the project's documented Python environment.

Confirm:

```text
python version
dependency state
pytest configuration
test count
pass/fail/skip/xpass state
warnings
```

Run the complete relevant suite.

Do not stop at:

```bash
pytest tests/
```

Also inspect:

```text
pyproject.toml
pytest.ini
tox.ini
setup.cfg
requirements*
```

for exclusions or filtering.

Report:

```text
discovered tests
executed tests
passed
failed
skipped
warnings
```

If 219/219 does not reproduce, identify precisely why.

---

# 6. Test Quality Audit

For each test module:

```text
test_validate_inputs.py
test_reconciliation.py
test_rate_card_analysis.py
test_trend_analysis.py
test_llm_analyst.py
```

determine:

1. What behaviour is covered
2. What financial invariants are tested
3. What edge cases are missing
4. Whether tests merely mirror implementation
5. Whether expected values were independently derived
6. Whether fixtures contain realistic ambiguity
7. Whether tests exercise failure states

Specifically check for missing tests around:

```text
duplicate invoice lines
duplicate sales lines
one-to-many mappings
many-to-one mappings
missing rate-card rows
multiple valid rates
overlapping effective periods
tax-inclusive vs tax-exclusive amounts
negative adjustments
credits
zero-value lines
currency symbols
thousands separators
rounding
date boundary issues
partial-period billing
service renames
service-map ambiguity
duplicate service identifiers
missing revenue
missing cost
negative margin
very low margin
mixed currencies
schema drift
column aliases
bad encodings
empty files
unexpected nulls
```

Classify test coverage:

```text
STRONG
ADEQUATE
WEAK
MISSING
```

---

# 7. Architecture Conformance Audit

Compare actual code against `ARCHITECTURE.md`.

For every declared pipeline layer, produce:

| Layer | Declared | Implemented | Tested | Finance-safe | Notes |
|---|---:|---:|---:|---:|---|

Audit all claimed layers, including:

```text
input/schema
normalization
reconciliation
rate validation
margin
trend
anomaly
severity
evidence
LLM interpretation
reporting
lineage
control/checklist
```

Highlight architectural drift.

---

# 8. SKILL.md Audit

Treat `SKILL.md` as an operational contract.

Verify the declared 15-step workflow against implementation:

```text
1. Input inventory
2. Schema detection
3. Column mapping
4. Data quality checks
5. Invoice normalization
6. Sales/revenue normalization
7. Rate-card matching
8. Reconciliation
9. Variance analysis
10. Margin/profitability analysis
11. Anomaly detection
12. Root-cause grouping
13. Executive summary
14. Evidence table
15. Open questions / missing data
```

For each step classify:

```text
IMPLEMENTED
PARTIAL
DOCUMENTED_ONLY
NOT_IMPLEMENTED
```

Also verify hard rules:

```text
no external financial data by default
no invented values
no guessed column meanings
mapping requested only when needed
deterministic calculations preferred
facts separated from interpretation
assumptions recorded
```

Check whether the code can violate these rules despite the prompt text.

---

# 9. Input Validation Audit

Audit:

```text
scripts/validate_inputs.py
```

Verify:

```text
multiple CSV support
missing-file handling
non-CSV rejection
row counts
column inventory
null counts
duplicate counts
numeric-looking detection
date-looking detection
encoding handling
empty CSV behaviour
malformed CSV behaviour
mapping suggestions
read-only behaviour
```

Determine whether:

```text
numeric-looking
date-looking
schema detection
```

are deterministic and conservative.

Flag any heuristic that can silently reinterpret business data.

---

# 10. Data Contract Audit

Audit:

```text
docs/data_contract.md
```

against actual code.

For all source types:

```text
supplier invoice
sales billing
rate card
service map
prior-period inputs
profitability/export inputs if supported
```

verify:

```text
required columns
optional columns
derived columns
types
keys
cardinality assumptions
nullability
date semantics
money semantics
tax semantics
identifier semantics
mapping behaviour
```

Look specifically for undocumented assumptions around join keys.

A financial reconciliation system MUST explicitly define:

```text
business key
technical key
join cardinality
fallback matching
duplicate handling
unmatched handling
```

Flag any implicit joins.

---

# 11. Loader Audit

Audit:

```text
scripts/load_inputs.py
```

Check:

```text
CSV ingestion
mapping application
normalization
schema validation
Parquet generation
type coercion
source preservation
row identity
lineage metadata
failure behaviour
```

Critical requirement:

Every transformed row should remain traceable to the original source row.

Determine whether the loader preserves:

```text
source file
source row
original value
normalized value
mapping used
transformation
```

where required.

---

# 12. Reconciliation Audit

Audit:

```text
invoice_analysis_skeleton.py
```

or the current reconciliation implementation if renamed.

Examine:

```text
invoice → sales
invoice → rate card
invoice → service map
sales → service map
```

Check matching logic for:

```text
exact match
fallback match
one-to-one
one-to-many
many-to-one
many-to-many
unmatched
ambiguous
duplicate
```

A many-to-many financial join must never silently proceed as though it were one-to-one.

Confirm whether row multiplication can inflate:

```text
cost
revenue
margin
variance counts
```

Add a specific audit for accidental Cartesian expansion.

---

# 13. Rate-Card Analysis Audit

Audit:

```text
rate_card_analysis.py
```

Verify:

```text
expected rate selection
effective-date handling
actual rate calculation
rate variance
absolute variance
percentage variance
margin
low-margin classification
exception output
```

Determine what occurs when:

```text
no rate exists
multiple rates apply
rate effective period overlaps
rate is zero
actual usage is zero
quantity is missing
tax treatment differs
service mapping is ambiguous
```

Do not accept "best effort" matching without visible status.

---

# 14. Margin Semantics Audit

This is high priority.

Find the exact definition of:

```text
revenue
cost
margin
margin %
```

Verify whether the code consistently uses:

```text
revenue_ex_tax - cost_ex_tax
```

or another governed definition.

Check for accidental mixing of:

```text
tax-inclusive revenue
tax-exclusive cost
gross revenue
net revenue
credits
discounts
rebates
one-off charges
```

Every margin metric must have one canonical definition.

If definitions differ between scripts, report a P0 defect.

---

# 15. Trend Analysis Audit

Audit:

```text
trend_analysis.py
```

Verify:

```text
period definition
prior-period alignment
service matching between periods
MoM calculations
absolute movement
percentage movement
spike detection
recurring changes
margin movement
new services
ceased services
```

Check denominator behaviour.

Percentage variance must not silently generate misleading results where the baseline is:

```text
0
null
negative
very small
```

Require explicit status such as:

```text
NOT_COMPARABLE
NEW
CEASED
UNDEFINED
```

where appropriate.

---

# 16. Anomaly Detection Audit

Identify whether anomaly detection is:

```text
deterministic
statistical
threshold-based
LLM-derived
```

For each anomaly type record:

```text
input
calculation
threshold
severity
evidence
```

Flag any anomaly label whose underlying logic exists only inside an LLM prompt.

Financial exceptions must be reproducible.

---

# 17. Severity Model Audit

The project states deterministic severity scoring is pending.

Verify this.

Find all current severity labels such as:

```text
critical
high
medium
low
warning
```

Determine whether severity is currently assigned by:

```text
hardcoded deterministic logic
configurable deterministic logic
LLM reasoning
template wording
manual classification
```

Any LLM-only severity assignment is not finance-control grade.

Recommend a canonical deterministic severity model, but do not implement it during the audit.

---

# 18. Evidence Rule Audit

Find the exact Evidence Rule.

Trace how evidence flows from:

```text
source CSV
→ normalized row
→ calculation
→ finding
→ LLM prompt
→ analyst report
```

For each finding, determine whether the system can identify:

```text
source file
source row
calculation
intermediate table
result
report claim
```

The final report must not contain a numeric claim without traceable evidence.

---

# 19. Citation Validator Gap

The project states citation validation is pending.

Assess what "citation" currently means.

Determine whether the LLM report references:

```text
table names
row IDs
source files
record IDs
finding IDs
calculation IDs
```

Design the audit criteria for a citation validator:

A cited claim is valid only when:

```text
reference exists
referenced record exists
reported value matches record
claim semantics match evidence
source lineage is preserved
```

Report current gaps.

---

# 20. LLM Analyst Audit

Audit:

```text
llm_analyst.py
```

Provider abstraction:

```text
OpenAI
Anthropic
DeepSeek
OpenAI-compatible
other supported providers
```

Check:

```text
API isolation
offline behaviour
prompt construction
evidence packaging
token limits
structured output
retry behaviour
error handling
mocking
provider-specific assumptions
```

Most importantly verify:

**Can the LLM introduce a numeric value that does not exist in deterministic outputs?**

If yes, flag as finance-control defect.

The LLM should ideally be restricted to:

```text
summarization
grouping
interpretation
prioritization
wording
```

not authoritative calculation.

---

# 21. Anti-Hallucination Audit

Actively attempt to break the Evidence Rule using local test inputs.

Test cases should include:

```text
missing margin data
conflicting rates
unmapped service
missing sales record
ambiguous service mapping
missing prior period
unavailable trend
null cost
null revenue
```

Determine whether the LLM:

```text
states UNKNOWN
states N/A
asks for data
```

or invents a plausible explanation/value.

---

# 22. Lineage Audit

The roadmap says:

```text
lineage.json append + phase-status marker
```

is pending.

Audit every script for existing provenance fields.

Determine whether pipeline artifacts can currently answer:

```text
Which script produced this?
Which version?
Which inputs?
Which mappings?
Which upstream tables?
At what time?
Using which config?
Was the phase complete or partial?
```

Recommend the minimal canonical lineage schema.

Do not create parallel lineage mechanisms if one already exists.

---

# 23. Phase Status Audit

Check whether outputs clearly state their completeness.

For example:

```text
RECONCILIATION_COMPLETE
RATE_ANALYSIS_COMPLETE
TREND_NOT_RUN
LLM_REPORT_COMPLETE
FINANCE_CONTROL_INCOMPLETE
```

A report must not look finance-control complete merely because Phase 4 ran successfully.

Audit whether this ambiguity exists today.

---

# 24. Service-Map Reconciliation Audit

The roadmap identifies this as pending.

Determine:

- current role of `service_map`
- whether it is required or optional
- what entities it maps
- expected cardinality
- effective dates
- alias support
- duplicate handling
- unresolved mapping behaviour

Assess whether the absence of service-map reconciliation can create incorrect:

```text
invoice matches
sales matches
rates
margin
trend
```

Classify impact.

---

# 25. Finance-Control Checklist Audit

The project states:

```text
finance_control_checklist.parquet
```

is pending.

Determine what finance controls already exist implicitly.

Propose a checklist schema containing fields such as:

```text
control_id
control_name
status
severity
affected_records
evidence_refs
blocking
notes
```

Potential control categories:

```text
input completeness
schema validity
join cardinality
reconciliation completeness
rate-card completeness
margin completeness
trend comparability
evidence completeness
citation validity
severity determinism
lineage completeness
LLM grounding
```

Classify controls as:

```text
PASS
FAIL
WARNING
NOT_APPLICABLE
NOT_RUN
BLOCKED
```

Do not implement until audit findings are complete.

---

# 26. Output Schema Audit

Audit:

```text
docs/output_schema.md
```

against actual generated Parquet and Markdown outputs.

The project claims:

```text
22 parquet tables + analyst_report.md
```

Verify:

```text
actual count
actual names
columns
keys
types
status fields
lineage fields
evidence IDs
```

Flag:

```text
documented but not generated
generated but undocumented
schema mismatch
unstable columns
```

---

# 27. Determinism Audit

For every script classify output as:

```text
DETERMINISTIC
DETERMINISTIC_WITH_CONFIG
NONDETERMINISTIC
LLM_DEPENDENT
```

Financial facts should be deterministic wherever possible.

LLM-dependent output must not overwrite deterministic facts.

---

# 28. Reproducibility Audit

Run the deterministic pipeline twice with identical fixtures.

Compare output hashes/content.

Ignoring approved volatile metadata such as timestamps, results should be reproducible.

Report any unexplained drift.

---

# 29. Idempotency Audit

Check whether rerunning the pipeline:

```text
duplicates records
appends duplicate findings
overwrites safely
creates inconsistent lineage
changes output unexpectedly
```

The expected rerun behaviour must be explicit.

---

# 30. Failure-Mode Audit

Test controlled failures:

```text
missing invoice file
missing sales file
missing rate card
missing service map
bad mapping YAML
invalid date
invalid money
duplicate IDs
empty file
partial prior-period data
LLM unavailable
LLM API error
unsupported provider
write failure
```

For each determine:

```text
fail closed
degrade safely
produce partial output
silently continue
```

Finance-control workflows should fail closed when authoritative calculations would otherwise be misleading.

---

# 31. Security / Privacy Audit

Check whether invoice/customer data can leak via:

```text
LLM prompts
logs
tracebacks
debug output
fixtures
cached files
environment dumps
```

Review `.gitignore`.

Ensure secrets and raw commercial data are not committed unintentionally.

Assess whether local-only deterministic operation works with Phase 4 disabled.

---

# 32. Dependency Audit

Inventory all runtime and dev dependencies.

Classify:

```text
REQUIRED
OPTIONAL
DEV_ONLY
UNUSED
```

Confirm the project remains aligned with its stated principles:

```text
plain Python
pandas
FOSS-friendly
no mandatory paid API
no unnecessary LangChain/LlamaIndex
offline-capable deterministic pipeline
```

Flag dependency creep.

---

# 33. Code Quality Audit

Do not perform stylistic refactoring.

Only identify issues materially affecting:

```text
correctness
maintainability
financial safety
testability
traceability
```

Look for:

```text
duplicated calculation logic
duplicated thresholds
magic numbers
silent exception handling
implicit type coercion
global mutable state
side effects
inconsistent schemas
```

---

# 34. Configuration Audit

Find all thresholds and business rules.

Determine where each lives:

```text
SKILL.md
Python constants
YAML
CLI arguments
prompt
test fixtures
```

A rule should have one authoritative owner.

Specifically inspect:

```text
variance thresholds
low-margin threshold
anomaly threshold
severity threshold
date tolerances
matching tolerances
rounding rules
```

Flag duplicate ownership.

---

# 35. Mapping Audit

Column and service mappings are high-risk.

Audit mapping format and behaviour.

Check:

```text
explicit source column
canonical destination
transformation
required/optional
fallback
ambiguity
version
```

No fuzzy or inferred mapping should silently become authoritative.

---

# 36. Accounting Semantics Boundary

Clearly identify what this project currently does and does NOT do.

Likely scope:

```text
internal management analysis
reconciliation
variance investigation
profitability analysis
```

Not necessarily:

```text
statutory accounting
tax return preparation
general ledger
journal posting
audit assurance
```

Check whether documentation or LLM output crosses this boundary.

Flag any language implying external accounting assurance.

---

# 37. Existing Strengths

The audit must explicitly identify what is already well designed.

Do not produce only defects.

Assess strengths such as:

```text
deterministic/LLM separation
provider independence
test coverage
offline capability
governance structure
source contracts
evidence controls
modular phases
```

This is necessary to avoid unnecessary rewrites.

---

# 38. Gap Severity

Classify findings:

```text
P0 — can materially produce incorrect financial conclusions
P1 — weakens finance-control reliability or traceability
P2 — maintainability/usability problem
P3 — cosmetic/documentation improvement
```

Examples of likely P0 categories:

```text
incorrect margin semantics
duplicate-row multiplication
ambiguous joins treated as valid
fabricated LLM numbers
wrong rate selection
silent missing-data substitution
```

Do not classify based solely on implementation effort.

Classify based on business risk.

---

# 39. Final Audit Deliverables

Create:

```text
docs/audit/current-state-audit.md
docs/audit/control-gap-matrix.md
docs/audit/implementation-vs-governance.md
docs/audit/test-coverage-audit.md
docs/audit/remediation-plan.md
```

Do not alter production logic while creating these.

---

# 40. `current-state-audit.md`

Required structure:

```text
EXECUTIVE STATUS

OVERALL VERDICT

WHAT EXISTS

WHAT WORKS

WHAT IS PARTIAL

WHAT IS DOCUMENTED ONLY

P0 FINDINGS

P1 FINDINGS

P2 FINDINGS

FINANCE-CONTROL READINESS

LLM SAFETY

EVIDENCE / LINEAGE READINESS

TEST QUALITY

ARCHITECTURE CONFORMANCE

RECOMMENDED NEXT STEP
```

Overall verdict must be one of:

```text
NOT RUNNABLE
RUNNABLE / UNSAFE
RUNNABLE / ANALYTIC USE ONLY
FINANCE-CONTROL CANDIDATE
FINANCE-CONTROL READY
```

Do not use `FINANCE-CONTROL READY` unless every blocking control is objectively satisfied.

---

# 41. Control Gap Matrix

Use columns:

```text
ID
Control
Current state
Evidence
Gap
Risk
Severity
Blocking
Required remediation
Owner module
```

---

# 42. Implementation vs Governance Matrix

For every important governed requirement:

```text
Requirement
Owner document
Implementation
Tests
Status
Conflict
```

Statuses:

```text
CONFORMANT
PARTIAL
NONCONFORMANT
UNIMPLEMENTED
UNGOVERNED
CONFLICTING
```

---

# 43. Remediation Plan

Do NOT rewrite the roadmap blindly.

Produce remediation ordered strictly by dependency and risk.

Use stages such as:

```text
Stage A — correctness defects
Stage B — control completeness
Stage C — evidence/citation integrity
Stage D — lineage
Stage E — LLM hardening
Stage F — optional integrations
```

Every task must state:

```text
problem
affected files
required behaviour
tests required
acceptance criteria
dependencies
```

---

# 44. Important Architectural Question

After completing the audit, assess whether this existing project should become the foundation for the broader finance/business-intelligence system.

Specifically answer:

### A. Can these components be generalized?

```text
evidence model
lineage model
calculation controls
severity model
citation validator
provider abstraction
LLM grounding
deterministic pipeline pattern
```

### B. Should these remain invoice-specific?

```text
invoice schemas
rate-card matching
service-map reconciliation
invoice/sales joins
invoice trend semantics
```

### C. Which abstractions should be extracted later into shared modules?

Do NOT extract them during the audit.

Avoid premature framework creation.

---

# 45. Relationship to Broader Business Intelligence Stack

Evaluate whether this eventual architecture is preferable:

```text
business-intelligence/
│
├── shared/
│   ├── evidence/
│   ├── provenance/
│   ├── controls/
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
    ├── decision-memo/
    └── listing-analysis/
```

versus leaving `internal-invoice-analysis` completely standalone.

Base the recommendation on actual current code rather than architectural preference.

---

# 46. Do Not Do During This Audit

Do NOT:

```text
rewrite SKILL.md
move folders
rename scripts
change schemas
extract shared libraries
introduce MCP
introduce LangGraph
introduce LangChain
add vector databases
switch dataframes libraries
replace pandas
change provider APIs
add external financial data
implement new business skills
```

unless required solely to make the project testable and the problem is explicitly documented first.

The purpose is to establish truth before changing architecture.

---

# 47. Final Response

At completion provide:

1. Final reproduced test result
2. Overall verdict
3. P0 count
4. P1 count
5. Top five blocking issues
6. What should explicitly NOT be changed
7. Whether the current project is suitable as the finance-control foundation for the wider Business Intelligence project
8. Exact next remediation task
9. Files created during the audit
10. No implementation changes unless separately requested

The final answer must distinguish clearly between:

```text
observed fact
inference
recommendation
```

Do not declare finance-control readiness merely because all tests pass.