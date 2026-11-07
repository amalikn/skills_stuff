---
Title: ansible override - learned connections
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned connections part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned connections

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-23** · ansible-core 2.21.5 · VERIFIED_PRIMARY (three Ubuntu 22.04 hosts over Teleport; `ps -eo args` against the probe's counts) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/files/probe.py` and `tasks/probe.yml` (uncommitted at writing) · Falsifier: an
> `environment:` value that does not appear in the remote shell's `/proc/<pid>/cmdline`
> A task's `environment:` values are put on the remote shell's command line, so they are visible to `ps` and to `pgrep -f` for as long as the task runs.
> A probe that received its patterns through `environment:` counted its own parent shell as a match (a process that did not exist). Leave the
> process's own ancestor chain out of any `pgrep -f` count, pass patterns on stdin instead, and never pass a secret through `environment:`.
>
> ```python
> # roles/smc_change/files/probe.py (2026-10-23)
> pids, pid = set(), str(os.getpid())
> while pid not in ("0", "") and pid not in pids:
>     pids.add(pid)
>     pid = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[1]   # ppid
> count = len([p for p in run(["pgrep", "-f", pattern])[1].split() if p not in pids])
> ```

> **Learned 2026-10-27 (i)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (source `plugins/connection/ssh.py` `_ssh_retry`, timed on a closed port: retries 3 = 4.6 s, 8 = 116.7 s) · Source: local-knowledge-ansible `playbooks/smc_change.yml` play vars · Falsifier: a retry after a
> remote command's own non-zero exit, or pauses not 0,1,3,7,15,30,30,30
> The ssh connection retries only when ssh itself returns 255, `retries` + 1 attempts, pausing `2**attempt - 1` seconds capped at 30. So
> `retries = 3` (ansible.cfg) rides out about 4 s; 8 about 2 minutes, enough for a satellite or Teleport blip. Set it per play with the
> `ansible_ssh_retries` variable (honoured from play `vars:`). A retry runs the whole module again: fine for idempotent tasks; an async
> start retried after the job began would start a second job.
>
> ```yaml
> vars:
>   ansible_ssh_retries: 8   # pauses 0+1+3+7+15+30+30+30 s
> ```

> **Learned 2026-11-06 (l)** · extra vars with spaces · VERIFIED_PRIMARY · Source: apn smc-resiliency `spike/build/run_roles.sh`, ansible-core 2.21.5,
> 2026-11-06 · Falsifier: `-e key='a b'` reaching the play as one value
> `-e ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'` is split at the spaces, and ssh got a bare `-o`
> ("argument -o: expected one argument", then "A worker was found in a dead state"). Pass such a value as JSON:
> `-e '{"ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"}'`. Also: an inventory that pins
> `ansible_python_interpreter=/usr/bin/python3.10` (Ubuntu 22.04) fails every module on 24.04 (python3.12); pin the interpreter per OS.
