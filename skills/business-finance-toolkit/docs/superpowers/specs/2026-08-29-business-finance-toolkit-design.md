# Business & Finance Toolkit Design

## Purpose

Build a production-oriented, greenfield business-advisory toolkit. Its primary job is to turn a proposed business or pilot into an explicit, evidence-backed assessment plan; it must not present a language model as an authoritative ledger, regulator, or final approver.

## Boundaries

- Keep `invoice-finance-analyst` separate. It is a future portfolio integration candidate, not a dependency or source of shared code.
- Use a modular Python package and a local CLI. Do not introduce microservices, vector databases, LangChain, LangGraph, or autonomous external actions.
- Make financial outputs deterministic: use `Decimal`, explicit rounding, typed inputs, and tests.
- Store facts as claims with source, quality, status, retrieval date, and provenance. Treat legal, tax, tariff, and compliance facts as unverified until an authoritative source is attached.

## Architecture

The package has five bounded areas:

1. `models`: Pydantic contracts for claims, evidence, lifecycle, approvals, decisions, and run manifests.
2. `calculators`: landed cost, unit economics, cash flow, scenarios, capital requirement, and hidden-cost discovery.
3. `advisor`: constructs an assessment plan, identifies missing evidence, runs deterministic calculators, and evaluates decision gates.
4. `domain_packs`: declarative generic-import and Australia/JDM checklists. Packs propose questions and cost categories; they do not encode regulatory conclusions.
5. `llm`: provider-neutral protocols. Any LLM may draft or classify, but deterministic outputs and human approvals remain outside the model.

Markdown skills are portable workflow guides. Each has a manifest, lifecycle state, inputs, outputs, human approval requirements, and references to the implementation contracts it may use.

## Data flow

`business idea -> advisor plan -> evidence/claim register -> deterministic calculations -> scenario results -> decision gates -> decision memo/run manifest`

Inputs and outputs may initially be JSON or YAML files. SQLite is the default local persistence option; pandas and DuckDB are optional adapters for tabular analysis rather than mandatory runtime dependencies.

## Safety and governance

- Claims use `USER_STATED`, `UNVERIFIED`, `VERIFIED_PRIMARY`, or `VERIFIED_SECONDARY` evidence labels.
- A decision can be `DRAFT`, `READY_FOR_REVIEW`, `APPROVED`, `DECLINED`, or `BLOCKED`.
- Only a named human approver may advance a decision beyond `READY_FOR_REVIEW`.
- Every CLI execution produces a run manifest including input hashes, calculator version, claims used, and generated artifacts.
- Sensitive financial data is not sent to an LLM unless the provider configuration explicitly permits it.

## Acceptance criteria

- A new user can install the package, run the sample generic-import pilot, and inspect a machine-readable result.
- Landed-cost, margin, cash-flow, scenario, capital, and gate computations are tested with exact decimal expectations.
- A missing critical claim or required approval blocks a pilot decision.
- Skills, domain packs, schemas, source-quality policy, roadmap, and FOSS provenance notes are included.
- The repository is packaged as a ZIP after fresh tests and tree inspection.

## Intentional limits

This starting repository is not tax, customs, legal, financial-planning, or accounting advice. It supplies traceable workflows and calculations; jurisdictional rules must be researched from primary sources before a decision relies on them.
