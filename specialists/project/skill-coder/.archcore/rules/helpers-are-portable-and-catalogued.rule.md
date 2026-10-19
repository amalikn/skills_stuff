---
title: Helpers are read-only, stdlib-only, tested and catalogued
type: rule
status: accepted
tags: [helpers, checkers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Helpers are read-only, stdlib-only, tested and catalogued

Status: accepted (stated in `AGENTS.md` "Working rules" and `SKILL.md`; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries). The runtime choice behind it is
[helpers-run-in-target-environment](../adr/helpers-run-in-target-environment.adr.md).

## Rule

- A helper in `scripts/` reads a project's code as files (parses, never imports) and reports. It writes nothing in the target except, on an
  explicit `--write-baseline`, its own baseline file (adoption, or recording an improvement).
- It is stdlib-only, declares `REQUIRES_PYTHON` and parses at that grammar.
- It has tests in `tests/test_helpers.py` and a row in `scripts/README.md`, both added in the same pass; a runnable helper also gets a `just`
  recipe. An imported module (`code_map.py`, `pyparse.py`, `ratchet.py`) is catalogued as "imported, not run" and has no recipe.
- The pack is held to its own rules: `just self-check` (inside `just check`) runs the helpers on the pack itself against its baselines.

## Why

The helpers run inside other projects' environments; a third-party import or a write would make the pack change what it measures.

## Enforcement

`tests/test_package_contract.py` (`test_helpers_portable_tested_and_documented`): every helper is tested, stdlib-only, declares `REQUIRES_PYTHON`, parses at that grammar and documents Args and
Returns. The skill-ai-it script-coverage check fails an uncatalogued script.
