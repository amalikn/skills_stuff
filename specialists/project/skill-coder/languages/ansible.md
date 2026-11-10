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
- [Tools](#tools)
- [Core rule mapping](#core-rule-mapping)
- [Size and limit tweaks](#size-and-limit-tweaks)
- [Topic files](#topic-files)

## Authoritative sources

Ansible documentation (check mode and diff mode, tags, strategies and `serial`, error handling, handlers, Vault, logging and `no_log`, `become`, tips and tricks), ansible-lint documentation (rules
`fqcn` and `no-changed-when`, profiles), Molecule documentation. Copies: `../documents/research-sources-20261019/`. The operator's lessons: auto-memory
`feedback_trace_all_references_before_ansible_change` (2026-07-28).

For a data-driven engine built on a role (a spec language, the template as an interpreter, seams to Python and shell): [engine-composition.md](../references/engine-composition.md).

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

## Topic files

The rest of this override lives in [ansible/](ansible/) (split 2026-11-07 by scripts/language_split.py: one topic per file).

| File | Blocks |
| --- | --- |
| [before-any-change-trace-every-reference.md](ansible/before-any-change-trace-every-reference.md) | 4 |
| [learned-connections.md](ansible/learned-connections.md) | 3 |
| [learned-execution.md](ansible/learned-execution.md) | 5 |
| [learned-lint-and-tests.md](ansible/learned-lint-and-tests.md) | 3 |
| [learned-other.md](ansible/learned-other.md) | 1 |
| [learned-templating.md](ansible/learned-templating.md) | 14 |
| [learned-tooling.md](ansible/learned-tooling.md) | 2 |
| [open-items.md](ansible/open-items.md) | 7 |
