This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, ARCHITECTURE.md, architecture.md, CONVENTIONS.md, ROADMAP.md, roadmap.md, SCRATCHPAD.md, CHANGELOG.md, context-map.yaml, scripts/README.md, scripts/**, justfile, Justfile, Taskfile.yml, Makefile, package.json, memory-bank/**/*.md, .archcore/**/*.md, docs/**/*.md
- Files matching these patterns are excluded: node_modules/**, .git/**, dist/**, build/**, cache/**, runtime/**, __pycache__/**, .venv/**, graphify-out/**, .ai-context/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.archcore/
  adr/
    default-activation-waits-for-testing.adr.md
    helpers-run-in-target-environment.adr.md
    naming-mapping-is-data.adr.md
  rules/
    code-map-holds-decisions-only.rule.md
    cross-project-write-back.rule.md
    helpers-are-portable-and-catalogued.rule.md
    pack-text-stays-generic.rule.md
    rule-precedence.rule.md
    rules-cite-sources.rule.md
  index.guide.md
docs/
  history/
    changelog-20261027_1213.md
    changelog-20261028_1943.md
    changelog-20261028_2101.md
    changelog-20261101_2353.md
    changelog-20261102_1132.md
    changelog-20261102_1348.md
    changelog-20261102_1434.md
    changelog-20261105_1156.md
    changelog-20261105_2139.md
    changelog-20261106_1030.md
    changelog-20261107_1723.md
    changelog-20261107_1732.md
    changelog-20261109_1222.md
    changelog-20261109_2227.md
    changelog-20261110_1246.md
    changelog-20261111_1100.md
    changelog-20261116_1737.md
    changelog-20261116_1752.md
    changelog-20261117_1101.md
    changelog-20261117_1859.md
    changelog-20261118_1557.md
    changelog-20261118_2102.md
    changelog-20261119_1538.md
    changelog-20261119_1554.md
    changelog-20261119_1601.md
    changelog-20261119_1603.md
    readme.md
    roadmap-20261027_1045.md
    roadmap-20261028_1311.md
scripts/
  call_timeouts.py
  check_governance.py
  code_map.py
  code_size.py
  code-size-baseline.json
  cpuprofile_summary.py
  doc-freshness-baseline.json
  group_timeouts.py
  import_layers.py
  language_split.py
  module_groups.py
  naming_check.py
  naming_table.py
  process_match.py
  pyparse.py
  ratchet.py
  README.md
  reflow_lossless.py
  role-check-baseline.json
  scaffold.py
  script_headers.py
  script-headers-baseline.json
  suppressions.py
  timeout-baseline.json
  write_back.py
  write_gates.py
AGENTS.md
AI_NAVIGATION.md
CHANGELOG.md
CLAUDE.md
context-map.yaml
justfile
Justfile
README.md
roadmap.md
ROADMAP.md
SCRATCHPAD.md
````

# Files

## File: .archcore/adr/default-activation-waits-for-testing.adr.md
````markdown
---
title: Installed now, made the default only after testing
type: adr
status: accepted
tags: [runtime, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: Installed now, made the default only after testing

Status: accepted (operator decisions in chat, 2026-10-19: "install it as skill but dont make it default yet" and "make it default once we have tested the skill"; source `SCRATCHPAD.md` KEEP item
"Activation"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Context

A pack named in the global policy as the skill "for any code" is loaded on every coding task in every project, by every agent. An untested pack in that position spreads its mistakes everywhere at
once.

## Decision

Two stages. Now: the pack is installed (directory symlinks into the Claude, Codex and Hermes skill folders, and its row in the skills_stuff `README.md`), so it can be invoked by name and tested.
Later, once the operator judges it tested: one pass makes it the default, in the global policy's "Skills, context, and task routing" line (then the Codex sync), the skills_stuff
`.agents/skill-surfaces.md` row, and governance `coding-guide.md` linking the pack as its detailed source. The live step list and test evidence stay in the `SCRATCHPAD.md` KEEP item.

## Consequences

- Until the switch, the pack is invoked by name only. Its `SKILL.md` description says so (2026-10-19 review: the first description began "Use before
  writing, changing ... code in any project", which made Claude match it on every coding task, a default in all but name). The switch restores
  that broad trigger in the description, in the same pass as the global policy line.
- Outside the pack, governance `coding-guide.md` already links its naming reference (2026-10-19) as the canonical naming mapping; that is a citation,
  not routing, and does not make the pack the default.
- The default switch is one pass across all three surfaces, never one surface at a time.
- skill-ai-it's code checks calling this pack's helpers (one source per rule) is a separate later change, not part of the switch.
````

## File: .archcore/adr/helpers-run-in-target-environment.adr.md
````markdown
---
title: Helpers run in the target project's environment
type: adr
status: accepted
tags: [helpers, runtime]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: Helpers run in the target project's environment

Status: accepted (decided by the operator in chat, 2026-10-19; first written outside `promote` mode, promotion approved by the operator the same day)

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
- Open (2026-10-19): no project pins a skill revision yet (unified-network-controller's `skill_paths.py` loads the working tree), and
  `just test-matrix` cannot run 3.11 until `mise install python@3.11`; the floor is proven by the 3.11 grammar parse only.
````

## File: .archcore/adr/naming-mapping-is-data.adr.md
````markdown
---
title: The naming mapping is data in naming.toml
type: adr
status: accepted
tags: [checkers, pack-content]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: The naming mapping is data in naming.toml

Status: accepted (operator decision in chat, 2026-10-19: "is it better to have a json or yaml or toml file for the mapping"; promoted 2026-10-19 on the operator's instruction to add the missing
Archcore entries)

## Context

The pack maps each language and kind of name to a case convention (`references/naming-conventions.md`, claims C-C72 to C-C79). A table written by hand in the reference and a separate list in a checker
can drift: what is shown and what is enforced would then disagree.

## Decision

`naming.toml` is the single source. TOML because the helpers read it with the target project's own Python (`tomllib`, stdlib from 3.11), with no parser to install. `scripts/naming_table.py` renders
the table between the generated markers in `references/naming-conventions.md`; `scripts/naming_check.py` checks code file names and `just` recipe names from the same file. A project adds overrides and
reasoned exceptions in its `code-map.toml` `[naming]` section, never by editing the pack's mapping.

## Consequences

- The table is never edited by hand; `just naming-table` regenerates it and `just self-check` fails while it differs from `naming.toml`.
- `tests/test_package_contract.py` (`test_naming_rows_cite_existing_captures`) fails a row whose source capture is missing under `documents/`.
- The convention itself (code files and identifiers follow their language, typed commands are kebab-case, a tool's parser wins) stays pack content in the reference, not in this record.
````

## File: .archcore/rules/code-map-holds-decisions-only.rule.md
````markdown
---
title: The code map holds decisions only
type: rule
status: accepted
tags: [checkers, helpers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: The code map holds decisions only

Status: accepted (operator decision in chat, 2026-10-19: "is there a need of code-map ... or is context-map enough?"; promotion approved by the operator the same day)

## Rule

A project's `code-map.toml` holds the human decisions the checkers act on: scan roots, the project's Python grammar, files no checker measures
(`[scan.exclude]`, each with its reason), size limit overrides, import layers, write-gate exceptions with reasons, timeout roots, naming overrides and
kept names (`[naming]`, `[naming.exceptions]`, each with its reason) and each module's promotion status. It never holds facts the code states (line counts,
import edges, header text); the checkers measure those, and their shrink-only baselines are separate machine-written files. It is TOML so the
helpers read it with the project's own Python. `context-map.yaml` stays the routing map (skill-ai-it owns it) and only points to the code map.

## Enforcement

`scripts/code_map.py` refuses an unknown section (a typo would switch a rule off), a module entry with an unknown status, a promoted module with no
skill file, and an unpromoted one with no reason or needs; `code_map.excluded()` and `naming_check.exceptions()` refuse an entry with no reason, and
`naming_check.py` fails an exception for a name that no longer breaks the mapping. `tests/test_helpers.py` (CodeMap, Naming) proves each refusal.
````

## File: .archcore/rules/cross-project-write-back.rule.md
````markdown
---
title: Reusable practice learned elsewhere is written back here
type: rule
status: accepted
tags: [pack-content, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Reusable practice learned elsewhere is written back here

Status: accepted (stated in `AGENTS.md` "Cross-project write-back trigger"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

Any project that invokes this skill and learns reusable programming practice writes it back before the session closes: a dated Learned entry in the focused reference or language file, plus one
`CHANGELOG.md` line under `## Unreleased` naming the file and date, read back after writing. A finding that contradicts existing text is a Disputed entry beside it (`Conflicts: <claim ID>`), never a
deletion or silent rewrite. If this source is not writable from the engaging task, the entry stays in the engaging project as a candidate. A project-specific rule stays in that project.

## Why

The pack improves only from real engagements; a lesson left in one project's notes is lost to every other project.

## Enforcement

`tests/test_package_contract.py` (`test_write_back_entries_logged`, proven able to fail by `test_bad_write_back_entries`): every Learned or Disputed entry has its CHANGELOG line. Entry format:
`references/evolution-and-write-back.md`.
````

## File: .archcore/rules/helpers-are-portable-and-catalogued.rule.md
````markdown
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
````

## File: .archcore/rules/pack-text-stays-generic.rule.md
````markdown
---
title: Pack text stays generic and safe
type: rule
status: accepted
tags: [pack-content, checkers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Pack text stays generic and safe

Status: accepted (stated in `AGENTS.md` "Working rules"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

No customer names, hostnames, private addresses, tokens, credentials or production domains in pack files. A governed project is named only as a rule's source. Verbatim third-party captures under
`documents/` are exempt from the address and domain checks (a specification's section numbers look like addresses), never from the credential and key checks.

## Why

The pack is installed into every agent and read by every project; anything specific in it leaks one environment into all of them.

## Enforcement

`tests/test_package_contract.py` (`test_text_is_safe`, proven able to fail by `test_unsafe_text`) catches credentials, private keys, private addresses and production domains. Customer names and
hostnames are not machine-checked; review.
````

## File: .archcore/rules/rule-precedence.rule.md
````markdown
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
````

## File: .archcore/rules/rules-cite-sources.rule.md
````markdown
---
title: Every rule says why and cites its source
type: rule
status: accepted
tags: [pack-content, checkers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Every rule says why and cites its source

Status: accepted (stated in `AGENTS.md` "Working rules"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

Every rule in the pack says why in one clause. Every load-bearing rule (one a decision depends on) also has a claim in `sources.yaml` citing its source: an operator rule as `USER_STATED` with its date, an external fact with a primary source and its retrieval date,
and its capture kept verbatim under `documents/` with a `readme.md` index. Material not checked against a source is labelled `UNVERIFIED`, never stated as fact.

## Why

The pack is loaded into other projects as guidance. A rule with no reason cannot be judged when it collides with a project, and a rule with no source cannot be re-checked when the tool or standard it
describes changes.

## Enforcement

`tests/test_package_contract.py`: `test_claim_ledger` (ledger schema) and `test_claim_captures_exist` (each cited capture is present). Which rules
are load-bearing, and that each rule says why, are checked by review: no test can tell a reason from a restatement.
````

## File: .archcore/index.guide.md
````markdown
---
title: Archcore index — skill-coder
status: accepted
tags: [index]
---

Durable index of the decisions and rules recorded for skill-coder. Accepted documents are the highest-authority statement of what the pack has decided; supersede one in place with a dated note naming
its replacement rather than deleting it. All nine record operator decisions or stated rules of 2026-10-19, each from a source it names. Two (the runtime ADR and the code-map rule) were first written
outside skill-ai-it's `promote` mode and held as `proposed`; the operator approved their promotion the same day, after a review that also corrected four entries (2026-10-19, CHANGELOG).

## adr/

| Document                                    | Status   |
| ------------------------------------------- | -------- |
| [default-activation-waits-for-testing.adr.md](adr/default-activation-waits-for-testing.adr.md) | accepted |
| [helpers-run-in-target-environment.adr.md](adr/helpers-run-in-target-environment.adr.md) | accepted |
| [naming-mapping-is-data.adr.md](adr/naming-mapping-is-data.adr.md) | accepted |

## rules/

| Document                                    | Status   |
| ------------------------------------------- | -------- |
| [code-map-holds-decisions-only.rule.md](rules/code-map-holds-decisions-only.rule.md) | accepted |
| [cross-project-write-back.rule.md](rules/cross-project-write-back.rule.md) | accepted |
| [helpers-are-portable-and-catalogued.rule.md](rules/helpers-are-portable-and-catalogued.rule.md) | accepted |
| [pack-text-stays-generic.rule.md](rules/pack-text-stays-generic.rule.md) | accepted |
| [rule-precedence.rule.md](rules/rule-precedence.rule.md) | accepted |
| [rules-cite-sources.rule.md](rules/rules-cite-sources.rule.md) | accepted |

## Never promoted, and why

| Candidate area                                                                                               | Reason                                                                                |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| specs/ — claim ledger and code-map schemas                                                                   | Specified executably by `tests/test_package_contract.py` and `scripts/code_map.py`    |
| Rules from the global policy, governance `coding-guide.md` and project code designs                          | Governed at their source; the pack cites them                                         |
| The programming rules in `references/` and `languages/` (naming convention, layering, timeouts, write gates) | Pack content, governed in its reference files with claims in `sources.yaml`; an       |
|                                                                                                              |   Archcore copy would drift                                                           |
| Research sources verbatim under `documents/`; docstrings with Args and Returns; no inline linter suppression | Global policy and operator feedback rules, inherited                                  |
| "Fix the project, not the check" and the other governance-checker rules                                      | skill-ai-it's managed governance block in `AGENTS.md`, owned upstream                 |
| Package version only in the `CHANGELOG.md` release heading                                                   | A one-line file convention in `AGENTS.md`, not a decision; no check enforces it       |
| `SCRATCHPAD.md` open items (adopt helpers in another project, Ansible module limit, shell limits UNVERIFIED) | Unresolved; promote once decided                                                      |
````

## File: docs/history/changelog-20261027_1213.md
````markdown
---
Title: Changelog archive 20261027_1213
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-19 00:00 to 2026-10-19 00:00
Last reviewed: 2026-10-27
Summary: 1 entries rotated out of CHANGELOG.md on 20261027_1213 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261027_1213

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 2026-10-19 | 0.1.0 — 2026-10-19 |  |

## 0.1.0 — 2026-10-19

### 20261019_1635 — Pack created

- Created (operator, 2026-10-19: "create skill-coder and capture all the intelligence for the programming in general ... programming language agnostic ... specific each language type of override that
  can be tweaked later"). Governance scaffold from skill-ai-it templates; content from the operator's rules (unified-network-controller code architecture design R1-R36, global policy, governance
  categories, auto-memory feedback) and primary sources (see `sources.yaml` and `documents/`).
- Helpers promoted from unified-network-controller and made generic, each characterised against the original: `import_layers.py` (from `scripts/checks/import_graph.py`: same 4 cycles on the same
  roots, same layer verdict), `write_gates.py` (from `check_write_gates`: with the project's patterns and register, 51 writers, every one gated or registered, as the project's own check). New:
  `code_size.py` (rule R34 with a warn tier: modules 300/400, functions 40/60, shell 100/200), `call_timeouts.py` (R15), `script_headers.py` (header = a script's front matter: summary, run line,
  safety), `code_map.py` and `templates/code-map.toml` (operator, 2026-10-19: one intent file for code, TOML so it is read with the project's own Python), `ratchet.py` (the shrink-only baseline).
- Runtime rule decided (operator, 2026-10-19): helpers run in the target project's environment with its interpreter; the pack's own interpreter only as a fallback; nothing installed into a project.
- Measured on unified-network-controller (read-only, 2026-10-19): 25 modules over 400 lines and 68 functions over 60; 30 runnable scripts with header gaps. Not acted on: recorded there as candidates.

### 20261019_1711 — Installed, not default; recipes kebab-case; behaviour evaluation

- Installed (operator, 2026-10-19: "install it as skill but dont make it default yet"): directory symlinks in `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain`, and a row in the
  skills_stuff `README.md`. The global routing line stays pending (SCRATCHPAD, Activation).
- Recipes renamed to kebab-case by skill-ai-it's upgrader after its rename map was inverted (`nav-upgrade`, `lint-md`, `audit-scripts` and the rest); the `[naming.exceptions]` kept for them were
  removed, and `naming_check.py` now reports no name off the mapping.
- Tests: behaviour evaluation of C-S02, C-S04 and C-S17 with and without the skill (results in SCRATCHPAD); new contract check that every capture a claim cites exists (the sample check done by hand,
  made permanent). 42 tests.
- Incident, corrected the same session: `.archcore/` ADR and rule were written directly during bootstrap and marked `accepted`, against
  `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/archcore-routing.md` (only `promote` writes Archcore content, with the operator's authorization). Found while
  reviewing that pattern for `just check`; both now `proposed`, awaiting the operator's promotion approval. `archcore status` passes.
- Feedback to all-scraper: the ShellCheck wiki page answered with a bot challenge during research; recorded in its `ROADMAP.md` Backlog.
````

## File: docs/history/changelog-20261028_1943.md
````markdown
---
Title: Changelog archive 20261028_1943
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-19 16:43 to 2026-10-19 16:43
Last reviewed: 2026-10-28
Summary: 1 entries rotated out of CHANGELOG.md on 20261028_1943 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261028_1943

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261019_1643 | 20261019_1643 — deterministic navigation |  |

## 20261019_1643 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md
````

## File: docs/history/changelog-20261028_2101.md
````markdown
---
Title: Changelog archive 20261028_2101
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-19 17:12 to 2026-10-19 17:12
Last reviewed: 2026-10-28
Summary: 1 entries rotated out of CHANGELOG.md on 20261028_2101 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261028_2101

## Index

| Stamp | Section | First line |
| --- | --- | --- |
|  | Unreleased |  |

## Unreleased

- 20261027 Pattern P-32 "Repoint callers after a move: plan, skip history, guard local namesakes" in `references/design-patterns.md` (skill-ai-it scripts reorganisation; reusable_candidate).
- 20261027 Learned in `references/safety-and-writes.md`: write_gates' default patterns skip local file writes; a package that rewrites governed files adds `write_patterns` (skill-ai-it: 0 to 23 writers, two ungated).
- 20261027 Learned in `references/version-control-and-review.md`: simulate a cherry-pick with `git merge-tree --merge-base` (no checkout); read a branch list whole (skill-smc `ansible_change_reach`).
- 20261027 Pattern P-31 "Append-only event ledger, content-derived IDs and approval bound to a body digest" in `references/design-patterns.md` (skill-knowledge-curator v1; reusable_candidate).
- 20261027 Pattern P-30 "Solve in a canonical frame, then transform the result" in `references/design-patterns.md` (skill-drawio fold; reusable_candidate).
- 20261027 Learned in `references/refactoring-and-promotion.md` (Moving code): prove a move unchanged with per-file sha256 plus a hash of the CLI output; no shim for an untracked prototype with no callers (skill-goal-guard 1dff9c8; reusable_candidate, owed from the 15:03 session).
- 20261027 Learned in `references/safety-and-writes.md`: `write_gates.py` sees entry points only; writes in library modules reached through `--apply` report "0 writers"; gate in the writer, test the plan, name the paths in the code map (skill-goal-guard).
- 20261026 Learned in `references/safety-and-writes.md`: `pgrep -f`/`pkill -f` match their own task when the pattern is in Ansible `environment:` (remote command line) or in the script text; pass it base64-encoded, spell commands through a variable (ansible-wifi smc_change).
- 20261026 Learned in `references/safety-and-writes.md`: complete only after cleanup; retain the original transaction and manifest across partial retries (controller red/green fixtures).

- 20261026 Learned 2026-10-26 in `references/version-control-and-review.md`: commit your own hunks while another session edits the same files (blob staging, proved in a scratch worktree)
- 20261026 Learned 2026-10-26 in `references/testing.md`: test through the entry point the user triggers; a host's default can depend on the call path (skill-drawio click actions)
- 20261023 Learned 2026-10-23 in `languages/yaml-json-toml.md`: a backtick cannot start a plain YAML scalar or flow-sequence item; quote it (unified-network-controller flow map)
- 20261023 Learned 2026-10-23 (b) in `languages/python.md` (pyright executionEnvironments for joined modules, not inline suppression) and Learned 2026-10-23 (b) in `references/generated-artifacts.md` (no `--` in an XML banner).
- 20261023 `just test` green again: 2026-10-23 entries labelled `VERIFIED-OBSERVED` relabelled `VERIFIED_PRIMARY` (text unchanged) in `languages/python.md`, `languages/yaml-json-toml.md`, `languages/ansible.md`, `languages/shell.md`; Learned 2026-10-23 (e) in `languages/ansible.md` given its missing Falsifier.
- 20261023 Operator rule in `SKILL.md`: one root linter per language for new files only. Learned 2026-10-23 in `languages/yaml-json-toml.md` (taplo, biome, djlint), `languages/shell.md` (shfmt editorconfig ignore, shellcheck from shfmt -f), and 2026-10-23 (f) in `languages/ansible.md` (include_tasks file:, folded-scalar newline, check_mode false for reads, inventory parse lint, controller-side state).
- 20261023 Learned 2026-10-23 (d, e) in `languages/ansible.md` (`-l` skips localhost plays, `'\n'` in folded scalars, file lookup of a list, unreachable hosts skipped without stopping a run; comment only tasks that need it) and 2026-10-23 in `languages/python.md` (ruff two-space, new files only with force-exclude, git-excluded symlinks, f-string backslash before 3.12).
- 20261023 Operator rule in `SKILL.md`, `languages/python.md`, `languages/shell.md`: two-space indentation in every language; ruff (`indent-width = 2`) formats and lints Python as yamllint does YAML.
- 20261023 Learned 2026-10-23 (a, b, c) in `languages/ansible.md`: `environment:` values sit on the remote command line (pgrep -f self-match, ps-visible); a skipped task re-registers its variable; block/rescue run records and `argv: [/bin/sh, -c]` for operator shell strings.
- 20261023 Learned 2026-10-23 in `references/generated-artifacts.md`: Quick Look previews only the first sheet of an .xlsx and collapses empty rows; review a moved-sheet copy and give spacer rows a height.
- 20261022 Learned 2026-10-22 (f) in `references/generated-artifacts.md`: size a hook-run formatter change, old against new, before it ships.
- 20261022 Learned 2026-10-22 (e) in `languages/python.md`: resolve the root as well as the target before `is_relative_to` (macOS /var is /private/var).
- 20261022 Learned 2026-10-22 (d) in `languages/shell.md`: tsh exits 1 on TERM; a deadline helper returns 124 on its own clock.
- 20261022 Learned 2026-10-22 (c) in `languages/shell.md`: a background job reads /dev/null only with job control on; `"$@" <&0 &` keeps a piped stdin under a deadline watcher.
- 20261022 Learned 2026-10-22 (b) in `languages/shell.md`: `dpkg-query -W '<glob>'` lists packages that are not installed; filter on `${db:Status-Abbrev}` = `ii`.
- 20261022 Learned 2026-10-22 in `languages/shell.md`: a later `</dev/null` replaces a here-string as stdin, so `bash -s` reads nothing; one stdin redirection per command.
- 20261021 Learned 2026-10-21 (b) in `references/refactoring-and-promotion.md`: find a moved file's readers by path, not only its importers.
- 20261021 Learned 2026-10-21 in `references/refactoring-and-promotion.md`: promote with `--project-root`, project strings as data (pilot byte-identical), and project checks loading the skill script by path.
- 20261021 Learned 2026-10-21 in `references/testing.md`: prove a reformatter moved no content by comparing rebuilt structure cell by cell, with a negative test.
- 20261021 Learned 2026-10-21 in `references/generated-artifacts.md`: a page rendered from the clock is rendered in the commit gate; its check notes, never fails, on date-only drift.
- 20261021 Learned 2026-10-21 in `languages/python.md`: register a path-loaded module in `sys.modules` before `exec_module` when it defines a dataclass.
- 20261021 Learned 2026-10-21 in `references/version-control-and-review.md`: per-project commit tool for a shared clone (shared lock, folder `git add -A --`, pathspec commit, rebase only on a clean tree; apn scripts/project_commit.py).
- 20261021 Learned 2026-10-21 in `languages/shell.md`: macOS has no `timeout`; give a command a deadline with `perl -e 'alarm N; exec @ARGV'`.
- 20261020 Learned 2026-10-20 (c) in `languages/shell.md`: a command reading stdin inside a script sent as `bash -s` swallows the rest of the script; `ssh -n`, `< /dev/null`. `references/errors-and-timeouts.md`: a stop handler ends its children in their own sessions first (registry, `end_all`; unified-network-controller 3f3bfcb).
- 20261020 Learned 2026-10-20 (b) in `references/testing.md`: a helper's OK says nothing about folders outside its roots (`--list` it). Learned 2026-10-20 in `languages/shell.md`: perl alarm before exec does not stop tsh; a watcher does. Learned 2026-10-20 in `languages/ansible.md`: render a role template outside the role with the task's options, role vars and role-precedence defaults.
- 20261020 Learned 2026-10-20 (b) in `languages/python.md`: place an inserted import from the AST, never by matching lines (imports inside remote-agent strings matched; unified-network-controller).
- 20261020 `group_timeouts.py` also counts a `Popen(...)` stopped with `.kill()`/`.terminate()` in the same function without `start_new_session=`/`process_group=` (a collector's per-site limit; flagged the old code, passes the fix, unified-network-controller 36fa18e).
- 20261020 `group_timeouts.py`: `tsh` is not a spawner (`tsh ssh` connects in-process; it is what ssh starts as the proxy); seven false positives in its first project run.
- 20261020 `code_map.py` accepts `[group_timeouts]` and `[suppressions]` (roots, baseline); `templates/code-map.toml` shows both; SETUP.md reviewed (still accurate).
- 20261020 New read-only helpers (operator, 2026-10-20: more rules as checkers, and a skeleton rather than written code): `scripts/suppressions.py` (inline linter suppressions per language, ratchet), `scripts/group_timeouts.py` (timed ssh/shell subprocess calls whose children outlive the timeout, ratchet), `scripts/scaffold.py` (prints a Python or shell script and its test meeting the pack's rules; writes nothing). Recipes, catalogue, SKILL.md routing, `just self-check` runs the two checkers on the pack; tests in `tests/test_quality_helpers.py`; the contract test now reads every `tests/test_*.py`. First finding: the `# type: ignore` in `scripts/check_governance.py`, fixed in skill-ai-it's template and this copy with an explicit type check.
- 20261020 Learned 2026-10-20 in `references/errors-and-timeouts.md`: a timed subprocess that starts children (ssh ProxyCommand, a shell) ends its whole process group (unified-network-controller 3efcb27).
- 20261020 Learned 2026-10-20 in `references/testing.md`: a guard test asserts which guard refused (message or distinct code), not the exit code alone; prove red with only that guard removed (smc-resiliency `_script-guards`).
- 20261020 `just test` green again: the five 7f4a7fc-era entries labelled `VERIFIED-OBSERVED` relabelled `VERIFIED_PRIMARY` (observed in the project's running code; text otherwise unchanged) in `references/refactoring-and-promotion.md`, `references/tooling-and-runtime.md`, `languages/python.md`, `languages/shell.md`; the private ATA address in `references/testing.md`'s excerpt replaced by the documentation address 192.0.2.53.
- 20261020 Learned 2026-10-20 in `references/version-control-and-review.md`: `rebase -X theirs` keeps the local side on conflicting hunks only; non-conflicting remote hunks still apply, so diff against a pre-rebase backup branch (vagrant_stuff 62f03f1).
- 20261020 Learned 2026-10-20 (b) in `references/refactoring-and-promotion.md`: proving a package or folder move unchanged (tests, byte-identical renders from a HEAD worktree, imports in the built runtime, the check); one-pass rewrites; what a text rewrite cannot see; a moved folder mapped by prefix.
- 20261020 Learned 2026-10-20 in `references/version-control-and-review.md`: in a clone shared by concurrent sessions commit by pathspec (`git commit -- <paths>`, `git add -N` for new files); a plain `git add` then commit let another session's commit take the staged files (apn b64a075).
- 20261020 Learned 2026-10-20 in `references/security.md`: gpg-agent's socket path limit breaks a throwaway GNUPGHOME under a deep folder; short `$HOME/.k.XXXX`, `--passphrase-file`, keep the creation-time revocation certificate (smc-resiliency `/Volumes/Data/_ai/_project/project_stuff/apn/smc-resiliency/scripts/make_release_key.sh`).
- 20261020 Made the default for code (operator: "if you are now happy with skill-coder, promote it as well"), after use in smc-resiliency and skill-ai-it (adopt_code_map.py, drift and code-map checks proven red, a release-key script): global policy `~/.agents/AGENTS.md` names it for any code beside `safe-change-validation` (Codex synced); the broad `SKILL.md` trigger restored; `/Volumes/Data/_ai/_skills/skills_stuff/.agents/skill-surfaces.md` row; `/Volumes/Data/_ai/governance/categories/coding-guide.md` links it as its detailed pack (content only, no `/Volumes/Data/_ai/governance/sync-map.yaml` change). The skills_stuff and project_stuff root AGENTS.md and each of the operator's skill packs with scripts name it for script changes.
- 20261020 Learned 2026-10-20 in `references/testing.md` (b: real captured sample at the production cut), `languages/shell.md` (`pkill -f` kills its own ssh session) and `languages/python.md` (SystemExit escapes `except Exception` in a pool) (unified-network-controller).
- 20261020 Learned 2026-10-20 in `references/refactoring-and-promotion.md`: adopt `code-map.toml` by moving decisions and keeping the project's checks; assert equality before deleting the old files (unified-network-controller).
- 20261020 Write-back contract: every entry recording how something is done carries a code excerpt (source path, commit) and, for a visual surface, a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` (operator, 2026-10-20).
- 20261020 Learned 2026-10-20 in `references/testing.md`: tie a mirror tool's inputs (preview scripts, image build context) to their source by a test that can fail (unified-network-controller).
- 20261020 Learned 2026-10-20 in `references/tooling-and-runtime.md`: forward recipe arguments with `[positional-arguments]` and `"$@"`, never `{{args}}` (unified-network-controller).
- Learned 2026-10-19 in `languages/python.md`: `Counter.most_common()` ties from set-built counts change order between runs; sort by `(-count, name)`.
- Learned 2026-10-19 in `languages/shell.md`: a multi-line command without `set -e` runs on after a failed edit step; guard it and run destructive steps separately.
- 20261019 `scripts/import_layers.py` graph report reproduces unified-network-controller's `scripts/checks/import_graph.py` field for field, so that
  script retired: a root ending `:self` keeps its folder as the package name; the report adds entry points, `sys.path` users, never-imported modules
  and unparsed files (`analyse()`, `render()`, `--json`); cross-package edges count each import statement; fan-in ties are ordered by name (they
  came from a set, so equal counts swapped between runs). Proof: identical JSON on UNC's four roots (601 lines). Tests in
  `tests/test_import_graph_report.py` (kept apart so `tests/test_helpers.py` stays within its 400-line limit). UNC's `check_import_layers` now calls
  `layer_violations()` (same verdict, its baseline file unchanged).
- 20261019 `ROADMAP.md` and `SETUP.md` added (operator, 2026-10-19: "add ROADMAP.md in both the skills", "and SETUP.md"), to skill-ai-it's templates; ROADMAP from this pack's SCRATCHPAD open items and unified-network-controller's retirement assessment, SETUP from the justfile, `.mise.toml` and requirements. README lists both and links SETUP from Quick start.
- 20261019 `context-map.yaml` and `repomix.config.json` no longer name the deleted `ARCHCORE_PROMOTION_CANDIDATES.md`; routing points at
  `.archcore/index.guide.md` (skill-ai-it pitfall, 2026-10-19).
- 20261019 Learned entry in `languages/python.md` (2026-10-19): after a `sys.path` seam, load modules with `importlib.import_module` instead of
  imports below code, so no `# noqa` is needed (from building skill-drawio's UNC wrapper and tests). `AI_NAVIGATION.md` pack routing mirrors the
  `SKILL.md` row for `module_groups.py`.
- 20261019 Calling projects write back (operator, 2026-10-19: "add the write back mechanism so that whatever learning is there, any project which is calling skill
  coder should write that learning back"): `references/evolution-and-write-back.md` gains "Projects that call this skill" (engaged means used; the calling session
  writes, reads back and commits here; the fixed parking heading `## skill-coder write-back candidates`); new read-only helper `scripts/write_back.py`
  (`just write-back`) lists parked entries in a project, with tests; `templates/project-agents-write-back.md` is the line a project may add to its AGENTS.md;
  `SKILL.md` and `AGENTS.md` state the obligation; skill-slurp-chat Step 5b lists skill-coder whenever code was written and runs the helper.
- 20261019 Module families become packages (operator, 2026-10-19: "is it better to create subdirectory under scripts and put all the related modules under that relevant
  folder with a proper name? ... make it part of the skill coder logic"): `references/module-and-function-shape.md` gains "Grouping modules into packages" (three or more
  modules sharing a prefix are a package; entry points stay at the top of `scripts/`; package names unique across loaded packs; one level, two at most);
  `languages/python.md` maps it (regular packages, relative imports, no namespace packages); new warn-only helper `scripts/module_groups.py` (`just module-groups`,
  `--strict` in `just self-check`), with tests.
- 20261019 Seven of the nine archcore entries (activation and naming ADRs; write-back, helpers, generic text, precedence and cite-sources rules)
  were written by a parallel session on the operator's instruction to add the missing entries, then reviewed here.
- 20261019 Archcore review (operator: "assess the archcore entries ... are they correct logically? any missing?", then "yes apply all"): all nine accepted
  (runtime ADR and code-map rule promoted); helpers rule allows the explicit `--write-baseline` write and exempts imported modules from recipes;
  code-map rule names `[scan.exclude]`, `[naming]` and their reason checks; rules-cite-sources limited to load-bearing rules; runtime ADR lists the
  missing skill pin and untested 3.11 as open; activation ADR records the narrowed description. `SKILL.md` description narrowed to invoke-by-name
  until activation (operator: "narrow until activation"). References gain the decided size tiers (`module-and-function-shape.md`) and the script
  header standard (`documentation-and-headers.md`), which had lived only in code and this log.

- 20261019 Archcore promotion (operator, 2026-10-19: "assess and add missing archcore entries"): 7 new accepted documents, each naming its source and enforcement. ADRs `naming-mapping-is-data`,
  `default-activation-waits-for-testing`; rules `rule-precedence`, `rules-cite-sources`, `cross-project-write-back`, `pack-text-stays-generic`, `helpers-are-portable-and-catalogued`.
  `.archcore/index.guide.md` lists them and records the candidates not promoted, with reasons; tags consolidated to a shared set. The two earlier records stay `proposed`.

- 20261019 skill-ai-it refresh: navigation blocks already at `2026-10-14-compact-v2` (dry run, no changes). `just govern` failed on 3 doc-freshness findings, fixed rather than baselined:
  `context-map.yaml` gains its header summary comment; the two proposed Archcore records (`.archcore/adr/helpers-run-in-target-environment.adr.md`,
  `.archcore/rules/code-map-holds-decisions-only.rule.md`) gain `Last reviewed: 2026-10-19` from their own `created` date. `just check`, `just test` (42), `just nav-validate` and `archcore doctor`
  pass.

- 20261019 Naming as data (operator, 2026-10-19: "is it better to have a json or yaml or toml file for the mapping"): `naming.toml` (TOML, read with the project's own Python) is the source;
  `scripts/naming_table.py` renders the table in `references/naming-conventions.md` (drift fails `just self-check`); `scripts/naming_check.py` checks file and `just` recipe names, with project
  overrides and reasoned exceptions in `code-map.toml` `[naming]`. Measured read-only: unified-network-controller 6 template recipes off the rule, no file; ansible-wifi 11 files (hyphenated or
  camelCase `.py`/`.sh`). Governance `/Volumes/Data/_ai/governance/categories/coding-guide.md` naming clause revised to the same rule.

- 20261019 Naming mapping (operator, 2026-10-19: "define a mapping for language against convention"): new `references/naming-conventions.md`, every row checked against a primary source (26 new
  captures); the rule is code files and identifiers follow their language, typed commands are kebab-case, a tool's parser wins. `module-and-function-shape.md` points to it; claims C-C72 to C-C79.
  `languages/ansible.md` gains the tag-rename transition step (behaviour evaluation gap). Shared `scripts/pyparse.py`; shell heredoc and `${#` fixes in `code_size.py` (found on a second repository).
````

## File: docs/history/changelog-20261101_2353.md
````markdown
---
Title: Changelog archive 20261101_2353
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-26 21:46 to 2026-10-26 21:46
Last reviewed: 2026-11-01
Summary: 1 entries rotated out of CHANGELOG.md on 20261101_2353 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261101_2353

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261026_2146 | 20261026_2146 — Ansible: until does not  |  |

## 20261026_2146 — Ansible: until does not retry unreachable; async drop-proof waits; callbacks_enabled in 2.21

- `languages/ansible.md`: Learned 2026-10-26 (e) - until/retries and unreachable hosts, async + await pattern, async shell in check mode, callback_whitelist ignored in 2.21, callback options are a literal DOCUMENTATION (local-knowledge-ansible `76b0f86`).
````

## File: docs/history/changelog-20261102_1132.md
````markdown
---
Title: Changelog archive 20261102_1132
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-26 22:22 to 2026-10-26 22:22
Last reviewed: 2026-11-02
Summary: 1 entries rotated out of CHANGELOG.md on 20261102_1132 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261102_1132

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261026_2222 | 20261026_2222 — Ansible: run_once is per |  |

## 20261026_2222 — Ansible: run_once is per serial batch, results reach every host

- `languages/ansible.md`: Learned 2026-10-26 (f) - run_once applies include_vars, set_fact and register to all batch hosts; when judged on the first host; once per batch, not per run.
````

## File: docs/history/changelog-20261102_1348.md
````markdown
---
Title: Changelog archive 20261102_1348
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-27 10:45 to 2026-10-27 10:45
Last reviewed: 2026-11-02
Summary: 1 entries rotated out of CHANGELOG.md on 20261102_1348 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261102_1348

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261027_1045 | 20261027_1045 — Ansible: once-per-run pl |  |

## 20261027_1045 — Ansible: once-per-run play, test precedence, ssh retry backoff, include apply; git -C paths

- `languages/ansible.md`: Learned 2026-10-27 (g) once-per-run play before the serial play with group_by keeps batches dense; (h) parenthesise a filter chain before a Jinja test; (i) ssh retries only
  rc 255, pauses 2^n-1 capped 30 s, 8 retries ride out ~117 s, per-play `ansible_ssh_retries`; (j) `run_once` on include_tasks needs `apply`, a skipped task still registers.
- `languages/python.md`: Learned 2026-10-27 `git -C` resolves a relative destination under its directory; resolve paths first.
````

## File: docs/history/changelog-20261102_1434.md
````markdown
---
Title: Changelog archive 20261102_1434
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-27 10:49 to 2026-10-27 10:49
Last reviewed: 2026-11-02
Summary: 1 entries rotated out of CHANGELOG.md on 20261102_1434 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261102_1434

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261027_1049 | 20261027_1049 — Design patterns referenc |  |

## 20261027_1049 — Design patterns reference: out-of-the-box logic from smc_change, per language

- `references/design-patterns.md` (new, operator 2026-10-27: capture the out-of-the-box logic so projects without SMCs benefit; like
  skill-nautobot's capability patterns): Learned 2026-10-27 (a-l), twelve patterns from the smc_change engine (generic engine, baseline
  gates, write-ahead journal with fingerprint, done ledger by target hash, prepare once then partition, detached long step, evidence tree,
  shared pool, joined plug-in probe, fail-open filters, code freeze under open transactions, plan then apply), each with Ansible and Python
  realisations. `SKILL.md`: routing row and a write-back contract paragraph making patterns owed by calling projects; pointers from
  `languages/ansible.md` and `languages/python.md`.
- `references/safety-and-writes.md`: Learned 2026-10-26 entry given its missing `Source:` field (contract test failed since 0918fc0) and its
  site name removed.
````

## File: docs/history/changelog-20261105_1156.md
````markdown
---
Title: Changelog archive 20261105_1156
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-27 11:15 to 2026-10-27 11:15
Last reviewed: 2026-11-05
Summary: 1 entries rotated out of CHANGELOG.md on 20261105_1156 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261105_1156

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261027_1115 | 20261027_1115 — Design patterns harveste |  |

## 20261027_1115 — Design patterns harvested from unified-network-controller and smc-resiliency (P-13 to P-29)

- `references/design-patterns.md`: Learned 2026-10-27 (m)-(z) and three more: P-13 to P-29 harvested from unified-network-controller
  (capability table, rollback classes and end states, ownership axes, neutral contract by two consumers, stale-lock proof, class rules with
  deny-wins exceptions, ranked-evidence evals, migration ratchet) and smc-resiliency (fallback chain, destroy-what-changed, scratch build and
  sandbox validation, signed newer-only config, self-guarding probe, verdict ledger; recovery on immutable parts and clock floor as design
  only). Dead-man revert timer (P-15) found in both projects; P-02 and P-10 gained a second project. Every key line was checked against its
  source before writing (17 of 17 found).
````

## File: docs/history/changelog-20261105_2139.md
````markdown
---
Title: Changelog archive 20261105_2139
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-27 12:13 to 2026-10-27 12:13
Last reviewed: 2026-11-05
Summary: 1 entries rotated out of CHANGELOG.md on 20261105_2139 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261105_2139

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261027_1213 | 20261027_1213 — Ansible: to_json in debu |  |

## 20261027_1213 — Ansible: to_json in debug output is escaped twice

- `languages/ansible.md`: Learned 2026-10-27 (k) - `to_json` inside a `debug` message list is escaped twice; write operator lines as words.
````

## File: docs/history/changelog-20261106_1030.md
````markdown
---
Title: Changelog archive 20261106_1030
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-27 15:01 to 2026-10-27 15:01
Last reviewed: 2026-11-06
Summary: 1 entries rotated out of CHANGELOG.md on 20261106_1030 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261106_1030

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261027_1501 | 20261027_1501 — Ansible include_tasks an |  |

## 20261027_1501 — Ansible include_tasks and lockstep batches, bash 3.2 empty arrays

- `languages/ansible.md` Learned 2026-10-27 (l) `include_tasks` loads when reached, so editing task files changes a running play; (m)
  `serial` batches run in lockstep, so stage-marker timers measure the batch, not the host.
- `languages/shell.md` Learned 2026-10-27: bash 3.2 `set -u` with an empty array; use `${arr[@]+"${arr[@]}"}` (verified on /bin/bash 3.2.57).
````

## File: docs/history/changelog-20261107_1723.md
````markdown
---
Title: Changelog archive 20261107_1723
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 13:11 to 2026-10-28 13:11
Last reviewed: 2026-11-07
Summary: 1 entries rotated out of CHANGELOG.md on 20261107_1723 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261107_1723

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_1311 | 20261028_1311 — process_match.py: unanch |  |

## 20261028_1311 — process_match.py: unanchored pgrep/pkill -f patterns become a check

- `scripts/process_match.py` (new): reports `pgrep -f` / `pkill -f` literal patterns not anchored with `^` in shell, YAML, Python and Jinja;
  comments and run-time patterns skipped. Tests in `tests/test_quality_helpers.py`; recipe `just process-match`; catalogued; `[process_match]` code-map section.
- `references/safety-and-writes.md` Learned 2026-10-28: anchor process patterns at the program and check them (four self-matches in ansible-wifi smc_change).
- `SKILL.md`: standing rule for anchored process patterns; tools table row.
````

## File: docs/history/changelog-20261107_1732.md
````markdown
---
Title: Changelog archive 20261107_1732
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 19:42 to 2026-10-28 19:42
Last reviewed: 2026-11-07
Summary: 1 entries rotated out of CHANGELOG.md on 20261107_1732 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261107_1732

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_1942 | 20261028_1942 — cpuprofile_summary helpe |  |

## 20261028_1942 — cpuprofile_summary helper

Added `scripts/cpuprofile_summary.py` (recipe `just cpuprofile-summary`, tests `tests/test_cpuprofile_summary.py`): reads V8 .cpuprofile files and
prints self time per extension, the hottest functions and the hottest stacks of the busiest (or `--ext`) extension. Read-only, stdlib only. Promoted
from the ansible-wifi session of 2026-10-28, where VS Code's Git view went stale because Foam pinned the extension host; the summary traced it to
Foam's orphans/placeholders refresh. Pre-existing, not from this change: `test_write_back_entries_logged` fails on a 2026-10-27 entry.
````

## File: docs/history/changelog-20261109_1222.md
````markdown
---
Title: Changelog archive 20261109_1222
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 21:01 to 2026-10-28 21:01
Last reviewed: 2026-11-09
Summary: 1 entries rotated out of CHANGELOG.md on 20261109_1222 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261109_1222

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_2101 | 20261028_2101 — Learned: freeing a lock  |  |

## 20261028_2101 — Learned: freeing a lock another process holds

`references/safety-and-writes.md`: Learned 2026-10-28 "freeing a lock another process holds": decide by the locks the holder has (end a refresh,
never a writer), never delete lock files, owner by device and inode. From the ansible-wifi apt lock guard (plans/apt-lock-guard-20261028_2055).
````

## File: docs/history/changelog-20261109_2227.md
````markdown
---
Title: Changelog archive 20261109_2227
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 22:29 to 2026-10-28 22:29
Last reviewed: 2026-11-09
Summary: 1 entries rotated out of CHANGELOG.md on 20261109_2227 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261109_2227

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_2229 | 20261028_2229 — Learned: a symlinked sou |  |

## 20261028_2229 — Learned: a symlinked source ships whatever is checked out

references/safety-and-writes.md: pin a copy from the commit when a deploy needs a specific version; a link only when the target cannot vary by branch (ansible-wifi apt-info-no-update, 2026-10-28).
````

## File: docs/history/changelog-20261110_1246.md
````markdown
---
Title: Changelog archive 20261110_1246
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 22:37 to 2026-10-28 22:37
Last reviewed: 2026-11-10
Summary: 1 entries rotated out of CHANGELOG.md on 20261110_1246 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261110_1246

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_2237 | 20261028_2237 — Learned: shared justfile |  |

## 20261028_2237 — Learned: shared justfile recipes and the editor

references/configuration-and-literals.md: an imported recipe file defines no variables (justfile_directory, source_directory); the VS Code just extension does not follow import for names but flags duplicates (ansible-wifi change.just, 2026-10-28).
````

## File: docs/history/changelog-20261111_1100.md
````markdown
---
Title: Changelog archive 20261111_1100
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-28 23:06 to 2026-10-28 23:06
Last reviewed: 2026-11-11
Summary: 1 entries rotated out of CHANGELOG.md on 20261111_1100 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261111_1100

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261028_2306 | 20261028_2306 — Learned: optimise the re |  |

## 20261028_2306 — Learned: optimise the real outcome, not a proxy

references/design-patterns.md: proxy ranks candidates, the real computation chooses, current state always a candidate (skill-drawio overview placement, 2026-10-28).
````

## File: docs/history/changelog-20261116_1737.md
````markdown
---
Title: Changelog archive 20261116_1737
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-29 12:20 to 2026-10-29 14:24
Last reviewed: 2026-11-16
Summary: 4 entries rotated out of CHANGELOG.md on 20261116_1737 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261116_1737

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261029_1220 | 20261029_1220 — Learned: a check that sk |  |
| 20261029_1257 | 20261029_1257 — Patterns P-33 to P-35 (m |  |
| 20261029_1420 | 20261029_1420 — Pattern P-36: widen a na |  |
| 20261029_1424 | 20261029_1424 — Patterns P-37 and P-38 ( |  |

## 20261029_1424 — Patterns P-37 and P-38 (skill-drawio speed and quality work)

Learned 2026-10-29 in `references/design-patterns.md`: a cache proved by a differential assert, keyed so an undo hits (skill-drawio 73017a9,
811c918); an estimate nominates, the real measure decides, never worse than the start (skill-drawio 1e6557d).


## 20261029_1420 — Pattern P-36: widen a name's scope by renaming in place

Learned 2026-10-29 in `references/design-patterns.md` (P-36), from unified-network-controller `smc_uplink_circuits.rename_legacy`
(e62633c): Circuits and NTDs named per site renamed to per box, never recreated.


## 20261029_1257 — Patterns P-33 to P-35 (multi-SMC build)

`references/design-patterns.md`: read all then write once; pick a moving leader once per cycle; place by evidence with a listed ledger (unified-network-controller, 2026-10-29).


## 20261029_1220 — Learned: a check that skips when its tool is missing cannot fail

Learned 2026-10-29 in `references/testing.md`: report a missing tool, never skip silently (unified-network-controller pre-commit hook, 27 to 29 Oct).
````

## File: docs/history/changelog-20261116_1752.md
````markdown
---
Title: Changelog archive 20261116_1752
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-29 19:15 to 2026-10-29 19:15
Last reviewed: 2026-11-16
Summary: 1 entries rotated out of CHANGELOG.md on 20261116_1752 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261116_1752

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261029_1915 | 20261029_1915 — Pattern P-39: carry a pl |  |

## 20261029_1915 — Pattern P-39: carry a placement over proven edges, narrow by direction

Learned 2026-10-29 in `references/design-patterns.md`: placement over a typed evidence graph, no site convention (unified-network-controller a8c58f9).
````

## File: docs/history/changelog-20261117_1101.md
````markdown
---
Title: Changelog archive 20261117_1101
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-29 19:25 to 2026-10-29 20:35
Last reviewed: 2026-11-17
Summary: 5 entries rotated out of CHANGELOG.md on 20261117_1101 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261117_1101

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261029_1925 | 20261029_1925 — Pattern P-40: hold citat |  |
| 20261029_2012 | 20261029_2012 — Harvest write-back: patt |  |
| 20261029_2027 | 20261029_2027 — Learned: know what the c |  |
| 20261029_2030 | 20261029_2030 — Backfilled log line for  |  |
| 20261029_2035 | 20261029_2035 — Write-back log index (ba |  |

## 20261029_2035 — Write-back log index (backfill)

Learned entries whose CHANGELOG line was rotated away or never named the file, indexed so the write-back contract test can trace each:

- `languages/ansible.md`: Learned 2026-10-23
- `languages/python.md`: Learned 2026-10-19, 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23
- `languages/shell.md`: Learned 2026-10-19, 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23
- `languages/yaml-json-toml.md`: Learned 2026-10-23
- `references/errors-and-timeouts.md`: Learned 2026-10-20
- `references/evolution-and-write-back.md`: Learned 2026-10-19
- `references/generated-artifacts.md`: Learned 2026-10-21, 2026-10-22, 2026-10-23
- `references/refactoring-and-promotion.md`: Learned 2026-10-20, 2026-10-21, 2026-10-27
- `references/safety-and-writes.md`: Learned 2026-10-27
- `references/security.md`: Learned 2026-10-20
- `references/testing.md`: Learned 2026-10-20, 2026-10-21, 2026-10-26
- `references/tooling-and-runtime.md`: Learned 2026-10-20
- `references/version-control-and-review.md`: Learned 2026-10-20, 2026-10-21, 2026-10-26, 2026-10-27


## 20261029_2030 — Backfilled log line for an existing write-back

`languages/ansible.md` Learned 2026-10-20 (ansible-core 2.21.5, smc-resiliency render spike) was written without its CHANGELOG line; logged now so the write-back contract test passes.


## 20261029_2012 — Harvest write-back: patterns P-41 to P-45 and twelve Learned entries

From the 2026-10-29 knowledge harvest of the apn and personal projects (read-only), every entry generic, sources named per entry:

- `references/design-patterns.md` Learned 2026-10-29 to (f): P-41 writing into files live sessions edit (marked region, CAS, settle window, idempotent ids; apn project_sync.py), P-42 FOUND / NOT_FOUND
  / CHECK_FAILED with a negative only from a complete walk, P-43 classify a captured body before storing it as evidence, P-44 surface the unclassified, P-45 an edited document as a contract with a
  fixture; P-01 gains a second shape (one analysis engine, a frozen config per supplier, a written column contract).
- `references/testing.md` Learned 2026-10-29 (b)-(f): prove which mechanism refused; incident regressions assert the refusal; layer invariants by AST scan plus an isolated-interpreter import and a
  negative control; pinned verifier baselines move with provenance; profile source files before analysis.
- `references/safety-and-writes.md` Learned 2026-10-29: per-run scratch files, never a fixed path; (b) a fetch cache is not a filter.
- `references/errors-and-timeouts.md` Learned 2026-10-29: caps, confirmation, pacing and backoff for fan-out fetchers; (b) missing, zero and filtered-empty never render the same. Contents block added
  (the file passed 100 lines).
- `languages/sql.md` Learned 2026-10-29: cast text money at ingestion and assert row counts after every filter.
- `references/configuration-and-literals.md` Learned 2026-10-29: bootstrap applies, rendered files hold persistent state (cloud-init).
- `references/generated-artifacts.md` Learned 2026-10-29: a copied lab VM definition, without keys, drift-checked against its canonical file.
- Skipped as already covered: polling speed-up (efficiency rules), capability-gated write pipeline (P-13, write rules), vendor contract and plug-ins (P-17), folder-scoped commits (version-control
  Learned 2026-10-21), runtime pinning (tooling-and-runtime), fixes go into the generator (generated-artifacts).


## 20261029_1925 — Pattern P-40: hold citations by a check (ledger, local store, rules as findings)

`references/design-patterns.md` P-40, Learned 2026-10-29 from skill-network-architect (check_ledger, fetch_sources, sources_ledger).


## 20261029_2027 — Learned: know what the commit gate runs

Learned 2026-10-29 in `references/version-control-and-review.md`: a gate without tests passed 14 failing tests (unified-network-controller e6dee23).
````

## File: docs/history/changelog-20261117_1859.md
````markdown
---
Title: Changelog archive 20261117_1859
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-30 12:24 to 2026-10-30 12:24
Last reviewed: 2026-11-17
Summary: 1 entries rotated out of CHANGELOG.md on 20261117_1859 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261117_1859

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261030_1224 | 20261030_1224 — Learned: filter preceden |  |

## 20261030_1224 — Learned: filter precedence, free-form shell splitting, import_tasks placement, pipefail with grep -q

Learned 2026-10-30 (ansible-wifi chat cad11710) in `languages/ansible.md` (a: a filter binds tighter than `+`; b: free-form `shell:` splits arguments, use `cmd:`; c: `import_tasks` only inside a play)
and `languages/shell.md` (`pipefail` turns a passing `grep -q` into SIGPIPE 141).

- `languages/ansible.md`: Learned 2026-10-30 (a), (b), (c)
- `languages/shell.md`: Learned 2026-10-30
````

## File: docs/history/changelog-20261118_1557.md
````markdown
---
Title: Changelog archive 20261118_1557
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-30 12:49 to 2026-10-30 12:49
Last reviewed: 2026-11-18
Summary: 1 entries rotated out of CHANGELOG.md on 20261118_1557 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261118_1557

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261030_1249 | 20261030_1249 — Pattern P-46: audience w |  |

## 20261030_1249 — Pattern P-46: audience words at the output boundary, with a leak guard

Learned 2026-10-30 (apn unified-network-controller, site workbook for the site team) in `references/design-patterns.md` P-46: translate the internal platform's words where the file is written, phrase
table then fallback, and refuse the write if the term survives.

- `references/design-patterns.md`: Learned 2026-10-30, P-46
````

## File: docs/history/changelog-20261118_2102.md
````markdown
---
Title: Changelog archive 20261118_2102
Category: archive
Status: archived
Source: CHANGELOG.md
Covers: 2026-10-30 17:21 to 2026-10-30 17:21
Last reviewed: 2026-11-18
Summary: 1 entries rotated out of CHANGELOG.md on 20261118_2102 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261118_2102

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261030_1721 | 20261030_1721 — Pattern P-47 (decide onc |  |

## 20261030_1721 — Pattern P-47 (decide once from facts, persist it); Learned: run_once set_fact freezes templates, 2.21 Jinja quirks

Learned 2026-10-30 (ansible-wifi chat 0a7b835b, smc_change conditions and loop, local-knowledge-ansible 7ef59c7) in `references/design-patterns.md` P-47 and `languages/ansible.md` (d: a run_once
`set_fact` renders host templates once, use a lookup-backed default; e: empty macro returns None, boolean `when`, no `length` test, JSON out of Jinja blocks).

- `references/design-patterns.md`: Learned 2026-10-30, P-47
- `languages/ansible.md`: Learned 2026-10-30 (d), (e)
````

## File: docs/history/changelog-20261119_1538.md
````markdown
---
Title: Changelog archive 20261119_1538
Category: archive
Status: archived
Authority: record
Scope: Entries rotated out of CHANGELOG.md, verbatim
Source: CHANGELOG.md
Covers: 2026-11-01 01:03 to 2026-11-01 01:03
Last reviewed: 2026-11-19
Summary: 1 entries rotated out of CHANGELOG.md on 20261119_1538 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261119_1538

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261101_0103 | 20261101_0103 — Gate output in recipes |  |

## 20261101_0103 — Gate output in recipes

- `references/testing.md`: Learned 2026-11-01, a gate must keep its output in the recipe (Continuum).
````

## File: docs/history/changelog-20261119_1554.md
````markdown
---
Title: Changelog archive 20261119_1554
Category: archive
Status: archived
Authority: record
Scope: Entries rotated out of CHANGELOG.md, verbatim
Source: CHANGELOG.md
Covers: 2026-11-01 19:37 to 2026-11-01 19:37
Last reviewed: 2026-11-19
Summary: 1 entries rotated out of CHANGELOG.md on 20261119_1554 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261119_1554

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261101_1937 | 20261101_1937 — Learned: Jinja dict keys |  |

## 20261101_1937 — Learned: Jinja dict keys through JSON, filtered loop index, folded newlines, CRLF edits

Learned 2026-11-01 in `languages/ansible.md`, from ansible-wifi smc_change.
````

## File: docs/history/changelog-20261119_1601.md
````markdown
---
Title: Changelog archive 20261119_1601
Category: archive
Status: archived
Authority: record
Scope: Entries rotated out of CHANGELOG.md, verbatim
Source: CHANGELOG.md
Covers: 2026-11-01 23:07 to 2026-11-01 23:07
Last reviewed: 2026-11-19
Summary: 1 entries rotated out of CHANGELOG.md on 20261119_1601 to keep it within its budget; verbatim except relative links. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261119_1601

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261101_2307 | 20261101_2307 — Learned: a predicate ans |  |

## 20261101_2307 — Learned: a predicate answering a second question

`references/testing.md`, from skill-knowledge-curator (2026-11-01).
````

## File: docs/history/changelog-20261119_1603.md
````markdown
---
Title: Changelog archive 20261119_1603
Category: archive
Status: archived
Authority: record
Scope: Entries rotated out of CHANGELOG.md, verbatim
Source: CHANGELOG.md
Covers: release 0.2.0, 2026-10-19 to 2026-11-19
Last reviewed: 2026-11-19
Summary: Release 0.2.0 (92 entries) moved out of CHANGELOG.md on 20261119_1603 when it was cut, to keep that file within its budget; verbatim. Read the index first; open an entry only when a live record cites it or the history is the question.
---

# Changelog archive 20261119_1603

## Index

| Stamp | Section | First line |
| --- | --- | --- |
| 20261119 | 0.2.0 — 2026-11-19 |  |

## 0.2.0 — 2026-11-19

Write-backs and reviews since 0.1.0 (2026-10-19): Learned entries from the operator's projects, the 2026-11-19 periodic review of 32 docs.

- 2026-11-19: references/configuration-and-literals.md, Learned 2026-11-19 (header values used as paths); testing.md production proof needs authorisation; stray `this` removed.
- 2026-11-19: periodic review (30-day doc-freshness): 31 files re-read in full and dated 2026-11-19, plus SETUP.md; body rules aligned with their Learned entries, Summaries, Scopes and
  Contents fixed, lifted UNVERIFIED labels where captures and tests now exist, ROADMAP restated (default since 2026-10-20; write-back test red, full scan). No Learned or Disputed entry changed.
- 2026-11-19: languages/rust.md, the `rustls-no-provider` unification recurred from a sibling workspace member (rule tightened), and a new section "Tests, build scripts and limits" (sqlx `migrate!` build script, `#[tokio::test]` starvation, jsonwebtoken leeway and algorithm, Unix socket path length); references/testing.md, mutation checks that never mutated; references/design-patterns.md, exact-commit pre-push gate (continuum-app).
- 2026-11-19: references/tooling-and-runtime.md Learned entries, act on macOS (socket flag only on the command line, host network, image gaps, pinning) and mise into the working cache;
  languages/rust.md Learned entry, sqlx 0.9 dynamic SQL, temporalio macros and missing_docs, per-test databases (Continuum).
- 2026-11-19: languages/rust.md Learned entry under Feature unification, a dependency's default features enabling reqwest `rustls-no-provider` (runtime panic on a green build; Continuum P1 spike).
- 2026-11-18: references/testing.md Learned entry, a fault-test harness that rescues the target must report ASSISTED, not PASS (smc-resiliency bench run).
- 2026-11-18: references/testing.md Learned entry, a justfile catalog check that read variables as recipes, masked by fake catalog rows (Continuum).

- 2026-11-18 new `scripts/reflow_lossless.py` and `tests/test_reflow_lossless.py` (eight cases), recipe `just reflow-lossless`: proves a re-wrapped markdown file changed no table cell and no word
  (operator, 2026-11-18: a lossless check, accept re-wraps); catalogued in scripts/README.md and SKILL.md; named in the Disputed entry of `references/safety-and-writes.md`

- 2026-11-18 `references/safety-and-writes.md`: Disputed, the same day's formatter-hook entry called a lossless re-wrap damage; compare tables un-wrapped cell by cell, not by tokens; a proven-lossless
  reflow is committable (unified-network-controller)

- 2026-11-18 `references/safety-and-writes.md`: Learned, a post-edit formatter hook rewrote a governed file far beyond the edit; compare tokens with HEAD, restore, re-apply by guarded exact
  replacement (unified-network-controller)

- 2026-11-18 `references/tooling-and-runtime.md`: Learned, a closing check recipe runs every step and fails at the end (unified-network-controller)
- 2026-11-18 `references/testing.md`: Learned, smoke-test a changed read-only script on the real host by piping the module over stdin (no file on the host), with the I/O injected for the offline test
  (unified-network-controller)
- 2026-11-18 write-back from apn smc-resiliency (staleness audit 20261118_1715): references/design-patterns.md P-76 (refuse a repeated key when loading YAML; `get_single_data()` instead of a
  suppressed S506).
- 2026-11-18 write-back from apn enterprise-strategy and smc-resiliency (chat 6128bdd9): references/design-patterns.md P-74 (add what a generator cannot write after it saves; prove it in the consuming
  application: slide motion and PowerPoint's own report) and P-75 (learn a person's hand edits: diff against the last build, sort by rule, make habits defaults).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d): languages/ansible/learned-execution.md Learned 2026-11-17 (n) (note unfinished hosts, fail them in the wrapper's last play so they keep the
  later plays).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d, smc_change playbooks): languages/ansible/learned-connections.md Learned 2026-11-17 (m) (`ansible_ssh_timeout` is the connect timeout behind
  "banner exchange"; a play var outranks `-T`).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d, rise 9f17dd64): languages/ansible/learned-lint-and-tests.md Learned 2026-11-17 (a) (a lint delta gate brings a rewritten file's old findings
  in as new) and (b) (`shell` with a pipe: `pipefail` plus `executable: /bin/bash`).

- 2026-11-17 write-back from skill-ascii-diagrams: references/testing.md Learned 2026-11-17 (c) (sweep a repair tool over real files against an independent checker).
- 2026-11-17 write-back from skill-drawio ascii-fix work: references/testing.md Learned 2026-11-17 (b) (same-length mutation reuses a stale `.pyc`; run with `python3 -B`, `touch` after restoring).
- 2026-11-17 write-back from apn smc-resiliency (S1 outlet fault cases, 1eb7ff15): references/design-patterns.md P-73 (fault in the standby side, idempotent restore in `finally`, mount-act-unmount
  keeping rc, harness-owned hard reset); references/testing.md Learned 2026-11-17 (formatter-tolerant fixture edits).
- 2026-11-16 write-back from apn enterprise-strategy (17 Nov meeting deck): references/design-patterns.md P-72 (a short derived deck: reused builders, wording table with must-match rules,
  byte-identical refactor proof); languages/javascript-typescript.md Learned 2026-11-16 (`require.main` run guard; pptxgenjs Company and Subject defaults).
- 2026-11-16 write-back from apn smc-resiliency (ASCII renderer promoted to skill-drawio): SKILL.md Standing rules, a lint config for every project or skill worked on that lacks one (operator,
  2026-11-16); references/refactoring-and-promotion.md Learned (promoting into a pack with no lint config: add ruff.toml with existing files excluded, never re-indent the promoted file; B905 strict
  zip).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (link width and soft wrap): languages/javascript-typescript.md Learned (VS Code soft wrap measures raw text plus injected text; a hiding
  decoration cannot change wrap points).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (table-reflow path rule): references/safety-and-writes.md Learned (a shared tool's default change reaches every hook that calls it: ship
  opt-in, prove with a flag-off run, mtime marker for the live window).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (mermaid full-size patch to markdown-inline-editor): references/design-patterns.md P-71 (anchor-guarded, re-runnable patch of a shipped
  bundle); languages/javascript-typescript.md Learned (load a VS Code extension bundle under Node with a permissive `vscode` stub; compile-only check of an inline script; security-hook false
  positives).
- 2026-11-16 write-back from smc-resiliency (bench power through a Matter strip, afe4f03b): references/design-patterns.md P-70 (physical map as data, the consumer named on each slot);
  languages/python/learned-other.md Learned (a stdlib WebSocket client for a local API).
- 2026-11-13 write-back from enterprise-strategy (weekly update builder, program pack menu card and keys): references/generated-artifacts.md Learned (a second renderer reads the first one's data
  module; a colour key from the states in use; yearless date labels sorted against the plan's first month, a label with no month refused).
- 2026-11-12 write-back from enterprise-strategy (scripts and slides arranged, d7bc439e; YAML view, 64a64b0c): references/refactoring-and-promotion.md Learned (what a text rewrite of moved paths
  misses: a sentence's full stop, links in a moved file, paths built from parts) and references/generated-artifacts.md Learned (a second format is a generated view with a `--check`, never a copy);
  design-patterns.md P-65 given its missing `· Source:` field; ROADMAP item for the red write-back contract test (13 entries the parser rejects).
- 2026-11-12 references/testing.md: Learned entry, planting a bad value in a real input to prove a test fails leaves the input newer, so an mtime-based derived check goes red; plant into a copy or
  restore the timestamp (from apn enterprise-strategy).
- 2026-11-12 write-back from enterprise-strategy (one-pager pack and strategy deck, apn a3e29af7, ee9046df, 6c262ea9): languages/javascript-typescript.md Learned, pptxgenjs text-box margins are
  points; convert in the one text helper.
- 2026-11-12 write-back from enterprise-strategy (skill-ai-it new-skill, d3132c2): references/design-patterns.md P-69 (a seed, a plan-first scaffold and a guard on the shared output) and
  languages/python/learned-other.md (load a sibling module by path; parse wrapped markdown table rows by indentation).
- 2026-11-11 (f) write-back from enterprise-strategy: references/version-control-and-review.md, run the check as well as the tests before a commit (a module budget and a write-back header form are
  check rules, not test rules).
- 2026-11-11 (e) promoted enterprise-strategy's two parked candidates of 2026-11-06: references/design-patterns.md P-68 (baseline beside forecast in a generated report) and
  languages/python/learned-other.md (accept the decoration hand-typed lines carry).
- 2026-11-11 (d) write-back from enterprise-strategy (apn project_sync, cc69e7c1): references/design-principles.md, principle 4: two lookups for the same thing share one search-scope function;
  fixtures carry every folder layout.
- 2026-11-11: front-matter description shortened to cut startup tokens; the full original text is kept verbatim in the new `## Full description` section of SKILL.md.
- 2026-11-11 (c) write-back from the token-optimizer session: languages/python/learned-other.md, splitting front matter on "\n---" drops the last line's newline (a line regex misses the final
  description line); check JSON dump round-trips byte for byte before rewriting a config
- 2026-11-11 (b) write-back from ansible-wifi (smc_lynis NO_PUBKEY): languages/ansible/learned-other.md, `apt_key` with `url` and no `id` never refreshes a key whose primary is present (a new vendor
  subkey stays missing); pin the subkey `id` or use `get_url` plus `signed-by=`
- 2026-11-11 languages/yaml-json-toml.md: Learned, TOML vs YAML for registries keyed by id (duplicate tables fail at parse, YAML keeps the last key silently), no stdlib TOML writer, JSON Lines for
  appended data (unified-network-controller session)
- 2026-11-11 templates/ruff.toml: a project's ruff config (two-space, 160 columns, the skills' rule set, existing files excluded until reformatted, Markdown excluded); languages/python.md names it
  (operator approved, from smc-resiliency)
- 2026-11-11 write-back from smc-resiliency (docs/history standard): references/design-patterns.md P-67 (move files and repoint references by resolving links), languages/python.md (ruff 0.17 formats
  Markdown: exclude `*.md`)
- 2026-11-11 write-back from smc-resiliency (Pad links): references/design-patterns.md P-66 (a localhost redirect for a link scheme a web app strips; skill-pad c931f50)
- 20261110 references/tooling-and-runtime.md: Learned 2026-11-10 (skill-pad): a dataclass module loaded by path needs a sys.modules entry; flush progress lines so errors stay in order.

- 2026-11-10 (c) write-back from smc-resiliency (urlcapture-prune change): languages/ansible/learned-templating.md (a wrapper template that includes another: values by `set`, two lost newlines, prove
  with `cmp`)
- 2026-11-10 (b) write-back from smc-resiliency (versions record, fleet survey, N05): references/design-patterns.md P-65 (one version record, pins found by pattern; adopted by UNC),
  languages/shell/learned-processes-and-timeouts.md (Go programs survive SIGALRM: fork and TERM then KILL; recurrence of editing a running script), references/errors-and-timeouts.md (stop an flock
  holder and judge by taking the lock)
- 2026-11-10 write-back from unified-network-controller (Nautobot 3.2.9 upgrade): languages/shell/learned-processes-and-timeouts.md (a `bash -s` script loses its remainder to a child reading stdin);
  the `{{args}}` interpolation rule in references/tooling-and-runtime.md (Learned 2026-10-20) recurred in a new recipe and was fixed with `[positional-arguments]`, no new entry
- 2026-11-10 write-back from smc-resiliency (flash step): references/testing.md (fakes from real tool output; smoke a refusal against a real wrong target)
- 2026-11-09 (e) write-back from smc-resiliency (N03 and the S1 bench): references/design-patterns.md P-64 (a fixed-length record overwritten in place), languages/shell/learned-other.md (stdout errors
  with exit 0; ssh host-key, ControlPath, agent and askpass traps; macOS screen, sync, sudo), references/testing.md (vfat inodes are made up at mount)
- 2026-11-09 (d) write-back from tools_stuff cline (benchmark and prompt-cost tools): references/design-patterns.md P-63 (agent benchmark: known answers in a throwaway copy, a watch on real repos and
  their submodules), references/security.md (a disposable CLI config can fall back to a cloud default URL; guard egress)
- 2026-11-09 (c) write-back from smc-resiliency (follow-up audit fixes): references/testing.md (an end state needs its cause on record; test a shell function cut out of its script; printf %q fakes),
  references/security.md (pin a release tarball to its GitHub asset digest; check a cached tool's executable, not a marker), languages/python.md (legacy files outside ruff include lose F821),
  references/design-patterns.md P-62 (bind a multi-part answer with one signature)
- 2026-11-09 (b) write-back from skill-vagrant: references/errors-and-timeouts.md (a streamed download can end short without an error; check Content-Length)
- 2026-11-09 write-back from skill-vagrant: references/efficiency-and-measurement.md (a pipe filter holds a long job's progress lines)
- 2026-11-09 write-back from unified-network-controller (three entries parked in its audit follow-up, promoted): (the errors-and-timeouts.md entry is dated 2026-11-08) references/safety-and-writes.md
  (a rollback verifies restored state, not reachability), references/testing.md (a negative assertion needs a probe that ran; cleanup is part of the verdict), references/errors-and-timeouts.md (held
  alarms reach derived projections; delivery needs a durable pending record)
- 2026-11-09 write-back from skill-proxmox: references/testing.md (a token lookahead that excludes '.' misses a sentence-final token; write the negative test as prose)
- 2026-11-08 (c) write-back from smc-resiliency: references/testing.md (read_text hides \r\n; a raw pty for serial tests; termios without pyserial)
- 2026-11-08 (b) write-back from smc-resiliency S1V: references/safety-and-writes.md (write, fsync, rename is not crash-safe on FAT)
- 2026-11-08 write-back from smc-resiliency: references/testing.md (read an injected fault back before judging the case; retry only the transport's failure)
- 2026-11-07 (b) write-back from smc-resiliency: languages/python.md (default-argument binding, wrapper recursion, stale cache), references/design-patterns.md (JWS with openssl, P-59 view hash)

- scripts/scaffold.py: Python skeletons now two-space (they printed four, against the pack's own rule; found by skill-vagrant's build agent, 2026-11-07); tests/test_language_split.py (new)
- scripts/language_split.py (new), languages/readme.md (When a language file splits): ansible.md and shell.md split into ansible/ and shell/ topic files (operator, 2026-11-07); `just check` holds
  every language file to 200 lines
- languages/hcl.md (new, Learned 2026-11-07), languages/python.md, shell.md, yaml-json-toml.md: Learned 2026-11-07 from smc-resiliency's lab package and linters
- references/design-patterns.md: Learned 2026-11-07, logic over adapters for a test rig, profile chosen by what the box reports
- references/engine-composition.md: Learned 2026-11-07, the language per boot environment
- references/testing.md: Learned 2026-11-06 (b), a timed case counts only with its setup read back and its fault overlapping the work (smc-resiliency s3_case.sh)
- languages/shell.md: Learned 2026-11-06, editing a script a running job executes; prlctl exec has no shell; refuse an empty derived argument
- languages/ansible.md: Learned 2026-11-06 (l), extra vars with spaces go as JSON; the interpreter pin is per OS
- references/design-patterns.md: P-59 export a spec to plain code with provenance hashes and a hand-edit guard; P-60 order resumed records by attempt (Learned 2026-11-06, local-knowledge-ansible
  7056782, c7cb38b)
- languages/ansible.md: Learned 2026-11-06 (k), lint-clean generated task YAML (one template at a name's end, joined templates, fold then read back)
- references/efficiency-and-measurement.md: Learned 2026-11-06, a per-check budget inside a suite, a render keyed by its inputs, profile with workers off (apn unified-network-controller).
- references/testing.md: Learned 2026-11-06, prove the instrument before trusting what it measures; languages/shell.md: Learned 2026-11-06, never edit a script while it runs (apn smc-resiliency S3).
- languages/javascript-typescript.md: Learned 2026-11-06, Playwright: real clicks on canvas, includeHidden for filtered rows, charset, skip guard (apn unified-network-controller d49d2043).
- references/design-patterns.md: P-58 second use (an evaluator holds what an unread or half-written input proves; Learned 2026-11-06, apn unified-network-controller 5c563f8b); no longer a candidate.
- references/design-patterns.md: P-58 Hold changes while blind; recover alone only by trials that undo themselves (Learned 2026-11-06, apn smc-resiliency 1dc80235).
- references/version-control-and-review.md: shared-index sweep confirmed 2026-11-05; Learned 2026-11-05, rerun tracked-only checks after the first commit and before the push (Continuum).
- languages/python.md: Learned 2026-11-05, `\b` matches at a hyphen; anchor names with `(?=[ \t:])` (skill-ai-it).
- references/version-control-and-review.md: Learned 2026-11-05, testing the exported index catches a file a local exclude kept out of git (skill-knowledge-curator fixture).
- references/design-patterns.md: P-56 trust a model verdict only after known controls, in words that cannot be read backwards; P-57 group by each item's most widely shared key, not single-link
  chaining (Learned 2026-11-05, skill-knowledge-curator).
- languages/shell.md: Learned 2026-11-05 (ii), remote half on stdin rather than a quoted string or declare -f; parallel checks with a line per host.
- languages/ansible.md: Learned 2026-11-05 (iii), facts and group_by groups outlive import_playbook; reset per run, test by value, name groups per run.
- languages/ansible.md: Learned 2026-11-05 (j), find with depth still reads every depth-N dir (slow on NFS/EFS; use GNU find -maxdepth); async is the hard limit, not retries x delay; extra vars beat
  set_fact, so tests must pass inputs, not outputs.
- languages/shell.md: Learned 2026-11-05, a delimiter inside a sed replacement turns the rest into flags (w writes stray files).
- languages/ansible.md: Learned 2026-11-05 (ii), strategy free drops run_once, any_errors_fatal and max_fail_percentage and refuses pause; YAML reads 20261105_120000 as an int.
- 20261105 tests/test_package_contract.py: write-back entries count as logged in rotated docs/history/changelog-*.md too (budget rotation had failed the test).
- 20261105 Learned 2026-11-05 in languages/ansible.md: (i) a failed run_once assert fails only the first host; a run-wide gate needs any_errors_fatal.
- 20261104 Learned 2026-11-04 in languages/ansible.md: (h) facts persist across plays per host, so one host per test case; quote assert items holding ': '.
- 20261104 Backfilled: Learned 2026-10-27 in languages/python.md, `git -C <dir>` reads relative paths after changing directory (a relative destination lands under <dir>); written without its CHANGELOG
  line.
- 20261104 Backfilled: Learned 2026-10-26 in references/safety-and-writes.md, an interrupted transaction finishes only on a completed marker and a repeated cleanup keeps the backup manifest; and
  process matching from automation kills or waits on itself (anchor pgrep -f); written without their CHANGELOG lines.
- 20261104 Backfilled: Learned 2026-10-26 in languages/ansible.md, (e) until/retries do not retry an unreachable host (use async + poll 0 and an await), (f) run_once applies the first host's result to
  the whole batch; written that day without its CHANGELOG line.
- 20261104 Learned 2026-11-04 in references/design-patterns.md: P-55 state a run can empty (one dict per run, old names read through role vars).
- 20261102 Learned 2026-11-02 in languages/python.md: lock before the read in a rebuild writer; prove it without timing.

- 20261102 Learned 2026-11-02 in languages/shell.md: crontab rewrite through a checked file; a guard around a scheduled job covers just after the tick too.

- 20261102 Learned 2026-11-02 in references/testing.md: a closing check without the tests; review text applied by script.

- 20261102 references/engine-composition.md: how a many-language engine interlocks (who does what, the seam table with a check per seam, a parser with no parser, seven moves, build order). Patterns
  P-50 to P-54 in references/design-patterns.md, and the index brought up to P-54. Learned 2026-11-02 in references/engine-composition.md and references/design-patterns.md.
````

## File: docs/history/readme.md
````markdown
---
Title: History
Category: folder-index
Status: current
Summary: Rotated records: CHANGELOG, SCRATCHPAD and ROADMAP entries moved out by their tools.
---

# History

<!-- history-index:start (generated by skill-ai-it history_layout.py; descriptions written by hand are kept) -->

## Change log

- [changelog-20261119_1603.md](changelog-20261119_1603.md) release 0.2.0, 92 entries, 2026-10-19 to 2026-11-19 (cut 2026-11-19)
- [changelog-20261119_1601.md](changelog-20261119_1601.md) 1 entry, 2026-11-01 to 2026-11-01: Learned: a predicate answering a second question
- [changelog-20261119_1554.md](changelog-20261119_1554.md) 1 entry, 2026-11-01 to 2026-11-01: Learned: Jinja dict keys through JSON, filtered loop index, folded newlines, CRLF edits
- [changelog-20261119_1538.md](changelog-20261119_1538.md) 1 entry, 2026-11-01 to 2026-11-01: Gate output in recipes
- [changelog-20261118_2102.md](changelog-20261118_2102.md) 1 entry, 2026-10-30 to 2026-10-30: Pattern P-47 (decide once from facts, persist it); Learned: run_once set_fact freezes templates, 2.21 Jinja quirks
- [changelog-20261118_1557.md](changelog-20261118_1557.md) 1 entry, 2026-10-30 to 2026-10-30: Pattern P-46: audience words at the output boundary, with a leak guard
- [changelog-20261117_1859.md](changelog-20261117_1859.md) 1 entry, 2026-10-30 to 2026-10-30: Learned: filter precedence, free-form shell splitting, import_tasks placement, pipefail with grep -q
- [changelog-20261117_1101.md](changelog-20261117_1101.md) 5 entries, 2026-10-29 to 2026-10-29: Write-back log index (backfill); Backfilled log line for an existing write-back; Harvest write-back: patterns P-41 to P-45 and twelve Learned entries; Pattern P-40: hold citations by a check (ledger, local store, rules ...
- [changelog-20261116_1752.md](changelog-20261116_1752.md) 1 entry, 2026-10-29 to 2026-10-29: Pattern P-39: carry a placement over proven edges, narrow by direction
- [changelog-20261116_1737.md](changelog-20261116_1737.md) 4 entries, 2026-10-29 to 2026-10-29: Patterns P-37 and P-38 (skill-drawio speed and quality work); Pattern P-36: widen a name's scope by renaming in place; Patterns P-33 to P-35 (multi-SMC build); Learned: a check that skips when its tool is missing cannot ...
- [changelog-20261111_1100.md](changelog-20261111_1100.md) 1 entry, 2026-10-28 to 2026-10-28: Learned: optimise the real outcome, not a proxy
- [changelog-20261110_1246.md](changelog-20261110_1246.md) 1 entry, 2026-10-28 to 2026-10-28: Learned: shared justfile recipes and the editor
- [changelog-20261109_2227.md](changelog-20261109_2227.md) 1 entry, 2026-10-28 to 2026-10-28: Learned: a symlinked source ships whatever is checked out
- [changelog-20261109_1222.md](changelog-20261109_1222.md) 1 entry, 2026-10-28 to 2026-10-28: Learned: freeing a lock another process holds
- [changelog-20261107_1732.md](changelog-20261107_1732.md) 1 entry, 2026-10-28 to 2026-10-28: cpuprofile_summary helper
- [changelog-20261107_1723.md](changelog-20261107_1723.md) 1 entry, 2026-10-28 to 2026-10-28: process_match.py: unanchored pgrep/pkill -f patterns become a check
- [changelog-20261106_1030.md](changelog-20261106_1030.md) 1 entry, 2026-10-27 to 2026-10-27: Ansible include_tasks and lockstep batches, bash 3.2 empty arrays
- [changelog-20261105_2139.md](changelog-20261105_2139.md) 1 entry, 2026-10-27 to 2026-10-27: Ansible: to_json in debug output is escaped twice
- [changelog-20261105_1156.md](changelog-20261105_1156.md) 1 entry, 2026-10-27 to 2026-10-27: Design patterns harvested from unified-network-controller and smc-resiliency (P-13 to P-29)
- [changelog-20261102_1434.md](changelog-20261102_1434.md) 1 entry, 2026-10-27 to 2026-10-27: Design patterns reference: out-of-the-box logic from smc_change, per language
- [changelog-20261102_1348.md](changelog-20261102_1348.md) 1 entry, 2026-10-27 to 2026-10-27: Ansible: once-per-run play, test precedence, ssh retry backoff, include apply; git -C paths
- [changelog-20261102_1132.md](changelog-20261102_1132.md) 1 entry, 2026-10-26 to 2026-10-26: Ansible: run_once is per serial batch, results reach every host
- [changelog-20261101_2353.md](changelog-20261101_2353.md) 1 entry, 2026-10-26 to 2026-10-26: Ansible: until does not retry unreachable; async drop-proof waits; callbacks_enabled in 2.21
- [changelog-20261028_2101.md](changelog-20261028_2101.md) 0 entries, 2026-10-19 to 2026-10-19
- [changelog-20261028_1943.md](changelog-20261028_1943.md) 1 entry, 2026-10-19 to 2026-10-19: deterministic navigation-control upgrade
- [changelog-20261027_1213.md](changelog-20261027_1213.md) 1 entry, 2026-10-19 to 2026-10-19: 2026-10-19

## Roadmap

- [roadmap-20261028_1311.md](roadmap-20261028_1311.md) 1 done item: Make it the default (done 2026-10-20, operator: "if ...
- [roadmap-20261027_1045.md](roadmap-20261027_1045.md) 1 done item: Layer check — UNC's check_import_layers calls scripts/import_layers.py (same ...

<!-- history-index:end -->
````

## File: docs/history/roadmap-20261027_1045.md
````markdown
---
Title: ROADMAP done items to 20261027_1045
Category: history
Status: archived
Authority: record
Scope: Done milestones moved out of ROADMAP.md by skill-ai-it scripts/roadmap_trim.py
Last reviewed: 2026-10-27
Summary: 1 done items moved verbatim from ROADMAP.md on 20261027_1045, under their section headings.
---

# ROADMAP done items to 20261027_1045

## Adoption in unified-network-controller

- [x] **Layer check** — UNC's `check_import_layers` calls `scripts/import_layers.py` (same verdict on 2026-10-19; its baseline file is already this format).
````

## File: docs/history/roadmap-20261028_1311.md
````markdown
---
Title: ROADMAP done items to 20261028_1311
Category: history
Status: archived
Authority: record
Scope: Done milestones moved out of ROADMAP.md by skill-ai-it scripts/records/roadmap_trim.py
Last reviewed: 2026-10-28
Summary: 1 done items moved verbatim from ROADMAP.md on 20261028_1311, under their section headings.
---

# ROADMAP done items to 20261028_1311

## Activation

- [x] **Make it the default** (done 2026-10-20, operator: "if you are now happy with skill-coder, promote it as well") — in one pass: the global policy line beside `safe-change-validation` and the Codex sync; the
  `skill-surfaces.md` row; restore the broad `SKILL.md` trigger; link it from the governance `coding-guide.md` (check `sync-map.yaml`). Steps in `SCRATCHPAD.md` Open items.
````

## File: scripts/call_timeouts.py
````python
#!/usr/bin/env python3
"""Find Python calls to the network or a subprocess that pass no timeout, as a shrink-only ratchet. Read-only unless --write-baseline. Stdlib only.

Why (unified-network-controller code architecture design, rule R15; its Phase 1 review found 16 of 96 such calls without one): a call with no
timeout can hang a job, a page or a whole collector cycle forever, and the hang looks like slowness rather than a fault. Every subprocess, HTTP
request and socket connect states how long it may take.

Found through `ast`, so only real calls count (not text in strings): subprocess.run/call/check_call/check_output, Popen(...).communicate/wait,
urllib.request.urlopen, requests/httpx verbs and request(), socket.create_connection. A call passing `**kwargs` is trusted (the timeout may be
inside). Other languages: see the pack's languages/ notes for the equivalent rule and linter.

Usage:
    call_timeouts.py --project-root . [--roots src,scripts] [--baseline scripts/timeout-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more untimed calls than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Dotted call names that must carry `timeout=`, by their last two parts (module.function or object.method).
NEEDS_TIMEOUT = {
    "subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output",
    "request.urlopen", "urllib.urlopen", "socket.create_connection",
    "requests.get", "requests.post", "requests.put", "requests.patch", "requests.delete", "requests.head", "requests.request",
    "httpx.get", "httpx.post", "httpx.put", "httpx.patch", "httpx.delete", "httpx.request",
}
#: Bare method names that must carry a timeout wherever they are called on a Popen.
POPEN_METHODS = {"communicate", "wait"}


def _dotted(node: ast.AST) -> str:
    """A call target as dotted text (`subprocess.run`), or "" when it is not a plain name chain.

    Args:
        node: the call's func node.

    Returns:
        The dotted name.
    """
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def untimed_calls(text: str, popen_names: frozenset = frozenset(), grammar: tuple[int, int] | None = None) -> list[tuple[int, str]]:
    """Calls in Python source that need a timeout and pass none.

    Args:
        text: the source.
        popen_names: variable names known to hold a Popen (found by the caller); `x.communicate()` on them counts.
        grammar: (major, minor) to parse with the target project's grammar; None for this interpreter's.

    Returns:
        (line, call name) per untimed call.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it).
    """
    tree = pyparse.parse(text, grammar)
    popens = set(popen_names)
    for node in ast.walk(tree):   # names bound to subprocess.Popen(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and _dotted(node.value.func).endswith("Popen"):
            popens |= {t.id for t in node.targets if isinstance(t, ast.Name)}
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _dotted(node.func)
        tail = ".".join(name.split(".")[-2:])
        popen_call = isinstance(node.func, ast.Attribute) and node.func.attr in POPEN_METHODS and _dotted(node.func.value) in popens
        if tail not in NEEDS_TIMEOUT and not popen_call:
            continue
        if any(k.arg == "timeout" or k.arg is None for k in node.keywords):
            continue
        out.append((node.lineno, name))
    return out


def measure(root: Path, roots: list[str], grammar: tuple[int, int] | None = None) -> tuple[dict[str, float], dict[str, list], list[str]]:
    """Untimed calls per file.

    Args:
        root: the project root.
        roots: folders to scan.
        grammar: the Python grammar to parse with.

    Returns:
        ({path: count} for files with any, {path: [(line, name)]}, ["path: error"] for files that do not parse).
    """
    unparsed: list[str] = []
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*.py")):
            if {".venv", "venv", "node_modules", "__pycache__"} & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                found = untimed_calls(path.read_text(encoding="utf-8", errors="replace"), grammar=grammar)
            except SyntaxError as exc:
                unparsed.append(f"{rel}: line {exc.lineno}: {exc.msg}")
                continue
            if found:
                counts[rel], detail[rel] = len(found), found
    return counts, detail, unparsed


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [timeouts] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [timeouts] baseline, else scripts/timeout-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every untimed call")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--python", help="parse at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"call_timeouts: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "timeouts")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"call_timeouts: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    grammar = code_map.grammar(args.python, cmap)
    args.baseline = args.baseline or code_map.section(cmap, "timeouts").get("baseline", "scripts/timeout-baseline.json")
    counts, detail, unparsed = measure(root, roots, grammar)
    for line in unparsed:
        print(f"FAIL unparsed: {line} (not checked; check --python matches the project)")
    if args.list:
        for rel, calls in detail.items():
            for line, name in calls:
                print(f"{rel}:{line}: {name}() has no timeout")
    base_path = root / args.baseline
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"call_timeouts: baseline written, {sum(counts.values()):g} untimed call(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "timeouts", base_path):
        print(line)
    if verdict.ok:
        print(f"call_timeouts: OK, {sum(counts.values()):g} untimed call(s), all within the baseline")
    return 0 if verdict.ok and not unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/check_governance.py
````python
#!/usr/bin/env python3
"""Governance coherence checks for skill-coder.

Turns this project's governance CLAIMS into assertions that fail. Stdlib only, so the gate never fails for environment reasons; exit 1 on any failure so it can gate the task runner.

Generated by skill-ai-it from templates/check_governance.py. Doctrine, check families, and the inference table live in the skill's patterns/governance-checks.md — read that before adding,
changing, or retiring a check.

Structure:
  CONFIG      — registries the agent tunes per project. Everything below CONFIG is generic.
  Tier 1      — universal checks. Present in every project.
  Tier 2      — conditional checks. Kept only when their trigger artifact exists.
  Tier 3      — project-specific invariants. Authored per project; each cites the rule it enforces.

Growth rule: this file is expected to grow with the project. A new class of artifact needs a coverage check; a new duplicated constant needs a registry entry. When a check fails, fix the
project, not the check.

Checks:
  1. Referenced paths in the governance surfaces resolve on disk (relative to the referencing file, then to the repo root).
  2. Index links resolve, and every indexed folder member is linked.
  3. Count claims in prose match reality (historical facts exempt).
  4. Cataloged items exist and existing items are cataloged.
  5. Task-runner recipes named in prose exist in the runner.
  5b. No recipe reaches an interpreter implicitly — neither a bare `python3`/`node` nor `mise exec -- python`.
  6. Derived artifacts are not older than their inputs.
  7. Every surface restating a registered constant states it identically, and nothing unregistered restates it.
  8. Every row of an append-only table stamps its pass, and no pass records the same entity twice.
  9. Every dated evidence capture states its URL, retrieval date and HTTP status, or names the capture that corrects it.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Repo-relative path to this file. Used to exclude the checker from the constant scan: it necessarily contains every
# registered constant's PATTERN, and comparing `rel` against a bare `Path(__file__).name` never matched, so the checker
# reported each of its own pattern definitions as an unregistered restatement.
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()

# --------------------------------------------------------------------------------------------------------------- CONFIG
# Tune these registries to the project. Leave a registry empty and its check contributes zero assertions rather than
# failing — coverage is measured by the assertion count, so an empty registry reads honestly as "not covered yet".

# Governance surfaces whose path references must resolve.
SURFACES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "SKILL.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "scripts/README.md",
    "languages/readme.md",
)

# Index file -> (folder it indexes, glob). Enforces BOTH directions: links resolve, and members are linked.
CATALOGS: dict[str, tuple[str, str]] = {
    # SKILL.md is the activation surface: it must route every reference and every language override.
    "SKILL.md": ("references", "*.md"),
    "AI_NAVIGATION.md": ("references", "*.md"),
    "languages/readme.md": ("languages", "*.md"),
    "scripts/README.md": ("scripts", "*.py"),
    ".archcore/index.guide.md": (".archcore", "*/*.md"),
}

