---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261027_1459
---

# skill-smc Changelog

## Contents

- [20261027_1459 — smc_change self-repair, kohana cron_job, lockstep timing; link health probe (v0.8.4 -> v0.8.5)](#20261027_1459--smc_change-self-repair-kohana-cron_job-lockstep-timing-link-health-probe-v084---v085)
- [20261027_1207 — Teleport re-join without a tunnel; first rcp PHP apply (v0.8.3 -> v0.8.4)](#20261027_1207--teleport-re-join-without-a-tunnel-first-rcp-php-apply-v083---v084)
- [20261027_1050 — smc_change: done SMCs skipped before connecting, runs per flavor, retries, TASK_TIMING, journal freeze (v0.8.2 -> v0.8.3)](#20261027_1050--smc_change-done-smcs-skipped-before-connecting-runs-per-flavor-retries-task_timing-journal-freeze-v082---v083)
- [20261026_2222 — smc_change: new order passed on two Pis; second drop at chroot dpkg (v0.8.1 -> v0.8.2)](#20261026_2222--smc_change-new-order-passed-on-two-pis-second-drop-at-chroot-dpkg-v081---v082)
- [20261026_2146 — smc_change drop-proof installs, lower dir first, runs table (v0.8.0 -> v0.8.1)](#20261026_2146--smc_change-drop-proof-installs-lower-dir-first-runs-table-v080---v081)
- [20261026_1844 — smc_change: Pi clock wait, remount retry, lower_busy, http timeout/retries, probe survives a dropped session, resume by default (v0.7.9 -> v0.8.0)](#20261026_1844--smc_change-pi-clock-wait-remount-retry-lower_busy-http-timeoutretries-probe-survives-a-dropped-session-resume-by-default-v079---v080)
- [20261026_1701 — smc_change safe recovery, completion after cleanup and phase timing (v0.7.8 -> v0.7.9)](#20261026_1701--smc_change-safe-recovery-completion-after-cleanup-and-phase-timing-v078---v079)
- [20261026_1617 — smc_change PHP verify: soak from the restart, start_now, named command checks, tstik AVR and 8080 checks; tstik-capture AVR counts (v0.7.7 -> v0.7.8)](#20261026_1617--smc_change-php-verify-soak-from-the-restart-start_now-named-command-checks-tstik-avr-and-8080-checks-tstik-capture-avr-counts-v077---v078)
- [20261026_1534 — smc_change backup.shared: name-identified backup files kept once for all SMCs (v0.7.6 -> v0.7.7)](#20261026_1534--smc_change-backupshared-name-identified-backup-files-kept-once-for-all-smcs-v076---v077)
- [20261026_1506 — smc_change flow map in parts, one E2E page per change spec (v0.7.5 -> v0.7.6)](#20261026_1506--smc_change-flow-map-in-parts-one-e2e-page-per-change-spec-v075---v076)
- [20261023_1737 — smc_change on an overlay Pi: close after restart, overlay_fallback, proves, soak_minutes; tstik bench note; identity probe hosts_name (v0.7.4 -> v0.7.5)](#20261023_1737--smc_change-on-an-overlay-pi-close-after-restart-overlay_fallback-proves-soak_minutes-tstik-bench-note-identity-probe-hosts_name-v074---v075)
- [20261023_1625 — smc_inventory_add.py: add a new SMC to an inventory without guessing (v0.7.3 -> v0.7.4)](#20261023_1625--smc_inventory_addpy-add-a-new-smc-to-an-inventory-without-guessing-v073---v074)
- [20261023_1536 — smc_change rollback mode and done-tracking; root linters for every language (v0.7.2 -> v0.7.3)](#20261023_1536--smc_change-rollback-mode-and-done-tracking-root-linters-for-every-language-v072---v073)
- [20261023_1455 — smc_change: generic role, probe split per check, cleanup, skip unreachable/refused, stages; ruff root config (v0.7.1 -> v0.7.2)](#20261023_1455--smc_change-generic-role-probe-split-per-check-cleanup-skip-unreachablerefused-stages-ruff-root-config-v071---v072)
- [20261023_1351 — backdoor-watch.sh resolves stage hosts; smc_change command guard (v0.7.0 -> v0.7.1)](#20261023_1351--backdoor-watchsh-resolves-stage-hosts-smc_change-command-guard-v070---v071)
- [20261023_1339 — Local-knowledge folder reference and index script; PHP verification by mapped files; smc_change role recorded (v0.6.9 -> v0.7.0)](#20261023_1339--local-knowledge-folder-reference-and-index-script-php-verification-by-mapped-files-smc_change-role-recorded-v069---v070)
- [20261022_1718 — Evidence capture: timeouts reported as such, full-capture timing, end-marker fix (v0.6.8 -> v0.6.9)](#20261022_1718--evidence-capture-timeouts-reported-as-such-full-capture-timing-end-marker-fix-v068---v069)
- [20261022_1703 — Evidence scripts: a deadline on every tsh call, with an offline test (v0.6.7 -> v0.6.8)](#20261022_1703--evidence-scripts-a-deadline-on-every-tsh-call-with-an-offline-test-v067---v068)
- [20261022_1653 — Asterisk memory measured on the rcp fleet; umoona still without Asterisk; evidence script lacks a tsh deadline (v0.6.6 -> v0.6.7)](#20261022_1653--asterisk-memory-measured-on-the-rcp-fleet-umoona-still-without-asterisk-evidence-script-lacks-a-tsh-deadline-v066---v067)
- [20261022_1623 — collect-smc-evidence-full.sh voip group records Asterisk resident memory (v0.6.5 -> v0.6.6)](#20261022_1623--collect-smc-evidence-fullsh-voip-group-records-asterisk-resident-memory-v065---v066)

## 20261027_1459 — smc_change self-repair, kohana cron_job, lockstep timing; link health probe (v0.8.4 -> v0.8.5)

- `references/19_smc-change-role.md`: stranded-run self-repair (`abandoned_clean`, apply only); kohana cron jobs on every flavor restarted as
  `respawn: cron_job`; rct-tstik is rct only (wh 8080 is python3); batches in lockstep; interim verify record; run-once and the tsh filter live.
- `references/03_communication-flows.md` (banana-well entry, committed 0d9859b without a version bump): afternoon Teleport errors were 30-40%
  loss at the first hop with the WAN idle.
- `scripts/smc_link_health.sh` (new, `just smc_link_health <smc>`, test `test_smc_link_health.py`): an SMC's uplink over Teleport (loss to
  first hop and proxy, Teleport error trend, clock, backlog, autossh restarts, WAN rate); smoke-run on banana-well-smc01.

## 20261027_1207 — Teleport re-join without a tunnel; first rcp PHP apply (v0.8.3 -> v0.8.4)

- `references/03_communication-flows.md` (node join section): a cleared `/var/lib/teleport` re-joins under a new host id that may never open its
  reverse tunnel (banana-well-smc01, 2026-10-27; cause unverified: clock or link); old record lingers until expiry; cluster-side read-only checks;
  on an overlay Pi the clear is RAM-only.
- `references/19_smc-change-role.md`: first rcp prod apply (jigalong-smc01, 10/10, 736 s, created `runs/rcp/`) and its verify (10/10).
- version 0.8.3 -> 0.8.4.

## 20261027_1050 — smc_change: done SMCs skipped before connecting, runs per flavor, retries, TASK_TIMING, journal freeze (v0.8.2 -> v0.8.3)

- `references/19_smc-change-role.md`: new section "Done skip, runs per flavor, retries, timing, journal freeze (2026-10-27)" with code
  excerpts (group_by split, recovery drift rule); per-flavor `runs/<flavor>/` paths throughout; captive portal render documented as part of the
  PHP verification (home and wifi/terms, bad markers, same status, unhealthy baseline refuses).
- `scripts/smc_change_runs_table.py` reads `runs/<flavor>/records` (every flavor from `runs/`, or one); `scripts/smc_change_compare_records.py`
  globs the per-flavor layout and closes its files (ruff SIM115). Unit test and smoke runs on real records pass.
- `RUNBOOK.md` unchanged in routing (reference 19 already routes smc_change); version 0.8.2 -> 0.8.3.

## 20261026_2222 — smc_change: new order passed on two Pis; second drop at chroot dpkg (v0.8.1 -> v0.8.2)

- `references/19_smc-change-role.md`: alpara and amatjatpalk 11/11 on the lower-dir-first order; alkngarrija-smc01 unreachable during the async chroot dpkg (second drop at that step, I/O-starvation hypothesis unverified); run_once patch and the operator's spec-declared design (open).

## 20261026_2146 — smc_change drop-proof installs, lower dir first, runs table (v0.8.0 -> v0.8.1)

- `references/19_smc-change-role.md`: new section "Drop-proof installs, leftover chroot, lower dir first (2026-10-26 evening)": the
  alice-well-smc01 chroot drop, `await_job.yml` (until does not retry unreachable), `own_leftover` resume, lower-dir-first apt_pin with
  `reboot_holders.py` and a planned reboot, the cron pause, check-mode lower assert, round-trip cost (5-24 s per task), the AVR probe
  collision; code excerpts from local-knowledge-ansible `76b0f86`.
- `scripts/smc_change_runs_table.py` (+ test, `just smc_change_runs <change>`): one line per run record with result, phase 6-9 seconds,
  reboot (boot_id), lower-dir holders or failure.

## 20261026_1844 — smc_change: Pi clock wait, remount retry, lower_busy, http timeout/retries, probe survives a dropped session, resume by default (v0.7.9 -> v0.8.0)

- `references/19_smc-change-role.md`: Learned 2026-10-26 (evening) entry: portal home page calls the WiFi API (2.8-10 s), Pi has no RTC (clock
  wait after a fallback reboot; timedatectl unreliable under ntpd), lower-dir remount retried 90 s and `lower_busy` recorded, Teleport session
  drops handled by `wait_for_connection`, resume on by default with drift allowed at phases 9-10; probe.yml excerpt. The earlier entry's
  `-e smc_change_resume=true` line corrected to the new default.
- `references/19_smc-change-role.md`, same day: Learned (19:30) run time on satellite SMCs (per-call cost, ControlPersist, pgrep self-match,
  dpkg-repack copies identical by md5sums so pooled builds are reused by checksum, apt cache copy for the lower dir); records feed recovery
  (pre-stage-5 failures, `already_done` tied to the spec target hash); `pkill -f` with the pattern in `environment:` killed its own session
  (base64 fix); resume after a code change refuses only phases 5-6; rollback material judged per file; the nightly `pkill -9 php` is a
  workaround (operator) with a flock proposal.
- manifest 0.7.9 -> 0.8.0.

## 20261026_1701 — smc_change safe recovery, completion after cleanup and phase timing (v0.7.8 -> v0.7.9)

## 20261026_1617 — smc_change PHP verify: soak from the restart, start_now, named command checks, tstik AVR and 8080 checks; tstik-capture AVR counts (v0.7.7 -> v0.7.8)

- `references/19_smc-change-role.md`: Learned 2026-10-26 entry: soak counted from the restart or reboot, `restart.processes[].start_now` (root's
  cron line run at once; only for programs that cope with a second start, as rct-tstik's `php -S` does), probe commands' `name`/`timeout`/note,
  the PHP spec's portal-terms, tstik 8080 and AVR read checks (`php artisan update:stats`, `Total Read Data[126,...]`, no AVR error; no AVR ever
  logged passes), RCT AVR fact (all but php-rct-smc01, operator), `pgrep -f` self-match in shells, nightly `pkill -9 php`, Run summary gates;
  with the verify.yml excerpt (local-knowledge-ansible `17a5803`, skill-smc `f13c22f`).
- `scripts/tstik-capture.sh`: capture 07 counts AVR reads, empty reads, AVR errors and `local.ERROR` per laravel.log file plus the top error kinds
  (smoke run warehouse-rct01 2026-10-26: 164,169 reads, 0 AVR errors, 308 network errors; ~90 s for the whole capture). Header: the cron
  frequency was written as every minute (arrkapa, 2026-10-07); root's crontab on warehouse-rct01, alice-well, cave-hill and adjamarragu runs
  `update:stats` every 5 minutes, so reset limits count runs. Catalogue row updated.
- manifest 0.7.7 -> 0.7.8.

## 20261026_1534 — smc_change backup.shared: name-identified backup files kept once for all SMCs (v0.7.6 -> v0.7.7)

- `references/19_smc-change-role.md`: Learned 2026-10-26 entry for spec field `backup.shared` (globs; matching backup files kept once per change on the
  controller under `runs/backups/shared/`, `shared.txt` per host, rollback copies them back; default per-SMC copies; name-only match, `paths.tgz`
  refused at spec load; dpkg-repack output differs per run so no checksum compare), with the cleanup.yml excerpt (local-knowledge-ansible `2ade781`);
  PHP spec example gains `shared: ['*.deb']`.
- manifest 0.7.6 -> 0.7.7.

## 20261026_1506 — smc_change flow map in parts, one E2E page per change spec (v0.7.5 -> v0.7.6)

- `references/19_smc-change-role.md`: the smc_change flow map is assembled from `roles/smc_change/drawio/parts/` (role parts) and each change
  folder's flow parts; each change spec gets its own `E2E: <change>` page explaining the change, its steps naming the stage (operator, 2026-10-26).
- `justfile`: `smc_change_flows` assembles `drawio/flows.yaml` from `drawio/parts/master.yaml` before rendering; `smc_change_flows_check` checks both.
- `references/19_smc-change-role.md`: one folder per change, `files/changes/<name>/` with the spec `<name>.yml`, its flow-map parts
  (`flow-components.yaml`, `flow-flows.yaml`) and `runs/` (records, `backups/`, `state/`; was `runs/<name>/`), `smc_change_runs_dir` (operator, 2026-10-26).

## 20261023_1737 — smc_change on an overlay Pi: close after restart, overlay_fallback, proves, soak_minutes; tstik bench note; identity probe hosts_name (v0.7.4 -> v0.7.5)

- `references/19_smc-change-role.md`: EBUSY on the first overlay apply (deleted-but-open inodes), lower dir now closed after stage 7, `reboot:
  overlay_fallback`, `verify.proves`, spec `soak_minutes`, `SMC_CHANGE_BACKUP` for command undo; proven on php-rct-smc01 (commits 01083c8, faf6866).
- `references/06_failure-modes.md`: tstik empty AVR reads mean nothing answers on ttyS0; the bench unit has no AVR; manual check commands.
- `references/08_ansible-authoring.md`: operator kept site ID 181 for php-rct-smc01. `justfile`: `smc_change_flows`, `smc_change_flows_check`.
- `scripts/pi_identity_probe.sh`: prints `hosts_name` (the 127.0.1.1 name in /etc/hosts) beside hostname and boot_hostname.

## 20261023_1625 — smc_inventory_add.py: add a new SMC to an inventory without guessing (v0.7.3 -> v0.7.4)

- `scripts/smc_inventory_add.py` + `just smc_inventory_add`: the three groups and three vars files for a new SMC, rendered from the repo's
  generator templates; plan by default, `--apply` writes; refuses an existing host/site/file; flags a shared site ID; `--siteid-from-box`.
  Proven on php-rct-smc01 (byte-identical to hand-made files, second apply refused, live box read). Operator, 2026-10-23.
- `references/08_ansible-authoring.md`: new section "Adding a new SMC to an inventory" (six pieces, site naming, generator caveat, standard rct
  interfaces, reading vars past the guard hook).
- `references/03_communication-flows.md`: site ID readable from the box's autossh -R port; generic image ID 181 is shared.
- `SKILL.md` decision tree: new point 6 for adding a box.

## 20261023_1536 — smc_change rollback mode and done-tracking; root linters for every language (v0.7.2 -> v0.7.3)

`19_smc-change-role.md`: rollback is a mode (per-type `<type>_rollback.yml`, controller or box backup, health plus restored gates);
per-host state in `runs/<spec>/state/` skips hosts already done, `smc_change_force` re-runs them. `18_local-knowledge-ansible.md`: one
root config per language (ruff, djlint, taplo, biome, shfmt/shellcheck via .editorconfig) and `lint_new.sh`. manifest 0.7.2 -> 0.7.3.

## 20261023_1455 — smc_change: generic role, probe split per check, cleanup, skip unreachable/refused, stages; ruff root config (v0.7.1 -> v0.7.2)

`19_smc-change-role.md` rewritten for the role as it now is: 11 announced stages, plan and result summaries worded by the probe, probe split
into `files/probe/NN_*.py` with a check registry (proven identical on four runs), only configured checks gated, stage 10 CLEANUP (nothing left
on the box after success, backups copied to the controller), records on the controller only, unreachable and refused hosts recorded and
skipped, run summary, rollback steps, ruff with two-space indent and `force-exclude` of the 22 existing files. manifest 0.7.1 -> 0.7.2.

## 20261023_1351 — backdoor-watch.sh resolves stage hosts; smc_change command guard (v0.7.0 -> v0.7.1)

`scripts/backdoor-watch.sh` matched only `*-smc0N` hosts in `inventories/*/prod`; it now takes any exact inventory host in prod or stage, then a site
name in prod then stage (operator, 2026-10-23). Tested: warehouse-rct01 (rct stage) 50484 UP while it is off Teleport; kupungarri and nocprov-smc01
unchanged. `19_smc-change-role.md`: a `command` action on an overlay box must set `chroot`. manifest 0.7.0 -> 0.7.1.

## 20261023_1339 — Local-knowledge folder reference and index script; PHP verification by mapped files; smc_change role recorded (v0.6.9 -> v0.7.0)

New `references/18_local-knowledge-ansible.md` (operator, 2026-10-23: the pack must stay across what is built in local-knowledge-ansible): layout,
symlink-plus-`.git/info/exclude` wiring, operator tooling (the new `smc_change` role, its PHP and php.ini specs, `smc_update_php.yml`), standing rule
to read it at the start of SMC work. New `references/19_smc-change-role.md` (operator: any project should be able to use smc_change): running it, spec format, gates, overlay
lower-dir persistence, run records, status; SKILL.md decision tree step 5 sends box changes to it. New read-only `scripts/local_knowledge_index.sh` (`just local_knowledge_index`, ~1 s). SKILL.md and RUNBOOK
point to both. `13_known-issues.md`: installed package version is not running code (warehouse-smc01 apache on a deleted libphp after
unattended-upgrades); rct has no `topology_interfaces`, read the portal from `apache2ctl -S`; Ansible `environment:` makes `pgrep -f` match the
probe's own shell. manifest 0.6.9 -> 0.7.0.

## 20261022_1718 — Evidence capture: timeouts reported as such, full-capture timing, end-marker fix (v0.6.8 -> v0.6.9)

Side note (the 300 s default was timed only on a voip run): full captures measured 86 s (bidyadanga, Sky Muster) and 93–97 s (kalumburu); default kept
with about 3x headroom. `with_deadline` returns 124 when its deadline is reached (tsh traps TERM and exits 1); `collect-smc-evidence-full.sh` prints
`SESSION TIMED OUT` and counts unreached captures as "not run" (live check with a 5 s limit). That count exposed a defect: output without a trailing
newline glued the RC marker to its last line, so `network/interfacecheck-script` was never closed or counted; the marker now starts on its own line
(kalumburu 145 of 145, other captures unchanged). `just test-deadline` gains a TERM-trapping case (12 checks). manifest 0.6.8 -> 0.6.9.

## 20261022_1703 — Evidence scripts: a deadline on every tsh call, with an offline test (v0.6.7 -> v0.6.8)

`scripts/collect-smc-evidence-full.sh` and `scripts/collect-smc-evidence.sh` call `tsh ssh` through `with_deadline` (the watcher from
`overlay-usage-breakdown.sh`, plus `<&0` so piped stdin survives when job control is on): probe 60 s, session 300 s, narrow per command 60 s, all
overridable. New `scripts/test_with_deadline.sh` (`just test-deadline`, offline): passes, and fails when the kill is disabled. Smoke run on kalumburu-smc01:
73 s, 11 of 11 voip captures. Known issue 2026-10-22 resolved. manifest 0.6.7 -> 0.6.8.

## 20261022_1653 — Asterisk memory measured on the rcp fleet; umoona still without Asterisk; evidence script lacks a tsh deadline (v0.6.6 -> v0.6.7)

Operator approved the read-only voip capture on all 17 rcp boxes (enterprise-strategy RouterOS study, 58 s): Asterisk 77–153 MB resident, about 100 MB
typical (`references/07_hardware-overlay.md`). `references/13_known-issues.md`: umoona-smc01 still has no Asterisk process (as on 2026-08-25), nocprov none;
`collect-smc-evidence-full.sh` has no per-call `tsh` deadline (run wrapped in a perl alarm). manifest 0.6.6 -> 0.6.7.
Corrected the same day (operator): umoona has no active SIP clients, so its missing Asterisk is known and not an outage.

## 20261022_1623 — collect-smc-evidence-full.sh voip group records Asterisk resident memory (v0.6.5 -> v0.6.6)

New capture `voip|asterisk-rss` (`ps -C asterisk -o pid=,rss=,vsz=,etime=,args=`): Prometheus has no process metrics, so this is the only per-process
sizing source; enterprise-strategy's RouterOS study needs it to size a containerised Asterisk. `bash -n` passes; not yet run on a box (the session's
fleet probe was denied by auto mode). Catalogued in `scripts/README.md`. manifest 0.6.5 -> 0.6.6.

Incident: commit df32f48 was made while `just check` failed (CHANGELOG 201 lines, over budget): the command piped the check into `tail`, so its exit
code did not gate the commit. Fixed in the next commit by rotating the CHANGELOG; the check passes.
