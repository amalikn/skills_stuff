---
Title: Voice and SIP
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  SIP trunk and voice platform architecture for an Australian provider: trunks and carrier redundancy, ATA and UNI-V access, codecs and bandwidth, emergency calls
  (000, 112, 106) and the ACMA determination, caller ID, number porting, call-record reconciliation, SIP security and testing obligations.
---

# Voice and SIP

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [SIP trunk architecture](#sip-trunk-architecture)
- [Carrier redundancy and failover](#carrier-redundancy-and-failover)
- [Access, ATA and UNI-V](#access-ata-and-uni-v)
- [Codecs and bandwidth](#codecs-and-bandwidth)
- [Emergency calls](#emergency-calls)
- [CLI and caller ID](#cli-and-caller-id)
- [Number porting](#number-porting)
- [Call-record reconciliation](#call-record-reconciliation)
- [SIP security](#sip-security)
- [Testing obligations](#testing-obligations)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Sources](#sources)
- [Further reading](#further-reading)

## Scope

- Decides: trunk topology (direct to PBX, via a session border controller or a central relay), carrier split and failover, codec and DTMF baseline, trunk dimensioning, emergency-call and CLI handling
  on every path, porting and number data, and the tests that must pass before a path carries traffic.
- Requirements to capture: inbound and outbound carriers, number ranges held, concurrent calls at busy hour, grade of service, sites and access types, emergency-call location data, fraud tolerance,
  recording and call-record needs.
- Hands to [australian-access-networks](australian-access-networks.md) (TC-1, UNI-V, copper exit), [service-provider-edge](service-provider-edge.md) (CGNAT and MTU for voice subscribers),
  [security-and-segmentation](security-and-segmentation.md) (SBC placement), [capacity-and-resilience](capacity-and-resilience.md) (availability arithmetic).
- Hands to skill-ifa for call-record and carrier-bill reconciliation, to skill-systems-architect for PBX hosts, databases and upgrades, and to the platform pack for device facts.
- Legal duties below are pointers to the instrument with its compilation date. They are not legal advice; confirm the current compilation before a design decision.

## Decision rules

| Rule | Value or threshold | Evidence |
| --- | --- | --- |
| A CSP with an emergency telephone service gives access to 000 (112 on mobile) | Every service, free, whether or not a number is issued | VERIFIED_PRIMARY [ECS Determination][ecsd] s14, s15, s33 |
| 106 (text relay) must reach the 106 call person on a standard telephone service | Arrangements for TTY and similar devices | VERIFIED_PRIMARY [ECS Determination][ecsd] s9, s17 |
| The service must send the calling number and the most precise location available | Automatically, at call time, as far as practicable | VERIFIED_PRIMARY [ECS Determination][ecsd] s23 |
| Networks carrying emergency calls need diversity and redundancy | Or written arrangements with another provider to carry them | VERIFIED_PRIMARY [ECS Determination][ecsd] s11 |
| Written arrangements with every carrier the CSP relies on | Delivery procedures, 106 arrangements, upstream agreements | VERIFIED_PRIMARY [ECS Determination][ecsd] s9 |
| Welfare check after a major outage on users with failed emergency calls | Linked to the Customer Communications for Outages Standard 2024 | VERIFIED_PRIMARY [ECS Determination][ecsd] s28 |
| 24x7 contact registered with the emergency call person; update by next business day | A person always answers | VERIFIED_PRIMARY [ECS Determination][ecsd] s26 |
| Service address goes to the IPND | Required by Telecommunications Act Schedule 2 Part 4 | VERIFIED_PRIMARY (definition in [ECS Determination][ecsd] s6) |
| Number portability is a customer right; CSPs need the technical capability | Telecommunications Numbering Plan 2025, Chapter 10 | VERIFIED_PRIMARY [Numbering Plan 2025][np2025] s103 |
| Geographic number porting process | Local Number Portability code C540:2023 | VERIFIED_SECONDARY [C540][c540] |
| Scam-call code obliges CLI checks and spoofing reports | C661:2022 Reducing Scam Calls and Scam SMs | VERIFIED_SECONDARY [ACMA caller ID][acma-cli] |
| G.711 is 64 kbit/s; RTP/UDP/IPv4 adds 40 bytes per packet | 80 kbit/s IP at 20 ms; 87.2 kbit/s on Ethernet | VERIFIED_PRIMARY [RFC 3551][rfc3551]; arithmetic derived |
| DTMF as RTP telephone-events | Not in-band audio over compressed codecs | VERIFIED_PRIMARY [RFC 4733][rfc4733] |
| Locate SIP servers with DNS (NAPTR, SRV, A) for failover | Several SRV targets with priorities | VERIFIED_PRIMARY [RFC 3263][rfc3263] |

## SIP trunk architecture

```text
Voice core: one policy point, two carriers, every path proven for 000 and CLI
                                       +---------------+   inbound numbers   +-----------+
  customers' PBXs / ATAs --+           |  SBC or relay |<--------------------| carrier A |
                           +---------->|  pair (HA):   |-------------------->| (in/out)  |
  staff PBX ---------------+           |  limits, CLI, |                     +-----------+
                                       |  CDR, fraud   |-------------------->+-----------+
                                       +---------------+   outbound backup   | carrier B |
                                              |                              | (in/out)  |
                                              v                              +-----------+
                                       call records -> billing and reconciliation
```

- Put policy (concurrent-call limits, CLI rules, fraud controls, call records) at one point, and make that point a redundant pair with a peer to each carrier. A shared relay with a peer to one carrier
  turns one carrier fault into a total outbound outage. UNVERIFIED (judgement from incidents).
- IP-authenticated static trunks avoid a registration dependency; a liveness probe (SIP OPTIONS) detects a dead peer. Registration-based trunks need [RFC 5626][rfc5626] keepalive behaviour behind NAT.
- Keep the number-to-service mapping in a database (it is also the DID inventory for billing), not in static dialplan.
- Classify the SBC or relay by function ([RFC 7092][rfc7092] B2BUA taxonomy): signalling-only relays and media-terminating SBCs fail differently and scale differently.
- Plan platform lifecycle: a PBX module removed upstream (for example Asterisk chan_sip, removed in Asterisk 21) forces a migration under time pressure. VERIFIED_SECONDARY [Asterisk chan_sip
  removal][ast-chansip].

## Carrier redundancy and failover

- Separate inbound and outbound carriers give partial resilience only: if outbound fails, inbound still works, but no outbound route remains. Design a tested outbound path through the second carrier.
  UNVERIFIED (judgement).
- Keep carrier selection in one parameter with a documented, rollback-first runbook, and know every call context it changes (outbound, forwarding, staff).
- Every failover path carries the same policy as the primary: channel limits, CLI handling, call-record headers, fraud controls, emergency routing.
- Inbound resilience depends on the number-holding carrier: ask how it reroutes to an alternate destination and test it.
- Emergency calls must still route when the primary carrier fails: the determination requires diversity and redundancy, or a written arrangement with another provider. VERIFIED_PRIMARY [ECS
  Determination][ecsd] s11.

## Access, ATA and UNI-V

- On nbn Fibre the UNI-V is an analogue port on the NTD with an inbuilt ATA; it gets a TC-1 allocation automatically and needs integration testing between the RSP voice platform and nbn before
  deployment. Elsewhere voice uses an RSP-supplied ATA or IP phone on UNI-D or UNI-DSL, in any traffic class. VERIFIED_PRIMARY [nbn PTS][nbn-pts] s2.1.2.
- Order TC-1 for voice where the access network offers it; DSCP marking alone on TC-4 does not create priority across the wholesale network
  ([australian-access-networks](australian-access-networks.md#nbn-access-model)).
- Powering: the ATA, NTD and router need mains power. Life-safety lines need battery backup or a mobile path. UNVERIFIED as a rule; the determination treats a mains outage at the premises as a matter
  beyond the provider's control (VERIFIED_PRIMARY [ECS Determination][ecsd] s12 note).
- Behind CGNAT, SIP from an ATA needs keepalives shorter than the mapping timeout or an outbound-connection mechanism ([RFC 5626][rfc5626]).

## Codecs and bandwidth

| Codec, 20 ms packets | Payload | IP (+40 B) | Ethernet (+18 B) | + PPPoE (+8 B) | Basis |
| --- | --- | --- | --- | --- | --- |
| G.711 A-law (PCMA) | 160 B | 80.0 kbit/s | 87.2 kbit/s | 90.4 kbit/s | [RFC 3551][rfc3551] |
| G.729 | 20 B | 24.0 kbit/s | 31.2 kbit/s | 34.4 kbit/s | [RFC 3551][rfc3551] |

- Per direction, per call. Add 4 bytes per VLAN tag on the wire. Arithmetic derived from header sizes ([RFC 3550][rfc3550] RTP 12 B, UDP 8 B, IPv4 20 B).
- Australian interconnect commonly uses G.711 A-law with RFC 4733 telephone-events. USER_STATED (carrier interconnect practice); confirm in each carrier's specification.
- Fax and modem-based devices (alarms, EFTPOS, lifts) need G.711 without compression or T.38; test each device class.
- Mark media EF and signalling CS3 or AF31 per [RFC 4594][rfc4594]; marking only helps on links that honour it.

## Emergency calls

The Telecommunications (Emergency Call Service) Determination 2019 binds carriers and carriage service providers. Read 2026-10-29: compilation No. 4, in force 2025-11-01, including amendments to
2025-10. VERIFIED_PRIMARY [ECS Determination][ecsd].

| Duty (section) | What it means for the design |
| --- | --- |
| Written arrangements (s9) | Documented emergency routing per carrier, including 106 and any satellite service |
| Diversity and redundancy (s11) | Emergency calls survive a single carrier, trunk or relay failure, or a written arrangement covers it |
| Access to 000 and 112 (s14, s15) | Every path, including failover paths and unregistered or suspended numbers (subject to the s12 exceptions) |
| 106 access (s17) | Text-relay calls reach the 106 call person |
| Carriage to the termination point (s19, s21) | Route on own network or another; highest priority within own network for 000 and 112 |
| Calling number and location (s23) | CLI must not be stripped or replaced on emergency calls; send the most precise location available |
| Contact details (s26) | A 24x7 contact with the emergency call person; changes notified by next business day |
| Welfare checks (s28) | After a major outage, find users whose emergency calls failed and check on them; call records must make that possible |
| Free of charge (s33) | No rating, no credit block, no barring of emergency numbers by plan |
| Non-genuine calls (s31) | Monitor 000/112 volumes 24x7 and have a documented stop process |

- Carrier testing duties in Part 5 (s75) apply to carriers and mobile networks; a CSP has no explicit test duty in Part 2, but cannot show compliance with s11, s15 and s23 without testing. UNVERIFIED
  as an obligation on CSPs; strongly recommended.
- Location for a fixed VoIP service comes from the IPND service address; a nomadic or moved service breaks that link. Keep IPND data current and record where a service may move.
- Exempt satellite services must notify the customer in writing that emergency calls are not possible (s13).

## CLI and caller ID

- Present only numbers the customer holds or is authorised to use. Use P-Asserted-Identity between trusted networks ([RFC 3325][rfc3325]) and a privacy flag for withheld numbers; never pass
  customer-supplied CLI to a carrier unchecked. VERIFIED_PRIMARY for the mechanism.
- The scam-call code (C661:2022) requires providers to identify, trace and block scam calls and to report CLI spoofing upstream with a copy to the ACMA. VERIFIED_SECONDARY [ACMA caller ID][acma-cli]
  and ACMA enforcement reports.
- Cryptographic caller identity ([RFC 8224][rfc8224]) exists; whether Australian carriers require it on interconnects: UNVERIFIED.
- CLI on emergency calls is a separate legal duty (s23 above); test it on every outbound path, including failover.

## Number porting

- Number portability is a customer right; a CSP involved in a portable service must have the technical capability to port. VERIFIED_PRIMARY [Numbering Plan 2025][np2025] Chapter 10.
- Geographic numbers port under C540:2023; mobile numbers under the mobile portability code. VERIFIED_SECONDARY [C540][c540].
- Design: number inventory as data (number, range, holding carrier, service, port status, IPND record); port-in cutover with a rollback; port-out detection so routing and billing stop. Copper exit
  drives bulk ports ([australian-access-networks](australian-access-networks.md#copper-exit-and-voice-migration)).

## Call-record reconciliation

- Retail call records and carrier records differ in format, time zone and rounding. Match on normalised number, call start (a window such as one minute), and duration tolerance, with confidence tiers;
  join usage on event date, not bill month. UNVERIFIED (practice); method owned by skill-ifa.
- Keep an internal-number register so own usage (support lines, call-centre numbers) is overhead, not unmatched customer usage.
- The platform must produce call records on every path: a failover that skips the call-record point loses billing and the welfare-check evidence for s28.

## SIP security

- Public SIP endpoints attract scanning and toll fraud: put an SBC or relay in front of PBXs, rate-limit registrations, ban repeated failures, use strong credentials, allow-list carrier addresses, and
  cap concurrent calls and spend per customer. UNVERIFIED (operational practice).
- Digest authentication is [RFC 8760][rfc8760] (SHA-256 support); encrypt signalling with TLS and media with SRTP ([RFC 3711][rfc3711]) where endpoints support it.
- Overload control ([RFC 7339][rfc7339]) and per-source limits keep a registration storm or attack from taking the platform down.
- Monitor for fraud by destination class (international, premium, mobile) and time of day; block high-risk destinations by default.

## Testing obligations

Test each path before it carries live traffic, and again after any carrier, routing or platform change. Record results as evidence.

| Test | On which paths | Pass condition |
| --- | --- | --- |
| 000 call (by arrangement with the emergency call person, or a test number the carrier provides) | Primary and each failover | Reaches the termination point; CLI and location delivered |
| 106 call | Each path serving standard telephone services | Reaches the 106 call person |
| 112 on a mobile-capable service | Where supplied | Routed as 000 |
| CLI presentation and withholding | Each carrier | Correct number shown; privacy honoured |
| 13/1300/1800 and international | Each carrier | Routed and rated as intended |
| Failover under load | Outbound carrier swap | Calls complete; limits and records still applied |
| Fax, alarm, lift devices | Each access type | Device reports succeed |

- Live 000 test calls must follow the emergency call person's test arrangements; do not place unannounced test calls. UNVERIFIED (procedure varies); ask the carrier.

## Patterns and anti-patterns

| Situation | Do | Avoid | Why |
| --- | --- | --- | --- |
| Two carriers | Peer the policy point to both, tested | Inbound on A, outbound on B only | One fault removes all outbound |
| Policy enforcement | Same limits and records on every path | Bypass the relay in a reroute | Fraud and billing gaps during incidents |
| Trunk capacity | Size in Erlangs; enforce limits at the edge | Rely on the carrier limit | Carrier rejects calls first; no local alarm |
| Emergency calls | Test 000/106 and CLI per path | Assume the backup carrier handles them | Legal duty; silent failure until needed |
| Numbers | Inventory as data with IPND link | Numbers in dialplan only | Porting, billing and location drift |
| Public registrar | SBC, rate limits, fraud caps | Open PBX on the internet | Toll fraud in hours |

## Failure modes and tests

| Failure | Signal | Test that proves detection and recovery |
| --- | --- | --- |
| Outbound carrier down | All outbound fails; inbound fine | OPTIONS probe alarm; switch selector; test call completes |
| Relay or SBC failure | All calls through it fail | Fail one HA member under load; calls continue |
| Emergency call fails on backup path | No answer, wrong CLI or no location | 000/106 test on the backup path before enabling it |
| CLI stripped on failover | Wrong or missing number at far end | Test call to a known handset per path |
| Trunk exhaustion | Busy tone at busy hour | Load to the session limit; edge limit and alarm act first |
| Registration flood | CPU high, registrations fail | Replay a scan in the lab; bans and rate limits engage |
| Call records missing on a path | Unbilled calls; no welfare-check evidence | Reconcile records per path after a failover test |

## Worked example

Question: a voice platform carries 30 Erlangs at busy hour. How many concurrent sessions are needed at 1% blocking, and what bandwidth on Ethernet with G.711?

| Step | Calculation | Result |
| --- | --- | --- |
| Erlang B, A = 30, target B <= 0.01 | Recursive B(N) = A x B(N-1) / (N + A x B(N-1)) | N = 42 gives B = 0.0074; N = 41 gives 0.0104 |
| Sessions to buy per carrier | 42 on the primary; the backup must also carry 42 if it takes all traffic | 42 + 42 |
| Bandwidth per direction | 42 x 87.2 kbit/s (G.711, 20 ms, Ethernet) | 3.66 Mbit/s each way |
| On PPPoE access | 42 x 90.4 kbit/s | 3.80 Mbit/s each way |

- No `just` helper exists for Erlang B; the figures were computed with the recursion above on 2026-10-29. Erlang B formula: VERIFIED_SECONDARY ([Erlang unit][erlang]).
- Verdict: 42 sessions per carrier, with edge limits at 42, and a backup path sized for full load or a written shed policy.
- Test: load test to 42 concurrent calls on each carrier; the 43rd call is rejected by the edge, not the carrier.

## Review checklist

- [ ] Carrier map: who holds which numbers, who terminates outbound, failover for each direction.
- [ ] Policy point is a redundant pair with a peer to each carrier; failover keeps limits, CLI and records.
- [ ] Trunks sized in Erlangs from measured busy hour; edge limits set below the carrier limit.
- [ ] 000, 106 and (where relevant) 112 tested on every path; CLI and location delivered; evidence kept.
- [ ] Diversity or a written arrangement for emergency calls (s11); 24x7 contact registered (s26).
- [ ] IPND data current; nomadic services identified.
- [ ] Number inventory as data; porting runbook with rollback.
- [ ] SBC or equivalent in front of public endpoints; fraud caps by destination.
- [ ] Device classes (fax, alarm, lift) tested per access type.

## Sources

Checked 2026-10-29. VERIFIED_PRIMARY: Telecommunications (Emergency Call Service) Determination 2019 compilation in force 2025-11-01 (read on legislation.gov.au), Telecommunications Numbering Plan
2025 (Chapter 10), nbn PTS 2026-09-01, every RFC row (rfc-editor.org metadata). VERIFIED_SECONDARY: C540:2023 and C661:2022 status (ACMA pages and enforcement reports, codes not read in full),
Asterisk chan_sip removal, Erlang B formula. UNVERIFIED: whether Australian carriers require RFC 8224, CSP-level test duties beyond the determination, carrier-specific codec baselines.

## Further reading

URLs resolved 2026-10-29.

Australian obligations:

- [Telecommunications (Emergency Call Service) Determination 2019][ecsd]: the current compilation; read Part 2 for carriage service providers.
- [Telecommunications Numbering Plan 2025][np2025]: numbering, portability (Chapter 10) and number use rules.
- [C540:2023 Local Number Portability code][c540]: the industry process for porting geographic numbers.
- [ACMA: caller ID and spoofing][acma-cli]: CLI rules and the scam-call code from the regulator.

SIP and media:

- [RFC 3261 SIP][rfc3261] and [RFC 3263 Locating SIP Servers][rfc3263]: the protocol and DNS-based failover.
- [RFC 3325 Asserted Identity][rfc3325] and [RFC 8224 Authenticated Identity][rfc8224]: how caller identity crosses networks.
- [RFC 4733 telephone-events][rfc4733] and [RFC 3551 RTP A/V profile][rfc3551]: DTMF and codec payload definitions.
- [RFC 7092 B2BUA taxonomy][rfc7092]: what an SBC or relay actually does to signalling and media.

[ecsd]: https://www.legislation.gov.au/F2019L01509/latest/text
[np2025]: https://www.legislation.gov.au/F2025L00409/latest/text
[c540]: https://www.commsalliance.com.au/__data/assets/pdf_file/0011/94556/C540_2023.pdf
[acma-cli]: https://www.acma.gov.au/calling-line-identification-and-spoofing
[nbn-pts]: https://www.nbnco.com.au/content/dam/nbn/documents/sell/wba/2026/sfaa-wba-nbn-ethernet-product-technical-specification-20260901.pdf.coredownload.pdf
[ast-chansip]: https://www.asterisk.org/?p=8849
[erlang]: https://en.wikipedia.org/wiki/Erlang_(unit)
[rfc3261]: https://www.rfc-editor.org/rfc/rfc3261.html
[rfc3263]: https://www.rfc-editor.org/rfc/rfc3263.html
[rfc3325]: https://www.rfc-editor.org/rfc/rfc3325.html
[rfc3550]: https://www.rfc-editor.org/rfc/rfc3550.html
[rfc3551]: https://www.rfc-editor.org/rfc/rfc3551.html
[rfc3711]: https://www.rfc-editor.org/rfc/rfc3711.html
[rfc4594]: https://www.rfc-editor.org/rfc/rfc4594.html
[rfc4733]: https://www.rfc-editor.org/rfc/rfc4733.html
[rfc5626]: https://www.rfc-editor.org/rfc/rfc5626.html
[rfc7092]: https://www.rfc-editor.org/rfc/rfc7092.html
[rfc7339]: https://www.rfc-editor.org/rfc/rfc7339.html
[rfc8224]: https://www.rfc-editor.org/rfc/rfc8224.html
[rfc8760]: https://www.rfc-editor.org/rfc/rfc8760.html