# Files a catalog may legitimately omit (the index itself, generated output, dotfiles).
CATALOG_EXEMPT: frozenset[str] = frozenset({"README.md", "__init__.py"})

# Countable noun -> (folder, glob). A prose claim like "26 documents" is checked against the real count. Choose the glob
# deliberately: "*.md" counts the folder's own index too, which is usually not what the prose means — prefer "[0-9]*.md"
# or a similar shape when the index is excluded from the claim.
COUNT_CLAIMS: dict[str, tuple[str, str]] = {
    # "documents": ("docs", "*.md"),
    # "scripts": ("scripts", "*.py"),
}

# Lines carrying this marker state a historical fact, not a live claim, and are exempt from count checking.
ASAT_MARKER = "count:asat"

# Lines carrying this marker show an ILLUSTRATIVE filename — a naming-convention example — not a reference to a file
# that must exist. Same shape as ASAT_MARKER: explicit, per line, and visible in the document itself rather than
# hidden in an ignore-list here.
EXAMPLE_MARKER = "path:example"

# Paths a governance surface references CONDITIONALLY ("when present"). The generic skill-ai-it navigation block names
# several; each is a real artifact in SOME governed project, so its absence here is a fact about this project's
# toolchain rather than a broken reference. Registered with a per-entry reason rather than silently ignore-listed, so
# the exemption stays reviewable — remove an entry the day the artifact appears. Tune per project.
CONDITIONAL_PATHS: frozenset[str] = frozenset({
    # Named by the generic skill-ai-it navigation block; this pack does not have them.
    "graphify-out/GRAPH_REPORT.md",     # Graphify disabled (operator, 2026-10-10)
    "Taskfile.yml", "Makefile", "package.json",
    "ARCHCORE_PROMOTION_CANDIDATES.md",  # transient queue, deleted by promote 2026-10-19; CHANGELOG mentions are history
    "ARCHITECTURE.md", "ROADMAP.md",    # a guidance pack: SKILL.md + references/ carry the design; open items live in SCRATCHPAD.md
    "memory-bank/activeContext.md", "memory-bank/progress.md", "memory-bank/decisionLog.md",
    ".ai-context/repo-pack.md",
    ".ai-context/governance-pack.md",   # generated by `just context-pack` when repomix is installed
    ".archcore/specs", ".archcore/guides", ".archcore/plans",   # never promoted, by decision: .archcore/index.guide.md
    "docs/history", "docs/trackers",    # created by `just rotate --apply` when a record first passes its budget; no trackers in a pack
    # Paths in the governed project the pack's rules came from, named as such in the citing text.
    "docs/engineering/unc-code-architecture-target-design-20261010_1221.md",
    "src/unc/layers.toml",
    "scripts/checks/import_graph.py",
    # Tool configuration files in a TARGET project, which SKILL.md tells the agent to read first.
    "pyproject.toml", ".golangci.yml", "rustfmt.toml", "rust-toolchain.toml",
})

