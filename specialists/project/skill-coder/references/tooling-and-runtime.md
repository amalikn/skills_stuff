---
Title: Tooling and runtime
Category: reference
Status: current
Authority: local-supplement
Scope: Pinned interpreters and CLI tools, virtual environments outside the repo, the task-runner catalog and script safety labels, local CI runs
Last reviewed: 2026-11-19
Summary: >-
  Interpreters pinned (mise) and addressed by path, never the bare one on PATH; the venv lives in a working-cache peer
  outside the repo; runtime state in a runtime peer; every runnable task is a catalogued recipe with a safety label; the closing check runs
  every step before it fails.
---

# Tooling and runtime

Which environment a skill's own helpers run in is a separate question: [runtime-boundaries.md](runtime-boundaries.md).

## Contents

- [Find what the project already pins](#find-what-the-project-already-pins)
- [Interpreters](#interpreters)
- [Where things live](#where-things-live)
- [The task catalog](#the-task-catalog)
- [Formatters and linters](#formatters-and-linters)

---

## Find what the project already pins

Before suggesting any tool or version, read what the project pins, in this order: `.mise.toml` or `mise.toml`, `.python-version` / `.nvmrc` / `.tool-versions`, the language manifest (`pyproject.toml`
`requires-python`, `package.json` `engines`, `go.mod` `go` and `toolchain` lines, `rust-toolchain.toml`, `Cargo.toml` `rust-version`), a `versions.yaml` or equivalent, then CI configuration. Why: the
project's pin outranks this skill's defaults, and a suggestion that ignores it breaks the build.

## Interpreters

- Pin the interpreter per project with mise (`.mise.toml`). For a new Python project the operator's default is Python 3.14, unless the project's manifest excludes it; a `requires-python` lower bound
  or a classifier list is not a cap (operator lesson `feedback_python_version_default`).
- Task-runner recipes address the interpreter by path through a variable (for example `{{py}}` pointing at the venv's `bin/python`) and depend on a `_require-venv` recipe, never a bare `python3` or
  `node`. Why: a bare interpreter resolves to whatever the host has; when the host changes, it fails in a way that reads like a code bug (skill-ai-it `templates/justfile` header).
- `mise exec -- python` is not the fix where a venv sits between mise and the interpreter: the dependency is implicit and degrades silently. For Node, `mise exec -- node` is the explicit form, as it
  is for CLI tools pinned in `.mise.toml` (Learned 2026-11-19). (skill-ai-it, VERIFIED against its template on 2026-10-19.)

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

> **Learned 2026-11-19** · local CI with act (nektos/act 0.2.98) on macOS with OrbStack · VERIFIED_PRIMARY (observed, each tested) · Source: continuum-app
> `justfile` ci-linux, `.github/workflows/ci.yml` (tools_stuff/continuum-app 9e12562) · Falsifier: a later act honouring the flag in .actrc.
> 1. `--container-daemon-socket -` works only on the command line: in `.actrc` (either `=-` or `-`) act 0.2.98 still mounts the Docker socket, so a job can control every container on the
> machine. Test with a step that runs `docker ps`, matching only the step's output lines (act echoes the command text).
> 2. act's default network is the host's: the job can talk to every container. `--network <own>` isolates it, but service containers are then not reachable by name; run the database in the job.
> 3. `catthehacker/ubuntu:act-latest` lacks rustup and protoc, and its Python is externally managed (PEP 668): install the toolchain with an action, protoc from apt, Python tools in a venv.
> 4. Pin every action to a commit SHA and the image by digest: on act, CI runs third-party code on your own machine.
>
> ```text
> ci-linux:
>     docker network inspect continuum-act >/dev/null 2>&1 || docker network create continuum-act >/dev/null
>     {{run}} act push -j ci --rm --container-daemon-socket - --network continuum-act
> ```

> **Learned 2026-11-19** · project-pinned CLI tools through mise, installed into the working cache · USER_STATED (operator: "that is the standard we follow in all the projects") ·
> Source: continuum-app `.mise.toml`, `justfile` · Falsifier: none, a rule. Pin tools in `.mise.toml` (`act = "0.2.98"`, `jj = "0.47.1"`) and point mise's data at the project's working cache, not
> `~/.local/share/mise` or Homebrew; recipes run the tools through `mise exec --` so no shell activation is needed.
>
> ```text
> export MISE_DATA_DIR := if os() == "macos" { "/Volumes/Data/_ai/_tool/tools-working-cache/<project>/mise" } else { env_var_or_default("MISE_DATA_DIR", "") }
> run := if os() == "macos" { "mise exec --" } else { "" }
> ```

## The task catalog

- Every runnable task is a recipe in the project's task runner (`justfile`, `Makefile`, `package.json` scripts), listed by `just --list` or equivalent. Why: agents run catalogued tasks only; an
  uncatalogued script has unknown safety.
- Each script has a row in the scripts catalog (`scripts/README.md`) with inputs, outputs and a safety label: read-only, writes local files, writes remote (needs `--apply`), destructive (needs the
  operator). Why: a reader decides whether running it is safe without reading code.
- A new or changed script updates its catalog row in the same change.
- The closing check (`just check` or the project's equivalent) runs lint, tests and governance checks together, every step even after one fails, and exits non-zero at the end naming the failed steps
  (Learned 2026-11-18).

## Formatters and linters

Use the project's configured formatter and linter; the language override names the usual ones. Configure rules project-wide in the tool's config file with a comment saying why, never per line
([documentation-and-headers.md](documentation-and-headers.md)). Why: one place to see what the project accepts.

> **Learned 2026-10-20** · just 1.58/1.59 (task runner) · VERIFIED_PRIMARY (unified-network-controller `unc01::run`, regression test tests/test_host_run.py) · Source: a recipe `run *args:` calling `wrapper {{args}}` · Falsifier: a just release where `{{args}}` interpolation keeps each argument's quoting
> **A recipe that forwards arguments must not interpolate them.** `{{args}}` is pasted into the shell line, so `just x::run -c 'a; b; ls ~'` ran only `a` remotely and the rest locally. Mark the recipe
> `[positional-arguments]` and pass `"$@"`; let the runner be swapped by an environment variable (`export RUNNER := env("RUNNER", "real-runner")`) so a test can point it at a stub that prints its argv
> and prove a compound command and a spaced argument arrive whole.


> **Learned 2026-11-10** · Python 3.14, scripts loaded by path · VERIFIED_PRIMARY · Source: skill-pad scripts/pad_tracker.py and
> tests/test_pad_tracker.py (skills_stuff b2e2e52) · Falsifier: a `@dataclass` module run through `spec.loader.exec_module` without a `sys.modules` entry that builds without error. A module that
> defines a `@dataclass` and is loaded with `importlib.util.spec_from_file_location` must be put in `sys.modules` under its name before `exec_module`: the dataclass decorator looks the module up by
> name and fails with `AttributeError: 'NoneType' object has no attribute '__dict__'`. Loading a sibling script this way also avoids `sys.path` edits and the inline lint suppression they need.

```python
# skill-pad tests/test_pad_tracker.py (skills_stuff b2e2e52)
_spec = importlib.util.spec_from_file_location("pad_tracker", Path(__file__).resolve().parents[1] / "scripts" / "pad_tracker.py")
pt = importlib.util.module_from_spec(_spec)
sys.modules["pad_tracker"] = pt  # dataclasses look the module up by name while the class is built
_spec.loader.exec_module(pt)
```

> **Learned 2026-11-10** · CLI progress output · VERIFIED_PRIMARY · Source: skill-pad scripts/pad_rewrite.py (skills_stuff a28cf80)
> · Falsifier: a run piped to `| tail -n 1` that shows its error line last without flushing. A script that prints progress to stdout and errors to stderr must flush each progress line (`print(..., flush=True)`):
> piped, stdout is block buffered and stderr is not, so the error appears before the line it belongs to, and `2>&1 | tail -1` shows a progress line instead of the error. Twice this read as a "silent
> stop"; the cause was an `update_conflict` printed out of order.

```python
# skill-pad scripts/pad_rewrite.py main() (skills_stuff a28cf80)
for label, cmd, stdin in todo:
  print(("apply " if a.apply else "plan  ") + label, flush=True)
```

> **Learned 2026-11-18** · task runner · VERIFIED_PRIMARY · Source: unified-network-controller justfile `check` and `lint` (commit after d8e02da0) · Falsifier: a just recipe of `@` lines that still runs the steps after a failing one
> In `just`, each `@cmd` line of a recipe ends the recipe when it fails, so a check made of several steps reports only the first failure. Write the closing check as one shebang recipe that runs every
> step through a small `step()` wrapper and exits 1 at the end with the failed steps named (excerpt in skill-ai-it `references/pitfalls.md`, same date). Proved red then green: a moved plan date failed
> the governance step and doc freshness still ran.
