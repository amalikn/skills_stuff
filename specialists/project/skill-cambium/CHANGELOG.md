---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261029_1158
---

# Changelog — skill-cambium

## Contents

- [20261029_1220 — cnWave SNMP silence is per unit (no version change)](#20261029_1220--cnwave-snmp-silence-is-per-unit-no-version-change)
- [20261029_1040 — cnWave 1.2.1 SNMP identity and E430W model name (no version change)](#20261029_1040--cnwave-121-snmp-identity-and-e430w-model-name-no-version-change)
- [20261027_2013 — skill-smc script paths moved into job folders (no version change)](#20261027_2013--skill-smc-script-paths-moved-into-job-folders-no-version-change)
- [20261020_0944 — Write-back evidence: code excerpts and screenshots (no version change)](#20261020_0944--write-back-evidence-code-excerpts-and-screenshots-no-version-change)
- [20261019_1119 — LINKPlanner best-server analysis is not footprint overlap (no version change)](#20261019_1119--linkplanner-best-server-analysis-is-not-footprint-overlap-no-version-change)
- [20261015_1750 — Volatile config keys per family; no family has a change marker (no version change)](#20261015_1750--volatile-config-keys-per-family-no-family-has-a-change-marker-no-version-change)
- [20261015_1553 — Concurrent SNMP walks lose no evidence; SNMP is not a login (no version change)](#20261015_1553--concurrent-snmp-walks-lose-no-evidence-snmp-is-not-a-login-no-version-change)
- [20261015_1442 — Radio parameters over SNMP per family; no azimuth or beamwidth anywhere (no version change)](#20261015_1442--radio-parameters-over-snmp-per-family-no-azimuth-or-beamwidth-anywhere-no-version-change)
- [20261015_1313 — A closed connection through the SMC hop is an unreachable unit (old-looma config backup) (no version change)](#20261015_1313--a-closed-connection-through-the-smc-hop-is-an-unreachable-unit-old-looma-config-backup-no-version-change)
- [20261015_1115 — LLDP as each family sends it: cnWave V5000 sends its address as the port id (no version change)](#20261015_1115--lldp-as-each-family-sends-it-cnwave-v5000-sends-its-address-as-the-port-id-no-version-change)
- [20261015_0130 — LAN MAC rule measured per family; cambiumLANMACAddress in the OID registry (v0.8.1 -> v0.8.2)](#20261015_0130--lan-mac-rule-measured-per-family-cambiumlanmacaddress-in-the-oid-registry-v081---v082)
- [20261014_2230 — MAC identity by family; Option 82 pairs no unit; as-built patterns across seven sets (v0.8.0 -> v0.8.1)](#20261014_2230--mac-identity-by-family-option-82-pairs-no-unit-as-built-patterns-across-seven-sets-v080---v081)
- [20261014_1956 — ePMP ARP MAC = LAN + 1 confirmed on Force 300-25 (v0.7.10 -> v0.8.0)](#20261014_1956--epmp-arp-mac--lan--1-confirmed-on-force-300-25-v0710---v080)
- [20261013_2226 — Sidekick commissioning leaves no installer record; as-built sets (v0.7.9 -> v0.7.10)](#20261013_2226--sidekick-commissioning-leaves-no-installer-record-as-built-sets-v079---v0710)
- [20261011_1744 — Correction: SM bridge table shows the router (show bridge sta), intermittently (v0.7.8 -> v0.7.9)](#20261011_1744--correction-sm-bridge-table-shows-the-router-show-bridge-sta-intermittently-v078---v079)
- [20261011_1431 — Router-to-SM facts by site type; no CFM on ePMP (v0.7.7 -> v0.7.8)](#20261011_1431--router-to-sm-facts-by-site-type-no-cfm-on-epmp-v077---v078)
- [20261011_1359 — Force 300 SM CLI: no neighbour or ARP view of its router (v0.7.6 -> v0.7.7)](#20261011_1359--force-300-sm-cli-no-neighbour-or-arp-view-of-its-router-v076---v077)
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

**20261016_2115 — v0.8.3:** Reference 03 adds observed as-built label variants, unique-match and conflict guards from UNC's conversion audit. No device changes.

## 20261029_1220 — cnWave SNMP silence is per unit (no version change)

Learned 2026-10-29 (b) in `references/05_known-issues.md`: firmware-1.4 cnWave units at one site split between answering SNMP and silent; read the silent ones by login.

## 20261029_1040 — cnWave 1.2.1 SNMP identity and E430W model name (no version change)

Learned 2026-10-29 in `references/05_known-issues.md`: cnWave 1.2.1 answers SNMP as plain net-snmp with sysName `node-<mac>`; an
E430W reports `cnPilot E430W`. From unified-network-controller's aurukun onboarding.

## 20261027_2013 — skill-smc script paths moved into job folders (no version change)

`scripts/README.md` and `references/site-addressing.yaml` now name `skill-smc/scripts/access/teleport-tunnel.sh` (skill-smc arranged its scripts by job,
2026-10-27). No content change.

## 20261020_0944 — Write-back evidence: code excerpts and screenshots (no version change)

Write-back contract: every entry recording how something is done carries a code excerpt (source path, commit) and, for a visual surface, a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` (operator, 2026-10-20). In `SKILL.md`.

## 20261019_1119 — LINKPlanner best-server analysis is not footprint overlap (no version change)

references/01_overview.md (RF planning) gains a Learned 2026-10-16 entry from LINKPlanner 6.4.3 documentation, found during unified-network-controller coverage research. Written in the 2026-10-19 backlog audit of 15–17 Oct.

## 20261015_1750 — Volatile config keys per family; no family has a change marker (no version change)

- `references/06_device-api-cli-reference.md`: consecutive backups show ePMP status keys, Enterprise `system.clock` and `system.reboot_reason` change
  without a real change; an R195P `nvram.cns_cloud_id` clear is real; no family exposes a config version or checksum. Found by unified-network-controller's
  change-only config backups.

## 20261015_1553 — Concurrent SNMP walks lose no evidence; SNMP is not a login (no version change)

- `references/05_known-issues.md`: four SM bridge walks at once from the SMC found as many units as one at a time (old-looma, 2026-10-15),
  and SNMP does not count toward the ePMP HTTPS login lockout. Found by unified-network-controller's onboarding speedups.

## 20261015_1442 — Radio parameters over SNMP per family; no azimuth or beamwidth anywhere (no version change)

- `references/snmp-oid-registry.yaml` and `references/06_device-api-cli-reference.md`: read live at old-looma (read-only): ePMP 3000L and
  Force 300 give frequency, width, power and antenna gain; XV2 per radio channel, width and power (unit assumed dBm); cnWave and R195P nothing
  usable; azimuth only as the installer's `sector_direction` in sysDescr, beamwidth from no family. Found by unified-network-controller's coverage map.

## 20261015_1313 — A closed connection through the SMC hop is an unreachable unit (old-looma config backup) (no version change)

- `references/05_known-issues.md`: new section. 15 backup failures at old-looma (ePMP SM TLS EOF, R195P SSH kex closed) were 12 units the SMC
  could not reach and 3 flapping; not TLS; cost per unit measured (SM 10-14 s, R195P 40-42 s, unreachable 11-12 s). Found by unified-network-controller.

## 20261015_1115 — LLDP as each family sends it: cnWave V5000 sends its address as the port id (no version change)

- `references/05_known-issues.md` LLDP section: port id subtype and description per family from a TP-Link lldpRemTable (ePMP 3000L, XV2:
  macAddress + `eth0`; cnWave V5000 1.5.2: networkAddress(4) with the management IPv4, empty description). Found by unified-network-controller's
  Neighbours tab showing `10.255.4.10` as a local port (yakanarra).

## 20261015_0130 — LAN MAC rule measured per family; cambiumLANMACAddress in the OID registry (v0.8.1 -> v0.8.2)

- `references/06_device-api-cli-reference.md`: per-family identify vs ARP measurements (ePMP identify = ARP - 1 on 75 units; R195P identify
  = ARP on 52, both the management MAC; Enterprise Wi-Fi and TP-Link equal ARP) and a correction: apn-unc01's R195P records hold the management
  MAC. `references/snmp-oid-registry.yaml`: `cambiumLANMACAddress` (MIB only, live GET unverified). From unified-network-controller, 2026-10-15.

## 20261014_2230 — MAC identity by family; Option 82 pairs no unit; as-built patterns across seven sets (v0.8.0 -> v0.8.1)

- `references/06_device-api-cli-reference.md`: an R195P identifies by its management MAC (base + 1) and an ePMP unit by its LAN MAC, so a MAC compare
  must choose one kind per family (unified-network-controller register on old-looma and umoona, 2026-10-14).
- `references/05_known-issues.md`: old-looma's lease and ARP counts by subnet (2026-10-14): the units' management addresses are static and Option 82
  alone pairs no unit with its SM.
- `references/03_asset-register-conventions.md`: patterns across the seven as-built sets (beagle-bay, pandanus-park, umoona, wangkatjungka, warburton,
  yakanarra with old-looma) and ports matched to drawn lines by position (unified-network-controller `unc.tasks.asbuilt`, 2026-10-14).

## 20261014_1956 — ePMP ARP MAC = LAN + 1 confirmed on Force 300-25 (v0.7.10 -> v0.8.0)

- `references/03_asset-register-conventions.md`: wandawuy's Force 300-25 PtP pair shows the same LAN + 1 ARP MAC as the 3000L units; storing the ARP MAC
  reads as drift at OpenWISP registration. Source: unified-network-controller, wandawuy register stage, 2026-10-14.

## 20261013_2226 — Sidekick commissioning leaves no installer record; as-built sets (v0.7.9 -> v0.7.10)

- **Sidekick commissioning leaves no installer record** (`references/05_known-issues.md`, after the low-touch installer-record section; from unified-network-controller
  CHANGELOG 20261012_0019, recorded late 2026-10-13): all 43 wangkatjungka SMs (non-low-touch, Sidekick-commissioned) answer a blank
  `snmpSystemDescription`, as do mowanjum's and kalumburu's; only the low-touch hook writes the JSON record.
- **As-built sets** (`references/03_asset-register-conventions.md`, new section; from unified-network-controller 2026-10-09/13, written back late): what a
  site's as-built set holds (chassis and tower drawings, KMZ, coverage map), its labels (APn, WifiBridge_n, F25, CIE/CEE, SWP n), how to read it as text
  (unified-network-controller `wc-local/scripts/site_onboarding/asbuilt_read.py`), its known v1.0 flaws (copied tower labels), and its use as the drift reference for deployed sites (format unc-as-built/1).

## 20261011_1744 — Correction: SM bridge table shows the router (show bridge sta), intermittently (v0.7.8 -> v0.7.9)

- **Correction: the Force 300 SM names its router on its LAN port, intermittently** (references/05_known-issues.md): `show bridge sta` on
  4.7.0.1 (not `show bridge sm`), the same `cambiumSTABridgeTable` as the web UI, REST and SNMP; the table flushes, so sample repeatedly. The
  2026-10-09 "only Own" and this morning's "no SM-side table" statements are corrected. Read-only, SNMP survey of 20 pairs plus 5 logins.

## 20261011_1431 — Router-to-SM facts by site type; no CFM on ePMP (v0.7.7 -> v0.7.8)

- **Site-type differences for router-to-SM placement** (references/05_known-issues.md, new 2026-10-11 entry): boot order reversed at kalumburu
  (router 1-167 s before its SM), an AP without Option 82 leaves the Remote ID empty while the description names the SM, the Omni 3000L bridge
  table missing routers, PtP roles from the mode, and no CFM MIB on ePMP 4.7.0.1. Read-only; asked by unified-network-controller.

## 20261011_1359 — Force 300 SM CLI: no neighbour or ARP view of its router (v0.7.6 -> v0.7.7)

- **Force 300 SM CLI cannot name its router** (references/05_known-issues.md, 2026-10-09 LLDP entry): on old-looma sm-47 (4.7.0.1) `show lldp-neighbors`
  returns an empty list and `show arp` holds only the SMC; `show ?` in a PTY hangs the probe. Read-only, two logins. Asked by unified-network-controller
  (topology accuracy, step 5).

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
