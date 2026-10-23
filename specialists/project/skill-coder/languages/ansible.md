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

> **Learned 2026-10-23** · ansible-core 2.21.5 · VERIFIED-OBSERVED (three Ubuntu 22.04 hosts over Teleport; `ps -eo args` against the probe's counts) ·
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

> **Learned 2026-10-23 (c)** · ansible-core 2.21.5, ansible-lint production profile · VERIFIED-OBSERVED (role runs on stage hosts; ansible-lint pass) ·
> Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/main.yml`, `record.yml`, `actions/command.yml` · Falsifier: a failed run that
> leaves no record
> To record every run of a role, failed ones included: wrap the role body in `block`/`rescue`; the rescue keeps `ansible_failed_task.name` and
> `ansible_failed_result.msg` in a fact, writes the record (`delegate_to: localhost`, `check_mode: false`, so check runs are recorded too) and fails
> again. A command that really needs a shell (an operator-supplied string with pipes) runs as `ansible.builtin.command: argv: [/bin/sh, -c, ...]`,
> which states the shell and passes ansible-lint `command-instead-of-shell` without a suppression.
