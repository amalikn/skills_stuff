---
Title: Australian access networks
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  How an architect designs on Australian wholesale access: nbn technologies, AVC/CVC/NNI/POI constructs, traffic classes, UNI types and what the
  retailer owns; the flat-rate pricing construct from 2026-07-01; private networks such as Opticomm (Uniti Wholesale); aggregators; satellite; copper exit;
  regulation pointers. Concepts and design consequences, not prices.
---

# Australian access networks

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [nbn access model](#nbn-access-model)
- [Pricing construct from 2026-07-01](#pricing-construct-from-2026-07-01)
- [POIs, NNI and backhaul](#pois-nni-and-backhaul)
- [Private networks and Uniti Wholesale](#private-networks-and-uniti-wholesale)
- [Aggregators and sub-RSPs](#aggregators-and-sub-rsps)
- [Satellite and fixed wireless](#satellite-and-fixed-wireless)
- [Copper exit and voice migration](#copper-exit-and-voice-migration)
- [Regulation pointers](#regulation-pointers)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Sources](#sources)
- [Further reading](#further-reading)

## Scope

- Decides: which wholesale access product and hand-off (Layer 2 bitstream or Layer 3 wholesale), direct POI presence versus an aggregator, NNI sizing and redundancy mode, traffic classes for voice,
  and what the retailer (RSP) must build behind the hand-off.
- Requirements to capture: footprint (POIs or private-network service areas served), access technology mix, speed-tier mix, busy-hour demand, voice and TC-1 needs, satellite share, migration
  timelines, regulatory obligations held by the RSP.
- Hands to [service-provider-edge](service-provider-edge.md) (BNG, CGNAT, IPv6, MTU behind the hand-off), [voice-and-sip](voice-and-sip.md) (voice over UNI-D or UNI-V),
  [capacity-and-resilience](capacity-and-resilience.md) (NNI and backhaul sizing), [wan-and-remote-access](wan-and-remote-access.md) (satellite latency and tunnels).
- Hands to skill-ifa for wholesale invoice and rate-card reconciliation, and to skill-systems-architect for OSS/BSS data models. Prices are never copied into this pack.
- Wholesale documents change several times a year. Every rule below carries the document date it was read from; re-read the current version before a decision.

## Decision rules

| Rule | Value or threshold | Evidence |
| --- | --- | --- |
| nbn is a Layer 2 service: logical circuits transparent to IPv4 and IPv6 | The RSP owns IP addressing, IPv6, BNG, CGNAT and DNS | VERIFIED_PRIMARY [nbn PTS 2026-09][nbn-pts] s2.1.1 |
| AVC = C-VLAN, CVC = S-VLAN of an IEEE 802.1ad provider bridge | Design the NNI as QinQ: S-tag per CVC, C-tag per AVC | VERIFIED_PRIMARY [nbn PTS][nbn-pts] s4.1.1, s5.1.1 |
| One NNI and one CVC per CSA where the RSP serves premises | An NNI is ordered per CSA, at the POI serving it | VERIFIED_PRIMARY [nbn PD 2026-09][nbn-pd] s1, s2 |
| Each AVC traffic class needs a CVC of the same class in that CSA | TC-1 voice needs a CVC TC-1, not only an AVC TC-1 | VERIFIED_PRIMARY [nbn PD][nbn-pd] s3 |
| Traffic classes are scheduled with strict priority | TC-1 voice (CIR, EF), TC-2 video (CIR, AF), TC-4 best effort (PIR, DF) | VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.2.1 |
| CVC TC-4 not charged on non-satellite networks from 2026-07-01 | Bundled TC-4 Offers became Flat-Rate Offers; no inclusions or ceiling | VERIFIED_PRIMARY [nbn FY27-FY29 roadmap][nbn-roadmap] |
| CVC TC-1, CVC TC-2 and satellite CVC TC-4 are still charged | Voice on TC-1 and all satellite capacity remain capacity purchases | VERIFIED_PRIMARY [nbn FY27-FY29 roadmap][nbn-roadmap] s3.2 |
| 121 POIs on the ACCC list (2012); street addresses confidential | Direct national presence means 121 interconnects and backhauls | VERIFIED_PRIMARY [ACCC POI list][accc-poi] |
| Satellite and terrestrial NNIs are separate | A satellite NNI never carries terrestrial AVCs, and the reverse | VERIFIED_PRIMARY [nbn PD][nbn-pd] s1.1(f) |
| NNI Group redundancy: Single Chassis (N:1) or Diverse Chassis (1:1) | Diverse Chassis halves usable bearer capacity | VERIFIED_PRIMARY [nbn PTS][nbn-pts] s6.2 |
| UNI-V (analogue port with ATA in the NTD) exists on Fibre only | Elsewhere voice needs an RSP-supplied ATA on UNI-D/UNI-DSL | VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.1.2, s3.1.1 |
| A private-network L3 product has no CVC and no TC-1 | Choosing L3 gives up own BNG control and a voice priority class | VERIFIED_PRIMARY [Opticomm price list 2026-07][opt-pl] s2.1 |
| Busy-hour utilisation per POI or aggregation circuit is the capacity KPI | Applies with or without a CVC charge | UNVERIFIED (operator practice, see Further reading on ACCC speed claims) |

- The SAU (Special Access Undertaking) was varied and accepted by the ACCC on 2023-10-17 and runs to 2040; it sets the price controls (a weighted average price control). VERIFIED_PRIMARY [nbn media
  statement 2023-10-17][nbn-sau-2023]; VERIFIED_SECONDARY [ACCC final decision page][accc-sau].

## nbn access model

```text
nbn wholesale path: everything right of the NNI belongs to the RSP
+----------+   +---------+   +-----+  AVC (C-VLAN)  +-----+   +---------+   +-------------+   +----------+
| end-user |-->| UNI on  |-->| nbn |===============>| POI |-->| NNI     |-->| RSP backhaul|-->| RSP BNG, |
| device   |   | the NTD |   | net |  CVC (S-VLAN)  |     |   | bearers |   | or aggreg.  |   | IP, DNS  |
+----------+   +---------+   +-----+  per CSA       +-----+   +---------+   +-------------+   +----------+
  UNI-D / UNI-DSL: data, one unicast AVC each        NNI Group: Single or Diverse Chassis
  UNI-V: analogue voice port, Fibre only, TC-1 bundled
```

| Technology | Premises demarcation (UNI) | Notes for the design |
| --- | --- | --- |
| FTTP (Fibre) | UNI-D Ethernet ports, optional UNI-V | Widest tier range; only technology with UNI-V |
| FTTC | UNI-D on an nbn connection device | Copper lead-in; tiers vary per line |
| FTTN / FTTB | UNI-DSL (VDSL2) | RSP modem terminates VDSL2; tiers are ranges, not fixed rates |
| HFC | UNI-D on the NTD | Shared coaxial segment |
| Fixed Wireless | UNI-D | Own tier set ("Wireless Plus", Fixed Wireless Home Fast and Superfast) |
| Sky Muster satellite | UNI-D | Separate NNI, CVC TC-4 still charged, fair use policy |

VERIFIED_PRIMARY: UNI availability by technology and AVC tiers per technology from the [nbn PTS][nbn-pts] s3.1.1 and the [nbn PD][nbn-pd] s3.2, both dated 2026-09-01.

- UNI-D addressing modes are Default-Mapped (untagged), DSCP-Mapped (untagged), Priority-Tagged and Tagged; not every mode exists on every network. The RSP CPE must match the mode ordered.
  VERIFIED_PRIMARY [nbn PTS][nbn-pts] s3.1.2.
- A speed tier is technology x tier x effective date. Ranges on FTTN/FTTB and FTTC are the maximum PIR the line may reach, not a minimum. VERIFIED_PRIMARY [nbn PD][nbn-pd] s3.2 note 2.
- Tier names on the 2026-09 description: Home Fast (500/50 on Fibre and HFC), Home Superfast (750/50), Home Ultrafast (about 1000/100), Home Hyperfast (2000/200 Fibre). Higher tiers carry a fair-use
  warning about disproportionate congestion. VERIFIED_PRIMARY [nbn PD][nbn-pd] s3.2.
- PIR is measured on Layer 2 frames, so small-frame traffic achieves less payload rate than the tier. VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.2.2.1.
- What the RSP owns: CPE (or not, per offer), BNG and subscriber sessions, IP and IPv6 plans, CGNAT, DNS, voice platform, NOC, and the backhaul from POI to its core. The IPv6 transition mechanism is
  the RSP choice, never a property of the access technology ([service-provider-edge](service-provider-edge.md#ipv6-transition)).

## Pricing construct from 2026-07-01

The construct matters to an architect because it moves the limiting resource. These are structural facts; prices stay in the wholesale price list.

| Period | TC-4 capacity construct (non-satellite) | What the RSP manages |
| --- | --- | --- |
| Before WBA5 (to 2023-11) | AVC per service plus CVC TC-4 bought per CSA in Mbps | CVC headroom per POI, weekly; congestion was a purchase decision |
| WBA5, 2023-12 to 2026-06 | 100 Mbps and above: AVC-only. 12/25/50: bundled AVC with CVC inclusion, overage "as utilised" | Overage on lower tiers only |
| From 2026-07-01 | All Bundled TC-4 Offers became Flat-Rate Offers; CVC TC-4 not charged; no inclusions, no ceiling | NNI bearers, backhaul and BNG capacity; no wholesale congestion lever |

- VERIFIED_PRIMARY [nbn FY27-FY29 pricing roadmap, published 2026-05-01][nbn-roadmap]: "From 1 July 2026, the Price of the CVC Offer (TC-4) in respect of all NBN Co Networks other than the NBN Co
  Satellite Network will be reduced to" zero "and all Bundled TC-4 Offers will become Flat-Rate Offers" (figure paraphrased).
- VERIFIED_PRIMARY [nbn media statement 2023-10-17][nbn-sau-2023]: the 2023 SAU variation scheduled removal of TC-4 CVC overage from all fixed line and fixed wireless products by 2026-07-01.
- Still a capacity purchase after 2026-07-01: CVC TC-1, CVC TC-2 (with Bundled TC-2 inclusions), satellite CVC TC-4, and NNI bearers. VERIFIED_PRIMARY [nbn roadmap][nbn-roadmap] s2, s3.2, s5.
- A basic 12/1 offer and a voice-capable 12 Mbps offer are separate products on the FY27 list. VERIFIED_PRIMARY [nbn roadmap][nbn-roadmap] s1.1.
- Design consequence: congestion now appears at the RSP side (NNI, aggregator circuit, backhaul, BNG) instead of a CVC policer. Re-baseline busy-hour headroom alarms on those elements. Billing logic
  must handle the transition month in which overage and flat rating coexist.
- Price controls (CPI-linked weighted average) and annual roadmaps apply under the SAU; FY28 and FY29 figures are indicative only. VERIFIED_PRIMARY [nbn roadmap][nbn-roadmap] introduction.

## POIs, NNI and backhaul

- 121 POIs were agreed by the ACCC and nbn (111 in Telstra exchanges, ten nbn-built). nbn may refuse interconnection elsewhere where needed for uniform national pricing. VERIFIED_PRIMARY [ACCC
  2012-11-05][accc-poi]. Whether the count has since changed: UNVERIFIED; read the current list.
- NNI bearer options on the FY27 list: 1000BASE-LX and -EX, 10GBASE-LR and -ER, 100GBASE-LR4 and -ER4, plus a virtual NNI (V-NNI) and NNI Link. V-NNI and NNI Link are not available for satellite.
  VERIFIED_PRIMARY [nbn roadmap][nbn-roadmap] s5.
- An NNI Group holds up to 8 bearers at 1 or 10 Gbit/s, or 2 (Single Chassis) or 4 (Diverse Chassis) at 100 Gbit/s; up to 4,000 CVCs per NNI Group; S-tags may not be over-booked. Adding bearers can
  lower aggregate efficiency because of IEEE 802.3ad frame distribution. VERIFIED_PRIMARY [nbn PTS][nbn-pts] s6.
- Diverse Chassis runs 1:1 (half the bearers are protect), so usable capacity is half the installed capacity. Single Chassis runs N:1 and loses one bearer of capacity per failure but shares one
  chassis. VERIFIED_PRIMARY [nbn PTS][nbn-pts] s6.2.
- Backhaul from each POI to the RSP core is the RSP problem: buy, build or rent through an aggregator. Count POIs x (two diverse backhauls, cross-connects, optics, NOC time) when comparing.

## Private networks and Uniti Wholesale

- Non-nbn fixed-line networks (apartment buildings, new estates) are regulated through the ACCC Superfast Broadband Access Service (SBAS) final access determination (2024-03-12). Uniti and TPG are the
  two largest SBAS suppliers, together more than one million premises; regulated terms apply if commercial agreement fails. VERIFIED_PRIMARY [ACCC SBAS][accc-sbas].
- Opticomm (part of Uniti Group) publishes its own RSP Master Agreement, product guides and price list; an RSP must sign the agreement and pass interoperability certification and business-readiness
  testing before supply. VERIFIED_PRIMARY [Opticomm become a service provider][opt-sp], [Opticomm legal documents][opt-legal].
- Opticomm products on the July 2026 price list ([opt-pl], VERIFIED_PRIMARY):
  - Ethernet Bitstream (Layer 2) with unlimited TC-4 CVC, delivered to a single POI in a data centre in each state capital, with a state backhaul aggregation fee. The RSP connects to that POI.
  - Bundled-CVC bitstream withdrawn from sale 2026-01-01 and exited 2026-06-30, with automatic migration to the unlimited plan.
  - Optional TC-1 (150 kbit/s standard) for voice and interactive video; the RSP orders TC-1 CVC, charged on the daily maximum provisioned.
  - Layer 3 Wholesale Broadband on the same access infrastructure: no CVC construct, no TC-1, service qualification required, static IP optional.
  - NNI bearers from 1 Gbit/s (T, LX, ZX) to 40 and 100 Gbit/s, and a virtual cross-connect.
- Design consequence: model every network in its own terms (its charge components, its POIs, its NNI). Never reuse nbn semantics for a private network, and compare L2 versus L3 per network on the
  whole stack (BNG, backhaul, transit, data centre, staff), not on the access price alone.
- Private networks hold statutory infrastructure provider (SIP) obligations in their declared areas and publish SIP declarations. VERIFIED_PRIMARY [Opticomm SIP declarations][opt-sipdecl].

## Aggregators and sub-RSPs

```text
Supply chain: rights and visibility shrink at each hand-off
+-----+   WBA (RSP rights: NNI,    +--------------------+   wholesale contract   +--------------------+
| nbn |-------------------------->| aggregator (holds  |---------------------->| sub-RSP: own BNG,  |
|     |   rebates, ordering)      | the WBA, NNIs, POI |   (only what the      | IP, CGNAT, voice,  |
+-----+                           | backhaul)          |    contract grants)   | aggregator NNI     |
                                  +--------------------+                       +--------------------+
```

- An aggregator holds the WBA, the nbn NNIs and the POI backhaul, and hands AVCs to a sub-RSP as Layer 2 (an OVC or similar) over a few NNI ports in a data centre, or as Layer 3. UNVERIFIED as a
  general fact; the structure follows from the WBA being held by the RSP of record.
- The sub-RSP does not own or see the nbn NNI; diversity, NNI sizing and rebate pass-through on the nbn side exist only as contract terms. Write them into the contract and audit them.
- Trade-off: aggregator mark-up and committed bandwidth per circuit versus own NNIs, backhaul, cross-connects and NOC effort per POI. Aggregation also pools statistical multiplexing into fewer
  circuits, which lowers the headroom needed per Mbit/s.
- Migration between direct and aggregated presence is a POI-by-POI cutover with transfer fees, duplicate billing during cut-over and customer notice
  ([migration-and-operations](migration-and-operations.md)).

## Satellite and fixed wireless

- Sky Muster uses two geostationary satellites; nbn describes a 72,000 km round trip that makes latency inherent, and says VPN traffic is metered and may perform poorly. VERIFIED_PRIMARY [nbn Sky
  Muster explained][nbn-sky]. RTT arithmetic is in [wan-and-remote-access](wan-and-remote-access.md#high-latency-satellite-and-radio-links).
- Satellite capacity is managed under a separate capacity-management section and the nbn Ethernet Fair Use Policy applies between nbn and the RSP. VERIFIED_PRIMARY [nbn PD][nbn-pd] s3.2 note 1. Retail
  fair-use and off-peak shaping rules: VERIFIED_SECONDARY (nbn consumer pages, retailer summaries).
- Satellite CVC TC-4 is still a CIR capacity purchase after 2026-07-01 and cannot be shared with other CVCs across the NNI. VERIFIED_PRIMARY [nbn PTS][nbn-pts] Table 1 note 5, [nbn
  roadmap][nbn-roadmap].
- Fixed Wireless has its own tiers (Wireless Plus has a maximum information rate, not a PIR). Busy-hour cell load, not the tier, sets experience. VERIFIED_PRIMARY [nbn PD][nbn-pd] s3.2 note 3.
- Design consequence: keep satellite services out of terrestrial aggregation designs; give them their own NNI, CVC sizing, MTU and tunnel decisions, and set user expectations for VPN use.

## Copper exit and voice migration

- In nbn fixed-line areas legacy copper phone and internet services are disconnected about 18 months after the area is ready for service; Fixed Wireless and satellite areas are not disconnected by
  nbn. Medical alarms, lift emergency phones and fire panels need a checked path before switch-off. VERIFIED_SECONDARY ([nbn medical alarms][nbn-alarm], ACMA reports).
- Voice options after copper: UNI-V on Fibre (ATA in the NTD, TC-1 bundled, integration testing with nbn required), an RSP ATA on UNI-D/UNI-DSL with any class, or a voice-only offer. VERIFIED_PRIMARY
  [nbn PTS][nbn-pts] s2.1.2.
- An nbn service needs mains power at the NTD and CPE; plan battery backup or a mobile fallback for life-safety lines ([voice-and-sip](voice-and-sip.md#emergency-calls)). UNVERIFIED as a design rule;
  nbn offers a battery backup service on Fibre (VERIFIED_PRIMARY [nbn PD][nbn-pd] product table).
- Porting the number is a voice-platform task ([voice-and-sip](voice-and-sip.md#number-porting)).

## Regulation pointers

| Instrument or body | What it governs for an access design | Evidence |
| --- | --- | --- |
| ACCC: nbn SAU (varied 2023-10-17, to 2040) | Price controls, product construct changes, NNI price review | VERIFIED_PRIMARY [nbn-sau-2023]; [accc-sau] |
| ACCC: s151DB POI list | Where nbn must interconnect | VERIFIED_PRIMARY [accc-poi] |
| ACCC: SBAS final access determination (2024) | Regulated terms for non-nbn superfast networks | VERIFIED_PRIMARY [accc-sbas] |
| nbn WBA (product description, PTS, price list, DCR annexure) | Contract terms an RSP builds against | VERIFIED_PRIMARY [nbn-wba] |
| ACMA: Emergency Call Service Determination 2019 | Emergency access on every voice service an RSP supplies | VERIFIED_PRIMARY, see [voice-and-sip](voice-and-sip.md#emergency-calls) |
| ACMA: statutory infrastructure provider register | Which network must connect premises in an area | VERIFIED_SECONDARY (ACMA site navigation) |

## Patterns and anti-patterns

| Situation | Do | Avoid | Why |
| --- | --- | --- | --- |
| Choosing L2 bitstream or L3 wholesale | Cost the whole stack per network | Compare access price only | BNG, backhaul, transit and staff dominate small RSPs |
| Voice priority on nbn | Order AVC TC-1 and CVC TC-1 | Mark DSCP EF on TC-4 and expect priority | Only TC-1 is scheduled ahead; marking alone does not create it |
| Capacity after 2026-07-01 | Alarm on NNI, backhaul and BNG busy hour | Keep CVC dashboards as the only view | The CVC policer no longer limits TC-4 |
| National footprint | Decide per POI: direct or aggregator | Assume all-direct or all-aggregated | 121 interconnects; tail POIs rarely pay back |
| NNI redundancy | Diverse Chassis and size for half | Count protect bearers as capacity | 1:1 protection halves usable bandwidth |
| Satellite customers | Separate NNI and design | Fold into terrestrial aggregation | Separate NNI by rule; CIR CVC; latency |
| Private networks | Own data model per network | Reuse nbn names (CVC, AVC) for their charges | Different products and POIs; reconciliation breaks |

## Failure modes and tests

| Failure | Signal | Test that proves detection and recovery |
| --- | --- | --- |
| NNI bearer loss in Single Chassis mode | Capacity drops by one bearer; possible busy-hour congestion | Busy-hour load against N-1 bearers; alarm on bearer down |
| Chassis loss with Diverse Chassis | Switch to protect bearers; brief loss | Planned bearer disable at a maintenance window; measure session impact |
| Backhaul cut between POI and core | All AVCs at that POI down | Diverse path traced; failover test; BNG storm sized ([edge](service-provider-edge.md#failover-and-reconnect-storms)) |
| Congestion moved from CVC to RSP side | Busy-hour throughput falls with no CVC alarm | Busy-hour utilisation per NNI and backhaul with alert thresholds |
| Wrong UNI-D mode (tagged vs untagged) | New service has link but no session | Activation test per technology and mode before volume orders |
| Voice on TC-4 under load | Jitter and loss at evening peak | Busy-hour MOS or jitter probe on TC-4 versus TC-1 |
| Aggregator NNI single point | All sub-RSP services down | Contracted diversity verified by trace; failover test on the aggregator side |
| Life-safety device on switched-off copper | Alarm cannot dial out | Inventory and per-device test before the disconnection date |

## Worked example

Question: an RSP serves 3,000 AVCs at one POI after 2026-07-01. Busy-hour average is 3 Mbit/s per active service (illustrative assumption; measure the real value). How many NNI bearers?

| Step | Calculation | Result |
| --- | --- | --- |
| Busy-hour demand | 3,000 x 3 Mbit/s | 9 Gbit/s |
| Headroom target | Keep busy hour under 70% of usable (assumption; queue knee in [architecture-method](architecture-method.md#quantitative-rules)) | 12.9 Gbit/s usable needed |
| Single Chassis, 10G bearers | ceil(12.9 / 10) = 2, plus 1 for N-1 | 3 x 10G, one chassis shared |
| Diverse Chassis, 10G bearers | usable = half the bearers: 2 working + 2 protect | 4 x 10G across two chassis |
| Diverse Chassis, 100G bearers | 1 working + 1 protect | 2 x 100G; headroom for growth |
| CVC TC-4 | Not charged; no CVC policer limit | Limiting resource is now NNI and backhaul |

- Verdict: Diverse Chassis with 2 x 100G removes the chassis single point and leaves growth room; the backhaul behind it must match. Revisit when tier mix shifts upward.
- Test: busy-hour utilisation per bearer for two weeks after cutover; planned working-bearer disable to confirm 1:1 protection.

## Review checklist

- [ ] Every product fact cites the wholesale document and its date; prices kept out of the design.
- [ ] Hand-off per network recorded: L2 (S-tag/C-tag plan) or L3, POI list, NNI redundancy mode.
- [ ] RSP-owned functions listed: BNG, IP and IPv6 plan, CGNAT, DNS, voice, backhaul, NOC.
- [ ] Capacity alarms set on NNI, backhaul and BNG for the post-2026-07-01 construct.
- [ ] Voice class decided: TC-1 (AVC and CVC ordered) or TC-4 with stated risk; UNI-V only where Fibre.
- [ ] Satellite, Fixed Wireless and private networks designed separately from terrestrial nbn.
- [ ] Aggregator contract covers NNI diversity, rebate pass-through and notification duties.
- [ ] Copper-exit inventory includes life-safety devices and number porting.

## Sources

Checked 2026-10-29. VERIFIED_PRIMARY: nbn Product Technical Specification and Product Description dated 2026-09-01, nbn FY27-FY29 SAU Pricing Roadmap (effective 2026-07-01), nbn SAU media statement
2023-10-17, ACCC POI list release 2012-11-05, ACCC SBAS determination release 2024-03-12, Opticomm price list July 2026 and legal pages. VERIFIED_SECONDARY: ACCC SAU final decision page (located by
search, not read in full), retail fair-use summaries, copper disconnection timing. UNVERIFIED: aggregator structure as a general fact, busy-hour headroom thresholds, the current POI count beyond the
2012 list.

## Further reading

URLs resolved 2026-10-29.

nbn wholesale:

- [nbn Wholesale Broadband Agreement documents][nbn-wba]: the current product description, technical specification, price lists and DCR annexure.
- [nbn Ethernet Product Technical Specification][nbn-pts]: UNI types and modes, traffic classes, AVC/CVC as 802.1ad, NNI Groups.
- [nbn Ethernet Product Description][nbn-pd]: orderable components, tiers per technology, satellite NNI separation.
- [nbn FY27-FY29 SAU Pricing Roadmap][nbn-roadmap]: the flat-rate construct from 2026-07-01 and what remains capacity-charged.

Regulation:

- [ACCC SAU variation final decision][accc-sau]: the 2023 acceptance and the regulatory reasoning.
- [ACCC list of points of interconnection][accc-poi]: why 121 POIs and how relocations work.
- [ACCC SBAS determination][accc-sbas]: regulated terms for non-nbn superfast networks.

Private networks and satellite:

- [Opticomm legal and wholesale documents][opt-legal]: RSP agreement, product guides, price lists.
- [nbn Sky Muster explained][nbn-sky]: latency, VPN and fair-use behaviour from the network owner.

[nbn-pts]: https://www.nbnco.com.au/content/dam/nbn/documents/sell/wba/2026/sfaa-wba-nbn-ethernet-product-technical-specification-20260901.pdf.coredownload.pdf
[nbn-pd]: https://www.nbnco.com.au/content/dam/nbn/documents/sell/wba/2026/sfaa-wba-nbn-ethernet-product-description-20260901.pdf.coredownload.pdf
[nbn-roadmap]: https://www.nbnco.com.au/content/dam/nbn/documents/sell/sau/FY27-FY29-Pricing-Roadmap-v1.0%E2%80%93010526.pdf.coredownload.pdf
[nbn-wba]: https://www.nbnco.com.au/rsps/supply-agreements/wba
[nbn-sau-2023]: https://www.nbnco.com.au/corporate-information/media-centre/media-statements/dawn-of-a-new-era-nbn-welcomes-accc-approval-of-sau-variation
[nbn-sky]: https://www.nbnco.com.au/learn/network-technology/sky-muster-explained
[nbn-alarm]: https://www.nbnco.com.au/learn/device-compatibility/medical-alarms
[accc-sau]: https://www.accc.gov.au/by-industry/telecommunications-and-internet/national-broadband-network-nbn-access-regulation/nbn-co-sau-variation-august-2023
[accc-poi]: https://www.accc.gov.au/media-release/the-accc-publishes-the-list-of-points-of-interconnection-to-the-national-broadband-network
[accc-sbas]: https://www.accc.gov.au/media-release/accc-extends-wholesale-price-controls-to-superfast-fixed-line-broadband-networks
[opt-pl]: https://files.opticomm.com.au/www/legal/Opticomm-Wholesale-Price-List-July-2026.pdf
[opt-legal]: https://www.opticomm.com.au/legal/
[opt-sp]: https://www.opticomm.com.au/become-a-service-provider/
[opt-sipdecl]: https://www.opticomm.com.au/legal/sip-declarations/
