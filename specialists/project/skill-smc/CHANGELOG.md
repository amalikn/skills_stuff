---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261119_1158
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

## Contents

- [20261119_1205 — early watchdog fed by the kernel driver from its probe; EEPROM update from partition 1 on both 2022 bootloaders; census reads memory (v0.15.1 -> v0.15.2)](#20261119_1205--early-watchdog-fed-by-the-kernel-driver-from-its-probe-eeprom-update-from-partition-1-on-both-2022-bootloaders-census-reads-memory-v0151---v0152)
- [20261118_2152 — Pi 4 early watchdog, 2022 bootloaders ignore the A/B selector, EEPROM staging on an A/B card (v0.15.0 -> v0.15.1)](#20261118_2152--pi-4-early-watchdog-2022-bootloaders-ignore-the-ab-selector-eeprom-staging-on-an-ab-card-v0150---v0151)
- [20261118_2049 — storage identity readable on x86 and Pi; low-touch description record (name, locid) (v0.14.9 -> v0.15.0)](#20261118_2049--storage-identity-readable-on-x86-and-pi-low-touch-description-record-name-locid-v0149---v0150)
- [20261118_1553 — rct tstik board restarts a stuck SMC (operator); wh flavours have none (v0.14.8 -> v0.14.9)](#20261118_1553--rct-tstik-board-restarts-a-stuck-smc-operator-wh-flavours-have-none-v0148---v0149)
- [20261117_1922 — smc_change: state-file timing; connect timeout 30 s; offline SMCs fail INCOMPLETE; ssh_handshake_time.sh (v0.14.7 -> v0.14.8)](#20261117_1922--smc_change-state-file-timing-connect-timeout-30-s-offline-smcs-fail-incomplete-ssh_handshake_timesh-v0147---v0148)
- [20261117_1857 — smc_change_multiple: never pass -e smc_change; vars guard blocks edits; delta gate on rewritten files (v0.14.6 -> v0.14.7)](#20261117_1857--smc_change_multiple-never-pass--e-smc_change-vars-guard-blocks-edits-delta-gate-on-rewritten-files-v0146---v0147)
- [20261117_1044 — Teleport self-upgrade cron on every flavour (v0.14.5 -> v0.14.6)](#20261117_1044--teleport-self-upgrade-cron-on-every-flavour-v0145---v0146)
- [20261116_1859 — Solutions to platforms (no version change)](#20261116_1859--solutions-to-platforms-no-version-change)
- [20261116_1736 — fleet facts for a remote conversion: boot partition free, root label, x86 disk layouts (v0.14.4 -> v0.14.5)](#20261116_1736--fleet-facts-for-a-remote-conversion-boot-partition-free-root-label-x86-disk-layouts-v0144---v0145)
- [20261111_1318 — smc_lynis NO_PUBKEY 7A9A1D9D5B27C6D3 and apt_key_subkey_probe.sh (v0.14.3 -> v0.14.4)](#20261111_1318--smc_lynis-no_pubkey-7a9a1d9d5b27c6d3-and-apt_key_subkey_probesh-v0143---v0144)
- [20261111_1213 — urlcapture-prune: galiwinku checked (v0.14.2 -> v0.14.3)](#20261111_1213--urlcapture-prune-galiwinku-checked-v0142---v0143)
- [20261111_1105 — urlcapture-prune first run read; uc-old-files needs the cw proxy (v0.14.1 -> v0.14.2)](#20261111_1105--urlcapture-prune-first-run-read-uc-old-files-needs-the-cw-proxy-v0141---v0142)
- [20261110_1355 — koonibba: wrong Teleport cluster, stale bastion keys, url_capture prune gaps, root-LV condition, urlcapture-prune change (v0.14.0 -> v0.14.1)](#20261110_1355--koonibba-wrong-teleport-cluster-stale-bastion-keys-url_capture-prune-gaps-root-lv-condition-urlcapture-prune-change-v0140---v0141)
- [20261110_1225 — Fleet survey probes, bootloader census, writers probe; probe deadlines fixed (v0.13.2 -> v0.14.0)](#20261110_1225--fleet-survey-probes-bootloader-census-writers-probe-probe-deadlines-fixed-v0132---v0140)
- [20261110_0202 — Deployed Pi fleet layout and root block spread (survey of 6) (v0.13.1 -> v0.13.2)](#20261110_0202--deployed-pi-fleet-layout-and-root-block-spread-survey-of-6-v0131---v0132)
- [20261110_0031 — Pi 4 on the fleet bootloader 2023-01-11: autoboot.txt on GPT and EEPROM update path (v0.13.0 -> v0.13.1)](#20261110_0031--pi-4-on-the-fleet-bootloader-2023-01-11-autoboottxt-on-gpt-and-eeprom-update-path-v0130---v0131)
- [20261109_2300 — Pi 4 A/B on a GPT card: bootloader, firmware and update traps (smc-resiliency S1) (v0.12.9 -> v0.13.0)](#20261109_2300--pi-4-ab-on-a-gpt-card-bootloader-firmware-and-update-traps-smc-resiliency-s1-v0129---v0130)
- [20261108_0155 — Pi 4 serial console (smc-resiliency S1 bench) (v0.12.8 -> v0.12.9)](#20261108_0155--pi-4-serial-console-smc-resiliency-s1-bench-v0128---v0129)
- [20261106_1630 — ansible-wifi smc_bases on Ubuntu 24.04 and in an image build (v0.12.7 -> v0.12.8)](#20261106_1630--ansible-wifi-smc_bases-on-ubuntu-2404-and-in-an-image-build-v0127---v0128)
- [20261106_1605 — Parallels linked clone shares the source's address; Parallels lab behaviour (v0.12.6 -> v0.12.7)](#20261106_1605--parallels-linked-clone-shares-the-sources-address-parallels-lab-behaviour-v0126---v0127)

- [20261118_1553 — rct tstik board restarts a stuck SMC (operator); wh flavours have none (v0.14.8 ->
  v0.14.9)](#20261118_1553--rct-tstik-board-restarts-a-stuck-smc-operator-wh-flavours-have-none-v0148---v0149)
- [20261117_1922 — smc_change: state-file timing; connect timeout 30 s; offline SMCs fail INCOMPLETE; ssh_handshake_time.sh (v0.14.7 ->
  v0.14.8)](#20261117_1922--smc_change-state-file-timing-connect-timeout-30-s-offline-smcs-fail-incomplete-ssh_handshake_timesh-v0147---v0148)
- [20261117_1857 — smc_change_multiple: never pass -e smc_change; vars guard blocks edits; delta gate on rewritten files (v0.14.6 ->
  v0.14.7)](#20261117_1857--smc_change_multiple-never-pass--e-smc_change-vars-guard-blocks-edits-delta-gate-on-rewritten-files-v0146---v0147)
- [20261117_1044 — Teleport self-upgrade cron on every flavour (v0.14.5 -> v0.14.6)](#20261117_1044--teleport-self-upgrade-cron-on-every-flavour-v0145---v0146)
- [20261116_1859 — Solutions to platforms (no version change)](#20261116_1859--solutions-to-platforms-no-version-change)
- [20261116_1736 — fleet facts for a remote conversion: boot partition free, root label, x86 disk layouts (v0.14.4 ->
  v0.14.5)](#20261116_1736--fleet-facts-for-a-remote-conversion-boot-partition-free-root-label-x86-disk-layouts-v0144---v0145)
- [20261111_1318 — smc_lynis NO_PUBKEY 7A9A1D9D5B27C6D3 and apt_key_subkey_probe.sh (v0.14.3 -> v0.14.4)](#20261111_1318--smc_lynis-no_pubkey-7a9a1d9d5b27c6d3-and-apt_key_subkey_probesh-v0143---v0144)
- [20261111_1213 — urlcapture-prune: galiwinku checked (v0.14.2 -> v0.14.3)](#20261111_1213--urlcapture-prune-galiwinku-checked-v0142---v0143)
- [20261111_1105 — urlcapture-prune first run read; uc-old-files needs the cw proxy (v0.14.1 -> v0.14.2)](#20261111_1105--urlcapture-prune-first-run-read-uc-old-files-needs-the-cw-proxy-v0141---v0142)
- [20261110_1355 — koonibba: wrong Teleport cluster, stale bastion keys, url_capture prune gaps, root-LV condition, urlcapture-prune change (v0.14.0 ->
  v0.14.1)](#20261110_1355--koonibba-wrong-teleport-cluster-stale-bastion-keys-url_capture-prune-gaps-root-lv-condition-urlcapture-prune-change-v0140---v0141)
- [20261110_1225 — Fleet survey probes, bootloader census, writers probe; probe deadlines fixed (v0.13.2 ->
  v0.14.0)](#20261110_1225--fleet-survey-probes-bootloader-census-writers-probe-probe-deadlines-fixed-v0132---v0140)
- [20261110_0202 — Deployed Pi fleet layout and root block spread (survey of 6) (v0.13.1 -> v0.13.2)](#20261110_0202--deployed-pi-fleet-layout-and-root-block-spread-survey-of-6-v0131---v0132)
- [20261110_0031 — Pi 4 on the fleet bootloader 2023-01-11: autoboot.txt on GPT and EEPROM update path (v0.13.0 ->
  v0.13.1)](#20261110_0031--pi-4-on-the-fleet-bootloader-2023-01-11-autoboottxt-on-gpt-and-eeprom-update-path-v0130---v0131)
- [20261109_2300 — Pi 4 A/B on a GPT card: bootloader, firmware and update traps (smc-resiliency S1) (v0.12.9 ->
  v0.13.0)](#20261109_2300--pi-4-ab-on-a-gpt-card-bootloader-firmware-and-update-traps-smc-resiliency-s1-v0129---v0130)
- [20261108_0155 — Pi 4 serial console (smc-resiliency S1 bench) (v0.12.8 -> v0.12.9)](#20261108_0155--pi-4-serial-console-smc-resiliency-s1-bench-v0128---v0129)
- [20261106_1630 — ansible-wifi smc_bases on Ubuntu 24.04 and in an image build (v0.12.7 -> v0.12.8)](#20261106_1630--ansible-wifi-smc_bases-on-ubuntu-2404-and-in-an-image-build-v0127---v0128)
- [20261106_1605 — Parallels linked clone shares the source's address; Parallels lab behaviour (v0.12.6 ->
  v0.12.7)](#20261106_1605--parallels-linked-clone-shares-the-sources-address-parallels-lab-behaviour-v0126---v0127)
- [20261106_1545 — smc_change export to a company task file; tracker orders resumed runs by attempt (v0.12.5 ->
  v0.12.6)](#20261106_1545--smc_change-export-to-a-company-task-file-tracker-orders-resumed-runs-by-attempt-v0125---v0126)
- [20261106_1300 — WAN routing confirmed live; link health per leg; Grafana tunnel; measured link figures (v0.12.4 ->
  v0.12.5)](#20261106_1300--wan-routing-confirmed-live-link-health-per-leg-grafana-tunnel-measured-link-figures-v0124---v0125)
- [20261106_1029 — Pi clock with no RTC on Ubuntu 24.04 measured (v0.12.3 -> v0.12.4)](#20261106_1029--pi-clock-with-no-rtc-on-ubuntu-2404-measured-v0123---v0124)
- [20261105_1758 — URL capture DNS mechanism measured; records plan proposed (v0.12.2 -> v0.12.3)](#20261105_1758--url-capture-dns-mechanism-measured-records-plan-proposed-v0122---v0123)
- [20261105_1634 — v8 resumable PCAP fetch, EFS find, Teleport path loss probe (v0.12.1 -> v0.12.2)](#20261105_1634--v8-resumable-pcap-fetch-efs-find-teleport-path-loss-probe-v0121---v0122)
- [20261105_1155 — smc_change Teleport login gate (v0.12.0 -> v0.12.1)](#20261105_1155--smc_change-teleport-login-gate-v0120---v0121)
- [20261104_2130 — Iridium batches 1-3 marked; rise deploy flashes; smc_mark_iridium.py (v0.11.9 ->
  v0.12.0)](#20261104_2130--iridium-batches-1-3-marked-rise-deploy-flashes-smc_mark_iridiumpy-v0119---v0120)
- [20261104_1900 — smc_change self-repair, every-goal success rule, applies_when (v0.11.8 -> v0.11.9)](#20261104_1900--smc_change-self-repair-every-goal-success-rule-applies_when-v0118---v0119)
- [20261104_1600 — smc_change chaining, per-change state, named value files (v0.11.7 -> v0.11.8)](#20261104_1600--smc_change-chaining-per-change-state-named-value-files-v0117---v0118)
- [20261102_1756 — smc_change skip, probe or force; per-SMC close (v0.11.6 -> v0.11.7)](#20261102_1756--smc_change-skip-probe-or-force-per-smc-close-v0116---v0117)

---

## 20261119_1205 — early watchdog fed by the kernel driver from its probe; EEPROM update from partition 1 on both 2022 bootloaders; census reads memory (v0.15.1 -> v0.15.2)

- references/07_hardware-overlay.md: Learned 2026-11-19 (VERIFIED_PRIMARY, bench Pi 4): a slow healthy boot (systemd 30 s late) is not reset by the early watchdog, the kernel driver
  feeds it from about 5 s after the arm; broken trial kernel reset alone with the overlay; partition-1 EEPROM staging works from 2022-04-26 and 2022-01-25, files left on p1.
- scripts/fleet/pi_bootloader_census.sh prints `mem_kb`; summarise_survey.py census tallies memory per flavour (test added). Not yet run on the fleet: Teleport certificate expired.
- From the smc-resiliency bench run of 2026-11-19 (lab test record section 25).

## 20261118_2152 — Pi 4 early watchdog, 2022 bootloaders ignore the A/B selector, EEPROM staging on an A/B card (v0.15.0 -> v0.15.1)

- references/07_hardware-overlay.md: Learned 2026-11-18 (VERIFIED_PRIMARY, bench Pi 4): an unstartable kernel freezes the Pi; the firmware arms the watchdog early only with the
  `early-watchdog` device-tree property, which Ubuntu's tree lacks (overlay given, 17 s reset measured); bootloaders 2022-04-26 and 2022-01-25 ignore `[tryboot]` and `tryboot_a_b`;
  where `rpi-eeprom-update` must stage an update for a bootloader without self-update, and the clean-up after.
- From the smc-resiliency bench run of 2026-11-18 (lab test record section 24).

## 20261118_2049 — storage identity readable on x86 and Pi; low-touch description record (name, locid) (v0.14.9 -> v0.15.0)

- references/07_hardware-overlay.md: Learned 2026-11-18 (VERIFIED_PRIMARY, two boxes): CFast model, serial and world-wide ID through `lsblk` and sysfs on x86; SD card ID, maker, date and serial
  in sysfs on a Pi; `smartctl` present on both; no package needed.
- references/02_service-map.md: Learned 2026-11-18 (VERIFIED_PRIMARY, one low-touch box): the per-unit description record in `/var/local/cnmaestro-provisioning/log.<MAC>` (`name`, `locid` from
  redis `next_locid`, `lot no`, `us`); the management address ends in `locid`; `name` is the RPZ record.
- From the unified-network-controller asset custody (D17) session of 2026-11-18, read-only reads on the operator's instruction.

## 20261118_1553 — rct tstik board restarts a stuck SMC (operator); wh flavours have none (v0.14.8 -> v0.14.9)

- references/06_failure-modes.md: Learned 2026-11-18 (USER_STATED): the tstik is a physical board wired to the Pi and restarts a stuck rct SMC by rules such as loss of the internet; the SMC restart
  sits in the board's AVR firmware, outside the rct-tstik app read on 2026-10-07, so that reading stands. The wh flavours (wh, nbn_wh) have no such board and no automatic restart.
- From the apn smc-resiliency concept deck session (6128bdd9), where the operator corrected a slide that said nothing restarts any hung SMC.

## 20261117_1922 — smc_change: state-file timing; connect timeout 30 s; offline SMCs fail INCOMPLETE; ssh_handshake_time.sh (v0.14.7 -> v0.14.8)

`references/19_smc-change-role.md` (smc_change_multiple bullets): a change's state file is written per SMC at its stage 11 under strategy free, never in check mode, and the SMSC play waits for the
whole AVR play; "banner exchange" timeouts are the ssh plugin's 10 s default against a ~9 s Teleport handshake, now `ansible_ssh_timeout: 30` in both smc_change playbooks (ansible-wifi chat f516e57d).

New read-only `scripts/access/ssh_handshake_time.sh` (`just ssh_handshake_time`, offline test `just test_ssh_handshake_time`, smoke-run on wujal-wujal-booth-smc01, catalogued in
`scripts/README.md`); reference 19: any SMC a run did not finish (offline, no record, unreachable, refused, failed, held back) is noted and fails INCOMPLETE, in the wrapper's last play when `smc_change_defer_incomplete` is set (operator; side-agent note on later plays).

## 20261117_1857 — smc_change_multiple: never pass -e smc_change; vars guard blocks edits; delta gate on rewritten files (v0.14.6 -> v0.14.7)

`references/19_smc-change-role.md` (smc_change_multiple bullets): `-e smc_change=<spec>` outranks each import's play var, so both imports ran rct-avr-smsc and the AVR flash never ran (23-SMC batch,
2026-11-17: 4 passed, 6 failed on AVR 2.14, 13 never started); what `6/11 ACTIONS` means and why the AVR version check fails instead of skipping. `references/13_known-issues.md`: the vars guard also
blocks non-printing edits of inventory host files (use `just smc_mark_iridium`); the lint delta gate brings old findings of a rewritten file in as new; pipefail needs bash (ansible-wifi chat
f516e57d).

## 20261117_1044 — Teleport self-upgrade cron on every flavour (v0.14.5 -> v0.14.6)

`references/03_communication-flows.md` "Teleport self-upgrade cron": `/upgrade_teleport.sh` daily at 00:00 on all flavours (ansible-wifi 906ee778), and why an image-based root drops it; cross-link to
the C6 `pkill -9 python3` entry (from apn smc-resiliency scheduled-writer inventory, 17 Nov 2026).

## 20261116_1859 — Solutions to platforms (no version change)

`references/01_overview.md` section 2: the Raspberry Pi solution covers the `rct` booths and the Wi-Fi hubs (`wh`, `nbn_wh`); Community Wi-Fi sites are all x86 (`rcp`, `nbn_accelerate`); management
material says "recover themselves" for SMC recovery (operator, 16 Nov 2026; from apn enterprise-strategy).

## 20261116_1736 — fleet facts for a remote conversion: boot partition free, root label, x86 disk layouts (v0.14.4 -> v0.14.5)

`references/07_hardware-overlay.md` Learned 2026-11-16, from the 2026-11-10 survey raw output re-read by smc-resiliency: Pi p1 free (rct and wh 138 to 140 MB, nbn_wh 116 and 26 MB),
`root=LABEL=writable` on all 41 Pis read, BOXER-6404 one-disk LVM with no free extents, BOXER-6641 two disks with the standby install.

## 20261111_1318 — smc_lynis NO_PUBKEY 7A9A1D9D5B27C6D3 and apt_key_subkey_probe.sh (v0.14.3 -> v0.14.4)

`references/06_failure-modes.md` (`ec58b08`): cisofy's 2025-10-22 signing subkey; `apt_key` with `url` alone does not import it on SMCs holding the older key, so the role pins the subkey `id`
(ansible-wifi master `9d504a89`, rise `c4d2ef51`). New read-only `scripts/probes/apt_key_subkey_probe.sh` (recipes `apt_key_subkey_probe`, `apt_key_subkey_probe_test`), smoke-run on
kaltjiti-fergon-smc01.

## 20261111_1213 — urlcapture-prune: galiwinku checked (v0.14.2 -> v0.14.3)

`references/19_smc-change-role.md`: galiwinku's check result; the applies wait for the operator.

## 20261111_1105 — urlcapture-prune first run read; uc-old-files needs the cw proxy (v0.14.1 -> v0.14.2)

`references/19_smc-change-role.md`: Learned 2026-11-11, the canary's first cron prune (13 GB to two months, root 49% to 26%) and `tsh_each.sh`'s apn-cluster default
(`PROXY=teleport.communitywifi.net.au` for nbn_accelerate boxes); the read recipe is `uc-old-files` (was `months`, `590716b`).

## 20261110_1355 — koonibba: wrong Teleport cluster, stale bastion keys, url_capture prune gaps, root-LV condition, urlcapture-prune change (v0.14.0 -> v0.14.1)

`references/01_overview.md`: a box missing from plain `tsh ls` is not offline (the cluster comes from the profile; nbn_accelerate is on communitywifi). `references/03_communication-flows.md`: Learned
2026-11-10, a changed bastion key disables the backdoor's forwarding under `StrictHostKeyChecking=no`; verified fix and fleet sweep; `backdoor-watch.sh` misses a site ID kept in group vars (fix
pending). `references/09_url-capture-pcap.md`: the on-box prune, three boxes without it, server check before deleting (`da4a328`). `references/13_known-issues.md`: `smc_system` root-LV condition
(ansible-wifi `0fc086ca`) and the `smc_bases.yml --tags` always-task hazard (`da4a328`). `references/19_smc-change-role.md`: change `urlcapture-prune`, the first template action (`14eabeb`).

## 20261110_1225 — Fleet survey probes, bootloader census, writers probe; probe deadlines fixed (v0.13.2 -> v0.14.0)

New: `scripts/probes/pi_resiliency_probe.sh`, `scripts/probes/smc_writers_probe.sh`, `scripts/fleet/sample_fleet.py`, `scripts/fleet/summarise_survey.py`, `scripts/fleet/pi_bootloader_census.sh`
(catalogued, recipes in the justfile). `x86_resiliency_probe.sh` also prints OS, partitions, I/O since boot and SMART. Fix: the `perl alarm; exec tsh` deadline in four probes never cut a hung tsh (Go
survives SIGALRM); they now fork and send TERM then KILL. `references/07_hardware-overlay.md`: Learned 2026-11-10: bootloader census, nbn_wh writable root, undervoltage, x86 watchdog and write rates.

## 20261110_0202 — Deployed Pi fleet layout and root block spread (survey of 6) (v0.13.1 -> v0.13.2)

`references/07_hardware-overlay.md`: Learned 2026-11-10: 22.04.1, MBR 62 GB, overlayroot, 5.6-6.9 GB used, bootloader 2023-01-11, and how far the ext4 root's blocks spread (read-only, Teleport).

## 20261110_0031 — Pi 4 on the fleet bootloader 2023-01-11: autoboot.txt on GPT and EEPROM update path (v0.13.0 -> v0.13.1)

`references/07_hardware-overlay.md`: Learned 2026-11-10: 2023-01-11 reads autoboot.txt on GPT and runs the full tryboot chain; an EEPROM update staged on the selected boot partition is applied; where
the 2023 image is (VERIFIED_PRIMARY, bench console).

## 20261109_2300 — Pi 4 A/B on a GPT card: bootloader, firmware and update traps (smc-resiliency S1) (v0.12.9 -> v0.13.0)

`references/07_hardware-overlay.md`: Learned 2026-11-09: autoboot.txt and tryboot on GPT (bootloader 2026-01-09), Ubuntu 24.04.5 start4.elf cannot boot partition 2 (firmware 1.20260915 can),
flash-kernel copies it back, rpi-eeprom-update auto-upgrades, vcgencmd exits 0 without root, PARTITION_WALK stops at 8, the watchdog only after systemd, a NoCloud seed per root (VERIFIED_PRIMARY,
bench console).

## 20261108_0155 — Pi 4 serial console (smc-resiliency S1 bench) (v0.12.8 -> v0.12.9)

`references/07_hardware-overlay.md`: Learned 2026-11-08: the primary UART pins, `BOOT_UART`, `uart_2ndstage`, `enable_uart` with `console=serial0`, and the lab's console recorder (Raspberry Pi
documentation, VERIFIED_PRIMARY).

## 20261106_1630 — ansible-wifi smc_bases on Ubuntu 24.04 and in an image build (v0.12.7 -> v0.12.8)

`references/08_ansible-authoring.md`: Learned 2026-11-06 (smc-resiliency S3 step 8): python3.10 pin, netaddr and ansible.posix on the controller, `smc_setup` sources.list, `smc_sshd` service name and
60 x 60 s retries, `smc_network` reboot and netplan. manifest 0.12.7 -> 0.12.8.

## 20261106_1605 — Parallels linked clone shares the source's address; Parallels lab behaviour (v0.12.6 -> v0.12.7)

`references/11_vagrant-lab.md` 12.7: Learned 2026-11-06 (smc-resiliency SM clone): a linked clone keeps the machine-id, so DHCP hands it the source's address and `vagrant ssh <source>` silently
reaches the clone; clone only a stopped VM; `prlctl exec` ends what it started and has no shell; a restart turns NIC offloads back on. manifest 0.12.6 -> 0.12.7.
