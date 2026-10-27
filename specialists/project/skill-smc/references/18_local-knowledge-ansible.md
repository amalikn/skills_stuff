---
Title: Local-knowledge folder for ansible-wifi
Category: reference
Status: current
Authority: local-supplement
Scope: /Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi and how it is wired into the ansible-wifi checkout
Last reviewed: 2026-10-23
Summary: >-
  What lives in the local-only ansible-wifi knowledge folder, how its playbooks, roles and governance files appear in the ansible-wifi repo without
  reaching Bitbucket, what operator tooling is built there (smc_change role), and the standing rule to read it at the start of SMC work.
---

# Local-knowledge folder for ansible-wifi

## Contents

- [Standing rule](#standing-rule)
- [Layout](#layout)
- [How it is wired into ansible-wifi](#how-it-is-wired-into-ansible-wifi)
- [Operator tooling built here](#operator-tooling-built-here)
- [Learned](#learned)

## Standing rule

`/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` is where ansible-wifi work that must not reach the Bitbucket repo is done and kept: governance, investigations, evidence, plans and
local-only operator playbooks and roles (operator, 2026-10-23). This pack must stay across it:

- At the start of SMC work, run `just local_knowledge_index` (or `scripts/ansible/local_knowledge_index.sh --days 3`) to see what is wired in and what changed lately, and read anything new under `playbooks/`,
  `roles/`, `evidence/` and `issues/` that bears on the task.
- When something new is built there (a playbook, a role, a change spec, a script, an evidence set), add it to [Operator tooling built here](#operator-tooling-built-here) or [Layout](#layout) in the same session, with its path and how to run
  it.
- Facts learned while working there still go to the matching `references/*.md` file; this file records the folder itself.

## Layout

| Folder                           | Holds                                                                                                       |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `ansible-wifi-root-governance/`  | the repo's governance files (AGENTS.md, CLAUDE.md, CHANGELOG.md, SCRATCHPAD.md, ROADMAP.md, .archcore, ...) |
| `evidence/`                      | dated evidence sets, e.g. `php-cve-2026-109618-20261022_1128/` (assessment, CSV, raw probes)                |
| `issues/`                        | per-fleet investigation folders (`rct-fleet`, `wh-fleet`, `apn`, `rcp-fleet`, ...)                          |
| `plans/`                         | design plans (`<slug>-YYYYMMDD_hhmm.md`)                                                                    |
| `playbooks/`                     | local-only operator playbooks, symlinked into the repo root                                                 |
| `roles/`                         | local-only roles, symlinked into `roles/` of the repo                                                       |
| `scripts/`                       | ansible-lint baseline and delta-gate scripts (promoted copies live in this pack's `scripts/`)               |
| `opa/`, `snapshots/`, `history/` | OPA policies and tests, state snapshots, archived history                                                   |
| `graphify-out/`, `ai-tooling/`   | generated knowledge graph; AI tooling notes                                                                 |

The folder is part of the `local-knowledge-ansible` git repository (remote on GitHub, private), not the ansible-wifi one.

## How it is wired into ansible-wifi

Every file the repo should see but not commit is an absolute symlink from the ansible-wifi checkout into this folder, and its repo-relative path is listed in the checkout's `.git/info/exclude` (not
`.gitignore`, which is committed). `git status --ignored` shows them as `!!`. To add one:

```bash
ln -s /Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/playbooks/<name>.yml /Volumes/Data/_ansible/ansible-wifi/<name>.yml
printf '<name>.yml\n' >> /Volumes/Data/_ansible/ansible-wifi/.git/info/exclude
git -C /Volumes/Data/_ansible/ansible-wifi check-ignore -v <name>.yml     # must name .git/info/exclude
```

One linter per language at the checkout root, each config a symlink into `ansible-wifi-root-governance/` and git-excluded the same way
(operator, 2026-10-23: two-space indent, new files only, existing files listed as excluded): `ruff.toml` (Python; 22 files
`force-exclude`d), `djlint.toml` (Jinja2, lint only, HTML rules ignored; 123 templates excluded), `.taplo.toml` (TOML), `biome.jsonc`
(JSON, biome 2.5.15 via npx; 18 files excluded), `.editorconfig` + `.shellcheckrc` (shell: shfmt honours the editorconfig `ignore = true`
list of the 24 existing scripts, shellcheck checks what shfmt lists). `./lint_new.sh` at the root runs them all plus an `ansible-inventory`
parse of every inventory (about 8 s); a negative test with one bad file per language failed every step. Tools that skip a git-excluded or
symlinked tree (ruff, shfmt, djlint) get the physical path of the local-only roles; `.editorconfig` is also linked into
`local-knowledge-ansible/ansible-wifi/` so shfmt finds it from there. A symlinked role resolves because `ansible.cfg` sets `roles_path = ./roles`. Keep a symlinked playbook self-contained or role-based: do not rely on paths relative to the playbook file.

## Operator tooling built here

| Item                                             | What it is                                                        | Run                                                                           |
| ------------------------------------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `roles/smc_change/` + `playbooks/smc_change.yml` | generic change role: one spec per change in                       | `ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <h>`        |
|                                                  |   `files/changes/<name>.yml`; before-probe, guard, backup,        |   `-e smc_change=<spec> [-e smc_change_mode=apply]`; default mode `check`     |
|                                                  |   actions (apt_pin, template, copy, ini, command) live and in the |   (read only)                                                                 |
|                                                  |   overlayroot lower dir, restart, reboot, after-probe and gates.  |                                                                               |
|                                                  |   Every run's JSON record lands in                                |                                                                               |
|                                                  |   `roles/smc_change/runs/<spec>/`. README in the role; skill-smc guide: `19_smc-change-role.md`.            |                                                                               |
| spec `php-cve-2026-109618`                       | php8.1 to 8.1.2-1ubuntu2.28 on rcp, nbn_accelerate, rct, wh (nbn_wh | as above                                                                      |
|                                                  |   only when allowed)                                              |                                                                               |
| spec `php-ini-upload-progress-off`               | interim php.ini mitigation (assessment 5.1)                       | as above                                                                      |
| `playbooks/smc_update_php.yml`                   | the single-file predecessor of the PHP spec; keep until the       | `ansible-playbook ... smc_update_php.yml -l <h> -e smc_php_mode=check`        |
|                                                  |   role's apply path is proven, then retire                        |                                                                               |

State on 2026-10-23: the role's `check` and `verify` modes ran on warehouse-smc01, nocprov-smc01 (x86) and warehouse-rct01 (Pi, overlay off). `apply` has not run anywhere; the overlay lower-dir chroot
path is `UNVERIFIED` until a canary on warehouse-rct01 with its overlay enabled.

## Learned

> **Learned 2026-10-23** · local-knowledge wiring · VERIFIED-OBSERVED (`git check-ignore -v`, `scripts/ansible/local_knowledge_index.sh`) · Source: ansible-wifi
> `.git/info/exclude` lines 77-79; local-knowledge-ansible `ansible-wifi/roles/smc_change/` (uncommitted at writing) · Falsifier: a symlink into this folder that `git status` lists as untracked 31
> paths in the ansible-wifi checkout are symlinks into this folder, all ignored through `.git/info/exclude`; a new local playbook or role follows the same pattern (the role's runs/ records stay in the
> knowledge repository). No visual surface.

> **Learned 2026-10-26** · VERIFIED_PRIMARY · local-only `roles/smc_change` now contains controller journals, explicit safe resume,
> read-only assess and phase timing; `justfile` catalogs four recovery fixtures. Source: role README and `references/19_smc-change-role.md`,
> Interrupted-change recovery section. No new diagnostic script was added to this pack; the helpers are runtime implementation owned by the role.
