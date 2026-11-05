---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261105_1155
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

## 20261105_1155 — smc_change Teleport login gate (v0.12.0 -> v0.12.1)

`references/19_smc-change-role.md`: new "Teleport login gate" entry. smc_change.yml and smc_change_multiple.yml now include
`roles/smc_change/tasks/tsh_login.yml` in their first play (`any_errors_fatal`), which runs `files/tsh_login.py` on `tsh status --format=json` and stops the
run before any SMC when a target proxy's login is missing, expired or has under `smc_change_tsh_min_minutes` (30) left. Found when expired logins made 10
rct SMCs unreachable at "Check the host answers". tsh 12 exits 1 on an expired active profile but still prints the JSON. Checked at each run start only;
a per-batch re-check is proposed, not decided. Flow parts updated, 16 trace steps accepted as an agent review. manifest 0.12.0 -> 0.12.1.

## 20261104_2130 — Iridium batches 1-3 marked; rise deploy flashes; smc_mark_iridium.py (v0.11.9 -> v0.12.0)

Learned 2026-11-04: `references/19_smc-change-role.md` (25 rct SMCs flagged on rise and master; `smc_rise_deploy.yml` passes `rct_avr_flash:
true`, proven on shelfo-crossing-smc01: AVR 2.14 -> 3.07, SMSC set; long site names miss four SMCs in `-l`; a host_vars file reverted on disk makes
the deploy skip both smc_change imports silently). New `scripts/ansible/smc_mark_iridium.py` with `test_smc_mark_iridium.py` (3 tests) and
`just smc_mark_iridium` / `just test_smc_mark_iridium`. Reference 18: `playbooks/smc_change_multiple.yml` (the two Iridium imports alone).

## 20261104_1900 — smc_change self-repair, every-goal success rule, applies_when (v0.11.8 -> v0.11.9)

