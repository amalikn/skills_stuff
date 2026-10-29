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
