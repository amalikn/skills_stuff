---
Title: Module and function shape
Category: reference
Status: current
Authority: local-supplement
Scope: Size budgets, single responsibility, naming and the shrink-only ratchet for existing oversize code
Last reviewed: 2026-10-19
Summary: >-
  Modules under 400 lines and functions under 60 by default, older oversize code held by a shrink-only ratchet, one
  responsibility per module, names in the domain's words, and front-end handlers that hold no logic.
---

# Module and function shape

## Size budgets

| Unit                                                           | Default budget      | Why                                                           |
| -------------------------------------------------------------- | ------------------- | ------------------------------------------------------------- |
| Module (file of code)                                          | under 400 lines     | An agent or reviewer opens one small file to change one thing |
| Function or method                                             | under 60 lines      | One screen; one idea; testable alone                          |
| File an agent loads whole (AGENTS.md, SKILL.md, SCRATCHPAD.md) | 200 lines and 25 KB | Always-loaded context stays cheap                             |
| Check or rule in a checker                                     | under 60 lines      | The check is its own documentation                            |

**Two thresholds per unit** (operator, 2026-10-19: "the number of lines before a script has to be modularised"): past the warning, plan the split along a real seam the next time the unit is touched
(it never fails a check); past the hard limit the unit must be split, and a check fails unless the shrink-only baseline records it.

| Language      | Module: warn / must split | Function: warn / must split | Source                                                                                                                     |
| ------------- | ------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Default (any) | 300 / 400                 | 40 / 60                     | Operator; the hard limits are a governed project's rule R34                                                                |
| Shell         | 100 / 200                 | 30 / 40                     | Operator; past about 100 lines a script belongs in a structured language (Google Shell Style Guide, UNVERIFIED             |
|               |                           |                             |   until captured)                                                                                                          |

`scripts/code_size.py` applies both tiers (`DEFAULT_LIMITS`, `LANG_LIMITS`); a project sets its own per language or file suffix in `code-map.toml` `[limits.<language>]` (`module`, `function`,
`warn_module`, `warn_function`).

The numbers are the operator's defaults (a governed project, unified-network-controller, rule R34; skill-ai-it checker structure). A language override may adjust them with a stated reason
([../languages/readme.md](../languages/readme.md)); a project's own numbers win.

## The shrink-only ratchet

Old code is not rewritten just to adopt a rule. Instead:

1. Measure on the day the rule is adopted and record each oversize unit with its size in a baseline file (for example `code-size-baseline.json`).
2. A new unit must meet the budget. A recorded unit may shrink, never grow. When it shrinks, write the new size into the baseline in the same change.
3. A unit that falls under the budget leaves the baseline.

Why: legacy code does not block work, and the count can only fall. The pack's `scripts/code_size.py` and `scripts/ratchet.py` implement this; the same pattern holds docstring shortfalls and warn-mode
checks ([testing.md](testing.md), [documentation-and-headers.md](documentation-and-headers.md)).

## Single responsibility

- A module does one job a sentence can state; its header says that sentence. Why: if the sentence needs "and", there are two modules.
- A runnable file is a front end, never also the shared library other files import. Why: importing a CLI drags its side effects and arguments into every caller (a governed project found one CLI
  imported by 47 modules).
- Front-end handlers parse input, build a context, call one service and render. They hold no business rule. Why: the rule then exists once for every front end.
- Pure decisions (given these facts, what should happen) are separate functions from the I/O that gathers the facts and applies the result. Why: the pure part tests with no fixtures, and the I/O part
  stays thin.

## Grouping modules into packages

Operator, 2026-10-19 ("when modularising a large piece of code, is it better to create a subdirectory under scripts and put all the related modules under that folder with a proper name? If so, make it
part of the skill-coder logic"): yes, when the split produces a family of modules.

- **Three or more modules that share a name prefix, or that only import each other, are a package**: move them into one folder named for the feature (`flowmap/model.py`, not `flowmap_model.py`). Why:
  a shared prefix is a folder trying to exist; the folder gives the family one place, one header and one import surface, and a reader lists it instead of grepping.
- **One or two modules stay flat.** Why: a folder per file adds a level to every path and import for nothing.
- **Runnable entry points stay at the top of `scripts/`**, catalogued in its README, and stay thin: parse arguments, call the package. The package holds the library and no CLI. Why: a file run by path
  cannot use the package's relative imports, and the catalog lists what may be run in one place ([Single responsibility](#single-responsibility): a CLI is never the shared library).
- **Inside a package, modules import each other relatively**; the package's `__init__` (or the language's equivalent) states the package's job in one sentence and lists its modules.
- **Package names are unique across everything a consumer loads.** A project that puts several skill packs' `scripts/` on its import path sees them as one namespace, so `common/` or `utils/` in two
  packs shadows one with the other. Name the package for its domain (`drawio`, `flowmap`). Why: a shadowed package fails far from the cause.
- **One level, two at most.** Why: depth makes paths long and moves hard; past two levels the code is a project of its own and belongs in a `src/` layout.
- **Moving modules into a package is a refactor**: every import, string path, recipe, catalog line and test reference changes in the same change, and before-and-after outputs match
  ([refactoring-and-promotion.md](refactoring-and-promotion.md)).

`scripts/module_groups.py` reports folders holding three or more code files with a shared prefix, as candidates (warn only).

## Naming

- **Code files and identifiers follow their language; typed commands (CLI commands, long options, task-runner recipes) are kebab-case; a tool's own parser wins for its names** (operator, 2026-10-19,
  replacing the 2026-10-07 snake_case-for-recipes clause of governance [`coding-guide.md`](/Volumes/Data/_ai/governance/categories/coding-guide.md)). The full verified mapping, language by language:
  [naming-conventions.md](naming-conventions.md). An existing name that breaks it is renamed when next touched, with every reference updated in the same change
  ([safety-and-writes.md](safety-and-writes.md), "Changing an identifier").
- Use the domain's words, not a tool's or vendor's, outside the seam that talks to that tool. Why: names outlive tools.
- Name for what a thing is or does, not how: `pending_orders`, not `list2`; a boolean reads as a question (`is_reachable`). Why: the reader should not need the body to know the meaning.
- Follow the language's case convention exactly (each override names it). Why: mixed conventions read as different things.
- No abbreviations a newcomer would not know; spell out units in names where a number has one (`timeout_s`, `size_bytes`). Why: a missing unit is a classic silent bug.
- Internal identifiers (field keys, alarm classes, record names) carry no product or brand name. Why: renaming a stored key is a migration.

## Typed records over loose maps

Data that crosses a function boundary more than once gets a declared type (frozen dataclass, struct, record, interface) with explicit conversion to and from its wire form. Why: a misspelt key in a map
fails at run time, far from the cause.
