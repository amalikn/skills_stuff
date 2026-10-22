---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261022_1621
---

# skill-smc Changelog

## Contents

- [20261022_1623 — collect-smc-evidence-full.sh voip group records Asterisk resident memory (v0.6.5 -> v0.6.6)](#20261022_1623--collect-smc-evidence-fullsh-voip-group-records-asterisk-resident-memory-v065---v066)
- [20261022_1621 — rcp Asterisk dialplan summarised; x86 fleet by model with its 7-day load (v0.6.4 -> v0.6.5)](#20261022_1621--rcp-asterisk-dialplan-summarised-x86-fleet-by-model-with-its-7-day-load-v064---v065)
- [20261022_1506 — Firmware access from the OS: UEFI and EEPROM lines in the x86 and Pi probes, deadlines (v0.6.3 -> v0.6.4)](#20261022_1506--firmware-access-from-the-os-uefi-and-eeprom-lines-in-the-x86-and-pi-probes-deadlines-v063---v064)
- [20261022_1426 — What WAN-side equipment tells an SMC about its site: Starlink position, Sky Muster NTD nothing (v0.6.2 -> v0.6.3)](#20261022_1426--what-wan-side-equipment-tells-an-smc-about-its-site-starlink-position-sky-muster-ntd-nothing-v062---v063)
- [20261022_1226 — backdoor_exec.sh passes a stdin script through (v0.6.1 -> v0.6.2)](#20261022_1226--backdoor_execsh-passes-a-stdin-script-through-v061---v062)
- [20261022_1200 — PHP CVE fleet status, extra PHP processes, backdoor hostname check, nbn_wh read rule (v0.6.0 -> v0.6.1)](#20261022_1200--php-cve-fleet-status-extra-php-processes-backdoor-hostname-check-nbn_wh-read-rule-v060---v061)
- [20261020_2028 — Sky Muster reads: session set-up and the concurrency curve (v0.5.9 -> v0.6.0)](#20261020_2028--sky-muster-reads-session-set-up-and-the-concurrency-curve-v059---v060)
- [20261020_1905 — networkd keeps changed netdevs; render with the task's options; /etc executables; fleet-health TSH_PROXY and fqdn2ip bundle (v0.5.8 -> v0.5.9)](#20261020_1905--networkd-keeps-changed-netdevs-render-with-the-tasks-options-etc-executables-fleet-health-tsh_proxy-and-fqdn2ip-bundle-v058---v059)
- [20261020_1752 — Pi uplink on the eth0 trunk; ssh forwards detach from the caller; Sky Muster read cost (v0.5.7 -> v0.5.8)](#20261020_1752--pi-uplink-on-the-eth0-trunk-ssh-forwards-detach-from-the-caller-sky-muster-read-cost-v057---v058)
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

## 20261022_1623 — collect-smc-evidence-full.sh voip group records Asterisk resident memory (v0.6.5 -> v0.6.6)

New capture `voip|asterisk-rss` (`ps -C asterisk -o pid=,rss=,vsz=,etime=,args=`): Prometheus has no process metrics, so this is the only per-process
sizing source; enterprise-strategy's RouterOS study needs it to size a containerised Asterisk. `bash -n` passes; not yet run on a box (the session's
fleet probe was denied by auto mode). Catalogued in `scripts/README.md`. manifest 0.6.5 -> 0.6.6.

## 20261022_1621 — rcp Asterisk dialplan summarised; x86 fleet by model with its 7-day load (v0.6.4 -> v0.6.5)

From enterprise-strategy's RouterOS future study (operator answers 20261022_1535). `references/02_service-map.md` VoIP: what the rcp dialplan does
(trunk to PBX0008, 4-digit extensions, DID or prompt inbound, barring, caller ID, 8888), with a code excerpt (ansible-wifi 35b32c36); the section is rcp
only, not "non-RCT". `references/07_hardware-overlay.md`: whole x86 fleet by model (28 BOXER-6404, 19 BOXER-6641, cores 4 and 6) with 7-day CPU and RAM
from Prometheus; no process metrics exist; anomalies (koonibba 98% root, warehouse 3 GB RAM, three boxes missing from Prometheus). manifest 0.6.4 -> 0.6.5.

## 20261022_1506 — Firmware access from the OS: UEFI and EEPROM lines in the x86 and Pi probes, deadlines (v0.6.3 -> v0.6.4)

`scripts/x86_resiliency_probe.sh` and `scripts/pi_identity_probe.sh`: UEFI and EEPROM lines; a deadline on every `tsh` call (`--deadline`, default
90 s; they had none) and stdin closed. `references/07_hardware-overlay.md` "Firmware access from the OS": all 47 x86 SMCs (two models, five BIOS
builds, ESRT on the BOXER-6404 only, Secure Boot off with no keys) and six Pi canaries (EEPROM 2023-01-11, minimal config, bundled image older).
Run for smc-resiliency's warehouse and retrofit flows.

## 20261022_1426 — What WAN-side equipment tells an SMC about its site: Starlink position, Sky Muster NTD nothing (v0.6.2 -> v0.6.3)

`references/03_communication-flows.md`: a Starlink dish gives latitude, longitude and altitude on its local gRPC interface (192.168.100.1:9200,
`get_location`) only when "allow access on local network" is on in the Starlink app (community tools, `VERIFIED_SECONDARY`, unofficial, untested on
the fleet); the Enterprise Telemetry API is behind account-manager access; the Sky Muster NTD has no documented local status page or API (negative
finding). Researched for smc-resiliency's site fingerprint (decision 20261022_1426).

## 20261022_1226 — backdoor_exec.sh passes a stdin script through (v0.6.1 -> v0.6.2)

`scripts/backdoor_exec.sh`: the `tsh` inside `backdoor-watch.sh` and `kp` read stdin, so a script given with `-` was eaten before it reached the box (rc 0,
no output). Every helper now runs with `</dev/null`. Retested 2026-10-22: goojarr-goonyool and mount-peachy (rct, Teleport down) probed through the backdoor.

## 20261022_1200 — PHP CVE fleet status, extra PHP processes, backdoor hostname check, nbn_wh read rule (v0.6.0 -> v0.6.1)

From the ansible-wifi PHP CVE-2026-109618/109619 assessment. `references/10_captive-portal.md`: PHP security status (Ubuntu fixed build
`8.1.2-1ubuntu2.28`, USN-8948-1; mod_php fleet-wide; builds drift, Pis included) and the other PHP processes to restart (rct-tstik
`php -S 10.254.0.1:8080` as root from cron; `apn-mqtt-client`). `references/07_hardware-overlay.md`: what "don't touch nbn_wh" means (no
changes; reads always allowed; operator, 2026-10-22). `references/03_communication-flows.md` Learned 2026-10-22: a backdoor port can answer
as another box (50501 = nocprov-smc01); nbn_wh Teleport running but no tunnel. `references/13_known-issues.md` Learned (f): dual-inventory
hosts, CRLF host_vars, no self-patching. New scripts `php_package_probe.sh` and `backdoor_exec.sh` (recipes, catalogue, smoke-tested);
`backdoor-watch.sh` strips `\r` from a CRLF siteid.

## 20261020_2028 — Sky Muster reads: session set-up and the concurrency curve (v0.5.9 -> v0.6.0)

`references/13_known-issues.md` Learned (e): a fresh Teleport session to a Sky Muster SMC 7 to 8 s against 0.01 s on a shared connection;
8.3, 5.8 and 4.3 s per unit at 4, 8 and 12 in flight (unified-network-controller satellite concurrency report).

## 20261020_1905 — networkd keeps changed netdevs; render with the task's options; /etc executables; fleet-health TSH_PROXY and fqdn2ip bundle (v0.5.8 -> v0.5.9)

From smc-resiliency's S2 spike and slurp. `references/06_failure-modes.md`: a netplan change to a VLAN, bond or bridge takes effect only at reboot
(networkctl(1)). `references/08_ansible-authoring.md`: rendering a role template outside the role. `references/07_hardware-overlay.md`: executables
under /etc, Unbound's stub and keys on the new image. `scripts/collect-fleet-health.sh`: `TSH_PROXY` (it used only the active profile, so every CW
capture failed) and a read-only `06-fqdn2ip-state` bundle (smoke: darlngunaya, all six ok). `scripts/overlay-usage-breakdown.sh --etc`: executables list.

## 20261020_1752 — Pi uplink on the eth0 trunk; ssh forwards detach from the caller; Sky Muster read cost (v0.5.7 -> v0.5.8)

`references/03_communication-flows.md`: Learned (b) a Pi's uplink Circuit sits on `eth0` (named interface, NTD on the switch), (c) `ssh` leaves
its `tsh proxy` child on a kill and `ssh -f` forwards leave the caller's session, so they are closed by name (confirms the 20261020_1141
lingering-proxy note). `references/13_known-issues.md`: Learned (d) about 40 to 50 s per unit read over Sky Muster Plus (unified-network-controller).

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
