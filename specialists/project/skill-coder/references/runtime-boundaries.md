---
Title: Runtime boundaries
Category: reference
Status: current
Authority: local-supplement
Scope: Which environment applies this skill's rules and runs its helper scripts, and how a project consumes skill code
Last reviewed: 2026-10-19
Summary: >-
  The default is the target project's own environment and tooling; skill helpers are stdlib-only, need Python 3.11, read
  code as files and run with the project's interpreter by path; the skill's pinned interpreter is a fallback only.
---

# Runtime boundaries

Operator decision, 2026-10-19. This skill dictates logic; the agent applies it inside the target project's own environment.

## The default (B): the target project's environment

- The rules in this pack are environment-free. Apply them with the project's own formatter, linter, type checker, test runner and pinned interpreter. Why: the project's tools and versions are what its
  build and CI use.
- Each language override names the tool a project should use, and how to find what the project already pins (`.mise.toml`, `pyproject.toml` `requires-python`, `package.json` `engines`, `go.mod`)
  before suggesting anything ([tooling-and-runtime.md](tooling-and-runtime.md)).
- The pack's helper scripts (`scripts/code_size.py`, `ratchet.py`, `import_layers.py`, `write_gates.py`, `call_timeouts.py`) are portable: standard library only, a declared minimum (`REQUIRES_PYTHON =
  (3, 11)`), and they read code as files (parse, never import), so the project's packages do not matter. Run them with the project's pinned interpreter by path:

  ```bash
  <project venv>/bin/python <skill>/scripts/code_size.py --project-root .
  ```

- A file that does not parse is reported, never skipped silently. Why: a skipped file is a check that passed without looking.

## The fallback (A): the skill's own pinned interpreter

Only when the project has no Python, or one below 3.11, run the same helper with the skill's own pinned interpreter:

```bash
just -f <skill>/justfile <recipe> --project-root <target>
```

This is safe because the helpers only read files. It never installs anything into the target.

## Who decides what

| Question                                           | A: skill environment (fallback)                                    | B: target environment (default)                                   |
| -------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Tool versions                                      | The skill's `.mise.toml`                                           | The project's pins                                                |
| Extra setup                                        | The skill's working-cache venv                                     | None; the project's existing environment                          |
| Third-party tools (formatter, linter, test runner) | Not used; helpers are stdlib-only                                  | The project's configured tools                                    |
| Non-Python targets (Go, Rust, TypeScript, shell)   | Python helpers read their files as text where a helper supports it | The language's own tools, as the override names                   |
| Engines a project imports                          | Never                                                              | Always: the project's interpreter, with the skill revision pinned |

Why B is the default: the result must match what the project's own build, CI and reviewers will see; a second environment can disagree with it and adds setup to every engagement.

## Rules that hold in both

1. Never install a skill's dependencies into a project's environment, or a project's into the skill's. Why: either install changes the other's behaviour silently.
2. Never rely on whatever `python3` or `node` is first on `PATH`; address the interpreter by path. Why: the ambient interpreter changes under you.
3. An engine a project imports runs in the project's interpreter, so it is stdlib-only, imports any third-party package lazily at the edge that needs it, and declares its minimum version.
4. A project that imports skill code pins the skill revision (a branch or commit pin its governance checks). When it moves the pin, it characterises the output (byte-identical, or the difference
   named) in the same change. Why: a skill change must not silently change a project's output.
5. Per language the same split holds: a Node helper or engine declares `engines` in `package.json`; a project's tool runs with the project's pinned toolchain.

The operator's rules here are claim C-C50 in `sources.yaml` (USER_STATED).
