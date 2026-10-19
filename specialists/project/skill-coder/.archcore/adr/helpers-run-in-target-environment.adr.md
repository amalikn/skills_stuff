---
title: Helpers run in the target project's environment
type: adr
status: proposed
tags: [runtime, helpers]
created: 2026-10-19
---

# ADR: Helpers run in the target project's environment

Status: proposed (decided by the operator in chat, 2026-10-19; written outside `promote` mode, so it awaits the operator's promotion approval)

## Context

The pack's own runtime (mise pin, working-cache venv) can differ from a target project's Python and package versions. Two options: run the helpers
in the pack's runtime against the project (A), or apply the logic inside the project's environment with its own tooling (B).

## Decision

B by default. The rules are applied with the project's own linters, formatters, test runner and pinned interpreter. The helpers are stdlib-only,
declare `REQUIRES_PYTHON = (3, 11)` (the floor is set by `tomllib`, used to read `code-map.toml`), read code as files and run with the project's
interpreter by path. A only as a fallback, when a project has no Python 3.11+: the same helper through this pack's recipe, which is safe because
helpers only read. Nothing is installed into a project for the pack's sake. Engines a project imports always run in the project's interpreter, and
the project pins the skill revision.

## Consequences

- The project's tool versions decide; the pack never fights a project's configuration.
- Helpers cannot use third-party libraries; the contract test enforces stdlib-only and the 3.11 grammar; `just test-matrix` runs them on each installed Python.
- The pack's own venv stays on the operator's default (3.14) and exists only for its recipes and tests.
