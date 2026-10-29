---
Title: APN operator context - OSS/BSS, fleet and platform data lessons
Category: operator-context
Status: current
Authority: internal
Scope: >-
  APN-specific lessons behind the general service-provider-systems, fleet-management, architecture-method and automation-and-safety references; shared by
  skill-network-architect and skill-systems-architect (systems pack reads this folder through a symlink)
Last reviewed: 2026-10-29
Summary: >-
  Operator-specific facts from APN projects (wholesale billing reconciliation, voice platform, fleet source of truth, vendor exit, platform repatriation),
  each with why it matters, its evidence path and the general reference section it applies. No customer, community or people names, addresses,
  credentials, prices, margins or invoice figures.
---

# APN operator context: OSS/BSS, fleet and platform data

This file holds what is specific to the operator. The general references stay operator-neutral and never link here. Evidence paths are under `/Volumes/Data/_ai/_project/project_stuff/apn/`. Supplier
and product names are kept because they are public; every figure from a supplier invoice, contract or rate card is omitted by operator rule (all such figures in the projects are ex-GST).

## Contents

- [Wholesale access and billing](#wholesale-access-and-billing)
- [Reconciliation pipelines](#reconciliation-pipelines)
- [Voice platform](#voice-platform)
- [Fleet source of truth and telemetry](#fleet-source-of-truth-and-telemetry)
- [Vendor exit and controller recovery](#vendor-exit-and-controller-recovery)
- [Platform decisions and method](#platform-decisions-and-method)

## Wholesale access and billing

**A1. Three access suppliers, three identifier sets.** nbn services arrive through an aggregator (Vocus) that holds the wholesale agreement; private fibre services come from Opticomm (owned by Uniti
Group). Each supplier keys services differently: the aggregator joins AVC ID to its charged-party field and its service record to an end-customer field; Opticomm service records need
float-to-integer-to-text normalisation before a join.
- Why: a join on an un-normalised key silently drops services from the margin and reconciliation sets.
- Evidence: `vocus-profitability/AGENTS.md`; `opticomm-profitability/SCRATCHPAD.md`; `voip-analysis/AGENTS.md` (Join keys).
- Applies to: [Identifiers and join keys](../../../skill-systems-architect/references/service-provider-systems.md#identifiers-and-join-keys).

**A2. Aggregator billing uses advance plus catch-up record types.** The aggregator invoice CSV bills each full month in advance (one record type) and a later positive partial-month catch-up (another);
there is no negative credit-back. Overage dated the first of a month with no end date is the prior month's usage. Partial months are pro-rated over a fixed denominator, not days in month.
- Why: bucketing by charge start date misattributes overage and activation-month cost.
- Evidence: `vocus-profitability/docs/reports/billing/billing-mechanics-pro-rata-20260520_1700.md`; `vocus-profitability/AGENTS.md` (Overage).
- Applies to: [Billing timing and the service-month grain](../../../skill-systems-architect/references/service-provider-systems.md#billing-timing-and-the-service-month-grain).

**A3. Discount base differs between invoice and profit report.** The invoice applies the discount to advance plus catch-up lines; the supplier profit report uses a narrower base, so the two never tie.
AVC and capacity discounts are separate lines at different rates; reading gross capacity alone once produced a phantom overcharge that was raised and withdrawn.
- Why: model the discount base explicitly and compute net unit rates across all record types before raising a query.
- Evidence: `vocus-profitability/docs/reports/analysis-tracker.md` (RECON-1); `vocus-profitability/.archcore/rules/cvc-billing-mechanics.md`.
- Applies to: [Billing timing and the service-month grain](../../../skill-systems-architect/references/service-provider-systems.md#billing-timing-and-the-service-month-grain); procedure in skill-ifa.

**A4. Plan-to-tier mismatch on a bulk activation.** A cohort of fixed wireless services sold on a lower retail plan was provisioned and billed on a higher wholesale tier; the correction showed as a
mid-month re-rate with a transition-month side effect.
- Why: the profile-match check (retail plan versus wholesale tier per service) belongs in every cycle.
- Evidence: `vocus-profitability/docs/reports/analysis-tracker.md` (INV-012, INV-014).
- Applies to: [Reconciliation pipeline](../../../skill-systems-architect/references/service-provider-systems.md#reconciliation-pipeline).

**A5. Subsidised school-student services are a separate population.** They carry no retail revenue and are funded by an nbn rebate joined from the nbn billing event file by Location ID; failed
location joins leave cost with no rebate.
- Why: needs its own service class, funding source and join key, outside commercial averages.
- Evidence: `vocus-profitability/AGENTS.md` (add_ssbi_rebates.py).
- Applies to: [Reconciliation pipeline](../../../skill-systems-architect/references/service-provider-systems.md#reconciliation-pipeline).

**A6. Supplier products leave the catalogue on fixed dates.** A bundled capacity product on the private fibre network was withdrawn from sale and exited on published dates; a capacity overage item
moved to a withdrawn-plans appendix.
- Why: cease-sale and exit dates drive migration plans for in-life services.
- Evidence: `opticomm-profitability/docs/references/opticomm-wholesale-price-list-jul2025.md` (section 1.3, Appendix 1).
- Applies to: [Catalogue, cost allocation and voice](../../../skill-systems-architect/references/service-provider-systems.md#catalogue-cost-allocation-and-voice).

## Reconciliation pipelines

**B1. Three-source set per network.** Each network has an invoice CSV, a per-service profitability report and a service reconciliation report (supplier status versus retail billing status, exception
code, profile match).
- Why: the exceptions between the three are the work queue.
- Evidence: `opticomm-profitability/docs/reports/source-inventory-current.md`; `vocus-profitability/AGENTS.md`.
- Applies to: [Reconciliation pipeline](../../../skill-systems-architect/references/service-provider-systems.md#reconciliation-pipeline).

**B2. A capacity list checked against itself.** The hand-kept aggregator capacity list drifted twice in three weeks after resizes while a check reported zero anomalies, because it validated the list
against itself. A ghost capacity circuit was billed for many months before a retroactive credit.
- Why: the named example of a vacuous check; reconcile to the latest invoice.
- Evidence: `vocus-profitability/.archcore/rules/cvc-billing-mechanics.md`; `vocus-profitability/docs/reports/analysis-tracker.md` (INV-011, DATA-1).
- Applies to: [Decision rules (checks that cannot fail)](../../references/architecture-method.md#decision-rules).

**B3. Contracted rate not loaded into supplier billing.** A newly signed lower rate was not applied; the invoice was internally correct but above contract. Contract rates are kept as slabs.
- Why: the two-oracle invoice check.
- Evidence: `vocus-profitability/scripts/validate_invoice.py` (docstring); `vocus-profitability/docs/reports/analysis-tracker.md` (INV-016).
- Applies to: [Decision rules](../../../skill-systems-architect/references/service-provider-systems.md#decision-rules); procedure in skill-ifa.

**B4. Service-month grain and two lineages.** One margin project fixed `(service_id, month)` as the grain by ADR; another keeps a regular flow from the supplier sheet and an enriched flow (rebates,
imputed revenue, bandwidth-allocated infrastructure pools), with a basis label on every margin. Missing monthly bandwidth exports block enrichment.
- Evidence: `opticomm-profitability/.archcore/adr/adr-001-service-month-grain.md`; `vocus-profitability/.archcore/rules/cost-model-pipeline-order.md`;
  `vocus-profitability/.archcore/rules/infra-cost-pool-values.md`.
- Applies to: [Reconciliation pipeline](../../../skill-systems-architect/references/service-provider-systems.md#reconciliation-pipeline).

**B5. Money arrived as text.** Voice price columns arrived as text with a currency symbol; a numeric comparison silently dropped every row.
- Evidence: `voip-analysis/.archcore/rules/rule-001-price-filter.md`.
- Applies to: [Decision rules](../../../skill-systems-architect/references/service-provider-systems.md#decision-rules).

**B6. File-drop analytics stack.** Monthly supplier CSVs become typed Parquet with dated archives, DuckDB views for analysis and Postgres for dashboards.
- Evidence: `vocus-profitability/AGENTS.md`; `voip-analysis/.archcore/adr/adr-004-cdr-naming-convention.md`.
- Applies to: [Reconciliation pipeline](../../../skill-systems-architect/references/service-provider-systems.md#reconciliation-pipeline).

## Voice platform

**C1. Mixed Asterisk generations with chan_sip live.** The PBX estate runs three Asterisk generations (1.6, 11 and 20), all on `chan_sip`, with an unused PJSIP tree. 1.6 and 11 are long past end of
life; 20 left full support on 2026-10-19.
- Why: no upgrade past 20 without a PJSIP migration; version consolidation is a lifecycle risk.
- Evidence: `apn-sip-setup/ARCHITECTURE.md`; `apn-sip-setup/SCRATCHPAD.md`.
- Applies to: [Catalogue, cost allocation and voice](../../../skill-systems-architect/references/service-provider-systems.md#catalogue-cost-allocation-and-voice).

**C2. Inbound DID lookup by AGI.** Inbound calls read a DID header (falling back to the request URI) and an AGI script maps DID to extension from the PBX database.
- Why: that table is the number inventory billing attribution needs.
- Evidence: `apn-sip-setup/docs/pbx-routing-reference-20260504_1112.md` (section 7.1).
- Applies to: [Catalogue, cost allocation and voice](../../../skill-systems-architect/references/service-provider-systems.md#catalogue-cost-allocation-and-voice).

**C3. One carrier account, several voice businesses.** The voice carrier account carries VoIP usage, PSTN resale rentals, inbound 13/1300/1800 usage and the company's own support numbers; attributing
PSTN rentals to VoIP made VoIP look loss-making.
- Evidence: `voip-analysis/.archcore/adr/adr-003-rec005-attribution-gate.md`; `voip-analysis/AGENTS.md`.
- Applies to: [Catalogue, cost allocation and voice](../../../skill-systems-architect/references/service-provider-systems.md#catalogue-cost-allocation-and-voice).

## Fleet source of truth and telemetry

**D1. Four ownership classes enforced by a Nautobot app.** Only the collector and importer service accounts write device-owned fields; an administrator is not a writer. Inventory fields become device
fields once the device reports them.
- Evidence: `unified-network-controller/docs/field-ownership/field-ownership-model-20260923_1336.md` (sections 1-2); `unified-network-controller/ARCHITECTURE.md`.
- Applies to: [Source of truth and field ownership](../../../skill-systems-architect/references/fleet-management.md#source-of-truth-and-field-ownership).

**D2. Uniqueness check caught tunnel cross-talk.** A cross-talk defect in the site tunnel nearly let a read from one box overwrite another record; the estate-wide uniqueness rule is the falsifier.
- Evidence: `unified-network-controller/docs/field-ownership/field-ownership-model-20260923_1336.md` (section 4).
- Applies to: [Source of truth and field ownership](../../../skill-systems-architect/references/fleet-management.md#source-of-truth-and-field-ownership).

**D3. Position, not unit; held swap.** Monitoring joins on the Nautobot record ID; a swap is held, then acknowledged by an operator job that moves identity and sends the old unit to Decommissioning.
- Evidence: `unified-network-controller/docs/field-ownership/field-ownership-model-20260923_1336.md` (section 5).
- Applies to: [Source of truth and field ownership](../../../skill-systems-architect/references/fleet-management.md#source-of-truth-and-field-ownership).

**D4. Single writer per DNS policy zone during migration.** An operator-owned field names the writer of each site's response-policy zone (legacy controller or the new controller); a validator refuses
hand edits to a legacy-owned zone.
- Evidence: `unified-network-controller/ARCHITECTURE.md` (RPZ authority).
- Applies to: [Decision rules](../../../skill-systems-architect/references/fleet-management.md#decision-rules).

**D5. Site-box push collector design.** Proposed spool on the site box: gzip batch per cycle, 48 h or 200 MB cap, counted drops, no readings before time sync, ingest rejects skew above 2 min, newest
batch first. Site boxes without a clock battery booted up to 13 months behind; deployed boxes with an overlay root keep any spool in RAM.
- Evidence: `unified-network-controller/docs/engineering/smc-push-collector-design-20261021_1757.md` (section 5).
- Applies to: [Telemetry collectors and spools](../../../skill-systems-architect/references/fleet-management.md#telemetry-collectors-and-spools).

**D6. A soak that looked slow was failing.** Collector runs failed in minutes on an expired access-proxy certificate for about 40 hours; the duration graph had no success state.
- Evidence: `unified-network-controller/docs/reports/monitoring/step2-soak-slowdown-cause-20260927_2130.md`.
- Applies to: [Telemetry collectors and spools](../../../skill-systems-architect/references/fleet-management.md#telemetry-collectors-and-spools).

**D7. Access-control test that could not tell mechanisms apart.** A token minted through the REST API was an admin token (the endpoint ignored the user field), and a real operator token was refused by
object permissions before the validator ran. Fix: mint through the ORM, assert the acting account in the change log, grant change permission so only the validator can refuse.
- Evidence: `unified-network-controller/docs/field-ownership/field-ownership-model-20260923_1336.md` (section 9).
- Applies to: [Test design](../../references/automation-and-safety.md#decision-rules).

**D8. Machine identity by cloud IAM join.** The access-proxy machine agent moved from static join tokens to cloud IAM delegated join, so rebuilt or long-offline hosts rejoin unattended. Already-issued
short-lived certificates hid a broken renewal until expiry.
- Evidence: `teleport/tbot/docs/why-we-moved-tbot-onboarding-to-aws-iam-delegated-join-20260324_1800.md`; `teleport/tbot/docs/ec2/ssh-continues-working-and-ttl-recommendation-20260324_1510.md`.
- Applies to: [Lifecycle and recovery](../../../skill-systems-architect/references/fleet-management.md#lifecycle-and-recovery).

## Vendor exit and controller recovery

**E1. Wireless controller dependency matrix.** Every controller capability of the wireless vendor is classed L0-L4 with an evidence state; forwarding is L0, onboarding, restore and device delete are
L2/L3. The on-premises controller guide documents a 90-day grace after licence sync fails, after which devices move to the onboarding queue (scope test-gated).
- Evidence: `cambium-swap/docs/architecture/dependency-matrix.md`; `cambium-swap/docs/architecture/cloud-anchor.md`.
- Applies to: [Vendor dependency and controller recovery](../../../skill-systems-architect/references/fleet-management.md#vendor-dependency-and-controller-recovery).

**E2. Controller identity rides on an address in DHCP option 43.** The local DHCP option hands devices an address, not a name, so a restore that changes the address needs a fleet-wide change. The DR
plan keeps block-level snapshots and machine images plus the surrounding cloud state as tier 1; the application backup is tier 2 and is documented as blocked while the licence anchor is disconnected.
- Evidence: `cambium-swap/docs/architecture/identity-model.md`; `cambium-swap/docs/dr/backup-strategy.md`.
- Applies to: [Vendor dependency and controller recovery](../../../skill-systems-architect/references/fleet-management.md#vendor-dependency-and-controller-recovery).

**E3. Two-track exit with triggers.** A staged exit over years and an emergency track; triggers include an insolvency appointment and an announced cloud end date, both of which fired.
- Evidence: `cambium-swap/docs/migration/exit-strategy.md`.
- Applies to: [Vendor dependency and controller recovery](../../../skill-systems-architect/references/fleet-management.md#vendor-dependency-and-controller-recovery).

**E4. Adopt by read-back.** The new controller never writes the legacy agent settings while the legacy controller is in service; it records units by reading values back through template bindings.
- Evidence: `unified-network-controller/docs/architecture/provisioning/unc-low-touch-provisioning-design-20260930_0319.md`.
- Applies to: [Vendor dependency and controller recovery](../../../skill-systems-architect/references/fleet-management.md#vendor-dependency-and-controller-recovery).

**E5. Controller rebuilt from code.** The new controller host is rebuilt by infrastructure code, cloud-init and a bootstrap script, with sites onboarded from scratch and no legacy export imported.
- Evidence: `unified-network-controller/ARCHITECTURE.md`; `unified-network-controller/ROADMAP.md`.
- Applies to: [Lifecycle and recovery](../../../skill-systems-architect/references/fleet-management.md#lifecycle-and-recovery).

## Platform decisions and method

**F1. Platform ADR withdrawn for lack of evidence.** The cloud-to-local programme chose about twenty platform products before any inventory existed; the inventory then showed a small container share
of compute. The ADR was withdrawn, and component approval is gated on inventory, utilisation and cost baselines.
- Evidence: `aws-to-local/.archcore/adr/withdraw-platform-baseline.adr.md`; `aws-to-local/docs/platform-approach-revision-plan-rev06-20260728_1723.md`.
- Applies to: [Decision rules (evidence before commitment)](../../references/architecture-method.md#decision-rules).

**F2. Optimised-cloud baseline and a stop gate.** The local option must beat an optimised cloud bill (eliminate, rightsize, then commit); if the benefit is not material after sensitivity analysis, the
programme stops as a success.
- Evidence: `aws-to-local/docs/platform-approach-revision-plan-rev06-20260728_1723.md` (section 6.2.11).
- Applies to: [Decision rules (evidence before commitment)](../../references/architecture-method.md#decision-rules).

**F3. Rack-separation requirement with two readings.** "Separate dedicated racks" read as a rack failure domain in one cluster or as separate clusters; the second doubles the node count. The project
sizes on the second, labels it pending, and asks for the driver.
- Evidence: `aws-to-local/.archcore/rules/size-on-the-unconfirmable-reading.rule.md`.
- Applies to: [Decision rules (evidence before commitment)](../../references/architecture-method.md#decision-rules).

**F4. Paper feasibility screen for the site router.** The site-router plan classifies each required function per model and firmware as native, add-on, central or not possible before any bench, with a
single-veto rule.
- Evidence: `enterprise-strategy/requirements/router-feasibility-test-plan-20261006_1410.md`.
- Applies to: [Decision rules (evidence before commitment)](../../references/architecture-method.md#decision-rules).

**F5. Canary 1 + 5 across sites and both access clusters.** One device of a type end to end, then five more (two from each of three sites, across both access-proxy clusters); the fleet batch runs
later from the script.
- Evidence: `unified-network-controller/docs/engineering/agent-rules-devices-and-sites-20261010_1750.md` (Canary rule).
- Applies to: [Validation tiers](../../references/automation-and-safety.md#validation-tiers).
