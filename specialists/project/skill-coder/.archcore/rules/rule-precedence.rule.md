---
title: Rule precedence - project, then language file, then core
type: rule
status: accepted
tags: [pack-content, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Rule precedence - project, then language file, then core

Status: accepted (stated in `AGENTS.md` "Working rules" and `SKILL.md`; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

- Core rules in `references/` are language-agnostic.
- A file in `languages/` may tighten a core rule, map it to that language's tools, or loosen it only with a stated reason; a loosening without a reason is void, and a language file never removes a
  safety rule.
- A project's own rules (its `AGENTS.md`, code design, `code-map.toml`, linter and formatter configuration) outrank both. Where they disagree with the pack, follow the project and say so; where two
  project sources disagree, stop and report.

## Why

The pack teaches practice; it does not govern projects. A pack rule that overrode a project's decided design would hide that decision from its owner.

## Enforcement

Review. `tests/test_package_contract.py` (`test_skill_routes_every_reference_and_language`) keeps every reference and language file routed from `SKILL.md`, so no rule file sits outside this order.
