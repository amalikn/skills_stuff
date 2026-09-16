"""
trend_analysis.py — Phase 3: MoM trend detection.

Compares current period invoice/sales parquets against prior period parquets.
Detects: new/removed services, usage spikes, recurring charge changes, margin movement.

Required inputs (from load_inputs.py):
  db/invoice.parquet              — current period invoice
  db/sales_billing.parquet        — current period sales
  db/prior_invoice.parquet        — prior period invoice (same format, prior month)
  db/prior_sales_billing.parquet  — prior period sales

Also reads (from invoice_analysis_skeleton.py):
  db/matched_lines.parquet        — for margin_movement calculation

Output tables:
  mom_variance          — per-service MoM invoice amount change
  new_services          — supplier_service_id in current invoice, not in prior
  removed_services      — supplier_service_id in prior invoice, not in current
  usage_spikes          — services where current > prior × USAGE_SPIKE_MULTIPLIER
  recurring_changes     — services where abs(pct_change) > RECURRING_CHANGE_THRESHOLD_PCT
  margin_movement       — per-service margin delta vs prior period

Usage:
    python scripts/trend_analysis.py
    python scripts/trend_analysis.py \\
        --invoice db/invoice.parquet \\
        --prior-invoice db/prior_invoice.parquet \\
        --sales db/sales_billing.parquet \\
        --prior-sales db/prior_sales_billing.parquet
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Thresholds — from SKILL.md Phase 3 calibration (vocus-profitability data)
# ---------------------------------------------------------------------------

USAGE_SPIKE_MULTIPLIER         = 2.0   # 2× prior — stable NBN billing; 2× = investigate
RECURRING_CHANGE_THRESHOLD_PCT = 0.05  # 5% — contractual rates; >5% MoM needs explanation

ROOT = Path(__file__).parent.parent
DB   = ROOT / "db"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _write_parquet(df: pd.DataFrame, name: str) -> Path:
    dest = DB / f"{name}.parquet"
    df.to_parquet(dest, index=False, compression="snappy")
    return dest


def _write_markdown(df: pd.DataFrame, name: str, run_dir: Path, title: str = "") -> Path:
    dest = run_dir / f"{name}.md"
    lines = []
    if title:
        lines.append(f"# {title}\n")
    lines.append(f"_Rows: {len(df)}_\n")
    lines.append(df.to_markdown(index=False))
    lines.append("")
    dest.write_text("\n".join(lines))
    return dest


def _service_ids(df: pd.DataFrame) -> set[str]:
    """Unique supplier_service_id values as strings."""
    return set(df["supplier_service_id"].astype(str).unique())


def _agg_by_service(df: pd.DataFrame, amount_col: str) -> pd.DataFrame:
    """Sum amount_col per supplier_service_id. Returns (supplier_service_id, amount)."""
    d = df.copy()
    d["supplier_service_id"] = d["supplier_service_id"].astype(str)
    return (
        d.groupby("supplier_service_id", observed=True)
         .agg(amount=(amount_col, "sum"))
         .reset_index()
    )


# ---------------------------------------------------------------------------
# MoM variance
# ---------------------------------------------------------------------------

def build_mom_variance(current_inv: pd.DataFrame, prior_inv: pd.DataFrame) -> pd.DataFrame:
    """
    Per-service invoice amount comparison for services present in BOTH periods.
    Flags spikes (current > prior × multiplier) and recurring changes (>5% change).
    """
    cur = _agg_by_service(current_inv, "amount_ex_tax").rename(columns={"amount": "current_amount"})
    pri = _agg_by_service(prior_inv, "amount_ex_tax").rename(columns={"amount": "prior_amount"})

    merged = cur.merge(pri, on="supplier_service_id", how="inner")

    merged["abs_change"] = (merged["current_amount"] - merged["prior_amount"]).round(4)
    merged["pct_change"] = (merged["abs_change"] / merged["prior_amount"]).round(6)
    merged["spike_flag"] = (
        merged["current_amount"] > merged["prior_amount"] * USAGE_SPIKE_MULTIPLIER
    )
    merged["recurring_change_flag"] = merged["pct_change"].abs() > RECURRING_CHANGE_THRESHOLD_PCT

    return merged.sort_values("supplier_service_id").reset_index(drop=True)


# ---------------------------------------------------------------------------
# New / removed services
# ---------------------------------------------------------------------------

def build_new_services(current_inv: pd.DataFrame, prior_inv: pd.DataFrame) -> pd.DataFrame:
    """Services in current invoice period not present in prior invoice period."""
    new_ids = _service_ids(current_inv) - _service_ids(prior_inv)
    d = current_inv.copy()
    d["supplier_service_id"] = d["supplier_service_id"].astype(str)
    cols = ["supplier_service_id", "billing_period_start", "service_type", "amount_ex_tax"]
    available = [c for c in cols if c in d.columns]
    return (
        d[d["supplier_service_id"].isin(new_ids)][available]
        .drop_duplicates(subset=["supplier_service_id"])
        .sort_values("supplier_service_id")
        .reset_index(drop=True)
    )


def build_removed_services(current_inv: pd.DataFrame, prior_inv: pd.DataFrame) -> pd.DataFrame:
    """Services in prior invoice period not present in current invoice period."""
    removed_ids = _service_ids(prior_inv) - _service_ids(current_inv)
    d = prior_inv.copy()
    d["supplier_service_id"] = d["supplier_service_id"].astype(str)
    cols = ["supplier_service_id", "billing_period_start", "service_type", "amount_ex_tax"]
    available = [c for c in cols if c in d.columns]
    return (
        d[d["supplier_service_id"].isin(removed_ids)][available]
        .drop_duplicates(subset=["supplier_service_id"])
        .sort_values("supplier_service_id")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Exception subsets
# ---------------------------------------------------------------------------

def build_usage_spikes(mom_variance: pd.DataFrame) -> pd.DataFrame:
    """MoM variance rows where spike_flag is True."""
    return mom_variance[mom_variance["spike_flag"] == True].copy().reset_index(drop=True)


def build_recurring_changes(mom_variance: pd.DataFrame) -> pd.DataFrame:
    """MoM variance rows where recurring_change_flag is True."""
    return mom_variance[mom_variance["recurring_change_flag"] == True].copy().reset_index(drop=True)


# ---------------------------------------------------------------------------
# Margin movement
# ---------------------------------------------------------------------------

def build_margin_movement(
    current_matched: pd.DataFrame,
    prior_inv: pd.DataFrame,
    prior_sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Per-service margin delta for services matched in the current period that also
    appeared in the prior period. Prior margin is computed directly from prior
    invoice + prior sales without requiring a prior skeleton run.
    """
    # Align prior sales join key
    ps = prior_sales.copy()
    if "our_service_id" in ps.columns and "supplier_service_id" not in ps.columns:
        ps = ps.rename(columns={"our_service_id": "supplier_service_id"})
    ps["supplier_service_id"] = ps["supplier_service_id"].astype(str)

    pi = prior_inv.copy()
    pi["supplier_service_id"] = pi["supplier_service_id"].astype(str)

    # Inner join prior invoice to prior sales
    prior_merged = pi.merge(
        ps[["supplier_service_id", "revenue_ex_tax"]],
        on="supplier_service_id",
        how="inner",
    )
    prior_merged["prior_margin"] = (
        prior_merged["revenue_ex_tax"] - prior_merged["amount_ex_tax"]
    ).round(4)

    prior_agg = (
        prior_merged.groupby("supplier_service_id")
        .agg(
            prior_margin  =("prior_margin", "sum"),
            prior_revenue =("revenue_ex_tax", "sum"),
        )
        .reset_index()
    )
    prior_agg["prior_margin_pct"] = (
        prior_agg["prior_margin"] / prior_agg["prior_revenue"]
    ).round(6)

    # Join to current matched lines
    cur = current_matched.copy()
    cur["supplier_service_id"] = cur["supplier_service_id"].astype(str)

    merged = cur.merge(
        prior_agg[["supplier_service_id", "prior_margin", "prior_margin_pct"]],
        on="supplier_service_id",
        how="inner",
    )
    merged["margin_delta_abs"] = (
        merged["direct_margin_ex_tax"] - merged["prior_margin"]
    ).round(4)
    merged["margin_delta_pct_pts"] = (
        merged["direct_margin_pct"] - merged["prior_margin_pct"]
    ).round(6)
    merged["margin_declined"] = merged["margin_delta_abs"] < 0

    cols = [
        "supplier_service_id", "billing_period_start",
        "direct_margin_ex_tax", "direct_margin_pct",
        "prior_margin", "prior_margin_pct",
        "margin_delta_abs", "margin_delta_pct_pts", "margin_declined",
    ]
    return merged[[c for c in cols if c in merged.columns]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Phase 3 assumptions
# ---------------------------------------------------------------------------

def build_phase3_assumptions() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "assumption_key": "usage_spike_multiplier",
            "value":          str(USAGE_SPIKE_MULTIPLIER),
            "rationale":      "NBN is stable recurring billing; 2× prior = billing anomaly or provisioning error",
            "source":         "default",
        },
        {
            "assumption_key": "recurring_change_threshold_pct",
            "value":          str(RECURRING_CHANGE_THRESHOLD_PCT),
            "rationale":      "Contractual AVC rates should not drift >5% MoM without a rate card update",
            "source":         "default",
        },
        {
            "assumption_key": "mom_comparison_key",
            "value":          "supplier_service_id",
            "rationale":      "Services identified by supplier_service_id across periods; billing_period differs by design",
            "source":         "default",
        },
        {
            "assumption_key": "prior_margin_source",
            "value":          "prior_invoice + prior_sales (direct join, no skeleton run required)",
            "rationale":      "Prior matched_lines.parquet not required; margin derived inline from prior period files",
            "source":         "default",
        },
    ])


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def run_trend_analysis(
    current_inv_pq:   Path,
    prior_inv_pq:     Path,
    current_sales_pq: Path,
    prior_sales_pq:   Path,
    matched_pq:       Path,
    output_dir:       Path | None = None,
) -> dict:
    run_id = str(uuid.uuid4())[:8]
    run_ts = _now()

    if output_dir is None:
        output_dir = ROOT / "output" / f"phase3_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    DB.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Phase 3 Trend Analysis: {run_id} ===")
    print(f"  current invoice : {current_inv_pq.name}")
    print(f"  prior invoice   : {prior_inv_pq.name}")

    # --- load ---
    current_inv   = pd.read_parquet(current_inv_pq)
    prior_inv     = pd.read_parquet(prior_inv_pq)
    current_sales = pd.read_parquet(current_sales_pq)
    prior_sales   = pd.read_parquet(prior_sales_pq)
    matched       = pd.read_parquet(matched_pq)

    print(f"\n  Current invoice rows : {len(current_inv)}")
    print(f"  Prior invoice rows   : {len(prior_inv)}")

    # --- build tables ---
    print("\nBuilding Phase 3 tables...")
    mom_variance       = build_mom_variance(current_inv, prior_inv)
    new_services       = build_new_services(current_inv, prior_inv)
    removed_services   = build_removed_services(current_inv, prior_inv)
    usage_spikes       = build_usage_spikes(mom_variance)
    recurring_changes  = build_recurring_changes(mom_variance)
    margin_movement    = build_margin_movement(matched, prior_inv, prior_sales)
    phase3_assumptions = build_phase3_assumptions()

    all_tables = {
        "mom_variance":        mom_variance,
        "new_services":        new_services,
        "removed_services":    removed_services,
        "usage_spikes":        usage_spikes,
        "recurring_changes":   recurring_changes,
        "margin_movement":     margin_movement,
        "phase3_assumptions":  phase3_assumptions,
    }

    # --- write parquet ---
    print("\nWriting parquet...")
    for name, df in all_tables.items():
        _write_parquet(df, name)
        print(f"  db/{name}.parquet  ({len(df)} rows)")

    # --- write markdown ---
    print("\nWriting markdown...")
    titles = {
        "mom_variance":        "MoM Variance — Invoice Amount by Service",
        "new_services":        "New Services (current period only)",
        "removed_services":    "Removed Services (prior period only)",
        "usage_spikes":        f"Usage Spikes (>{USAGE_SPIKE_MULTIPLIER}× prior amount)",
        "recurring_changes":   f"Recurring Charge Changes (>{RECURRING_CHANGE_THRESHOLD_PCT:.0%} MoM)",
        "margin_movement":     "Margin Movement vs Prior Period",
        "phase3_assumptions":  "Phase 3 Assumptions",
    }
    for name, df in all_tables.items():
        _write_markdown(df, name, output_dir, title=titles.get(name, name))
        print(f"  output/phase3_{run_id}/{name}.md")

    # --- summary ---
    print(f"\n{'='*52}")
    print(f"  New services              : {len(new_services)}")
    print(f"  Removed services          : {len(removed_services)}")
    print(f"  Usage spikes              : {len(usage_spikes)}")
    print(f"  Recurring charge changes  : {len(recurring_changes)}")
    print(f"  Margin movement tracked   : {len(margin_movement)}")

    if len(usage_spikes):
        print(f"\n  Usage spikes (>{USAGE_SPIKE_MULTIPLIER}× prior):")
        for _, r in usage_spikes.iterrows():
            print(f"    {r['supplier_service_id']}  prior=${r['prior_amount']:.2f}  "
                  f"current=${r['current_amount']:.2f}  "
                  f"change={r['pct_change']*100:.1f}%")

    print(f"\nDone. Run ID: {run_id}")
    return {
        "run_id":     run_id,
        "run_ts":     run_ts,
        "output_dir": str(output_dir),
        "tables":     all_tables,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 3 trend analysis.")
    parser.add_argument("--invoice",       default=str(DB / "invoice.parquet"))
    parser.add_argument("--prior-invoice", default=str(DB / "prior_invoice.parquet"))
    parser.add_argument("--sales",         default=str(DB / "sales_billing.parquet"))
    parser.add_argument("--prior-sales",   default=str(DB / "prior_sales_billing.parquet"))
    parser.add_argument("--matched",       default=str(DB / "matched_lines.parquet"))
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    required = {
        "invoice":       Path(args.invoice),
        "prior-invoice": Path(args.prior_invoice),
        "sales":         Path(args.sales),
        "prior-sales":   Path(args.prior_sales),
        "matched":       Path(args.matched),
    }
    for label, p in required.items():
        if not p.exists():
            print(f"ERROR: {label} not found: {p}", file=sys.stderr)
            print("Run load_inputs.py and invoice_analysis_skeleton.py first.", file=sys.stderr)
            return 1

    out_dir = Path(args.output_dir) if args.output_dir else None
    run_trend_analysis(
        Path(args.invoice), Path(args.prior_invoice),
        Path(args.sales), Path(args.prior_sales),
        Path(args.matched), out_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
