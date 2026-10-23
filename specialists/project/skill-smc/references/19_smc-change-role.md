---
Title: smc_change role - making any change to SMCs with before/after proof
Category: reference
Status: current
Authority: local-supplement
Scope: >-
  roles/smc_change and smc_change.yml (source local-knowledge-ansible/ansible-wifi, symlinked into the ansible-wifi checkout); usable from any
  project that changes SMC boxes
Last reviewed: 2026-10-23
Summary: >-
  How to run smc_change, write a change spec, read its stages, gates and run records, how it persists a change on overlayroot Pis, what it
  leaves on a box (nothing, after a success), how to roll back, how to extend it, and what is proven so far.
---

# smc_change role

## Contents

- [When to use it](#when-to-use-it)
- [Where it is](#where-it-is)
- [Running it](#running-it)
- [Stages and output](#stages-and-output)
- [Writing a change spec](#writing-a-change-spec)
- [What it checks](#what-it-checks)
- [Overlayroot persistence](#overlayroot-persistence)
- [Nothing left on the box, run records, rollback](#nothing-left-on-the-box-run-records-rollback)
- [Already done, and force](#already-done-and-force)
- [Extending it](#extending-it)
- [Status and open items](#status-and-open-items)
- [Pitfalls it already handles](#pitfalls-it-already-handles)

## When to use it

Any change to SMC boxes that must be proven harmless: a package to a fixed version, a config file from a template, an ini option, a scripted step. Built for the PHP CVE-2026-109618 rollout
(2026-10-23, operator: "not limited to just this kind of change"). A project outside ansible-wifi that needs to change SMCs adds a spec rather than writing its own playbook.

## Where it is

| Path                                                                                   | Seen in the ansible-wifi checkout as |
| -------------------------------------------------------------------------------------- | ------------------------------------ |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/roles/smc_change/`        | `roles/smc_change` (symlink)         |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/playbooks/smc_change.yml` | `smc_change.yml` (symlink)           |
| `.../ansible-wifi-root-governance/ruff.toml`                                           | `ruff.toml` (symlink)                |

All listed in the checkout's `.git/info/exclude`, so none reaches Bitbucket. The role's `README.md` is the full manual and the header of `smc_change.yml` explains every `-e` option. Wiring and the
rest of that folder: `18_local-knowledge-ansible.md`.

## Running it

```bash
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec>                        # check: read only
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec> -e smc_change_mode=apply
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec> -e smc_change_mode=verify
```

Main options: `smc_change_serial` (default 1), `smc_change_on_refusal` (`skip` default: a refused host is recorded and skipped), `smc_change_rollback` (`repack` default), `smc_change_soak_minutes`
(5), `smc_change_reboot` (true), `smc_change_allow_unhealthy_baseline`, `smc_change_allow_nbn_wh`, `smc_change_report_dir` (default `roles/smc_change/runs`). An unreachable host is recorded and
skipped, so one offline box does not stop a fleet run (side-agent review, 2026-10-23); a host that fails after its change started stops the run.

Rollout pattern (operator, depth before breadth): one stage box in `check`, then `apply`; one prod box per flavor; then the flavor with `-e smc_change_serial=5`, run by the operator from the
handed-over command.

## Stages and output

Eleven stages, each printed as `STAGE n/11 NAME - what it does now` (operator, 2026-10-23: show where the play is): 1 SPEC, 2 SCOPE, 3 PROBE, 4 GUARD, 5 BACKUP, 6 ACTIONS, 7 RESTART, 8 REBOOT, 9
VERIFY, 10 CLEANUP, 11 RECORD. check runs 1-4 and 11; verify 1-4, 9 and 11; apply all. The output has **Change requested** (stage 1), **Planned on this host** (stage 4, e.g. `1. apt_pin: php8.1-common
8.1.2-1ubuntu2.18 -> 8.1.2-1ubuntu2.28`), a HOST/HEALTH/CHECK summary, a **RESULT** block (`PASSED: all 10 gates hold (...)` plus one `CHECK` line per check), and a final play listing every host of
the run with its result (`passed`, `gates_failed`, `failed`, `refused`, `unreachable`, `probed`).

## Writing a change spec

`files/changes/<name>.yml`, `name` equal to the file name; templates in `templates/<name>/`, copied files in `files/<name>/`. A check runs only when the spec lists it. The PHP spec, abridged (source:
`roles/smc_change/files/changes/php-cve-2026-109618.yml`, uncommitted at writing):

```yaml
name: php-cve-2026-109618
applies_to: {flavors: [rcp, nbn_accelerate, rct, wh, nbn_wh], arch: [x86_64, aarch64]}
actions:
  - {type: apt_pin, packages: ['php8.1*', 'libapache2-mod-php8.1'], version: 8.1.2-1ubuntu2.28}
backup: {paths: [/etc/php, /etc/apache2], repack: true}
restart:
  services: [apache2]
  processes:
    - {pattern: 'php Start.php', respawn: cron}   # apn-mqtt-client
    - {pattern: 'php -S ', respawn: cron}         # rct-tstik on 10.254.0.1:8080
reboot: overlay_only
verify:
  services_active: [apache2]
  commands: [{cmd: apache2ctl configtest}, {cmd: apache2ctl -M, expect_text: php_module}]
  same_as_before: ['php -m']
  stale_maps: [php]
  http: [{name: portal, fqdn_var: smc_bases_portal_fqdn, protocol_var: smc_bases_portal_protocol, same_status: true,
          bad_markers: [must be writable, Undefined variable, Fatal error, Kohana_Exception, '<?php']}]
  logs: [{path: /var/log/apache2/error.log, fail_on: 'PHP (Fatal|Parse) error|Segmentation fault'}]
  report_only: [{path: /var/log/apache2/access.log, count: {5xx: '" 5\d\d ', pin_activations: 'wifi/access/\d+ HTTP/[\d.]+" 302 '}}]
```

Action types: `apt_pin` (packages, version), `template` and `copy` (src, dest, owner, group, mode), `ini` (path, section, option, value), `command` (cmd, check, chroot; on an overlay box `chroot` is
required). Other specs: `php-ini-upload-progress-off` (an `ini` action).

## What it checks

Only checks the spec configures produce a gate: `overlay` (always), `services`, `commands`, `same_as_before`, `http`, `http_same_status`, `packages`, `files`, `persisted` (overlay boxes), `stale` (no
process maps a deleted file matching `stale_maps`), `logs`, `processes` (each cron-respawned process that ran before runs again). Before an apply, the configured `services`, `commands` and `http` must
hold, else the host is refused. HTTP endpoints are fetched by their real ServerName with `curl --resolve` to the address `apache2ctl -S` binds (rct hosts have no `topology_interfaces`; a `localhost`
probe hits the default vhost, `10_captive-portal.md` 11.8).

## Overlayroot persistence

The lower dir `/media/root-ro` is remounted rw for the write phase and always back to ro. File actions write to both paths; `apt_pin` installs live, then `dpkg -i` of the same .debs in a chroot of the
lower dir with `policy-rc.d` returning 101, and refuses to go on unless the lower dir's dpkg database shows the version, so a box is never rebooted onto the old build. Then one reboot (operator choice
over the two- reboot disable/enable-overlay path). `UNVERIFIED` until the warehouse-rct01 canary. Core (source `roles/smc_change/tasks/actions/apt_pin.yml`):

```yaml
- name: Install the .debs inside the chroot
  ansible.builtin.shell:
    cmd: >-
      chroot {{ smc_change_lower_dir }} /bin/sh -c 'DEBIAN_FRONTEND=noninteractive
      dpkg --force-confdef --force-confold -i {{ smc_change_stage_dir }}/*.deb'
```

## Nothing left on the box, run records, rollback

Operator, 2026-10-23: nothing may be left on an SMC after a successful change. The role writes nothing on the box except the change and, during the run, its backup. Stage 10 (successful apply only)
copies the backup to `runs/<spec>/backups/<host>-<start>/` on the controller, removes it from the box (lower dir included), removes the .debs apt downloaded and dpkg-repack if the run installed it,
and fails if anything it listed is left. A failed run keeps its backup on the box. Every run writes `runs/<spec>/<host>-<spec>-<mode>-<start>.json` on the controller only: result, stage and task of a
failure, refusal or unreachable reason, gates, plan, backup path, both probes.

Rollback is a mode: `-e smc_change_mode=rollback` (operator, 2026-10-23). It finds the newest backup of the change for the host (controller
`runs/<spec>/backups/<host>-*` first, else one a failed apply left on the box; `-e smc_change_rollback_from=<host>-<start>` picks one),
stages it, and undoes the actions last first through `tasks/actions/<type>_rollback.yml`: `apt_pin` reinstalls the saved .debs with
`dpkg -i` (live, and in a lower-dir chroot on overlay boxes), `template`/`copy`/`ini` restore the file from `paths.tgz`, `command` runs the
spec's `undo`. It restarts, reboots per the spec, and is judged on health plus `restored`. Allowed on an unhealthy box. Check-mode run on
nocprov-smc01 found the box backup of the operator's apply and its six `.18` builds; a real rollback has not run (it would reinstate the
vulnerable build).

## Already done, and force

Each passed apply or rollback is stored per host in `runs/<spec>/state/<host>.json` on the controller (operator, 2026-10-23: a rerun must
skip the SMCs already done). The next apply skips such a host as `already_done`, records it and goes on with the rest; `-e
smc_change_force=true` re-runs them (tested in check mode on nocprov-smc01 with a stored state: skipped, then not skipped with force).

## Extending it

The role's tasks name no action or check type (operator, 2026-10-23: generic). Type knowledge lives in two places: `tasks/actions/<type>.yml` (how to make a change; register anything to remove in
`smc_change_cleanup_paths`/`_globs`/`_packages`) and `files/probe/NN_<check>.py`, one file per check type that calls `register(Check(...))` with `collect`, `healthy`, `gates`, `persisted`, `describe`
and, for an action type, `plan`. `tasks/probe.yml` joins the parts in name order and pipes them to `python3 -`, so nothing is written to the box. Python is two-space indented and checked with ruff
(`files/probe/check.sh`: lint on the joined program, format per part) against the project-root `ruff.toml`, which excludes the 22 existing four-space files with `force-exclude` (operator: new files
only).

```python
# roles/smc_change/files/probe/99_main.py (2026-10-23)
for check in CHECKS:
  check.call("collect", cfg, out, base)
...
gates = {"overlay": out["overlay"] == base["overlay"]}
for check in CHECKS:
  gates.update(check.call("gates", cfg, out, base, default={}))
```

The split was proven behaviour-neutral: four runs (check and verify on warehouse-smc01 and nocprov-smc01) gave identical records before and after, timestamps and live traffic counts aside.

## Status and open items

As of 2026-10-23:

- nocprov-smc01 (x86 stage bench box): `apply` by the operator moved php8.1 .18 to .28, all gates passed (before the cleanup stage existed, so its backup, 7 host-side records, dpkg-repack and 7 cached
  .debs are still on it).
- warehouse-smc01: packages at .28 by unattended-upgrades, apache still on the deleted old libphp (`verify` fails `stale`).
- Pi canary warehouse-rct01 off Teleport since about 13:45 (backdoor up); the overlay path is `UNVERIFIED`.
- Not yet run: an `apply` with the cleanup stage (the agent's apply was refused by the auto-mode classifier; operator to run it).
- `playbooks/smc_update_php.yml` stays until the role's overlay apply path is proven.

## Pitfalls it already handles

- Installed version is not running code: the `stale` gate reads `/proc/*/maps` (13_known-issues, Learned 2026-10-23).
- Ansible `environment:` values sit on the remote command line, so `pgrep -f` matched the probe's own shell; the probe leaves its ancestor chain out (13_known-issues, Learned 2026-10-23 (b)).
- A skipped task re-registers its variable; chroot open/close share a fact instead (skill-coder `languages/ansible.md`).
- A YAML folded scalar passes `'\n'` to Jinja as a literal backslash-n; the probe join uses a newline variable from a double-quoted string.
- A `-l` limit also filters a `hosts: localhost` play; the run stamp and summary run on the managed group, delegated to localhost.
- ruff honours `.git/info/exclude` through the checkout's symlink and then finds no files; `check.sh` works from the physical path.
- A `command` action on an overlay box must set `chroot`, or the role's own reboot undoes it unseen (side-agent review).