# Task runner file, or None if the project has none.
TASK_RUNNER: str | None = "justfile"

# Files whose prose names task-runner recipes.
RUNNER_REFERENCES: tuple[str, ...] = ("README.md", "AGENTS.md", "AI_NAVIGATION.md", "scripts/README.md", "SKILL.md")

# Recipes that BUILD the venv from the mise pin — e.g. "bootstrap" in templates/justfile. {{py}} cannot exist yet when
# these run, so their own `mise exec -- python -m venv .venv` line is the one legitimate implicit-interpreter call, not
# a violation of the rule it otherwise enforces. Leave empty if the project has no such recipe.
VENV_BUILDER_RECIPES: frozenset[str] = frozenset({"bootstrap"})

# Generated artifact -> inputs it must not be older than.
DERIVED: dict[str, tuple[str, ...]] = {
    # "docs/CLASS-PROFILES.md": ("scripts/class_profiles.py", "process/vehicle-classes.yaml"),
}

# Facts deliberately restated across surfaces. Each entry: the regex that recognises a statement of the fact, and every
# file allowed to state it. Drift fails; so does an UNREGISTERED file stating it — that is what makes this self-extending.
# Pair each entry with a spec document explaining why the duplication is intentional.
CONSTANT_SURFACES: dict[str, dict[str, object]] = {
    # "profit-gate": {
    #     "pattern": r"\$2,500",
    #     "surfaces": ("AGENTS.md", "docs/07-DECISIONS.md"),
    #     "owner": ".archcore/rules/purchase-discipline.rule.md",
    # },
}

# Append-only tables and the columns that give them their grain: (entity column, pass column). An append-only table
# records a re-measurement by ADDING a row, which is right and useless on its own — without a column that orders the
# passes there is no way to compute which row is current, and every aggregate over the table double-counts whatever was
# re-measured. Found in a governed project on 2026-08-28 with twelve rows standing for eight entities, the supersession
# recorded only in a prose note. Register the table here and the grain becomes an assertion instead of an intention.
APPEND_ONLY_TABLES: dict[str, tuple[str, str]] = {
    # "data/sku-scores.csv": ("sku_id", "scored_at"),
}

# Folder of dated evidence captures, or None if the project keeps none. A capture asserts what a source said on a date.
EVIDENCE_DIR: str | None = None  # e.g. "trackers/source-captures"

# The index file inside EVIDENCE_DIR, exempt from the provenance header because it is a catalog, not a capture.
EVIDENCE_INDEX = "README.md"

# Header fields that make a capture re-openable by someone who was not there: where it came from, when, and whether the
# fetch actually succeeded. A capture naming no URL and no HTTP status is a recollection in a capture's clothing — in
# the project this was promoted from, exactly that produced a VERIFIED cost row whose only recorded fetch returned 403.
EVIDENCE_PROVENANCE_FIELDS: tuple[str, ...] = ("Canonical URL", "Retrieved", "HTTP status")

# Captures taken before the provenance rule existed. Each MUST name the later capture supplying the missing provenance —
# this is a correction record, not an exemption. Where captures are immutable the only way to clear an entry is to take
# the correcting capture, which is the behaviour the rule wants. Removing an entry whose correction does not exist turns
# the check red rather than quiet, so the list cannot be emptied by deletion.
EVIDENCE_PROVENANCE_CORRECTED: dict[str, str] = {
    # "uae-wholesale-moq-discounts-20260828.md": "wholesale-house-price-provenance-20260828.md",
}

# Extensions scanned when hunting for unregistered restatements of a constant.
SCAN_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".yaml", ".yml"})

# Path-token discrimination. Prose is full of tokens that look like paths and are not; tune until the check is quiet.
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")
REPO_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"})
# Folders a bare file name (`code_size.py`, `testing.md`) is resolved against.
NAME_ROOTS: tuple[str, ...] = ("references", "languages", "scripts", "tests", "templates")
IGNORE_PREFIXES: tuple[str, ...] = ("http://", "https://", "mailto:", "~/", "/")
IGNORE_EXACT: frozenset[str] = frozenset({"README.md", "AGENTS.md", "CLAUDE.md", "SCRATCHPAD.md", "CHANGELOG.md"})

# --------------------------------------------------------------------------------------------------------------- HARNESS

failures: list[str] = []
checks_run = 0


def fail(check: str, detail: str) -> None:
    """Record one failure under its check name; main() prints them all at the end, so one defect never hides the next."""
    failures.append(f"{check}: {detail}")


def counted() -> None:
    """Record one assertion actually evaluated. Never call this per function — only per real comparison."""
    global checks_run
    checks_run += 1


def read(rel: str) -> str | None:
    """A project-relative file's text, or None when it does not exist. Callers decide whether absence is itself a failure."""
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def without_code(text: str) -> str:
    """Strip fenced code blocks. Their contents are examples, not claims about this repo."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def table_rows(rel: str) -> list[dict[str, str]]:
    """Read a CSV as dicts, or an empty list when it does not exist — an absent table contributes zero assertions."""
    path = ROOT / rel
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def members(folder: str, glob: str) -> list[Path]:
    """Files in a project folder that match glob, sorted, dotfiles excluded. An absent folder has no members rather than raising."""
    base = ROOT / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob(glob) if p.is_file() and not p.name.startswith("."))


# --------------------------------------------------------------------------------------------------------------- TIER 1


def check_referenced_paths() -> None:
    """Every repo-relative path named in a governance surface resolves on disk."""
    for surface in SURFACES:
        text = read(surface)
        if text is None:
            fail("surface", f"{surface} is listed as a governance surface but does not exist")
            counted()
            continue
        body = "\n".join(l for l in without_code(text).splitlines() if EXAMPLE_MARKER not in l)
        tokens = set(re.findall(r"`([^`\n]+)`", body))
        tokens |= {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", body)}
        for raw in sorted(tokens):
            tok = raw.split("#", 1)[0].strip().rstrip("/")
            if not tok or tok in IGNORE_EXACT or tok in CONDITIONAL_PATHS or tok.startswith(IGNORE_PREFIXES):
                continue
            if not PATHLIKE.match(tok):
                continue
            suffix = Path(tok).suffix
            if "/" not in tok and suffix not in REPO_SUFFIXES:
                continue
            if suffix and suffix not in REPO_SUFFIXES:
                continue
            counted()
            # Resolve relative to the file that MAKES the reference first, then relative to ROOT. Resolving only
            # against ROOT false-fails every correct relative link written inside a subfolder README.
            near = (ROOT / surface).parent / tok
            # A bare name (`code_size.py`) is the pack's own prose naming a helper or reference; it must exist in one of NAME_ROOTS.
            bare = "/" not in tok and any((ROOT / folder / tok).exists() for folder in NAME_ROOTS)
            if not near.exists() and not (ROOT / tok).exists() and not bare:
                fail("path", f"{surface} references `{tok}` which does not exist")


def check_index_links() -> None:
    """Links inside an index file resolve, relative to the index's own folder."""
    for index in CATALOGS:
        text = read(index)
        if text is None:
            fail("index", f"catalog {index} does not exist")
            counted()
            continue
        base = (ROOT / index).parent
        for target in {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", without_code(text))}:
            tok = target.split("#", 1)[0].strip()
            if not tok or tok.startswith(IGNORE_PREFIXES):
                continue
            counted()
            if not (base / tok).exists():
                fail("index", f"{index} links `{tok}` which does not exist")


def check_count_claims() -> None:
    """Prose stating a quantity matches the real count. Lines marked as historical facts are exempt."""
    for noun, (folder, glob) in COUNT_CLAIMS.items():
        actual = len(members(folder, glob))
        pattern = re.compile(rf"(\d+)\s+{re.escape(noun)}\b", re.IGNORECASE)
        for surface in SURFACES:
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != actual:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; {folder}/{glob} holds {actual}")


def check_catalog_coverage() -> None:
    """Both directions: the catalog names nothing missing, and nothing present is uncataloged.

    The second direction is the one that grows silently, and it is what makes this checker self-extending — a new file
    turns the build red until it is registered somewhere.
    """
    for index, (folder, glob) in CATALOGS.items():
        text = read(index)
        if text is None:
            continue
        body = without_code(text)
        for item in members(folder, glob):
            if item.name in CATALOG_EXEMPT or (ROOT / index).resolve() == item.resolve():
                continue
            counted()
            if item.name not in body:
                fail("coverage", f"{folder}/{item.name} exists but is not cataloged in {index}")


# --------------------------------------------------------------------------------------------------------------- TIER 2
# Keep a check below only while its trigger artifact exists. Delete the rest rather than leaving inert scaffolding.


def check_task_recipes() -> None:
    """Recipes named in prose exist in the task runner, and every cataloged script has a way to be run."""
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        fail("runner", f"{TASK_RUNNER} is configured but does not exist")
        counted()
        return
    recipes = {m.group(1) for m in re.finditer(r"^([a-zA-Z][\w-]*)\s*(?:[*+a-zA-Z_].*)?:(?!=)", runner, re.MULTILINE)}
    for surface in RUNNER_REFERENCES:
        text = read(surface)
        if text is None:
            continue
        for named in {m.group(1) for m in re.finditer(r"`just ([a-zA-Z][\w-]*)", without_code(text))}:
            counted()
            if named not in recipes:
                fail("runner", f"{surface} names recipe `{named}` which {TASK_RUNNER} does not define")


# Code files that kept a kebab-case name when the snake_case rule arrived. Listed here, by repo-relative path, until they are next touched and renamed
# (governance coding-guide: renamed when touched, references updated in the same change; never a new one). Empty is the goal.
KEBAB_LEGACY: frozenset[str] = frozenset()
CODE_SUFFIXES: frozenset[str] = frozenset({".py", ".sh", ".bash", ".js", ".mjs", ".ts", ".rb", ".pl"})


def check_file_naming() -> None:
    """Every code file under scripts/ is named in snake_case; a hyphen in its name fails unless the file is listed in KEBAB_LEGACY.

    Governance coding-guide (operator, 2026-10-07): snake_case for every code file and command name. A Python file must be an importable identifier
    (PEP 8; a hyphen is the minus operator to `import`), and the Google Shell Style Guide asks the same of shell ("make_template but not
    make-template"). One rule for every language is what stops a `survey-summary.py` appearing beside `survey_summary.py`. kebab-case belongs only to
    names fixed outside the code: skill names, document slugs, repo and folder names. A KEBAB_LEGACY entry whose file no longer exists also fails, so
    the list shrinks as files are renamed instead of going stale.
    """
    scripts = ROOT / "scripts"
    found = sorted(p for p in scripts.rglob("*") if p.is_file() and p.suffix in CODE_SUFFIXES) if scripts.is_dir() else []
    for path in found:
        rel = path.relative_to(ROOT).as_posix()
        counted()
        if "-" in path.stem and rel not in KEBAB_LEGACY:
            fail("file-naming", f"{rel} is kebab-case; name code files in snake_case ({path.stem.replace('-', '_')}{path.suffix}) and update "
                                f"every reference, or list it in KEBAB_LEGACY until it is next touched")
    for rel in sorted(KEBAB_LEGACY):
        counted()
        if not (ROOT / rel).is_file():
            fail("file-naming", f"KEBAB_LEGACY lists {rel}, which no longer exists: remove the entry")


def check_function_docs() -> None:
    """Every function in scripts/ says what it does: a docstring on each Python function, a comment block above each shell function.

    Operator, 2026-10-07: every function gets proper comments, in the style of ansible-wifi's rise_watchdog.py (a summary line, then the reasoning and
    the failure behaviour where it is not obvious). Python code embedded as a string constant (snmp_via_smc.py's AGENT, run on the SMC) is parsed and
    held to the same rule, because it is code a reader has to trust. A shell function needs at least one `#` line directly above its definition.
    """
    import ast

    def undocumented(tree: ast.AST) -> list[str]:
        """Names of the function definitions in tree that have no docstring."""
        return [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not ast.get_docstring(n)]

    for path in sorted((ROOT / "scripts").glob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            fail("function-docs", f"{rel} does not parse: {e}")
            continue
        counted()
        for name in undocumented(tree):
            fail("function-docs", f"{rel}: function `{name}` has no docstring")
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "\ndef " in node.value:
                try:
                    inner = ast.parse(node.value)
                except SyntaxError:
                    continue  # a string that only mentions `def` is prose, not embedded code
                counted()
                for name in undocumented(inner):
                    fail("function-docs", f"{rel}: embedded function `{name}` (line {node.lineno}) has no docstring")
    for path in sorted((ROOT / "scripts").glob("*.sh")):
        rel = path.relative_to(ROOT).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if re.match(r"^\s*[A-Za-z_][\w-]*\s*\(\)\s*\{", line):
                counted()
                if i == 0 or not lines[i - 1].lstrip().startswith("#"):
                    fail("function-docs", f"{rel}:{i + 1} shell function `{line.strip()[:40]}` has no comment block above it")




def check_interpreter_pinning() -> None:
    """No task recipe reaches an interpreter implicitly.

    Two defects, one root cause — the recipe does not say which interpreter it means:

    1. A BARE `python3`/`node`/`npx`/`ruby` resolves to whatever is on PATH, not to what .mise.toml pins.
    2. `mise exec -- python` resolves to the venv only while `_.python.venv` activation applies. It tests clean, reads
       as pinned, and degrades SILENTLY to the host interpreter when that activation stops holding.

    Both are the "it works on the machine it was written on" class. Recipes must address {{py}} by path and depend on
    _require-venv. Node has no venv layer, so `mise exec -- node` is the legitimate explicit form for it and is allowed.

    Exception: VENV_BUILDER_RECIPES (e.g. "bootstrap") create the venv from the mise pin, so {{py}} cannot exist yet
    when they run — their own `mise exec -- python -m venv .venv` line is the one legitimate implicit call, not a
    violation of the rule it otherwise enforces. Found missing during unified-network-controller's bootstrap
    (2026-09-18): the template's own `bootstrap` recipe failed the check it ships with, because nothing tracked which
    recipe a line belongs to. `cambium-swap` had already patched this locally; ported back here so every project
    generated from this template gets it, instead of each one rediscovering and re-fixing it independently.

    Rule: the runtime-isolation section of skill-ai-it's SKILL.md, and the RUNTIME PINNING header of templates/justfile.
    """
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        return
    recipe: str | None = None
    for lineno, line in enumerate(runner.splitlines(), 1):
        header = re.match(r"^([a-zA-Z_][\w-]*)\s*(?:[*+a-zA-Z_][^:]*)?:(?!=)", line)
        if header:
            recipe = header.group(1)
            continue
        if not line.startswith((" ", "\t")):
            continue  # only recipe bodies are commands; headers and variable assignments are not
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Blank out quoted literals, keeping offsets intact: an interpreter NAME inside a string is a label being
        # printed (`printf 'python  '`), not a command being run.
        scan = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
        counted()
        if re.search(r"mise\s+exec\b[^|;]*--\s+python", scan) and recipe not in VENV_BUILDER_RECIPES:
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} reaches Python through an implicit `mise exec -- python` — address the venv "
                f"interpreter by path via {{{{py}}}} and guard it with _require-venv",
            )
        for match in re.finditer(r"(?<![-\w/])(python3?|npx|ruby|node)\b", scan):
            # `mise exec -- <interp>` is handled above for python; for the rest it is the sanctioned explicit form.
            if re.search(r"mise\s+(exec\b[^|;]*--|run)\s*$", scan[: match.start()]):
                continue
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} calls bare `{match.group(1)}` — route it through the pinned interpreter",
            )
        # 3. A recipe that runs a script BY PATH (`scripts/check.py`, `./tool.js`) never names an interpreter, so the script's
        #    shebang (`#!/usr/bin/env python3`) picks the host one. Missed until 2026-10-07: skill-mikrotik passed this check
        #    with every recipe written that way, because the check only looked for interpreter NAMES on recipe lines.
        for cmd in re.split(r"&&|\|\||;|\|", scan):
            words = cmd.strip().lstrip("@-").split()
            while words and re.match(r"^[A-Za-z_]\w*=", words[0]):
                words = words[1:]  # leading VAR=value assignments are not the command
            if words and re.search(r"\.(py|js|mjs|rb)$", words[0]):
                fail(
                    "runtime",
                    f"{TASK_RUNNER}:{lineno} runs `{words[0]}` by path, so its shebang picks the interpreter — call it as "
                    f"{{{{py}}}} {words[0]} and depend on _require-venv",
                )
    # 4. Shell scripts under scripts/ that call a bare interpreter inline (`... | python3 -c`, `python3 - <<EOF`) undo the
    #    pinning from inside: the recipe pins nothing they run. They take the interpreter from a variable the task runner sets
    #    (`py=${PROJ_PY:-python3}` then `"$py"`; the recipe passes PROJ_PY={{py}}), so a direct run still works and a recipe
    #    run is pinned. A line whose interpreter runs on ANOTHER host (`ssh host python3 ...`) is marked `# runtime: remote`.
    scripts_dir = ROOT / "scripts"
    for path in sorted(scripts_dir.glob("**/*.sh")) if scripts_dir.is_dir() else []:
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "# runtime: remote" in line:
                continue
            scan = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
            counted()
            for match in re.finditer(r"(?<![-\w/.:$])(python3?|node)\b(?![.\w])", scan):
                fail(
                    "runtime",
                    f"{rel}:{lineno} calls bare `{match.group(1)}` — take it from a variable the task runner sets "
                    f"(py=${{PROJ_PY:-python3}}, then \"$py\"; the recipe passes {{{{py}}}})",
                )


