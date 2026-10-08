---
Title: How the MikroTik site switches are provisioned
Category: reference
Status: current
Authority: local-supplement
Scope: The Raspberry Pi provisioning script that builds each RB450Gx4 site switch, what it sets, and the issues it leaves on every unit
Last reviewed: 2026-10-08
Summary: A Pi script (450gmk3_v1.1.py, kept here as a read-only reference) upgrades each new switch to RouterOS 7.8 over SFTP and sends two SSH command batches. The batches pin the cloned port MACs and set logging, time, services and PoE.
---

# How the MikroTik Site Switches Are Provisioned

## Contents

- [The script file](#the-script-file)
- [The process](#the-process)
- [What the script sets](#what-the-script-sets)
- [Issues the script puts on every switch](#issues-the-script-puts-on-every-switch)
- [Defects visible in the code](#defects-visible-in-the-code)
- [The commands](#the-commands)

---

## The script file

The team's provisioning script is [`450gmk3_v1.1.py`](../450gmk3_v1.1.py) in this pack's root, supplied by the operator on 2026-10-08 as **a read-only
reference**: never edit it. A change the team needs goes into our own version under `scripts/`, with the reference left as the record of what the
team runs (operator, 2026-10-08). sha256 `1f346831c028db5da2784c73d12e130e491fe46350d99858c024e110dca380cc`; a different hash means the team's copy
moved and this page needs re-checking. It holds the admin password in clear text and is committed as is to the private repo (operator decision 2026-10-08, commit
`471c970`; known issue 13); never quote that value into another file.

It runs on the Raspberry Pi with `paramiko`, `ping3` and `colorama`, from a working directory holding `mikrotik/routeros-7.8-arm.npk` and
`mikrotik/450g-changelog_v1.1.txt`, and appends each finished unit's serial number to `mikrotik/450g.log`. A `v1.0` existed before it.

## The process

VERIFIED-SOURCE (read from `450gmk3_v1.1.py`, 2026-10-08):

1. **Bench setup** the script prints: the switch on its DC power cable, not PoE, and the Pi's Ethernet in **ether5**.
2. **Find the switch.** It pings the factory address `192.168.88.1` until it answers. If `10.255.0.5` answers instead, the unit is already
   provisioned: the script logs in with the fleet password, looks for `changelog_v1.1` in `/file print` to report v1.1 or "likely v1.0", and offers
   `/system reset-configuration` (y) or asks for a different router (n).
3. **Hardware check.** `/system resource print` must show `board-name: RB450Gx4`, or the script stops. The serial number is cut from that output.
4. **Version marker.** SFTP-uploads `450g-changelog_v1.1.txt` to the switch's flash, so `/file print` on any switch shows which script version built it.
5. **RouterOS.** Unless `/system package print` shows `routeros  7.8`, SFTP-uploads `routeros-7.8-arm.npk` and reboots to install it.
6. **RouterBoard firmware.** Unless `current-firmware: 7.8`, runs `/system routerboard upgrade` and reboots.
7. **Part 1** over SSH to `192.168.88.1` as `admin` with the factory empty password: strips the factory config, builds the VLAN bridges, gives the switch
   `10.255.0.5/24` on `bridge-vlan500` and pins the port MACs.
8. **Part 2** over SSH to `10.255.0.5` (VLAN 500 through ether5): removes the factory `bridge` and its address and sets ports, services, time, the admin
   password and PoE.
9. **Read-back checks**, each stopping the script on failure: RouterOS and RouterBoard firmware 7.8, time zone `Australia/Melbourne`, ether5
   `forced-on`, the six VLAN interfaces, `10.255.0.5/24` present and no `192.168.88` address left. Then it logs the serial, rings the bell and waits for
   the next switch.

Still unknown: who owns the script and the Pi, and how the Metal APs are provisioned (their MACs are unique, so not with this script). Known issue 12.

## What the script sets

| Area           | Setting                                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Port MACs      | **ether1–ether5 pinned to `6C:3B:6B:53:F0:D5`–`…D9` on every unit**: the source of the fleet's cloned MACs (`01_overview.md`) |
| Bridges, VLANs | One bridge per VLAN (500, 501, 521, 522); sub-interfaces on ether1 (500/501/521/522) and ether5 (500/501); matches delye      |
| Ports          | ether1 and ether2 untagged in `bridge-vlan521` (`hw=no`), ether3 in `bridge-vlan522` (`hw=no`), ether4 in `bridge-vlan500`    |
| Management     | `10.255.0.5/24` on `bridge-vlan500`, default route via `10.255.0.1` (the SMC), DNS `8.8.8.8`, `8.8.4.4`                       |
| Time           | Time zone `Australia/Melbourne`; NTP client on, servers `10.255.0.1` and `139.180.160.82`                                     |
| Logging        | Logging rules 0, 1 and 2 sent to `action=disk`                                                                                |
| Firewall       | Factory filter rules 1–11 and the NAT rule removed; DHCP server, client and pool removed; remote DNS requests off            |
| Services       | telnet, ftp, api, api-ssl off; www and www-ssl on; ssh and winbox limited to `10.255.0.0/24`                                  |
| MAC access     | MAC server and MAC Winbox allowed on all interfaces                                                                           |
| System         | Identity `450Gx4` on every unit; admin password set (same value on every unit); `protected-routerboot=disabled`              |
| PoE            | ether5 `poe-out forced-on`: the Metal AP is powered by the switch                                                             |

These are the settings the script sends. The surveyed running state agrees on the port layout and the MACs (delye, amuroona); the time, logging and service
settings have not been read back from a device yet (known issues 3 and 4).

## Issues the script puts on every switch

- **Cloned MACs.** The five `/interface ethernet set [ find default-name=etherN ] mac-address=…` commands at the end of part 1. Deleting them from the
  script is the whole fix for new switches; the existing fleet needs `reset-mac-address` (`01_overview.md`, known issue 11).
- **One admin password, stored in clear text** in the script and the same on every switch. The vault entry is the reference
  (`<secret:keepassxc:Network/mikrotik switch & metal ap>`); never copy the value into this pack. Known issue 13.
- **MAC Winbox and MAC Telnet open on all interfaces**, including the NTD port (ether2) and the second WAN (ether3). Anyone on the same layer-2 segment can
  reach the login prompt. Known issue 13.
- **HTTP (`www`) on, with no address limit**, alongside `www-ssl`. The switch's only address is on VLAN 500, which limits the exposure. Known issue 13.
- **Every switch is named `450Gx4`.** Identify a switch by SMC host plus serial number, never by identity or MAC.

## Defects visible in the code

From reading the code, not seen on a run (2026-10-08). Fix them only in our own version, never in the reference.

- **Two checks compare text with bytes.** `'changelog_v1.1' in output` (re-run path) and `'current-firmware: 7.8' in output` (read-back) test a `str`
  against the `bytes` paramiko returns, which raises `TypeError` in Python 3. If the Pi runs Python 3, a run would stop at the RouterBoard read-back,
  after the configuration is applied but before the serial is logged, and a re-run on a configured unit would stop before offering the reset.
- **The ten-minute timeout starts when the script starts.** Each "wait for reboot" loop ends on a ping reply **or** on that one deadline, and carries on
  either way, so a slow second reboot is treated as a success and the next SSH step fails instead.
- **The serial is a fixed byte slice** (`output[141:152]`) of `/system resource print`, so any change in that output's layout logs the wrong text.
- **Every SSH step opens a new connection** and never closes it.

## The commands

As sent by the script, one command per line (the script joins each part into one `; `-separated line). The admin password is redacted.

### Part 1 (factory switch)

```routeros
/system logging set action=disk numbers=0
/system logging set action=disk numbers=1
/system logging set action=disk numbers=2
/ip pool remove 0
/ip dhcp-server remove 0
/ip dhcp-client remove 0
/ip dhcp-server network remove 0
/ip dns set allow-remote-requests=no
/ip dns static remove 0
/ip firewall filter remove 11
/ip firewall filter remove 10
/ip firewall filter remove 9
/ip firewall filter remove 8
/ip firewall filter remove 7
/ip firewall filter remove 6
/ip firewall filter remove 5
/ip firewall filter remove 4
/ip firewall filter remove 3
/ip firewall filter remove 2
/ip firewall filter remove 1
/ip firewall nat remove 0
/interface bridge add name=bridge-vlan500
/interface bridge add name=bridge-vlan501
/interface bridge add name=bridge-vlan521
/interface bridge add name=bridge-vlan522
/interface vlan add interface=ether1 name=eth1-vlan500 vlan-id=500
/interface vlan add interface=ether1 name=eth1-vlan501 vlan-id=501
/interface vlan add interface=ether1 name=eth1-vlan521 vlan-id=521
/interface vlan add interface=ether1 name=eth1-vlan522 vlan-id=522
/interface vlan add interface=ether5 name=eth5-vlan500 vlan-id=500
/interface vlan add interface=ether5 name=eth5-vlan501 vlan-id=501
/ip address add address=10.255.0.5/24 comment=defconf interface=bridge-vlan500 network=10.255.0.0
/interface bridge port add bridge=bridge-vlan500 interface=eth1-vlan500
/interface bridge port add bridge=bridge-vlan500 interface=eth5-vlan500
/interface ethernet set [ find default-name=ether1 ] mac-address=6C:3B:6B:53:F0:D5
/interface ethernet set [ find default-name=ether2 ] mac-address=6C:3B:6B:53:F0:D6
/interface ethernet set [ find default-name=ether3 ] mac-address=6C:3B:6B:53:F0:D7
/interface ethernet set [ find default-name=ether4 ] mac-address=6C:3B:6B:53:F0:D8
/interface ethernet set [ find default-name=ether5 ] mac-address=6C:3B:6B:53:F0:D9
```

### Part 2 (on `10.255.0.5`, VLAN 500)

```routeros
/interface bridge port remove 0
/interface bridge port remove 1
/interface bridge port remove 2
/interface bridge port remove 3
/interface bridge remove bridge
/ip address remove 0
/interface bridge port add bridge=bridge-vlan500 interface=ether4
/interface bridge port add bridge=bridge-vlan501 interface=eth1-vlan501
/interface bridge port add bridge=bridge-vlan501 interface=eth5-vlan501
/interface bridge port add bridge=bridge-vlan521 interface=ether1 hw=no
/interface bridge port add bridge=bridge-vlan521 interface=ether2 hw=no
/interface bridge port add bridge=bridge-vlan521 interface=eth1-vlan521
/interface bridge port add bridge=bridge-vlan522 interface=eth1-vlan522
/interface bridge port add bridge=bridge-vlan522 interface=ether3 hw=no
/ip dns set servers=8.8.8.8,8.8.4.4
/ip route add distance=1 gateway=10.255.0.1
/ip service set telnet disabled=yes
/ip service set ftp disabled=yes
/ip service set www-ssl disabled=no
/ip service set www disabled=no
/ip service set ssh address=10.255.0.0/24
/ip service set api disabled=yes
/ip service set winbox address=10.255.0.0/24
/ip service set api-ssl disabled=yes
/system clock set time-zone-name=Australia/Melbourne
/user set admin password=<redacted>
/system identity set name=450Gx4
/system ntp client set enabled=yes server=10.255.0.1,139.180.160.82
/system routerboard settings set protected-routerboot=disabled
/tool mac-server set allowed-interface-list=all
/tool mac-server mac-winbox set allowed-interface-list=all
/interface ethernet poe set ether5 poe-out forced-on
```
