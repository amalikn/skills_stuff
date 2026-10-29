---
Title: Routing, switching and control planes
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: Routing, switching and control-plane decision rules, patterns, failure modes, a convergence worked example and a review checklist.
---

# Routing, switching and control planes

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Forwarding and control model](#forwarding-and-control-model)
- [EVPN and VXLAN fabrics](#evpn-and-vxlan-fabrics)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Sources](#sources)
- [Further reading](#further-reading)

## Scope

- Decides: route sources and policy, IGP versus BGP, BGP edge filtering, failure detection, ECMP, EVPN/VXLAN control plane, L2 boundaries, multicast and QoS.
- Hands to [addressing-and-ipv6](addressing-and-ipv6.md): prefixes, VRF scopes and summarisation blocks.
- Hands to [wan-and-remote-access](wan-and-remote-access.md#mtu-budget): MTU budget for every overlay; to [datacenter-cloud-containers](datacenter-cloud-containers.md): fabric sizing.
- Hands to platform packs (skill-mikrotik, skill-cambium, skill-smc): exact commands and release defaults. This pack holds no deployment configuration.

## Decision rules

Evidence: VERIFIED_PRIMARY rows link the RFC (checked 2026-10-29). Platform defaults stay UNVERIFIED until checked for the deployed release.

| Rule                                          | Value or threshold                                                    | Evidence                      |
| --------------------------------------------- | --------------------------------------------------------------------- | ----------------------------- |
| Static route only for bounded, stable cases   | Add a liveness check, or a remote failure blackholes                  | UNVERIFIED (judgement)        |
| Pick IGP or BGP by boundary and policy        | Also scale, convergence, team skill; no fabric for fashion            | UNVERIFIED (judgement)        |
| eBGP without policy accepts and sends nothing | Default deny both ways; older code may be permissive                  | VERIFIED_PRIMARY [RFC 8212][rfc8212] |
| Filter every edge session                     | Bogons, special-purpose, own prefixes inbound                         | VERIFIED_PRIMARY [RFC 7454][rfc7454] |
| Reject too-specific prefixes                  | Commonly longer than /24 IPv4 or /48 IPv6                             | VERIFIED_PRIMARY [RFC 7454][rfc7454] |
| Max-prefix per session                        | Alarm before the trip                                                 | VERIFIED_PRIMARY [RFC 7454][rfc7454] |
| Route-origin validation                       | Drop Invalid; keep NotFound (bulk of table); checks origin AS only    | VERIFIED_PRIMARY [RFC 6811][rfc6811] |
| BGP roles and OTC attribute                   | Provider, Customer, Peer, RS, RS-Client; detect leaks; add to filters | VERIFIED_PRIMARY [RFC 9234][rfc9234] |
| TTL security (GTSM)                           | Record per session                                                    | VERIFIED_PRIMARY [RFC 5082][rfc5082] |
| TCP-AO; MD5 only where TCP-AO is unavailable  | Record per session                                                    | VERIFIED_PRIMARY [RFC 5925][rfc5925] |
| Graceful shutdown before maintenance          | Drain with the community first                                        | VERIFIED_PRIMARY [RFC 8326][rfc8326] |
| BGP hold time                                 | Suggested 90 s; implementations vary                                  | VERIFIED_PRIMARY [RFC 4271][rfc4271] |
| BFD for sub-second detection                  | Detection = remote multiplier x negotiated interval                   | VERIFIED_PRIMARY [RFC 5880][rfc5880] |
| Single-hop BFD                                | UDP 3784; TTL/Hop Limit 255 checked on receipt                        | VERIFIED_PRIMARY [RFC 5881][rfc5881] |
| Multihop BFD                                  | UDP 4784                                                              | VERIFIED_PRIMARY [RFC 5883][rfc5883] |
| No aggressive BFD on lossy or software paths  | Size from measured loss and CPU; add dampening                        | UNVERIFIED (field practice)   |
| Convergence = detection + propagation + FIB   | Measure FIB programming on the real hardware                          | UNVERIFIED (method)           |
| ECMP hashes per flow                          | A few elephant flows polarise load at any path count                  | VERIFIED_PRIMARY [RFC 2992][rfc2992] |
| Hash inputs                                   | 5-tuple, inner VXLAN headers, IPv6 flow label                         | VERIFIED_PRIMARY [RFC 6438][rfc6438] |
| Resilient hashing                             | Limits rehash when a member drops                                     | UNVERIFIED (platform feature) |
| eBGP-only datacenter fabric                   | No IGP; ASN per leaf or rack; handle AS-path loops                    | VERIFIED_PRIMARY [RFC 7938][rfc7938] |
| 16-bit private ASNs                           | 64512-65534; alone they cap a fabric at 1023 ASNs                     | VERIFIED_PRIMARY [RFC 6996][rfc6996] |
| 32-bit private ASNs                           | 4200000000-4294967294                                                 | VERIFIED_PRIMARY [RFC 6996][rfc6996] |
| IPv4 over IPv6 next hops ("unnumbered")       | Confirm every peer and monitoring tool supports it                    | VERIFIED_PRIMARY [RFC 8950][rfc8950] |
| VTEPs never fragment                          | Underlay MTU must carry VXLAN overhead; UDP 4789                      | VERIFIED_PRIMARY [RFC 7348][rfc7348] |
| STP root placement                            | Required wherever an L2 loop can form                                 | UNVERIFIED (judgement)        |
| QoS cannot create bandwidth                   | Verify DSCP across carrier, tunnel outer header, WMM                  | UNVERIFIED (judgement)        |
| Probe finer than the target                   | 1 s target: probe every 10-100 ms                                     | UNVERIFIED (method)           |

- IGP checks (OSPF/IS-IS): area or level boundaries, summarisation, adjacency authentication, flooding scope, SPF load on change.
- BGP next hop: record next-hop-self, third-party next hop at IXPs and the policy communities.

## Forwarding and control model

- For each important prefix record: origin, intended propagation, next-hop resolution, return path, filtering, failure withdrawal.
- List connected, static, dynamic, default and policy routes; redistribution; VRFs; route targets; anycast and first-hop roles.
- An established adjacency does not prove the right routes or traffic are accepted.
- A route in the RIB does not prove it is in the FIB or hardware table.

```text
Control plane versus data plane: two separate proofs
         +------+   +---------------+   +---------------+   +----------------+   +---------------+   +------+
control: | peer |-->| import policy |-->| RIB best path |-->| FIB / hardware |-->| export policy |-->| peer |
         +------+   +---------------+   +---------------+   +----------------+   +---------------+   +------+
         +---------+   +------------+   +--------------------+   +---------------+   +--------+
data:    | ingress |-->| VRF lookup |-->| next hop resolved? |-->| underlay path |-->| egress |
         +---------+   +------------+   +--------------------+   +---------------+   +--------+
return path: a separate lookup on the far device; prove it with its own test
```

Layer-2 boundaries:

- A VLAN ID is local unless the design maps it end to end. A VNI is fabric-wide; keep the VLAN-to-VNI map as source of truth.
- Document tagging and native VLAN, allowed trunks, loop prevention, MAC learning, flooding, multicast and gateway placement.
- Check LACP rate, min-links, multi-chassis dependencies, peer-link loss and split-brain. Test MLAG and EVPN-MH separately; they fail differently.
- No undocumented L2 extension over WAN, especially where the application only needs routed reachability.

Multicast and QoS:

- Multicast: source/group scope, IGMP/MLD, PIM-SM or SSM policy, platform support. Test joins, leaves, flooding, querier loss, source failure.
- QoS at every bottleneck: classification and trust, DSCP marking, policing versus shaping, queue scheduling, admission control.
- Real-time media: agree loss, latency, jitter and concealment from measured user quality, not a universal target.

## EVPN and VXLAN fabrics

| Route type            | Purpose                               | Design decision it drives                     |
| --------------------- | ------------------------------------- | --------------------------------------------- |
| 1 Ethernet A-D        | Multihoming mass withdraw, aliasing   | ESI per host bundle                           |
| 2 MAC/IP              | Host reachability, ARP/ND suppression | Suppression on or off                         |
| 3 Inclusive multicast | BUM replication list                  | Ingress replication versus underlay multicast |
| 4 Ethernet segment    | Designated forwarder election         | DF behaviour on member loss                   |
| 5 IP prefix           | Routed prefixes in a VRF              | Symmetric IRB, L3 VNI per VRF                 |

- Standards: EVPN [RFC 7432][rfc7432]; over VXLAN/NVGRE/Geneve [RFC 8365][rfc8365]; IRB [RFC 9135][rfc9135]; type 5 [RFC 9136][rfc9136]. VERIFIED_PRIMARY.
- Symmetric IRB: L3 VNI per VRF, scales, needs a transit VNI. Asymmetric: every VLAN on every leaf.
- Also decide: EVPN multihoming (ESI) versus MLAG, anycast gateway MAC/IP consistency, RD/RT allocation scheme.

```text
EVPN/VXLAN fabric: underlay, overlay and multihoming roles
              +--------------------------------------------+
              | spine: eBGP or iBGP RR, underlay + EVPN    |
              +--------------------------------------------+
                 |                                      |
          +-------------+                        +-------------+
          | leaf A      |                        | leaf B      |
          | VTEP 1 /32  |                        | VTEP 2 /32  |
          +-------------+                        +-------------+
                 |          ESI-LAG (one bundle)        |
                 +-----------------+--------------------+
                                   |
                              +---------+
                              | host    |
                              +---------+
underlay: loopback /32 per VTEP; p2p /31 or unnumbered
overlay:  L2 VNI per VLAN; L3 VNI per VRF (symmetric IRB)
multihoming: DF election per ES; aliasing; mass withdraw by route type 1
```

## Patterns and anti-patterns

| Pattern                                       | Use when                           | Anti-pattern                        | Why it fails                                       |
| --------------------------------------------- | ---------------------------------- | ----------------------------------- | -------------------------------------------------- |
| Explicit import and export policy per session | Every eBGP session                 | Rely on platform default            | Older code is permissive; one leak floods the peer |
| BFD sized from measured loss                  | Fast failover on stable media      | 50 ms BFD on radio or satellite     | Burst loss triggers flaps and churn                |
| Static route plus liveness check              | Small stub site, one exit          | Bare static default to a remote hop | Remote failure is invisible; traffic blackholes    |
| eBGP-only Clos                                | Many leaves, simple policy         | IGP plus iBGP full mesh at scale    | More protocols, more failure interactions          |
| Symmetric IRB with L3 VNI                     | Many VRFs or VLANs                 | Asymmetric IRB fabric-wide          | Every VLAN on every leaf; table and flood growth   |
| Routed reachability between sites             | Applications need IP only          | L2 stretched over WAN               | One broadcast domain spans a slow, lossy link      |
| Resilient hashing                             | Bundles or ECMP groups that change | Plain modulo hash                   | Member loss rehashes every flow                    |

## Failure modes and tests

| Failure                              | Symptom                                  | Blast radius                       | Test that proves the design handles it                          |
| ------------------------------------ | ---------------------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| Route leak from customer to upstream | Traffic for others transits you          | Internet-wide for leaked prefixes  | Export a test prefix set; confirm only owned aggregates leave   |
| Max-prefix trip                      | Session drops; all routes from peer gone | Every prefix via that peer         | Lab: exceed the warn level; alarm fires before the trip         |
| RIB/FIB mismatch                     | Route shown, traffic dropped             | Prefixes beyond hardware table     | Compare RIB and FIB counts; send traffic to a late-added prefix |
| Slow detection without BFD           | Up to hold time of blackhole             | All flows on the failed path       | Pull a link silently (no carrier loss); measure loss window     |
| BFD flap on lossy link               | Route churn, repeated short outages      | Site or path                       | Replay measured loss in lab; count flaps per hour               |
| ECMP polarisation                    | One path hot, others idle                | Fabric throughput                  | Run elephant flows; read per-member counters                    |
| MLAG peer-link loss / split brain    | Duplicate frames or isolated hosts       | Every dual-homed host              | Cut peer link under load; verify secondary behaviour            |
| Asymmetric return path               | Stateful device drops replies            | Flows crossing that device         | Trace both directions; fail one exit; repeat                    |
| Overlay MTU short                    | Small packets work, large hang           | Every tenant flow over the overlay | DF-set probes at full size and one byte above                   |
| TCAM or next-hop group exhaustion    | New routes fail to program               | New prefixes or ECMP groups        | Load table to design size plus growth in lab                    |

Also test route presence and absence, preference, management reachability after policy change, and failback.

## Worked example

Question: can a dual-homed site meet a 1 s interruption target on loss of its primary uplink?

Inputs (illustrative): BGP over a fibre uplink; BFD interval 300 ms, multiplier 3; backup path pre-installed as a second route.

| Step                  | Calculation                           | Result                 |
| --------------------- | ------------------------------------- | ---------------------- |
| Detection with BFD    | 3 x 300 ms                            | 900 ms                 |
| Detection without BFD | Hold time 90 s ([RFC 4271][rfc4271] suggestion) | Up to 90 s             |
| Propagation           | Local decision; backup already in RIB | ~0 ms (measure)        |
| FIB update            | Platform-specific; must be measured   | Unknown until lab test |
| Budget left for FIB   | 1,000 - 900 ms                        | 100 ms                 |

- Verdict: 300 ms x 3 leaves 100 ms for FIB programming. That is too tight to accept without a measurement.
- Option: 100 ms x 3 = 300 ms detection on fibre, leaving 700 ms. Do not use that on a lossy radio path.
- Test: probe at 10 ms across the cut; interruption = lost probes x 10 ms. Accept only if the measured value is under 1 s in 10 of 10 cuts.

## Review checklist

- [ ] Every important prefix has origin, propagation, return path and withdrawal behaviour recorded.
- [ ] Every eBGP session has explicit import and export policy, max-prefix and session protection.
- [ ] ROV handling states Invalid dropped and NotFound accepted.
- [ ] Detection time is computed (multiplier x interval) and sized for the medium's measured loss.
- [ ] Convergence is measured end to end, including FIB programming on real hardware.
- [ ] ECMP hash inputs and elephant-flow behaviour are stated.
- [ ] Overlay MTU is computed and proven with DF-set probes.
- [ ] L2 extent, STP root, MLAG or ESI behaviour on peer loss are documented and tested.
- [ ] Platform defaults are labelled UNVERIFIED until checked for the deployed release.

## Sources

Every rule row links its primary source (VERIFIED_PRIMARY, checked 2026-10-29). The FRRouting BGP guide is under Further reading.

## Further reading

URLs resolved 2026-10-29. The decision rules stay above; these give depth.

BGP policy and routing security:

- [RFC 7454 (BCP 194) BGP Operations and Security][rfc7454]: full edge filter, max-prefix and session-protection checklist.
- [MANRS Network Operators actions][manrs]: industry baseline on filtering, anti-spoofing, coordination and validation.
- [NLnet Labs RPKI documentation][rpki]: ROA design, validator deployment and ROV failure modes.
- [RFC 9234 Route Leak Prevention Using Roles][rfc9234]: role negotiation and OTC attribute semantics.

Datacenter fabrics and EVPN:

- [RFC 7938 BGP in Large-Scale Data Centers][rfc7938]: eBGP-only Clos design, ASN allocation and ECMP rationale.
- [RFC 8365 EVPN as a Network Virtualization Overlay][rfc8365]: VXLAN/Geneve EVPN, split horizon and multihoming over IP.
- [RFC 9135 Integrated Routing and Bridging in EVPN][rfc9135]: symmetric versus asymmetric IRB packet walks.
- [FRRouting EVPN guide][frr-evpn]: an open implementation of EVPN route types, VNIs and multihoming.
- [FRRouting BGP guide][frr-bgp]: unnumbered peering, policy and RPKI integration in an open stack.

Linux forwarding plane:

- [Linux kernel VRF][k-vrf]: l3mdev VRF semantics used by Linux-based NOS and hosts.
- [Linux kernel bonding][k-bond]: LACP modes, hash policies and failover behaviour.
- [Linux kernel VXLAN][k-vxlan]: VTEP, FDB and learning behaviour on Linux.

[rfc2992]: https://www.rfc-editor.org/rfc/rfc2992.html [rfc4271]: https://www.rfc-editor.org/rfc/rfc4271.html [rfc5082]: https://www.rfc-editor.org/rfc/rfc5082.html [rfc5880]:
https://www.rfc-editor.org/rfc/rfc5880.html [rfc5881]: https://www.rfc-editor.org/rfc/rfc5881.html [rfc5883]: https://www.rfc-editor.org/rfc/rfc5883.html [rfc5925]:
https://www.rfc-editor.org/rfc/rfc5925.html [rfc6438]: https://www.rfc-editor.org/rfc/rfc6438.html [rfc6811]: https://www.rfc-editor.org/rfc/rfc6811.html [rfc6996]:
https://www.rfc-editor.org/rfc/rfc6996.html [rfc7348]: https://www.rfc-editor.org/rfc/rfc7348.html [rfc7432]: https://www.rfc-editor.org/rfc/rfc7432.html [rfc7454]:
https://www.rfc-editor.org/rfc/rfc7454.html [rfc7938]: https://www.rfc-editor.org/rfc/rfc7938.html [rfc8212]: https://www.rfc-editor.org/rfc/rfc8212.html [rfc8326]:
https://www.rfc-editor.org/rfc/rfc8326.html [rfc8365]: https://www.rfc-editor.org/rfc/rfc8365.html [rfc8950]: https://www.rfc-editor.org/rfc/rfc8950.html [rfc9135]:
https://www.rfc-editor.org/rfc/rfc9135.html [rfc9136]: https://www.rfc-editor.org/rfc/rfc9136.html [rfc9234]: https://www.rfc-editor.org/rfc/rfc9234.html [manrs]: https://manrs.org/netops/ [rpki]:
https://rpki.readthedocs.io/en/latest/ [frr-bgp]: https://docs.frrouting.org/en/latest/bgp.html [frr-evpn]: https://docs.frrouting.org/en/latest/evpn.html [k-vrf]:
https://docs.kernel.org/networking/vrf.html [k-bond]: https://docs.kernel.org/networking/bonding.html [k-vxlan]: https://docs.kernel.org/networking/vxlan.html