# --------------------------------------------------------------------------------------------------------------- TIER 3
# Project-specific invariants. Each check states, in its docstring, the project rule it enforces and where that rule
# lives. A check whose justification cannot be found is a check the next agent deletes.


def check_derived_freshness() -> None:
    """Generated artifacts are not older than the sources they are generated from.

    Freshness only — it proves a rebuild happened, not that the rebuild used the right source. Where the generator can
    stamp its source into the output, add a provenance check alongside this one; see patterns/governance-checks.md.
    """
    for output, inputs in DERIVED.items():
        out = ROOT / output
        if not out.is_file():
            fail("derived", f"{output} is registered as generated but does not exist")
            counted()
            continue
        for src in inputs:
            source = ROOT / src
            counted()
            if not source.is_file():
                fail("derived", f"{output} declares input `{src}` which does not exist")
            elif out.stat().st_mtime < source.stat().st_mtime:
                fail("derived", f"{output} is older than its input `{src}` — regenerate it")


def check_constant_sync() -> None:
    """Facts restated across surfaces stay identical, and no unregistered file restates them.

    Duplication here is deliberate: the operator must read the value at the point of decision without following a
    pointer. So the duplication stays and the sync is enforced. Orphan detection is the half that makes it self-extending.
    """
    for name, entry in CONSTANT_SURFACES.items():
        pattern = re.compile(str(entry["pattern"]))
        surfaces = entry["surfaces"]
        if not isinstance(surfaces, (list, tuple)):   # a single string would be read character by character
            raise TypeError(f"CONSTANT_SURFACES[{name!r}]['surfaces'] must be a list, not {type(surfaces).__name__}")
        registered = {str(s) for s in surfaces}
        owner = str(entry.get("owner", ""))

        for surface in sorted(registered):
            text = read(surface)
            counted()
            if text is None:
                fail("constant", f"{name}: registered surface {surface} does not exist")
            elif not pattern.search(without_code(text)):
                fail("constant", f"{name}: {surface} is registered but no longer states it (owner: {owner or 'unset'})")

        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in registered or rel.startswith(".") or "/." in rel or rel == SELF or rel.startswith("docs/history/") or rel == "CHANGELOG.md":  # dated history: rotated records and the change log (2026-10-14)
                continue
            counted()
            if pattern.search(without_code(path.read_text(encoding="utf-8", errors="ignore"))):
                fail("constant", f"{name}: {rel} states it but is not registered in CONSTANT_SURFACES")


def check_append_only_grain() -> None:
    """Every row of an append-only table stamps its pass, and no pass records the same entity twice.

    Registered in APPEND_ONLY_TABLES. Two distinct failures, both silent: a row with an EMPTY pass column cannot be
    ordered against any other row, so nothing can say which measurement is current; and a REPEATED (entity, pass) pair
    means one pass measured one entity twice, so every count and every aggregate over the table is wrong by however
    many rows were duplicated. Neither shows up as an error — the table still parses and the report still renders.

    A re-measurement is a NEW pass. Reusing the previous pass identifier to record one is the defect this catches.
    """
    for rel, (entity_col, pass_col) in APPEND_ONLY_TABLES.items():
        rows = table_rows(rel)
        if not rows:
            counted()
            if not (ROOT / rel).is_file():
                fail("append-only-grain", f"{rel} is registered as append-only but does not exist")
            continue
        seen: dict[tuple[str, str], int] = {}
        for i, row in enumerate(rows, start=2):  # line 1 is the header
            counted()
            if entity_col not in row or pass_col not in row:
                fail("append-only-grain",
                     f"{rel} has no {entity_col!r}/{pass_col!r} column; the registered grain does not match the table")
                break
            pass_id = (row.get(pass_col) or "").strip()
            if not pass_id:
                fail("append-only-grain", f"{rel} line {i} has empty {pass_col}; the pass is the grain")
                continue
            key = ((row.get(entity_col) or "").strip(), pass_id)
            if key in seen:
                fail("append-only-grain",
                     f"{rel} line {i} repeats {entity_col} {key[0]!r} for pass {pass_id} (first seen line {seen[key]}); "
                     f"a re-measurement is a NEW pass, so give it a new {pass_col}")
            else:
                seen[key] = i


def check_evidence_provenance() -> None:
    """Every markdown capture states where it came from, when, and whether the fetch succeeded.

    Enforces the global source-discipline policy (~/.agents/AGENTS.md, 'Citations travel into the documentation'): a
    VERIFIED figure means a capture exists that someone else can re-open. Presence of a capture FILE is not that —
    a file with no URL and no HTTP status proves only that somebody wrote something down.

    A capture missing the header is accepted ONLY while it names its correcting capture in
    EVIDENCE_PROVENANCE_CORRECTED and that capture is on disk.
    """
    if EVIDENCE_DIR is None:
        return
    for item in members(EVIDENCE_DIR, "*.md"):
        if item.name == EVIDENCE_INDEX:
            continue
        counted()
        text = read(f"{EVIDENCE_DIR}/{item.name}") or ""
        missing = [f for f in EVIDENCE_PROVENANCE_FIELDS if f"**{f}**" not in text]
        if not missing:
            continue
        corrector = EVIDENCE_PROVENANCE_CORRECTED.get(item.name)
        if corrector is None:
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} states no {', '.join(missing)}; a capture nobody can re-open is not evidence")
        elif not (ROOT / EVIDENCE_DIR / corrector).is_file():
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} defers its provenance to {corrector}, which does not exist")


# --------------------------------------------------------------------------------------------------------------- MAIN

CHECKS = (
    check_referenced_paths,
    check_index_links,
    check_count_claims,
    check_catalog_coverage,
    check_task_recipes,
    check_interpreter_pinning,
    check_function_docs,
    check_file_naming,
    check_derived_freshness,
    check_constant_sync,
    check_append_only_grain,
    check_evidence_provenance,
)


def main() -> int:
    """Run every registered check, print each unique failure, and return the exit code: 0 when all passed, 1 when anything failed."""
    for check in CHECKS:
        check()

    # The same defect can be reported by more than one matching pattern; a doubled count erodes trust in the number.
    unique = sorted(set(failures))
    if unique:
        print(f"FAIL — {len(unique)} issue(s) across {checks_run} checks\n")
        for f in unique:
            print(f"  ✗ {f}")
        return 1

    print(f"OK — {checks_run} governance checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/code_map.py
````python
#!/usr/bin/env python3
"""Read a project's code map (`code-map.toml`): the human decisions about its code that the pack's checkers act on. Stdlib only (tomllib).

Why (operator, 2026-10-19: "is there a need of code-map like we have context-map or target-map or guide-map"): a project's code intent was
spread over several files that drift apart (an import-layer TOML, a write-gate register inside a checker, a promotion register, a refactor
tracker). The code map holds that intent in one place, data first, and every checker in this pack reads its own section from it.

It holds only decisions, never facts the code states: no line counts, import edges or header text (the checkers measure those, and their
shrink-only baselines stay separate, machine-written files). TOML, not YAML, because the checkers run with the target project's own
interpreter and Python 3.11 reads TOML without installing anything.

Sections (all optional; template: the pack's templates/code-map.toml):
    [scan]            roots = ["src", "scripts"]; python = "3.11"; [scan.exclude] "<path>" = "<why its rule lives elsewhere>"
    [limits.<lang>]   module, function, warn_module, warn_function  (lang: python, shell, c-family, or a suffix such as "go")
    [layers]          src = "src"; package = "app"; baseline = "..."; then [layers.rules.<subpackage>] layer, may_import
    [write_gates]     roots, suffixes, write_patterns, apply_pattern; [write_gates.exceptions] "<path>" = "<reason>"
    [timeouts]        roots; baseline
    [group_timeouts]  roots; baseline   (timed ssh/shell subprocess calls that leave children running)
    [suppressions]    roots; baseline   (inline linter suppressions)
    [process_match]   roots             (unanchored pgrep/pkill -f patterns)
    [naming]          recipe = "<convention>"; [naming.files] "<glob>" = "<convention>"  (overrides the pack's naming.toml)
    [modules."<path>"] status = "project_only" | "candidate" | "promoted"; reason; needs; skill

Imported, not run: `from code_map import load, section`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: Section names a code map may have; anything else is reported, so a typo does not silently switch a rule off.
SECTIONS = ("scan", "limits", "layers", "write_gates", "timeouts", "group_timeouts", "suppressions", "process_match", "modules", "naming", "meta")
STATUSES = ("project_only", "candidate", "promoted")


def load(path: Path | None) -> dict:
    """Read and check a code map.

    Args:
        path: the code-map.toml file, or None for no map.

    Returns:
        The map as a dict ({} for None).

    Raises:
        ValueError: when the file does not parse, names an unknown section, or a module entry has an unknown status or no reason.
    """
    if path is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    problems = [f"unknown section [{k}]" for k in data if k not in SECTIONS]
    for rel, entry in data.get("modules", {}).items():
        if entry.get("status") not in STATUSES:
            problems.append(f"modules.\"{rel}\": status must be one of {', '.join(STATUSES)}")
        elif entry["status"] == "promoted" and not entry.get("skill"):
            problems.append(f"modules.\"{rel}\": a promoted module names the skill file it moved to")
        elif entry["status"] != "promoted" and not (entry.get("reason") or entry.get("needs")):
            problems.append(f"modules.\"{rel}\": say why (reason) or what it still needs (needs)")
    if problems:
        raise ValueError(f"{path}: " + "; ".join(problems))
    return data


def section(data: dict, name: str) -> dict:
    """One section of a loaded map.

    Args:
        data: load()'s result.
        name: a name from SECTIONS.

    Returns:
        The section ({} when absent).
    """
    return dict(data.get(name, {}))


def for_root(root: Path, given: Path | None) -> dict:
    """The code map a checker uses: the one given, else `code-map.toml` at the project root when it exists, else none.

    Args:
        root: the project root.
        given: --code-map as passed (relative to the root), or None.

    Returns:
        load()'s result.

    Raises:
        ValueError: as load().
    """
    path = root / given if given else root / "code-map.toml"
    return load(path if (given or path.is_file()) else None)


def grammar(cli: str | None, data: dict) -> tuple[int, int] | None:
    """The Python grammar to parse with: --python, else `[scan] python`, else this interpreter's.

    Args:
        cli: --python as passed, or None.
        data: load()'s result.

    Returns:
        (major, minor), or None.
    """
    text = cli or section(data, "scan").get("python")
    return tuple(int(x) for x in str(text).split(".")[:2]) if text else None


def scan_roots(data: dict, own: str = "", default: str = "src,scripts") -> str:
    """The folders a checker scans: its own section's `roots`, else `[scan] roots`, else the default.

    Args:
        data: load()'s result.
        own: the checker's section name.
        default: comma-separated fallback.

    Returns:
        Comma-separated folders.
    """
    roots = section(data, own).get("roots") if own else None
    roots = roots or section(data, "scan").get("roots")
    return ",".join(roots) if roots else default


def excluded(data: dict) -> dict[str, str]:
    """Files no checker measures, each with the reason (a file whose rule is owned elsewhere, such as a checker generated from another skill's
    template, or vendored code).

    Args:
        data: load()'s result.

    Returns:
        {repo-relative path: reason} from `[scan.exclude]`.

    Raises:
        ValueError: when an entry has no reason.
    """
    out = dict(section(data, "scan").get("exclude", {}))
    if blank := [k for k, v in out.items() if not str(v).strip()]:
        raise ValueError(f"[scan.exclude] entries need a reason: {', '.join(blank)}")
    return out
````

## File: scripts/code_size.py
````python
#!/usr/bin/env python3
"""Hold modules and functions to a size limit in any language, as a shrink-only ratchet. Read-only unless --write-baseline. Stdlib only.

Why (unified-network-controller code architecture design, rule R34, 2026-10-10): "a module stays under 400 lines and a function under 60; a larger
one at adoption is recorded with its size and may only shrink". Small units are cheaper to read, test and replace; the limit is a prompt to split
along a real seam, not an aesthetic.

How functions are found, per language (LANGS): Python exactly, through `ast`; shell by `name() {` or `function name` and brace depth; C-family
languages (JavaScript, TypeScript, Go, Rust, Java, C, C#, Kotlin, Swift, PHP) by a function header pattern and brace depth, ignoring braces in
strings and comments. The brace scan is a heuristic: it is right for code a formatter has laid out, and says so in its output.

Two thresholds per unit: past `warn_*` the unit is reported as a warning (plan the split along a seam the next time it is touched); past the hard
limit it fails unless the baseline records it. Defaults (DEFAULT_LIMITS, LANG_LIMITS): modules warn 300 / fail 400, functions warn 40 / fail 60;
shell scripts warn 100 / fail 200, functions 30 / 40. A project overrides any of them per language or suffix with --limits FILE (JSON
{"go": {"module": 600}, "sh": {...}}), which is how a language override is kept without editing this script.

Usage:
    code_size.py --project-root . [--roots src,scripts] [--baseline scripts/code-size-baseline.json]
    code_size.py --project-root . --write-baseline      # adopt: record today's oversized units
    code_size.py --project-root . --list                # every oversized unit, baseline or not
Exit: 0 when nothing is over its allowance and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Language by file suffix.
LANGS = {".py": "python", ".sh": "shell", ".bash": "shell", ".js": "c-family", ".mjs": "c-family", ".ts": "c-family", ".tsx": "c-family",
         ".jsx": "c-family", ".go": "c-family", ".rs": "c-family", ".java": "c-family", ".c": "c-family", ".h": "c-family", ".cs": "c-family",
         ".kt": "c-family", ".swift": "c-family", ".php": "c-family"}
#: Lines at which a unit must be split (fails the check unless baselined) and at which the split should be planned (a warning, never a failure).
DEFAULT_LIMITS = {"module": 400, "function": 60, "warn_module": 300, "warn_function": 40}
#: Built-in language defaults over DEFAULT_LIMITS. Shell: past about 100 lines a script belongs in a structured language (Google Shell Style
#: Guide; UNVERIFIED until the pack's sources record it), so the warning is 100 and the hard limit 200.
LANG_LIMITS = {"shell": {"module": 200, "function": 40, "warn_module": 100, "warn_function": 30}}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "vendor", "dist", "build", ".mypy_cache", ".ruff_cache"}
SHELL_FN = re.compile(r"^\s*(?:function\s+([A-Za-z_][\w-]*)\s*(?:\(\))?|([A-Za-z_][\w-]*)\s*\(\))\s*\{?\s*$")
C_FN = re.compile(r"^\s*(?:export\s+|pub(?:\([^)]*\))?\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|override\s+|fun\s+|func\s+|fn\s+|"
                  r"function\s+)*(?:func\s*(?:\([^)]*\)\s*)?|fn\s+|function\s*\*?\s*|fun\s+)?([A-Za-z_$][\w$]*)\s*(?:<[^>]*>)?\s*\([^;]*$")
C_KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "else", "do", "try", "match", "loop", "select", "with"}


def python_functions(text: str, grammar: tuple[int, int] | None = None) -> list[tuple[str, int]]:
    """Every function and method in Python source, with its length in lines (decorators excluded).

    Args:
        text: the source.
        grammar: (major, minor) to parse with the target project's grammar (ast feature_version); None for this interpreter's.

    Returns:
        (qualified name, lines) per function.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it; a file is never skipped silently).
    """
    tree = pyparse.parse(text, grammar)
    out: list[tuple[str, int]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        """Collect functions under one node.

        Args:
            node: an AST node.
            prefix: the qualified name of the enclosing class or function.
        """
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                out.append((name, child.end_lineno - child.lineno + 1))
                walk(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")

    walk(tree, "")
    return out


def _strip_line(line: str, state: dict) -> str:
    """A C-family or shell line with string, character and comment contents removed, so only code braces remain.

    Shell has no `//` or `/* */` comments (`dir/*` is a glob), and `#` starts a comment only at the start of a word (`${#arr[@]}` is code).

    Args:
        line: one source line.
        state: {"block": bool, "shell": bool}; "block" carries an open /* comment */ across lines.

    Returns:
        The line's code characters.
    """
    out, i, quote = [], 0, ""
    while i < len(line):
        two = line[i:i + 2]
        if state["block"]:
            if two == "*/":
                state["block"], i = False, i + 2
                continue
            i += 1
            continue
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        shell = state.get("shell")
        if two == "/*" and not shell:
            state["block"], i = True, i + 2
            continue
        if (two == "//" and not shell) or (shell and ch == "#" and (i == 0 or line[i - 1] in " \t;|&(")):
            break
        if ch in "\"'`":
            quote = ch
        else:
            out.append(ch)
        i += 1
    return "".join(out)


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w]*)\1")


def _blank_heredocs(lines: list[str]) -> list[str]:
    """Shell lines with every here-document body blanked, so braces in embedded JSON, Terraform or templates are not counted as code.

    Args:
        lines: the script's lines.

    Returns:
        The same number of lines; a body line becomes "" and the line opening the here-document keeps only its text before `<<`.
    """
    out, end = [], None
    for line in lines:
        if end is not None:
            out.append("")
            if line.strip() == end:
                end = None
            continue
        m = HEREDOC.search(line)
        if m and "<<<" not in line:
            end = m.group(2)
            out.append(line[:m.start()])
        else:
            out.append(line)
    return out


def brace_functions(text: str, lang: str) -> list[tuple[str, int]]:
    """Functions in a brace language or shell, found by header pattern and brace depth (a heuristic for formatted code).

    Args:
        text: the source.
        lang: "c-family" or "shell".

    Returns:
        (name, lines) per function whose body closes; nested functions are counted on their own and inside their parent.
    """
    lines = text.splitlines()
    header = SHELL_FN if lang == "shell" else C_FN
    state = {"block": False, "shell": lang == "shell"}
    code = [_strip_line(line, state) for line in (_blank_heredocs(lines) if lang == "shell" else lines)]
    out: list[tuple[str, int]] = []
    for start, line in enumerate(lines):
        m = header.match(line)
        if not m:
            continue
        name = next(g for g in m.groups() if g)
        if name in C_KEYWORDS:
            continue
        depth, opened = 0, False
        for end in range(start, min(len(lines), start + 5000)):
            depth += code[end].count("{") - code[end].count("}")
            opened = opened or "{" in code[end]
            if opened and depth <= 0:
                out.append((name, end - start + 1))
                break
            if not opened and end - start > 3:   # a declaration with no body (prototype, interface method)
                break
    return out


@dataclass
class Measurement:
    """What measure() found.

    Args:
        modules: {path: lines} for modules over their hard limit.
        functions: {"path::name": lines} for functions over their hard limit.
        warnings: "path: N lines (plan the split at W, must split at H)" per unit past its warning but within its hard limit.
        unparsed: "path: line L: error" per file that did not parse (reported, never skipped silently).
    """

    modules: dict[str, float] = field(default_factory=dict)
    functions: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)


def limits_for(path: Path, lang: str, overrides: dict[str, dict], base: dict | None = None) -> dict[str, int]:
    """The four limits for one file: the base, then the language's built-in default, then the project's language and suffix overrides.

    Args:
        path: the file.
        lang: its language from LANGS.
        overrides: the project's {language or suffix: {key: n}} (keys as DEFAULT_LIMITS).
        base: limits for every language; default DEFAULT_LIMITS.

    Returns:
        {"module", "function", "warn_module", "warn_function"}.
    """
    return {**(base or DEFAULT_LIMITS), **LANG_LIMITS.get(lang, {}), **overrides.get(lang, {}), **overrides.get(path.suffix.lstrip("."), {})}


def _check_unit(out: Measurement, key: str, size: int, hard: int, warn: int, bucket: dict) -> None:
    """File one unit as over its hard limit, past its warning, or fine.

    Args:
        out: the measurement being filled.
        key: the unit's key (path, or path::name).
        size: its length in lines.
        hard: the limit that fails.
        warn: the limit that warns.
        bucket: out.modules or out.functions.
    """
    if size > hard:
        bucket[key] = max(size, bucket.get(key, 0))
    elif size > warn:
        out.warnings.append(f"{key}: {size} lines (plan the split at {warn}, must split at {hard})")


