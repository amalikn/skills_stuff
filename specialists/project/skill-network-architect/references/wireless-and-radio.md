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

| Rule                                                      | Value or threshold                                                   | Evidence                                               |
| --------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------ |
| Signal strength alone does not prove capacity             | Slowest, most-retrying clients set cell capacity                     | UNVERIFIED (airtime principle)                         |
| Plan from a measured survey and the regulatory instrument | Never from memory or vendor pages                                    | UNVERIFIED (method)                                    |
| 2.4 GHz channel width                                     | 20 MHz                                                               | UNVERIFIED (judgement)                                 |
| 5/6 GHz channel width                                     | From AP count and reuse, not the datasheet maximum                   | UNVERIFIED (judgement)                                 |
| DFS: availability check before use; move on radar         | Treat a DFS hit as an availability event; log it                     | UNVERIFIED (CAC times: read the instrument)            |
| 6 GHz security                                            | WPA3 or Enhanced Open (OWE) only; PMF mandatory; no WPA2             | VERIFIED_SECONDARY [Meraki WPA3 guide][meraki] (WPA3 v3.4 s11.2) |
| OWE transition mode on 6 GHz                              | Not supported                                                        | VERIFIED_SECONDARY [Meraki WPA3 guide][meraki]         |
| WPA3 networks require PMF                                 | Tri-band SSID needs WPA3 everywhere, or split SSIDs                  | VERIFIED_PRIMARY [WFA security][wfa-sec]               |
| Wi-Fi 7 (802.11be-2024)                                   | 320 MHz in 6 GHz, MLO, 4K-QAM                                        | VERIFIED_PRIMARY [WFA Wi-Fi 7][wfa-7]                  |
| 4K-QAM and MLO                                            | Need very high SNR; MLO needs client, AP and controller support      | UNVERIFIED (judgement)                                 |
| 802.11k / v / r                                           | Neighbour reports / BSS transition steering / fast re-keying         | UNVERIFIED (summary of IEEE 802.11)                    |
| Clients decide when to roam                               | Test real client types before FT on a shared SSID                    | UNVERIFIED (field observation)                         |
| Each SSID beacons per radio                               | SSID count costs airtime                                             | UNVERIFIED (judgement)                                 |
| Free-space loss                                           | Lbf = 32.4 + 20 log10 f(MHz) + 20 log10 d(km) dB                     | VERIFIED_PRIMARY [ITU-R P.525-5][p525] eq. 6           |
| First Fresnel radius                                      | F1 = 17.3 sqrt(d1 d2 / (f d)) m; f GHz, d km                         | VERIFIED_PRIMARY [ITU-R P.530-19][p530] s2.2.2         |
| Clearance                                                 | >= 60% F1 free space; 1.0 F1 at k = 4/3; 0.0-0.6 F1 at worst-month k | VERIFIED_PRIMARY [ITU-R P.530-19][p530] s2.2.2         |
| Fade margin                                               | Output of an availability target (P.530 methods), not a constant     | VERIFIED_PRIMARY [ITU-R P.530-19][p530]                |
| Co-located TDD radios                                     | Same frame timing and DL/UL ratio, or they desensitise               | UNVERIFIED (confirm with skill-cambium)                |

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
- Whether the 2025 instrument contains 6425-6585 MHz: UNVERIFIED (text not machine-readable at check time). Read it before planning 320 MHz channels.
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

[meraki]: https://documentation.meraki.com/MR/Encryption_and_Authentication/WPA3_Encryption_and_Configuration_Guide [wfa-sec]: https://www.wi-fi.org/discover-wi-fi/security [wfa-7]:
https://www.wi-fi.org/discover-wi-fi/wi-fi-certified-7 [p525]: https://www.itu.int/rec/R-REC-P.525/en [p530]: https://www.itu.int/rec/R-REC-P.530/en [lipd]:
https://www.legislation.gov.au/F2025L01047/latest/text [acma-lipd]: https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence [acma-reg]:
https://www.acma.gov.au/register-radiocommunications-licences [acma-6g]: https://acma.gov.au/sites/default/files/2024-12/Outcomes%20paper%20-%20Future%20use%20of%20the%20upper%206%20GHz%20band_0.pdf
