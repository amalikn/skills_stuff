---
Title: RouterOS platform features for a router-as-site-box evaluation
Category: reference
Status: current
Authority: >-
  MikroTik documentation and product pages read 2026-10-22 (manual.mikrotik.com, mikrotik.com, upgrade.mikrotik.com); vendor pages stay authoritative.
  Nothing here was tried on a device.
Scope: Containers, device-mode, Netinstall, remote access and candidate models, for any project weighing a MikroTik router in place of an SMC
Last reviewed: 2026-10-22
Summary: >-
  What RouterOS 7 offers natively for running applications (containers), installing and resetting (Netinstall, device-mode), reaching the router and the
  devices behind it over CGNAT and satellite, and which current models can carry containers. Written back from enterprise-strategy's RouterOS future study.
---

# RouterOS platform features for a router-as-site-box evaluation

Written back 2026-10-22 from enterprise-strategy's [RouterOS future
study](/Volumes/Data/_ai/_project/project_stuff/apn/enterprise-strategy/workstreams/redefine-baseline/routeros-smc-replacement-future-study-20261022_1323.md), which keeps copies of every page cited
here under its `sources/routeros-smc-replacement-future-study-20261022_1323/` folder. The installed fleet (RB450Gx4 and Metal 52 ac on RouterOS 7.8) is described in `01_overview.md` and
`07_equipment-and-snmp.md`; this file covers features the fleet does not use today. Labels: `VERIFIED-DOC` (vendor documentation, read 2026-10-22), `VERIFIED-SECONDARY`, `UNVERIFIED`.

## Contents

