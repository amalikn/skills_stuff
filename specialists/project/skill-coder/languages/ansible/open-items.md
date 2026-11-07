---
Title: ansible override - open items
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The open items part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: open items

Part of [ansible.md](../ansible.md).

- Pinned ansible-lint profile recommendation and Molecule driver choice: UNVERIFIED stubs.

> Design patterns realised in Ansible (resumable journal, done ledger, partition before batch, plug-in probe, plan then apply) are in
> [../references/design-patterns.md](../references/design-patterns.md), table "Language realisations"; entries here record the Ansible behaviour they rely on.

>  **Learned 2026-11-05 (i)** · ansible-core 2.21.5, a gate as a run_once task · VERIFIED_PRIMARY (prod rct inventory, check mode, two and three hosts:
>  recap `failed=1` on the first host, `ok=1 failed=0` on the other, no later play) · Source: local-knowledge-ansible
>  `ansible-wifi/roles/smc_change/tasks/tsh_login.yml`, `playbooks/smc_change.yml` first play (uncommitted 2026-11-05) · Falsifier: a recap in which
>  every host of the play shows failed=1 after one run_once assert fails
>  A `run_once` assert that fails marks only the first host failed; the other hosts stay `ok`. A run-wide gate therefore needs `any_errors_fatal: true`
>  on its play, so the failure ends the run instead of leaving later plays to the other hosts.
>
>  ```yaml
>  - name: Check the Teleport logins this run needs
>    hosts: smc_bases
>    gather_facts: false
>    any_errors_fatal: true            # the run_once failure inside ends the whole run
>    tasks:
>      - name: Check the Teleport logins this run needs
>        ansible.builtin.include_role: {name: smc_change, tasks_from: tsh_login.yml}   # run_once command + assert
>  ```

>  **Learned 2026-11-05 (ii)** · ansible-core 2.21.5, `strategy: free` with `serial` · VERIFIED_PRIMARY (four local dummy hosts, serial 2, and a
>  check-mode run on two production hosts) · Source: local-knowledge-ansible plans/smc-change-free-timeouts-20261105 · Falsifier: under free, a
>  failed host with `max_fail_percentage: 0` stops the next batch, or `pause` runs per host
>  Under `free`, Ansible warns that `run_once` and `any_errors_fatal` are not supported, and it refuses `ansible.builtin.pause` outright ("bypasses
>  the host loop"). It also ignores `max_fail_percentage`: with one failed host, linear stopped the run but free started the next batch. Before
>  switching a play to free, grep its tasks for `pause`, `run_once`, `any_errors_fatal` and cross-host reads. Use `ansible.builtin.wait_for:
>  {timeout: N}` delegated to localhost for a wait, and rebuild any first-failure stop as a gate that reads the run's own results before each host
>  starts. Also: YAML 1.1 reads an unquoted `20261105_120000` as the integer 20261105120000 (underscores are digit separators), so quote stamps.
>  ```yaml
>  - name: Let client traffic reach the changed box   # was ansible.builtin.pause, refused under strategy free
>    ansible.builtin.wait_for: {timeout: "{{ soak_left | int }}"}
>    delegate_to: localhost
>  ```

Three traps met building a resumable fetch playbook:

1. **`find` with `depth:` still reads every depth-N directory.** The walk lists a directory before the depth test runs, and prunes (`del dirs[:]`) only once it is inside one, so the contents of
   every depth-N directory are read and their entries type-checked. On a network filesystem (NFS/EFS) that is a round trip per entry: minutes, with the module in state `D`. To list directories at a
   fixed depth, use GNU find, which never opens them:
   ```python
   # ansible/modules/find.py (ansible-core 2.21.5), the walk loop
   for root, dirs, files in os.walk(npath, ..., topdown=True):
       for fsobj in (files + dirs):
           ...
           if depth > params['depth']:
               del dirs[:]      # pruned only after this directory was already listed
               continue
   ```
   ```yaml
   # ansible-malik smc_get_pcapv8.yml (2026-11-05): ~1.6 s instead of minutes on EFS
   - shell: find {{ root | quote }} -mindepth 2 -maxdepth 2 -type d \( -name {{ m | quote }} -o -name '{{ m }}[0-9][0-9]' \) -print
     register: scan
     changed_when: false
   ```
2. **`async:` is the job's hard limit; `retries × delay` on `async_status` only sets how long it is polled.** With `async: 7200` and `retries: 300, delay: 60`, Ansible killed the job at 7,200 s
   (`Timeout exceeded`); the 5 h of polling never applied. Size `async` from the work (bytes ÷ measured rate, plus margin) and derive `retries` from it: `retries: "{{ (async_s | int // 60) + 5 }}"`.
3. **Extra vars beat `set_fact`, so a test that passes a fact with `-e` skips the logic that sets it.** The first mock test passed `zipped_files_dir` as an extra var and stayed green while the task
   choosing it was never exercised. Pass the inputs of the logic under test, never its outputs.

>  **Learned 2026-11-05 (iii)** · ansible-core 2.21.5, one role imported twice with `import_playbook` in one run · VERIFIED_PRIMARY (dummy hosts;
>  a production run where the second change skipped a host as done, citing the first change's record) · Source: local-knowledge-ansible
>  plans/smc-change-free-timeouts-20261105 · Falsifier: a `set_fact` from the first import is undefined in the second
>  Host facts (`set_fact`, registered results) and `group_by` groups outlive an `import_playbook`. A role that sets a flag only when it holds, and
>  tests it with `is defined`, inherits the first run's value in the second; a host also stays in a group the first run put it in. Ansible
>  cannot unset a fact or remove a host from a group, and `meta: clear_facts` leaves `set_fact` values (tested). So reset each per-run flag at
>  the run's start to a value its readers treat as "not set" (`''` or `{}` tested by length, `~` by `is none`), and name groups per run
>  (`todo_{{ change }}`): a play's `hosts:` can be templated from `import_playbook` vars (tested).
