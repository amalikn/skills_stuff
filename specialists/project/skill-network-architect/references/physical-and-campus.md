---
Title: Physical infrastructure and campus design
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: Physical, cabling, power and campus decision rules, failure domains, patterns, failure modes, a PoE and UPS worked example and a review checklist.
---

# Physical infrastructure and campus design

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Failure domains](#failure-domains)
- [Optical and copper reach](#optical-and-copper-reach)
- [PoE classes](#poe-classes)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: campus shape, L2 extent, failure domains, copper versus fibre, optical and PoE budgets, UPS runtime, grounding and OOB.
- Physical truth to collect: sites, buildings, racks, cable paths, rooms, power feeds, UPS/generator/solar, heat, dust, water, support access time.
- Per link: interface, optic and fibre type, distance, connector, wavelength, transceiver support, speed/duplex, error counters, history.
- Hands to [routing-and-switching](routing-and-switching.md) (STP, LAG, MLAG detail) and skill-mikrotik or skill-cambium (model capabilities, passive PoE).

## Decision rules

| Rule                                               | Value or threshold                                                   | Evidence                                                   |
| -------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------- |
| Carrier name and circuit ID do not prove diversity | Ask for demarcation, duct, entry, last mile, shared poles            | UNVERIFIED (judgement)                                     |
| Satellite has one physical path                    | Terminal, power and mount                                            | UNVERIFIED (judgement)                                     |
| Routed access removes STP from the failure path    | EVPN where L2 stretch is needed; collapsed core for one closet       | UNVERIFIED (judgement)                                     |
| STP where it exists                                | Name root and backup root, edge/BPDU protection, loop effect on mgmt | UNVERIFIED (judgement)                                     |
| LAG spreads flows, not one flow                    | Check hash, member loss, LACP rate, peer-link loss                   | UNVERIFIED (judgement)                                     |
| Two devices on one UPS                             | One power failure domain                                             | UNVERIFIED (judgement)                                     |
| Twisted-pair channel                               | 100 m channel = 90 m permanent link + up to 10 m of cords (derived)  | VERIFIED_SECONDARY Fluke (see Optical and copper reach)    |
| 10GBASE-T at 100 m                                 | Category 6A; Cat 6 only to 37 m (37-55 m if alien crosstalk allows)  | VERIFIED_SECONDARY Fluke (TIA TSB-155 quoted)              |
| Inter-building and growth runs                     | Single-mode OS2 (G.652); G.657 for tight bends                       | UNVERIFIED (judgement); specs [G.652][g652], [G.657][g657] |
| Multimode OM3/OM4                                  | Short in-room or riser runs only                                     | UNVERIFIED (judgement)                                     |
| Optical reach per PHY                              | See the reach table below; confirm against the exact optic           | VERIFIED_SECONDARY [Cisco SFP+ data sheet][cisco-sfp]      |
| Optical power budget                               | Min Tx power - Rx sensitivity; use the exact optic's datasheet       | UNVERIFIED (method)                                        |
| Required loss                                      | Fibre dB/km x km + connector pairs + splices + margin                | UNVERIFIED (per-element values: TIA-568.3)                 |
| Accept fibre on a tested OLTS result               | Check Rx overload on short SMF                                       | UNVERIFIED (method)                                        |
| Trend DOM light, CRC, FCS, symbol errors           | "Up" with rising errors is a pending outage                          | UNVERIFIED (judgement)                                     |
| PoE budget                                         | From PD class or worst-case draw, with one PSU failed                | UNVERIFIED (judgement)                                     |
| Passive PoE is not 802.3                           | Never mix onto an 802.3 port without the vendor's rules              | UNVERIFIED (judgement)                                     |
| UPS runtime                                        | Usable Wh x inverter efficiency / load W; derate; timed discharge    | UNVERIFIED (arithmetic)                                    |
| Surge-protect outdoor copper at entry              | Bond racks to building earth; AS/NZS 1768 for lightning              | UNVERIFIED (pointer)                                       |
| Australian customer cabling                        | Registered cabler; AS/CA S009:2020 Wiring Rules                      | VERIFIED_PRIMARY [ACMA Cabling Provider Rules][acma-cab]   |

- Cabling rules sit under the Telecommunications (Cabling Provider) Rules 2025 (same source, checked 2026-10-29).
- Define a shutdown order: site controller, uplink and management stay up longest; non-critical PoE sheds first.

## Failure domains

```text
Campus failure domains (FD) and the power feeds behind them
            +--------+     state sync       +--------+
WAN A ----->| edge A |<-------------------->| edge B |<----- WAN B / satellite
            +--------+                      +--------+
                |                               |
            +--------+   L3 or MLAG peer    +--------+
            | core A |<-------------------->| core B |
            +--------+                      +--------+
                |                               |
         +------+---+                    +------+---+
         |          |                    |          |
     +--------+ +--------+           +--------+ +--------+
     | acc 1  | | acc 2  |           | acc 3  | | acc 4  |
     +--------+ +--------+           +--------+ +--------+
FD1: each edge with its own feed | FD2: the core pair | FD3: each access switch or stack
power: UPS-A feeds edge A + core A; UPS-B feeds edge B + core B (must match the logical pairs)
X: if UPS-A and UPS-B share one upstream circuit, the pair is one power FD
OOB: independent path and power to the consoles of edge and core
dual-home access switches to both cores where the design needs it (omitted for clarity)
```

Every cross-link needs a defined routing or bridging mode and loop-prevention behaviour.

## Optical and copper reach

Copper (checked 2026-10-29):

- Permanent link (fixed cable, panel to outlet) at most 90 m; channel (link plus all patch and equipment cords) at most 100 m, so cords total at most 10 m
  (derived). VERIFIED_SECONDARY ([Fluke, "Channel, Permanent Link, Patch Cords, MPTL, E2E"](https://www.flukenetworks.com/blog/cabling-chronicles/channel-permanent-link-patch-cords-mptl-e2e-oh-my)),
  which describes the ANSI/TIA-568.2-D test configurations.
- Field testers accept length up to 10% over (99 m link, 110 m channel) for NVP uncertainty under ANSI/TIA-1152. That is test tolerance, not design length;
  insertion loss usually fails first. VERIFIED_SECONDARY ([Fluke, "Going the Distance"](https://www.flukenetworks.com/blog/cabling-chronicles/going-distance)).
- 10GBASE-T to 100 m needs Category 6A. TIA TSB-155 (quoted by Fluke): Category 6 should work to 37 m, 37-55 m depending on alien crosstalk.
  VERIFIED_SECONDARY ([Fluke, "10GBASE-T field testing requirements"](https://www.flukenetworks.com/knowledge-base/applicationstandards-articles-copper/10gbase-t-field-testing-requirements)).
- ISO/IEC 11801-1 uses the same channel and permanent-link model, but its length limits were not read: UNVERIFIED (standard is paywalled).

Optical reach per IEEE 802.3 PHY, as stated by Cisco data sheets for standard-compliant optics. VERIFIED_SECONDARY (checked 2026-10-29); the IEEE 802.3
clause text itself is paywalled and was not read.

| PHY          | Medium              | Reach                                  | Source                             |
| ------------ | ------------------- | -------------------------------------- | ---------------------------------- |
| 10GBASE-SR   | OM3 / OM4 multimode | 300 m / 400 m (OM2 82 m, OM1 33 m)     | Cisco SFP+                         |
| 10GBASE-LR   | G.652 single-mode   | 10 km                                  | Cisco SFP+                         |
| 25GBASE-SR   | OM3 / OM4 multimode | 70 m / 100 m; needs RS-FEC on the host | Cisco SFP28                        |
| 100GBASE-SR4 | OM3 / OM4, MPO-12   | 70 m / 100 m                           | Cisco QSFP100                      |

Data sheets (checked 2026-10-29):

- Cisco SFP+: [Cisco 10GBASE SFP+ Modules Data Sheet](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/data_sheet_c78-455693.html).
- Cisco SFP28: [Cisco 25GBASE SFP28 Modules Data Sheet](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/datasheet-c78-736950.html).
- Cisco QSFP100: [Cisco 100GBASE QSFP Modules Data Sheet](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/datasheet-c78-736282.html).

- Vendor "extended" optics (for example Cisco 10/25GBASE-CSR at 300/400 m) are not the IEEE PHY reach; record the part number.
- 25GBASE-SR full reach needs RS-FEC on the host ports (Cisco SFP28); record the FEC mode of both ends in the build record.

## PoE classes

Power at the PSE port versus guaranteed at the PD. VERIFIED_SECONDARY ([Ethernet Alliance 802.3bt overview v2.1][ea-bt], checked 2026-10-29).

| Type | Standard | Classes | Max PSE (W) | Max PD (W) | Pairs                 |
| ---- | -------- | ------- | ----------- | ---------- | --------------------- |
| 1    | 802.3af  | 0-3     | 15.4        | 13.0       | 2                     |
| 2    | 802.3at  | 4       | 30          | 25.5       | 2                     |
| 3    | 802.3bt  | 5 / 6   | 45 / 60     | 40 / 51    | 2 or 4 (class 5-6: 4) |
| 4    | 802.3bt  | 7 / 8   | 75 / 90     | 62 / 71.3  | 4                     |

- A higher-Type PSE also powers every lower class.
- The IEEE page lists 802.3bt-2018 as Superseded (checked 2026-10-29). Cite consolidated IEEE 802.3 (802.3-2022 active) for normative text.

## Patterns and anti-patterns

| Pattern                            | Use when                 | Anti-pattern                       | Why it fails                                |
| ---------------------------------- | ------------------------ | ---------------------------------- | ------------------------------------------- |
| Power FDs match logical pairs      | Any redundant pair       | Both members on one UPS or circuit | One feed fault kills the pair               |
| Fibre between buildings            | Any inter-building run   | Copper between buildings           | Ground-potential and lightning paths; reach |
| Routed access                      | Multi-closet campus      | Campus-wide VLANs                  | Loops and floods cross every closet         |
| Trended optical and error counters | Every uplink             | Alarm on link down only            | Degrading links fail without warning        |
| PoE budget with one PSU failed     | Critical PDs             | Budget from port count             | PDs drop when a PSU fails                   |
| OOB on separate path and power     | Remote or critical sites | OOB through the production switch  | The failure it serves also kills it         |

## Failure modes and tests

| Failure                   | Symptom                          | Blast radius                   | Test that proves the design handles it                |
| ------------------------- | -------------------------------- | ------------------------------ | ----------------------------------------------------- |
| Shared duct or pole cut   | Both "diverse" links down        | Site                           | Trace both paths end to end on paper and on site      |
| UPS or feed failure       | Pair members go down together    | Power FD                       | Switch off one feed; the other side carries load      |
| PSU failure on PoE switch | PDs drop or renegotiate          | Ports beyond remaining budget  | Pull one PSU under full PoE load                      |
| L2 loop                   | Broadcast storm; management lost | L2 domain                      | Patch a loop in lab; BPDU guard and storm control act |
| Dirty or damaged fibre    | Rising CRC and falling Rx light  | Link                           | Trend DOM; OLTS on install and after repair           |
| Rx overload on short SMF  | Errors on a new short link       | Link                           | Measure Rx light against the optic's maximum          |
| Surge on outdoor copper   | Port or device failure           | Mast devices, connected switch | Inspect entry protection and earth bonding            |
| UPS runtime below claim   | Early shutdown in an outage      | Site                           | Timed discharge test at real load                     |

Prove maintenance works at the intended reduced capacity. An interface being "up" is not a service test.

## Worked example

Question: can a 370 W PoE switch and a 1,000 Wh UPS carry a small site for 60 minutes?

Inputs (illustrative): 8 APs class 4, 4 cameras class 3, 2 radios class 4; switch 60 W, router 40 W, satellite terminal 50 W.

| Step                           | Calculation                         | Result                   |
| ------------------------------ | ----------------------------------- | ------------------------ |
| PoE demand at PSE              | 8 x 30 + 4 x 15.4 + 2 x 30          | 361.6 W                  |
| PoE headroom, both PSUs        | 370 - 361.6                         | 8.4 W (2.3%): too thin   |
| One PSU failed (185 W assumed) | 361.6 > 185                         | Fails: decide shed order |
| Total site load                | 361.6 + 60 + 40 + 50                | 511.6 W                  |
| UPS runtime                    | 1,000 Wh x 0.9 / 511.6 W            | 1.76 h = 106 min         |
| Derated 20% for age and heat   | 106 x 0.8                           | ~85 min: meets 60 min    |
| Shed cameras at 5 min          | Load 450 W; 1,000 x 0.9 x 0.8 / 450 | ~96 min                  |

- Optical check (illustrative values; use datasheets): 2 km x 0.4 dB + 2 pairs x 0.5 dB + 2 splices x 0.1 dB + 1 dB margin = 3.0 dB.
- Compare 3.0 dB with the optic's power budget; accept on the OLTS result, not the estimate.
- Verdict: PoE fails N-1 PSU; buy a larger PSU or set a shed list. UPS passes after derating; prove by a timed discharge.

## Review checklist

- [ ] Physical paths traced for every "diverse" link: duct, entry, pole, exchange.
- [ ] Power failure domains match logical pairs; upstream circuits checked.
- [ ] L2 extent bounded; STP root named where STP exists.
- [ ] Fibre type and optic reach from datasheets; OLTS results attached.
- [ ] PoE budget computed with one PSU failed; passive PoE isolated.
- [ ] UPS runtime computed, derated and proven by a timed discharge.
- [ ] Surge protection and earthing at every outdoor copper entry.
- [ ] OOB has its own path and power and survives the failures it serves.
- [ ] Australian cabling by a registered cabler to AS/CA S009.

## Further reading

Ethernet, PoE and cabling:

- [IEEE 802.3-2022](https://standards.ieee.org/ieee/802.3/10422/): PHY reach, PoE (Clauses 33/145) and LAG normative text.
- [Ethernet Alliance 802.3bt overview][ea-bt]: PoE types, classes and PSE/PD interoperability.
- [TIA standards catalogue](https://www.tiaonline.org/standards/catalog/): locate ANSI/TIA-568.2 (copper) and -568.3 (fibre) limits.

Fibre:

- [ITU-T G.652][g652]: standard single-mode fibre characteristics.
- [ITU-T G.657][g657]: bend-insensitive single-mode fibre in tight routes.

Australian installation rules:

- [ACMA Cabling Provider Rules][acma-cab]: registered-cabler duties and the AS/CA S009 Wiring Rules.

[g652]: https://www.itu.int/rec/T-REC-G.652/en
[g657]: https://www.itu.int/rec/T-REC-G.657/en
[cisco-sfp]: https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/data_sheet_c78-455693.html
[ea-bt]: https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf
[acma-cab]: https://www.acma.gov.au/cabling-provider-rules
