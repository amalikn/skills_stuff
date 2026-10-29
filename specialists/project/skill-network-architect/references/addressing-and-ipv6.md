---
Title: Addressing, IPAM and IPv6
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: Addressing, IPAM and IPv6 decision rules, patterns, failure modes, a checked site-plan worked example and a review checklist.
---

# Addressing, IPAM and IPv6

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Allocation hierarchy](#allocation-hierarchy)
- [IPv6 operation and translation](#ipv6-operation-and-translation)
- [Overlap and migration](#overlap-and-migration)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: allocation hierarchy, routing scopes (VRFs), summarisation, special-purpose space, IPv6 sizing, translation and overlap handling.
- Hands to [routing-and-switching](routing-and-switching.md): summaries and prefix ownership; to [network-services](network-services.md): DHCP scopes, RA and reverse DNS.
- Hands to [security-and-segmentation](security-and-segmentation.md): the IPv6 firewall boundary; to IPAM (skill-nautobot if selected): the authoritative record.
- Form: [ip-addressing-plan template](../templates/ip-addressing-plan.md).

## Decision rules

Evidence: VERIFIED_PRIMARY rows link the source (checked 2026-10-29). UNVERIFIED rows are architecture judgement, not standards facts.

| Rule                                                   | Value or threshold                                                  | Evidence                            |
| ------------------------------------------------------ | ------------------------------------------------------------------- | ----------------------------------- |
| RFC 1918 private space                                 | 10/8, 172.16/12, 192.168/16                                         | VERIFIED_PRIMARY [RFC 1918][rfc1918] |
| Avoid merger hot spots for anything that interconnects | 10/8 and 192.168.0/24-192.168.1/24 collide most                     | UNVERIFIED (observation)            |
| 100.64.0.0/10 is CGNAT Shared Address Space            | Not RFC 1918; never for enterprise LANs; carriers and clouds use it | VERIFIED_PRIMARY [RFC 6598][rfc6598] |
| Documentation prefixes only in examples                | 192.0.2/24, 198.51.100/24, 203.0.113/24, 2001:db8::/32, 3fff::/20   | VERIFIED_PRIMARY [RFC 9637][rfc9637] |
| Bogon filters from the IANA registries                 | Generate, never type from memory                                    | IANA [v4][iana4], [v6][iana6] registries (RFC 6890) |
| ULA uses fd00::/8 plus a random 40-bit Global ID       | fd00::/48 or sequential IDs defeat merger safety; ULA is not GUA    | VERIFIED_PRIMARY [RFC 4193][rfc4193] |
| One /64 per L2 segment                                 | SLAAC needs a 64-bit interface ID; longer prefixes break it         | VERIFIED_PRIMARY [RFC 7421][rfc7421] |
| End site gets /48 or /56                               | Persistent prefixes; RIPE-690 discourages longer than /56           | VERIFIED_PRIMARY [RFC 6177][rfc6177], [RIPE-690][ripe690] |
| Inter-router link /127                                 | Reserve the containing /64 per link                                 | VERIFIED_PRIMARY [RFC 6164][rfc6164] |
| GUA on WAN links                                       | Helps troubleshooting                                               | VERIFIED_PRIMARY [RIPE-690][ripe690] |
| IPv4 point-to-point /31                                | No broadcast-host rule on p2p                                       | VERIFIED_PRIMARY [RFC 3021][rfc3021] |
| Hosts hold many IPv6 addresses                         | Identify by prefix or identity, never one address                   | VERIFIED_PRIMARY [RFC 7934][rfc7934] |
| Routers do not fragment IPv6                           | Minimum link MTU 1280                                               | VERIFIED_PRIMARY [RFC 8200][rfc8200] |
| Nibble-aligned IPv6 boundaries                         | /44, /48, /52, /56, /60, /64 for clean reverse DNS                  | UNVERIFIED (judgement)              |
| Same prefix in two VRFs is valid                       | Until the VRFs must interconnect                                    | UNVERIFIED (judgement)              |

- Keep allocations, pools and endpoint assignments separate. A pool nested in its allocation is not a duplicate subnet.
- Make every routing scope explicit; decide public ownership, private ranges, CGNAT exposure and IPv6 allocation constraints.

## Allocation hierarchy

```text
IPv6 and IPv4 allocation hierarchy (one level summarises the next)
provider or RIR block (e.g. /32 or /29)
  +-- region or function ............. /40 - /44
       +-- site ...................... /48 (RFC 6177, RIPE-690: /48 or /56 per end site)
            +-- zone or VRF .......... /52 - /56
                 +-- segment ......... /64 (one per L2 segment; SLAAC needs it)
                 +-- p2p link ........ /127 configured, /64 reserved (RFC 6164)
                 +-- loopbacks ....... /128 from one dedicated /64
IPv4 mirror: site /16-/22 from RFC 1918; segment = measured hosts + growth;
             p2p /31 (RFC 3021); loopbacks /32 from a dedicated block
```

## IPv6 operation and translation

- Record prefix source, delegated sizes, address formation, RA, DHCPv6, DNS, ND, ICMPv6 and default routing.
- Test both families for security and reachability. Happy Eyeballs hides a broken family from users, not from monitoring.
- Never block all ICMPv6: Packet Too Big, ND and RA are required. Protect access segments against rogue RAs.
- IPv6 has no implicit NAT boundary. The stateful firewall is the boundary; write it explicitly, not by copying IPv4 NAT rules.
- Test DNS answer selection, path MTU and application binding per family.

| Translation fact               | Value                                                                             | Evidence                            |
| ------------------------------ | --------------------------------------------------------------------------------- | ----------------------------------- |
| NAT64 plus DNS64               | IPv6-only clients reach IPv4-only services                                        | VERIFIED_PRIMARY [RFC 6146][rfc6146], [RFC 6147][rfc6147] |
| Well-known NAT64 prefix        | 64:ff9b::/96                                                                      | VERIFIED_PRIMARY [RFC 6052][rfc6052] |
| Local-use translator prefix    | 64:ff9b:1::/48                                                                    | VERIFIED_PRIMARY [RFC 8215][rfc8215] |
| Clients learn the NAT64 prefix | PREF64 in RA, or DNS discovery                                                    | VERIFIED_PRIMARY [RFC 8781][rfc8781], [RFC 7050][rfc7050] |
| IPv6-Only Preferred            | DHCPv4 option 108; capable hosts drop IPv4, legacy keep it                        | VERIFIED_PRIMARY [RFC 8925][rfc8925] |
| DNS64 limits                   | Breaks client DNSSEC validation; fails for IPv4 literals; 464XLAT covers literals | UNVERIFIED (judgement)              |

## Overlap and migration

- Before joining two offices that share a prefix, list the actually conflicting endpoints and dependencies.
- Compare: renumbering, isolated routing contexts, translated service prefixes, application gateways.
- Translation changes DNS, logging, ACLs and identity. A VPN encrypts; it does not remove duplicate addressing.
- Renumbering: stage secondary addresses, update reservations, DNS, rules and monitoring, keep the old path until acceptance.
- Lower DNS TTLs before renumbering. Keep current internet defaults unless the approved plan changes them.

```text
Overlapping offices joined through translated prefixes
+-----------------------+   +---------------------+
| office A 10.20.0.0/16 |-->| NAT to 10.91.0.0/16 |---+
+-----------------------+   +---------------------+   |   +------------------------------------------+
                                                      +-->| tunnel routes only 10.91/16 and 10.92/16 |
+-----------------------+   +---------------------+   |   +------------------------------------------+
| office B 10.20.0.0/16 |-->| NAT to 10.92.0.0/16 |---+
+-----------------------+   +---------------------+
cross-site DNS must answer translated addresses; logs show translated sources
alternative: renumber one office in stages, then remove the NAT
```

## Patterns and anti-patterns

| Pattern                        | Use when                     | Anti-pattern                       | Why it fails                                 |
| ------------------------------ | ---------------------------- | ---------------------------------- | -------------------------------------------- |
| Hierarchical site blocks       | Sites summarise upstream     | Allocate in request order          | No summary; every site is a separate route   |
| Random ULA Global ID           | Internal IPv6 that may merge | fd00::/48 or sequential IDs        | Two merged sites collide                     |
| Persistent delegated prefix    | Every end site               | Dynamic prefix from the ISP        | Renumbers every segment, rule and DNS record |
| /64 per segment, /127 per link | All IPv6                     | /120 host segments to "save space" | SLAAC and host features break                |
| Explicit IPv6 firewall         | Dual stack                   | Assume NAT protects IPv6           | No NAT exists; IPv6 is wide open             |
| Reserved cloud supernet        | Before the first VPC         | Pick VPC CIDRs ad hoc              | Overlap blocks peering later                 |
| Translation as a bridge        | Short merger window          | Permanent double NAT               | Logs, ACLs and DNS stay confused             |

## Failure modes and tests

| Failure                            | Symptom                                       | Blast radius              | Test that proves the design handles it                    |
| ---------------------------------- | --------------------------------------------- | ------------------------- | --------------------------------------------------------- |
| Overlap inside one routing scope   | Intermittent reachability, wrong host answers | Both segments             | `just ip-plan` exit 0 on the concrete segments            |
| Collision with carrier CGNAT range | Remote site cannot reach some hosts           | Site behind that carrier  | List upstream addresses per site; check against 100.64/10 |
| Rogue RA on access segment         | Hosts take a bogus gateway                    | Whole segment             | Inject an RA in lab; RA-Guard drops it                    |
| ICMPv6 Too Big filtered            | Large IPv6 transfers hang                     | Every tunnelled IPv6 flow | Full-size DF probe; confirm PTB reaches sender            |
| Delegated prefix changes           | Rules and DNS point at old prefix             | Whole site                | Bounce the WAN; compare prefix before and after           |
| DHCP scope exhaustion              | New clients get no address                    | Segment                   | Size pool to peak plus growth; alarm at a set fill        |
| IPv6 path broken, IPv4 fine        | Users fine, monitoring fails                  | Whole family              | Monitor each family separately                            |

## Worked example

Question: does a four-segment site plan overlap anything, and is every gateway inside its segment?

Input `site-plan.json` (documentation prefixes, illustrative):

```json
{"schema_version": 1, "segments": [
 {"id": "s12-mgmt", "scope": "corp", "cidr": "10.12.0.0/26", "gateway": "10.12.0.1"},
 {"id": "s12-users", "scope": "corp", "cidr": "10.12.1.0/24", "gateway": "10.12.1.1"},
 {"id": "s12-iot", "scope": "corp", "cidr": "10.12.2.0/25", "gateway": "10.12.2.1"},
 {"id": "s12-wan-p2p", "scope": "corp", "cidr": "10.12.255.0/31", "gateway": "10.12.255.1"},
 {"id": "s12-users-v6", "scope": "corp", "cidr": "2001:db8:12:10::/64", "gateway": "2001:db8:12:10::1"},
 {"id": "s12-guest", "scope": "guest", "cidr": "10.12.1.0/24", "gateway": "10.12.1.1"},
 {"id": "s12-voice", "scope": "corp", "cidr": "10.12.1.128/25"}]}
```

| Run | Command                                                  | Result                                            |
| --- | -------------------------------------------------------- | ------------------------------------------------- |
| 1   | `just ip-plan site-plan.json`                            | exit 1: `corp IPv4: s12-voice overlaps s12-users` |
| 2   | Move s12-voice to 10.12.3.0/25, gateway 10.12.3.1; rerun | exit 0, 7 segments, 0.0002 s                      |

- s12-guest reuses 10.12.1.0/24 without a finding: it sits in scope `guest`. That is valid only while guest never routes to corp.
- The /31 gateway passes: the checker applies no broadcast rule to /31.
- Sizing check: users /24 = 254 hosts. Peak 180 devices x 1.3 growth = 234; fits with 20 spare.
- Not proven by the run: hierarchy, pools, DHCP, DNS, route leaks. Review those by hand.

## Review checklist

- [ ] Hierarchy summarises at every level; site blocks can be withdrawn as one prefix.
- [ ] Every routing scope is named; intentional reuse sits in separate scopes.
- [ ] No enterprise use of 100.64.0.0/10; carrier and cloud ranges checked for collision.
- [ ] Examples use documentation prefixes only.
- [ ] IPv6: /48 or /56 per site, /64 per segment, /127 per link, persistent prefix.
- [ ] ULA, if used, has a random Global ID.
- [ ] IPv6 firewall boundary is explicit; ICMPv6 PTB, ND and RA permitted; RA-Guard on access.
- [ ] `just ip-plan` exit 0 on the concrete segments, with output attached.
- [ ] Overlap plan names translation or renumbering, with DNS and logging consequences.

## Further reading

URLs resolved 2026-10-29.

Planning and allocation:

- [RIPE-690 IPv6 prefix assignment for end-users][ripe690]: /48 versus /56, persistent prefixes and WAN link numbering.
- [RFC 6177 IPv6 Address Assignment to End Sites][rfc6177]: why end sites get many /64s.
- [RFC 7421 Analysis of the 64-bit Boundary][rfc7421]: what breaks when a segment is not a /64.
- [RFC 7934 Host Address Availability][rfc7934]: why hosts need many addresses and what that means for controls.

Special-purpose space:

- [IANA IPv4 special-purpose registry](https://www.iana.org/assignments/iana-ipv4-special-registry/): authoritative bogon and reserved list.
- [IANA IPv6 special-purpose registry](https://www.iana.org/assignments/iana-ipv6-special-registry/): IPv6 equivalent, including NAT64 and documentation.
- [RFC 4193 Unique Local IPv6 Unicast Addresses][rfc4193]: Global ID algorithm and ULA routing rules.

Transition:

- [RFC 6146 Stateful NAT64][rfc6146] and [RFC 6147 DNS64][rfc6147]: translation behaviour and DNS synthesis limits.
- [RFC 8925 IPv6-Only Preferred Option for DHCPv4][rfc8925]: running IPv6-mostly segments.
- [Linux kernel IP sysctl](https://docs.kernel.org/networking/ip-sysctl.html): host RA, temporary address and ND behaviour.

[rfc1918]: https://www.rfc-editor.org/rfc/rfc1918.html [rfc3021]: https://www.rfc-editor.org/rfc/rfc3021.html [rfc4193]: https://www.rfc-editor.org/rfc/rfc4193.html [rfc6052]:
https://www.rfc-editor.org/rfc/rfc6052.html [rfc6146]: https://www.rfc-editor.org/rfc/rfc6146.html [rfc6147]: https://www.rfc-editor.org/rfc/rfc6147.html [rfc6164]:
https://www.rfc-editor.org/rfc/rfc6164.html [rfc6177]: https://www.rfc-editor.org/rfc/rfc6177.html [rfc6598]: https://www.rfc-editor.org/rfc/rfc6598.html [rfc6890]:
https://www.rfc-editor.org/rfc/rfc6890.html [rfc7050]: https://www.rfc-editor.org/rfc/rfc7050.html [rfc7421]: https://www.rfc-editor.org/rfc/rfc7421.html [rfc7934]:
https://www.rfc-editor.org/rfc/rfc7934.html [rfc8200]: https://www.rfc-editor.org/rfc/rfc8200.html [rfc8215]: https://www.rfc-editor.org/rfc/rfc8215.html [rfc8781]:
https://www.rfc-editor.org/rfc/rfc8781.html [rfc8925]: https://www.rfc-editor.org/rfc/rfc8925.html [rfc9637]: https://www.rfc-editor.org/rfc/rfc9637.html [ripe690]:
https://www.ripe.net/publications/docs/ripe-690/