def measure(root: Path, roots: list[str], overrides: dict[str, dict], base: dict | None = None,
            grammar: tuple[int, int] | None = None, exclude: frozenset = frozenset()) -> Measurement:
    """Every module and function past its language's warning or hard limit.

    Args:
        root: the project root.
        roots: folders to scan, relative to the root.
        overrides: the project's {language or suffix: {key: n}}.
        base: limits for every language; default DEFAULT_LIMITS.
        grammar: the Python grammar to parse with (see python_functions).
        exclude: repo-relative files not measured (the code map's [scan.exclude]).

    Returns:
        The measurement.
    """
    out = Measurement()
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            lang = LANGS.get(path.suffix)
            if not lang or not path.is_file() or SKIP_PARTS & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            if rel in exclude:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lim = limits_for(path, lang, overrides, base)
            _check_unit(out, rel, len(text.splitlines()), lim["module"], lim["warn_module"], out.modules)
            try:
                found = python_functions(text, grammar) if lang == "python" else brace_functions(text, lang)
            except SyntaxError as exc:
                out.unparsed.append(f"{rel}: line {exc.lineno}: {exc.msg}")
                continue
            for name, size in found:
                _check_unit(out, f"{rel}::{name}", size, lim["function"], lim["warn_function"], out.functions)
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line: measure, compare with the baseline, or write it.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within allowance and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders to scan (default: the code map's, else src,scripts; missing ones are skipped)")
    ap.add_argument("--baseline", default="scripts/code-size-baseline.json")
    ap.add_argument("--limits", type=Path, help='JSON {"<language or suffix>": {"module": n, "function": m, "warn_module": w, "warn_function": v}}')
    ap.add_argument("--write-baseline", action="store_true", help="record today's oversized units (adoption or after an improvement)")
    ap.add_argument("--list", action="store_true", help="print every oversized unit and every warning")
    ap.add_argument("--python", help="parse Python at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"code_size: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap)
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"code_size: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    overrides = {**code_map.section(cmap, "limits"), **(json.loads(args.limits.read_text(encoding="utf-8")) if args.limits else {})}
    grammar = code_map.grammar(args.python, cmap)
    try:
        exclude = frozenset(code_map.excluded(cmap))
    except ValueError as exc:
        print(f"code_size: {exc}", file=sys.stderr)
        return 2
    got = measure(root, roots, overrides, grammar=grammar, exclude=exclude)
    for line in got.unparsed:
        print(f"FAIL unparsed: {line} (not measured; check --python matches the project)")
    found = {**{f"module {k}": v for k, v in got.modules.items()}, **{f"function {k}": v for k, v in got.functions.items()}}
    base_path = root / args.baseline
    if args.list:
        print("\n".join([f"{key}: {size:g} lines" for key, size in sorted(found.items())] + [f"WARN {w}" for w in got.warnings]))
    if args.write_baseline:
        ratchet.save(base_path, found)
        print(f"code_size: baseline written, {len(got.modules)} module(s) and {len(got.functions)} function(s) over ({base_path})")
        return 0
    verdict = ratchet.compare(found, ratchet.load(base_path))
    print("\n".join(ratchet.report(verdict, "size", base_path)) or
          f"code_size: OK, {len(found)} oversized unit(s) within the baseline, {len(got.warnings)} warning(s) (--list shows them)")
    return 0 if verdict.ok and not got.unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/code-size-baseline.json
````json
{}
````

## File: scripts/cpuprofile_summary.py
````python
#!/usr/bin/env python3
"""Summarise V8 .cpuprofile files (VS Code extension host, Node, Chrome): self time per extension, hottest functions, hottest stacks. Read-only. Stdlib only.

Why (Learned 2026-10-28, ansible-wifi): VS Code's Git view went stale and each git call took ~950 ms although the same command took 70 ms on the
CLI. The extension host was pinned, and exthost.log named an extension and saved a .cpuprofile per stall. Reading those profiles by hand is not
practical; this reduces each one to the extension, the functions and the call chain that burn the time, which is what points at the cause
(there: Foam re-labelling every note against every same-named note, fed by symlinked snapshot folders).

Profiles live where exthost.log says (`UNRESPONSIVE extension host: '<ext>' took N% ... saved PROFILE here: 'file://...'`), usually
$TMPDIR/exthost-*.cpuprofile. Stacks show only frames from the extension under study: `--ext` names it, else the one with the most self time.

Usage:
    cpuprofile_summary.py PROFILE [PROFILE ...] [--top 6] [--ext foam.foam-vscode]
Exit: 0 when every profile was read, 1 when one could not be read or parsed, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: The extension folder in a script URL, e.g. .../extensions/foam.foam-vscode-0.46.0/out/... -> foam.foam-vscode-0.46.0.
EXT_DIR = re.compile(r"/extensions/([^/]+)/")


def ext_of(url: str) -> str:
    """Name the owner of a call frame from its script URL.

    Args:
        url: the frame's script URL (empty for native frames and the garbage collector).

    Returns:
        The extension folder name, "core" for other scripts (VS Code itself, Node), or "(native/gc)" when there is no URL.
    """
    m = EXT_DIR.search(url or "")
    if m:
        return m.group(1)
    return "core" if url else "(native/gc)"


def summarise(prof: dict, top: int = 6, ext: str | None = None) -> dict:
    """Reduce one parsed profile to self time by extension, by function and by stack of the extension under study.

    Args:
        prof: the parsed .cpuprofile JSON (keys nodes, samples, timeDeltas).
        top: how many rows to keep in each list.
        ext: substring naming the extension whose frames make up the stacks; None picks the extension with the most self time.

    Returns:
        A dict with total_ms, ext (the one studied), and lists by_ext, by_fn, by_stack of (label, percent of total) rows, largest first.
    """
    nodes = {n["id"]: n for n in prof["nodes"]}
    parent = {c: n["id"] for n in prof["nodes"] for c in n.get("children", [])}
    self_us: collections.Counter = collections.Counter()
    for sid, dt in zip(prof["samples"], prof["timeDeltas"]):
        self_us[sid] += dt
    total = sum(self_us.values()) or 1
    by_ext: collections.Counter = collections.Counter()
    by_fn: collections.Counter = collections.Counter()
    for nid, us in self_us.items():
        cf = nodes[nid]["callFrame"]
        by_ext[ext_of(cf["url"])] += us
        by_fn[f"{cf['functionName'] or '(anon)'}  {ext_of(cf['url'])}:{cf['lineNumber']}"] += us
    studied = ext or next((e for e, _ in by_ext.most_common() if e not in ("core", "(native/gc)")), "")
    by_stack: collections.Counter = collections.Counter()
    for nid, us in self_us.items():
        chain, cur = [], nid
        while cur in nodes:  # innermost frame first, up to the root
            f = nodes[cur]["callFrame"]
            if studied and studied in ext_of(f["url"]):
                chain.append(f"{f['functionName'] or '(anon)'}:{f['lineNumber']}")
            cur = parent.get(cur)
        if chain:
            by_stack[" <- ".join(chain[:8])] += us

    def rows(c: collections.Counter) -> list[tuple[str, float]]:
        """Top rows of a counter as percentages of the profile's total.

        Args:
            c: microseconds per label.

        Returns:
            Up to `top` (label, percent) pairs, largest first.
        """
        return [(k, round(v * 100 / total, 1)) for k, v in c.most_common(top)]

    return {"total_ms": round(total / 1000), "ext": studied, "by_ext": rows(by_ext), "by_fn": rows(by_fn), "by_stack": rows(by_stack)}


def render(name: str, s: dict) -> str:
    """Format one summary for the console.

    Args:
        name: the profile's file name, for the heading.
        s: a summary from summarise().

    Returns:
        The text block, one row per line.
    """
    out = [f"== {name}  total {s['total_ms']} ms  stacks for: {s['ext'] or '(none)'}"]
    for kind in ("ext", "fn", "stack"):
        out += [f"  {kind:5} {pct:5.1f}%  {label}" for label, pct in s[f"by_{kind}"]]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Summarise each profile named on the command line.

    Args:
        argv: command-line arguments; None reads sys.argv.

    Returns:
        0 when every profile was read, 1 when one could not be read or parsed.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("profiles", nargs="+", type=Path, help=".cpuprofile files")
    ap.add_argument("--top", type=int, default=6, help="rows per list (default 6)")
    ap.add_argument("--ext", help="extension (substring) whose frames form the stacks; default: the one with the most self time")
    args = ap.parse_args(argv)
    rc = 0
    for p in args.profiles:
        try:
            with p.open(encoding="utf-8") as fh:
                prof = json.load(fh)
            print(render(p.name, summarise(prof, args.top, args.ext)))
        except (OSError, ValueError, KeyError) as exc:
            print(f"== {p.name}  unreadable: {exc}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/doc-freshness-baseline.json
````json
{}
````

## File: scripts/group_timeouts.py
````python
#!/usr/bin/env python3
"""Find timed subprocess calls whose command starts children of its own (ssh, a shell), which the timeout leaves running, as a shrink-only
ratchet. Read-only unless --write-baseline. Stdlib only.

Why (references/errors-and-timeouts.md, Learned 2026-10-20): `subprocess.run(timeout=)` kills only the process it started. `ssh` to a host
reached through a ProxyCommand (`tsh proxy ssh`, a jump host) starts the proxy as its own child, and a shell starts the pipeline it runs; both
outlive the kill. In one project, Teleport proxies to an unreachable box were still running ten minutes after the 90 s timeout, and the host's
load rose. The fix is a runner that starts the child in its own session and ends the whole process group on timeout.

Counted, through `ast`: subprocess.run/call/check_call/check_output with `timeout=` whose command is a list or tuple starting with one of
SPAWNERS, a call to a function named like one (`ssh_argv(...)`, `bash_cmd(...)`), or `shell=True`. A call passing `**kwargs` is trusted.
Also a `Popen(...)` stopped with `.kill()` or `.terminate()` in the same function without `start_new_session=`/`process_group=` (2026-10-20:
a collector's per-site limit killed only the child, and the child's ssh proxies and forwards ran on).

Usage:
    group_timeouts.py --project-root . [--roots src,scripts] [--baseline scripts/group-timeout-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more such calls than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import call_timeouts
import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Commands that start children of their own: ssh and its relatives start a ProxyCommand; a shell starts what it runs. Not `tsh`:
#: `tsh ssh` connects in-process and starts no child, so killing it ends the session (it is what ssh starts as the proxy).
SPAWNERS = {"ssh", "scp", "sftp", "rsync", "autossh", "sh", "bash", "zsh", "dash"}
#: The run family: these wait for the child and kill only it on timeout.
RUN_FAMILY = {"subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output"}


def _command_name(node: ast.AST) -> str:
    """The program a call's first argument starts, as far as the source shows it.

    Args:
        node: the call's first positional argument.

    Returns:
        The program ("ssh"), the last part of a builder function's name ("ssh_argv" for remote.ssh_argv(...)), or "".
    """
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return Path(first.value).name
        return ""
    if isinstance(node, ast.Call):
        return call_timeouts._dotted(node.func).split(".")[-1]
    return ""


def _popen_killed_alone(tree: ast.AST) -> list[tuple[int, str]]:
    """Popen children stopped with `.kill()` or `.terminate()` that were not started in their own session: the signal reaches only the child.

    Per function: a name bound to `Popen(...)` (assignment or `with ... as`), a `<name>.kill()`/`.terminate()` anywhere in that function, and no
    `start_new_session=` or `process_group=` on the Popen call (with them, the caller can end the group with os.killpg).

    Args:
        tree: the parsed module.

    Returns:
        (line of the Popen call, "Popen(...).kill()") per finding.
    """
    out: list[tuple[int, str]] = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        bound: dict[str, ast.Call] = {}
        for node in ast.walk(func):
            pairs = []
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                pairs = [(t, node.value) for t in node.targets]
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                pairs = [(i.optional_vars, i.context_expr) for i in node.items if isinstance(i.context_expr, ast.Call)]
            for target, call in pairs:
                if isinstance(target, ast.Name) and call_timeouts._dotted(call.func).endswith("Popen"):
                    bound[target.id] = call
        stopped = {n.func.value.id for n in ast.walk(func) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr in {"kill", "terminate"} and isinstance(n.func.value, ast.Name)}
        for name in sorted(stopped & bound.keys()):
            call = bound[name]
            if not {k.arg for k in call.keywords} & {"start_new_session", "process_group", None}:
                out.append((call.lineno, f"Popen(...) stopped with {name}.kill()/terminate()"))
    return out


def group_unsafe_calls(text: str, grammar: tuple[int, int] | None = None) -> list[tuple[int, str]]:
    """Timed run-family calls whose command starts children the timeout would leave running.

    Args:
        text: the Python source.
        grammar: (major, minor) to parse with the target project's grammar; None for this interpreter's.

    Returns:
        (line, "subprocess.run(ssh ...)") per call.

    Raises:
        SyntaxError: when the source does not parse (the caller reports it).
    """
    tree = pyparse.parse(text, grammar)
    out: list[tuple[int, str]] = _popen_killed_alone(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_timeouts._dotted(node.func)
        if ".".join(name.split(".")[-2:]) not in RUN_FAMILY:
            continue
        keywords = {k.arg for k in node.keywords}
        if "timeout" not in keywords or None in keywords:
            continue
        shell = any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords)
        program = _command_name(node.args[0]) if node.args else ""
        spawns = shell or program in SPAWNERS or any(program.endswith(f"_{s}") or program.startswith(f"{s}_") for s in SPAWNERS)
        if spawns:
            out.append((node.lineno, f"{name}({'shell=True' if shell else program} ...)"))
    return out


def measure(root: Path, roots: list[str], grammar: tuple[int, int] | None = None) -> tuple[dict[str, float], dict[str, list], list[str]]:
    """Group-unsafe calls per file.

    Args:
        root: the project root.
        roots: folders to scan.
        grammar: the Python grammar to parse with.

    Returns:
        ({path: count} for files with any, {path: [(line, text)]}, ["path: error"] for files that do not parse).
    """
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    unparsed: list[str] = []
    for folder in roots:
        for path in sorted((root / folder).rglob("*.py")):
            if {".venv", "venv", "node_modules", "__pycache__"} & set(path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                found = group_unsafe_calls(path.read_text(encoding="utf-8", errors="replace"), grammar)
            except SyntaxError as exc:
                unparsed.append(f"{rel}: line {exc.lineno}: {exc.msg}")
                continue
            if found:
                counts[rel], detail[rel] = len(found), found
    return counts, detail, unparsed


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [group_timeouts] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [group_timeouts] baseline, else scripts/group-timeout-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every such call")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--python", help="parse at this grammar (the project's version, e.g. 3.11)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"group_timeouts: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "group_timeouts")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"group_timeouts: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    base_path = root / (args.baseline or code_map.section(cmap, "group_timeouts").get("baseline", "scripts/group-timeout-baseline.json"))
    counts, detail, unparsed = measure(root, roots, code_map.grammar(args.python, cmap))
    for line in unparsed:
        print(f"FAIL unparsed: {line} (not checked; check --python matches the project)")
    if args.list:
        for rel, calls in detail.items():
            for line, text in calls:
                print(f"{rel}:{line}: {text} kills only its child on timeout; end the process group")
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"group_timeouts: baseline written, {sum(counts.values()):g} call(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "group timeouts", base_path):
        print(line)
    if verdict.ok:
        print(f"group_timeouts: OK, {sum(counts.values()):g} call(s), all within the baseline")
    return 0 if verdict.ok and not unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/import_layers.py
````python
#!/usr/bin/env python3
"""Python import structure: layer violations against a rules file, import cycles, and a package-level import graph. Read-only. Stdlib only.

Promoted from unified-network-controller `scripts/checks/import_graph.py` (2026-10-19). Why (its code architecture design, principles 2 and rules
R2-R3): dependencies point inwards and there are no import cycles, so a lower layer can be tested and replaced without the code above it. The
rule is data: a TOML file with one table per top-level package of the checked package, its layer name and the packages it may import:

    [core]
    layer = "L0"
    may_import = []
    [services]
    layer = "L5"
    may_import = ["core", "backends.skills"]   # a dotted entry allows that subpackage only

A package the file does not list is not checked yet, so a code base adopts layers one package at a time. Accepted violations (code moved in
unchanged) go in a baseline file, one line each; any other violation fails.

Usage:
    import_layers.py --project-root . --src src --package app --layers src/app/layers.toml [--baseline scripts/import-layers-baseline.json]
    import_layers.py --project-root . --graph --roots src,scripts                    # modules, edges, fan-in, cycles (report only)
    import_layers.py --project-root . --graph --roots lib,tools:self --json          # a root ending ":self" keeps its folder as the first name part
Exit: 0 when no new violation (and no cycle with --fail-on-cycles), 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import collections
import json
import sys
import tomllib
from pathlib import Path

import code_map
import pyparse

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


def _imported_names(tree: ast.AST) -> list[str]:
    """Absolute dotted names a module imports (relative imports are inside its own package and never cross a layer).

    Args:
        tree: the parsed module.

    Returns:
        Names in source order.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.append(node.module)
    return out


def _graph_names(module: str, path: Path, tree: ast.AST) -> list[str]:
    """The dotted names a module imports for the graph: relative imports made absolute, and `from pkg import name` as `pkg.name` (name may be
    a submodule; resolution falls back to `pkg` when it is not).

    Args:
        module: the importing module's dotted name.
        path: its file (an `__init__.py` resolves relative imports from itself).
        tree: its parsed AST.

    Returns:
        Imported dotted names in source order.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                base = node.module or ""
            else:
                parts = module.split(".")
                keep = len(parts) - node.level + (1 if path.name == "__init__.py" else 0)
                base = ".".join(parts[:max(keep, 0)] + ([node.module] if node.module else []))
            out += [f"{base}.{a.name}" if base else a.name for a in node.names]
    return out


def layer_violations(src: Path, package: str, rules: dict) -> list[str]:
    """Imports inside `src/<package>` that break the layer rules.

    A module in subpackage P may import `<package>` itself, P, and what P's `may_import` lists.

    Args:
        src: the folder holding the package.
        package: the top-level package name.
        rules: the parsed TOML {subpackage: {"layer": str, "may_import": [str]}}.

    Returns:
        Sorted lines `<module> -> <imported module> (<layer> <P> may not import <Q>)`.
    """
    found: set[str] = set()
    for path in sorted((src / package).rglob("*.py")):
        parts = path.relative_to(src).with_suffix("").parts
        module = ".".join(p for p in parts if p != "__init__")
        sub = parts[1] if len(parts) > 2 else None
        if sub not in rules:
            continue
        allowed = rules[sub].get("may_import", [])
        for name in _imported_names(pyparse.parse(path.read_text(encoding="utf-8"))):
            if not name.startswith(package + "."):
                continue
            target = name.split(".")[1:]
            if target[0] == sub or any(".".join(target[: len(a.split("."))]) == a for a in allowed):
                continue
            found.add(f"{module} -> {name} ({rules[sub]['layer']} {sub} may not import {target[0]})")
    return sorted(found)


def module_map(root: Path, roots: list[str]) -> dict[str, Path]:
    """Every Python module under the roots, by dotted name.

    A root is named relative to itself (`src`: `src/app/x.py` is `app.x`), or, with a `:self` suffix, keeps its folder as the first name part
    (`scripts:self`: `scripts/x.py` is `scripts.x`), for a folder of loose scripts that should count as one package (2026-10-19).

    Args:
        root: the project root.
        roots: folders relative to the root, each optionally ending `:self`.

    Returns:
        {dotted name: path}; a package's `__init__` is named as the package.
    """
    mods: dict[str, Path] = {}
    for entry in roots:
        folder, _, naming = entry.strip().partition(":")
        base = root / folder
        for path in sorted(base.rglob("*.py")) if base.is_dir() else []:
            if "__pycache__" not in path.parts:
                rel = path.relative_to(root if naming == "self" else base).with_suffix("")
                mods[".".join(rel.parts).removesuffix(".__init__")] = path
    return mods


def graph(mods: dict[str, Path]) -> dict[str, set[str]]:
    """Which known module imports which.

    Args:
        mods: module_map()'s result.

    Returns:
        {module: modules it imports}; stdlib and third-party imports are left out.
    """
    out: dict[str, set[str]] = collections.defaultdict(set)
    for name, path in mods.items():
        try:
            tree = pyparse.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for imported in _graph_names(name, path, tree):
            parts = imported.split(".")
            hit = next((".".join(parts[:i]) for i in range(len(parts), 0, -1) if ".".join(parts[:i]) in mods), None)
            if hit and hit != name:
                out[name].add(hit)
    return out


def cycles(edges: dict[str, set[str]], nodes: list[str]) -> list[list[str]]:
    """Import cycles: strongly connected components of more than one module (Tarjan, iterative, so deep graphs do not hit the recursion limit).

    Args:
        edges: module -> modules it imports.
        nodes: every module.

    Returns:
        Each cycle as a sorted list of names.
    """
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    found: list[list[str]] = []
    for start in nodes:
        if start in index:
            continue
        work = [(start, iter(sorted(edges.get(start, ()))))]
        index[start] = low[start] = len(index)
        stack.append(start)
        on_stack.add(start)
        while work:
            node, children = work[-1]
            child = next((c for c in children if c not in index or c in on_stack), None)
            if child is not None and child not in index:
                index[child] = low[child] = len(index)
                stack.append(child)
                on_stack.add(child)
                work.append((child, iter(sorted(edges.get(child, ())))))
                continue
            if child is not None:
                low[node] = min(low[node], index[child])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                comp = []
                while (member := stack.pop()) != node:
                    on_stack.discard(member)
                    comp.append(member)
                on_stack.discard(node)
                comp.append(node)
                if len(comp) > 1:
                    found.append(sorted(comp))
    return found


def _top(module: str) -> str:
    """A module's top-level package.

    Args:
        module: a dotted name.

    Returns:
        Its first part.
    """
    return module.split(".")[0]


def analyse(root: Path, mods: dict[str, Path], edges: dict[str, set[str]]) -> dict:
    """The import structure as data: modules and entry points per package, cross-package edges, fan-in, never-imported modules, `sys.path` users,
    cycles and files that did not parse (the measures a code-structure review compares stage by stage).

    Args:
        root: the project root (paths are reported relative to it).
        mods: module_map()'s result.
        edges: graph()'s result.

    Returns:
        {"modules", "entry_points", "edges": [{"from", "to", "count"}], "fan_in": [[module, n]] (top 30), "never_imported", "sys_path", "cycles",
        "unparsed"}.
    """
    mains: collections.Counter = collections.Counter()
    cross: collections.Counter = collections.Counter()
    syspath, unparsed = [], []
    for name, path in mods.items():
        src = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = pyparse.parse(src)
        except SyntaxError:
            unparsed.append(path.relative_to(root).as_posix())
            continue
        if '__name__ == "__main__"' in src or "__name__ == '__main__'" in src:
            mains[_top(name)] += 1
        if "sys.path" in src:
            syspath.append(path.relative_to(root).as_posix())
        # An edge counts every import statement that crosses packages (the measure the code-structure reviews compare), not distinct pairs.
        for imported in _graph_names(name, path, tree):
            parts = imported.split(".")
            hit = next((".".join(parts[:i]) for i in range(len(parts), 0, -1) if ".".join(parts[:i]) in mods), None)
            if hit and hit != name and _top(hit) != _top(name):
                cross[(_top(name), _top(hit))] += 1
    counts = collections.Counter(b for bs in edges.values() for b in bs)
    # Ties are broken by name: edges are sets, so most_common() alone would order equal counts differently from run to run.
    fan_in = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:30]
    return {"modules": dict(collections.Counter(map(_top, mods))), "entry_points": dict(mains),
            "edges": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(cross.items())],
            "fan_in": [list(x) for x in fan_in], "never_imported": sorted(m for m in mods if m not in counts),
            "sys_path": sorted(syspath), "cycles": cycles(edges, list(mods)), "unparsed": unparsed}


def render(result: dict) -> list[str]:
    """analyse()'s result as report lines.

    Args:
        result: analyse()'s dict.

    Returns:
        Report lines.
    """
    lines = ["modules per package: " + ", ".join(f"{k} {v}" for k, v in sorted(result["modules"].items())),
             "entry points per package: " + ", ".join(f"{k} {v}" for k, v in sorted(result["entry_points"].items())),
             "cross-package import edges (from -> to: count):"]
    lines += [f"  {e['from']} -> {e['to']}: {e['count']}" for e in result["edges"]]
    lines.append("top fan-in: " + ", ".join(f"{m} {n}" for m, n in result["fan_in"]))
    lines.append(f"sys.path manipulators: {len(result['sys_path'])}")
    lines.append(f"never imported (entry points included): {len(result['never_imported'])}")
    lines.append("cycles: " + ("; ".join(" <-> ".join(c) for c in result["cycles"]) or "none"))
    if result["unparsed"]:
        lines.append("did not parse: " + ", ".join(result["unparsed"]))
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command line: check layers against the baseline, or print the graph report.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when clean, 1 on a new violation (or a cycle with --fail-on-cycles), 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--src", default="src", help="folder holding the checked package")
    ap.add_argument("--package", help="top-level package to check against --layers")
    ap.add_argument("--layers", help="TOML rules file, relative to the root")
    ap.add_argument("--baseline", help="JSON list of accepted violation lines")
    ap.add_argument("--graph", action="store_true", help="print the import graph report for --roots")
    ap.add_argument("--roots", help="comma-separated folders for --graph and cycle checks, each optionally ending :self (default: the code map's [scan] roots, else src)")
    ap.add_argument("--json", action="store_true", help="with --graph, print the report as JSON")
    ap.add_argument("--fail-on-cycles", action="store_true")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"import_layers: {exc}", file=sys.stderr)
        return 2
    layers = code_map.section(cmap, "layers")
    rc = 0
    mods = module_map(root, (args.roots or code_map.scan_roots(cmap, default="src")).split(","))
    edges = graph(mods)
    if args.graph:
        result = analyse(root, mods, edges)
        print(json.dumps(result, indent=1) if args.json else "\n".join(render(result)))
    if args.fail_on_cycles and (found := cycles(edges, list(mods))):
        print("\n".join("cycle: " + " <-> ".join(c) for c in found))
        rc = 1
    if args.layers or layers.get("rules"):
        package = args.package or layers.get("package")
        if not package:
            print("layer rules need --package (or [layers] package in the code map)", file=sys.stderr)
            return 2
        rules = tomllib.loads((root / args.layers).read_text(encoding="utf-8")) if args.layers else layers["rules"]
        baseline = args.baseline or layers.get("baseline")
        accepted = set(json.loads((root / baseline).read_text(encoding="utf-8"))) if baseline and (root / baseline).is_file() else set()
        src = args.src if args.src != "src" else layers.get("src", "src")
        new = [v for v in layer_violations(root / src, package, rules) if v not in accepted]
        print("\n".join(f"layer: {v}" for v in new) if new else f"layers: no new violation ({args.layers or 'code map'})")
        rc = rc or (1 if new else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/language_split.py
````python
"""Keep each language override small: report language files over budget, and split one into a folder of topic files.

Run: python3 scripts/language_split.py [--check] [--lang <name> --apply]   (just language-split ...)
Read-only by default: prints each languages/*.md (and languages/<lang>/*.md) with its lines and bytes against the budget (200 lines, 25 KB:
an agent loads a language file whole). --check exits 1 when any is over. --lang <name> --apply splits languages/<name>.md: the entry file keeps
its front matter, Contents, Authoritative sources, Tools, Core rule mapping and Size tweaks, plus an index of topic files; every other H2
section moves to languages/<name>/<section-slug>.md, and each `> **Learned` block goes to the topic file named in languages/<name>/topics.toml
(`[topics] <file-stem> = ["keyword", ...]`, first match wins; unmatched blocks to learned-other.md). The split writes only when the words of
the result equal the words of the original (index lines aside); otherwise it changes nothing. Operator rule 2026-11-07.
Exit: 0 ok or split; 1 over budget (--check) or the word check failed; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

REQUIRES_PYTHON = (3, 11)

LANGS = Path(__file__).resolve().parents[1] / "languages"
BUDGET_LINES, BUDGET_BYTES = 200, 25 * 1024
KEEP = ("contents", "authoritative sources", "tools", "core rule mapping", "size and limit tweaks")


def slug(title: str) -> str:
  """A file stem from a heading.

  Args:
    title: the heading text.

  Returns:
    Lower-case words joined by hyphens.
  """
  return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def over(path: Path) -> str:
  """Why a file is over budget, or "".

  Args:
    path: the markdown file.

  Returns:
    The reason, or "" within budget.
  """
  text = path.read_text(encoding="utf-8")
  n, b = text.count("\n"), len(text.encode())
  return f"{n} lines, {b // 1024} KB (budget {BUDGET_LINES} lines, {BUDGET_BYTES // 1024} KB)" if n > BUDGET_LINES or b > BUDGET_BYTES else ""


def sections(text: str) -> tuple[str, list[tuple[str, str]]]:
  """Split a file into its head (front matter and title) and its H2 sections.

  Args:
    text: the file.

  Returns:
    (head, [(title, body including the heading line)]).
  """
  parts = re.split(r"(?m)^(?=## )", text)
  return parts[0], [(p.splitlines()[0][3:].strip(), p) for p in parts[1:]]


def blocks(body: str) -> list[str]:
  """Split a section body into paragraphs, a `>` quote run counting as one block.

  Args:
    body: the section text without its heading.

  Returns:
    The blocks, each ending in a newline.
  """
  out, cur, quote = [], [], None
  for line in body.splitlines(keepends=True):
    is_q = line.startswith(">")
    if line.strip() == "" or (cur and quote is not None and is_q != quote):
      if cur:
        out.append("".join(cur))
      cur, quote = ([], None) if line.strip() == "" else ([line], is_q)
      continue
    cur.append(line)
    quote = is_q if quote is None else quote
  if cur:
    out.append("".join(cur))
  return out


def front(lang: str, stem: str) -> str:
  """The front matter of a topic file.

  Args:
    lang: the language stem.
    stem: the topic file stem.

  Returns:
    The fenced front matter block.
  """
  return (f"---\nTitle: {lang} override - {stem.replace('-', ' ')}\nCategory: reference\nStatus: current\nAuthority: local-supplement\n"
          f"Scope: one topic of languages/{lang}.md (split by scripts/language_split.py)\nLast reviewed: 2026-11-07\n"
          f"Summary: The {stem.replace('-', ' ')} part of the {lang} override; the entry file holds the tools and the core rule mapping.\n---\n\n")


def words(text: str) -> Counter:
  """The multiset of words, for the before-and-after check.

  Args:
    text: any text.

  Returns:
    A Counter of word tokens.
  """
  return Counter(re.findall(r"[A-Za-z0-9_]+", text))


def split(lang: str, apply: bool) -> int:
  """Split one language file into an entry file and a folder of topic files.

  Args:
    lang: the file stem under languages/.
    apply: write the result (after the word check).

  Returns:
    0 split or planned; 1 the word check failed; 2 no such file.
  """
  src = LANGS / f"{lang}.md"
  if not src.is_file():
    print(f"no {src}")
    return 2
  topics_file = LANGS / lang / "topics.toml"
  topics = tomllib.loads(topics_file.read_text(encoding="utf-8")).get("topics", {}) if topics_file.is_file() else {}
  original = src.read_text(encoding="utf-8")
  head, secs = sections(original)
  entry, files = [head], {}
  for title, body in secs:
    if title.lower() in KEEP:
      entry.append(body)
      continue
    heading, rest = body.split("\n", 1) if "\n" in body else (body, "")
    for blk in blocks(rest):
      if blk.startswith("> **Learned"):
        low = blk.lower()
        stem = next((t for t, kws in topics.items() if any(k.lower() in low for k in kws)), "learned-other")
      else:
        stem = slug(title)
      files.setdefault(stem, []).append(blk)
  index = ["## Topic files\n\n", f"The rest of this override lives in [{lang}/]({lang}/) (split 2026-11-07 by scripts/language_split.py: one topic per file).\n\n",
           "| File | Blocks |\n| --- | --- |\n"] + [f"| [{s}.md]({lang}/{s}.md) | {len(b)} |\n" for s, b in sorted(files.items())]
  kept = [t for t, _ in secs if t.lower() in KEEP and t.lower() != "contents"] + ["Topic files"]
  toc = "## Contents\n\n" + "".join(f"- [{t}](#{slug(t)})\n" for t in kept) + "\n"
  entry = [toc if e.startswith("## Contents") else e for e in entry]
  new_entry = "".join(entry).rstrip("\n") + "\n\n" + "".join(index)
  outs = {LANGS / lang / f"{s}.md": front(lang, s) + f"# {lang}: {s.replace('-', ' ')}\n\nPart of [{lang}.md](../{lang}.md).\n\n" + "\n".join(b)
          for s, b in files.items()}
  dropped = "".join(f"## {t}\n" for t, _ in secs if t.lower() not in KEEP) + "".join(b for t, b in secs if t.lower() == "contents")
  lost = words(original) - words(new_entry + "".join(outs.values())) - words(dropped)
  if lost:
    print(f"word check failed: {sum(lost.values())} words would be lost, e.g. {list(lost)[:5]}; nothing written")
    return 1
  for path, text in outs.items():
    print(f"{'write' if apply else 'plan: write'} {path.relative_to(LANGS.parent)} ({text.count(chr(10))} lines)")
  print(f"{'rewrite' if apply else 'plan: rewrite'} {src.relative_to(LANGS.parent)} ({new_entry.count(chr(10))} lines, was {original.count(chr(10))})")
  if apply:
    (LANGS / lang).mkdir(exist_ok=True)
    for path, text in outs.items():
      path.write_text(text, encoding="utf-8")
    src.write_text(new_entry, encoding="utf-8")
  return 0


def main() -> int:
  """Report, check or split.

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--check", action="store_true", help="exit 1 when any language file is over budget")
  ap.add_argument("--lang", help="the language file to split")
  ap.add_argument("--apply", action="store_true", help="with --lang: write the split")
  args = ap.parse_args()
  if args.lang:
    return split(args.lang, args.apply)
  bad = 0
  for path in sorted(LANGS.glob("*.md")) + sorted(LANGS.glob("*/*.md")):
    why = over(path)
    bad += bool(why)
    if why or not args.check:
      print(f"{'OVER' if why else 'ok  '} {path.relative_to(LANGS.parent)}{': ' + why + ' (split it: --lang <name> --apply)' if why else ''}")
  return 1 if bad and args.check else 0


if __name__ == "__main__":
  sys.exit(main())
````

## File: scripts/module_groups.py
````python
#!/usr/bin/env python3
"""Report folders where three or more code files share a name prefix: a module family that wants to be a package. Read-only, warn only. Stdlib only.

Why (operator, 2026-10-19: "when modularising a large piece of code, is it better to create a subdirectory under scripts and put all the related
modules under that relevant folder with a proper name? If so, then make it part of the skill coder logic"): a shared prefix (`flowmap_model.py`,
`flowmap_overview.py`, `flowmap_pages.py`) is a folder trying to exist. The rule and its exceptions are in references/module-and-function-shape.md,
"Grouping modules into packages". This helper finds the candidates; whether to move them is a judgement (a refactor), so it never fails by default.

A prefix is the file name up to its first `_` or `-`. Test files (`test_`) and the files a language names by convention are not grouped.

Usage:
    module_groups.py --project-root . [--roots scripts,src] [--min 3] [--strict]
Exit: 0 (warn only); with --strict 1 when a candidate exists; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: Code file suffixes grouped.
CODE_SUFFIXES = (".py", ".sh", ".bash", ".js", ".mjs", ".ts", ".go", ".rs")
#: Prefixes never grouped: test files are named by the test runner's convention, not by feature.
EXEMPT_PREFIXES = ("test", "conftest")
#: Folders never walked.
SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".venv", "venv", "fixtures"}
PREFIX = re.compile(r"^([A-Za-z0-9]+)[_-].+")


def prefix_of(name: str) -> str | None:
    """A code file's family prefix.

    Args:
        name: the file name.

    Returns:
        The text before the first `_` or `-` of a code file's stem, or None for a non-code file, a one-word name or an exempt prefix.
    """
    path = Path(name)
    if path.suffix not in CODE_SUFFIXES:
        return None
    m = PREFIX.match(path.stem)
    if not m or m.group(1).lower() in EXEMPT_PREFIXES:
        return None
    return m.group(1)


def candidates(root: Path, roots: list[str], least: int = 3) -> list[tuple[str, str, list[str]]]:
    """Every folder under the roots with `least` or more code files sharing a prefix.

    Args:
        root: the project root.
        roots: folders under it to walk.
        least: the smallest family reported.

    Returns:
        (folder relative to root, prefix, file names) per family, sorted by folder then prefix.
    """
    out = []
    for folder in roots:
        base = root / folder
        dirs = [base, *sorted(p for p in base.rglob("*") if p.is_dir())] if base.is_dir() else []
        for d in dirs:
            if any(part in SKIP_DIRS or part.startswith(".") for part in d.relative_to(root).parts):
                continue
            families: dict[str, list[str]] = {}
            for f in sorted(p for p in d.iterdir() if p.is_file()):
                if (pre := prefix_of(f.name)) is not None:
                    families.setdefault(pre, []).append(f.name)
            for pre, names in sorted(families.items()):
                if len(names) >= least:
                    out.append((d.relative_to(root).as_posix(), pre, names))
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 (warn only), or 1 with --strict when a candidate exists; 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else scripts,src)")
    ap.add_argument("--min", type=int, default=3, help="the smallest family reported (default 3)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a candidate exists")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        wanted = args.roots or code_map.scan_roots(code_map.for_root(root, args.code_map), default="scripts,src")
    except (OSError, ValueError) as exc:
        print(f"module_groups: {exc}", file=sys.stderr)
        return 2
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots or args.min < 2:
        print(f"module_groups: no folder of {wanted} under {root}, or --min below 2", file=sys.stderr)
        return 2
    found = candidates(root, roots, args.min)
    for folder, pre, names in found:
        print(f"{folder}: {len(names)} files share `{pre}`: {', '.join(names)}; candidate package {folder}/{pre}/")
    print(f"module_groups: {len(found)} candidate famil{'y' if len(found) == 1 else 'ies'} (references/module-and-function-shape.md, "
          "'Grouping modules into packages')")
    return 1 if (args.strict and found) else 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/naming_check.py
````python
#!/usr/bin/env python3
"""Check a project's code file names and task-runner recipe names against skill-coder's naming mapping, as a shrink-only ratchet. Read-only
unless --write-baseline. Stdlib only.

Why (operator, 2026-10-19: "define a mapping for language against convention"; "is it better to have a json or yaml or toml file for the mapping"):
the mapping lives as data in the pack's `naming.toml` (TOML, so this runs with the project's own Python), and this checks what can be seen without
parsing code: file names by language, and `just` recipe names. Names inside code (functions, variables, classes) are the language linter's job; each
such row in the mapping names the tool.

A project overrides the mapping in its `code-map.toml`:
    [naming]
    recipe = "snake_case"                  # this project's recipes keep underscores
    [naming.files]
    "*.js" = "kebab-case"                  # this project's JavaScript files
keeps a name with a reason in `[naming.exceptions]` ("recipe nav_upgrade" = "owned by skill-ai-it's template"), and leaves files out with
`[scan.exclude]`. Python dunder files (`__init__.py`, `__main__.py`) and private recipes (a leading `_`) are judged without
their underscores. Existing names that break the rule go in the baseline and are renamed when next touched.

Usage:
    naming_check.py --project-root . [--roots src,scripts] [--baseline scripts/naming-baseline.json] [--list] [--write-baseline]
Exit: 0 when nothing new breaks the mapping and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import tomllib
from pathlib import Path

import code_map
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: The pack's mapping (the source of truth; references/naming-conventions.md's table is rendered from it).
MAPPING = Path(__file__).resolve().parent.parent / "naming.toml"
CHECKS = ("file", "recipe", "linter")
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "vendor", "dist", "build"}
#: A recipe header: a name at the start of a line, optional parameters (which may hold `="default"`), then a colon that is not `:=`.
RECIPE = re.compile(r"^(@?)([A-Za-z_][\w-]*)\s*(?:[*+$A-Za-z_].*?)?:(?!=)", re.M)


def load_mapping(path: Path = MAPPING) -> dict:
    """Read and check the naming mapping.

    Args:
        path: the TOML file.

    Returns:
        {"conventions": {name: regex}, "rule": [rule, ...]}.

    Raises:
        ValueError: when a rule has an unknown check, or a file or recipe rule names a convention with no regex or has no globs.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    conventions, problems = data.get("conventions", {}), []
    for i, rule in enumerate(data.get("rule", [])):
        where = f"rule {i + 1} ({rule.get('language')}, {rule.get('element')})"
        if rule.get("check") not in CHECKS:
            problems.append(f"{where}: check must be one of {', '.join(CHECKS)}")
        elif rule["check"] in ("file", "recipe") and rule.get("convention") not in conventions:
            problems.append(f"{where}: a checked rule needs a convention with a regex in [conventions]")
        elif rule["check"] == "file" and not rule.get("globs"):
            problems.append(f"{where}: a file rule needs globs")
        elif rule["check"] == "linter" and not rule.get("tool"):
            problems.append(f"{where}: a linter rule names the tool that checks it")
    if problems:
        raise ValueError(f"{path.name}: " + "; ".join(problems))
    return data


def _stem(name: str) -> str:
    """A file or recipe name as judged: suffix removed, dunder and private underscores stripped.

    Args:
        name: the file name or recipe name.

    Returns:
        The part the convention applies to.
    """
    stem = name.split(".", 1)[0] if "." in name else name
    return stem.strip("_")


def file_findings(root: Path, roots: list[str], mapping: dict, overrides: dict, exclude: set[str]) -> dict[str, str]:
    """Code files whose names break their language's convention.

    Args:
        root: the project root.
        roots: folders to scan.
        mapping: load_mapping()'s result.
        overrides: {glob: convention} from the project's [naming.files].
        exclude: repo-relative files never checked ([scan.exclude]).

    Returns:
        {"file <path>": "<convention> (<language>)"} per breaking file.
    """
    regex = {k: re.compile(v) for k, v in mapping["conventions"].items()}
    rules = [(g, r["convention"], r["language"], tuple(r.get("exclude_globs", ()))) for r in mapping["rule"] if r["check"] == "file" for g in r["globs"]]
    rules = [(g, overrides.get(g, conv), lang, ex) for g, conv, lang, ex in rules] + [(g, c, "project", ()) for g, c in overrides.items()
                                                                                       if g not in {r[0] for r in rules}]
    out: dict[str, str] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")) if (root / folder).is_dir() else []:
            rel = path.relative_to(root).as_posix()
            if not path.is_file() or rel in exclude or SKIP_PARTS & set(path.parts):
                continue
            for glob, conv, lang, ex in rules:
                if fnmatch.fnmatch(path.name, glob) and not any(fnmatch.fnmatch(rel, e) for e in ex):
                    if conv not in regex:
                        raise ValueError(f"[naming.files] {glob}: unknown convention {conv}")
                    if not regex[conv].match(_stem(path.name)):
                        out[f"file {rel}"] = f"{conv} ({lang})"
                    break
    return out


def recipe_findings(root: Path, mapping: dict, convention: str | None) -> dict[str, str]:
    """`just` recipes whose names break the recipe convention.

    Args:
        root: the project root (its justfile is read).
        mapping: load_mapping()'s result.
        convention: the project's [naming] recipe override, or None for the mapping's.

    Returns:
        {"recipe <name>": "<convention>"} per breaking recipe.

    Raises:
        ValueError: when the convention has no regex.
    """
    runner = next((root / n for n in ("justfile", "Justfile", ".justfile") if (root / n).is_file()), None)
    if runner is None:
        return {}
    conv = convention or next(r["convention"] for r in mapping["rule"] if r["check"] == "recipe")
    if conv not in mapping["conventions"]:
        raise ValueError(f"[naming] recipe: unknown convention {conv}")
    pattern = re.compile(mapping["conventions"][conv])
    names = {m.group(2) for m in RECIPE.finditer(runner.read_text(encoding="utf-8")) if m.group(2) not in ("set", "export", "import", "mod", "alias")}
    return {f"recipe {n}": conv for n in sorted(names) if not pattern.match(_stem(n))}


def exceptions(naming: dict) -> dict[str, str]:
    """Names a project keeps although they break the mapping, each with its reason (for example recipes owned by another skill's template).

    Args:
        naming: the code map's [naming] section.

    Returns:
        {"file <path>" or "recipe <name>": reason}.

    Raises:
        ValueError: when an entry has no reason.
    """
    out = dict(naming.get("exceptions", {}))
    if blank := [k for k, v in out.items() if not str(v).strip()]:
        raise ValueError(f"[naming.exceptions] entries need a reason: {', '.join(blank)}")
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", default="scripts/naming-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every name that breaks the mapping")
    ap.add_argument("--write-baseline", action="store_true", help="record today's names (adoption or after renames)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap, mapping = code_map.for_root(root, args.code_map), load_mapping()
        naming = code_map.section(cmap, "naming")
        roots = [r for r in (args.roots or code_map.scan_roots(cmap)).split(",") if r]
        kept = exceptions(naming)
        found = {**file_findings(root, roots, mapping, dict(naming.get("files", {})), set(code_map.excluded(cmap))),
                 **recipe_findings(root, mapping, naming.get("recipe"))}
        stale = sorted(k for k in kept if k not in found)
        found = {k: v for k, v in found.items() if k not in kept}
    except (OSError, ValueError) as exc:
        print(f"naming_check: {exc}", file=sys.stderr)
        return 2
    if args.list:
        print("\n".join(f"{key}: expected {conv}" for key, conv in found.items()))
    base_path = root / args.baseline
    counts = {key: 1 for key in found}
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"naming_check: baseline written, {len(counts)} name(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    lines = ratchet.report(verdict, "naming", base_path) + [f"STALE naming: exception {k} no longer breaks the mapping (or is gone): remove it" for k in stale]
    print("\n".join(lines) or f"naming_check: OK, {len(counts)} name(s) off the mapping in the baseline, {len(kept)} kept by exception")
    return 0 if verdict.ok and not stale else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/naming_table.py
````python
#!/usr/bin/env python3
"""Render the naming table in references/naming-conventions.md from the pack's naming.toml, or report when the table is out of step. Writes only
the table between its markers, and only with --write. Stdlib only.

Why (operator, 2026-10-19): the mapping is data first, like a flow map; the reference shows it to readers and must never drift from what
naming_check.py enforces, so the table is generated, never edited by hand.

Usage:
    naming_table.py            # exit 1 when the table differs from what naming.toml renders
    naming_table.py --write    # rewrite the table between the markers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import naming_check

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
PACK = Path(__file__).resolve().parent.parent
REFERENCE = PACK / "references" / "naming-conventions.md"
BEGIN = "<!-- BEGIN GENERATED: naming table (scripts/naming_table.py from naming.toml; do not edit) -->"
END = "<!-- END GENERATED: naming table -->"
HEAD = ("Language", "Element", "Convention", "Checked by", "Source (capture)")


def render(mapping: dict) -> str:
    """The table, one row per rule, columns padded so the raw markdown reads as a table.

    Args:
        mapping: naming_check.load_mapping()'s result.

    Returns:
        The markdown table, newline-terminated.
    """
    rows = []
    for r in mapping["rule"]:
        checked = {"file": "`naming_check.py` (file names)", "recipe": "`naming_check.py` (recipes)"}.get(r["check"], r.get("tool", ""))
        source = r["source"] + (f" (`{r['capture']}`)" if r.get("capture") else "")
        rows.append((r["language"], r["element"], r["convention"], checked, source))
    width = [max(len(x[i]) for x in [HEAD, *rows]) for i in range(len(HEAD))]
    return "\n".join(_row(cells, width) for cells in [HEAD, tuple("-" * w for w in width), *rows]) + "\n"


def _row(cells: tuple, width: list[int]) -> str:
    """One table row, each cell padded to its column's width.

    Args:
        cells: the row's cells.
        width: each column's width.

    Returns:
        The markdown row.
    """
    return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, width)) + " |"


