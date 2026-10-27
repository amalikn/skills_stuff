---
Title: Ansible override
Category: reference
Status: current
Authority: local-supplement
Scope: Ansible playbooks, roles, inventories and Jinja2 templates
Last reviewed: 2026-10-19
Summary: >-
  Trace every reference (templates included) and classify tag versus variable before a change, because a renamed tag fails
  silently; check and diff mode as the dry run; idempotence proven by a second run; FQCN; no_log and Vault for secrets;
  narrow become; handlers; one host then a canary; ansible-lint, yamllint and Molecule.
---

# Ansible override

Device-, site- or repository-specific Ansible facts belong to the skill that owns that estate (for example skill-smc for the ansible-wifi repository), not here. This file holds practice true of any
Ansible code.

## Contents

- [Authoritative sources](#authoritative-sources)
- [Before any change: trace every reference](#before-any-change-trace-every-reference)
- [Tools](#tools)
- [Core rule mapping](#core-rule-mapping)
- [Size and limit tweaks](#size-and-limit-tweaks)
- [Open items](#open-items)

## Authoritative sources

Ansible documentation (check mode and diff mode, tags, strategies and `serial`, error handling, handlers, Vault, logging and `no_log`, `become`, tips and tricks), ansible-lint documentation (rules
`fqcn` and `no-changed-when`, profiles), Molecule documentation. Copies: `../documents/research-sources-20261019/`. The operator's lessons: auto-memory
`feedback_trace_all_references_before_ansible_change` (2026-07-28).

## Before any change: trace every reference

Operator directive: understand the complete impact of any change by going through every reference to it in other roles and files. Before editing any identifier (tag, variable, handler, role name, file
path):

1. Search the whole repository with every file type that can hold it: `*.yml`, `*.yaml`, `*.j2`, `*.sh`, `*.cfg`, `*.ini`, `*.json`, `*.md`. **Templates (`*.j2`) are the ones people forget**; they
   consume variables, and a YAML-only search misses them.
2. **Classify every hit** as tag declaration, variable, or unrelated namesake before changing anything. The same word is often both a tag and a variable. Anchor any edit pattern (for example
   `^\s*tags:\s*<name>$`) rather than replacing blindly.
3. Check external callers: CI jobs, scripts and runbooks that pass `--tags` or `--skip-tags`.
4. Collision-check a new name against the repository's existing tag vocabulary.
5. Verify selection with `--list-tasks` and behaviour with a `--check --diff` dry run; `--syntax-check` and `--list-tasks` do not show that a selected task is destructive.
6. **Decide the transition explicitly.** When every caller is inside the repository, rename in one change and update them all. When a caller may sit outside it (another repository, a job template, a
   scheduler, an operator's notes), list both names for one transition (`tags: [<new>, <old>]`), record the old name and its removal condition in the change log, and remove it once no caller remains.
   This is the shim rule for code moves ([references/refactoring-and-promotion.md](../references/refactoring-and-promotion.md)) applied to a tag: the old name keeps working until nothing uses it, and
   it is never left in place without a recorded end (USER_STATED: the operator's renames keep an old name readable during a transition, 2026-10-19).

**A renamed tag fails silently.** Ansible does not warn on an unmatched tag: the old command still exits 0 and runs only the tasks tagged `always`, while selecting none of the intended ones. After a
rename, update every runbook and history copy (USER_STATED; the documentation's `always` and `never` tag behaviour is VERIFIED_PRIMARY, the lack of a warning is from the operator's incident).

Why: a tag added to fix one bug once made a destructive wipe-and-re-clone reachable under a name that read like a repair, coupled to a template in another role.

## Tools

| Job        | Tool                                                                     | Note                                                                                                      |
| ---------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Lint       | ansible-lint, at the profile the project sets (`min` up to `production`) | Profiles gradually increase rule strictness (VERIFIED_PRIMARY)                                            |
| YAML lint  | yamllint                                                                 | See [yaml-json-toml.md](yaml-json-toml.md)                                                                |
| Role tests | Molecule                                                                 | Tests collections, playbooks and roles; supports the latest two major Ansible versions (VERIFIED_PRIMARY) |
| Dry run    | `ansible-playbook --check --diff`                                        | See the mapping below                                                                                     |
| Version    | The project's pin of `ansible-core` and collections (`requirements.yml`) | Read the docs for that version                                                                            |

## Core rule mapping

| Core reference                      | In Ansible                                                                                                                                                     |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| safety-and-writes (plan then apply) | `--check --diff` is the plan. Modules that support check mode report the changes they would make; modules that do not support it report nothing and do nothing |
|                                     |   (VERIFIED_PRIMARY), and tasks that depend on a registered result from a skipped task may not show output. Say which tasks the dry run did not cover          |
| safety-and-writes (idempotence)     | Run twice; the second run must report `changed=0`. Commands and shell tasks declare `changed_when`, or `creates`/`removes` (ansible-lint                       |
|                                     |   `no-changed-when`, VERIFIED_PRIMARY)                                                                                                                         |
| safety-and-writes (canary           | One host end to end, then a small canary with `serial` and `max_fail_percentage` (VERIFIED_PRIMARY keywords); the fleet run is the operator's, from a command  |
|   before batch)                     |   handed over, never an agent-run batch (operator, depth before breadth)                                                                                       |
| security (secrets)                  | Secrets from Ansible Vault or a lookup to the secret store, never inline; `no_log: true` on any task that carries one (VERIFIED_PRIMARY); Vault protects data  |
|                                     |   at rest only, so `no_log` still matters once decrypted (VERIFIED_PRIMARY)                                                                                    |
| security (least privilege)          | `become` on the task or block that needs it, not the whole play (UNVERIFIED as a documented recommendation; follows least privilege)                           |
| design-principles (vocabulary)      | Fully qualified collection names (`ansible.builtin.copy`), checked by ansible-lint `fqcn` (VERIFIED_PRIMARY)                                                   |
| errors-and-timeouts                 | `block` and `rescue` for recovery; `any_errors_fatal` or `max_fail_percentage` to stop a bad rollout; `timeout` on tasks and `async` for long ones. Note tag   |
|                                     |   selection supersedes block error handling: an untagged `rescue` or `always` section does not run when tags select only the block (VERIFIED_PRIMARY)          |
| efficiency-and-measurement          | Handlers instead of repeated restarts (a handler runs only once however many tasks notify it, VERIFIED_PRIMARY); SSH pipelining and fact caching where the     |
|                                     |   project allows (UNVERIFIED stub)                                                                                                                             |
| documentation-and-headers           | A role `README.md` and `meta/main.yml` list the role's variables, defaults, tags and handlers; each playbook starts with a `#` block giving purpose and usage  |
| configuration-and-literals          | Hosts and addresses in inventory and `group_vars`, never in tasks; defaults in `defaults/main.yml`                                                             |
| documentation-and-headers           | No `# noqa` on a task; fix the cause (FQCN, a truthy value, a rename with every reference updated)                                                             |
|   (suppression)                     |                                                                                                                                                                |

## Size and limit tweaks

| Item                      | Value                                                             | Reason                                                                         |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| A role's `tasks/main.yml` | About 200 lines, split with `import_tasks` by concern beyond that | UNVERIFIED judgement; maps the core module budget to tasks                     |
| A playbook                | Under about 100 lines; logic belongs in roles                     | UNVERIFIED judgement                                                           |
| Task name                 | Every task has a `name`                                           | Output and `--start-at-task` rely on it (UNVERIFIED rule name in ansible-lint) |

## Open items

- Pinned ansible-lint profile recommendation and Molecule driver choice: UNVERIFIED stubs.

> **Learned 2026-10-20** · ansible-core 2.21.5 · VERIFIED_PRIMARY · Source: smc-resiliency spike/render_site.sh and spike/render/tasks (apn
> e764a3e) against ansible-wifi f3a5dca8 · Falsifier: a template that renders identically without its task's options
> To render a role's template outside the role (to build a config image, a diff, a preview), copy what the real task and play pass, not just the
> `src`: the task's options (`lstrip_blocks: yes` here: without it the netplan file came out unparseable), the role vars the playbook sets (the role
> defaults were null placeholders), and the defaults at role precedence (a throwaway role linking the real `defaults/main.yml`; `include_vars` would
> outrank the inventory). Prove it against a file the real role wrote on a live host.

> **Learned 2026-10-23** · ansible-core 2.21.5 · VERIFIED_PRIMARY (three Ubuntu 22.04 hosts over Teleport; `ps -eo args` against the probe's counts) ·
> Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/files/probe.py` and `tasks/probe.yml` (uncommitted at writing) · Falsifier: an
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

> **Learned 2026-10-23 (b)** · ansible-core 2.21.5 · VERIFIED_PRIMARY · Source: docs.ansible.com playbook_guide/playbooks_variables.html, "Registering variables"
> ("If a task fails or is skipped, Ansible still registers a variable with a failure or skipped status", read 2026-10-23); local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/chroot.yml` · Falsifier: a skipped task that
> leaves an earlier registered value in place
> A task file included twice with a step switch (`open` / `close`) cannot hand a registered result from one pass to the other: on the second pass
> the skipped task re-registers the name with a skipped result. Keep the decision in a fact the second pass does not touch:
>
> ```yaml
> - name: Remember whether this role adds policy-rc.d
>   ansible.builtin.set_fact:
>     smc_change_policyrcd_added: "{{ not smc_change_policyrcd.stat.exists }}"
>   when: smc_change_chroot_step == 'open'
> ```

> **Learned 2026-10-23 (c)** · ansible-core 2.21.5, ansible-lint production profile · VERIFIED_PRIMARY (role runs on stage hosts; ansible-lint pass) ·
> Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/main.yml`, `record.yml`, `actions/command.yml` · Falsifier: a failed run that
> leaves no record
> To record every run of a role, failed ones included: wrap the role body in `block`/`rescue`; the rescue keeps `ansible_failed_task.name` and
> `ansible_failed_result.msg` in a fact, writes the record (`delegate_to: localhost`, `check_mode: false`, so check runs are recorded too) and fails
> again. A command that really needs a shell (an operator-supplied string with pipes) runs as `ansible.builtin.command: argv: [/bin/sh, -c, ...]`,
> which states the shell and passes ansible-lint `command-instead-of-shell` without a suppression.

> **Learned 2026-10-23 (d)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (smc_change runs, stage hosts) · Source: local-knowledge-ansible
> `ansible-wifi/roles/smc_change/tasks/probe.yml`, `playbooks/smc_change.yml` (uncommitted at writing) · Falsifier: a `-l host` run that still
> runs a `hosts: localhost` play
> Four traps met building one role: (1) a `-l` limit filters every play, so a `hosts: localhost` play is skipped ("no hosts matched"); run
> such steps in the managed group's play with `run_once: true` and `delegate_to: localhost` (`delegate_facts: true` to keep a fact there).
> (2) In a folded scalar (`>-`), `'\n'` inside Jinja reaches the output as a literal backslash-n; take the newline from a variable set in a
> double-quoted YAML string (`nl: "\n\n"`). (3) `lookup('file', <list>)` fails ("'_AnsibleLazyTemplateList' object has no attribute
> 'split'"); loop over the files and accumulate. (4) With `ignore_unreachable: true` on a first `ping`, an offline host can be recorded and
> ended with `meta: end_host`, which is not a failure, so `max_fail_percentage: 0` does not stop the run for the hosts after it.
>
> ```yaml
> - name: Join the probe parts in name order
>   ansible.builtin.set_fact:
>     smc_change_probe_src: >-
>       {{ (smc_change_probe_src if smc_change_idx > 0 else '') ~ lookup('ansible.builtin.file', smc_change_part) ~ smc_change_nl }}
>   vars:
>     smc_change_nl: "\n\n"
>   loop: "{{ query('ansible.builtin.fileglob', role_path ~ '/files/probe/*.py') | sort }}"
> ```

> **Learned 2026-10-23 (e)** · task comments · USER_STATED (operator, 2026-10-23: "not for every task but the simple ones you can ignore
> but the ones which should have some description you can add") · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/` ·
> Falsifier: the operator asks for a comment on every task, or for none
> A comment goes above a task only when it says something the name does not: why the task exists, a constraint, a non-obvious effect or
> failure mode. Simple tasks (a stage banner, a debug print, an include whose name says it all) carry none. Each task file starts with a
> header block: purpose, Called by, Reads, Sets, Notes.

> **Learned 2026-10-23 (f)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (smc_change role, ansible-lint production profile) · Source:
> local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/` · Falsifier: a templated free-form include_tasks that passes syntax-check
> (1) `include_tasks: "{{ 'a.yml' if x else 'b.yml' }}"` fails syntax-check ("Invalid options"); write `include_tasks:` with `file: ...`.
> (2) In a folded scalar (`>-`) a more-indented continuation line keeps its newline, which shows as `\n` in output; keep continuations at
> the same indent or move the expression into a variable. (3) Read-only commands whose output a later task prints need `check_mode:
> false`, or a `--check` run reports empty values. (4) Lint for inventories: `ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED=true
> ansible-inventory -i <file> --list` fails on a source that does not parse; it reads only, so it can cover every inventory, existing ones
> included. (5) Per-host state a rerun must honour (done hosts skipped, a force flag to redo them) belongs on the controller (one file per
> host, written with `delegate_to: localhost`), not on the managed box.

> **Learned 2026-10-26 (e)** · ansible-core 2.21.5, ansible.posix 2.2.2 · VERIFIED_PRIMARY (core source, runs on SMCs over Teleport) ·
> Source: local-knowledge-ansible `76b0f86` `ansible-wifi/roles/smc_change/tasks/await_job.yml`, `callback_plugins/task_timing.py` ·
> Falsifier: an `until` loop that retries after "Connection timed out during banner exchange"
> (1) `until`/`retries` do not retry an unreachable host: a connection failure raises out of the retry loop in `task_executor.py`. For a
> long job over a link that drops, start it with `async: N` + `poll: 0` (the job keeps running detached, so the drop no longer kills dpkg
> mid-install), poll with `async_status` + `until` + `ignore_unreachable: true`, then `wait_for_connection` and poll again when the first
> poll came back unreachable. (2) `async` + `poll: 0` on `shell` under `--check` runs nothing ("Command would have run if not in check
> mode"), and `async_status` supports check mode. (3) ansible-core 2.21 ignores the old `[defaults] callback_whitelist`
> (`ansible-config dump` shows `CALLBACKS_ENABLED = []`); use `callbacks_enabled`. A callback with `CALLBACK_NEEDS_ENABLED = False` in a
> playbook-adjacent `callback_plugins/` loads without any config. (4) A callback's options come from a literal `DOCUMENTATION` string read
> by the loader (not executed), so a subclass of `profile_tasks` must copy the option definitions, not import them.
>
> ```yaml
> - name: Install the target build live
>   ansible.builtin.apt: {name: "{{ specs }}", state: present, only_upgrade: true}
>   async: 1800
>   poll: 0
>   register: job
> - name: Wait for the live install
>   ansible.builtin.include_tasks: await_job.yml   # async_status until finished, ignore_unreachable, wait_for_connection, poll again
>   vars: {smc_change_job: "{{ job }}", smc_change_job_name: the live install}
> ```

> **Learned 2026-10-26 (f)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local test: three local hosts, `serial: 3`, two `include_tasks`) ·
> Source: local-knowledge-ansible `plans/smc-change-run-once-20261026_2220.patch` · Falsifier: a `run_once` task whose fact or register is
> missing on the second host of the batch
> `run_once: true` runs the task on the first host of the batch and applies its result to every host in the batch: `include_vars`, a
> looping `set_fact` that accumulates, and a delegated command's `register` all reached h2 and h3. The `when` is judged on the first host
> only, so use it only where the condition is the same for every host. It is once per serial batch, not once per run: with `serial: 5`
> and 10 hosts it runs twice; for once per run use a play on `localhost` before the host play and read `hostvars['localhost']`.
>
> ```yaml
> - name: Join the probe parts in name order
>   ansible.builtin.set_fact:
>     src: "{{ (src if idx > 0 else '') ~ lookup('ansible.builtin.file', part) }}"
>   loop: "{{ query('ansible.builtin.fileglob', role_path ~ '/files/probe/*.py') | sort }}"
>   loop_control: {loop_var: part, index_var: idx}
>   when: src is not defined or base is none
>   run_once: true
> ```

> **Learned 2026-10-27 (g)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local tests on rct prod inventory, controller only) ·
> Source: local-knowledge-ansible `playbooks/smc_change.yml` first play + `roles/smc_change/tasks/pending.yml` · Falsifier: a host the first
> play left out of the group still appears in the second play's serial batches
> To do work once per run and keep serial batches dense, put a play with no `serial` before the serial play: work there runs once
> (`run_once` there is once per run, since the play has one batch), and `group_by` sorts hosts into a group the next play targets
> (`hosts: smc_change_todo`). Serial batches are built from that play's host list when it starts, so excluded hosts take no slot. A group with
> no members gives "Could not match supplied host pattern ... skipping: no hosts matched" and the play is skipped, not failed; set any fact a
> later play reads (a run-start stamp) in the first play, with `delegate_to: localhost` + `delegate_facts: true`.
>
> ```yaml
> - name: Prepare the run and pick the SMCs it still has to do
>   hosts: smc_bases
>   gather_facts: false
>   tasks:
>     - name: Sort the targeted SMCs
>       ansible.builtin.group_by:
>         key: "{{ 'smc_change_done' if smc_change_done_why is defined else 'smc_change_todo' }}"
> - name: Apply one SMC change spec and verify it
>   hosts: smc_change_todo
>   serial: "{{ smc_change_serial | default(1) }}"
> ```

> **Learned 2026-10-27 (h)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (bug seen, fix tested with `ansible -m debug`) ·
> Source: local-knowledge-ansible `roles/smc_change/tasks/pending.yml` (Teleport proxy) · Falsifier: `x | default('') is search('[.]t[.]')`
> true for a matching x without parentheses
> Parenthesise a filter chain before a test: `ansible_host | default('') is search('\\.teleport\\.')` evaluated false for
> `host01.teleport.example.net` inside a `when`/`if`, while `(ansible_host | default('')) is search('[.]teleport[.]')` is true. `[.]` also
> avoids backslash escaping across YAML and Jinja string literals.
>
> ```yaml
> smc_change_tsh_proxy: >-
>   {{ (ansible_host | default('')) | regex_replace('^' ~ (inventory_hostname | regex_escape) ~ '[.]', '')
>      if (ansible_host | default('')) is search('[.]teleport[.]') else '' }}
> ```

> **Learned 2026-10-27 (i)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (source `plugins/connection/ssh.py` `_ssh_retry`, timed on a closed
> port: retries 3 = 4.6 s, 8 = 116.7 s) · Source: local-knowledge-ansible `playbooks/smc_change.yml` play vars · Falsifier: a retry after a
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

> **Learned 2026-10-27 (j)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local run: three hosts, plan banner printed once with `apply`; part 2
> is Ansible's documented behaviour that a skipped task still registers its variable, not tested here) · Source: local-knowledge-ansible
> `plans/smc-change-resume-20261027_1038/prepare-once.patch` (`tasks/prepare.yml`, `tasks/recovery.yml`) · Falsifier: tasks inside a
> `run_once` include running on every host
> (1) `run_once` set on `include_tasks` belongs to the include; give the included tasks the keyword with `apply: {run_once: true}`.
> (2) A task skipped by `when` still sets its `register` (to a skipped result), so a fact that may come from elsewhere needs its own name:
> the role fingerprint prepared once is `smc_change_code_fingerprint`, and the per-host command keeps `register: smc_change_code_digest`,
> read as `smc_change_code_fingerprint | default(smc_change_code_digest.stdout)`.
>
> ```yaml
> - name: Load and check the change spec once
>   ansible.builtin.include_tasks:
>     file: load_spec.yml
>     apply:
>       run_once: true
>   vars:
>     smc_change_spec_only: true
> ```

> Design patterns realised in Ansible (resumable journal, done ledger, partition before batch, plug-in probe, plan then apply) are in
> [../references/design-patterns.md](../references/design-patterns.md), table "Language realisations"; entries here record the Ansible behaviour they rely on.

> **Learned 2026-10-27 (k)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (seen in smc_change run output, fixed and re-rendered in a scratch copy) ·
> Source: local-knowledge-ansible `plans/smc-change-resume-20261027_1038/prepare-once.patch` (`tasks/plan.yml`) · Falsifier: a `to_json` value
> inside a `debug` message list printed without backslashes
> `debug` prints its `msg` as JSON, so a list item built with `to_json` is encoded twice and every quote shows as `\"`
> (`BACKUP   {\"paths\": [\"/etc/php\", ...]}`). For operator-facing lines, write the values as words (`join(', ')`, a phrase per flag), and
> keep `to_json` for files and machine records.
>
> ```yaml
> - 'BACKUP   ' ~ ((smc_change_spec.backup.paths | default([]) | join(', ')) or 'no paths')
>   ~ ('; repack the packages about to change' if smc_change_spec.backup.repack | default(false) else '')
> ```

> **Learned 2026-10-27 (l)** · ansible-core 2.21.5, `include_tasks` · VERIFIED_PRIMARY (a running rct apply batch started 12:50 picked up task
> files edited at 13:00-13:15; traced per file, harmless only because its spec and probe program were already loaded) · Source:
> local-knowledge-ansible `roles/smc_change/tasks/main.yml` (dynamic includes), commit 0e8a2f0 · Falsifier: an edit to an included task file
> after a play started that the play does not run
> `include_tasks` reads its file when the play reaches it, not at start, so editing a role's task files while a playbook runs changes that
> run mid-flight (`import_tasks` is static). Edit task files only when no playbook using them runs; for long rollouts, freeze or stage edits.

> **Learned 2026-10-27 (m)** · ansible-core 2.21.5, `serial` batches, linear strategy · VERIFIED_PRIMARY (smc_change summaries: five and six
> hosts with identical per-stage seconds) · Source: local-knowledge-ansible `tasks/stage.yml` (phase timing per stage entry) · Falsifier: per-host
> stage times that differ within one batch for hosts that ran every stage
> With the default linear strategy every task finishes on all hosts of a batch before the next starts, so a per-host timer between stage
> markers measures the batch's wall-clock for that stage: the slowest host (or one reboot) sets every host's line. Measure per-host work
> with a task-timing callback, not stage markers, and size budgets per batch.
