---
Title: smc_change role - making any change to SMCs with before/after proof
Category: reference
Status: current
Authority: local-supplement
Scope: >-
  roles/smc_change and smc_change.yml (source local-knowledge-ansible/ansible-wifi, symlinked into the ansible-wifi checkout); usable from any
  project that changes SMC boxes
Last reviewed: 2026-10-26
Summary: >-
  How to run smc_change, write a change spec, read its stages, gates and run records, how it persists a change on overlayroot Pis, what it
  leaves on a box (nothing, after a success), how to roll back, how to extend it, and what is proven so far.
---

# smc_change role

## Contents

- [Interrupted-change recovery and production PHP review (2026-10-26)](#interrupted-change-recovery-and-production-php-review-2026-10-26)
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
(5), `smc_change_reboot` (true), `smc_change_allow_unhealthy_baseline`, `smc_change_allow_nbn_wh`, `smc_change_report_dir` (default `roles/smc_change/files/changes`), `smc_change_runs_dir` (default `<report_dir>/<change>/runs`). An unreachable host is recorded and
skipped, so one offline box does not stop a fleet run (side-agent review, 2026-10-23); a host that fails after its change started stops the run.

Rollout pattern (operator, depth before breadth): one stage box in `check`, then `apply`; one prod box per flavor; then the flavor with `-e smc_change_serial=5`, run by the operator from the
handed-over command.

## Stages and output

Eleven stages, each printed as `STAGE n/11 NAME - what it does now` (operator, 2026-10-23: show where the play is): 1 SPEC, 2 SCOPE, 3 PROBE, 4 GUARD, 5 BACKUP, 6 ACTIONS, 7 RESTART, 8 REBOOT, 9
VERIFY, 10 CLEANUP, 11 RECORD. check runs 1-4 and 11; verify 1-4, 9 and 11; apply all. The output has **Change requested** (stage 1), **Planned on this host** (stage 4, e.g. `1. apt_pin: php8.1-common
8.1.2-1ubuntu2.18 -> 8.1.2-1ubuntu2.28`), a HOST/HEALTH/CHECK summary, a **RESULT** block (`PASSED: all 10 gates hold (...)` plus one `CHECK` line per check), and a final play listing every host of
the run with its result (`passed`, `gates_failed`, `failed`, `refused`, `unreachable`, `probed`).

## Writing a change spec

`files/changes/<name>/<name>.yml` (one folder per change: the spec, its flow-map parts and its `runs/`; operator, 2026-10-26), `name` equal to the file name; templates in `templates/<name>/`, copied files in `files/<name>/`. A check runs only when the spec lists it. The PHP spec, abridged (source:
`roles/smc_change/files/changes/php-cve-2026-109618/php-cve-2026-109618.yml`):

```yaml
name: php-cve-2026-109618
applies_to: {flavors: [rcp, nbn_accelerate, rct, wh, nbn_wh], arch: [x86_64, aarch64]}
actions:
  - {type: apt_pin, packages: ['php8.1*', 'libapache2-mod-php8.1'], version: 8.1.2-1ubuntu2.28}
backup: {paths: [/etc/php, /etc/apache2], repack: true, shared: ['*.deb']}
restart:
  services: [apache2]
  processes:
    - {pattern: 'php Start.php', respawn: cron}   # apn-mqtt-client
    - {pattern: 'php -S ', respawn: cron, start_now: true}   # rct-tstik on 10.254.0.1:8080
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
copies the backup to `files/changes/<spec>/runs/<flavor>/backups/<host>-<start>/` on the controller, removes it from the box (lower dir included), removes the .debs apt downloaded and dpkg-repack if the run installed it,
and fails if anything it listed is left. A failed run keeps its backup on the box. Every run writes `files/changes/<spec>/runs/<flavor>/records/<host>-<spec>-<mode>-<start>.json` (standard layout since 2026-10-27, operator: one folder per flavor, the `-i` inventory folder, made on its first run; moved by
`local-knowledge-ansible/ansible-wifi/scripts/smc_change_runs_by_flavor.py`, which moved six active journals safely because `defaults/` is outside the
resume fingerprint; older trees kept them flat in `runs/` or `runs/records/`) on the controller only: result, stage and task of a
failure, refusal or unreachable reason, gates, plan, backup path, both probes.

Rollback is a mode: `-e smc_change_mode=rollback` (operator, 2026-10-23). It finds the newest backup of the change for the host (controller
`files/changes/<spec>/runs/<flavor>/backups/<host>-*` first, else one a failed apply left on the box; `-e smc_change_rollback_from=<host>-<start>` picks one),
stages it, and undoes the actions last first through `tasks/actions/<type>_rollback.yml`: `apt_pin` reinstalls the saved .debs with
`dpkg -i` (live, and in a lower-dir chroot on overlay boxes), `template`/`copy`/`ini` restore the file from `paths.tgz`, `command` runs the
spec's `undo`. It restarts, reboots per the spec, and is judged on health plus `restored`. Allowed on an unhealthy box. Check-mode run on
nocprov-smc01 found the box backup of the operator's apply and its six `.18` builds; a real rollback has not run (it would reinstate the
vulnerable build).

## Already done, and force

Each passed apply or rollback is stored per host in `files/changes/<spec>/runs/<flavor>/state/<host>.json` on the controller (operator, 2026-10-23: a rerun must
skip the SMCs already done). Since 2026-10-27 (operator: a done SMC is ignored, not verified again) the playbook's first play, `tasks/pending.yml`, reads that state and
the journal on the controller and runs the change play over `smc_change_todo` only: done SMCs get no ping, probe, serial slot or record
(apply, check and assess skip a passed apply; rollback a passed rollback; verify never). Before that, each skip still cost about 17 s and a
batch slot (`already_done` records of 20261027_081918). Proved controller-only: check on 20-mile and alpara ran in 2 s with no connection;
the split put arrkapa-smc01 (no state) in todo; `-e
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

> **Learned 2026-10-23** · overlay lower dir close and reboot policy · VERIFIED-OBSERVED (php-rct-smc01, first real overlay apply and rollback) ·
> Source: roles/smc_change/tasks/main.yml, tasks/persist_overlay.yml, tasks/reboot.yml (local-knowledge, uncommitted local-only role) · Falsifier: an
> overlay apply that replaces a file a running process maps and still remounts the lower dir ro before that process restarts
> The first overlay apply failed at stage 6: `mount -o remount,ro /media/root-ro` gave "mount point is busy". dpkg in the chroot had replaced
> `libphp8.1.so`, the PHP extensions and `/usr/bin/php8.1` in the lower dir while apache2 and cron's `php -S` still mapped the old inodes
> (`/proc/<pid>/maps` "(deleted)"); a filesystem with unlinked-but-open inodes refuses a read-only remount. Restarting apache2 and killing `php -S`
> (cron relaunches it) emptied the list and the remount worked. Fix: the lower dir now closes after stage 7 (restart), and only a failed backup or
> action closes it at once; a close that still fails names the holders. New spec policy `reboot: overlay_fallback` (operator, 2026-10-23: reboot only
> as the last resort): an overlay box reboots only when the lower dir stays read-write after the restarts, then the role checks it came back ro;
> otherwise the apt_pin chroot check of the lower dir's dpkg database is the persistence proof. The PHP spec uses it. Rollback then passed with no
> reboot (lower dir ro, `.18` live and lower). The kernel calls changes to a mounted overlay's lower layer undefined behaviour (VERIFIED_PRIMARY,
> docs.kernel.org/filesystems/overlayfs.html, "Changes to underlying filesystems"); the upper tmpfs copy masks it until the next reboot.
>
> ```yaml
> - name: Restart
>   ansible.builtin.include_tasks: restart.yml
> # The restarts above released the replaced files, so the lower dir can go read-only again.
> - name: Close the lower dir
>   ansible.builtin.include_tasks: persist_overlay.yml
>   vars:
>     smc_change_overlay_step: close
>     smc_change_overlay_tolerate: "{{ smc_change_spec.reboot | default('never') == 'overlay_fallback' and smc_change_reboot | bool }}"
>   when: smc_change_before.overlay
> ```
>
> Flow map: `roles/smc_change/drawio/parts/master.yaml` and its parts assemble to `drawio/flows.yaml`, which renders `drawio/flows.drawio`, both with
> `just smc_change_flows`; `just smc_change_flows_check` reports drift in either. Pages: Overview, `E2E flow` (the modes Check, Apply,
> Verify, Rollback), one `E2E: <change>` page per change spec, then the mode pages. A change spec's folder `files/changes/<spec>/` holds its parts
> `flow-components.yaml` and `flow-flows.yaml`, included from master, and a family in `drawing.families` with `own_page: true, flow_pages: false`: its flows explain
> the change itself (where the affected code runs, the fix, why it takes effect, the proof, the rollback), each step naming the stage that
> does it, numbered from 1 and kept off the `E2E flow` page. Written by hand from the spec; nothing generates them (operator, 2026-10-26).

