---
Title: ansible override - learned execution
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned execution part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned execution

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-26 (e)** · ansible-core 2.21.5, ansible.posix 2.2.2 · VERIFIED_PRIMARY (core source, runs on SMCs over Teleport) · Source: local-knowledge-ansible `76b0f86` `ansible-wifi/roles/smc_change/tasks/await_job.yml`, `callback_plugins/task_timing.py` · Falsifier: an `until` loop that retries after "Connection timed out during banner exchange"
> (1) `until`/`retries` do not retry an unreachable host: a connection failure raises out of the retry loop in `task_executor.py`. For a long job over a link that drops, start it with `async: N` +
> `poll: 0` (the job keeps running detached, so the drop no longer kills dpkg mid-install), poll with `async_status` + `until` + `ignore_unreachable: true`, then `wait_for_connection` and poll again
> when the first poll came back unreachable. (2) `async` + `poll: 0` on `shell` under `--check` runs nothing ("Command would have run if not in check mode"), and `async_status` supports check mode.
> (3) ansible-core 2.21 ignores the old `[defaults] callback_whitelist` (`ansible-config dump` shows `CALLBACKS_ENABLED = []`); use `callbacks_enabled`. A callback with `CALLBACK_NEEDS_ENABLED =
> False` in a playbook-adjacent `callback_plugins/` loads without any config. (4) A callback's options come from a literal `DOCUMENTATION` string read by the loader (not executed), so a subclass of
> `profile_tasks` must copy the option definitions, not import them.
>
> ```yaml
> - name: Install the target build live
>  ansible.builtin.apt: {name: "{{ specs }}", state: present, only_upgrade: true}
>  async: 1800
>  poll: 0
>  register: job
> - name: Wait for the live install
>  ansible.builtin.include_tasks: await_job.yml   # async_status until finished, ignore_unreachable, wait_for_connection, poll again
>  vars: {smc_change_job: "{{ job }}", smc_change_job_name: the live install}
> ```

> **Learned 2026-10-27 (g)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local tests on rct prod inventory, controller only) · Source: local-knowledge-ansible `playbooks/smc_change.yml` first play + `roles/smc_change/tasks/pending.yml` · Falsifier: a host the first
> play left out of the group still appears in the second play's serial batches To do work once per run and keep serial batches dense, put a play with no `serial` before the serial play: work there
> runs once (`run_once` there is once per run, since the play has one batch), and `group_by` sorts hosts into a group the next play targets (`hosts: smc_change_todo`). Serial batches are built from
> that play's host list when it starts, so excluded hosts take no slot. A group with no members gives "Could not match supplied host pattern ... skipping: no hosts matched" and the play is skipped,
> not failed; set any fact a later play reads (a run-start stamp) in the first play, with `delegate_to: localhost` + `delegate_facts: true`.
>
> ```yaml
> - name: Prepare the run and pick the SMCs it still has to do
>  hosts: smc_bases
>  gather_facts: false
>  tasks:
>    - name: Sort the targeted SMCs
>      ansible.builtin.group_by:
>        key: "{{ 'smc_change_done' if smc_change_done_why is defined else 'smc_change_todo' }}"
> - name: Apply one SMC change spec and verify it
>  hosts: smc_change_todo
>  serial: "{{ smc_change_serial | default(1) }}"
> ```

> **Learned 2026-10-27 (j)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local run: three hosts, plan banner printed once with `apply`; part 2 is Ansible's documented behaviour that a skipped task still registers its variable, not tested here) · Source: local-knowledge-ansible `plans/smc-change-resume-20261027_1038/prepare-once.patch` (`tasks/prepare.yml`, `tasks/recovery.yml`) · Falsifier: tasks inside a
> `run_once` include running on every host (1) `run_once` set on `include_tasks` belongs to the include; give the included tasks the keyword with `apply: {run_once: true}`. (2) A task skipped by
> `when` still sets its `register` (to a skipped result), so a fact that may come from elsewhere needs its own name: the role fingerprint prepared once is `smc_change_code_fingerprint`, and the
> per-host command keeps `register: smc_change_code_digest`, read as `smc_change_code_fingerprint | default(smc_change_code_digest.stdout)`.
>
> ```yaml
> - name: Load and check the change spec once
>  ansible.builtin.include_tasks:
>    file: load_spec.yml
>    apply:
>      run_once: true
>  vars:
>    smc_change_spec_only: true
> ```

