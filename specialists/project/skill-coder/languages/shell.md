---
Title: Shell override
Category: reference
Status: current
Authority: local-supplement
Scope: Bash and POSIX sh scripts, task-runner recipe bodies and wrapper scripts
Last reviewed: 2026-10-19
Summary: >-
  Bash for executables with set -euo pipefail, ShellCheck on every script, quote every expansion, function comment blocks
  with Globals, Arguments, Outputs and Returns, and rewrite in a structured language past about 100 lines.
---

# Shell override

## Authoritative sources

The Google Shell Style Guide, the GNU Bash manual (The Set Builtin), the ShellCheck README and wiki (SC2086). Copies: `../documents/research-sources-20261019/`.

## Tools

| Job    | Tool                                                                | Note                                                                      |
| ------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Lint   | ShellCheck                                                          | Google recommends it "for all scripts, large or small" (VERIFIED_PRIMARY) |
| Format | shfmt                                                               | UNVERIFIED: no source fetched; use if the project configures it           |
| Tests  | bats, or a test in the project's main language that runs the script | UNVERIFIED stub                                                           |

## Core rule mapping

| Core reference              | In shell                                                                                                                                                               |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers   | A top-of-file comment with purpose and usage; each function has a comment block with Globals, Arguments, Outputs and Returns (Google, VERIFIED_PRIMARY)                |
| errors-and-timeouts         | Start Bash scripts with `set -euo pipefail`: `-e` exits on an unhandled failure, `-u` treats unset variables as errors, `pipefail` gives a pipeline the status of the  |
|                             |   last command to fail (Bash manual, VERIFIED_PRIMARY); wrap network commands with `timeout` or the tool's own timeout flag                                            |
| version-control-and-review  | Gate on `rc=$?` captured right after the command, never through a pipe or `;`                                                                                          |
| security                    | Quote every expansion (`"$var"`, `"$@"`): SC2086 says to double quote to prevent globbing and word splitting (VERIFIED_PRIMARY); `--` before untrusted arguments; no   |
|                             |   evaluating input as code; `mktemp` for temporary files                                                                                                               |
| configuration-and-literals  | Read settings from the environment with a checked default (`: "${ROOT:?ROOT is required}"`); no absolute paths or hosts in the script                                  |
| safety-and-writes           | A destructive script prints its plan and needs `--apply`; make writes idempotent (`mkdir -p`, compare before copy)                                                     |
| tooling-and-runtime         | Recipes call the interpreter by path variable; long commands split across lines with trailing `\` for readability (operator lesson)                                    |
| documentation-and-headers   | No inline `# shellcheck disable=`; fix the cause; a project-wide `.shellcheckrc` entry carries a comment saying why                                                    |
|   (suppression)             |                                                                                                                                                                        |

## Size and limit tweaks

| Item          | Value                                                         | Reason                                                                                                               |
| ------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Script length | About 100 lines, or any non-trivial control flow: rewrite in  | Google: "you should rewrite it in a more structured language now. Bear in mind that scripts grow"                    |
|               |   a structured language                                       |   (VERIFIED_PRIMARY). Tightens the core 400-line module budget                                                       |
| Line length   | 80                                                            | Google Shell Style Guide (VERIFIED_PRIMARY); a project's own setting wins                                            |
| Function      | Core 60 lines                                                 | No change                                                                                                            |

## POSIX sh

Where a script must run under `/bin/sh` (minimal images, some embedded systems), `pipefail` may be missing on older shells and arrays do not exist; keep such scripts tiny and say in the header why
they are POSIX. UNVERIFIED which target shells support `pipefail`; check the target's shell manual.

## Open items

- Test framework choice and a formatter: UNVERIFIED stubs.
