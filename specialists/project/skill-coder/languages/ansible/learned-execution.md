---
Title: ansible override - learned execution
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned execution part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned execution

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-26 (e)** · ansible-core 2.21.5, ansible.posix 2.2.2 · VERIFIED_PRIMARY (core source, runs on SMCs over Teleport) · Source: local-knowledge-ansible `76b0f86` `ansible-wifi/roles/smc_change/tasks/await_job.yml`, `callback_plugins/task_timing.py` · Falsifier: an `until` loop that retries after "Connection timed out during banner exchange"
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

> **Learned 2026-10-27 (g)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local tests on rct prod inventory, controller only) · Source: local-knowledge-ansible `playbooks/smc_change.yml` first play + `roles/smc_change/tasks/pending.yml` · Falsifier: a host the first
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

> **Learned 2026-10-27 (j)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local run: three hosts, plan banner printed once with `apply`; part 2 is Ansible's documented behaviour that a skipped task still registers its variable, not tested here) · Source: local-knowledge-ansible `plans/smc-change-resume-20261027_1038/prepare-once.patch` (`tasks/prepare.yml`, `tasks/recovery.yml`) · Falsifier: tasks inside a
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

> **Learned 2026-10-27 (l)** · ansible-core 2.21.5, `include_tasks` · VERIFIED_PRIMARY (a running rct apply batch started 12:50 picked up task files edited at 13:00-13:15; traced per file, harmless only because its spec and probe program were already loaded) · Source: local-knowledge-ansible `roles/smc_change/tasks/main.yml` (dynamic includes), commit 0e8a2f0 · Falsifier: an edit to an included task file
> after a play started that the play does not run
> `include_tasks` reads its file when the play reaches it, not at start, so editing a role's task files while a playbook runs changes that
> run mid-flight (`import_tasks` is static). Edit task files only when no playbook using them runs; for long rollouts, freeze or stage edits.

> **Learned 2026-10-27 (m)** · ansible-core 2.21.5, `serial` batches, linear strategy · VERIFIED_PRIMARY (smc_change summaries: five and six hosts with identical per-stage seconds) · Source: local-knowledge-ansible `tasks/stage.yml` (phase timing per stage entry) · Falsifier: per-host
> stage times that differ within one batch for hosts that ran every stage
> With the default linear strategy every task finishes on all hosts of a batch before the next starts, so a per-host timer between stage
> markers measures the batch's wall-clock for that stage: the slowest host (or one reboot) sets every host's line. Measure per-host work
> with a task-timing callback, not stage markers, and size budgets per batch.
