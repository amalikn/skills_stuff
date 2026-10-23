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
  How to run smc_change, write a change spec, read its gates and run records, how it persists a change on overlayroot Pis, and what is proven so
  far. Use it for any package, config-file or command change to SMCs instead of an ad hoc playbook.
---

# smc_change role

## Contents

- [When to use it](#when-to-use-it)
- [Where it is](#where-it-is)
- [Running it](#running-it)
- [Writing a change spec](#writing-a-change-spec)
- [What it checks](#what-it-checks)
- [Overlayroot persistence](#overlayroot-persistence)
- [Run records](#run-records)
- [Status and open items](#status-and-open-items)
- [Pitfalls it already handles](#pitfalls-it-already-handles)

## When to use it

Any change to SMC boxes that must be proven harmless: a package to a fixed version, a config file from a template, an ini option, a scripted step. It probes the box before, refuses an unhealthy or
full box, backs up, applies the change live and (on Pis with overlayroot) in the lower dir, restarts what runs the changed code, reboots when the spec says, probes again and fails the host on any gate
that does not hold. Built for the PHP CVE-2026-109618 rollout (2026-10-23, operator: "not limited to just this kind of change"). A project outside ansible-wifi that needs to change SMCs should add a
spec here rather than write its own playbook.

## Where it is

| Path                                                                                   | Seen in the ansible-wifi checkout as |
| -------------------------------------------------------------------------------------- | ------------------------------------ |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/roles/smc_change/`        | `roles/smc_change` (symlink)         |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/playbooks/smc_change.yml` | `smc_change.yml` (symlink)           |

Both are listed in the checkout's `.git/info/exclude`, so they never reach Bitbucket; the source is in the local-knowledge-ansible repository (private GitHub). Wiring and the rest of that folder:
`18_local-knowledge-ansible.md`. The role's own `README.md` is the full manual.

## Running it

From the ansible-wifi root, one inventory per run (topology_vars load per inventory):

```bash
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec>                       # check: read only
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec> -e smc_change_mode=apply
ansible-playbook -i inventories/<flavor>/<env> smc_change.yml -l <host> -e smc_change=<spec> -e smc_change_mode=verify
```

| Variable                              | Default  | Meaning                                                                          |
| ------------------------------------- | -------- | -------------------------------------------------------------------------------- |
| `smc_change`                          | required | spec name in `files/changes/`                                                    |
| `smc_change_mode`                     | `check`  | `check` read only; `apply`; `verify` (probe twice, gates, no change)             |
| `smc_change_serial`                   | 1        | hosts per batch; `max_fail_percentage: 0` stops the run at the first failed host |
| `smc_change_rollback`                 | `repack` | `repack` saves the apt_pin packages as .deb first; `fix_forward` does not        |
| `smc_change_soak_minutes`             | 5        | wait after apply so client traffic reaches the box before the after-probe        |
| `smc_change_reboot`                   | true     | false never reboots, whatever the spec says                                      |
| `smc_change_allow_unhealthy_baseline` | false    | apply even when the before-probe is unhealthy                                    |
| `smc_change_allow_nbn_wh`             | false    | nbn_wh only on an explicit operator decision (ansible-wifi AGENTS.md)            |
| `smc_change_report_dir`               | `runs/`  | controller directory for run records                                             |

Rollout pattern (operator, depth before breadth): one stage box in `check`, then `apply`; one prod box per flavor; then the flavor with `-e smc_change_serial=5`, run by the operator from the
handed-over command.

## Writing a change spec

`files/changes/<name>.yml`, `name` equal to the file name. Templates in `templates/<name>/`, copied files in `files/<name>/`. A check runs only when the spec lists it. The PHP spec, abridged (source:
`roles/smc_change/files/changes/php-cve-2026-109618.yml`, local-knowledge-ansible, uncommitted at writing):

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
  report_only: [{path: /var/log/apache2/access.log, count: ['" 5\d\d ', 'wifi/access/\d+ HTTP/[\d.]+" 302 ']}]
```

| Action     | Fields                                                  | Overlay box                                                      |
| ---------- | ------------------------------------------------------- | ---------------------------------------------------------------- |
| `apt_pin`  | `packages` (dpkg globs; only installed ones), `version` | live apt, then `dpkg -i` of the same .debs in a lower-dir chroot |
| `template` | `src`, `dest`, `owner`, `group`, `mode`                 | rendered to the live path and the lower-dir path                 |
| `copy`     | `src`, `dest`, `owner`, `group`, `mode`                 | same                                                             |
| `ini`      | `path`, `section`, `option`, `value`                    | same (community.general.ini_file)                                |
| `command`  | `cmd`, `check` (exit 0 = already done), `chroot`        | with `chroot: true` also run in the lower-dir chroot             |

Other specs in place: `php-ini-upload-progress-off` (the interim php.ini mitigation, an `ini` action).

## What it checks

`files/probe.py` (read only, run as `python3 -` on the box) produces the before-probe and the after-probe, and judges them. Before an apply the `services`, `commands` and `http` checks must hold;
after, every gate must:

| Gate               | Holds when                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| `services`         | every `services_active` unit is active                                                         |
| `commands`         | each command exits 0 (or `expect_rc`) and prints `expect_text`                                 |
| `http`             | each endpoint answers a redirect, or 200 with HTML and no `bad_markers`                        |
| `http_same_status` | each `same_status` endpoint answers the code it answered before                                |
| `packages`         | apt_pin: same package set as before, all at the version                                        |
| `persisted`        | overlay boxes: the lower dir's dpkg database and file hashes hold what was written             |
| `files`            | written files still hash as written (after a reboot: as written to the lower dir)              |
| `overlay`          | overlayroot in the state it was in before                                                      |
| `stale`            | no process maps a deleted file matching `stale_maps` (everything restarted onto the new build) |
| `same_as_before`   | each listed command prints the same sorted output                                              |
| `logs`             | no line written since the before-probe matches `fail_on`                                       |
| `processes`        | each cron-respawned process that ran before runs again                                         |

HTTP endpoints are fetched by their real ServerName with `curl --resolve` to the address `apache2ctl -S` binds it to (rct hosts have no `topology_interfaces`; a `localhost` probe hits the default
vhost and looks healthy on a dead portal, `10_captive-portal.md` 11.8).

## Overlayroot persistence

On a box whose `/` is overlayroot the role remounts `/media/root-ro` read-write for the write phase and always remounts it read-only after. For `apt_pin` it installs live (fixed at once, held in
tmpfs), downloads the same .debs into the lower dir and installs them in a chroot of it with `/usr/sbin/policy-rc.d` returning 101, then refuses to continue unless the lower dir's dpkg database shows
the version, so a box is never rebooted onto the old build. Core of it (source `roles/smc_change/tasks/actions/apt_pin.yml`, uncommitted at writing):

```yaml
- name: Install the .debs inside the chroot
  ansible.builtin.shell:
    cmd: >-
      chroot {{ smc_change_lower_dir }} /bin/sh -c 'DEBIAN_FRONTEND=noninteractive
      dpkg --force-confdef --force-confold -i {{ smc_change_stage_dir }}/*.deb'
- name: Read the lower dir's versions
  ansible.builtin.command:
    cmd: >-
      dpkg-query --admindir={{ smc_change_lower_dir }}/var/lib/dpkg -W '-f=${Package}=${Version}\n'
      {{ smc_change_pin.pkgs.keys() | join(' ') }}
```

Chosen by the operator (2026-10-23) over the two-reboot path (`smc_disable_overlay.yml`, change, `smc_enable_overlay.yml`). `UNVERIFIED`: overlayfs leaves changes to a mounted lower dir undefined; the
reboot that follows clears that state. Backups go under the lower dir so they survive it. See `07_hardware-overlay.md` §8 for the overlay itself.

## Run records

Every run (check, apply, verify, failed) writes `roles/smc_change/runs/<spec>/<host>-<spec>-<mode>-<start>.json` on the controller: result (`probed`, `passed`, `gates_failed`, `failed`), failure task
and message, gates, backup path, expected file hashes, the full before and after probes. Apply and verify runs also leave a copy in `/var/log/smc_change/` on the host (tmpfs on overlay boxes). The
role body runs in `block`/`rescue`, so a refusal or a crash is recorded too.

## Status and open items

As of 2026-10-23:

- `check` and `verify` ran on warehouse-smc01 and nocprov-smc01 (x86) and warehouse-rct01 (Pi, overlay off). `verify` on warehouse-smc01 failed `stale` correctly: apache still maps the deleted old
  `libphp8.1.so` after unattended-upgrades moved the packages to `.28` (13_known-issues).
- `apply` has not run anywhere. Next: `smc_enable_overlay.yml` on warehouse-rct01, then `apply` of `php-cve-2026-109618` there (operator choice of canary), reboot it once more by hand and `verify`.
- `playbooks/smc_update_php.yml` (single-file predecessor) stays until the role's apply path is proven.

## Pitfalls it already handles

- Installed version is not running code: the `stale` gate reads `/proc/*/maps` for deleted files (13_known-issues, Learned 2026-10-23).
- Ansible `environment:` values sit on the remote shell's command line, so `pgrep -f` matched the probe's own shell; the probe leaves its ancestor chain out of every count (13_known-issues, Learned
  2026-10-23 (b)).
- A skipped task re-registers its variable; decisions shared between the chroot open and close passes are kept in a fact (skill-coder `languages/ansible.md`, Learned 2026-10-23 (b)).
- Cron-started PHP processes (apn-mqtt-client, rct-tstik) are killed and waited on up to 7 minutes; a process with `respawn: none` is never killed.
