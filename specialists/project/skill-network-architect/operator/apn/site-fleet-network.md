---
Title: Operator context - site fleet network lessons
Category: operator-context
Status: current
Authority: internal
Scope: One operator's remote-site fleet (site boxes behind satellite and terrestrial links); not general guidance
Last reviewed: 2026-10-29
Summary: >-
  Operator-specific lessons from the site-box fleet, its controller, access, switching and resolver projects, each with why it matters, an evidence path under
  the operator's project folder and the general reference section it applies to. No site, community, customer or people names, addresses or prices.
---

# Operator context: site fleet network lessons

## Contents

- [How to read this file](#how-to-read-this-file)
- [Site shape and placement](#site-shape-and-placement)
- [Management and access](#management-and-access)
- [Telemetry over satellite](#telemetry-over-satellite)
- [Discovery and identity](#discovery-and-identity)
- [Site services, WAN and power](#site-services-wan-and-power)
- [Controller exit and onboarding](#controller-exit-and-onboarding)
- [Site devices](#site-devices)
- [Datacenter switching and resolvers](#datacenter-switching-and-resolvers)
- [Withheld evidence paths](#withheld-evidence-paths)

## How to read this file

- These are facts about one operator's estate, harvested read-only on 2026-10-29. The general rule lives in the linked reference; this file holds the local evidence and numbers that taught it.
- `APN` below means `/Volumes/Data/_ai/_project/project_stuff/apn`. `SMC-SKILL` means `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`.
- The site box is the operator's single gateway appliance (an SMC); Teleport is the access proxy; Nautobot and OpenWISP form the controller being built to replace a vendor console.
- Evidence labels: VERIFIED_SECONDARY (read from a project document, not re-observed on the system) unless stated.
- Some evidence folders are named after a customer or community; those paths are withheld (last section).

## Site shape and placement

1. One box in the user's path (operator rule). A router plus a second box that both carry user traffic was withdrawn as a site shape; a second box is allowed only for extras and must fail open.
   - Why: series components multiply failure for one user outcome; recovery time, not a second box, limits a site.
   - Evidence: `APN/enterprise-strategy/.archcore/rules/one-box-in-the-user-path.rule.md`; `APN/enterprise-strategy/architecture/simplified-target-sketch-20261006_1350.md`
   - Applies: [Site shapes and the one-box rule](../../references/remote-site-fleet.md#site-shapes-and-the-one-box-rule)
2. Two site shapes are in play: router only (portal, filter, controller central) and one simplified site box with A/B updates and a watchdog.
   - Why: the shape decides what must work over the slowest link.
   - Evidence: same sketch.
   - Applies: [Site shapes and the one-box rule](../../references/remote-site-fleet.md#site-shapes-and-the-one-box-rule)
3. Router feasibility is decided on paper first (six steps, native / add-on / central / not possible per model and firmware), with the old box kept on the shelf in the pilot.
   - Why: hardware purchases follow a written veto rule, not a demo.
   - Evidence: `APN/enterprise-strategy/requirements/router-feasibility-test-plan-20261006_1410.md`
   - Applies: [Paper-first feasibility](../../references/remote-site-fleet.md#paper-first-feasibility)
4. The operator designs for 600-800 ms RTT on its GEO satellite sites (USER_STATED operator figure) against under 100 ms on LEO. The captive portal's per-page-load validation is the function most
   likely to force a local box at GEO sites.
   - Why: central placement passes or fails per link class.
   - Evidence: router feasibility test plan (Decision rule); simplified target sketch (What decides it)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)
5. The fleet stays mixed (operator rule): hardware stays until it fails, replacements follow stock; "one AP family per role" was withdrawn within the hour.
   - Why: per-vendor adapters are a standing cost in the controller's TCO.
   - Evidence: `APN/enterprise-strategy/.archcore/rules/fleet-stays-mixed.rule.md`
   - Applies: [Site shapes and the one-box rule](../../references/remote-site-fleet.md#site-shapes-and-the-one-box-rule)
6. Hundreds of site boxes each downloaded and compiled the same filter list (about 107 MB) into identical databases; a full-copy step after rsync kept about 124 MB per box per day of writes. Proposed:
   build centrally, ship the final form.
   - Why: duplicated work over satellite and flash wear on every box.
   - Evidence: `APN/smc-squid-redesign/` (plan file, lines ~101-148)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)

43. Five site-box flavours in two Ansible clusters, each cluster with its own central inventory and its own Teleport cluster: three Raspberry Pi flavours (`rct` about 300 sites, `wh` 24, `nbn_wh` 2;
    read-only root on `rct` and `wh` only) and two x86 (`rcp` 18 production sites with VoIP on the box, `nbn_accelerate` about 20). Role conditionals key off hardware class or exact flavour, never the
    cluster. A wrong flavour guess is a silent failure, and one node name can exist on both clusters as two boxes. (Added 2026-11-10.)
   - Why: the flavour decides the image, the access path and which services a site has; site and box counts differ by source (item 62).
   - Evidence: `SMC-SKILL/references/01_overview.md` (cluster comparison; section 2, USER_STATED operator 2026-10-06 and 2026-11-04);
     `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` (SMC estate table)
   - Applies: [Site shapes and the one-box rule](../../references/remote-site-fleet.md#site-shapes-and-the-one-box-rule)
44. Fixed VLAN pattern on every site: 500 management and 501 clients bridged on the box (502 too on x86); 521 to 538 standalone uplink VLANs on x86; 621 and 631 carry the `starlink`-role leg. A Pi has
    one wired port that is both the trunk to the site switch and, untagged, the internet (default route from the switch VLAN carrying the Sky Muster terminal); its 521 reaches only the modem's own
    subnet. An inventory that picks uplinks by role misses the real Pi uplink; read the interface holding the default route. (Added 2026-11-10.)
   - Why: designs, discovery and uplink models must follow the interface that carries the default route, not a label.
   - Evidence: `SMC-SKILL/references/02_service-map.md` (Live-verified network layout, x86 layout); `SMC-SKILL/references/03_communication-flows.md` (rct Site Addressing, Learned 2026-10-20,
     VERIFIED-OBSERVED)
   - Applies: [Site dependencies on the box](../../references/remote-site-fleet.md#site-dependencies-on-the-box)
45. x86 cabling convention: ports 1 and 2 go straight to a carrier terminal, ports 3 and 4 are trunks to switch 1 and switch 2, and the uplink VLANs are split between the two trunks. A switch carrying
    several carrier circuits as access VLANs fails them together; a direct port does not. Interface names and port order differ by model, so nothing may assume them. (Added 2026-11-10.)
   - Why: "several circuits failed at once" means first checking whether they share a switch trunk.
   - Evidence: `SMC-SKILL/references/02_service-map.md` (Physical port order, USER_STATED operator 2026-09-24); `SMC-SKILL/references/01_overview.md` (WAN Uplink Topology Pattern);
     `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` D12 IC2
   - Applies: [Failure domains](../../references/physical-and-campus.md#failure-domains)
46. The captive portal is required on every product and fails closed when its central back end is unreachable (no new access); content filtering is required at all community sites; RADIUS and 802.1X
    are used nowhere (portal PIN plus connection marking). (Added 2026-11-10.)
   - Why: the portal back end is a hard central dependency for new sessions at every site.
   - Evidence: `SMC-SKILL/references/01_overview.md` section 2 (USER_STATED operator 2026-10-06); `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` (notes)
   - Applies: [Placing services by link RTT](../../references/remote-site-fleet.md#placing-services-by-link-rtt)

## Management and access

7. A central collector reaches devices through each site box over Teleport, with edge execution as the fallback; constraints are a numbered register (no inbound to sites, overlapping IP space,
   constrained backhaul, central DB never reachable from a site).
   - Why: every design option is checked against the same written constraints.
   - Evidence: `APN/unified-network-controller/ARCHITECTURE.md` (lines ~78-83, 176-177); `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md`
     (lines ~73-90)
   - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
8. Only TCP crosses the Teleport port-forwards: SNMP and ping run on the site box over SSH; one poller needed a hand-built UDP relay; the controller's central ping check cannot pass and must be
   disabled.
   - Evidence: tech-stack options register (lines ~155-157, 396)
   - Applies: [Zero-trust access to remote fleets](../../references/security-and-segmentation.md#zero-trust-access-to-remote-fleets)
9. Proposed direct L3 reach: kernel WireGuard from each box plus per-site NETMAP onto a unique block; scored 90/100 against two overlay alternatives (54 and 63); a lab with two sites holding the same
   private address answered from the right site; several fleet boxes already carry the modules.
   - Why: gives central tools UDP and ICMP while Teleport stays for people.
   - Evidence: tech-stack options register (lines ~162-176); `APN/unified-network-controller/docs/reports/smc-and-site-network/direct-device-reach-options-20261015_1722.md`
   - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
10. An expired access certificate took 94 of 156 monitored devices critical with 17,309 "cert has expired" lines and nothing naming the certificate.
    - Why: a shared access dependency looked like a fleet failure.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~534-546)
    - Applies: [Zero-trust access to remote fleets](../../references/security-and-segmentation.md#zero-trust-access-to-remote-fleets)
11. Planned management path for router-only sites: WireGuard dial-out to an operator hub with a 25 s keepalive, a second independent tunnel to a second hub, on-site MAC-layer recovery; vendor cloud
    relays rejected; TCP-mode VPNs rejected for satellite.
    - Evidence: `APN/enterprise-strategy/` RouterOS study (Remote access section)
    - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
12. An unaudited autossh reverse tunnel bypasses the audited access path and is slated to retire.
    - Evidence: `APN/enterprise-strategy/architecture/current-state-architecture-20261006_1321.md`
    - Applies: [Zero-trust access to remote fleets](../../references/security-and-segmentation.md#zero-trust-access-to-remote-fleets)
13. Access discipline: every remote call has a deadline; nodes are picked at random from the live list; the backdoor path is tried before a box is called unreachable; switches and APs are read-only,
    writes only with operator approval.
    - Evidence: `APN/AGENTS.md` (skill-smc and skill-mikrotik rules)
    - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)

47. The backdoor in detail: an always-on autossh reverse tunnel from the box's sshd to a per-cluster bastion on port 50000 plus the site's unique ID, independent of the Teleport agent. It survives
    a hung agent, not a hung kernel, has no session recording, and a listening port does not prove the right box answered (a box imaged from a generic build can carry the image's ID; read the host
    name first). Operator rule: never call a box unreachable before checking it. `Disputed`: retirement is undecided (operator 2026-10-06) against "slated to retire" in item 12. (Added 2026-11-10.)
   - Evidence: `SMC-SKILL/references/03_communication-flows.md` (Backdoor SSH Access, Learned 2026-10-22); `SMC-SKILL/references/01_overview.md` section 2
   - Applies: [Zero-trust access to remote fleets](../../references/security-and-segmentation.md#zero-trust-access-to-remote-fleets)
48. The two Teleport clusters are independent roots: every command names its proxy; the subordinate-cluster flag fails with a transport error that two sessions read as a fleet outage. Devices are
    reached only through the box (port-forward or ProxyJump, nothing installed on the box), and device host keys collide across sites, so known-hosts are kept per site. (Added 2026-11-10.)
   - Why: a flag mistake looks like an outage; a shared known-hosts file looks like an attack.
   - Evidence: `SMC-SKILL/references/01_overview.md` (Remote Access, incident 2026-09-18, operator rule 2026-09-29)
   - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
49. Teleport is a monitoring dependency since D2 (decided 2026-09-21): an outage or a failed bot renewal darkens every site at once, and a still-valid 12-hour certificate hides a broken renewal for
    hours. On 2026-11-05 the bastion kept session records and audit events with no retention (root disk 94 %), and ran Teleport 13.4 while the bot and operator clients were 12.4. (Added 2026-11-10.)
   - Why: one central host and its disk are a single point of failure for all site access and monitoring; alert on renewal failure and disk, not on SSH failure.
   - Evidence: `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` D2 inherited constraints; `SMC-SKILL/references/03_communication-flows.md`
     (bastion read 2026-11-05)
   - Applies: [Zero-trust access to remote fleets](../../references/security-and-segmentation.md#zero-trust-access-to-remote-fleets)

## Telemetry over satellite

14. A fresh Teleport session to one site costs 6.9-8.0 s; each unit read 33-52 s; the largest site (306 units) hit its 900 s limit every cycle and read about 90 units.
    - Evidence: `APN/unified-network-controller/docs/reports/monitoring/collector-satellite-concurrency-20261020_2023.md`
    - Applies: [Polling over GEO and on-box readers](../../references/remote-site-fleet.md#polling-over-geo-and-on-box-readers)
15. A fleet cycle over 37 sites and 168 devices fell from 4,549 s to 752 s with six sites in parallel, one shared connection per box and one probe before any walk; a 15-minute budget now warns.
    - Evidence: `APN/unified-network-controller/docs/reports/monitoring/collector-cycle-speedup-20261009_1830.md`
    - Applies: [Polling over GEO and on-box readers](../../references/remote-site-fleet.md#polling-over-geo-and-on-box-readers)
16. Proposed on-box push collector: gzip batch per cycle, spool capped at 48 h or 200 MB, drops counted, time-sync gate (2 min skew), newest first then backlog, ack after the stored-metrics check.
    - Evidence: `APN/unified-network-controller/docs/engineering/smc-push-collector-design-20261021_1757.md` (section 5)
    - Applies: [Polling over GEO and on-box readers](../../references/remote-site-fleet.md#polling-over-geo-and-on-box-readers)
17. The controller's push API returned success while a later task stored nothing (four pushes lost all metrics; 18 of 26 devices went critical).
    - Evidence: tech-stack options register (lines ~393-420)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
18. Box hangs went unnoticed for about six months: the silent-host alert rules fired, but nobody had verified where they routed.
    - Evidence: `APN/smc-resiliency/docs/recovery/smc-hang-recovery-options-20261006_1214.md` (What actually happened); `SMC-SKILL/references/06_failure-modes.md` (lines ~218-222)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
19. No HTTP check existed on the captive portal (10 of 16 portal sites down for 7 days unseen); no per-link internet alert; ping bots covered part of the fleet.
    - Evidence: current-state architecture (2026-10-06)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
20. Passive FTP failed at some sites while `curl -I` on the FTP URL passed (control connection only); the feed moved to rsync.
    - Evidence: `APN/smc-file-writing-analysis/.archcore/rules/RULE-024-a-probe-must-exercise-the-workloads-channel.md`
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
21. The site role named "URL capture" records DNS queries (port 53), not URLs; backhaul telemetry has bytes but no application classification.
    - Evidence: `APN/docs/wifi-metrics-coverage.xlsx` (rows URL Capture, Backhaul Top Applications, Devices Connected)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)

50. More exact than item 14: a working SSH read through Teleport takes 7 to 9 s (a 6 s deadline failed healthy boxes; rule: 10 s an attempt, two attempts, deadlines on `tsh status` and `tsh ls`), and
    a
    per-unit read costs about 7.4 s at a Sky Muster site against 3.2 s at a terrestrial one, so stages batch per site and reuse one connection. Link profiles: [site-backhaul.md](site-backhaul.md).
    (Added 2026-11-10.)
   - Evidence: `SMC-SKILL/references/01_overview.md` (Learned 2026-10-16 and 2026-10-29, VERIFIED_PRIMARY in source)
   - Applies: [Polling over GEO and on-box readers](../../references/remote-site-fleet.md#polling-over-geo-and-on-box-readers)

## Discovery and identity

22. Measured source accuracy against install records: AP bridge table 38/38 and 43/43; switch FDB beyond the AP port 0/50 and 0/67; install-record SSID 358/359; router-to-radio from live sources 39/52
    and 10/76, 53/53 with the install record.
    - Evidence: `APN/unified-network-controller/docs/architecture/topology/correlation-rules-explained-20261009_1743.md` (section 8.1)
    - Applies: [Discovery evidence ranking](../../references/remote-site-fleet.md#discovery-evidence-ranking)
23. Provisioning-hook logs on the box named the radio each router was installed behind (63 of 66); option 82 Remote ID ties a CPE to its radio; the logs are backed up before any box is replaced.
    - Evidence: `APN/unified-network-controller/ARCHITECTURE.md` (lines ~92-94)
    - Applies: [Discovery evidence ranking](../../references/remote-site-fleet.md#discovery-evidence-ranking)
24. 752 management IPs recur across sites; one IPAM namespace per site; a two-site isolation test passed 12/12.
    - Evidence: tech-stack options register (line ~159); `APN/unified-network-controller/docs/reports/nautobot/d36-namespace-isolation-test-20260921_1329.md`
    - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
25. Only one site in the estate is known to ring; a loop drawn anywhere else is a placement error.
    - Evidence: `APN/unified-network-controller/docs/engineering/agent-rules-devices-and-sites-20261010_1750.md`
    - Applies: [Discovery evidence ranking](../../references/remote-site-fleet.md#discovery-evidence-ranking)
26. Site intent comes from Ansible topology variables imported into Nautobot; drift is shown in three tiers and never written back.
    - Evidence: `APN/unified-network-controller/ARCHITECTURE.md` (lines ~194-204)
    - Applies: [Discovery evidence ranking](../../references/remote-site-fleet.md#discovery-evidence-ranking)

## Site services, WAN and power

27. Site switches and APs take DHCP and DNS from the site box on the management VLAN; a remote power-cycler can cycle the switch.
    - Evidence: `APN/AGENTS.md` (skill-mikrotik rule)
    - Applies: [Site dependencies on the box](../../references/remote-site-fleet.md#site-dependencies-on-the-box)
28. `fib_multipath_hash_policy` was 0 on every multi-WAN box; DNS to fixed resolvers and health pings pinned to one uplink; ECMP membership had no health eviction. Accidental ECMP across links is a
    listed current-state defect.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~457-504)
    - Applies: [ECMP hashing pitfalls](../../references/routing-and-switching.md#ecmp-hashing-pitfalls)
29. A central service enforced a source-IP ACL; a site whose public address moved outside the usual NAT pool broke silently.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~505-533)
    - Applies: [Multi-WAN, VRRP and power](../../references/remote-site-fleet.md#multi-wan-vrrp-and-power)
30. The box's single port feeds a switch carrying the satellite terminal, AP management, client and modem VLANs; the whole trunk went silent while the box kept transmitting.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~377-405)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
31. Four solar hub sites went dark from about 03:30 to 09:00 with 17 to 44 boots per site in 90 days, dozens June to November, 0 to 5 December to February, two winters running; no RTC.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~349-364)
    - Applies: [Multi-WAN, VRRP and power](../../references/remote-site-fleet.md#multi-wan-vrrp-and-power)
32. A Pi-class box logged undervoltage 1,859 to 7,352 times a day while the volt-alarm metric read 0; the 48 V switch stayed up 68 days while the box rebooted.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~366-376)
    - Applies: [Multi-WAN, VRRP and power](../../references/remote-site-fleet.md#multi-wan-vrrp-and-power)
33. A cron restarting the DHCP client on a failed ping made a degraded link worse; a revert that batch-stopped six DHCP interfaces dropped the session.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~406-456); `APN/smc-file-writing-analysis/.archcore/rules/RULE-015-never-batch-stop-all-dhcp-interfaces.md`
    - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
34. Decision (2026-10-29): a three-box site (one box per tower, 60 GHz ring) runs keepalived VRRP without conntrack sync, each box its own DHCP range, modelled with Nautobot redundancy groups, polled
    through the management master, split brain alarmed first; a single public-address ping track (weight -30) fails about hourly.
    - Evidence: `APN/unified-network-controller/docs/architecture/site-model/multi-smc-sites-design-20261029_1027.md`
    - Applies: [Multi-WAN, VRRP and power](../../references/remote-site-fleet.md#multi-wan-vrrp-and-power)
35. A short-outage census filed sub-six-hour outages as connectivity; at solar sites most were power. A health-check restart storm (686 restarts per hour) was noise, not cause.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines ~349-365); `APN/smc-resiliency/docs/recovery/smc-hang-recovery-options-20261006_1214.md` (option F)
    - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)

51. Multi-WAN routing as built (read live on two boxes 2026-11-06): each `internet` leg has its own routing table and a `from` rule (a dhclient hook); the main table has one multipath default written
    by
    the portal's gateway-status job; the `starlink`-role leg gets a plain metric-100 default and no table; stale `from` rules pile up. The labels are inverted: Starlink became primary under the
    `internet` label, and `starlink` now marks the single Sky Muster backup. UNC models every uplink as role Internet plus a Circuit whose provider comes from the far side (decided 2026-09-27 and
    2026-10-08, lab only). (Added 2026-11-10.)
   - Why: one ping from the box measures one leg; a label never says which carrier a leg uses.
   - Evidence: `SMC-SKILL/references/03_communication-flows.md` (WAN Uplink Addressing, Learned 2026-11-06); `APN/unified-network-controller/ARCHITECTURE.md` (WAN uplinks)
   - Applies: [ECMP hashing pitfalls](../../references/routing-and-switching.md#ecmp-hashing-pitfalls)
52. Ingress shaping on Starlink legs is a hand-installed per-site TBF and ifb script outside Ansible (rates differ per site; Sky Muster backup and carrier-managed legs unshaped); the QoS role is gated
    to the Pi flavour only. A fleet QoS and fair-use design is open (D19, raised 2026-10-26). (Added 2026-11-10.)
   - Why: a rebuild loses the shaping silently; fair use over satellite has no design yet.
   - Evidence: `SMC-SKILL/references/03_communication-flows.md` (Manual TBF/ifb Ingress Shaping);
     `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` D19
   - Applies: [Redundancy and CGNAT](../../references/wan-and-remote-access.md#redundancy-and-cgnat)
53. Two DNS paths on one box: client DNS goes to unbound, then stubby, whose single upstream is DNS over TLS through an autossh local forward to the Teleport bastion (no failover; bind9 with RPZ on
    the low-touch group instead); the box's own lookups go straight to public resolvers. The tunnel is unmonitored and its retirement undecided. (Added 2026-11-10.)
   - Why: the bastion is also the client DNS upstream for most sites; the effect of losing it on clients is UNVERIFIED (inferred from the single upstream).
   - Evidence: `SMC-SKILL/references/02_service-map.md` (Core Networking); `APN/enterprise-strategy/architecture/current-state-architecture-20261006_1321.md`
   - Applies: [Dependency order](../../references/network-services.md#dependency-order)
54. Reach checks in use: UNC's uplink check every 15 minutes sends pings and a DNS query out of each leg and raises `uplink_down`; a per-leg round-trip probe binds to each leg's address. For a dark
    VLAN, an RX counter of exactly zero rules out firewall and routing, and a sibling VLAN on the same parent passing traffic clears the cable and NIC. (Added 2026-11-10.)
   - Evidence: `SMC-SKILL/references/03_communication-flows.md` (WAN-Path Diagnostic Techniques, Recurrence 2026-10-13, Learned 2026-11-06)
   - Applies: [Probes, alert routing and outages that are not connectivity](../../references/observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity)
55. Proposed, not decided: the reach ladder for the new images. The box checks path (uplink, gateway, public anchor), then the controller's endpoint (TCP and TLS), then its service (authenticated
    heartbeat); only a failure local to the box starts a timer toward a self-undoing trial; a central fault (controller, Teleport, public DNS) never starts a fleet-wide action, and an outage never
    reverts a version. Principle USER_STATED by the operator 2026-11-05. (Added 2026-11-10.)
   - Why: a whole fleet acting on a central outage at the same hour is a larger incident than the outage.
   - Evidence: `APN/smc-resiliency/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` section 9.4
   - Applies: [Site dependencies on the box](../../references/remote-site-fleet.md#site-dependencies-on-the-box)

## Controller exit and onboarding

36. Factory-default units reach the vendor controller through site DHCP option 43, and on some sites a DHCP-lease hook registers them; replacing the controller changes both. Required test: a
    factory-default device finds the controller with no site visit.
    - Evidence: `APN/enterprise-strategy/architecture/current-state-architecture-20261006_1321.md` (flows); router feasibility plan (D01, E07)
    - Applies: [Onboarding and controller exit](../../references/remote-site-fleet.md#onboarding-and-controller-exit)
37. The controller is being rebuilt on Nautobot and OpenWISP after a vendor's reported administration; vendor consoles (several instances, one without an API) stay beneath it where useful. The
    vendor-status claim is UNVERIFIED here.
    - Evidence: `APN/enterprise-strategy/slides/unc-business-case-slide-20261010_1600.md`; `APN/cambium-swap/docs/migration/requirements.md`
    - Applies: [Onboarding and controller exit](../../references/remote-site-fleet.md#onboarding-and-controller-exit)
38. Every device family in the fleet is rollback class R0 today (no proven write mechanism); one partial REST restore ran on a test unit.
    - Evidence: `APN/unified-network-controller/docs/architecture/provisioning/config-restore-and-rollback-classes-20260926_2320.md`
    - Applies: [Onboarding and controller exit](../../references/remote-site-fleet.md#onboarding-and-controller-exit)
39. Field cost is a named driver: rising field prices, unreported weekend truck rolls, low-touch installs over two days on site; remote-resolution target 90% (a target, not firm).
    - Evidence: `APN/enterprise-strategy/docs/program-brief-20261006_1055.md` (sections 2 and 8)
    - Applies: [Onboarding and controller exit](../../references/remote-site-fleet.md#onboarding-and-controller-exit)

56. Update to item 37: the operator recorded on 2026-11-05 and 2026-11-06 that the vendor console continues after the product-line sale; the 13 Nov exit target is withdrawn and site-box resiliency
    has priority over controller work. The vendor's ePMP, Enterprise Wi-Fi and console lines went to one buyer (production resuming is a vendor claim, UNVERIFIED), PMP, PTP and 60 GHz to another.
    (Added 2026-11-10.)
   - Evidence: `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` section 1 (Currency note 2026-11-06);
     `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` section A
   - Applies: [Onboarding and controller exit](../../references/remote-site-fleet.md#onboarding-and-controller-exit)
57. Proposed site-box to controller contract (draft v0.2, contract 0.3.0 on 2026-11-09): fourteen interfaces, most proved on the box side in the lab against a stand-in, events, Teleport identity and
    per-layer versions proposed; the box only pulls over outbound HTTPS; every request is a compact JWS (EdDSA) bound to its endpoint with a one-time nonce; the release store must serve HTTP/2 with
    range requests; time comes from the controller or the site gateway by address. Nothing is agreed until the controller answers and the operator records it in D12. (Added 2026-11-10.)
   - Why: the transport (Teleport or an overlay) is not trusted; the message is.
   - Evidence: `APN/smc-resiliency/docs/interfaces/unc/interfaces.yaml`, `readme.md` there
   - Applies: [Management behind carrier NAT](../../references/remote-site-fleet.md#management-behind-carrier-nat)
58. Proposed (operator 2026-10-22): a site fingerprint to notice a box carried to another site: switch identity over LLDP or MNDP, AP and ATA MACs from leases, the uplink gateway MAC, public address
    and ASN, and on Starlink the dish position. The controller judges; the box changes nothing on a mismatch. A Sky Muster terminal offers nothing readable. (Added 2026-11-10.)
   - Evidence: `APN/smc-resiliency/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` section 10
   - Applies: [Discovery evidence ranking](../../references/remote-site-fleet.md#discovery-evidence-ranking)

## Site devices

59. On the Pi flavour the site switch is a MikroTik RB450Gx4 (294 of 297 reached, RouterOS 7.8): ether1 the box trunk, ether2 the satellite terminal, ether3 a second WAN, ether4 the phone UI, ether5
    the
    one AP (a MikroTik Metal 52 ac). It sits in both the user and WAN paths on a solar bus of about 24 V; every surveyed switch carries identical port MACs (cloned config); the box's app
    power-cycles it after about 11 minutes of failed pings. (Added 2026-11-10.)
   - Why: never key inventory on these MACs; capture the switch log before a power-cycle; check switch uptime against box uptime before blaming the satellite.
   - Evidence: `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` A07, B02 (VERIFIED-OBSERVED 2026-10-07);
     `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-mikrotik/SKILL.md`
   - Applies: [Failure domains](../../references/physical-and-campus.md#failure-domains)
60. x86 sites run two TP-Link SG2428P switches (both online at some sites, one on standby at others) with a guessable read-write SNMP v2c community; the controller onboards them through the same sweep
    as radios and parses their configs with netutils' `linux` parser (decided 2026-09-30). (Added 2026-11-10.)
   - Evidence: `APN/enterprise-strategy/requirements/component-inventory-20261006_1321.md` B01; `SMC-SKILL/references/16_tplink-site-switches.md`; `APN/unified-network-controller/ARCHITECTURE.md`
     (Site switches)
   - Applies: [Port and wireless access control](../../references/security-and-segmentation.md#port-and-wireless-access-control)
61. RouterOS as the site box is a parked, unscheduled study, not adopted and no dependency of the controller or site-box projects (operator 2026-10-22). Candidates: the installed RB450Gx4 for Pi sites
    (containers need RouterOS 7.4 or later; the fleet runs 7.8), RB5009 for the small x86 class, CCR2004-16G-2S+PC for the large; container support is not parity, and Netinstall needs Layer 2
    adjacency, so a broken remote router cannot reinstall itself. (Added 2026-11-10.)
   - Evidence: `APN/enterprise-strategy/workstreams/redefine-baseline/routeros-smc-replacement-future-study-20261022_1323.md` (Executive summary, Candidate models)
   - Applies: [Paper-first feasibility](../../references/remote-site-fleet.md#paper-first-feasibility)
62. `Disputed` (counts): x86 site boxes are 47 by model (28 small, 19 large, read 2026-10-22), 18 `rcp` production sites plus about 20 `nbn_accelerate` sites by the operator and skill-smc, 34 x86
    Devices in Nautobot, and 36 sites in the controller register, whose environment table also describes the site box as x86 Ubuntu or Debian (corrected to Ubuntu 22.04 in its D12 IC1) and omits the
    Pi fleet. Units and dates differ; re-count from the inventory before using a figure. (Added 2026-11-10.)
   - Evidence: `APN/enterprise-strategy/workstreams/redefine-baseline/routeros-smc-replacement-future-study-20261022_1323.md` (Candidate models); `SMC-SKILL/references/01_overview.md` section 2;
     `APN/unified-network-controller/ARCHITECTURE.md` (Components); `APN/unified-network-controller/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` section 1
   - Applies: [Site shapes and the one-box rule](../../references/remote-site-fleet.md#site-shapes-and-the-one-box-rule)

## Datacenter switching and resolvers

40. The switching refresh baseline is a routed spine-leaf with EVPN/VXLAN; MPLS must be justified with evidence; written re-open triggers and four thresholds for segment routing; standard switch MTU
    2000.
    - Evidence: `APN/switching-refresh/02_decision-rationale-vxlan-over-mpls-20260330_2225.md`; `APN/switching-refresh/08_segment-routing-reconsideration-triggers-20260331_0848.md`;
      `APN/switching-refresh/01_design-principles-20260330_2225.md`
    - Applies: [Transport baseline and re-open triggers](../../references/routing-and-switching.md#transport-baseline-and-re-open-triggers)
41. A customer resolver VM looked CPU-bound: kernel default receive buffers (212992), about 67k UDP receive-buffer errors, one combined virtio queue, almost all NIC interrupts on one of 8 vCPUs.
    Tuning order: buffers, multiqueue, IRQ spread, then CPU, with a gate including even load-balancer distribution.
    - Evidence: `APN/docs/customer-resolvers/` (UDP receive review and tuning plan, 2026-04-02; file names carry hostnames)
    - Applies: [Resolver receive path](../../references/network-services.md#resolver-receive-path)
42. Multiqueue for that VM was planned as a libvirt definition change (queues 4, one socket of 8 cores) with a full shutdown and start, a saved definition for rollback.
    - Evidence: `APN/docs/customer-resolvers/` (NIC multiqueue tuning plan, 2026-04-02)
    - Applies: [Resolver receive path](../../references/network-services.md#resolver-receive-path)

## Withheld evidence paths

- Tender, government-site and community-fibre lessons (site VLAN template, data residency, incumbent takeover, permits, site tiers, temporary sites, demarcation, 60 GHz alignment, central breakout)
  come from project folders named after a customer or a community. Their paths are not written here; find them through `APN/README.md`.
  Their generic lessons are in [remote-site-fleet](../../references/remote-site-fleet.md).
