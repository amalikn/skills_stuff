---
Title: Operator context - site backhaul and links
Category: operator-context
Status: current
Authority: internal
Scope: One operator's remote-site backhaul (geostationary and LEO satellite, nbn legs); not general guidance
Last reviewed: 2026-11-10
Summary: >-
  Operator-specific facts about the links behind the operator's site boxes, harvested read-only on 2026-11-10: link classes and how the carrier is identified,
  measured round trips, loss and rates, why round trips set transfer time, the MTU gap, carrier NAT, the emergency satellite modem swap and what is measured.
  Each item has why it matters, an evidence path and the general section it applies to. No site, customer or people names, addresses or prices.
---

# Operator context: site backhaul and links

## Contents

- [How to read this file](#how-to-read-this-file)
- [Link classes and carriers](#link-classes-and-carriers)
- [Measured link profiles](#measured-link-profiles)
- [Design consequences](#design-consequences)
- [Carrier NAT and the emergency modem](#carrier-nat-and-the-emergency-modem)
- [What is measured](#what-is-measured)

## How to read this file

- `APN` below means `/Volumes/Data/_ai/_project/project_stuff/apn`. `SMC-SKILL` means `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`.
- Evidence labels: VERIFIED_SECONDARY (read from a project document, not re-observed) unless stated; "in source" means the source records it with that label.
- Subscriber broadband (nbn through an aggregator, Opticomm) is a different network: [access-and-voice.md](access-and-voice.md). Polling numbers over these links:
  [site-fleet-network.md](site-fleet-network.md)
  items 14, 15 and 50.

## Link classes and carriers

1. nbn Sky Muster Plus (geostationary) is the primary at most sites and at every Pi site; the x86 deployments of the past year use Starlink as primary, several legs per box, with one Sky Muster leg as
   backup; multi-WAN x86 boxes can carry several nbn legs each (six per box at the multi-box site). USER_STATED (operator, 2026-10-06); six legs VERIFIED_PRIMARY in source (2026-10-29).
   - Why: the link class decides what may be placed centrally and every timeout.
   - Evidence: `SMC-SKILL/references/01_overview.md` (section 2, Learned 2026-10-29)
   - Applies: [High-latency, satellite and radio links](../../references/wan-and-remote-access.md#high-latency-satellite-and-radio-links)
2. On a Pi site the Sky Muster terminal hangs off the site switch and reaches the box untagged on its one port; the public address answers as the retail satellite provider (IPSTAR), not nbn.
   VERIFIED-OBSERVED in source, 2026-10-20.
   - Evidence: `SMC-SKILL/references/03_communication-flows.md` (Learned 2026-10-20)
   - Applies: [Satellite and fixed wireless](../../references/australian-access-networks.md#satellite-and-fixed-wireless)
3. Decision (2026-10-08): the carrier of an uplink is read from the far side (public-address ASN, the Starlink dish's own ID), never from the build's interface name; each uplink is a Circuit whose
   provider is the carrier with the retail provider beside it, and the terminal is a black-box pass-through device. Built in the lab only.
   - Why: the build's `starlink` label now marks the Sky Muster backup (see site-fleet-network item 51).
   - Evidence: `APN/unified-network-controller/ARCHITECTURE.md` (WAN uplinks and their carriers)
   - Applies: [Redundancy and CGNAT](../../references/wan-and-remote-access.md#redundancy-and-cgnat)
4. Constraint C3 of the controller: constrained backhaul with outages measured in days, so no raw SNMP walks across the WAN and local buffering with replay is required.
   - Evidence: `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` (section 2)
   - Applies: [Polling over GEO and on-box readers](../../references/remote-site-fleet.md#polling-over-geo-and-on-box-readers)

## Measured link profiles

5. Read-only, 600 pings to the access proxy per box and 30-day speedtest medians, 2026-11-06 (VERIFIED_PRIMARY in source):

   | Link | Round trip min / avg / max | Loss | Rates (median) |
   | --- | --- | --- | --- |
   | Sky Muster, one box | 543 / 700 / 2447 ms | 3 of 600 (0.5 %) | 48 down / 5 up Mbit/s |
   | Sky Muster, about 300 sites | ping 560 to 700 ms | many sites' 10th percentile is 0 (failed tests) | 48 / 5 Mbit/s |
   | Starlink legs, one box | 56 / 64 / 100 ms | 0 of 600 | about 108 / 45 Mbit/s |
   | Starlink, four sites | ping 24 to 33 ms | - | 45 to 297 down, 5 to 57 up |

   - Why: the lab profiles (`geo` 48/5 Mbit/s, 700 ms, 0.25 % loss each way; `geo-slow` 5/1; `leo` 108/45, 64 ms) are calibrated from these. Speedtests use parallel connections, so one TCP
     stream gets less; jitter is not modelled.
   - Evidence: `APN/smc-resiliency/docs/pi/pi-spike-s3-delivery-20261106_1044.md` (section 2); `SMC-SKILL/references/01_overview.md` (Learned 2026-11-06)
   - Applies: [High-latency, satellite and radio links](../../references/wan-and-remote-access.md#high-latency-satellite-and-radio-links)
6. `Disputed`: skill-smc's link section says every box is on satellite with a minimum round trip of about 600 ms; the operator's later answer (Starlink under 100 ms on recent x86 sites) and the
   measured
   56 to 64 ms Starlink legs contradict it. The 600 ms floor holds for Sky Muster only. On one mixed box the Sky Muster backup measured 760 ms while its Starlink legs measured 60 to 68 ms.
   - Evidence: `SMC-SKILL/references/01_overview.md` (Network Link - Satellite against section 2); `SMC-SKILL/references/03_communication-flows.md` (Learned 2026-11-06)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)

## Design consequences

7. Round trips, not bandwidth, set transfer time on the geostationary link: a 41 MB image delta took 558 s at 48 Mbit/s and 600 s at 5 Mbit/s (about 500 sequential range requests at 700 ms), and
   38 s on the LEO profile. VERIFIED_PRIMARY (lab VMs).
   - Why: fewer, larger requests help more than a faster plan; a release store must serve HTTP/2 with range requests.
   - Evidence: `APN/smc-resiliency/docs/pi/pi-spike-s3-delivery-20261106_1044.md` (findings S3-5, S3-7, section 7)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)
8. No measured path MTU for Sky Muster or Starlink legs exists in the records read. The direct-reach overlay proposal starts its WireGuard interface at 1380 and measures in its trial (UNVERIFIED);
   the 1496 in the delivery lab is a lab-network artefact, not a field value.
   - Why: any tunnel design over these links needs a measured budget first.
   - Evidence: `APN/unified-network-controller/docs/reports/smc-and-site-network/direct-device-reach-options-20261015_1722.md` (constraints table);
     `APN/smc-resiliency/docs/pi/pi-spike-s3-delivery-20261106_1044.md` (section 6)
   - Applies: [MTU budget](../../references/wan-and-remote-access.md#mtu-budget)
9. Image delivery is bounded by throughput and quotas, not latency: a full Pi release is estimated at 1.2 to 2 GB compressed (UNVERIFIED until built), and activation waits for a site maintenance
   window (proposed 02:00 to 05:00 local time).
   - Evidence: `APN/smc-resiliency/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (section 8)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)

## Carrier NAT and the emergency modem

10. Every leg of a multi-WAN box can leave through one public address after carrier NAT, so per-leg theories about a far-end source-address policy cannot hold; Starlink legs lease from the RFC 6598
    shared space, which the overlay proposal reserves against.
    - Evidence: `SMC-SKILL/references/03_communication-flows.md` (Per-Site Public Egress IP); controller register D1.2 IC-O2
    - Applies: [Redundancy and CGNAT](../../references/wan-and-remote-access.md#redundancy-and-cgnat)
11. Thuraya to Iridium on the Pi flavour is a phone modem swap, not a backhaul change: the box's app reads a controller board that drives power rails, fans, the charger and a satellite modem for
    emergency calls and SMS. The same app is kept on an Iridium branch with new board firmware, rolled out per box; the Iridium site visits are the planned moment to fit new SD cards, and those
    plan rows were at risk in November 2026. USER_STATED (operator, 2026-10-06, update 2026-10-28); board reads VERIFIED_PRIMARY in source.
    - Why: the swap schedule drives the Pi image rollout.
    - Evidence: `SMC-SKILL/references/01_overview.md` (section 2, Tstik); `SMC-SKILL/references/02_service-map.md` (Learned 2026-10-30, 2026-11-02);
      `APN/smc-resiliency/docs/trackers/plan-tracker.md`
    - Applies: [Site dependencies on the box](../../references/remote-site-fleet.md#site-dependencies-on-the-box)

## What is measured

12. Measured today: an hourly speedtest exporter and ten iperf servers on every box, the controller's 15-minute per-leg reach check, an on-demand per-leg round-trip probe, and interface byte
    counters per VLAN in central Prometheus. Not measured: jitter, path MTU, application classification on the backhaul, a per-link internet alert. Per-site carrier links are not inventoried.
    - Evidence: `SMC-SKILL/references/02_service-map.md` (Monitoring); `SMC-SKILL/references/03_communication-flows.md`;
      `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` (notes)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
