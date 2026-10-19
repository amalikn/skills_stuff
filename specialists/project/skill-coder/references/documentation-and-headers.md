---
Title: Documentation and headers
Category: reference
Status: current
Authority: local-supplement
Scope: File purpose headers, docstrings or doc comments with Args, Returns and Raises, and comments that explain why
Last reviewed: 2026-10-19
Summary: >-
  Every file states its purpose in its native header; every module, class and function documents its parameters, what it
  returns and when it raises; comments explain why, not what; enforced by a docstring ratchet.
---

# Documentation and headers

## File purpose headers

Every file states its purpose in its type's native header, so a reader can judge it without reading the body. Why: an agent triages a folder from headers (operator standard, governance
`naming-and-file-summary-guide.md`; a governed project's rule R35).

| File type                               | Native header                                                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Python                                  | Module docstring                                                                                               |
| Shell, YAML, TOML, Dockerfile, justfile | Leading `#` comment block                                                                                      |
| Go                                      | Package comment (`// Package x ...`) in one file of the package                                                |
| Rust                                    | Crate or module inner doc comment (`//!`)                                                                      |
| JavaScript and TypeScript               | Leading `/** ... */` file comment (`@file` or `@packageDocumentation`)                                         |
| SQL                                     | Leading `--` comment block                                                                                     |
| JSON (no comments allowed)              | A `_meta` object with `purpose` where the consumer tolerates an extra key; otherwise a sibling `readme.md` row |
| Markdown                                | Front matter (Title, Category, Status, Authority, Scope, Last reviewed, Summary)                               |

The module header says what the file is for, why it exists (the decision or incident behind it), what it reads and writes, and how it is run (a `Usage:` block with real command lines). Why: a reader
should not need the code to know whether running it is safe.

Canonical sources for these rules: governance [`coding-guide.md`](/Volumes/Data/_ai/governance/categories/coding-guide.md) (2026-10-07) and
[`naming-and-file-summary-guide.md`](/Volumes/Data/_ai/governance/categories/naming-and-file-summary-guide.md) "Code docstrings" (2026-10-08); this file restates
them and links there rather than diverging. A script that takes inputs (flags, environment variables, arguments) has an `Inputs:` section in its header with a
concrete usage example immediately after it (coding-guide). Why: the operator sees the parameter surface and a valid invocation together.

## Docstrings and doc comments

Operator standard for every script created or changed in any repo (2026-10-08):

- **Class and function:** a one-line summary, then
  - `Args:` naming every parameter (not `self` or `cls`), what it holds and its accepted values;
  - `Returns:` what comes back and its shape, and what an empty or null result means;
  - `Raises:` when it raises or exits (for example `SystemExit` with the condition).
- Nested helpers follow the same rule. A function with no parameters and no return value needs only the summary.
- Shell functions carry the same content in a comment block above the function.
- Say what it does and gives back in plain terms; do not restate the type annotation alone, and do not open with "this function".

Each language has its own spelling of these sections (Google-style for Python, `@param`/`@returns`/`@throws` for TSDoc and JSDoc, `# Errors` and `# Panics` headings for Rust, sentences for Go). The
language override names it. Why: the content is fixed; the syntax follows the language's tools.

Every new layer, contract or service names its consumers in its docstring. Why: an abstraction must show it was earned ([design-principles.md](design-principles.md)).

## Comments

- A comment explains why: the constraint, the incident, the trade-off. The code already says what. Why: a "what" comment goes stale silently.
- A workaround names the upstream issue or version it works around and the condition for removing it. Why: otherwise it outlives its cause.
- Never silence a linter with an inline suppression (`# noqa`, `// eslint-disable-line`, `#[allow]` on one line, `# shellcheck disable`) to make a check pass. Fix the cause: rename, refactor,
  configure the rule project-wide with a reason. Why: the operator rejected inline suppression (lesson, recorded in auto-memory `feedback_no_noqa`). A language override may name the rare legitimate
  case (generated code, a false positive filed upstream) and how to record it.

## Enforcement: the docstring ratchet

A project's governance check parses every source file and counts, per file, docstrings that are absent, lack a parameter under `Args:`, or lack `Returns:` for a function that returns a value. A
baseline records the counts on adoption day; a new file must be at zero; a count may never rise; a count that falls is written into the baseline in the same change. Why: legacy code does not block
work and the debt only falls (first implemented in a governed project's `check_docstrings` with `docstring-baseline.json`).

## Long documents

Design and plan documents use tables and ASCII diagrams where they help; a Mermaid diagram keeps an ASCII version beside it. A staged plan gives every stage a target, prerequisites, steps, a
completion checklist and rollback. Why: plain text renders everywhere, and a stage without rollback is a one-way door.
