---
Title: MikroTik devices in the SMC fleet
Category: reference
Status: current
Authority: local-supplement
Scope: Models, firmware, port and VLAN layout, power, and fleet ranges for the MikroTik devices behind SMC boxes
Last reviewed: 2026-10-08
Summary: rct sites run an RB450Gx4 switch and a Metal 52 ac AP on RouterOS 7.8 from a ~24-28 V bus; wh sites run the same switch on ~48 V with no MikroTik AP. Port map, VLANs and fleet ranges.
---

# MikroTik Devices in the SMC Fleet

## Contents

- [Devices per flavor](#devices-per-flavor)
- [Switch port and VLAN layout (rct, delye)](#switch-port-and-vlan-layout-rct-delye)
- [Power](#power)
- [Fleet ranges (rct survey 2026-10-07)](#fleet-ranges-rct-survey-2026-10-07)

## Devices per flavor

| Flavor                            | Switch (`10.255.0.5`)                           | AP (`10.255.0.20`)                                  | Evidence                                    |
| --------------------------------- | ----------------------------------------------- | --------------------------------------------------- | ------------------------------------------- |
| `rct`                             | RB450Gx4 r2, RouterOS 7.8 (294 of 297 reached)  | Metal 52 ac, RouterOS 7.8 (289 of 297 reached)      | VERIFIED-OBSERVED, fleet survey 2026-10-07  |
| `wh`                              | RB450Gx4, RouterOS 7.8 (laramba, canteen-creek, areyonga, glen-hill) | Cambium XV2-2T0 at `.20` (verified 2026-10-07; glen-hill 2026-10-08; areyonga's `.20` did not answer; see skill-cambium) | VERIFIED-OBSERVED, 2026-10-07 and 2026-10-08 |
| `nbn_wh`, `rcp`, `nbn_accelerate` | not checked                                     | not checked                                         | see `05_known-issues.md`                    |

Every surveyed device ran RouterOS 7.8 (stable, build 2023-02-24); RB450Gx4 factory firmware 6.48.6/6.48.7. One login (KeePass `Network/mikrotik switch & metal ap`) works on every `rct` switch and AP
and on the two `wh` switches tried.

## Switch port and VLAN layout (rct, delye)

VERIFIED-OBSERVED on delye 2026-10-07 (`/interface bridge port print`, `/ip address print`). The switch uses one bridge per VLAN, not a VLAN-filtering bridge.

| Port   | Connects to                                  | Bridge membership                                                                  |
| ------ | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| ether1 | SMC eth0 (trunk 500, 501, 521, 522)          | `eth1-vlan500/501/521/522` sub-interfaces; ether1 untagged in `bridge-vlan521`     |
| ether2 | Satellite modem Uni-D1 (NTD), access 521     | untagged in `bridge-vlan521` (same L2 as the SMC's untagged eth0 and its VLAN 521) |
| ether3 | Satellite modem Uni-D2, access 522           | `bridge-vlan522`, inactive at delye                                                |
| ether4 | Dallas Delta ATA UI (`rct` only), access 500 | untagged in `bridge-vlan500`; negotiates 10 Mbps half duplex                       |
| ether5 | AP, PoE: Metal 52 ac (`rct`), Cambium (`wh`) | `eth5-vlan500/501` (trunk 500, 501)                                                |

The provisioning script builds exactly this layout (`06_provisioning.md`). Management address `10.255.0.5/24` on `bridge-vlan500`. The SMC side of the same trunk is `eth0` with `eth0.500`, `eth0.501`, `vlan521`, `vlan522` (skill-smc). The two `wh` switches also carry a VLAN
502 sub-interface on ether1; their full layout is not captured yet.

**Which unit is on each port** (VERIFIED-OBSERVED, 20-mile switch, 2026-10-08). `/ip neighbor print` is empty (discovery is limited to the empty `LAN` list),
so read the bridge host table instead: `/interface bridge host print where !local`. ether1 shows the SMC's eth0 MAC; `eth5-vlan500` and `eth5-vlan501` show
the AP's MAC; ether4 the ATA's MAC; ether2 (in `bridge-vlan521`) the satellite modem's MAC (`BC:4A:56:4F:AF:41` at 20-mile). VLAN sub-interfaces are named
`ethN-vlanV` and sit on the physical port `etherN`, so strip the suffix to get the port. unified-network-controller records Nautobot Cables from this table
(`site_cables.py`). The ATA on ether4 is a Dallas Delta DDC_VoIP-m; its facts live in skill-smc `references/17_site-ata-dallas-delta.md`.

### Site design (Mk3 connection diagram)

Source: `references/mk3-connection-diagram-v0.5.pdf` (operator, 2026-10-07): the Mk3 site, true for `rct` and `wh` except that `wh` has no Dallas Delta ATA
and a Cambium AP in place of the Metal AP (operator). Read with care: it is a v0.5 design drawing, and two SMC-side values differ from ansible-wifi
(skill-smc `references/03_communication-flows.md`, rct site addressing).

- **Satellite modem** (Sky Muster NTD) is not VLAN-aware: Uni-D1 on ether2 (VLAN 521), Uni-D2 on ether3 (VLAN 522). The two WAN VLANs are two ports of
  the same modem.
- **Why ether1 is also untagged in `bridge-vlan521`:** the SMC and switch need untagged internet so Ansible is not cut off during first deployment; the SMC's
  untagged `eth0` and VLAN 521 meet ether2 on that bridge.
- **Dallas Delta ATA UI** (`rct`): `192.168.5.253/24`, gateway `192.168.5.100` (the SMC's second address on VLAN 500, kept for this phone), no VLAN. A
  Thuraya satellite phone is wired to it as backup; the UI's BIA module switches to Thuraya when the UI has no SIP registration. UI states: 1 not registered,
  2 registered and on hook, 3 call in progress.
- **AP:** Ethernet on VLAN 500 at `10.255.0.20/24` (gateway `10.255.0.1`), Wi-Fi bridged into VLAN 501, powered from ether5.
- **SMC Wi-Fi:** the SMC's own `wlan0` (SSID `A8_Management`) is bridged into VLAN 500. The PSK is not recorded here.

## Power

- `rct`: switch 23.6–30.0 V, median 27.0 V; AP 22.7–27.8 V, median 25.7 V. A ~24 V solar bus. The SMC's TSTIK app can cut the switch rail; the AP restarts with the switch (uptime within an hour of the
  switch's at 284 of 289 sites), and the provisioning script sets ether5 `poe-out forced-on` (`06_provisioning.md`): the AP is powered by the switch.
- `wh`: switch 48.4–48.5 V (laramba, canteen-creek): a 48 V supply, separate from the Pi's 5 V supply. canteen-creek's switch had been up 68 days (since 2026-07-31, the day of its last daily blackout)
  while its Pi rebooted on 2026-10-01 and logs continuous undervoltage: the Pi's supply fails on its own (skill-smc 06_failure-modes.md, Pi undervoltage).

## Fleet ranges (rct survey 2026-10-07)

Source: `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/mikrotik-survey-20261007_1421/` (`survey.csv`, `summary.txt`, raw per device).

| Measure                                              | Switch                 | AP                            |
| ---------------------------------------------------- | ---------------------- | ----------------------------- |
| Uptime median / max                                  | 132 d / 451 d          | 132 d / 451 d                 |
| Power-cycled since their SMC booted (>1 day younger) | 11 of 294              | 12 of 289                     |
| Temperature median / max                             | 45 C / 66 C (bungardi) | 35 C / 68 C (penyeme)         |
| Below 24 V                                           | woodji 23.6 V          | 7 sites, lowest woodji 22.7 V |

Link-downs since device boot, physical ports:
- ether1 (SMC trunk): median 7; only rollah stands out (1,987). The SMC-to-switch link is stable fleet-wide.
- ether4 (phone UI): the largest counts (racecourse 47,914, fish-river 36,832, cow-lagoon 18,306): phones that keep dropping link.
- ether2 (Sky Muster NTD): up to ~10,000 (imperrenth, yuelamu-10mile, berraja). Each TSTIK modem power-cycle adds at least one.
- AP `wlan1` link-downs up to ~6,300 (gnylmarung): the wireless interface, not a cable.
- Two sensors read implausibly cold (kwala: switch 2 C, AP 0 C).

## Cloned MAC addresses (all 294 rct switches, 2026-10-07)

Every surveyed switch has a different serial number (294 unique) but the same port MACs: ether1 `6C:3B:6B:53:F0:D5` on all 294, and the `wh` switches at laramba and
canteen-creek answer ARP for `10.255.0.5` from `6c:3b:6b:53:f0:d8` exactly as `rct` switches do. Harmless inside a site, but any inventory, DHCP reservation,
monitoring or cnMaestro-style tool keyed on MAC will see one device. Identify switches by SMC host plus serial, never by MAC.

VERIFIED-OBSERVED 2026-10-08: the same five port MACs (ether1 `6C:3B:6B:53:F0:D5` to ether5 `...:D9`) at 20-mile (`rct`) and areyonga (`wh`), and the identity
is the factory default `450Gx4` on all four switches read that day (20-mile, adjamarragu, areyonga, glen-hill); the APs' identity is `AP1`. Neither MAC nor
identity names a unit: the serial is the only identity.

### Cause and remedy

- **Cause** (USER_STATED, operator 2026-10-07, with the script's commands): the Raspberry Pi provisioning script ends part 1 with
  `/interface ethernet set [ find default-name=etherN ] mac-address=6C:3B:6B:53:F0:D5` … `…D9` for ether1 to ether5, so every switch it builds gets the same
  five MACs (`06_provisioning.md`). Matches delye's `/export terse`, which pins those MACs on each port.
- **VERIFIED-OBSERVED** (amuroona, 2026-10-07): ether1 `orig-mac-address=78:9A:18:39:D1:2A` (factory) vs `mac-address=6C:3B:6B:53:F0:D5` (set by the script);
  all four bridges `auto-mac=yes`, so they inherit the pinned port MACs. The Metal APs are not affected (289 of 289 unique).
- **Remedy, proposed, not applied** (needs operator approval):
  - **New switches:** delete the five `mac-address=` commands from part 1 of the Pi script. Each new unit then keeps its factory MACs; nothing else in the
    script sets a MAC (the bridges use `auto-mac`).
  - **Existing fleet:** `/interface ethernet reset-mac-address [find]` returns each port to its `orig-mac-address`; then confirm each bridge's `mac-address`
    follows (the Bridging docs say a bridge keeps its saved auto MAC until a higher-priority source appears, so a reboot or an explicit
    `auto-mac=no admin-mac=<that unit's ether1 orig MAC>` may be needed). The docs show `reset-mac-address` for wireless (`/interface/wireless
    reset-mac-address`) and list `orig-mac-address` for Ethernet; the Ethernet form is unconfirmed on a device (known issue 11), so the first switch is also
    the test.
    Tested 2026-10-08 on glen-hill (known issue 11): the command works on 7.8 and the bridges follow without a reboot or `admin-mac`.
  - **Rollout:** the change moves the switch's MAC on every VLAN, so the SMC and APs re-learn it (ARP), a brief blip. One switch first, then a small canary,
    then the fleet.

## One AP per rct site

`rct` sites have a single AP (the Metal 52 ac) and no point-to-point bridges (operator, 2026-10-07). `wh` point-to-point bridges are Cambium ePMP and are tracked in
skill-cambium `references/05_known-issues.md`.
