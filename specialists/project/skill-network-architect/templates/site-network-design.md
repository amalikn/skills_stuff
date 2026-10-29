---
Title: Site network design template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Per-site build sheet covering WAN and backhaul, MTU budget, radio links, switching and VLANs, Wi-Fi, management and OOB, power and PoE, monitoring and acceptance.
---

# <site-code> site network design

Worked example: [examples/filled/site-network-design.md](../examples/filled/site-network-design.md).

## Contents

- [How to use](#how-to-use)
- [1. Site summary](#1-site-summary)
- [2. Topology](#2-topology)
- [3. WAN and backhaul](#3-wan-and-backhaul)
- [4. MTU budget](#4-mtu-budget)
- [5. Radio links](#5-radio-links)
- [6. Switching and VLANs](#6-switching-and-vlans)
- [7. Wi-Fi](#7-wi-fi)
- [8. Management and out-of-band](#8-management-and-out-of-band)
- [9. Power and PoE budget](#9-power-and-poe-budget)
- [10. Monitoring and acceptance](#10-monitoring-and-acceptance)
- [11. Review state](#11-review-state)

## How to use

- One sheet per site, or one per site type plus a per-site delta table.
- Values come from the addressing plan, the site survey and the equipment specialists.
- Specialists: skill-smc (site box), skill-mikrotik (switches), skill-cambium (radios and APs).
- Mark every device fact with its source and evidence label.
- Run the models and paste exit code and key outputs: [mtu_budget.py](../scripts/mtu_budget.py) (`just mtu <file>`),
  [link_budget.py](../scripts/link_budget.py) (`just link-budget <file>`).
- A model pass is static evidence. Acceptance still needs on-site measurement.
- Red flags to scan before sign-off: [red-flags](../references/red-flags.md).

## 1. Site summary

| Field                                           | Value                                              | Label |
| ----------------------------------------------- | -------------------------------------------------- | ----- |
| Site code / type / address block                | <site-code> / <type> / <IPv4 block>, <IPv6 prefix> |       |
| Services carried                                | <service list with REQ IDs>                        |       |
| Users / devices (peak)                          | <n> / <n>                                          |       |
| Access constraints (travel time, hours, escort) |                                                    |       |
| Site owner / ops owner                          | <role> / <role>                                    |       |

## 2. Topology

```text
Site topology (fill in types, rates and models; mark any single point found with X)
+----------------+                      +----------------+
| upstream PoP A |                      | upstream PoP B |
+----------------+                      +----------------+
        |  backhaul A: <type, rate>             |  backhaul B or LTE: <type, rate>
        +-------------------+-------------------+
                            |
                  +-------------------+          +------------+
                  | site router / box |<-console-| OOB device |---> <independent path> ---> mgmt network
                  +-------------------+          +------------+
                            |  trunk
                  +-------------------+
                  | switch            |
                  +-------------------+
                            |  access
                 +----------+----------+
                 |          |          |
              +-----+   +-------+   +-----+
              | APs |   | hosts |   | IoT |
              +-----+   +-------+   +-----+
power: mains --> UPS <n> min --> router, switch, radios (PoE)
```

## 3. WAN and backhaul

| Link | Type (fibre, radio, fixed access, LTE, satellite) | Provider / circuit ref | Committed / burst rate | Latency p95 | Diverse path from | Failover method and time | Label |
| ---- | ------------------------------------------------- | ---------------------- | ---------------------- | ----------- | ----------------- | ------------------------ | ----- |
| A    |                                                   |                        |                        |             |                   |                          |       |
| B    |                                                   |                        |                        |             |                   |                          |       |

## 4. MTU budget

| Path            | Underlay MTU | Encapsulation layers               | Required payload MTU | Model result (`mtu_budget.py`) | Measured (DF probe) |
| --------------- | ------------ | ---------------------------------- | -------------------- | ------------------------------ | ------------------- |
| <site>-to-<hub> | <n>          | <wireguard-ipv4, dot1q-inner, ...> | <n>                  | exit <n>, margin <n> B         |                     |

*If short: raise underlay MTU, clamp TCP MSS at <point>, or reduce payload MTU on <interface>; record the choice in an ADR.*

## 5. Radio links

| Link | Band / width | Distance | Antenna gains | Tx power (in EIRP limit) | Rx sens. at rate | Fade margin req. / model | Fresnel clear | Model exit | Measured RSSI / SNR |
| ---- | ------------ | -------- | ------------- | ------------------------ | ---------------- | ------------------------ | ------------- | ---------- | ------------------- |
|      |              | <n> km   | <n> dBi       | <n> dBm                  | <n> dBm          | <n> / <n> dB             | <n>% of F1    |            |                     |

*The model is free-space only (no rain, multipath or diffraction); confirm the regulatory limit from the regulator's instrument.*

## 6. Switching and VLANs

| VLAN | Name / function | VRF | IPv4 / IPv6 | Ports (access / trunk) | STP / loop protection | DHCP snooping, RA guard | Label |
| ---- | --------------- | --- | ----------- | ---------------------- | --------------------- | ----------------------- | ----- |
|      |                 |     |             |                        |                       |                         |       |

Port map: *attach per-port table (port, device, VLAN mode, PoE class, speed/duplex expected).*

## 7. Wi-Fi

| SSID | VLAN | Security (WPA3, 802.1X, PSK) | Band(s) | Client count design | AP count / model | Channel plan and width | Min data rate | Survey ref |
| ---- | ---- | ---------------------------- | ------- | ------------------- | ---------------- | ---------------------- | ------------- | ---------- |
|      |      |                              |         |                     |                  |                        |               |            |

## 8. Management and out-of-band

| Item                                           | Value                                |
| ---------------------------------------------- | ------------------------------------ |
| Management VLAN / VRF / prefix                 |                                      |
| OOB path (independent of production backhaul?) |                                      |
| Console access to router/switch                |                                      |
| Break-glass access when AAA is down            | *method, custody; no credentials here* |
| Config backup target and schedule              |                                      |

## 9. Power and PoE budget

| Device | Qty | Draw (typ / max W) | PoE class / source port | Subtotal max W |
| ------ | --- | ------------------ | ----------------------- | -------------- |
|        |     |                    |                         |                |

Switch PoE budget <n> W vs demand <n> W (headroom <n>%). UPS capacity <n> VA / <n> W, runtime at load <n> min vs required <n> min.

## 10. Monitoring and acceptance

| Signal                        | Source | Threshold | Alert owner | Acceptance test and result |
| ----------------------------- | ------ | --------- | ----------- | -------------------------- |
| Backhaul reachability / loss  |        |           |             |                            |
| Radio RSSI / SNR / modulation |        |           |             |                            |
| PoE and UPS state             |        |           |             |                            |
| User-outcome probe            |        |           |             |                            |

## 11. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
