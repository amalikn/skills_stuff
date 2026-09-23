# Scripts

## Contents

- [Shared rules](#shared-rules)
- [validate_suite.py](#validate_suitepy)
- [record_result.py](#record_resultpy)
- [render_report.py](#render_reportpy)
- [record_writeback.py](#record_writebackpy)
- [eval_common.py](#eval_commonpy)
- [check_governance.py](#check_governancepy)
- [Running these scripts](#running-these-scripts)
- [Safety labels](#safety-labels)

## Shared rules

The scripts are Python standard-library tools. They do not execute the evaluator named in a suite. JSON-compatible YAML works without dependencies; ordinary YAML additionally needs OSI-licensed
PyYAML. Inputs should be backed up before manual edits; JSONL history is append-only.

## validate_suite.py

Purpose: validate suite shape, key schema invariants, evidence altitude, oracle independence, falsifiability, and optionally a JSONL history. Inputs: `--suite` and optional `--history`. Output:
diagnostics to stdout/stderr and non-zero exit on failure. Safety: read-only. Idempotency: yes.

## record_result.py

Purpose: append one externally observed result or declared invalidation. Inputs: suite, history path, eval/slice id, verdict plus evidence, or `--invalidate` plus reason/reference. Output: exactly one
JSONL line unless `--dry-run`. Safety: append-only; it never overwrites or executes an eval. Idempotency: no by design—each invocation is a distinct historical record.

## render_report.py

Purpose: project the latest observation per declared eval/slice into a Markdown scorecard. Inputs: suite, history, output, and optional render time. Output: overwritten derived report. Safety: writes
only the selected report path; it never changes source history. Idempotency: yes for unchanged inputs and `--now`.

## record_writeback.py

Purpose: append one routing record to `ledger.jsonl`, naming a finding returned by a consuming project and the
file(s) that now carry it. Inputs: `--source-project`, `--kind`, `--finding`, and either `--incorporated-in <paths>` or
`--open`; optional `--commit`, `--supersedes`, `--notes`, `--ts`, `--dry-run`. Output: one appended JSONL line.

**It records where knowledge went, not the knowledge.** Every `--incorporated-in` path must already exist, so a row
cannot claim a destination before the content is in it; `--open` records an honest outstanding loop instead. Safety:
append-only, never rewrites a line. Idempotency: no — each run appends a new row with a new `entry_id`; supersede a
mistaken row rather than editing it.

## eval_common.py

Purpose: shared helpers used by the three package scripts — suite loading, JSONL reading, duration parsing, and the layer-rank lookup. Inputs: none directly; it is imported, not invoked. Output: none.
Safety: `safe` — it is a library module with no side effects and no entry point. Idempotency: not applicable.

## check_governance.py

Purpose: assert this project's governance claims against the filesystem — that referenced paths resolve, that every script is cataloged here, that the checked-in example reports are not older than the
suites and histories they were rendered from, that recipes address the pinned interpreter rather than a bare `python3`, and that the package version is stated identically on its three surfaces. Inputs:
the repository itself; no arguments. Output: pass/fail diagnostics and an assertion count; non-zero exit on any failure. Safety: `safe` — read-only, and deliberately standard-library only so the gate
can never fail for environment reasons. Idempotency: yes.

Run it with `just check`. When it fails, fix the project, not the check: narrowing a check to make a run green converts a real finding into a permanent blind spot. Adding a script, a generated
artifact, or a new surface that restates a registered constant means extending its registries in the same pass.

## Running these scripts

Recipes address the interpreter by absolute path from the working-cache venv, never a bare `python3`, because the host interpreter is not the one `.mise.toml` pins.

```bash
just bootstrap    # build the venv from the pinned runtimes (safe to re-run)
just runtimes     # print the interpreters the recipes will actually use
just validate-all # template suite, example suites, negative fixtures
just check        # governance coherence assertions
```

## Safety labels

| Script | Safety | Idempotent |
|---|---|---|
| `validate_suite.py` | `safe` (read-only) | yes |
| `record_result.py` | `modifies-files` (append-only; never overwrites, never executes an eval) | no, by design — each call is a distinct historical record |
| `render_report.py` | `modifies-files` (overwrites only the selected report path) | yes for unchanged inputs and `--now` |
| `record_writeback.py` | `modifies-files` (appends one line to `ledger.jsonl`) | no — each run appends a new row |
| `eval_common.py` | `safe` (library module) | not applicable |
| `check_governance.py` | `safe` (read-only) | yes |

Treat any script not listed here as `unknown` safety until inspected. `just check` fails when this table's file list and `scripts/` disagree in either direction.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

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
