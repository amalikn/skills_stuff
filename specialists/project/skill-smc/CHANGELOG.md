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

# skill-smc Changelog

## Contents

- [20261010_1805 — Governed-file standard: recipes, records rotated (v0.3.6 -> v0.3.7)](#20261010_1805--governed-file-standard-recipes-records-rotated-v036---v037)
- [20261009_1806 — Sidekick and the low-touch hook: confirmed and unplugged releases a unit (v0.3.5 -> v0.3.6)](#20261009_1806--sidekick-and-the-low-touch-hook-confirmed-and-unplugged-releases-a-unit-v035---v036)
- [20261009_1714 — What else the low-touch hook logs record: state and secret, events, the SM by its own MAC, preferred_ssid names the AP (v0.3.4 -> v0.3.5)](#20261009_1714--what-else-the-low-touch-hook-logs-record-state-and-secret-events-the-sm-by-its-own-mac-preferred_ssid-names-the-ap-v034---v035)
- [20261009_1705 — The provisioning hook's per-unit logs are a low-touch site's install-time pairing (v0.3.3 -> v0.3.4)](#20261009_1705--the-provisioning-hooks-per-unit-logs-are-a-low-touch-sites-install-time-pairing-v033---v034)
- [20261009_1652 — Low-touch provisioning logs live only on the SMC; sizes per site, backup in UNC (v0.3.2 -> v0.3.3)](#20261009_1652--low-touch-provisioning-logs-live-only-on-the-smc-sizes-per-site-backup-in-unc-v032---v033)
- [20261009_1552 — An SMC's DHCP history lives in a short journal and is not a unit's boot history (v0.3.1 -> v0.3.2)](#20261009_1552--an-smcs-dhcp-history-lives-in-a-short-journal-and-is-not-a-units-boot-history-v031---v032)
- [20261008_1206 — Pi identity probe and rct site ATA settings reader promoted to scripts/ (v0.2.2 -> v0.2.3)](#20261008_1206--pi-identity-probe-and-rct-site-ata-settings-reader-promoted-to-scripts-v022---v023)
- [20261008_1147 — Raspberry Pi SMC identity and ports, rct site ATA, vendor sources linked (v0.2.1 -> v0.2.2)](#20261008_1147--raspberry-pi-smc-identity-and-ports-rct-site-ata-vendor-sources-linked-v021---v022)
- [20260930_1221 — Terminology: access is free via T&C acceptance, not a paid PIN (v0.1.75 -> v0.1.76)](#20260930_1221--terminology-access-is-free-via-tc-acceptance-not-a-paid-pin-v0175---v0176)
- [20260930_1202 — bot-cw-dashboard wipes PIN marks on koonibba/amata; a zero ECLIPSE_MARK count is not normal (v0.1.73 -> v0.1.74)](#20260930_1202--bot-cw-dashboard-wipes-pin-marks-on-koonibbaamata-a-zero-eclipse_mark-count-is-not-normal-v0173---v0174)
- [20260911_1120 — bungardi-smc01 confirmed as third broken site; Eclipse "PIN Last Issued" admin report documented as a third corroborating evidence source (v0.1.35 -> v0.1.36)](#20260911_1120--bungardi-smc01-confirmed-as-third-broken-site-eclipse-pin-last-issued-admin-report-documented-as-a-third-corroborating-evidence-source-v0135---v0136)
- [20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update](#20260626_1845--v013-project-coherence-checklist--references10-13-content-update)

## 20261010_1805 — Governed-file standard: recipes, records rotated (v0.3.6 -> v0.3.7)

- Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains
  `ai_it`, a second `check` line running skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate`
  recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`, `just history`); `doc_freshness.py --write-baseline`
  grandfathers existing findings (scripts/doc-freshness-baseline.json, 27 entries), so only new ones fail.
- CHANGELOG.md rotated 2,046 -> 152 lines, this entry included (118 entries to `docs/history/`), and SCRATCHPAD.md 561 -> 240 lines
  (62 entries); SCRATCHPAD stays over budget (24 undated entries and 3 open items kept) and is a ratchet finding until they are reviewed.

## 20261009_1806 — Sidekick and the low-touch hook: confirmed and unplugged releases a unit (v0.3.5 -> v0.3.6)

- `references/13_known-issues.md`: what Sidekick is and how it is deployed, its addresses per family, the hook's release condition (`confirmed`
  and no ping to 169.254.1.17), what the hook copies from the record, `lotno` versus `locid`, `tower` dropped, replacement records. Read from the
  sidekick repository (operator, 2026-10-09).

## 20261009_1714 — What else the low-touch hook logs record: state and secret, events, the SM by its own MAC, preferred_ssid names the AP (v0.3.4 -> v0.3.5)

- `references/13_known-issues.md`: beyond the 0.3.4 pairing section: the state dump, events, more description keys, and the cnMaestro client secret;
  upstream-wait MAC = Remote ID - 1 (60 of 60); `preferred_ssid` `WifiBridge_N` = AP `3000L-ap-N` (59 of 59); measured on old-looma's logs.

## 20261009_1705 — The provisioning hook's per-unit logs are a low-touch site's install-time pairing (v0.3.3 -> v0.3.4)

- `references/13_known-issues.md`: new section "the provisioning hook's logs are the site's install-time pairing": what each `log.<MAC>` records
  (vendor class, Option 82 Remote ID, the cnMaestro description with `us`, `lot no`, `ext`, `locid`); at old-looma 63 of 66 routers name one SM
  and 3 tower routers have an empty Remote ID; an XV2 beyond a PtP link reports the first SM on its path; 10 logged units never landed in
  Nautobot; read reduced on the box. Complements the 0.3.3 entry on where the logs live and their backup.
- Write-back from unified-network-controller (CHANGELOG 20261009_1705, reader `smc-dhcp-relay`, correlate rule 4h).

## 20261009_1652 — Low-touch provisioning logs live only on the SMC; sizes per site, backup in UNC (v0.3.2 -> v0.3.3)

- `references/13_known-issues.md`: `/var/local/cnmaestro-provisioning` (one log per provisioned unit, Option 82 Remote ID included) is kept only
  on the box; sizes read on seven low-touch SMCs; the copy is unified-network-controller `just wc::provisioning-backup` (operator, 2026-10-09:
  keep them in case an SMC is replaced).

## 20261009_1552 — An SMC's DHCP history lives in a short journal and is not a unit's boot history (v0.3.1 -> v0.3.2)

- 13_known-issues.md: dhcpd logs to the journal only (about 13 hours at old-looma-smc01), Prometheus keeps no per-unit history, and low-touch
  units leave DHCP after provisioning; read-only probe 2026-10-09 for unified-network-controller pairing.

## 20261008_1206 — Pi identity probe and rct site ATA settings reader promoted to scripts/ (v0.2.2 -> v0.2.3)

Promoted from a 2026-10-08 unified-network-controller session (scratchpad originals, generalised).

- New `scripts/pi_identity_probe.sh`: read-only Raspberry Pi SMC identity probe over Teleport; `--proxy` required, node names only, exits 1 on an unreachable
  node. Recipe `just pi_identity_probe <proxy> <node>...`. Smoke-tested 2026-10-08 on 20-mile-smc01 (teleport.apn.au) and a non-existent node (rc 1).
- New `scripts/ata_settings_read.py`: reads the Dallas Delta DDC_VoIP-m settings, phonebook and digitmap pages through each SMC with the empty PIN,
  drops secret-named fields on the SMC and again locally, tolerates the short body, reports `Registered`, and compares units. Recipe
  `just ata_settings_read <proxy> <node>...`. Smoke-tested offline against a local fake unit (short body, secret fields absent from output) and live on
  adjamarragu, akwalirrumanja and alamirra: all `Registered : Yes`, 86 of 92 settings fields identical, digitmap `m003` differs at akwalirrumanja.
- `scripts/README.md`: both catalogued with safety labels. `justfile`: the two recipes.
- `references/17_site-ata-dallas-delta.md` and `references/07_hardware-overlay.md` (Raspberry Pi SMC identity) link the scripts; 17 records the digitmap difference.
- `manifest.json`: 0.2.2 -> 0.2.3.

## 20261008_1147 — Raspberry Pi SMC identity and ports, rct site ATA, vendor sources linked (v0.2.1 -> v0.2.2)

VERIFIED-OBSERVED 2026-10-08, read-only over Teleport apn on 20-mile and adjamarragu (`rct`), areyonga and glen-hill (`wh`), from unified-network-controller work.

- `references/07_hardware-overlay.md`: new section, Raspberry Pi SMC identity, ports and bootloader. No DMI; model from `/proc/device-tree/model`, revision `d03115` (4B Rev 1.5, 8 GB, Sony UK);
  SoC serial as the identity anchor; eth0 MAC not derived from the serial on the Pi 4; one wired port `eth0` carrying the WAN `/30` and VLANs 500, 501, 521, 522; `wlan0` AP on areyonga; no snmpd
  (operator: no SNMP on the Pis for now); EEPROM 2023-01-11 vs upstream 2026-09-23 and the misleading `rpi-eeprom-update`. Links the vendor-sources folder and `firmware-files/raspberry-pi/`.
  Contents also gains the two 2026-10-07 sections it was missing.
- `references/03_communication-flows.md` (rct Site Addressing): `bridge_500` holds both management addresses live; the `[10.255.0.0/24, 192.168.5.0/24]` pair is in every rct, wh and nbn_wh
  topology file and no x86 one; the four site VLANs.
- `references/02_service-map.md` (snmpd on the SMC): Pi boxes have no agent, by decision.
- New `references/17_site-ata-dallas-delta.md`: the rct site ATA (DDC_VoIP-m `042112` at `192.168.5.253`), web UI only, empty PIN, no SSH or SNMP, SIP `Registered` readout, 83 of 93 settings
  identical, the short `Content-Length`, unreachable units. Routed from RUNBOOK, SKILL.md, AI_NAVIGATION.md and context-map.yaml, with both vendor-sources folders.
- `references/13_known-issues.md`: 2026-10-08 entry (kintore-smc01 not in Teleport, aeroplane-1 and 20-mile ATAs, empty ATA PIN, Pi bootloaders behind); Contents gains the missing 2026-10-07 lines.
- `manifest.json`: 0.2.1 -> 0.2.2.

## 20260930_1221 — Terminology: access is free via T&C acceptance, not a paid PIN (v0.1.75 -> v0.1.76)

- `references/13_known-issues.md` (2026-09-30 section): "paid PIN" / "paid device" wording replaced with "access mark" / "T&C-accepted device". Per the
  operator, users at these sites never buy a PIN: they accept a terms-and-conditions page and a PIN/mark is issued in the background (Eclipse
  free-PIN flow). A note saying so was added. The heading changed, so its anchor changed too. The v0.1.74 CHANGELOG entry keeps its original wording
  (append-only).

## 20260930_1202 — bot-cw-dashboard wipes PIN marks on koonibba/amata; a zero ECLIPSE_MARK count is not normal (v0.1.73 -> v0.1.74)

- `references/13_known-issues.md`: new 2026-09-30 section. Teleport user `bot-cw-dashboard` (54.66.73.128) restarts netfilter-persistent on koonibba (137/24h) and amata (45/24h) through a "usage fix"
  routine. Each restart reloads a mark-less `rules.v4` and removes every paid PIN, leaving koonibba with 0 authorised devices for 45% of sampled minutes. This is the root cause of koonibba's ~90%
  usage drop. The 2026-09-15 carrier-throttling conclusion is withdrawn. Fleet survey of 31 SMCs included; side findings and 2 `correlate-pin-activation.sh` bugs recorded.
- `references/14_pin-activation-diagnosis.md`: CORRECTED the 2026-09-11 bullet that called a 0-mark snapshot normal on a healthy site (amata). Healthy sites hold a steady non-zero count; a zero means
  the chain was wiped. Added per-minute sampling as the detection method and the correct mark-count command.

## 20260911_1120 — bungardi-smc01 confirmed as third broken site; Eclipse "PIN Last Issued" admin report documented as a third corroborating evidence source (v0.1.35 -> v0.1.36)

**Trigger:** Operator shared a screenshot of the Eclipse admin "PIN Last Issued" report (per-site last-issue date, all `nbn_accelerate`/`nbn_wh` communities) and flagged `bungardi` as still
suspiciously unresolved from the prior session's "unreachable" status, plus a batch of sites showing `Sep 10` as possibly-nothing-but-worth-checking.

- `bungardi-smc01`'s Teleport tunnel recovered on retry (the earlier "no tunnel connection found" was transient). Live-audited: `deny_info` still points at `teleport.communitywifi.net.au`,
  `squid.conf` mtime 2025-09-18, 2 marks / 2 activations in the log window — same dead signature as `hope-vale`/`kowanyama`. **Third confirmed-broken site.**
- Ran `audit-pin-activation.sh` against the six operator-flagged `Sep 10`/`Sep 9` sites (`arawerr`, `loanbun`, `burawa`, `warakurna`, `pipalyatjara`, `mungkarta`): all showed healthy 302 counts
  (57–526) — cleared as false alarms, normal daily variance.
- Documented the Eclipse "PIN Last Issued" report itself in `references/14_pin-activation-diagnosis.md` §14.6 as a third independent evidence source (outside this fleet's own tooling) — corrects the
  prior framing that pin-generation data was Eclipse-side and effectively unreachable; it's unreachable from *this fleet's* tooling specifically, but the operator has a working admin view for it.
  Landed on the same three sites as both of this pack's own mechanisms, independently.
- Updated `references/13_known-issues.md`'s `bungardi-smc01` entry from "could not be verified live" to confirmed-broken, and updated the "still actively broken" list fleet-wide from 2 sites to 3.
- Updated the §14.7 case-study table with `bungardi`'s real numbers.

Applied to: `references/13_known-issues.md`, `references/14_pin-activation-diagnosis.md`, `manifest.json`, `CHANGELOG.md`.

---

## 20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update

### Added

- `AGENTS.md` — `## Project-coherence checklist` section: explicit Tier 1-4 update instructions for when `project-coherence` runs on this pack, with domain-to-reference routing table and cross-repo
  trigger rule from ansible-wifi sessions.

### Updated

- `references/10_captive-portal.md` — captive portal two-tier arch, Eclipse config.txt sync mechanism, PHP-FPM SetHandler + a2enconf alternative, PHP short_open_tag (PHP 8.1), Kohana exception
  handler.
- `references/11_vagrant-lab.md` — vsmc networkd race condition full root cause chain (eth1 bounce → stale DHCP lease → default route drop → Teleport unreachable); Vagrant guard fix.
- `references/12_content-filtering.md` — Eclipse identity model (T&C → auto-PIN → MAC binding → connmark), MAC randomization impact table (stable/bypass/rotate), CAKE fair queuing on bridge_501 with
  WAN capacity rationale.
- `manifest.json` — version bumped 0.1.2 → 0.1.3; `updated_at` set to 2026-06-26T18:45:00Z.
- `SCRATCHPAD.md` — current state updated; session history entry added; open items updated for v0.1.3.

### Notes

- Content updates fed from ansible-wifi 2026-06-26 session RUNBOOK audit (MK keys: `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`).
- Governance-pack regeneration pending (`.ai-context/governance-pack.md` is stale after this change).
