---
Title: shell override - learned safety
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
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

> **Disputed 2026-11-19** · POSIX sh, `trap ... EXIT` · VERIFIED_PRIMARY (macOS `/bin/sh` and dash on Ubuntu, OrbStack `continuum-linux`) · Source: continuum-app `.githooks/pre-push` (TD-196,
> DL-037), commit 0ffd12f · Falsifier: macOS `/bin/sh -c 'set -eu; f(){ rc=$?; exit "$rc"; }; trap f EXIT; : "${X:?}"'` returning non-zero · Conflicts: the Learned 2026-11-02 `trap
> ... EXIT` entry above (its snippet "keeps the step's exit code")
> Saving `$?` does not help on macOS `/bin/sh`: after a `set -u` or `${X:?}` failure, `$?` is already 0 when the EXIT trap runs, so the snippet above exits 0 (dash exits 2). A plain `false` under
> `set -e` is reported correctly by both (1), so a test with `false` does not catch it. Where a false pass matters (a gate, a pre-push hook), set a flag on the last line and refuse to exit 0 without
> it. Measured on both shells: `false`, `${X:?}` and an unset `$Y` give 1 (macOS) and 1/2/2 (dash); only the completed run gives 0.
>
> ```sh
> finished=0
> on_exit() {
>   rc=$?
>   [ "$finished" = 1 ] || [ "$rc" -ne 0 ] || rc=1   # macOS sh: $? is 0 after a set -u failure
>   cleanup || echo "cleanup failed (result unchanged)" >&2
>   exit "$rc"
> }
> trap on_exit EXIT
> # ... the work ...
> finished=1
> ```

> **Learned 2026-11-02** · POSIX sh, crontab rewrite · VERIFIED_PRIMARY (offline test with stub commands) · Source: ansible-wifi `roles/smc_change/files/tests/test_spec_stats_cron.py`, commit 70bb516 ·
> Falsifier: a `crontab` that refuses empty input. `crontab -l | sed ... | crontab -` installs an empty crontab when the read fails, even under `set -e`, as a pipeline reports its last command. Write
> to a file, check the wanted line is in it, then install it:
>
> ```sh
> crontab -l > "$t"
> sed -i -E "$e" "$t"
> grep -Fqx "$j" "$t" || exit 1
> crontab "$t"
> ```

> **Learned 2026-11-02** · any guard around a scheduled job · VERIFIED_PRIMARY (production log: two runs of one job in the same second) · Source: ansible-wifi `files/changes/rct-avr-smsc/scripts/smsc_prove_page.sh`, commit 70bb516 ·
> Falsifier: a scheduler that shows the job in the process table before its tick. A guard that stops at the tick plus a process check leaves a gap: the job is not in the process table until the
> scheduler has started it. Hold off for a few seconds after the tick too, and read the schedule on the box, as a box can differ from what the code deploys.

> **Learned 2026-11-19** · Bash under `set -euo pipefail` · VERIFIED_PRIMARY (rc 141 on a real 7.7 GB card write; a guard test reproduces it) · Source: smc-resiliency
> lab/payloads/lab_flash_io.sh `readback_sha`, 20261119_2340 · Falsifier: a pipeline whose early-exiting reader leaves the writer alive and the status 0. A read-back like `reader | head -c N | shasum`
> fails when the reader still has bytes to write after `head` has its N: the reader dies of SIGPIPE (141), `pipefail` makes the pipeline fail, and `set -e` exits before the compare runs, so nothing is
> reported and no cleanup happens. Turn pipefail off for that pipeline only, in a subshell, and let the compare be the check: a short or failed read gives a different hash. Separately, on macOS a
> card's new FAT partition is auto-mounted between a raw write and its read-back, and Spotlight and fseventsd change it: write sector 0 (the partition table) last, with the rest written and compared
> first.
>
> ```bash
> # lab/payloads/lab_flash_io.sh
> readback_sha() {
>   local blocks=$((($2 + BS - 1) / BS))
>   (
>     set +o pipefail
>     dd if="$1" bs=$BS count=$blocks 2>/dev/null | head -c "$2" | shasum -a 256 | cut -d' ' -f1
>   )
> }
> ```

> **Learned 2026-11-25 (c)** · bash 3.2 and 5.x, `set -euo pipefail` · VERIFIED_PRIMARY (reproduced: the node setup stopped silently until fixed) · Source:
> home NAS project `scripts/host/pve_alerts.sh`, `scripts/ct/samba_setup.sh`, `scripts/ct/tailscale_setup.sh` (commit 98ab4a7) · Falsifier: `printf x | { read -r v; echo $?; }` printing 0
> `read -r v` returns 1 when the input ends without a newline, even though it filled `v`. A secret piped from a password-manager wrapper that strips the
> newline (`printf '%s'`) therefore stops a `set -e` script at the `read`, with no message. Accept a last line without a newline explicitly, then
> check the value:
> ```bash
> read -r topic || true   # the value arrives without a trailing newline; read returns 1 at EOF
> [ -n "$topic" ] || { echo "empty value on stdin" >&2; exit 1; }
> ```
