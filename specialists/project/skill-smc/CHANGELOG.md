---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261120_2119
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

## Contents

- [20261120_2119 — smc_change render check and lint mode; variables_files on ansible-core 2.18 (v0.16.7 -> v0.16.8)](#20261120_2119--smc_change-render-check-and-lint-mode-variables_files-on-ansible-core-218-v0167---v0168)
- [20261120_1724 — --check previews of the bases and rise playbooks: what they need and the reboot-handler hazard (v0.16.6 -> v0.16.7)](#20261120_1724----check-previews-of-the-bases-and-rise-playbooks-what-they-need-and-the-reboot-handler-hazard-v0166---v0167)
- [20261120_1702 — smc_writers_probe reads installed timers, cron dirs, logrotate, freshclam; fleet facts of 20 Nov (v0.16.5 -> v0.16.6)](#20261120_1702--smc_writers_probe-reads-installed-timers-cron-dirs-logrotate-freshclam-fleet-facts-of-20-nov-v0165---v0166)
- [20261120_0451 — rise re-run disables the overlay; the pre-push hook's venv and worktree; smc_graylog not idempotent (v0.16.4 -> v0.16.5)](#20261120_0451--rise-re-run-disables-the-overlay-the-pre-push-hooks-venv-and-worktree-smc_graylog-not-idempotent-v0164---v0165)
- [20261120_0440 — lint-baseline-refresh.sh fixed: no delete before generate, output taken from the project root, git common dir (v0.16.3 -> v0.16.4)](#20261120_0440--lint-baseline-refreshsh-fixed-no-delete-before-generate-output-taken-from-the-project-root-git-common-dir-v0163---v0164)
- [20261120_0400 — rise deploy on a stage Iridium bench Pi; controller symlinks; cost per task (v0.16.2 -> v0.16.3)](#20261120_0400--rise-deploy-on-a-stage-iridium-bench-pi-controller-symlinks-cost-per-task-v0162---v0163)
- [20261120_0250 — clone rename fixed; check-mode limits, --diff leaks the join token, the interface-activation hook loop (v0.16.1 -> v0.16.2)](#20261120_0250--clone-rename-fixed-check-mode-limits---diff-leaks-the-join-token-the-interface-activation-hook-loop-v0161---v0162)
- [20261120_0050 — bench Pi inventoried on iridium and rise; Pi field image has no serial console and mounts root with discard (v0.16.0 -> v0.16.1)](#20261120_0050--bench-pi-inventoried-on-iridium-and-rise-pi-field-image-has-no-serial-console-and-mounts-root-with-discard-v0160---v0161)
- [20261119_1852 — smc_root_key_probe.sh; the warehouse field image read; root's key and password shared fleet-wide (v0.15.9 -> v0.16.0)](#20261119_1852--smc_root_key_probesh-the-warehouse-field-image-read-roots-key-and-password-shared-fleet-wide-v0159---v0160)
- [20261119_1830 — role_rerun_cost.py promoted; Ookla rate limit; Bitbucket fleet trust gap (v0.15.8 -> v0.15.9)](#20261119_1830--role_rerun_costpy-promoted-ookla-rate-limit-bitbucket-fleet-trust-gap-v0158---v0159)
- [20261119_1650 — Periodic review; 90-day window; identifiers redacted; smc_update_php.yml retired (v0.15.7 -> v0.15.8)](#20261119_1650--periodic-review-90-day-window-identifiers-redacted-smc_update_phpyml-retired-v0157---v0158)
- [20261119_1648 — topology_variance.py promoted; vars guard matches on command text (v0.15.6 -> v0.15.7)](#20261119_1648--topology_variancepy-promoted-vars-guard-matches-on-command-text-v0156---v0157)
- [20261119_1638 — smc_inventory_add: every flavor, templates owned by the skill, Iridium written as plain true (v0.15.5 -> v0.15.6)](#20261119_1638--smc_inventory_add-every-flavor-templates-owned-by-the-skill-iridium-written-as-plain-true-v0155---v0156)
- [20261119_1554 — smc_freeze_probe.sh; deployed Pi package and freeze state; pin-kernel quirk (v0.15.4 -> v0.15.5)](#20261119_1554--smc_freeze_probesh-deployed-pi-package-and-freeze-state-pin-kernel-quirk-v0154---v0155)
- [20261119_1303 — both platforms always (operator); deployed x86 SMCs have no watchdog and kernel.panic 0 (v0.15.3 -> v0.15.4)](#20261119_1303--both-platforms-always-operator-deployed-x86-smcs-have-no-watchdog-and-kernelpanic-0-v0153---v0154)
- [20261119_1250 — correction: the kernel feeds an armed watchdog for ever before userspace (open_timeout 0); watchdog.open_timeout=60 resets a stuck trial; census: every Pi 8 GB (v0.15.2 -> v0.15.3)](#20261119_1250--correction-the-kernel-feeds-an-armed-watchdog-for-ever-before-userspace-open_timeout-0-watchdogopen_timeout60-resets-a-stuck-trial-census-every-pi-8-gb-v0152---v0153)
- [20261119_1205 — early watchdog fed by the kernel driver from its probe; EEPROM update from partition 1 on both 2022 bootloaders; census reads memory (v0.15.1 -> v0.15.2)](#20261119_1205--early-watchdog-fed-by-the-kernel-driver-from-its-probe-eeprom-update-from-partition-1-on-both-2022-bootloaders-census-reads-memory-v0151---v0152)
- [20261118_2152 — Pi 4 early watchdog, 2022 bootloaders ignore the A/B selector, EEPROM staging on an A/B card (v0.15.0 -> v0.15.1)](#20261118_2152--pi-4-early-watchdog-2022-bootloaders-ignore-the-ab-selector-eeprom-staging-on-an-ab-card-v0150---v0151)
- [20261118_2049 — storage identity readable on x86 and Pi; low-touch description record (name, locid) (v0.14.9 -> v0.15.0)](#20261118_2049--storage-identity-readable-on-x86-and-pi-low-touch-description-record-name-locid-v0149---v0150)
- [20261118_1553 — rct tstik board restarts a stuck SMC (operator); wh flavours have none (v0.14.8 -> v0.14.9)](#20261118_1553--rct-tstik-board-restarts-a-stuck-smc-operator-wh-flavours-have-none-v0148---v0149)
- [20261117_1922 — smc_change: state-file timing; connect timeout 30 s; offline SMCs fail INCOMPLETE; ssh_handshake_time.sh (v0.14.7 -> v0.14.8)](#20261117_1922--smc_change-state-file-timing-connect-timeout-30-s-offline-smcs-fail-incomplete-ssh_handshake_timesh-v0147---v0148)
- [20261117_1857 — smc_change_multiple: never pass -e smc_change; vars guard blocks edits; delta gate on rewritten files (v0.14.6 -> v0.14.7)](#20261117_1857--smc_change_multiple-never-pass--e-smc_change-vars-guard-blocks-edits-delta-gate-on-rewritten-files-v0146---v0147)
- [20261117_1044 — Teleport self-upgrade cron on every flavour (v0.14.5 -> v0.14.6)](#20261117_1044--teleport-self-upgrade-cron-on-every-flavour-v0145---v0146)

---

## 20261120_2119 — smc_change render check and lint mode; variables_files on ansible-core 2.18 (v0.16.7 -> v0.16.8)

- references/19_smc-change-role.md: render check (D1) and controller-only lint mode (D2) of smc_change; why specs with variables_files fail from a 2.18 controller (smc-resiliency 20261120, local-knowledge-ansible 45055e7 and bb79a08).

## 20261120_1724 — --check previews of the bases and rise playbooks: what they need and the reboot-handler hazard (v0.16.6 -> v0.16.7)

- references/08_ansible-authoring.md: Learned entry on making `--check` reach the end on overlay hubs, and rise's `check_mode: no` reboot handler (smc-resiliency 20261120).

## 20261120_1702 — smc_writers_probe reads installed timers, cron dirs, logrotate, freshclam; fleet facts of 20 Nov (v0.16.5 -> v0.16.6)

- scripts/probes/smc_writers_probe.sh: adds installed systemd timers (last and next run), `/etc/cron.{hourly,daily,weekly,monthly}` contents, logrotate configs and freshclam's state; canary on one rct Pi (31.6 s), then 14 boxes (13 answered, 305 s). scripts/README.md updated.
- references/07_hardware-overlay.md: Learned entries for the x86 model census (26 plain BOXER-6404 with one CFast, 18 BOXER-6641), freshclam failed on nbn_accelerate, no USB drive on field Pis (smc-resiliency 20261120).

## 20261120_0451 — rise re-run disables the overlay; the pre-push hook's venv and worktree; smc_graylog not idempotent (v0.16.4 -> v0.16.5)

- references/08_ansible-authoring.md: a re-run of smc_rise_deploy on an overlay box turns overlayroot off, reboots and deploys (not a no-change
  run; operator correction); the pre-push hook needs the controller's full ansible package and lints a worktree without the untracked lint configs
  when the pushed commit is not HEAD; smc_graylog reports changed=3 on every run (smc-resiliency 20261120).

## 20261120_0440 — lint-baseline-refresh.sh fixed: no delete before generate, output taken from the project root, git common dir (v0.16.3 -> v0.16.4)

- scripts/ansible/lint-baseline-refresh.sh: deleted the baseline before generating (a failed run left none), looked for ansible-lint's output in .git/
  (it writes `.ansible-lint-ignore` in the project root, left as a stray untracked file), and broke in a linked worktree. Now it takes the output
  from the root and restores the root file, writes to the git common dir as the delta gate reads it, keeps `.prev`, merges by default (`--replace`).
  Smoke run on an ansible-wifi iridium worktree: 3932 entries in 45 s (smc-resiliency 20261120).

## 20261120_0400 — rise deploy on a stage Iridium bench Pi; controller symlinks; cost per task (v0.16.2 -> v0.16.3)

- references/08_ansible-authoring.md: smc_rise_deploy stops at the tstik spec on an rct stage Iridium host (`-e smc_bases_iridium=false` on a bench Pi);
  the controller VM needs `/Volumes/Data` linked to follow smc_change.yml; measured cost per task over 100 Mbps (smc-resiliency 20261120).

## 20261120_0250 — clone rename fixed; check-mode limits, --diff leaks the join token, the interface-activation hook loop (v0.16.1 -> v0.16.2)

- scripts/ansible/smc_inventory_add.py: `rename_hosts` replaces whole host names (a generic image's `-iridium-20241121` suffix was kept, so no topology vars reached the host); two tests in
  test_smc_inventory_add.py (10 pass).
- references/08_ansible-authoring.md: Learned 2026-11-20, check mode stops smc_bases, smc_rename and smc_prometheus; `--diff` writes the Teleport join token into logs (mask before keeping); topology
  vars show only in a playbook run.
- references/06_failure-modes.md: Learned 2026-11-20, the interface-activation hook loops when untagged eth0 gets a DHCP lease (smc-resiliency BUG-102).

## 20261120_0050 — bench Pi inventoried on iridium and rise; Pi field image has no serial console and mounts root with discard (v0.16.0 -> v0.16.1)

- references/08_ansible-authoring.md: Learned 2026-11-20, adding a bench or renamed SMC (a name with vars files can belong to another box; a generic image's site ID 181; the same entry on iridium and
  rise through `--repo`; `smc_rename.yml` needs the ansible-apn controller for its python3.10 local step).
- references/07_hardware-overlay.md: Learned 2026-11-20, the Pi field image has no serial console (cmdline `console=tty1` only), root is mounted with online discard (a no-name card failed DISCARD;
  smc-resiliency Pad BUG-101), and a FAT edit is lost to a crash before writeback.

## 20261119_1852 — smc_root_key_probe.sh; the warehouse field image read; root's key and password shared fleet-wide (v0.15.9 -> v0.16.0)

- New scripts/probes/smc_root_key_probe.sh (`just smc_root_key_probe`), catalogued in scripts/README.md; smoke run on five boxes, Pi and x86.
- references/07_hardware-overlay.md: the warehouse field image section (versions, Teleport joins under the hostname, network and MANAGEMENT chain, enabled units).
- references/13_known-issues.md: root's SSH key and password shared on every box read (smc-resiliency B19-06, OPEN, critical).
- scripts/check_governance.py version-single-source: an underscore before a number (a Debian package file name such as fatrace_0.16.3-1) is not a version stamp; found when the pack moved to 0.16.0;
  tested both ways (v0.16.3 and 0.16.0 still flagged).

## 20261119_1830 — role_rerun_cost.py promoted; Ookla rate limit; Bitbucket fleet trust gap (v0.15.8 -> v0.15.9)

- `scripts/ansible/role_rerun_cost.py` promoted (recipes `role_rerun_cost`, `role_rerun_cost_test`; catalogue rows; 3 offline tests): tasks per role and always-working patterns of a playbook's roles.
  First run on iridium: smc_bases + smc_prometheus 588 tasks, 22 per-item package loops; 0.25 s.
- Ref 06: Ookla rate limit (rc 173) at the old speedtest license step; the fix `35276a62` was rise-only until 2026-11-19 (iridium `11daa2b5`, master `48bf6839`). Contents block also gains the
  2026-10-20 netplan entry it lacked.
- Ref 13: Bitbucket entry, fleet trust not rolled out (records show alkngarrija-smc01 only; Pad TASK-21). Earlier the same day: "Now live" entry (`743576a2`).
- Ref 18: the smc_bases converge-and-skip plan and the ansible-wifi Pad workspace links (this pack has its own `.pad.toml`, `45d20393`).
- Ref 13 (18:45): smc_change tstik runs depend on the branch: rise (old address) fails every clone and rollback, iridium fails where known_hosts lacks ssh.bitbucket.org.

## 20261119_1650 — Periodic review; 90-day window; identifiers redacted; smc_update_php.yml retired (v0.15.7 -> v0.15.8)

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19 (two were hidden by the baseline); reference ranges 01-19, spec and run-record paths, live status of
  smc_change. Review window now 90 days (`--window-days 90`).
- Identifiers redacted (operator): a person's name and the SMSC and destination numbers in refs 02, 06 and 19 replaced with placeholders.
- `playbooks/smc_update_php.yml` retired (operator; overlay apply proven): refs 18 and 19.

## 20261119_1648 — topology_variance.py promoted; vars guard matches on command text (v0.15.6 -> v0.15.7)

- New scripts/ansible/topology_variance.py (`just topology_variance`, offline test `just test_topology_variance`), catalogued in scripts/README.md; smoke run on ansible-wifi master, 0.2 s.
- references/13_known-issues.md: 2026-11-19, the vars guard refuses commands whose text names group or host vars paths (commit message, `git add` of new files, CHANGELOG heredoc), with what passed; an
  OPA hook refused a read-only `[!.]*.yml` loop.
- references/08_ansible-authoring.md: the topology survey figures are from branch `iridium`; master differs (rcp 34 files, 25 layouts).
- (added 16:58) references/08_ansible-authoring.md: an Eclipse site name does not set the flavor ("RCP - Haji Ali Homstead" is a Pi rct site named for its RCP project; operator).

## 20261119_1638 — smc_inventory_add: every flavor, templates owned by the skill, Iridium written as plain true (v0.15.5 -> v0.15.6)

- templates/inventory/ (new): common/ group_vars, host_vars and standard topology; nbn_accelerate/ sized topology. The repo generator's rct host_vars wrote `smc_bases_iridium: "True"` and its topology
  templates failed the pre-push lint.
- scripts/ansible/smc_inventory_add.py: flavors rct, wh, nbn_wh, nbn_accelerate, rcp; `--size`, `--topology-from`, `--templates`; refuses quoted Iridium, empty NIC names, trailing whitespace; prints
  NICs and VLAN IDs to check. New test_smc_inventory_add.py (8 tests, `just test_smc_inventory_add`).
- ruff.toml (new, existing Python excluded) and `just lint_py`, run by `just check`.
- references/08_ansible-authoring.md: topology survey per flavor, generator template faults, branch placement; scripts/README.md catalogue.

## 20261119_1554 — smc_freeze_probe.sh; deployed Pi package and freeze state; pin-kernel quirk (v0.15.4 -> v0.15.5)

- New scripts/probes/smc_freeze_probe.sh (`just smc_freeze_probe`), catalogued in scripts/README.md; smoke run on a real hub.
- references/07_hardware-overlay.md: Learned 2026-11-19, deployed Pi freeze state, package state (22.04.1 base, systemd 249.11-0ubuntu3.7, kernel 1078 held), pin-kernel version rule that never
  matches, apt_info.py every 5 min, mosquitto outside its gate.

## 20261119_1303 — both platforms always (operator); deployed x86 SMCs have no watchdog and kernel.panic 0 (v0.15.3 -> v0.15.4)

- SKILL.md: every SMC answer covers the Pi and x86, or names the other platform's alternative (operator, 2026-11-19).
- references/07_hardware-overlay.md: Learned 2026-11-19, three deployed x86 SMCs read: no watchdog, kernel.panic 0, lockup and hung-task panics off.

## 20261119_1250 — correction: the kernel feeds an armed watchdog for ever before userspace (open_timeout 0); watchdog.open_timeout=60 resets a stuck trial; census: every Pi 8 GB (v0.15.2 -> v0.15.3)

- references/07_hardware-overlay.md: the 2026-11-19 entry corrected in place (it called the arm-to-probe window the only unprotected one); open_timeout facts (kernel docs, raspi config) and the bench
  result; no hard-lockup detector on the Pi 4; the fleet census (311 of 318, all 8 GB; 45 rct on 2022 bootloaders).

## 20261119_1205 — early watchdog fed by the kernel driver from its probe; EEPROM update from partition 1 on both 2022 bootloaders; census reads memory (v0.15.1 -> v0.15.2)

- references/07_hardware-overlay.md: Learned 2026-11-19 (VERIFIED_PRIMARY, bench Pi 4): a slow healthy boot (systemd 30 s late) is not reset by the early watchdog, the kernel driver feeds it from
  about 5 s after the arm; broken trial kernel reset alone with the overlay; partition-1 EEPROM staging works from 2022-04-26 and 2022-01-25, files left on p1.
- scripts/fleet/pi_bootloader_census.sh prints `mem_kb`; summarise_survey.py census tallies memory per flavour (test added). Not yet run on the fleet: Teleport certificate expired.
- From the smc-resiliency bench run of 2026-11-19 (lab test record section 25).

## 20261118_2152 — Pi 4 early watchdog, 2022 bootloaders ignore the A/B selector, EEPROM staging on an A/B card (v0.15.0 -> v0.15.1)

- references/07_hardware-overlay.md: Learned 2026-11-18 (VERIFIED_PRIMARY, bench Pi 4): an unstartable kernel freezes the Pi; the firmware arms the watchdog early only with the `early-watchdog`
  device-tree property, which Ubuntu's tree lacks (overlay given, 17 s reset measured); bootloaders 2022-04-26 and 2022-01-25 ignore `[tryboot]` and `tryboot_a_b`; where `rpi-eeprom-update` must stage
  an update for a bootloader without self-update, and the clean-up after.
- From the smc-resiliency bench run of 2026-11-18 (lab test record section 24).

## 20261118_2049 — storage identity readable on x86 and Pi; low-touch description record (name, locid) (v0.14.9 -> v0.15.0)

- references/07_hardware-overlay.md: Learned 2026-11-18 (VERIFIED_PRIMARY, two boxes): CFast model, serial and world-wide ID through `lsblk` and sysfs on x86; SD card ID, maker, date and serial in
  sysfs on a Pi; `smartctl` present on both; no package needed.
- references/02_service-map.md: Learned 2026-11-18 (VERIFIED_PRIMARY, one low-touch box): the per-unit description record in `/var/local/cnmaestro-provisioning/log.<MAC>` (`name`, `locid` from redis
  `next_locid`, `lot no`, `us`); the management address ends in `locid`; `name` is the RPZ record.
- From the unified-network-controller asset custody (D17) session of 2026-11-18, read-only reads on the operator's instruction.

## 20261118_1553 — rct tstik board restarts a stuck SMC (operator); wh flavours have none (v0.14.8 -> v0.14.9)

- references/06_failure-modes.md: Learned 2026-11-18 (USER_STATED): the tstik is a physical board wired to the Pi and restarts a stuck rct SMC by rules such as loss of the internet; the SMC restart
  sits in the board's AVR firmware, outside the rct-tstik app read on 2026-10-07, so that reading stands. The wh flavours (wh, nbn_wh) have no such board and no automatic restart.
- From the apn smc-resiliency concept deck session (6128bdd9), where the operator corrected a slide that said nothing restarts any hung SMC.

## 20261117_1922 — smc_change: state-file timing; connect timeout 30 s; offline SMCs fail INCOMPLETE; ssh_handshake_time.sh (v0.14.7 -> v0.14.8)

`references/19_smc-change-role.md` (smc_change_multiple bullets): a change's state file is written per SMC at its stage 11 under strategy free, never in check mode, and the SMSC play waits for the
whole AVR play; "banner exchange" timeouts are the ssh plugin's 10 s default against a ~9 s Teleport handshake, now `ansible_ssh_timeout: 30` in both smc_change playbooks (ansible-wifi chat f516e57d).

New read-only `scripts/access/ssh_handshake_time.sh` (`just ssh_handshake_time`, offline test `just test_ssh_handshake_time`, smoke-run on wujal-wujal-booth-smc01, catalogued in `scripts/README.md`);
reference 19: any SMC a run did not finish (offline, no record, unreachable, refused, failed, held back) is noted and fails INCOMPLETE, in the wrapper's last play when `smc_change_defer_incomplete` is
set (operator; side-agent note on later plays).

## 20261117_1857 — smc_change_multiple: never pass -e smc_change; vars guard blocks edits; delta gate on rewritten files (v0.14.6 -> v0.14.7)

`references/19_smc-change-role.md` (smc_change_multiple bullets): `-e smc_change=<spec>` outranks each import's play var, so both imports ran rct-avr-smsc and the AVR flash never ran (23-SMC batch,
2026-11-17: 4 passed, 6 failed on AVR 2.14, 13 never started); what `6/11 ACTIONS` means and why the AVR version check fails instead of skipping. `references/13_known-issues.md`: the vars guard also
blocks non-printing edits of inventory host files (use `just smc_mark_iridium`); the lint delta gate brings old findings of a rewritten file in as new; pipefail needs bash (ansible-wifi chat
f516e57d).

## 20261117_1044 — Teleport self-upgrade cron on every flavour (v0.14.5 -> v0.14.6)

`references/03_communication-flows.md` "Teleport self-upgrade cron": `/upgrade_teleport.sh` daily at 00:00 on all flavours (ansible-wifi 906ee778), and why an image-based root drops it; cross-link to
the C6 `pkill -9 python3` entry (from apn smc-resiliency scheduled-writer inventory, 17 Nov 2026).
