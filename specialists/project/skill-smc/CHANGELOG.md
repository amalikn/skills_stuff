---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261026_1534
---

# skill-smc Changelog

## Contents

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
- [20261022_1621 — rcp Asterisk dialplan summarised; x86 fleet by model with its 7-day load (v0.6.4 -> v0.6.5)](#20261022_1621--rcp-asterisk-dialplan-summarised-x86-fleet-by-model-with-its-7-day-load-v064---v065)
- [20261022_1506 — Firmware access from the OS: UEFI and EEPROM lines in the x86 and Pi probes, deadlines (v0.6.3 -> v0.6.4)](#20261022_1506--firmware-access-from-the-os-uefi-and-eeprom-lines-in-the-x86-and-pi-probes-deadlines-v063---v064)
- [20261022_1426 — What WAN-side equipment tells an SMC about its site: Starlink position, Sky Muster NTD nothing (v0.6.2 -> v0.6.3)](#20261022_1426--what-wan-side-equipment-tells-an-smc-about-its-site-starlink-position-sky-muster-ntd-nothing-v062---v063)
- [20261022_1226 — backdoor_exec.sh passes a stdin script through (v0.6.1 -> v0.6.2)](#20261022_1226--backdoor_execsh-passes-a-stdin-script-through-v061---v062)
- [20261022_1200 — PHP CVE fleet status, extra PHP processes, backdoor hostname check, nbn_wh read rule (v0.6.0 -> v0.6.1)](#20261022_1200--php-cve-fleet-status-extra-php-processes-backdoor-hostname-check-nbn_wh-read-rule-v060---v061)
- [20261020_2028 — Sky Muster reads: session set-up and the concurrency curve (v0.5.9 -> v0.6.0)](#20261020_2028--sky-muster-reads-session-set-up-and-the-concurrency-curve-v059---v060)
- [20261020_1905 — networkd keeps changed netdevs; render with the task's options; /etc executables; fleet-health TSH_PROXY and fqdn2ip bundle (v0.5.8 -> v0.5.9)](#20261020_1905--networkd-keeps-changed-netdevs-render-with-the-tasks-options-etc-executables-fleet-health-tsh_proxy-and-fqdn2ip-bundle-v058---v059)
- [20261020_1752 — Pi uplink on the eth0 trunk; ssh forwards detach from the caller; Sky Muster read cost (v0.5.7 -> v0.5.8)](#20261020_1752--pi-uplink-on-the-eth0-trunk-ssh-forwards-detach-from-the-caller-sky-muster-read-cost-v057---v058)
- [20261020_1706 — /etc census in overlay-usage-breakdown; fqdn2ip still on darlngunaya (v0.5.6 -> v0.5.7)](#20261020_1706--etc-census-in-overlay-usage-breakdown-fqdn2ip-still-on-darlngunaya-v056---v057)
- [20261020_1647 — Run-time writers under /etc; read-only /etc on the new image (v0.5.5 -> v0.5.6)](#20261020_1647--run-time-writers-under-etc-read-only-etc-on-the-new-image-v055---v056)

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

## 20261022_1621 — rcp Asterisk dialplan summarised; x86 fleet by model with its 7-day load (v0.6.4 -> v0.6.5)

From enterprise-strategy's RouterOS future study (operator answers 20261022_1535). `references/02_service-map.md` VoIP: what the rcp dialplan does
(trunk to PBX0008, 4-digit extensions, DID or prompt inbound, barring, caller ID, 8888), with a code excerpt (ansible-wifi 35b32c36); the section is rcp
only, not "non-RCT". `references/07_hardware-overlay.md`: whole x86 fleet by model (28 BOXER-6404, 19 BOXER-6641, cores 4 and 6) with 7-day CPU and RAM
from Prometheus; no process metrics exist; anomalies (koonibba 98% root, warehouse 3 GB RAM, three boxes missing from Prometheus). manifest 0.6.4 -> 0.6.5.

## 20261022_1506 — Firmware access from the OS: UEFI and EEPROM lines in the x86 and Pi probes, deadlines (v0.6.3 -> v0.6.4)

`scripts/x86_resiliency_probe.sh` and `scripts/pi_identity_probe.sh`: UEFI and EEPROM lines; a deadline on every `tsh` call (`--deadline`, default
90 s; they had none) and stdin closed. `references/07_hardware-overlay.md` "Firmware access from the OS": all 47 x86 SMCs (two models, five BIOS
builds, ESRT on the BOXER-6404 only, Secure Boot off with no keys) and six Pi canaries (EEPROM 2023-01-11, minimal config, bundled image older).
Run for smc-resiliency's warehouse and retrofit flows.

## 20261022_1426 — What WAN-side equipment tells an SMC about its site: Starlink position, Sky Muster NTD nothing (v0.6.2 -> v0.6.3)

`references/03_communication-flows.md`: a Starlink dish gives latitude, longitude and altitude on its local gRPC interface (192.168.100.1:9200,
`get_location`) only when "allow access on local network" is on in the Starlink app (community tools, `VERIFIED_SECONDARY`, unofficial, untested on
the fleet); the Enterprise Telemetry API is behind account-manager access; the Sky Muster NTD has no documented local status page or API (negative
finding). Researched for smc-resiliency's site fingerprint (decision 20261022_1426).

## 20261022_1226 — backdoor_exec.sh passes a stdin script through (v0.6.1 -> v0.6.2)

`scripts/backdoor_exec.sh`: the `tsh` inside `backdoor-watch.sh` and `kp` read stdin, so a script given with `-` was eaten before it reached the box (rc 0,
no output). Every helper now runs with `</dev/null`. Retested 2026-10-22: goojarr-goonyool and mount-peachy (rct, Teleport down) probed through the backdoor.

## 20261022_1200 — PHP CVE fleet status, extra PHP processes, backdoor hostname check, nbn_wh read rule (v0.6.0 -> v0.6.1)

From the ansible-wifi PHP CVE-2026-109618/109619 assessment. `references/10_captive-portal.md`: PHP security status (Ubuntu fixed build
`8.1.2-1ubuntu2.28`, USN-8948-1; mod_php fleet-wide; builds drift, Pis included) and the other PHP processes to restart (rct-tstik
`php -S 10.254.0.1:8080` as root from cron; `apn-mqtt-client`). `references/07_hardware-overlay.md`: what "don't touch nbn_wh" means (no
changes; reads always allowed; operator, 2026-10-22). `references/03_communication-flows.md` Learned 2026-10-22: a backdoor port can answer
as another box (50501 = nocprov-smc01); nbn_wh Teleport running but no tunnel. `references/13_known-issues.md` Learned (f): dual-inventory
hosts, CRLF host_vars, no self-patching. New scripts `php_package_probe.sh` and `backdoor_exec.sh` (recipes, catalogue, smoke-tested);
`backdoor-watch.sh` strips `\r` from a CRLF siteid.

## 20261020_2028 — Sky Muster reads: session set-up and the concurrency curve (v0.5.9 -> v0.6.0)

`references/13_known-issues.md` Learned (e): a fresh Teleport session to a Sky Muster SMC 7 to 8 s against 0.01 s on a shared connection;
8.3, 5.8 and 4.3 s per unit at 4, 8 and 12 in flight (unified-network-controller satellite concurrency report).

## 20261020_1905 — networkd keeps changed netdevs; render with the task's options; /etc executables; fleet-health TSH_PROXY and fqdn2ip bundle (v0.5.8 -> v0.5.9)

From smc-resiliency's S2 spike and slurp. `references/06_failure-modes.md`: a netplan change to a VLAN, bond or bridge takes effect only at reboot
(networkctl(1)). `references/08_ansible-authoring.md`: rendering a role template outside the role. `references/07_hardware-overlay.md`: executables
under /etc, Unbound's stub and keys on the new image. `scripts/collect-fleet-health.sh`: `TSH_PROXY` (it used only the active profile, so every CW
capture failed) and a read-only `06-fqdn2ip-state` bundle (smoke: darlngunaya, all six ok). `scripts/overlay-usage-breakdown.sh --etc`: executables list.

## 20261020_1752 — Pi uplink on the eth0 trunk; ssh forwards detach from the caller; Sky Muster read cost (v0.5.7 -> v0.5.8)

`references/03_communication-flows.md`: Learned (b) a Pi's uplink Circuit sits on `eth0` (named interface, NTD on the switch), (c) `ssh` leaves
its `tsh proxy` child on a kill and `ssh -f` forwards leave the caller's session, so they are closed by name (confirms the 20261020_1141
lingering-proxy note). `references/13_known-issues.md`: Learned (d) about 40 to 50 s per unit read over Sky Muster Plus (unified-network-controller).

## 20261020_1706 — /etc census in overlay-usage-breakdown; fqdn2ip still on darlngunaya (v0.5.6 -> v0.5.7)

`scripts/overlay-usage-breakdown.sh` gains `--etc` (the `/etc` census, true uptime) and a per-host deadline (`HOST_DEADLINE`, 60 s; a perl alarm
before exec did not stop `tsh`, so a watcher sends TERM then KILL; proved with a 3 s limit). `references/07_hardware-overlay.md`: census of six
long-up boxes. `references/13_known-issues.md`: fqdn2ip still active on darlngunaya-smc01 (nbn_wh), removed on bungardi; to look at later.

## 20261020_1647 — Run-time writers under /etc; read-only /etc on the new image (v0.5.5 -> v0.5.6)

Learned 2026-10-20 in `references/07_hardware-overlay.md` (new section): the four run-time writers under `/etc` (teleport-tags-exporter,
fake-hwclock, squid blocklists, multipathd) with x86 daily counts, and that a merged confext on systemd 255 makes `/etc` read-only and noexec.
From smc-resiliency's S2 R2 work.
