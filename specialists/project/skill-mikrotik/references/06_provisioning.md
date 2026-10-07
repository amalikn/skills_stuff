---
Title: How the MikroTik site switches are provisioned
Category: reference
Status: current
Authority: local-supplement
Scope: The Raspberry Pi provisioning script that builds each RB450Gx4 site switch, what it sets, and the issues it leaves on every unit
Last reviewed: 2026-10-07
Summary: A Pi pushes RouterOS 7.8 over TFTP and two SSH command batches to each new switch. The batches pin the cloned port MACs and set logging, time, services and PoE.
---

# How the MikroTik Site Switches Are Provisioned

## Contents

- [The process](#the-process)
- [What the script sets](#what-the-script-sets)
- [Issues the script puts on every switch](#issues-the-script-puts-on-every-switch)
- [The commands](#the-commands)

---

## The process

USER_STATED (operator, 2026-10-07), with the script's commands pasted by the operator:

1. The new RB450Gx4 is plugged into a Raspberry Pi provisioning station. A script on the Pi pushes the firmware, `routeros-7.8-arm.npk`, over TFTP, then
   connects over SSH and sends **part 1**.
2. Part 1 strips the factory config and builds the VLAN bridges, then gives the switch `10.255.0.5/24` on `bridge-vlan500`.
3. The script reconnects to `10.255.0.5` on VLAN 500 and sends **part 2**, which removes the factory `bridge` and its address and finishes the port, service
   and system settings.

Not yet known: where the script lives and who owns it, the address it first connects to (presumably the factory `192.168.88.1`), and whether the Metal APs
are provisioned the same way (their MACs are unique, so not with these MAC lines). Known issue 12.

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