> **Learned 2026-10-27 (l)** · ansible-core 2.21.5, `include_tasks` · VERIFIED_PRIMARY (a running rct apply batch started 12:50 picked up task files edited at 13:00-13:15; traced per file, harmless only because its spec and probe program were already loaded) · Source: local-knowledge-ansible `roles/smc_change/tasks/main.yml` (dynamic includes), commit 0e8a2f0 · Falsifier: an edit to an included task file
> after a play started that the play does not run `include_tasks` reads its file when the play reaches it, not at start, so editing a role's task files while a playbook runs changes that run
> mid-flight (`import_tasks` is static). Edit task files only when no playbook using them runs; for long rollouts, freeze or stage edits.

> **Learned 2026-10-27 (m)** · ansible-core 2.21.5, `serial` batches, linear strategy · VERIFIED_PRIMARY (smc_change summaries: five and six hosts with identical per-stage seconds) · Source: local-knowledge-ansible `tasks/stage.yml` (phase timing per stage entry) · Falsifier: per-host
> stage times that differ within one batch for hosts that ran every stage With the default linear strategy every task finishes on all hosts of a batch before the next starts, so a per-host timer
> between stage markers measures the batch's wall-clock for that stage: the slowest host (or one reboot) sets every host's line. Measure per-host work with a task-timing callback, not stage markers,
> and size budgets per batch.

