# Implementation vs Governance Matrix: Internal Invoice Analysis

## Contents

- [Authority map](#authority-map)
- [Requirement matrix](#requirement-matrix)
- [Governance conflicts](#governance-conflicts)
- [Ownership conclusion](#ownership-conclusion)

## Authority map

| Subject                                  | Primary owner                        | Supporting owner                           | Audit conclusion                                                     |
| ---------------------------------------- | ------------------------------------ | ------------------------------------------ | -------------------------------------------------------------------- |
| Agent and repository constraints         | `AGENTS.md`                          | `AI_NAVIGATION.md`, parent `../AGENTS.md`  | Clear for operational constraints.                                   |
| Context and source priority              | `AI_NAVIGATION.md`                   | `context-map.yaml`                         | Clear; architecture/specification hierarchy is explicit.             |
| Architecture and invariants              | `ARCHITECTURE.md`                    | `ROADMAP.md`                               | Clear in intent, but present-tense flow includes planned behavior.   |
| Workflow semantics and user-facing rules | `internal-invoice-analysis/SKILL.md` | `docs/data_contract.md`                    | Duplicated; the skill is broader than code.                          |
| Input/data contracts                     | `docs/data_contract.md`              | mapping YAMLs and validator constants      | Clear owner, but implementation has drift.                           |
| Output contracts                         | `docs/output_schema.md`              | scripts                                    | Clear owner, with a small documentation/code mismatch.               |
| Severity logic                           | `ARCHITECTURE.md` and `SKILL.md`     | `ROADMAP.md`                               | Conflicting current state: formula declared, implementation pending. |
| Evidence rules                           | `SKILL.md`                           | `ARCHITECTURE.md`, `llm_analyst.py` prompt | Contract exists, enforcement does not.                               |
| Roadmap/status                           | `ROADMAP.md`                         | `CHANGELOG.md`                             | Clear and mostly accurate.                                           |
| Setup/dependencies                       | `SETUP.md`                           | `justfile`, scripts README                 | No machine-readable source of truth.                                 |

## Requirement matrix

| Requirement                 | Owner document      | Implementation                                 | Tests                         | Status        | Conflict                                        |
| --------------------------- | ------------------- | ---------------------------------------------- | ----------------------------- | ------------- | ----------------------------------------------- |
| No external financial data  | `SKILL.md`          | No external data code in deterministic phases; | Prompt-string test only.      | CONFORMANT    | External data ban does not constrain provider   |
|   by default                |                     |   LLM endpoint is configured by operator.      |                               |               |   data transfer.                                |
| No invented values          | `SKILL.md`          | Pandas calculations use inputs; LLM text is    | No fabricated-response        | PARTIAL       | Prompt rule lacks enforcement.                  |
|                             |                     |   free-form.                                   |   rejection test.             |               |                                                 |
| User-confirmed mappings     | Data contract       | Existing mapping is mandatory.                 | Missing mapping/column tests  | PARTIAL       | Heuristic suggestions pick first header; no     |
|                             |                     |                                                |   exist.                      |               |   confidence/candidate logic.                   |
| Mapping only when needed    | `SKILL.md`          | Loader requires mapping for every CSV.         | Indirect validation coverage. | PARTIAL       | Operational workflow is more rigid than skill   |
|                             |                     |                                                |                               |               |   wording.                                      |
| Deterministic calculations  | `SKILL.md`,         | Phase 1B–3 calculation functions are           | Fixture assertions and        | PARTIAL       | IDs/timestamps make artifacts non-byte-stable.  |
|                             |   architecture      |   deterministic for fixtures.                  |   two-run audit probe.        |               |                                                 |
| Facts separated from        | `SKILL.md`          | Tables and LLM report are separate files.      | Writer and prompt tests.      | PARTIAL       | LLM output can still state unvalidated facts.   |
|   interpretation            |                     |                                                |                               |               |                                                 |
| Assumptions recorded        | `SKILL.md`          | Phase 1B–3 assumption tables exist.            | Assumption-table tests.       | PARTIAL       | Mapping, date format, input scope, service-map  |
|                             |                     |                                                |                               |               |   use, and phase status absent.                 |
| Preserve unmatched records  | Architecture        | Invoice-only and sales-only tables exist.      | Fixture coverage.             | PARTIAL       | Duplicate invoices are dropped; ambiguous       |
|                             |   invariant         |                                                |                               |               |   matches remain matched.                       |
| Exact reconciliation        | `SKILL.md`          | Exact service ID plus start period only.       | Happy-path tests.             | PARTIAL       | Service-map, description, manual, period modes, |
|   priority                  |                     |                                                |                               |               |   and duplicates absent.                        |
| No many-to-many financial   | Audit requirement   | No validation exists.                          | No tests.                     | NONCONFORMANT | None.                                           |
|   joins                     |   and implicit      |                                                |                               |               |                                                 |
|                             |   architecture      |                                                |                               |               |                                                 |
| Rate effective/expiry dates | Data contract and   | Latest effective row per service type wins.    | Tests only single effective   | NONCONFORMANT | Roadmap correctly records defect.               |
|                             |   roadmap           |                                                |   date.                       |               |                                                 |
| Ex-tax margin definition    | Architecture        | `revenue_ex_tax - invoice_amount_ex_tax`.      | Unit assertions.              | PARTIAL       | Upstream join safety and credit/tax             |
|                             |   invariant         |                                                |                               |               |   classification absent.                        |
| Variance definition         | Data contract       | Code calculates invoice less sales-recorded    | Assertions use sales cost.    | CONFLICTING   | Data contract says invoice less revenue; output |
|                             |                     |   cost.                                        |                               |               |   schema/code say cost.                         |
| Tax/GST separation          | `SKILL.md`          | Tax fields load only.                          | No downstream tests.          | UNIMPLEMENTED | Roadmap marks gap; skill reads as current       |
|                             |                     |                                                |                               |               |   workflow.                                     |
| Credit/reversal/negative    | `SKILL.md`          | None.                                          | No tests.                     | UNIMPLEMENTED | Roadmap marks gap.                              |
|   classification            |                     |                                                |                               |               |                                                 |
| Mixed-currency handling     | `SKILL.md`          | None.                                          | No tests.                     | UNIMPLEMENTED | Data contract assumes AUD, validator does not   |
|                             |                     |                                                |                               |               |   enforce it.                                   |
| Deterministic severity      | Architecture and    | None.                                          | No tests.                     | CONFLICTING   | Architecture says deterministic while roadmap   |
|                             |   skill             |                                                |                               |               |   says pending.                                 |
| Evidence citations          | `SKILL.md`, output  | Prompt requires citation string.               | Prompt-string tests.          | NONCONFORMANT | Documentation implies requirement is enforced.  |
|                             |   schema            |                                                |                               |               |                                                 |
| LLM cannot alter            | Architecture        | LLM sees only selected tables, but report text | Mock transport tests only.    | PARTIAL       | No numeric claim comparison.                    |
|   calculations              |                     |   is unconstrained after response.             |                               |               |                                                 |
| Lineage manifest            | Roadmap             | None.                                          | No tests.                     | UNIMPLEMENTED | None.                                           |
| Phase-completeness marker   | Roadmap             | None.                                          | No tests.                     | UNIMPLEMENTED | None.                                           |
| 22 derived parquet outputs  | Output schema       | All 22 present in current fixture db.          | End-to-end table checks.      | CONFORMANT    | No schema enforcement or run-scope linkage.     |
| Finance-control checklist   | Architecture,       | None.                                          | No tests.                     | UNIMPLEMENTED | All governing docs correctly mark pending.      |
|                             |   roadmap, skill    |                                                |                               |               |                                                 |
| Provider-agnostic LLM       | Architecture,       | OpenAI-compatible client and configurable base | Mock provider-parameter       | CONFORMANT    | No provider validation/retry/privacy policy.    |
|   transport                 |   scripts README    |   URL.                                         |   tests.                      |               |                                                 |
| Offline deterministic       | Setup, scripts      | Phase 1B–3 run without network.                | Tests are local except no     | PARTIAL       | Tests depend on existing db state.              |
|   operation                 |   README            |                                                |   full clean-checkout test.   |               |                                                 |

## Governance conflicts

1. **Severity state.** `ARCHITECTURE.md` describes severity as deterministic and gives a formula. The same document adds a pending-implementation note; `ROADMAP.md` states the implementation is
   absent. The roadmap is the accurate status source. The architecture should label the formula as planned rather than present capability.
2. **Variance semantics.** `docs/data_contract.md` defines `variance_abs` as invoice amount less revenue. The implementation, output schema, and tests define it as invoice amount less sales-recorded
   cost. The latter is consistent with a supplier-cost reconciliation. The data contract requires correction before feature work.
3. **Mapping ambiguity.** The data contract promises candidate/confidence handling and analysis halt for ambiguous heuristic mapping. `suggest_mapping()` returns the first substring match and does not
   calculate confidence or detect multiple candidates. Users still manually save mappings, but the stated control is not implemented.
4. **Date semantics.** The contract allows both AU and US short dates. The loader selects `dayfirst=True`, so a source-specific US format can silently change dates. Neither document owns a
   mapping-level date format.
5. **Current versus target workflow.** `SKILL.md` describes a 15-step control workflow with service maps, tax separation, rate eligibility, duplicates, evidence, and severity. The roadmap
   distinguishes many of these as pending. The skill should remain the operational target, but status labels must accompany every unimplemented step.
6. **Runtime version.** `AGENTS.md` and `SETUP.md` state Python 3.14.4. The documented venv currently runs 3.14.7. This is configuration drift rather than a calculation defect.

## Ownership conclusion

**Observed fact.** No single document owns every financial rule. `SKILL.md`, `ARCHITECTURE.md`, `docs/data_contract.md`, output schema, Python constants, and roadmap each contain pieces.

**Recommendation.** Retain the existing separation but assign one owner per rule type: data semantics and join/cardinality in the data contract; executable thresholds in versioned configuration;
workflow/reporting constraints in the skill; architectural invariants in architecture; phase status only in the roadmap; output shapes in output schema. Scripts should import configuration rather
than restate hard-coded thresholds.
