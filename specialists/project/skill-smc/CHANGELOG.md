---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261020_1706
---

# skill-smc Changelog

## Contents

- [20261020_1706 — /etc census in overlay-usage-breakdown; fqdn2ip still on darlngunaya (v0.5.6 -> v0.5.7)](#20261020_1706--etc-census-in-overlay-usage-breakdown-fqdn2ip-still-on-darlngunaya-v056---v057)
- [20261020_1647 — Run-time writers under /etc; read-only /etc on the new image (v0.5.5 -> v0.5.6)](#20261020_1647--run-time-writers-under-etc-read-only-etc-on-the-new-image-v055---v056)
- [20261020_1335 — A Pi SMC's internet is eth0 untagged, read on five rct sites (v0.5.4 -> v0.5.5)](#20261020_1335--a-pi-smcs-internet-is-eth0-untagged-read-on-five-rct-sites-v054---v055)
- [20261020_1322 — Ubuntu 24.04 arm64 spike VM for the read-only Pi image (v0.5.3 -> v0.5.4)](#20261020_1322--ubuntu-2404-arm64-spike-vm-for-the-read-only-pi-image-v053---v054)
- [20261020_1141 — ATA page markers by position; lingering tsh proxy after an ssh timeout (v0.5.2 -> v0.5.3)](#20261020_1141--ata-page-markers-by-position-lingering-tsh-proxy-after-an-ssh-timeout-v052---v053)
- [20261020_0944 — Write-back evidence: code excerpts and screenshots (v0.5.1 -> v0.5.2)](#20261020_0944--write-back-evidence-code-excerpts-and-screenshots-v051---v052)
- [20261020_0939 — Client MACs may be stored; S11 ATA reads; IPSSH as TP-Link; Teleport command labels (v0.5.0 -> v0.5.1)](#20261020_0939--client-macs-may-be-stored-s11-ata-reads-ipssh-as-tp-link-teleport-command-labels-v050---v051)
- [20261020_0049 — Bot-host skill scripts, dhcpd shared networks, uplink gateway (v0.4.9 -> v0.5.0)](#20261020_0049--bot-host-skill-scripts-dhcpd-shared-networks-uplink-gateway-v049---v050)
- [20261019_1119 — Working Teleport SSH reads take 7–9 s; 10 s attempts, two tries, random nodes (v0.4.8 -> v0.4.9)](#20261019_1119--working-teleport-ssh-reads-take-79-s-10-s-attempts-two-tries-random-nodes-v048---v049)
- [20261015_1751 — WireGuard and NETMAP kernel modules present on rcp and rct SMCs; no overlay tools installed (no version change)](#20261015_1751--wireguard-and-netmap-kernel-modules-present-on-rcp-and-rct-smcs-no-overlay-tools-installed-no-version-change)
- [20261015_1632 — Operator's account of the 1 Sep trigger, monthly PIN expiry, two incident-evidence scripts (v0.4.7 -> v0.4.8)](#20261015_1632--operators-account-of-the-1-sep-trigger-monthly-pin-expiry-two-incident-evidence-scripts-v047---v048)
- [20261015_1558 — Why the 2025 portal misconfiguration stayed latent; 1 Sep trigger checks (v0.4.6 -> v0.4.7)](#20261015_1558--why-the-2025-portal-misconfiguration-stayed-latent-1-sep-trigger-checks-v046---v047)
- [20261015_1553 — The SMC runs four parallel SNMP walks cleanly; fping absent on old-looma-smc01 too (v0.4.5 -> v0.4.6)](#20261015_1553--the-smc-runs-four-parallel-snmp-walks-cleanly-fping-absent-on-old-looma-smc01-too-v045---v046)
- [20261015_1515 — Three-site PIN outage dated by conntrack; koonibba bot restarts stopped 2026-10-01, 9 Oct Xbox spike (v0.4.5 -> v0.4.6)](#20261015_1515--three-site-pin-outage-dated-by-conntrack-koonibba-bot-restarts-stopped-2026-10-01-9-oct-xbox-spike-v045---v046)
- [20261015_1441 — fping absent on yakanarra-smc01; iputils ping used for device ping (v0.4.4 -> v0.4.5)](#20261015_1441--fping-absent-on-yakanarra-smc01-iputils-ping-used-for-device-ping-v044---v045)
- [20261014_2345 — Topology_vars differ by branch; read them at the listing ref (v0.4.3 -> v0.4.4)](#20261014_2345--topology_vars-differ-by-branch-read-them-at-the-listing-ref-v043---v044)
- [20261014_2230 — Central chassis port plans from as-built sets; old-looma SWP 24 corrected (v0.4.2 -> v0.4.3)](#20261014_2230--central-chassis-port-plans-from-as-built-sets-old-looma-swp-24-corrected-v042---v043)
- [20261014_1956 — BIND check-names on the smc_ltp RPZ zone (v0.4.1 -> v0.4.2)](#20261014_1956--bind-check-names-on-the-smc_ltp-rpz-zone-v041---v042)
- [20261014_1513 — x86 SMC facts, Teleport static-token join, x86 resiliency probe (v0.4.0 -> v0.4.1)](#20261014_1513--x86-smc-facts-teleport-static-token-join-x86-resiliency-probe-v040---v041)
- [20261014_0900 — Pi bootloader already supports tryboot A/B (v0.3.9 -> v0.4.0)](#20261014_0900--pi-bootloader-already-supports-tryboot-ab-v039---v040)
- [20261013_2352 — umoona vlan621 dark again; uplink check cost (v0.3.8 -> v0.3.9)](#20261013_2352--umoona-vlan621-dark-again-uplink-check-cost-v038---v039)
- [20261013_2225 — Teleport Machine ID facts, site topology, two 2026-10-13 entries recorded (v0.3.7 -> v0.3.8)](#20261013_2225--teleport-machine-id-facts-site-topology-two-2026-10-13-entries-recorded-v037---v038)
- [20261010_1805 — Governed-file standard: recipes, records rotated (v0.3.6 -> v0.3.7)](#20261010_1805--governed-file-standard-recipes-records-rotated-v036---v037)
- [20261009_1806 — Sidekick and the low-touch hook: confirmed and unplugged releases a unit (v0.3.5 -> v0.3.6)](#20261009_1806--sidekick-and-the-low-touch-hook-confirmed-and-unplugged-releases-a-unit-v035---v036)
- [20261009_1714 — What else the low-touch hook logs record: state and secret, events, the SM by its own MAC, preferred_ssid names the AP (v0.3.4 -> v0.3.5)](#20261009_1714--what-else-the-low-touch-hook-logs-record-state-and-secret-events-the-sm-by-its-own-mac-preferred_ssid-names-the-ap-v034---v035)

## 20261020_1706 — /etc census in overlay-usage-breakdown; fqdn2ip still on darlngunaya (v0.5.6 -> v0.5.7)

`scripts/overlay-usage-breakdown.sh` gains `--etc` (the `/etc` census, true uptime) and a per-host deadline (`HOST_DEADLINE`, 60 s; a perl alarm
before exec did not stop `tsh`, so a watcher sends TERM then KILL; proved with a 3 s limit). `references/07_hardware-overlay.md`: census of six
long-up boxes. `references/13_known-issues.md`: fqdn2ip still active on darlngunaya-smc01 (nbn_wh), removed on bungardi; to look at later.

## 20261020_1647 — Run-time writers under /etc; read-only /etc on the new image (v0.5.5 -> v0.5.6)

Learned 2026-10-20 in `references/07_hardware-overlay.md` (new section): the four run-time writers under `/etc` (teleport-tags-exporter,
fake-hwclock, squid blocklists, multipathd) with x86 daily counts, and that a merged confext on systemd 255 makes `/etc` read-only and noexec.
From smc-resiliency's S2 R2 work.

## 20261020_1335 — A Pi SMC's internet is eth0 untagged, read on five rct sites (v0.5.4 -> v0.5.5)

References: `references/03_communication-flows.md`, Learned 2026-10-20: the default route and the public IP (AS38172 IPSTAR) are on `eth0`;
`vlan521` only reaches the modem's subnet (curl rc 7), `vlan522` has no address; read the default route's interface, not only a role's
interfaces (unified-network-controller `uplink_provider.read`, 03e4a8e). manifest 0.5.4 -> 0.5.5.

## 20261020_1322 — Ubuntu 24.04 arm64 spike VM for the read-only Pi image (v0.5.3 -> v0.5.4)

References: `references/11_vagrant-lab.md` 12.7, Learned 2026-10-20 (smc-resiliency spike VM): a Parallels VM on Apple Silicon is arm64, so the
Pi image's systemd steps run there before a spare Pi; package facts for Ubuntu 24.04.3 arm64 (systemd 255.4, sysupdate in `systemd`, dissect in
`systemd-container`, erofs loads); tryboot cannot. manifest 0.5.3 -> 0.5.4.

## 20261020_1141 — ATA page markers by position; lingering tsh proxy after an ssh timeout (v0.5.2 -> v0.5.3)

`references/17_site-ata-dallas-delta.md` Learned 2026-10-20 (b): "Dallas Delta Corp" is past byte 24,545 on S11, "DDC_VoIP" is in both
generations' first 2 KB; six DDC_VoIP-m sites read (unified-network-controller 075d6b9, 5b3d4e6). `references/13_known-issues.md`: `tsh proxy`
children can outlive a timed-out ssh on a Machine ID host (cause unverified) and the process-group pattern that leaves nothing behind.

## 20261020_0944 — Write-back evidence: code excerpts and screenshots (v0.5.1 -> v0.5.2)

Write-back contract: every entry recording how something is done carries a code excerpt (source path, commit) and, for a visual surface, a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` (operator, 2026-10-20). In `SKILL.md`; today's entries in 03, 13, 16 and 17 carry their excerpts, screenshots marked pending until UNC 0.8.47 is deployed.

## 20261020_0939 — Client MACs may be stored; S11 ATA reads; IPSSH as TP-Link; Teleport command labels (v0.5.0 -> v0.5.1)

From unified-network-controller's 2026-10-20 run. `references/13_known-issues.md`: the never-store-client-MACs rule superseded (operator), dhcpd's
`epoch` lease-time form. `references/17_site-ata-dallas-delta.md`: 20-mile's ATA is a DDC_VoIP-BIA on S11 firmware, read with `--http0.9` and
`/auth` then `/SYS`, `/_REG`, `/webdata`; adjamarragu's ATA MAC changed. `references/16_tplink-site-switches.md`: UNC treats IPSSH as TP-Link;
gan-gan's two IPSSH hosts. `references/03_communication-flows.md`: Teleport command labels read from one `tsh ls` per cluster, `overlay` values
across the fleet, the `lat` label differs from tstiklatlon. All read back after writing.

## 20261020_0049 — Bot-host skill scripts, dhcpd shared networks, uplink gateway (v0.4.9 -> v0.5.0)

- `references/13_known-issues.md`: three entries from unified-network-controller, 2026-10-19/20: skill scripts on a Machine ID host need
  `TSH_IDENTITY` and `sshpass`; dhcpd's shared networks (`public`, `management`, `provisioning`) and an on-box lease summary that keeps client
  MACs on the SMC; an uplink's gateway is in its policy routing table (`ip -4 route show table all dev <iface>`).

## 20261019_1119 — Working Teleport SSH reads take 7–9 s; 10 s attempts, two tries, random nodes (v0.4.8 -> v0.4.9)

references/01_overview.md (Network Link — Satellite) gains a Learned 2026-10-16 entry from the unified-network-controller host verifier: fresh tsh ssh reads took 7–9 s and a 6 s deadline failed healthy boxes. Written in the 2026-10-19 backlog audit of 15–17 Oct.

## 20261015_1751 — WireGuard and NETMAP kernel modules present on rcp and rct SMCs; no overlay tools installed (no version change)

- `references/07_hardware-overlay.md`: read-only on umoona and old-looma (rcp) and adjamarragu and alamirra (rct Pi): `wireguard.ko` and
  `xt_NETMAP.ko` present, iptables 1.8.7, netplan 0.104/0.105, no wireguard-tools or tailscale; every box is 10.255.0.1. Found by
  unified-network-controller's direct-reach design.

## 20261015_1632 — Operator's account of the 1 Sep trigger, monthly PIN expiry, two incident-evidence scripts (v0.4.7 -> v0.4.8)

- `references/13_known-issues.md`: operator-stated August Route 53 `A` change for `communitywifi.net.au` to `10.254.0.1` as the trigger, with what is and is not verified; pointer to the nbn response record.
- `references/14_pin-activation-diagnosis.md`: free PINs expire on the 1st of each month.
- New read-only scripts `scripts/dns_capture_top.sh` and `scripts/teleport_sessions.py`, catalogued in `scripts/README.md`, recipes in `justfile`; smoke-tested on koonibba 2026-10-09 and the 2026-08-31..09-01 audit window.

## 20261015_1558 — Why the 2025 portal misconfiguration stayed latent; 1 Sep trigger checks (v0.4.6 -> v0.4.7)

- `references/13_known-issues.md` (2026-09-11 entry): Unbound template line that masked the wrong redirect, 5 Sep unbound rewrite, cert and Route 53 ruled out, CloudTrail and Graylog gaps, staff sessions 1-3 Sep.

## 20261015_1553 — The SMC runs four parallel SNMP walks cleanly; fping absent on old-looma-smc01 too (v0.4.5 -> v0.4.6)

- `references/02_service-map.md`: old-looma-smc01 (rcp) ran 4 concurrent snmpwalks plus 2 shared SSH sessions without errors (2026-10-15);
  fping is not installed there either. Found by unified-network-controller's onboarding speedups.

## 20261015_1515 — Three-site PIN outage dated by conntrack; koonibba bot restarts stopped 2026-10-01, 9 Oct Xbox spike (v0.4.5 -> v0.4.6)

- `references/13_known-issues.md` (2026-09-11 portal-FQDN entry): onset 2026-09-01 at hope-vale, kowanyama, galiwinku only; recovery times; galiwinku nightly pattern; operator-stated monthly PIN expiry; 1 Aug question open.
- `references/13_known-issues.md` (2026-09-30 bot entry): restarts stopped 2026-10-01 13:06, bot still connects; 9-10 Oct spike traced to an Xbox One PIN activation and Xbox/Netflix downloads (DNS-inferred).

## 20261015_1441 — fping absent on yakanarra-smc01; iputils ping used for device ping (v0.4.4 -> v0.4.5)

- `references/07_hardware-overlay.md`: `fping` is not on yakanarra-smc01 (rcp) despite the 2026-09-23 install; iputils `ping` answers in
  12 s cold through Teleport. unified-network-controller's Device Ping uses `ping` (2026-10-15).

## 20261014_2345 — Topology_vars differ by branch; read them at the listing ref (v0.4.3 -> v0.4.4)

- `references/08_ansible-authoring.md` (Cache Coherence Rules): yakanarra's and wangkatjungka's topology_vars are on `big_push`, not `rise`; a
  tool listing sites from one ref reads their files from it (unified-network-controller yakanarra uplink labels, 2026-10-14).

## 20261014_2230 — Central chassis port plans from as-built sets; old-looma SWP 24 corrected (v0.4.2 -> v0.4.3)

- `references/16_tplink-site-switches.md`: wangkatjungka's and yakanarra's central chassis port plans read from their as-built drawings (checked
  against the rendered PDFs), and a correction: old-looma's SWP 24 line enters Switch2, not Switch1 (draw.io XML and PDF). Source:
  unified-network-controller as-built generator, 2026-10-14.

## 20261014_1956 — BIND check-names on the smc_ltp RPZ zone (v0.4.1 -> v0.4.2)

- `references/02_service-map.md`: BIND refuses an underscore in an A or AAAA name of a primary zone (`check-names` fail), so names written for
  `db.cambium-rpz` are lowercase with hyphens. Source: unified-network-controller's Nautobot-only RPZ records, 2026-10-14.

## 20261014_1513 — x86 SMC facts, Teleport static-token join, x86 resiliency probe (v0.4.0 -> v0.4.1)

- `references/07_hardware-overlay.md`: `smc_disk_failover` mechanics read at source (hourly cron, 24 failed hours of pings, `BootNext` to another `ubuntu`
  entry, reboot; a no-op on one-disk BOXER-6404 boxes); BOXER-6641 two SSDs vs BOXER-6404 one CFast with a full LVM group; no hardware watchdog loaded,
  drivers shipped; systemd 249. Operator, 2026-10-14: future x86 SMCs have one disk, no two-disk models.
- `references/03_communication-flows.md`: the SMC Teleport node joins with a static `auth_token`, default `/var/lib/teleport`, site-level static labels;
  deleting the data dir and restarting re-joins the node (operator).
- New `scripts/x86_resiliency_probe.sh` and recipe `x86_resiliency_probe` (read-only), smoke-run on horn-island-smc01 and jigalong-smc01; catalogued.
- Source: smc-resiliency x86 plan and identity-partition design, 2026-10-14.

## 20261014_0900 — Pi bootloader already supports tryboot A/B (v0.3.9 -> v0.4.0)

- **Pi 4 bootloader A/B** (`references/07_hardware-overlay.md`, `VERIFIED_PRIMARY` from Raspberry Pi's release notes and docs): the fleet's 2023-01-11
  EEPROM supports `autoboot.txt` with `tryboot_a_b=1` (default since 2022-12-01); GPT untested. From unified-network-controller's read-only Pi image research.
- **Incident:** first committed as 0.3.10 with the pack's check failing (a patch number must stay single-digit); recommitted as 0.4.0 with the check passing.
- **Moved paths:** the SMC resiliency plans and the hang-recovery note now live in `apn/smc-resiliency` (`references/06_failure-modes.md`, `07_hardware-overlay.md`).

## 20261013_2352 — umoona vlan621 dark again; uplink check cost (v0.3.8 -> v0.3.9)

- **umoona `starlink01` (`vlan621`) reached nothing** on consecutive 15-minute UNC uplink checks from 2026-10-13 23:28 AEDT while its four internet uplinks
  reached everything (`references/03_communication-flows.md`, WAN-path diagnostics): the 2026-07-30 switch-side fix has not held; cause not yet read.
- **Uplink check cost:** one SSH session per SMC, 15 to 19 s for four or five uplinks.

## 20261013_2225 — Teleport Machine ID facts, site topology, two 2026-10-13 entries recorded (v0.3.7 -> v0.3.8)

- **Teleport Machine ID (tbot)** (`references/03_communication-flows.md`, new section under inbound access; from unified-network-controller apn-unc01,
  2026-10-12/13): use the bot output as the ACL reader, never root (OpenSSH refuses the 0660-looking key for its owner); an IAM-joined bot re-joins at every
  renewal, so its token needs a far-future `expires` (Teleport 12.4.34 `lib/auth/bot.go:183` reads expiry unconditionally); tctl 12.4.34 has no `bots update`
  (rm, add, clear state); an IAM token's `aws_arn` wildcard is a trust boundary.
- **Site topology** (`references/01_overview.md`, operator 2026-10-13, USER_STATED): no loop or ring except Kalumburu; a few routers cabled at towers.
- **Recorded late** (written 2026-10-13, no entry then): `references/13_known-issues.md` uplink ids are role labels whose meaning inverted, and how UNC records
  the drift (commit 2e12b87); `scripts/tplink-switch.sh` takes an optional `TSH_IDENTITY` (Machine ID bot identity) for hosts without a tsh login (791d787).
- **Central chassis port plan from an as-built** (`references/16_tplink-site-switches.md`, new section; old-looma rcp low-touch, v1.0 drawing): SWP n =
  gigabitEthernet 1/0/n; SMC, sectors via injectors, AP1, V5000, Starlink Direct NTDs on SMC VLANs enp2s0.521-526, nbn NTD enp2s0.621, tower router on
  Switch2; two uplinks straight on SMC ports; each row checked against Nautobot cables and LLDP.

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
