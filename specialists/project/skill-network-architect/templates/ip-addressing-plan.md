---
Title: IP addressing plan template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: IPv4 and IPv6 allocation hierarchy, per-site block, VLAN and VRF map, reserved ranges and growth rules, with concrete segments validated by ip_plan_check.py.
---

# <organisation or programme> IP addressing plan

Based on:

- IPv6 end-site assignment: [RFC 6177](https://www.rfc-editor.org/rfc/rfc6177.html) and [RIPE-690](https://www.ripe.net/publications/docs/ripe-690/).
- IPv4 private space: [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html).
- Documentation prefixes, examples only: [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737.html) (IPv4), [RFC 3849](https://www.rfc-editor.org/rfc/rfc3849.html) (IPv6).

## How to use

- Design top-down: aggregate, region, site, function, segment. Each level summarises; a site block moves or withdraws as one prefix.
- Allocate IPv6 on nibble boundaries (/48, /52, /56, /60, /64) so reverse DNS and reading stay simple.
- Every LAN segment is a /64. Never smaller: SLAAC needs it.
- Write concrete segments as JSON: `schema_version: 1`, `segments: [{id, scope, cidr, gateway}]`; scope = VRF or routing table.
- Run [ip_plan_check.py](../scripts/ip_plan_check.py) (`just ip-plan <file>`); example: [examples/ip-plan.json](../examples/ip-plan.json).
- The checker finds overlaps within a scope and non-canonical CIDRs only. It does not check hierarchy, pools, route leaks, DHCP or DNS.
- Keep the authoritative copy in the IPAM system; this document holds the rules.
- Worked example and failure modes: [addressing-and-ipv6](../references/addressing-and-ipv6.md#worked-example).

## 1. Sources and authority

| Item                                                           | Value                                                            | Label |
| -------------------------------------------------------------- | ---------------------------------------------------------------- | ----- |
| IPv4 space held                                                | <private aggregate(s)>, <public assignment(s)>                   |       |
| IPv6 space held                                                | <PA or PI prefix, length> from <registry or upstream>            |       |
| Authoritative IPAM / writer                                    | <system> / <role or automation>                                  |       |
| Overlap with partners, carriers, VPN peers, container defaults | *list and how avoided (e.g. CGNAT 100.64.0.0/10, Docker defaults)* |       |

## 2. Hierarchy

```text
Allocation hierarchy (each level summarises the one below)
IPv6 <aggregate>/<n>
  +-- region or function block ... /<n+?>   e.g. infrastructure | sites | datacentre | reserved
       +-- site .................. /48 or /56, one per <site-code>, summarised upstream
            +-- function ......... /60   users | voice | mgmt | iot | infra
                 +-- segment ..... /64   one VLAN = one /64
IPv4 <aggregate>/<n>
  +-- site ....................... /<n> (e.g. /22)
       +-- VLAN segment .......... /24-/28, sized to hosts x growth
       +-- p2p link .............. /31
       +-- loopback .............. /32
```

| Level              | IPv4 size | IPv6 size                 | Count available | Count planned (horizon) | Allocation rule                                      |
| ------------------ | --------- | ------------------------- | --------------- | ----------------------- | ---------------------------------------------------- |
| Region or function |           |                           |                 |                         |                                                      |
| Site               | /<n>      | /48 or /56                |                 |                         | sequential by <site-code> number / sparse for growth |
| Segment            | /<n>      | /64                       |                 |                         |                                                      |
| Point-to-point     | /31       | /127 (plus reserved /64)  |                 |                         |                                                      |
| Loopback           | /32       | /128 from a dedicated /64 |                 |                         |                                                      |

## 3. Per-site block layout

| Offset in site block | Function                   | VLAN ID | VRF        | IPv4        | IPv6    | Gateway convention | DHCP / SLAAC / static | Notes              |
| -------------------- | -------------------------- | ------- | ---------- | ----------- | ------- | ------------------ | --------------------- | ------------------ |
| 0                    | infrastructure / loopbacks | -       | <vrf>      | <first /28> | <::/64> | n/a                | static                |                    |
| 1                    | management                 | <id>    | <mgmt vrf> |             |         | first usable       | static                | reachable from OOB |
| 2                    | users                      | <id>    | <user vrf> |             |         |                    | DHCP / SLAAC          |                    |
| 3                    | voice                      | <id>    |            |             |         |                    |                       |                    |
| 4                    | IoT / building systems     | <id>    |            |             |         |                    |                       |                    |
| 15                   | reserved for growth        | -       | -          |             |         |                    |                       |                    |

## 4. VLAN and VRF map

| VRF / routing table | Purpose    | Route targets / import-export | VLAN IDs | Leaks to (and why) | Enforcement point |
| ------------------- | ---------- | ----------------------------- | -------- | ------------------ | ----------------- |
| <mgmt>              | management | <rt>                          | <ids>    | none               | <device/function> |

## 5. Reserved and special ranges

| Range   | Purpose                         | Never routed to | Source |
| ------- | ------------------------------- | --------------- | ------ |
| <range> | future sites                    |                 |        |
| <range> | lab and test                    | production      |        |
| <range> | NAT pools / CGNAT               |                 |        |
| <range> | anycast services (DNS, gateway) |                 |        |

## 6. Rules, growth and review state

- Gateway, DHCP pool and static-range conventions within a segment: *e.g. gateway first usable, statics .2-.31.*
- Growth trigger: *segment utilisation > <n>% or site count > <n> per block.*
- Withdrawal: *how a returned block is quarantined before reuse.*

| Revision | State    | Date | Reviewer (role) | Checker result (exit code, file) |
| -------- | -------- | ---- | --------------- | -------------------------------- |
| r1       | proposed |      |                 |                                  |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