> **Learned 2026-10-23** · spec fields proves and soak_minutes, undo backup path · VERIFIED_PRIMARY · Source: php-rct-smc01 runs of
> etc-hosts-hostname (apply refused, then rollback, apply); roles/smc_change files/probe/30_commands.py, tasks/load_spec.yml,
> tasks/actions/command_rollback.yml, tasks/verify.yml · Falsifier: an apply refused as unhealthy only because a `proves` check is false before the change
> `verify.commands` doubles as baseline health, so a spec whose checks describe the fixed state was refused as "already unhealthy" (needed
> `-e smc_change_allow_unhealthy_baseline=true`). New `verify.proves` (same form as commands): run in both probes, never counted as health,
> judged as the `proves` gate after an apply and ignored by a rollback (which is judged on health plus `restored`). New spec `soak_minutes`
> (operator, 2026-10-23): `-e smc_change_soak_minutes` wins, then the spec, then 5; 0 for a change that restarts nothing (hosts change: 45 s, not
> 6 min). A `command` action's `undo` gets `SMC_CHANGE_BACKUP`, the folder of the backup being restored as seen live or inside the chroot:
> after a passed apply the cleanup stage leaves no backup on the box, and rollback stages the controller copy in `/var/cache/smc_change/rollback`
> (lower dir on overlay boxes); the spec itself is templated at load and cannot name role variables. Spec `etc-hosts-hostname` writes the
> smc_network form (`127.0.0.1 localhost <host>`, `127.0.1.1 <host>`) live and in the lower dir; proven apply, rollback, apply.
>
> ```yaml
> - name: Run the undo live
>   ansible.builtin.command:
>     argv: [/bin/sh, -c, "{{ smc_change_action.undo }}"]
>   environment:
>     SMC_CHANGE_BACKUP: "{{ smc_change_rb_dir }}"
> ```

