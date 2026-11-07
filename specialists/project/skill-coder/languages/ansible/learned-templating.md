---
Title: ansible override - learned templating
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned templating part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned templating

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-20** · ansible-core 2.21.5 · VERIFIED_PRIMARY · Source: smc-resiliency spike/render_site.sh and spike/render/tasks (apn e764a3e) against ansible-wifi f3a5dca8 · Falsifier: a template that renders identically without its task's options
> To render a role's template outside the role (to build a config image, a diff, a preview), copy what the real task and play pass, not just the
> `src`: the task's options (`lstrip_blocks: yes` here: without it the netplan file came out unparseable), the role vars the playbook sets (the role
> defaults were null placeholders), and the defaults at role precedence (a throwaway role linking the real `defaults/main.yml`; `include_vars` would
> outrank the inventory). Prove it against a file the real role wrote on a live host.

> **Learned 2026-10-23 (b)** · ansible-core 2.21.5 · VERIFIED_PRIMARY · Source: docs.ansible.com playbook_guide/playbooks_variables.html, "Registering variables" ("If a task fails or is skipped, Ansible still registers a variable with a failure or skipped status", read 2026-10-23); local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/chroot.yml` · Falsifier: a skipped task that
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

> **Learned 2026-10-23 (d)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (smc_change runs, stage hosts) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/probe.yml`, `playbooks/smc_change.yml` (uncommitted at writing) · Falsifier: a `-l host` run that still
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

> **Learned 2026-10-23 (f)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (smc_change role, ansible-lint production profile) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/` · Falsifier: a templated free-form include_tasks that passes syntax-check
> (1) `include_tasks: "{{ 'a.yml' if x else 'b.yml' }}"` fails syntax-check ("Invalid options"); write `include_tasks:` with `file: ...`.
> (2) In a folded scalar (`>-`) a more-indented continuation line keeps its newline, which shows as `\n` in output; keep continuations at
> the same indent or move the expression into a variable. (3) Read-only commands whose output a later task prints need `check_mode:
> false`, or a `--check` run reports empty values. (4) Lint for inventories: `ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED=true
> ansible-inventory -i <file> --list` fails on a source that does not parse; it reads only, so it can cover every inventory, existing ones
> included. (5) Per-host state a rerun must honour (done hosts skipped, a force flag to redo them) belongs on the controller (one file per
> host, written with `delegate_to: localhost`), not on the managed box.

> **Learned 2026-10-26 (f)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (local test: three local hosts, `serial: 3`, two `include_tasks`) · Source: local-knowledge-ansible `plans/smc-change-run-once-20261026_2220.patch` · Falsifier: a `run_once` task whose fact or register is
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

> **Learned 2026-10-27 (h)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (bug seen, fix tested with `ansible -m debug`) · Source: local-knowledge-ansible `roles/smc_change/tasks/pending.yml` (Teleport proxy) · Falsifier: `x | default('') is search('[.]t[.]')`
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

> **Learned 2026-10-30 (a)** · Jinja2 3 in ansible-core 2.21.5, filters and `+` · VERIFIED_PRIMARY (local render; an `apt_pin` names list deduplicated only its last term) · Source:
> local-knowledge-ansible `roles/smc_change/tasks/actions/apt_pin.yml` (`smc_change_pin_names`), commit cf4f994 · Falsifier: `{{ [1] + [1] | unique | list }}` rendering `[1]`
> A filter binds tighter than `+`, `~` and comparisons: `a + b | default([]) + c | unique | list` applies `unique | list` to `c` alone. Wrap each
> operand that takes a filter and the whole sum: `((a | list) + (b | default([])) + (c | default([]))) | unique | list`.

> **Learned 2026-10-30 (b)** · ansible-core 2.21.5, free-form `shell:` / `command:` · VERIFIED_PRIMARY (`--syntax-check`: "failed at splitting arguments, either an
> unbalanced jinja2 block or quotes" on a `shell: |` script copied from a spec) · Source: ansible-wifi `roles/smc_application/tasks/ubuntu-php-cve-2026-109618.yml`, commit fb6ae80b ·
> Falsifier: a free-form `shell: |` holding `'Class "?[^ ]+"? not found'` that passes `--syntax-check`
> The free-form form runs Ansible's `k=v` argument splitter over the script, which fails on a quote it cannot pair (a `"` inside `'...'` in a
> regex is enough). Pass scripts as `shell: {cmd: |, executable: /bin/bash}`: `cmd` is not split. Same for any script copied in from elsewhere.

> **Learned 2026-10-30 (c)** · ansible-core 2.21.5, `import_tasks` placement · VERIFIED_PRIMARY (`'import_tasks' is not a valid attribute for a Play`) · Source: ansible-wifi
> `smc_rise_deploy.yml`, commit fb6ae80b · Falsifier: a playbook with `- import_tasks: x.yml` at play level passing `--syntax-check`
> A playbook's top level takes plays and `import_playbook` only; `import_tasks` / `include_tasks` must sit in a play's `tasks:`. To run a task file
> between imported playbooks, wrap it in its own play (`hosts`, `gather_facts`, `tasks: [import_tasks ...]`); `when:` on that import still
> applies to every imported task, and host facts set by earlier plays (`set_fact`) are still there.

