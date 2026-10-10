---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_1801
---

# Changelog — skill-cambium

## Contents

- [20261010_1805 — Governed-file standard: recipes, CHANGELOG rotated (v0.7.5 -> v0.7.6)](#20261010_1805--governed-file-standard-recipes-changelog-rotated-v075---v076)
- [20261009_1806 — Sidekick writes the ePMP installer record: field formats, write OIDs, model map (v0.7.4 -> v0.7.5)](#20261009_1806--sidekick-writes-the-epmp-installer-record-field-formats-write-oids-model-map-v074---v075)
- [20261009_1705 — R195P to SM: the provisioning record, measured against every live source; towers boot together; V2000 answers SNMP (v0.7.3 -> v0.7.4)](#20261009_1705--r195p-to-sm-the-provisioning-record-measured-against-every-live-source-towers-boot-together-v2000-answers-snmp-v073---v074)
- [20261009_1547 — Force 300 / R195P boot window re-measured on 30 pairs; isolated reboots (v0.7.2 -> v0.7.3)](#20261009_1547--force-300--r195p-boot-window-re-measured-on-30-pairs-isolated-reboots-v072---v073)
- [20261009_1408 — home-48 syslog test rolled back (v0.7.1 -> v0.7.2)](#20261009_1408--home-48-syslog-test-rolled-back-v071---v072)
- [20261009_1348 — Force 300 SM and R195P: one to one, PoE dependency and failure states (device view) (v0.7.0 -> v0.7.1)](#20261009_1348--force-300-sm-and-r195p-one-to-one-poe-dependency-and-failure-states-device-view-v070---v071)
- [20261009_1341 — R195P host keys regenerated each boot (ramfs /etc); remote syslog off as provisioned; nvram enable does nothing (v0.6.52 -> v0.7.0)](#20261009_1341--r195p-host-keys-regenerated-each-boot-ramfs-etc-remote-syslog-off-as-provisioned-nvram-enable-does-nothing-v0652---v070)
- [20261009_1315 — Force 300 SM LLDP transmit failing; R195P LLDP tooling and no central logs (v0.6.51 -> v0.6.52)](#20261009_1315--force-300-sm-lldp-transmit-failing-r195p-lldp-tooling-and-no-central-logs-v0651---v0652)
- [20261009_1048 — An ePMP radio's role is its mode, not its model: cambiumSubModeType (v0.6.50 -> v0.6.51)](#20261009_1048--an-epmp-radios-role-is-its-mode-not-its-model-cambiumsubmodetype-v0650---v0651)
- [20261009_0330 — Which SM an R195P hangs from: the 3000L bridge table and Option 82, not the units (v0.6.49 -> v0.6.50)](#20261009_0330--which-sm-an-r195p-hangs-from-the-3000l-bridge-table-and-option-82-not-the-units-v0649---v0650)
- [20261009_0207 — epmp_field_probe.py: an ePMP unit's fields with values withheld, and the installer's record (v0.6.48 -> v0.6.49)](#20261009_0207--epmp_field_probepy-an-epmp-units-fields-with-values-withheld-and-the-installers-record-v0648---v0649)
- [20261009_0153 — Installer record in sysDescr, Force 300 position fields, coarse range, cnWave sites (v0.6.47 -> v0.6.48)](#20261009_0153--installer-record-in-sysdescr-force-300-position-fields-coarse-range-cnwave-sites-v0647---v0648)
- [20261009_0120 — Station table range and angle, Force 300 has no MAC table, R195P attachment not readable (v0.6.46 -> v0.6.47)](#20261009_0120--station-table-range-and-angle-force-300-has-no-mac-table-r195p-attachment-not-readable-v0646---v0647)
- [20260930_1221 — Terminology: "paid PIN" corrected to access mark (v0.6.26 -> v0.6.27)](#20260930_1221--terminology-paid-pin-corrected-to-access-mark-v0626---v0627)

## 20261010_1805 — Governed-file standard: recipes, CHANGELOG rotated (v0.7.5 -> v0.7.6)

- Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains
  `ai_it`, a second `check` line running skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate`
  recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`, `just history`); `doc_freshness.py --write-baseline`
  grandfathers existing findings (scripts/doc-freshness-baseline.json, 193 entries), so only new ones fail.
- CHANGELOG.md rotated 1,742 -> 112 lines, this entry included (90 entries to `docs/history/`); SCRATCHPAD.md (150) within budget.

## 20261009_1806 — Sidekick writes the ePMP installer record: field formats, write OIDs, model map (v0.7.4 -> v0.7.5)

- `references/05_known-issues.md` (installer record section): Sidekick as the writer, the OID it writes, units and formats of `align` and
  `test`, where `lat`/`lon` are and are not written, `sector_direction`, `type`/`replaced_mac`, the hardware-ID model map, the preferred-AP table.
  Read from the sidekick repository (operator, 2026-10-09).

## 20261009_1705 — R195P to SM: the provisioning record, measured against every live source; towers boot together; V2000 answers SNMP (v0.7.3 -> v0.7.4)

- `references/05_known-issues.md` "Which SM an R195P is cabled to": a third source, the install record in the SMC's provisioning logs (Option 82
  Remote ID and the hook's `us`), and its measurement at old-looma (63 of 66 routers name one SM; bridge table 38 of 38, burst 3 of 3, Wi-Fi clients
  6 of 6 at two or more clients and 9 of 20 at one). New paragraph: a tower's units boot together; the V2000 answers SNMP.
- Write-back from unified-network-controller (CHANGELOG 20261009_1705, correlate rules 4h and 4i).

## 20261009_1547 — Force 300 / R195P boot window re-measured on 30 pairs; isolated reboots (v0.7.2 -> v0.7.3)

- 05_known-issues.md: the router's sysUpTime starts 115-151 s after its SM's on 30 pairs (old-looma run 20261009_1417; 124-162 s on the first 19);
  a site-wide outage boots dozens of units inside one window, so the window names an SM only after an isolated premises reboot, where one SM in
  the window was the right one on 16 of 16 proven pairs (unified-network-controller `wc-local/scripts/topology/pairing.py`, rule `boot-isolated`).

## 20261009_1408 — home-48 syslog test rolled back (v0.7.1 -> v0.7.2)

- 05_known-issues.md: the operator set RemoteSyslogEnable and DBID_SYSLOG_SERVER back on home-48 and rebooted it (2026-10-09).

## 20261009_1348 — Force 300 SM and R195P: one to one, PoE dependency and failure states (device view) (v0.7.0 -> v0.7.1)

- known-issues: operator, 2026-10-09 (captured in both skill-cambium and skill-smc at the operator's request); measurements from
  unified-network-controller old-looma.

## 20261009_1341 — R195P host keys regenerated each boot (ramfs /etc); remote syslog off as provisioned; nvram enable does nothing (v0.6.52 -> v0.7.0)

- known-issues: from unified-network-controller, old-looma (home-48 tested at the operator's shell; SMC read-only), 2026-10-09.

## 20261009_1315 — Force 300 SM LLDP transmit failing; R195P LLDP tooling and no central logs (v0.6.51 -> v0.6.52)

- 05_known-issues.md: sm-55 `send_lldp: SIOCG-IF-INDEX failed for eth1`; R195P `cdpd-cp` listen heard nothing; R195P LLDP tooling; no router
  logs centrally. From unified-network-controller D10, read-only at old-looma and through Graylog.

## 20261009_1048 — An ePMP radio's role is its mode, not its model: cambiumSubModeType (v0.6.50 -> v0.6.51)

- snmp-oid-registry.yaml: `cambiumSubModeType` (.1.3.6.1.4.1.17713.21.1.1.33.0; 4 ePTP Slave, 5 ePTP Master), and that an ePTP master answers the station
  and bridge tables like a 3000L while the slave answers neither.
- 05_known-issues.md: the "Force 300 has no bridge table" note scoped to the SM.
- From unified-network-controller D10 at old-looma (read-only SNMP): an ePTP pair held as two PtMP SMs, so no reader read it.

## 20261009_0330 — Which SM an R195P hangs from: the 3000L bridge table and Option 82, not the units (v0.6.49 -> v0.6.50)

- snmp-oid-registry.yaml: 3000L `cambiumAPBridgeTable` and IF-MIB counters (they lag); Force 300 IF-MIB counters; R195P IF-MIB negative.
- 05_known-issues.md: the R195P section corrected: the AP's bridge table and the router's Wi-Fi clients joined with the SMC's Option 82 leases name the SM; old-looma names disagree for some routers.
- 06_device-api-cli-reference.md: a burst trace on cnWave port counters (tower 4's CN nic2 carries 3000L-ap-5).
- From unified-network-controller D10, read-only at old-looma (ICMP only for the bursts).

## 20261009_0207 — epmp_field_probe.py: an ePMP unit's fields with values withheld, and the installer's record (v0.6.48 -> v0.6.49)

- `scripts/epmp_field_probe.py`, recipe `just epmp-fields`: the read-only REST field check run by hand on 2026-10-09 (Force 300 position fields at hope-vale and old-looma), made persistent: one login, coordinates and secrets never printed, `--installer` decodes the low-touch record. Smoke-tested on old-looma sm-33.

## 20261009_0153 — Installer record in sysDescr, Force 300 position fields, coarse range, cnWave sites (v0.6.47 -> v0.6.48)

- `references/snmp-oid-registry.yaml`: Force 300 typed-in position fields (no azimuth); sysDescr holds the installer's JSON record at
  low-touch sites; station range is coarse (149 m steps at old-looma).
- `references/05_known-issues.md`: the installer's record (old-looma 57 of 60 radios) and cnWave controller sites. From
  unified-network-controller's D10 work.

## 20261009_0120 — Station table range and angle, Force 300 has no MAC table, R195P attachment not readable (v0.6.46 -> v0.6.47)

- `references/snmp-oid-registry.yaml`: cambiumAPConnectedSTAEntry column 29 is often 0 (not ranged); no column is an angle and the 3000L has no angle
  of arrival (2x2 MIMO, external antenna; product page read 2026-10-09); subscriber MACs are the record's + 1 with the address agreeing. Force
  300-16: no BRIDGE, Q-BRIDGE or ARP MIB over SNMP, REST bridge table lists only itself (kalumburu, 2026-10-09).
- `references/05_known-issues.md`: which subscriber an R195P is cabled to cannot be read from the units; the two-fact chain rule used instead.
  From unified-network-controller's D10 link discovery.

## 20260930_1221 — Terminology: "paid PIN" corrected to access mark (v0.6.26 -> v0.6.27)

- `references/05_known-issues.md` (dashboard bots section): the nbn bot's routine now reads "wipes every device's access mark", not "every paid PIN".
  Access at these sites is free via T&C acceptance (operator, 2026-09-30).