> **Learned 2026-10-26** · spec field backup.shared: name-identified backup files kept once for all SMCs · VERIFIED_PRIMARY (offline) · Source:
> local-knowledge-ansible `2ade781`, roles/smc_change tasks/cleanup.yml, tasks/rollback_locate.yml, tasks/load_spec.yml; warehouse-rct01 apply
> 20261026_145159 fetched the same seven php8.1 .debs per SMC · Falsifier: a second SMC at an already pooled version still fetches its .debs
> Operator, 2026-10-26: the same build must not be copied from every SMC, and which files that applies to is the change spec's choice, not the
> role's (the role stays generic; a future change may want per-SMC copies or share another file type). Spec `backup.shared` is a list of globs;
> stage 10 fetches only backup files whose name the controller pool `files/changes/<spec>/runs/<flavor>/backups/shared/`
> lacks, links fetched ones into the pool (`ln` never overwrites, so two SMCs fetching the same name at once leave one copy) and writes
> `shared.txt` in the host folder; rollback copies the listed files back beside `paths.tgz`. Absent or `[]` = full copy per SMC (etc-hosts-hostname,
> php-ini-upload-progress-off). The match is by name only: dpkg-repack of one build on two SMCs gives different bytes (embedded timestamps), so a
> checksum compare would never share anything. Only list files whose name changes when the content does (`<package>_<version>_<arch>.deb`); the
> spec loader refuses globs matching `paths.tgz` (same name on every SMC, that SMC's own config). Per-SMC config differences stay in `paths.tgz`,
> restored after `dpkg -i --force-confold`. Tested offline (glob split, pool skip, race guard, missing `shared.txt`); not yet run on an SMC.
>
> ```yaml
> # roles/smc_change/tasks/cleanup.yml (local-knowledge-ansible 2ade781)
> - name: Copy the backups to the controller
>   ansible.builtin.fetch:
>     src: "{{ smc_change_file }}"
>     dest: "{{ smc_change_ctl_backup }}/"
>     flat: true
>   loop: "{{ smc_change_backup_files.files | default([]) | map(attribute='path') | reject('in', smc_change_pooled_on_box) | list }}"
> ```

> **Learned 2026-10-26** · soak counted from the restart, start_now, PHP checks beyond the portal home page · VERIFIED_PRIMARY (offline role
> code; live probes read-only) · Source: roles/smc_change tasks/restart.yml, tasks/reboot.yml, tasks/verify.yml, playbooks/smc_change.yml (Run
> summary); warehouse-rct01 apply 20261026_145159 (17 min: ~3.5 min cron wait then a 5 min soak that saw 1 access-log line); access logs of 4
> prod RCT SMCs (adjamarragu, alice-well, bidyadanga-airport, cave-hill: 13-123 page loads over all kept logs) · Falsifier: a soak that runs
> the full soak_minutes after a cron wait, or a start_now process that runs twice
> The soak waits only for what is left of `soak_minutes` after the restart (or the reboot), so the cron wait counts toward it. A `restart.processes`
> entry with `start_now: true` is started at once from root's own cron line (cron's `/bin/sh`, `PATH=/usr/bin:/bin` and the crontab's `NAME=value`
> lines, via `setsid -f`), after waiting up to 10 s for the old process to exit. Only for programs that cope with cron starting them again: rct-tstik
> (`cd /var/www/html/rct-tstik/public && nohup php -S 10.254.0.1:8080 &>/dev/null`, no "already running?" check) does, because a second copy cannot
> bind the port. Spec php-cve-2026-109618 now soaks 1 minute and checks the portal's `/index.php/wifi/terms` (a second view, loaded by real
> clients; `/` and `/index.php/wifi/index` are the same page) and the tstik page on 8080 by port test plus page text. `pgrep -f 'php -S '` inside
> a shell matches the shell's own command line, so shell checks test the port instead. Root's crontab also runs `57 23 * * * pkill -9 php` (kills
> CLI PHP nightly; cron restarts it). The final Run summary now prints each host's gates (`gates 10/10 hold: ...` or the failed ones).
> Probe commands take optional `name` (labels the line and shows the command's last output line) and `timeout` (s, default 30). The PHP spec
> checks rct-tstik's AVR by running `php artisan update:stats` (root cron */5; ~15 s, 24 serial reads over `SerialIIO("serial4", 19200 ...)`
> in app/Services/IOManager.php) and judging the lines it appends to storage/logs/laravel.log: at least one `Total Read Data[126,...]` and no
> `Unable to read the data from AVR`. Every RCT SMC has an AVR except the bench Pi php-rct-smc01 (operator, 2026-10-26), whose log holds only
> empty reads and that error; a log that never held a `Total Read Data[126` line is taken as no AVR and passes. laravel.log is one large
> file (270-436 MB on prod) with thousands of network `local.ERROR` lines (cURL 6/28, socket_connect), so a gate on any ERROR would fail every
> site; 0 AVR errors ever on warehouse-rct01, alice-well, cave-hill, adjamarragu. Check mode on warehouse-rct01 (2026-10-26, 120 s): portal-terms
> 200, tstik page renders, 24 AVR reads, no errors. `/index.php/wifi/terms` answers 200 with HTML on prod wh, nbn_accelerate, nbn_wh and rcp too.
>
> ```yaml
> - name: Let client traffic reach the changed box (what is left of the soak)
>   ansible.builtin.pause:
>     seconds: "{{ smc_change_soak_left }}"
>   vars:
>     smc_change_soak_left: >-
>       {{ [smc_change_soak | int * 60 - (now().timestamp() | int - smc_change_restarted_at | default(now().timestamp()) | int), 0] | max }}
> ```

