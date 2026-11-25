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

> **Learned 2026-11-25** · macOS launchd agents · VERIFIED_PRIMARY (PATH and `python3` observed: "command not found" under launchd, fixed by the plist PATH; the
> cloud-folder hang cause is UNVERIFIED) · Source: continuum-app `deploy/mac/dev.continuum.domain-renew.plist.template` (3d7c9b1), TASK-588 · Falsifier: a launchd job whose PATH includes
> `/opt/homebrew/bin` without setting it. A launchd job's PATH is `/usr/bin:/bin:/usr/sbin:/sbin`: Homebrew CLIs are "command not found", so set `EnvironmentVariables`
> PATH in the plist; `python3` there is the system 3.9, so name the project venv's python by path. A job that opened a file under `~/Library/CloudStorage` (a File
> Provider cloud folder) hung inside a CLI; the cause is unverified (likely macOS privacy control on background access to cloud folders). Run a new job once with
> `launchctl kickstart gui/$(id -u)/<label>` and watch it for hangs before leaving it installed.
>
> ```xml
> <key>ProgramArguments</key>
> <array>
>   <string>@PY@</string>   <!-- the project venv's python: launchd's python3 is the system 3.9 -->
>   <string>-I</string>
>   <string>@REPO@/scripts/deploy/domain_renew.py</string>
> </array>
> <key>EnvironmentVariables</key>
> <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
> ```

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

> **Learned 2026-11-19** · act 0.2.98 local Actions cache (`~/.cache/actcache`) · VERIFIED_PRIMARY · Source: nektos/act v0.2.98 `pkg/artifactcache/handler.go:203-209, 433-436`; continuum-app
> `scripts/act_cache_prune.sh` (0ffd12f) · Falsifier: a later act that prunes archives by count, or a restore failing after an archive file was deleted
> A cache step (`Swatinem/rust-cache`) saves a new archive (0.3 to 1.1 GiB for a Rust workspace) whenever its key changes, under `cache/<id>/<id>`; act removes one only after 7 days unused
> (`keepUnused`), so several pushes a day fill a disk (5.1 GiB in a day; a push failed "No space left on device"). Deleting archive files is safe: on lookup act drops the index record of a
> missing file and reports a miss. Prune by count after each run, newest first by modification time, never touching `cache/tmp` (uploads in progress). On macOS `~/.cache` and `/Volumes/Data`
> can share one APFS container, so a cache in the home folder fills the data volume too.

> **Learned 2026-11-19** · act 0.2.98 cache server and proxies · VERIFIED_PRIMARY (`act --help`; job logs through Squid) · Source: continuum-app `justfile` `ci-linux` (a1fefdd) · Falsifier: act binding
> to loopback by default, or `@actions/cache` sending plain HTTP through the proxy
> act's cache server binds by default to the machine's outbound (LAN) address, so other hosts on the LAN can reach it. Bind it to loopback on a fixed port and give jobs an external URL:
> `--cache-server-addr 127.0.0.1 --cache-server-port 18790 --cache-server-external-url http://host.docker.internal:18790`. Behind a forward proxy the cache client tunnels with CONNECT even
> to that `http://` URL ("tunneling socket could not be established, statusCode=403" until CONNECT to the cache port was allowed). Pass both cases of the proxy variables with `--env` and keep
> `localhost,127.0.0.1` in NO_PROXY for services inside the job.

> **Learned 2026-11-19** · project-pinned CLI tools through mise, installed into the working cache · USER_STATED (operator: "that is the standard we follow in all the projects") ·
> Source: continuum-app `.mise.toml`, `justfile` · Falsifier: none, a rule. Pin tools in `.mise.toml` (`act = "0.2.98"`, `jj = "0.47.1"`) and point mise's data at the project's working cache, not
> `~/.local/share/mise` or Homebrew; recipes run the tools through `mise exec --` so no shell activation is needed.
>
> ```text
> export MISE_DATA_DIR := if os() == "macos" { "/Volumes/Data/_ai/_tool/tools-working-cache/<project>/mise" } else { env_var_or_default("MISE_DATA_DIR", "") }
> run := if os() == "macos" { "mise exec --" } else { "" }
> ```

## The task catalog

> **Learned 2026-11-19** · just `export` variables and direct tool calls · VERIFIED_PRIMARY (observed twice in one project) · Source: continuum-app `justfile` line `export CARGO_TARGET_DIR`,
> `AGENTS.md` (2026-11-19) · Falsifier: a direct `cargo` call in the repo honouring the justfile's CARGO_TARGET_DIR
> A justfile `export` reaches only the commands just runs. An agent that calls `cargo` (or any tool) directly in the same folder gets the tool's default, so a governed
> build-cache path silently becomes `./target` (2.1 GiB, gitignored, unnoticed until a disk check). Run tools through recipes, or export the variable in the shell first,
> and say so in the project's AGENTS.md.

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

> **Learned 2026-11-24** · a local CI image for act: one Dockerfile, a tag hashed from the pins, setup steps skipped by a variable · VERIFIED_PRIMARY (Linux job 295 s
> to 233 s warm) · Source: continuum-app `scripts/ci/image/Dockerfile`, `scripts/ci/ci_image.sh`, `.github/workflows/ci.yml` (2227449) · Falsifier: an act release
> ignoring `--var` in `if:`. The tag is the SHA-256 of the Dockerfile, the workflow and the toolchain file, so a pin change builds a new image and a stale one is never
> used; act runs with `-P ubuntu-latest=<tag> --pull=false --var CI_IMAGE=baked`, actions carry `if: vars.CI_IMAGE != 'baked'`, and install steps are guarded with
> `command -v` so the workflow still runs on the bare image. Three traps on the way: (1) `ENV PATH=...` replacing the base image's PATH removed act's node, so every
> node action failed: write `PATH=/opt/x/bin:$PATH`; (2) fixing that line, near the top, invalidated every later layer: a 13-minute rebuild (put late fixes late);
> (3) the first run on a new image is cold (rust-cache key changes): 445 s once.

> **Learned 2026-11-25** · exact-text edit scripts after a formatter · VERIFIED_PRIMARY (observed twice in one session) · Source: continuum-app
> `deploy/coordinator/realm_sync.py`, `restore.py` (5dbeb4d) · Falsifier: an edit script that finds its target after ruff/rustfmt re-wrapped it.
> A formatter (ruff format, rustfmt, the markdown hook) re-wraps a call one argument per line; a later `str.replace` written against the one-line form
> then matches nothing and the old value silently stays (here a hard-coded username and a fixed temporary user: about 20 minutes of "Invalid user
> credentials"). Every scripted replacement asserts it matched exactly once (`assert s.count(old) == 1`), and after any formatter run the target lines
> are re-read before the next scripted edit.

