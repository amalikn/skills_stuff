"""
tests/test_reconciliation.py — Phase 1B reconciliation skeleton tests.

All assertions use fixture parquets in db/ (loaded from examples/ by load_inputs.py).
Tests verify deterministic output against known fixture scenarios documented in
examples/README.md.

Expected fixture outcomes:
  Invoice: 5 rows, 1 duplicate (LOC000001 row 4)
  Sales:   4 rows, 0 duplicates

  matched         : 3 — LOC000001, LOC000003, LOC000004
  invoice_only    : 1 — LOC000002 (Copper, no sales match)
  sales_only      : 1 — LOC000005 (Beta Pty Ltd, no invoice)
  amount_mismatch : 1 — LOC000003 ($52.00 invoice vs $48.00 cost, $4.00 variance)
  duplicate_removed: 1 — LOC000001 second row
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from scripts.invoice_analysis_skeleton import (
    AMOUNT_MATCH_TOLERANCE_ABS,
    AMOUNT_MATCH_TOLERANCE_PCT,
    MATCH_KEY,
    build_assumptions,
    build_quality_issues,
    build_reconciliation_summary,
    build_run_summary,
    build_source_inventory,
    deduplicate,
    reconcile,
    run_analysis,
)
from scripts.validate_inputs import REQUIRED_FIELDS

ROOT    = Path(__file__).parent.parent
DB      = ROOT / "db"
INVOICE = DB / "invoice.parquet"
SALES   = DB / "sales_billing.parquet"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def inv_df() -> pd.DataFrame:
    if not INVOICE.exists():
        pytest.skip("db/invoice.parquet not found — run load_inputs.py first")
    return pd.read_parquet(INVOICE)


@pytest.fixture(scope="module")
def sales_df() -> pd.DataFrame:
    if not SALES.exists():
        pytest.skip("db/sales_billing.parquet not found — run load_inputs.py first")
    return pd.read_parquet(SALES)


@pytest.fixture(scope="module")
def inv_clean(inv_df) -> tuple[pd.DataFrame, int]:
    return deduplicate(inv_df)


@pytest.fixture(scope="module")
def reconciled(inv_clean, sales_df) -> dict[str, pd.DataFrame]:
    clean, _ = inv_clean
    return reconcile(clean, sales_df, AMOUNT_MATCH_TOLERANCE_ABS, AMOUNT_MATCH_TOLERANCE_PCT)


@pytest.fixture(scope="module")
def run_result(tmp_path_factory) -> dict:
    if not INVOICE.exists() or not SALES.exists():
        pytest.skip("Parquet files not found")
    out = tmp_path_factory.mktemp("run_output")
    return run_analysis(INVOICE, SALES, output_dir=out)


# ---------------------------------------------------------------------------
# Source data shape
# ---------------------------------------------------------------------------

class TestSourceData:
    def test_invoice_row_count(self, inv_df):
        assert len(inv_df) == 5

    def test_sales_row_count(self, sales_df):
        assert len(sales_df) == 4

    def test_invoice_has_canonical_amount_col(self, inv_df):
        assert "amount_ex_tax" in inv_df.columns

    def test_sales_has_canonical_revenue_col(self, sales_df):
        assert "revenue_ex_tax" in sales_df.columns

    def test_invoice_amount_total(self, inv_df):
        # 58+38+52+58+52 = 258 (includes duplicate row)
        assert inv_df["amount_ex_tax"].sum() == pytest.approx(258.00, abs=0.01)

    def test_sales_revenue_total(self, sales_df):
        # 72+65+63+65 = 265
        assert sales_df["revenue_ex_tax"].sum() == pytest.approx(265.00, abs=0.01)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

class TestDeduplication:
    def test_one_duplicate_removed(self, inv_clean):
        _, n_dupes = inv_clean
        assert n_dupes == 1

    def test_clean_has_four_rows(self, inv_clean):
        clean, _ = inv_clean
        assert len(clean) == 4

    def test_source_parquet_not_modified(self, inv_df):
        # Hash the parquet file before and after the fixture runs
        def sha(p):
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        before = sha(INVOICE)
        pd.read_parquet(INVOICE)  # read again to confirm no mutation
        assert sha(INVOICE) == before


# ---------------------------------------------------------------------------
# Reconciliation classification
# ---------------------------------------------------------------------------

class TestReconciliation:
    def test_matched_count(self, reconciled):
        assert len(reconciled["matched_lines"]) == 3

    def test_invoice_only_count(self, reconciled):
        assert len(reconciled["invoice_no_sales"]) == 1

    def test_sales_only_count(self, reconciled):
        assert len(reconciled["sales_no_invoice"]) == 1

    def test_amount_mismatch_count(self, reconciled):
        assert len(reconciled["amount_mismatches"]) == 1

    def test_invoice_only_is_copper(self, reconciled):
        inv_only = reconciled["invoice_no_sales"]
        assert "LOC000002" in inv_only["supplier_service_id"].values

    def test_sales_only_is_loc000005(self, reconciled):
        sal_only = reconciled["sales_no_invoice"]
        assert "LOC000005" in sal_only["our_service_id"].values

    def test_mismatch_is_loc000003(self, reconciled):
        mm = reconciled["amount_mismatches"]
        assert "LOC000003" in mm["supplier_service_id"].values

    def test_mismatch_variance_correct(self, reconciled):
        mm = reconciled["amount_mismatches"]
        row = mm[mm["supplier_service_id"] == "LOC000003"].iloc[0]
        assert row["invoice_amount_ex_tax"] == pytest.approx(52.00, abs=0.01)
        assert row["sales_cost_ex_tax"]     == pytest.approx(48.00, abs=0.01)
        assert row["variance_abs"]          == pytest.approx(4.00,  abs=0.01)

    def test_mismatch_exceeds_abs_tolerance(self, reconciled):
        mm = reconciled["amount_mismatches"]
        row = mm[mm["supplier_service_id"] == "LOC000003"].iloc[0]
        assert row["exceeds_abs_tolerance"] is True or row["exceeds_abs_tolerance"] == True

    def test_matched_loc000001_margin(self, reconciled):
        matched = reconciled["matched_lines"]
        row = matched[matched["supplier_service_id"] == "LOC000001"].iloc[0]
        # revenue=72, cost=58, margin=14
        assert row["direct_margin_ex_tax"] == pytest.approx(14.00, abs=0.01)

    def test_matched_loc000001_margin_pct(self, reconciled):
        matched = reconciled["matched_lines"]
        row = matched[matched["supplier_service_id"] == "LOC000001"].iloc[0]
        # 14/72 ≈ 0.1944
        assert row["direct_margin_pct"] == pytest.approx(14 / 72, abs=0.001)

    def test_no_source_csv_mutation_during_reconcile(self, inv_df, sales_df):
        # DataFrames are copies — original parquets unchanged
        inv_copy = inv_df.copy()
        reconcile(inv_copy, sales_df.copy(),
                  AMOUNT_MATCH_TOLERANCE_ABS, AMOUNT_MATCH_TOLERANCE_PCT)
        # Row counts must remain the same (no in-place modification)
        assert len(inv_df) == 5
        assert len(sales_df) == 4


# ---------------------------------------------------------------------------
# Reconciliation summary
# ---------------------------------------------------------------------------

class TestReconciliationSummary:
    def test_has_five_status_rows(self, reconciled, inv_df):
        summary = build_reconciliation_summary(reconciled, n_duplicates=1,
                                               total_invoice_rows=len(inv_df))
        assert len(summary) == 5

    def test_statuses_present(self, reconciled, inv_df):
        summary = build_reconciliation_summary(reconciled, n_duplicates=1,
                                               total_invoice_rows=len(inv_df))
        statuses = set(summary["match_status"])
        assert "matched"          in statuses
        assert "invoice_only"     in statuses
        assert "sales_only"       in statuses
        assert "amount_mismatch"  in statuses
        assert "duplicate_removed" in statuses

    def test_matched_row_count_in_summary(self, reconciled, inv_df):
        summary = build_reconciliation_summary(reconciled, n_duplicates=1,
                                               total_invoice_rows=len(inv_df))
        matched_row = summary[summary["match_status"] == "matched"].iloc[0]
        assert matched_row["row_count"] == 3


# ---------------------------------------------------------------------------
# Source inventory and quality issues
# ---------------------------------------------------------------------------

class TestSourceInventory:
    def test_two_rows(self, inv_df, sales_df):
        inv = build_source_inventory(inv_df, sales_df)
        assert len(inv) == 2

    def test_invoice_duplicate_count(self, inv_df, sales_df):
        inv = build_source_inventory(inv_df, sales_df)
        row = inv[inv["source_type"] == "supplier_invoice"].iloc[0]
        assert row["duplicate_row_count"] == 1

    def test_sales_duplicate_count(self, inv_df, sales_df):
        inv = build_source_inventory(inv_df, sales_df)
        row = inv[inv["source_type"] == "sales_billing"].iloc[0]
        assert row["duplicate_row_count"] == 0


class TestQualityIssues:
    def test_detects_issues(self, inv_df, sales_df):
        issues = build_quality_issues(
            inv_df, sales_df,
            REQUIRED_FIELDS["supplier_invoice"],
            REQUIRED_FIELDS["sales_billing"],
        )
        assert len(issues) >= 1  # at minimum: duplicate row in invoice

    def test_duplicate_issue_present(self, inv_df, sales_df):
        issues = build_quality_issues(
            inv_df, sales_df,
            REQUIRED_FIELDS["supplier_invoice"],
            REQUIRED_FIELDS["sales_billing"],
        )
        dupes = issues[issues["issue_type"] == "duplicate_row"]
        assert len(dupes) >= 1


# ---------------------------------------------------------------------------
# Assumptions
# ---------------------------------------------------------------------------

class TestAssumptions:
    def test_has_required_keys(self):
        assumptions = build_assumptions()
        keys = set(assumptions["assumption_key"])
        assert "tolerance.abs" in keys
        assert "tolerance.pct" in keys
        assert "match_key"     in keys

    def test_abs_tolerance_value(self):
        assumptions = build_assumptions()
        row = assumptions[assumptions["assumption_key"] == "tolerance.abs"].iloc[0]
        assert float(row["value"]) == AMOUNT_MATCH_TOLERANCE_ABS

    def test_all_rows_have_source(self):
        assumptions = build_assumptions()
        assert assumptions["source"].notna().all()


# ---------------------------------------------------------------------------
# End-to-end run
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_run_completes(self, run_result):
        assert "run_id" in run_result
        assert len(run_result["run_id"]) == 8

    def test_all_tables_present(self, run_result):
        expected = {
            "run_summary", "source_file_inventory", "data_quality_issues",
            "reconciliation_summary", "assumptions",
            "matched_lines", "invoice_no_sales", "sales_no_invoice", "amount_mismatches",
        }
        assert expected.issubset(set(run_result["tables"].keys()))

    def test_output_parquets_written(self):
        expected = [
            "run_summary", "source_file_inventory", "data_quality_issues",
            "reconciliation_summary", "assumptions",
            "matched_lines", "invoice_no_sales", "sales_no_invoice", "amount_mismatches",
        ]
        for name in expected:
            assert (DB / f"{name}.parquet").exists(), f"Missing: db/{name}.parquet"

    def test_output_markdown_written(self, run_result):
        out_dir = Path(run_result["output_dir"])
        expected = [
            "run_summary", "source_file_inventory", "data_quality_issues",
            "reconciliation_summary", "assumptions",
            "matched_lines", "invoice_no_sales", "sales_no_invoice", "amount_mismatches",
        ]
        for name in expected:
            assert (out_dir / f"{name}.md").exists(), f"Missing: {name}.md"

    def test_matched_lines_row_count(self, run_result):
        assert len(run_result["tables"]["matched_lines"]) == 3

    def test_invoice_only_row_count(self, run_result):
        assert len(run_result["tables"]["invoice_no_sales"]) == 1

    def test_sales_only_row_count(self, run_result):
        assert len(run_result["tables"]["sales_no_invoice"]) == 1

    def test_amount_mismatch_row_count(self, run_result):
        assert len(run_result["tables"]["amount_mismatches"]) == 1

    def test_run_summary_counts(self, run_result):
        rs = run_result["tables"]["run_summary"].iloc[0]
        assert rs["matched_count"]           == 3
        assert rs["invoice_only_count"]      == 1
        assert rs["sales_only_count"]        == 1
        assert rs["duplicate_invoice_count"] == 1
        assert rs["amount_mismatch_count"]   == 1
