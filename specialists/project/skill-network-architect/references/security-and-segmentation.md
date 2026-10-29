---
Title: Network security, segmentation and trust
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Network security and segmentation decision rules, a trust-boundary pass that states attacker capabilities and non-capabilities, zone matrix, failure
  modes, a ranked abuse-path worked example and a review checklist.
---

# Network security, segmentation and trust

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Trust-boundary pass](#trust-boundary-pass)
- [Zone matrix](#zone-matrix)
- [Port and wireless access control](#port-and-wireless-access-control)
- [Zero-trust access to remote fleets](#zero-trust-access-to-remote-fleets)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: trust zones and boundaries, flow policy, enforcement points, port and wireless access control, L2 and edge protections, management access.
- Network owns flow policy and network enforcement; skill-systems-architect owns host and application enforcement and identity services.
- skill-nautobot may model policy intent if selected; skill-openwisp may carry telemetry. A policy record is not proof of enforcement.
- Compliance mapping (ISM, Essential Eight, CIS) is a separate evidence exercise. Never declare compliance from a design checklist.

## Decision rules

| Rule                                        | Value or threshold                                               | Evidence                                    |
| ------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------- |
| Network location is not trust               | Authenticate and authorise each session per request, from policy | VERIFIED_PRIMARY [NIST SP 800-207][sp800-207] (Aug 2020) |
| Segmentation still matters                  | It bounds blast radius when identity controls fail               | UNVERIFIED (judgement)                      |
| Segment by trust and flows                  | Never by department names alone                                  | UNVERIFIED (judgement)                      |
| Stateful devices on asymmetric paths        | Return traffic dropped; design symmetry or sync                  | UNVERIFIED (judgement)                      |
| EVPN fabrics                                | VRF per trust zone; inter-VRF policy at a firewall or border     | UNVERIFIED (common pattern)                 |
| Route leaking without a policy point        | A hole, not segmentation                                         | UNVERIFIED (judgement)                      |
| TLS settings for published services         | Follow BCP 195                                                   | VERIFIED_PRIMARY [RFC 9325][rfc9325]        |
| Port-based access control                   | IEEE 802.1X-2020 is current                                      | VERIFIED_PRIMARY [IEEE 802.1X-2020][dot1x]  |
| RADIUS attributes for 802.1X                | Informational guidance                                           | VERIFIED_PRIMARY [RFC 3580][rfc3580]        |
| Prefer EAP-TLS (certificates both sides)    | EAP-TLS 1.3 is Standards Track                                   | VERIFIED_PRIMARY [RFC 9190][rfc9190]        |
| Password EAP methods                        | Depend on server-certificate validation on every client          | UNVERIFIED (field observation)              |
| MAC authentication bypass                   | An identifier, not authentication; narrow profile                | UNVERIFIED (judgement)                      |
| AAA unreachable                             | Decide fail-closed or local critical policy; write it; test it   | UNVERIFIED (judgement)                      |
| RADIUS/UDP forgeable on path                | CVE-2024-3596; use TLS or a protected path                       | VERIFIED_PRIMARY [network-services](network-services.md) |
| RA-Guard on access                          | IPv4-only filters leave rogue RA open on dual stack              | VERIFIED_PRIMARY [RFC 6105][rfc6105]        |
| SAVI-DHCP source validation                 | Where the platform supports it                                   | VERIFIED_PRIMARY [RFC 7513][rfc7513]        |
| Edge anti-spoofing                          | Feasible-path uRPF; strict uRPF breaks multihomed asymmetry      | VERIFIED_PRIMARY [RFC 8704][rfc8704] (BCP 84) |
| Access ports                                | BPDU guard, storm control; loop protection on risky ports        | UNVERIFIED (judgement)                      |
| Management plane                            | Own VRF/VLAN, privileged gateway only, OOB where possible        | UNVERIFIED (judgement)                      |
| Remote sites dial out to the management hub | Record what breaks when the broker is down                       | UNVERIFIED (judgement)                      |
| Access-proxy agents dial out over reverse tunnels | Works behind firewalls and CGNAT; the proxy becomes a shared dependency | VERIFIED_PRIMARY [Teleport agents][tp-agents] |
| Access proxies and SSH forwards carry TCP   | UDP (SNMP, NTP) and ICMP probes run on the site box or need an L3 overlay | VERIFIED_PRIMARY [Teleport TCP apps][tp-tcp], [ssh(1)][ssh1] |
| Short-lived certificates expire by design   | Expiry of a shared access certificate fails every target at once | VERIFIED_PRIMARY [Teleport authentication][tp-auth] |
| Do not authorise remote sites by source IP  | Consumer and multi-carrier NAT addresses drift                   | UNVERIFIED (field observation)              |

- Also select among routed ACLs, stateful firewalls, host policy, proxies, identity-aware access, NAC and microsegmentation by control need.
- Model rule order, implicit defaults, state tables, NAT order, fail-open or fail-closed and HA state sync.
- Published services: TLS termination, certificate lifecycle, health checks, rate limits, DDoS response, backend restrictions.
- Encryption is not endpoint identity, data authorisation or protection from a malicious client.

## Trust-boundary pass

Run this for every site type. It is a short threat pass, not a full threat model.

1. List assets: data, control planes, credentials, management access, recovery copies.
2. List each trust boundary as a concrete edge. Per edge record protocol, authentication, encryption, filtering and rate limits.
3. State attacker capabilities per entry point. Then state what the attacker cannot do, and the control that makes it so.
4. Rank abuse paths by likelihood x impact, lowered for controls that are verified, not merely configured.
5. Ask one to three targeted questions where an answer would change the ranking.
6. Coverage check: every edge has a threat or an explicit "none found".

```text
Trust boundaries as concrete edges (:: = trust boundary; E1-E4 = edges to review)
  UNTRUSTED       ::        SITE ACCESS ZONE        ::        SERVICES ZONE
+------------+    ::    +----------------------+    ::    +--------------------+
| internet   |-E1-::--->| user, guest, IoT     |-E2-::--->| app and data tier  |
+------------+    ::    +----------------------+    ::    +--------------------+
                  ::                                ::
+------------+    ::    +----------------------+    ::    +--------------------+
| admin      |-E3-::--->| privileged gateway   |-E4-::--->| management plane   |
+------------+    ::    +----------------------+    ::    +--------------------+
E1: stateful edge, anti-spoofing, published services only
E2: 802.1X role or VRF, firewall between zones
E3: MFA, logged session
E4: dedicated management VRF, OOB where possible
```

| Entry point            | Attacker can                                             | Attacker cannot (and the control)                          |
| ---------------------- | -------------------------------------------------------- | ---------------------------------------------------------- |
| Guest SSID client      | Send any frame on its segment; scan what it can route to | Reach mgmt or users (VRF, no route, firewall deny, tested) |
| Guest SSID client      | Spoof its MAC; try rogue DHCP or RA                      | Serve other clients (client isolation, snooping, RA-Guard) |
| Compromised IoT device | Talk to its named peers and vendor list                  | Reach user devices (zone deny, tested both families)       |
| On-path in site LAN    | Read and alter RADIUS/UDP                                | Forge RADIUS inside TLS (RadSec or protected path)         |
| Internet               | Reach published services and the edge                    | Initiate to a CGNAT site (no inbound mapping)              |
| Stolen user credential | Use the user's app ports                                 | Reach management (privileged gateway with MFA)             |

- Never claim a "cannot" without the test that proves it. An untested control is a capability.
- Keep severity honest: an abuse path that needs a capability the attacker lacks drops in rank.

## Zone matrix

Fill one per site type with real flows. Every allow names an owner and a test; every deny has a test too.

| from to  | mgmt | user  | guest   | IoT/OT    | services  | internet    |
| -------- | ---- | ----- | ------- | --------- | --------- | ----------- |
| mgmt     | -    | deny  | deny    | admin (a) | admin (a) | updates     |
| user     | deny | -     | deny    | deny      | app ports | allow       |
| guest    | deny | deny  | isolate | deny      | DNS/DHCP  | allow       |
| IoT/OT   | deny | deny  | deny    | deny (b)  | named     | vendor list |
| services | logs | reply | reply   | reply     | -         | named       |

(a) admin = from the privileged gateway only, logged. (b) peer traffic only where the OT design needs it.

- Build a source, destination, service matrix with purpose, owner, direction, authentication, encryption, logging and expiry for temporary access.
- Cover management, user, guest, IoT/OT, workload, storage, backup and recovery planes. Each need not be a separate physical fabric.
- Backup and recovery: separate access and separate deletion authority.

## Port and wireless access control

```text
802.1X with EAP-TLS: who talks to whom
+------------+   EAPOL   +----------------+   RADIUS in TLS   +-------------+
| supplicant |<--------->| authenticator  |<----------------->| auth server |
| (client)   |           | (switch or AP) |                   | (RADIUS)    |
+------------+           +----------------+                   +-------------+
EAP-TLS: client and server certificates, carried end to end through the authenticator
Access-Accept + attributes --> port or SSID opens with a VLAN, ACL or role
later changes: CoA or Disconnect (RFC 5176)
```

## Zero-trust access to remote fleets

An identity-aware access proxy (Teleport, a similar broker, or SSH through a bastion) suits a fleet of sites behind carrier NAT: the agent on
each site box dials out, and people reach devices through the proxy with per-person identity and audit. It has limits that shape the design.

```text
ZERO-TRUST ACCESS TO A SITE BEHIND CGNAT: what crosses the proxy, and what must not depend on it
+--------+  TLS/mTLS  +------------------+  reverse tunnel  +-------------+  TCP only  +----------------+
| person |----------->| access proxy     |<-----------------| site box    |----------->| site devices   |
| or tool|            | (identity, audit)|   (site dials)   | agent       |            | (same IPs as   |
+--------+            +------------------+                  +-------------+            |  other sites)  |
                                                              |  UDP/ICMP run here     +----------------+
                                                              |  (SNMP, ping, NTP)
recovery: second hub or independent tunnel ----------------> site box   (never through the same proxy)
```

Each limit, its consequence, the design response and the evidence:

- **TCP transport.** Application access covers "any TCP-based application"; SSH `-L` and `-R` forward a TCP port or Unix socket, and `-D` is a SOCKS server.
  Central SNMP (UDP) and ping (ICMP) cannot cross, so a central ping check fails by construction. Run UDP and ICMP probes on the site box over a remote
  command and return the output, or add an address-translating L3 overlay. VERIFIED_PRIMARY [Teleport TCP apps][tp-tcp], [ssh(1)][ssh1]; no UDP or ICMP
  transport found in the Teleport application-access docs (explicit negative, 2026-10-29).
- **Repeated management addresses.** Cookie-cutter sites reuse one plan, so an IP alone names many devices. Key every record, metric and job on
  (site, IP) or a device ID, with one IPAM namespace or VRF per site. UNVERIFIED (design method).
- **Overlay to overlapping sites.** Two sites answer for the same address. Map each site range 1:1 onto a unique block (Linux NETMAP, nat table only)
  or use 4via6, and record the mapping in IPAM. VERIFIED_PRIMARY [iptables-extensions][ipt-ext] (NETMAP).
- **Shared proxy and certificates.** A proxy outage or certificate expiry looks like every site failing. Keep a recovery channel that does not use
  the proxy (a second hub, an independent tunnel, out-of-band power) and alarm on the shared dependency first. VERIFIED_PRIMARY
  [Teleport authentication][tp-auth] (certificates auto-expire); the response is UNVERIFIED (judgement).
- **Per-session cost over high RTT.** Each new session costs seconds over geostationary satellite. Reuse one connection per site and time-bound every
  remote call. UNVERIFIED (measured in one estate; see [remote-site fleet](remote-site-fleet.md#polling-over-geo-and-on-box-readers)).
- **A tunnel key is not a person.** WireGuard peers are keys (cryptokey routing), so tunnel logs cannot attribute actions to people. Attribute through
  the proxy or AAA on the device. VERIFIED_PRIMARY [WireGuard paper](https://www.wireguard.com/papers/wireguard.pdf).

- An unaudited back door (a reverse tunnel outside the proxy) defeats the audit the proxy exists for. Govern it as the documented recovery
  channel or remove it.
- Before declaring a site down, check the access path (certificate validity, proxy login, agent status) and try the second path. A fleet
  where most targets fail at the same moment with the same error is a shared-dependency failure until proven otherwise.

## Patterns and anti-patterns

| Pattern                            | Use when                 | Anti-pattern                     | Why it fails                                    |
| ---------------------------------- | ------------------------ | -------------------------------- | ----------------------------------------------- |
| Zones from trust and flows         | Every design             | Zones from org chart             | Same-trust devices split; different trust mixed |
| VRF per zone, policy at a firewall | EVPN or multi-VRF sites  | Route leaks between VRFs         | Traffic bypasses every policy point             |
| EAP-TLS with validated server cert | Managed clients          | PEAP without server validation   | Credentials captured by a rogue AP              |
| Narrow profile for MAB devices     | Cameras, printers, OT    | MAB into the user zone           | A spoofed MAC gets user access                  |
| Dual-stack first-hop protection    | Any IPv6-enabled segment | IPv4-only snooping and DAI       | Rogue RA hijacks IPv6 traffic                   |
| Deny tests alongside allow tests   | Every change             | Test only that wanted flows work | Holes ship unnoticed                            |
| Dial-out management                | Remote sites             | Inbound management exposed       | Exposed attack surface; fails behind CGNAT      |
| UDP and ICMP probes on the site box | TCP-only access proxy   | Central SNMP or ping through it  | The proxy cannot carry them                     |
| Recovery path independent of proxy | Proxy-managed fleets    | One proxy for access and recovery | Proxy or certificate fault strands every site  |
| Authenticated site sessions        | Sites on NAT or multi-carrier WAN | Source-IP allowlists       | Address drifts; site breaks silently           |

## Failure modes and tests

| Failure                                   | Symptom                         | Blast radius            | Test that proves the design handles it             |
| ----------------------------------------- | ------------------------------- | ----------------------- | -------------------------------------------------- |
| Unintended route leak between VRFs        | Cross-zone reach without policy | Both zones              | Denied-flow test from each zone, IPv4 and IPv6     |
| Asymmetric path through stateful firewall | Replies dropped                 | Flows through that pair | Fail one path; retest established and new sessions |
| AAA outage                                | Nobody joins, or everyone joins | Site                    | Cut AAA; verify the written fail mode              |
| Rogue RA or DHCP                          | Clients get attacker gateway    | Segment                 | Inject in lab; RA-Guard and snooping drop it       |
| Strict uRPF on multihomed edge            | Legitimate traffic dropped      | Multihomed prefixes     | Fail one upstream; check drops                     |
| Management reachable from user zone       | Admin surface exposed           | All devices             | Scan management prefixes from user and guest       |
| Policy change locks out admins            | Loss of management              | Site or fleet           | Keep OOB and old policy; canary smallest scope     |
| Firewall HA failover without state sync   | Sessions reset                  | All stateful flows      | Fail the active unit under load                    |
| Access certificate or proxy expiry        | Most sites fail at once         | Whole fleet (access)    | Let a test certificate expire; one shared alarm fires |
| Site NAT address drifts                   | Allowlisted service refuses site | One site                | Move a test site to another egress; service still works |

Change rules: precompute the semantic rule diff, keep old policy and OOB access, canary the smallest scope. Test from real sources (wired, each SSID, VPN, each site type), both families, new and
established sessions, DNS, NAT and return path. Log without capturing credentials or needless payload. Never disable host-key checks or bypass authentication to make automation pass.

## Worked example

Question: which guest-SSID abuse path ranks first at a branch, and how many tests does its zone matrix need?

Scale: likelihood and impact 1-5; score = L x I; subtract 1 per verified control (illustrative method).

| Abuse path                                        | L   | I   | Raw | Verified controls               | Score |
| ------------------------------------------------- | --- | --- | --- | ------------------------------- | ----- |
| Guest client sends rogue RA on dual-stack segment | 3   | 4   | 12  | Client isolation (1)            | 11    |
| Guest client reaches management prefixes          | 2   | 5   | 10  | VRF + firewall deny, tested (2) | 8     |
| Guest client exhausts DHCP pool                   | 3   | 2   | 6   | None                            | 6     |

- Rank 1 is the rogue RA: RA-Guard is configured but untested, so it earns no deduction. Test it, then rescore.
- Targeted question: is IPv6 enabled on the guest segment? If not, rank 1 drops out.
- Test count: 5 sources x 6 destinations = 30 cells, minus 3 "-" cells = 27 flows; x 2 families = 54 tests.
- Each of the 3 guest source contexts (2 SSIDs, captive portal) repeats the guest row: 6 x 2 x 3 = 36 guest tests.

## Review checklist

- [ ] Trust boundaries listed as edges with protocol, authentication, encryption and filtering.
- [ ] Attacker capabilities and non-capabilities stated per entry point, each "cannot" backed by a test.
- [ ] Abuse paths ranked; deductions only for verified controls.
- [ ] Zone matrix filled per site type; every allow and deny has an owner and a test.
- [ ] 802.1X method, server-certificate validation and AAA-down behaviour decided and tested.
- [ ] First-hop protections cover IPv4 and IPv6.
- [ ] Management reachable only via the privileged gateway or OOB.
- [ ] Access proxy: TCP-only limit planned for (on-box UDP and ICMP probes); identity keyed on (site, IP); recovery path independent of the proxy; certificate expiry alarmed.
- [ ] Rule change has a semantic diff, canary scope, rollback and OOB access.
- [ ] No compliance claim made from this checklist.

## Further reading

Zero trust and architecture:

- [NIST SP 800-207][sp800-207]: zero trust tenets and logical components (PDP/PEP).
- [NIST SP 800-207A](https://csrc.nist.gov/pubs/sp/800/207/a/final): identity-tier policy in cloud-native, multi-location systems.
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model): stage a zero trust roadmap by pillar.
- [NIST SP 800-41 Rev. 1](https://csrc.nist.gov/pubs/sp/800/41/r1/final): firewall policy design (2009, still the NIST firewall guide).

Access control:

- [IEEE 802.1X-2020][dot1x]: port-based access control and MACsec key agreement.
- [RFC 9190][rfc9190] and [RFC 3580][rfc3580]: EAP-TLS 1.3 and RADIUS attributes for 802.1X.
- [RFC 5176](https://www.rfc-editor.org/rfc/rfc5176.html): CoA and Disconnect when policy must change mid-session.

Remote fleet access:

- [Teleport agent architecture][tp-agents]: reverse tunnels from agents to the proxy.
- [Teleport authentication][tp-auth]: short-lived certificates and their expiry.
- [OpenSSH ssh(1)][ssh1]: what `-L`, `-R`, `-D` and `-w` forward.

Edge and first-hop:

- [RFC 6105][rfc6105], [RFC 7513][rfc7513] and [RFC 8704][rfc8704]: RA-Guard, SAVI and uRPF.
- [RFC 9325][rfc9325]: current TLS and DTLS configuration guidance.

Controls frameworks:

- [Australian ISM][ism]: Australian Government network and gateway controls.
- [CIS Controls v8.1](https://www.cisecurity.org/controls/v8-1): a prioritised control set to map designs against.

[sp800-207]: https://csrc.nist.gov/pubs/sp/800/207/final
[dot1x]: https://standards.ieee.org/ieee/802.1X/7345/
[rfc3580]: https://www.rfc-editor.org/rfc/rfc3580.html
[rfc6105]: https://www.rfc-editor.org/rfc/rfc6105.html
[rfc7513]: https://www.rfc-editor.org/rfc/rfc7513.html
[rfc8704]: https://www.rfc-editor.org/rfc/rfc8704.html
[rfc9190]: https://www.rfc-editor.org/rfc/rfc9190.html
[rfc9325]: https://www.rfc-editor.org/rfc/rfc9325.html
[ism]: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism
[tp-agents]: https://goteleport.com/docs/reference/architecture/agents/
[tp-tcp]: https://goteleport.com/docs/enroll-resources/application-access/protect-apps/tcp/
[tp-auth]: https://goteleport.com/docs/reference/architecture/authentication/
[ssh1]: https://man.openbsd.org/ssh.1
[ipt-ext]: https://ipset.netfilter.org/iptables-extensions.man.html
