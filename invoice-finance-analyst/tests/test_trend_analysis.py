"""
tests/test_trend_analysis.py — Phase 3 trend detection tests.

Prior period fixtures are loaded from examples/ automatically if not in db/.
Current period parquets (invoice, sales_billing, matched_lines) must already
exist from Phase 1B skeleton run.

Fixture scenario (prior period = February 2026):

  Prior invoice (4 rows):
    LOC000002  NBN Copper 25/5   $32.00  → current=$38.00  change=+18.75%  recurring_change=True
    LOC000003  NBN Wireless 25/5 $25.00  → current=$52.00  change=+108%    spike=True
    LOC000004  NBN Fibre 50/20   $50.00  → current=$52.00  change=+4%      stable (no flags)
    LOC000006  NBN Copper 25/5   $38.00  → not in current  → removed

  Current invoice (after dedup, 4 rows):
    LOC000001  NBN Fibre 100/20  $58.00  → not in prior    → new service
    LOC000002  (tracked above)
    LOC000003  (tracked above)
    LOC000004  (tracked above)

  Expected:
    mom_variance         : 3 rows (LOC000002, LOC000003, LOC000004)
    new_services         : 1 row  (LOC000001)
    removed_services     : 1 row  (LOC000006)
    usage_spikes         : 1 row  (LOC000003)
    recurring_changes    : 2 rows (LOC000002 + LOC000003)
    margin_movement      : 2 rows (LOC000003, LOC000004 — in both current matched + prior)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.trend_analysis import (
    RECURRING_CHANGE_THRESHOLD_PCT,
    USAGE_SPIKE_MULTIPLIER,
    build_margin_movement,
    build_mom_variance,
    build_new_services,
    build_phase3_assumptions,
    build_recurring_changes,
    build_removed_services,
    build_usage_spikes,
    run_trend_analysis,
)

ROOT     = Path(__file__).parent.parent
DB       = ROOT / "db"
EXAMPLES = ROOT / "examples"

INVOICE_PQ       = DB / "invoice.parquet"
SALES_PQ         = DB / "sales_billing.parquet"
MATCHED_PQ       = DB / "matched_lines.parquet"
PRIOR_INVOICE_PQ = DB / "prior_invoice.parquet"
PRIOR_SALES_PQ   = DB / "prior_sales_billing.parquet"


# ---------------------------------------------------------------------------
# Session-scoped setup: load prior period parquets if absent
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def ensure_phase3_db():
    from scripts.load_inputs import ingest

    if not PRIOR_INVOICE_PQ.exists():
        ingest(
            EXAMPLES / "prior_invoice_sample.csv",
            EXAMPLES / "mapping_supplier_invoice.yaml",
            parquet_name="prior_invoice",
        )

    if not PRIOR_SALES_PQ.exists():
        ingest(
            EXAMPLES / "prior_sales_billing_sample.csv",
            EXAMPLES / "mapping_sales_billing.yaml",
            parquet_name="prior_sales_billing",
        )

    for label, p in [("invoice", INVOICE_PQ), ("sales_billing", SALES_PQ),
                     ("matched_lines", MATCHED_PQ)]:
        if not p.exists():
            pytest.skip(f"db/{label}.parquet not found — run invoice_analysis_skeleton.py first")


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def current_inv() -> pd.DataFrame:
    return pd.read_parquet(INVOICE_PQ)


@pytest.fixture(scope="module")
def prior_inv() -> pd.DataFrame:
    return pd.read_parquet(PRIOR_INVOICE_PQ)


@pytest.fixture(scope="module")
def current_sales() -> pd.DataFrame:
    return pd.read_parquet(SALES_PQ)


@pytest.fixture(scope="module")
def prior_sales() -> pd.DataFrame:
    return pd.read_parquet(PRIOR_SALES_PQ)


@pytest.fixture(scope="module")
def matched() -> pd.DataFrame:
    return pd.read_parquet(MATCHED_PQ)


@pytest.fixture(scope="module")
def mom_variance(current_inv, prior_inv) -> pd.DataFrame:
    return build_mom_variance(current_inv, prior_inv)


@pytest.fixture(scope="module")
def new_services(current_inv, prior_inv) -> pd.DataFrame:
    return build_new_services(current_inv, prior_inv)


@pytest.fixture(scope="module")
def removed_services(current_inv, prior_inv) -> pd.DataFrame:
    return build_removed_services(current_inv, prior_inv)


@pytest.fixture(scope="module")
def usage_spikes(mom_variance) -> pd.DataFrame:
    return build_usage_spikes(mom_variance)


@pytest.fixture(scope="module")
def recurring_changes(mom_variance) -> pd.DataFrame:
    return build_recurring_changes(mom_variance)


@pytest.fixture(scope="module")
def margin_movement(matched, prior_inv, prior_sales) -> pd.DataFrame:
    return build_margin_movement(matched, prior_inv, prior_sales)


@pytest.fixture(scope="module")
def run_result(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("phase3_output")
    return run_trend_analysis(
        INVOICE_PQ, PRIOR_INVOICE_PQ,
        SALES_PQ, PRIOR_SALES_PQ,
        MATCHED_PQ, output_dir=out,
    )


# ---------------------------------------------------------------------------
# Prior period input shape
# ---------------------------------------------------------------------------

class TestPriorInput:
    def test_prior_invoice_row_count(self, prior_inv):
        assert len(prior_inv) == 4

    def test_prior_sales_row_count(self, prior_sales):
        assert len(prior_sales) == 3

    def test_prior_has_amount_col(self, prior_inv):
        assert "amount_ex_tax" in prior_inv.columns

    def test_prior_has_service_id(self, prior_inv):
        assert "supplier_service_id" in prior_inv.columns

    def test_prior_invoice_includes_loc000006(self, prior_inv):
        ids = prior_inv["supplier_service_id"].astype(str).tolist()
        assert "LOC000006" in ids

    def test_prior_invoice_excludes_loc000001(self, prior_inv):
        ids = prior_inv["supplier_service_id"].astype(str).tolist()
        assert "LOC000001" not in ids


# ---------------------------------------------------------------------------
# MoM variance
# ---------------------------------------------------------------------------

class TestMomVariance:
    def test_three_tracked_services(self, mom_variance):
        # Services in both periods: LOC000002, LOC000003, LOC000004
        assert len(mom_variance) == 3

    def test_has_required_columns(self, mom_variance):
        required = {
            "supplier_service_id", "current_amount", "prior_amount",
            "abs_change", "pct_change", "spike_flag", "recurring_change_flag",
        }
        assert required.issubset(set(mom_variance.columns))

    def test_loc000002_change(self, mom_variance):
        # prior=$32, current=$38, change=+18.75%
        row = mom_variance[mom_variance["supplier_service_id"] == "LOC000002"].iloc[0]
        assert row["prior_amount"]   == pytest.approx(32.00, abs=0.01)
        assert row["current_amount"] == pytest.approx(38.00, abs=0.01)
        assert row["abs_change"]     == pytest.approx(6.00,  abs=0.01)
        assert row["pct_change"]     == pytest.approx(6 / 32, abs=0.001)
        assert row["spike_flag"]             == False
        assert row["recurring_change_flag"]  == True   # 18.75% > 5%

    def test_loc000003_spike(self, mom_variance):
        # prior=$25, current=$52, change=+108%
        row = mom_variance[mom_variance["supplier_service_id"] == "LOC000003"].iloc[0]
        assert row["prior_amount"]   == pytest.approx(25.00, abs=0.01)
        assert row["current_amount"] == pytest.approx(52.00, abs=0.01)
        assert row["spike_flag"]             == True   # 52 > 25*2=50
        assert row["recurring_change_flag"]  == True   # 108% > 5%

    def test_loc000004_stable(self, mom_variance):
        # prior=$50, current=$52, change=+4% — below all thresholds
        row = mom_variance[mom_variance["supplier_service_id"] == "LOC000004"].iloc[0]
        assert row["prior_amount"]   == pytest.approx(50.00, abs=0.01)
        assert row["current_amount"] == pytest.approx(52.00, abs=0.01)
        assert row["spike_flag"]             == False
        assert row["recurring_change_flag"]  == False   # 4% < 5%

    def test_loc000001_not_tracked(self, mom_variance):
        # LOC000001 is new (not in prior) — must not appear in mom_variance
        assert "LOC000001" not in mom_variance["supplier_service_id"].values

    def test_loc000006_not_tracked(self, mom_variance):
        # LOC000006 is removed (not in current) — must not appear in mom_variance
        assert "LOC000006" not in mom_variance["supplier_service_id"].values


# ---------------------------------------------------------------------------
# New services
# ---------------------------------------------------------------------------

class TestNewServices:
    def test_one_new_service(self, new_services):
        assert len(new_services) == 1

    def test_loc000001_is_new(self, new_services):
        assert "LOC000001" in new_services["supplier_service_id"].values

    def test_has_amount_col(self, new_services):
        assert "amount_ex_tax" in new_services.columns


# ---------------------------------------------------------------------------
# Removed services
# ---------------------------------------------------------------------------

class TestRemovedServices:
    def test_one_removed_service(self, removed_services):
        assert len(removed_services) == 1

    def test_loc000006_is_removed(self, removed_services):
        assert "LOC000006" in removed_services["supplier_service_id"].values

    def test_prior_amount_present(self, removed_services):
        row = removed_services[removed_services["supplier_service_id"] == "LOC000006"].iloc[0]
        assert row["amount_ex_tax"] == pytest.approx(38.00, abs=0.01)


# ---------------------------------------------------------------------------
# Usage spikes
# ---------------------------------------------------------------------------

class TestUsageSpikes:
    def test_one_spike(self, usage_spikes):
        assert len(usage_spikes) == 1

    def test_loc000003_is_spike(self, usage_spikes):
        assert "LOC000003" in usage_spikes["supplier_service_id"].values

    def test_spike_exceeds_multiplier(self, usage_spikes):
        row = usage_spikes.iloc[0]
        assert row["current_amount"] > row["prior_amount"] * USAGE_SPIKE_MULTIPLIER

    def test_threshold_value(self):
        assert USAGE_SPIKE_MULTIPLIER == pytest.approx(2.0, abs=1e-6)

    def test_synthetic_spike_detected(self):
        """Verify spike detection fires at just above 2× threshold."""
        # prior=$100, current=$201 → 201 > 100*2=200 → True
        df = pd.DataFrame([
            {"supplier_service_id": "SVC-A", "amount_ex_tax": 100.0},
        ])
        df2 = pd.DataFrame([
            {"supplier_service_id": "SVC-A", "amount_ex_tax": 201.0},
        ])
        mv = build_mom_variance(df2, df)
        assert mv.iloc[0]["spike_flag"] == True

    def test_synthetic_below_spike_not_flagged(self):
        """Verify exactly 2× is not flagged (strict greater-than)."""
        # prior=$100, current=$200 → 200 > 100*2=200 → False
        df = pd.DataFrame([
            {"supplier_service_id": "SVC-B", "amount_ex_tax": 100.0},
        ])
        df2 = pd.DataFrame([
            {"supplier_service_id": "SVC-B", "amount_ex_tax": 200.0},
        ])
        mv = build_mom_variance(df2, df)
        assert mv.iloc[0]["spike_flag"] == False


# ---------------------------------------------------------------------------
# Recurring changes
# ---------------------------------------------------------------------------

class TestRecurringChanges:
    def test_two_recurring_changes(self, recurring_changes):
        # LOC000002 (18.75%) and LOC000003 (108%) both exceed 5%
        assert len(recurring_changes) == 2

    def test_loc000002_flagged(self, recurring_changes):
        assert "LOC000002" in recurring_changes["supplier_service_id"].values

    def test_loc000003_flagged(self, recurring_changes):
        assert "LOC000003" in recurring_changes["supplier_service_id"].values

    def test_loc000004_not_flagged(self, recurring_changes):
        assert "LOC000004" not in recurring_changes["supplier_service_id"].values

    def test_threshold_value(self):
        assert RECURRING_CHANGE_THRESHOLD_PCT == pytest.approx(0.05, abs=1e-6)

    def test_all_exceed_threshold(self, recurring_changes):
        assert (recurring_changes["pct_change"].abs() > RECURRING_CHANGE_THRESHOLD_PCT).all()


# ---------------------------------------------------------------------------
# Margin movement
# ---------------------------------------------------------------------------

class TestMarginMovement:
    def test_two_services_tracked(self, margin_movement):
        # LOC000003 and LOC000004 are in both current matched and prior
        # LOC000001 is new → not in prior → excluded from inner join
        assert len(margin_movement) == 2

    def test_has_required_columns(self, margin_movement):
        required = {
            "supplier_service_id",
            "direct_margin_ex_tax", "direct_margin_pct",
            "prior_margin", "prior_margin_pct",
            "margin_delta_abs", "margin_delta_pct_pts", "margin_declined",
        }
        assert required.issubset(set(margin_movement.columns))

    def test_loc000003_margin_declined(self, margin_movement):
        # Current: revenue=$63, cost=$52 → margin=$11 (17.5%)
        # Prior:   revenue=$60, cost=$25 → margin=$35 (58.3%)
        # Delta: 11 - 35 = -$24 → declined
        row = margin_movement[margin_movement["supplier_service_id"] == "LOC000003"].iloc[0]
        assert row["direct_margin_ex_tax"] == pytest.approx(11.00, abs=0.01)
        assert row["prior_margin"]         == pytest.approx(35.00, abs=0.01)
        assert row["margin_delta_abs"]     == pytest.approx(-24.00, abs=0.01)
        assert row["margin_declined"]      == True

    def test_loc000004_margin_improved(self, margin_movement):
        # Current: revenue=$65, cost=$52 → margin=$13 (20%)
        # Prior:   revenue=$60, cost=$50 → margin=$10 (16.7%)
        # Delta: 13 - 10 = +$3 → improved
        row = margin_movement[margin_movement["supplier_service_id"] == "LOC000004"].iloc[0]
        assert row["direct_margin_ex_tax"] == pytest.approx(13.00, abs=0.01)
        assert row["prior_margin"]         == pytest.approx(10.00, abs=0.01)
        assert row["margin_delta_abs"]     == pytest.approx(3.00, abs=0.01)
        assert row["margin_declined"]      == False

    def test_loc000001_excluded_new_service(self, margin_movement):
        # LOC000001 is new — no prior data — excluded from margin movement
        assert "LOC000001" not in margin_movement["supplier_service_id"].values


# ---------------------------------------------------------------------------
# Phase 3 assumptions
# ---------------------------------------------------------------------------

class TestPhase3Assumptions:
    def test_has_required_keys(self):
        assumptions = build_phase3_assumptions()
        keys = set(assumptions["assumption_key"])
        assert "usage_spike_multiplier"          in keys
        assert "recurring_change_threshold_pct"  in keys
        assert "mom_comparison_key"              in keys
        assert "prior_margin_source"             in keys

    def test_spike_multiplier_value(self):
        assumptions = build_phase3_assumptions()
        row = assumptions[assumptions["assumption_key"] == "usage_spike_multiplier"].iloc[0]
        assert float(row["value"]) == USAGE_SPIKE_MULTIPLIER

    def test_all_rows_have_source(self):
        assumptions = build_phase3_assumptions()
        assert assumptions["source"].notna().all()


# ---------------------------------------------------------------------------
# End-to-end run
# ---------------------------------------------------------------------------

class TestEndToEndPhase3:
    def test_run_completes(self, run_result):
        assert "run_id" in run_result
        assert len(run_result["run_id"]) == 8

    def test_all_tables_present(self, run_result):
        expected = {
            "mom_variance", "new_services", "removed_services",
            "usage_spikes", "recurring_changes",
            "margin_movement", "phase3_assumptions",
        }
        assert expected.issubset(set(run_result["tables"].keys()))

    def test_output_parquets_written(self):
        expected = [
            "mom_variance", "new_services", "removed_services",
            "usage_spikes", "recurring_changes",
            "margin_movement", "phase3_assumptions",
        ]
        for name in expected:
            assert (DB / f"{name}.parquet").exists(), f"Missing: db/{name}.parquet"

    def test_output_markdown_written(self, run_result):
        out_dir = Path(run_result["output_dir"])
        for name in ["mom_variance", "new_services", "removed_services",
                     "usage_spikes", "recurring_changes", "margin_movement"]:
            assert (out_dir / f"{name}.md").exists(), f"Missing: {name}.md"

    def test_new_services_count(self, run_result):
        assert len(run_result["tables"]["new_services"]) == 1

    def test_removed_services_count(self, run_result):
        assert len(run_result["tables"]["removed_services"]) == 1

    def test_usage_spikes_count(self, run_result):
        assert len(run_result["tables"]["usage_spikes"]) == 1

    def test_recurring_changes_count(self, run_result):
        assert len(run_result["tables"]["recurring_changes"]) == 2

    def test_margin_movement_count(self, run_result):
        assert len(run_result["tables"]["margin_movement"]) == 2
