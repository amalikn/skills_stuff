---
Title: WAN, internet edge and remote access
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: WAN, internet edge and remote-access decision rules, MTU budget, patterns, failure modes, a tunnel-over-satellite worked example and a review checklist.
---

# WAN, internet edge and remote access

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [High-latency, satellite and radio links](#high-latency-satellite-and-radio-links)
- [MTU budget](#mtu-budget)
- [Redundancy and CGNAT](#redundancy-and-cgnat)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Sources](#sources)
- [Further reading](#further-reading)

## Scope

- Decides: access options, tunnels and VPN, MTU budget, carrier diversity, failover and failback, remote-user access, cutover.
- Requirements to capture: sites, latency-sensitive apps, inbound publishing, egress policy, both-direction bandwidth, burst, caps, contention.
- Also: data sovereignty, carrier availability, outage tolerance, contract terms, escalation paths, remote support constraints.
- Hands to [routing-and-switching](routing-and-switching.md) (BFD, BGP), [capacity-and-resilience](capacity-and-resilience.md) (sizing), skill-systems-architect (degraded-link replication).
- Hands to skill-smc (SMC access and ansible-wifi reports), skill-cambium or skill-mikrotik (radio paths).

## Decision rules

| Rule                                                    | Value or threshold                                  | Evidence                                        |
| ------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------- |
| Record per access link: public, static, or behind CGNAT | CGNAT space is 100.64.0.0/10                        | VERIFIED_PRIMARY [RFC 6598][rfc6598]            |
| CGN behaviour (mappings, ports, logging)                | Read before designing inbound access                | VERIFIED_PRIMARY [RFC 6888][rfc6888]            |
| Behind CGNAT nothing inbound works                      | Tunnels and management start at the site            | Derived from [RFC 6888][rfc6888]                |
| Keepalive shorter than carrier NAT mapping timeout      | Measure it; carriers rarely publish it              | UNVERIFIED (field experience)                   |
| IKEv2 / ESP for IPsec                                   | NAT traversal moves IKE and ESP to UDP 4500         | VERIFIED_PRIMARY [RFC 7296][rfc7296], [RFC 4303][rfc4303] |
| WireGuard is a fixed suite (Noise, ChaCha20-Poly1305)   | Simple audits; no algorithm agility                 | VERIFIED_PRIMARY [WireGuard paper][wg]          |
| Handshake is not reachability                           | Test the application through the tunnel             | UNVERIFIED (judgement)                          |
| PEPs split TCP on satellite                             | Tunnels and QUIC hide TCP, so lose the acceleration | VERIFIED_PRIMARY [RFC 3135][rfc3135] (IPsec); QUIC derived |
| Never rely on fragmentation                             | Clamp MSS; permit ICMP Too Big                      | VERIFIED_PRIMARY [RFC 8900][rfc8900] (BCP 230)  |
| PMTUD needs ICMP Too Big to reach the sender            | Filtered ICMP = blackhole for large packets         | VERIFIED_PRIMARY [RFC 1191][rfc1191], [RFC 8201][rfc8201] |
| Prefer PLPMTUD where the app supports it                | TCP; datagram base 1200 B for UDP                   | VERIFIED_PRIMARY [RFC 4821][rfc4821], [RFC 8899][rfc8899] |
| IPv6 inside any tunnel                                  | Needs >= 1280, or the tunnel must fragment itself   | VERIFIED_PRIMARY [RFC 8200][rfc8200]            |
| Tunnel MTU traps                                        | Read before stacking encapsulations                 | VERIFIED_PRIMARY [RFC 4459][rfc4459]            |
| Fail back with a hold-down                              | A flapping primary must not oscillate traffic       | UNVERIFIED (judgement)                          |
| Two carriers on one pole or satellite gateway           | One failure domain                                  | UNVERIFIED (judgement)                          |

- Remote users: decide identity and device posture, least-privilege app access, split or full tunnel, DNS and lost-device response.
- Keep emergency management paths independent of the component being changed.
- Compare leased private service, internet VPN, SD-WAN, cloud interconnect and app-level access against the service criteria.

## High-latency, satellite and radio links

- Measure latency, jitter, loss, MTU and availability under real conditions, including weather and busy hour.
- GEO is 35,786 km up. Up and down twice gives at least ~477 ms RTT before processing (derived: 4 x 35,786 km / c).
- Size TCP windows to the bandwidth-delay product: 50 Mbit/s at 600 ms RTT needs ~3.75 MB in flight.
- A 64 KB window caps that path near 0.9 Mbit/s.
- Decide per traffic class whether to tunnel. Measure throughput inside and outside the tunnel before committing.
- Radio loss is not congestion, but loss-based TCP backs off anyway. Record the congestion control on important endpoints.
- No sub-second BFD or aggressive routing timers over links with measured burst loss.

## MTU budget

Compute from the smallest link MTU on the path, then prove it with DF-set probes. Helper: `just mtu <file>` ([mtu_budget.py](../scripts/mtu_budget.py)).

| Layer added                      | Bytes   | Basis                                                             |
| -------------------------------- | ------- | ----------------------------------------------------------------- |
| PPPoE                            | 8       | PPPoE 6 + PPP 2, [RFC 2516][rfc2516]                              |
| GRE over IPv4, no key / with key | 24 / 28 | outer IPv4 20 + GRE 4 (+4 key), [RFC 2784][rfc2784], [RFC 2890][rfc2890] |
| WireGuard over IPv4 / IPv6       | 60 / 80 | outer IP 20/40 + UDP 8 + header 16 + Poly1305 tag 16              |
| IPsec ESP tunnel, AES-GCM, IPv4  | 54-57   | IP 20 + SPI/seq 8 + IV 8 + pad 0-3 + trailer 2 + ICV 16, [RFC 4106][rfc4106]; `just mtu` layer `esp-gcm-ipv4` = 57 |
| ... plus NAT-T                   | +8      | UDP 4500 encapsulation                                            |
| VXLAN over IPv4 / IPv6           | 50 / 70 | includes inner Ethernet 14, [RFC 7348][rfc7348]                   |
| MPLS label                       | 4 each  | per label in the stack                                            |

```text
MTU stack: PPPoE access, WireGuard tunnel, VXLAN inside (bytes)
  1500  access link IP MTU (Ethernet)
-    8  PPPoE                               = 1492
-   60  WireGuard over IPv4                 = 1432  inner IP MTU
-   50  VXLAN inside the tunnel (if any)    = 1382  tenant IP MTU
-   40  IPv4 + TCP headers (IPv6: 60)       = 1342  TCP MSS to clamp
```

## Redundancy and CGNAT

- Validate separate failure domains for carrier, CPE, power, antenna, cable, upstream exchange and DNS.
- Decide failover and failback, route stability, degraded capacity and asymmetric paths.
- NAT and firewall state does not move between edges unless synchronised.
- Path steering is a testable control; applications react differently to path change.
- Budget backup and rebuild traffic alongside interactive load.

```text
Dual-edge WAN failover (X = failed element)
                     +--------+    +-----------------------+
                +--->| edge A |-X->| carrier 1 fibre/radio |--+
+------------+  |    +--------+    +-----------------------+  |    +----------------+
| site LAN   |--+                                             +--->| hub / internet |
| gateway    |  |    +--------+    +-----------------------+  |    +----------------+
+------------+  +--->| edge B |--->| carrier 2 satellite   |--+
                     +--------+    +-----------------------+
detect:     BFD or probe through the tunnel, never interface state alone
on loss A:  tunnel A down -> routes withdrawn -> traffic via B at degraded capacity
            NAT and firewall sessions on A are lost; new public source address via B
recovery:   hold-down timer, then fail back; sessions on B reset again
management: must reach the site through B alone (prove it)
```

```text
Site behind carrier-grade NAT: every session starts at the site
     +--------------------------+    +---------------+    +------------------------+
out: | site router (100.64.x.x) |--->| carrier CGNAT |--->| hub broker (mgmt, VPN) |
     +--------------------------+    +---------------+    +------------------------+
in:  hub --> site: X  (no mapping exists until the site sends first)
keepalive interval < carrier mapping timeout (measure it)
```

## Patterns and anti-patterns

| Pattern                                 | Use when                             | Anti-pattern                   | Why it fails                                  |
| --------------------------------------- | ------------------------------------ | ------------------------------ | --------------------------------------------- |
| Site-initiated tunnel with keepalive    | Site behind CGNAT or dynamic address | Inbound management to the site | No inbound mapping exists                     |
| MSS clamp plus ICMP Too Big permitted   | Any tunnel                           | Block all ICMP "for security"  | PMTUD blackhole; large transfers hang         |
| Probe-based failover through the tunnel | Carrier faults beyond the CPE        | Interface-state failover       | Link stays up while the path is dead          |
| Hold-down before failback               | Unstable primary                     | Immediate failback             | Traffic oscillates; sessions reset repeatedly |
| Per-class tunnel decision on satellite  | PEP-accelerated carrier              | Tunnel everything              | TCP loses PEP acceleration                    |
| Verified physical diversity             | "Redundant" carriers                 | Trust two circuit IDs          | Shared pole, duct or gateway                  |

## Failure modes and tests

| Failure                          | Symptom                              | Blast radius                   | Test that proves the design handles it                        |
| -------------------------------- | ------------------------------------ | ------------------------------ | ------------------------------------------------------------- |
| PMTUD blackhole                  | Small packets work, large hang       | Every flow over the tunnel     | DF probes at computed MTU and one byte above                  |
| Primary carrier loss             | Failover to backup at lower capacity | Whole site                     | Planned link pull; observe routes, sessions, alarms, failback |
| Silent path loss (link up)       | No failover, total loss              | Whole site                     | Drop traffic upstream of CPE in lab; probe detects            |
| CGNAT mapping expiry             | Tunnel stalls after idle             | Management and VPN             | Idle the tunnel past the measured timeout                     |
| Flapping primary                 | Repeated short outages               | Whole site                     | Toggle primary; confirm hold-down holds                       |
| Asymmetric return after failover | Stateful drops                       | Flows through firewalls or NAT | Trace both directions after failover                          |
| Backup capacity exceeded         | Congestion on backup                 | Interactive and bulk traffic   | Run busy-hour load on backup alone                            |
| Management lost on failover      | Cannot reach site via backup         | Operations                     | Reach management through B with A down                        |

Cutover: start from a traffic matrix and a scoped canary. Keep existing defaults during an additive rollout unless rerouting is intended. Test LAN, internet, DNS, critical apps, long-lived sessions
and reverse access.

## Worked example

Question: can a site on GEO satellite (50 Mbit/s, 600 ms RTT, PPPoE) carry a WireGuard tunnel with a VXLAN overlay at 1500 B tenant MTU?

| Step                    | Calculation or command                      | Result                                         |
| ----------------------- | ------------------------------------------- | ---------------------------------------------- |
| MTU model               | `just mtu examples/mtu-budget-short.json`   | exit 1: payload 1382, 118 short of 1500        |
| Fix needed              | Raise underlay to 1618, or lower tenant MTU | Access link fixed at 1500, so lower tenant MTU |
| TCP MSS to clamp        | 1382 - 40 (IPv4) / - 60 (IPv6)              | 1342 / 1322                                    |
| Bandwidth-delay product | 50 Mbit/s x 0.6 s / 8                       | 3.75 MB in flight                              |
| 64 KB window ceiling    | 65,536 x 8 / 0.6 s                          | ~0.87 Mbit/s per flow                          |
| PEP effect              | Tunnel hides TCP from the carrier PEP       | Measure throughput inside and outside          |

- Verdict: set tenant MTU 1382, clamp MSS 1342, and confirm hosts use window scaling up to 3.75 MB.
- Test: DF probes at 1382 (pass) and 1383 (fail); single-flow throughput inside and outside the tunnel.

## Review checklist

- [ ] Each access link recorded as public, static or CGNAT; site-initiated tunnels where CGNAT.
- [ ] Keepalive interval set below the measured carrier mapping timeout.
- [ ] MTU budget computed with `just mtu`; MSS clamp point and value stated; ICMP Too Big permitted.
- [ ] Physical diversity traced: carrier, CPE, power, antenna, pole, exchange, gateway.
- [ ] Failover detection works through the path, not on interface state.
- [ ] Failback has a hold-down; session loss on failover is accepted and stated.
- [ ] Backup carries busy-hour load or the shed list is written.
- [ ] Management reaches the site through the backup alone.
- [ ] Satellite: BDP and PEP effect measured inside and outside the tunnel.

## Sources

VERIFIED_PRIMARY, checked 2026-10-29: every rule row links its RFC; also [RFC 4106][rfc4106] (ESP AES-GCM) and [RFC 2516][rfc2516] (PPPoE). Derived arithmetic (header sums, GEO RTT, bandwidth-delay
product) follows from those sources. UNVERIFIED: the CGNAT timeout and PEP prevalence remarks are field experience, not standards facts.

## Further reading

URLs resolved 2026-10-29.

MTU and fragmentation:

- [RFC 8899 Datagram PLPMTUD][rfc8899]: probing MTU without depending on ICMP.
- [RFC 8900 IP Fragmentation Considered Fragile][rfc8900]: why fragmentation fails and what to do instead.
- [RFC 4459 MTU and Fragmentation Issues with In-the-Network Tunneling][rfc4459]: tunnel MTU failure modes.

Tunnels and VPN:

- [WireGuard whitepaper][wg]: message formats, timers and the cryptokey routing model.
- [WireGuard protocol and cryptography](https://www.wireguard.com/protocol/): the fixed cipher suite and handshake.
- [RFC 7296 IKEv2][rfc7296]: IKE negotiation, rekeying and NAT traversal.

Carrier edge and satellite:

- [RFC 6888 Common Requirements for Carrier-Grade NATs][rfc6888]: what CGN does to mappings, ports and logging.
- [RFC 3135 Performance Enhancing Proxies][rfc3135]: TCP splitting on satellite paths and its conflict with IPsec.
- [MANRS Network Operators actions](https://manrs.org/netops/): edge anti-spoofing and filtering at the internet border.

[rfc1191]: https://www.rfc-editor.org/rfc/rfc1191.html [rfc2516]: https://www.rfc-editor.org/rfc/rfc2516.html [rfc2784]: https://www.rfc-editor.org/rfc/rfc2784.html [rfc2890]:
https://www.rfc-editor.org/rfc/rfc2890.html [rfc3135]: https://www.rfc-editor.org/rfc/rfc3135.html [rfc4106]: https://www.rfc-editor.org/rfc/rfc4106.html [rfc4303]:
https://www.rfc-editor.org/rfc/rfc4303.html [rfc4459]: https://www.rfc-editor.org/rfc/rfc4459.html [rfc4821]: https://www.rfc-editor.org/rfc/rfc4821.html [rfc6598]:
https://www.rfc-editor.org/rfc/rfc6598.html [rfc6888]: https://www.rfc-editor.org/rfc/rfc6888.html [rfc7296]: https://www.rfc-editor.org/rfc/rfc7296.html [rfc7348]:
https://www.rfc-editor.org/rfc/rfc7348.html [rfc8200]: https://www.rfc-editor.org/rfc/rfc8200.html [rfc8201]: https://www.rfc-editor.org/rfc/rfc8201.html [rfc8899]:
https://www.rfc-editor.org/rfc/rfc8899.html [rfc8900]: https://www.rfc-editor.org/rfc/rfc8900.html [wg]: https://www.wireguard.com/papers/wireguard.pdf
