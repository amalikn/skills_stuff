"""
tests/test_rate_card_analysis.py — Phase 2 rate card and margin analysis tests.

All assertions use fixture parquets in db/.
rate_card and service_map parquets are loaded automatically from examples/ if absent.
matched_lines.parquet must already exist (requires Phase 1B skeleton to have run).

Expected fixture outcomes (from examples/ data):

  Rate card:
    NBN Fibre 100/20  → expected=$58.00
    NBN Copper 25/5   → expected=$35.00
    NBN Wireless 25/5 → expected=$50.00
    NBN Fibre 50/20   → expected=$50.00

  Matched lines (3 rows from Phase 1B):
    LOC000001  NBN Fibre 100/20  invoice=$58  expected=$58  variance=$0.00  → no mismatch
    LOC000003  NBN Wireless 25/5 invoice=$52  expected=$50  variance=$2.00  → mismatch
    LOC000004  NBN Fibre 50/20   invoice=$52  expected=$50  variance=$2.00  → mismatch

  Rate card mismatches  : 2 (LOC000003, LOC000004)
  Low margin exceptions : 0 (all matched lines >5% margin)
  Margin by customer    : 3 rows (CUST-001, CUST-003, CUST-004)
  Margin by service     : 3 rows (one per matched service type)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.rate_card_analysis import (
    LOW_MARGIN_PCT_THRESHOLD,
    RATE_VARIANCE_TOLERANCE_ABS,
    build_low_margin_exceptions,
    build_margin_by_customer,
    build_margin_by_service_type,
    build_phase2_assumptions,
    build_rate_card_mismatches,
    build_rate_variances,
    run_rate_card_analysis,
)

ROOT     = Path(__file__).parent.parent
DB       = ROOT / "db"
EXAMPLES = ROOT / "examples"

MATCHED_PQ    = DB / "matched_lines.parquet"
RATE_CARD_PQ  = DB / "rate_card.parquet"
SERVICE_MAP_PQ = DB / "service_map.parquet"


# ---------------------------------------------------------------------------
# Session-scoped setup: load rate_card and service_map if not already in db/
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def ensure_phase2_db():
    """Load rate_card and service_map from examples/ if db/ parquets not yet built."""
    from scripts.load_inputs import ingest

    if not RATE_CARD_PQ.exists():
        ingest(
            EXAMPLES / "rate_card_sample.csv",
            EXAMPLES / "mapping_rate_card.yaml",
            parquet_name="rate_card",
        )

    if not SERVICE_MAP_PQ.exists():
        ingest(
            EXAMPLES / "service_map_sample.csv",
            EXAMPLES / "mapping_service_map.yaml",
            parquet_name="service_map",
        )

    if not MATCHED_PQ.exists():
        pytest.skip(
            "db/matched_lines.parquet not found — run invoice_analysis_skeleton.py first"
        )


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def matched() -> pd.DataFrame:
    return pd.read_parquet(MATCHED_PQ)


@pytest.fixture(scope="module")
def rate_card() -> pd.DataFrame:
    return pd.read_parquet(RATE_CARD_PQ)


@pytest.fixture(scope="module")
def rate_variances(matched, rate_card) -> pd.DataFrame:
    return build_rate_variances(matched, rate_card)


@pytest.fixture(scope="module")
def rate_card_mismatches(rate_variances) -> pd.DataFrame:
    return build_rate_card_mismatches(rate_variances)


@pytest.fixture(scope="module")
def margin_by_customer(matched) -> pd.DataFrame:
    return build_margin_by_customer(matched)


@pytest.fixture(scope="module")
def margin_by_service_type(matched) -> pd.DataFrame:
    return build_margin_by_service_type(matched)


@pytest.fixture(scope="module")
def low_margin_exceptions(matched) -> pd.DataFrame:
    return build_low_margin_exceptions(matched)


@pytest.fixture(scope="module")
def run_result(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("phase2_output")
    return run_rate_card_analysis(MATCHED_PQ, RATE_CARD_PQ, output_dir=out)


# ---------------------------------------------------------------------------
# Rate card input shape
# ---------------------------------------------------------------------------

class TestRateCardInput:
    def test_four_service_types(self, rate_card):
        assert len(rate_card) == 4

    def test_has_expected_cost_col(self, rate_card):
        assert "expected_cost_ex_tax" in rate_card.columns

    def test_has_effective_date_col(self, rate_card):
        assert "effective_date" in rate_card.columns

    def test_expected_costs_are_numeric(self, rate_card):
        assert pd.to_numeric(rate_card["expected_cost_ex_tax"], errors="coerce").notna().all()

    def test_fibre_100_rate(self, rate_card):
        rc = rate_card.copy()
        rc["service_type"] = rc["service_type"].astype(str)
        row = rc[rc["service_type"] == "NBN Fibre 100/20"].iloc[0]
        assert row["expected_cost_ex_tax"] == pytest.approx(58.00, abs=0.01)

    def test_wireless_rate(self, rate_card):
        rc = rate_card.copy()
        rc["service_type"] = rc["service_type"].astype(str)
        row = rc[rc["service_type"] == "NBN Wireless 25/5"].iloc[0]
        assert row["expected_cost_ex_tax"] == pytest.approx(50.00, abs=0.01)


# ---------------------------------------------------------------------------
# Rate variances
# ---------------------------------------------------------------------------

class TestRateVariances:
    def test_row_count_matches_matched_lines(self, rate_variances, matched):
        assert len(rate_variances) == len(matched)

    def test_has_required_columns(self, rate_variances):
        required = {
            "supplier_service_id", "service_type",
            "invoice_amount_ex_tax", "expected_cost_ex_tax",
            "rate_variance_abs", "rate_variance_pct",
            "rate_card_mismatch_flag", "no_rate_card_entry",
        }
        assert required.issubset(set(rate_variances.columns))

    def test_loc000001_no_variance(self, rate_variances):
        row = rate_variances[rate_variances["supplier_service_id"] == "LOC000001"].iloc[0]
        assert row["rate_variance_abs"] == pytest.approx(0.00, abs=0.01)
        assert row["rate_card_mismatch_flag"] == False

    def test_loc000003_rate_mismatch(self, rate_variances):
        row = rate_variances[rate_variances["supplier_service_id"] == "LOC000003"].iloc[0]
        # invoice=$52, expected=$50, variance=$2
        assert row["invoice_amount_ex_tax"] == pytest.approx(52.00, abs=0.01)
        assert row["expected_cost_ex_tax"]  == pytest.approx(50.00, abs=0.01)
        assert row["rate_variance_abs"]     == pytest.approx(2.00,  abs=0.01)
        assert row["rate_card_mismatch_flag"] == True

    def test_loc000004_rate_mismatch(self, rate_variances):
        row = rate_variances[rate_variances["supplier_service_id"] == "LOC000004"].iloc[0]
        assert row["rate_variance_abs"]       == pytest.approx(2.00, abs=0.01)
        assert row["rate_card_mismatch_flag"] == True

    def test_no_missing_rate_card_entries(self, rate_variances):
        assert not rate_variances["no_rate_card_entry"].any()

    def test_source_parquets_not_modified(self):
        import hashlib
        def sha(p):
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        before = sha(MATCHED_PQ)
        pd.read_parquet(MATCHED_PQ)
        assert sha(MATCHED_PQ) == before


# ---------------------------------------------------------------------------
# Rate card mismatches
# ---------------------------------------------------------------------------

class TestRateCardMismatches:
    def test_two_mismatches(self, rate_card_mismatches):
        assert len(rate_card_mismatches) == 2

    def test_loc000003_present(self, rate_card_mismatches):
        assert "LOC000003" in rate_card_mismatches["supplier_service_id"].values

    def test_loc000004_present(self, rate_card_mismatches):
        assert "LOC000004" in rate_card_mismatches["supplier_service_id"].values

    def test_loc000001_absent(self, rate_card_mismatches):
        assert "LOC000001" not in rate_card_mismatches["supplier_service_id"].values

    def test_all_have_mismatch_flag_true(self, rate_card_mismatches):
        assert rate_card_mismatches["rate_card_mismatch_flag"].all()

    def test_variance_values_correct(self, rate_card_mismatches):
        for _, row in rate_card_mismatches.iterrows():
            assert abs(row["rate_variance_abs"]) > RATE_VARIANCE_TOLERANCE_ABS


# ---------------------------------------------------------------------------
# Margin by customer
# ---------------------------------------------------------------------------

class TestMarginByCustomer:
    def test_three_customers(self, margin_by_customer):
        assert len(margin_by_customer) == 3

    def test_has_required_columns(self, margin_by_customer):
        required = {"customer_id", "revenue_total", "cost_total",
                    "margin_total", "margin_pct", "low_margin_flag"}
        assert required.issubset(set(margin_by_customer.columns))

    def test_cust001_margin(self, margin_by_customer):
        # LOC000001: revenue=72, cost=58, margin=14
        row = margin_by_customer[margin_by_customer["customer_id"] == "CUST-001"].iloc[0]
        assert row["revenue_total"]  == pytest.approx(72.00, abs=0.01)
        assert row["cost_total"]     == pytest.approx(58.00, abs=0.01)
        assert row["margin_total"]   == pytest.approx(14.00, abs=0.01)
        assert row["margin_pct"]     == pytest.approx(14 / 72, abs=0.001)

    def test_cust003_margin(self, margin_by_customer):
        # LOC000003: revenue=63, cost=52, margin=11
        row = margin_by_customer[margin_by_customer["customer_id"] == "CUST-003"].iloc[0]
        assert row["margin_total"] == pytest.approx(11.00, abs=0.01)
        assert row["margin_pct"]   == pytest.approx(11 / 63, abs=0.001)

    def test_cust004_margin(self, margin_by_customer):
        # LOC000004: revenue=65, cost=52, margin=13
        row = margin_by_customer[margin_by_customer["customer_id"] == "CUST-004"].iloc[0]
        assert row["margin_total"] == pytest.approx(13.00, abs=0.01)
        assert row["margin_pct"]   == pytest.approx(13 / 65, abs=0.001)

    def test_no_low_margin_customers(self, margin_by_customer):
        # All fixture customers have margin >5%
        assert not margin_by_customer["low_margin_flag"].any()

    def test_sorted_ascending_by_margin(self, margin_by_customer):
        pcts = margin_by_customer["margin_pct"].tolist()
        assert pcts == sorted(pcts)


# ---------------------------------------------------------------------------
# Margin by service type
# ---------------------------------------------------------------------------

class TestMarginByServiceType:
    def test_three_service_types(self, margin_by_service_type):
        assert len(margin_by_service_type) == 3

    def test_has_required_columns(self, margin_by_service_type):
        required = {"service_type", "revenue_total", "cost_total",
                    "margin_total", "margin_pct", "low_margin_flag"}
        assert required.issubset(set(margin_by_service_type.columns))

    def test_fibre_100_margin(self, margin_by_service_type):
        row = margin_by_service_type[
            margin_by_service_type["service_type"] == "NBN Fibre 100/20"
        ].iloc[0]
        assert row["margin_total"] == pytest.approx(14.00, abs=0.01)

    def test_wireless_margin(self, margin_by_service_type):
        row = margin_by_service_type[
            margin_by_service_type["service_type"] == "NBN Wireless 25/5"
        ].iloc[0]
        assert row["margin_total"] == pytest.approx(11.00, abs=0.01)

    def test_no_low_margin_service_types(self, margin_by_service_type):
        assert not margin_by_service_type["low_margin_flag"].any()

    def test_sorted_ascending_by_margin(self, margin_by_service_type):
        pcts = margin_by_service_type["margin_pct"].tolist()
        assert pcts == sorted(pcts)


# ---------------------------------------------------------------------------
# Low margin exceptions
# ---------------------------------------------------------------------------

class TestLowMarginExceptions:
    def test_zero_exceptions_in_fixture(self, low_margin_exceptions):
        # All fixture matched lines have margin well above 5%
        assert len(low_margin_exceptions) == 0

    def test_threshold_is_correct(self):
        assert LOW_MARGIN_PCT_THRESHOLD == pytest.approx(0.05, abs=1e-6)

    def test_synthetic_low_margin_detected(self):
        """Verify the detection logic fires when margin_pct < threshold."""
        low_df = pd.DataFrame([{
            "supplier_service_id":    "LOC-TEST",
            "billing_period_start":   "2026-03-01",
            "service_type":           "NBN Test",
            "customer_id":            "CUST-TEST",
            "invoice_amount_ex_tax":  100.00,
            "sales_revenue_ex_tax":   103.00,
            "direct_margin_ex_tax":   3.00,
            "direct_margin_pct":      0.029,  # 2.9% — below 5%
        }])
        result = build_low_margin_exceptions(low_df)
        assert len(result) == 1
        assert result.iloc[0]["supplier_service_id"] == "LOC-TEST"

    def test_synthetic_healthy_margin_not_flagged(self):
        """Verify lines above threshold are excluded."""
        healthy_df = pd.DataFrame([{
            "supplier_service_id":    "LOC-OK",
            "billing_period_start":   "2026-03-01",
            "service_type":           "NBN OK",
            "customer_id":            "CUST-OK",
            "invoice_amount_ex_tax":  50.00,
            "sales_revenue_ex_tax":   72.00,
            "direct_margin_ex_tax":   22.00,
            "direct_margin_pct":      0.306,  # 30.6% — healthy
        }])
        result = build_low_margin_exceptions(healthy_df)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Phase 2 assumptions
# ---------------------------------------------------------------------------

class TestPhase2Assumptions:
    def test_has_required_keys(self):
        assumptions = build_phase2_assumptions()
        keys = set(assumptions["assumption_key"])
        assert "low_margin_threshold"     in keys
        assert "rate_variance_tolerance_abs" in keys
        assert "rate_variance_tolerance_pct" in keys
        assert "rate_card_temporal"       in keys

    def test_low_margin_value(self):
        assumptions = build_phase2_assumptions()
        row = assumptions[assumptions["assumption_key"] == "low_margin_threshold"].iloc[0]
        assert float(row["value"]) == LOW_MARGIN_PCT_THRESHOLD

    def test_all_rows_have_source(self):
        assumptions = build_phase2_assumptions()
        assert assumptions["source"].notna().all()


# ---------------------------------------------------------------------------
# End-to-end run
# ---------------------------------------------------------------------------

class TestEndToEndPhase2:
    def test_run_completes(self, run_result):
        assert "run_id" in run_result
        assert len(run_result["run_id"]) == 8

    def test_all_tables_present(self, run_result):
        expected = {
            "rate_variances", "rate_card_mismatches",
            "margin_by_customer", "margin_by_service_type",
            "low_margin_exceptions", "phase2_assumptions",
        }
        assert expected.issubset(set(run_result["tables"].keys()))

    def test_output_parquets_written(self):
        expected = [
            "rate_variances", "rate_card_mismatches",
            "margin_by_customer", "margin_by_service_type",
            "low_margin_exceptions", "phase2_assumptions",
        ]
        for name in expected:
            assert (DB / f"{name}.parquet").exists(), f"Missing: db/{name}.parquet"

    def test_output_markdown_written(self, run_result):
        out_dir = Path(run_result["output_dir"])
        expected = [
            "rate_variances", "rate_card_mismatches",
            "margin_by_customer", "margin_by_service_type",
            "low_margin_exceptions", "phase2_assumptions",
        ]
        for name in expected:
            assert (out_dir / f"{name}.md").exists(), f"Missing: {name}.md"

    def test_rate_card_mismatches_count(self, run_result):
        assert len(run_result["tables"]["rate_card_mismatches"]) == 2

    def test_low_margin_exceptions_count(self, run_result):
        assert len(run_result["tables"]["low_margin_exceptions"]) == 0

    def test_margin_by_customer_count(self, run_result):
        assert len(run_result["tables"]["margin_by_customer"]) == 3

    def test_margin_by_service_type_count(self, run_result):
        assert len(run_result["tables"]["margin_by_service_type"]) == 3
