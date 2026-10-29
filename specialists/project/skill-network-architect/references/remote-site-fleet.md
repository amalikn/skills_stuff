---
Title: Remote-site fleet architecture
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Architecture of a fleet of remote sites behind geostationary satellite and terrestrial links with one site box in the user's path: site shapes, the one-box rule,
  paper-first feasibility, service placement by link RTT, management behind carrier NAT, polling and on-box readers, discovery evidence, site dependencies,
  multi-WAN hashing, power-driven outages, VRRP sites and onboarding.
---

# Remote-site fleet architecture

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Site shapes and the one-box rule](#site-shapes-and-the-one-box-rule)
- [Paper-first feasibility](#paper-first-feasibility)
- [Placing services by link RTT](#placing-services-by-link-rtt)
- [Management behind carrier NAT](#management-behind-carrier-nat)
- [Polling over GEO and on-box readers](#polling-over-geo-and-on-box-readers)
- [Discovery evidence ranking](#discovery-evidence-ranking)
- [Site dependencies on the box](#site-dependencies-on-the-box)
- [Multi-WAN, VRRP and power](#multi-wan-vrrp-and-power)
- [Onboarding and controller exit](#onboarding-and-controller-exit)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: site shape, what runs on the site box and what runs centrally, the management and recovery paths, how telemetry leaves the site, how topology is discovered, and what the site needs from the
  box during rollback.
- The fleet: many small sites (tens to hundreds of devices each) on geostationary (GEO) satellite, LEO satellite, fixed wireless or fibre, often behind carrier-grade NAT, with one gateway box ("site
  box") between users and the WAN, and site visits that are slow and costly.
- Hands to [wan-and-remote-access](wan-and-remote-access.md) (tunnels, MTU, CGNAT keepalives, BDP) and [network-services](network-services.md) (DHCP, DNS, option 43).
- Hands to [security-and-segmentation](security-and-segmentation.md#zero-trust-access-to-remote-fleets) (access proxy limits) and
  [routing-and-switching](routing-and-switching.md#ecmp-hashing-pitfalls) (ECMP).
- Hands to [observability-troubleshooting](observability-troubleshooting.md#probes-alert-routing-and-outages-that-are-not-connectivity) (probes, alerts, outage classes).
- Hands to skill-systems-architect (box OS, A/B images, watchdog, storage wear), skill-smc, skill-mikrotik and skill-cambium (device facts), skill-nautobot (IPAM namespaces, redundancy objects).

## Decision rules

| Rule | Value or threshold | Evidence |
| --- | --- | --- |
| GEO adds physics latency no design removes | At least ~477 ms RTT before processing; design for 600-800 ms | Derived (4 x 35,786 km / c) |
| Components in series multiply availability | A = A1 x A2 x ...; a second box in the user path lowers A | Derived (series formula); `just availability` |
| One box in the user's path | Any extra box carries extras only and fails open | UNVERIFIED (design rule from field experience) |
| Central placement must pass over the slowest | Test at the worst RTT the product sells, not the average | UNVERIFIED (design rule) |
| link class |  |  |
| Behind CGNAT the site initiates every session | Agents and tunnels dial out; nothing inbound | VERIFIED_PRIMARY [RFC 6888][rfc6888], [Teleport][tp-agents] |
|  |  | (reverse tunnels) |
| NAT UDP mapping timer | MUST NOT expire under 2 min; 5 min or more RECOMMENDED; carriers vary, measure | VERIFIED_PRIMARY [RFC 4787][rfc4787] REQ-5 |
| WireGuard keepalive behind NAT | 25 s works with a wide variety of firewalls; off by default | VERIFIED_PRIMARY [WireGuard quickstart][wg-qs] |
| Access proxies carry TCP | UDP and ICMP probes run on the site box | VERIFIED_PRIMARY [Teleport][tp-tcp], [ssh(1)][ssh1] |
| IP is not identity when site plans repeat | Key on (site, IP) or a device ID; one IPAM namespace per site | UNVERIFIED (design method) |
| Store-and-forward on the box | Atomic batch files (write, fsync file and directory, rename) | VERIFIED_PRIMARY [rename(2)][rename2], [fsync(2)][fsync2] |
| Edge agents can buffer to disk while the link | Bounded by a disk cap, then oldest dropped | VERIFIED_PRIMARY [vmagent][vmagent] (one product; check the |
| is down |  | chosen agent) |
| Relay information as topology evidence | Option 82 Circuit ID (1) and Remote ID (2) tie a client to its access point | VERIFIED_PRIMARY [RFC 3046][rfc3046] |
|  | of attachment |  |
| Option 43 is opaque and vendor-defined | Often carries the controller address; a controller exit must re-point it | VERIFIED_PRIMARY [RFC 2132][rfc2132] s8.4 |
| Linux multipath defaults | Layer 3 hash; failed next hops stay in the group | VERIFIED_PRIMARY [ip-sysctl][k-ipsysctl] |
| VRRP moves the gateway address only | Sessions and NAT state stay behind unless synchronised | VERIFIED_PRIMARY [RFC 5798][rfc5798]; sync remark derived |

## Site shapes and the one-box rule

Redundancy at a small remote site is usually uneconomic, so the real choice is which single point of failure to keep and how fast it recovers.

```text
SITE SHAPES: one box in the user's path; anything else fails open
Shape A, router only (portal, filter, controller central)
+-------+   +-------------+   +----------------+   +------------+   +--------------------+
| users |-->| APs, switch |-->| site router    |-->| WAN (GEO,  |-->| central services   |
+-------+   +-------------+   | (native funcs) |   | LEO, fibre)|   | portal, controller |
                              +----------------+   +------------+   +--------------------+
Shape C, one site box (portal, DNS, DHCP, shaping on the box; A/B images, watchdog)
+-------+   +-------------+   +----------------+   +------------+
| users |-->| APs, switch |-->| site box       |-->| WAN        |
+-------+   +-------------+   +----------------+   +------------+
Rejected: router + second box that also carries user traffic (two series failure points)
+-------+   +-------------+   +--------+   +-------------+   +-----+
| users |-->| APs, switch |-->| router |-->| portal box  |-->| WAN |   user outcome needs both
+-------+   +-------------+   +--------+   +-------------+   +-----+
```

- Shape A fits when every required function is native on the router or passes the central test over the slowest link.
- Shape C fits when a required function must stay local (for example a portal that validates every page load at GEO latency).
- Neither removes the single point of failure. Invest in recovery time instead: a hardware watchdog, out-of-band power cycling, A/B images with automatic rollback, and a second management path
  (UNVERIFIED, judgement; the series formula shows why a second in-path box does not help).
- An auxiliary box (cache, logger, analytics) is allowed when it is out of the forwarding path or fails open: users keep internet when it dies. Prove fail-open with a pull test.
- Simplify by putting each component through four questions: can one central copy serve all sites; is there an owned requirement; is a person doing it by hand; does its failure need a site visit. The
  components no owner can justify become questions for the business, not design work.
- Mixed fleets are a constraint, not a defect. Specify devices by function, absorb the mix in templates and adapters, and price each vendor adapter.

## Paper-first feasibility

Eliminate candidate devices on paper before buying hardware. Steps 1-4 cost nothing.

| Step | Action | Output |
| --- | --- | --- |
| 1 | The owner marks each function required or not | Required-function list |
| 2 | Each required function becomes a behavioural pass/fail test with owner thresholds | Test list |
| 3 | Per named model and exact firmware: native, add-on package, central, or impossible; cite vendor documentation for that firmware | Feasibility matrix |
| 4 | Apply the rule: one required function that is neither local nor movable central fails the candidate; add-ons are recorded as dependencies | Shortlist |
| 5 | Bench the shortlist against the step 2 tests | Bench results |
| 6 | Pilot one site with the old box kept on the shelf as rollback | Pilot report |

- "Central" counts only if the function passes its test over the slowest link class the product sells (next section).
- Firmware matters: a function native in one release may be an add-on or absent in another. Record the release next to every cell.

## Placing services by link RTT

```text
SERVICE PLACEMENT BY WORST LINK RTT (illustrative classes; measure your own)
+------------------+---------------------+----------------------------------------------------+
| link class       | RTT to design for   | chatty central auth, portal, config push           |
+------------------+---------------------+----------------------------------------------------+
| fibre, terrest.  | tens of ms          | central is usually fine                            |
| LEO satellite    | tens of ms, varies  | central usually fine; test in busy hour            |
| GEO satellite    | 600-800 ms          | local unless the function tolerates many RTTs      |
+------------------+---------------------+----------------------------------------------------+
```

- Count round trips per user action. A portal that validates every page load, a login with several redirects, or a config run with hundreds of request/response steps multiplies the RTT. Ten round
  trips at 700 ms is 7 s of waiting before any data moves.
- Record the placement answer per product and per link class. A site moving from GEO to LEO can change it.
- Shared artefacts (block lists, filter databases, images): build once centrally and ship the final form as a delta; look for the local copy step that undoes the transport saving. HTTP proxy filtering
  does not see inside HTTPS; filter by DNS policy where HTTPS dominates (UNVERIFIED, judgement).
- Voice and fairness: shape at the site edge before NAT or the tunnel, with per-host fairness and an explicit voice class, and set the shaper below the variable satellite capacity. Test on every WAN
  the site uses (UNVERIFIED; candidate shapers are CAKE or HTB with an ingress device).

## Management behind carrier NAT

```text
MANAGEMENT AND RECOVERY FOR A CGNAT SITE: two independent dial-out paths
                         +------------------+
            +----------->| access proxy     |<----- people and tools (TCP, audited)
            | reverse    | (hub 1)          |
            | tunnel     +------------------+
+-----------+--+
| site box     |  UDP/ICMP probes, SNMP, ping run here and return output over the TCP session
| agent + VPN  |
+-----------+--+
            | tunnel     +------------------+
            +----------->| recovery hub 2   |<----- operators when hub 1 or its certificates fail
              (keepalive)| (independent)    |
                         +------------------+
out-of-band: remote power cycling for the box and the switch, not via either hub
```

- The site dials out; a keepalive below the carrier's mapping timeout keeps the path open ([RFC 4787][rfc4787], [WireGuard quickstart][wg-qs]).
- The recovery channel must not depend on the access proxy, its certificate authority or its agent. A shared certificate that expires fails every site at once and looks like a fleet outage ([Teleport
  authentication][tp-auth]: certificates auto-expire by design).
- An access proxy carries TCP. Plan SNMP, NTP checks and ping as commands on the site box, or add an address-translating L3 overlay (1:1 static mapping of each site range onto a unique block with
  NETMAP, [iptables-extensions][ipt-ext]) and record the mapping in IPAM.
- Management addresses repeat across cookie-cutter sites. Every record, metric, job and alert key carries the site, or uses a device ID.
- Avoid vendor-cloud relays when "manageable without the vendor cloud" is a requirement. Avoid TCP-encapsulated VPNs on lossy high-RTT links (TCP inside TCP retransmits twice; UNVERIFIED, inference).
  A tunnel key identifies a device, not a person; attribute people through the proxy or device AAA.
- Tooling discipline: a deadline on every remote call; confirm through the second path before declaring a site unreachable; change interfaces one at a time with the management interface last,
  identified from the live session rather than the default route.
- Self-heal actions (restart a DHCP client on a failed ping) need backoff, a cap and an event record; on a degraded but live link they cause the flap they try to fix.

Lab questions before a satellite-site management design: carrier NAT mapping lifetime and reconnect time after an outage per link type; tunnel MTU and MSS per encapsulation; API timeouts at the worst
RTT; whether audit through the device's AAA matches the proxy's audit; whether security settings survive a reimage.

## Polling over GEO and on-box readers

Request/response polling across GEO does not scale with concurrency, because the fixed cost per session and per request is round trips, not bandwidth.

Measured in one estate over GEO (no site identifiers):

| Quantity | Value |
| --- | --- |
| New access-proxy session to one site | 6.9-8.0 s |
| One device read (several HTTPS round trips) | 33-52 s |
| Largest site, about 300 devices, against a 900 s per-site budget | about 90 devices read per cycle |
| Same site with 12 reads in flight (projected) | about 1,350 s, still over budget |
| Fleet cycle, serial sites, about 71 s fixed cost per site, 31.6 s per silent device | 4,549 s |
| Six sites in parallel, one shared connection per box, one probe before any walk | 752 s |

- Reuse one connection per site, run bounded parallelism across sites, and make a silent device cost one probe. Set a cycle budget and alarm on it.
- Where polling still misses the budget, move the reader to the box and ship batches. Decide on purpose whether a gap during WAN loss is acceptable; if not, something on the box must buffer.

On-box reader with a crash-safe spool:

```text
ON-BOX READER: store and forward, at-least-once, idempotent replay
+---------+   +----------------------+   +-------------------+   +--------------+   +----------+
| devices |-->| reader on site box   |-->| spool (capped)    |-->| uplink drain |-->| ingest   |
+---------+   | skip if clock unsync |   | tmp, fsync, rename|   | newest first,|   | ack only |
              +----------------------+   | sequence numbers  |   | then backlog |   | after    |
                                         | drops counted     |   | oldest first |   | stored   |
                                         +-------------------+   +--------------+   +----------+
```

- Write each batch to a temporary file, fsync the file and its directory, then rename: readers never see a partial batch ([rename(2)][rename2], [fsync(2)][fsync2]).
- Cap the spool by age and size; drop oldest first and count every drop, so loss is bounded and visible.
- Gate on time: take no readings while the clock is unsynchronised; ingest refuses batches too skewed or dated in the future.
- Drain the newest batch first (current state), then the backlog oldest first.
- Acknowledge only after the stored data is verified; replay is idempotent on (device, time). An accepted push is not stored data.
- A RAM-backed root (overlay on RAM) loses the spool on reboot; place it on persistent storage and budget the write wear (skill-systems-architect).

## Discovery evidence ranking

Rank topology sources by measured accuracy against ground truth (install records), not by protocol prestige.

Measured in one estate against install records (wireless point-to-multipoint access behind site boxes):

| Source | Agreement with install records | Use |
| --- | --- | --- |
| Access point bridge table (client behind which AP) | 38/38 and 43/43 at two sites | High for placement |
| Switch MAC table beyond the AP port | 0/50 and 0/67 | Do not use for placement |
| Wi-Fi clients behind a router, two or more clients | 6/6 | Medium |
| Wi-Fi clients behind a router, one client | 9/20 (phones roam) | Low |
| Provisioning-time record (SSID at install) | 358/359 | High |
| Router-to-radio from live sources only | 39/52 and 10/76 | Low to medium |
| Router-to-radio with the install record | 53/53 | High |

- A switch learns every client behind a wireless bridge on the bridge port, so its MAC table says "somewhere behind this port", not "which radio".
- Install-time records (provisioning hook logs, DHCP relay information, [RFC 3046][rfc3046] Remote ID) are often the best access-topology truth. Archive them as primary sources before hardware turns
  over.
- Identity needs an exact MAC, or a near MAC with an agreeing address. One heuristic alone is low confidence; a MAC shared by two devices gives no answer.
- Separate device I/O from inference: normalise every source into one observation shape (source, kind, a, b, confidence, detail), keep conflicts for a person to decide, carry first-seen and last-seen
  across runs, and never drop a link only because it was not seen this run.
- Feed known invariants into inference as checks: a loop drawn in a tree-shaped access network is a placement error unless the site is known to ring.
- Check that a discovery tool models overlapping VRFs and radio links before adopting it. One sample site is not a fleet rate.

## Site dependencies on the box

```text
WHAT THE SITE TAKES FROM THE BOX: every arrow must survive the box's rollback or safe image
+----------------------+   DHCP, DNS (management VLAN)   +---------------------+
| switch, APs, radios  |<--------------------------------| site box            |
| (site devices)       |<-- controller discovery --------| (normal, safe and   |
|                      |    (option 43 or DNS name)      |  rollback images)   |
|                      |<-- NTP, gateway ----------------|                     |
+----------------------+                                 +---------------------+
```

- List every service site devices consume from the box: DHCP, DNS, controller discovery (DHCP option 43 or a DNS name), NTP, default gateway.
- Keep that list in the box's safe and rollback images, or a rollback takes the site's management plane down with it. Test controller discovery in rollback drills.
- Out-of-band power control per site (box and switch). Outage triage separates switch or cable faults from box faults.
- At sites where the customer runs part of the LAN, write the demarcation: who owns which device and what may connect where. Public Wi-Fi stays off the customer's corporate network.

## Multi-WAN, VRRP and power

Multi-WAN boxes:
- With the Linux default Layer 3 hash and no neighbour check, fixed destinations (resolvers, health targets) pin to one uplink even when it is dead upstream ([ip-sysctl][k-ipsysctl]; detail in [ECMP
  hashing pitfalls](routing-and-switching.md#ecmp-hashing-pitfalls)). Signature: names fail intermittently, a raw IP works.
- Health checks per uplink with source routing; evict dead next hops; record each box's intended mode (active/backup, weighted, managed ECMP).
- Do not authorise a site by its source address at central services: a NAT pool or carrier change moves it silently.
- WAN handoff stays generic (Ethernet with DHCP); moving from per-tower breakout to one central feed is an architecture change, not a circuit swap.

VRRP sites (several boxes, one per tower, sharing a gateway):
- VRRP elects a master and moves the virtual address ([RFC 5798][rfc5798]). Without connection-state sync, failover drops sessions; that can be acceptable for best-effort Wi-Fi.
- Give each box its own DHCP range so leases never conflict.
- Track several targets or the default route, never one public address: a single ping target failing about hourly flaps the master.
- Poll and manage through the current master, alarm on split brain first, and model the group with the inventory's native redundancy objects.

Power:
- At solar sites, outages cluster before dawn in winter: boots at nearly the same clock time on many days, dozens a season in winter and almost none in summer. Size battery autonomy for the winter
  worst case, give the box a real-time clock or early time sync, and classify dark periods by boot-time pattern.
- An instantaneous undervoltage gauge can read 0 while the kernel logs thousands of events a day; use latched flags and logs. Feed small boxes from a correctly sized regulated supply.

## Onboarding and controller exit

- Zero-touch onboarding (DHCP option 43, a DHCP lease hook, a cloud redirect) is a hidden dependency on the controller. Inventory it and re-point it before a controller cut-over.
- Acceptance test: a factory-default device finds the new controller with no site visit.
- Keep a written answer to "what still works if the controller vendor disappears" (configuration, monitoring, provisioning, licences, firmware) and a costed exit path.
- Replacement requirements from a vendor failure: no mandatory vendor cloud for steady state, restore or onboarding; no licence fuse; a local API; firmware verifiable offline.
- Declare each platform's rollback class before automating writes to it: native timed revert, verified whole restore, compensating write, or none (safe stop and a visit). Many embedded radios and CPE
  have no commit-confirm ([automation and safety](automation-and-safety.md)).
- Field cost drives design: each visit to a remote community can need permits and inspection lead time, so self-recovery and remote rebuild are worth more there. Measure the remote-resolution rate
  from incident records.

## Patterns and anti-patterns

| Pattern | Use when | Anti-pattern | Why it fails |
| --- | --- | --- | --- |
| One box in the user path; extras fail open | Small remote sites | Router plus an in-path portal box | Two series failure points for one outcome |
| Recovery time over redundancy | Redundancy uneconomic at the edge | Second box "for availability" | Adds failure points; recovery still needs a visit |
| Central only if it passes over GEO | Mixed link classes | Placement tested on fibre | Chatty functions fail at 600-800 ms |
| On-box reader with a capped spool | Polling misses the cycle budget | More concurrency over GEO | Round trips, not bandwidth, dominate |
| Two independent dial-out paths | CGNAT sites | Recovery through the same proxy | One certificate or proxy fault strands the fleet |
| (site, IP) or device ID keys | Repeated site address plans | IP-keyed tools | Data from one site lands on another |
| Sources ranked by measured accuracy | Topology discovery | Switch MAC tables behind wireless bridges | Every client appears on the bridge port |
| Rollback image keeps site services | Site devices lease from the box | Generic rollback image | Rollback takes the management plane down |
| Per-uplink health checks | Multi-WAN boxes | Health ping through ECMP | Tests only the hashed uplink |

## Failure modes and tests

| Failure | Signal | Test that proves detection and recovery |
| --- | --- | --- |
| In-path auxiliary box dies | Users lose internet | Pull the auxiliary box; users keep internet (fail-open) |
| Central function too chatty for GEO | Portal or login times out at satellite sites | Run the function's test at 800 ms RTT in a lab |
| Access certificate or proxy fails | Most sites critical at once | Expire a test certificate; one shared alarm fires; recovery hub still reaches a site |
| CGNAT mapping expires | Tunnel stalls after idle | Idle past the measured mapping timeout; keepalive holds it |
| Poll cycle overruns | Cycle time over budget | Budget alarm fires in a lab with injected per-read delay |
| Box reboots mid-write | Partial or duplicate batch | Kill the reader during a write; no partial batch is ingested; replay is idempotent |
| WAN loss longer than spool | Data gap | Hold the WAN down past the cap; drops are counted and reported |
| Rollback drops site services | Switch and APs lose leases or controller | Roll a lab box back; site devices keep DHCP, DNS and register |
| ECMP pins to a dead uplink | Fixed destinations fail | Black-hole one uplink upstream; dead next hop evicted within target |
| VRRP tracks one flaky target | Master flaps | Drop the single target; master holds when several targets are tracked |
| Solar autonomy short in winter | Same-clock-time boots | Boot-time series against season before blaming the link |
| Onboarding still points at the old controller | Reset devices never register | Factory-reset a device on site; it registers with the new controller |

## Worked example

Question: a site on GEO needs a captive portal. Option 1 puts the portal on the one site box. Option 2 keeps the router and adds a portal box in the user path. Does either meet a 99% user-internet
target, and what does the second box cost? Inputs (illustrative): site power 0.998, satellite WAN 0.995, site box or router 0.999, portal box 0.997.

| Model | Command | Result |
| --- | --- | --- |
| Power, WAN, one site box in series | `just availability one-box.json` | 0.992017; 4,198.74 min/yr; status pass, exit 0 |
| Power, WAN, router, portal box in series | `just availability two-box.json` | 0.989041; 5,764.03 min/yr; status findings, exit 1 |

- Hand check: 0.998 x 0.995 x 0.999 = 0.992017; x 0.997 = 0.989041. Matches.
- The in-path portal box costs about 1,565 min/yr and misses the target. Either put the portal on the one box, or make the second box fail open (users bypass it when it fails), which removes it from
  the series.
- Latency check for the portal: 10 round trips per login at 700 ms is 7 s; a per-page validation adds 0.7 s to every page. At GEO sites the portal stays local.

## Review checklist

- [ ] Site shape chosen; one box in the user path; every auxiliary box proven to fail open.
- [ ] Feasibility matrix per model and firmware (native, add-on, central, impossible) with the veto rule applied.
- [ ] Each central function tested at the slowest link class's RTT.
- [ ] Two independent dial-out management paths; recovery does not use the access proxy or its certificates; out-of-band power per site.
- [ ] UDP and ICMP probes run on the box, or an address-translating overlay is recorded in IPAM.
- [ ] Every tool keys on (site, IP) or a device ID.
- [ ] Poll cycle measured per phase with a budget alarm; on-box reader with a capped, counted, crash-safe spool where needed.
- [ ] Discovery sources ranked by measured accuracy; install records archived before hardware turns over.
- [ ] Services site devices take from the box listed and kept in safe and rollback images; controller discovery tested in a rollback drill.
- [ ] Multi-WAN: hash policy set, dead next hops evicted, per-uplink health checks; no source-IP authorisation of sites.
- [ ] VRRP sites: separate DHCP ranges, several tracked targets, split-brain alarm, management through the master.
- [ ] Power: winter autonomy sized; dark periods classified by boot pattern; undervoltage read from latched flags.
- [ ] Onboarding dependencies (option 43, hooks) inventoried; factory-reset test passes before a controller cut-over.

## Further reading

URLs resolved 2026-10-29.

Carrier NAT and dial-out access:

- [RFC 4787 NAT behavioural requirements for UDP][rfc4787]: mapping timers and why keepalives are needed.
- [RFC 6888 Common requirements for carrier-grade NATs][rfc6888]: what CGN does to mappings and ports.
- [WireGuard quickstart][wg-qs]: persistent keepalive behind NAT.
- [Teleport agent architecture][tp-agents] and [Teleport TCP application access][tp-tcp]: reverse tunnels and the TCP scope of application access.
- [iptables-extensions][ipt-ext]: NETMAP for 1:1 translation of overlapping site ranges.

Edge telemetry:

- [vmagent][vmagent]: on-disk buffering for unreliable links (one example of an edge agent with a persistent queue).
- [rename(2)][rename2] and [fsync(2)][fsync2]: the atomic-file pattern behind a crash-safe spool.

Site services and gateways:

- [RFC 3046 DHCP relay agent information][rfc3046]: Circuit ID and Remote ID as topology evidence.
- [RFC 2132 DHCP options][rfc2132]: option 43 vendor-specific information.
- [RFC 5798 VRRPv3][rfc5798]: master election, preemption and advertisement timing.
- [Linux kernel IP sysctl][k-ipsysctl]: multipath hash policy and neighbour-aware next-hop selection.

[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
[rfc3046]: https://www.rfc-editor.org/rfc/rfc3046.html
[rfc4787]: https://www.rfc-editor.org/rfc/rfc4787.html
[rfc5798]: https://www.rfc-editor.org/rfc/rfc5798.html
[rfc6888]: https://www.rfc-editor.org/rfc/rfc6888.html
[wg-qs]: https://www.wireguard.com/quickstart/
[tp-agents]: https://goteleport.com/docs/reference/architecture/agents/
[tp-tcp]: https://goteleport.com/docs/enroll-resources/application-access/protect-apps/tcp/
[tp-auth]: https://goteleport.com/docs/reference/architecture/authentication/
[ssh1]: https://man.openbsd.org/ssh.1
[ipt-ext]: https://ipset.netfilter.org/iptables-extensions.man.html
[vmagent]: https://docs.victoriametrics.com/victoriametrics/vmagent/
[rename2]: https://man7.org/linux/man-pages/man2/rename.2.html
[fsync2]: https://man7.org/linux/man-pages/man2/fsync.2.html
[k-ipsysctl]: https://docs.kernel.org/networking/ip-sysctl.html
