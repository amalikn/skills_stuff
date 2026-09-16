# Examples — Fixture Guide

## Contents

- [Files](#files)
- [Reconciliation Scenarios by Row](#reconciliation-scenarios-by-row)
  - [supplier_invoice_sample.csv](#supplier_invoice_samplecsv)
  - [sales_billing_sample.csv](#sales_billing_samplecsv)
- [Validator Test Coverage](#validator-test-coverage)
- [Phase 2 Rate Card Scenarios](#phase-2-rate-card-scenarios)
  - [rate_card_sample.csv](#rate_card_samplecsv)
  - [service_map_sample.csv](#service_map_samplecsv)
- [Phase 3 Trend Detection Scenarios](#phase-3-trend-detection-scenarios)
  - [prior_invoice_sample.csv (February 2026)](#prior_invoice_samplecsv-february-2026)
  - [prior_sales_billing_sample.csv (February 2026)](#prior_sales_billing_samplecsv-february-2026)
- [Notes](#notes)

---

Minimal CSV fixtures for Phase 1A validation tests and Phase 1B reconciliation tests.
Column names deliberately differ from canonical names to exercise the mapping layer.

## Files

| File | Source Type | Purpose |
|---|---|---|
| `supplier_invoice_sample.csv` | `supplier_invoice` | 5 rows covering all Phase 1B reconciliation scenarios |
| `sales_billing_sample.csv` | `sales_billing` | 4 rows as the reconciliation counterpart |
| `mapping_supplier_invoice.yaml` | — | Column map: invoice sample → canonical field names |
| `mapping_sales_billing.yaml` | — | Column map: sales billing sample → canonical field names |
| `rate_card_sample.csv` | `rate_card` | 4 rows — one expected cost per service type (Phase 2) |
| `mapping_rate_card.yaml` | — | Column map: rate card sample → canonical field names |
| `service_map_sample.csv` | `service_map` | 5 rows — supplier_service_id ↔ internal service_id mapping (Phase 2) |
| `mapping_service_map.yaml` | — | Column map: service map sample → canonical field names |
| `prior_invoice_sample.csv` | `supplier_invoice` | 4 rows — February 2026 invoice for MoM comparison (Phase 3) |
| `prior_sales_billing_sample.csv` | `sales_billing` | 3 rows — February 2026 sales for prior-period margin (Phase 3) |

## Reconciliation Scenarios by Row

### supplier_invoice_sample.csv

| Row | AVC ID | Scenario | Expected outcome |
|---|---|---|---|
| 1 | LOC000001 | Matched | Pairs with sales row 1; direct margin = $14.00 |
| 2 | LOC000002 | Invoice only | No sales counterpart; flagged as unmatched |
| 3 | LOC000003 | Amount mismatch | Sales records cost as $48.00; invoice says $52.00; variance = $4.00 (>$0.02 tolerance) |
| 4 | LOC000001 | Duplicate | Exact copy of row 1; flagged as duplicate invoice line |
| 5 | LOC000004 | Matched | Pairs with sales row 4; null description tests null-count detection |

### sales_billing_sample.csv

| Row | Service Ref | Scenario | Expected outcome |
|---|---|---|---|
| 1 | LOC000001 | Matched | Pairs with invoice row 1 |
| 2 | LOC000005 | Sales only | No invoice counterpart; flagged as unmatched |
| 3 | LOC000003 | Amount mismatch | Cost $48.00 vs invoice $52.00; null in Cost ExGST for row 2 tests null-count |
| 4 | LOC000004 | Matched | Pairs with invoice row 5 |

## Validator Test Coverage

These fixtures support the following Phase 1A pytest assertions:

- Valid CSV accepted without error
- Row count reported correctly (invoice: 5, sales: 4)
- Null count detected (invoice description row 5; sales cost row 2)
- Duplicate row detected (invoice rows 1 and 4 are identical)
- Numeric columns identified (`Net Charge`, `GST`, `Revenue ExGST`, `Cost ExGST`)
- Date columns identified (`Inv Date`, `Period From`, `Period To`, `Billing Start`, `Billing End`)
- Source files not modified after validation (hash comparison)

## Phase 2 Rate Card Scenarios

### rate_card_sample.csv

| Service Type | Expected Cost | Fixture outcome |
|---|---|---|
| NBN Fibre 100/20 | $58.00 | LOC000001 matches exactly — no rate variance |
| NBN Copper 25/5 | $35.00 | LOC000002 is invoice_only; rate card used for reference |
| NBN Wireless 25/5 | $50.00 | LOC000003 over-charged: invoice=$52 vs expected=$50 → $2 rate variance |
| NBN Fibre 50/20 | $50.00 | LOC000004 over-charged: invoice=$52 vs expected=$50 → $2 rate variance |

Rate card mismatches expected: 2 (LOC000003, LOC000004).

### service_map_sample.csv

| Supplier ID | Internal ID | Customer | Notes |
|---|---|---|---|
| LOC000001 | SVC-0001 | CUST-001 | Matched to Acme Corp |
| LOC000002 | SVC-0002 | (none) | Invoice-only; no customer assigned |
| LOC000003 | SVC-0003 | CUST-003 | Matched to Gamma Inc |
| LOC000004 | SVC-0004 | CUST-004 | Matched to Delta Ltd |
| LOC000005 | SVC-0005 | CUST-002 | Sales-only; Beta Pty Ltd |

## Phase 3 Trend Detection Scenarios

### prior_invoice_sample.csv (February 2026)

| AVC ID | Present in current (March) | MoM outcome |
|---|---|---|
| LOC000002 | Yes | Tracked in mom_variance — amount increased 18.75%; recurring_change_flag=True |
| LOC000003 | Yes | Tracked in mom_variance — amount more than doubled; spike_flag=True, recurring_change_flag=True |
| LOC000004 | Yes | Tracked in mom_variance — amount stable (0% change); no flags |
| LOC000006 | No (current has LOC000001 instead) | removed_services |

### prior_sales_billing_sample.csv (February 2026)

| Service Ref | Outcome |
|---|---|
| LOC000003 | Prior margin computed: revenue=$60 - cost=$25 = $35; current margin lower → margin_declined=True |
| LOC000004 | Prior margin computed: revenue=$60 - cost=$50 = $10; current margin higher → margin_declined=False |
| LOC000006 | Not joined (removed service — no current matched_lines entry) |

Prior period fixtures use the **same mapping YAMLs** as current period (`mapping_supplier_invoice.yaml`,
`mapping_sales_billing.yaml`). Load with `--name prior_invoice` and `--name prior_sales_billing`.

## Notes

- All amounts are AUD ex GST.
- Current billing period: March 2026. Prior period: February 2026.
- `our_service_id` in sales billing uses the same `LOC*` identifiers as `supplier_service_id`
  in Phase 1 fixtures for simplicity. The `service_map` (Phase 2) provides the canonical
  mapping when supplier and internal IDs diverge.
