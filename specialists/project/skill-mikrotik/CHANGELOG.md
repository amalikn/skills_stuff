# Changelog

## 20261008_1303 — reset-mac-address script for one switch at a time (v0.1.22 -> v0.1.23)

- `scripts/mikrotik_mac_reset.py` (stdlib only), from the glen-hill session of 2026-10-08 (known issue 11): for one `<smc> <ip>` it saves the before-state
  (routerboard, ethernet and bridge `print detail`) to a capture folder, reports each port's `mac-address` against `orig-mac-address` and each bridge's MAC,
  and plans only. With `--apply` it runs `/interface ethernet reset-mac-address [find]` through `scripts/mikrotik_exec.sh` with `MT_ALLOW_WRITE=1` for that call,
  waits, reads back (retried once on a failed forward, exit 4) and verifies every port at its factory MAC and every `auto-mac` bridge on one of them. JSON
  summary on stdout for an inventory update. Refuses a list of hosts (one switch at a time, operator 2026-10-08). Recipe `just mac_reset`; catalogued in
  `scripts/README.md`; pointer added to `references/05_known-issues.md` #11.
- Smoke test: `--help` clean; plan-only run against glen-hill-smc01 10.255.0.5 (already reset) reported all five ports at their factory MACs, all four
  bridges on a factory MAC, `result: nothing_to_do`, exit 0, nothing written. `--apply` not run anywhere.

## 20261008_1234 — RouterOS firmware fetch and verify script promoted (v0.1.21 -> v0.1.22)

- `scripts/routeros_firmware_fetch.py` (stdlib only), from two session scripts used for 7.8, 7.12.2, 7.23.7 and 7.24.5: fetches one version's `routeros`,
  `all_packages`, `wireless` (mipsbe, skipped when the host serves the 0-byte pre-7.13 placeholder) and `netinstall` files, resumes truncated ones with HTTP
  Range, verifies size, ETag md5 and the published `.sha256` (saved beside the file; none for 7.8 or 7.12.x), prints manifest-ready YAML, stops on HTTP 429.
  `--verify-only` downloads nothing. Recipe `just firmware_fetch`; catalogued in `scripts/README.md`.
