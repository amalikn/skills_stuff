---
Title: Datacenter, cloud and container networking
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: Datacenter fabric, cloud and container networking decision rules, patterns, failure modes, an N-1 and MTU worked example and a review checklist.
---

# Datacenter, cloud and container networking

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Fabric shape](#fabric-shape)
- [Cloud provider facts](#cloud-provider-facts)
- [Containers](#containers)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: fabric topology and oversubscription, underlay and overlay MTU, cloud and hybrid addressing, container network model and policy enforcement.
- Hands to [routing-and-switching](routing-and-switching.md): BGP, BFD, ECMP hashing and EVPN detail; to [addressing-and-ipv6](addressing-and-ipv6.md): cloud supernet.
- Hands to skill-systems-architect: placement, node reserve, storage, workload limits and maintenance sequencing.
- Use version-matched implementation documentation before producing manifests or provider templates.

## Decision rules

| Rule                                         | Value or threshold                                                 | Evidence                                        |
| -------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------- |
| Leaf/spine: every leaf to every spine        | No leaf-leaf links except an MLAG peer link; leaf to leaf = 2 hops | UNVERIFIED (Clos convention)                    |
| Oversubscription per leaf                    | Host-facing bandwidth / spine-facing bandwidth                     | UNVERIFIED (arithmetic)                         |
| Losing 1 of N spines removes 1/N of capacity | Size N so N-1 still carries busy hour                              | UNVERIFIED (arithmetic)                         |
| Underlay addressing                          | /31 or unnumbered p2p; /32 loopback as router ID and VTEP          | VERIFIED_PRIMARY [RFC 7938][rfc7938] (eBGP-only rationale) |
| VXLAN overhead                               | 50 B over IPv4, 70 B over IPv6                                     | VERIFIED_PRIMARY [RFC 7348][rfc7348] s5 (derived sum) |
| VTEPs must not fragment                      | Underlay carries the overhead                                      | VERIFIED_PRIMARY [RFC 7348][rfc7348]            |
| 1500 B tenant over VXLAN/IPv4                | Underlay IP MTU >= 1550; 1554 with inner 802.1Q                    | VERIFIED_PRIMARY [RFC 7348][rfc7348] (derived)  |
| Geneve overhead                              | 8 B base plus variable options, over UDP                           | VERIFIED_PRIMARY [RFC 8926][rfc8926]            |
| Jumbo underlay, tenant well below            | Record both; prove with DF probes, not counters                    | UNVERIFIED (judgement)                          |
| Lossless RoCE                                | Needs PFC/ECN end to end; agree with systems                       | UNVERIFIED (judgement)                          |
| OOB management                               | Must not depend on the fabric it manages                           | UNVERIFIED (judgement)                          |
| Physical separation of planes                | Justify from failure or performance evidence                       | UNVERIFIED (judgement)                          |
| Reserve a cloud supernet first               | Overlapping VPCs cannot peer or route without translation          | UNVERIFIED (judgement)                          |

- VXLAN 50 B = outer IPv4 20 + UDP 8 + VXLAN 8 + inner Ethernet 14. The inner frame header rides inside the outer IP packet.
- Keep management, workload, migration and storage logically separate. Storage: latency and loss, rebuild bandwidth, path redundancy, QoS.

## Fabric shape

```text
Leaf/spine (folded Clos): one routed uplink per leaf per spine
          spine 1   spine 2   spine 3   spine 4
leaf 1       x         x         x         x
leaf 2       x         x         x         x
leaf 3       x         x         x         x
leaf 4       x         x         x         x
legend: x = routed p2p uplink (/31 or unnumbered); leaf to leaf = 2 hops via any spine (ECMP x4)
host: dual-homed to leaf 1 + leaf 2 (one LACP bundle; MLAG or EVPN ESI)
overlay VNIs and VRFs ride the underlay: underlay up does not prove tenant reachability
```

## Cloud provider facts

VERIFIED_PRIMARY, checked 2026-10-29. Re-check before design sign-off.

| Provider | Fact that changes sizing                                                  | Source               |
| -------- | ------------------------------------------------------------------------- | -------------------- |
| AWS      | First four and last address of every subnet reserved                      | [AWS subnet sizing][aws-subnet] |
| Azure    | Five addresses reserved per subnet                                        | [Azure VNet FAQ][azure-faq] |
| GCP      | Subnet at least /29; primary range can grow, never shrink                 | [GCP subnets][gcp-subnets] |
| AWS      | 9001 MTU inside a VPC                                                     | [AWS EC2 MTU][aws-mtu] |
| AWS      | 1500 via internet gateway, VPN, or inter-Region without transit gateway   | [AWS EC2 MTU][aws-mtu] |
| AWS      | 8500 over inter-Region VPC peering                                        | [AWS EC2 MTU][aws-mtu] |
| GCP      | Default VPC MTU 1460; configurable 1300-8896                              | [GCP MTU][gcp-mtu]   |
| GCP      | Subnet gateway does not answer ICMP or decrement TTL; never a ping target | [GCP subnets][gcp-subnets], [GCP MTU][gcp-mtu] |

- Treat VPC/VNet as provider implementations of routing, policy, naming and service reachability.
- Inventory CIDR overlap, transit, route propagation, private endpoints, egress/NAT, VPN or direct links, quotas and DNS views.
- Hybrid tunnels add overhead on top: take the smallest MTU on the path; clamp TCP MSS at the tunnel edge.
- Include egress cost, address exhaustion, control-plane outage, regional dependency and exit options. Never invent current prices.
- A private endpoint or route entry does not grant application authorisation.

## Containers

- Kubernetes model: every pod has a unique cluster-wide IP; pods reach each other without NAT. The CNI plugin implements it.
- A Service gives a stable virtual IP over EndpointSlices.
- NetworkPolicy works only if the CNI enforces it. Otherwise the API accepts policies that do nothing. Prove enforcement with a denied-path test.
- Gateway API succeeds Ingress. Choose one; record which controller owns it.
- Pod and service CIDRs must not overlap any on-prem, VPN or carrier range the cluster reaches.
- Native routing (pod CIDRs in BGP) removes encapsulation but puts pod routes in the fabric. Size the table; filter what is advertised.
- Add a service mesh only for a named application need: it adds certificates, resources and operations.
- Name owners for ingress, host firewall, load balancer and policy layers.

```text
Pod traffic paths (pod MTU = node MTU - encapsulation; a mismatch hangs large transfers)
           +-----+   +------+   +------------+   +-------------------------+   +------------+   +-----+
east-west: | pod |-->| veth |-->| node netns |-->| CNI: encap or BGP route |-->| other node |-->| pod |
           +-----+   +------+   +------------+   +-------------------------+   +------------+   +-----+
           +-----+   +-----------------+   +------------------------+   +----------+
egress:    | pod |-->| SNAT to node IP |-->| NAT gateway / firewall |-->| external |
           +-----+   +-----------------+   +------------------------+   +----------+
service:   client --> Service VIP (kube-proxy or eBPF DNAT) --> one EndpointSlice pod
```

## Patterns and anti-patterns

| Pattern                             | Use when                           | Anti-pattern                         | Why it fails                              |
| ----------------------------------- | ---------------------------------- | ------------------------------------ | ----------------------------------------- |
| Size spines for N-1                 | Any fabric carrying busy-hour load | Size for all spines up               | One spine loss saturates the rest         |
| Jumbo underlay, standard tenant MTU | VXLAN or Geneve overlays           | 1500 underlay with 1500 tenant       | Overlay drops or fragments full frames    |
| Reserved cloud supernet             | Before the first VPC               | Default VPC CIDRs                    | Overlap blocks peering and hybrid routing |
| Denied-path test per policy         | Kubernetes NetworkPolicy           | Trust the applied manifest           | CNI may ignore policy silently            |
| Native routing with filters         | Large clusters, no encap wanted    | Advertise every pod route unfiltered | Fabric table growth and leaks             |
| OOB on its own path and power       | Every fabric                       | Manage the fabric in-band only       | Fabric failure locks out its own repair   |

## Failure modes and tests

| Failure                    | Symptom                                  | Blast radius                       | Test that proves the design handles it                               |
| -------------------------- | ---------------------------------------- | ---------------------------------- | -------------------------------------------------------------------- |
| Spine loss                 | Higher latency and drops at busy hour    | Whole fabric capacity              | Fail a spine under load; compare throughput with the N-1 calculation |
| Leaf uplink loss           | Leaf runs at reduced uplink              | Hosts on that leaf                 | Fail one uplink under load; read per-uplink counters                 |
| Elephant flows on one path | One link saturated, others idle          | Storage, backup, migration traffic | Run parallel bulk transfers; check per-member load                   |
| Overlay MTU short          | Small packets work, large hang           | Every tenant flow                  | DF-set probes at full size across every overlay and hybrid tunnel    |
| Policy not enforced        | Denied traffic passes                    | Every namespace                    | Send a denied flow; it must fail                                     |
| Pod CIDR overlap           | Some on-prem hosts unreachable from pods | Cluster egress                     | Compare pod/service CIDRs with every reachable range                 |
| Cloud control-plane outage | Changes fail; running paths may stay     | Region or account                  | Tabletop the change freeze; confirm data paths persist               |
| Node drain                 | Brief loss for pods on the node          | Pods on that node                  | Drain under load; measure errors                                     |

Prove lost rack, host, link and control-plane recovery only where the requirements name those scenarios.

## Worked example

Question: does a leaf with 48 x 25G down and 8 x 100G up (2 per spine, 4 spines) survive one spine loss at busy hour?

Inputs (illustrative): measured busy-hour leaf-to-spine load 500 Gbit/s; target utilisation under failure 85%.

| Step              | Calculation                          | Result           |
| ----------------- | ------------------------------------ | ---------------- |
| Oversubscription  | 48 x 25 / (8 x 100) = 1200 / 800     | 1.5:1            |
| Normal uplink use | 500 / 800                            | 62.5%            |
| One spine lost    | Uplinks 8 - 2 = 6 x 100 = 600 Gbit/s | 1200 / 600 = 2:1 |
| Use at N-1        | 500 / 600                            | 83.3%, under 85% |
| Headroom at N-1   | 0.85 x 600 - 500                     | 10 Gbit/s        |

MTU for the overlay, with `dc-mtu.json` holding two paths (vxlan-ipv4 + dot1q-inner, required payload 1500):

| Command                | Underlay | Result                                                 |
| ---------------------- | -------- | ------------------------------------------------------ |
| `just mtu dc-mtu.json` | 1500     | exit 1: payload 1446, 54 short; raise underlay to 1554 |
| (same run)             | 9216     | payload 9162; TCP MSS 9122 (IPv4)                      |

- Verdict: N-1 passes with 10 Gbit/s headroom, which is thin. Re-measure monthly; add a spine above 80% normal use.
- MTU verdict: set underlay 9216; keep tenant MTU 1500; prove with DF-set probes at 1500 and 1501.

## Review checklist

- [ ] Oversubscription stated per leaf, normal and N-1, against measured busy-hour load.
- [ ] Underlay and tenant MTU recorded; `just mtu` run; DF probes planned on every overlay and hybrid tunnel.
- [ ] Elephant flows (storage, backup, migration) placed and tested.
- [ ] OOB management independent of the fabric and its power.
- [ ] Cloud supernet reserved; provider reserved addresses and MTU limits applied per path.
- [ ] Pod and service CIDRs checked against every reachable range.
- [ ] NetworkPolicy enforcement proven with a denied-path test.
- [ ] Owners named for ingress, LB, host firewall and policy layers.

## Further reading

URLs resolved 2026-10-29.

Fabric and overlay:

- [RFC 7938 BGP in Large-Scale Data Centers][rfc7938]: Clos topology, ECMP and failure behaviour at scale.
- [RFC 8365 EVPN Network Virtualization Overlay](https://www.rfc-editor.org/rfc/rfc8365.html): EVPN over VXLAN/Geneve and multihoming.
- [Linux kernel VXLAN](https://docs.kernel.org/networking/vxlan.html): how Linux VTEPs learn and forward.
- [FRRouting EVPN](https://docs.frrouting.org/en/latest/evpn.html): an open EVPN control-plane implementation.

Cloud:

- [AWS EC2 network MTU][aws-mtu]: jumbo frame limits per path type.
- [AWS VPC subnet sizing][aws-subnet]: reserved addresses and allowed sizes.
- [Azure Virtual Network FAQ][azure-faq]: address space, reserved addresses and VNet limits.
- [Azure TCP/IP performance tuning][azure-tune]: MTU, fragmentation and latency effects in Azure.
- [Google Cloud VPC MTU][gcp-mtu]: MTU ranges, mismatch behaviour and MSS clamping.
- [Google Cloud subnets][gcp-subnets]: primary and secondary ranges and unusable addresses.

Containers:

- [Kubernetes architecture](https://kubernetes.io/docs/concepts/architecture/): control plane and node components.
- [Kubernetes Services, Load Balancing and Networking](https://kubernetes.io/docs/concepts/services-networking/): network model and Service semantics.
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/): policy semantics and default-deny patterns.
- [Gateway API](https://gateway-api.sigs.k8s.io/): role-oriented ingress and its implementations.
- [CNI specification](https://www.cni.dev/docs/spec/): what a network plugin must and need not do.
- [Cilium routing concepts](https://docs.cilium.io/en/stable/network/concepts/routing/): encapsulation versus native routing in one widely used CNI.

[rfc7348]: https://www.rfc-editor.org/rfc/rfc7348.html
[rfc7938]: https://www.rfc-editor.org/rfc/rfc7938.html
[rfc8926]: https://www.rfc-editor.org/rfc/rfc8926.html
[aws-subnet]: https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
[aws-mtu]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/network_mtu.html
[azure-faq]: https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq
[azure-tune]: https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-tcpip-performance-tuning
[gcp-subnets]: https://cloud.google.com/vpc/docs/subnets
[gcp-mtu]: https://cloud.google.com/vpc/docs/mtu
