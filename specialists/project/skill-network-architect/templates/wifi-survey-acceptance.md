---
Title: Wi-Fi survey and acceptance template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: >-
  Predictive versus on-site survey record, per-area targets for signal, SNR, channel utilisation, retries and roaming, client types tested,
  measured results against targets and sign-off.
---

# <site-code> Wi-Fi survey and acceptance

Based on (checked 2026-10-29):

- Cisco VoWLAN targets: cell edge -67 dBm, 25 dB SNR, utilisation under 50%, retransmissions under 20%, loss under 1%. VERIFIED_SECONDARY.
- Source: [Cisco VoWLAN Troubleshooting Guide, chapter 8](https://www.cisco.com/c/en/us/td/docs/wireless/technology/vowlan/troubleshooting/vowlan_troubleshoot/8_Site_Survey_RF_Design_Valid.html).
- Vendor guidance for voice from the 802.11a/b/g/n era. Adapted here: per-area targets, client classes and a results table.

## Contents

- [How to use](#how-to-use)
- [1. Survey record](#1-survey-record)
- [2. Areas and targets](#2-areas-and-targets)
- [3. Client types](#3-client-types)
- [4. Measured results versus targets](#4-measured-results-versus-targets)
- [5. Deviations and actions](#5-deviations-and-actions)
- [6. Sign-off](#6-sign-off)
- [7. Review state](#7-review-state)

## How to use

- A predictive survey (floor plan, wall losses, AP model) designs; an on-site survey (pre-install AP-on-a-stick, or post-install validation) proves. Never sign off on a predictive survey alone.
- Set targets per area from the application and the weakest client, not one number for the building. Voice targets below are Cisco's; data-only and IoT areas need their own source or a label.
- Measure with the client types that will use the area (section 3). A survey adapter is not a phone.
- Record the survey tool, adapter, software version and the date; results are not comparable across adapters without that.
- Throughput targets are goodput per client at busy hour: method in [wireless-and-radio](../references/wireless-and-radio.md#usable-throughput-from-phy-rate).
- Regulatory limits (EIRP, PSD, indoor-only bands): same reference, Regulatory (Australia).
- Feeds the Wi-Fi section of [site-network-design](site-network-design.md) and the [test-and-acceptance-plan](test-and-acceptance-plan.md).

```text
Survey flow (each arrow needs the previous step's evidence)
+------------------+    +-------------------+    +-----------------+    +------------------+    +-----------+
| requirements per | -> | predictive survey | -> | pre-install     | -> | install, then    | -> | sign-off  |
| area and client  |    | (model, AP plan)  |    | AP-on-a-stick   |    | validation walk  |    | or rework |
+------------------+    +-------------------+    | (optional)      |    | + client tests   |    +-----------+
                                                 +-----------------+    +------------------+
predictive = design input only; validation = measured with real clients at busy hour
```

## 1. Survey record

| Field                                   | Predictive                   | On-site validation  |
| --------------------------------------- | ---------------------------- | ------------------- |
| Date / surveyor (role)                  |                              |                     |
| Tool and version                        |                              |                     |
| Adapter or reference client             | n/a                          |                     |
| Floor plan source and scale check       |                              |                     |
| Wall and material attenuation source    | *measured / library / assumed* | n/a                 |
| AP model, antenna, mounting height      |                              |                     |
| Survey type (passive, active, spectrum) | n/a                          |                     |
| Busy-hour conditions present?           | n/a                          | *yes / no; occupancy* |
| Report or project file reference        |                              |                     |

## 2. Areas and targets

| Area   | Use (voice, data, IoT) | Band(s) | Min signal | Min SNR | Roaming overlap   | Max utilisation | Max retries | Roam time | Goodput per client | Target source    |
| ------ | ---------------------- | ------- | ---------- | ------- | ----------------- | --------------- | ----------- | --------- | ------------------ | ---------------- |
| <area> | voice                  | 5 GHz   | -67 dBm    | 25 dB   | 15-20% (5 GHz)    | 50%             | 20%         | <n> ms    | <n> Mbps           | Cisco VoWLAN     |
| <area> | data                   |         | <n> dBm    | <n> dB  |                   | <n>%            | <n>%        |           | <n> Mbps           | *requirement ID* |
| <area> | IoT                    | 2.4 GHz | <n> dBm    | <n> dB  | n/a               |                 |             | n/a       |                    |                  |

Voice also needs noise floor at or below -92 dBm, packet loss under 1% and jitter under 100 ms (same Cisco source). Cisco states 20% overlap for 2.4 GHz and 15-20% for 5 GHz on different channels.

## 3. Client types

| Client class      | Example model / OS | Bands, streams, max width | 802.11k / v / r | WPA3 / 6 GHz | Roaming behaviour notes | Tested in areas |
| ----------------- | ------------------ | ------------------------- | --------------- | ------------ | ----------------------- | --------------- |
| Voice handset     |                    |                           |                 |              |                         |                 |
| Laptop            |                    |                           |                 |              |                         |                 |
| Scanner / IoT     |                    |                           |                 |              |                         |                 |
| Weakest supported |                    |                           |                 |              |                         |                 |

## 4. Measured results versus targets

| Area   | Signal p10 | SNR p10 | Utilisation (busy hour) | Retries | Roam time (client) | Goodput (client, direction) | Co-channel APs heard | Pass / fail |
| ------ | ---------- | ------- | ----------------------- | ------- | ------------------ | --------------------------- | -------------------- | ----------- |
| <area> |            |         |                         |         |                    |                             |                      |             |

- Report a low percentile (p10) of the survey points, not the mean; a mean hides the coverage holes.
- State whether measurements came from the survey adapter or a real client, and at which transmit power and channel plan.

## 5. Deviations and actions

| Area | Target missed | Measured | Cause (coverage, interference, client, config) | Action (AP move, power, channel, add AP, accept) | Owner | Re-test date |
| ---- | ------------- | -------- | ---------------------------------------------- | ------------------------------------------------ | ----- | ------------ |
|      |               |          |                                                |                                                  |       |              |

## 6. Sign-off

| Role                  | Name | Decision (accept, accept with exceptions, reject) | Exceptions accepted | Date |
| --------------------- | ---- | ------------------------------------------------- | ------------------- | ---- |
| Network architect     |      |                                                   |                     |      |
| Site or service owner |      |                                                   |                     |      |
| Installer             |      |                                                   |                     |      |

## 7. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