## Interrupted-change recovery and production PHP review (2026-10-26)

`VERIFIED_PRIMARY` (source and direct runtime, ansible-wifi branch `rise`; local-knowledge base `aacf57c` plus uncommitted recovery work):
production RCT PHP apply 20261026_161421 passed 11/11 gates in 792 s. Seven `.18` packages became `.28` live and in the lower dir; lower dir ro,
no reboot, portal/terms/TSTIK render, 24 AVR reads without errors, unchanged modules, no deleted PHP maps. Fresh read-only checks confirmed
package/service/mount/pages/cleanup state; controller config tar and seven saved old builds exist. PIN activation and forced reboot survival
were not demonstrated. Review: local-knowledge `evidence/smc-change-recovery-20261026_1701.md`.

`USER_STATED` (2026-10-26): add a generic recovery journal and safe explicit resume; optimize only after phase timings exist.
`VERIFIED_PRIMARY`: prior `verify.yml` called `record.yml`, which marked done before cleanup. Interim records now say `verified`; only final
verified-and-cleaned applies/rollbacks say `passed` and update state. Journals under `runs/<flavor>/journal/<host>.json` are controller-only, 0600,
written before writes/phases, retaining the original baseline/id/backup/cleanup ownership. Attempts have separate record timestamps.

Use `-e smc_change_mode=assess` for read-only recovery safety (skips application commands); it reports complete, safe_to_restart,
safe_to_resume or needs_repair. Resume is on by default (`smc_change_resume: true`, operator 2026-10-26; `false` refuses an unfinished SMC), in the original mode. An unfinished journal blocks a new apply even
with force. Changed spec/code/assets, incomplete dpkg state, chroot residue, changed overlay or missing backup evidence refuse recovery.
Phase 5 repeats backup; 6 replays only actions declaring `resume_safe: true`; 7/8 repeats restart/close; 9/10 reverifies then repeats cleanup.
PHP's exact-version action opts in. Writable lower layers route through restart/close and must be ro at verification. A partly deleted
remote backup cannot truncate the controller shared-file manifest: cleanup uses the original journaled list. Do not run competing controllers
for the same SMC/change; atomic journal replacement is not an operator lock. Legacy failures have no inferred resume checkpoint. Legacy check-mode/read-only records neither invent a failure nor hide a prior real failure.

```yaml
# roles/smc_change/tasks/record.yml (base aacf57c + uncommitted 2026-10-26 recovery)
- name: Store this host's state when the apply or rollback passed
  ansible.builtin.include_tasks: state.yml
  vars:
    smc_change_state_step: write
  when:
    - smc_change_mode in ['apply', 'rollback']
    - smc_change_record.result == 'passed'
    - smc_change_cleanup_complete | default(false) | bool
```

Validation: five unit-test methods (~0.013 s, stage/safety scenarios), real controller journal/state fixture, red/green partial-cleanup
regression; read-only live resume-fact fixture (25 OK, changed=0) and assessment passed. A real interrupted mutating SMC has not been
fault-injected. `lint_new.sh` all language/inventory checks passed in 9.26 s. Records now include phase timings, elapsed seconds, budget and
over-budget flag (900 s default; report, never abandon an in-flight SMC). Prior run lacked phase timings: 302 s came after the final probe;
performance optimization is deferred to measured subsequent runs. Flow map adds Assess/Resume; renders/checks and six changed pages reviewed.
Screenshots: `screenshots/20261026-smc-change-recovery/` (generic pages, no customer identifiers).

