---
Title: ansible override - learned lint and tests
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned lint and tests part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned lint and tests

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-23 (c)** · ansible-core 2.21.5, ansible-lint production profile · VERIFIED_PRIMARY (role runs on stage hosts; ansible-lint pass) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/main.yml`, `record.yml`, `actions/command.yml` · Falsifier: a failed run that
> leaves no record To record every run of a role, failed ones included: wrap the role body in `block`/`rescue`; the rescue keeps `ansible_failed_task.name` and `ansible_failed_result.msg` in a fact,
> writes the record (`delegate_to: localhost`, `check_mode: false`, so check runs are recorded too) and fails again. A command that really needs a shell (an operator-supplied string with pipes) runs
> as `ansible.builtin.command: argv: [/bin/sh, -c, ...]`, which states the shell and passes ansible-lint `command-instead-of-shell` without a suppression.

> **Learned 2026-10-30 (f)** · ansible-core 2.21.5 in git hooks: "Ansible requires blocking IO on stdin/stdout/stderr. Non-blocking file handles
> detected: <stderr>" · VERIFIED_PRIMARY (ansible-wifi pre-push hook failed from VS Code's Git and from an agent shell; passed after the fix, push 9a3a21f0..a8a9d254) · Source: ansible-wifi
> `.git/hooks/pre-push` (local hook, 2026-10-30) · Falsifier: the same hook failing with all three descriptors redirected to files ansible-core checks that fds 0-2 are blocking at start. A hook
> inherits git's pipes, which VS Code and agent terminals leave non-blocking, so any `ansible-playbook`/`ansible-lint` run there must get plain files on all three: `cmd </dev/null >"$log" 2>&1 || {
> cat "$log" >&2; fail; }`. Redirecting stdout alone (`>/dev/null`) is not enough.

> **Learned 2026-11-04 (h)** · ansible-core 2.21.5, test playbooks · VERIFIED_PRIMARY (local-knowledge-ansible smc_change test_guard_goals.yml failed, then passed; 3ebbe56) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/files/tests/test_guard_goals.yml` · Falsifier: a second play on the same host that does not see a fact the first play set
> Facts set in one play stay on that host for every later play of the run, so test cases written as plays on one host leak into each other (a refusal fact from case 1 failed case 2). Give each case
> its own host (`-i case1,case2,case3, -c local`, `hosts: case1`). Also: an `assert` list item with `: ` inside a plain scalar (`- x == 'a: b'`) parses as a mapping and fails with "Conditional
> expressions must be strings"; quote the whole item.

> **Learned 2026-11-17 (a)** · ansible-lint delta gates (a pre-push gate that fails only on findings new since a base commit) · VERIFIED_PRIMARY (ansible-wifi push refused, then
> passed after the fix; rise c4d2ef51..9f17dd64) · Source: ansible-wifi `.git/hooks/pre-push`, `roles/smc_url_capture/tasks/main.yml` · Falsifier: a gate that keeps a rewritten file's old findings out
> of the new count
>
> A delta gate matches findings by file and line content against the base. When a commit in the pushed range rewrites most of a file, its untouched-looking old findings (short module names here) come
> in as new and block the push. Fix them in that file in the same push (here `ansible.builtin.` on all ten tasks); lint the whole file before pushing a rewrite.

> **Learned 2026-11-17 (b)** · `ansible.builtin.shell` with a pipe on Ubuntu 22.04 targets · UNVERIFIED for dash (ansible-lint `risky-shell-pipe` is VERIFIED_PRIMARY; whether
> 22.04's dash accepts `pipefail` was not checked on an SMC) · Source: ansible-wifi `roles/smc_url_capture/tasks/v1_teardown.yml` (rise 9f17dd64) · Falsifier: `set -o pipefail` succeeding under the
> target's `/bin/sh`
>
> The shell module runs `/bin/sh`, which is dash on Ubuntu, and older dash has no `pipefail`, so `set -o pipefail;` alone may fail there. Add it and `args: executable: /bin/bash`. Check what the
> pipeline's new exit status does to the task: `screen -ls` exits non-zero even when it lists sessions, harmless only because the task had `failed_when: false`.
