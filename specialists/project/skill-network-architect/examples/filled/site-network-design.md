---
Title: site-a site network design (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/site-network-design.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Build sheet for site-a after DES-012: satellite plus LTE WAN, tunnel MTU from `just mtu`, a 3.2 km 5 GHz PtP link from `just link-budget`, VLANs,
  Wi-Fi, OOB, PoE and UPS budget, monitoring and acceptance. All site facts are fictional.
---

# site-a site network design

Fills template: [templates/site-network-design.md](../../templates/site-network-design.md).

- Fictional operator "Example Remote Networks" (ERN). Device and site facts are invented and labelled USER_STATED; datasheet values not read from a real datasheet are UNVERIFIED.
- Inputs: [site-network-design.json](site-network-design.json) (MTU), [site-network-design-radio.json](site-network-design-radio.json) (radio).
- Design: [DES-012](design.md). Addresses: [ip-addressing-plan.md](ip-addressing-plan.md).

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

How this example applied the template's rules:

- One sheet for site-a; the other 23 LTE-covered sites use the same sheet with a per-site delta table (not shown).
- Specialist facts still to confirm: site box WAN ports and MTU settings (skill-smc), switch PoE budget (skill-mikrotik), PtP and AP models and sensitivity (skill-cambium).
- Both models below pass; that is static evidence. The "Measured" columns stay empty until acceptance (T-05, T-07).
- Red flags scanned before review: the fade margin passes by only 0.27 dB; the LTE and OOB devices share a carrier (CF-02 in the failure analysis).

## 1. Site summary

| Field                                           | Value                                                                                 | Label       |
| ----------------------------------------------- | ------------------------------------------------------------------------------------- | ----------- |
| Site code / type / address block                | site-a / clinic with pump station, satellite + LTE / 10.80.0.0/22, 2001:db8:4001::/48 | USER_STATED |
| Services carried                                | booking and voice via hub-1 (REQ-01..04), pump telemetry (REQ-01), guest Wi-Fi local  | USER_STATED |
| Users / devices (peak)                          | 9 staff + 60 guests / 96 devices                                                      | USER_STATED |
| Access constraints (travel time, hours, escort) | 6 h drive from the regional depot; clinic hours 08:00-18:00; no escort needed         | USER_STATED |
| Site owner / ops owner                          | clinic services manager / NOC lead                                                    | USER_STATED |

## 2. Topology

```text
site-a topology (planned; X = single point, accepted in DES-012: site box and switch)
+---------------------+                       +---------------------+
| SAT-1 LEO network   |                       | MNO-1 LTE network   |
+---------------------+                       +---------------------+
        |  A: satellite 100/15 Mbit/s                 |  B: LTE 30/10 Mbit/s
        |  (terminal on roof, PoE injector)           |  (LTE router, ext. antenna)
        +-------------------+-------------------------+
                            |
                  +---------------------+         +------------------+
                X | site box (rev-A)    |<-console-| OOB device       |--> MNO-1 own SIM --> hub-1 mgmt
                  +---------------------+         +------------------+
                            |  trunk (VLAN 10, 20, 30, 40, 50)
                  +---------------------+
                X | MikroTik PoE switch |
                  +---------------------+
                            |  access and trunk ports
       +-----------+--------+---------+------------+
       |           |                  |            |
   +-------+   +--------+   +-----------------+   +---------+
   | 3 APs |   | 4 IP   |   | PtP radio 5745  |   | camera  |
   |       |   | phones |   | MHz, 3.2 km     |   | (IoT)   |
   +-------+   +--------+   +-----------------+   +---------+
                                     |
                            +-----------------+
                            | pump station    |  telemetry RTU, VLAN 40
                            | (clinic radio)  |
                            +-----------------+
power: mains --> UPS 1000 VA / 600 W --> site box, switch (PoE), LTE router, sat terminal, OOB device
```

## 3. WAN and backhaul

| Link | Type (fibre, radio, fixed access, LTE, satellite) | Provider / circuit ref  | Committed / burst rate    | Latency p95 | Diverse path from     | Failover method and time        | Label       |
| ---- | ------------------------------------------------- | ----------------------- | ------------------------- | ----------- | --------------------- | ------------------------------- | ----------- |
| A    | LEO satellite, CGNAT, underlay MTU 1500           | SAT-1 / SAT1-SVC-0101   | best effort / plan        | 62 ms       | B: different network; | primary                         | USER_STATED |
|      |                                                   |                         |   100/15 Mbit/s           |             |   shared site mains   |                                 |             |
| B    | LTE, CGNAT, underlay MTU 1428 (ASM-01)            | MNO-1 / SIM             | best effort / 30/10       | 88 ms       | A: as above           | probe loss 3 x 10 s, then route | USER_STATED |
|      |                                                   |   ref MNO1-0101         |   Mbit/s measured         |             |                       |   move; budget 60 s (REQ-02)    |             |

## 4. MTU budget

Tunnel interface MTU 1360 on both tunnels (CHG-031). The model checks that each underlay carries a 1360-byte inner packet after the WireGuard IPv4 overhead of 60 bytes (pack value, scripts/README.md).

```text
$ just mtu examples/filled/site-network-design.json            # exit 0
  "status": "pass"
  site-a-sat-wg-1360: underlay 1500, overhead 60, payload_mtu 1440, tcp_mss_ipv4 1400
  site-a-lte-wg-1360: underlay 1428, overhead 60, payload_mtu 1368, tcp_mss_ipv4 1328
```

| Path               | Underlay MTU | Encapsulation layers | Required payload MTU | Model result (`mtu_budget.py`)    | Measured (DF probe)     |
| ------------------ | ------------ | -------------------- | -------------------- | --------------------------------- | ----------------------- |
| site-a-to-hub, sat | 1500         | wireguard-ipv4       | 1360                 | exit 0, margin 80 B (1440 - 1360) | not yet measured (T-05) |
| site-a-to-hub, LTE | 1428         | wireguard-ipv4       | 1360                 | exit 0, margin 8 B (1368 - 1360)  | not yet measured (T-05) |

Choice recorded in ADR-0007 consequences and CHG-031: lower the inner MTU to 1360 on both tunnels and clamp TCP MSS to 1320 (1360 - 40) at the site box, so a failover never changes the payload
ceiling. The 8-byte LTE margin rests on ASM-01; the DF probe in T-05 settles it.

## 5. Radio links

PtP from the site box switch to the pump station. Inputs USER_STATED (path survey) and UNVERIFIED (radio sensitivity at the chosen rate, not read from a datasheet here).

```text
$ just link-budget examples/filled/site-network-design-radio.json   # exit 0
  site-a-to-clinic-5745: fspl_db 117.73, rx_level_dbm -55.73, fade_margin_db 15.27,
  midpoint_fresnel_m 6.46; obstacle at 1.1 km: fresnel_radius_m 6.14,
  effective_clearance_m 4.86, clear_fraction 0.793
```

| Link                  | Band / width  | Distance | Antenna gains | Tx power (in EIRP limit)     | Rx sens. at rate  | Fade margin req. / model | Fresnel clear    | Model exit | Measured RSSI / SNR |
| --------------------- | ------------- | -------- | ------------- | ---------------------------- | ----------------- | ------------------------ | ---------------- | ---------- | ------------------- |
| site-a-to-clinic-5745 | 5745 MHz /    | 3.2 km   | 23 / 23 dBi   | 18 dBm; EIRP 41 dBm, limit   | -71               | 15 / 15.27 dB            | 79.3% of F1 at   | 0          | not yet             |
|                       |   20 MHz      |          |               |   UNVERIFIED (CON-04)        |   dBm             |                          |   the water tank |            |   measured (T-07)   |
|                       |               |          |               |                              |   (UNVERIFIED)    |                          |                  |            |                     |

Check of the arithmetic: FSPL = 20 log10(3.2) + 20 log10(5745) + 32.44 = 10.10 + 75.19 + 32.44 = 117.73 dB; received = 18 + 23 + 23 - 2 - 117.73 = -55.73 dBm; margin = -55.73 - (-71) = 15.27 dB. The
margin clears the requirement by 0.27 dB and the model has no rain or multipath term, so the review asks for one of: a rate one step lower (better sensitivity), or 1 dB less cable loss by mounting the
radio at the mast head. Fresnel clearance 79.3% is above the 60% rule.

## 6. Switching and VLANs

| VLAN | Name / function   | VRF          | IPv4 / IPv6                            | Ports (access / trunk)           | STP / loop protection      | DHCP snooping, RA guard | Label       |
| ---- | ----------------- | ------------ | -------------------------------------- | -------------------------------- | -------------------------- | ----------------------- | ----------- |
| 10   | management        | corp         | 10.80.0.64/26 / 2001:db8:4001:10::/64  | trunk to box, APs, PtP; access 8 | RSTP, edge on access ports | on / on                 | USER_STATED |
| 20   | staff users       | corp         | 10.80.1.0/24 / 2001:db8:4001:20::/64   | APs (tagged); access 5-6         | RSTP, BPDU guard on access | on / on                 | USER_STATED |
| 30   | voice             | corp         | 10.80.0.128/26 / 2001:db8:4001:30::/64 | access 1-4 (phones)              | RSTP, BPDU guard           | on / on                 | USER_STATED |
| 40   | IoT and telemetry | corp         | 10.80.0.192/26 / 2001:db8:4001:40::/64 | PtP trunk; access 7 (camera)     | RSTP; loop detect on PtP   | on / on                 | USER_STATED |
| 50   | guest Wi-Fi       | guest-site-a | 172.16.50.0/24 / none (local NAT only) | APs (tagged)                     | RSTP                       | on / n/a                | USER_STATED |

Port map (MikroTik PoE switch, port numbers USER_STATED):

| Port | Device         | VLAN mode                          | PoE class                              | Speed / duplex expected |
| ---- | -------------- | ---------------------------------- | -------------------------------------- | ----------------------- |
| 1-4  | IP phones      | access 30                          | 802.3af                                | 1G full                 |
| 5-6  | staff desktops | access 20                          | off                                    | 1G full                 |
| 7    | camera         | access 40                          | 802.3af                                | 100M full               |
| 8    | OOB device LAN | access 10                          | off                                    | 1G full                 |
| 9-11 | APs 1-3        | trunk 10 untagged, 20/40/50 tagged | 802.3at                                | 1G full                 |
| 12   | PtP radio      | trunk 10 untagged, 40 tagged       | 802.3at | 1G full                 |
| 13   | site box LAN   | trunk 10, 20, 30, 40, 50           | off                                    | 1G full                 |

## 7. Wi-Fi

| SSID      | VLAN | Security (WPA3, 802.1X, PSK)    | Band(s)    | Client count design | AP count / model              | Channel plan and width                 | Min data rate | Survey ref          |
| --------- | ---- | ------------------------------- | ---------- | ------------------- | ----------------------------- | -------------------------------------- | ------------- | ------------------- |
| ern-staff | 20   | WPA3-Enterprise (RADIUS         | 5 GHz      | 20                  | 3 / Cambium indoor            | 36, 44, 52 at 20 MHz; 149 avoided (PtP | 12 Mbit/s     | SURV-site-a-2026-09 |
|           |      |   at hub-1)                     |            |                     |   AP (skill-cambium)          |   at 5745)                             |               |                     |
| ern-guest | 50   | WPA3-Personal, rotated monthly  | 2.4 +      | 60                  | same 3 APs                    | 2.4 GHz 1, 6, 11 at 20 MHz             | 12 Mbit/s     | SURV-site-a-2026-09 |
|           |      |                                 |   5 GHz    |                     |                               |                                        |               |                     |
| ern-iot   | 40   | WPA2-PSK (legacy sensors)       | 2.4 GHz    | 6                   | same 3 APs                    | as guest                               | 6 Mbit/s      | SURV-site-a-2026-09 |

ern-staff depends on RADIUS at hub-1: a client that is already associated keeps working during a WAN outage, but a new 802.1X login fails while both WAN paths are down (FM-07).

## 8. Management and out-of-band

| Item                                           | Value                                                                                                 |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Management VLAN / VRF / prefix                 | VLAN 10 / corp / 10.80.0.64/26, gateway 10.80.0.65; site box loopback 10.80.0.1/32                    |
| OOB path (independent of production backhaul?) | OOB device on its own MNO-1 SIM: independent of the site box and the tunnels, shares MNO-1 with WAN B |
| Console access to router/switch                | OOB device serial ports 1 (site box) and 2 (switch)                                                   |
| Break-glass access when AAA is down            | local break-glass account per device, credential in the ERN secret store, two-person retrieval        |
| Config backup target and schedule              | nightly to hub-1 by Nautobot Golden Config; before and after every change (CHG pre-check P4)          |

## 9. Power and PoE budget

Draw values USER_STATED from the site survey; maxima are UNVERIFIED until checked against each datasheet.

| Device                     | Qty | Draw (typ / max W) | PoE class / source port  | Subtotal max W |
| -------------------------- | --- | ------------------ | ------------------------ | -------------- |
| Cambium indoor AP          | 3   | 9 / 13             | 802.3at / ports 9-11     | 39             |
| Cambium PtP radio (local)  | 1   | 10 / 15            | 802.3at / port 12        | 15             |
| IP phone                   | 4   | 3 / 5              | 802.3af / ports 1-4      | 20             |
| camera                     | 1   | 5 / 8              | 802.3af / port 7         | 8              |
| PoE subtotal               |     |                    |                          | 82             |
| site box                   | 1   | 18 / 25            | mains via UPS            | 25             |
| MikroTik switch (own draw) | 1   | 12 / 20            | mains via UPS            | 20             |
| LTE router                 | 1   | 5 / 8              | mains via UPS            | 8              |
| satellite terminal         | 1   | 50 / 75            | own PoE injector via UPS | 75             |
| OOB device                 | 1   | 4 / 6              | mains via UPS            | 6              |
| UPS load total             |     |                    |                          | 216            |

Switch PoE budget 140 W (UNVERIFIED datasheet) vs demand 82 W (headroom (140 - 82) / 140 = 41.4%). UPS capacity 1000 VA / 600 W, runtime at 216 W 38 min (USER_STATED, vendor runtime chart) vs required
30 min (REQ-09).

## 10. Monitoring and acceptance

| Signal                        | Source                                | Threshold                                     | Alert owner | Acceptance test and result       |
| ----------------------------- | ------------------------------------- | --------------------------------------------- | ----------- | -------------------------------- |
| Backhaul reachability / loss  | per-tunnel probe, Prometheus          | 3 losses in 30 s; loss > 2% over 5 min        | NOC on-call | T-01, T-02: not yet run          |
| Standby tunnel health         | wg-lte keepalive + probe              | no handshake for 180 s                        | NOC on-call | T-06: not yet run                |
| DF probe at 1360 bytes        | probe host on VLAN 10, both tunnels   | any loss of the 1360-byte probe               | NOC on-call | T-05: not yet run                |
| Radio RSSI / SNR / modulation | OpenWISP via the radio's SNMP         | RSSI below -62 dBm or rate step down 2 levels | NOC on-call | T-07: not yet run                |
| PoE and UPS state             | switch PoE table; UPS SNMP            | PoE use > 80% of 140 W; on battery > 60 s     | NOC on-call | T-08: UPS self-test, not yet run |
| User-outcome probe            | HTTPS probe to hub-1 VIP from VLAN 10 | success < 99.5% over 24 h                     | NOC lead    | T-01: not yet run                |

The RSSI alert threshold sits 6.27 dB below the -55.73 dBm model value, leaving room for normal variation before an alert, and well above the -71 dBm sensitivity.

## 11. Review state

| Revision | State           | Date       | Reviewer (role)   | Evidence                                                  |
| -------- | --------------- | ---------- | ----------------- | --------------------------------------------------------- |
| r1       | proposed        | 2026-10-20 | network architect | `just mtu` and `just link-budget` runs above              |
| r1       | evidence-needed | 2026-10-27 | NOC lead          | fade margin thin; PoE and UPS maxima need datasheet check |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
