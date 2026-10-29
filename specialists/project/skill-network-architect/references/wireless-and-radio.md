---
Title: Wireless, radio, branch and IoT design
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: Wi-Fi, point-to-point radio, branch and IoT decision rules, Australian regulatory pointers, failure modes, a link-budget worked example and a review checklist.
---

# Wireless, radio, branch and IoT design

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Regulatory (Australia)](#regulatory-australia)
- [Radio link budget](#radio-link-budget)
- [Usable throughput from PHY rate](#usable-throughput-from-phy-rate)
- [Access and edge constraints](#access-and-edge-constraints)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: coverage versus capacity, bands, channels and widths, security per band, roaming, PtP/PtMP radio budgets, offline branch behaviour.
- Inputs: floor or site plans, device density, client capability (band, streams, 6 GHz, WPA3, 802.11r/k/v), apps, mobility, power, uplinks.
- Hands to [security-and-segmentation](security-and-segmentation.md) and [network-services](network-services.md): 802.1X, guest isolation, local services.
- Hands to skill-cambium (Cambium models, firmware, radio metrics, sync), skill-mikrotik (RouterOS; scope may be read-only), skill-smc (site box, reports).
- Never copy site passwords, addresses, coordinates or assumptions into this portable skill.

## Decision rules

| Rule                                                      | Value or threshold                                                   | Evidence                                                         |
| --------------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Signal strength alone does not prove capacity             | Slowest, most-retrying clients set cell capacity                     | UNVERIFIED (airtime principle)                                   |
| Plan from a measured survey and the regulatory instrument | Never from memory or vendor pages                                    | UNVERIFIED (method)                                              |
| 2.4 GHz channel width                                     | 20 MHz                                                               | UNVERIFIED (judgement)                                           |
| 5/6 GHz channel width                                     | From AP count and reuse, not the datasheet maximum                   | UNVERIFIED (judgement)                                           |
| DFS: availability check (CAC), then monitor               | CAC 60 s (10 min in 5600-5650 MHz); move in 10 s; off 30 min         | VERIFIED_PRIMARY ETSI EN 301 893 Table D.1                       |
| 6 GHz security                                            | WPA3 or Enhanced Open (OWE) only; PMF mandatory; no WPA2             | VERIFIED_SECONDARY [Meraki WPA3 guide][meraki] (WPA3 v3.4 s11.2) |
| OWE transition mode on 6 GHz                              | Not supported                                                        | VERIFIED_SECONDARY [Meraki WPA3 guide][meraki]                   |
| WPA3 networks require PMF                                 | Tri-band SSID needs WPA3 everywhere, or split SSIDs                  | VERIFIED_PRIMARY [WFA security][wfa-sec]                         |
| Wi-Fi 7 (802.11be-2024)                                   | 320 MHz in 6 GHz, MLO, 4K-QAM                                        | VERIFIED_PRIMARY [WFA Wi-Fi 7][wfa-7]                            |
| 4K-QAM and MLO                                            | Need very high SNR; MLO needs client, AP and controller support      | UNVERIFIED (judgement)                                           |
| 802.11k / v / r                                           | Neighbour reports / BSS transition steering / fast re-keying         | UNVERIFIED (summary of IEEE 802.11)                              |
| Clients decide when to roam                               | Test real client types before FT on a shared SSID                    | UNVERIFIED (field observation)                                   |
| Each SSID beacons per radio                               | SSID count costs airtime                                             | UNVERIFIED (judgement)                                           |
| Free-space loss                                           | Lbf = 32.4 + 20 log10 f(MHz) + 20 log10 d(km) dB                     | VERIFIED_PRIMARY [ITU-R P.525-5][p525] eq. 6                     |
| First Fresnel radius                                      | F1 = 17.3 sqrt(d1 d2 / (f d)) m; f GHz, d km                         | VERIFIED_PRIMARY [ITU-R P.530-19][p530] s2.2.2                   |
| Clearance                                                 | >= 60% F1 free space; 1.0 F1 at k = 4/3; 0.0-0.6 F1 at worst-month k | VERIFIED_PRIMARY [ITU-R P.530-19][p530] s2.2.2                   |
| Fade margin                                               | Output of an availability target (P.530 methods), not a constant     | VERIFIED_PRIMARY [ITU-R P.530-19][p530]                          |
| Co-located TDD radios                                     | Same frame timing and DL/UL ratio, or they desensitise               | UNVERIFIED (confirm with skill-cambium)                          |

- Measure, do not assume: retry rate, channel utilisation, roam events, auth latency, DHCP time, uplink and PoE headroom per AP.
- A nominal link rate is not throughput. Record channel width, TDD ratio, modulation adaptation, asymmetry, scheduler and sector contention.
- Mast work: alignment record (azimuth, tilt, RSL both ends), grounding and surge protection at entry, drip loops, mount loading.
- A radio's GPS timing sync is not a site coordinate.

## Regulatory (Australia)

- Wi-Fi and most short-range devices: LIPD Class Licence 2025 (F2025L01047), replacing the 2015 licence. VERIFIED_PRIMARY ([ACMA LIPD page][acma-lipd], [instrument][lipd], checked 2026-10-29).
- Read bands, EIRP, EIRP density, indoor-only conditions, DFS/TPC duties and exclusion zones from that instrument. Never from vendor pages or old papers.
- A class licence gives no interference protection. A backhaul that must not be interfered with needs an apparatus licence; check the [ACMA register][acma-reg].
- Lower 6 GHz (5925-6425 MHz) is available to RLANs under LIPD. In Dec 2024 ACMA decided to add 6425-6585 MHz at the 2025 remake. VERIFIED_PRIMARY ([ACMA upper 6 GHz outcomes paper][acma-6g], checked
  2026-10-29).
- The 2025 instrument does contain 6425-6585 MHz: RLAN items 13 and 14 of Schedule 1 Table 8 cover 5925-6585 MHz. VERIFIED_PRIMARY
  ([instrument as made, registered 2025-09-05](https://www.legislation.gov.au/F2025L01047/asmade/2025-09-05/text/original/pdf), Part 8, clauses 38 and 42-49, checked 2026-10-29;
  the latest-version page resolves to this as-made text, no compilation yet).

5 and 6 GHz rows of Table 8 (EIRP = maximum EIRP column; PSD = additional limitation clause). VERIFIED_PRIMARY (same instrument, checked 2026-10-29); dBm values derived.

| Item | Class              | Band (MHz)              | Max EIRP                       | PSD limit                | Other conditions (clause)                                                  |
| ---- | ------------------ | ----------------------- | ------------------------------ | ------------------------ | -------------------------------------------------------------------------- |
| 8    | Digital modulation | 5150-5250               | 1 W, averaged over the burst   | none stated              | Max 125 mW (21 dBm) EIRP above 30 degrees elevation (44)                   |
| 9    | Digital modulation | 5725-5850               | 4 W (36 dBm)                   | 25 mW per 3 kHz peak     | (43)                                                                       |
| 10   | RLAN               | 5150-5250               | 200 mW (23 dBm), burst average | 10 mW/MHz                | Indoors only (45)                                                          |
| 11   | RLAN               | 5250-5350               | 200 mW (23 dBm), burst average | 10 mW/MHz                | Indoors only; DFS; TPC if EIRP above 100 mW (46)                           |
| 12   | RLAN               | 5470-5600 and 5650-5725 | 1 W (30 dBm), burst average    | 50 mW/MHz mean           | DFS; TPC if EIRP above 500 mW (47)                                         |
| 5    | Frequency hopping  | 5925-6425               | 25 mW (14 dBm)                 | 10 mW/MHz                | At least 15 hops; max 20 MHz bandwidth; contention-based access (42)       |
| 13   | RLAN               | 5925-6585               | 250 mW (24 dBm)                | 12.5 mW/MHz (11 dBm/MHz) | Indoors only; contention-based access; below 5925 MHz max -27 dBm/MHz (48) |
| 14   | RLAN               | 5925-6585               | 25 mW (14 dBm)                 | 1.25 mW/MHz (1 dBm/MHz)  | No indoor condition; contention-based; below 5925 MHz max -37 dBm/MHz (49) |

- Derived: in 6 GHz the PSD cap reaches the EIRP cap at 20 MHz (12.5 x 20 = 250 mW; 1.25 x 20 = 25 mW). A wider channel spreads the same total EIRP, so per-MHz power
  falls (250 mW over 160 MHz = 1.56 mW/MHz). Wide 6 GHz channels trade range for rate.
- 5600-5650 MHz (the weather-radar sub-band) is not in item 12, so an Australian RLAN under item 12 never meets the ETSI 10-minute CAC case.
- DFS in Australia: items 11 and 12 require "Dynamic Frequency Selection", and TPC above a threshold, and only note that IEEE 802.11 provides for both.
  The instrument sets no CAC time, non-occupancy period or detection threshold (negative finding, VERIFIED_PRIMARY, same instrument, checked 2026-10-29).
  Those values come from the equipment test standard, [ETSI EN 301 893 V2.2.1 (2024-11)](https://www.etsi.org/deliver/etsi_en/301800_301899/301893/02.02.01_60/en_301893v020201p.pdf) Table D.1:
  CAC 60 s (10 min in 5600-5650 MHz), channel move 10 s, non-occupancy 30 min; V2.1.1 (2017) has the same values. VERIFIED_PRIMARY (checked 2026-10-29).
- Which EN 301 893 edition the Australian equipment rules call up (via AS/NZS 4268) is UNVERIFIED; read the Short Range Equipment Standard before relying on it.
- Equipment must also meet the Short Range Equipment Standard in the Radiocommunications Equipment (General) Rules 2021 (ACMA LIPD page, checked 2026-10-29).

## Radio link budget

Helper: `just link-budget <file>` ([link_budget.py](../scripts/link_budget.py)); free space plus earth bulge only.

```text
Point-to-point link budget (dB and dBm; each line adds or subtracts)
  Tx power (dBm) - Tx cable/connector loss + Tx antenna gain (dBi)  = EIRP   <-- regulatory cap applies here
- free-space path loss                                              (ITU-R P.525)
- obstruction or diffraction loss                                   (ITU-R P.526)
- gas, rain, multipath allowance                                    (P.530; P.838 above ~10 GHz)
+ Rx antenna gain (dBi) - Rx cable/connector loss
= received signal level, RSL (dBm)
fade margin (dB) = RSL - Rx sensitivity at the needed MCS and channel width (datasheet)
```

- Earth bulge = d1 d2 / (12.74 k) m (geometry, derived). Use tropical-climate clearances where climate is uncertain.
- State the availability target, the method and the margin together.

```text
Service path through a wireless site (X = typical failure point)
+--------+   +------------+   +------------+   +-------------+   +---------+   +----------+   +---------+
| client |-->| RF airtime |-->| AP / radio |-->| uplink, PoE |-->| gateway |-->| backhaul |-->| service |
+--------+   +------------+   +------------+   +-------------+   +---------+   +----------+   +---------+
                    X                X                X               X              X
              interference       DFS move       power budget   local services  fade, outage
```

## Usable throughput from PHY rate

A PHY (data) rate is the on-air rate of one frame at one MCS, width, stream count and guard interval. Users get goodput: what is left after contention, preambles,
acknowledgements, TCP acknowledgements, retries, other clients and the other direction. Plan from goodput; quote PHY rates only as an input.

Wi-Fi rules (all checked 2026-10-29):

| Rule                                                      | Value or method                                                                     | Evidence                               |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------- |
| Data rate is not throughput                               | Overhead: management frames, contention, collisions, ACKs; varies with SNR and RSSI | VERIFIED_SECONDARY Cisco 212892        |
| Planning ratio: one client, clean channel, large transfer | Expected throughput = data rate x 0.7 (65-70% efficiency)                           | VERIFIED_SECONDARY Cisco 212892        |
| Per-access overhead does not shrink with rate             | 802.11n EDCA: mean idle 110.5 us per frame; 1500 B lasts 80 us at 150 Mbps          | VERIFIED_SECONDARY Salameh 2014        |
| Without aggregation, efficiency collapses                 | 600 Mbps 802.11n sending single frames: 9% of capacity                              | VERIFIED_SECONDARY Salameh 2014        |
| Aggregation (A-MPDU) recovers most of it                  | 802.11n, 1500 B: 72.2 Mbps -> 32.45 without / 67.76 with; 600 -> 52.24 / 469.4      | VERIFIED_SECONDARY Candela slides      |
| TCP ACKs cost airtime too                                 | 802.11a 54 Mbps: ideal-MAC UDP 30.2; measured TCP 19.4 Mbps (36%), one client       | VERIFIED_SECONDARY Salameh 2014        |
| The medium is shared                                      | One client 160-200 Mbps; two at once 80-100 each; four 40-50 each                   | VERIFIED_SECONDARY Cisco 212892        |
| Half duplex: one transmitter at a time                    | DL, UL and every client share one airtime budget; so do co-channel cells in range   | UNVERIFIED (CSMA/CA principle)         |
| Slow clients cost more airtime per bit                    | Size with airtime-weighted rates (method below), not the mean rate                  | UNVERIFIED (method; airtime principle) |

Wi-Fi method:

1. Take each client class's data rate at its planned cell-edge signal from the MCS table (width, streams, guard interval, MCS from the survey's RSSI and SNR).
2. Single-client goodput = data rate x efficiency. Use 0.7 for planning; replace with a measured ratio (iperf, large transfer) for the real client and AP.
3. Cell goodput when n clients each get equal throughput (each needs time 1 / R_i per bit): per-client x = 1 / sum(1 / R_i); cell total = n x. R_i is the
   goodput rate from step 2. This is arithmetic; the equal-throughput assumption is UNVERIFIED and real schedulers (airtime fairness, OFDMA) change it.
4. Divide by the number of co-channel cells that hear each other, then compare with busy-hour demand per direction. Keep utilisation headroom (see the
   [survey acceptance template](../templates/wifi-survey-acceptance.md)).

Point-to-point and point-to-multipoint TDD radios:

| Rule                                          | Value or method                                                                         | Evidence                                   |
| --------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------ |
| TDD splits one channel in time                | DL = aggregate x DL share; UL = aggregate x UL share; never quote aggregate as each way | VERIFIED_SECONDARY ePMP PtP primer         |
| Fixed ratios                                  | ePMP: 75/25, 50/50, 30/70 fixed per frame; Flexible adapts per frame                    | VERIFIED_SECONDARY ePMP PtP primer         |
| Reuse needs identical ratio and GPS sync      | Same DL/UL ratio on neighbouring sectors and towers; not Flexible                       | VERIFIED_SECONDARY ePMP optimisation guide |
| Uplink-heavy traffic (CCTV)                   | Ratio from measured demand per direction; Cambium suggests 30/70 for CCTV               | VERIFIED_SECONDARY ePMP PtP primer         |
| Modulation steps down as the signal fades     | Rate at fade = highest MCS whose sensitivity is at or below the faded RSL               | UNVERIFIED (method; datasheet values)      |
| Vendor capacity tables include frame overhead | Use the per-MCS, width and ratio table; PHY x ratio overstates                          | UNVERIFIED (method)                        |
| PtMP subscribers share the sector             | Divide by active subscribers, weighted by their MCS (Wi-Fi method)                      | UNVERIFIED (method)                        |

Sources for the two tables above (checked 2026-10-29):

- Cisco 212892, "Validate and Test Wi-Fi 6/6E and Wi-Fi 7 Wireless Throughput":
  [Cisco TAC document 212892](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
  (Cisco TAC, updated 2025-01-08).
- Salameh 2014: [Salameh et al., "HACK: Hierarchical ACKs for Efficient Wireless Medium Utilization", USENIX ATC 2014](https://www.usenix.org/system/files/conference/atc14/atc14-paper-salameh.pdf).
- Candela slides: [Candela Technologies, "Wi-Fi Technology Fundamentals" module 3, session 3d, aggregation table](https://candelatech.com/courses-2023/Session3d_slides.pdf).
- ePMP PtP primer, Cambium "ePMP Point-to-Point Configuration Primer" (software 3.0):
  [community-hosted copy](https://d1okf4ta8xniw3.cloudfront.net/original/2X/a/a04632b940f8e276874b591c67c87bf4cd19f8b3.pdf).
- ePMP optimisation guide: [Cambium ePMP "Optimization Guide", community-hosted copy](https://d1okf4ta8xniw3.cloudfront.net/original/2X/b/befb3be044d619c009700b5d8a93b33b497d8f93.pdf).

```text
TDD frame on one channel (75/25 shown); the same split repeats every frame
|<--------------------------------- frame period --------------------------------->|
| downlink: 75% of usable time                              |gap| uplink: 25%   |gap|
fade -> modulation steps down -> both directions shrink by the same factor
```

### Worked example: throughput

Wi-Fi cell. Inputs: Cisco's example of a 2-stream Wi-Fi 6 client on 20 MHz, data rate 240-280 Mbps (Cisco 212892, linked above).
Use 280 Mbps. Ten active clients; three of them are slow clients at 70 Mbps (illustrative input).

| Step                                              | Calculation                             | Result                          |
| ------------------------------------------------- | --------------------------------------- | ------------------------------- |
| Fast client goodput                               | 280 x 0.7                               | 196 Mbps                        |
| Slow client goodput                               | 70 x 0.7                                | 49 Mbps                         |
| Ten fast clients, equal throughput                | 196 / 10                                | 19.6 Mbps each, 196 Mbps cell   |
| Seven fast + three slow                           | x = 1 / (7 / 196 + 3 / 49) = 1 / 0.0969 | 10.3 Mbps each, 103 Mbps cell   |
| Effect of three slow clients                      | 103 / 196                               | Cell goodput falls by about 47% |
| Same cell on a channel shared with a neighbour AP | 103 / 2                                 | About 52 Mbps for all ten       |

Verdict: the cell supports 10 Mbps per client only with no co-channel neighbour. Move slow clients' coverage up (more APs, raise minimum data rate) before adding width.

PtP TDD link. Inputs: the 10 km link from the [link budget worked example](#worked-example), RSL -63.71 dBm. Illustrative datasheet rows (use the real radio's): top MCS
needs -65 dBm and gives 400 Mbps aggregate; the middle MCS needs -71 dBm, 280 Mbps; a low MCS needs -77 dBm, 160 Mbps. Ratio 75/25.

| State      | RSL (dBm) | Highest MCS that closes | Aggregate | Downlink (x 0.75) | Uplink (x 0.25) |
| ---------- | --------- | ----------------------- | --------- | ----------------- | --------------- |
| Clear sky  | -63.71    | Top (-65)               | 400 Mbps  | 300 Mbps          | 100 Mbps        |
| 6 dB fade  | -69.71    | Middle (-71)            | 280 Mbps  | 210 Mbps          | 70 Mbps         |
| 12 dB fade | -75.71    | Low (-77)               | 160 Mbps  | 120 Mbps          | 40 Mbps         |

- Verdict: if the service needs 150 Mbps downlink at the availability target, the link must hold the middle MCS through the design fade. The 16.29 dB margin in the
  link budget was against -80 dBm, not against the rate the service needs. State margin per required MCS.
- Then measure: MCS and throughput per direction under load, through a weather cycle (see [PtP link record](../templates/ptp-link-record.md)).

## Access and edge constraints

- Choose 802.1X (EAP-TLS preferred), PSK/SAE, guest or onboarding from client capability and risk.
- Separate AP management, client, guest, IoT and backhaul trust. No uniform VLAN/SSID scheme that ignores client isolation.
- Unreliable WAN: local auth fallback, cached policy, local DNS/DHCP/time, monitoring backfill, survival without the cloud controller.
- IoT/OT may need narrow exception policies and maintenance windows. No broad scans or firmware updates without scope.

## Patterns and anti-patterns

| Pattern                                   | Use when                     | Anti-pattern                   | Why it fails                             |
| ----------------------------------------- | ---------------------------- | ------------------------------ | ---------------------------------------- |
| Capacity plan from airtime and client mix | Dense sites                  | Coverage-only (RSSI) plan      | Cells full; slow clients consume airtime |
| Width sized from reuse                    | Many APs                     | Widest channel everywhere      | Co-channel contention cuts throughput    |
| Split SSIDs or WPA3 everywhere            | Tri-band with legacy clients | One WPA2 SSID on 6 GHz         | 6 GHz forbids WPA2                       |
| Non-DFS or monitored DFS for backhaul     | Critical radio links         | Unlogged DFS channel           | Radar move drops the link without trace  |
| Apparatus licence for critical PtP        | Interference must not occur  | Class-licence band for a trunk | No protection from new interferers       |
| Margin from availability target           | Every PtP link               | Fixed "20 dB" rule             | Over- or under-built for the climate     |
| Local services at the branch              | Satellite or radio WAN       | Central-only DHCP, DNS, auth   | WAN loss stops the site                  |

## Failure modes and tests

| Failure                             | Symptom                              | Blast radius                | Test that proves the design handles it                 |
| ----------------------------------- | ------------------------------------ | --------------------------- | ------------------------------------------------------ |
| DFS radar event                     | AP goes quiet or moves; clients drop | Cell, or the whole backhaul | Trigger or simulate DFS; log; confirm fallback channel |
| Co-channel contention               | High utilisation, low throughput     | Neighbouring cells          | Busy-hour survey; utilisation and retry per channel    |
| Roaming failure                     | Voice drops, re-auth delays          | Mobile clients              | Walk test per client type with FT on and off           |
| Rain or multipath fade              | Modulation drops, then outage        | Everything behind the link  | Fade margin over a weather cycle; MCS under load       |
| Fresnel obstruction (growth, build) | Lower RSL than predicted             | Link                        | Predicted vs measured RSL both ends, within a few dB   |
| TDD desensitisation                 | Throughput loss on co-located radios | Sector or site              | Compare with neighbour radios off; check sync          |
| Controller or WAN loss              | New clients cannot join              | Site                        | Cut WAN; join a new client; auth fallback works        |
| AP power or uplink loss             | Coverage hole                        | Cell                        | Pull PoE; neighbours cover or the gap is recorded      |

Also test guest isolation, policy denial and monitoring freshness. Record survey limits instead of calling a desk design "validated coverage".

## Worked example

Question: does a 5.8 GHz PtP link close with 15 dB margin and 60% Fresnel clearance at 10 km, and at 15 km?

Inputs: Tx 20 dBm, 23 dBi each end, 2 dB losses, sensitivity -80 dBm, obstacle 10 m below the line at mid-path.

| Step                          | 10 km (`just link-budget examples/link-budget.json`) | 15 km (same values, d = 15) |
| ----------------------------- | ---------------------------------------------------- | --------------------------- |
| FSPL                          | 127.71 dB                                            | 131.23 dB                   |
| RSL = 20 + 23 + 23 - 2 - FSPL | -63.71 dBm                                           | -67.23 dBm                  |
| Fade margin = RSL - (-80)     | 16.29 dB: pass                                       | 12.77 dB: below 15          |
| Midpoint F1                   | 11.37 m                                              | 13.92 m                     |
| Clearance after earth bulge   | 8.53 m = 75% F1: pass                                | 6.69 m = 48% F1: below 60%  |
| Exit code                     | 0                                                    | 1                           |

- Hand check (10 km): 32.4 + 20 log10 5800 (75.3) + 20 log10 10 (20.0) = 127.7 dB. Matches.
- Verdict for 15 km: raise antennas by about 2 m for clearance, and use larger antennas or a lower MCS for margin. Rerun.
- The model has no rain, multipath or EIRP check; confirm EIRP against the LIPD instrument.

## Review checklist

- [ ] Capacity plan uses client mix and airtime, not coverage alone.
- [ ] Channel widths sized from AP count and reuse; 2.4 GHz at 20 MHz.
- [ ] Security per band stated; 6 GHz uses WPA3 or OWE with PMF.
- [ ] DFS behaviour and logging decided for every critical cell and backhaul.
- [ ] Regulatory limits read from the current instrument; licence type chosen per link.
- [ ] `just link-budget` run; margin tied to an availability target; Fresnel and bulge checked.
- [ ] Predicted vs measured RSL recorded both ends after install.
- [ ] Capacity stated as goodput per direction, airtime-weighted for slow clients; TDD ratio and per-MCS fade margin stated.
- [ ] 5/6 GHz EIRP and PSD read from LIPD 2025 Table 8; indoor-only items (10, 11, 13) not used outdoors.
- [ ] Branch keeps working through WAN and controller loss.

## Further reading

Standards and certification:

- [IEEE 802.11-2024](https://standards.ieee.org/ieee/802.11/10548/): base MAC/PHY including 802.11k/r/v behaviour.
- [IEEE 802.11be-2024](https://standards.ieee.org/ieee/802.11be/7516/): Wi-Fi 7 (EHT, MLO) normative detail.
- [IEEE 802.11 timelines](https://www.ieee802.org/11/Reports/802.11_Timelines.htm): which amendment is published, rolled up or in draft.
- [Wi-Fi Alliance security][wfa-sec] and [Wi-Fi CERTIFIED 7][wfa-7]: certification-level security and feature requirements.

Propagation and link budgets:

- [ITU-R P.530][p530]: clearance rules, multipath and rain outage prediction on terrestrial LOS links.
- [ITU-R P.525][p525] and [ITU-R P.526](https://www.itu.int/rec/R-REC-P.526/en): free-space loss and diffraction over obstacles.
- [ITU-R P.837](https://www.itu.int/rec/R-REC-P.837/en) and [ITU-R P.838](https://www.itu.int/rec/R-REC-P.838/en): rainfall rate and rain attenuation above ~10 GHz.

Australian regulation:

- [LIPD Class Licence 2025][lipd]: permitted bands, EIRP and conditions before any channel or power plan.
- [ACMA LIPD overview][acma-lipd]: which equipment rules apply and the Murchison radio quiet zone.
- [ACMA 6 GHz outcomes paper (Dec 2024)][acma-6g]: lower and upper 6 GHz RLAN decisions.
- [ACMA licence register][acma-reg]: apparatus licences near a planned path.

[meraki]: https://documentation.meraki.com/MR/Encryption_and_Authentication/WPA3_Encryption_and_Configuration_Guide
[wfa-sec]: https://www.wi-fi.org/discover-wi-fi/security
[wfa-7]: https://www.wi-fi.org/discover-wi-fi/wi-fi-certified-7
[p525]: https://www.itu.int/rec/R-REC-P.525/en
[p530]: https://www.itu.int/rec/R-REC-P.530/en
[lipd]: https://www.legislation.gov.au/F2025L01047/latest/text
[acma-lipd]: https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence
[acma-reg]: https://www.acma.gov.au/register-radiocommunications-licences
[acma-6g]: https://acma.gov.au/sites/default/files/2024-12/Outcomes%20paper%20-%20Future%20use%20of%20the%20upper%206%20GHz%20band_0.pdf
