---
Title: ansible override - learned tooling
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned tooling part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned tooling

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-23 (e)** · task comments · USER_STATED (operator, 2026-10-23: "not for every task but the simple ones you can ignore but the ones which should have some description you can add") · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/` · Falsifier: the operator asks for a comment on every task, or for none
> A comment goes above a task only when it says something the name does not: why the task exists, a constraint, a non-obvious effect or
> failure mode. Simple tasks (a stage banner, a debug print, an include whose name says it all) carry none. Each task file starts with a
> header block: purpose, Called by, Reads, Sets, Notes.

> **Learned 2026-11-05 (j)** · ansible-core 2.18.8 (controller VM) and 2.21.5 (source read), `find` depth, `async`, extra vars · VERIFIED_PRIMARY (module source; observed on an EFS-backed store) · Source: `ansible/modules/find.py` lines 569-579 (2.21.5); ansible-malik `smc_get_pcapv8.yml` (2026-11-05) · Falsifier: a `find` with `depth: N` whose run time does not grow with the number of entries inside the depth-N directories

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