> **Learned 2026-10-30 (d)** · ansible-core 2.21.5, `set_fact` with `run_once` freezes host-variable templates · VERIFIED_PRIMARY (two local hosts,
> `hv=AAA`/`BBB`: the include_vars value rendered per host, the run_once set_fact gave `AAA` to both) · Source: local-knowledge-ansible
> `ansible-wifi/roles/smc_change/defaults/main.yml` `smc_change_actions`, commit 7ef59c7 · Falsifier: a run_once `set_fact` of a structure holding
> `{{ inventory_hostname }}` that renders per host afterwards
> Data loaded with `include_vars` stays a lazy template: each host renders its own variables on use. A `set_fact` renders at set time, and
> with `run_once` that is the first host's render, copied to every host. To derive data from per-host templates once per run, make it a
> variable whose value is a lookup, e.g. `x: "{{ lookup('ansible.builtin.template', role_path ~ '/templates/x.j2') | from_json }}"` in
> `defaults/`: it renders per host on each use (put the logic in `templates/` so a code fingerprint covers it). Outside a role task `role_path`
> is unset, and `include_role` keeps role defaults private unless `public: true`.

> **Learned 2026-10-30 (e)** · ansible-core 2.21.5 templating quirks in Jinja blocks · VERIFIED_PRIMARY (local runs of tasks/conditions.yml and
> load_spec.yml) · Source: local-knowledge-ansible commit 7ef59c7 · Falsifier: an empty `{% macro %}` call that yields `''`; `when:` accepting a dict
> - A macro whose output is empty returns **None**, not `''`: `m(x).split('|')` raises. Collect results with `namespace(list=[])` in a loop.
> - `when:` needs a real boolean: `when: a | default({}) or b` fails ("derived from value of type 'dict'"); write `(a | default({}) | length > 0)`.
> - There is no `length` test: `reject('length')` fails; use `map('length') | select('equalto', 0)`.
> - `set_fact` from a `{% %}` block: build JSON text (`{{ out | to_json }}`) and `| from_json` it, so the structure survives as data.

> **Learned 2026-11-01** · Ansible and tooling traps from a role refactor · VERIFIED_PRIMARY (ansible-wifi roles/smc_change test runs, ansible-core 2.21.5) · Source: ansible-wifi `roles/smc_change/tasks/conditions.yml`, `tasks/stage.yml`,
> `files/tests/test_action_report.yml` (local-knowledge-ansible, 2026-11-01) · Falsifier: an int-keyed dict surviving `to_json | from_json`
> - A dict built in Jinja and passed through `to_json | from_json` has string keys. `commits.update({i: x})` then `.get(i)` never matches: key on strings, read with `.get(i | string)`.
> - `loop.index0` under `{% for a in list if cond %}` counts the filtered items, not the list. Filter inside the loop body when the index must match the list.
> - A `>-` scalar keeps the newline around a more-indented line, so a Jinja continuation line prints a literal `\n`. Normalise once where the text is printed.
> - An unquoted task name with `: ` after a Jinja expression is a YAML parse error (ansible-playbook exit 4). Use ` - `.
> - A script editing a CRLF file must read and write with `newline=''`: a plain `open()` rewrites every line. A diff of hundreds of lines for a small edit is that.
> - Never probe a tool with `--help` on a production box unless its help is confirmed: `flash-kernel --help` took the flag as a kernel version and started installing.
>
> ```yaml
> # roles/smc_change/tasks/conditions.yml: string keys, because the dict crosses JSON
> {%- if r.value -%}{%- set _ = commits.update({name[8:]: r.value}) -%}{%- endif -%}
> {%- set now = (c.commits | default({})).get(i | string, '') -%}
> ```

> **Learned 2026-11-06 (k)** · ansible-lint 26.10.1 (ansible-core 2.21.5) production profile, PyYAML 6.0.3 · VERIFIED_PRIMARY (generated task files went from 51 findings
> to 0) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/files/export_tasks.py` `tidy_name`, `join_templates` (7056782) · Falsifier:
> a name with one template at its end flagged by `name[template]`, or `{{ (a) ~ (b) }}` rendering differently from `{{ a }}{{ b }}`.
> Generating task YAML for ansible-lint: `name[template]` wants at most one template, at the end, so move a name's templates to its end as one
> expression (`text - {{ (x) ~ ' ' ~ (y) }}`) and capitalise it (`name[casing]`). PyYAML cannot fold a string with no spaces, so `{{ a }}{{ b }}` runs
> stay over the line limit: join them as `{{ (a) ~ (b) }}` (parentheses keep `if/else` and filters bound; same rendered text, tested under Jinja).
> Dump with a width (here 120), then `safe_load` the dump and compare with the data: a fold that changed a value refuses the write.
