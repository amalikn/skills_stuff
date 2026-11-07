---
Title: shell override - learned safety
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned safety part of the shell override; the entry file holds the tools and the core rule mapping.
---

# shell: learned safety

Part of [shell.md](../shell.md).

> **Learned 2026-11-02** · POSIX sh, `trap ... EXIT` · VERIFIED_PRIMARY (macOS `/bin/sh` rc 0; dash on Ubuntu 22.04 rc 2) · Source: ansible-wifi `rct-avr-smsc`, test `test_write_needs_every_value` · Falsifier: macOS `/bin/sh`
> returning non-zero from the snippet below A plain `trap 'rm -f "$f"' EXIT` can turn a failed step into exit 0, depending on the shell: with `: "${X:?}"` failing, macOS `sh` returned 0 and dash 2. A
> test run under the local `/bin/sh` is not proof of the target's shell. Keep the code, or avoid the trap: a transient file the runner removes needs none.
>
> ```sh
> trap 'rc=$?; rm -f "$f"; exit "$rc"' EXIT   # keeps the step's exit code
> ```

> **Learned 2026-11-02** · POSIX sh, crontab rewrite · VERIFIED_PRIMARY (offline test with stub commands) · Source: ansible-wifi `roles/smc_change/files/tests/test_spec_stats_cron.py`, commit 70bb516 ·
> Falsifier: a `crontab` that refuses empty input.
> `crontab -l | sed ... | crontab -` installs an empty crontab when the read fails, even under `set -e`, as a pipeline reports its last command. Write to a file, check the wanted line is in it, then install it:
>
> ```sh
> crontab -l > "$t"
> sed -i -E "$e" "$t"
> grep -Fqx "$j" "$t" || exit 1
> crontab "$t"
> ```

> **Learned 2026-11-02** · any guard around a scheduled job · VERIFIED_PRIMARY (production log: two runs of one job in the same second) · Source: ansible-wifi `files/changes/rct-avr-smsc/scripts/smsc_prove_page.sh`, commit 70bb516 ·
> Falsifier: a scheduler that shows the job in the process table before its tick.
> A guard that stops at the tick plus a process check leaves a gap: the job is not in the process table until the scheduler has started it. Hold off for a few seconds after the tick too, and read the
> schedule on the box, as a box can differ from what the code deploys.
