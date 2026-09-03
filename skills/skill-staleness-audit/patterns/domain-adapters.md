# Domain adapters

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The nine patterns in `defect-taxonomy.md` are about **claim types**, not about any particular repository layout. This file maps each claim type onto where it actually lives in different kinds of
project, so the audit works outside the governed-markdown corpus it was first extracted from.

**Read the adapter for your domain before Phase 1.** It tells you which surfaces to inventory. The phases, the standard and the checklist are unchanged.

## Contents

- [The six claim types](#the-six-claim-types)
- [Software / codebase](#software--codebase)
- [Research and analysis corpora](#research-and-analysis-corpora)
- [Financial modelling](#financial-modelling)
- [Network and infrastructure](#network-and-infrastructure)
- [Business operations and process](#business-operations-and-process)
- [Data and ML pipelines](#data-and-ml-pipelines)
- [Degrading gracefully](#degrading-gracefully)
- [Building an adapter for a new domain](#building-an-adapter-for-a-new-domain)

---

## The six claim types

Every pattern in the taxonomy is one of these. The taxonomy's nine entries are the common *manifestations*; these six are what they are underneath.

| Claim type | The staleness question |
|---|---|
| **Threshold** | A number that gates a decision — did it move somewhere and not everywhere? |
| **Verdict** | A conclusion, status or recommendation — did the reversal reach every place it is stored? |
| **Count / metadata** | A self-description — does it still match what it describes? |
| **Provenance** | An input's origin — was it ever checked, and against how many observations? |
| **Derived artifact** | Anything generated — does its generator still encode the current model? |
| **Evidence** | A captured record of what an external source said — is it still byte-faithful? |

The audit is the same everywhere: **find the claims, find every copy, find the ones reality has moved past, then make the finding unable to recur.**

## Software / codebase

| Claim type | Where it lives |
|---|---|
| Threshold | Timeouts, retry limits, rate limits, cache TTLs, pagination sizes, feature-flag defaults, SLO targets — duplicated across service config, client config, docs and tests |
| Verdict | Deprecation status, support matrices, "recommended approach" in READMEs and ADRs, `@deprecated` annotations that outlived the removal |
| Count / metadata | "Supports N databases", API version lists, dependency versions in prose vs lockfile, badge claims, example counts |
| Provenance | Magic numbers with no comment; benchmark figures in a README with no date or hardware; "we chose X because it's faster" with no measurement |
| Derived artifact | Generated clients, OpenAPI specs, migrations, protobufs, type stubs, docs sites, lockfiles |
| Evidence | Vendored third-party licences, captured API responses in fixtures, recorded HTTP cassettes |

**Highest-yield first checks.** Config values duplicated between code and docs. A README example that no longer compiles against the current API. A test asserting a constant that was changed only in
source. **Deprecated code paths still referenced in onboarding docs** — the classic band-M finding here, because new people follow them.

**The band-M question:** *does anything here touch auth, money, data deletion, or a public contract?*

## Research and analysis corpora

| Claim type | Where it lives |
|---|---|
| Threshold | Significance levels, inclusion/exclusion criteria, confidence thresholds, sample-size floors |
| Verdict | A finding later contradicted by newer data; a superseded literature position; a retracted source still cited |
| Count / metadata | "N studies reviewed", corpus sizes, date ranges, "last updated" |
| Provenance | A figure quoted without its source, or with a source that no longer says it; secondary citations passed off as primary |
| Derived artifact | Charts, summary tables, generated bibliographies, computed aggregates |
| Evidence | Captured source documents, PDFs, transcripts, scraped pages |

**Highest-yield first checks.** A conclusion in the abstract that the body no longer supports. **A citation chain where the primary source was never read** — the research equivalent of the unverified
purchase price. Retracted or superseded sources still load-bearing.

**The band-M question:** *would anyone make a decision, allocate funding, or publish on the strength of this?*

## Financial modelling

This domain has the sharpest version of every pattern, because the arithmetic is usually right and the inputs usually are not.

| Claim type | Where it lives |
|---|---|
| Threshold | Hurdle rates, discount rates, margin gates, approval limits, covenant thresholds, tax and duty rates |
| Verdict | Buy/hold/sell, go/no-go, "recommended scenario", approval status |
| Count / metadata | Model version, "as at" dates, scenario counts, check counts |
| Provenance | **Every input.** Which are quoted, which observed, which assumed, and how many observations behind each |
| Derived artifact | The workbook itself if generated; exported summaries; board packs; cash-flow projections |
| Evidence | Quotes, rate cards, invoices, market captures, auction records |

**Highest-yield first checks.** A rate treated as a constant when it is an input (tax, duty, FX). **A back-solve — max bid, break-even, required price — computed against a floor that a gate has since
outgrown.** A headline figure resting on a single observation. Both sides of a margin describing different populations.

**The band-M question:** almost everything here is M. Rank within it by *how close to cash* — a bid ceiling outranks a summary table.

**Non-negotiable:** a model passing every formula check can still be confidently wrong, because formula checks validate arithmetic and say nothing about inputs. See `evidence-integrity.md`.

## Network and infrastructure

| Claim type | Where it lives |
|---|---|
| Threshold | MTU, timers, thresholds in alerting rules, capacity limits, IP pool sizes, QoS classes, retention windows |
| Verdict | "Decommissioned", "migrated", "production", device roles, "safe to reboot" |
| Count / metadata | Device counts, site inventories, "N sites migrated", diagram vintages |
| Provenance | A topology diagram with no capture date; an inventory hand-maintained beside a discovered one |
| Derived artifact | Generated configs, templates rendered per device, IaC plans, diagrams from inventory |
| Evidence | Captured `show` output, packet captures, change records, vendor advisories |

**Highest-yield first checks.** **Inventory versus reality** — the definitive staleness domain, because the network changes without telling the documentation. A runbook naming a decommissioned device.
A template variable renamed in one playbook and not another, where the old name **fails silently** rather than erroring. Diagrams with no date.

**The band-M question:** *would following this cause an outage, a security exposure, or a change applied to the wrong device?*

## Business operations and process

| Claim type | Where it lives |
|---|---|
| Threshold | Approval limits, SLAs, escalation triggers, pricing tiers, discount authority |
| Verdict | Vendor status, contract state, "preferred supplier", policy decisions |
| Count / metadata | Headcount, org charts, "last reviewed", policy version |
| Provenance | A price or term with no contract reference; a policy citing superseded legislation |
| Derived artifact | Generated reports, dashboards, exported registers |
| Evidence | Signed contracts, correspondence, regulatory captures |

**Highest-yield first checks.** **Runbooks and templates that get copied per case** — same reasoning as pattern 3, and the most common live-instruction defect in this domain. Approval limits stated in
several policies. Named individuals who have changed role. Legislation cited by superseded section number.

**The band-M question:** *does anyone act on this without checking, or does it go to a regulator, client or auditor?*

## Data and ML pipelines

| Claim type | Where it lives |
|---|---|
| Threshold | Filter criteria, outlier bounds, train/test splits, decision thresholds, drift alarms |
| Verdict | Model selection, "champion" designation, feature importance conclusions |
| Count / metadata | Row counts, feature counts, dataset versions, "trained on data through …" |
| Provenance | Dataset lineage, label sources, which figures came from which run |
| Derived artifact | Trained models, feature stores, generated dashboards, notebooks re-run |
| Evidence | Raw data snapshots, annotation batches, eval sets |

**Highest-yield first checks.** A reported metric from a run whose code has since changed. **A filter applied at display time rather than before aggregation** — the population-matching defect. Eval
sets contaminated by later training data. A "champion" model whose challenger already won.

**The band-M question:** *does a decision, a customer outcome, or a published number depend on this?*

## Degrading gracefully

The phases assume some infrastructure. When it is absent, substitute rather than skip:

| Assumed | If absent | Substitute |
|---|---|---|
| Git | Not version-controlled | Phase 0 snapshot is **mandatory**, not optional — copy the tree before any edit |
| A check suite | No automated checks | Phase 5 **creates the first one**. A single script that fails on one real invariant beats none |
| Generated artifacts | Nothing derived | Skip the generator questions; say so in the report |
| A change log | None | Create one. The reasoning has to land somewhere durable |
| Memory backends | Not configured | Write a dated audit report into the project instead |

**Never report a phase as done because its infrastructure was missing.** Report it as *not applicable, because X does not exist here* — those are different, and the second is often itself a finding.

## Building an adapter for a new domain

1. Take the six claim types.
2. For each, ask **where does this domain physically store that kind of claim?** List the file types, not the individual files.
3. Identify the domain's **silent-failure mode** — the thing that goes wrong without erroring. Networks: a renamed variable that still exits 0. Finance: arithmetic that is right about a wrong input.
   Code: a deprecated path that still works. That failure mode is where the band-M findings concentrate.
4. Write the domain's **band-M question** in one sentence.
5. Add it here.
