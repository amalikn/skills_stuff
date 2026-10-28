---
Title: Setup — skill-coder
Category: setup
Status: current
Authority: canonical
Scope: Installing and running skill-coder, both as a pack under development and its helpers against a project
Last reviewed: 2026-10-28
Summary: >-
  A working setup needs mise, just and Python 3.11 or later; the helpers are stdlib-only and run with the target project's own interpreter, and the pack's
  venv in the skills working cache is only for its own recipes and fallback runs.
Depends on: justfile, .mise.toml, requirements.txt, templates/code-map.toml
---

# Setup — skill-coder

## Contents

- [Prerequisites](#prerequisites)
- [Bootstrap](#bootstrap)
- [Using it from a project](#using-it-from-a-project)
- [Environment](#environment)
- [First run](#first-run)
- [Troubleshooting](#troubleshooting)

## Prerequisites

| Tool   | Version                                                 | Pinned in                                          | Needed for                                                                   |
| ------ | ------------------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------- |
| mise   | any current                                             | -                                                  | Installing the pinned Python (`just bootstrap`, `just test-matrix`)          |
| just   | any current                                             | -                                                  | The task catalog (`just --list`)                                             |
| Python | 3.14 for the pack's venv; 3.11 or later for the helpers | `.mise.toml`; `REQUIRES_PYTHON = (3, 11)` in       | Everything; 3.11 is the floor because `code-map.toml` is read with `tomllib` |
|        |                                                         |   the helpers                                      |                                                                              |
| PyYAML | 6.0.3                                                   | `tests/requirements.txt` (via `requirements.txt`)  | The pack's contract test only; the helpers are stdlib-only                   |

## Bootstrap

`just bootstrap` (once), then `just test` and `just check`. Bootstrap copies `.mise.toml` into the working cache `/Volumes/Data/_ai/_skills/skills-working-cache/skill-coder`, installs the pinned
Python there, builds `.venv` and installs `requirements.txt`. Nothing is installed into the pack folder. `just test-matrix` runs the helper tests under every Python from 3.11 that mise has installed
and names the ones it could not test.

## Using it from a project

The skill is installed as directory symlinks back to this folder: `~/.claude/skills/skill-coder`, `~/.codex/skills/skill-coder` and `~/.hermes/skills/domain/skill-coder`. It is invoked by name until
it is made the default ([ROADMAP.md](ROADMAP.md)).

- Run a helper with the project's own interpreter, from the project root: `<project python> <this pack>/scripts/code_size.py --project-root . --list` (any helper; catalogue in
  [scripts/README.md](scripts/README.md)). Nothing is installed into the project.
- Copy [templates/code-map.toml](templates/code-map.toml) to the project root to record its decisions (scan roots, limits, layers, naming exceptions).
- On adoption, record today's findings once with each helper's `--write-baseline`; after that only new findings fail.
- When the project has no Python 3.11 or later, use this pack's recipes as the fallback (`just code-size --project-root <path>` and so on).

## Environment

No environment variables and no secrets.

## First run

`just self-check` runs the helpers on this pack itself and passes. Against a project, `just code-size --project-root <path> --list` prints its oversized modules and functions; with no baseline yet,
every one shows as a failure, which is expected before adoption.

## Troubleshooting

- `venv missing at ... — run: just bootstrap`: the working-cache venv is not built yet; run `just bootstrap`.
- A helper refuses to run: the interpreter is older than 3.11; use the project's newer one or this pack's recipe.
- Every finding fails on a project: it has no baseline; record one with `--write-baseline` when adopting, never to hide new code.
- `python 3.11: not installed through mise, NOT TESTED` from `just test-matrix`: `mise install python@3.11`, then run it again.