> **Learned 2026-11-05 (i)** · ansible-core 2.21.5, a gate as a run_once task · VERIFIED_PRIMARY (prod rct inventory, check mode, two and three hosts:
> recap `failed=1` on the first host, `ok=1 failed=0` on the other, no later play) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/tsh_login.yml`, `playbooks/smc_change.yml`
> first play (uncommitted 2026-11-05) · Falsifier: a recap in which every host of the play shows failed=1 after one run_once assert fails A `run_once` assert that fails marks only the first host
> failed; the other hosts stay `ok`. A run-wide gate therefore needs `any_errors_fatal: true` on its play, so the failure ends the run instead of leaving later plays to the other hosts.
>
> ```yaml
> - name: Check the Teleport logins this run needs
>   hosts: smc_bases
>   gather_facts: false
>   any_errors_fatal: true            # the run_once failure inside ends the whole run
>   tasks:
>     - name: Check the Teleport logins this run needs
>       ansible.builtin.include_role: {name: smc_change, tasks_from: tsh_login.yml}   # run_once command + assert
> ```

> **Learned 2026-11-05 (k)** · ansible-core 2.21.5, `strategy: free` with `serial` · VERIFIED_PRIMARY (four local dummy hosts, serial 2, and a
> check-mode run on two production hosts) · Source: local-knowledge-ansible plans/smc-change-free-timeouts-20261105 · Falsifier: under free, a failed host with `max_fail_percentage: 0` stops the next
> batch, or `pause` runs per host Under `free`, Ansible warns that `run_once` and `any_errors_fatal` are not supported, and it refuses `ansible.builtin.pause` outright ("bypasses the host loop"). It
> also ignores `max_fail_percentage`: with one failed host, linear stopped the run but free started the next batch. Before switching a play to free, grep its tasks for `pause`, `run_once`,
> `any_errors_fatal` and cross-host reads. Use `ansible.builtin.wait_for: {timeout: N}` delegated to localhost for a wait, and rebuild any first-failure stop as a gate that reads the run's own results
> before each host starts. Also: YAML 1.1 reads an unquoted `20261105_120000` as the integer 20261105120000 (underscores are digit separators), so quote stamps.
> ```yaml
> - name: Let client traffic reach the changed box   # was ansible.builtin.pause, refused under strategy free
>   ansible.builtin.wait_for: {timeout: "{{ soak_left | int }}"}
>   delegate_to: localhost
> ```

> **Learned 2026-11-05 (l)** · ansible-core 2.21.5, one role imported twice with `import_playbook` in one run · VERIFIED_PRIMARY (dummy hosts;
> a production run where the second change skipped a host as done, citing the first change's record) · Source: local-knowledge-ansible plans/smc-change-free-timeouts-20261105 · Falsifier: a `set_fact`
> from the first import is undefined in the second Host facts (`set_fact`, registered results) and `group_by` groups outlive an `import_playbook`. A role that sets a flag only when it holds, and tests
> it with `is defined`, inherits the first run's value in the second; a host also stays in a group the first run put it in. Ansible cannot unset a fact or remove a host from a group, and `meta:
> clear_facts` leaves `set_fact` values (tested). So reset each per-run flag at the run's start to a value its readers treat as "not set" (`''` or `{}` tested by length, `~` by `is none`), and name
> groups per run (`todo_{{ change }}`): a play's `hosts:` can be templated from `import_playbook` vars (tested).

> **Learned 2026-11-17 (n)** · ansible-core 2.21 multi-play playbooks (import_playbook chains) · VERIFIED_PRIMARY (local test: six local hosts, deferred mode ran the later play
> on all six, then failed the three unfinished ones; standalone mode failed them at once) · Source: local-knowledge-ansible `playbooks/smc_change.yml`, `smc_change_multiple.yml`, ansible-wifi
> `smc_rise_deploy.yml` (2026-11-17) · Falsifier: a host failed in play N still running a task of play N+1 without `meta: clear_host_errors`
>
> A host that ends a play with `meta: end_host` or a skipped import shows `ok` in PLAY RECAP however little was done, and a host failed in one play leaves every later play of the run. To show
> unfinished work without costing the later plays: note the reason in a host fact (`set_fact: incomplete: "{{ incomplete | default([]) + [reason] }}"`), fail at once only when nothing wraps the
> playbook (`when: not defer_incomplete | default(false)`), and let each wrapper set `defer_incomplete: true` and end with one play that fails every host whose list is non-empty. Judge "finished" from
> an allow-list of outcomes, so a new failure kind is incomplete by default.

> **Learned 2026-11-19 (o)** · `ansible.builtin.git`, existing checkout, repo URL changed · VERIFIED_PRIMARY · Source: ansible-core `modules/git.py` lines 1381-1415 (the copy bundled
> with ansible-lint 26.10.1; the controller's own ansible-core was not checked) · Falsifier: a run with `update: no` that rewrites `remote.origin.url`
>
> When `dest` already holds a checkout, `update: no` returns at once (the `elif not update:` branch): no fetch, and the remote URL is not rewritten, so a moved Git host breaks nothing until something
> fetches there. With updating on (the default) the module calls `set_remote_url` first, so changing `repo:` repoints the checkout to the new address. A task that wipes `dest` and clones again always
> gets the new URL, but also resets everything git does not track (here directories that needed chmod 777 afterwards).
>
> ```python
> # ansible-core lib/ansible/modules/git.py (abridged)
> elif not update:
>     # Just return having found a repo already in the dest path
>     result['before'] = get_version(module, git_path, dest)
>     module.exit_json(**result)
> else:
>     ...
>     remote_url_changed = set_remote_url(git_path, module, repo, dest, remote)
> ```

> **Learned 2026-11-20** · ansible --check · VERIFIED_PRIMARY · Source: test playbooks on ansible-core 2.18.8 and 2.21.6 (smc-resiliency session, ansible-wifi branches local/bases-check-mode ef0c9230 and local/rise-check-mode 960300a4) · Falsifier: a skipped command task under --check whose registered result has no `rc`
> Under `--check`, a skipped `command`/`shell` task still registers a result with `rc: 0` and `stdout: ""`, so `x.rc == 0` reads true and `x.rc | default(1)`
> never applies. On a skipped result `until` IS evaluated while `changed_when` and `failed_when` are not. A wait loop on a skipped probe therefore runs its full
> retries under `--check` and fails: end it with `ansible_check_mode` directly. Mark only read-only probes `check_mode: false`; guard writers' consumers with
> `not ansible_check_mode`. A handler or task with `check_mode: no` that reboots runs for real under `--check` (`ansible_check_mode` stays true inside it, so
> `when: not ansible_check_mode` stops it).
>
> ```yaml
> # roles/smc_dns_mgmt/tasks/main.yml (ansible-wifi local/bases-check-mode ef0c9230)
> - name: Wait for port 53 to be released
>   ansible.builtin.shell: ss -lunp | grep -q ':53 '
>   register: ss
>   until: ansible_check_mode or ss.rc == 1   # was: ss.rc | default(1) == 1 (never defaulted: skipped => rc 0)
> ```

> **Learned 2026-11-20** · ansible-core 2.18 templating · VERIFIED_PRIMARY · Source: reproduced on 2.18.8 and 2.21.6 (local-knowledge-ansible roles/smc_change, commit 45055e7; smc-resiliency session) · Falsifier: on 2.18, `big_var.subkey | default([])` loading the subkey while another key of big_var is undefined
> On 2.18 reading a variable templates it whole, so `spec.files | default([])` fails on any undefined reference elsewhere in `spec`, and `default()`
> swallows that error: the expression silently becomes `[]`. 2.19+ templates lazily and is not affected. To read one field of a templated dict on 2.18,
> read it from the source as written (`lookup('file', path) | from_yaml`), and render fields one by one in an action plugin when the error must name the field.

