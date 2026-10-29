---
Title: ERN IP addressing plan (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/ip-addressing-plan.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  IPv4 and IPv6 hierarchy for a 40-site satellite-connected operator and its hub: one /22 and one /48 per site, /26 function units, a local-only guest
  VRF reused per site, tunnel /31 pools; 408 segments checked by `just ip-plan`. All facts are fictional; addresses use RFC 1918 and RFC 3849 space.
---

# Example Remote Networks IP addressing plan

Fills template: [templates/ip-addressing-plan.md](../../templates/ip-addressing-plan.md).

- Fictional operator "Example Remote Networks" (ERN). Holdings and allocations are invented and labelled USER_STATED.
- Concrete segments: [ip-addressing-plan.json](ip-addressing-plan.json) (hub plus all 40 sites, 408 segments).
- IPv6 uses the documentation prefix 2001:db8::/32 (RFC 3849) as if it were the operator's PA assignment; public IPv4 uses 203.0.113.0/24 (RFC 5737).

## Contents

- [How to use](#how-to-use)
- [1. Sources and authority](#1-sources-and-authority)
- [2. Hierarchy](#2-hierarchy)
- [3. Per-site block layout](#3-per-site-block-layout)
- [4. VLAN and VRF map](#4-vlan-and-vrf-map)
- [5. Reserved and special ranges](#5-reserved-and-special-ranges)
- [6. Rules, growth and review state](#6-rules-growth-and-review-state)

## How to use

How this example applied the template's rules:

- Top-down: ERN aggregate, then hub and site blocks, then function units, then segments. Each site withdraws as one IPv4 /22 and one IPv6 /48.
- IPv6 on nibble boundaries: /40 sites aggregate, /48 per site, /60 per function, /64 per VLAN.
- The checker ran on every concrete segment; it proves no overlap inside a scope and canonical CIDRs only.

```text
$ just ip-plan examples/filled/ip-addressing-plan.json         # exit 0
  "status": "pass",
  "findings": [],
  "segments": 408,
  "elapsed_seconds": 0.002679
```

The 40 guest segments all use 172.16.50.0/24; they pass because each sits in its own scope (guest-site-a .. guest-site-an), which is how the checker models a VRF. Putting them in one shared scope
gives 39 overlap findings (re-run with the scopes merged: exit 1, 39 findings), which is the correct answer for a routed design and the reason the guest VRF must never leak.

## 1. Sources and authority

| Item                                                           | Value                                                                                                                 | Label       |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------- |
| IPv4 space held                                                | 10.80.0.0/15 sites, 10.10.0.0/16 hub (RFC 1918); 203.0.113.10-11 concentrators (RFC 5737)                             | USER_STATED |
| IPv6 space held                                                | 2001:db8:4000::/40 from the upstream PA /32 (documentation prefix standing in)                                        | USER_STATED |
| Authoritative IPAM / writer                                    | Nautobot IPAM / `tunnel-provision` and `site-onboard` jobs; people edit only via change                               | USER_STATED |
| Overlap with partners, carriers, VPN peers, container defaults | both WAN carriers hand out CGNAT 100.64.0.0/10: never used inside; Docker default 172.17.0.0/16 on hub hosts: kept    | USER_STATED |
|                                                                |   out of every plan; guest 172.16.50.0/24 never routed                                                                |             |

## 2. Hierarchy

```text
Allocation hierarchy (each level summarises the one below)
IPv6 2001:db8:4000::/40   (256 x /48)
  +-- hub ...................... 2001:db8:4000::/48           index 0
  +-- sites .................... 2001:db8:4001::/48 .. 4028   index 1-40 (hex), one per site-code
       +-- function ............ /60   :0 infra | :10 mgmt | :20 users | :30 voice | :40 iot
            +-- segment ........ /64   one VLAN = one /64, e.g. 2001:db8:4001:10::/64
IPv4 10.80.0.0/15 sites (10.80.0.0/16 in use, 10.81.0.0/16 reserved)
  +-- site ..................... /22   site n = 10.80.(4 x (n - 1)).0/22, site-a = 10.80.0.0/22
       +-- function unit ....... /26   16 units per site; users take 4 units (/24)
       +-- loopback ............ /32   10.80.(4 x (n - 1)).1 from unit 0
IPv4 10.10.0.0/16 hub
  +-- hub VLANs ................ /24   100 servers, 101 Proxmox mgmt, 102 corosync, 103 Ceph/backup
  +-- tunnel pools ............. /24   10.10.200.0/24 satellite, 10.10.201.0/24 LTE; one /31 per site each
```

| Level              | IPv4 size            | IPv6 size                 | Count available                     | Count planned (horizon)  | Allocation rule                                         |
| ------------------ | -------------------- | ------------------------- | ----------------------------------- | ------------------------ | ------------------------------------------------------- |
| Region or function | /16 (hub, sites)     | /40 sites, /48 hub        | 2 x /16 sites in the /15            | 1 now, 1 at 57+ sites    | sites first /16; second /16 opened by the growth rule   |
| Site               | /22                  | /48                       | 64 per /16; 256 per /40             | 40 now (60 in 3 years)   | sequential by site index; index n gives both prefixes   |
| Segment            | /26 unit (users /24) | /64                       | 16 units per site; 16 x /60 per /48 | 8 units used, 8 reserved | function at a fixed unit offset (section 3)             |
| Point-to-point     | /31                  | /127 (plus reserved /64)  | 128 per tunnel pool                 | 40 per pool (60)         | site n: 10.10.200.(2n - 2)/31 and 10.10.201.(2n - 2)/31 |
| Loopback           | /32                  | /128 from a dedicated /64 | 1 per site                          | 40 (60)                  | IPv4 .1 of unit 0; IPv6 2001:db8:40nn::1/128            |

Arithmetic: a /22 holds 1,024 addresses = 16 x /26 of 64; a /16 holds 64 x /22; a /40 holds 2^(48 - 40) = 256 x /48; a /24 holds 128 x /31. Horizon 60 sites uses 60 of 64 /22.

## 3. Per-site block layout

Shown for site-a (index 1). For site n, add 4 x (n - 1) to the third IPv4 octet and use 40nn (hex n) in the IPv6 prefix; site-b is 10.80.4.0/22 and 2001:db8:4002::/48.

| Offset in site block | Function                 | VLAN ID | VRF          | IPv4           | IPv6                  | Gateway convention | DHCP / SLAAC / static    | Notes                            |
| -------------------- | ------------------------ | ------- | ------------ | -------------- | --------------------- | ------------------ | ------------------------ | -------------------------------- |
| 0                    | infrastructure           | -       | corp         | 10.80.0.0/26   | 2001:db8:4001::/64    | n/a                | static                   | loopback 10.80.0.1/32, ::1/128   |
|                      |   / loopbacks            |         |              |                |                       |                    |                          |                                  |
| 1                    | management               | 10      | corp         | 10.80.0.64/26  | 2001:db8:4001:10::/64 | .65 / ::1          | static .66-.126          | reachable from OOB               |
| 2                    | voice                    | 30      | corp         | 10.80.0.128/26 | 2001:db8:4001:30::/64 | .129 / ::1         | DHCP .140-.190 / SLAAC   | QoS EF at site box               |
| 3                    | IoT / building systems   | 40      | corp         | 10.80.0.192/26 | 2001:db8:4001:40::/64 | .193 / ::1         | static .194-.209,        | pump RTU, camera                 |
|                      |                          |         |              |                |                       |                    |   DHCP rest              |                                  |
| 4-7                  | staff users              | 20      | corp         | 10.80.1.0/24   | 2001:db8:4001:20::/64 | .1 / ::1           | DHCP .32-.254 / SLAAC    | statics .2-.31                   |
| 8-15                 | reserved for growth      | -       | -            | 10.80.2.0/23   | all other /60s       | -                  | -                        | not announced                    |
| -                    | guest Wi-Fi              | 50      | guest-site-a | 172.16.50.0/24 | none                  | .1                 | DHCP .10-.250            | local NAT to satellite,          |
|                      |                          |         |              |                |                       |                    |                          |   never routed                   |

## 4. VLAN and VRF map

| VRF / routing table | Purpose                              | Route targets / import-export                      | VLAN IDs      | Leaks to (and why)                   | Enforcement point           |
| ------------------- | ------------------------------------ | -------------------------------------------------- | ------------- | ------------------------------------ | --------------------------- |
| corp                | management, staff, voice, IoT        | no MPLS; site /22 and /48 announced over           | 10, 20,       | none; default route from             | site box zone policy        |
|                     |                                      |   both tunnels                                     |   30, 40      |   hub-1 breakout                     |                             |
| guest-site-a        | guest internet, local only           | none; default route to wan-sat only                | 50            | none                                 | site box NAT and            |
|                     |                                      |                                                    |               |                                      |   zone policy               |
| wan-sat             | satellite underlay, carries          | none                                               | WAN port A    | none                                 | site box WAN policy         |
|                     |   wg-sat only                        |                                                    |               |                                      |                             |
| wan-lte             | LTE underlay, carries wg-lte only    | none                                               | WAN port B    | none                                 | site box WAN policy         |

## 5. Reserved and special ranges

| Range              | Purpose                                     | Never routed to                 | Source                         |
| ------------------ | ------------------------------------------- | ------------------------------- | ------------------------------ |
| 10.81.0.0/16       | future sites 65-128                         | anywhere until opened           | this plan, USER_STATED         |
| 10.99.0.0/16       | lab and test                                | production corp VRF             | this plan, USER_STATED         |
| 100.64.0.0/10      | carrier CGNAT on both WANs (not ours)       | corp VRF; never assigned inside | RFC 6598 (pack addressing reference) |
| 172.16.50.0/24     | guest, reused per site in guest-<site> VRFs | corp VRF, hub-1                 | this plan, USER_STATED         |
| 10.10.255.0/24     | anycast services: DNS resolver 10.10.255.53 | guest VRFs                      | this plan, USER_STATED         |
| 2001:db8:40ff::/48 | IPv6 lab                                    | production                      | this plan, USER_STATED         |

## 6. Rules, growth and review state

- Gateway first usable address in every segment (IPv6 ::1). Statics at the bottom of a segment, DHCP above them; ranges per function in section 3.
- Growth trigger: users segment above 70% of DHCP scope for 7 days at a site (move to a second users unit from the reserved 8-15); or site count above 56 (7/8 of 64), which opens 10.81.0.0/16.
- Withdrawal: a closed site's /22 and /48 stay in Nautobot with status "deprecated" for 90 days and are absent from both tunnel pools before reuse.

| Revision | State    | Date       | Reviewer (role)   | Checker result (exit code, file)                              |
| -------- | -------- | ---------- | ----------------- | ------------------------------------------------------------- |
| r1       | proposed | 2026-10-14 | network architect | exit 0, examples/filled/ip-addressing-plan.json, 408 segments |
| r1       | reviewed | 2026-10-29 | NOC lead          | exit 0 re-run; guest-scope reuse confirmed as intended        |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
