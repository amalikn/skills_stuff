---
Title: Service provider OSS/BSS systems
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  OSS/BSS architecture for a retail ISP that buys access from nbn, a private fibre network and an aggregator: service identifiers and join keys, order and
  assurance flows, billing timing, three-source reconciliation, raw versus enriched data, product catalogue lifecycle, cost allocation, voice platform systems
  and data quality checks.
---

# Service provider OSS/BSS systems

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Identifiers and join keys](#identifiers-and-join-keys)
- [Billing timing and the service-month grain](#billing-timing-and-the-service-month-grain)
- [Reconciliation pipeline](#reconciliation-pipeline)
- [Catalogue, cost allocation and voice](#catalogue-cost-allocation-and-voice)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- The systems side of wholesale access: identifiers, order, qualification and assurance flows, usage and billing feeds, and the data model that joins them.
- Billing and reconciliation pipelines: supplier invoice, supplier service report and own billing, checked every cycle.
- Product catalogue lifecycle, shared-cost allocation, and voice platform systems (PBX lifecycle, number-to-service lookup).
- Network constructs (AVC/CVC capacity, POI, NNI, traffic classes) belong to skill-network-architect. Line-by-line invoice checks, rate-card variance and margin reports belong to skill-ifa
  (internal-invoice-analysis); this file says what the pipeline must provide, not how to audit an invoice.
- Database engines and replication: [databases-and-ha](databases-and-ha.md). Pipeline storage: [storage-and-data](storage-and-data.md).

## Decision rules

- One atomic grain for cost and revenue: one row per service per month. Every report aggregates up from it, never down.
- Keep raw supplier data and enriched data in separate lineages. A derived file never feeds back into the raw flow.
- Every money column is a number with a stated currency and tax basis at ingestion, never text. PostgreSQL recommends `numeric` for monetary amounts and warns against floating point. VERIFIED_PRIMARY,
  [pg-numeric], checked 2026-10-29.
- The PostgreSQL `money` type formats by `lc_monetary`; a restore into a database with a different setting may fail. Prefer `numeric` plus a currency column. VERIFIED_PRIMARY, [pg-money], checked
  2026-10-29.
- Store every figure with one tax basis (in Australia, wholesale figures are usually ex-GST) and a flag per source column; convert at ingestion. USER_STATED convention; confirm the basis on each
  supplier file.
- A reconciliation compares against an independent oracle. A check of a data set against itself cannot fail and proves nothing (see [architecture method](architecture-method.md#decision-rules)).
- Validate a supplier invoice against two oracles: the rate the supplier applied and the contracted rate. An invoice can be internally consistent and still above contract. Keep contract rates as slabs
  with effective dates. Procedure: skill-ifa.
- Every charge type has an explicit service-period rule (advance, catch-up or arrears). Never derive the service month from a charge start date alone.
- Fail closed when an enrichment input is missing (usage export, rebate file, mapping row). A guessed fallback silently corrupts every downstream figure.

## Identifiers and join keys

Identify each object by the supplier key for that object, and record the key per supplier in a data dictionary.

| Object           | nbn key                        | Private fibre / aggregator   | Own systems                       |
| ---------------- | ------------------------------ | ---------------------------- | --------------------------------- |
| Premises         | Location ID: `LOC` + 12 digits | supplier site or premises ID | address record, location ID       |
| Access circuit   | AVC ID: `AVC` + 12 digits      | supplier access ID           | service record -> AVC             |
| Product instance | PRI (product instance ID)      | supplier service record      | product subscription              |
| Shared capacity  | CVC / OVC IDs                  | aggregator OVC or bandwidth  | capacity pool record              |
| Telephone number | n/a                            | carrier service number       | number inventory (DID -> service) |

- AVC ID is `AVC` followed by 12 digits and authorises a transfer between providers. VERIFIED_PRIMARY, [acma-avc], checked 2026-10-29.
- Location ID example `LOC000033782101` appears in the nbn WBA operations manual (2011 edition). VERIFIED_PRIMARY for the format at that date, [nbn-ops].
- PRI format and current B2B field names: UNVERIFIED. Read the current nbn WBA documents before coding a validator.
- A private fibre network issues its own access identifiers; do not reuse nbn validators for them.
- Normalise types before joining. A numeric ID read as float loses digits or gains `.0`; keep identifiers as text with a format check.
- Measure join coverage on every run: matched, unmatched left, unmatched right. A falling match rate is a data defect, not a business result.

```text
IDENTIFIER MODEL: one premises, one access circuit, one or more services and numbers

+-------------+  1   n  +----------------+  1   1  +------------------+  1   n  +-----------------+
| premises    |-------->| access circuit |-------->| service (BSS)    |-------->| number (DID)    |
| LOC ID      |         | AVC ID or      |         | service record,  |         | E.164, carrier  |
|             |         | supplier ID    |         | plan, customer   |         | service number  |
+-------------+         +----------------+         +------------------+         +-----------------+
                                |                            |
                                v                            v
                        +----------------+          +------------------+
                        | shared pool    |          | service-month row|
                        | CVC/OVC, NNI,  |--alloc-->| cost, revenue,   |
                        | backhaul       |          | basis labels     |
                        +----------------+          +------------------+
```

Order, qualification and assurance at concept level (supplier B2B portals and APIs implement these; names vary by supplier):

| Flow                  | Input key         | Output that the OSS must store                     | Reconciled against               |
| --------------------- | ----------------- | -------------------------------------------------- | -------------------------------- |
| Service qualification | address -> LOC ID | technology, available tiers, install requirements  | order outcome                    |
| Order (connect)       | LOC ID, product   | AVC/PRI, appointment, activation date              | first invoice line for the AVC   |
| Modify (re-rate)      | AVC/PRI, new tier | effective date of the new speed profile            | invoice tier vs retail plan      |
| Disconnect / churn    | AVC/PRI           | cease date, transfer-out flag                      | last advance line and catch-up   |
| Assurance (fault)     | AVC/PRI or LOC ID | ticket ID, timestamps, outcome, rebate eligibility | supplier ticket and rebate lines |

- The nbn B2B specification models location qualification and order management as separate processes. VERIFIED_PRIMARY (2011-era documents), [nbn-ops]; the current interface may differ.
- Activation in the OSS and billing start in the BSS are separate events. A bulk activation that skips the BSS step leaves cost without revenue.

## Billing timing and the service-month grain

| Charge pattern      | Billed when                                | Service month it belongs to                   | Pipeline rule                          |
| ------------------- | ------------------------------------------ | --------------------------------------------- | -------------------------------------- |
| Advance rental      | at the start of the month it covers        | the invoice month                             | one full month per active service      |
| Catch-up (pro-rata) | on a later invoice                         | the earlier partial month (activation, churn) | attribute back; cost of M can land M+1 |
| Arrears (usage)     | after the usage period, often same invoice | the prior month                               | use the event or period date           |
| One-off             | when incurred                              | the event date                                | tag with the order or ticket ID        |
| Credit or rebate    | when granted                               | the period it compensates, if stated          | keep separate from the rate it offsets |

- The pro-rata denominator (days in month, a fixed figure, or other) is a supplier rule. Derive it from invoice traces and encode it per supplier.
- Usage joins use the event date. The bill month is for invoice totals only; late-billed usage otherwise lands in the wrong month.
- A discount stated as a percentage has a base. Two systems computing the same percentage on different bases never reconcile; model the base explicitly.

## Reconciliation pipeline

Reconcile three sources every cycle: the supplier invoice, the supplier service report (their list of active services and profiles) and the own billing (BSS) service book. Exceptions are the work
queue.

```text
THREE-SOURCE MONTHLY RECONCILIATION: exceptions, not totals, are the output

+------------------+   +--------------------+   +-------------------+
| supplier invoice |   | supplier service   |   | own billing (BSS) |
| (charges)        |   | report (actives)   |   | service book      |
+--------+---------+   +---------+----------+   +---------+---------+
         |                       |                        |
         v                       v                        v
+--------------------------------------------------------------------+
| raw layer: typed, immutable, dated per supplier file               |
+--------------------------------------------------------------------+
         |  normalise keys (AVC, LOC, service record, number)
         v
+--------------------------------------------------------------------+
| service-month rows: one per service per month, basis labelled      |
+--------------------------------------------------------------------+
         |
         +--> billed, not active in BSS         -> cost leak queue
         +--> active in BSS, not billed         -> revenue or supplier gap
         +--> tier billed != retail plan tier   -> profile-match queue
         +--> billed at rate != contract slab   -> skill-ifa contract check
         +--> capacity billed, not in inventory -> ghost circuit queue
```

- Reconcile capacity inventory (CVC, OVC, NNI) to the latest invoice, never to the inventory file it was built from.
- Keep raw and enriched lineages apart. Enrichment adds subsidies, imputed revenue and allocated pools; each figure carries a basis label (supplier, imputed, allocated estimate) so a reader knows what
  was measured.
- Keep dated, immutable snapshots of every input and rebuild the query layer from them. Diffing two snapshots shows what changed; the analysis store is disposable.
- File drop to typed columnar files to an analysis engine is enough at small-ISP scale; dashboards read a loaded copy, not the analysis files.
- Subsidised or government-funded services are a separate service class with their own funding source and join key. Keep them out of commercial averages and track their net cost.

## Catalogue, cost allocation and voice

Product catalogue lifecycle:

```text
CATALOGUE STATES: a retail product points at one supplier product per state change

+-------+   +----------+   +-----------+   +----------------+   +--------+
| draft |-->| on sale  |-->| cease     |-->| exit (supplier |-->| closed |
|       |   |          |   | sale      |   | withdraws)     |   |        |
+-------+   +----------+   +-----------+   +----------------+   +--------+
                               |                  ^
                               +-- migration plan-+   every in-life service moved before exit
```

- Record cease-sale and exit dates from the supplier price list in the catalogue, with the mapping from retail plan to wholesale product and speed tier.
- A rate-card change is a coordinated change set (catalogue, mapping, validation rules). Verify the product identity and effective date of a rate card before comparing invoices to it.

Shared-cost allocation:

- Only the access circuit is a direct per-service charge. Shared pools (capacity, NNI, backhaul, transit, data centre) need a stated allocation rule.
- Allocate by measured usage (average or busy-hour throughput per service). Treat pool values as configurable estimates until sourced, and fail closed when the usage input for the month is missing.

Voice platform systems:

- Number-to-service mapping lives in a database the dialplan queries, not in static dialplan. The same table is the number inventory that billing attribution needs.
- Classify every carrier voice charge to a product line by joining its number to each product inventory. Keep an internal-number register so own usage (support lines, call-centre numbers) shows as
  overhead.
- Asterisk LTS releases get 4 years of full support plus 1 year of security fixes; standard releases at least 1 + 1. VERIFIED_PRIMARY, [asterisk-versions], checked 2026-10-29.
- Dates on that page, checked 2026-10-29: 20.x LTS security-fix-only from 2026-10-19, EOL 2027-10-19; 22.x LTS EOL 2029-10-16; 24.x LTS released 2026-10-15, EOL 2031-10-15. Re-read the page before
  planning; the table changes.
- `chan_sip` was deprecated in Asterisk 17 and is not included from Asterisk 21. VERIFIED_PRIMARY, [asterisk-chan-sip], checked 2026-10-29. An estate on `chan_sip` must move to PJSIP before it can
  upgrade past 20.
- Carriage of emergency calls (000, and 112 on mobile) and location information is a regulatory obligation on the provider of the voice service. VERIFIED_SECONDARY, [acma-emergency], checked
  2026-10-29. Test emergency calling and caller ID after every trunk reroute.

## Patterns and anti-patterns

| Situation                         | Do                                                | Avoid                                   | Why                                             |
| --------------------------------- | ------------------------------------------------- | --------------------------------------- | ----------------------------------------------- |
| Choosing the fact-table grain     | one row per service per month                     | invoice-line grain for margin reports   | invoice lines double count catch-up and credits |
| Money from supplier files         | cast to `numeric` at ingestion, assert row counts | filter on a text column such as `'$20'` | a text comparison drops rows without an error   |
| Checking a capacity inventory     | compare to the latest supplier invoice            | compare the inventory to its own export | a self-check reports zero anomalies forever     |
| Invoice validation                | applied rate and contracted rate, separately      | one rate check                          | a correct-looking invoice can ignore a contract |
| Enriching cost data               | separate lineage, basis label on every figure     | overwrite raw columns with estimates    | nobody can tell measured from allocated later   |
| Missing usage file for allocation | stop the enrichment run                           | reuse last month or an average          | the error spreads into every service            |
| DID routing                       | database lookup from the dialplan                 | numbers hard-coded per context          | the dialplan becomes the only number inventory  |

## Failure modes and tests

| Failure                                     | Signal                                           | Test that proves detection and recovery                       |
| ------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| Service billed by supplier, absent from BSS | cost with no revenue for the service-month       | seed one billed AVC with no BSS row; it lands in the queue    |
| Wrong default speed tier on bulk activation | wholesale tier above retail plan tier            | seed a mismatch; profile-match check flags it in the cycle    |
| Arrears usage bucketed by charge start date | usage spikes in the wrong month                  | replay a known month; usage matches the event-date total      |
| Identifier type drift (float, lost zeros)   | join coverage drops                              | feed an ID as float; ingestion rejects it with a format error |
| Missing enrichment input                    | run completes with fallback values               | remove the usage file; the run must stop non-zero             |
| Ghost capacity circuit                      | billed OVC/CVC absent from the inventory         | add one invoice line with no inventory row; it is flagged     |
| Voice platform past end of life             | no security fixes; module absent in next version | inventory versions against the vendor table every quarter     |

## Worked example

Illustrative arithmetic only (invented units, not supplier figures). One month, one shared backhaul pool of 900 cost units, three services with measured average throughput 2, 3 and 4 Mbit/s.

| Step                          | Arithmetic               | Result                                 |
| ----------------------------- | ------------------------ | -------------------------------------- |
| Total measured usage          | 2 + 3 + 4                | 9 Mbit/s                               |
| Service A share               | 900 x 2 / 9              | 200 units, basis "allocated"           |
| Service B share               | 900 x 3 / 9              | 300 units, basis "allocated"           |
| Service C share               | 900 x 4 / 9              | 400 units, basis "allocated"           |
| Service C activates on day 20 | catch-up on next invoice | cost row for this month, billed in M+1 |
| Usage file missing next month | run stops; no allocation | exit non-zero, queue item              |

- The allocated rows carry the basis label, so a margin report shows how much of each service cost is measured and how much is estimated.

## Review checklist

- [ ] Data dictionary names the key per object and per supplier; identifiers stored as text with a format check
- [ ] Fact grain is one row per service per month; reports only aggregate up
- [ ] Every charge type has an advance, catch-up or arrears rule and a pro-rata rule per supplier
- [ ] Three-source reconciliation runs every cycle; exception queues have owners
- [ ] Capacity inventory reconciled to the latest invoice, not to itself
- [ ] Money stored as `numeric` with currency and tax basis; row counts asserted after each filter
- [ ] Raw and enriched lineages separate; every enriched figure carries a basis label
- [ ] Enrichment fails closed on a missing input
- [ ] Catalogue holds cease-sale and exit dates with a migration plan per affected product
- [ ] Number inventory is the database the dialplan reads; voice platform versions tracked against the vendor table
- [ ] Invoice line checks and contract-rate checks handed to skill-ifa

## Further reading

Links checked 2026-10-29.

- [acma-avc]: ACMA, NBN access transfer and the AVC ID; the identifier format and its role in a transfer.
- [nbn-ops]: nbn WBA operations manual (2011); identifier examples and RSP ticket actions. Old; confirm against the current WBA.
- [Communications Alliance AVC ID fact sheet](https://www.commsalliance.com.au/wp-content/uploads/2025/06/AVC-ID-Fact-Sheet_2025.pdf): industry view of the AVC ID.
- [pg-numeric]: PostgreSQL numeric types; why money uses `numeric`, not floating point.
- [pg-money]: PostgreSQL `money` type and its locale dependence.
- [asterisk-versions]: Asterisk release series, LTS and standard support periods and dates.
- [asterisk-chan-sip]: Asterisk project notice of the `chan_sip` removal in version 21.
- [acma-emergency]: ACMA emergency call obligations for providers.
- [Uniti acquisition of OptiComm](https://www.itnews.com.au/news/opticomm-snapped-up-by-uniti-for-532m-549274): ownership of the private fibre network (secondary).
- [Parquet file metadata](https://parquet.apache.org/docs/file-format/metadata/): footer key-value metadata for snapshot provenance.

[acma-avc]: https://www.acma.gov.au/test-nbn-service-working
[nbn-ops]: https://mobile.nbnco.com.au/content/dam/nbnco/presentations/wba-operations-manual-final-16-aug-11.pdf
[pg-numeric]: https://www.postgresql.org/docs/current/datatype-numeric.html
[pg-money]: https://www.postgresql.org/docs/current/datatype-money.html
[asterisk-versions]: https://docs.asterisk.org/About-the-Project/Asterisk-Versions/
[asterisk-chan-sip]: https://www.asterisk.org/asterisk-21-module-removal-chan_sip/
[acma-emergency]: https://www.acma.gov.au/emergency-calls
