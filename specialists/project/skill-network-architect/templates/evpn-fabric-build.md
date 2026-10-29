---
Title: EVPN fabric build template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: >-
  Build sheet for a BGP-routed Clos underlay with an EVPN-VXLAN overlay: addressing and ASNs, VNI, VRF, RT and RD allocation, IRB mode, ESI multihoming,
  MTU budget, BFD and the failure tests that accept the fabric.
---

# <fabric name> EVPN fabric build

Based on (each checked 2026-10-29 against the RFC text, VERIFIED_PRIMARY):

- BGP-only Clos underlay, one ASN for all Tier 1 (spine) devices, one per Tier 2 cluster, one per Tier 3 (leaf) device: [RFC 7938](https://www.rfc-editor.org/rfc/rfc7938.html) s5.2.1.
- Private Use ASNs 64512-65534 (RFC 7938 s5.2.2); four-octet range 4200000000-4294967294: [RFC 6996](https://www.rfc-editor.org/rfc/rfc6996.html).
- EVPN, Ethernet segments, Single-Active and All-Active multihoming: [RFC 7432](https://www.rfc-editor.org/rfc/rfc7432.html).
- EVPN over VXLAN, RT auto-derivation with one VNI per EVI, split-horizon for multihoming: [RFC 8365](https://www.rfc-editor.org/rfc/rfc8365.html).
- VXLAN, 24-bit VNI (about 16 M segments): [RFC 7348](https://www.rfc-editor.org/rfc/rfc7348.html).
- Symmetric and asymmetric IRB, "a trade-off between scale" and "control plane simplicity": [RFC 9135](https://www.rfc-editor.org/rfc/rfc9135.html).
- IP prefix routes (route type 5): [RFC 9136](https://www.rfc-editor.org/rfc/rfc9136.html).
- BFD: [RFC 5880](https://www.rfc-editor.org/rfc/rfc5880.html), [RFC 5881](https://www.rfc-editor.org/rfc/rfc5881.html).

## Contents

- [How to use](#how-to-use)
- [1. Fabric summary](#1-fabric-summary)
- [2. Underlay addressing and ASNs](#2-underlay-addressing-and-asns)
- [3. Overlay allocation: VNI, VRF, RT, RD](#3-overlay-allocation-vni-vrf-rt-rd)
- [4. IRB mode](#4-irb-mode)
- [5. ESI multihoming](#5-esi-multihoming)
- [6. MTU budget](#6-mtu-budget)
- [7. BFD and timers](#7-bfd-and-timers)
- [8. Failure tests](#8-failure-tests)
- [9. Review state](#9-review-state)

## How to use

- Fill sections 1-3 from the [IP addressing plan](ip-addressing-plan.md) and check them with `just ip-plan <file>`.
- Allocation rules (how a VNI, RT or RD is derived) go in this sheet; per-tenant rows can live in the source of truth (for example Nautobot).
- Choose the IRB mode once per fabric and record the reason in a [decision record](decision-record.md).
- Run the MTU budget with `just mtu <file>` ([mtu_budget.py](../scripts/mtu_budget.py)); paste exit code and margin.
- Platform syntax and defaults (RT auto-derivation, ESI type, ARP suppression) need version-matched vendor docs and a label.
- Acceptance is section 8 run on the built fabric. A model pass is static evidence only.
- Rules and failure modes: [datacenter-cloud-containers](../references/datacenter-cloud-containers.md) and [routing-and-switching](../references/routing-and-switching.md).

```text
Two-tier Clos (RFC 7938 three-stage folded); eBGP on every link, EVPN over the same or separate sessions
         +-----------+                +-----------+
         | spine 1   |                | spine 2   |      one ASN for all spines
         +-----------+                +-----------+
          |    |    \                  /    |    |
          |    |     \----------------/     |    |       every leaf to every spine, /31 or unnumbered
          |    |     /----------------\     |    |
         +---------+  +---------+  +---------+  +---------+
         | leaf 1  |  | leaf 2  |  | leaf 3  |  | leaf 4  |   one ASN per leaf (or per leaf pair)
         +---------+  +---------+  +---------+  +---------+
              \          /              |            |
            ESI-LAG (All-Active)      host          border leaf --> WAN / firewall
              +--------+
              | server |
              +--------+
VTEP = leaf loopback; overlay = VXLAN; MTU must carry the 50 B (IPv4 outer) per frame
```

## 1. Fabric summary

| Field                           | Value                                                  | Label |
| ------------------------------- | ------------------------------------------------------ | ----- |
| Spines / leaves / border leaves | <n> / <n> / <n>                                        |       |
| Platform and OS version         | <model> <version>                                      |       |
| Underlay protocol               | eBGP (RFC 7938) / OSPF / IS-IS                         |       |
| Overlay control plane           | EVPN address family on <underlay or loopback> sessions |       |
| Tenants (VRFs) / L2 segments    | <n> / <n>                                              |       |
| Oversubscription leaf uplink    | <n>:1                                                  |       |

## 2. Underlay addressing and ASNs

| Role        | ASN rule                       | Loopback (router ID, VTEP) | P2P links    | Example      | Label |
| ----------- | ------------------------------ | -------------------------- | ------------ | ------------ | ----- |
| Spine       | one shared ASN <asn>           | <prefix>/32 from <block>   | /31 per link | 65000        |       |
| Leaf        | one per leaf, or per leaf pair | <prefix>/32 from <block>   | /31 per link | 65101, 65102 |       |
| Border leaf | as leaf                        | <prefix>/32                | /31          |              |       |

- Four-octet private ASNs where more than 1023 are needed (RFC 6996 range above). Leaf pairs sharing an ASN need allowas-in or as-override (platform-specific, UNVERIFIED per platform); record which.
- ECMP: maximum paths <n>; multipath across different neighbour ASNs enabled (RFC 7938 s6.2); load-balancing hash fields <list>.

## 3. Overlay allocation: VNI, VRF, RT, RD

| Object              | Allocation rule                                         | Range   | Example             | Collision check |
| ------------------- | ------------------------------------------------------- | ------- | ------------------- | --------------- |
| L2 VNI (MAC-VRF)    | <base> + VLAN ID                                        | <n>-<n> | 10100 for VLAN 100  |                 |
| L3 VNI (IP-VRF)     | <base> + tenant ID                                      | <n>-<n> | 50001               |                 |
| RD                  | <loopback>:<EVI or VRF ID> (type 1, auto)               |         | 10.0.0.11:100       |                 |
| RT (L2)             | auto-derived from ASN and VNI (RFC 8365) or <asn>:<vni> |         | 65101:10100 or auto |                 |
| RT (L3)             | <common ASN>:<L3 VNI> so all leaves match               |         | 65000:50001         |                 |
| Anycast gateway MAC | one per fabric                                          |         | <mac>               |                 |

Note: auto-derived RTs embed the local ASN. With one ASN per leaf, auto RTs differ per leaf; set RTs explicitly or confirm the platform rewrites the ASN part (label with version and source).

| Tenant VRF | L3 VNI | VLAN / L2 VNI list | Subnets (anycast gateway) | Route leaking to | Label |
| ---------- | ------ | ------------------ | ------------------------- | ---------------- | ----- |
|            |        |                    |                           |                  |       |

## 4. IRB mode

| Option         | Lookups                                         | Each leaf needs                         | Choose when                                 |
| -------------- | ----------------------------------------------- | --------------------------------------- | ------------------------------------------- |
| Symmetric IRB  | Ingress and egress both route (RFC 9135)        | Only its local subnets plus the L3 VNI  | Many subnets, not all on every leaf (scale) |
| Asymmetric IRB | Ingress: MAC, IP, MAC lookups; egress: MAC only | Every subnet and its ARP and MAC tables | Few subnets; simpler control plane          |

Chosen: *symmetric / asymmetric*, ADR <id>. Type 5 prefix routes (RFC 9136) for external and silent hosts: *yes / no.*

## 5. ESI multihoming

| ESI           | Attached device | Leaves      | Mode (All-Active / Single-Active, RFC 7432) | LACP system ID | DF election          | Core isolation action | Label |
| ------------- | --------------- | ----------- | ------------------------------------------- | -------------- | -------------------- | --------------------- | ----- |
| <10-byte ESI> | <server>        | leaf1/leaf2 | All-Active                                  | <mac>          | default / preference |                       |       |

- Record the ESI type and derivation (manual or from LACP) and how mass withdrawal and split-horizon behave on the platform.

## 6. MTU budget

| Path                  | Underlay MTU | Layers (mtu_budget.py names) | Required payload | Model result           | Measured (DF probe, size) |
| --------------------- | ------------ | ---------------------------- | ---------------- | ---------------------- | ------------------------- |
| leaf-to-leaf tenant   | 9216         | vxlan-ipv4, dot1q-inner      | 9000             | exit <n>, margin <n> B |                           |
| DCI over a 1500 B WAN | 1500         | vxlan-ipv4                   | <n>              |                        |                           |

`vxlan-ipv4` is 50 B (outer IPv4 20 + UDP 8 + VXLAN 8 + inner Ethernet 14, RFC 7348); `vxlan-ipv6` is 70 B. The bundled example `examples/mtu-budget.json` holds the jumbo case.

## 7. BFD and timers

| Session type                      | BFD interval x multiplier | Detection time | BGP hold / keepalive | Graceful restart | Label |
| --------------------------------- | ------------------------- | -------------- | -------------------- | ---------------- | ----- |
| Underlay eBGP (link)              | <n> ms x <n>              | <n> ms         | <n> / <n> s          |                  |       |
| Overlay EVPN (loopback, multihop) |                           |                |                      |                  |       |

## 8. Failure tests

| Test                                       | Method                                        | Expected                                          | Measured (loss, time) | Pass |
| ------------------------------------------ | --------------------------------------------- | ------------------------------------------------- | --------------------- | ---- |
| Spine down                                 | Power off one spine under load                | ECMP reroute; loss within <n> ms target           |                       |      |
| Leaf uplink down (silent, no carrier loss) | Filter BFD on one link                        | BFD detects in interval x multiplier              |                       |      |
| ESI member link down                       | Pull one LAG member                           | Mass withdrawal; traffic on the other leaf        |                       |      |
| Leaf of an ESI pair down                   | Power off leaf 1                              | Host stays up on leaf 2; DF re-elected            |                       |      |
| Core isolation of one leaf                 | Shut all uplinks of leaf 1                    | ESI ports go down on leaf 1 (not a black hole)    |                       |      |
| Host move                                  | Move a VM between leaves                      | MAC mobility sequence increments; traffic follows |                       |      |
| Duplicate MAC                              | Same MAC on two leaves                        | Detected and logged; no flapping storm            |                       |      |
| MTU                                        | DF ping at required payload across the fabric | Passes at payload, fails at payload + 1           |                       |      |
| Border loss                                | Fail one border leaf                          | External routes withdrawn; other border carries   |                       |      |

## 9. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
