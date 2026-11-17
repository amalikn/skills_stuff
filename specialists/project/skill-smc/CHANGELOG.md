---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261117_1859
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

## Contents

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
- [20261106_1545 — smc_change export to a company task file; tracker orders resumed runs by attempt (v0.12.5 -> v0.12.6)](#20261106_1545--smc_change-export-to-a-company-task-file-tracker-orders-resumed-runs-by-attempt-v0125---v0126)
- [20261106_1300 — WAN routing confirmed live; link health per leg; Grafana tunnel; measured link figures (v0.12.4 -> v0.12.5)](#20261106_1300--wan-routing-confirmed-live-link-health-per-leg-grafana-tunnel-measured-link-figures-v0124---v0125)
- [20261106_1029 — Pi clock with no RTC on Ubuntu 24.04 measured (v0.12.3 -> v0.12.4)](#20261106_1029--pi-clock-with-no-rtc-on-ubuntu-2404-measured-v0123---v0124)
- [20261105_1758 — URL capture DNS mechanism measured; records plan proposed (v0.12.2 -> v0.12.3)](#20261105_1758--url-capture-dns-mechanism-measured-records-plan-proposed-v0122---v0123)
- [20261105_1634 — v8 resumable PCAP fetch, EFS find, Teleport path loss probe (v0.12.1 -> v0.12.2)](#20261105_1634--v8-resumable-pcap-fetch-efs-find-teleport-path-loss-probe-v0121---v0122)
- [20261105_1155 — smc_change Teleport login gate (v0.12.0 -> v0.12.1)](#20261105_1155--smc_change-teleport-login-gate-v0120---v0121)
- [20261104_2130 — Iridium batches 1-3 marked; rise deploy flashes; smc_mark_iridium.py (v0.11.9 -> v0.12.0)](#20261104_2130--iridium-batches-1-3-marked-rise-deploy-flashes-smc_mark_iridiumpy-v0119---v0120)
- [20261104_1900 — smc_change self-repair, every-goal success rule, applies_when (v0.11.8 -> v0.11.9)](#20261104_1900--smc_change-self-repair-every-goal-success-rule-applies_when-v0118---v0119)
- [20261104_1600 — smc_change chaining, per-change state, named value files (v0.11.7 -> v0.11.8)](#20261104_1600--smc_change-chaining-per-change-state-named-value-files-v0117---v0118)
- [20261102_1756 — smc_change skip, probe or force; per-SMC close (v0.11.6 -> v0.11.7)](#20261102_1756--smc_change-skip-probe-or-force-per-smc-close-v0116---v0117)
- [20261102_1721 — update:stats cron standard, port guard after cron starts (v0.11.5 -> v0.11.6)](#20261102_1721--updatestats-cron-standard-port-guard-after-cron-starts-v0115---v0116)
- [20261102_1434 — smc_change flows held to the code (v0.11.4 -> v0.11.5)](#20261102_1434--smc_change-flows-held-to-the-code-v0114---v0115)

---

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

## 20261106_1545 — smc_change export to a company task file; tracker orders resumed runs by attempt (v0.12.5 -> v0.12.6)

`references/19_smc-change-role.md`: new section, Export to a company role (Learned 2026-11-06, local-knowledge-ansible 7056782): `just export_change`, `export_check`, `export_drift`; what is carried
and left out, the play's own fail gate; and the tracker entry for resumed runs (c7cb38b, written 2026-11-06 earlier, committed 613c1c1). manifest 0.12.5 -> 0.12.6.

## 20261106_1300 — WAN routing confirmed live; link health per leg; Grafana tunnel; measured link figures (v0.12.4 -> v0.12.5)

`references/03_communication-flows.md`: Learned 2026-11-06, rcp routing confirmed on two boxes (per-leg tables and `from` rules by the dhclient hook, main-table multipath default by the portal's
`gateway.php`, `starlink`-role legs without a table, stale rules); Learned 2026-11-06, the APN Grafana tunnel (`tsh ssh -N -L 53000:localhost:3000 root@apn-prometheus01`). `references/01_overview.md`:
Learned 2026-11-06, measured round trips and the speedtest medians. `scripts/probes/smc_link_health.sh` measures every WAN leg, binds no-table legs to their device and reports stale rules (live on
warburton-smc01); `scripts/README.md` updated. From smc-resiliency S3. manifest 0.12.4 -> 0.12.5.

## 20261106_1029 — Pi clock with no RTC on Ubuntu 24.04 measured (v0.12.3 -> v0.12.4)

`references/07_hardware-overlay.md`: Learned 2026-11-06, a 24.04 box with no RTC boots at systemd's build date unless `/usr/lib/clock-epoch` sets a floor (systemd 255 reads it); chrony with the
gateway by address steps a 22.5 h error 16.3 s after boot without DNS (smc-resiliency S2 report section 8, apn 1dc80235). manifest 0.12.3 -> 0.12.4.

## 20261105_1758 — URL capture DNS mechanism measured; records plan proposed (v0.12.2 -> v0.12.3)

`references/09_url-capture-pcap.md`: Learned 2026-11-05 (b), what the v2 DNS capture holds (queries only, IPv4 only, a new tcpdump per 5-minute chunk, no drop count), one measured day (mornington 1.8
M queries, 2.3% to outside resolvers), measured smaller formats (3-6x records, 27-59x daily), the pcapfix cost for 202610 (154,097 files, 143 corrupt incl. 47 v2 chunks; parallel 6.4x faster), macOS
tcpdump cannot read a pcap from stdin, and the proposed lossless-records plan (not decided). Same entry: v8 promoted over v6 after the 202610 process run (ref 09).

## 20261105_1634 — v8 resumable PCAP fetch, EFS find, Teleport path loss probe (v0.12.1 -> v0.12.2)

`references/09_url-capture-pcap.md`: Learned 2026-11-05, v7 fetch timeouts and the resumable `ansible-malik/smc_get_pcapv8.yml` (newest staging dir reused automatically, `.partial` tars, resumable
retried rsync with a 6 h async limit, size check before the staging dir is deleted) and the slow `find` module on the EFS-backed capture store (one `find -maxdepth 2`: 1.65 s). Also commits the
earlier session's v7 fetch-timestamp paragraph (step 5). `references/03_communication-flows.md`: Learned 2026-11-05, one TCP stream from an AWS Teleport host to the activ8me home line caps at ~1.2
MB/s because of ~0.25% packet loss on the access leg (AAPT first hop), not Teleport, EC2 or the VM; BBR on the sender gave 10.4 MB/s (test route removed); apn-teleport01 facts (root disk 94%, 383 GB
of Teleport logs, Teleport 13.4.24). New `scripts/probes/teleport_path_throughput.sh` with `just teleport_path_throughput` (catalogued in `scripts/README.md`), smoke-run on apn-teleport01 (1 min, `-s
8 -p 3 -n 300`). manifest 0.12.1 -> 0.12.2. Same day 17:04: the first real v8 run passed (17 tars, 10 GB, size-checked, gzip-valid); ref 09 updated (cfca2a5). Later: ref 03 apn-teleport01 disk 93%
after cleanup; ref 09 promotion approved pending process_files; SKILL.md names the _ansible skills registry as a caller.

## 20261105_1155 — smc_change Teleport login gate (v0.12.0 -> v0.12.1)

`references/19_smc-change-role.md`: new "Teleport login gate" entry. smc_change.yml and smc_change_multiple.yml now include `roles/smc_change/tasks/tsh_login.yml` in their first play
(`any_errors_fatal`), which runs `files/tsh_login.py` on `tsh status --format=json` and stops the run before any SMC when a target proxy's login is missing, expired or has under
`smc_change_tsh_min_minutes` (30) left. Found when expired logins made 10 rct SMCs unreachable at "Check the host answers". tsh 12 exits 1 on an expired active profile but still prints the JSON.
Checked at each run start only; a per-batch re-check is proposed, not decided. Flow parts updated, 16 trace steps accepted as an agent review. manifest 0.12.0 -> 0.12.1.

## 20261104_2130 — Iridium batches 1-3 marked; rise deploy flashes; smc_mark_iridium.py (v0.11.9 -> v0.12.0)

Learned 2026-11-04: `references/19_smc-change-role.md` (25 rct SMCs flagged on rise and master; `smc_rise_deploy.yml` passes `rct_avr_flash: true`, proven on shelfo-crossing-smc01: AVR 2.14 -> 3.07,
SMSC set; long site names miss four SMCs in `-l`; a host_vars file reverted on disk makes the deploy skip both smc_change imports silently). New `scripts/ansible/smc_mark_iridium.py` with
`test_smc_mark_iridium.py` (3 tests) and `just smc_mark_iridium` / `just test_smc_mark_iridium`. Reference 18: `playbooks/smc_change_multiple.yml` (the two Iridium imports alone).

## 20261104_1900 — smc_change self-repair, every-goal success rule, applies_when (v0.11.8 -> v0.11.9)

Learned 2026-11-04: `references/19_smc-change-role.md` (cut-off runs repair themselves, lower dir guard, a change passes only when every action's goal holds, `applies_when`, the-crossing-smc01 and
scrubby-bore-smc01 cases); `smc_change_trace` passes quoted arguments whole. Then: Iridium sites are flashed in advance of the hardware swap; the Thuraya SIM loss is accepted (reference 19).

## 20261104_1600 — smc_change chaining, per-change state, named value files (v0.11.7 -> v0.11.8)

Learned 2026-11-04: `references/19_smc-change-role.md` (`smc_changes` chain in one run, five slots of `smc_change_run.yml`, per-change state dicts and `vars/main.yml` read-through, HELD gate in apply
and rollback, `variables_files` with grouped `smc_change_vars`, both rct changes in the scripts and variables form, `smc_bases_tstik_avr_version`, check-mode chain on alkngarrija-smc01). Also
`references/01_overview.md`: `tsh --proxy=<domain> ssh` when a plain `tsh ssh` is denied (operator-confirmed 2026-11-03, written by that day's session and committed here). Later the same day: flows
brought up to date (0 steps to review), quiet unused chain slots, first real apply on the rewritten role. Then: chains moved to `smc_change_chain.yml`; `smc_change.yml` runs one change with no slots
(operator decision). Then: the in-process chain withdrawn and archived (operator decision); reference 19 notes it at the top of the section.

## 20261102_1756 — smc_change skip, probe or force; per-SMC close (v0.11.6 -> v0.11.7)

Learned 2026-11-02: `references/19_smc-change-role.md` (per-SMC summary and tracker, queue time, nothing-changed path, `probe_first`, `smc_change_probe`, `checks` hash, `target-hash` correction, 39 s
in-place stop), `references/13_known-issues.md` (a `-l` host absent from the inventory).

## 20261102_1721 — update:stats cron standard, port guard after cron starts (v0.11.5 -> v0.11.6)

Learned 2026-11-02: `references/13_known-issues.md` (`*/1` boxes, guard gap, `gates.stale` crash), `references/02_service-map.md` (two crontab copies on overlay SMCs),
`references/19_smc-change-role.md` (action 8, checked crontab write, trace_sync accept).

## 20261102_1434 — smc_change flows held to the code (v0.11.4 -> v0.11.5)

`smc_change_flows_check` also audits the layout and runs trace_sync; new recipes `smc_change_trace` and `smc_change_ask` (skill-drawio references/charts-and-trace.md).
