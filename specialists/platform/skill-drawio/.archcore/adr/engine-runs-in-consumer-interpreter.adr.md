---
title: The engine runs in the consuming project's interpreter
type: adr
status: accepted
tags: [engine, runtime]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: The engine runs in the consuming project's interpreter

Status: accepted (sources `scripts/README.md` "How a project uses the engine", `AGENTS.md` working rules; same model as skill-coder's accepted ADR `helpers-run-in-target-environment`; promoted
2026-10-19 on the operator's instruction "promote and accept")

## Context

The pack's own venv (mise pin, working cache) can differ from a consuming project's Python. Installing into a project for the pack's sake, or running the project's drawing through the pack's venv,
couples the two.

## Decision

The engine runs in the consuming project's own interpreter, Python 3.11 or newer, stdlib only, with PyYAML imported at the edge. A project with its own constants imports the `drawio` and `flowmap`
packages through its one seam to the skills; any other project runs `render_flowmap.py` by path.

## Consequences

- `tests/test_package_contract.py` `test_modules_portable_catalogued_tested_and_documented` enforces the 3.11 grammar and no third-party import at module level.
- Open (2026-10-19): `just test-matrix` has not run on 3.11 here (not installed); the floor is proven by the grammar parse only.
