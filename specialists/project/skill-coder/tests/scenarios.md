---
Title: skill-coder scenarios
Category: reference
Status: current
Authority: local-supplement
Scope: Behaviour scenarios that show whether an agent applied skill-coder correctly
Last reviewed: 2026-10-19
Summary: >-
  Seventeen scenarios with prompt, trigger, first reference, decision points and prohibited conclusions, covering core rules,
  every language override and negative controls.
---

# skill-coder scenarios

Each scenario passes only when the expected first reference, decision points and prohibited conclusions are met.

## Contents

- [C-S01 — Project rule conflicts with the skill](#c-s01--project-rule-conflicts-with-the-skill)
- [C-S02 — New writer script](#c-s02--new-writer-script)
- [C-S03 — Bug fix](#c-s03--bug-fix)
- [C-S04 — Refactor of untested code](#c-s04--refactor-of-untested-code)
- [C-S05 — Slow scheduled job](#c-s05--slow-scheduled-job)
- [C-S06 — Commit after a check](#c-s06--commit-after-a-check)
- [C-S07 — Python helper with a subprocess](#c-s07--python-helper-with-a-subprocess)
- [C-S08 — Shell wrapper](#c-s08--shell-wrapper)
- [C-S09 — TypeScript API client](#c-s09--typescript-api-client)
- [C-S10 — Go service call](#c-s10--go-service-call)
- [C-S11 — Rust library error type](#c-s11--rust-library-error-type)
- [C-S12 — SQL report query](#c-s12--sql-report-query)
- [C-S13 — YAML catalog entry](#c-s13--yaml-catalog-entry)
- [C-S14 — Negative control: platform fact](#c-s14--negative-control-platform-fact)
- [C-S15 — Negative control: no reusable learning](#c-s15--negative-control-no-reusable-learning)
- [C-S16 — Helper on a project with old Python](#c-s16--helper-on-a-project-with-old-python)

---

## C-S01 — Project rule conflicts with the skill

Prompt: The project's code standard sets functions under 40 lines; add a 55-line function. Trigger: yes. First reference: the project's own `AGENTS.md`, then `references/module-and-function-shape.md`.
Decide that the project's 40 wins and split the function. Prohibit citing the skill's 60-line default as permission.

## C-S02 — New writer script

Prompt: Write a script that updates records in a remote system. Trigger: yes. First reference: `references/safety-and-writes.md`. Decide plan-by-default, `--apply`, a named non-administrator writer,
idempotence and record-after-confirm. Prohibit a script that writes on its first run without a flag.

## C-S03 — Bug fix

Prompt: A parser drops the last row; fix it. Trigger: yes. First reference: `references/testing.md`. Decide a failing test first, then the fix. Prohibit a fix with no test that failed before it.

## C-S04 — Refactor of untested code

Prompt: Split a 900-line module into three. Trigger: yes. First reference: `references/refactoring-and-promotion.md`. Decide characterisation output before and after (byte-identical), shims and
moved-paths entries, string-path updates, and a baseline entry for anything still oversize. Prohibit a behaviour change in the same commit, or claiming safety from thin tests alone.

## C-S05 — Slow scheduled job

Prompt: The nightly job takes 70 minutes and nobody set a budget. Trigger: yes. First reference: `references/efficiency-and-measurement.md`. Decide a stated budget, per-phase timing on a real run,
connection reuse and bounded parallelism, and before-and-after numbers in the change log. Prohibit optimising without measuring, or dropping a check to save time.

## C-S06 — Commit after a check

Prompt: Run the checks and commit. Trigger: yes. First reference: `references/version-control-and-review.md`. Decide `rc=$?` captured before any `tail`, and commit only on 0, in the repo being worked
in only. Prohibit `check | tail && git commit` or `check; git commit`.

## C-S07 — Python helper with a subprocess

Prompt: Add a Python function that calls an external CLI. Trigger: yes. First reference: `languages/python.md`, then `references/errors-and-timeouts.md`. Decide `subprocess.run([...], timeout=<from
settings>, check=True)`, typed errors, and Google-style Args, Returns, Raises. Prohibit `shell=True` with input, no timeout, or a bare `except:`.

## C-S08 — Shell wrapper

Prompt: Write a Bash wrapper that copies files to a host. Trigger: yes. First reference: `languages/shell.md`. Decide `set -euo pipefail`, quoted expansions, ShellCheck clean, a function comment
block, host from the environment, and a plan without `--apply`. Prohibit an inline `# shellcheck disable` or a hard-coded host.

## C-S09 — TypeScript API client

Prompt: Add a TypeScript client for an HTTP service. Trigger: yes. First reference: `languages/javascript-typescript.md`. Decide `strict`, no `any` across the module boundary, a timeout signal on
every request, TSDoc on exports, and the Node version from the project's pin. Prohibit `// @ts-ignore` to make it compile.

## C-S10 — Go service call

Prompt: Add a Go function that queries a remote API. Trigger: yes. First reference: `languages/go.md`. Decide `ctx context.Context` first, `WithTimeout`, wrapped errors with `%w`, lowercase error
strings, and a table-driven test. Prohibit a panic on a normal error or ignoring a returned error.

## C-S11 — Rust library error type

Prompt: Design the error type for a Rust parsing crate. Trigger: yes. First reference: `languages/rust.md`. Decide a meaningful error type implementing `std::error::Error`, `Result` returns, and doc
comments with Errors and Panics sections and a `?`-based example. Prohibit `unwrap` on input in library code.

## C-S12 — SQL report query

Prompt: Write a query filtered by a user-supplied customer id. Trigger: yes. First reference: `languages/sql.md`, then `references/security.md`. Decide a bound parameter, explicit columns, a header
comment, and SQLFluff with the project's dialect. Prohibit string concatenation of the id.

## C-S13 — YAML catalog entry

Prompt: Add a new kind to a YAML catalog whose values include `no` and `3.10`. Trigger: yes. First reference: `languages/yaml-json-toml.md`, then `references/generated-artifacts.md`. Decide quoting of
`"no"` and `"3.10"`, unique keys, editing the source part not the rendered file, and one render before the check. Prohibit hand-editing the generated catalog.

## C-S14 — Negative control: platform fact

Prompt: Which API field holds a device's serial number in the inventory platform? Trigger: no (domain skill). First reference: the platform's domain skill. Decide to route there. Prohibit answering
the platform fact from this skill.

## C-S15 — Negative control: no reusable learning

Prompt: Close a routine change that applied existing rules with no surprise. Trigger: yes. First reference: `references/evolution-and-write-back.md`. Classify `no_new_reusable_learning` and say so.
Prohibit adding a Learned entry or a CHANGELOG line with nothing new.

## C-S16 — Helper on a project with old Python

Prompt: Run the size check on a project pinned to Python 3.9. Trigger: yes. First reference: `references/runtime-boundaries.md`. Decide the fallback: run the helper through the skill's own recipe with
`--project-root`, because the project is below 3.11, and report any file that does not parse. Prohibit installing anything into the project's environment, or skipping unparsable files silently.

## C-S17 — Ansible tag rename

Prompt: Rename an Ansible tag that reads like a repair. Trigger: yes. First reference: `languages/ansible.md`. Decide a whole-repository search including
`*.j2`, classification of each hit as tag or variable, external callers checked, a `--list-tasks` and `--check --diff` run, and every runbook updated. Prohibit
a blind replace, or calling the rename safe because the old command still exits 0.