> **Learned 2026-10-26 (evening)** · overlay Pi reboot fallback, Pi clock, satellite session drops, resume by default · VERIFIED_PRIMARY
> (live read-only: adjamarragu-smc01 records 20261026_173435/180915/182818, assess runs; alice-well, cave-hill portal timings) · Source:
> roles/smc_change tasks/persist_overlay.yml, reboot.yml, probe.yml, recovery.yml, files/probe/40_http.py, files/recovery.py (local-knowledge-ansible,
> uncommitted at write time) · Falsifier: a fallback reboot whose record has no `lower_busy`, or an after-probe that fails on a page answering in 3 s
> - **Portal home page is slow by design**: `/` calls the WiFi API upstream (`Model::factory('WIFI_API')` in `controller/wifi.php`), 2.8-10 s on
>   unpatched RCT SMCs; `/index.php/wifi/terms` answers in 0.04 s. adjamarragu-smc01 missed the probe's fixed 20 s right after its fallback reboot
>   (curl rc 28) while terms answered: http checks now take per-endpoint `timeout` (portal 45) and `retries` (1, only on curl 7/28/52/56).
> - **A Pi has no RTC**: after a boot its clock is wrong until NTP corrects it (adjamarragu's apache logged its post-boot start ~8 min early);
>   HTTPS calls fail (tstik logs `certificate is not yet valid`) and Teleport is slow to connect (operator). `timedatectl` NTPSynchronized stays
>   `no` under ntpd (warehouse-rct01), so reboot.yml waits until the SMC clock is within 60 s of the controller's (10 min, not fatal).
> - **Lower dir EBUSY**: the remount was tried once, straight after the restarts; it is now tried every 10 s for 90 s before the fallback reboot,
>   and the record keeps `lower_busy` (error, attempts, holders: mapped and open deleted files, `/var/log` left out). What held adjamarragu's
>   lower dir is unknown: holders were only printed then, and the reboot cleared the overlay upper layer.
> - **Teleport tunnels drop sessions** ("Connection closed by UNKNOWN port 65535") while `tsh ls` still lists the node: the probe ignores one
>   unreachable result, waits with `wait_for_connection` (600 s) and probes again. Ansible's docs do not say `until`/`retries` repeat an
>   unreachable task, so the role does not rely on that.
> - **Records feed recovery**: a failed run that stopped before stage 5 with no backup changed nothing and is skipped by `legacy_failed`
>   (aeroplane-1-smc01 was refused `needs_repair` twice over its own pre-change refusals); `already_done` is not tied to the role-code
>   fingerprint (a role edit would otherwise re-run restarts and a possible reboot on every patched SMC) but to `target`, a hash of the spec's
>   actions without `resume_safe`, stored with the state: a spec moved to a newer build re-runs its SMCs; older states without it count as done.
> - **Resume**: on by default; nothing unfinished means a normal run (one command for a batch); code changed since the start refuses phases 5-8
>   but lets 9-10 (verify, cleanup) run on the current code (`drifted` in the decision); a writable lower dir with drift is refused.
>
> ```yaml
> - name: Probe the host ({{ 'before' if smc_change_probe_base is none else 'after' }})
>   ansible.builtin.command: &smc_change_probe_cmd
>     cmd: python3 -
>     stdin: "{{ smc_change_probe_src }}"
>   register: smc_change_probe_first
>   ignore_unreachable: true
> - name: Wait for the connection after it dropped mid-probe
>   ansible.builtin.wait_for_connection: {timeout: 600, sleep: 10}
>   when: smc_change_probe_first.unreachable | default(false)
> ```

> **Learned 2026-10-26 (19:30)** · smc_change run time on satellite SMCs · VERIFIED_PRIMARY (aeroplane-1-smc01 apply 185058 phase timings and
> its /var/log/dpkg.log; warehouse-rct01 check runs; alice-well read-only pool match) · Source: roles/smc_change (local-knowledge-ansible,
> uncommitted at write time) · Falsifier: a probe whose AVR read takes > 30 s with no cron run in progress
> - A remote Ansible call costs ~3.5 s over Teleport+satellite; a reconnect 11-15 s (ControlPersist 60 s drops it after each soak or wait).
>   The play now sets `ansible_ssh_args` with ControlPersist 10m and ServerAliveInterval 15 x 3.
> - `pgrep -f` inside a shell matches the shell's own command line whenever the script text contains the pattern's target, even with the
>   `[a]rtisan` trick if the script also runs `php artisan ...` literally: the AVR check waited 60 s every probe. Spell the command through
>   a variable (`a=artisan; php "$a" update:stats`).
> - Two `dpkg-repack` copies of one installed build are different files (control holds "Repackaged on <date>", archive metadata differs) with
>   identical `md5sums`; comparing sha256 of `/var/lib/dpkg/info/<pkg>[:arch].md5sums` with the pooled .deb's md5sums, plus a clean
>   `dpkg --verify`, identifies the build. Stage 5 now reuses pooled builds that way and skips installing dpkg-repack when all match.
> - apt's cache keeps the .debs of the live install (`/var/cache/apt/archives`, RAM upper layer on overlay Pis: gone after a restart); the
>   lower-dir install copies them instead of `apt-get download` again.
>
> ```bash
> a=artisan
> for i in $(seq 1 60); do pgrep -f '[a]rtisan update:stats' >/dev/null || break; sleep 1; done
> cd /var/www/html/rct-tstik && timeout 120 php "$a" update:stats >/dev/null 2>&1
> ```
> - Resume after a code change (2026-10-26, widened by the operator after akwalirrumanja-smc01 was cut off in stage 7): only backup and
>   actions (5-6) are refused; restart, close, verify and cleanup (7-10) run on current code. Rollback material is judged per file on the
>   SMC or the controller (pooled builds live only in the pool). Journal timings are named from the phase number.
> - `pkill -f` from a task whose `environment:` holds the pattern kills the task itself: Ansible puts environment variables on the remote
>   command line (akwalirrumanja-smc01 lost its session at the stop/start step twice). The pattern now goes base64-encoded:
>
> ```yaml
>   environment:
>     SMC_PATTERN_B64: "{{ smc_change_proc.pattern | b64encode }}"
>   # in the script: pat=$(printf '%s' "$SMC_PATTERN_B64" | base64 -d); pkill -f -- "$pat"
> ```
> - Root's `57 23 * * * pkill -9 php` on RCT SMCs is a workaround (operator, 2026-10-26): it clears PHP and Python processes that pile up
>   from cron jobs started without a running-check (e.g. `*/5 ... nohup php -S 10.254.0.1:8080`). Proposed, not decided: guard those cron
>   lines with `flock -n` (or a pgrep check) and drop the nightly kill.


## Drop-proof installs, leftover chroot, lower dir first (2026-10-26 evening)

`VERIFIED_PRIMARY` (runtime, local-knowledge-ansible `76b0f86`): alice-well-smc01's Teleport session dropped at "Install the .debs inside
the chroot". dpkg finished in the lower dir (lower dpkg `ii .28`, audit clean) but the block's `always` close never ran: binds on
`/media/root-ro/{dev,dev/pts,proc,sys}`, `policy-rc.d`, staging dir, lower rw. The next run refused `needs_repair` (correct). After a manual
unbind/remove the resume passed 11/11, but two `php /usr/local/bin/kohana status:update:usage` processes (not in the spec's restart list)
held old php8.1 files, the remount stayed EBUSY for 138 s and the SMC rebooted (phase 8 455 s). Fixes:

- Installs run async and wait through `tasks/await_job.yml`. An `until` loop does not retry an unreachable host (ansible-core
  `task_executor.py`: a connection failure raises out of the retry loop), so the wait copies the probe's pattern:

```yaml
# roles/smc_change/tasks/await_job.yml (76b0f86)
- name: Wait for {{ smc_change_job_name }}
  ansible.builtin.async_status:
    jid: "{{ smc_change_job.ansible_job_id }}"
  register: smc_change_job_first
  until: smc_change_job_first.finished | default(false)
  retries: "{{ (smc_change_job_minutes | default(30) | int) * 6 }}"
  delay: 10
  ignore_unreachable: true
- name: Wait for the connection after it dropped during {{ smc_change_job_name }}
  ansible.builtin.wait_for_connection: {timeout: 600, sleep: 10}
  when: smc_change_job_first.unreachable | default(false)
# ... then async_status again (a second drop ends the play for the host)
```

- `files/recovery_safety.py` reports `dpkg_busy` (by `/proc/<pid>/comm`, so no command line self-matches) and `own_leftover` (the journal
  says policy-rc.d was not there before, nothing installing); `recovery.py` then returns `safe_to_resume` with `close_chroot`, and main.yml
  closes the chroot and removes the staging dir before anything else. Anyone else's chroot, a running dpkg or a failed audit stays
  `needs_repair`.
- `USER_STATED` (operator, 2026-10-26): on overlay SMCs apt_pin installs the lower dir first and live only when no reboot follows; cron is
  paused for the gap. After the lower-dir install `files/reboot_holders.py` (read-only, 0.3 s on alice-well) lists processes mapping or
  holding deleted files owned by the changed packages (lower dpkg `-L`), split into ones the spec restarts (systemd unit in the cgroup, or a
  restart pattern) and others; any other holder after up to 60 s, or spec `always`/`overlay_only`, sets `smc_change_reboot_planned`
  (journalled): no live install, no stage 7 restarts, lower dir flushed, stage 8 reboots.

```yaml
# roles/smc_change/tasks/actions/apt_pin.yml (76b0f86) - the cron pause before the chroot dpkg
systemctl is-active -q cron || { echo "cron not running"; exit 0; }
systemctl stop smc-change-cron-resume.timer 2>/dev/null || true
systemd-run --quiet --unit=smc-change-cron-resume --on-active=15min /bin/systemctl start cron
systemctl stop cron
```

- Check mode: the lower-dir version read runs with `check_mode: false` and the assert is skipped in check mode (it failed on overlay SMCs
  against an empty list). Async `shell` under `--check` returns "Command would have run if not in check mode" and runs nothing (tested).
- `VERIFIED_PRIMARY` measurement: any task that touches an SMC costs 5-24 s over Teleport/satellite; a `--check` apply on alkngarrija-smc01
  spent 123 s in stage 6 with nothing installed. alligator-hole-smc01 (async code, live-first) passed 11/11 in 441 s, stage 6 240 s.
- Incident: an agent check run and the operator's apply probed alkngarrija-smc01 at the same second; both `artisan update:stats` hit the AVR
  serial port, one read failed (`Unable to read the data from AVR`), both runs refused. One controller per SMC, check runs included.
- Not yet run for real: the lower-dir-first order, the cron pause, a real drop through `await_job.yml`. Test SMC: alkngarrija-smc01
  (operator: not warehouse-rct01). Runs table: `just smc_change_runs <change>` (`scripts/ansible/smc_change_runs_table.py`).

`VERIFIED_PRIMARY` (runs 2026-10-26 21:38-22:20, role at local-knowledge-ansible `76b0f86`): the lower-dir-first order passed 11/11 on
alpara-smc01 and amatjatpalk-smc01 (overlay, live install after the lower dir, no reboot, stage 6 261/244 s, cron-started processes back
after the pause). alkngarrija-smc01's first real apply lost SSH ~2 min into the async chroot dpkg (banner timeouts) and stayed unreachable
past `wait_for_connection`'s 600 s; the Teleport tunnel was still listed while SSH closed and the autossh backdoor was down. Second drop
today at the same step (alice-well-smc01 the first): `UNVERIFIED` hypothesis that dpkg's writes to the SD card starve sshd; to check on the
SMC's dpkg.log and journal, candidate fix `ionice -c3 nice -n19` on the chroot dpkg. `run_once` for the role's bookkeeping is a patch in
local-knowledge `plans/smc-change-run-once-20261026_2220.patch` (not applied); the operator wants run-once steps defined by the role and
declared in the change spec (design open).

## Done skip, runs per flavor, retries, timing, journal freeze (2026-10-27)

Source: local-knowledge-ansible ansible-wifi CHANGELOG 20261027_1042; runbook `plans/smc-change-resume-20261027_1038/README.md`.

- **Done SMCs are left out before any connection** (operator: "an smc which has been completed ... is ignored in the next run"). The
  playbook's first play (no serial, controller only) runs `tasks/pending.yml` and the change play runs over `smc_change_todo`. apply, check
  and assess skip a passed apply of the current target; rollback a passed rollback; verify never; `-e smc_change_force=true` none. The
  summary lists them as ALREADY DONE.

  ```yaml
  - name: Group the host as done or still to do
    ansible.builtin.group_by:
      key: "{{ 'smc_change_done' if smc_change_done_why is defined else 'smc_change_todo' }}"
  ```

- **Run evidence per flavor** (operator: "the standard for all the changes"): `files/changes/<spec>/runs/<flavor>/{records,state,journal,
  backups}`, flavor = the `-i` inventory folder, made on its first run (`smc_change_runs_dir` in `defaults/main.yml`). Moved by
  `scripts/smc_change_runs_by_flavor.py` (dry run by default; `--with-active` only when `runs_dir` moves in the same step).
- **SSH retries**: `ansible_ssh_retries: 8` on the change play rides out ~117 s of a satellite or Teleport blip (rc 255 only; ansible.cfg's 3
  gave ~4 s). Seen: banana-well-smc01 "Data could not be sent ... Connection closed" while staging .debs in stage 6.
- **TASK_TIMING**: `true` writes `task_timing/smc_change-<start>.json` (slowest first) and prints one line; `verbose` also prints the per-task
  lines and recap (the old `true`); `TASK_TIMING_DIR` moves it.
- **Teleport online filter (live since 2026-10-27 13:24)**: `tsh ls --proxy=<proxy> --format=json flavor=<inventory folder>,env=<inventory file>`
  once per run; the `flavor` and `env` labels match the inventory folder and file (rct prod 290, rct stage 1; rcp prod 17 of 21 in
  inventory, the four `generic-*` hosts not in Teleport). Label form and `--query 'labels.flavor == "rct"'` return the same.
- **Run-once preparation (live since 2026-10-27 13:24; 9 probe-join lines per SMC gone)**: `tasks/prepare.yml` does spec load and check, plan banner, fingerprint, probe program and
  folders once per run in the first play; `tasks/probe_cfg.yml` keeps the per-SMC HTTP resolution.
- **Captive portal render is part of the PHP verification**: the spec's `http` checks `portal` (home) and `portal-terms`
  (`/index.php/wifi/terms`) at the SMC's portal FQDN must redirect, or answer 200 with HTML and none of the bad markers, with the same status
  as the before-probe; a portal broken before the change refuses the apply (`files/probe/40_http.py`, `tasks/guard.yml`). Shown as the first
  step of the PHP Prove flow.
- **An active journal freezes the role code** (RULE-007, incident 2026-10-27): editing `tasks/pending.yml` under open journals made six
  resumes `needs_repair`; they resume only on the exact file they started with (both kept with sha256 in the plans folder). The fingerprint
  covers `tasks`, `templates`, `files` (less `files/changes`, `files/tests`) plus the resolved spec, so the spec is frozen too; `defaults/`,
  `meta/`, `drawio/` and the playbook are not.

  ```python
  drifted = journal.get("fingerprint") != data.get("fingerprint")
  if drifted and journal.get("phase") not in (7, 8, 9, 10):
    result["reasons"] = ["Host or resolved spec fingerprint changed; do not replay this transaction."]
  ```

**First rcp prod apply (2026-10-27).** jigalong-smc01 (x86_64, plain root): apply `20261027_112044` passed 10/10 gates in 736 s with no reboot
(BACKUP 89 s, ACTIONS 143 s, VERIFY 311 s, CLEANUP 159 s; the empty rcp pool meant its own repack); it created `runs/rcp/{state,journal,
records}` on its first run, proving the per-flavor layout for a new flavor. A read-only `verify` at 12:05 passed 10/10 (49 s), captive portal
home and terms 200 with HTML and no PHP error markers.

## Stranded-run self-repair, kohana cron jobs, lockstep timing, wh and nbn_accelerate (2026-10-27 afternoon)

Source: local-knowledge-ansible ansible-wifi CHANGELOG 20261027_1451; commits 0e8a2f0 (recovery, cron_job, tstik check), 7ff3a30
(prepare-once live, interim record).

- **A drifted apply cut off at 5-6 that installed nothing repairs itself (`abandoned_clean`)** (operator: "why cant it be built into the
  php fix change?"). Five rct SMCs were stuck at 6/11 after a role edit; read-only, every php8.1 package was still the old build live and in
  the lower dir and only the lower dir was left read-write. Now: lower dir remounted read-only, journal moved to
  `runs/<flavor>/journal/superseded/<host>-<start>.json`, fresh start. Apply mode only: check, verify and assess reach the same decision
  (the journal's mode stands in for theirs) and must not change the box (found by a side agent before any such run).

  ```python
  # files/recovery.py (0e8a2f0)
  return all(b.get("pkgs") == n.get("pkgs") and b.get("pkgs_lower") == n.get("pkgs_lower") for b, n in zip(pins_before, pins_now))
  ...
  if (drifted and journal.get("phase") in (5, 6) and journal.get("mode") == "apply" == data.get("mode")
      and not safety.get("dpkg_busy") and safety.get("chroot_clear") is True and untouched(...)):
    result.update(classification="abandoned_clean", can_start=True, supersede_journal=True, close_lower=bool(safety.get("lower_rw")))
  ```

- **Every flavor runs the portal's Kohana jobs from root's cron** (`kohana status:update:usage` every minute, `status:update:status` every
  5, `status:clean:up` daily; rcp also `status:push:wifi:site:broker`; read on jigalong, barrakiah, areyonga, engawala). One still on the
  old build held the lower dir past the 90 s close window and forced the fallback reboot (areyonga-smc01, binjari-top-camp-smc01:
  `lower_busy` holder `php /usr/local/bin/kohana status:update:usage`). Spec restarts them with the new `respawn: cron_job`: stopped
  whenever one is running at the restart (not only if the before-probe saw one), never waited for, not in the processes gate. Root's own
  nightly `pkill -9 php` already kills them.

  ```yaml
  # tasks/restart.yml (0e8a2f0)
  when:
    - smc_change_proc.respawn | default('none') != 'none'
    - smc_change_proc.respawn == 'cron_job' or smc_change_before.processes[smc_change_proc.pattern] | default(0) | int > 0
  ```

- **rct-tstik exists on rct only; wh serves python3 telemetry on 8080.** A check keyed on "something listens on 8080" refused three wh SMCs
  as unhealthy; it now skips where `/var/www/html/rct-tstik` is absent. Per flavor, the long-running cron PHP program: rcp, nbn_accelerate,
  nbn_wh `php Start.php` (apn-mqtt-client); rct `php -S` on 10.254.0.1:8080 (rct-tstik); wh none.
- **Batches run in lockstep.** With `smc_change_serial` N, Ansible's linear strategy finishes each task on every host before the next, so
  every host's stage time is the batch's: one fallback reboot (314 s) or a slow satellite host sets every line (wh batch of five 1,151 s, rct
  batch of six 1,828 s, both over the 900 s budget). A host resumed past a stage shows its wait inside the stage before.
- **Interim verify record**: verify.yml writes a record before cleanup; it no longer opens stage 11, so the summary reads 9 VERIFY,
  10 CLEANUP, 11 RECORD (`smc_change_record_interim`).
- **`include_tasks` files load when reached**: editing `tasks/` while a playbook runs changes the running play, journals or not.
- **Results:** wh 6/6 passed (engawala canary; areyonga fallback reboot); first nbn_accelerate amata-smc01 passed (x86, no reboot,
  `php Start.php` 2 before and after); rct batches of five (12:29) and six (12:50) passed.

## rct-tstik-iridium-update: a command that writes the lower dir itself, copy sources under RULE-007 (2026-10-28)

Source: local-knowledge-ansible ansible-wifi (base commit 608697b, change uncommitted at writing), change record
`roles/smc_change/files/changes/rct-tstik-iridium-update/rct-tstik-iridium-update-20261028_1221.md`.

- **The spec**: rct only. rct-tstik to `release/iridium` at `smc_bases_telemetry_iridium_git.commit` (1318c7b), `py_avrloader_v2.py` and AVR firmware
  V3.07 to `/home`; `reboot: never`; gates from the tester's checks (stats page as `commands`; iridium routes, `artisan self:tests` + `/st_results`,
  AVR menu `-m` with exit 0, HEAD at the commit live and lower as `proves`). Canary aeroplane-1-smc01 passed 8/8 gates in 592 s (2026-10-28).
- **Spec values can name inventory vars.** The spec is templated at load per host, so `'{{ smc_bases_telemetry_iridium_git.commit }}'` in a
  command keeps the inventory the one place the commit lives (role vars are not available there; `command_rollback.yml` header).
- **A command that persists itself, no chroot, no reboot.** For a large tree pulled over the satellite, `chroot: true` would download it twice. The
  command clones live, then `cp -a` into `/media/root-ro` (read-write during stage 6), and its `check` asserts both HEADs:

  ```yaml
  # files/changes/rct-tstik-iridium-update/rct-tstik-iridium-update.yml (excerpt)
    - type: command
      chroot: false
      check: &tstik_at_commit >-
        c='{{ smc_bases_telemetry_iridium_git.commit }}'; d='{{ smc_bases_telemetry_iridium_git.dest }}'; l=/media/root-ro;
        [ "$(git -C "$d" rev-parse HEAD 2>/dev/null)" = "$c" ] || exit 1;
        findmnt "$l" >/dev/null 2>&1 || exit 0;
        [ "$(git -C "$l$d" rev-parse HEAD 2>/dev/null)" = "$c" ]
  ```

  The same anchor is reused as a `proves` entry, so the persistence is gated, not assumed. Cost: the new tree (~54 MiB + .git) sits in the upper
  tmpfs until the next boot (operator accepted, 2026-10-28).
- **Copy sources while RULE-007 freezes `files/`.** `copy` reads `files/<spec>/<src>`; adding files there changes the role fingerprint and breaks
  active journals' resume. A directory symlink `files/<spec> -> changes/<spec>` is invisible to `recovery.py --fingerprint` (`is_file()` false,
  `rglob` does not follow it): fingerprint `2f6534b46e94...` identical before and after.

  ```python
  # files/recovery.py fingerprint (608697b)
  for folder in ("tasks", "templates", "files"):
    for path in sorted((root / folder).rglob("*")):
      relative = path.relative_to(root)
      if not path.is_file() or "__pycache__" in relative.parts or relative.parts[:2] in (("files", "changes"), ("files", "tests")):
        continue
  ```

- **copy cannot roll back a file that did not exist.** `copy_rollback.yml` always includes `_files_rollback.yml`, which fails when `paths.tgz`
  lacks the file; new files (`/home/...`) therefore stop a rollback. Put command actions last so their undo runs first. Fix waiting in
  `plans/smc-change-copy-rollback-new-file-20261028_1145.patch` (remove a copied file the backup never held).
- **A check that must fail before the change belongs in `proves`.** `commands` must already hold before an apply or the SMC is refused; the loader
  is absent and the tree is master before, so those checks are `proves`.
- **Check mode can still act** when a probe command does: `artisan self:tests` writes `st_results.blade.php` and `update:stats` reads the AVR.
- **The probe prints `proves` by command text**, not `name` (cosmetic; noted while the role is frozen).
