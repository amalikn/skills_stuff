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

> **Learned 2026-10-19** · bash (agent tool calls) · USER_STATED · Source: two incidents on 2026-10-19 (skill-drawio CHANGELOG, Archcore promotion; unified-network-controller, import_graph retirement) · Falsifier: a multi-line tool command whose later line does not run after an earlier step fails without set -e
> A multi-line command run without `set -e` carries on after a failed step: an edit script that stopped on its own assertion was followed by a
> `git rm` on the next line, twice in one day. Guard each edit step (`... || exit 1`) or start the block with `set -euo pipefail`, and put a
> destructive step (delete, `git rm`, push) in its own call after the edit is confirmed.

> **Learned 2026-10-20** · bash, procps `pkill -f` over ssh · VERIFIED_PRIMARY (one incident: the remote session ended with ssh exit 255) · Source:
> unified-network-controller session 2026-10-20, a scratch check on apn-unc01 · Falsifier: a `pkill -f <path>` run through `ssh host '<command>'`
> that leaves its own session alive
> `pkill -f <pattern>` matches full command lines, including the remote shell running it: `ssh host 'cd /tmp/x; pkill -f /tmp/x/run.sh; ...'`
> killed its own `bash -c` (whose command line contains the pattern) and dropped the session. Match on something only the target has, or read
> the PID first (`pgrep -f` then exclude `$$`), or make the pattern not match itself (`pkill -f '[/]tmp/x/run.sh'`).
>
> ```bash
> # wrong: the remote bash -c line contains the pattern, so pkill ends its own session (ssh exit 255)
> ssh host 'cd /tmp/x; pkill -f /tmp/x/run.sh; nohup /tmp/x/run.sh &'
> # right: a bracket the pattern matches but its own text does not
> ssh host "pkill -f '[/]tmp/x/run.sh'; nohup /tmp/x/run.sh >/tmp/x/log 2>&1 &"
> ```

## Open items

- Test framework choice and a formatter: UNVERIFIED stubs.

> **Learned 2026-10-20** · bash on macOS, tsh 17/18 · VERIFIED_PRIMARY · Source: skill-smc scripts/overlay-usage-breakdown.sh `with_deadline`
> (skills_stuff 01f5bb3) · Falsifier: `perl -e 'alarm 60; exec @ARGV' tsh ssh ...` ending at 60 s
> macOS has no `timeout(1)`, and `perl -e 'alarm N; exec @ARGV' cmd` did not stop `tsh ssh` (it ran 2 min 50 s past a 60 s alarm). A watcher does:
>
> ```bash
> with_deadline() {
>   "$@" & local pid=$!
>   ( sleep "$deadline"; kill -TERM "$pid" 2>/dev/null; sleep 5; kill -KILL "$pid" 2>/dev/null ) & local watcher=$!
>   wait "$pid"; local rc=$?
>   kill "$watcher" 2>/dev/null; wait "$watcher" 2>/dev/null
>   return $rc
> }
> ```
>
> Prove it with a short limit (3 s stopped the host in 8 s, the 5 s KILL grace included).

> **Learned 2026-10-20 (c)** · bash, a script sent over ssh on stdin (`ssh host bash -s < script`) · VERIFIED_PRIMARY (three trial runs did
> nothing past their first line; with `ssh -n` they ran) · Source: unified-network-controller `infra/apn-unc01/ops/collector-trial.sh` (its
> predecessor in a session scratchpad, 2026-10-20) · Falsifier: an ssh release that does not read stdin when given a remote command
> A script that reaches a host as `bash -s` reads its own lines from stdin. Any command inside it that reads stdin, `ssh` first of all (also
> `read`, `docker exec -i`, a Python program without input), swallows the rest of the script, which then ends silently after that line with
> exit 0. Give every such inner command its own stdin:
>
> ```bash
> la() { timeout 30 ssh -n -o BatchMode=yes "$h" cat /proc/loadavg; }          # -n: stdin from /dev/null
> timeout 900 "$PY" batch_push_devices.py ... --dry-run < /dev/null > "$out" 2>&1
> ```