Learned 2026-11-04: `references/19_smc-change-role.md` (cut-off runs repair themselves, lower dir guard, a change passes only when every action's goal holds, `applies_when`, the-crossing-smc01 and scrubby-bore-smc01 cases); `smc_change_trace` passes quoted arguments whole.
Then: Iridium sites are flashed in advance of the hardware swap; the Thuraya SIM loss is accepted (reference 19).

## 20261104_1600 — smc_change chaining, per-change state, named value files (v0.11.7 -> v0.11.8)

Learned 2026-11-04: `references/19_smc-change-role.md` (`smc_changes` chain in one run, five slots of `smc_change_run.yml`, per-change state dicts and
`vars/main.yml` read-through, HELD gate in apply and rollback, `variables_files` with grouped `smc_change_vars`, both rct changes in the scripts and
variables form, `smc_bases_tstik_avr_version`, check-mode chain on alkngarrija-smc01). Also `references/01_overview.md`: `tsh --proxy=<domain> ssh`
when a plain `tsh ssh` is denied (operator-confirmed 2026-11-03, written by that day's session and committed here).
Later the same day: flows brought up to date (0 steps to review), quiet unused chain slots, first real apply on the rewritten role.
Then: chains moved to `smc_change_chain.yml`; `smc_change.yml` runs one change with no slots (operator decision).
Then: the in-process chain withdrawn and archived (operator decision); reference 19 notes it at the top of the section.

## 20261102_1756 — smc_change skip, probe or force; per-SMC close (v0.11.6 -> v0.11.7)

Learned 2026-11-02: `references/19_smc-change-role.md` (per-SMC summary and tracker, queue time, nothing-changed path, `probe_first`, `smc_change_probe`, `checks` hash, `target-hash` correction, 39 s in-place stop), `references/13_known-issues.md` (a `-l` host absent from the inventory).

## 20261102_1721 — update:stats cron standard, port guard after cron starts (v0.11.5 -> v0.11.6)

Learned 2026-11-02: `references/13_known-issues.md` (`*/1` boxes, guard gap, `gates.stale` crash), `references/02_service-map.md` (two crontab copies on overlay SMCs), `references/19_smc-change-role.md` (action 8, checked crontab write, trace_sync accept).

## 20261102_1434 — smc_change flows held to the code (v0.11.4 -> v0.11.5)

`smc_change_flows_check` also audits the layout and runs trace_sync; new recipes `smc_change_trace` and `smc_change_ask` (skill-drawio references/charts-and-trace.md).

## 20261102_1347 — smc_change specs, trackers, shared scripts; AVR numbers ruling (v0.11.3 -> v0.11.4)

Learned 2026-11-02: `references/19_smc-change-role.md` (vars, scripts, files/shared, transient tool, pool naming, fact_same, trackers, abandoned_clean apt_pin only), `references/02_service-map.md` (three numbers, reboot evidence, stats page, port), `references/18_local-knowledge-ansible.md`.

## 20261102_1132 — AVR emergency and SMS numbers (v0.11.2 -> v0.11.3)

Learned 2026-11-02 (rct-tstik 971d8d0, warehouse-rct01): `references/02_service-map.md` (framing, `/ec` path, blank fields kept, survey), `references/18_local-knowledge-ansible.md` (`avr_emergency.py`).

## 20261101_1958 — smc_qos back on the meta-package (v0.11.1 -> v0.11.2)

Learned 2026-11-01 (ansible-wifi `rise` c22318fe): `references/13_known-issues.md`, kernel drift entry.

## 20261101_1944 — Kernel fix reaches rise (v0.11.0 -> v0.11.1)

Learned 2026-11-01 (ansible-wifi `rise` 8684e5ec): `references/13_known-issues.md`, kernel drift entry.

## 20261101_1937 — smc_change reporting and fallback, kernel drift, pre-push venv (v0.10.11 -> v0.11.0)

Learned 2026-11-01: `references/13_known-issues.md` (overlay `Find root device details`, AVR ahead of Iridium, unpinned kernel meta-package and purge without re-flash, stats 2.11, pre-push venv, deploy never enables overlay), `references/19_smc-change-role.md` (action outcomes, busy lower dir, RULE-011, governance of the role), `SKILL.md` pointer. New `scripts/probes/smc_boot_kernel_probe.sh`, `just smc_boot_kernel`.

## 20261101_0214 — apt-get update fix reaches rise (v0.10.10 -> v0.10.11)

Learned 2026-11-01 (ansible-wifi `rise` a9d6e6b7): `references/13_known-issues.md`, branch reach of the helper change.

## 20261101_0128 — one failed apt source stopping smc_bases; apt module versus apt-get update (v0.10.9 -> v0.10.10)

Learned 2026-11-01 (ansible-wifi `iridium` 8608c717): `references/13_known-issues.md`.

## 20261101_0108 — overlayroot.conf vs local.conf in smc_disable_overlay; Teleport vars (v0.10.8 -> v0.10.9)

Learned 2026-11-01 (ansible-wifi `iridium` afbc8f1b): `references/13_known-issues.md`.

## 20261101_0030 — PHP fix ported from rise to a master-based branch; pre-push traps (v0.10.7 -> v0.10.8)

Learned 2026-11-01 (ansible-wifi `iridium` 4aaebca0): `references/13_known-issues.md` (guard_no_overlay travels with the PHP tasks, pinned names in master's
custom_apt_install, smc_bases.yml CRLF and the lint delta gate, hook venv without ansible.posix, vars guard behaviour).

## 20261030_1719 — rct-tstik AVR data map, smc_change conditions and loop, rct_avr_probe modem fields (v0.10.6 -> v0.10.7)

Learned 2026-10-30 (ansible-wifi chat 0a7b835b): `references/02_service-map.md` (what update:stats reads from the AVR, stats.json, master's
Thuraya labels and unpadded version, `/bin/sh` is dash), `references/19_smc-change-role.md` (facts, conditions, when, loop; local-knowledge-ansible
`7ef59c7`). `scripts/probes/rct_avr_probe.sh` adds modem, modem_net, modem_comms and sim (Iridium* or Thuraya* fields); its test passes.
manifest 0.10.6 -> 0.10.7.

## 20261030_1222 — install_missing, controller lookups and pinned PHP, Teleport duplicate node after a data-dir wipe (v0.10.5 -> v0.10.6)

Learned 2026-10-30 (ansible-wifi chat cad11710): `references/19_smc-change-role.md` (apt_pin `install_missing`, kept out of the target;
local-knowledge-ansible `cf4f994`), `references/08_ansible-authoring.md` (pipe lookups run on the controller, macOS `date -Is`; smc_application
PHP pinned against the ondrej PPA, mod_php kept; ansible-wifi `fb6ae80b`), `references/03_communication-flows.md` (kaltjiti-fergon-smc01: two
node records for ~9 min after clearing `/var/lib/teleport`; old-process errors; exit 127 from a stale `versions` label). manifest 0.10.5 -> 0.10.6.

## 20261029_2011 — Harvest write-back: tbot repair, onboarding latency, D12, Kea gate, switch needs, voice options, DNS-only capture (v0.10.4 -> v0.10.5)

Learned 2026-10-29 from the architect-pack harvest of apn projects: `references/03_communication-flows.md` (stale tbot state; "did not match any
allow rules" from an orphaned bot role and expired token), `references/01_overview.md` (about 7 s a unit through Teleport over satellite, ranked
fixes; D12 P0 software lifecycle under the A/B decision), `references/13_known-issues.md` (ISC DHCP end of life and the gated Kea port; the rct switch
takes gateway and NTP from the SMC, not DHCP, cross-referenced to skill-mikrotik), `references/02_service-map.md` (Asterisk replacement options; CDR
and CEL back-ends noloaded), `references/09_url-capture-pcap.md` (the capture filter is `dst port 53`). Skipped as covered: tbot state reset, proxy
naming, fleet utilisation, Asterisk RSS, tmpfiles.d rule, deadline and random-node access rules. manifest 0.10.4 -> 0.10.5.

## 20261029_1750 — Inbound route to the peer architect skills (v0.10.3 -> v0.10.4)

SKILL.md Related Skills names skill-network-architect and skill-systems-architect and when to call them (design rather than device facts), with their
handoff form; they call back here for platform facts (operator, 2026-10-29). manifest 0.10.3 -> 0.10.4.

## 20261029_1417 — aurukun: six WAN legs per box; a leg down at draft time is left out (v0.10.2 -> v0.10.3)

Learned 2026-10-29 in `references/01_overview.md` (WAN legs): every aurukun box has six NBN Co WAN legs with their own routing
tables; an uplink plan drafted while one is down leaves it out (unified-network-controller, smc01 `enp1s0`).

## 20261029_1257 — FDB and VIP placement evidence; TL- model prefix on old SG2428P firmware (v0.10.1 -> v0.10.2)

Learned 2026-10-29 in `references/01_overview.md` (VRRP) and `references/16_tplink-site-switches.md` (b).

## 20261029_1215 — ssh_handshake_probe: what SSH a device behind an SMC offers, no login (v0.10.0 -> v0.10.1)

- `scripts/switch/ssh_handshake_probe.py` (+ `test_ssh_handshake_probe.py`, recipe `just ssh_handshake_probe <proxy> <node> <ip>...`): one tsh
  session, `ssh -vv` with no authentication per address; prints banner, kex, host key, cipher/MAC and auth methods, so an `IPSSH-6.6.0` switch is
  told from a `TPSSH` one before a login. Smoke run 2026-10-29 on aurukun-smc01 (10.255.1.2 IPSSH, 10.255.3.1 TPSSH): 19 s. Promoted from a
  unified-network-controller session's ad hoc probe.

## 20261029_1058 — TP-Link switches on IPSSH firmware: legacy SSH fallbacks (v0.9.9 -> v0.10.0)

- `scripts/switch/tplink_cli_driver.py` and `tplink-switch.sh` append `ssh-dss`, `hmac-md5`, `diffie-hellman-group1-sha1` and `aes128-cbc` as
  fallbacks: SG2428P firmware 4.0.1 (`IPSSH-6.6.0`) offers nothing else, and three aurukun switches could not be read. Learned 2026-10-29 in
  `references/16_tplink-site-switches.md`.

## 20261029_0958 — ha capture group, multi-SMC hosts and --proxy; aurukun VRRP layout (v0.9.8 -> v0.9.9)

- `scripts/capture/collect-smc-evidence-full.sh`: `ha` group (keepalived, VIPs, track scripts, transitions, dhcpd failover and leases;
  `auth_pass` redacted), `<site>-smcNN` hosts kept as given, `--proxy` / `SMC_TSH_PROXY` on every tsh call. Catalogue: `scripts/README.md`.
- Learned 2026-10-29 in `references/01_overview.md` (VRRP): aurukun's keepalived source build, VIPs per VLAN, `google_ping` weight -30, no
  DHCP failover (each box leases its own clients). Found for unified-network-controller's multi-SMC model.

## 20261028_2046 — stuck apt_info.py holds the apt lists lock; apt_lock_probe.sh (v0.9.7 -> v0.9.8)

- references/13: 2026-10-28 entry: node_exporter apt_info.py hung 11-120 days holding /var/lib/apt/lists/lock on 3 rct SMCs; smc_change
  apt_pin workaround (excerpt); root fix `4889af8` on local rise-multi only.
- scripts/probes/apt_lock_probe.sh (`just apt_lock_probe`), catalogued: lock owner by path (lslocks), dpkg and archives lock holders,
  apt_info.py ages, newest list. Fleet run: 5 more stuck apt_info.py (references/13).
- references/13: 2026-10-28 overlay left read-write mid-change: needs_repair repair, hidden first failure, `at` re-arm, tmpfs /var/log,
  unbound interface-automatic on a REDIRECT box.
- manifest 0.9.7 -> 0.9.8.

## 20261028_1559 — PIN funnel and fleet check, runtime budget clock (v0.9.6 -> v0.9.7)

- references/14 §14.9: change-or-upstream triage for a PIN drop after a change (Galiwinku squid fail-open 2026-10-28, not PHP); PIN =
  auto-generated on T&C acceptance (operator).
- scripts/capture/pin-funnel-hourly.sh (`just pin_funnel`) and pin-fleet-check.sh (`just pin_fleet_check`), catalogued (c3e856b, 4b61a2d).
- references/19: runtime budget counts the wait for earlier batches (stage 1 clock not reset per batch); read real time as elapsed minus SPEC.
- manifest 0.9.6 -> 0.9.7.

## 20261028_1516 — rct_avr_probe.sh and AVR routing (v0.9.5 -> v0.9.6)

- `scripts/probes/rct_avr_probe.sh` (new, read-only): RCT AVR firmware per SMC from tstik stats.json (AVRVersion, TiniVer, age), rct-tstik HEAD,
  loader, overlay; `QUERY=1` asks the AVR (one version request, after waiting for update:stats). Test `probes/test_rct_avr_probe.py`, recipe
  `just rct_avr_probe`, catalogue row. Smoke: warehouse-rct01, mooloowa-smc01, gilroyd-smc01 in 12 s.
- `RUNBOOK.md`: routing row for RCT tstik AVR firmware (06_failure-modes AVR entries, the probe).

## 20261028_1442 — AVR V3.07 vs Thuraya, fleet AVR state (v0.9.4 -> v0.9.5)

- `references/06_failure-modes.md`: AVR V3.07 on a Thuraya control board loses the board SIM (Chris Blair); fleet AVR state (27 V3.07, malupirti V3.06, rest V2.14);
  flash only after Iridium is installed (`rct_avr_flash`).

## 20261028_1315 — Automated AVR flash, probe self-match, resume_safe (v0.9.3 -> v0.9.4)

- `references/19_smc-change-role.md`: automated AVR flash in a transient systemd unit (warehouse-rct01 3.06 -> 3.07, 269 s), probe self-match
  through PROBE_CONFIG on the command line (anchor `pgrep -f` at `^php`; probe 155 s -> 31 s), two-part repair of a failed run whose spec
  changed (journal and record to superseded/), reviewed `resume_safe` per action.

## 20261028_1242 — AVR serial collision verified on warehouse-rct01 (v0.9.2 -> v0.9.3)

- `references/06_failure-modes.md`: Learned entry: rct-tstik and the AVR loader collide on `/dev/ttyS0` (warehouse-rct01 test: tstik run 0/24 good
  while overlapped, 24/24 before and after); tstik re-runs stty 19200 and flushes before every send; pause tstik cron for a flash; frame format.
- `references/02_service-map.md`: deploy reference names `roles/smc_application/tasks/main.yml` instead of a person.