def splice(text: str, table: str) -> str:
    """The reference with the table between the markers replaced.

    Args:
        text: the reference's text.
        table: render()'s output.

    Returns:
        The new text.

    Raises:
        ValueError: when the markers are missing.
    """
    if BEGIN not in text or END not in text:
        raise ValueError(f"{REFERENCE.name} lacks the generated-table markers")
    head, rest = text.split(BEGIN, 1)
    return f"{head}{BEGIN}\n\n{table}\n{END}{rest.split(END, 1)[1]}"


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when current (or written), 1 on drift, 2 on a bad mapping or missing markers.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="rewrite the table")
    args = ap.parse_args(argv)
    try:
        current = REFERENCE.read_text(encoding="utf-8")
        wanted = splice(current, render(naming_check.load_mapping()))
    except (OSError, ValueError) as exc:
        print(f"naming_table: {exc}", file=sys.stderr)
        return 2
    if args.write:
        REFERENCE.write_text(wanted, encoding="utf-8")
        print(f"naming_table: wrote {REFERENCE.relative_to(PACK)}")
        return 0
    if wanted != current:
        print(f"naming_table: {REFERENCE.relative_to(PACK)} is out of step with naming.toml; run `just naming-table`")
        return 1
    print("naming_table: OK, the table matches naming.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/process_match.py
````python
#!/usr/bin/env python3
"""Find `pgrep -f` / `pkill -f` patterns that are not anchored with `^`, which can match the automation's own command line. Read-only. Stdlib only.

Why (references/safety-and-writes.md, Learned 2026-10-26 and 2026-10-28): `-f` matches whole command lines, and the pattern's text keeps turning
up in other command lines: a shell script's own text is its `sh -c` line, Ansible `environment:` values sit on the remote command line, a
cron job's shell carries the job. An unanchored wait then waits on itself and a pkill ends its own session. Recurred four times in one
project (ansible-wifi smc_change, 2026-10-26 to 2026-10-28) although the rule was already written down, so it is now a check. Anchor at the
real program instead (`pgrep -f '^php artisan update:stats'`): a shell line starts with /bin/sh and cannot match.

Only literal quoted patterns are read; a pattern built at run time (`pgrep -f "$p"`) is not judged. Markdown is not scanned (docs show the
wrong form on purpose), and a call after a `#` on its line is a comment and is skipped.

Usage:
    process_match.py --project-root . [--roots roles,scripts] [--list]
Exit: 0 when every literal pattern is anchored, 1 when one is not, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: A pgrep or pkill call with an -f flag (alone or combined, e.g. -fc, -af) followed by a quoted literal pattern.
CALL = re.compile(r"""\b(?P<tool>pgrep|pkill)\b(?:\s+-\w+)*?\s+-[A-Za-z]*f[A-Za-z]*(?:\s+-\w+)*\s+(?P<q>['"])(?P<pat>[^'"\n]*)(?P=q)""")

SUFFIXES = {".sh", ".bash", ".yml", ".yaml", ".py", ".j2", ".service", ".timer", ".cron"}
SKIP_PARTS = {".venv", "venv", "node_modules", "__pycache__", ".git", "target", "dist", "build"}


def unanchored(text: str) -> list[tuple[int, str, str]]:
    """Unanchored pgrep/pkill -f patterns in a file's text.

    Args:
        text: the file's text.

    Returns:
        (line, tool, pattern) per pattern that does not start with ^.
    """
    out: list[tuple[int, str, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        hash_at = line.find("#")
        for m in CALL.finditer(line):
            if 0 <= hash_at < m.start():
                continue  # a shell or YAML comment: never executed
            pat = m.group("pat")
            if pat.startswith(("$", "{{")):
                continue  # built at run time (shell variable or Jinja): its text is not known here
            if not pat.startswith("^"):
                out.append((n, m.group("tool"), m.group("pat")))
    return out


def scan(root: Path, roots: list[str]) -> dict[str, list[tuple[int, str, str]]]:
    """Findings per file under the roots.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        {relative path: [(line, tool, pattern)]} for files with any.
    """
    found: dict[str, list[tuple[int, str, str]]] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES or SKIP_PARTS & set(path.parts):
                continue
            hits = unanchored(path.read_text(encoding="utf-8", errors="replace"))
            if hits:
                found[path.relative_to(root).as_posix()] = hits
    return found


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when every literal pattern is anchored, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [process_match] or [scan] roots, else src,scripts)")
    ap.add_argument("--list", action="store_true", help="print every finding (the default prints them too; kept for symmetry)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"process_match: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "process_match")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"process_match: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    found = scan(root, roots)
    for rel, hits in found.items():
        for line, tool, pat in hits:
            print(f"{rel}:{line}: {tool} -f '{pat}' is not anchored with ^; anchor it at the program's own command line (e.g. '^php artisan ...')")
    total = sum(len(h) for h in found.values())
    print(f"process_match: {'OK, every literal pgrep/pkill -f pattern is anchored' if not total else f'{total} unanchored pattern(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/pyparse.py
````python
#!/usr/bin/env python3
"""Parse Python source the way every helper in this pack does: at the target project's grammar, with the parser's own warnings silenced.
Imported, not run; reads nothing. Stdlib only.

Why: the helpers parse other projects' code as data. `ast.parse` prints a SyntaxWarning for things like an invalid escape sequence in a
non-raw string; those are the project's linter's business, and printed here they bury the helper's own findings (first seen on a 1,125-file
Ansible repository, 2026-10-19). A file that does not parse at all still raises, so the caller reports it.
"""

from __future__ import annotations

import ast
import warnings

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


def parse(text: str, grammar: tuple[int, int] | None = None) -> ast.Module:
    """Parse source quietly.

    Args:
        text: the source.
        grammar: (major, minor) for ast's feature_version (the project's Python), or None for this interpreter's grammar.

    Returns:
        The module's AST.

    Raises:
        SyntaxError: when the source does not parse at that grammar.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(text, feature_version=grammar)
````

## File: scripts/ratchet.py
````python
#!/usr/bin/env python3
"""A shrink-only baseline for code-quality counts: old code may carry findings it was adopted with, new findings fail, and a fixed one must be
recorded so it cannot come back. Stdlib only.

Why: a rule adopted on an existing code base (a size limit, a docstring standard, a timeout on every call) cannot be met in one change. The
operator's pattern in unified-network-controller (docstring baseline, import-layer baseline, R34 code size, 2026-10-08 to 2026-10-13) is a
baseline file that only tightens. Every checker in this pack uses this module for it.

Baseline file: JSON {key: number}. A key is whatever the checker counts per (a file path, or `path::function`).

Imported, not run: `from ratchet import compare, load, save`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


@dataclass
class Verdict:
    """What compare() found.

    Args:
        regressions: keys over their allowance, as "key: found N, allowed M".
        improved: keys now under their allowance, as "key: found N, baseline M" (record them with save()).
        gone: baseline keys no longer present (record with save()).
    """

    regressions: list[str] = field(default_factory=list)
    improved: list[str] = field(default_factory=list)
    gone: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when nothing regressed and the baseline is current.

        Returns:
            Whether the check passes.
        """
        return not (self.regressions or self.improved or self.gone)


def load(path: Path) -> dict[str, float]:
    """Read a baseline; a missing file is an empty baseline (every finding is new).

    Args:
        path: the baseline JSON file.

    Returns:
        {key: allowed value}.

    Raises:
        ValueError: when the file is not a JSON object of numbers.
    """
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(v, (int, float)) for v in data.values()):
        raise ValueError(f"{path}: a baseline is a JSON object of numbers")
    return data


def compare(found: dict[str, float], baseline: dict[str, float]) -> Verdict:
    """Hold today's counts to the baseline.

    Args:
        found: {key: value} measured now (only keys over the limit, or with a non-zero count).
        baseline: {key: allowed value}; a key not in it is allowed 0.

    Returns:
        The verdict.
    """
    out = Verdict()
    for key in sorted(found):
        allowed = baseline.get(key, 0)
        if found[key] > allowed:
            out.regressions.append(f"{key}: found {found[key]:g}, allowed {allowed:g}")
        elif found[key] < allowed:
            out.improved.append(f"{key}: found {found[key]:g}, baseline {allowed:g}")
    out.gone = sorted(k for k in baseline if k not in found)
    return out


def save(path: Path, found: dict[str, float]) -> None:
    """Write today's counts as the baseline (on adoption, or after an improvement), sorted so the diff is readable.

    Args:
        path: the baseline JSON file.
        found: {key: value}.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(found.items())), indent=1) + "\n", encoding="utf-8")


def report(verdict: Verdict, what: str, baseline_path: Path) -> list[str]:
    """Human-readable lines for a verdict.

    Args:
        verdict: compare()'s result.
        what: what is counted, for the messages ("module lines").
        baseline_path: the baseline file, named in the fix hint.

    Returns:
        One line per finding, each saying what to do.
    """
    lines = [f"FAIL {what}: {r} — fix the code (a baseline is only for code adopted with the finding)" for r in verdict.regressions]
    lines += [f"STALE {what}: {r} — record the improvement: rerun with --write-baseline ({baseline_path})" for r in verdict.improved]
    lines += [f"STALE {what}: {k} is in the baseline but no longer found — rerun with --write-baseline" for k in verdict.gone]
    return lines
````

## File: scripts/README.md
````markdown
# Script Inventory

skill-coder's helpers: stdlib-only checkers that hold any project's code to the pack's rules, plus the pack's own governance checker.

## Contents

- [How to run a helper against a project](#how-to-run-a-helper-against-a-project)
- [Runtimes](#runtimes)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Baselines and the code map](#baselines-and-the-code-map)
- [Safety Labels](#safety-labels)

---

## How to run a helper against a project

Default: run it with the **target project's own pinned interpreter**, by path, from the project root. The helpers are stdlib-only, need Python 3.11 or
newer (`REQUIRES_PYTHON` in each file) and only read files, so nothing is installed into the project:

```bash
<project venv>/bin/python /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-coder/scripts/code_size.py --project-root . --list
```

Fallback, only when the project has no Python 3.11+: run the same helper with this pack's interpreter through its recipe, pointing at the project:
`just -f <this pack>/justfile code-size --project-root /path/to/project`. Each helper reads its settings from the project's `code-map.toml` when
one is at the project root (template: `templates/code-map.toml`); command-line flags win over the map.

## Runtimes

| Runtime | Resolved by                                                                | Actual                                                              |
| ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml`    | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-coder/.venv` |

`just runtimes` prints what the recipes use; `just bootstrap` rebuilds the venv (safe to re-run). The venv is only for this pack's own recipes and
tests (it adds PyYAML for the contract test); the helpers need nothing from it. `just test-matrix` runs the helper tests under every Python from 3.11
that mise has installed. Do not invoke the pack's recipes through a bare `python3`.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

## Task Inventory

| Task                  | Purpose                                                                   | Inputs                         | Outputs                | Safety            | Idempotent | When to use                                |
| --------------------- | ------------------------------------------------------------------------- | ------------------------------ | ---------------------- | ----------------- | ---------- | ------------------------------------------ |
| `just test`           | Contract and helper tests                                                 | `tests/`, pack files           | Console, exit status   | `safe`            | Yes        | Before calling any change complete         |
| `just test-matrix`    | Helper tests under each installed Python from 3.11                        | `tests/test_helpers.py`        | One line per version   | `safe`            | Yes        | After changing a helper                    |
| `just self-check`     | The pack held to its own rules (size, timeouts, groups, suppressions, write gates, headers) | `scripts/`, `tests/`, baselines | Console, exit status  | `safe`            | Yes        | Part of `just check`                       |
| `just check`          | Governance coherence, doc freshness, roles, then `self-check`             | Governance surfaces            | Console, exit status   | `safe`            | Yes        | Before claiming durable work complete      |
| `just code-size`      | `scripts/code_size.py` against a project (fallback runtime)               | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | Project lacks Python 3.11+                 |
| `just call-timeouts`  | `scripts/call_timeouts.py` against a project (fallback runtime)           | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just suppressions`   | `scripts/suppressions.py` against a project (fallback runtime)            | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just group-timeouts` | `scripts/group_timeouts.py` against a project (fallback runtime)          | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just process-match`  | `scripts/process_match.py` against a project (fallback runtime)           | `--project-root`, `--roots`    | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just reflow-lossless` | `scripts/reflow_lossless.py`: prove a re-wrapped markdown file changed no cell and no word | `BEFORE AFTER` or `--git FILE`, `--table-reflow`, `--ignore-contents` | Verdict, exit status | `safe` | Yes | After a formatter hook re-wraps a file |
| `just cpuprofile-summary` | `scripts/cpuprofile_summary.py`: .cpuprofile files to self time per extension, hot functions, stacks | Profile paths, `--ext`, `--top` | Console, exit status | `safe` | Yes | VS Code (or Node) stalls: extension host pinned |
| `just scaffold`       | `scripts/scaffold.py`: prints a new script's and its test's skeleton       | `--lang`, `--name`, `--summary` | Console               | `safe`            | Yes        | Starting a new script                      |
| `just write-gates`    | `scripts/write_gates.py` against a project (fallback runtime)             | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just import-layers`  | `scripts/import_layers.py` against a project (fallback runtime)           | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just script-headers` | `scripts/script_headers.py` against a project (fallback runtime)          | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just naming-check`  | `scripts/naming_check.py` against a project (fallback runtime)            | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just module-groups` | `scripts/module_groups.py` against a project (fallback runtime)           | `--project-root`, code map     | Candidates (warn only) | `safe`            | Yes        | Modularising code; reviews                 |
| `just write-back`    | `scripts/write_back.py`: entries a project holds for this skill, to promote | `--project-root`, `--skill`    | Pending entries        | `safe`            | Yes        | Every slurp; before closing an engagement  |
| `just naming-table`  | Re-renders the naming table from `naming.toml`                            | `naming.toml`                  | The reference's table  | `modifies-files`  | Yes        | After editing `naming.toml`                |
| `just helpers`        | Lists the helper files                                                    | `scripts/`                     | Console                | `safe`            | Yes        | Orientation                                |
| `just context-pack`   | Regenerates `.ai-context/governance-pack.md` (support only)               | `repomix.config.json`          | `.ai-context/`         | `modifies-files`  | Yes        | After large changes                        |
| `just bootstrap`      | Builds the pack's working-cache venv from the mise pin                    | `.mise.toml`, requirements     | venv outside the repo  | `modifies-files`  | Yes        | First use, or after a pin change           |
| `just inventory`      | Lists tasks and this inventory                                            | `justfile`, this file          | Console                | `safe`            | Yes        | First check before running automation      |
| `just audit-scripts`  | Script/catalog drift                                                      | `scripts/`, this file          | Console                | `safe`            | Yes        | During refresh or audit                    |
| `just preflight`      | runtimes, audit-scripts, test, self-check, check, lint-md                 | Pack files                     | Console                | `safe`            | Yes        | Before commit or handoff                   |
| `just nav-upgrade-dry-run` / `just nav-upgrade` / `just nav-validate` / `just nav-check-diff` | skill-ai-it navigation layer upgrade and validation | skill-ai-it scripts | Console, file changes on upgrade | `review-required` (upgrade) | Yes | When skill-ai-it's blocks change |

## Raw Script Inventory

| Script                       | Purpose                                                                                     | Inputs                                  | Outputs                          | Safety                       | Idempotent | When to use                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------- | ---------------------------- | ---------- | --------------------------------------------- |
| `scripts/code_size.py`       | Module and function size limits, warn and fail tiers, per language, shrink-only baseline     | Source files, code map, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check; adopting the size rule           |
| `scripts/call_timeouts.py`   | Python network and subprocess calls without a timeout, shrink-only baseline                  | Python files, code map, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check                                   |
| `scripts/suppressions.py`    | Inline linter suppressions per language (`noqa`, `type: ignore`, `shellcheck disable`, `eslint-disable`, `@ts-ignore`, `nolint`, Rust `allow`), shrink-only baseline | Code files, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/group_timeouts.py`  | Timed `subprocess.run`-family calls whose command (ssh, scp, rsync, a shell, `shell=True`) starts children the timeout leaves running, shrink-only baseline | Python files, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/process_match.py`  | `pgrep -f` / `pkill -f` literal patterns not anchored with `^`, which can match the automation's own command line (shell, YAML, Python, Jinja; comments and run-time patterns skipped) | Code files, code map | Findings, exit status | `safe` | Yes | Every check of shell or Ansible code |
| `scripts/reflow_lossless.py` | Whether two versions of a markdown file differ only in line breaks: tables un-wrapped by table-reflow and compared row by row and cell by cell, prose word by word; exit 2 when tables cannot be proven | Two files, or one file against HEAD; table-reflow's `cli.mjs` | `lossless` or the differing spans and rows, exit status | `safe` | Yes | Before committing or reverting a whole-file reflow |
| `scripts/language_split.py` | Language override files over budget (200 lines, 25 KB); `--lang <name> --apply` splits one into `languages/<name>/` topic files routed by its `languages/ansible/topics.toml`-style keyword map, with a word-for-word check |
| `scripts/cpuprofile_summary.py` | V8 .cpuprofile (VS Code extension host, Node, Chrome) reduced to self time per extension, hottest functions and the studied extension's hottest stacks | Profile files, `--ext`, `--top` | Console, exit status | `safe` | Yes | An extension host or Node process stalls and a profile was saved |
| `scripts/scaffold.py`        | Prints the skeleton of a new Python or shell script and its test, meeting this pack's rules; writes nothing | `--lang`, `--name`, `--summary`, `--writes` | Console | `safe` | Yes | Starting a new script |
| `scripts/write_gates.py`     | Entry points that write without `--apply`, and stale register entries                        | Source files, code map or JSON config   | Findings                         | `safe`                       | Yes        | Every check                                   |
| `scripts/import_layers.py`   | Python import layer rules, cycles and a package import graph (`--json`; a root ending `:self` keeps its folder name) | Python files, code map or layers TOML   | Findings or a graph report       | `safe`                       | Yes        | Every check; structure reviews                |
| `scripts/script_headers.py`  | Runnable scripts whose native header lacks a summary, a run line or a safety statement       | Python and shell files, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check                                   |
| `scripts/naming_check.py`   | Code file names and `just` recipe names against `naming.toml` and the project's `[naming]` overrides, shrink-only baseline | Files, justfile, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/naming_table.py`   | Renders the naming table in `references/naming-conventions.md` from `naming.toml`; reports drift | `naming.toml` | The table (with `--write`) | `modifies-files` with `--write`, else `safe` | Yes | After editing `naming.toml` |
| `scripts/module_groups.py`  | Folders where three or more code files share a name prefix: candidate packages (warn only; `--strict` fails) | Source files, code map | Candidates | `safe` | Yes | Modularising code; reviews |
| `scripts/write_back.py`     | Write-back entries a project parked for a skill (under a heading naming it), to promote into the skill (`--strict` fails while one is pending) | Markdown files | Pending entries | `safe` | Yes | Every slurp (skill-slurp-chat Step 5b) |
| `scripts/code_map.py`        | Loads and checks a project's `code-map.toml` (imported by the helpers)                       | `code-map.toml`                         | Settings                         | `safe`                       | Yes        | Imported, not run                             |
| `scripts/pyparse.py`         | Parses Python at the project's grammar with parser warnings silenced (imported by the helpers) | Python source                           | AST or SyntaxError               | `safe`                       | Yes        | Imported, not run                             |
| `scripts/ratchet.py`         | The shrink-only baseline every helper uses (imported)                                        | Baseline JSON                           | Verdicts                         | `safe`                       | Yes        | Imported, not run                             |
| `scripts/check_governance.py` | This pack's governance checker (from skill-ai-it's template)                                | Governance surfaces                     | Findings, exit status            | `safe`                       | Yes        | Through `just check`                          |

## Baselines and the code map

`scripts/code-size-baseline.json`, `scripts/timeout-baseline.json` and `scripts/script-headers-baseline.json` are machine-written by the helpers'
`--write-baseline` (adoption, or recording an improvement); never edit them by hand. `../code-map.toml` holds this pack's own decisions.

## Safety Labels

| Label                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `safe`                 | Read-only or low-risk repeatable operation                        |
| `review-required`      | Needs human review before execution                               |
| `destructive`          | Deletes, overwrites, migrates, deploys, or changes external state |
| `external-network`     | Calls external services or APIs                                   |
| `modifies-files`       | Writes to repo/project files                                      |
| `requires-secrets`     | Requires secret values                                            |
| `requires-credentials` | Requires authenticated local/session credentials                  |
| `long-running`         | May take significant time                                         |
| `unknown`              | Not yet classified; do not run without inspection                 |

## Governance recipes (skill-ai-it)

- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
````

## File: scripts/reflow_lossless.py
````python
#!/usr/bin/env python3
"""Prove that a re-wrapped markdown file changed no table cell and no word. Read-only.

Why: a formatter hook re-wraps a whole markdown file on the first edit when the file was not already in its normal form. The diff is then far
larger than the edit and reads as damage; on 2026-11-18 a lossless re-wrap of a 1,400-line register was reported as corruption because a token
comparison cannot tell a table re-wrap from damage (a table wraps column by column, so the word order changes). This compares the two versions
the only safe way: tables un-wrapped and matched row by row and cell by cell, prose matched word by word (operator, 2026-11-18).

Usage:
  reflow_lossless.py BEFORE AFTER --table-reflow <path to table-reflow cli.mjs>
  reflow_lossless.py --git FILE --table-reflow <cli.mjs>      # BEFORE is the file at HEAD, AFTER the working copy
  TABLE_REFLOW_CLI=<cli.mjs> reflow_lossless.py --git FILE --ignore-contents

Exit 0: no cell and no word changed. Exit 1: differences, listed. Exit 2: bad arguments, or tables present and no un-wrapper to prove them.
It writes nothing but temporary copies, which it removes.
"""

from __future__ import annotations

import argparse
import difflib
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Callable

#: Oldest Python this helper runs on (the pack's contract test parses it at that grammar).
REQUIRES_PYTHON = (3, 11)

#: Seconds any one call out (git, node) may take; every call states one.
CALL_TIMEOUT_S = 60

#: How many differing spans or rows are printed before the rest are only counted.
SHOWN = 5

SEPARATOR = re.compile(r":?-{1,}:?")
CONTENTS = re.compile(r"^#{1,6}\s+Contents\s*$")
HEADING = re.compile(r"^#{1,6}\s")


def is_table_line(line: str) -> bool:
  """Whether a line belongs to a markdown table.

  Args:
    line: one line of the file.

  Returns:
    True when its first non-blank character is a pipe.
  """
  return line.lstrip().startswith("|")


def drop_contents(lines: list[str]) -> list[str]:
  """Remove a generated `Contents` block, which a formatter may rebuild.

  Args:
    lines: the file's lines.

  Returns:
    The lines without the Contents heading and its body, up to the next heading or horizontal rule.
  """
  out, skipping = [], False
  for line in lines:
    if CONTENTS.match(line):
      skipping = True
      continue
    if skipping and (HEADING.match(line) or line.strip() == "---"):
      skipping = False
    if not skipping:
      out.append(line)
  return out


def prose_words(text: str, ignore_contents: bool = False) -> list[str]:
  """The words of everything that is not a table, in order.

  Args:
    text: the file's text.
    ignore_contents: leave a generated Contents block out.

  Returns:
    Words split on white space. A blockquote marker at the start of a line is dropped, because re-wrapping a quoted paragraph changes how
    many lines carry one.
  """
  lines = text.split("\n")
  if ignore_contents:
    lines = drop_contents(lines)
  words: list[str] = []
  for line in lines:
    if is_table_line(line):
      continue
    words.extend(re.sub(r"^\s*(>\s*)+", "", line).split())
  return words


def table_rows(unwrapped: str) -> list[tuple[str, ...]]:
  """The rows of every table in an un-wrapped file, as cells.

  Args:
    unwrapped: the file's text after its tables were un-wrapped to one line per row.

  Returns:
    One tuple of cells per table row, white space collapsed; a separator row becomes dashes of one length.
  """
  rows = []
  for line in unwrapped.split("\n"):
    if not is_table_line(line):
      continue
    cells = [re.sub(r"\s+", " ", cell).strip() for cell in line.strip().strip("|").split("|")]
    if cells and all(SEPARATOR.fullmatch(cell) for cell in cells if cell):
      cells = ["---"] * len(cells)
    rows.append(tuple(cells))
  return rows


def unwrap_with_cli(cli: pathlib.Path) -> Callable[[str], str]:
  """Build an un-wrapper that runs the table-reflow command line on a temporary copy.

  Args:
    cli: path of table-reflow's `cli.mjs`.

  Returns:
    A function from a file's text to the same text with every table row on one line.
  """

  def unwrap(text: str) -> str:
    """Un-wrap one text.

    Args:
      text: the file's text.

    Returns:
      The text with tables un-wrapped.

    Raises:
      subprocess.CalledProcessError: the tool refused the file.
      subprocess.TimeoutExpired: the tool took longer than CALL_TIMEOUT_S.
    """
    with tempfile.TemporaryDirectory() as tmp:
      copy = pathlib.Path(tmp) / "doc.md"
      copy.write_text(text, encoding="utf-8")
      subprocess.run(["node", str(cli), str(copy), "--unwrap", "--in-place"], check=True, capture_output=True, timeout=CALL_TIMEOUT_S)
      return copy.read_text(encoding="utf-8")

  return unwrap


def differences(before: str, after: str, unwrap: Callable[[str], str] | None, ignore_contents: bool = False) -> list[str]:
  """Every way the two texts differ in content.

  Args:
    before: the text before the re-wrap.
    after: the text after it.
    unwrap: un-wraps tables; None when no un-wrapper is available.
    ignore_contents: leave a generated Contents block out of the prose comparison.

  Returns:
    One line per finding; empty when no cell and no word changed.

  Raises:
    ValueError: a table is present and there is no un-wrapper to prove it.
  """
  found: list[str] = []
  a, b = prose_words(before, ignore_contents), prose_words(after, ignore_contents)
  if a != b:
    spans = [op for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op[0] != "equal"]
    found.append(f"prose: {len(spans)} differing span(s) ({len(a)} words before, {len(b)} after)")
    for tag, i1, i2, j1, j2 in spans[:SHOWN]:
      found.append(f"  {tag}: {' '.join(a[i1:i2])[:120]!r} -> {' '.join(b[j1:j2])[:120]!r}")
  has_tables = any(is_table_line(line) for line in (before + "\n" + after).split("\n"))
  if has_tables:
    if unwrap is None:
      raise ValueError("the file has tables and no un-wrapper was given (--table-reflow or TABLE_REFLOW_CLI)")
    ra, rb = table_rows(unwrap(before)), table_rows(unwrap(after))
    if ra != rb:
      blocks = [op for op in difflib.SequenceMatcher(None, ra, rb, autojunk=False).get_opcodes() if op[0] != "equal"]
      found.append(f"tables: {len(blocks)} differing block(s) of rows ({len(ra)} rows before, {len(rb)} after)")
      for tag, i1, i2, j1, j2 in blocks[:SHOWN]:
        found.append(f"  {tag}: {' | '.join(ra[i1])[:120] if i1 < len(ra) else ''!r} -> {' | '.join(rb[j1])[:120] if j1 < len(rb) else ''!r}")
  return found


def head_text(path: pathlib.Path) -> str:
  """A file's text as committed at HEAD.

  Args:
    path: the working-copy file.

  Returns:
    Its text at HEAD.

  Raises:
    subprocess.CalledProcessError: the file is not tracked, or this is not a git repository.
  """
  run = subprocess.run(["git", "-C", str(path.parent), "show", f"HEAD:./{path.name}"], check=True, capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
  return run.stdout


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 when lossless, 1 when content differs, 2 on bad arguments or when tables cannot be proven.
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("files", nargs="*", help="BEFORE AFTER, or with --git one FILE")
  ap.add_argument("--git", action="store_true", help="compare FILE at HEAD with the working copy")
  ap.add_argument("--table-reflow", default=os.environ.get("TABLE_REFLOW_CLI", ""), help="path of table-reflow's cli.mjs (or TABLE_REFLOW_CLI)")
  ap.add_argument("--ignore-contents", action="store_true", help="leave a generated Contents block out of the prose comparison")
  args = ap.parse_args(argv)
  try:
    if args.git:
      if len(args.files) != 1:
        ap.error("--git takes one FILE")
      path = pathlib.Path(args.files[0]).resolve()
      before, after = head_text(path), path.read_text(encoding="utf-8")
    else:
      if len(args.files) != 2:
        ap.error("give BEFORE and AFTER, or --git FILE")
      before, after = (pathlib.Path(f).read_text(encoding="utf-8") for f in args.files)
    cli = pathlib.Path(args.table_reflow) if args.table_reflow else None
    if cli is not None and not cli.is_file():
      print(f"table-reflow command line not found: {cli}", file=sys.stderr)
      return 2
    found = differences(before, after, unwrap_with_cli(cli) if cli else None, args.ignore_contents)
  except ValueError as exc:
    print(f"cannot prove it: {exc}", file=sys.stderr)
    return 2
  except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
    print(f"could not read or un-wrap: {exc}", file=sys.stderr)
    return 2
  if found:
    print("NOT lossless:")
    print("\n".join(found))
    return 1
  print("lossless: no table cell and no word changed")
  return 0


if __name__ == "__main__":
  sys.exit(main())
````

## File: scripts/role-check-baseline.json
````json
{}
````

## File: scripts/scaffold.py
````python
#!/usr/bin/env python3
"""Print the skeleton of a new script and its test that already meets this pack's rules; the agent fills in the logic. Read-only: it prints to
stdout and writes nothing.

Why (operator, 2026-10-20: the project writes its code, the skill supplies the practice): boilerplate written from memory drifts (a missing
Args block, a write path without --apply, a subprocess without a timeout). The skeleton carries the purpose header (summary, why, how it is run,
what it touches), documented functions, the --apply gate when the script writes, timeouts on every call out, and an offline test of the plan.
The project's own rules still outrank it: adjust the skeleton to the project's layout, names and test runner before use.

Usage:
    scaffold.py --lang python --name sync_widgets --summary "Copy widgets from A to B" [--writes] [--run "just sync-widgets"]
    scaffold.py --lang shell --name backup_db --summary "Dump the database" --writes
Exit: 0 after printing, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from string import Template

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

PY_MODULE = Template('''#!/usr/bin/env python3
"""$summary. $safety

Why: <the problem this solves and who asked for it, with a date>.

Usage:
    $run
"""

from __future__ import annotations

import argparse
import subprocess
import sys

#: Seconds any one call out (subprocess, HTTP, socket) may take; every call states one.
CALL_TIMEOUT_S = 30


def plan(items: list[str]) -> list[str]:
    """What the run would do, one line per change; pure, so the test can check it.

    Args:
        items: <what the plan is built from>.

    Returns:
        One line per change.
    """
    return [f"would change {item}" for item in items]

$apply_func
def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 on success, 1 on a failure it reports, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\\n")[0])
$apply_arg    args = ap.parse_args(argv)
    lines = plan([])
    print("\\n".join(lines) or "nothing to do")
$apply_call    return 0


if __name__ == "__main__":
    sys.exit(main())
''')

PY_APPLY_FUNC = '''
def apply(lines: list[str]) -> int:
    """Make the planned changes; called only with --apply.

    Args:
        lines: the plan.

    Returns:
        The number of changes made.

    Raises:
        subprocess.TimeoutExpired: when a call out exceeds CALL_TIMEOUT_S (for a command that starts children, such as ssh or a shell, end
            the whole process group instead: see the pack's errors-and-timeouts reference).
    """
    for _line in lines:
        subprocess.run(["true"], check=True, timeout=CALL_TIMEOUT_S)   # <the change>
    return len(lines)

'''

PY_TEST = Template('''"""Offline tests for $name: the plan is right, and nothing is written without --apply.

Run: <the project's test runner>.
"""

import io
import unittest
from contextlib import redirect_stdout

import $name


class Plan(unittest.TestCase):
    """The plan names each change; a dry run changes nothing."""

    def test_plan_lists_each_change(self):
        self.assertEqual($name.plan(["a"]), ["would change a"])

    def test_dry_run_prints_and_exits_0(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual($name.main([]), 0)
        self.assertIn("nothing to do", out.getvalue())


if __name__ == "__main__":
    unittest.main()
''')

SH_MODULE = Template('''#!/usr/bin/env bash
# $summary. $safety
# Why: <the problem this solves and who asked for it, with a date>.
# Usage: $run
set -euo pipefail

CALL_TIMEOUT_S=30   # every call out is bounded: `bounded <cmd>` (for ssh, see the pack's errors-and-timeouts reference)
SITE=""   # an example option with a value; replace with the script's own
$apply_var
# bounded
#   Run a command for at most CALL_TIMEOUT_S seconds: GNU timeout where installed, else perl's alarm (macOS ships perl, not timeout).
#   Args: $$@ the command and its arguments.
#   Returns: the command's status; 124 (timeout) or 142 (alarm) when it ran too long.
bounded() {
  if command -v timeout >/dev/null 2>&1; then timeout "$$CALL_TIMEOUT_S" "$$@"; else perl -e 'alarm shift; exec @ARGV' "$$CALL_TIMEOUT_S" "$$@"; fi
}

# plan
#   Print one line per change the run would make.
#   Args: none.
#   Returns: 0.
plan() {
  echo "would change <item> at $${SITE:-every site}"
}
$apply_func
# main
#   Parse arguments, print the plan$apply_doc.
#   Args: $$@ the command line.
#   Returns: 0 on success; exits 2 on bad arguments.
main() {
  while [ $$# -gt 0 ]; do
    case "$$1" in
      --site) SITE="$${2:?--site needs a value}"; shift ;;
$apply_case      -h|--help) sed -n '2,4p' "$$0"; exit 0 ;;
      *) echo "$name: unknown argument $$1" >&2; exit 2 ;;
    esac
    shift
  done
  plan
$apply_call}

main "$$@"
''')


def two_space(text: str) -> str:
    """Re-indent a four-space template to the pack's two-space rule (operator, 2026-10-23), leading spaces only.

    Args:
        text: generated Python.

    Returns:
        The same code with each leading run of spaces halved.
    """
    return re.sub(r"(?m)^( +)", lambda m: " " * (len(m.group(1)) // 2), text)


def python_files(name: str, summary: str, writes: bool, run: str) -> dict[str, str]:
    """The Python module and its test.

    Args:
        name: the module name (snake_case).
        summary: one sentence saying what it does.
        writes: whether it changes anything (adds the --apply gate).
        run: how it is run.

    Returns:
        {file name: text}.
    """
    module = PY_MODULE.substitute(
        summary=summary.rstrip("."), run=run,
        safety="Writes only with --apply; without it, prints the plan." if writes else "Read-only.",
        apply_func=PY_APPLY_FUNC if writes else "",
        apply_arg='    ap.add_argument("--apply", action="store_true", help="make the changes; without it, print the plan")\n' if writes else "",
        apply_call="    if args.apply:\n        print(f\"changed {apply(lines)}\")\n" if writes else "")
    return {f"{name}.py": two_space(module), f"test_{name}.py": two_space(PY_TEST.substitute(name=name))}


def shell_files(name: str, summary: str, writes: bool, run: str) -> dict[str, str]:
    """The shell script.

    Args:
        name: the script name (snake_case).
        summary: one sentence saying what it does.
        writes: whether it changes anything (adds the --apply gate).
        run: how it is run.

    Returns:
        {file name: text}.
    """
    script = SH_MODULE.substitute(
        name=name, summary=summary.rstrip("."), run=run,
        safety="Writes only with --apply; without it, prints the plan." if writes else "Read-only.",
        apply_var="APPLY=0\n" if writes else "",
        apply_func=("\n# apply\n#   Make the planned changes; called only with --apply.\n#   Args: none.\n#   Returns: 0; exits non-zero on a failed change.\n"
                    "apply() {\n  bounded true   # <the change>\n}\n") if writes else "",
        apply_doc=" and, with --apply, make the changes" if writes else "",
        apply_case="      --apply) APPLY=1 ;;\n" if writes else "",
        apply_call='  [ "$APPLY" = 1 ] && apply\n  return 0\n' if writes else "")
    return {f"{name}.sh": script}


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 after printing, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lang", choices=["python", "shell"], required=True)
    ap.add_argument("--name", required=True, help="snake_case module or script name, no suffix")
    ap.add_argument("--summary", required=True, help="one sentence: what it does")
    ap.add_argument("--writes", action="store_true", help="it changes something: add the --apply gate")
    ap.add_argument("--run", help="how it is run (default: the script with its flags)")
    args = ap.parse_args(argv)
    if not NAME_RE.match(args.name):
        print(f"scaffold: --name {args.name!r} is not snake_case", file=sys.stderr)
        return 2
    suffix = ".py" if args.lang == "python" else ".sh"
    run = args.run or f"{args.name}{suffix}" + (" [--apply]" if args.writes else "")
    files = (python_files if args.lang == "python" else shell_files)(args.name, args.summary, args.writes, run)
    for fname, text in files.items():
        print(f"===== {fname}\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/script_headers.py
````python
#!/usr/bin/env python3
"""Check that every runnable script's native header says what it is for, how to run it and what it touches, as a shrink-only ratchet.
Read-only unless --write-baseline. Stdlib only.

Why (operator, 2026-10-19: "should we also define front matter ... for individual scripts"): a script's header is its front matter, in the form
its language allows (governance `naming-and-file-summary-guide.md`, "File headers"): the module docstring for Python, the leading `#` comment
block (after the shebang) for shell. skill-ai-it's doc_freshness.py already fails a file with no summary line; this adds what a reader needs
before running it:

    summary   the first line says what the script is for
    run       a `Usage:` or `Run:` line (or `Imported, not run` for a module that is only imported)
    safety    what it touches: read-only, files only, or how its writes are gated (`--apply`, a plan/apply subcommand)

Only entry points are checked (Python with a `__main__` block, shell with a shebang); a library module needs only its summary.

Usage:
    script_headers.py --project-root . [--roots scripts,src] [--baseline scripts/script-headers-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more missing parts than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import code_map
import pyparse
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: The header parts and how each is recognised.
PARTS = {
    "run": re.compile(r"(?im)^\s*(?:usage|run)\b.*:|\bimported, not run\b"),
    "safety": re.compile(r"(?i)\bread[- ]only\b|\bfiles only\b|--apply\b|\bwrites?\b|\bdry[- ]run\b|\bplan\b|\bchanges nothing\b|\bno side effects\b"),
}
SHELL_SUFFIXES = (".sh", ".bash")


def header(text: str, suffix: str) -> str | None:
    """A script's header in its native form.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        The Python module docstring, or the shell comment block after the shebang (without `#`); None when the file has none or does not parse.
    """
    if suffix == ".py":
        try:
            return ast.get_docstring(pyparse.parse(text))
        except SyntaxError:
            return None
    lines = text.splitlines()[1:] if text.startswith("#!") else text.splitlines()
    block = []
    for line in lines:
        if not line.startswith("#"):
            break
        block.append(line.lstrip("#").strip())
    return "\n".join(block).strip() or None


def is_entry(text: str, suffix: str) -> bool:
    """Whether a file is meant to be run.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        True for Python with a `__main__` block or a shell script with a shebang.
    """
    if suffix == ".py":
        return re.search(r"""__name__\s*==\s*["']__main__["']""", text) is not None
    return suffix in SHELL_SUFFIXES and text.startswith("#!")


def missing_parts(text: str, suffix: str) -> list[str]:
    """Which header parts a runnable script lacks.

    Args:
        text: the file's text.
        suffix: its suffix.

    Returns:
        A subset of ["summary", "run", "safety"] (all three when there is no header); empty for a library module with a summary.
    """
    head = header(text, suffix)
    if not head:
        return ["summary", "run", "safety"] if is_entry(text, suffix) else ["summary"]
    if not is_entry(text, suffix):
        return []
    return [name for name, pattern in PARTS.items() if not pattern.search(head)]


def measure(root: Path, roots: list[str]) -> dict[str, list[str]]:
    """Missing header parts per script.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        {path: missing parts} for files missing any.
    """
    out: dict[str, list[str]] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if path.suffix not in (".py", *SHELL_SUFFIXES) or not path.is_file() or "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            missing = missing_parts(path.read_text(encoding="utf-8", errors="replace"), path.suffix)
            if missing:
                out[path.relative_to(root).as_posix()] = missing
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else scripts,src)")
    ap.add_argument("--baseline", default="scripts/script-headers-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every script with a missing header part")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        wanted = args.roots or code_map.scan_roots(code_map.for_root(root, args.code_map), default="scripts,src")
    except (OSError, ValueError) as exc:
        print(f"script_headers: {exc}", file=sys.stderr)
        return 2
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"script_headers: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    found = measure(root, roots)
    counts = {rel: len(parts) for rel, parts in found.items()}
    if args.list:
        print("\n".join(f"{rel}: header lacks {', '.join(parts)}" for rel, parts in found.items()))
    base_path = root / args.baseline
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"script_headers: baseline written, {len(counts)} file(s) with gaps")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    print("\n".join(ratchet.report(verdict, "header", base_path)) or f"script_headers: OK, {len(counts)} file(s) with gaps, all within the baseline")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/script-headers-baseline.json
````json
{
 "scripts/check_governance.py": 2
}
````

## File: scripts/suppressions.py
````python
#!/usr/bin/env python3
"""Find inline linter suppressions (noqa, type: ignore, shellcheck disable, eslint-disable, nolint, allow), as a shrink-only ratchet.
Read-only unless --write-baseline. Stdlib only.

Why (operator rule, references/documentation-and-headers.md: never silence a linter inline): a suppression hides the finding instead of fixing
it, and an agent under pressure adds one rather than restructure the code (2026-10-20: a `# noqa: E402` was written into a new test, and only
review caught it). Existing ones are counted per file so adoption is possible; a new one fails the check.

Python comments are read with `tokenize`, so a marker inside a string never counts. Other languages are read per line: a marker counts only
after that language's comment opener (`#`, `//`, `--`, `/*`), or as Rust's `#[allow(` / `#![allow(` attribute.

Usage:
    suppressions.py --project-root . [--roots src,scripts] [--baseline scripts/suppressions-baseline.json] [--list] [--write-baseline]
Exit: 0 when no file has more suppressions than its baseline and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import tokenize
from pathlib import Path

import code_map
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Python comment markers that silence a linter or type checker.
PY_MARKERS = re.compile(r"\bnoqa\b|\btype:\s*ignore\b|\bpylint:\s*disable|\bpyright:\s*ignore\b|\bmypy:\s*ignore|\bruff:\s*noqa\b", re.I)

#: Per file suffix: (comment openers, markers). A marker counts only after an opener on the same line.
LANGUAGES: dict[str, tuple[tuple[str, ...], re.Pattern]] = {
    ".sh": (("#",), re.compile(r"shellcheck\s+disable=")),
    ".bash": (("#",), re.compile(r"shellcheck\s+disable=")),
    ".js": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".mjs": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".cjs": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".jsx": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".ts": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".tsx": (("//", "/*"), re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore")),
    ".go": (("//",), re.compile(r"\bnolint\b")),
    ".sql": (("--",), re.compile(r"\bnoqa\b")),
    ".yml": (("#",), re.compile(r"yamllint\s+disable")),
    ".yaml": (("#",), re.compile(r"yamllint\s+disable")),
}
#: Rust silences lints with an attribute, not a comment.
RUST_ALLOW = re.compile(r"^\s*#!?\[allow\(")

SKIP_PARTS = {".venv", "venv", "node_modules", "__pycache__", ".git", "target", "dist", "build"}


def python_suppressions(text: str) -> list[tuple[int, str]]:
    """Suppression comments in Python source.

    Args:
        text: the source.

    Returns:
        (line, comment text) per suppression; a source that does not tokenize gives what was read before the error.
    """
    out: list[tuple[int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT and PY_MARKERS.search(tok.string):
                out.append((tok.start[0], tok.string.strip()))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


def line_suppressions(text: str, suffix: str) -> list[tuple[int, str]]:
    """Suppressions in a non-Python file, read per line.

    Args:
        text: the file's text.
        suffix: its suffix (".sh", ".ts", ".rs", ...).

    Returns:
        (line, text) per suppression; an unknown suffix gives none.
    """
    out: list[tuple[int, str]] = []
    if suffix == ".rs":
        return [(n, line.strip()) for n, line in enumerate(text.splitlines(), 1) if RUST_ALLOW.match(line)]
    if suffix not in LANGUAGES:
        return out
    openers, marker = LANGUAGES[suffix]
    for n, line in enumerate(text.splitlines(), 1):
        starts = [line.find(o) for o in openers if o in line]
        if not starts:
            continue
        comment = line[min(starts):]
        if marker.search(comment):
            out.append((n, comment.strip()))
    return out


def suppressions(path: Path) -> list[tuple[int, str]]:
    """Suppressions in one file, by its suffix.

    Args:
        path: the file.

    Returns:
        (line, text) per suppression.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    return python_suppressions(text) if path.suffix == ".py" else line_suppressions(text, path.suffix)


def measure(root: Path, roots: list[str]) -> tuple[dict[str, float], dict[str, list]]:
    """Suppressions per file under the roots.

    Args:
        root: the project root.
        roots: folders to scan.

    Returns:
        ({path: count} for files with any, {path: [(line, text)]}).
    """
    counts: dict[str, float] = {}
    detail: dict[str, list] = {}
    wanted = {".py", ".rs", *LANGUAGES}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file() or path.suffix not in wanted or SKIP_PARTS & set(path.parts):
                continue
            found = suppressions(path)
            if found:
                rel = path.relative_to(root).as_posix()
                counts[rel], detail[rel] = len(found), found
    return counts, detail


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [suppressions] or [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", help="default: the code map's [suppressions] baseline, else scripts/suppressions-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every suppression")
    ap.add_argument("--write-baseline", action="store_true", help="record today's counts (adoption or after an improvement)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap = code_map.for_root(root, args.code_map)
    except (OSError, ValueError) as exc:
        print(f"suppressions: {exc}", file=sys.stderr)
        return 2
    wanted = args.roots or code_map.scan_roots(cmap, "suppressions")
    roots = [r for r in wanted.split(",") if r and (root / r).is_dir()]
    if not roots:
        print(f"suppressions: none of {wanted} exists under {root}", file=sys.stderr)
        return 2
    base_path = root / (args.baseline or code_map.section(cmap, "suppressions").get("baseline", "scripts/suppressions-baseline.json"))
    counts, detail = measure(root, roots)
    if args.list:
        for rel, found in detail.items():
            for line, text in found:
                print(f"{rel}:{line}: {text}")
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"suppressions: baseline written, {sum(counts.values()):g} suppression(s) in {len(counts)} file(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    for line in ratchet.report(verdict, "suppressions", base_path):
        print(line)
    if verdict.ok:
        print(f"suppressions: OK, {sum(counts.values()):g} suppression(s), all within the baseline")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/timeout-baseline.json
````json
{}
````

## File: scripts/write_back.py
````python
#!/usr/bin/env python3
"""Find write-back entries a project is still holding for a skill, so the next engagement promotes them into the skill. Read-only. Stdlib only.

Why (operator, 2026-10-19: "add the write back mechanism so that whatever learning is there, any project which is calling skill coder should
write that learning back"): when a session cannot write the skill's source, the contract (references/evolution-and-write-back.md) parks the entry
in the engaging project under a heading naming the skill. Without a way to find those entries again they stay there; this lists them, and the
slurp (skill-slurp-chat Step 5b) runs it for every engaged skill.

An entry is a `> **Learned YYYY-MM-DD**` or `> **Disputed YYYY-MM-DD**` blockquote line inside a Markdown section whose heading names the skill
(for example `## skill-coder write-back candidates`); the section ends at the next heading of the same or a higher level.

Usage:
    write_back.py --project-root /path/to/project [--skill skill-coder] [--strict]
Exit: 0 (report); with --strict 1 while an entry is pending; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
ENTRY = re.compile(r"^>\s*\*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})\*\*")
#: Folders never read: rebuildable caches, history archives (a rotated entry was already handled), vendored code.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "history", "archive"}


def pending_in(text: str, skill: str) -> list[tuple[int, str, str]]:
    """The entries parked for a skill in one Markdown text.

    Args:
        text: the file's text.
        skill: the skill's name as it appears in the parking heading.

    Returns:
        (line number, kind, date) per entry inside a section whose heading names the skill; code fences are skipped.
    """
    out, level, fence = [], 0, False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if (h := HEADING.match(line)) is not None:
            depth = len(h.group(1))
            if level and depth <= level:
                level = 0
            if skill.lower() in h.group(2).lower():
                level = depth
            continue
        if level and (e := ENTRY.match(line)) is not None:
            out.append((n, e.group(1), e.group(2)))
    return out


def pending(root: Path, skill: str) -> list[tuple[str, int, str, str]]:
    """Every entry a project holds for a skill.

    Args:
        root: the project root.
        skill: the skill's name.

    Returns:
        (file relative to root, line number, kind, date) per entry, in path order.
    """
    found = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found += [(rel.as_posix(), n, kind, date) for n, kind, date in pending_in(text, skill)]
    return found


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, or 1 with --strict while an entry is pending; 2 when the project root is not a folder.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--skill", default="skill-coder", help="the skill whose parked entries to find (default skill-coder)")
    ap.add_argument("--strict", action="store_true", help="exit 1 while an entry is pending")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    if not root.is_dir():
        print(f"write_back: {root} is not a folder", file=sys.stderr)
        return 2
    found = pending(root, args.skill)
    for rel, n, kind, date in found:
        print(f"{rel}:{n}: {kind} {date} parked for {args.skill}: promote it into the skill, then remove it here")
    print(f"write_back: {len(found)} entr{'y' if len(found) == 1 else 'ies'} pending for {args.skill} in {root.name}")
    return 1 if (args.strict and found) else 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/write_gates.py
````python
#!/usr/bin/env python3
"""Find entry-point scripts that write without a dry-run default: every writer takes `--apply`, or is registered with the reason it may not.
Read-only. Stdlib only.

Promoted from unified-network-controller `check_write_gates` (2026-10-19). Why (operator, 2026-10-06): a test script wrote to production devices
and a seeding script could delete real records on a bare run. The rule: read is the default; a script that changes anything prints its plan and
changes nothing until it is run with `--apply` (a subcommand such as `apply` counts when registered). A registered exception names its own gate.

A writer is an entry point (the language's main marker) whose text matches a write pattern. The patterns are a heuristic and project-specific
writes are added in the config; a registered exception that no longer writes, no longer exists or now takes `--apply` fails too, so the register
cannot go stale.

Config (JSON, optional; every key optional):
    {"roots": ["scripts"], "suffixes": [".py", ".sh"], "write_patterns": ["\\\\.delete\\\\("], "apply_pattern": "--apply",
     "exceptions": {"scripts/collector.py": "pushes metrics by design; --dry-run reads only"}}

Usage:
    write_gates.py --project-root . [--config scripts/write-gates.json] [--list]
Exit: 0 when every writer is gated or registered and the register is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Write patterns every project starts with, any language: changes to a live system (HTTP writes, SQL changes) and recursive deletion. Matched
#: case-sensitively (`"delete"` as an action name is not an HTTP DELETE). Writing a local generated file is not a live write (a renderer's
#: `--write` is its own gate); add project-specific writes (an SNMP set, a client library's create call) in the config.
DEFAULT_WRITES = (
    r"""["'](?:POST|PATCH|PUT|DELETE)["']""",
    r"\b(?:requests|httpx|session|client)\.(?:post|patch|put|delete)\(",
    r"\bshutil\.rmtree\(",
    r"\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|DROP\s+TABLE|ALTER\s+TABLE|TRUNCATE\s+TABLE)\b",
    r"\bfetch\([^)]*method:\s*[\"'](?:POST|PUT|PATCH|DELETE)",
)
#: Further patterns for shell scripts only (in other languages these words are mostly prose in docstrings): recursive or forced removal,
#: package installs, service control.
SHELL_WRITES = (
    r"\brm\s+-[a-z]*[rf][a-z]*\b",
    r"\b(?:apt|apt-get|dnf|yum|brew)\s+install\b|\bpip3?\s+install\b",
    r"\bsystemctl\s+(?:restart|stop|start|enable|disable)\b",
)
SHELL_SUFFIXES = (".sh", ".bash")
#: What marks a file as an entry point, per suffix.
ENTRY = {".py": r"""__name__\s*==\s*["']__main__["']""", ".sh": r"^#!", ".bash": r"^#!", ".js": r"^#!|process\.argv", ".ts": r"^#!|process\.argv",
         ".go": r"^func main\(", ".rs": r"^fn main\("}
DEFAULT_APPLY = r"--apply\b"


def load_config(path: Path | None, cmap: dict | None = None) -> dict:
    """The checker's settings: the JSON config if given, else the code map's [write_gates] section, defaults filled in.

    Args:
        path: the JSON config, or None.
        cmap: a loaded code map (code_map.load), or None.

    Returns:
        {"roots", "suffixes", "write_patterns", "apply_pattern", "exceptions"}.

    Raises:
        ValueError: when the file is not a JSON object.
    """
    cfg = json.loads(path.read_text(encoding="utf-8")) if path else code_map.section(cmap or {}, "write_gates")
    if not isinstance(cfg, dict):
        raise ValueError("write-gates config must be a JSON object")
    return {"roots": cfg.get("roots", ["scripts"]), "suffixes": cfg.get("suffixes", sorted(ENTRY)),
            "write_patterns": list(DEFAULT_WRITES) + list(cfg.get("write_patterns", [])),
            "apply_pattern": cfg.get("apply_pattern", DEFAULT_APPLY), "exceptions": dict(cfg.get("exceptions", {}))}


def writers(root: Path, cfg: dict, skip: set[str]) -> dict[str, bool]:
    """Every entry point that writes, and whether it takes the apply flag.

    Args:
        root: the project root.
        cfg: load_config()'s result.
        skip: repo-relative files never examined (the checker and its config).

    Returns:
        {path: has apply flag}.
    """
    write = re.compile("|".join(f"(?:{p})" for p in cfg["write_patterns"]))
    shell = re.compile("|".join(f"(?:{p})" for p in SHELL_WRITES))
    apply = re.compile(cfg["apply_pattern"])
    out: dict[str, bool] = {}
    for folder in cfg["roots"]:
        base = root / folder
        for path in sorted(base.rglob("*")) if base.is_dir() else []:
            rel = path.relative_to(root).as_posix()
            if not path.is_file() or path.suffix not in cfg["suffixes"] or rel in skip or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            writes = write.search(text) or (path.suffix in SHELL_SUFFIXES and shell.search(text))
            if re.search(ENTRY.get(path.suffix, r"$^"), text, re.M) and writes:
                out[rel] = bool(apply.search(text))
    return out


def problems(found: dict[str, bool], exceptions: dict[str, str]) -> list[str]:
    """Unregistered ungated writers and stale register entries.

    Args:
        found: writers()'s result.
        exceptions: {path: reason} from the config.

    Returns:
        One message per problem.
    """
    out = [f"{rel} writes without taking --apply: make it plan by default with --apply, or register it with its gate and reason"
           for rel, gated in sorted(found.items()) if not gated and rel not in exceptions]
    for rel, reason in sorted(exceptions.items()):
        if not str(reason).strip():
            out.append(f"exception {rel} has no reason")
        elif rel not in found:
            out.append(f"exception {rel} no longer exists or no longer writes: remove it")
        elif found[rel]:
            out.append(f"exception {rel} now takes --apply: remove it")
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when clean, 1 on a problem, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--config", type=Path, help="JSON config (roots, suffixes, write_patterns, apply_pattern, exceptions)")
    ap.add_argument("--list", action="store_true", help="print every writer found and whether it is gated")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cfg = load_config(args.config, code_map.for_root(root, args.code_map))
    except (OSError, ValueError) as exc:
        print(f"write_gates: {exc}", file=sys.stderr)
        return 2
    skip = {Path(__file__).resolve().relative_to(root).as_posix()} if Path(__file__).resolve().is_relative_to(root) else set()
    found = writers(root, cfg, skip)
    if args.list:
        for rel, gated in found.items():
            print(f"{'gated   ' if gated else 'UNGATED '} {rel}" + (f"  ({cfg['exceptions'][rel]})" if rel in cfg["exceptions"] else ""))
    issues = problems(found, cfg["exceptions"])
    for line in issues:
        print(f"FAIL write-gate: {line}")
    if not issues:
        print(f"write_gates: OK, {len(found)} writer(s), every one gated or registered")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: AGENTS.md
````markdown
---
Title: skill-coder Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-coder pack — canonical, cross-project source of reusable programming practice
Last reviewed: 2026-11-19
Summary: >-
  Agent guidance for maintaining and using skill-coder: artifact roles, the runtime rule for its helpers, the code map, the write-back obligation
  and the gates to run before calling work complete.
Budget: 150 lines, 12 KB
---

@../../../AGENTS.md

# AGENTS.md

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## AI navigation and context preflight

Before answering, planning or editing, read [AI_NAVIGATION.md](AI_NAVIGATION.md) first: it routes everything else (read order, source priority, task routing, scripts, checks, compaction recovery).
Read [context-map.yaml](context-map.yaml) only when changing routing or companion files.

- Sources disagree: stop and report, never guess. `SCRATCHPAD.md` is not durable truth unless marked `KEEP`; generated output never is.
- Run catalogued tasks only (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety. A new or changed script updates `scripts/README.md`.
- Before calling work done: `just check` (fix the project, not the check), and a `CHANGELOG.md` entry for any governance or navigation change.
- Preserve user content outside managed blocks.

<!-- END MANAGED: skill-ai-it:navigation -->

## Contents

- [Working rules](#working-rules)
- [Runtime rule for the helpers](#runtime-rule-for-the-helpers)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

---

## Working rules

- [SKILL.md](SKILL.md) is the activation surface and must route every file in `references/` and `languages/`; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors it.
- Core rules in `references/` are language-agnostic. A language file may tighten a rule, loosen it only with a stated reason, or map it to that
  language's tools. A project's own rules (its `AGENTS.md`, code design, `code-map.toml`) outrank both; say so when they differ.
- Every rule says why in one clause and cites its source in [sources.yaml](sources.yaml): operator rules as `USER_STATED`, external facts with a
  primary source and retrieval date. Unverified material is labelled `UNVERIFIED`, never stated as fact.
- No customer names, hostnames, private addresses, tokens or production domains in pack files; a governed project is named only as a rule's source.
- `scripts/` holds stdlib-only helpers with tests in `tests/test_helpers.py`; a new helper is catalogued in [scripts/README.md](scripts/README.md)
  and gets a recipe in the same pass. The pack is held to its own rules by `just self-check` (inside `just check`).
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading.
- Research sources go verbatim under `documents/` with a `readme.md` index; downloads never go to `/tmp` or a scratchpad.
- Triage before opening: `just docs <folder>`; run `just stale` before editing; old records via `just history <term>`. <!-- path:example -->

## Runtime rule for the helpers

Operator, 2026-10-19 (assessed against the alternative of a separate skill runtime): the logic is applied inside the target project's own
environment with that project's own tooling. The helpers are stdlib-only, declare `REQUIRES_PYTHON = (3, 11)`, read code as files, and run with
the project's pinned interpreter by path. Only when a project has no Python 3.11+ does an agent run them through this pack's recipes
(`just -f <pack>/justfile <recipe> --project-root <project>`), which is safe because they only read. Nothing is ever installed into a project for
the pack's sake. `just test-matrix` proves the helpers on every installed Python from 3.11.

## Package contract

`tests/test_package_contract.py` is the pack's executable contract: every reference and language file is routed from `SKILL.md`; claims follow the
ledger schema; every Learned or Disputed entry has a CHANGELOG line naming the file and date; every helper is tested, stdlib-only, declares
`REQUIRES_PYTHON` and parses at that grammar; every function and class has an `Args:`/`Returns:` docstring; no unsafe text anywhere. Run
`just test` and `just check` before claiming any change complete.

## Cross-project write-back trigger

Any project that invokes this skill and learns reusable programming practice writes it back here before the session closes: a dated Learned entry
in the focused reference (or language file) plus one CHANGELOG line under `## Unreleased`, read back after writing (format in
`references/evolution-and-write-back.md`). If this source is not writable from the engaging task, leave the entry in the engaging project as a
candidate under `## skill-coder write-back candidates`, where `scripts/write_back.py` finds it for the next engagement to promote. A project-specific
rule stays in that project. The calling session owes this whether or not its project routes to this skill; skill-slurp-chat Step 5b rechecks it
(`references/evolution-and-write-back.md`, "Projects that call this skill").

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and `just check` gates on them. It is stdlib-only
and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this project's
documents and silent decay.

### The checker grows with the project

The check count is a coverage signal, not a score. It is expected to rise as the project acquires structure. Extend it on these triggers:

| Change made | Required checker update |
|---|---|
| Add a document to a cataloged folder | None — the coverage check fails until the index links it. That is the intended workflow, not an error to route around |
| Add a script or task | Catalog it in `scripts/README.md` and the task runner; coverage fails until then |
| Add a new **class** of artifact (new folder, new document type) | Add a `CATALOGS` entry, plus a contract check if the class has a declared filename or frontmatter form |
| Add a generated artifact | Add a `DERIVED` entry; add a provenance check too if the generator can stamp its source into the output |
| State a threshold, rate, deadline, or canonical path in a new file | Register the file in `CONSTANT_SURFACES`; the sync check fails until it is registered |
| Change a constant's value | Update the owning rule first, then every registered surface, in one pass — the sync check verifies the pass was complete |
| Rename or move a file | Nothing — path resolution catches every stale reference automatically |
| Retire a check | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed |

### Rules that are not negotiable

- **When a check fails, fix the project, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot
  that the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the project deliberately and watching it go red. A check that scans an empty set is an assumption wearing a test's clothes.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the surrounding logic implements it — a script's output can state a rule its code no longer applies.
  Where a check must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts and states recorded as past facts are evidence, not live claims. Mark those lines `<!-- count:asat -->` rather than editing the record to satisfy the checker.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- skill-ai-it (bootstrap source): [/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: AI_NAVIGATION.md
````markdown
---
Title: AI Navigation
Category: navigation
Status: current
Authority: local-supplement
Scope: Context entrypoint for AI agents in skill-coder
Last reviewed: 2026-11-16
Summary: Where project truth lives, what to read first, what is authoritative and what must be updated after work; a router, not the knowledge store.
Budget: 150 lines, 12 KB
---

# AI Navigation — skill-coder

Purpose: the project's context entrypoint for AI agents: where project truth lives, what to read first, what is authoritative and what must be updated after work. A router, not the knowledge store.
Full tables and procedures: [navigation reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/readme.md).

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file, including any project-authored sections below the END marker, and the upgrader regenerates everything
between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Script and Task Navigation](#script-and-task-navigation)
- [Governance coherence checks](#governance-coherence-checks)
- [Companion consistency](#companion-consistency)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)
- [Pack routing](#pack-routing)

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Mandatory read order

`AGENTS.md`, then this file, then `context-map.yaml`, then the newest `CHANGELOG.md` entries, then relevant `.archcore/` and `memory-bank/` files if present, then the docs and code the task needs.
Triage before opening: `just docs <folder>` (one header line per file); `just stale` lists stale docs.

## Source priority

`.archcore/` accepted documents, then `AGENTS.md` / `CLAUDE.md`, this file, `context-map.yaml`, `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `memory-bank/`, `SCRATCHPAD.md`, then drafts and
archives. `SCRATCHPAD.md` is transient unless marked `KEEP` or promoted.

## Project context files

High: `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`; highest when present: `.archcore/`. Medium-high: `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`. Medium: `memory-bank/`. Low:
`SCRATCHPAD.md`. On need only: `docs/history/` (rotated records, one folder per kind; `just history <term>`) and `docs/trackers/` (open items). Generated, never truth: `.ai-context/`. Full table:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/read-order-and-sources.md#project-context-files).

## Task routing

| Question               | Read first                                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------- |
| Architecture or design | `.archcore/adr/`, `.archcore/specs/`, `ARCHITECTURE.md`, `docs/`; never answer from the scratchpad alone |
| Planning or status     | `.archcore/plans/`, `ROADMAP.md`, `CHANGELOG.md`, `memory-bank/`; say so when they disagree              |
| Agents or governance   | `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`, `.archcore/rules/`                              |
| Implementation or code | `AGENTS.md`, `context-map.yaml`, `.archcore/specs/`, the source and its tests                            |
| Documentation          | `.archcore/`, `README.md`, `CHANGELOG.md`, `docs/`; leave companions consistent                          |

## Script and Task Navigation

`just --list` first, then `scripts/README.md`, then any other runner. Never run an uncatalogued script, or one marked `destructive`, `review-required` or `unknown`, without review; propose a catalogue
update when it is stale.

## Governance coherence checks

Run `just check` (or `scripts/check_governance.py`) before calling a durable change done and after adding, moving or retiring a file. When it fails, fix the project, not the check; a new artifact
class, generated output or restated constant extends the checker's registries in the same pass.

## Companion consistency

`AGENTS.md` goes with this file, `context-map.yaml` and `scripts/README.md`; a new script goes with `scripts/README.md`, `justfile` and the checker. `context-map.yaml` `update_rules` is authoritative
for this project.

## Drift handling

When files disagree: stop, name them, say which has higher authority, propose the smallest correction. Never merge conflicting assumptions silently.

## Update rules

Decision: `.archcore/adr/`. Rule: `.archcore/rules/` or `AGENTS.md`. Routing: this file and `context-map.yaml`. Any governance or navigation change: `CHANGELOG.md`. Records over budget: `just budget
--apply`. Full table: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/change-rules.md#update-rules).

## Generated context

`.ai-context/` packs help navigation and are never a source of truth; regenerate after large changes with `repomix --config repomix.config.json`.

## Context compaction recovery

Re-read this file, `.archcore/` and the newest `CHANGELOG.md` entries; check `SCRATCHPAD.md` against the memory backends; confirm companions agree. Steps:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#context-compaction-recovery).

## Audit procedure

`just check` and `just stale` cover the mechanical part; the ten manual checks are in the
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#audit-procedure).

## Agent answer contract

Cite file paths; never invent project state; say "not found in project context" when unsupported; separate confirmed facts from assumptions; ask only when required, otherwise proceed with stated
assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack routing

Mirrors `SKILL.md` for agents entering through this router. Core rules first, then the language file; the project's own rules outrank both.

| Task                                                                                       | Core reference                           | Then                                         |
| ------------------------------------------------------------------------------------------ | ---------------------------------------- | -------------------------------------------- |
| Shape a new module, package or service; choose layers; decide whether to build             | [references/design-principles.md](references/design-principles.md) | the language file                            |
| Reuse a proven design: resumable work, done ledger, partition before batch                   | [references/design-patterns.md](references/design-patterns.md) | the language file's realisation             |
| Compose an engine from several languages; who does what; the seams | [references/engine-composition.md](references/engine-composition.md) |
| Size, split, group into packages or name modules and functions; adopt a size budget on old code | [references/module-and-function-shape.md](references/module-and-function-shape.md) | `scripts/code_size.py`, `scripts/ratchet.py`, `scripts/module_groups.py` |
| Name files, identifiers, commands and recipes in any language | [references/naming-conventions.md](references/naming-conventions.md) | the language file |
| File headers, docstrings, doc comments, comments, lint suppression                         | [references/documentation-and-headers.md](references/documentation-and-headers.md) | `scripts/suppressions.py`, `scaffold.py`     |
| Anything that writes: files, databases, devices, remote systems; deletes; batches; renames | [references/safety-and-writes.md](references/safety-and-writes.md) | `scripts/write_gates.py`                     |
| Error types, exit codes, timeouts, retries, unknown third-party errors                     | [references/errors-and-timeouts.md](references/errors-and-timeouts.md) | `scripts/call_timeouts.py`, `group_timeouts.py` |
| Settings, paths, hosts, tokens, version pins, catalog data, config directives              | [references/configuration-and-literals.md](references/configuration-and-literals.md) |                                              |
| Tests, fakes, characterisation, negative tests for checks, real-target proof               | [references/testing.md](references/testing.md) | the language file's test runner              |
| Refactor, move code, shims, promote a script to a skill                                    | [references/refactoring-and-promotion.md](references/refactoring-and-promotion.md) |                                              |
| Jobs, loops and pages over many items; runtime budgets                                     | [references/efficiency-and-measurement.md](references/efficiency-and-measurement.md) |                                              |
| Generated files, renderers, drift checks, lock files                                       | [references/generated-artifacts.md](references/generated-artifacts.md) |                                              |
| Interpreters, venvs, task runner, scripts catalog                                          | [references/tooling-and-runtime.md](references/tooling-and-runtime.md) |                                              |
| Which environment runs this skill's helpers; projects importing skill code                 | [references/runtime-boundaries.md](references/runtime-boundaries.md) |                                              |
| Add, use or upgrade a dependency                                                           | [references/dependencies.md](references/dependencies.md) | [references/security.md](references/security.md) |
| Input, injection, secrets, least privilege, supply chain                                   | [references/security.md](references/security.md) | the language file's injection row            |
| Commits, change logs, versions, review, definition of done                                 | [references/version-control-and-review.md](references/version-control-and-review.md) |                                              |
| Closeout: record what this engagement taught                                               | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |                                              |

Language overrides: [languages/readme.md](languages/readme.md) indexes one file per language.
````

## File: CHANGELOG.md
````markdown
---
Title: skill-coder changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-coder pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Summary: Release history and governance changes of skill-coder; the release heading holds the version of record.
Last rotated: 20261119_1601
---

# Changelog

## Contents

- [Unreleased](#unreleased)
- [20261119_1601 — deterministic navigation-control upgrade](#20261119_1601--deterministic-navigation-control-upgrade)
- [20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records](#20261102_1347--learned-exit-trap-exit-code-ruff-through-a-symlink-tracker-from-records)
- [20261102_1132 — Learned: one write frame for many fields](#20261102_1132--learned-one-write-frame-for-many-fields)
- [20261101_2353 — Learned: guard first and dry-run a gate that hides records](#20261101_2353--learned-guard-first-and-dry-run-a-gate-that-hides-records)

---

## Unreleased

## 20261119_1601 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md

## 20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records

`languages/shell.md`, `languages/python.md`, `references/design-patterns.md` P-49, from ansible-wifi (2026-11-02).

## 20261102_1132 — Learned: one write frame for many fields

`references/design-patterns.md` P-48, from ansible-wifi (2026-11-02).

## 20261101_2353 — Learned: guard first and dry-run a gate that hides records

`references/testing.md`, from skill-knowledge-curator (2026-11-01).
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
````

## File: context-map.yaml
````yaml
# Machine-readable context map: this project's governance files, routing, update rules and generated outputs (skill-ai-it).
version: 1
project:
  name: skill-coder
  context_policy: AI_NAVIGATION.md is the human-readable router; this file is the
    machine-readable routing map.
bootstrap:
  required_first_read:
  - AGENTS.md
  - AI_NAVIGATION.md
  - context-map.yaml
  - CHANGELOG.md
authority_order:
- path: .archcore/adr
  type: architecture_decisions
  authority: highest
- path: .archcore/rules
  type: durable_rules
  authority: highest
- path: .archcore/specs
  type: design_contracts
  authority: highest
- path: .archcore/guides
  type: operating_guides
  authority: high
- path: .archcore/plans
  type: approved_plans
  authority: high
- path: AGENTS.md
  type: agent_instructions
  authority: high
- path: CLAUDE.md
  type: claude_specific_instructions
  authority: high
- path: AI_NAVIGATION.md
  type: context_router
  authority: high
- path: context-map.yaml
  type: machine_routing_map
  authority: high
- path: CHANGELOG.md
  type: project_history
  authority: medium_high
- path: ARCHITECTURE.md
  type: architecture_overview
  authority: medium_high
- path: ROADMAP.md
  type: roadmap
  authority: medium_high
- path: memory-bank/activeContext.md
  type: active_context
  authority: medium
- path: memory-bank/progress.md
  type: progress_state
  authority: medium
- path: memory-bank/decisionLog.md
  type: working_decision_log
  authority: medium
- path: SCRATCHPAD.md
  type: transient_notes
  authority: low
context_sources:
  archcore:
    enabled: true
    root: .archcore
    read_first_for:
    - architecture_decision
    - governance_rule
    - design_contract
    - implementation_plan
    - operating_procedure
    - durable_project_truth
  memory_bank:
    enabled: true
    root: memory-bank
    files:
      active_context: memory-bank/activeContext.md
      progress: memory-bank/progress.md
      decisions: memory-bank/decisionLog.md
      patterns: memory-bank/systemPatterns.md
      open_questions: memory-bank/openQuestions.md
  generated:
    graphify:
      enabled: true
      root: graphify-out
      preferred_files:
      - graphify-out/GRAPH_REPORT.md
      - graphify-out/graph.json
    repomix:
      enabled: true
      root: .ai-context
      preferred_files:
      - .ai-context/governance-pack.md
      - .ai-context/repo-pack.md
routing:
  architecture:
    description: Architecture, design, topology, components, boundaries, trade-offs.
    read:
    - .archcore/adr
    - .archcore/specs
    - ARCHITECTURE.md
    - architecture.md
    - docs/**/*.md
    avoid_as_authority:
    - SCRATCHPAD.md
    - scratchpad.md
  planning:
    description: Roadmap, work breakdown, current status, next steps.
    read:
    - .archcore/plans
    - .archcore/index.guide.md
    - ROADMAP.md
    - roadmap.md
    - CHANGELOG.md
    - memory-bank/progress.md
    - memory-bank/activeContext.md
    - SCRATCHPAD.md
  governance:
    description: Agent behaviour, project rules, file update rules, workflow rules.
    read:
    - AGENTS.md
    - CLAUDE.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md
    - .archcore/rules
    - .archcore/index.guide.md
  implementation:
    description: Code, scripts, configs, tests, automation.
    read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - .archcore/specs
    - .archcore/rules
    - src/**
    - scripts/**
    - tests/**
    tools:
      preferred:
      - serena
      - graphify
      - repomix
      optional:
      - semgrep
      - markdownlint
      - vale
  scripts:
    purpose: Project-local scripts, automation, task runners, and executable workflows.
    read_first:
    - justfile
    - Justfile
    - scripts/README.md
    - Taskfile.yml
    - Makefile
    - package.json
    generated_support:
    - graphify-out
    - .ai-context
    rules:
    - Respect existing canonical runner first.
    - Prefer just --list and just <task> when a justfile exists.
    - Read scripts/README.md before running raw scripts.
    - Treat uncataloged scripts as unknown safety.
    - Do not run destructive scripts without explicit review.
    - Run scripts/check_governance.py before claiming durable work complete; when
      it fails, fix the project, not the check.
  automation:
    purpose: Repeatable operational workflows and project task entrypoints.
    read_first:
    - justfile
    - Justfile
    - scripts/README.md
    - Taskfile.yml
    - Makefile
    - package.json
    - docs/automation.md
    rules:
    - Prefer cataloged commands.
    - Prefer just when a justfile exists.
    - Confirm inputs, outputs, side effects, and safety before execution.
  documentation:
    description: README, docs, architecture docs, user guides.
    read:
    - README.md
    - CHANGELOG.md
    - docs/**/*.md
    - ARCHITECTURE.md
    - architecture.md
    - .archcore/guides
    - .archcore/specs
    - memory-bank/activeContext.md
  troubleshooting:
    description: Issue investigation, debugging, root cause analysis.
    read:
    - memory-bank/activeContext.md
    - memory-bank/progress.md
    - SCRATCHPAD.md
    - scratchpad.md
    - docs/**/*.md
    - logs/**
    - reports/**
update_rules:
  durable_decision:
    update:
    - .archcore/adr
    also_consider:
    - ARCHITECTURE.md
    - architecture.md
    - memory-bank/decisionLog.md
  durable_rule:
    update:
    - .archcore/rules
    also_consider:
    - AGENTS.md
    - AI_NAVIGATION.md
  design_contract:
    update:
    - .archcore/specs
    also_consider:
    - ARCHITECTURE.md
    - architecture.md
    - docs/**/*.md
  operating_procedure:
    update:
    - .archcore/guides
    also_consider:
    - README.md
    - docs/**/*.md
  plan_change:
    update:
    - .archcore/plans
    - ROADMAP.md
    - roadmap.md
    - memory-bank/progress.md
  working_context_change:
    update:
    - memory-bank/activeContext.md
  temporary_note:
    update:
    - SCRATCHPAD.md
  routing_change:
    update:
    - AI_NAVIGATION.md
    - context-map.yaml
    - AGENTS.md
  governance_history:
    update:
    - CHANGELOG.md
  new_artifact_class:
    update:
    - scripts/check_governance.py
    also_consider:
    - AGENTS.md
    - scripts/README.md
  governance_navigation:
    AGENTS.md:
      companions:
      - AI_NAVIGATION.md
      - context-map.yaml
      - scripts/README.md
    AI_NAVIGATION.md:
      companions:
      - context-map.yaml
    context-map.yaml:
      companions:
      - AI_NAVIGATION.md
    scripts/README.md:
      companions:
      - AGENTS.md
      - context-map.yaml
    new_script_added:
      companions:
      - scripts/README.md
      - AGENTS.md
      - justfile
drift_policy:
  on_conflict:
    action: stop_and_report
    required_output:
    - conflicting_files
    - higher_authority_source
    - recommended_fix
    - assumptions
  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true
generated_context_policy:
  regenerate_after:
  - architecture_change
  - major_doc_change
  - roadmap_restructure
  - new_archcore_documents
  - significant_code_restructure
  commands:
    graphify: graphify update .
    repomix_governance: repomix --config repomix.config.json
audit_checks:
  governance_file_presence:
  - README.md
  - AGENTS.md
  - CLAUDE.md
  - AI_NAVIGATION.md
  - context-map.yaml
  - CHANGELOG.md
  version_consistency:
    description: Verify managed block version strings match current skill version.
    action: report_mismatch
  companion_update_completeness:
    description: When a governance file changes, verify all companion files in update_rules
      were also updated.
    action: report_missing
  generated_output_policy:
    description: Verify Graphify and Repomix outputs are classified as generated support,
      not canonical truth.
    action: report_violation
  task_runner_consistency:
    description: Verify cataloged tasks in scripts/README.md match actual script files.
    action: report_drift
  no_stale_references:
    description: Detect references to removed tools, old task runners, or superseded
      governance assumptions.
    action: report_stale
promotion_rules:
  archcore:
    allowed_init_modes:
    - bootstrap
    - navigation-add
    - refresh
    content_write_modes:
    - promote
    required_authorization: true
    candidates_report: ARCHCORE_PROMOTION_CANDIDATES.md
    extract_heuristics_source: patterns/archcore-routing.md
    exclusion:
    - CHANGELOG.md (history only)
    - generated files (.ai-context/, graphify-out/)
    - unmarked SCRATCHPAD sections
    - draft/obsolete roadmap items
context_recovery:
  procedure:
  - Read AI_NAVIGATION.md first for navigation map.
  - Load .archcore/ context if present (durable truth).
  - 'Graphify is disabled (operator, 2026-10-10): do not regenerate graphify-out/.'
  - 'Regenerate .ai-context/ with: repomix --config repomix.config.json'
  - Verify SCRATCHPAD.md has current state. If empty, populate from memory-keeper
    / mcp-project-context.
  - Verify CHANGELOG.md is current.
  - Verify AI_NAVIGATION.md and context-map.yaml companion consistency.
  evidence_label: Context recovered at <timestamp> via skill-ai-it context-recovery
    procedure.
answer_contract:
  require_source_paths: true
  unsupported_answer: not found in project context
  distinguish_assumptions: true
  do_not_invent_state: true
skill_ai_it_version: 2026-10-14-compact-v2
````

## File: justfile
````
# just task catalog for skill-coder.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-coder"
py := wc + "/.venv/bin/python"
ai_it := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py
    @just self-check
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root . --check
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root . --check
    @{{py}} scripts/language_split.py --check

# Language files over budget, or split one into a folder of topic files: just language-split [--lang <name> --apply]. Read-only by default
language-split *ARGS: _require-venv
    @{{py}} scripts/language_split.py {{ARGS}}

# Session preflight: list stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only.
stale: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root .

# Root governance files outside their roles (skill-ai-it references/governed-file-roles.md). Read-only.
roles: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root .

# One-step governance to the current skill-ai-it standard: adoption, budgets + check, role findings; content fixes: /skill-ai-it refresh. Modifies files
govern: _require-venv
    #!/usr/bin/env bash
    # Runtime budget: under 60 s on a governed project (measured 2026-10-14 in CHANGELOG); each step prints its own result.
    root="$(cd "." && pwd)" || exit 2
    start=$(date +%s)
    if [ "${GOVERN_ALLOW_DIRTY:-}" != "1" ]; then {{py}} "{{ai_it}}/scripts/checks/govern_guard.py" --project-root "$root" || exit 1; fi
    if grep -q "skill-ai-it-version" "$root/AI_NAVIGATION.md" 2>/dev/null; then
      nav="$(mktemp)"
      {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" --dry-run >"$nav" 2>&1
      if grep -qiE "REFUSED|re-serialised|legacy-layout|proposed" "$nav"; then echo "navigation blocks: upgrade needs review, run /skill-ai-it refresh"
      elif grep -q "would" "$nav"; then
        {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" | grep -E "^Changed files" || true
      fi
      rm -f "$nav"
    fi
    {{py}} "{{ai_it}}/scripts/adoption/adopt_governed_files.py" --project-root "$root" --apply || exit 1
    {{py}} "{{ai_it}}/scripts/adoption/adopt_code_map.py" --project-root "$root" --apply || exit 1
    log="$(mktemp)"; trap 'rm -f "$log"' EXIT; {{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root "$root" --apply | tee "$log"; rc=${PIPESTATUS[0]}
    {{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root "$root" --prune-baseline; {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root" --prune-baseline
    {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root"
    echo "govern: $(basename "$root") $([ $rc -eq 0 ] && echo OK || echo "NEEDS ATTENTION: $(grep -Eo 'UNFINISHED: .*|project check: FAILED|audit: (LOST|SPLIT)[^,]*' "$log" | head -1)") in $(( $(date +%s) - start ))s; content fixes: /skill-ai-it refresh"
    exit $rc

# Triage: one line per file (status, review date, summary) from its header, so a file is judged without being opened
docs *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/file_headers.py" --project-root . {{ARGS}}

# Rotated history on demand: `just history <term>` searches the CHANGELOG archives (SCRATCHPAD: `just history <term> SCRATCHPAD.md`)
history TERM RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --find "{{TERM}}" {{RECORD}}

# Print one rotated entry by its stamp, when a live entry cites it: `just history-show 20260918_1200`
history-show STAMP RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --show {{STAMP}} {{RECORD}}

# Keep CHANGELOG, SCRATCHPAD and ROADMAP within budget: plan by default; `just rotate --apply` (slurp runs `just budget`, which trims ROADMAP too)
rotate *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} CHANGELOG.md
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} SCRATCHPAD.md
    @{{py}} "{{ai_it}}/scripts/records/roadmap_trim.py" --project-root . {{ARGS}}

# Bring governed files within budget: normalise, rotate, move non-working-state sections out, audit, check. Plan by default; `--apply` to do it
budget *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root . {{ARGS}}

# Add a CHANGELOG entry in this project's own heading style and order, with its Contents line: plan by default, `--apply` to write
[positional-arguments]
changelog-entry *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/add_changelog_entry.py" --project-root . "$@"

# Move durable reference sections (anchors, procedures) out of a governed file into an on-need doc: plan by default, `--apply` to write
[positional-arguments]
move-sections *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/move_sections.py" --project-root . "$@"

# Large Markdown: each heading with its line range, so one section is read instead of the file: `just outline docs/x.md`. Read-only
[positional-arguments]
outline *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . outline "$@"

# Print one section by title, `Parent > Child` path or #anchor (exact by default, `~text` for a substring): `just section docs/x.md "Stage 1"`. Read-only
[positional-arguments]
section *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . section "$@"

# The pack's own offline contract + helper tests
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helper tests under every Python that mise has installed from 3.11 up: the helpers run with each target project's own interpreter
test-matrix:
    #!/usr/bin/env bash
    set -uo pipefail
    rc=0; ran=0
    for v in 3.11 3.12 3.13 3.14; do
      tool="python@$v"
      where=$(mise where "$tool" 2>/dev/null) || { echo "$tool: not installed through mise, NOT TESTED (mise install $tool)"; continue; }
      bin="$where/bin/python3"
      [ -x "$bin" ] || { echo "python $v: no interpreter at $bin, NOT TESTED"; continue; }
      ran=$((ran + 1))
      if "$bin" -m unittest discover -s tests -p 'test_*helpers.py' >/dev/null 2>&1; then echo "python $v: OK"; else echo "python $v: FAIL"; rc=1; fi
    done
    [ "$ran" -gt 0 ] || { echo "no interpreter from 3.11 up is installed through mise" >&2; exit 1; }
    exit $rc

# The helpers this pack ships (stdlib-only; run them with the target project's interpreter, or these recipes as the fallback)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Read-only: module and function sizes against the limits and a project's baseline, e.g. just code-size --project-root /path/to/project --list
[positional-arguments]
code-size *args: _require-venv
    @{{py}} scripts/code_size.py "$@"

# Read-only: Python calls to the network or a subprocess with no timeout, e.g. just call-timeouts --project-root /path/to/project --list
[positional-arguments]
call-timeouts *args: _require-venv
    @{{py}} scripts/call_timeouts.py "$@"

# Read-only: pgrep/pkill -f literal patterns not anchored with ^ (they can match the automation's own command line), e.g. just process-match --project-root /path --roots roles,scripts
[positional-arguments]
process-match *args: _require-venv
    @{{py}} scripts/process_match.py "$@"

# Read-only: prove a re-wrapped markdown file changed no table cell and no word, e.g. just reflow-lossless --git FILE --table-reflow <cli.mjs> --ignore-contents
[positional-arguments]
reflow-lossless *args: _require-venv
    @{{py}} scripts/reflow_lossless.py "$@"

# Read-only: V8 .cpuprofile files (VS Code extension host stalls) reduced to self time per extension, hot functions and stacks, e.g. just cpuprofile-summary $TMPDIR/exthost-*.cpuprofile
[positional-arguments]
cpuprofile-summary *args: _require-venv
    @{{py}} scripts/cpuprofile_summary.py "$@"

# Read-only: inline linter suppressions (noqa, type: ignore, shellcheck disable, eslint-disable, nolint, allow), e.g. just suppressions --project-root /path --list
[positional-arguments]
suppressions *args: _require-venv
    @{{py}} scripts/suppressions.py "$@"

# Read-only: timed subprocess calls whose command (ssh, a shell) starts children the timeout leaves running, e.g. just group-timeouts --project-root /path --list
[positional-arguments]
group-timeouts *args: _require-venv
    @{{py}} scripts/group_timeouts.py "$@"

# Read-only: print the skeleton of a new script and its test (writes nothing), e.g. just scaffold --lang python --name sync_x --summary "Sync X" --writes
[positional-arguments]
scaffold *args: _require-venv
    @{{py}} scripts/scaffold.py "$@"

# Read-only: entry points that write without --apply, e.g. just write-gates --project-root /path/to/project --config scripts/write-gates.json
[positional-arguments]
write-gates *args: _require-venv
    @{{py}} scripts/write_gates.py "$@"

# Read-only: Python import layers and cycles, e.g. just import-layers --project-root /path --package app --layers src/app/layers.toml
[positional-arguments]
import-layers *args: _require-venv
    @{{py}} scripts/import_layers.py "$@"

# Read-only: runnable scripts whose header lacks a summary, a run line or a safety statement, e.g. just script-headers --project-root /path --list
[positional-arguments]
script-headers *args: _require-venv
    @{{py}} scripts/script_headers.py "$@"

# Read-only: code file and recipe names against the naming mapping (naming.toml plus the project's [naming]), e.g. just naming-check --project-root /path --list
[positional-arguments]
naming-check *args: _require-venv
    @{{py}} scripts/naming_check.py "$@"

# Read-only, warn only: folders where three or more code files share a name prefix (candidate packages), e.g. just module-groups --project-root /path --strict
[positional-arguments]
module-groups *args: _require-venv
    @{{py}} scripts/module_groups.py "$@"

# Read-only: write-back entries a project parked for a skill (under a heading naming it), to promote, e.g. just write-back --project-root /path --strict
[positional-arguments]
write-back *args: _require-venv
    @{{py}} scripts/write_back.py "$@"

# Render the naming table in references/naming-conventions.md from naming.toml (modifies that file only)
naming-table: _require-venv
    @{{py}} scripts/naming_table.py --write

# The pack held to its own rules: sizes, timeouts (and process groups), suppressions, write gates, headers, names, and the naming table in step (each against its baseline in scripts/)
self-check: _require-venv
    @{{py}} scripts/code_size.py --project-root . --roots scripts,tests
    @{{py}} scripts/call_timeouts.py --project-root . --roots scripts,tests
    @{{py}} scripts/group_timeouts.py --project-root . --roots scripts,tests
    @{{py}} scripts/suppressions.py --project-root . --roots scripts,tests
    @{{py}} scripts/write_gates.py --project-root .
    @{{py}} scripts/script_headers.py --project-root . --roots scripts
    @{{py}} scripts/naming_check.py --project-root .
    @{{py}} scripts/naming_table.py
    @{{py}} scripts/module_groups.py --project-root . --roots scripts,tests --strict

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Run safe local preflight checks
preflight: runtimes audit-scripts test self-check check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/check_expected_diff.py" --project-root .

# Context map after an upgrade: key changes by content and comments lost vs a git ref (default HEAD); exit 1 while a comment is lost. Read-only
nav-check-context-map REF="HEAD": _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/yaml_key_diff.py" --project-root . --ref "{{REF}}"

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/selftest_blocks.py"
````

## File: Justfile
````
# just task catalog for skill-coder.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-coder"
py := wc + "/.venv/bin/python"
ai_it := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py
    @just self-check
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root . --check
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root . --check
    @{{py}} scripts/language_split.py --check

# Language files over budget, or split one into a folder of topic files: just language-split [--lang <name> --apply]. Read-only by default
language-split *ARGS: _require-venv
    @{{py}} scripts/language_split.py {{ARGS}}

# Session preflight: list stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only.
stale: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root .

# Root governance files outside their roles (skill-ai-it references/governed-file-roles.md). Read-only.
roles: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root .

# One-step governance to the current skill-ai-it standard: adoption, budgets + check, role findings; content fixes: /skill-ai-it refresh. Modifies files
govern: _require-venv
    #!/usr/bin/env bash
    # Runtime budget: under 60 s on a governed project (measured 2026-10-14 in CHANGELOG); each step prints its own result.
    root="$(cd "." && pwd)" || exit 2
    start=$(date +%s)
    if [ "${GOVERN_ALLOW_DIRTY:-}" != "1" ]; then {{py}} "{{ai_it}}/scripts/checks/govern_guard.py" --project-root "$root" || exit 1; fi
    if grep -q "skill-ai-it-version" "$root/AI_NAVIGATION.md" 2>/dev/null; then
      nav="$(mktemp)"
      {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" --dry-run >"$nav" 2>&1
      if grep -qiE "REFUSED|re-serialised|legacy-layout|proposed" "$nav"; then echo "navigation blocks: upgrade needs review, run /skill-ai-it refresh"
      elif grep -q "would" "$nav"; then
        {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" | grep -E "^Changed files" || true
      fi
      rm -f "$nav"
    fi
    {{py}} "{{ai_it}}/scripts/adoption/adopt_governed_files.py" --project-root "$root" --apply || exit 1
    {{py}} "{{ai_it}}/scripts/adoption/adopt_code_map.py" --project-root "$root" --apply || exit 1
    log="$(mktemp)"; trap 'rm -f "$log"' EXIT; {{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root "$root" --apply | tee "$log"; rc=${PIPESTATUS[0]}
    {{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root "$root" --prune-baseline; {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root" --prune-baseline
    {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root"
    echo "govern: $(basename "$root") $([ $rc -eq 0 ] && echo OK || echo "NEEDS ATTENTION: $(grep -Eo 'UNFINISHED: .*|project check: FAILED|audit: (LOST|SPLIT)[^,]*' "$log" | head -1)") in $(( $(date +%s) - start ))s; content fixes: /skill-ai-it refresh"
    exit $rc

# Triage: one line per file (status, review date, summary) from its header, so a file is judged without being opened
docs *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/file_headers.py" --project-root . {{ARGS}}

# Rotated history on demand: `just history <term>` searches the CHANGELOG archives (SCRATCHPAD: `just history <term> SCRATCHPAD.md`)
history TERM RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --find "{{TERM}}" {{RECORD}}

# Print one rotated entry by its stamp, when a live entry cites it: `just history-show 20260918_1200`
history-show STAMP RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --show {{STAMP}} {{RECORD}}

# Keep CHANGELOG, SCRATCHPAD and ROADMAP within budget: plan by default; `just rotate --apply` (slurp runs `just budget`, which trims ROADMAP too)
rotate *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} CHANGELOG.md
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} SCRATCHPAD.md
    @{{py}} "{{ai_it}}/scripts/records/roadmap_trim.py" --project-root . {{ARGS}}

# Bring governed files within budget: normalise, rotate, move non-working-state sections out, audit, check. Plan by default; `--apply` to do it
budget *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root . {{ARGS}}

# Add a CHANGELOG entry in this project's own heading style and order, with its Contents line: plan by default, `--apply` to write
[positional-arguments]
changelog-entry *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/add_changelog_entry.py" --project-root . "$@"

# Move durable reference sections (anchors, procedures) out of a governed file into an on-need doc: plan by default, `--apply` to write
[positional-arguments]
move-sections *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/move_sections.py" --project-root . "$@"

# Large Markdown: each heading with its line range, so one section is read instead of the file: `just outline docs/x.md`. Read-only
[positional-arguments]
outline *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . outline "$@"

# Print one section by title, `Parent > Child` path or #anchor (exact by default, `~text` for a substring): `just section docs/x.md "Stage 1"`. Read-only
[positional-arguments]
section *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . section "$@"

# The pack's own offline contract + helper tests
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helper tests under every Python that mise has installed from 3.11 up: the helpers run with each target project's own interpreter
test-matrix:
    #!/usr/bin/env bash
    set -uo pipefail
    rc=0; ran=0
    for v in 3.11 3.12 3.13 3.14; do
      tool="python@$v"
      where=$(mise where "$tool" 2>/dev/null) || { echo "$tool: not installed through mise, NOT TESTED (mise install $tool)"; continue; }
      bin="$where/bin/python3"
      [ -x "$bin" ] || { echo "python $v: no interpreter at $bin, NOT TESTED"; continue; }
      ran=$((ran + 1))
      if "$bin" -m unittest discover -s tests -p 'test_*helpers.py' >/dev/null 2>&1; then echo "python $v: OK"; else echo "python $v: FAIL"; rc=1; fi
    done
    [ "$ran" -gt 0 ] || { echo "no interpreter from 3.11 up is installed through mise" >&2; exit 1; }
    exit $rc

# The helpers this pack ships (stdlib-only; run them with the target project's interpreter, or these recipes as the fallback)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Read-only: module and function sizes against the limits and a project's baseline, e.g. just code-size --project-root /path/to/project --list
[positional-arguments]
code-size *args: _require-venv
    @{{py}} scripts/code_size.py "$@"

# Read-only: Python calls to the network or a subprocess with no timeout, e.g. just call-timeouts --project-root /path/to/project --list
[positional-arguments]
call-timeouts *args: _require-venv
    @{{py}} scripts/call_timeouts.py "$@"

# Read-only: pgrep/pkill -f literal patterns not anchored with ^ (they can match the automation's own command line), e.g. just process-match --project-root /path --roots roles,scripts
[positional-arguments]
process-match *args: _require-venv
    @{{py}} scripts/process_match.py "$@"

# Read-only: prove a re-wrapped markdown file changed no table cell and no word, e.g. just reflow-lossless --git FILE --table-reflow <cli.mjs> --ignore-contents
[positional-arguments]
reflow-lossless *args: _require-venv
    @{{py}} scripts/reflow_lossless.py "$@"

# Read-only: V8 .cpuprofile files (VS Code extension host stalls) reduced to self time per extension, hot functions and stacks, e.g. just cpuprofile-summary $TMPDIR/exthost-*.cpuprofile
[positional-arguments]
cpuprofile-summary *args: _require-venv
    @{{py}} scripts/cpuprofile_summary.py "$@"

# Read-only: inline linter suppressions (noqa, type: ignore, shellcheck disable, eslint-disable, nolint, allow), e.g. just suppressions --project-root /path --list
[positional-arguments]
suppressions *args: _require-venv
    @{{py}} scripts/suppressions.py "$@"

# Read-only: timed subprocess calls whose command (ssh, a shell) starts children the timeout leaves running, e.g. just group-timeouts --project-root /path --list
[positional-arguments]
group-timeouts *args: _require-venv
    @{{py}} scripts/group_timeouts.py "$@"

# Read-only: print the skeleton of a new script and its test (writes nothing), e.g. just scaffold --lang python --name sync_x --summary "Sync X" --writes
[positional-arguments]
scaffold *args: _require-venv
    @{{py}} scripts/scaffold.py "$@"

# Read-only: entry points that write without --apply, e.g. just write-gates --project-root /path/to/project --config scripts/write-gates.json
[positional-arguments]
write-gates *args: _require-venv
    @{{py}} scripts/write_gates.py "$@"

# Read-only: Python import layers and cycles, e.g. just import-layers --project-root /path --package app --layers src/app/layers.toml
[positional-arguments]
import-layers *args: _require-venv
    @{{py}} scripts/import_layers.py "$@"

# Read-only: runnable scripts whose header lacks a summary, a run line or a safety statement, e.g. just script-headers --project-root /path --list
[positional-arguments]
script-headers *args: _require-venv
    @{{py}} scripts/script_headers.py "$@"

# Read-only: code file and recipe names against the naming mapping (naming.toml plus the project's [naming]), e.g. just naming-check --project-root /path --list
[positional-arguments]
naming-check *args: _require-venv
    @{{py}} scripts/naming_check.py "$@"

# Read-only, warn only: folders where three or more code files share a name prefix (candidate packages), e.g. just module-groups --project-root /path --strict
[positional-arguments]
module-groups *args: _require-venv
    @{{py}} scripts/module_groups.py "$@"

# Read-only: write-back entries a project parked for a skill (under a heading naming it), to promote, e.g. just write-back --project-root /path --strict
[positional-arguments]
write-back *args: _require-venv
    @{{py}} scripts/write_back.py "$@"

# Render the naming table in references/naming-conventions.md from naming.toml (modifies that file only)
naming-table: _require-venv
    @{{py}} scripts/naming_table.py --write

# The pack held to its own rules: sizes, timeouts (and process groups), suppressions, write gates, headers, names, and the naming table in step (each against its baseline in scripts/)
self-check: _require-venv
    @{{py}} scripts/code_size.py --project-root . --roots scripts,tests
    @{{py}} scripts/call_timeouts.py --project-root . --roots scripts,tests
    @{{py}} scripts/group_timeouts.py --project-root . --roots scripts,tests
    @{{py}} scripts/suppressions.py --project-root . --roots scripts,tests
    @{{py}} scripts/write_gates.py --project-root .
    @{{py}} scripts/script_headers.py --project-root . --roots scripts
    @{{py}} scripts/naming_check.py --project-root .
    @{{py}} scripts/naming_table.py
    @{{py}} scripts/module_groups.py --project-root . --roots scripts,tests --strict

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Run safe local preflight checks
preflight: runtimes audit-scripts test self-check check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/check_expected_diff.py" --project-root .

# Context map after an upgrade: key changes by content and comments lost vs a git ref (default HEAD); exit 1 while a comment is lost. Read-only
nav-check-context-map REF="HEAD": _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/yaml_key_diff.py" --project-root . --ref "{{REF}}"

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/selftest_blocks.py"
````

## File: README.md
````markdown
---
Title: skill-coder
Category: folder-index
Status: current
Authority: local-supplement
Scope: skill-coder pack — language-agnostic programming practice with per-language overrides and stdlib checkers
Last reviewed: 2026-11-19
Summary: Entry index for skill-coder, with what the pack is for, its folders and key files, and where governance lives.
Budget: 200 lines, 25 KB
---

# skill-coder

Canonical, cross-project pack for writing, changing, reviewing and refactoring code in any language. The rules are language-agnostic; files under `languages/` tighten, loosen (with a reason) or map
them to each language's tools; a project's own rules outrank both.

## Purpose

Reusable, evidence-graded programming practice for any project, current or future, distilled from the operator's governed projects (rules first proven in unified-network-controller) and primary
sources. The pack also ships stdlib checkers that hold a project to the rules: they run with the project's own interpreter and read its `code-map.toml`.

## Quick start

- Using the skill in a project: invoke `skill-coder`; it reads the project's own rules first, then routes from [SKILL.md](SKILL.md).
- Running a checker against a project: `<project python> <this pack>/scripts/code_size.py --project-root . --list` (any helper; see [scripts/README.md](scripts/README.md)); copy [templates/code-map.toml](templates/code-map.toml) to the project root
  to set its decisions.
- Working on the pack: `just bootstrap` once, then `just test` and `just check` before calling a change complete. Full setup: [SETUP.md](SETUP.md).

## Folder index

- [references/](references/) — one focused file per topic; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [languages/](languages/) — per-language overrides. Index: [languages/readme.md](languages/readme.md)
- [scripts/](scripts/) — the checkers and the pack's governance checker. Index: [scripts/README.md](scripts/README.md)
- [templates/](templates/) — `code-map.toml` for a project to copy
- [tests/](tests/) — contract and helper tests, scenarios
- [documents/](documents/) — research sources pulled verbatim, with their index
- [docs/history/](docs/history/) — rotated CHANGELOG and ROADMAP records (`just history <term>`). Index: [docs/history/readme.md](docs/history/readme.md)

## Key files

| File          | Role                                                                      |
| ------------- | ------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, routing, write-back contract        |
| [sources.yaml](sources.yaml) | Claim ledger with evidence labels                                         |
| [code-map.toml](code-map.toml) | This pack's own code decisions (it is held to its own rules)              |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record                                        |
| [ROADMAP.md](ROADMAP.md) | Current phase and open milestones; done items rotate to `docs/history/`   |
| [SETUP.md](SETUP.md) | Prerequisites, bootstrap, use from a project, troubleshooting             |
| [justfile](justfile) | Task catalog: `just --list`; `just test` and `just check` gate completion |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: roadmap.md
````markdown
---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-coder
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-11-19
---

# Roadmap — skill-coder

## Current phase

**2026-11-19.** Version 0.1.0 is built and installed (Claude, Codex, Hermes) and has been the default for code work since 2026-10-20 (global `~/.agents/AGENTS.md` names it for any code; history: `just
history "Made the default"`). Projects write back to it regularly. skill-drawio is built to its rules. Open work is skill-ai-it calling the helpers, adoption in unified-network-controller, the red
write-back contract test, and the evidence gaps below.

## Activation

- [ ] **skill-ai-it calls these helpers** — after activation, skill-ai-it's code checks call this pack's helpers, so each rule has one source.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **Per-root package naming** — `import_layers.py --graph` names packages by top folder; UNC's graph names them per root (`under`/`self`), 16 packages against
  29. Add the option (or a roots table in `code-map.toml`), match UNC's report, then UNC's `scripts/checks/import_graph.py` retires.
- [ ] **Write gates** — decide whether local file writes count as writes (`write_gates.py` found none in skill-drawio although `--write`/`--apply` write files; on UNC it flagged a capture script UNC's
  own check does not see). Then UNC's patterns and register move into a `--config` file.
- [ ] **Baselines** — UNC adopts the helpers with recorded baselines (`--write-baseline`) and a `code-map.toml`, so existing findings do not turn `just check` red.

## Evidence and languages

- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (the declared floor is untested).
- [ ] **Shell limits** — the 100-line warn is now sourced (`documents/research-sources-20261019/google-shell-style.txt` line 53, "more than 100 lines long"); the 200-line fail in `code_size.py`
  `LANG_LIMITS` has no source: record it as the pack's own decision or find one (reviewed 2026-11-19).
- [ ] **Write-back contract test red (found 2026-11-12, enterprise-strategy closeout)** — `tests/test_package_contract.py` test_write_back_entries_logged stops on 13 Learned entries written 2026-10-30
  to 2026-11-12 (languages/ansible/learned-templating.md 90 and 139; languages/python/learned-other.md 119; languages/shell/learned-other.md 22; references/design-patterns.md 1040, 1424, 1459, 1661,
  1686; design-principles.md 48; engine-composition.md 188; testing.md 313 and 318; tooling-and-runtime.md 81). Some look well formed, so check the parser's header join (six lines, " ·" at a line end)
  before rewriting entries. design-patterns.md P-65 (2026-11-10) only lacked its `· Source:` field and was fixed in the same closeout. **State 2026-11-19 (full scan, not first failure):** 13 malformed
  headers (languages/rust.md 61, `(recurred)` is not a one-letter suffix; design-patterns.md 1101, 1119, 1330, 1344, 1362, 1382; design-principles.md 48; engine-composition.md 162;
  generated-artifacts.md 97; refactoring-and-promotion.md 135; testing.md 304; tooling-and-runtime.md 99) and 6 entries with no CHANGELOG line (design-patterns.md 2026-11-05 ×2, errors-and-timeouts.md
  2026-11-10, generated-artifacts.md 2026-11-12, security.md 2026-11-09 ×2). testing.md also repeats labels (2026-10-20 (b), 2026-11-02, 11-08, 11-09, 11-18 twice each). Line numbers drift; rescan
  before fixing.
- [ ] **Ansible and YAML size** — `code_size.py` measures no `.yml` files; decide a task-file limit once `languages/ansible.md` has a source.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
````

## File: ROADMAP.md
````markdown
---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-coder
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-11-19
---

# Roadmap — skill-coder

## Current phase

**2026-11-19.** Version 0.1.0 is built and installed (Claude, Codex, Hermes) and has been the default for code work since 2026-10-20 (global `~/.agents/AGENTS.md` names it for any code; history: `just
history "Made the default"`). Projects write back to it regularly. skill-drawio is built to its rules. Open work is skill-ai-it calling the helpers, adoption in unified-network-controller, the red
write-back contract test, and the evidence gaps below.

## Activation

- [ ] **skill-ai-it calls these helpers** — after activation, skill-ai-it's code checks call this pack's helpers, so each rule has one source.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **Per-root package naming** — `import_layers.py --graph` names packages by top folder; UNC's graph names them per root (`under`/`self`), 16 packages against
  29. Add the option (or a roots table in `code-map.toml`), match UNC's report, then UNC's `scripts/checks/import_graph.py` retires.
- [ ] **Write gates** — decide whether local file writes count as writes (`write_gates.py` found none in skill-drawio although `--write`/`--apply` write files; on UNC it flagged a capture script UNC's
  own check does not see). Then UNC's patterns and register move into a `--config` file.
- [ ] **Baselines** — UNC adopts the helpers with recorded baselines (`--write-baseline`) and a `code-map.toml`, so existing findings do not turn `just check` red.

## Evidence and languages

- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (the declared floor is untested).
- [ ] **Shell limits** — the 100-line warn is now sourced (`documents/research-sources-20261019/google-shell-style.txt` line 53, "more than 100 lines long"); the 200-line fail in `code_size.py`
  `LANG_LIMITS` has no source: record it as the pack's own decision or find one (reviewed 2026-11-19).
- [ ] **Write-back contract test red (found 2026-11-12, enterprise-strategy closeout)** — `tests/test_package_contract.py` test_write_back_entries_logged stops on 13 Learned entries written 2026-10-30
  to 2026-11-12 (languages/ansible/learned-templating.md 90 and 139; languages/python/learned-other.md 119; languages/shell/learned-other.md 22; references/design-patterns.md 1040, 1424, 1459, 1661,
  1686; design-principles.md 48; engine-composition.md 188; testing.md 313 and 318; tooling-and-runtime.md 81). Some look well formed, so check the parser's header join (six lines, " ·" at a line end)
  before rewriting entries. design-patterns.md P-65 (2026-11-10) only lacked its `· Source:` field and was fixed in the same closeout. **State 2026-11-19 (full scan, not first failure):** 13 malformed
  headers (languages/rust.md 61, `(recurred)` is not a one-letter suffix; design-patterns.md 1101, 1119, 1330, 1344, 1362, 1382; design-principles.md 48; engine-composition.md 162;
  generated-artifacts.md 97; refactoring-and-promotion.md 135; testing.md 304; tooling-and-runtime.md 99) and 6 entries with no CHANGELOG line (design-patterns.md 2026-11-05 ×2, errors-and-timeouts.md
  2026-11-10, generated-artifacts.md 2026-11-12, security.md 2026-11-09 ×2). testing.md also repeats labels (2026-10-20 (b), 2026-11-02, 11-08, 11-09, 11-18 twice each). Line numbers drift; rescan
  before fixing.
- [ ] **Ansible and YAML size** — `code_size.py` measures no `.yml` files; decide a task-file limit once `languages/ansible.md` has a source.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
````

## File: SCRATCHPAD.md
````markdown
---
Title: skill-coder scratchpad
Category: state
Status: current
Authority: local-supplement
Scope: Working state of the skill-coder pack between sessions
Last reviewed: 2026-10-19
Kind: state
Budget: 200 lines, 25 KB
Keep: KEEP-marked items only
Open items tracker: docs/trackers/open-items-20261119_1559.md
Summary: Transient working state for skill-coder; durable facts move to references, sources.yaml or CHANGELOG.
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261107_1723
---

# Scratchpad

## Open items

- KEEP enforcement of skill-coder on every code change (operator, 2026-11-11, unified-network-controller session: "shouldn't we be making it
  mandatory that whenever any code change needs to happen, skill coder should be used"; all four layers chosen, built in a dedicated session).
  Today a hook only checks that skill-coder was loaded, not that the code follows it; that session wrote two scripts and a plan's script
  excerpts with four-space indentation, a 51-line function and five logic bugs before checks and a review caught them. Build, smallest first:
  (1) lint code in documents: skill-ai-it `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/scripts/markdown/md_examples_check.py` also runs the project's formatter and lint on Python excerpts;
  (2) the load gate in every repo: UNC's `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/registries/skill-domains.json` code rule (`.py`, `.sh`, `.js`, `.ts`, justfile) moved to the
  governance hooks so skills_stuff, tools and every project get it; (3) a check on each code write: a PostToolUse hook runs the fast
  checkers (`ruff format --check` with the project's config, `script_headers`, `call_timeouts`, `code_size`) on the written file and shows the
  findings to the agent (a settings change: show it before applying); (4) skill-coder checks in every project's `just check`, a Core item of
  skill-ai-it's central tooling plan, rolled out in its waves. Feedback memory: `/Volumes/Data/_ai/claude-auto-memory/feedback_skill_coder_before_code.md`.
- KEEP design-patterns.md follow-ups (2026-10-27): (1) all twelve patterns are `reusable_candidate`: when a second project uses one, cite it and
  raise the evidence (falsifiers are in each header); (2) P-05 is CANDIDATE until ansible-wifi applies `plans/smc-change-resume-20261027_1038/
  prepare-once.patch` and its canary passes; (3) harvest patterns from other projects (operator: "all the out of the box thinking"):
  DONE for unified-network-controller and smc-resiliency (P-13 to P-29, 2026-10-27; P-02, P-10, P-15 now in two projects); still to
  harvest: skill-drawio (data-first diagrams with drift check), skill-ai-it (governed-file budgets and rotation); (4) Python column has two suggested rows (P-05, P-06): move to built when a project does.
- KEEP Activation DONE 2026-10-20 (operator: "if you are now happy with skill-coder, promote it as well"; all four steps below, in one pass).
  Was PENDING until the pack is tested (operator, 2026-10-19: "make it default once we have tested the skill"). Then, in one pass:
  1. global policy `~/.agents/AGENTS.md`, "Skills, context, and task routing": "for any code use `skill-coder`" beside `safe-change-validation`; re-run
     `/Volumes/Data/_ai/governance/scripts/sync-codex-agents.sh` so `~/.codex/AGENTS.md` carries it; 2. DONE 2026-10-19 (operator: "install it as skill but dont make it default yet"): directory
     symlinks into `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` and the skills_stuff `README.md` row;
     3. still to do with the default: `/Volumes/Data/_ai/_skills/skills_stuff/.agents/skill-surfaces.md` row, and restore the broad `SKILL.md` trigger
     ("Use before writing, changing, reviewing or refactoring code in any project"; narrowed to invoke-by-name until activation, operator 2026-10-19);
  4. `/Volumes/Data/_ai/governance/categories/coding-guide.md` links skill-coder as its detailed pack (check `/Volumes/Data/_ai/governance/sync-map.yaml`). Later, separately: skill-ai-it's code checks
     call skill-coder's helpers (one source per rule).

- Done 2026-10-20: unified-network-controller adopted `code-map.toml` (layers, write gates, module statuses). Open: its check scans Python only; `write_gates.py`
  also flags its shell backup runner (the config-backup shell script). Baselines (`--write-baseline`) not yet adopted there.
````
