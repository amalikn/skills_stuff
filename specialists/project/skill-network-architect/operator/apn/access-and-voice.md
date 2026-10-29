---
Title: APN operator context - access, subscriber edge and voice
Category: operator-context
Status: current
Authority: internal
Scope: >-
  Operator-specific lessons from the APN projects (vocus-profitability, opticomm-profitability, voip-analysis, apn-sip-setup, vbng/podbng-lab and the apn root docs) that apply
  the general references on Australian access networks, the service provider edge and voice
Last reviewed: 2026-10-29
Summary: >-
  Facts about how the operator buys access, runs its subscriber edge lab and carries voice, each with why it matters architecturally, its evidence path and the general section it
  applies. No customer, community or people names, addresses, credentials, prices, margins or invoice figures; carrier figures stay in the projects (ex-GST there, never here).
---

# APN operator context: access, subscriber edge and voice

## Contents

- [How to use this file](#how-to-use-this-file)
- [Wholesale access](#wholesale-access)
- [Subscriber edge lab](#subscriber-edge-lab)
- [Voice platform](#voice-platform)
- [Shared services](#shared-services)

## How to use this file

- General rules live in the references; this file records where the operator's own estate confirms, contradicts or extends them. Read the linked general section first.
- Evidence paths are relative to `/Volumes/Data/_ai/_project/project_stuff/apn/`. They are internal analysis workspaces built from wholesale documents and lab work; treat each item as USER_STATED
  (project record) unless the general reference verifies the generic rule.
- Every item: the fact, why it matters, evidence, and the general section it applies.

## Wholesale access

- **The operator is a sub-RSP: it holds no nbn WBA; Vocus is the RSP of record and the operator buys under a downstream wholesale agreement.** Why: NNI diversity, nbn rebates and ordering rights exist
  for the operator only as contract terms; pass-through and notification clauses must be explicit and audited. Evidence:
  `vocus-profitability/docs/references/summary-sfaa-wba-nbn-ethernet-dcr-annexure-20260101.md`. Applies: [Aggregators and
  sub-RSPs](../../references/australian-access-networks.md#aggregators-and-sub-rsps).
- **nbn AVCs reach the operator as Layer 2 over a small number of 10G NNI ports in a Sydney data centre; aggregator bandwidth is a committed pool per OVC.** Why: the operator BNG and its NNI must be
  sized for committed plus burst on each OVC, and the aggregator NNI is a concentrated failure domain to cover in the contract. Evidence:
  `vocus-profitability/docs/reports/billing/rate-card-reference-20260520_1430.md` (Key Contract Terms; commitment figures not copied). Applies: [POIs, NNI and
  backhaul](../../references/australian-access-networks.md#pois-nni-and-backhaul).
- **Historically the operator had direct presence at about half of the nbn POIs and moved to the aggregator Layer 2 service to consolidate backhaul; the migration excluded satellite services.** Why:
  the direct-versus-aggregated decision is per POI; migrations run POI by POI with transfer fees, duplicate billing and customer notice; satellite stays a separate design. Evidence:
  `vocus-profitability/docs/references/SoW-Migrate-AVCs-to-NCL2-2024.md`; `vocus-profitability/docs/reports/analysis-tracker.md` (NQ4). Applies: [Aggregators and
  sub-RSPs](../../references/australian-access-networks.md#aggregators-and-sub-rsps), [Satellite and fixed wireless](../../references/australian-access-networks.md#satellite-and-fixed-wireless).
- **When the operator ran direct POIs, the NOC resized each CVC weekly to hold evening speeds; higher tiers needed more burst headroom.** Why: after 2026-07-01 the CVC lever is gone for TC-4; the same
  busy-hour discipline moves to the OVC, NNI and backhaul. Evidence: `vocus-profitability/docs/references/SoW-Migrate-AVCs-to-NCL2-2024.md`. Applies: [Pricing construct from
  2026-07-01](../../references/australian-access-networks.md#pricing-construct-from-2026-07-01).
- **On the aggregator invoices, overage lines fell to zero from July 2026 usage after the flat-rate card; the transition month mixed both constructs.** Why: confirms the nbn construct change reached
  the operator through the aggregator; billing and capacity logic must handle the transition month. Whether the aggregator card mirrors nbn timing exactly: UNVERIFIED. Evidence:
  `vocus-profitability/docs/reports/analysis-tracker.md` (INV-013, INV-014); `vocus-profitability/AGENTS.md` (Overage bullet). Applies: [Pricing construct from
  2026-07-01](../../references/australian-access-networks.md#pricing-construct-from-2026-07-01).
- **The residential base is all TC-4; TC-1 and TC-2 appear only in wholesale rebate terms, not in the operator's services.** Why: voice over nbn currently runs on best effort; any voice quality
  commitment needs TC-1 ordered (AVC and CVC) or a stated risk. Evidence: `vocus-profitability/docs/references/summary-sfaa-wba-nbn-ethernet-dcr-annexure-20260101.md`;
  `opticomm-profitability/docs/references/opticomm-wholesale-price-list-jul2025.md` (s1.4). Applies: [nbn access model](../../references/australian-access-networks.md#nbn-access-model), [Access, ATA
  and UNI-V](../../references/voice-and-sip.md#access-ata-and-uni-v).
- **A cohort of Fixed Wireless services was provisioned at a higher wholesale tier than the retail plan; the correction showed as a mid-month re-rate.** Why: a profile-match check between retail plan
  and wholesale tier belongs in every billing cycle; a wrong default profile at bulk activation leaks for months. Evidence: `vocus-profitability/docs/reports/analysis-tracker.md` (INV-012, INV-014;
  counts not copied). Applies: [nbn access model](../../references/australian-access-networks.md#nbn-access-model) (tier = technology x tier x date).
- **A manually kept OVC list drifted after resizes, a check validated the list against itself, and one circuit was billed long after it should have ceased.** Why: circuit inventory must be reconciled
  against the supplier's latest invoice as an independent oracle; ghost-circuit detection is a standing check. Evidence: `vocus-profitability/.archcore/rules/cvc-billing-mechanics.md`;
  `vocus-profitability/docs/reports/analysis-tracker.md` (INV-011, DATA-1). Applies: [Failure modes and tests](../../references/australian-access-networks.md#failure-modes-and-tests).
- **Opticomm was modelled at both Layer 2 (Ethernet Bitstream to the operator BNG) and Layer 3 (wholesale broadband); the cheaper layer differed between Opticomm and the aggregator.** Why: confirms
  the per-network, whole-stack L2 versus L3 rule; Opticomm charges (access, OVC and state backhaul aggregation) keep their own names in the data model, never "CVC". Evidence:
  `opticomm-profitability/SCRATCHPAD.md` (L2 vs L3, SBA terminology); `opticomm-profitability/.archcore/rules/no-vocus-schema-copy.md`. Applies: [Private networks and Uniti
  Wholesale](../../references/australian-access-networks.md#private-networks-and-uniti-wholesale).
- **The voice-only nbn tier exists on the operator's rate card while legacy copper resale lines decline month on month.** Why: copper exit is under way in the base; number porting, voice-only AVC or
  OTT SIP, and life-safety device checks belong in the migration plan. Evidence: `voip-analysis/.archcore/adr/adr-003-rec005-attribution-gate.md`;
  `vocus-profitability/docs/reports/billing/rate-card-reference-20260520_1430.md`. Applies: [Copper exit and voice
  migration](../../references/australian-access-networks.md#copper-exit-and-voice-migration).

## Subscriber edge lab

The vBNG work is a lab (podbng-lab), not a production design. Lab results are lab evidence only.

- **Reference stack: VPP data plane, Accel-PPP session plane, FreeRADIUS, Kea DHCPv4, FRR (BGP, BFD) and keepalived (VRRP), with control services on K3s; production target 40,000 concurrent IPoE
  sessions per BNG, while a lab VM reaches roughly 2,000-5,000.** Why: each plane boundary is a versioned contract; scale must be proven on target hardware. Evidence:
  `vbng/podbng-lab/ARCHITECTURE.md`; `vbng/podbng-lab/docs/testing/testing-plan.md` (session targets). Applies: [BNG design](../../references/service-provider-edge.md#bng-design).
- **IPoE with DHCP-triggered sessions and MAC as the RADIUS username was proven; PPPoE fell back to local authentication because the RADIUS plugin path was broken.** Why: one session type proven is
  not both proven; record PPPoE as unproven until it authenticates through RADIUS. Evidence: `vbng/podbng-lab/docs/planning/vbng-lab-buildout-roadmap-20260427_1041.md`;
  `vbng/podbng-lab/adr/claude-code-orchestrate/` (ADR 9). Applies: [BNG design](../../references/service-provider-edge.md#bng-design).
- **QinQ uses one S-VLAN per wholesale network (nbn and Opticomm) and a C-VLAN per subscriber; a hypervisor bridge with VLAN filtering on silently strips inner tags.** Why: confirms the per-wholesaler
  S-tag domain; prove double tags pass the virtual bridge before debugging the BNG. Evidence: `vbng/podbng-lab/docs/testing/testing-plan.md` (QinQ pre-flight). Applies: [BNG
  design](../../references/service-provider-edge.md#bng-design).
- **The first test plan described the aggregate policer direction three contradictory ways; the fix wrote it once as uplink sub-interface input.** Why: hierarchical policing needs one unambiguous
  direction statement tested with counters. Evidence: `vbng/podbng-lab/docs/testing/testing-plan.md` (policer direction fix). Applies: [BNG
  design](../../references/service-provider-edge.md#bng-design).
- **CoA was first keyed on User-Name or source IP and one sender used a vendor rate attribute the policy agent ignored, so the NAS acknowledged with no rate change.** Why: one session-identity
  contract (Acct-Session-Id) and a read-back of the applied policer. Evidence: `vbng/podbng-lab/docs/testing/testing-plan.md`; ADR 10 under `vbng/podbng-lab/adr/claude-code-orchestrate/`. Applies:
  [RADIUS AAA and CoA](../../references/service-provider-edge.md#radius-aaa-and-coa).
- **CoA was silently rejected for hours while Access-Request tests passed; the BlastRADIUS hardening had been "confirmed" by a substring grep that matched a commented-out line.** Why: separate tests
  per RADIUS operation; anchored configuration checks. Evidence: `vbng/podbng-lab/docs/crewai/claude-code-orchestrate/retrospective-20260415.md`. Applies: [RADIUS AAA and
  CoA](../../references/service-provider-edge.md#radius-aaa-and-coa), [Lab validation pitfalls](../../references/service-provider-edge.md#lab-validation-pitfalls).
- **Kea behind a Kubernetes NodePort failed because SNAT rewrote the relay source; host ports on pinned nodes fixed it.** Why: no NAT or load-balancer hop between DHCP relay and server. Evidence:
  `vbng/podbng-lab/docs/testing/testing-plan.md` (Kea NodePort fix). Applies: [Lab validation pitfalls](../../references/service-provider-edge.md#lab-validation-pitfalls).
- **The anti-spoofing decision record attaches the ACL to uplink input while the test plan says access interface; the host firewall never sees data-plane traffic.** Why: the two documents disagree;
  source validation belongs on subscriber-facing ingress. Resolve the decision record before production. Evidence: ADR 11 under `vbng/podbng-lab/adr/claude-code-orchestrate/`;
  `vbng/podbng-lab/docs/testing/testing-plan.md` (Stage 9). Applies: [Anti-spoofing](../../references/service-provider-edge.md#anti-spoofing).
- **VRRP runs on a kernel NIC with hooks that move the VIP inside the data plane; measured failover was under 10 s, dominated by hypervisor shutdown time, not VRRP timers.** Why: measure the whole
  detection chain before writing an SLA; sub-second needs BFD. Evidence: ADR 12 under `vbng/podbng-lab/adr/claude-code-orchestrate/`;
  `vbng/podbng-lab/docs/crewai/claude-code-orchestrate/retrospective-20260415.md`. Applies: [Failover and reconnect storms](../../references/service-provider-edge.md#failover-and-reconnect-storms).
- **A decision record calls sessions "preserved" after BNG failover; what it shows is the surviving node's own sessions. The failed node's subscribers re-establish (a production storm of about 40,000
  rebinds, target under 20 s).** Why: name the HA claim exactly and size RADIUS, DHCP and CGNAT for the storm. Evidence: `vbng/podbng-lab/docs/testing/testing-plan.md` (Stage 11 and 11a); ADR 12.
  Applies: [Failover and reconnect storms](../../references/service-provider-edge.md#failover-and-reconnect-storms).
- **No lab document sets or tests PPPoE MTU, RFC 4638, QinQ frame size or MSS clamping.** Why: negative finding; the edge design is incomplete until the MTU budget is written and probed. Evidence:
  `vbng/podbng-lab/docs/testing/testing-plan.md` (no MTU section); `vbng/podbng-lab/templates/cloud-init/` (no MTU settings). Applies: [MTU and MSS with
  PPPoE](../../references/service-provider-edge.md#mtu-and-mss-with-pppoe).
- **CGNAT and IPv6 are roadmap items; IPv6 is disabled kernel-wide on lab hosts; the roadmap attributes DS-Lite to FTTP and MAP-E to FTTN, which is wrong.** Why: nbn is Layer 2; the IPv6 mechanism is
  the operator's choice. Disabled IPv6 also broke RADIUS listeners in the lab. Evidence: `vbng/podbng-lab/docs/planning/FEATURE-ROADMAP.md` (IPv6, CGNAT sections); `vbng/podbng-lab/RECONSTRUCTION.md`.
  Applies: [IPv6 transition](../../references/service-provider-edge.md#ipv6-transition), [CGNAT and logging](../../references/service-provider-edge.md#cgnat-and-logging).
- **Several lab tests passed vacuously: a data-plane CLI printed text and exited 0 for a command that does not exist in that release, and a host-stack command was used to count subscriber sessions.**
  Why: assert on specific content, use the session daemon as the observable, add negative tests. Evidence: `vbng/podbng-lab/docs/crewai/claude-code-orchestrate/retrospective-20260415.md`;
  `vbng/podbng-lab/CHANGELOG.md`. Applies: [Lab validation pitfalls](../../references/service-provider-edge.md#lab-validation-pitfalls).

## Voice platform

- **Inbound numbers are hosted by one carrier and outbound terminates through another; an outbound carrier device outage stopped outbound calls estate-wide while inbound stayed up.** Why: split
  carriers give partial resilience only; a tested outbound failover is required. Evidence: `apn-sip-setup/ARCHITECTURE.md`; `apn-sip-setup/incidents/` (2026-05-04 outage record). Applies: [Carrier
  redundancy and failover](../../references/voice-and-sip.md#carrier-redundancy-and-failover).
- **Customer and staff PBXs route outbound through one relay PBX that peers to one carrier; staff traffic could not be rerouted during the outage.** Why: the policy point must be an HA pair with a
  peer to each carrier. Evidence: `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s2.2, s4.2). Applies: [SIP trunk architecture](../../references/voice-and-sip.md#sip-trunk-architecture).
- **One dialplan global selects the outbound trunk for both outbound and forwarding contexts; changing it and reloading is the reroute and the rollback.** Why: a single selector is a good lever; the
  runbook must list every context it changes. Evidence: `apn-sip-setup/ARCHITECTURE.md`. Applies: [Carrier redundancy and failover](../../references/voice-and-sip.md#carrier-redundancy-and-failover).
- **The relay enforces per-customer concurrent-call limits and billing-header handling for customer traffic; a reroute that bypasses the relay bypasses both.** Why: failover paths need policy parity.
  Evidence: `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s4.3, s8.2). Applies: [Carrier redundancy and failover](../../references/voice-and-sip.md#carrier-redundancy-and-failover).
- **Trunk capacity is a carrier concurrent-session allocation and the PBX peer has no local call limit.** Why: the carrier limit is the first control today; set an edge limit below it and alarm on it.
  Evidence: `voip-analysis/.archcore/rules/rule-004-rec005-pstn-exclusion.md`; `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s3.2). Applies: [Worked
  example](../../references/voice-and-sip.md#worked-example).
- **Carrier peers use G.711 A-law only, RFC 2833 DTMF, IP-authenticated static peers and OPTIONS liveness.** Why: matches the general baseline; RFC 4733 now defines telephone-events. Evidence:
  `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s3.5). Applies: [Codecs and bandwidth](../../references/voice-and-sip.md#codecs-and-bandwidth).
- **The PBX estate spans three Asterisk generations with chan_sip live and an unused PJSIP tree; chan_sip is removed in Asterisk 21.** Why: platform lifecycle risk; PJSIP migration and consolidation
  need a plan before any upgrade. Evidence: `apn-sip-setup/ARCHITECTURE.md`; `apn-sip-setup/SCRATCHPAD.md`. Applies: [SIP trunk architecture](../../references/voice-and-sip.md#sip-trunk-architecture).
- **Inbound DIDs are mapped to extensions by a database lookup, not static dialplan.** Why: that table is the DID inventory for billing and porting; keep it authoritative. Evidence:
  `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s7.1). Applies: [Number porting](../../references/voice-and-sip.md#number-porting).
- **The customer PBX accepts a large number of SIP registrations on a public interface, protected by fail2ban.** Why: an SBC in front, rate limits and fraud caps are the target state. Evidence:
  `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s3.1; counts not copied). Applies: [SIP security](../../references/voice-and-sip.md#sip-security).
- **Whether 000, 13xx/1800 and caller ID work through the alternate outbound carrier is listed as open and untested.** Why: the Emergency Call Service Determination requires access and CLI on every
  service; the alternate path must be tested before use. Evidence: `apn-sip-setup/ARCHITECTURE.md` (Invariants); `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (s8.2). Applies: [Emergency
  calls](../../references/voice-and-sip.md#emergency-calls), [Testing obligations](../../references/voice-and-sip.md#testing-obligations).
- **On the remote-site boxes the telephony role configures call records but disables the RADIUS, ODBC and PostgreSQL back-ends; emergency-call reporting is unproven.** Why: call-record evidence is
  needed for billing and for post-outage welfare checks; record the state as contradictory until a record is seen. Evidence: `docs/wifi-metrics-coverage.xlsx` (rows Calls Made, Calls Received,
  Emergency Calls). Applies: [Call-record reconciliation](../../references/voice-and-sip.md#call-record-reconciliation), [Emergency calls](../../references/voice-and-sip.md#emergency-calls).
- **Retail call records are matched to carrier records by number, call minute (plus or minus one) and duration tolerance with confidence tiers; usage joins on call date.** Why: method owned by
  skill-ifa; the network design must keep records on every path. Evidence: `voip-analysis/docs/apn-cdr-to-aapt-bef-call-matching-knowledge-20260611_1820.md`; `voip-analysis/AGENTS.md`. Applies:
  [Call-record reconciliation](../../references/voice-and-sip.md#call-record-reconciliation).

## Shared services

- **Customer resolvers sit behind a load balancer; a hot member is first a distribution question (a heavy CGNAT or satellite gateway source landing on one member), then a host question.** Why: CGNAT
  concentrates many subscribers behind few sources, which skews per-source hashing. Evidence: `docs/customer-resolvers/` (UDP receive tuning plan, 2026-04-02); `README.md` (Documentation routing).
  Applies: [CGNAT and logging](../../references/service-provider-edge.md#cgnat-and-logging).