- [Releases and documentation](#releases-and-documentation)
- [Containers and device-mode](#containers-and-device-mode)
- [Netinstall](#netinstall)
- [Remote access](#remote-access)
- [Models that can carry containers](#models-that-can-carry-containers)
- [Asterisk in a container](#asterisk-in-a-container)

## Releases and documentation

- Current releases on 2026-10-22: stable 7.24.5, long-term 7.23.8, testing 7.25rc3 (upgrade.mikrotik.com). `VERIFIED-DOC`
- help.mikrotik.com (Confluence) pages say they are **frozen**; the live manual is manual.mikrotik.com, built for 7.26 and showing no per-page revision date. Cite the page and the release it
  describes. `VERIFIED-DOC`

## Containers and device-mode

- Separate `container` package; arm, arm64 and x86 only (mipsbe and smips are not listed). `VERIFIED-DOC`
- Enabling needs device-mode `container=yes`, confirmed **physically**: the reset button, or a cold reboot on x86. Netinstall 7.22+ can set device-mode during install. So enabling containers is a
  warehouse or attended step, never a remote one. `VERIFIED-DOC`
- External disk recommended (at least 100 MB/s and 10K IOPS), not built-in NAND; pulling a remote image needs plenty of free RAM; per-container `memory-high` and `memory-max` (1 MB floor from 7.23),
  `swap-max`. `VERIFIED-DOC`
- Networking is a veth behind NAT with a dst-nat rule per port, or a veth bridged onto the LAN ("equivalent to host" networking). No host-network mode. `VERIFIED-DOC`
- MikroTik's container app catalogue includes `cloudflared`; it has no Asterisk, Teleport or Tailscale entry. `VERIFIED-DOC` (negative finding)

## Netinstall

- Conventional Netinstall needs a host on the target's **same layer-2 segment** and the target in Etherboot; it reformats system storage, with documented retention options. `VERIFIED-DOC`
- A RouterOS **Netinstall package** (documented from 7.24beta1) lets a second MikroTik act as the install server, still on the same layer-2 segment. `VERIFIED-DOC`
- Configure scripts become persistent custom defaults used after later resets; Mode scripts run once; scripts are limited to 120 s (7.22). `VERIFIED-DOC`

## Remote access

| Method                           | Behind CGNAT, no inbound port | Reaches LAN devices              | Needs MikroTik cloud | Notes                                                                   |
| -------------------------------- | ----------------------------- | -------------------------------- | -------------------- | ----------------------------------------------------------------------- |
| WireGuard, site dials a hub      | Yes (keepalive, e.g. 25 s)    | Yes, routed                      | No                   | `wg-import`, `show-client-config`, `responder`;                         |
|                                  |                               |                                  |                      |   `client-allowed-address` from 7.21                                    |
| Back To Home (BTH)               | Yes, via MikroTik relays      | Yes with `allow-lan=yes`         | **Yes**              | 7.12+, ARM/ARM64/TILE only; revoking destroys keys                      |
| IP Cloud DDNS                    | Name only                     | No                               | Yes                  | Not on x86                                                              |
| ZeroTier                         | Yes                           | Yes, routed                      | No (ZeroTier roots)  | Package, ARM/ARM64 only                                                 |
| IPsec IKEv2, OpenVPN, SSTP, L2TP | Yes, as initiator or client   | Yes                              | No                   | TCP modes risk TCP over TCP on satellite (inference)                    |
| EoIP or VXLAN in a tunnel        | Rides the tunnel              | Layer 2: carries RoMON,          | No                   |                                                                         |
|                                  |                               |   MAC tools                      |                      |                                                                         |
| RoMON, MAC-Telnet, MAC-WinBox    | Layer 2 only                  | MikroTik devices only            | No                   | RoMON is unencrypted (MD5-authenticated)                                |
| SSH forwarding, reverse proxy    | Through a tunnel              | Yes, TCP and device web pages    | No                   | Reverse proxy not on SMIPS                                              |
| Dude                             | —                             | —                                | —                    | Discontinued                                                            |

- MikroTik cloud services (DDNS, BTH, the cloud relay) need MikroTik hardware or a CHR with a paid perpetual licence; **RouterOS x86 has none**. `VERIFIED-DOC`
- There is no official Tailscale package; claims of one "since 7.11" are called a hallucination on the MikroTik forum (23 Sep 2026). Tailscale is a community container image. `VERIFIED-SECONDARY`. A
  Teleport agent in a container is undocumented. `UNVERIFIED`
- Router logins can go through RADIUS (`/user/aaa`) for per-person attribution; whether that matches Teleport's audit is untested.

## Models that can carry containers

Product pages read 2026-10-22; prices are MikroTik list prices in USD. `VERIFIED-DOC`

| Model                | CPU                       | RAM      | Storage for containers | Power, temperature                    | USD             |
| -------------------- | ------------------------- | -------- | ---------------------- | ------------------------------------- | --------------- |
| RB450Gx4 (installed) | ARM32, 4 cores, ≤ 896 MHz | 1 GB     | 512 MB NAND; microSD   | 10–57 V DC; −40 to 70 °C (bare board) | 99              |
| hAP ax3              | ARM64, 4 cores, ≤ 1.8 GHz | 1 GB     | 128 MB; USB 3.0        | 12–28 V; −40 to 70 °C                 | 139             |
| hAP ax2              | ARM64, 4 cores, 864 MHz   | 1 GB     | 128 MB; **no expansion** | 12–28 V; −40 to 50 °C                 | 99              |
| L009UiGS-RM          | ARM32, 2 cores, 800 MHz   | 512 MB   | 128 MB; USB 3.0        | 24–56 V; −40 to 70 °C                 | 119             |
| RB5009UG+S+IN        | ARM64, 4 cores, ≤ 1.4 GHz | 1 GB     | 1 GB NAND; USB 3.0     | 24–57 V; −40 to 60 °C                 | 219             |
| RB5009UPr+S+OUT      | as above                  | 1 GB     | 1 GB NAND; USB 3.0     | PoE-in; −40 to 70 °C, IP66            | 319             |
| CCR2004-16G-2S+PC    | ARM64, 4 cores, 1.2 GHz   | 4 GB     | 128 MB; USB            | 36–57 V DC, passive; −20 to 60 °C     | 465             |
| CCR2116-12G-4S+      | ARM64, 16 cores, 2.0 GHz  | 16 GB    | 128 MB; 1 × M.2        | AC, 4 fans; −20 to 60 °C              | 995             |
| RouterOS x86         | the host's                | ≥ 512 MB | any SATA, NVMe or USB  | the host's                            | L4 45 to L6 250 |

- RouterOS x86 licences are tied to the storage drive's Software ID; a failed drive's replacement key is issued once per licence. `VERIFIED-DOC`
- The installed RB450Gx4 fleet runs 7.8; containers need 7.4+ and the upgrade path from 7.8 to 7.13+ goes through 7.12.2 (`firmware-manifest.yaml`). Enabling containers on an installed unit therefore
  means one attended visit per box.
- The mikrotik.com slug for the CCR2116 is `ccr2116_12g_4splus` (`ccr2116_12g_4s` returns 404).

## Asterisk in a container

- No MikroTik guide; one forum report (2022) of a self-built Asterisk working in a RouterOS container, with no figures. `VERIFIED-SECONDARY`
- Alpine 3.24 aarch64: `asterisk` 22.9.0 is 26.8 MiB installed, `pjproject` 2.17 is 2.8 MiB, `asterisk-sounds-en` 2.5 MiB. andrius/asterisk publishes arm64 images. `VERIFIED-DOC`
- Open: `res_timing_timerfd` under the RouterOS kernel (there is no DAHDI); RTP through a bridged veth versus dst-nat; `/ip firewall service-port sip` defaults to `sip-direct-media=yes` and is usually
  turned off in front of a B2BUA (`UNVERIFIED`).
- The SMC dialplan it would carry is in skill-smc (`02_service-map.md`, VoIP).
