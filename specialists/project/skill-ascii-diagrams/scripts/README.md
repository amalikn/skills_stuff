---
Title: Script inventory — skill-ascii-diagrams
Category: catalogue
Status: current
Authority: canonical
Scope: Every script and task in skill-ascii-diagrams with inputs, outputs and safety
Last reviewed: 2026-11-17
Summary: >-
  Two front ends (draw from a spec, fix existing diagrams) and the `ascii` package they share; all stdlib Python 3.11 or later, read-only unless `--apply`.
---

# Script inventory

Run the front ends through this pack's recipes (`just ascii-flow-render`, `just ascii-fix`; `just bootstrap` once) or, from a project, with the project's interpreter by path: `<python> <this
pack>/scripts/ascii_fix.py docs/design.md`. Moved from skill-drawio on 2026-11-17 (operator: its own skill).

## Task inventory

| Task                     | Purpose                                                                    | Inputs       | Outputs            | Safety           | Idempotent | When to use              |
| ------------------------ | -------------------------------------------------------------------------- | ------------ | ------------------ | ---------------- | ---------- | ------------------------ |
| `just ascii-flow-render` | `scripts/ascii_flow_render.py`: draw a diagram from a JSON spec (chain,    | a JSON spec  | diagram on stdout  | `safe`           | Yes        | A new diagram for        |
|                          |   grid, box, text, columns)                                                |              |                    |                  |            |   a document             |
| `just ascii-fix`         | `scripts/ascii_fix.py`: repair existing diagrams; diff by default,         | Markdown or  | diff and findings; | `write-gated`    | Yes        | A drawn diagram drifted  |
|                          |   `--apply` writes, never a GENERATED file                                 |   plain-text |   the file         |                  |            |                          |
|                          |                                                                            |   files      |   with `--apply`   |                  |            |                          |
|                          |   (`--check`: a read-only gate, exit 1 when a diagram would change)        |              |                    |                  |            |                          |
| `just test`              | unit and contract tests                                                    | `tests/`     | console            | `safe`           | Yes        | Before calling a         |
|                          |                                                                            |              |                    |                  |            |   change done            |
| `just lint`              | ruff check and format check                                                | the pack     | console            | `safe`           | Yes        | Part of `just check`     |
| `just check`             | doc freshness, roles, pack contract, lint                                  | the pack     | console,           | `safe`           | Yes        | Before a commit          |
|                          |                                                                            |              |   exit status      |                  |            |                          |
| `just bootstrap`         | the pack's venv in the skills working cache                                | `.mise.toml` | venv outside       | `modifies-files` | Yes        | First use                |
|                          |                                                                            |              |   the repo         |                  |            |                          |

## Raw script inventory

| Script                         | Purpose                                                                                                                                             | Safety        |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `scripts/ascii_flow_render.py` | Front end: ASCII flow diagrams for Markdown from a JSON spec                                                                                        | `safe`        |
| `scripts/ascii_fix.py`         | Front end: repairs existing ASCII diagrams at their edges; read-only unless `--apply`; refuses GENERATED files                                      | `write-gated` |
| `scripts/ascii/__init__.py`    | Package `ascii`: shared logic of the front ends                                                                                                     | `safe`        |
| `scripts/ascii/checks.py`      | Checks and connector snapping: wide characters and tabs, arrows missing their box, straying connectors (ideas from box-diagram and asciiflow,       | `safe`        |
|                                |   both MIT)                                                                                                                                         |               |
