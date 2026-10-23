---
name: skill-coder
description: >-
  Programming practice for any project and any language. Use before writing, changing, reviewing or refactoring code in any project: designing modules and layers;
  adding scripts and CLIs; tests and checks; error handling and timeouts; write safety; configuration; performance and runtime budgets; dependencies;
  security; and promoting reusable code into a skill. Language overrides cover Python, shell, JavaScript/TypeScript, Go, Rust, SQL, YAML/JSON/TOML and Ansible.
  Not for a platform's or device's own facts (use that domain skill), not for prose or governance documents alone, and never above the project's own rules.
---

# Coder

## Contents

- [Role and non-goals](#role-and-non-goals)
- [Orient first](#orient-first)
- [Route the task](#route-the-task)
- [The pack's tools](#the-packs-tools)
- [How the override layer works](#how-the-override-layer-works)
- [Standing rules that apply to every task](#standing-rules-that-apply-to-every-task)
- [Standing write-back contract](#standing-write-back-contract)
- [Evidence](#evidence)

---

## Role and non-goals

This skill holds the operator's programming practice in one place: how code is shaped, documented, made safe, tested, measured, refactored and promoted, in any language. It dictates logic; the agent
applies it inside the target project with that project's own tools.

Non-goals: it does not hold facts about a platform, product or device (a domain skill does), it does not replace a project's architecture document, and it never authorises a write, deploy, delete or
commit on its own.

## Orient first

1. **Read the project's own rules before this skill.** `AGENTS.md`, its navigation file, any code architecture or standards document, and the tool configs (`pyproject.toml`, `.eslintrc`,
   `.golangci.yml`, `rustfmt.toml`, `.sqlfluff`, `.yamllint`). **Project rules outrank this skill.** Where they disagree, follow the project and say so; where two project sources disagree, stop and
   report.
2. **Find what the project pins** (`.mise.toml`, `requires-python`, `package.json` `engines`, `go.mod`, `rust-toolchain.toml`) and use its formatter, linter, type checker and test runner
   ([references/tooling-and-runtime.md](references/tooling-and-runtime.md)).
3. **Find the closing check** (`just check`, `make check`, CI) and the task catalog; run catalogued tasks only.
4. **Check the owning skill before stating a domain fact**, and the exact-version documentation before writing a directive, flag or API call.
5. Then open the core reference for the task, and the language file for the language.

## Route the task

| Task                                                                                          | Core reference                           | Then                                                      |
| --------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| Shape a new module, package or service; choose layers; decide whether to build                | [references/design-principles.md](references/design-principles.md) | the language file                                         |
| Size, split, group into packages or name modules and functions; adopt a size budget on        | [references/module-and-function-shape.md](references/module-and-function-shape.md) | `scripts/code_size.py`,                                   |
|   old code                                                                                    |                                          |   `scripts/ratchet.py`, `scripts/module_groups.py`        |
| Name files, identifiers, commands and recipes in any language                                 | [references/naming-conventions.md](references/naming-conventions.md) | the language file                                         |
| File headers, docstrings, doc comments, comments, lint suppression                            | [references/documentation-and-headers.md](references/documentation-and-headers.md) | `scripts/suppressions.py`, `scaffold.py`                  |
| Anything that writes: files, databases, devices, remote systems; deletes; batches; renames    | [references/safety-and-writes.md](references/safety-and-writes.md) | `scripts/write_gates.py`                                  |
| Error types, exit codes, timeouts, retries, unknown third-party errors                        | [references/errors-and-timeouts.md](references/errors-and-timeouts.md) | `scripts/call_timeouts.py`, `group_timeouts.py`            |
| Settings, paths, hosts, tokens, version pins, catalog data, config directives                 | [references/configuration-and-literals.md](references/configuration-and-literals.md) |                                                           |
| Tests, fakes, characterisation, negative tests for checks, real-target proof                  | [references/testing.md](references/testing.md) | the language file's test runner                           |
| Refactor, move code, shims, promote a script to a skill                                       | [references/refactoring-and-promotion.md](references/refactoring-and-promotion.md) |                                                           |
| Jobs, loops and pages over many items; runtime budgets                                        | [references/efficiency-and-measurement.md](references/efficiency-and-measurement.md) |                                                           |
| Generated files, renderers, drift checks, lock files                                          | [references/generated-artifacts.md](references/generated-artifacts.md) |                                                           |
| Interpreters, venvs, task runner, scripts catalog                                             | [references/tooling-and-runtime.md](references/tooling-and-runtime.md) |                                                           |
| Which environment runs this skill's helpers; projects importing skill code                    | [references/runtime-boundaries.md](references/runtime-boundaries.md) |                                                           |
| Add, use or upgrade a dependency                                                              | [references/dependencies.md](references/dependencies.md) | [references/security.md](references/security.md)          |
| Input, injection, secrets, least privilege, supply chain                                      | [references/security.md](references/security.md) | the language file's injection row                         |
| Commits, change logs, versions, review, definition of done                                    | [references/version-control-and-review.md](references/version-control-and-review.md) |                                                           |
| Closeout: record what this engagement taught                                                  | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |                                                           |

| Language                        | Override file                      |
| ------------------------------- | ---------------------------------- |
| Override contract and file list | [languages/readme.md](languages/readme.md) |
| Python                          | [languages/python.md](languages/python.md) |
| Bash and POSIX sh               | [languages/shell.md](languages/shell.md) |
| JavaScript and TypeScript       | [languages/javascript-typescript.md](languages/javascript-typescript.md) |
| Go                              | [languages/go.md](languages/go.md) |
| Rust                            | [languages/rust.md](languages/rust.md) |
| SQL                             | [languages/sql.md](languages/sql.md) |
| YAML, JSON, TOML                | [languages/yaml-json-toml.md](languages/yaml-json-toml.md) |
| Ansible                         | [languages/ansible.md](languages/ansible.md) |

## The pack's tools

`scripts/` holds stdlib-only helpers that read a project's code as files (never import it) and report; they write nothing in the target. Run them with the project's pinned interpreter by path, and
fall back to the skill's own recipe only when the project has no Python 3.11 or later ([references/runtime-boundaries.md](references/runtime-boundaries.md)). `scripts/README.md` catalogues their
inputs, outputs and safety labels.

| Script                      | What it reports                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------- |
| `scripts/code_size.py`      | Modules and functions over the size budget                                            |
| `scripts/ratchet.py`        | A count compared with its shrink-only baseline                                        |
| `scripts/import_layers.py`  | Imports that break a declared layer table, and import cycles                          |
| `scripts/write_gates.py`    | Write paths reachable without the apply gate                                          |
| `scripts/call_timeouts.py`  | Network calls and subprocesses without a timeout                                      |
| `scripts/script_headers.py` | Runnable scripts whose header lacks a summary, run line or safety statement           |
| `scripts/module_groups.py`  | Folders where three or more code files share a prefix: candidate packages (warn only) |
| `scripts/write_back.py`     | Write-back entries a project parked for this skill, to promote                        |
| `scripts/naming_check.py`   | File and recipe names off the naming mapping (`naming.toml`)                          |
| `scripts/suppressions.py`  | Inline linter suppressions (`noqa`, `type: ignore`, `shellcheck disable`, `eslint-disable`, ...) |
| `scripts/group_timeouts.py` | Timed subprocess calls (ssh, a shell) whose children outlive the timeout             |
| `scripts/scaffold.py`       | Prints a new script and its test skeleton that meet these rules (writes nothing)     |

## How the override layer works

```text
core rule (references/*.md)
   -> languages/<lang>.md may TIGHTEN it, LOOSEN it with a stated reason,
      MAP it to the language's idiom, or ADD the tool commands
   -> the project's own rules override both
```

A language file never removes a safety rule. A loosening without a reason is void. Details: [languages/readme.md](languages/readme.md).

## Standing rules that apply to every task

- Read by default; any write prints a plan and needs `--apply`; canary before batch; report success at the outcome the operator sees.
- Every network call and subprocess has a timeout; no deployment literals in code; no secrets in code, logs or output.
- Every file has a purpose header; every function documents Args, Returns and Raises in the language's syntax; never silence a linter inline.
- A refactor changes no behaviour and proves it with a before-and-after comparison.
- State and measure the runtime of anything that repeats.
- Gate a commit, push or deploy on the check's own exit code, never through a pipe or `;`.
- One linter per language, configured once at the project root, for new files only: existing files are listed as excluded in that
  config and reformatted only on a decision (operator, 2026-10-23). Python ruff, YAML yamllint, Jinja2 djlint (lint only), TOML taplo,
  JSON biome, shell shfmt + shellcheck, Ansible inventories parsed by ansible-inventory; see the language files.
- Indent with two spaces in every language (operator, 2026-10-23); Python is formatted and linted with ruff (`indent-width = 2`), as YAML
  is with yamllint. Existing tracked code keeps its indentation until a reformat is decided.
- Label load-bearing claims `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`, `UNVERIFIED` or `USER_STATED`; never present a guess as a fact.

## Standing write-back contract

Touching this skill's domain, invoked or not, engages its write-back. At closeout classify the engagement (`no_new_reusable_learning`, `verified_reusable_update`, `reusable_candidate`,
`contradicts_existing_claim`, `language_specific`, `project_only`, `domain_only`) and, when there is something to write, add a dated entry to the file a future reader would open, plus one CHANGELOG
line under `## Unreleased` naming that file and date:

```text
> **Learned YYYY-MM-DD** · <scope> · <EVIDENCE> · Source: <URL or file:line> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

A contradiction is a `Disputed` entry beside the old text with `Conflicts: <claim ID>`; never delete or silently rewrite. Read the edited file back. Full contract, release reconciliation and
promotion: [references/evolution-and-write-back.md](references/evolution-and-write-back.md).

**The calling project owes it** (operator, 2026-10-19: "any project which is calling skill coder should write that learning back"). A session in any project that invoked this skill, followed its rules
or ran its helpers is engaged, and its closeout (skill-slurp-chat Step 5b) classifies, writes and commits the entry here. When this source cannot be written, the entry is parked in the project under
`## skill-coder write-back candidates`; `scripts/write_back.py --project-root <project>` lists parked entries, and the next engagement promotes them and removes them there.

**Evidence with every entry (operator, 2026-10-20; every calling project owes it).** A write-back that records how something is done carries
(1) a **code excerpt** of the logic that does it: the few lines that matter (about 30 at most), as a fenced block with its source path and
commit, secrets and customer identifiers removed; and (2) for anything with a visual surface (Nautobot, OpenWISP, a device web UI, a draw.io
render) a **screenshot** as reference, saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image, what it
shows and where it was taken. Site names, addresses, MACs and serials are redacted or the shot is taken on a lab or sample instance; when the
surface is not live yet, the entry says "screenshot pending: <page>, after <deploy>" and the next engagement adds it.

## Evidence

Load-bearing claims are in `sources.yaml` (IDs `C-C..`), with the operator's rules as `USER_STATED`. External sources are kept verbatim under `documents/research-sources-20261019/` with a `readme.md`
index. Behaviour scenarios: `tests/scenarios.md`.