- Smoke test: `--verify-only 7.12.2` reported all six files match (size and ETag md5; sha256 equal to the manifest's), no download; `--verify-only 7.23.7
  --arch mipsbe` five of five including the published sha256; `--help` clean.
- Linked from `references/07_equipment-and-snmp.md` (Firmware) and the `references/firmware-manifest.yaml` header.

## 20261008_1227 — the team's provisioning script added as a read-only reference (v0.1.20 -> v0.1.21)

- `450gmk3_v1.1.py` (pack root): the Pi script the team uses to build RB450Gx4 switches, supplied by the operator. Read-only: never edited; a change goes
  into our own version under `scripts/` (operator, 2026-10-08). The operator chose to commit it as is, admin password included (2026-10-08); not yet committed.
- `references/06_provisioning.md` corrected against the script: firmware goes over **SFTP**, not TFTP; first contact is the factory `192.168.88.1` with an
  empty password; new *The script file* (path, sha256, dependencies, files it needs) and *Defects visible in the code* sections, and the full step list
  (bench setup, re-run detection and reset offer, RB450Gx4 check, the v1.1 changelog file it leaves on flash as a version marker, RouterOS and RouterBoard 7.8,
  read-back checks). The two command batches match the documented ones exactly (39 and 32 commands).
- `references/05_known-issues.md`: 12 partly closed (script and first contact known; owner and AP provisioning open); 13 corrected (the password is now in
  a file, the reference script); new 16 (which script version built each switch, via the flash marker) and 17 (two `str`-in-`bytes` checks that would
  crash under Python 3, from reading the code).
- `RUNBOOK.md`, `SKILL.md`: routing names the script; the pack's local `AGENTS.md` carries the read-only rule.

## 20261008_1226 — reset-mac-address tested on one switch (known issue 11)

- glen-hill-switch01 (operator approved): `/interface ethernet reset-mac-address [find]` works on RouterOS 7.8; ports back to their factory MACs and the
  `auto-mac` bridges followed without a reboot; no outage seen. `references/05_known-issues.md` #11 and `references/01_overview.md` updated. Version 0.1.20.

## 20261008_1207 — RouterOS 7.12.2 firmware files, the required stop from 7.8 (v0.1.18 -> v0.1.19)

- `firmware-files/7.12.2/`: `routeros` (arm, mipsbe), `all_packages` (arm, mipsbe) and `netinstall` (.zip, .tar.gz) for 7.12.2 (2023-12-20), the last 7.12.x on
  download.mikrotik.com (7.12.3 returns 404). The 7.13 changelog requires an upgrade from before 7.12 to pass through 7.12.x, so the path is 7.8 -> 7.12.2 ->
  7.23.7 or 7.24.5. No separate `wireless` package (bundled; the host serves a 0-byte placeholder) and no published `.sha256` for 7.12.x.
- `references/firmware-manifest.yaml`: six 7.12.2 entries with size, sha256, md5 and ETag check; header notes the intermediate step.
- `references/07_equipment-and-snmp.md` (Firmware): 7.12.2 is kept; the "no 7.12.x image" sentence replaced. `SKILL.md`, `RUNBOOK.md` and the vendor-sources readme list 7.12.2.
- `manifest.json`: 0.1.18 -> 0.1.19.

## 20261008_1149 — SNMP on four more sites, identical MACs on wh, bridge host table, firmware files and the 7.12 stop (v0.1.17 -> v0.1.18)

VERIFIED-OBSERVED 2026-10-08 from unified-network-controller work over Teleport apn.

- `references/07_equipment-and-snmp.md` (SNMP): read-only SNMP enabled (`just snmp_community enable`, the vault read-only community, allowed from the SMC only, `public` disabled) on the
  20-mile switch and AP, adjamarragu switch and AP, areyonga switch and glen-hill switch; a table lists every enabled unit with its serial. Each answered sysDescr and the mtxr serial.
- `references/07_equipment-and-snmp.md` (Firmware, Vendor sources): firmware files for 7.8, 7.23.7, 7.24.5 in `firmware-files/` with `references/firmware-manifest.yaml` (committed, operator
  2026-10-08); upgrade from 7.8 needs a stop at 7.12.x for the wireless package conversion (VERIFIED-DOC, 7.13 changelog). Manifest linked from the vendor-sources readme, RUNBOOK and SKILL.md.
- `references/05_known-issues.md` #14: the enabled units listed.
- `references/01_overview.md`: identical port MACs at 20-mile and areyonga (`wh`), identity `450Gx4` / `AP1` everywhere, so serial is the only identity; `wh` row adds areyonga and glen-hill
  (glen-hill's `.20` is a Cambium XV2-2T0, areyonga's did not answer); which unit is on each port from the bridge host table, `ethN-vlanV` naming, the ATA cross-reference to skill-smc.
- `references/03_routeros-cli-reference.md`: `/interface bridge host print where !local` and the empty `/ip neighbor print`.
- `manifest.json`: 0.1.17 -> 0.1.18.

## 20261007_2034 — arrkapa switch log: clock and retention read correctly (v0.1.16 -> v0.1.17)

- `references/04_failure-modes.md`: the arrkapa switch clock ran about 8 h 25 min slow and its log times go backwards around crashes; take the loop cadence
  from the SMC kernel log (eth0 down 249 times 01:28-16:00), not the switch log.
- `references/05_known-issues.md` #3 and #4, `references/03_routeros-cli-reference.md`, `SKILL.md`: the log survived 43 crash reboots on that unit
  (mechanism unverified), so "lost on reboot" was too strong. Site dark again from 20:08 AEDT; capture queued with `WAIT_UP=1`.

## 20261007_2009 — Scripts and recipes renamed to snake_case (v0.1.15 -> v0.1.16)

- Operator (2026-10-07): snake_case for every code file and command name (governance coding-guide). `scripts/mikrotik_exec.sh`,
  `scripts/mikrotik_fleet_survey.sh`, `scripts/mikrotik_site_capture.sh`, `scripts/mikrotik_snmp_community.py` and `scripts/survey_summary.py` (git mv
  from the kebab names); recipes `mib_oids`, `fetch_doc`, `product_text`, `snmp_community`. Every live reference updated, here and in UNC's device-type
  matrix and the ansible-wifi SCRATCHPAD; older entries below keep the names they were written with.
- `scripts/check_governance.py`: `RENAMED_PATHS` resolves an old name in this CHANGELOG only; `check_file_naming` (from skill-ai-it) fails on a new
  kebab-case code file. Renamed scripts re-tested live on amuroona (read-only).

## 20261007_1938 — Every script function documented; check_function_docs (v0.1.14 -> v0.1.15)

- Operator (2026-10-07): every function gets proper comments, like ansible-wifi's `roles/smc_rise_watchdog/templates/rise_watchdog.py.j2`. Docstrings added to the 23 undocumented
  functions (`scripts/check_governance.py`, `scripts/confluence_fetch.py`, `scripts/mib_oids.py`, `scripts/mikrotik-snmp-community.py`, `scripts/snmp_via_smc.py`
  and its embedded SMC agent, `scripts/survey-summary.py`), comment blocks above the two shell functions, section banners in the agent.
- `scripts/product_text.py` rewritten as documented functions; its retrieval date is now today's, not a fixed 2026-10-07.
- `scripts/check_governance.py` `check_function_docs`: fails on a Python function without a docstring (embedded code included) or a shell function without
  a comment above it; on the committed scripts it reports 11. `AGENTS.md` working rule.
- The documented agent re-tested live on amuroona (read-only GET and walk).

## 20261007_1909 — SNMP write test on amuroona's switch; redaction fix (v0.1.13 -> v0.1.14)

- Operational (operator approved; the operator added the temporary read-write community, removed after the test): `sysName` SET applied and restored
  (450Gx4 -> 450Gx4-snmpw -> 450Gx4, 19:05-19:06, confirmed over SSH); `sysLocation` SET returns noError but is not applied; the read-only community's
  SET is refused (readOnly). End state: SNMP on, read-only community only, `public` disabled, identity and location as before.
- `references/snmp-oid-registry.yaml`: sysName `access: rw` with the GET-lag note; sysLocation negative recorded. `references/07_equipment-and-snmp.md`,
  known issue 14 updated.
- `scripts/mikrotik-snmp-community.py`: redacts every community name in its output except `public`. Before this, a run with the read-write entry printed
  the read-only community in clear (operator's terminal, 2026-10-07).

## 20261007_1901 — SNMP verified on amuroona; GPS recorded per type (v0.1.12 -> v0.1.13)

- Operational (operator approved): SNMP enabled read-only on amuroona's switch (10.255.0.5, 18:51) and AP (10.255.0.20, 18:53); default `public`
  disabled; vault community allowed from the SMC only. No write was made: adding a read-write community for the write test was refused by this
  session's permission check.
- `references/snmp-oid-registry.yaml`: 25 OIDs verified on the switch and 21 on the AP (moved from `candidates`, with values); empty tables noted; a
  `gps` block per type (operator: check every vendor's devices for GPS): neither gives coordinates.
- `references/07_equipment-and-snmp.md` SNMP section and known issue 14 rewritten from the results (gauge temperature in whole degrees, PoE state only,
  sysObjectID not a model key, AP radio at 2.4 GHz).

## 20261007_1849 — Pinned runtime, SNMP tools, known issue 14 findings (v0.1.11 -> v0.1.12)

- Runtime isolation (operator): `.mise.toml` (Python 3.14), `requirements.txt` (stdlib only), venv in the working-cache peer
  `/Volumes/Data/_ai/_skills/skills-working-cache/skill-mikrotik/.venv` (`just bootstrap`, `just runtimes`); every recipe goes through `{{py}}` and
  `_require-venv`; `scripts/mikrotik-exec.sh` and `scripts/mikrotik-fleet-survey.sh` take Python from `MT_PY`. `scripts/check_governance.py` now fails on shebang-run
  recipes and inline interpreters (from skill-ai-it).
- `justfile`: `exec`, `snmp` and `snmp-community` use positional arguments, so a multi-word RouterOS command reaches the script whole (it was split into
  words and refused by the read-only guard).
- `scripts/snmp_via_smc.py` (new): SNMP v2c get/walk/set from the SMC with no net-snmp, community from KeePass on stdin. Tested only against a unit with
  SNMP off (clean timeout).
- `scripts/mikrotik-snmp-community.py` (new): enable/remove/show a community, value redacted. Not yet run on a device: the session's permission check
  refused remote writes.
- `references/05_known-issues.md` item 14: default `public` community on both units, no `snmp-set` in RouterOS 7.8, SMC has Python but no net-snmp.

## 20261007_1655 — Equipment, SNMP OID registry, MIBs and vendor sources (v0.1.10 -> v0.1.11)

- `references/vendor-sources-20261007_1640/` (new, operator: research kept in the skill, MIBs too): MIKROTIK-MIB for RouterOS 7.8 and 7.24.5, help.mikrotik.com
  pages, product pages and PDFs, changelogs 7.8 to 7.24.5, three forum threads (secondary), indexed in its `readme.md`.
- `references/snmp-oid-registry.yaml` (new): both models with equipment facts, verified `routeros_cli` reads, and candidate OIDs resolved from the 7.8 MIB;
  `oids` empty because SNMP is disabled on every unit checked.
- `references/07_equipment-and-snmp.md` (new): specs, SNMP, firmware (no IPQ-40xx kernel fix up to 7.24.5), the cpu-frequency warning, MAC commands.
- `references/05_known-issues.md`: items 8 and 11 updated; new 14 (SNMP disabled) and 15 (cpu-frequency warning).
- `scripts/mib_oids.py`, `scripts/confluence_fetch.py`, `scripts/product_text.py` promoted from the research session, with `just mib-oids`, `fetch-doc`,
  `product-text`.

## 20261007_1623 — Mk3 connection diagram: what is on each port, rct vs wh (v0.1.9 -> v0.1.10)

- `references/mk3-connection-diagram-v0.5.pdf` (new): the operator's Mk3 site diagram, moved here from the pack root (was `Mk3 Connection Diagram v0.5 1.pdf`).
- `references/01_overview.md`: port table names the real devices (ether2 and ether3 are the satellite modem's Uni-D1 and Uni-D2, not a separate second WAN;
  ether4 the Dallas Delta ATA UI on `rct`; ether5 the PoE AP, Metal on `rct` and Cambium on `wh`); new Site design section (untagged-internet reason for
  ether1 in `bridge-vlan521`, ATA and Thuraya backup, AP addressing, SMC Wi-Fi SSID).
- skill-smc 0.1.98: SMC-side addressing from ansible-wifi compared with the diagram (diagram stale on management DNS and a `192.168.100.2` note).

## 20261007_1620 — Cloned MACs come from the provisioning script, not a backup (v0.1.8 -> v0.1.9)

- **Correction:** v0.1.4 put the cloned MACs down to one binary backup restored onto every switch. The operator described the real process (a Raspberry Pi
  pushes `routeros-7.8-arm.npk` over TFTP and two SSH command batches) and pasted the commands: part 1 pins `mac-address=` on ether1–ether5. The backup
  explanation and its vendor-doc quote are removed from `references/01_overview.md`; the new-switch fix is now deleting those five commands from the script.
- `references/06_provisioning.md` (new): the process, what the script sets, the issues it leaves on every unit, and the commands one per line, password redacted.
- `references/01_overview.md`: port layout and ether5 PoE confirmed by the script.
- `references/05_known-issues.md`: items 3 (time zone and NTP) and 4 (logging to disk) updated from the script; new 12 (script location, owner, APs) and 13
  (shared clear-text admin password, MAC access on all ports, HTTP on, protected RouterBOOT off).
- `RUNBOOK.md`, `SKILL.md`: routing for `references/06_provisioning.md`. `SCRATCHPAD.md`: cause corrected.

## 20261007_1605 — arrkapa root cause: switch kernel-failure / watchdog reboot loop (v0.1.7 -> v0.1.8)

- `references/04_failure-modes.md`: arrkapa finding with evidence; new signature section (watchdog timer + kernel failure loop) and how to tell it from a power cut.
- `references/05_known-issues.md`: item 1 closed; batavia-downs left open.

## 20261007_1602 — Fleet survey host list without word splitting (v0.1.6 -> v0.1.7)

- `scripts/mikrotik-fleet-survey.sh`: Teleport host list read one per line into an array instead of an unquoted `$(...)` (shellcheck SC2046); works on
  bash 3.2 and with an empty list under `set -u`.

## 20261007_1557 — Operational record and memory channel (v0.1.5 -> v0.1.6)

- Operational, no pack file changed: cross-links added in skill-smc and skill-cambium `SKILL.md` Related Skills and an "Also invoke `skill-mikrotik`" rule in
  ansible-wifi `AGENTS.md`; enterprise-strategy `AGENTS.md` Knowledge sources and `README.md` list this pack (operator: use it like skill-cambium and
  skill-smc), and its three running sessions were messaged. First fleet survey attempt aborted at ~8 sites (per-command SSH sessions, ~4 h ETA); batching fixed
  it. Two devices refused the correct password for a few minutes at about 14:30 (known issue 7).
- Memory: memory-keeper channel `skill-mikrotik` and project-context project `skill-mikrotik` created at this slurp (keys and IDs in `SCRATCHPAD.md`). Until
  then every entry about this pack sat under `ansible-wifi`.

## 20261007_1542 — Cloned-MAC remedy: missing steps and open item (v0.1.4 -> v0.1.5)

- `references/01_overview.md`: remedy split into new switches, existing fleet and rollout; adds why MAC lines must be stripped (golden unit is a clone), setting
  the admin password after `/import`, and one switch, then canary, then fleet.
- `references/05_known-issues.md`: item 11, Ethernet `reset-mac-address` and bridge MAC follow-through untested.
- `SCRATCHPAD.md`: cloned-MAC state and next action.

## 20261007_1534 — Cloned MACs: cause from vendor docs, factory MAC observed, remedy proposed (v0.1.3 -> v0.1.4)

- `references/01_overview.md`: binary backup restores MACs (VERIFIED-DOC); amuroona orig vs current MAC; APs unaffected; text-export template and `reset-mac-address` remedy, proposed not applied.

## 20261007_1525 — KeePass entry renamed; rct single-AP fact (v0.1.2 -> v0.1.3)

- KeePass entry is now `Network/mikrotik switch & metal ap` (operator fixed the spelling); `scripts/mikrotik-exec.sh` default and all references updated.
- `references/01_overview.md`: rct sites have one AP and no point-to-point bridges (operator).

## 20261007_1501 — Cloned switch MACs; wh AP verified as Cambium (v0.1.1 -> v0.1.2)

- `references/01_overview.md`: all 294 rct switches share port MACs (`6C:3B:6B:53:F0:D5` on ether1) despite unique serials; wh `.20` verified as a Cambium XV2-2T0 (previously stated without checking).

## 20261007_1443 — rct fleet survey results, wh canary (v0.1.0 -> v0.1.1)

- `references/01_overview.md` (new content): devices per flavor, delye port/VLAN map, power (rct ~24-28 V, wh 48 V), fleet ranges from the 297-site survey.
- `references/04_failure-modes.md`: fleet port-level link-down patterns (ether1 quiet, ether4 phone and ether2 NTD noisy).
- `references/05_known-issues.md`: rewritten as a list; item 2 narrowed (wh has the switch, 48 V, no MikroTik AP); items 9 (rollah ether1) and 10 (kwala sensors) added.
- `scripts/survey-summary.py` (new, read-only); `scripts/mikrotik-exec.sh` batching and login retry; survey duration corrected to 19 minutes.

## 20261007_1422 — Pack created (v0.1.0)

- Seeded from the arrkapa (`rct`) outage investigation: the operator added the MikroTik login to KeePass (`Network/microtik switch & metal ap`) and asked for a pack built like skill-cambium and
  skill-smc, with a write-back loop.
- `SKILL.md` (triggers, Standing Write-Back Contract, decision tree), `AGENTS.md` (self-evolution loop), `RUNBOOK.md`, `manifest.json`, `justfile`, `README.md`, `SCRATCHPAD.md`.
- `references/01..05`: overview and fleet ranges, device access, RouterOS CLI reference, failure modes (arrkapa trunk silence, delye SMC-port flapping, TSTIK switch power-cycles), known issues.
- `scripts/`: `scripts/mikrotik-exec.sh` (read-only RouterOS over a Teleport port-forward, password never on the SMC, batched sessions, login retry), `scripts/mikrotik-fleet-survey.sh`, `scripts/mikrotik-site-capture.sh`
  (`WAIT_UP=1`), `check_governance.py` (copied from skill-cambium, registries retuned).
- Tested read-only on delye-smc01 and amuroona-smc01; fleet survey of reachable `rct` sites in `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/mikrotik-survey-20261007_1421/`.
