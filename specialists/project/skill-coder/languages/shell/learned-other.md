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

> **Learned 2026-11-09** · shell, ssh and macOS tooling · VERIFIED_PRIMARY (smc-resiliency S1 bench, transcript spike/out/s1-pi4-bench.log) ·
> Source: smc-resiliency lab/adapters/transports.py @ 01cf282c and later · Falsifier: the behaviours below not reproducing on the same versions.
> - A tool that prints its error on stdout and exits 0 (`vcgencmd` without root: `Can't open device file: /dev/vcio`) makes `cmd > file && next`
>   carry the error text forward as data. Check the content (an expected key or shape), not only the exit code.
> - ssh with `StrictHostKeyChecking=no` and a saved key that no longer matches (an A/B box: each slot has its own host key) disables password
>   authentication silently; use `UserKnownHostsFile=/dev/null` for such lab boxes only. A ControlPath must be under 104 bytes. An agent holding
>   many keys exhausts the server's MaxAuthTries before the password: `SSH_AUTH_SOCK=` with `-o PubkeyAuthentication=no` or `IdentitiesOnly=yes`.
> - A password helper (`SSH_ASKPASS` with `SSH_ASKPASS_REQUIRE=force`) keeps a vault password out of argv, output and logs.
> - macOS: `screen` 4.00.03 has no `-Logfile` (`-L` writes `screenlog.0` in the working folder); `sync FILE` ignores the file and syncs everything
>   (slow); a `sudo` prompt behind `ssh ... | sudo dd` can sit hidden until Enter is pressed.
> - Typing into a console by fixed sleeps sends a password at the wrong prompt and echoes it into the log; wait for each prompt on screen first.

