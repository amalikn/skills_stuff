---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261029_1751
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

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

## 20261028_1224 — rct-tstik iridium change: self-persisting command, symlinked copy sources, AVR flash (v0.9.1 -> v0.9.2)

- `references/19_smc-change-role.md`: new section for the smc_change spec `rct-tstik-iridium-update` (canary aeroplane-1-smc01 passed 8/8 gates, 592 s): spec values naming inventory vars, a command
  action that persists itself into the lower dir (no chroot, no reboot) with a `proves` check of both HEADs, copy sources served by a directory symlink that leaves the RULE-007 fingerprint unchanged,
  copy rollback cannot remove a file that did not exist (patch in ansible-wifi `plans/`), checks false before the change go in `proves`, check mode can still act.
- `references/06_failure-modes.md`: Learned entry on the AVR firmware flash (one "Protocol Error" at block 13, passed on retry; serial contention with cron's `update:stats` suspected, UNVERIFIED), the
  vendor loader's exit 0 everywhere, endless retry and 19500 baud, and `py_avrloader_v2.py` exit codes and two-digit minor version; hand copies on an overlay SMC vanish at reboot.
- `references/01_overview.md`: Tstik open question answered: Iridium keeps `rct-tstik` on `release/iridium` (1318c7b) with AVR firmware V3.07; `smc_bases_iridium: true` also switches portal branch,
  latlon role and Teleport lat/lon labels.
- `references/02_service-map.md`: how tstik is served (`php -S` from cron, not Apache), the iridium routes, the self test, tracked `config.json`.
- Source: local-knowledge-ansible ansible-wifi change record `rct-tstik-iridium-update-20261028_1221.md`.

## 20261027_2015 — Slurp close: governed-file adoption, sibling write-backs (v0.9.0 -> v0.9.1)

- skill-ai-it `adopt_governed_files.py --apply`: recipes `roles`, `govern`, `budget`, `changelog-entry`, `move-sections`, `outline`, `section`; file roles
  in `check`; front matter on `README.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `SCRATCHPAD.md`; `scripts/role-check-baseline.json`
  (kept at `scripts/` with the other baselines; `check_scripts_layout` allows it).
- Write-backs: skill-staleness-audit (`inverse_sweep.py` `(+ .txt)` twins, two tool hazards), skill-coder (Learned: cherry-pick simulation with
  `git merge-tree`; read branch lists whole), skill-cambium (paths to `scripts/access/teleport-tunnel.sh`).
- Incident: a `grep` printing ansible-wifi `group_vars` content was blocked by the ansible-vars-guard hook (19:39); rerun with file names only.
- Open, not decided: `updated_at` format; dropping tracker items 5 and 10 (SCRATCHPAD Open items).

## 20261027_2012 — scripts/ arranged into job folders; layout and catalogue checks (v0.8.9 -> v0.9.0)

- 43 scripts moved (`git mv`) into `scripts/ansible|access|probes|capture|fleet|metrics|routing|switch/`; tests beside their script; the two
  sub-justfiles and the governance files stay at `scripts/` (operator, 2026-10-27). Pack-root and `.graylog-token` paths now resolve two levels
  up; `fleet-health.justfile` calls `./<folder>/<script>`. 102 path references in live files updated; CHANGELOG, `docs/history/`, `docs/audits/`
  and the investigation template `routing-diagnostics.justfile` left as written.
- Callers in other repos updated, no shims (operator choice): unified-network-controller `site_onboarding/identify_candidates.py`,
  `site_cables.py`, `docs/flows/parts/flows-native-platform-flows.yaml` (+ re-assembled `flows.yaml`); skill-cambium `scripts/README.md`,
  `references/site-addressing.yaml`; ansible-wifi root-governance `AGENTS.md` and the fleet-hardware-audit README; smc-resiliency `SCRATCHPAD.md`;
  enterprise-strategy `asterisk-probe-20261022/run1.sh`. Dated reports keep the old paths.
- `check_governance.py`: the scripts catalogue walks `**/*` (subfolder files were invisible to it); new `check_scripts_layout`. Both proven red, then
  green. Layout table in `scripts/README.md`; rules in `AGENTS.md`; decisions in `ARCHITECTURE.md`; branch-reach pointer in `SKILL.md`.
- Verified: unit tests (ansible, probes), `just test-deadline`, all justfiles parse, every shell script parses, `metrics/` imports, pack root and
  token resolve, `just ansible_change_reach`, `just local_knowledge_index`. Not run: recipes that need Teleport.

## 20261027_1953 — Staleness audit: branch reach, two checker gaps, version rule (v0.8.8 -> v0.8.9)

- First staleness audit of the pack (report under `docs/audits/`). Three material findings, all one cause: `rise` and `rise-multi` diverged
  at `e1077c17` (2025-12-09), so July apt fixes and url_capture v2 are not on `rise`. In-place notes in `references/08`, `09`, `13`.
- `scripts/check_governance.py`: skips the audit's gitignored snapshot when resolving bare names (every audit turned `just check` red);
  new `check_recipe_interpreter` fails a recipe that runs bare `python3`. Four recipes (`smc_change_compare`, `smc_change_runs`,
  `smc_inventory_add`, `teleport_sessions`) now use the venv. Both checks proven red, then green.
- `AGENTS.md` Tier 3: the version is bumped with every CHANGELOG entry, as the checker already required.
- Tracker item 4: `17583da3` is pushed (`origin/internet-label-rename`, `origin/unc-virtual-smc-malik-rcp01`), not merged; the first branch list
  had been cut by `head -3`.
- Open, proposed not decided: `updated_at` format — the version rule says `YYYYMMDD_hhmm`, the manifest has used `YYYY-MM-DD` throughout.

## 20261027_1947 — ansible_change_reach probe; July apt fixes and smc_ltp fix not on rise (v0.8.7 -> v0.8.8)

- New `scripts/ansible_change_reach.py` (`just ansible_change_reach <commit>`, offline test `test_ansible_change_reach.py`, 5 tests): per commit,
  on `rise`/`origin/rise` or not, the branches holding it, and whether a cherry-pick would be clean (`git merge-tree`, no checkout); optional
  inventory group hosts. Read-only; 0.65 s for two commits plus the `smc_ltp` graph.
- Its first run found `0c51cb1` (apt timer mask) and `4889af8` (`apt_info.py` without `cache.update()`) also absent from `rise` (67a44aa3): a
  `rise` run of `smc_system`/`smc_node_exporter` would revert the 2026-07-15 fix. Notes in `references/08_ansible-authoring.md` and
  `references/13_known-issues.md`; tracker items 4 and 12 updated. Cherry-pick of `17583da3` deferred to the branch-merge work (operator, 2026-10-27).

## 20261027_1937 — Open-items tracker reviewed (v0.8.6 -> v0.8.7)

- `docs/trackers/open-items-20261010_1821.md`: reviewed all 13 items against ansible-wifi `rise` 67a44aa3; a dated note on each, none closed.
  Item 4 corrected: the `smc_ltp` inventory change is committed (`17583da3`) but only on feature branches, not `rise`. Items 5 and 10 marked
  drop candidates for the operator. Last reviewed 2026-10-27, next review 2026-11-10. `just check` doc-freshness failure cleared.

## 20261027_1922 — Quoted code excerpt restored after a markdown hook bug (v0.8.5 -> v0.8.6)

- `references/07_hardware-overlay.md`: the quoted `teleport-tags-exporter.py` excerpt had been joined into one line by the markdown hook (a `rewrap.py` bug
  with quoted fences, fixed in scripts_stuff 2026-10-27); restored from git history. The generated `.ai-context/governance-pack.md` still holds the
  flattened copy until `just context-pack` is next run.

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
