---
Title: shell override - learned other
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned other part of the shell override; the entry file holds the tools and the core rule mapping.
---

# shell: learned other

Part of [shell.md](../shell.md).

> **Learned 2026-11-06** · bash, scripts that run long · VERIFIED_SECONDARY · Source: the bash manual's reading of input in chunks (bash reads a
> script file as it executes); observed risk in apn smc-resiliency S3 when a measured run lasted an hour · Falsifier: a bash version that reads the
> whole file before running it
> **Never edit a script while it runs.** bash reads the file as it goes, so an edit to a running script (a long measured run, a slow
> rollout) can make it execute half-old, half-new lines. Edit after it ends, or run long jobs from a copy (`cp x.sh /tmp/x.$$.sh && bash
> /tmp/x.$$.sh`), or wrap the body in a function called on the last line so the whole file is parsed first.

> **Learned 2026-10-30** · bash, `set -o pipefail` with `grep -q` · VERIFIED_PRIMARY (ansible-lint `risky-shell-pipe` on `ss ... | grep -q`; reasoning from `grep -q`
> exiting at the first match) · Source: ansible-wifi `roles/smc_application/tasks/ubuntu-php-cve-2026-109618.yml` review, commit fb6ae80b · Falsifier: `set -o pipefail; yes | grep -q y` returning 0
> `grep -q` (and `head`) exits at the first match; the writer then dies of SIGPIPE (141), and with `pipefail` the pipeline fails on a match: a check that passes turns into a failure. Adding `pipefail`
> because a linter asks is wrong there. Drop the pipe (`grep -q X <<<"$(cmd)"`, or capture first: `out=$(cmd); grep -q X <<<"$out"`), or keep `pipefail` only where every stage reads all its input.
