---
Title: Tooling and runtime
Category: reference
Status: current
Authority: local-supplement
Scope: Pinned interpreters, virtual environments outside the repo, the task-runner catalog and script safety labels
Last reviewed: 2026-10-19
Summary: >-
  Interpreters pinned (mise) and addressed by path, never the bare one on PATH; the venv lives in a working-cache peer
  outside the repo; runtime state in a runtime peer; every runnable task is a catalogued recipe with a safety label.
---

# Tooling and runtime

Which environment a skill's own helpers run in is a separate question: [runtime-boundaries.md](runtime-boundaries.md).

## Find what the project already pins

Before suggesting any tool or version, read what the project pins, in this order: `.mise.toml` or `mise.toml`, `.python-version` / `.nvmrc` / `.tool-versions`, the language manifest (`pyproject.toml`
`requires-python`, `package.json` `engines`, `go.mod` `go` and `toolchain` lines, `rust-toolchain.toml`, `Cargo.toml` `rust-version`), a `versions.yaml` or equivalent, then CI configuration. Why: the
project's pin outranks this skill's defaults, and a suggestion that ignores it breaks the build.

## Interpreters

- Pin the interpreter per project with mise (`.mise.toml`). For a new Python project the operator's default is Python 3.14, unless the project's manifest excludes it; a `requires-python` lower bound
  or a classifier list is not a cap (operator lesson `feedback_python_version_default`).
- Task-runner recipes address the interpreter by path through a variable (for example `{{py}}` pointing at the venv's `bin/python`) and depend on a `_require-venv` recipe, never a bare `python3` or
  `node`. Why: a bare interpreter resolves to whatever the host has; when the host changes, it fails in a way that reads like a code bug (skill-ai-it `templates/justfile` header).
- `mise exec -- python` is not the fix where a venv sits between mise and the interpreter: the dependency is implicit and degrades silently. For Node, `mise exec -- node` is the explicit form.
  (skill-ai-it, VERIFIED against its template on 2026-10-19.)

## Where things live

| Kind                              | Place                                                    | Why                                                                                                   |
| --------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Source                            | the `*_stuff` repo                                       | Source of truth, versioned                                                                            |
| Virtual environment               | the working-cache                                        | Rebuildable; never committed (Python's own docs say a venv is not checked into source control and is  |
|                                   |   peer: `<parent>-working-cache/<name>/venv/`            |   not movable, VERIFIED_PRIMARY)                                                                      |
| Logs, pid files, sockets          | the runtime peer: `<parent>-runtime/<name>/{logs,run}/`  | Ephemeral; safe to delete                                                                             |
| Operator-managed persistent state | the data peer, or beside the project when it has a local | Durable; not rebuildable                                                                              |
|                                   |   upstream clone                                         |                                                                                                       |

Source: governance `storage-routing-guide.md` (2026-04-23). A project's own layout wins where it states one.

## The task catalog

- Every runnable task is a recipe in the project's task runner (`justfile`, `Makefile`, `package.json` scripts), listed by `just --list` or equivalent. Why: agents run catalogued tasks only; an
  uncatalogued script has unknown safety.
- Each script has a row in the scripts catalog (`scripts/README.md`) with inputs, outputs and a safety label: read-only, writes local files, writes remote (needs `--apply`), destructive (needs the
  operator). Why: a reader decides whether running it is safe without reading code.
- A new or changed script updates its catalog row in the same change.
- The closing check (`just check` or the project's equivalent) runs lint, tests and governance checks together.

## Formatters and linters

Use the project's configured formatter and linter; the language override names the usual ones. Configure rules project-wide in the tool's config file with a comment saying why, never per line
([documentation-and-headers.md](documentation-and-headers.md)). Why: one place to see what the project accepts.

> **Learned 2026-10-20** · just 1.58/1.59 (task runner) · VERIFIED_PRIMARY (unified-network-controller `unc01::run`, regression test tests/test_host_run.py) · Source: a recipe `run *args:` calling `wrapper {{args}}` · Falsifier: a just release where `{{args}}` interpolation keeps each argument's quoting
> **A recipe that forwards arguments must not interpolate them.** `{{args}}` is pasted into the shell line, so `just x::run -c 'a; b; ls ~'` ran only
> `a` remotely and the rest locally. Mark the recipe `[positional-arguments]` and pass `"$@"`; let the runner be swapped by an environment variable
> (`export RUNNER := env("RUNNER", "real-runner")`) so a test can point it at a stub that prints its argv and prove a compound command and a
> spaced argument arrive whole.

