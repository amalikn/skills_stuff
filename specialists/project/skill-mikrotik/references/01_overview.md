---
Title: MikroTik devices in the SMC fleet
Category: reference
Status: current
Authority: local-supplement
Scope: Models, firmware, port and VLAN layout, power, and fleet ranges for the MikroTik devices behind SMC boxes
Last reviewed: 2026-10-07
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
| `wh`                              | RB450Gx4, RouterOS 7.8 (laramba, canteen-creek) | Cambium XV2-2T0 at `.20` (verified 2026-10-07, see skill-cambium) | VERIFIED-OBSERVED, 2-site canary 2026-10-07 |
| `nbn_wh`, `rcp`, `nbn_accelerate` | not checked                                     | not checked                                         | see `05_known-issues.md`                    |

Every surveyed device ran RouterOS 7.8 (stable, build 2023-02-24); RB450Gx4 factory firmware 6.48.6/6.48.7. One login (KeePass `Network/mikrotik switch & metal ap`) works on every `rct` switch and AP
and on the two `wh` switches tried.

## Switch port and VLAN layout (rct, delye)

VERIFIED-OBSERVED on delye 2026-10-07 (`/interface bridge port print`, `/ip address print`). The switch uses one bridge per VLAN, not a VLAN-filtering bridge.

| Port   | Connects to            | Bridge membership                                                                  |
| ------ | ---------------------- | ---------------------------------------------------------------------------------- |
| ether1 | SMC eth0 (trunk)       | `eth1-vlan500/501/521/522` sub-interfaces; ether1 untagged in `bridge-vlan521`     |
| ether2 | Sky Muster NTD         | untagged in `bridge-vlan521` (same L2 as the SMC's untagged eth0 and its VLAN 521) |
| ether3 | second WAN (VLAN 522)  | `bridge-vlan522`, inactive at delye                                                |
| ether4 | phone UI (192.168.5.x) | untagged in `bridge-vlan500`; negotiates 10 Mbps half duplex                       |
| ether5 | Metal AP (trunk)       | `eth5-vlan500/501`                                                                 |

Management address `10.255.0.5/24` on `bridge-vlan500`. The SMC side of the same trunk is `eth0` with `eth0.500`, `eth0.501`, `vlan521`, `vlan522` (skill-smc). The two `wh` switches also carry a VLAN
502 sub-interface on ether1; their full layout is not captured yet.

## Power

- `rct`: switch 23.6–30.0 V, median 27.0 V; AP 22.7–27.8 V, median 25.7 V. A ~24 V solar bus. The SMC's TSTIK app can cut the switch rail; the AP restarts with the switch (uptime within an hour of the
  switch's at 284 of 289 sites), consistent with the AP being powered through the switch.
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
canteen-creek answer ARP for `10.255.0.5` from `6c:3b:6b:53:f0:d8` exactly as `rct` switches do. delye's `/export terse` pins `mac-address=` on each port
(`…F0:D5` to `…F0:D9`). The fleet was most likely built by restoring one unit's binary backup. Harmless inside a site, but any inventory, DHCP reservation,
monitoring or cnMaestro-style tool keyed on MAC will see one device. Identify switches by SMC host plus serial, never by MAC.

### Why, and the remedy (operator confirmed 2026-10-07: one backup restored onto every switch)

- **VERIFIED-DOC** (help.mikrotik.com, Backup, read 2026-10-07): "The RouterOS backup feature allows cloning a router configuration in binary format, which
  can then be re-applied on the same device. The system's backup file also contains the device's MAC addresses, which are restored when the backup file is
  loaded." A binary `.backup` cannot be made without MACs; it is meant for the same device. For copying a configuration to other devices the same docs point
  to `/export` and `/import` (plain text, "to clone the whole configuration from one router to another").
- **VERIFIED-OBSERVED** (amuroona, 2026-10-07): ether1 `orig-mac-address=78:9A:18:39:D1:2A` (factory) vs `mac-address=6C:3B:6B:53:F0:D5` (cloned); all four
  bridges `auto-mac=yes`, so they inherit the cloned port MACs. The Metal APs are not affected (289 of 289 unique).
- **Remedy, proposed, not applied** (needs operator approval):
  - **New switches:** build from a text template, not the binary backup. `/export` the golden switch, delete every `mac-address=` line and any bridge
    `admin-mac=` line, then `/import` the cleaned file on each new unit so it keeps its factory MACs. The lines must be removed because the golden unit is
    itself a clone: delye's export pins the cloned MACs. RouterOS 7 exports leave out sensitive values (`03_routeros-cli-reference.md`), so set the admin
    password separately after the import.
  - **Existing fleet:** `/interface ethernet reset-mac-address [find]` returns each port to its `orig-mac-address`; then confirm each bridge's `mac-address`
    follows (the Bridging docs say a bridge keeps its saved auto MAC until a higher-priority source appears, so a reboot or an explicit
    `auto-mac=no admin-mac=<that unit's ether1 orig MAC>` may be needed). The docs show `reset-mac-address` for wireless (`/interface/wireless
    reset-mac-address`) and list `orig-mac-address` for Ethernet; the Ethernet form is unconfirmed on a device (known issue 11), so the first switch is also
    the test.
  - **Rollout:** the change moves the switch's MAC on every VLAN, so the SMC and APs re-learn it (ARP), a brief blip. One switch first, then a small canary,
    then the fleet.

## One AP per rct site

`rct` sites have a single AP (the Metal 52 ac) and no point-to-point bridges (operator, 2026-10-07). `wh` point-to-point bridges are Cambium ePMP and are tracked in
skill-cambium `references/05_known-issues.md`.
