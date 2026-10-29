---
Title: Service provider edge
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Subscriber edge design behind a wholesale hand-off: BNG plane split, PPPoE versus IPoE, RADIUS AAA and CoA, session scale and reconnect storms, state sync,
  CGNAT and its logging, the RSP's IPv6 transition choice, anti-spoofing placement, MTU and MSS with PPPoE, and lab validation pitfalls.
---

# Service provider edge

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [BNG design](#bng-design)
- [RADIUS AAA and CoA](#radius-aaa-and-coa)
- [Failover and reconnect storms](#failover-and-reconnect-storms)
- [CGNAT and logging](#cgnat-and-logging)
- [IPv6 transition](#ipv6-transition)
- [Anti-spoofing](#anti-spoofing)
- [MTU and MSS with PPPoE](#mtu-and-mss-with-pppoe)
- [Lab validation pitfalls](#lab-validation-pitfalls)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Sources](#sources)
- [Further reading](#further-reading)

## Scope

- Decides: subscriber session type, BNG placement and redundancy, AAA and dynamic authorisation contract, address strategy (public, CGNAT, IPv6 with a transition mechanism), source validation, MTU and
  MSS at the edge, and how the edge is validated before production.
- Requirements to capture: concurrent sessions per BNG and in total, session setup rate during recovery, tiers and policers, address supply, lawful-request response time, CPE fleet behaviour (PPPoE or
  DHCP, IPv6 support), hand-off encapsulation from the wholesaler.
- Hands to [australian-access-networks](australian-access-networks.md) (what the wholesaler hands over), [addressing-and-ipv6](addressing-and-ipv6.md) (prefix plans),
  [network-services](network-services.md) (DHCP, DNS and RADIUS server design), [routing-and-switching](routing-and-switching.md) (BGP, BFD, VRRP),
  [security-and-segmentation](security-and-segmentation.md) (management plane).
- Hands to skill-systems-architect for the hosts and clusters that run AAA, DHCP and logging, and to skill-eval-manager for acceptance-test discipline.

## Decision rules

| Rule | Value or threshold | Evidence |
| --- | --- | --- |
| PPPoE adds 8 bytes; default MRU 1492 | MSS clamp to 1452 (IPv4) or 1432 (IPv6) at 1500 underlay | VERIFIED_PRIMARY [RFC 2516][rfc2516]; arithmetic by `just mtu` |
| PPPoE payload 1500 needs RFC 4638 and an underlay of 1508 or more | Every hop to the BNG must pass the larger frame | VERIFIED_PRIMARY [RFC 4638][rfc4638] |
| IPoE session key: DHCP relay agent information (Option 82) or MAC | Keep the relay address and Option 82 intact to the server | VERIFIED_PRIMARY [RFC 3046][rfc3046] |
| CoA and Disconnect identify the session by attributes the NAS holds | Use Acct-Session-Id (plus NAS identity); User-Name can match many | VERIFIED_PRIMARY [RFC 5176][rfc5176] s3 |
| CoA-ACK means the request was accepted, not that forwarding changed | Read back the applied policer or filter | UNVERIFIED (judgement from lab experience) |
| RADIUS over UDP without Message-Authenticator is forgeable (CVE-2024-3596) | Require it on server and every NAS, after testing both | VERIFIED_SECONDARY [Jisc advisory][jisc-blast] |
| CGNAT shared space | 100.64.0.0/10, never routed on the internet | VERIFIED_PRIMARY [RFC 6598][rfc6598] |
| CGN must limit external ports per subscriber and default to paired pooling | Configurable per-subscriber port limits | VERIFIED_PRIMARY [RFC 6888][rfc6888] REQ-2, REQ-4 |
| Do not reuse a freed external port for 120 s | Unless TCP state is tracked | VERIFIED_PRIMARY [RFC 6888][rfc6888] REQ-8 |
| A CGN must offer subscriber control of mappings (PCP recommended) | Plan inbound-hosting customers | VERIFIED_PRIMARY [RFC 6888][rfc6888] REQ-9 |
| Port-block or deterministic allocation reduces log volume | Log per block, or compute the mapping | VERIFIED_PRIMARY [RFC 7422][rfc7422], [RFC 6888][rfc6888] REQ-14 |
| An external IP alone does not identify a subscriber behind CGNAT | Requests need IP, port and time; servers should log source port | VERIFIED_PRIMARY [RFC 6302][rfc6302], [RFC 6269][rfc6269] |
| nbn carries IPv4 and IPv6 transparently at Layer 2 | The IPv6 transition mechanism is the RSP choice | VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.1.1 |
| Ingress filtering on subscriber-facing interfaces | Strict uRPF or per-pool permits where routing is symmetric | VERIFIED_PRIMARY [RFC 2827][rfc2827], [RFC 3704][rfc3704] |
| VRRPv3 for first-hop redundancy; BFD for sub-second detection | RFC 9568 obsoletes RFC 5798 | VERIFIED_PRIMARY [RFC 9568][rfc9568], [RFC 5880][rfc5880] |

## BNG design

```text
Open-source BNG: three planes, each interface is a contract to version and test
             +-------------------------------------------------------------+
subscriber   | data plane (fast path): forwarding, policers, ACL, NAT      |  uplink
QinQ ------->|   S-tag per wholesaler, C-tag per subscriber                |-------> core
             +-----------------------------^-------------------------------+
                                           | session state, policer updates
             +-----------------------------+-------------------------------+
             | session plane: PPPoE / IPoE daemon, DHCP relay, RADIUS NAS   |
             +-----------------------------^-------------------------------+
                                           | Access, Accounting, CoA / DM, DHCP
             +-----------------------------+-------------------------------+
             | control plane: RADIUS, DHCP (v4/v6), BGP/BFD, VRRP, logging  |
             +-------------------------------------------------------------+
```

| Choice | PPPoE | IPoE (DHCP-triggered sessions) |
| --- | --- | --- |
| Session key | Username and password (PAP/CHAP) | Option 82 circuit ID, remote ID or MAC |
| Overhead | 8 bytes per packet; MSS clamp | None beyond VLAN tags |
| CPE requirement | PPPoE client and credentials | DHCP client; nothing to configure |
| Moving parts | Discovery, LCP, auth, IPCP/IPv6CP | DHCP relay path and lease state |
| Failure recovery | PADI storm after BNG loss | DHCP rebind storm after BNG loss |
| Typical fit | Existing PPPoE CPE fleet; multi-wholesaler realms by credential | Greenfield; CPE fleet unknown; simpler support |

- Decide session type from what the access network and the CPE fleet actually send. A lab that proves one type has not proved the other. UNVERIFIED (judgement).
- Model each wholesale network as its own S-tag domain so policing, accounting and RADIUS realm selection key off the outer tag. VERIFIED_PRIMARY for the tag model: AVC = C-VLAN, CVC = S-VLAN, IEEE
  802.1ad ([nbn PTS][nbn-pts] s4, s5).
- Hierarchical policing: write the direction once ("traffic from X towards Y, applied at interface Z input") and prove it with counters. Aggregate policers sit where paid capacity enters;
  per-subscriber policers nest below. Policer burst (CBS) must suit TCP. VERIFIED_PRIMARY for meter definitions ([RFC 2697][rfc2697], [RFC 2698][rfc2698]).
- Keep the tier catalogue as data (profile name to CIR, EIR, burst) and push it through an API with read-back, not CLI scraping.
- Kernel-bypass data planes: kernel firewalls protect only the host; routing protocol packets need a punt path or a separate kernel interface; election signalling (VRRP) and address ownership are
  bound by hooks. Re-verify every command against the deployed release. UNVERIFIED (implementation-specific; read the forwarder documentation).
- Size session scale on the target hardware. A virtual lab proves protocol behaviour, not scale.

## RADIUS AAA and CoA

- Authentication ([RFC 2865][rfc2865]), accounting ([RFC 2866][rfc2866]) and dynamic authorisation (CoA and Disconnect, [RFC 5176][rfc5176]) are separate operations on separate ports; give each its
  own acceptance test. VERIFIED_PRIMARY.
- One session-identity contract for every CoA sender and the NAS: Acct-Session-Id, optionally with User-Name and NAS identity. Confirm the NAS reads the attribute the sender writes (a standard
  Filter-Id versus a vendor-specific attribute). VERIFIED_PRIMARY for identification attributes ([RFC 5176][rfc5176] s3).
- Message-Authenticator ([RFC 2869][rfc2869]) on every packet is the BlastRADIUS mitigation; enabling enforcement before every NAS sends it breaks sessions silently. VERIFIED_SECONDARY [Jisc
  advisory][jisc-blast]. Check configuration with anchored matches, never a substring grep that also matches a commented line.
- Interim accounting interval sets usage-data freshness and RADIUS load: load = sessions / interval. 40,000 sessions at 600 s = about 67 packets per second steady, before storms.
- Keep RADIUS reachable during a BNG failover and size it for the storm rate ([Failover and reconnect storms](#failover-and-reconnect-storms)).

## Failover and reconnect storms

```text
BNG pair: a path fails over; sessions do not, unless state is synchronised
                 +-------+  sessions S1..Sn   +---------+
 subscribers ===>| BNG-1 |------------------->|         |
   (QinQ)    \   +-------+   X fails          |  core   |
              \  +-------+                    |         |
               ->| BNG-2 |------------------->|         |
                 +-------+  takes VIP/path    +---------+
 without state sync: every S1..Sn re-establishes on BNG-2
   PPPoE: PADI -> auth -> IPCP     IPoE: DHCP rebind/discover -> auth
   RADIUS Access + Accounting-Start, DHCP leases, CGNAT mappings: all at storm rate
```

- Name the HA claim exactly: first-hop failover gives a path; it does not move sessions. Without session-state synchronisation (or stateless IPoE with fast rebind), a BNG failure is a reconnect storm.
  UNVERIFIED as a product statement; true of any design without explicit state sync.
- Storm load = sessions to recover / target recovery time. 40,000 sessions in 20 s = 2,000 session setups per second across RADIUS, DHCP and CGNAT. Throttle or randomise reconnect at CPE and BNG where
  possible.
- Measure the full detection chain (hypervisor or chassis shutdown, VRRP or BFD, routing convergence) before writing an SLA. The protocol timer is rarely the dominant term.
- CGNAT mappings are lost with the node unless synchronised; every subscriber gets a new external address and port block.

## CGNAT and logging

- Use 100.64.0.0/10 for the inside ([RFC 6598][rfc6598]); expect the application impacts catalogued in [RFC 7021][rfc7021] and [RFC 6269][rfc6269] (geolocation, abuse blocking, inbound services, port
  exhaustion). VERIFIED_PRIMARY.
- Choose an allocation scheme for log volume: per-session logs (largest), port-block allocation (one record per block), or deterministic mapping (computed, almost no logs) ([RFC 7422][rfc7422]).
  Deterministic mapping trades flexibility (fixed ports per subscriber) for log volume.
- Lawful requests arrive as external IP, port and time. Keep CGNAT records joinable to the subscriber record (session accounting, circuit ID) with synchronised clocks (NTP) and an explicit time zone.
- Australian data retention (Telecommunications (Interception and Access) Act 1979, Part 5-1A) requires service providers to retain specified data for at least two years. VERIFIED_SECONDARY [Home
  Affairs data retention guideline][ha-dr]. Whether port numbers are a mandatory data item: UNVERIFIED; take legal advice before sizing log storage.
- A heavy CGNAT source can skew per-source load balancing at shared services (resolvers, caches). Check per-member rates before tuning one member. UNVERIFIED (field experience).

## IPv6 transition

| Mechanism | What the RSP runs | CPE requirement | Evidence |
| --- | --- | --- | --- |
| Dual stack with CGNAT for IPv4 | CGN plus native IPv6 (DHCPv6-PD) | IPv6 CE router ([RFC 7084][rfc7084]) | VERIFIED_PRIMARY |
| DS-Lite | AFTR (IPv4-in-IPv6, CGN at the AFTR) | B4 element | VERIFIED_PRIMARY [RFC 6333][rfc6333] |
| MAP-E | Border relay, stateless port-set mapping | MAP CE | VERIFIED_PRIMARY [RFC 7597][rfc7597] |
| 464XLAT | NAT64 (PLAT) with DNS64 | CLAT | VERIFIED_PRIMARY [RFC 6877][rfc6877], [RFC 6146][rfc6146], [RFC 6147][rfc6147] |

- Over a Layer 2 wholesale service the access technology does not choose the mechanism; the RSP and its CPE fleet do. VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.1.1.
- IPv4-as-a-service needs CE support ([RFC 8585][rfc8585]); an unmanaged CPE fleet usually forces dual stack plus CGNAT. UNVERIFIED (judgement).
- DHCPv6 is now [RFC 9915][rfc9915] (obsoletes RFC 8415). Relay remote-ID ([RFC 4649][rfc4649]) and the lightweight relay ([RFC 6221][rfc6221]) carry the subscriber key for IPv6 as Option 82 does for
  IPv4. VERIFIED_PRIMARY.
- Never disable IPv6 kernel-wide in a lab: daemons bound to `::` fail in ways production will not show, and dual stack stays unproven.

## Anti-spoofing

- Validate source addresses where subscriber traffic enters (access-side ingress, per session or per pool), not on the uplink. VERIFIED_PRIMARY [RFC 2827][rfc2827] (BCP 38), [RFC 3704][rfc3704] (BCP
  84).
- Generate the permits from the address allocator (pools, delegated prefixes), so a new pool cannot be forgotten. Strict uRPF suits single-homed subscribers; enhanced feasible-path uRPF ([RFC
  8704][rfc8704]) suits multihomed customers.
- A default deny on a shared interface also drops VRRP, BGP and DHCP; add explicit control-protocol permits and test them.
- On a kernel-bypass box, inspect the forwarding engine ACL during an incident, not the host firewall.

## MTU and MSS with PPPoE

- Budget per access encapsulation: PPPoE 8 bytes; each 802.1Q tag 4 bytes on the wire (frame size, not IP MTU). Run `just mtu` with the `pppoe` layer
  ([wan-and-remote-access](wan-and-remote-access.md#mtu-budget)).
- Clamp TCP MSS on the BNG for PPPoE sessions; permit ICMP Packet Too Big. VERIFIED_PRIMARY [RFC 8900][rfc8900], [RFC 8201][rfc8201].
- RFC 4638 restores a 1500-byte PPPoE payload only if the CPE, the access network, the NNI and the BNG all accept the larger frame. The nbn UNI and NNI maximum frame sizes are in the nbn Network
  Interface Specifications (not read for this reference): UNVERIFIED until checked.
- Test with DF-set probes at the computed MTU and one byte above, from a subscriber position, in both directions.

## Lab validation pitfalls

- A check that passes when the feature is absent is vacuous. Assert on specific content, check exit codes, and add a negative test that must fail. Some CLIs print help and exit 0 for an unknown
  command. UNVERIFIED (observed behaviour; see [automation-and-safety](automation-and-safety.md#validation-tiers)).
- Use the right observable: subscriber sessions from the session daemon, policer state from the data plane, leases from the DHCP server; not a host-stack or interface-up proxy.
- Test auth, accounting, CoA and Disconnect separately. A passing Access-Request proves nothing about CoA.
- Put no NAT, load-balancer SNAT or overlay hop between a DHCP relay and the server; it rewrites the relay address (giaddr) and breaks subnet selection ([RFC 3046][rfc3046]).
- Freeze the lab (kernel, packages) before integration tests; an overnight upgrade can remove a kernel module the design depends on.
- Canary one node before the fleet; write stage smoke gates before stage automation.
- Never describe a lab result as production validation ([architecture-method](architecture-method.md#evidence-labels-and-layers)).

## Patterns and anti-patterns

| Situation | Do | Avoid | Why |
| --- | --- | --- | --- |
| Unknown CPE fleet | IPoE with Option 82 keyed sessions | PPPoE by default | Fewer moving parts; no credentials to manage |
| Dynamic policy changes | CoA keyed on Acct-Session-Id with read-back | CoA by User-Name or IP | Ambiguous match; ACK without change |
| BNG HA claim | "Path fails over; sessions re-establish" | "Sessions preserved" without state sync | Storm unplanned; RADIUS and DHCP overwhelmed |
| CGNAT logging | Port blocks or deterministic mapping | Per-session logs at scale | Log volume and lawful-request search time |
| IPv6 | Dual stack from day one in the lab | `ipv6.disable=1` on hosts | Hides real defects |
| Source validation | Per pool on access ingress | One broad permit on the uplink | Spoofed sources pass; wrong direction |
| PPPoE MTU | MSS clamp plus ICMP permitted | Assume 1500 end to end | Large packets black-holed |

## Failure modes and tests

| Failure | Signal | Test that proves detection and recovery |
| --- | --- | --- |
| BNG node loss | All its sessions drop; storm on the peer | Power-off one BNG at busy-hour session count in the lab; measure recovery to 95% sessions |
| RADIUS unreachable | New sessions fail; existing continue | Block RADIUS; confirm fallback policy and alarm |
| CoA ignored | ACK returned, rate unchanged | CoA changes tier; read back the policer; negative test with wrong attribute |
| BlastRADIUS enforcement mismatch | Silent auth failures after hardening | Enable on a canary NAS; Access, Accounting and CoA each tested |
| CGNAT port exhaustion | Subscriber cannot open new flows | Load one subscriber past the port limit; alarm fires |
| Spoofed source from subscriber | Spoofed packets leave the network | Send forged source from a test subscriber; dropped and counted |
| PPPoE MTU blackhole | Small pages load, large transfers hang | DF probes at 1492 and 1493; MSS observed in SYN |
| DHCP relay path rewritten | Wrong pool or no lease | Lease from each relay subnet with Option 82 visible at the server |

## Worked example

Question: subscribers arrive on PPPoE over a 1500-byte access path. What MSS clamp applies, and what does a full 1500-byte PPPoE payload need?

| Step | Command or calculation | Result |
| --- | --- | --- |
| Standard PPPoE | `just mtu` path `pppoe-standard`: underlay 1500, layer `pppoe` | payload 1492; finding "8 short of 1500"; exit 1 |
| MSS clamp | helper output | 1452 (IPv4), 1432 (IPv6) |
| RFC 4638 path | path `pppoe-rfc4638`: underlay 1508, layer `pppoe` | payload 1500; MSS 1460 / 1440 |
| Storm sizing | 40,000 sessions / 20 s target | 2,000 setups per second at RADIUS, DHCP, CGNAT |
| Accounting load | 40,000 / 600 s interim interval | about 67 accounting packets per second steady |

- Input file shape: `{"schema_version": 1, "paths": [{"id": "pppoe-standard", "underlay_mtu": 1500, "layers": ["pppoe"], "required_payload_mtu": 1500}]}`; output from
  [mtu_budget.py](../scripts/mtu_budget.py) run 2026-10-29.
- Verdict: clamp MSS 1452/1432 unless every hop is proven to carry 1508-byte frames; then RFC 4638 with 1460/1440.
- Test: DF probes from a subscriber at 1492 (pass) and 1493 (fail) on the standard path.

## Review checklist

- [ ] Session type chosen from the CPE fleet and access hand-off, with the other type marked unproven.
- [ ] S-tag per wholesale network; policer direction written in one unambiguous form and tested with counters.
- [ ] CoA contract: identity attributes, NAS-read attribute, read-back step.
- [ ] Message-Authenticator enforced after every NAS is confirmed to send it.
- [ ] Reconnect storm rate computed and RADIUS, DHCP, CGNAT sized for it.
- [ ] CGNAT allocation scheme, log fields, clock source and retention stated; legal retention checked.
- [ ] IPv6 mechanism chosen by the RSP and tested dual stack in the lab.
- [ ] Source validation on access ingress, generated from the allocator; control protocols permitted.
- [ ] MTU budget from `just mtu`; MSS clamp point and value; DF probe results.
- [ ] Every acceptance test has a negative case that fails when the feature is absent.

## Sources

Checked 2026-10-29. VERIFIED_PRIMARY: every RFC row (titles and status confirmed on rfc-editor.org; RFC 8415 obsoleted by RFC 9915, RFC 5798 by RFC 9568), RFC 6888 REQ text, nbn PTS 2026-09-01.
VERIFIED_SECONDARY: BlastRADIUS mitigation (Jisc advisory and vendor notes), data retention period (Home Affairs guideline). UNVERIFIED: storm and accounting rates (arithmetic on assumed inputs), port
numbers as a mandatory retention item, nbn maximum frame sizes, kernel-bypass implementation notes.

## Further reading

URLs resolved 2026-10-29.

Sessions and AAA:

- [RFC 2516 PPPoE][rfc2516] and [RFC 4638 PPPoE MTU above 1492][rfc4638]: discovery, overhead and baby-giant negotiation.
- [RFC 5176 Dynamic Authorization Extensions to RADIUS][rfc5176]: CoA and Disconnect identification rules.
- [Jisc BlastRADIUS advisory][jisc-blast]: enforcing Message-Authenticator and the breakage to test for.

Addressing and translation:

- [RFC 6888 Common Requirements for CGNs][rfc6888] and [RFC 7422 Deterministic CGN][rfc7422]: port limits, allocation and logging.
- [RFC 6302 Logging Recommendations for Internet-Facing Servers][rfc6302]: why the far end must log source ports.
- [RFC 6333 DS-Lite][rfc6333], [RFC 7597 MAP-E][rfc7597], [RFC 6877 464XLAT][rfc6877]: the transition mechanisms an RSP chooses between.

Edge security:

- [RFC 2827 BCP 38][rfc2827], [RFC 3704 BCP 84][rfc3704], [RFC 8704 enhanced uRPF][rfc8704]: where and how to validate sources.

[rfc2516]: https://www.rfc-editor.org/rfc/rfc2516.html
[rfc2697]: https://www.rfc-editor.org/rfc/rfc2697.html
[rfc2698]: https://www.rfc-editor.org/rfc/rfc2698.html
[rfc2827]: https://www.rfc-editor.org/rfc/rfc2827.html
[rfc2865]: https://www.rfc-editor.org/rfc/rfc2865.html
[rfc2866]: https://www.rfc-editor.org/rfc/rfc2866.html
[rfc2869]: https://www.rfc-editor.org/rfc/rfc2869.html
[rfc3046]: https://www.rfc-editor.org/rfc/rfc3046.html
[rfc3704]: https://www.rfc-editor.org/rfc/rfc3704.html
[rfc4638]: https://www.rfc-editor.org/rfc/rfc4638.html
[rfc4649]: https://www.rfc-editor.org/rfc/rfc4649.html
[rfc5176]: https://www.rfc-editor.org/rfc/rfc5176.html
[rfc5880]: https://www.rfc-editor.org/rfc/rfc5880.html
[rfc6146]: https://www.rfc-editor.org/rfc/rfc6146.html
[rfc6147]: https://www.rfc-editor.org/rfc/rfc6147.html
[rfc6221]: https://www.rfc-editor.org/rfc/rfc6221.html
[rfc6269]: https://www.rfc-editor.org/rfc/rfc6269.html
[rfc6302]: https://www.rfc-editor.org/rfc/rfc6302.html
[rfc6333]: https://www.rfc-editor.org/rfc/rfc6333.html
[rfc6598]: https://www.rfc-editor.org/rfc/rfc6598.html
[rfc6877]: https://www.rfc-editor.org/rfc/rfc6877.html
[rfc6888]: https://www.rfc-editor.org/rfc/rfc6888.html
[rfc7021]: https://www.rfc-editor.org/rfc/rfc7021.html
[rfc7084]: https://www.rfc-editor.org/rfc/rfc7084.html
[rfc7422]: https://www.rfc-editor.org/rfc/rfc7422.html
[rfc7597]: https://www.rfc-editor.org/rfc/rfc7597.html
[rfc8201]: https://www.rfc-editor.org/rfc/rfc8201.html
[rfc8585]: https://www.rfc-editor.org/rfc/rfc8585.html
[rfc8704]: https://www.rfc-editor.org/rfc/rfc8704.html
[rfc8900]: https://www.rfc-editor.org/rfc/rfc8900.html
[rfc9568]: https://www.rfc-editor.org/rfc/rfc9568.html
[rfc9915]: https://www.rfc-editor.org/rfc/rfc9915.html
[nbn-pts]: https://www.nbnco.com.au/content/dam/nbn/documents/sell/wba/2026/sfaa-wba-nbn-ethernet-product-technical-specification-20260901.pdf.coredownload.pdf
[jisc-blast]: https://community.jisc.ac.uk/node/48998
[ha-dr]: https://www.homeaffairs.gov.au/criminal-justice/files/guidelines-telecommunications-interception-and-access-act-1979/guideline-data-retention-guideline.pdf
