# Business & Finance Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable, evidence-governed business-advisory toolkit with deterministic commercial calculations.

**Architecture:** Use one Python package with Pydantic models and Decimal calculators. Keep skill workflows and domain packs declarative, use JSON/YAML boundary files, and make approval and provenance explicit.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, pytest, standard-library SQLite, optional pandas/DuckDB adapters.

---

### Task 1: Package contract and test harness

**Files:** `pyproject.toml`, `src/bftoolkit/__init__.py`, `tests/test_models.py`

- [ ] Write a failing test that constructs a primary-source claim and rejects a source-free verified claim.
- [ ] Run `python -m pytest tests/test_models.py -q` and confirm it fails because the model is absent.
- [ ] Implement evidence, claim, lifecycle, approval, decision, and run-manifest models.
- [ ] Re-run the test and confirm it passes.

### Task 2: Deterministic commercial calculators

**Files:** `src/bftoolkit/calculators/*.py`, `tests/test_calculators.py`

- [ ] Write failing tests for landed cost, contribution margin, monthly closing cash, scenario deltas, and required capital.
- [ ] Run `python -m pytest tests/test_calculators.py -q` and confirm expected missing-import failures.
- [ ] Implement calculations using `Decimal` and explicit `ROUND_HALF_UP` monetary rounding.
- [ ] Re-run calculator tests and confirm exact expected results.

### Task 3: Advisor plan, gates, and provenance

**Files:** `src/bftoolkit/advisor.py`, `src/bftoolkit/gates.py`, `src/bftoolkit/provenance.py`, `tests/test_advisor.py`

- [ ] Write failing tests for a generic-import assessment plan and a blocked decision with a missing critical claim.
- [ ] Run `python -m pytest tests/test_advisor.py -q` and confirm it fails before the modules exist.
- [ ] Implement plan assembly, gate evaluation, and deterministic input hashing/run manifests.
- [ ] Re-run advisor tests and confirm expected plan and gate outcomes.

### Task 4: CLI, schemas, configuration, and domain packs

**Files:** `src/bftoolkit/cli.py`, `schemas/*.json`, `config/*.yaml`, `src/bftoolkit/domain_packs/*.py`, `examples/*`, `tests/test_cli.py`

- [ ] Write a failing CLI test for the sample pilot command.
- [ ] Run `python -m pytest tests/test_cli.py -q` and confirm the entry point is absent.
- [ ] Implement a read-only `assess` command that emits JSON and supplies generic-import/Australia-JDM checklist prompts.
- [ ] Re-run the CLI test and inspect the sample JSON.

### Task 5: Skill portfolio and governance documentation

**Files:** `skills/*/SKILL.md`, `skills/*/manifest.yaml`, `README.md`, `AGENTS.md`, `docs/**/*.md`, `third_party/*.md`

- [ ] Create portable skill instructions and manifests for the requested portfolio.
- [ ] Document claim quality, approvals, source policy, LLM contracts, domain-pack limits, roadmap, and FOSS conceptual provenance.
- [ ] Validate YAML/JSON and scan Markdown for unresolved placeholders.

### Task 6: Package verification and delivery

**Files:** `tools/validate_repository.py`, `tests/fixtures/*`, output ZIP

- [ ] Add a structural validator for manifests, JSON schemas, and mandatory repository files.
- [ ] Run the complete test suite and structural validator.
- [ ] Inspect the final tree and create `business-finance-toolkit.zip` excluding caches and build artefacts.
